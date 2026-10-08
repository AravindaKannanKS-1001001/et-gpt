// ET-GPT: single OpenAI-compatible model (NVIDIA Nemotron by default).
// Provider wiring lives in providers.ts; capabilities are static config here.
export const DEFAULT_CHAT_MODEL =
  process.env.OPENAI_COMPATIBLE_MODEL ?? "nvidia/nemotron-3.5-lightning-30b-a3b";

export const titleModel = { id: DEFAULT_CHAT_MODEL };

export type ModelCapabilities = {
  tools: boolean;
  vision: boolean;
  reasoning: boolean;
};

export type ChatModel = {
  id: string;
  name: string;
  provider: string;
  description: string;
  reasoningEffort?: "none" | "minimal" | "low" | "medium" | "high";
};

export const chatModels: ChatModel[] = [
  {
    description: "EarthTekniks assistant",
    id: DEFAULT_CHAT_MODEL,
    name: "ET-GPT",
    provider: "nvidia",
  },
];

// ponytail: static caps; vision stays false until verified against the endpoint (Phase 4).
export async function getCapabilities(): Promise<
  Record<string, ModelCapabilities>
> {
  return Object.fromEntries(
    chatModels.map((m) => [
      m.id,
      { reasoning: false, tools: true, vision: false },
    ])
  );
}

export const isDemo = false;

export type GatewayModelWithCapabilities = ChatModel & {
  capabilities: ModelCapabilities;
};

export async function getAllGatewayModels(): Promise<
  GatewayModelWithCapabilities[]
> {
  return [];
}

export function getActiveModels(): ChatModel[] {
  return chatModels;
}

export const allowedModelIds = new Set(chatModels.map((m) => m.id));

export const modelsByProvider = chatModels.reduce(
  (acc, model) => {
    (acc[model.provider] ??= []).push(model);
    return acc;
  },
  {} as Record<string, ChatModel[]>
);

export type ModelAvailability = "healthy" | "impacted" | "unknown";

export async function getModelAvailability(
  _modelId: string
): Promise<ModelAvailability> {
  return "unknown";
}
