# STATUS — read this first in a new session

*Updated 2026-07-22, session 2 (in progress). Companion to `spec/credit-map-spec.md` (the governing spec, v1.1 top-down) and `CLAUDE.md`. Work tracker: `PLAN.md`.*

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

**Session 2 (2026-07-22) — all footed and committed:**
- **Aging (A)** — acquired+maturity on all 8,582 D1 rows: 53.7% bought <12mo, wavg 1.72y vs 70% maturities >10y (conveyor, not vault); PL youngest shelf (1.05y) and 30.1% of the new cohort; Q4-2025 surge $35.6B incl 12/22 $6.1B spike. Findings 44–46.
- **Concentration (B)** — description-column parser fix (quirk #10, regression-gated); top-10 issuer prefixes $22.7B = 14.3%; **10 of 12 largest are PL-rated 2025 vintages** (AP Grange $3.64B, AMAPS, AP Alkaios, Atlas, SVF II, Stonepeak); AP Grange anatomy verified vs raw (acquired 12/22/2025 at par, marked 106.2 nine days later, full-year coupon received — re-papering fingerprint). Findings 47–49.
- **Time series (C)** — YE2023+YE2024 statements through the same parser (era-2 quirks #11–14); gates: 2025 exact / 2024 +$1 logged / 2023 −$327K assigned residual. **THE RESULT: PL channel 3.4× in two years ($11.7B→$40.1B, 15.6%→25.3%); FE shrank $5.1B absolute in 2025 while book grew $27.9B; printed quality flat throughout. Cohort test run 1 (2023 PL→2025): mostly benign where testable ($2.2B up vs $0.3B down) with a violent tail (one 12-notch miss) and letters that never graduate.** YE2021/22 schedules not public — coverage boundary logged. Findings 50–53.
- **The engine (G)** — dashboard section ⑦: full float→ROE tree from 20 new banked 10-K claims. ROE-common 16.6% / ex-AOCI 13.2% / ADIP realized 12.2% / Apollo take $4.07B; 10bp losses ≈ −1pt ROE; provisioning 3–7bp on a 1.7y-old book. Finding 54.
- **Letter-slip stress (H)** — C-1 factors banked (Milliman 2021); slip 2/3 notches → 376%/337% CAL (bound) = NOT a solvency event, but below-IG share 2.9%→7.0–14.2% = junk-share/funding event; the slipped risk lives at AARe behind the mirror-check boundary. Run-stress: runnable ~$71B vs ~$11B natural liquidity (the ratchet). Findings 55–56, panel in ⑥.
- **Quarterly+annual engine workbook (I)** — `dossiers/athene/athene-quarterly-engine.xlsx`: Michael's stock-and-flow sheet live; Engine (4Q24–1Q26) + Engine-FY (FY2023–25) as exact row mirrors, 163 live checks; sources = 2 clean supplements + 10-K MD&A, cross-gated exact. **Finding 57: NIS 1.65%→1.34% in four quarters, SRE margin <1% first time; net flows 17.2→4.8→9.0B; runnable FA share 21%→27.2%.** 7 older supplements glyph-encoded (decoder parked).

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
