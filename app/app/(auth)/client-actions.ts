"use client";

import { z } from "zod";
import { authClient } from "@/lib/auth-client";

const authFormSchema = z.object({
  email: z.email(),
  password: z.string().min(8),
});

export type LoginActionState = {
  status: "idle" | "in_progress" | "success" | "failed" | "invalid_data" | "unverified";
};

// Client-side calls so Better Auth sets/refreshes the session cookies normally
// (an existing guest session is upgraded and its chats move to the account).
export const login = async (_: LoginActionState, formData: FormData): Promise<LoginActionState> => {
  const parsed = authFormSchema.safeParse({
    email: formData.get("email"),
    password: formData.get("password"),
  });
  if (!parsed.success) {
    return { status: "invalid_data" };
  }
  const { error } = await authClient.signIn.email(parsed.data);
  if (error?.status === 403) {
    return { status: "unverified" };
  }
  return { status: error ? "failed" : "success" };
};

export type RegisterActionState = {
  status: "idle" | "in_progress" | "success" | "failed" | "user_exists" | "invalid_data";
};

export const register = async (_: RegisterActionState, formData: FormData): Promise<RegisterActionState> => {
  const parsed = authFormSchema.safeParse({
    email: formData.get("email"),
    password: formData.get("password"),
  });
  if (!parsed.success) {
    return { status: "invalid_data" };
  }
  const { error } = await authClient.signUp.email({
    ...parsed.data,
    name: parsed.data.email.split("@")[0],
  });
  if (error?.code === "USER_ALREADY_EXISTS_USE_ANOTHER_EMAIL" || error?.code === "USER_ALREADY_EXISTS") {
    return { status: "user_exists" };
  }
  return { status: error ? "failed" : "success" };
};
