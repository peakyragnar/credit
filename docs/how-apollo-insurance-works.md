# How Apollo/Athene Insurance Works — a teaching note

**Purpose:** plain-English mental model of what Athene actually is, so the numbers in the dossier mean something. Read top to bottom once; after that it's a reference. Nothing here is a finding — it's the background you need before the findings make sense.

---

## 0. The one question this note answers

> Is the Athene flow — policyholders → US insurer → Bermuda reinsurer → private credit → borrowers, with Apollo alongside — *how insurance works*, or just *one way* to do it?

**One way.** And a specific, relatively new, aggressive one. All insurance shares a single engine (Section 1). But there are several different businesses built on that engine (Section 2), and within the one Athene is in, there's a spectrum from conservative to aggressive — Athene sits at the far aggressive end on purpose (Sections 3–4). If you remember nothing else: **the basic engine is universal; almost every distinctive thing about Athene is a deliberate choice, not a necessity.**

---

## 1. The engine every insurer shares: take money now, pay later, keep the gap

Strip away all the jargon and every insurer on earth does the same three things:

```
   ┌─────────────┐     money now      ┌─────────────┐
   │  Customers  │ ─────────────────▶ │   Insurer   │
   └─────────────┘                    └─────────────┘
                                             │
                          invests the money  │  (the "float")
                                             ▼
                                      ┌─────────────┐
                                      │   Assets    │  earns a return
                                      └─────────────┘
                                             │
   ┌─────────────┐    money later (claims,   │
   │  Customers  │ ◀── benefits, payouts) ───┘
   └─────────────┘
```

1. **Collect money now** (premiums or deposits).
2. **Pay money later** (claims, benefits, or the savings back with interest).
3. **Invest the money in between** — the pile of not-yet-paid-out cash is the **float**.

The insurer makes money two ways: **underwriting** (did I collect more than I paid out?) and **investment** (what did I earn on the float in the meantime?). Every insurer is some blend of "underwriter" and "investor." *Which blend* is what splits the industry into different businesses.

---

## 2. The four businesses built on that engine

Same engine, very different machines bolted onto it:

```
                          UNDERWRITING-DRIVEN  ◀──────────────▶  INVESTMENT-DRIVEN
                          (profit from risk)                    (profit from spread)

  ┌────────────────┐   ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
  │  A. P&C        │   │  B. Protection │   │  C. Spread /   │   │  D. PE-        │
  │  insurance     │   │  life          │   │  annuity       │   │  insurance     │
  │                │   │                │   │  (traditional) │   │  ← ATHENE      │
  ├────────────────┤   ├────────────────┤   ├────────────────┤   ├────────────────┤
  │ car, home,     │   │ term & whole   │   │ fixed/indexed  │   │ same products  │
  │ liability      │   │ life           │   │ annuities      │   │ as C, but      │
  │                │   │                │   │                │   │ supercharged   │
  │ risk: claims   │   │ risk: death    │   │ risk: mostly   │   │ (Section 3)    │
  │  vs premiums   │   │  timing        │   │  the spread    │   │                │
  │                │   │                │   │                │   │                │
  │ e.g. GEICO,    │   │ e.g. Northwest │   │ e.g. a plain   │   │ e.g. Athene,   │
  │  Berkshire     │   │  -ern Mutual,  │   │  stock life    │   │  Global Atl.,  │
  │                │   │  MassMutual    │   │  annuity book  │   │  Aspida...     │
  └────────────────┘   └────────────────┘   └────────────────┘   └────────────────┘
```

**A. Property & Casualty** — car, home, business liability. The money-out is *unpredictable* (an accident could happen tomorrow), so the float must be invested **conservatively and liquid**. Profit comes mainly from **underwriting** — pricing risk better than the next insurer. This is Warren Buffett's Berkshire model. *Athene is not this at all.*

**B. Protection life** — term and whole life, sold mostly by old mutual companies owned by their policyholders. The risk is **mortality** (when people die). They invest for **decades, conservatively** (investment-grade bonds), and compete on underwriting and patient compounding. Slow and boring by design. *Athene is not this either.*

**C. Spread / annuity business (traditional)** — here's the pivot. An **annuity is not really insurance against a disaster — it's a savings product.** You hand the insurer money; they promise to pay you a set interest rate for a set time; you get it back later. The insurer's profit is the **spread**: what they earn investing your money *minus* what they promised to pay you.

```
   you get promised:        3%
   insurer earns:           5%   on your money
   ─────────────────────────────
   the SPREAD (profit):     2%   ← this is the whole game
```

This is already **more of an asset-management business than an insurance business** — a bank-like spread machine wearing an insurance wrapper. A *traditional* annuity writer runs it conservatively: invest-grade public bonds, full capital held at home, money managed at arm's length.

**D. PE-insurance — where Athene lives.** Take business C and push every lever to its limit. Same annuity products, same spread engine — but re-engineered by an affiliated private-equity firm (Apollo) to make the spread wider, the balance sheet bigger, and the capital go further. *That re-engineering is the next section, and it's the whole reason this project exists.*

So the flow you learned is **model D specifically.** Roughly 20 groups run it (Apollo/Athene, KKR/Global Atlantic, Blackstone, Ares, Brookfield, etc. — our target list). It barely existed before ~2009 (Apollo founded Athene in 2009). Regulators call it "asset-intensive reinsurance"; critics call it the "Bermuda triangle." It is one model among four, and the newest.

---

## 3. The four levers that turn business C into business D

A traditional annuity writer and Athene sell the *same product*. Athene is different because Apollo pulls four levers at once. Each lever widens profit — and each one creates one of the risks we hunt.

```
  LEVER                    TRADITIONAL           ATHENE / PE-INSURANCE        creates
  ─────────────────────────────────────────────────────────────────────────────────
  1. What you invest in    investment-grade      private credit the          ← F1 credit
                           public bonds          affiliate ORIGINATES          quality
                                                  (higher yield, illiquid,
                                                   hard to mark, opaque)      ← F2 marks

  2. Where capital sits    onshore, full         Bermuda reinsurer, lighter  ← F4 opacity
                           US capital rules       capital + tax rules

  3. Who manages money     third party,          the affiliate (Apollo)       (fees at
                           arm's length          owns insurer, picks assets,   every step)
                                                  originates them, marks them,
                                                  earns fees on all of it

  4. How you fund it       sticky retail         retail annuities PLUS        ← F4 run-
                           annuities             institutional funding          nability
                                                  (FABN) that can leave
                                                  on a schedule
```

**Lever 1 — asset side: originate-to-hold private credit.** Instead of buying public bonds anyone can price, invest in private loans, asset-backed deals, and fund stakes that **Apollo itself originates**. Higher yield → wider spread. But these assets are illiquid, have no market price (so their value is an *opinion*, not a quote), and are often behind non-disclosing entities. → This is why we hunt **F1 (bad credit at low yield)** and **F2 (mismarked credit)**.

**Lever 2 — capital side: reinsure to Bermuda.** A US insurer must hold a thick capital cushion under US rules. Reinsure the business to an affiliated Bermuda company and the same book needs *less* capital and pays *less* tax — freeing capital to write even more. Note: reinsurance itself is normal and healthy; the twist here is reinsuring to a company **you own**, for capital/tax efficiency, not to transfer risk to an outside party. → This is why we measure **F4 opacity** (how much sits behind lightly-disclosed offshore entities).

**Lever 3 — ownership: the affiliate does everything.** In the traditional model the insurer and its asset manager are separate, dealing at arm's length. Here **Apollo owns the insurer, chooses the investments, originates many of them, decides what they're worth, and collects a fee at every touch** ($1.44B in FY2025). Great business for Apollo. The conflict is structural: the same firm that profits from *volume* also grades its own homework on *quality*. → This is the core reason the whole thesis ("optimized for filling pipes, not credit quality") is even plausible.

**Lever 4 — funding side: institutional money (FABN).** Alongside sticky retiree annuities, raise big money fast by selling **funding-agreement-backed notes** to bond investors — borrowing dressed as insurance (see glossary). It scales fast but it's **not sticky**: it has maturity dates and must be rolled over; if markets freeze or your credit looks shaky, it must be repaid *on schedule*. → This is why we score **F4 runnability**: bad illiquid assets + patient money = slow bleed; the *same assets + runnable money = an event.*

---

## 4. Athene's actual flow, with the levers labelled

Now the picture you've seen, annotated with which lever is doing what — and the real YE2025 numbers from the dossier:

```
   Policyholders + institutions
        │  $83.4B in during 2025   ← Lever 4: $35.4B of it is funding
        │                             agreements (institutional, runnable)
        ▼
   ┌──────────────────────────────────────────┐
   │  US insurer: Athene Annuity & Life (Iowa) │   the licensed face;
   │  "AAIA" — where your contract legally sits │   sells the annuities
   └──────────────────────────────────────────┘
        │
        │  ← Lever 2: cede the economics to Bermuda
        │     $168B held as ModCo + $74B ceded outright,
        │     ALL to one affiliate:
        ▼
   ┌──────────────────────────────────────────┐
   │  Bermuda reinsurer: Athene Annuity Re     │   lighter capital + tax;
   │  "AARe" — also, oddly, AAIA's OWNER        │   where the economics pool
   └──────────────────────────────────────────┘
        │
        │  ← Lever 1: invest in private credit
        │     $321B portfolio, much of it Apollo-originated
        ▼
   ┌──────────────────────────────────────────┐
   │  Assets → real borrowers (companies,       │
   │  real estate, asset-backed deals)          │
   └──────────────────────────────────────────┘

   Alongside EVERY arrow:  Apollo (Lever 3)
   ── owns the insurer, owns the reinsurer, picks + originates the
      assets, marks them, and collects fees ($1.44B in 2025) ──
```

The "US → Bermuda → US sandwich" that confused earlier (AARe is both AAIA's *parent* and its *reinsurer*) is just Lever 2 taken to its structural conclusion: the Bermuda reinsurer isn't a sibling the US insurer *does business with* — it's been placed *above* the US insurer in the ownership chain, so ownership, dividends, and reinsurance economics all pool in the same lightly-disclosed Bermuda company.

---

## 5. What this means for the credit work

None of the four levers is illegal or even necessarily wrong. Reinsurance, annuities, private credit, and funding agreements are all legitimate tools. The **thesis being tested** is whether pulling all four at once — under an owner that profits from volume — has quietly degraded credit quality while the disclosure that would reveal it moved offshore.

That's why the map is built the way it is:

- Lever 1 makes asset values *opinions* → we hunt mismarks (**F2**) and yield-vs-quality gaps (**F1**).
- Lever 2 moves the truth offshore → we measure how much is hidden (**F4 opacity**) and rebuild the economic ledger from treaties.
- Lever 3 means one firm grades its own homework → every number it reports is a *claim* to be checked against an independent source, never a truth.
- Lever 4 makes the funding runnable → we score how fast the money can leave (**F4 runnability**).

**The honest counter-case matters too:** a well-run PE-insurer genuinely can earn a wider spread safely — Apollo really is good at origination, and private credit really can out-yield public bonds for the same risk. The map has to be able to conclude "this group is clean" where the evidence says so. We are testing the levers, not assuming they've been abused.

---

## Glossary (the terms you'll keep hitting)

| Term | Plain meaning |
|---|---|
| **Float** | The pile of customer money the insurer holds before it has to pay it back; what gets invested. |
| **Spread** | Investment return earned *minus* interest promised to the customer. The core profit of an annuity writer. |
| **Annuity** | A savings product, not disaster insurance: give money now, get a promised rate, get it back later. |
| **Funding agreement / FABN** | Borrowing dressed as insurance: a trust sells notes to bond investors, hands the cash to the insurer, and the insurer issues an insurance contract (the funding agreement) in return. Legally an insurance liability, economically a bond. **Not sticky** — has maturities, must be rolled over. FABR (repo version) and FHLB advances are cousins. |
| **Reinsurance** | One insurer offloads risk (and reserves) to another. Normal — *unless* the reinsurer is one you own, offshore, for capital/tax efficiency. |
| **Ceding** | The act of passing business to a reinsurer. The US insurer "cedes" to Bermuda. |
| **Reserves** | The money set aside representing what the insurer owes policyholders. The central liability number. |
| **ModCo (modified coinsurance)** | A reinsurance form where the *assets stay legally on the US insurer's books* but the economics belong to the reinsurer. The single biggest reason the legal ledger and the economic ledger diverge — $168B of it at AAIA alone. |
| **Funds withheld** | Similar idea: the ceding insurer physically keeps the assets as collateral for reinsurance it has ceded. Onshore legally, offshore economically. |
| **Private credit** | Loans and credit assets not traded on public markets — no market price, so value is an estimate. Athene's asset engine, Apollo-originated. |
| **Statutory (SAP) vs GAAP** | Two accounting languages: SAP is what US insurers file with state regulators (conservative, entity-level); GAAP is the investor-facing consolidated version. They don't tie exactly — different rules, different perimeters. |
| **Sidecar / ACRA / ADIP** | Vehicles holding *outside* investors' capital alongside Athene's, invested the same way. Apollo earns fees on this third-party money too (~$15B of it). |
| **Bermuda / BMA** | Bermuda Monetary Authority — the offshore regulator with lighter capital rules and less public disclosure than US states. Where AARe reports. |

---

*Companion to `spec/credit-map-spec.md`. The findings F1–F4 referenced here are defined in spec §1.1.*
