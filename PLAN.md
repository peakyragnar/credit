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

### C. `[ ]` Time-series backfill YE2021→2024 — the main event
1. Document hunt first: public sources only (state DOI portals, company disclosures). Partial coverage is acceptable and logged; no purchased data.
2. Structure-era mapping: pre-2025 Schedule D categories → PBBD bridge (documented in runbook before parsing).
3. Re-run existing parsers per year; every year passes the same footing gates as 4Q2025.
4. Dashboard: trend panels on the flow view (each key number becomes a path), plus optional year switcher.
- **Unlocks:** designation migration by rating source (THE private-letter discriminator), BBB− cliff history, vintage/cohort survival, source-mix drift, spread trend.
- **Gate per year:** schedules foot to that year's printed control totals or go to the exception pile.

### D. `[ ]` Level 3 rollforward — bounded side-extraction from AHL 10-K (already local)
- FV hierarchy totals + Level 3 rollforward (transfers in/out, purchases, gains) by year.
- Framing: Level 3 = holder-marked assets — the opacity question on the GAAP ruler, cross-check to the 31% identifier-private floor.
- Glossary: add Level 1 / Level 2 / Level 3 in plain language.
- **Output:** dashboard context panel + teaching-doc section.

### E. `[ ]` Schedule B mortgage drill — $52.1B resi book (AAIA pp. 495–2475)

### F. `[ ]` D4 obligor resolution + BDC engine
- Reaches the untestable 94% of related-party flow; upgrades B's coarse buckets to true industry/sector + concentration.

## Parked small items (pull in opportunistically)
- `[ ]` Schedule D Part 3 (acquisitions) parse — vendor column separates street purchases from affiliate transfers; discriminator for the Q4-2025 surge (finding 46).
- `[ ]` Matched-pair leftovers: 2 suspect "market" legs at exactly 100.000 (finding 43); mix-controlled RP test extensions.
- `[ ]` ACRA public disclosure hunt.
- `[ ]` ALRe $4.5B outflow trace.
- `[ ]` Funding-agreement (liability-side) maturity ladder via XBRL.
- `[ ]` Bermuda permitted-practices table.
- `[ ]` Dossier emit + runbook v1 freeze (Phase-0 formal close).

## Evidence log
*(append: date · item · what moved · commit)*
- 2026-07-22 · B · description-column fix in `parse_sched_d.py` (quirk #10; reparse gated byte-identical by `tools/check_d1_reparse.py`, names now on 100% of rows) → `tools/compute_d1_concentration.py` → `extract/athene/d1_concentration.csv` (foots exactly) · findings 47–49 (whale shelf: top-10 = $22.7B, 10/12 PL + 2025 vintage; AP Grange anatomy verified vs raw p.5903) · dashboard concentration panel in ⑤ · glossary +1 (CUSIP6) · repo venv `.venv` with pypdf for parser runs.
- 2026-07-22 · A · `tools/compute_d1_aging.py` → `extract/athene/d1_aging.csv` (6 tables + wavg, all foot to $158,852,395,199 exactly; f38 cross-check reproduced to the dollar) · findings 44–46 · dashboard aging panel in ⑤ · glossary +2 terms · exception logged (11271L-10-2 no-date/matured-2020) · runbook quirk #9. Follow-up spawned: Part 3 vendor parse (street vs affiliate on the Q4 surge) → parked list.
