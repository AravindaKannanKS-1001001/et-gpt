"use client";

import { useState } from "react";
import { useActiveChat } from "@/hooks/use-active-chat";
import type { ChatMessage } from "@/lib/types";

type AnyPart = {
  type: string;
  state?: string;
  toolCallId?: string;
  input?: unknown;
  output?: unknown;
  // biome-ignore lint/suspicious/noExplicitAny: data parts are loosely typed
  data?: any;
};

// Customer-friendly names for MCP/local tools (no raw tool jargon in the UI).
const LABELS: Record<string, string> = {
  createPlan: "Planning the steps",
  describe_table: "Reading a catalog table",
  get_calculator: "Reading the calculator's inputs",
  get_document: "Reading a document",
  get_product: "Looking up a product",
  get_reference: "Reading a reference table",
  get_table_knowledge: "Reading catalog notes",
  list_families: "Browsing lens families",
  list_tables: "Listing catalog tables",
  loadSkill: "Checking how to handle this",
  lookup: "Looking up a value",
  lookup_model: "Finding a lens model",
  search_calculator: "Finding the right calculator",
  search_knowledge: "Searching the catalog guide",
  search_knowledge_base: "Searching EarthTekniks information",
  search_lookups: "Finding reference tables",
  search_products: "Searching the catalog",
};

const box =
  "w-[min(100%,460px)] rounded-xl border border-border/50 bg-card p-3 text-[13px] shadow-[var(--shadow-card)]";

function Plan({ part }: { part: AnyPart }) {
  const out = part.output as
    | { goal?: string; steps?: { area: string; title: string }[] }
    | undefined;
  if (!out?.steps) {
    return null;
  }
  return (
    <div aria-label="Plan" className={box}>
      <div className="mb-1.5 font-semibold text-primary">Plan</div>
      <ol className="list-decimal space-y-1 pl-5">
        {out.steps.map((s, i) => (
          <li key={`${i}-${s.title}`}>
            {s.title} <span className="text-muted-foreground">· {s.area}</span>
          </li>
        ))}
      </ol>
    </div>
  );
}

function Activity({ name, state }: { name: string; state?: string }) {
  const done = state === "output-available";
  const failed = state === "output-error";
  return (
    <div
      className="flex items-center gap-2 text-[12px] text-muted-foreground"
      role="status"
    >
      <span aria-hidden>{failed ? "⚠" : done ? "✓" : "…"}</span>
      <span>{LABELS[name] ?? "Working on it"}</span>
    </div>
  );
}

type Prop = { description?: string; title?: string; type?: string };

function CalculationForm({ part }: { part: AnyPart }) {
  const { messages, sendMessage, status } = useActiveChat();
  const out = part.output as
    | {
        formula_id: string;
        schema: { properties: Record<string, Prop>; required?: string[] };
        prefill: Record<string, number | string>;
        error?: string;
      }
    | undefined;
  const id = part.toolCallId as string;
  const answered = messages.some(
    (m: ChatMessage) =>
      m.role === "user" &&
      (m.parts as AnyPart[]).some(
        (p) => p.type === "data-calculationDecision" && p.data?.proposalId === id
      )
  );
  const [values, setValues] = useState<Record<string, string>>(
    Object.fromEntries(
      Object.entries(out?.prefill ?? {}).map(([k, v]) => [k, String(v)])
    )
  );
  const [note, setNote] = useState("");
  const [err, setErr] = useState<string | null>(null);

  if (!out || out.error) {
    return (
      <div className={box}>{out?.error ?? "That calculator is unavailable."}</div>
    );
  }
  const props = out.schema.properties ?? {};
  const required = new Set(out.schema.required ?? []);
  const busy = status === "submitted" || status === "streaming";

  const submit = (action: "approve" | "cancel") => {
    let args: Record<string, number | string> | undefined;
    if (action === "approve") {
      args = {};
      for (const [k, p] of Object.entries(props)) {
        const raw = (values[k] ?? "").trim();
        if (!raw) {
          if (required.has(k)) {
            setErr(`Please fill in "${p.title ?? k}".`);
            return;
          }
          continue;
        }
        if (p.type === "number" || p.type === "integer") {
          const num = Number(raw);
          if (!Number.isFinite(num)) {
            setErr(`"${p.title ?? k}" must be a number.`);
            return;
          }
          args[k] = num;
        } else {
          args[k] = raw;
        }
      }
    }
    setErr(null);
    sendMessage({
      parts: [
        {
          data: { action, args, note: note.trim() || undefined, proposalId: id },
          type: "data-calculationDecision",
        },
      ],
      role: "user",
    } as never);
  };

  return (
    <form
      aria-label={`Calculation ${out.formula_id}`}
      className={box}
      onSubmit={(e) => {
        e.preventDefault();
        submit("approve");
      }}
    >
      <div className="mb-1 font-semibold text-primary">
        Review calculation: {out.formula_id.replace(/_/g, " ")}
      </div>
      <p className="mb-2 text-muted-foreground">
        Check or edit the values. Nothing runs until you approve. Blank fields
        were not provided.
      </p>
      <div className="space-y-2">
        {Object.entries(props).map(([k, p]) => (
          <label className="block" key={k}>
            <span className="font-medium">
              {p.title ?? k}
              {required.has(k) ? " *" : ""}
            </span>
            <input
              className="mt-0.5 w-full rounded-md border border-border/60 bg-background px-2 py-1.5 disabled:opacity-60"
              disabled={answered || busy}
              inputMode={p.type === "number" ? "decimal" : undefined}
              name={k}
              onChange={(e) => setValues((v) => ({ ...v, [k]: e.target.value }))}
              placeholder="not provided"
              value={values[k] ?? ""}
            />
            {p.description ? (
              <span className="text-[11px] text-muted-foreground">
                {p.description}
              </span>
            ) : null}
          </label>
        ))}
        <label className="block">
          <span className="font-medium">Additional context (optional)</span>
          <textarea
            className="mt-0.5 w-full rounded-md border border-border/60 bg-background px-2 py-1.5 disabled:opacity-60"
            disabled={answered || busy}
            maxLength={500}
            onChange={(e) => setNote(e.target.value)}
            rows={2}
            value={note}
          />
        </label>
      </div>
      {err ? (
        <p className="mt-2 text-red-600" role="alert">
          {err}
        </p>
      ) : null}
      {answered ? (
        <p className="mt-2 text-muted-foreground">You have answered this form.</p>
      ) : (
        <div className="mt-3 flex justify-end gap-2">
          <button
            className="rounded-md px-3 py-1.5 text-muted-foreground hover:bg-muted"
            disabled={busy}
            onClick={() => submit("cancel")}
            type="button"
          >
            Cancel
          </button>
          <button
            className="rounded-md bg-primary px-3 py-1.5 text-primary-foreground hover:bg-primary/90 disabled:opacity-60"
            disabled={busy}
            type="submit"
          >
            Approve &amp; run
          </button>
        </div>
      )}
    </form>
  );
}

function CalculationResult({ part }: { part: AnyPart }) {
  const input = part.input as { formula_id?: string } | undefined;
  return (
    <div aria-label="Calculation result" className={box}>
      <div className="mb-1 font-semibold text-primary">
        Result: {(input?.formula_id ?? "").replace(/_/g, " ")}
      </div>
      <pre className="overflow-x-auto whitespace-pre-wrap text-[12px]">
        {JSON.stringify(part.output, null, 2)}
      </pre>
    </div>
  );
}

/** Renders ET-GPT's own tool parts; returns undefined for anything else. */
export function renderEtPart(part: AnyPart, key: string) {
  const { type } = part;
  if (type === "data-calculationDecision") {
    return (
      <div className="text-[12px] text-muted-foreground" key={key}>
        {part.data?.action === "cancel"
          ? "✕ You cancelled the calculation"
          : "✓ You approved the calculation"}
      </div>
    );
  }
  if (type === "tool-createPlan") {
    return <Plan key={key} part={part} />;
  }
  if (type === "tool-proposeCalculation") {
    return part.state === "output-available" ? (
      <CalculationForm key={key} part={part} />
    ) : (
      <Activity key={key} name="get_calculator" state={part.state} />
    );
  }
  if (type === "tool-calculate") {
    return <CalculationResult key={key} part={part} />;
  }
  if (type === "dynamic-tool" || type.startsWith("tool-")) {
    const name =
      type === "dynamic-tool"
        ? String((part as { toolName?: string }).toolName)
        : type.slice(5);
    return <Activity key={key} name={name} state={part.state} />;
  }
  return undefined;
}
