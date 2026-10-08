import type { UserType } from "@/app/(auth)/auth";
import { ChatbotError } from "@/lib/errors";

// Single authorization point. Every route calls assertCan() before acting;
// ownership is additionally enforced by Postgres RLS.
export type Action =
  | "chat:create"
  | "chat:read_own"
  | "chat:delete_own"
  | "tool:read"
  | "tool:calculate"
  | "upload:create"
  | "memory:long_term"
  | "admin:access";

const GUEST: Action[] = ["chat:create", "chat:read_own", "chat:delete_own", "tool:read"];
const USER: Action[] = [...GUEST, "tool:calculate", "upload:create", "memory:long_term"];
const matrix: Record<UserType, Action[]> = {
  admin: [...USER, "admin:access"],
  guest: GUEST,
  user: USER,
};

export function can(type: UserType | undefined, action: Action) {
  return !!type && matrix[type].includes(action);
}

export function assertCan(type: UserType | undefined, action: Action) {
  if (!can(type, action)) {
    throw new ChatbotError(type ? "forbidden:api" : "unauthorized:chat");
  }
}
