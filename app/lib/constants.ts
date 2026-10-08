export const isProductionEnvironment = process.env.NODE_ENV === "production";
export const isDevelopmentEnvironment = process.env.NODE_ENV === "development";
export const isTestEnvironment = Boolean(
  process.env.PLAYWRIGHT_TEST_BASE_URL ||
    process.env.PLAYWRIGHT ||
    process.env.CI_PLAYWRIGHT
);

export const suggestions = [
  "What does EarthTekniks do?",
  "Which lens do I need for a 100 mm field of view?",
  "How do I calculate working distance?",
  "Tell me about your inspection systems",
];
