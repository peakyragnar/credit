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

## Capital-cushion findings (from AARe FS Note "Statutory Requirements", 2026-07-21)
10. **AADE merger confirmed with date**: AADE merged into AAIA on **October 11, 2025** (related-parties note). Census hypothesis #2 closed.
11. **BMA classes confirmed**: AARe and ALRe are **Class E**; ACRA 1A and ACRA 2A are **Class C**. Census open item closed (register lookup no longer needed for these four).
12. **AAIA max dividend without Iowa approval: $0** (both 2025 and 2024) — the lead US insurer has no ordinary dividend capacity; all upstreaming needs regulatory sign-off.
13. **Vermont captive solvent only via permitted practice**: Athene Re USA IV counts $76M face amount of letters of credit as admitted assets; the note states that without this practice it "would not have exceeded authorized control level RBC." A US onshore shadow-insurance structure, disclosed in plain text.
14. **ALRe capital down $3.9B in a year** ($17.6B → $13.7B) while earning +$0.6B — implies ~$4.5B of distributions/other movements out of ALRe. Trace at L1.
15. **Bermuda CIT revoked January 2026** (per the note): AARe to record a full valuation allowance in Q1 2026 — capital effects AARe $(847)M, ACRA 1A +$164M, ACRA 2A $(45)M. The Bermuda tax regime is moving under the structure in real time.
16. **Intercompany liquidity web**: revolving notes — AHL owes ALRe $2.22B (2.29% fixed), AUSA owes ALRe $417M; AARe can borrow $1B from AUSA ($19M drawn). Below-market related-party lending; map at L1.
17. **Bermuda permitted practices boost capital**: p.64 shows increases to capital & surplus "due to permitted practices" of $1,982M / $808M / $2,655M / $2,655M / $54M (column mapping to entities not yet pinned — extract the full table at L1).

## L1 findings (treaty decomposition + FCR, 2026-07-21)
18. **Treaty table footed 8/8.** All 29 AAIA→AARe Schedule S rows encode to `extract/athene/treaties.csv`; premiums, ModCo, reserve credit, and funds withheld each sum exactly to the printed section totals (18,265,046,901 / 110,346,917,726 / 65,263,421,108 / 65,543,636,517 / 52,198,633,311 …). The offshore door is now decomposed with zero residual.
19. **Bermuda cushion compressing fast** (FCR §8b, April 2026): AARe BSCR **242% → 202%** (ECR required capital $11.9B → $15.2B, +27%); ALRe BSCR **453% → 309%**. Still above the 120%-of-ECR target level, but the one-year trend is steep — required capital is growing much faster than eligible capital.
20. **Three capital measures diverge at AARe**: GAAP $42.9B vs Bermuda statutory (SFS) $23.7B vs EBS eligible $30.6B. Mapping the prudential filters/permitted practices between them is an L2 item.
21. **ACRA is NOT in the Bermuda sub-group FCR** — the FCR covers only AARe + ALRe + ALReI. The sidecars (with the ADIP third-party capital) file separately; their FCR/disclosure needs its own hunt. Opacity note: the group's own public Bermuda narrative excludes the third-party-capital vehicles.
22. **ALReI is the Class C in the sub-group** (tiny: £65M eligible capital, GBP-denominated) — distinct from ACRA 1A/2A's Class C designation in the AARe GAAP note.
23. **Mirror-check status: PARTIAL.** AARe publishes no unconsolidated statutory FS (only consolidated GAAP, which eliminates the AAIA intercompany). The FCR's EBS view confirms the Bermuda side at aggregate level, and ALRe's unconsolidated stat FS ($29.0B gross reserves assumed) evidences the retro layer — but a line-item AAIA-ceded ↔ AARe-assumed reconciliation is not possible from public documents. **This measured gap IS the opacity finding Gober described; it's now quantified and logged, not papered over.**

## Asset-side findings (⑤ decomposed, 2026-07-21)
24. **Composition foots exactly.** Summary Investment Schedule: issuer credit obligations $85.39B + ABS $73.46B = bonds $158,852,395,199 to the dollar; all 12 categories sum to total invested assets $282,171,785,028. Mortgage split (resi $52.10B + comm $33.64B + mezz $1.00B − allowance $0.107B) reconciles through Schedule B Verification with one $1 printed-rounding exception (logged in runbook/exceptions.md).
25. **The "bonds" are ~46% asset-backed securities.** $73.5B of the $158.9B is ABS ($58.7B financial self-liquidating, $10.1B financial non-self-liquidating, $4.7B non-financial). Plain corporates are only $40.9B (26%). Another ~$26B of the issuer-credit bucket is structured-adjacent: bonds issued by funds ($11.8B), single-entity-backed ($8.7B), project finance ($5.6B). The portfolio is predominantly structured/private credit, not traditional bonds.
26. **The mortgage book is majority residential**: $52.1B resi vs $33.6B commercial — contrary to the CRE-heavy assumption. Whole-loan resi at this scale is its own concentration question (origination channel? MidCap/third-party? L2).
27. **PBBD verdict (Q1 answered for AAIA): the +21% bond growth is REAL, not reclassification.** Note 2 discloses the full adoption impact: only $1,648.5M (GA) + $229.0M (SA) reclassified OUT of Schedule D into BA at 1/1/2025; measurement-basis surplus impact "not material." Adjusting for it, apples-to-apples bond growth is ~+22.8% — the reclass slightly *understates* reported growth. The canonical false signal is absent here; the growth is genuine origination.
28. **Turnover is enormous**: $97.5B of bonds acquired and $71.6B disposed in one year against a $131B starting book (~55% disposal rate); mortgages $38.4B acquired / $12.7B disposed. This is an actively traded/originated book, not buy-and-hold — vintage-aging analysis must account for churn.
29. **Schedule BA is small at AAIA ($17.5B, 6.2%)** — the fund-stakes/opacity bucket is modest at the lead entity (grew from $11.6B, +50% yoy though). The look-through problem concentrates in ABS structure, not BA funds, at this entity.
30. **Error correction disclosed**: $64.0M understatement of aggregate life reserves discovered during 2025 (Note 2). Small vs $110.6B, but a data point on controls.
31. **FA maturity ladder: not extractable from the AHL 10-K text** (tables render poorly / live in XBRL). Open item — source it from the ISCL note tables or XBRL at L2. Logged, not estimated.

## The asset drill — standing spec (agreed 2026-07-21)

The structure buckets (Summary Investment Schedule) are NOT a public/private split; private credit cuts across corporates, both ABS buckets, bank loans, mortgages, and BA. Only the ~$15.8B of government paper is clearly public. The drill therefore proceeds by *classifying lines along the market-status axis*, in levels:

- **D1 — line classification (~$243B, Schedule D Part 1 + B + BA line level):** tag every position by identifier type (CUSIP vs PPN vs none), private-placement/registration flags, and rating source (SVO vs filing-exempt vs private letter rating). Output: the honest private-credit share, per entity — currently only boundable, not known.
- **D2 — quality and its source:** NAIC designation mix; PLR share (the NAIC found private ratings inflated up to 6 notches); affiliated-originator share (Apollo/MidCap/Atlas-originated paper identifiable by issuer name patterns + related-party flags).
- **D3 — yield vs risk:** cross the classification against Schedule D yield/income columns — is the book earning private-credit spreads or IG spreads on opinion-marked paper? (F1 core.)
- **D4 — obligor resolution:** map line items to actual borrowers (the resolution registry); intersect with BDC/CLO holdings for cross-holder mark dispersion. (F2 core; the moat.)
- **Residential mortgage sub-drill:** $52.1B of resi whole loans — origination channel, geography, credit box (Schedule B detail + trends).

Rule carried from the composition work: every level foots to the level above; market-status proportions are never estimated, only measured.


## D2/D3 first results (2026-07-21, all from footed line data)

32. **The BBB− cliff is NOT propped by private letters — mostly.** Of the $18.5B at 2.C (BBB−, last notch above junk): **76.0% carries public agency ratings (FE)**; PL is only $1.4B (7.4%), self-assigned Z/YE $1.8B (9.5%). The "private letters at the IG boundary" story is largely absent at AAIA. Clean is a valid answer; recorded as such.
33. **Where PL actually lives: the middle of the book.** The $40.1B PL book clusters at A ($11.8B), BBB+ ($11.4B), A− ($4.2B), BBB ($5.2B) — 81% between A and BBB. Not cliff-adjacent, but capital-relevant (designation sets the RBC charge) and quality-relevant at scale.
34. **PL paper yields ~0.6–0.9pp MORE than FE paper at the SAME notch** (recent vintages 2024–25, BACV-weighted effective yields): A: 6.08% vs 5.39%; A−: 6.11% vs 5.39%; BBB+: 6.06% vs 5.44%; BBB: 6.73% vs 5.79%. Benchmark: PL-rated "A" paper (6.08%) yields between public BBB (5.79%) and public BBB− (6.36%) — i.e., **the market prices PL "A" paper roughly like public BBB/BBB−, 2–3 notches below its letter** — the same magnitude as the NAIC's private-ratings inflation finding.
35. **Two readings, deliberately unresolved:** (a) benign — an illiquidity/complexity premium on private placements at identical true quality (the industry's own pitch); (b) adverse — yield-implied ratings say the letters are generous. Yield alone cannot discriminate. The discriminators are downstream: impairment/migration outcomes by rating source (needs period backfill) and cross-holder marks (D4). Logged as the central open question of F1.
36. Caveats on 34: effective-rate and symbol columns are ungated (verification lane pending); sector mix differs between FE and PL books (PL skews corporate/infrastructure privates); vintage controlled only to 2024–25 acquisition years.
37. **Verification lane run 1: 145/145 clean.** Three independent cheap-model verifiers re-extracted a stratified sample (all whales ≥$400M + PL + no-description + random) from raw text: zero parser errors; all flags were fixture artifacts (multi-lot CUSIPs, the no-ID placeholder). The D2/D3 columns (designation, symbol, rates) are now sample-verified, not just money-gated.
38. **No-identifier bonds: 481 rows, $9.9B** (placeholder 000000-00-0) — private by construction. Identifier-based private-placement floor rises to **$49.3B = 31.0% of the bond book** (PPN $39.4B + no-ID $9.9B); still a floor.
39. **Disposal machine fully decomposed, footed to the dollar on money.** FY2025 disposals $72,140,293,824 = Part 4 detail $45.4B + Part 5 same-year round-trips $26.7B — consideration reconciles EXACTLY; combined total G/L $77.2M vs printed $73.9M (+$3.2M residual = dropped sparse adjustment rows + category-101 cluster, logged in exceptions as unresolved-other per protocol); OTTI closure within $0.6M.
40. **37% of the year's disposals were same-year round-trips** ($26.7B bought AND sold within 2025) — Part 5. The dominant pattern on its face pages: buy Treasuries from dealers (Deutsche, Citi, Wells), sell weeks later to ACRA sidecar accounts — the street→sidecar funding pipeline.
41. **Related-party disposals: $9.21B across 889 named trades** — buyers: AARE Surplus ($2.29B), ACRA RE 2B ($1.51B), ACRA RE 2A ($0.94B), ALRe accounts, AARE II, "ALRe Modco - VIAC GA" (the Venerable block!), and Apollo Global Securities LLC ($0.40B — Apollo's own broker-dealer as counterparty).
42. **Gains realized on related-party sales run ~10× richer: +49bp of consideration vs +5bp on third-party sales** ($45.2M on $9.2B vs $32.0M on $62.9B). Two readings, deliberately unresolved: (benign) different asset mix — affiliates get seeded with seasoned/appreciated paper; (adverse) gains preferentially realized through affiliate transactions where price isn't market-tested — textbook F2 transfer-pricing surface. Discriminator: mix-controlled comparison (same CUSIP sold to both related and third parties in the period) — computable from this data. Queued.

## Phase 1 bonus (parked)
- BMA Class E declaration page lists Global Atlantic's entities: Ivy Re, Ivy Re II, Ivy Peak Co-Invest Re I/II, Global Atlantic Ivy Re III, GA Iris Re, Global Atlantic Assurance — a head start on the GA census.
