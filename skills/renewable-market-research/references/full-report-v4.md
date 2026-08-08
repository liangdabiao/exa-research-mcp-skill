# V4 Full Report Architecture

Use this reference whenever generating the **full** country wind-market report. It is the report contract; `references/pdf-pipeline.md` only covers authoring and PDF layout mechanics.

## Positioning

The full report is a **country wind-market status master report**. It is not a strategy recommendation memo and not the lite delivery version.

Its job is to describe, with evidence boundaries:

- why wind develops in the country;
- how market capacity is segmented;
- which projects exist and what their status is;
- who the developers, owners, EPCs, OEMs, financiers, and O&M parties are;
- how policy, permitting, development flow, and PPA mechanisms work;
- where OEM procurement windows and decision chains stand today;
- what grid, storage, interconnection, curtailment, localization, and financing constraints exist;
- which conclusions are verified facts, which are assumptions, and which remain pending verification.

The full report must not make final go/no-go, factory-build, pricing, or bid-strategy decisions for the reader. Mingyang/MySE material should be expressed as factual relevance, procurement window, decision-chain position, opportunity MW, and pending verification, not as recommended action.

## Core Principles

> Search broadly, calculate narrowly. Collect many leads, but do not admit them loosely.

> The project ledger is the skeleton, market narrative is the explanation, project cards are the fact base, and evidence boundaries are the guardrail.

Hard rule: key project-card fields must not be deleted because the body text is compressed. The main body may summarize; the project-card appendix or card block must preserve complete fields, with `not found`, `unavailable`, or `not applicable` when evidence is absent.

## Chapter Contract

| Chapter | Name | Question Answered | Main Output |
|---|---|---|---|
| 0 | Report scope and evidence rules | How capacity, stage, opportunity, and confidence are defined | capacity definitions, stage definitions, conclusion-evidence rules |
| 1 | Executive summary | What are the most important current market facts | core facts, key-number dashboard, project status summary |
| 2 | National power fundamentals | What power-system context explains wind growth | capacity, generation, load, demand gap, thermal/gas substitution |
| 3 | Policy, permitting, development flow, and PPA mechanism | How projects move from policy target to buildable asset | policy table, development flow, permit path, PPA nodes |
| 4 | Market capacity definitions and project segmentation | Which capacity can be counted and which remains lead/watchlist | pipeline funnel, confirmed capacity, opportunity capacity, watchlist |
| 5 | Full project ledger | Which projects exist and whether capacity can be reconciled | master project ledger |
| 6 | Key project cards | What the complete facts are for material projects | complete project cards |
| 7 | Developers, owners, and decision-right structure | Who controls projects and who influences procurement | developer matrix, equity structure, decision-right map |
| 8 | Wind resource, geography, and turbine-fit inference | How known turbine choices bound technical assumptions when resource reports are incomplete | turbine parameter table, inference table, regional mapping, competitor platform table |
| 9 | OEM competition landscape | Who is locked, shortlisted, unknown, or absent | OEM share, locked MW, turbine distribution, competition status |
| 10 | EPC, financiers, O&M, and supply-chain network | Who builds, finances, operates, and supplies | EPC, financier, O&M, and supply-chain tables |
| 11 | Localization and industrial policy status | What localization requirements and local footprints exist | localization policy, factory/service footprint, supply-chain status |
| 12 | Grid, storage, interconnection, and curtailment constraints | What system constraints affect project execution | grid bottlenecks, BESS requirements, transmission routes, curtailment risk |
| 13 | Tariff, project economics, and bankability status | What commercial and financing structures are observable | PPA tariff, guarantees, financing structure, bankability facts |
| 14 | Procurement window and decision-chain status | Which projects have undecided turbines and who decides when | unallocated OEM MW, procurement-window table, decision-chain table |
| 15 | Risk matrix and constraint conditions | What current market risks and constraints exist | risk matrix and constraint notes |
| 16 | Data-source and conclusion-confidence appendix | Which evidence supports which conclusions | conclusion-evidence table, source table, pending-verification items |

## Chapter-Agent Ownership

V4 full reports default to `v4-heavy-chapter-agent`, not the 10-agent Standard profile. Use at least 15 logical agents and target 20 roles: main integrator, chapter workers, delayed Chapter 1 summary worker, independent verification agent, and independent reflection reviewer. If real subagents are unavailable, run the same roles sequentially and record `agentMode=collapsed-sequential`.

| Chapter | Writer Role | Verification |
|---|---|---|
| 0 | `chapter_0_scope_evidence_worker` | reviewer pass |
| 1 | `chapter_1_executive_summary_worker` | independent verification + reviewer pass after Chapters 2-16 |
| 2 | `chapter_2_market_fundamentals_worker` | reviewer pass |
| 3 | `chapter_3_policy_permitting_worker` | independent verification + reviewer pass |
| 4 | `chapter_4_capacity_segmentation_worker` | independent verification + reviewer pass |
| 5 | `chapter_5_project_ledger_worker` | independent verification + reviewer pass |
| 6 | `chapter_6_project_cards_worker` | independent verification + reviewer pass |
| 7 | `chapter_7_owner_decision_worker` | reviewer pass |
| 8 | `chapter_8_wind_resource_turbine_fit_worker` | reviewer pass |
| 9 | `chapter_9_oem_competition_worker` | independent verification + reviewer pass |
| 10 | `chapter_10_epc_finance_om_supply_worker` | reviewer pass |
| 11 | `chapter_11_localization_worker` | reviewer pass |
| 12 | `chapter_12_grid_storage_worker` | reviewer pass |
| 13 | `chapter_13_tariff_bankability_worker` | independent verification + reviewer pass |
| 14 | `chapter_14_procurement_window_worker` | independent verification + reviewer pass |
| 15 | `chapter_15_risk_matrix_worker` | reviewer pass |
| 16 | `chapter_16_evidence_appendix_worker` | independent verification + reviewer pass |

Critical chapter verification means the chapter writer cannot self-release the chapter. The verifier must check source-to-field continuity, capacity treatment, evidence confidence, pending-verification notes, and contradiction status before the main integrator assembles the full report.

## Chapter Requirements

### 0. Report Scope And Evidence Rules

Purpose: prevent drift in later capacity, project-stage, opportunity, and confidence judgments.

Required tables:

- Capacity definition table: operational, under construction, financing closed, PPA signed, decree-backed, tendering, MOU/JDA, watchlist, national long-term target.
- Project-stage definition table: evidence required before each stage can be counted.
- Opportunity capacity definition table: separate project MW, unallocated-OEM MW, and `Opportunity MW`.
- Conclusion-evidence rule table: source tier, whether it directly proves the claim, confidence, and pending verification.

### 1. Executive Summary

Purpose: establish a fast market-status overview.

Write fact-based summary only; do not write recommendations.

Required content:

- 3-5 market core facts;
- key-number dashboard;
- project segmentation summary;
- locked OEM versus undisclosed/unallocated OEM summary;
- major constraint summary;
- report date, data cutoff, and latest major update anchor.

### 2. National Power Fundamentals

Purpose: explain why wind can grow.

Required tables:

- Power mix: thermal, hydro, solar PV, wind, BESS, total capacity.
- Generation: annual total generation, wind, solar, green-power share.
- Demand and load: peak load, annual demand, demand growth, demand forecast.
- Substitution logic: thermal aging, gas import exposure, coal/gas structure, power deficit.

### 3. Policy, Permitting, Development Flow, And PPA Mechanism

Purpose: describe how projects legally and commercially progress.

Required modules:

- Policy evolution: law/policy, date, target, scope.
- Project acquisition route: auction, direct negotiation, government decree, JDA, MoU.
- Permit path: land, ESIA, grid/interconnection, construction permit, electricity license.
- PPA nodes: signatory, offtaker, tenor, guarantee, currency.
- Development flow: MoU/JDA -> wind measurement/ESIA -> PPA -> financial close -> NTP -> COD.
- Procurement nodes: OEM procurement, EPC procurement, financing constraints, MDB review.

### 4. Market Capacity Definitions And Project Segmentation

Purpose: answer the real market-capacity question.

Use this segmentation baseline:

| Layer | Count In Confirmed Capacity | Count In Opportunity Capacity | Notes |
|---|---|---|---|
| Operational | yes | no |  |
| Under construction | yes | depends on OEM status |  |
| Financing closed | yes | depends on OEM status |  |
| PPA/decree-backed | cautious | yes |  |
| Tendering | no/cautious | yes |  |
| MOU/JDA | no | watchlist |  |
| National target | no | upper-bound only |  |

Always provide confirmed capacity, opportunity capacity, watchlist capacity, and national long-term target capacity separately.

### 5. Full Project Ledger

Purpose: create a project database that is reconcilable, auditable, and updateable.

Required fields:

| Field | Meaning |
|---|---|
| Project ID | unified project identifier |
| Alias Group ID | duplicate-prevention group |
| Canonical project name | deduplicated standard name |
| Project aliases | English, local, Chinese, and old-report names |
| Capacity MW | total project capacity |
| Opportunity MW | addressable/unallocated capacity |
| BESS | MW/MWh |
| Project stage | operational, under construction, financing closed, PPA, decree, tender, MOU, watchlist |
| Status Basis | stage evidence |
| Counted in confirmed capacity | yes/no |
| Counted in opportunity capacity | yes/no |
| Location | state, province, district, site |
| Sponsor/Owner | developer or owner |
| SPV | project company |
| Equity structure | shareholding |
| Acquisition route | auction, direct negotiation, decree, JDA, MoU |
| OEM | awarded, pending, shortlisted, undisclosed |
| Procurement Status | not tendered, RFQ, shortlisted, awarded, framework, undisclosed |
| Turbine model | known model |
| EPC | EPC or installer |
| O&M party | owner, OEM, or third party |
| Financiers | MDB, commercial bank, policy bank |
| PPA/offtaker | grid, single buyer, corporate offtaker |
| Tariff | public, estimated, undisclosed |
| COD/timeline | operational or target date |
| Next Milestone | RFQ, financial close, NTP, COD, ESIA approval |
| Decision Maker | headquarters, regional company, SPV, EPC, government, MDB |
| Influencers | MDB, EPC, government, grid, shareholders |
| Key evidence | decree, MDB, official site, ESIA, press release |
| Field Confidence | field-level confidence |
| Last Checked Date | most recent verification date |
| Pending Verification | next fact to verify |
| Mingyang Relevance | high, medium, low, none; fact-based only |
| Relevance Rationale | unallocated OEM, framework tie, project stage, technical fit, etc. |
| Main Risks | grid, finance, competition, land, policy, ESG |

### 6. Key Project Cards

Purpose: preserve complete facts for material projects.

Project-card fields must not be removed due to body-length compression.

Required modules:

| Module | Fields |
|---|---|
| Basic information | project name, capacity, location, stage, COD |
| Owner structure | developer, SPV, equity, government counterpart |
| Technical plan | OEM, turbine model, turbine count, BESS, transmission line |
| Commercial structure | PPA, offtaker, tariff, tenor, guarantee |
| Financing structure | total investment, lenders, financial-close status |
| Development flow | land, ESIA, interconnection, construction permit, electricity license |
| Engineering supply chain | EPC, logistics, lifting, localization requirements |
| O&M arrangement | O&M party, service tenor, spare parts, local service base |
| Current progress | latest event, next node, procurement window |
| Decision chain | decision maker, influencers, MDB/government/EPC role |
| Mingyang relevance | Opportunity MW, relevance rationale, pending verification |
| Risks and constraints | grid, land, ESG, financing, competition |
| Evidence boundary | verified facts, reasonable assumptions, pending verification |

### 7. Developers, Owners, And Decision-Right Structure

Required tables:

- Developer ranking: developer, country, controlled MW, project count, stage distribution.
- Project-owner matrix: project, SPV, equity structure, government counterpart.
- Decision-right structure: headquarters, regional company, SPV, EPC, MDB, government roles.
- Developer preference: existing OEM, existing EPC, financier, acquisition route.

### 8. Wind Resource, Geography, And Turbine-Fit Inference

Do not pretend to know exact wind-resource data when it is not sourced. Use locked turbine models to infer technical boundaries, and state what cannot be inferred.

Required tables:

- Known operational/locked turbine parameter table: project, region, status, OEM, model, unit MW, rotor diameter, hub height, turbine count, technical route, known capacity factor/annual generation, evidence level.
- Turbine-choice inference table: observed fact, reasonable inference, cannot infer.
- Region-project-model mapping table: region, known project, known model, inferred resource/constraint characteristics, note.
- Competitor platform positioning table: OEM, model/platform, known project, key parameters, technical positioning, fit scenario, risk/pending verification.

### 9. OEM Competition Landscape

Required tables:

- OEM locked-capacity table: OEM, project, capacity, turbine model, status.
- OEM share table: operational, locked, shortlisted, undisclosed.
- Unallocated OEM capacity table: project, capacity, stage, procurement status.
- OEM competition status table: existing record, developer relationship, financing precedent, risk.

### 10. EPC, Financiers, O&M, And Supply-Chain Network

Describe who participates; do not judge whether to partner.

Required tables:

- EPC matrix: EPC, project, role, scale, owner relationship.
- Financier matrix: financier, project, amount, instrument, stage.
- O&M table: project, O&M party, tenor, LTSA, local team, spare-parts base.
- Supply-chain table: logistics, lifting, towers, blades, substation, service base.

### 11. Localization And Industrial Policy Status

Describe requirements and existing footprints only; do not decide whether to build a factory.

Required tables:

- Localization policy table: policy source, applicable projects, requirement.
- Local manufacturing footprint: company, product, location, capacity, status.
- Local service footprint: service base, spare-parts warehouse, O&M team.
- OEM access linkage: whether localization affects procurement, financing, or policy support.

### 12. Grid, Storage, Interconnection, And Curtailment Constraints

Required tables:

- Grid topology: main grid, voltage level, key substations, export/transmission corridors.
- Project interconnection: project, connection point, transmission line, interconnection status.
- BESS requirement: policy requirement, project configuration, MW/MWh, status.
- Curtailment/absorption: curtailment data, regional bottleneck, reason.
- Transmission-route table: line, length, investment, financing, progress.

### 13. Tariff, Project Economics, And Bankability Status

Describe commercial-structure facts; do not provide investment advice.

Required tables:

- PPA tariff: project, tariff, currency, tenor, source.
- PPA structure: offtaker, guarantee, take-and-pay/take-or-pay, indexation.
- Financing structure: debt/equity ratio, MDB, commercial loan, guarantee tool.
- Bankability facts: OEM precedent, MDB acceptance, ESIA, guarantee structure.
- Sensitivities: FX, curtailment, interest rate, inflation, grid delay.

### 14. Procurement Window And Decision-Chain Status

Describe who decides turbines and when.

Required subsections:

- 14.1 Unallocated OEM capacity table.
- 14.2 Procurement-window table.
- 14.3 Decision-chain table.
- 14.4 Project relevance matrix.
- 14.5 Pending-verification table.

Procurement-window table fields: project, capacity, Opportunity MW, current stage, OEM status, RFQ/tender/NTP timing, decision maker, influencer, pending verification.

Do not write Mingyang actions here. Use pending verification and relevance.

### 15. Risk Matrix And Constraint Conditions

Required table: risk, current fact, affected object, severity, evidence, pending verification.

Risk categories:

- policy risk;
- PPA/offtaker risk;
- FX risk;
- financing risk;
- grid/curtailment risk;
- land/ESG risk;
- logistics/lifting risk;
- localization risk;
- OEM competition risk;
- project-delay risk.

### 16. Data-Source And Conclusion-Confidence Appendix

Purpose: prevent the mistake of treating every conclusion as strong merely because one source is strong.

Conclusion-evidence table fields: conclusion, source, source tier, direct proof yes/no, confidence, pending verification.

Evidence requirements by conclusion type:

| Conclusion Type | Evidence Requirement |
|---|---|
| Project existence | decree, MDB, or developer official source is stronger |
| Capacity | MDB, ESIA, PPA, or decree is stronger |
| Project stage | COD, NTP, or financial close must have corresponding evidence |
| OEM award | developer, OEM, or EPC announcement is stronger |
| Tariff | tender document, PPA, or MDB document is stronger |
| O&M arrangement | contract, developer announcement, or project document is stronger |
| Mingyang relevance | usually inference; must mark basis and confidence |

## Writer Flow

1. Start from the validated rich master JSON, canonical project ledger, source trace, and depth records.
2. Write Chapter 0 before drafting conclusions so capacity and confidence rules are fixed.
3. Build Chapters 5 and 6 directly from the master JSON and cross-read matching depth records. If depth records contain richer fields, update the master JSON or mark the field as unavailable before drafting.
4. Write Chapters 7-14 from project-linked participant, technology, grid, tariff, localization, and procurement-window records. Avoid generic company profiles.
5. Write Chapter 1 only after Chapters 2-16 are current, then back-check every summary number against the ledger.
6. Keep recommendations out of the full report. If the user asks for strategy or sales actions, produce a separate executive brief, action memo, or lite addendum.
