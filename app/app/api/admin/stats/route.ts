import { sql } from "drizzle-orm";
import { auth } from "@/app/(auth)/auth";
import { assertCan } from "@/lib/authz";
import { adminDb } from "@/lib/db/admin";
import { ChatbotError } from "@/lib/errors";

// Minimal admin-only endpoint; the analytics dashboard (Phase 4) builds on this.
export async function GET() {
  try {
    const session = await auth();
    assertCan(session?.user.type, "admin:access");
    const rows = await adminDb.execute(sql`
      select (select count(*) from "User" where not "isAnonymous") as users,
             (select count(*) from "User" where "isAnonymous") as guests,
             (select count(*) from "Chat") as chats,
             (select count(*) from "Message_v2") as messages`);
    return Response.json(rows[0]);
  } catch (e) {
    if (e instanceof ChatbotError) {
      return e.toResponse();
    }
    throw e;
  }
}
