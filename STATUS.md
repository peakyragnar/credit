# STATUS — read this first in a new session

*Updated 2026-07-21, end of session 1. Companion to `spec/credit-map-spec.md` (the governing spec, v1.1 top-down) and `CLAUDE.md`.*

## Where the project stands

Phase 0 (Athene by hand) is deep into the asset drill — far ahead of the original week-3 plan. The Phase-0 gate ("can evidence chains beat an analyst?") is already demonstrably passed; formal dossier emit + runbook v1 freeze remain.

**Done, all footed and committed:**
- **Census/spine** — 65 entities, cocodes/FEINs/LEIs/BMA classes, ownership sandwich verified: AHL → Athene USA Corp (IA) → **AARe (Bermuda) = the pivot** → US fleet + ALRe/ALReI/AARe II. `spine/athene/entities.csv`, findings 1–17.
- **L0 control totals** — 100+ cited claims in `extract/athene/l0-claims.csv` (inflows $83.4B, reserves $271B net, ModCo $168.3B, capital/RBC/BSCR, fees $1.44B…).
- **L1 treaty decomposition** — 29 AAIA→AARe treaties, 8/8 gates (`extract/athene/treaties.csv`); Bermuda FCR: AARe BSCR 242%→202%, ALRe 453%→309%; mirror-check boundary quantified (AARe has no public unconsolidated SFS).
- **D1 line-level bonds** — 8,582 positions, BACV foots TO THE DOLLAR both sections (`sched_d_part1_lines.csv` + parser `tools/parse_sched_d.py`); PPN+no-ID private floor $49.3B = 31%; PL ratings $40.1B = 25.3%; verification lane ran (145/145 clean, 3 haiku scouts).
- **D2/D3** — BBB− cliff ($18.5B) is 76% publicly rated (exculpatory, recorded); PL yields +0.6–0.9pp vs FE at same notch (PL "A" prices like public BBB/BBB−) — central F1 question, deliberately unresolved.
- **Disposals (Parts 4+5)** — $72,140,293,824 consideration EXACT (P4 $45.4B + P5 round-trips $26.7B); 37% same-year flips (street→ACRA pipeline); **$9.21B related-party disposals, 889 named trades** incl Apollo Global Securities; RP gains +49bp vs +5bp third-party; **matched-pair test: clean where testable (6% coverage), 94% untestable by construction** — findings 39–43.
- **Net spread** — AAIA: NII $12.73B − FWH pass-through to AARe $3.42B − credited $3.68B − OTTI $0.16B ≈ **$5.5B**; GAAP cross-check $5.8B.

## The living surfaces
- **Dashboard** (artifact, stable URL): https://claude.ai/code/artifact/0dfa08f5-a1c0-49b7-b080-d578fdf98b39 — flow-structured ①→⑥ + ⑤b disposal machine. Regenerate: `python3 tools/render_athene_dashboard.py` then republish same path.
- **Teaching doc** (artifact): https://claude.ai/code/artifact/f52dd3e0-5ffe-43dc-857e-49e2e7aa81d0 — `docs/how-apollo-insurance-works.{md,html}` incl. glossary (Michael's reference; update glossary whenever new jargon appears).
- **Findings ledger**: `spine/athene/findings.md` (43 numbered findings). **Runbook**: `runbook/runbook.md` (8-stage pipeline spec + 8 parser quirks). **Exceptions**: `runbook/exceptions.md` (2 entries, incl. the $3.2M disposal-G/L OTHER residual).

## Standing method (hard-won, do not regress)
- Exact-equality footing gates; residuals ASSIGNED or logged as OTHER — never plugged. (The FV-masquerading-as-BACV bug was caught only by exactness.)
- Deterministic parsers for tabular schedules; cheap-model verification lanes on samples; main loop adjudicates. Parser quirks documented in runbook (PPN charset #@*, split cells, padding-phantom cells ×3, rollup codes…).
- Claims are bitemporal rows w/ sha256; views regenerated from CSVs, never hand-edited; both-readings discipline (benign+adverse) on every ambiguous finding.
- AAIA statement PDF (221MB) is local-only (`raw/…/aaia-statutory-4q2025.pdf`), refetch via manifest URL; sha in manifest.

## Queue (agreed order)

**→ Superseded by `PLAN.md` (living tracker, order re-agreed 2026-07-22): aging + concentration from the existing D1 extract first, then the time-series backfill, then Level 3 rollforward, then mortgages, then D4. The list below is the session-1 snapshot, kept for history.**
1. **Time series / period backfill** — YE2021→2024 annuals through existing parsers (structure-era mapping: pre-2025 Schedule D uses old categories, PBBD bridge documented). Unlocks: designation migration by rating source (THE PL discriminator), cliff history, vintage aging, source-mix drift, spread trend.
2. Matched-pair leftovers: 2 suspect "market" legs at exactly 100.000 in finding 43; mix-controlled RP test extensions.
3. Schedule B mortgage drill ($52.1B resi book, pp 495–2475). 4. D4 obligor resolution + BDC engine (reaches the 94% untestable RP flow). 5. Small: ACRA public disclosure hunt, ALRe $4.5B outflow trace, FA maturity ladder via XBRL, Bermuda permitted-practices table, dossier emit + runbook v1 freeze.

## Michael's working style (observed)
Finance background; wants plain-language teaching with every new term added to the glossary; visual learner — dashboard is the primary surface, everything must attach to the flow; insists on hard reconciliation ("don't plug; if exhausted, put into OTHER and log"); treat extraction as a reusable system (period/entity-agnostic), never one-offs; commercial frame = credit research/trading (spec §1), clean-is-a-valid-answer discipline matters to him.
