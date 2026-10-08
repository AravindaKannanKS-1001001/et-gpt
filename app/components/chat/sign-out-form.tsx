"use client";

import { authClient } from "@/lib/auth-client";

export const SignOutForm = () => (
  <button
    className="w-full px-1 py-0.5 text-left text-red-500"
    onClick={() => authClient.signOut().then(() => window.location.assign("/"))}
    type="button"
  >
    Sign out
  </button>
);
