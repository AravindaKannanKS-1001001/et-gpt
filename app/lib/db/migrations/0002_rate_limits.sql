-- Storage for rate-limiter-flexible (RateLimiterPostgres).
CREATE TABLE IF NOT EXISTS "rate_limits" (
  "key" varchar(255) PRIMARY KEY,
  "points" int NOT NULL DEFAULT 0,
  "expire" bigint
);
