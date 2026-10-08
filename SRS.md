# ET-GPT — Software Requirements Specification (v0.1, Phase 0)

## 1. Purpose and scope
ET-GPT is an embeddable AI support chatbot for EarthTekniks (machine vision, optics, factory automation). It is a **new build** on an actively maintained open-source foundation. It connects to the existing, independently deployed MCP servers (calculator, company knowledge, catalog) and is embedded in the mock website. The old `earthtekniks-assistant-suite/chatbot` is a behavioural reference only; its code is not the base.

Principle: glue maintained libraries; write custom code only where none exists.

## 2. Architecture

```
Visitor → mock website → widget.js (shadow DOM) → ET-GPT (Next.js) → MCP servers (HTTP)
                                                     ├─ Postgres (Better Auth, RLS, pgvector in Phase 4)
                                                     ├─ NVIDIA Nemotron (answers, tools)
                                                     └─ OpenJEV (routing / classification only)
```

| Concern | Choice | Alternative rejected |
|---|---|---|
| Base app | `vercel/chatbot` (Next.js, AI SDK, shadcn/ui, Drizzle, Postgres) | Writing from scratch; the old suite chatbot (user-declared broken) |
| Auth | **Better Auth** on the app's own Postgres: `anonymous` plugin (guest), email+password with mandatory verification (user), `admin` plugin (role). Decided in Phase 2: no Supabase (no hosted project, Docker unavailable). | Supabase Auth (needs an external project or Docker); Auth.js (template default, beta) |
| LLM | AI SDK `@ai-sdk/openai-compatible` → NVIDIA; Mock provider via `MockLanguageModel` (`ai/test`) | Custom provider layer |
| Router / guard classifier | OpenJEV `POST https://api.openjev.sh/v1/systemone` (choice/score/noul) | Second LLM router |
| MCP | `@ai-sdk/mcp` over streamable HTTP | Re-implementing servers |
| Rate limits | `rate-limiter-flexible` (Postgres store; per-minute then per-day per user, guest sessions per IP) plus Better Auth's built-in limiter on sign-in/sign-up | Hand-rolled counters; Upstash (paid/extra service) |
| PII redaction | **Microsoft Presidio** (spaCy `en_core_web_md` NER + pattern recognizers) as a local HTTP service `pii-service/` (`/redact-batch`). `openredaction` was evaluated in Phase 3 and rejected (missed phones/PAN/SSN, mangled normal words). Fails closed. | `openredaction` (poor precision/recall), hand-written regexes |
| Long-term memory | `mem0` OSS with pgvector (verified/admin only) | Custom RAG memory |
| Background jobs | `pg-boss` (Postgres queue) | Redis/BullMQ (extra service) |
| Skills | Anthropic `SKILL.md` folders | Custom format |
| Audio | In-browser Whisper via `@huggingface/transformers` (free, no server cost) | Paid STT |
| Images | Nemotron if vision-capable, else a free NVIDIA vision endpoint with the same key (verify in Phase 1) | Paid vision API |
| Analytics | Reuse existing `/admin/insights` design, rebuilt on the new schema | — |
| Deploy | Docker Compose | — |

### 2.1 Stable interfaces
1. Embed: `<script src="{ORIGIN}/widget.js" data-widget-id="…">`; no secrets in host page.
2. `POST /api/chat` — identity derived from Supabase session, never from the body.
3. `authorize(principal, action, resource)` — single backend authorization point; RLS is the second layer.
4. `LanguageModel` (AI SDK) — NVIDIA or Mock via `LLM_PROVIDER`.
5. `Router.classify(redactedText, history) → {intent, ambiguous, complexity, confidence}` — OpenJEV or Mock.
6. `Guardrail` pipeline: PII redact → scope/injection check → rate/time budget.
7. MCP config: `{name, url, headers, allowedRoles}`.
8. Skill: `skills/<name>/SKILL.md`.

## 3. Roles and limits

| Role | Requests | Tools | Memory |
|---|---|---|---|
| guest (anonymous) | 5 per day, 2 per minute | read-only knowledge and catalog | session only; none long-term |
| user (verified email) | 50 per day, 5 per minute | + calculator (with approval), uploads, voice | short + long-term |
| admin | configurable | all, plus config and analytics | all |

A "request" is one inbound user message, regardless of internal model/tool calls. Per request: max 10 model steps (continuable by approval for verified users), 60 s wall-clock budget, bounded input size and upload size. Limits are configuration, not code.

## 4. Functional requirements

- **FR-1 Chat:** streaming responses, persistent conversations, history, session management.
- **FR-2 Widget:** floating launcher, expandable panel, mobile and desktop, isolated styles (shadow DOM), brand colour `#003399`, Poppins/Open Sans from the existing site.
- **FR-3 Understanding:** ambiguous requests get one clarifying question; nothing is assumed. Unfamiliar terms are explained.
- **FR-4 Planning:** for multi-part requests the assistant shows a plan and follows it: knowledge → calculation inputs → catalog narrowing. If inputs cannot be obtained it says so explicitly.
- **FR-5 Multiple candidates:** all grounded candidates are examined; tradeoffs are explained; no silent pruning.
- **FR-6 Human in the loop:** every calculation shows a schema-driven editable form. Only user-stated or tool-confirmed values are prefilled; unknowns stay blank; approval or cancel. A prior approval never authorizes a new calculation. Cancel executes nothing.
- **FR-7 Pricing:** no prices, discounts, ranges or currency amounts; direct to https://www.etplautomation.com/contact.html. (Carried over from the existing SRS.)
- **FR-8 Scope:** decline unrelated requests politely and invite an EarthTekniks question.
- **FR-9 Guardrails:** PII is redacted before text reaches OpenJEV or logs; retrieved content is data, not instructions; secrets and system prompts are never disclosed.
- **FR-10 MCP:** configurable HTTP servers; tool discovery; execution filtered by role at discovery **and** at call time.
- **FR-11 Skills:** reusable workflows extracted from the existing tests, each documented (see §7).
- **FR-12 Multimodal:** image upload and microphone input for verified users.
- **FR-13 Memory:** short-term sliding window with exact-value-preserving compaction; long-term per-user memory for verified/admin only; background workers compact context and tool output.
- **FR-14 Budget continuation:** when a limit that approval can extend is hit, pause and offer continue or answer-from-evidence. Hard limits (credits, model context) are explained, not offered for extension.
- **FR-15 Analytics (admin only):** customer questions, trends, common issues, unanswered queries, usage, improvement suggestions; customer PII not shown.
- **FR-16 Errors:** plain-language errors with a next step; input stays usable.

### 4.2 Calculation protocol (implemented, Phase 3)
1. The model may call `proposeCalculation(formula_id, prefill)`. It never receives `calculate`. The server reads the formula's real input schema from the MCP server and keeps only prefill values the customer actually typed (each stated number fills one input).
2. The UI renders an editable form (blank = not provided) with an optional context field. The turn ends at the form.
3. The customer answers with a `data-calculationDecision` message `{proposalId, action: approve|cancel, args, note}`.
4. The server accepts it only if that proposal exists in the caller's own saved chat and is unanswered (single use, else 409), the caller may calculate (verified user or admin, else 403), and `args` validate against the schema (else 422). Cancel runs nothing and calls no model. Approve: the server calls `calculate` itself with the edited inputs, streams the result card, and the model continues the original task.
5. Answering a form is a continuation, not a new request, so it does not consume quota.

## 5. Security and isolation
- Every conversation row carries `userId`; Postgres RLS is enforced because the app connects as the non-owner role `et_app` (no BYPASSRLS) and every query runs in a transaction that sets `app.user_id` / `app.role` (`lib/db/queries.ts: scoped`). No principal => no rows. Admins may SELECT all chats but cannot modify them. `et_app` has no access to Session/Account/Verification. Identity, rate limit storage and admin jobs use a separate owner connection (`POSTGRES_URL_ADMIN`).
- All API handlers call `assertCan()` (`lib/authz.ts`); client-supplied IDs are verified for ownership.
- Secrets only in server env / secret store; `.env` git-ignored; `.env.example` committed.
- OpenJEV and NVIDIA receive only redacted text. OpenJEV is a third-party, community-funded service (not TypeSafe-affiliated); a Mock/LLM fallback keeps the product working if it is down or throttled.
- Guest anonymous accounts are rate-limited by IP and session; abusive IPs are blocked.

## 6. Testing strategy
Unit tests with the Mock LLM/Router; real HTTP tests against a running stack for authorization matrix and cross-user isolation; real MCP calls against the cloned servers; Playwright on the mock website for the widget; RLS tests directly in Postgres; PII recall measured on a labelled sample. Exactly one controlled live NVIDIA verification in Phase 5.

## 7. Behaviours mined from existing tests (to port as tests/skills)
From `chatbot/tests/*` and the MCP server's 17 tools:
1. **calc-with-approval:** find formula → read real schema → open form → wait for approval → execute → continue original goal.
2. **calc→catalog chain:** use approved result to narrow catalog search.
3. **prefill grounding:** values the user never stated are blanked; a stated number fills one input only.
4. **cancel is inert:** no model call, no execution.
5. **numeric-fact validation:** answers may not contain numbers absent from user/tool evidence.
6. **pending forms don't break follow-ups.**
7. **context compaction keeps exact facts** and whole tool-call pairs.
8. **tenant/visitor isolation** and no secrets in embed/loader.
9. **insight jobs:** scheduled, activity-gated, keep last good report.

## 8. Acceptance criteria (measurable)
- AC-1 Guest sending a 6th request in a day gets HTTP 429 with reset time; 3rd request within a minute gets 429.
- AC-2 User A cannot read/modify/delete user B's conversation, file, memory (HTTP 403/404 and direct SQL under RLS returns 0 rows).
- AC-3 Guest has no calculator, upload or long-term memory access (denied at API, not only hidden in UI).
- AC-4 Calculation never executes without approval; cancel leaves 0 calculator calls (asserted via MCP call log).
- AC-5 "Calculate focal length then pick a lens" produces plan → form → approved result → catalog search using that result → answer with tradeoffs.
- AC-6 Ambiguous query yields exactly one clarifying question and 0 tool calls.
- AC-7 No answer contains a currency amount for price questions.
- AC-8 Seeded PII (email, phone, card, name) never appears in OpenJEV/NVIDIA request bodies or logs; recall reported on a sample ≥ 50 items.
- AC-9 Embed works on the mock website with only origin + widget ID and does not alter host page styles.
- AC-10 Image and audio inputs reach the model and produce an answer.
- AC-11 `docker compose up` on a clean machine yields a healthy stack; one live NVIDIA call succeeds.
- AC-12 Non-admin receives 403 on every admin route.

## 9. Phases and risks
Phases 0–5 as agreed; each ends in a report and a stop. Risks: OpenJEV is community-funded and may throttle (fallback router); Nemotron may lack vision (second free NVIDIA model); NER-quality PII needs measurement; anonymous guests can be abused (IP limits plus Supabase captcha if needed).
