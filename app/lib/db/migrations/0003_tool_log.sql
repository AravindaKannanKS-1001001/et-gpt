-- Audit of MCP tool executions (written by the server via the owner connection).
CREATE TABLE IF NOT EXISTS "ToolLog" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "userId" uuid NOT NULL,
  "chatId" uuid,
  "tool" text NOT NULL,
  "ok" boolean NOT NULL,
  "createdAt" timestamp NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS "ToolLog_user_idx" ON "ToolLog" ("userId", "createdAt");
