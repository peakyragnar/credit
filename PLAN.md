# PLAN — living work tracker

*Order agreed with Michael 2026-07-22 (session 2). This is the tracker; STATUS.md is the session handoff; `spec/credit-map-spec.md` governs method. Update the checkbox + evidence line at each milestone — never delete rows, strike them.*

Status legend: `[ ]` not started · `[~]` in progress · `[x]` done (footed + on dashboard) · `[!]` blocked (see note)

## Working order

### A. `[x]` Aging + maturity ladder — from existing D1 extract, no new documents — DONE 2026-07-22
- BACV-weighted holding-age distribution from `acquired` column of `extract/athene/sched_d_part1_lines.csv` (8,582 positions).
- Splits: PL vs. publicly rated · private placement vs. public · rating band.
- Maturity ladder from `maturity` column (absorbs the old queue-#5 "FA maturity ladder" asset-side half).
- Tie-in: age of the *kept* book vs. the 37% same-year flips in the disposal machine.
- **Gate:** every bucket sums back to the footed D1 BACV total, exact.
- **Output:** dashboard panel + findings entries.

### B. `[x]` Coarse concentration panel — same snapshot — DONE 2026-07-22
- PBBD category mix (ICO / ABS / etc.) from the section codes already parsed.
- Top-obligor concentration via issuer-name normalization (no external data; grouping quality logged, unresolved names go to OTHER, never guessed).
- **Gate:** groups sum to footed total; normalization exceptions logged in `runbook/exceptions.md`.
- **Output:** dashboard panel.
- Explicitly NOT: true industry/sector mapping — that waits for F (D4 engine). Half-resolved sectors are worse than honest coarse buckets.

### C. `[x]` Time-series backfill — DONE 2026-07-22 for YE2023+YE2024 (YE2021/22 = logged coverage boundary)
- Documents: YE2023 (106MB) + YE2024 (158MB) full statements fetched from ir.athene.com (manifest + sha256, local-only). **YE2021/YE2022: only the 40-page core+notes part is public ("2-5" of 5); Wayback empty — coverage boundary, logged in manifest + finding 50.** Revisit doors: state DOI records requests, NAIC data (paid — Phase 1 decision).
- Parser: year-parameterized (`parse_sched_d.py <year>`); era-2 quirks #11–#14 in runbook; 2025 regression byte-identical.
- Gates: 2025 exact · 2024 +$1 logged · 2023 −$326,724 assigned residual (4.3 ppm, written-off tail, exceptions ledger).
- Outputs: `sched_d_part1_lines_2023/2024.csv`, `d1_trends.csv` (footed), trends panel on dashboard, findings 50–53 incl. the channel-shift result and cohort-test run 1.
- Remaining sub-items → parked list: 2024 cohort run + FE control group; exited-PL cross-ref vs Part 4 buyers; designation-source trend for 2024 partial-year cohort.
1. Document hunt first: public sources only (state DOI portals, company disclosures). Partial coverage is acceptable and logged; no purchased data.
2. Structure-era mapping: pre-2025 Schedule D categories → PBBD bridge (documented in runbook before parsing).
3. Re-run existing parsers per year; every year passes the same footing gates as 4Q2025.
4. Dashboard: trend panels on the flow view (each key number becomes a path), plus optional year switcher.
- **Unlocks:** designation migration by rating source (THE private-letter discriminator), BBB− cliff history, vintage/cohort survival, source-mix drift, spread trend.
- **Gate per year:** schedules foot to that year's printed control totals or go to the exception pile.

### G. `[x]` The engine panel — ROE/ROIC driver tree — DONE 2026-07-22
- Full float→ROE waterfall from banked claims (20 new L0 claims, cross-foots exact); dashboard section ⑦.
- ROE-common 16.6% / ex-AOCI 13.2% / total 13.7% / ADIP realized 12.2% / Apollo take $4.07B; 10bp-losses ≈ −1pt ROE sensitivity.
- **Gate:** every line traces to a banked claim; income/equity/expense cross-foots exact. Finding 54.

### H. `[x]` Letter-slip stress — DONE 2026-07-22 (capital-at-risk instrument; absorbed old D/Level-3 item)
- Re-grade the $40.1B PL book at yield-implied ratings (2–3 notch slip per D3); recompute RBC C-1 charges (public NAIC factors) → impact on AAIA CAL ratio and Bermuda BSCR trend.
- Companion: run-stress arithmetic (runnable 26.3% of liabilities vs $1.7B <1y asset maturities + 31% identifier-private book).
- Level 3 rollforward from 10-K folds in here as the GAAP-ruler cross-check.

### D. `[→H]` Level 3 rollforward — absorbed into H (letter-slip stress)
- FV hierarchy totals + Level 3 rollforward (transfers in/out, purchases, gains) by year.
- Framing: Level 3 = holder-marked assets — the opacity question on the GAAP ruler, cross-check to the 31% identifier-private floor.
- Glossary: add Level 1 / Level 2 / Level 3 in plain language.
- **Output:** dashboard context panel + teaching-doc section.

### E. `[ ]` Schedule B mortgage drill — $52.1B resi book (AAIA pp. 495–2475)

### F. `[ ]` D4 obligor resolution + BDC engine
- Reaches the untestable 94% of related-party flow; upgrades B's coarse buckets to true industry/sector + concentration.

### I. `[x]` Quarterly engine workbook — DONE 2026-07-22 (Michael's stock-and-flow sheet, live)
- 9 supplements fetched (manifest+sha); 2 clean docs parsed (`tools/parse_fin_supplement.py`, 384 cells, all cross-foot + overlap gates); 7 older docs glyph-encoded → decoder parked.
- `dossiers/athene/athene-quarterly-engine.xlsx`: 4 sheets, 77 live identity checks, formulas recalc in Excel; 2Q26 column ready. Finding 57 (spread compression + flow deceleration, quarterly).

## PHASE 1 — GLOBAL ATLANTIC (goal set 2026-07-22: full Athene-parity process + comparison artifact)
### GA-1 `[~]` Document hunt — census sources, statutory statements, KKR filings, Bermuda FCR
### GA-2 `[ ]` Census/spine — entities, cocodes, LEIs, Bermuda classes (BMA head start in findings: Ivy Re I/II/III, Ivy Peak I/II, GA Iris Re, Global Atlantic Assurance)
### GA-3 `[ ]` L0 control totals — banked claims from primary docs
### GA-4 `[ ]` Statutory bond drill — Schedule D through the parameterized parsers (if statements public), aging/concentration/source trends
### GA-5 `[ ]` Quarterly + annual engine — KKR insurance-segment series 2023–2026, gated
### GA-6 `[ ]` GA surfaces — dashboard artifact + engine workbook, verified
### GA-7 `[ ]` THE COMPARISON — Athene vs Global Atlantic HTML artifact: 3 years quarterly + annual + all 2026 reported; same footed metrics side by side

## New ideas (Michael, 2026-07-22 — parked, not yet scoped)
- `[ ]` **Funding-map queries**: "which businesses does Athene/Apollo finance?" — issuer names now on 100% of D1 rows makes this queryable (the whale shelf was the first output); scope a proper query surface after D4 resolution.
- `[ ]` **Peer normalization layer**: same footed metrics (PL share, private floor, aging, concentration, ROE tree, capital trends) computed identically across PE-insurance peers — KKR/Global Atlantic (already Phase 1), Brookfield/AEL, Ares/Aspida, Blue Owl — so quality is comparable, not narrative. This is the Phase-1+ payoff of the parameterized parsers.

## Parked small items (pull in opportunistically)
- `[ ]` Supplement glyph decoder — recover 1Q24–3Q24 quarterly columns from the encoded-font supplements (CID subsets are monotonic; letters crack via known labels, digits pin via overlap quarters); extends the workbook left.
- `[ ]` Schedule D Part 3 (acquisitions) parse — vendor column separates street purchases from affiliate transfers; discriminator for the Q4-2025 surge (finding 46). Now cheap: parser is year-parameterized and Part 3 pages are bookmarked in all three PDFs.
- `[ ]` Cohort test run 2: 2024 PL cohort + FE control group; cross-ref exited-PL CUSIPs against Part 4/5 disposal buyers (did the bad letters exit via affiliates?).
- `[ ]` YE2021/22 schedule hunt, other doors: state insurance department records requests; check AADE (Delaware) statements for the same era as a proxy lane.
- `[ ]` Matched-pair leftovers: 2 suspect "market" legs at exactly 100.000 (finding 43); mix-controlled RP test extensions.
- `[ ]` ACRA public disclosure hunt.
- `[ ]` ALRe $4.5B outflow trace.
- `[ ]` Funding-agreement (liability-side) maturity ladder via XBRL.
- `[ ]` Bermuda permitted-practices table.
- `[ ]` Dossier emit + runbook v1 freeze (Phase-0 formal close).

### J. `[x]` The Read — the verdict layer — DONE 2026-07-22
- Michael's call: conclusions weren't apparent in the artifacts; the sheet wasn't driving the argument. New conclusions-first HTML surface (`tools/render_the_read.py` → `dossiers/athene/the-read.html`, stable artifact URL in STATUS): verdict, hypothesis scoreboard w/ badges, margin-cycle sparklines, seasoning clock (only 17.5% of book old enough to be informative), structural drift, 12 tripwires w/ trip levels, 3 alpha paths, falsifiers both directions. Every number from the footed extracts; regenerates after any re-run. Excel workbook remains the recalculating model; The Read is the reading layer.

## Evidence log
*(append: date · item · what moved · commit)*
- 2026-07-22 · J · The Read rendered + published (new stable artifact); dashboard header now links to it; STATUS points START HERE.
- 2026-07-22 · I-v2 · four new mirrored sections (statutory features / mgmt NIA+quality / GAAP income-to-common / equity+ROE): parsers extended (788 suppl. cells + 99 annual cells, all gated), 316 live checks · finding 58 (1Q26 net loss −$1,973M common; equity −13% in Q; provisions −67% while book +75%).
- 2026-07-22 · I-annual · `parse_10k_annual_tables.py` (66 cells FY2023–25, gates incl. quarters-vs-10-K cross-source exact) · Engine-FY sheet added (annual columns + live Σ-quarters audit column); 97 total live checks.
- 2026-07-22 · I · 9 supplements fetched+hashed · parser w/ exact gates (2 clean docs, 384 cells, overlaps identical) · quarterly engine workbook (77 live checks, python-verified identities) · finding 57 · glossary +2.
- 2026-07-22 · H · C-1 factors banked (Milliman 11/2021, sha) · `compute_letter_slip.py` (PL gate exact) → slip 2/3 = 376%/337% CAL bound, below-IG 7.0%/14.2% · run-stress $71B vs $11B + ratchet · dashboard panel in ⑥ · findings 55–56.
- 2026-07-22 · G · 20 new L0 claims from 10-K (income/equity/expense stacks, cross-foots exact) · dashboard section ⑦ (engine waterfall + 6 return cards + levers callout) · glossary +3 (ROE/hurdle, AOCI, NCI realized return) · finding 54.
- 2026-07-22 · C · doc hunt (4 fetched, 2 full + 2 partial-only, manifest+sha) · parser year-parameterized, era-2 quirks #11–14, 2025 regression byte-identical · gates 2025 exact / 2024 +$1 / 2023 −$327K assigned · `d1_trends.csv` footed · THE RESULT: PL 3.4× in 2yrs to 25.3%, FE −$5.1B absolute in 2025, quality prints flat; cohort run 1 mostly benign w/ violent tail (12-notch miss) · findings 50–53 · trends panel on dashboard.
- 2026-07-22 · B · description-column fix in `parse_sched_d.py` (quirk #10; reparse gated byte-identical by `tools/check_d1_reparse.py`, names now on 100% of rows) → `tools/compute_d1_concentration.py` → `extract/athene/d1_concentration.csv` (foots exactly) · findings 47–49 (whale shelf: top-10 = $22.7B, 10/12 PL + 2025 vintage; AP Grange anatomy verified vs raw p.5903) · dashboard concentration panel in ⑤ · glossary +1 (CUSIP6) · repo venv `.venv` with pypdf for parser runs.
- 2026-07-22 · A · `tools/compute_d1_aging.py` → `extract/athene/d1_aging.csv` (6 tables + wavg, all foot to $158,852,395,199 exactly; f38 cross-check reproduced to the dollar) · findings 44–46 · dashboard aging panel in ⑤ · glossary +2 terms · exception logged (11271L-10-2 no-date/matured-2020) · runbook quirk #9. Follow-up spawned: Part 3 vendor parse (street vs affiliate on the Q4 surge) → parked list.
