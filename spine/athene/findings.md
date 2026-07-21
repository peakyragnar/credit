# Census findings — Athene complex

Working notes from the entity-map build. Each item is a finding or an open verification, not a conclusion. Sources: FY2025 EX-21 exhibits (APO, AHL), AAIA YE2025 statutory statement Schedule Y (pages 148, 203–441), GLEIF API.

## Reconciliations run
1. **AHL EX-21 ⊆ APO EX-21: PASS.** All 45 entities in Athene Holding's FY2025 EX-21 appear verbatim in Apollo's FY2025 EX-21.
2. **Schedule Y ↔ EX-21 cross-check: PASS on the insurance core.** Every insurer/reinsurer in the EX-21 lists appears in Schedule Y Part 1A with consistent domiciles.

## Verified structural findings (cited to AAIA Schedule Y, YE2025)
3. **The ownership sandwich.** The chain is AHL (Bermuda) → Athene USA Corporation (Iowa) → **Athene Annuity Re Ltd. (Bermuda, FEIN 98-1408540)** → Athene Annuity and Life Company (61689, the entire US fleet) AND ALRe, ALReI, AARe II. A US holdco owns the Bermuda reinsurer that owns the US insurers. AARe is the structural pivot of the whole group — not ALRe as commonly assumed. (Part 1A: AAIA "RE" row shows Directly Controlled By = Athene Annuity Re Ltd., 100%; AARe row shows UDP = Athene USA Corporation.)
4. **AADE is gone, confirmed.** Not in either EX-21 and not in Schedule Y; AAIA (61689) is the reporting entity and lead insurer. Only AADE RML, LLC survives as a name trace.
5. **NAIC group 4734 "Apollo Global Mgmt Grp" is much bigger than Athene.** Same regulated group and same ultimate controlling persons (AGM; M. Rowan; L. Black) include: **Aspen** (43460 TX, 10717 ND), **Catalina runoff** (Alea North America 24899, SPARTA 20613, National American of CA 23671, ProBuilders 11671), **Venerable** (80942, + Corporate Solutions Life Re 68365, Rocky Range 16308; UCP shared with Crestview/RCP/others), **LifePoint** (Upper Peninsula Health Plan 52615). Part 1 explicitly names Aspen, Athene, Catalina, LifePoint, VA Capital as insurer-controlling portfolio companies.
6. **Athene ↔ Venerable economic link.** ALRe owns 13.000% of VA Capital Company LLC (Venerable's parent). Corporate Solutions Life Reinsurance Company (68365) is Venerable's, not Athene's.
7. **ACRA third-party split is visible.** ACRA 1A is only 33.000%-owned by ACRA Holding Ltd. — the remainder is third-party ADIP capital. ACRA Holding 2 Ltd. is 100% ALRe-owned (the gen-2 Athene side). ACRA 1A owns ACRA International (100%) and ACRA LP (99%).
8. **ALRe's other holdings:** Athene Asset L.P. (100%), A-A Onshore Fund LLC (99.37%), ADIP (Athene) Carry Plan.
9. **Cocodes captured:** AAIA 61689, AANY 68039, ALICNY 63932 (owned by AANY), SARC 15306 (99% AAIA), Athene Re USA IV 14179 (100% AAIA).

## Open items
- **BMA register/class confirmation** for ALRe, AARe, ALReI, AARe II, ACRA entities — the Class E declaration-of-compliance page listed no Athene entities on its first page (paginated or filed elsewhere?); classes should come from FCRs. Note: BMA does host AARe's audited GAAP FS.
- **ACRA 2A/2B parent stakes** — Schedule Y search with hyphen variants needed.
- **Athene Annuity Re II Ltd. purpose** — new; find its FCR/first filings.
- **Japan entities** — materiality unknown.
- **Part 2 inter-affiliate flows** (page 440) — large numbers visible (e.g., ~$10.3B AAIA-related), extraction deferred to L1.
- **Oversized-file policy:** AAIA statement (221MB) exceeds GitHub's 100MB limit — kept local-only, hash+URL in manifest. Decide: git-lfs vs manifest-refetch policy for large statutory PDFs.

## Phase 1 bonus (parked)
- BMA Class E declaration page lists Global Atlantic's entities: Ivy Re, Ivy Re II, Ivy Peak Co-Invest Re I/II, Global Atlantic Ivy Re III, GA Iris Re, Global Atlantic Assurance — a head start on the GA census.
