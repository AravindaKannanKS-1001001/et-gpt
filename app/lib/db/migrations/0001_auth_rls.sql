-- Phase 2: Better Auth identity tables + row-level security.
ALTER TABLE "User" DROP COLUMN IF EXISTS "password";
ALTER TABLE "User" ALTER COLUMN "email" TYPE varchar(255);
ALTER TABLE "User" ADD CONSTRAINT "User_email_unique" UNIQUE ("email");
UPDATE "User" SET "name" = '' WHERE "name" IS NULL;
ALTER TABLE "User" ALTER COLUMN "name" SET DEFAULT '';
ALTER TABLE "User" ALTER COLUMN "name" SET NOT NULL;
ALTER TABLE "User" ADD COLUMN IF NOT EXISTS "role" text NOT NULL DEFAULT 'user';
ALTER TABLE "User" ADD COLUMN IF NOT EXISTS "banned" boolean NOT NULL DEFAULT false;
ALTER TABLE "User" ADD COLUMN IF NOT EXISTS "banReason" text;
ALTER TABLE "User" ADD COLUMN IF NOT EXISTS "banExpires" timestamp;

CREATE TABLE IF NOT EXISTS "Session" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  "expiresAt" timestamp NOT NULL,
  "token" text NOT NULL UNIQUE,
  "createdAt" timestamp NOT NULL DEFAULT now(),
  "updatedAt" timestamp NOT NULL DEFAULT now(),
  "ipAddress" text,
  "userAgent" text,
  "impersonatedBy" text,
  "userId" uuid NOT NULL REFERENCES "User"("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "Session_userId_idx" ON "Session" ("userId");
CREATE TABLE IF NOT EXISTS "Account" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  "accountId" text NOT NULL,
  "providerId" text NOT NULL,
  "userId" uuid NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "accessToken" text, "refreshToken" text, "idToken" text,
  "accessTokenExpiresAt" timestamp, "refreshTokenExpiresAt" timestamp,
  "scope" text, "password" text,
  "createdAt" timestamp NOT NULL DEFAULT now(),
  "updatedAt" timestamp NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS "Account_userId_idx" ON "Account" ("userId");
CREATE TABLE IF NOT EXISTS "Verification" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  "identifier" text NOT NULL,
  "value" text NOT NULL,
  "expiresAt" timestamp NOT NULL,
  "createdAt" timestamp NOT NULL DEFAULT now(),
  "updatedAt" timestamp NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS "AuthRateLimit" (
  "id" text PRIMARY KEY NOT NULL,
  "key" text NOT NULL,
  "count" bigint NOT NULL,
  "lastRequest" bigint NOT NULL
);

-- Row-level security. The app connects as role et_app (no BYPASSRLS); every
-- query runs in a transaction that sets app.user_id / app.role. Unset = no rows.
ALTER TABLE "Chat" ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS chat_sel ON "Chat";
DROP POLICY IF EXISTS chat_mod ON "Chat";
CREATE POLICY chat_sel ON "Chat" FOR SELECT USING ("userId"::text = current_setting('app.user_id', true) OR current_setting('app.role', true) = 'admin');
CREATE POLICY chat_mod ON "Chat" FOR ALL USING ("userId"::text = current_setting('app.user_id', true)) WITH CHECK ("userId"::text = current_setting('app.user_id', true));
ALTER TABLE "Message_v2" ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS msg_sel ON "Message_v2";
DROP POLICY IF EXISTS msg_mod ON "Message_v2";
CREATE POLICY msg_sel ON "Message_v2" FOR SELECT USING (EXISTS (SELECT 1 FROM "Chat" c WHERE c.id = "chatId" AND c."userId"::text = current_setting('app.user_id', true)) OR current_setting('app.role', true) = 'admin');
CREATE POLICY msg_mod ON "Message_v2" FOR ALL USING (EXISTS (SELECT 1 FROM "Chat" c WHERE c.id = "chatId" AND c."userId"::text = current_setting('app.user_id', true))) WITH CHECK (EXISTS (SELECT 1 FROM "Chat" c WHERE c.id = "chatId" AND c."userId"::text = current_setting('app.user_id', true)));
ALTER TABLE "Vote_v2" ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS vote_sel ON "Vote_v2";
DROP POLICY IF EXISTS vote_mod ON "Vote_v2";
CREATE POLICY vote_sel ON "Vote_v2" FOR SELECT USING (EXISTS (SELECT 1 FROM "Chat" c WHERE c.id = "chatId" AND c."userId"::text = current_setting('app.user_id', true)) OR current_setting('app.role', true) = 'admin');
CREATE POLICY vote_mod ON "Vote_v2" FOR ALL USING (EXISTS (SELECT 1 FROM "Chat" c WHERE c.id = "chatId" AND c."userId"::text = current_setting('app.user_id', true))) WITH CHECK (EXISTS (SELECT 1 FROM "Chat" c WHERE c.id = "chatId" AND c."userId"::text = current_setting('app.user_id', true)));
ALTER TABLE "Stream" ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS stream_sel ON "Stream";
DROP POLICY IF EXISTS stream_mod ON "Stream";
CREATE POLICY stream_sel ON "Stream" FOR SELECT USING (EXISTS (SELECT 1 FROM "Chat" c WHERE c.id = "chatId" AND c."userId"::text = current_setting('app.user_id', true)) OR current_setting('app.role', true) = 'admin');
CREATE POLICY stream_mod ON "Stream" FOR ALL USING (EXISTS (SELECT 1 FROM "Chat" c WHERE c.id = "chatId" AND c."userId"::text = current_setting('app.user_id', true))) WITH CHECK (EXISTS (SELECT 1 FROM "Chat" c WHERE c.id = "chatId" AND c."userId"::text = current_setting('app.user_id', true)));
ALTER TABLE "Document" ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS doc_sel ON "Document";
DROP POLICY IF EXISTS doc_mod ON "Document";
CREATE POLICY doc_sel ON "Document" FOR SELECT USING ("userId"::text = current_setting('app.user_id', true) OR current_setting('app.role', true) = 'admin');
CREATE POLICY doc_mod ON "Document" FOR ALL USING ("userId"::text = current_setting('app.user_id', true)) WITH CHECK ("userId"::text = current_setting('app.user_id', true));
ALTER TABLE "Suggestion" ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS sugg_sel ON "Suggestion";
DROP POLICY IF EXISTS sugg_mod ON "Suggestion";
CREATE POLICY sugg_sel ON "Suggestion" FOR SELECT USING ("userId"::text = current_setting('app.user_id', true) OR current_setting('app.role', true) = 'admin');
CREATE POLICY sugg_mod ON "Suggestion" FOR ALL USING ("userId"::text = current_setting('app.user_id', true)) WITH CHECK ("userId"::text = current_setting('app.user_id', true));
