import type { RouteDecision } from "@/lib/router";

export const CONTACT_URL = "https://www.etplautomation.com/contact.html";

export const CANNED = {
  injection:
    "I can't change my rules or share internal instructions. I'm happy to help with EarthTekniks products, optics calculations or machine-vision questions though.",
  offTopic:
    "I can only help with EarthTekniks products, machine vision, optics, inspection and automation. Is there something along those lines I can help with?",
  piiDown:
    "The privacy filter is temporarily unavailable, so I can't process messages right now. Please try again in a moment.",
};

// Thresholds are tunable; OpenJEV confidence is a signal, not a guarantee.
export const T = { ambiguous: 0.7, injection: 0.8, offTopic: 0.85 };

// Deterministic backstop that does not depend on the router being up.
const INJECTION_RE =
  /(ignore|disregard|forget)\s+(all\s+|the\s+|your\s+)?(previous|prior|above|earlier)\s+(instructions|rules|prompt)|reveal\s+(your\s+|the\s+)?(system\s+)?(prompt|instructions)|print\s+(your\s+)?system\s+prompt/i;

export function blockReason(text: string, r: RouteDecision | null): "injection" | "off_topic" | null {
  if (INJECTION_RE.test(text) || (r && r.injection >= T.injection)) {
    return "injection";
  }
  if (r && r.intent === "off_topic" && r.intentConfidence >= T.offTopic) {
    return "off_topic";
  }
  return null;
}

/** System-prompt hints derived from the routing decision (never block by themselves). */
export function routeHints(r: RouteDecision | null): string {
  if (!r) {
    return "";
  }
  const h: string[] = [];
  const needsDetail = ["catalog_lookup", "calculation", "chain"].includes(r.intent);
  if (r.intent === "price_quote") {
    h.push(`This is a price/quote request. Do not state any amount; direct the customer to ${CONTACT_URL}.`);
  } else if (needsDetail && r.ambiguous >= T.ambiguous) {
    h.push(
      "The latest request is ambiguous. Ask exactly ONE short clarifying question and call NO tools. Do not guess or assume values."
    );
  } else if (r.intent === "chain") {
    h.push(
      "This is a multi-step request. Call createPlan FIRST with the ordered steps (knowledge, calculation inputs, calculation, catalog narrowing). If a calculation input cannot be obtained, say so explicitly."
    );
  }
  return h.join("\n");
}

const CURRENCY_RE = /(?:[$€£₹]\s?\d[\d,]*(?:\.\d+)?|\b(?:USD|INR|EUR|GBP|Rs\.?)\s?\d[\d,]*(?:\.\d+)?|\b\d[\d,]*(?:\.\d+)?\s?(?:USD|INR|EUR|GBP|rupees|dollars)\b)/gi;
const HOLD_RE = /^(?:USD|INR|EUR|GBP|Rs\.?|[$€£₹])$/i;

export function maskPrices(text: string) {
  return text.replace(CURRENCY_RE, "[price not shown]");
}

/**
 * Stream transform masking currency amounts in text deltas.
 * Words are buffered until whitespace; a trailing currency code/symbol is held
 * back so "USD" + " 500" cannot slip through split.
 * ponytail: an amount split inside a single word could slip through. Upgrade:
 * validate the finished message server-side.
 */
type Chunk = { type: string; id?: string; text?: string };
export function priceMaskTransform() {
  return () => {
    const held = new Map<string, string>();
    return new TransformStream<Chunk, Chunk>({
      transform(chunk, controller) {
        if (chunk.type === "text-delta" && chunk.id !== undefined) {
          const buf = (held.get(chunk.id) ?? "") + (chunk.text ?? "");
          const m = buf.match(/^([\s\S]*\s)(\S*)$/);
          let emit = m ? m[1] : "";
          let rest = m ? m[2] : buf;
          const last = emit.trimEnd().split(/\s/).pop() ?? "";
          if (emit && HOLD_RE.test(last)) {
            const cut = emit.trimEnd().length - last.length;
            rest = emit.slice(cut) + rest;
            emit = emit.slice(0, cut);
          }
          held.set(chunk.id, rest);
          if (emit) {
            controller.enqueue({ ...chunk, text: maskPrices(emit) });
          }
          return;
        }
        if (chunk.type === "text-end" && chunk.id !== undefined) {
          const rest = held.get(chunk.id);
          held.delete(chunk.id);
          if (rest) {
            controller.enqueue({ id: chunk.id, text: maskPrices(rest), type: "text-delta" });
          }
        }
        controller.enqueue(chunk);
      },
    });
  };
}
