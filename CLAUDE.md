# CLAUDE.md — Credit Map repo

Read `spec/credit-map-spec.md` before doing anything; it is the spec. When in doubt, re-read it rather than improvising.

Standing rules (summary — the spec governs):

- **Top-down.** Control totals first (L0), decompose one level at a time (L1), line-level only where a hard question demands it (L2). Every level reconciles to the level above; residuals are findings (missed entity or opacity), logged, never hidden.
- **Data model.** Store claims, not truths; bitemporal (as-of + published + version); marks are observations by holders; economic ledger derived, never stored. Postgres only — no graph DB.
- **Footing gate.** Every extracted schedule foots to printed control totals or goes to the exception pile. No silent acceptance.
- **Phase 0.** Public documents only; no purchased data. No automation before run 2. No orchestration harness.
- **Discipline.** The machine outputs anomalies with evidence chains, never verdicts. No bubble narrative baked in — clean is a valid answer.
- **Stop points for Michael.** Entity-map review before L2 drilling; low-confidence resolution queue; exception queue; phase gate.
- **Flywheel.** Every exception resolved gets written back into `runbook/runbook.md` / `runbook/exceptions.md`.
- **EDGAR access.** Set `SEC_EDGAR_USER_AGENT` in `.env` (see `.env.example`); stay under 10 req/s. No key needed anywhere in Phase 0.
