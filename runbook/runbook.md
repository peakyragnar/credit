# Runbook — the extraction system

**Status: v0.5** — the system design, written from the first supervised execution (Athene, YE2025, 2026-07-21). Every stage below was run by hand at least once; automation lands per spec §8.8 (generalize at run 2, industrialize at Phase 2). This document is the spec for that automation: **extraction is a system parameterized by (group, entity, period, document) — never a one-off.** Optimization order: **accuracy > cost > speed.**

## The pipeline (per document)

```
ACQUIRE → HASH → LOCATE → PARSE → GATE → VERIFY → CLAIMS → RENDER
```

| Stage | What | Tooling tier | Accuracy mechanism |
|---|---|---|---|
| **1. Acquire** | Fetch the document from its canonical source (EDGAR w/ UA header; IR pages; BMA/athene.bm). URL recorded. | code | manifest row created before anything else; gaps logged with reason, never skipped silently |
| **2. Hash** | sha256 immediately; row in `acquisition/manifest.csv` (group, entity, doc_type, period, url, published, fetched, sha, status) | code | every downstream claim carries this sha — the evidence chain root |
| **3. Locate** | Find target schedules inside the document (PDF outline/bookmarks first — statutory statements are reliably bookmarked; text search fallback) | code | page numbers recorded so extraction is re-runnable and citable |
| **4. Parse** | Extract the schedule's rows/cells. Deterministic code (pypdf text + structure-aware parsing). LLMs are NOT the primary extractor for tabular schedules. | **code** | deterministic = reproducible; parser version noted with output |
| **5. Gate** | Foot everything against the statement's own printed control totals (9999999 rows, verification schedules, statement-face lines). Exact equality by default; ≤$2 tolerance ONLY for printed-rounding, and every use logged in `exceptions.md`. | code | **the iron rule (spec §4.3): unfooted = exception pile, never accepted** |
| **6. Verify** | Second decorrelated lens: cheap model (haiku/sonnet tier) re-extracts a sample (2–5%) + every hard/ambiguous row; disagreement → exception queue. Third lens where available: NAIC aggregates, the mirror entity's own filings. | cheap LLM | decorrelation; sampling rate escalates on any section that fails gates |
| **7. Claims** | Every accepted number becomes a row in `extract/<group>/…claims.csv`: metric, value, unit, basis (GAAP/SAP/EBS/mgmt), entity_scope, **as_of, published** (bitemporal), source_doc, source_location, sha256. Store claims, not truths. | code + main loop | adjudication of exceptions is main-loop (frontier) only; judgment never delegated |
| **8. Render** | Dossier/dashboard views generated FROM the claims files by script (`tools/render_*.py`) — views are derived, never hand-maintained. | code | regenerating a view can never change a number |

## Period-independence rules (why this works for every period)

1. **Claims are bitemporal**: every row carries `as_of` + `published`. Loading YE2023 next to YE2025 is additive — no schema change, no overwrites. "What was knowable on date T" stays answerable.
2. **Parsers are keyed to schedule structure, not to a year** — with a **structure-era table**: statutory Schedule D pre-2025 (old categories) vs 2025+ (PBBD: issuer-credit / ABS split). Cross-era comparisons route through documented mappings (first instance: the PBBD bridge, Note 2 disclosure + D-verification restated line 1).
3. **Documents per (entity, period) are enumerable** from stable sources (EDGAR indexes, IR archive pages, BMA/athene.bm) — the acquisition stage is a function, not a hunt.
4. **Backfill = the same pipeline over more (period) values.** Periods are independent worker runs, same as groups. Order: annuals back to ~2020 first; quarterlies only where a signal warrants.

## Cost/speed/accuracy dials (agreed 2026-07-21)

- Volume extraction on structured schedules: **code, ~zero marginal cost** — never spend model tokens reading table rows that parse deterministically.
- Model spend concentrates where models add value: verification sampling, ambiguous-row classification, name/obligor resolution, exception adjudication.
- Sampling rate is adaptive: baseline 2–5%; any gate failure raises the rate on that section, not globally.
- Frontier (main loop) reviews: all exceptions, all judgment calls, all coalescence. Cheap tiers never write conclusions.
- Parallelism comes from **independence** (per-document, per-period, per-group runs), never shared-state coordination (spec §8.1).

## Proven instances (the by-hand run this system generalizes)

- EX-21 exhibits (HTML parse + cross-reconciliation): APO/AHL FY2025 — 45/45 subset check.
- Statutory statement face + Schedule S (AAIA YE2025): 29-treaty decomposition, 8/8 footing gates.
- Summary Investment Schedule + D/B/BA verifications (AAIA YE2025): composition + 3 bridges, 7 checks, one $1 printed-rounding exception (logged).
- Schedule Y Part 1A (AAIA YE2025): ownership chain + cocodes.
- Bermuda FCR + AARe GAAP FS: EBS/BSCR capital table; per-entity capital & surplus.
- GLEIF API: LEI enrichment.

## Not yet built (queued, in order)

- **D1 line-level parser** (Schedule D Part 1 / B / BA at position level) — first industrial run of stages 4–7; defines the classification schema (identifier type, private flags, rating source).
- Verification lane wiring (cheap-model sampled re-extraction against parser output).
- Period backfill driver (same pipeline, list of periods).
- XBRL extraction for GAAP tables that render poorly as text (first target: funding-agreement maturity ladder).

## Standing exceptions & resolutions

See `exceptions.md`. Every exception resolved in any run gets generalized into a rule here — later runs inherit the scar tissue.
