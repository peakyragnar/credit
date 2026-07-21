# Census findings — Athene complex (in progress)

Working notes from the entity-map build. Each item is a finding or an open verification, not a conclusion.

## Reconciliations run
1. **AHL EX-21 ⊆ APO EX-21: PASS.** All 45 entities in Athene Holding's FY2025 EX-21 appear verbatim in Apollo's FY2025 EX-21. The two source lists agree.

## Findings to verify
2. **AADE absent.** Athene Annuity & Life Assurance Company (Delaware) — historically one of the main US insurers — does not appear in either FY2025 EX-21. Only `AADE RML, LLC` survives as a name trace. Hypothesis: merged into Athene Annuity and Life Company (AAIA). Verify in 10-K text / Iowa DOI / Schedule Y before treating AAIA as the sole lead entity.
3. **Athene Annuity Re II Ltd. (Bermuda)** — not in the prior working sketch. New reinsurer. Verify BMA class and purpose (FCR should exist if Class C/D/E).
4. **Two NY insurers**: Athene Annuity & Life Assurance Company of New York AND Athene Life Insurance Company of New York. Verify the second's status (active book vs shell).
5. **Structured Annuity Reinsurance Company (Iowa)** and **Athene Re USA IV, Inc. (Vermont)** — onshore reinsurers/captives; verify roles. Vermont = limited public disclosure; feeds the opacity ratio if reserves sit there.
6. **ACRA family fuller than sketched**: Holding + 1A + 1B + International + LP (DE) + Holding 2 + 2A + 2B + ADIP Carry Plan. Sidecar structure has at least two generations with A/B splits — treaty mapping at L1 must keep these distinct.
7. **Japan entities** (Athene Japan K.K., Athene Re Japan Solutions) — new jurisdiction not in the sketch. Verify whether reserves are material.

## Census gaps (next steps)
- **Schedule Y** (statutory, Iowa DOI): the regulated-group org chart + NAIC cocodes. Not yet fetched.
- **BMA register**: confirm registration + class for each Bermuda reinsurer. Not yet fetched.
- **Identifiers**: NAIC cocodes, LEIs (GLEIF), BMA registrations — all columns currently empty in `entities.csv`.
- **EX-21 limitation**: lists "subsidiaries of the registrant" — may omit entities below materiality thresholds and definitely omits non-consolidated affiliates (Athora, ADIP funds themselves, third-party ACRA investors).
