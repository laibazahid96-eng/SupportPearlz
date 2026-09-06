# From Prototype to Production

## Service
Expose authenticated `/health` and `/chat` endpoints behind a FastAPI service. Store per-session state in a shared store, enforce request timeouts, and protect vector-store access with concurrency-safe clients.

## Knowledge lifecycle
Every source receives an owner, version and last-updated timestamp. A content change triggers validation, source-level delete/upsert, cache invalidation and the regression suite. A failed ingestion is rolled back to the previous known-good index. Target staleness window: one hour for policy changes.

## Guardrails
Auto-send only high-confidence, low-risk factual answers. Draft for human review when confidence is partial or when money, legal commitments, safety, or ambiguity is involved. Never let generated text directly execute refunds, credits, discounts, bookings, or other side effects. Redact unnecessary PII before model calls and logs.

## Observability
Log latency, retrieval scores, tokens, model/version, refusal, escalation and customer follow-up. Run regression evaluation on every prompt, model, or index change. Release should be blocked if groundedness or citation accuracy falls below the agreed bar.

## Cost and scale
At 700 questions/day, use caching for repeated questions and a smaller model for routine generation where evaluation shows no quality loss. Track embedding and generation cost separately. Define p50/p95 latency targets and a provider-outage fallback, such as a second provider or human-only support mode.

## Accountability
Support Operations owns policy correctness; Engineering owns system reliability; Knowledge owners approve document changes; Compliance reviews high-risk automated claims. The assistant is an evidence retrieval system, not an authority to invent commercial policy.
