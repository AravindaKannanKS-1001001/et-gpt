import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";

// Owner connection: used ONLY for identity (Better Auth), rate-limit storage,
// and admin jobs. Never use it for customer data reads on behalf of a user.
const url = process.env.POSTGRES_URL_ADMIN ?? "";
export const adminSql = postgres(url);
export const adminDb = drizzle(adminSql);
