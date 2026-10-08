import { AsyncLocalStorage } from "node:async_hooks";

// Who is making the current request; read by queries.ts to set RLS context.
export type Principal = { userId: string; role: string };
export const principalStore = new AsyncLocalStorage<Principal>();
