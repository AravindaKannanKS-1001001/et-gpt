// PII redaction via the local Microsoft Presidio service (pii-service/).
// Everything sent to OpenJEV / the LLM goes through here. Fail closed.
const URL_BASE = process.env.PII_URL ?? "http://127.0.0.1:8010";
const cache = new Map<string, string>();

export class PiiUnavailableError extends Error {
  constructor() {
    super("Privacy filter unavailable");
  }
}

export async function redactTexts(texts: string[]): Promise<string[]> {
  const missing = [...new Set(texts.filter((t) => t && !cache.has(t)))];
  if (missing.length) {
    let out: string[];
    try {
      const res = await fetch(`${URL_BASE}/redact-batch`, {
        body: JSON.stringify({ texts: missing }),
        headers: { "content-type": "application/json" },
        method: "POST",
        signal: AbortSignal.timeout(5000),
      });
      if (!res.ok) {
        throw new Error(String(res.status));
      }
      out = ((await res.json()) as { texts: string[] }).texts;
    } catch {
      throw new PiiUnavailableError();
    }
    missing.forEach((t, i) => {
      if (cache.size > 2000) {
        cache.clear();
      }
      cache.set(t, out[i]);
    });
  }
  return texts.map((t) => (t ? (cache.get(t) as string) : t));
}
