import { headers } from "next/headers";
import { authServer } from "@/lib/auth";
import { principalStore } from "@/lib/db/principal";

export type UserType = "guest" | "user" | "admin";

export type AppSession = {
  user: { id: string; email: string; name: string; type: UserType };
};

export function userTypeOf(u: {
  role?: string | null;
  isAnonymous?: boolean | null;
}): UserType {
  if (u.role === "admin") {
    return "admin";
  }
  return u.isAnonymous ? "guest" : "user";
}

/** Current session mapped to an ET-GPT principal, or null. */
export async function auth(): Promise<AppSession | null> {
  const s = await authServer.api.getSession({ headers: await headers() });
  if (!s) {
    return null;
  }
  const u = s.user as typeof s.user & { role?: string; isAnonymous?: boolean };
  return {
    user: { email: u.email, id: u.id, name: u.name, type: userTypeOf(u) },
  };
}

/** Wrap a route handler so all DB queries inside carry the caller's RLS context. */
export function withPrincipal<A extends unknown[], R>(
  handler: (...args: A) => Promise<R>
) {
  return async (...args: A): Promise<R> => {
    const session = await auth();
    return principalStore.run(
      session
        ? { role: session.user.type === "admin" ? "admin" : "user", userId: session.user.id }
        : { role: "", userId: "" },
      () => handler(...args)
    );
  };
}
