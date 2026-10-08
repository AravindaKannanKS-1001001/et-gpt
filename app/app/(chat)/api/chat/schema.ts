import { z } from "zod";

const textPartSchema = z.object({
  text: z.string().min(1).max(2000),
  type: z.enum(["text"]),
});

const filePartSchema = z.object({
  mediaType: z.enum(["image/jpeg", "image/png"]),
  name: z.string().min(1).max(100),
  type: z.enum(["file"]),
  url: z.url(),
});

// Customer's answer to a calculation form (approve with edited inputs, or cancel).
const decisionPartSchema = z.object({
  data: z.object({
    action: z.enum(["approve", "cancel"]),
    args: z.record(z.string(), z.union([z.number(), z.string()])).optional(),
    note: z.string().max(500).optional(),
    proposalId: z.string().min(1).max(100),
  }),
  type: z.literal("data-calculationDecision"),
});

const partSchema = z.union([textPartSchema, filePartSchema, decisionPartSchema]);

const userMessageSchema = z.object({
  id: z.uuid(),
  parts: z.array(partSchema),
  role: z.enum(["user"]),
});

export const postRequestBodySchema = z.object({
  id: z.uuid(),
  message: userMessageSchema,
  selectedChatModel: z.string(),
  selectedVisibilityType: z.enum(["public", "private"]),
});

export type PostRequestBody = z.infer<typeof postRequestBodySchema>;
