# Workflow Modes

`renewable-market-research` is a workflow-oriented market intelligence skill. It should collect broadly, verify carefully, and write final outputs only from confirmed or clearly qualified claims.

## Core Workflow Principles

1. Follow the hard order: wind first, ledger first, full report descriptive, strategy/action briefs separate.
2. Separate collection, review, synthesis, and executive compression.
3. Keep writer agents and reviewer agents separate.
4. Store evidence in files before writing conclusions.
5. Keep a rich master JSON between depth files and reports, then derive a compact canonical project ledger for identity, dedupe, status buckets, and watchlist/rejected decisions. Chapters must read rich fields from the master JSON and use the ledger only as the project-control registry.
6. Never place unverified leads in the confirmed pipeline.
7. Separate official plans, auction targets, installed capacity, confirmed project pipeline, all-phase pipeline, watchlist, duplicate, and rejected records.
8. Preserve broad discovery coverage, but make final capacity/project counts narrower through verified ledger buckets.
9. Search in English plus the country's official/local language(s); record the language coverage in the search plan or `index.json`.
10. Convert important facts into decision-useful implications.
11. Mark assumptions explicitly and keep unsupported claims in `rejected_claims` or watchlists.
12. Keep the default analysis focused on one target country; add peer-country comparisons only when the user explicitly requests a benchmark.
13. Treat storage, solar PV, grid, hydrogen, ammonia, methanol, I-REC, CBAM, and industrial offtake as adjacent opportunity context only when they affect wind project value, PPA/tariff economics, interconnection, procurement, or sales entry.
14. Route all final conclusions through the Continuity, Evidence, and Contradiction gates before synthesis or executive compression.
15. After downstream chapters change, rerun a summary/conclusion backpropagation pass so the executive section reflects the latest master JSON, ledger, and synthesis.
16. Use V4 Heavy Chapter-Agent Workflow as the default for benchmark-surpassing country wind-market reports. Standard and Lite are reductions of the same file/gate architecture, not separate logic.

## Lite Workflow

Use for quick market checks and early go/no-go screening.

Agents:

1. `policy_agent`
2. `pipeline_agent`
3. `product_fit_agent`
4. `skeptic_agent`
5. `synthesis_agent`
6. `executive_agent`

Outputs:

- One-page market judgment.
- Confirmed leads and watchlist leads.
- Rich master JSON plus a canonical project ledger or compact project registry for any project claims.
- Top policy, grid, product-fit, and execution risks.
- Immediate next actions only when the user asks for strategy or sales follow-up.
- Three executive judgments with evidence support after Continuity, Evidence, and Contradiction Gate review.

## Standard Workflow

Use for country-level wind, solar, storage, or integrated renewable market reports.

Agents:

1. `policy_agent`
2. `pipeline_agent`
3. `owner_agent`
4. `grid_agent`
5. `product_fit_agent`
6. `finance_agent`
7. `competitor_agent`
8. `skeptic_agent`
9. `synthesis_agent`
10. `executive_agent`

Outputs:

- Lite report.
- Full report using the V4 0-16 chapter structure in `references/full-report-v4.md`.
- V4 gate artifacts in order: candidate project pool, source trace/evidence table, project ledger, capacity reconciliation, participant ledger, OEM competition matrix, procurement window table, detailed project cards, full report, then lite report.
- Standalone market key-indicator dashboard with time-series comparisons.
- Rich master JSON and canonical project pipeline ledger.
- Project pipeline cards in the report body, plus CSV/appendix tables when useful.
- Owner/developer/EPC/competitor map.
- Anchor developer deep dives when material to the market, such as ACWA, Masdar, state entities, or dominant IPPs.
- OEM/equipment supplier panorama, logistics/installation analysis, and auction/PPA tariff comparison.
- Participant-role matrix tying every material owner, OEM, EPC, financier, and channel actor to project roles, MW exposure, procurement influence, relationship strength, and evidence confidence.
- Product-fit assessment for Mingyang/MySE solutions.
- Separate sales-action plan only when the user asks for strategy or next actions.
- Executive brief based only on conclusions that passed the Continuity, Evidence, and Contradiction gates.
- Evidence archive and rejected-claims register.

## Heavy Workflow

Use for benchmark-surpassing country wind-market reports where pipeline accuracy, participant depth, OEM competition, procurement-window clarity, citation auditability, and evidence-bound market status are more important than speed.

V4 full reports must use `v4-heavy-chapter-agent` by default: at least 15 logical agents and a target topology of 20 logical roles. Do not default to the 10-agent Standard profile for a V4 full report unless the user explicitly asks for a smaller run.

Agent topology:

1. `main_orchestrator_integrator`: owns run state, task split, artifact order, aggregation, master JSON, canonical ledger, final integration, summary refresh, and handoff.
2. `chapter_0_scope_evidence_worker`: owns Chapter 0 capacity, stage, opportunity, and confidence rules.
3. `chapter_2_market_fundamentals_worker`: owns Chapter 2 power fundamentals, demand/load gap, and market indicators.
4. `chapter_3_policy_permitting_worker`: owns Chapter 3 policy, permitting, development flow, and PPA mechanism.
5. `chapter_4_capacity_segmentation_worker`: owns Chapter 4 capacity segmentation and confirmed/opportunity/watchlist totals.
6. `chapter_5_project_ledger_worker`: owns Chapter 5 full project ledger.
7. `chapter_6_project_cards_worker`: owns Chapter 6 complete project cards.
8. `chapter_7_owner_decision_worker`: owns Chapter 7 developers, owners, SPVs, and decision rights.
9. `chapter_8_wind_resource_turbine_fit_worker`: owns Chapter 8 wind resource, geography, and turbine-fit inference.
10. `chapter_9_oem_competition_worker`: owns Chapter 9 OEM competition, locked MW, and unallocated OEM MW.
11. `chapter_10_epc_finance_om_supply_worker`: owns Chapter 10 EPC, financiers, O&M, and supply-chain network.
12. `chapter_11_localization_worker`: owns Chapter 11 localization and industrial policy status.
13. `chapter_12_grid_storage_worker`: owns Chapter 12 grid, storage, interconnection, and curtailment constraints.
14. `chapter_13_tariff_bankability_worker`: owns Chapter 13 tariff, project economics, and bankability status.
15. `chapter_14_procurement_window_worker`: owns Chapter 14 procurement window and decision-chain status.
16. `chapter_15_risk_matrix_worker`: owns Chapter 15 risk matrix and constraint conditions.
17. `chapter_16_evidence_appendix_worker`: owns Chapter 16 source and conclusion-confidence appendix.
18. `chapter_1_executive_summary_worker`: owns Chapter 1 only after Chapters 2-16, capacity reconciliation, and no-strategy scan are current.
19. `verification_agent`: independently verifies critical project/policy/tariff/OEM/procurement/evidence fields and writes source-audit plus chapter-verification artifacts.
20. `reflection_reviewer`: independently scores each stage and chapter, lists critical blockers, and writes executable gap tasks.

If the host cannot spawn 20 real child agents, run these roles as separate sequential lanes and record `agentMode=collapsed-sequential`. The role artifacts, ownership boundaries, and verification gates remain mandatory.

Critical chapters requiring writer/verifier separation:

- Chapter 1 executive summary.
- Chapter 3 policy/PPA/development flow.
- Chapter 4 capacity segmentation.
- Chapter 5 full project ledger.
- Chapter 6 key project cards.
- Chapter 9 OEM competition landscape.
- Chapter 13 tariff/project economics/bankability.
- Chapter 14 procurement window and decision-chain status.
- Chapter 16 data-source and conclusion-confidence appendix.

Heavy Workflow stage loop:

1. Search plan reflection: reviewer checks local-language coverage, Chinese-capital search, new-entrant search, anomaly hunting, official-source backtrace, and mandatory evidence thresholds before workers start.
2. Evidence reflection: reviewer checks depth files for coverage, source quality, search passes, critical-field verification, and unexplained blind spots.
3. Ledger reflection: reviewer checks canonical IDs, alias merging, confirmed/watchlist/duplicate/rejected buckets, capacity totals, rich-field propagation, and source-to-final continuity.
4. Report reflection: reviewer checks the V4 0-16 chapter structure, full project ledger, project cards, developer/OEM depth, logistics, tariff/bankability status, procurement-window table, source-confidence appendix, summary freshness, and absence of benchmark sections unless requested.

Stage advancement rules:

- A stage may advance only when `critical_blockers == 0`.
- Score improvement alone is insufficient; the current stage must also meet the threshold in `review_gates.md`.
- If a stage fails, the reviewer must write `data/renewable-market/{slug}-gap-tasks.json` with owner lane, missing artifact, required evidence method, and acceptance criterion.
- The main agent reruns only the affected lanes, then reruns verification/review for that stage.

Heavy Workflow outputs include all Standard outputs plus:

- `data/renewable-market/{slug}-v4_agent_plan.json`
- `data/renewable-market/report_chapters/{slug}-chapter-*.md`
- `data/renewable-market/chapter_verification/{slug}-chapter-*-verification.json`
- `data/renewable-market/{slug}-search-coverage.json`
- `data/renewable-market/{slug}-source-audit.json`
- `data/renewable-market/{slug}-reflection-review.json`
- `data/renewable-market/{slug}-gap-tasks.json` when gaps remain
- Optional `data/renewable-market/{slug}-run-status.json` for a JS scheduler or resumable harness

## Deep Workflow

Use for strategic questions such as NEOM energy configuration, Saudi localization factory strategy, floating offshore wind strategy, market-entry M&A, or integrated energy pricing logic.

Additional requirements:

- Start from the Heavy Workflow topology unless the user explicitly chooses a smaller profile.
- Multiple evidence-review loops.
- Scenario comparison.
- Assumptions register.
- Evidence archive.
- Omission audit covering local-language, Chinese-capital, new-entrant, legal-backtrace, and anomaly-hunter search passes.
- Human review gates before final external delivery.
- Sensitivity analysis for uncertain policy, grid, tariff, FX, localization, and demand assumptions.

Deep Workflow outputs should include all Standard Workflow outputs plus:

- Scenario matrix focused on the target country unless an explicit benchmark scope is requested.
- Assumptions register.
- Decision tree.
- Risk-trigger watchlist.
- Management recommendation memo.

## Output Discipline

Research collection can be broad. Final writing must be narrow:

- Use confirmed facts where possible.
- Qualify uncertain facts.
- Label assumptions.
- Move interesting but non-decision-useful information to appendices.
- Do not let adjacent-energy topics displace wind project pipeline, market participants, OEM competition, or procurement-window analysis.
- Do not list participants as generic company profiles; tie each material company to projects, role, MW exposure, procurement influence, and sales relevance.
- Full-report procurement conclusions must name the project or portfolio, MW scale, timing, procurement route, current OEM status, decision maker/influencer, evidence confidence, and pending verification. Recommended actions belong in a separate brief when requested.
- Do not write claims that cannot pass the review gates.
- Do not write or freeze executive summaries until the final master JSON, project ledger, policy backtrace, and synthesis are current.
