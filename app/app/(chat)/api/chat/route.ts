import {
  convertToModelMessages,
  createUIMessageStream,
  createUIMessageStreamResponse,
  hasToolCall,
  isStepCount,
  streamText,
  type ToolSet,
  toUIMessageStream,
} from "ai";
import { auth, withPrincipal } from "@/app/(auth)/auth";
import { regularPrompt } from "@/lib/ai/prompts";
import { getLanguageModel } from "@/lib/ai/providers";
import { createPlan, loadSkill, proposeCalculation } from "@/lib/ai/tools/local";
import { assertCan, can } from "@/lib/authz";
import { type Schema, validateArgs } from "@/lib/calc";
import {
  deleteChatById,
  getChatById,
  getMessagesByChatId,
  saveChat,
  saveMessages,
  updateChatTitleById,
} from "@/lib/db/queries";
import { ChatbotError } from "@/lib/errors";
import { blockReason, CANNED, priceMaskTransform, routeHints } from "@/lib/guardrails";
import { openMcp, parseToolResult } from "@/lib/mcp";
import { PiiUnavailableError, redactTexts } from "@/lib/pii";
import {
  consumeRequest,
  MAX_MODEL_STEPS,
  RateLimitedError,
  REQUEST_TIME_BUDGET_MS,
} from "@/lib/ratelimit";
import { classify } from "@/lib/router";
import { skillsPrompt } from "@/lib/skills";
import type { CalculationDecision, ChatMessage } from "@/lib/types";
import { convertToUIMessages, generateUUID, getTextFromMessage } from "@/lib/utils";
import { generateTitleFromUserMessage } from "../../actions";
import { type PostRequestBody, postRequestBodySchema } from "./schema";

export const maxDuration = 60;

function hasPgCode(error: unknown, code: string): boolean {
  let e = error as { code?: string; cause?: unknown } | undefined;
  while (e) {
    if (e.code === code) {
      return true;
    }
    e = e.cause as typeof e;
  }
  return false;
}

type AnyPart = { type: string; [k: string]: unknown };
const isDecision = (p: AnyPart): p is AnyPart & { data: CalculationDecision } =>
  p.type === "data-calculationDecision";

/** The open (unanswered) calculation form with this id, from the saved chat. */
function pendingProposal(history: ChatMessage[], proposalId: string) {
  const answered = history.some(
    (m) =>
      m.role === "user" &&
      (m.parts as AnyPart[]).some((p) => isDecision(p) && p.data.proposalId === proposalId)
  );
  if (answered) {
    return null;
  }
  for (const m of history) {
    if (m.role !== "assistant") {
      continue;
    }
    for (const p of m.parts as AnyPart[]) {
      if (
        p.type === "tool-proposeCalculation" &&
        p.toolCallId === proposalId &&
        p.state === "output-available" &&
        p.output &&
        !(p.output as { error?: unknown }).error
      ) {
        return p.output as { formula_id: string; schema: Schema; prefill: Record<string, unknown> };
      }
    }
  }
  return null;
}

const describeDecision = (d: CalculationDecision, formula?: string) =>
  d.action === "cancel"
    ? "Customer cancelled the calculation."
    : `Customer approved calculation ${formula ?? ""} with inputs ${JSON.stringify(d.args ?? {})}.${d.note ? ` Note: ${d.note}` : ""}`;

/**
 * What the model sees: user text is PII-redacted, calculation answers become
 * text, and approved calculation results in earlier assistant turns are text.
 */
async function toModelView(ui: ChatMessage[], extraResult?: string) {
  const raw: string[] = [];
  for (const m of ui) {
    if (m.role === "user") {
      for (const p of m.parts as AnyPart[]) {
        if (p.type === "text") {
          raw.push(p.text as string);
        }
        if (isDecision(p) && p.data.note) {
          raw.push(p.data.note);
        }
      }
    }
  }
  const red = await redactTexts(raw);
  let i = 0;
  const formulas = new Map<string, string>();
  for (const m of ui) {
    for (const p of m.parts as AnyPart[]) {
      if (p.type === "tool-proposeCalculation" && p.output) {
        formulas.set(String(p.toolCallId), String((p.output as { formula_id?: string }).formula_id));
      }
    }
  }
  const view = ui.map((m) => {
    const parts: AnyPart[] = [];
    for (const p of m.parts as AnyPart[]) {
      if (m.role === "user" && p.type === "text") {
        parts.push({ ...p, text: red[i++] });
      } else if (m.role === "user" && isDecision(p)) {
        const note = p.data.note ? red[i++] : undefined;
        parts.push({
          text: describeDecision({ ...p.data, note }, formulas.get(p.data.proposalId)),
          type: "text",
        });
      } else if (m.role === "assistant" && p.type === "tool-calculate") {
        parts.push({
          text: `[Approved calculation executed by the server. inputs: ${JSON.stringify(p.input)} result: ${JSON.stringify(p.output)}]`,
          type: "text",
        });
      } else if (!p.type.startsWith("data-")) {
        parts.push(p);
      }
    }
    return { ...m, parts } as ChatMessage;
  });
  if (extraResult) {
    const last = view.at(-1);
    if (last?.role === "user") {
      const joined = (last.parts as AnyPart[])
        .filter((p) => p.type === "text")
        .map((p) => p.text)
        .join("");
      last.parts = [{ text: `${joined} ${extraResult} Continue the original request.`, type: "text" }] as never;
    }
  }
  return {
    latest: [...view].reverse().find((m) => m.role === "user"),
    messages: await convertToModelMessages(view, { ignoreIncompleteToolCalls: true }),
    view,
  };
}

function textStream(
  text: string,
  persist: (m: ChatMessage[]) => Promise<void>,
  titlePromise?: Promise<string> | null,
  chatId?: string
) {
  return createUIMessageStream({
    execute: async ({ writer }) => {
      const tid = generateUUID();
      writer.write({ id: tid, type: "text-start" });
      writer.write({ delta: text, id: tid, type: "text-delta" });
      writer.write({ id: tid, type: "text-end" });
      if (titlePromise && chatId) {
        try {
          const title = await titlePromise;
          writer.write({ data: title, type: "data-chat-title" });
          updateChatTitleById({ chatId, title });
        } catch {
          /* non-fatal */
        }
      }
    },
    generateId: generateUUID,
    onEnd: async ({ messages }) => persist(messages as ChatMessage[]),
  });
}

async function POSTImpl(request: Request) {
  let body: PostRequestBody;
  try {
    body = postRequestBodySchema.parse(await request.json());
  } catch {
    return new ChatbotError("bad_request:api").toResponse();
  }

  try {
    const { id, message, selectedVisibilityType } = body;
    const session = await auth();
    if (!session?.user) {
      return new ChatbotError("unauthorized:chat").toResponse();
    }
    const { type: role, id: userId } = session.user;
    assertCan(role, "chat:create");

    const decisionPart = (message.parts as AnyPart[]).find(isDecision);
    // A calculation answer continues the same request: it is not a new question.
    if (!decisionPart) {
      await consumeRequest(userId, role);
    }

    const chat = await getChatById({ id });
    let history: ChatMessage[] = [];
    let titlePromise: Promise<string> | null = null;
    if (chat) {
      if (chat.userId !== userId) {
        return new ChatbotError("forbidden:chat").toResponse();
      }
      history = convertToUIMessages(await getMessagesByChatId({ id }));
    } else {
      if (decisionPart) {
        // No such chat for this user (it may belong to someone else; RLS hides it).
        return new ChatbotError("forbidden:chat").toResponse();
      }
      try {
        await saveChat({ id, title: "New chat", userId, visibility: selectedVisibilityType });
      } catch (error) {
        // RLS hides other users' chats, so a reused id surfaces as a unique violation.
        if (hasPgCode(error, "23505")) {
          return new ChatbotError("forbidden:chat").toResponse();
        }
        throw error;
      }
      titlePromise = generateTitleFromUserMessage({ message: message as never });
    }

    const userMessage = message as unknown as ChatMessage;
    const persist = async (finished: ChatMessage[]) => {
      if (finished.length) {
        await saveMessages({
          messages: finished.map((m) => ({
            attachments: [],
            chatId: id,
            createdAt: new Date(),
            id: m.id,
            parts: m.parts,
            role: m.role,
          })),
        });
      }
    };

    // ---- Answer to a calculation form -------------------------------------
    let extraResult: string | undefined;
    let syntheticCalc: { toolCallId: string; input: unknown; output: unknown } | undefined;
    let mcpForDecision: Awaited<ReturnType<typeof openMcp>> | undefined;
    if (decisionPart) {
      const d = decisionPart.data;
      const proposal = pendingProposal(history, d.proposalId);
      if (!proposal) {
        return Response.json(
          { code: "bad_request:api", message: "That calculation form is no longer open." },
          { status: 409 }
        );
      }
      if (d.action === "cancel") {
        await persist([userMessage]);
        return createUIMessageStreamResponse({
          stream: textStream("Calculation cancelled. Nothing was run.", persist),
        });
      }
      assertCan(role, "tool:calculate");
      const problem = validateArgs(proposal.schema, d.args ?? {});
      if (problem) {
        return Response.json(
          { code: "bad_request:api", message: `Please check the inputs: ${problem}` },
          { status: 422 }
        );
      }
      mcpForDecision = await openMcp(role, userId, id);
      const args = d.args ?? {};
      let output: unknown;
      try {
        output = parseToolResult(
          await mcpForDecision.call("calculate", { args, formula_id: proposal.formula_id })
        );
      } catch (e) {
        output = { error: e instanceof Error ? e.message : "calculation failed" };
      }
      syntheticCalc = {
        input: { args, formula_id: proposal.formula_id },
        output,
        toolCallId: generateUUID(),
      };
      extraResult = `Server executed it; result: ${JSON.stringify(output)}.`;
    }

    await persist([userMessage]);
    const ui = [...history, userMessage];

    // ---- Guardrails: redact, route, block -----------------------------------
    const model = await toModelView(ui, extraResult);
    const latestText = model.latest ? getTextFromMessage(model.latest as never) : "";
    let routeDecision = null;
    if (!decisionPart) {
      const tail = model.view
        .slice(-5)
        .map((m) => `${m.role}: ${getTextFromMessage(m as never).slice(0, 400)}`)
        .join("\n");
      routeDecision = await classify(tail, latestText);
      const blocked = blockReason(latestText, routeDecision);
      if (blocked) {
        return createUIMessageStreamResponse({
          stream: textStream(
            blocked === "injection" ? CANNED.injection : CANNED.offTopic,
            persist,
            titlePromise,
            id
          ),
        });
      }
    }

    // ---- Tools (role-filtered) and model call -------------------------------
    const mcp = mcpForDecision ?? (await openMcp(role, userId, id));
    const userTexts = ui
      .filter((m) => m.role === "user")
      .flatMap((m) =>
        (m.parts as AnyPart[]).filter((p) => p.type === "text").map((p) => String(p.text))
      );
    const canCalc = can(role, "tool:calculate");
    const tools = {
      ...mcp.tools,
      createPlan,
      loadSkill,
      ...(canCalc ? { proposeCalculation: proposeCalculation({ call: mcp.call, userTexts }) } : {}),
    };
    const instructions = [
      regularPrompt,
      skillsPrompt(),
      canCalc
        ? "Calculations: never run them yourself. Use proposeCalculation; the customer approves in a form."
        : "This visitor is a guest: calculations are not available. If they ask for one, explain it needs a verified account (sign in), and still help with explanations and catalog lookups.",
      mcp.degraded
        ? "Some data tools are currently unavailable. Say so plainly; never invent product data."
        : "",
      routeHints(routeDecision),
    ]
      .filter(Boolean)
      .join("\n\n");

    const stream = createUIMessageStream({
      execute: async ({ writer }) => {
        if (syntheticCalc) {
          writer.write({ messageId: generateUUID(), type: "start" });
          writer.write({
            input: syntheticCalc.input,
            toolCallId: syntheticCalc.toolCallId,
            toolName: "calculate",
            type: "tool-input-available",
          } as never);
          writer.write({
            output: syntheticCalc.output,
            toolCallId: syntheticCalc.toolCallId,
            type: "tool-output-available",
          } as never);
        }
        const result = streamText({
          abortSignal: AbortSignal.timeout(REQUEST_TIME_BUDGET_MS),
          experimental_transform: priceMaskTransform() as never,
          instructions,
          messages: model.messages,
          model: getLanguageModel(),
          onAbort: () => void mcp.close(),
          onEnd: () => void mcp.close(),
          onError: () => void mcp.close(),
          stopWhen: [isStepCount(MAX_MODEL_STEPS), hasToolCall("proposeCalculation")],
          tools: tools as ToolSet,
        });
        writer.merge(
          toUIMessageStream({ sendStart: !syntheticCalc, stream: result.stream }) as never
        );
        if (titlePromise) {
          try {
            const title = await titlePromise;
            writer.write({ data: title, type: "data-chat-title" });
            updateChatTitleById({ chatId: id, title });
          } catch {
            /* non-fatal */
          }
        }
      },
      generateId: generateUUID,
      onEnd: async ({ messages }) => persist(messages as ChatMessage[]),
      onError: () => "Sorry, something went wrong. Please try again.",
    });
    return createUIMessageStreamResponse({ stream });
  } catch (error) {
    if (error instanceof RateLimitedError) {
      return Response.json(
        { code: "rate_limit:chat", message: error.message },
        { headers: { "Retry-After": String(error.retryAfterSec) }, status: 429 }
      );
    }
    if (error instanceof PiiUnavailableError) {
      return Response.json({ code: "offline:chat", message: CANNED.piiDown }, { status: 503 });
    }
    if (error instanceof ChatbotError) {
      return error.toResponse();
    }
    console.error("Unhandled error in chat API:", error);
    return new ChatbotError("offline:chat").toResponse();
  }
}

async function DELETEImpl(request: Request) {
  const id = new URL(request.url).searchParams.get("id");
  if (!id) {
    return new ChatbotError("bad_request:api").toResponse();
  }
  const session = await auth();
  if (!session?.user) {
    return new ChatbotError("unauthorized:chat").toResponse();
  }
  const chat = await getChatById({ id });
  if (chat?.userId !== session.user.id) {
    return new ChatbotError("forbidden:chat").toResponse();
  }
  return Response.json(await deleteChatById({ id }), { status: 200 });
}

export const POST = withPrincipal(POSTImpl);
export const DELETE = withPrincipal(DELETEImpl);
