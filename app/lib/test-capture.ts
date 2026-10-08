import { appendFileSync, mkdirSync } from "node:fs";

// Test hook: when TEST_CAPTURE_DIR is set, append what would be sent to the LLM
// / OpenJEV so tests can assert that no raw PII leaves the server. No-op otherwise.
export function captureForTests(channel: "llm" | "router", payload: unknown) {
  const dir = process.env.TEST_CAPTURE_DIR;
  if (!dir) {
    return;
  }
  mkdirSync(dir, { recursive: true });
  appendFileSync(`${dir}/${channel}.log`, `${JSON.stringify(payload)}\n`);
}
