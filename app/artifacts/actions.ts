"use server";

import { withPrincipal } from "@/app/(auth)/auth";
import { getSuggestionsByDocumentId } from "@/lib/db/queries";

export async function getSuggestions({ documentId }: { documentId: string }) {
  return withPrincipal(async () => {
    const suggestions = await getSuggestionsByDocumentId({ documentId });
    return suggestions ?? [];
  })();
}
