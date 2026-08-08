---
name: renewable-market-research
description: Workflow skill for evidence-based renewable energy market research, V4 full country wind-market status reports, source-to-final continuity, project pipeline verification, deduplication, product-fit analysis, factual procurement-window mapping, and executive briefing compression. Use for overseas wind, solar, storage, hydrogen, grid, or clean-energy market research where evidence quality, source traceability, omission control, uncertainty control, and decision usefulness matter more than long reports.
---

# Renewable Market Research

## Goal

Research **any country + any renewable/new-energy technology** as an evidence-driven market intelligence workflow for market judgment, project pipeline verification, product-fit analysis, factual procurement-window mapping, and executive reporting. Preserve reusable market data plus traditional report deliverables:

1. **Full report**: V4 country wind-market status master report with scope/evidence rules, capacity segmentation, full project ledger, key project cards, participant/decision-chain mapping, OEM/EPC/finance/O&M/localization/grid/tariff/risk facts, and source-confidence appendix. It is not a strategy recommendation memo.
2. **Lite report**: shorter delivery version with polished structure, project pipeline essentials, and reduced deep/proprietary analysis.
3. **Executive or action brief**: optional separate output when the user asks for strategy, sales actions, or management recommendations.

Use an effective-harnesses mindset: persist state to files, make progress resumable, validate outputs, and avoid returning large raw search payloads through chat.

## Operating Principle

**Wind first, recall first, ledger strict, full report descriptive.**

For wind-market tasks, treat the report as a national wind market study, not a broad energy overview. The core line is project pipeline, market participants, OEM/EPC competition, policy/PPA/tariff context, procurement-window facts, and evidence boundaries. Keep recommendations outside the full report unless the user asks for a separate executive or action brief.

Run research in two modes. First, run high-recall discovery with dynamic frontier expansion: search entry names must not be assumed complete at initialization. Start from fixed seed templates, historical baseline entries, and authority-source categories; then extract every discovered project, developer, SPV, OEM, EPC, lender, law/decree, offtaker, grid entity, region, authority source, and adjacent-opportunity signal into `search_frontier.json`. Search the newly discovered entries in later rounds. Do not reject early-stage items during recall. Any candidate with a project name plus at least one signal such as capacity, actor, location, agreement, decree, news, financing, OEM/EPC link, or grid/PPA clue must enter `candidate_project_pool.json`.

Bound high recall with frontier priority, not with early deletion. Treat P0 as wind project/commercial core, P1 as wind policy/grid/revenue context, P2 as one-hop market enablers, P3 as adjacent topics that expand only with explicit wind impact, and P4 as deferred macro background. P0/P1 entries drive convergence; P2/P3/P4 entries are preserved but must not create infinite search drift unless promoted by wind-linked evidence.

Harden P0/P1 with role-separated execution and evaluation. Every P0/P1 frontier entry must receive an executor role, a different evaluator role, an execution artifact, an evaluation artifact, and an evaluation status before ledger admission. P2/P3/P4 entries do not need this hard gate unless promoted to P0/P1. Role separation does not require two real processes when unavailable; a single session may run separate executor and evaluator passes, but must write separate artifacts.

Second, run verification and reconciliation: merge duplicates, classify every candidate as `operational`, `financing_closed`, `under_construction`, `ppa_signed`, `decree_backed`, `mou_or_early_stage`, `watchlist`, `duplicate`, `rejected`, or `unresolved`, backtrace policies and tariffs, verify source traces, and calculate all capacity totals from `{slug}-pipeline-ledger.json`. Search should be broad; ledger admission should be strict. Final reports must be generated from the reconciled ledger and rich master JSON, not from raw notes.

Adjacent topics such as storage, solar PV, grid, green hydrogen, ammonia, methanol, I-REC, CBAM, and industrial green-power demand may enter the main report only when they change wind project value, PPA/tariff economics, interconnection, procurement route, OEM opportunity, or sales entry point. Otherwise keep them as appendix/gap notes.

## Required Reading

Load only the reference needed for the current step:

- `references/file-mode-research.md`: parallel/file-mode collection workflow, tool priority, convergence rules, and child-agent prompt template.
- `references/data-model.md`: directory layout, `index.json`, main JSON schema, canonical project ledger, depth JSON schema, and CSV columns.
- `workflow.md`: Lite, Standard, and Deep workflow modes for decision-oriented market intelligence.
- `agent_roles.md`: writer, reviewer, synthesis, and executive role separation.
- `review_gates.md`: Evidence, Contradiction, Business, and Executive gates that final claims must pass.
- `schema/*.schema.json`: machine-readable schemas for evidence, findings, projects, decisions, reviews, and reports.
- `prompts/*.md`: role-specific prompts for orchestrator, policy, pipeline, owner, product-fit, grid, finance, competitor, verification, skeptic/reflection, synthesis, and executive agents.
- `references/full-report-v4.md`: required V4 full-report architecture, chapter contract, project-ledger fields, project-card fields, and full-report writer flow.
- `references/pdf-pipeline.md`: full/lite report structure, Markdown/HTML/PDF pipeline, Chinese/English font handling, table alignment, and output risks.
- `references/windows-native.md`: Windows native PowerShell/Python startup commands, CSV export wrapper, PDF caveats, and Chrome MCP browser rules.
- `references/search-orchestration.md`: intent-aware query planning, search-lane coverage gates, local-language/china-capital/anomaly passes, validation script usage, and evidence-ranking guidance.

## Workflow Modes

Choose the mode in `workflow.md` before collecting data:

- **Lite Workflow**: quick market checks using policy, pipeline, product-fit, skeptic, synthesis, and executive agents. Output a one-page market judgment, confirmed leads, risks, and next actions.
- **Standard Workflow**: country-level reports using policy, pipeline, owner, grid, product-fit, finance, competitor, skeptic, synthesis, and executive agents. Output lite report, V4 full report, project ledger/cards, procurement-window and decision-chain tables, and an executive brief or action memo only when requested.
- **Heavy Workflow**: default for V4 full country wind-market reports. Use the `v4-heavy-chapter-agent` profile: at least 15 logical agents and a target topology of 20 roles covering chapter workers, one independent verification agent, and one independent reflection/reviewer. Output all Standard deliverables plus source-audit, chapter-verification, reflection-review, and gap-task artifacts. If fewer real agents are available, collapse lanes sequentially but keep the same roles, files, gates, and review loops.
- **Deep Workflow**: strategic questions requiring multiple review loops, scenario comparison, assumptions register, evidence archive, and human review gates.

## Standard Workflow

1. **Normalize task**
   - Extract `country`, `technology`, language, report depth, and target audience.
   - Identify official/local languages plus English before search. If unknown, add an early query to identify official language names and scripts.
   - Collect known project aliases, translated names, local names, developer names, and Chinese company names as seed terms for later anomaly and deduplication passes.
   - Slugify to `{country_slug}-{technology_slug}` such as `uzbekistan-wind`.
   - Create `data/renewable-market/` and `data/renewable-market/depth/` if missing.
   - For long-form research, generate a search plan with `scripts/search_orchestration.py plan` before assigning workers.

2. **Resume or initialize harness state**
   - Read `data/renewable-market/index.json` if present.
   - If `{country_slug}-{technology_slug}.json` exists, run an incremental update; otherwise run first-time collection.
   - Optionally add/maintain `feature_list.json` entries for: collection, aggregation, full report, lite report, PDF rendering.

3. **Split research dimensions**
   Use focused dimensions depending on scope. For OEM/commercial-entry asks (for example Mingyang), use **demand-first framing**: start from electricity demand gap and monetizable offtake, then validate resource/technology constraints.
   - demand-load-gap (generation, consumption, peak load, imports/exports, 5-10 year outlook)
   - market-key-indicators-timeseries (generation YoY, latest Q/month data, wind/solar 3-year trend, installed capacity, imports/exports, pipeline MW)
   - power-mix-replacement (retirements, thermal constraints, hydro flexibility, wind/solar complementarity)
   - grid-storage-transmission (curtailment risk, substations/lines, storage requirement, cross-border corridors)
   - policy-ppa-economics (auction/FIT/PPA, tariff history, FX risk, localization, IRR/ROE if estimable)
   - auction-tariff-comparison (project-level winning tariffs, PPA tenor, currency/indexation, sponsor, capacity, source confidence)
   - project-pipeline-layered (operational, under-construction, awarded/PPA, MOU, early stage)
   - owners-partners-routes (state entities, IPPs, EPC/developer networks, contact pathways)
   - anchor-developer-deep-dives (material developers such as ACWA/Masdar/state entities: financials, full local portfolio, key people, partners, IRR assumptions when supportable)
   - competitor-oem-landscape (full OEM/supplier panorama, turbine platforms/specs, product roadmap, BNEF or credible market-share trend when available, localization and tie strength)
   - epc-om-logistics-lifting (route length/time, ports/rail/road/border crossings, component dimensions/weights, crane/heavy-lift firms, installation window risks)
   - localization-supply-chain (tower/blade/nacelle/BESS ecosystem and JV options)
   - esg-land-community (ESIA, biodiversity, land/community, IFI social constraints)
   - carbon-greenpower-hydrogen (I-REC, CBAM, enterprise PPA, hydrogen/ammonia links)
   - china-finance-ecosystem (Chinese EPC/developers/financiers and policy-bank support)
   - chinese-developer-deep-dives (listed code, revenue/profit/margin, team/local presence, financing innovation, project roles)
   - local-language-china-capital-trace (Chinese capital + local-language project names + Chinese EPC/OEM/SPV traces)
   - new-entrant-hunter (new IPPs, new SPVs, first-time EPC/OEM entries, corporate offtakers)
   - policy-law-backtrace (reverse policy targets, auctions, tariffs, and capacity numbers to original laws, decrees, orders, and regulator documents)
   - anomaly-hunter (misspellings, transliterations, PDF/table/map-only mentions, renamed phases, and projects outside known patterns)
   - optional-single-country-benchmark (only if explicitly requested; keep default analysis on the target country, not another country comparison)
   - mingyang-entry-strategy (12/36/60 month actions across turbine, hybrid, EPC, O&M, local manufacturing)
   - Keep wind as the primary object: storage, solar, hydrogen, ammonia, methanol, and industrial offtake dimensions should explain how they affect wind projects, not become standalone market reports.

4. **Recall in file mode**
   - Prefer Exa semantic search/fetch/deep-search tools for broad discovery.
   - Use Chrome MCP as the first fallback/verification browser when Exa misses dynamic, PDF, table, map, ecommerce, or JavaScript-rendered evidence.
   - Fall back to general browser/search tools only after Exa and Chrome MCP are insufficient.
   - For V4 full reports, use the `v4-heavy-chapter-agent` topology from `workflow.md`, `agent_roles.md`, and the generated search plan. It has at least 15 logical agents and targets 20 roles: main integrator, chapter workers for Chapters 0 and 2-16, delayed Chapter 1 summary worker, independent `verification_agent`, and independent `reflection_reviewer`.
   - Critical chapters require work/verification separation before final release: Chapters 1, 3, 4, 5, 6, 9, 13, 14, and 16.
   - When host policy and user request allow parallel agents, assign each role or dimension to a child agent that writes its assigned file artifact and replies only `DONE`.
   - If parallel agents are unavailable, perform the same roles sequentially, record `agentMode=collapsed-sequential`, and still write per-role or per-dimension JSON/Markdown artifacts.
   - Never paste large raw search results into the main response.
   - Workers should follow the generated search plan: use query variants, domain boosts, freshness hints, and minimum evidence gates per dimension.
   - During Recall Mode, workers must not silently discard project-like leads. Write all candidate leads to `data/renewable-market/{slug}-candidate_project_pool.json` or to depth files that the main agent merges into that pool.
   - Search entry coverage must include fixed seed templates, historical baseline entries, authority-source enumeration, and dynamically discovered project, developer, SPV, OEM, EPC, finance, policy/legal, region, local-language, Chinese-language, and adjacent-opportunity entries. Each lane must either produce candidate/frontier records or record a clear no-find/gap note.
   - Apply frontier priority before scheduling follow-up searches: P0 wind project/commercial-core and P1 policy/grid/revenue entries expand automatically; P2 supply-chain/logistics/local-manufacturing/finance background is one-hop; P3 storage, solar, hydrogen, ammonia, methanol, I-REC, CBAM, and industrial green-power traces expand only when they affect wind opportunities; P4 generic energy macro is deferred background.
   - For P0/P1 entries, assign `executor_role` and a different `evaluator_role` before ledger admission. The executor writes the collection/synthesis artifact; the evaluator writes the independent verification artifact and sets `evaluation_status` to `passed`, `passed_with_gaps`, or `blocked`.
   - Recall Mode must run at least five rounds: fixed seed templates, baseline/authority enumeration, entity expansion, reverse-source search, then alias/anomaly/source-backtrace search. After round five, continue until the P0/P1 high-priority frontier is exhausted.
   - Every depth record should include `searchPass` or `searchPasses` such as `english-broad`, `official-language`, `china-capital-local-language`, `new-entrant`, `source-backtrace`, `anomaly-hunter`, or `chrome-verification`.
   - Treat Chrome MCP as an integrated verification lane, not only a debug check: when Exa finds a candidate official PDF/table/map/dynamic page, verify it in Chrome MCP when available and record the verification method.
   - Treat Exa search/quota/no-more-results boundary as a handoff trigger, not a completion condition. When Exa reaches a boundary and Chrome MCP has not run, enter `chrome-verification` or record `tool_unavailable=chrome-mcp`, affected fields, and `verification_status=pending` or `blocked`.
   - Key confirmed-pipeline fields must be verified later by `chrome-mcp`, `exa-fetch`, or `manual-file`; `exa-search` discovery alone is not enough for final ledger admission.

5. **Detect frontier convergence**
   - Do not stop before at least five Recall Mode rounds are complete.
   - Do not stop because the model feels the search is sufficient. Stop only when all P0/P1 high-priority frontier entries are searched, classified, or explicitly deferred; all baseline seed entities are classified; all authority source categories are attempted; and two consecutive post-minimum rounds produce zero new P0/P1 entries.
   - P2/P3/P4 entries do not block convergence unless promoted to P0/P1 by evidence that they affect wind capacity, project status, PPA/tariff, grid, offtake, procurement, OEM/EPC, or project finance.
   - Record convergence, searched rounds, new entries, stalled rounds, deferred entries, and remaining gaps in `index.json` and `{slug}-frontier_convergence.json`.

6. **Verify, reconcile, and aggregate data**
   - Treat `candidate_project_pool.json` as the required recall artifact. Every candidate must be carried forward into a ledger treatment such as confirmed, watchlist, duplicate, rejected, or unresolved; never make old leads disappear without a classification.
   - Build source-specific verification artifacts such as `{slug}-source_trace.json` and conclusion-level `{slug}-evidence_table.json` before ledger admission. `evidence_table` must follow `schema/evidence-table.schema.json` and record evidence boundaries for project stage, capacity, OEM, tariff, financing, PPA/offtaker, procurement window, and Mingyang relevance.
   - Split aggregation into two required passes. First, merge all depth files and candidate records into the full `{slug}.json` using the rich schema in `references/data-model.md`; preserve project-card fields such as coordinates, site area, annual generation, annual CO2 reduction, investment, turbine model/count/specs, storage, logistics, community impact, and personnel/developer data when found.
   - Validate the full `{slug}.json` before deriving downstream files. If a rich field exists in a depth file but is absent from the matching main JSON project, update the main JSON or mark the field explicitly as `not found`, `unavailable`, or `not applicable` with a gap note.
   - Build `{slug}-project_ledger.json` or `{slug}-pipeline-ledger.json` from the validated main JSON, not directly as a replacement for it. The ledger owns canonical project IDs, local/English/Chinese aliases, dedupe keys, source traces, evidence layers, confirmed/watchlist/rejected state, merge/reject decisions, `Opportunity MW`, and V4 fields in `schema/project-ledger.schema.json`.
   - Treat `{slug}.json` as the rich report data source, `depth/*.json` as the required cross-read/fallback evidence layer, and `{slug}-pipeline-ledger.json` as the canonical dedupe/evidence registry. The ledger alone is not sufficient to write final project cards or deep-dive chapters.
   - Generate `{slug}-participant_ledger.json` after capacity reconciliation, using the already-created source/evidence artifacts so owners, developers, EPCs, OEMs, financiers, and O&M actors are tied to project role and procurement influence.
   - Generate `{slug}-source_trace.json` and `{slug}-evidence_table.json` before detailed project cards or report prose. `evidence_table` must follow `schema/evidence-table.schema.json` and record conclusion-level evidence for project stage, capacity, OEM, tariff, financing, PPA/offtaker, procurement window, and Mingyang relevance.
   - Generate `{slug}-project_cards.json` only after source/evidence artifacts exist. Project cards must follow `schema/project-card.schema.json`; unknown values may be `待核`, `unavailable`, or `not found`, but required fields cannot disappear.
   - Export project rows to `{slug}.csv`; use `scripts/export_projects_csv.py` when convenient.
   - Deduplicate by canonical name, local-language aliases, translated names, location, sponsor/SPV, capacity, coordinates if available, phase boundaries, and source URL. Same-name/different-source records must be merged or explicitly rejected/watchlisted.
   - For project pipeline, classify each project evidence layer as one of: `news-announcement`, `mou-framework`, `ppa-signed`, `financing-closed`, `construction-started`, `cod-operational`.
   - For ledger status, classify every candidate as exactly one of: `operational`, `financing_closed`, `under_construction`, `ppa_signed`, `decree_backed`, `mou_or_early_stage`, `watchlist`, `duplicate`, `rejected`, or `unresolved`.
   - Admit P0/P1 candidates to the ledger only after role-separated execution/evaluation exists. `passed` may enter the appropriate ledger status when source/evidence requirements are met. `passed_with_gaps` may enter watchlist/unresolved or downgraded fields, but not confirmed capacity totals. `blocked` or `pending` cannot enter confirmed totals.
   - Policy targets, auction targets, tariff numbers, and capacity goals must include an original legal/regulator/auction backtrace or be downgraded with an uncertainty note.
   - For confirmed projects, verify these critical fields with `chrome-mcp`, `exa-fetch`, or `manual-file` before final writing when the field is present: project name/alias, capacity, status/evidence stage, owner/developer/SPV, location, COD/target COD, PPA, financing/investment, EPC/OEM/turbine, and construction start.
   - Preserve both breadth and convergence: keep all discovered project candidates in confirmed/watchlist/duplicate/rejected/unresolved buckets, but report confirmed capacity only from verified, deduplicated ledger records.
   - Calculate capacity totals, status totals, undecided OEM opportunity MW, and sales opportunity tables from the ledger, not from narrative notes.

7. **Generate reports**
   - Write `{slug}-report.md` for the full internal report.
   - Write `{slug}-lite.md` for the lite delivery report.
   - Full reports must follow the V4 0-16 chapter structure in `references/full-report-v4.md`, including report scope/evidence rules, market capacity definitions, full project ledger, key project cards, developer/decision-right structure, turbine-fit inference, OEM competition, EPC/finance/O&M/supply chain, localization, grid/storage/curtailment, tariff/bankability, procurement-window status, risks, and source-confidence appendix.
   - Do not write the full report until the V4 generation pipeline is complete: `candidate_project_pool` -> `source_trace/evidence_table` -> `project_ledger` -> `capacity_reconciliation` -> `participant_ledger` -> `oem_competition_matrix` -> `procurement_window_table` -> `detailed_project_cards` -> `full_report` -> `lite_report`.
   - Present the project pipeline in the report body as project cards grouped by status/evidence stage. Use tables only for appendices, CSV exports, or compact summary indexes.
   - Chapter 5 is an exception: the full project ledger table is required. Chapter 6 must still preserve complete project cards.
   - Before writing each project card or project/developer chapter, cross-read the matching `depth/*.json` records named in `sourceTrace` or `mergedFromDepthRecords`. Check at minimum annualGenerationGWh, annualCO2ReductionTonnes, investmentUSD, turbineModel, turbineCount, storageMWh, coordinates, turbine specs, logistics route, community/land impact, biodiversity/bird protection, jobs/local employment, and personnel/developer data.
   - If a depth file contains a richer field than `{slug}.json`, update `{slug}.json` and rerun integrity validation before writing the report. Do not silently downgrade to `{slug}-pipeline-ledger.json` when the main JSON is incomplete.
   - Do not include a Regional Benchmark Comparison section unless the user explicitly requests a benchmark.
   - For controlled PDF layout, prefer Markdown as the authoring source, convert Markdown to HTML with a controlled template, then render HTML to PDF. Direct HTML authoring is acceptable only for highly designed final decks or when Markdown cannot represent required layout.
   - Report CSS should use Microsoft YaHei (`微软雅黑`, `Microsoft YaHei`) for Chinese text and Times New Roman for English/Latin text; tables should use fixed widths, explicit column alignment, and print CSS to avoid broken pipeline tables.
   - Render PDFs when the environment has a working HTML/PDF stack; otherwise deliver MD and HTML and explain the limitation. On Windows native, prefer PowerShell/Python steps over Bash or `make.sh`.
   - Full/lite reports must cite sources and include data-confidence notes.
   - Market participants must be tied to projects and procurement influence. Do not list owners, OEMs, EPCs, financiers, or adjacent-energy actors unless their role, project link, competitive position, or sales relevance is stated.
   - In the full report, Mingyang/MySE content must be factual relevance and pending verification: project, Opportunity MW, current OEM status, procurement route/window, decision maker, influencers, technical fit, risk, and evidence confidence. Put recommended actions in a separate executive/action brief only when requested.
   - Write the executive summary after Chapters 2-16 are current, then run a backpropagation pass: compare every summary number, project count, capacity total, risk, procurement-window statement, and confidence note against the latest canonical ledger and synthesis. If any downstream chapter changed, update the summary before release.

8. **Validate and hand off**
   - Validate JSON syntax, CSV row count, and search coverage; use `scripts/search_orchestration.py validate` when a search plan exists.
   - Run `scripts/validate_market_integrity.py` or its PowerShell wrapper to identify duplicate candidates, missing source fields, missing source-to-final metadata, and policy target records without legal backtrace.
   - In Heavy Workflow, run reflection loops after search planning, evidence collection, ledger aggregation, and final report drafting. A stage may advance only when the reviewer reports no critical blockers and the stage meets the thresholds in `review_gates.md`; score improvement alone is not enough.
   - Confirm both report files exist.
   - If PDFs were requested, confirm both PDFs exist or document why PDF rendering was skipped.
   - Summarize new files, coverage, gaps, and next update path.
   - Ensure every key fact contains source URL, date, confidence, and uncertainty notes.

## Default Output Paths

For `{slug}=uzbekistan-wind`:

```text
data/renewable-market/
├── index.json
├── uzbekistan-wind.json
├── uzbekistan-wind.csv
├── depth/
│   ├── project-pipeline.json
│   ├── ifi-financing.json
│   ├── technology-epc.json
│   └── carbon-hydrogen.json
├── uzbekistan-wind-report.md
├── uzbekistan-wind-lite.md
├── uzbekistan-wind-report.pdf
└── uzbekistan-wind-lite.pdf
```

Also produce:

- `data/renewable-market/{slug}-pipeline-ledger.json`
- `data/renewable-market/{slug}-seed_entities.json`
- `data/renewable-market/{slug}-search_frontier.json`
- `data/renewable-market/{slug}-discovered_entries.json`
- `data/renewable-market/{slug}-authority_sources.json`
- `data/renewable-market/{slug}-candidate_project_pool.json`
- `data/renewable-market/{slug}-developer_project_map.json`
- `data/renewable-market/{slug}-source_trace.json`
- `data/renewable-market/{slug}-frontier_execution_review.json`
- `data/renewable-market/{slug}-project_ledger.json`
- `data/renewable-market/{slug}-project_cards.json`
- `data/renewable-market/{slug}-participant_ledger.json`
- `data/renewable-market/{slug}-oem_competition.json`
- `data/renewable-market/{slug}-procurement_window.json`
- `data/renewable-market/{slug}-evidence_table.json`
- `data/renewable-market/{slug}-risk_matrix.json`
- `data/renewable-market/{slug}-tracking_watchlist.json`
- `data/renewable-market/{slug}-v4_agent_plan.json`
- `data/renewable-market/report_chapters/{slug}-chapter-*.md`
- `data/renewable-market/chapter_verification/{slug}-chapter-*-verification.json`
- `data/renewable-market/{slug}-search_coverage_matrix.md`
- `data/renewable-market/{slug}-frontier_convergence.json`
- `data/renewable-market/{slug}-capacity_reconciliation.md`
- `data/renewable-market/{slug}-contradiction_queue.json`
- `data/renewable-market/{slug}-integrity.json`
- `data/renewable-market/{slug}-source-audit.json` in Heavy Workflow
- `data/renewable-market/chapter_verification/` artifacts for critical V4 chapters in Heavy Workflow
- `data/renewable-market/{slug}-reflection-review.json` in Heavy Workflow
- `data/renewable-market/{slug}-gap-tasks.json` in Heavy Workflow when gaps remain

## Review Gates

Before final writing, apply `review_gates.md`:

1. **Continuity Gate**: every final summary claim must trace back to the latest canonical ledger or reviewed synthesis, and stale summaries must be rewritten after downstream chapter updates.
2. **Evidence Gate**: unsupported claims and weak single-source claims cannot become high-confidence final claims; every final conclusion must pass this gate.
3. **Critical Field Gate**: confirmed-pipeline critical fields must have `chrome-mcp`, `exa-fetch`, or `manual-file` verification. Otherwise downgrade the project/field to watchlist or uncertainty; do not leave it as a final confirmed fact.
4. **Contradiction Gate**: reconcile installed/planned/pipeline capacity, status conflicts, COD conflicts, duplicates, translated names, local-language aliases, phase confusion, and offshore/floating/onshore classification; every final conclusion must pass this gate before synthesis.
5. **Business Gate**: convert important facts into report implications such as capacity treatment, procurement window, product-fit relevance, risk judgment, pending verification, or executive decision context.
6. **Reflection Gate**: require the independent reviewer to score each stage, list critical blockers, and generate gap tasks. Do not advance a stage merely because its score improved; it must meet the stage threshold and have zero critical blockers.
7. **Executive Gate**: compress final output into three evidence-backed core judgments and avoid vague potential claims unless quantified and qualified.

## Quality Gates

Run these checks when files are produced. Use the host's Python launcher (`python3` on Unix-like systems, `py -3` on Windows):

```text
python -m json.tool data/renewable-market/index.json > <temp>/renewable-index.validated.json
python -m json.tool data/renewable-market/{slug}.json > <temp>/renewable-main.validated.json
python -m json.tool data/renewable-market/{slug}-project_ledger.json > <temp>/renewable-project-ledger.validated.json
python -m json.tool data/renewable-market/{slug}-project_cards.json > <temp>/renewable-project-cards.validated.json
python -m json.tool data/renewable-market/{slug}-evidence_table.json > <temp>/renewable-evidence-table.validated.json
python skills/renewable-market-research/scripts/export_projects_csv.py data/renewable-market/{slug}.json data/renewable-market/{slug}.csv
python skills/renewable-market-research/scripts/validate_market_integrity.py data/renewable-market/{slug}.json --depth-dir data/renewable-market/depth --candidate-pool data/renewable-market/{slug}-candidate_project_pool.json --project-ledger data/renewable-market/{slug}-project_ledger.json --project-cards data/renewable-market/{slug}-project_cards.json --evidence-table data/renewable-market/{slug}-evidence_table.json --full-report data/renewable-market/{slug}-report.md --output data/renewable-market/{slug}-integrity.json
```

On Windows native, use the PowerShell commands in `references/windows-native.md`. Mark unavailable checks as skipped only with an explicit environment reason.

## Windows Native Quick Commands

When running on Windows native, read `references/windows-native.md` and use PowerShell/Python commands such as:

```powershell
New-Item -ItemType Directory -Force data/renewable-market/depth | Out-Null
py -3 -m json.tool data/renewable-market/index.json > $env:TEMP\renewable-index.validated.json
.\skills\renewable-market-research\scripts\export_projects_csv.ps1 -InputJson .\data\renewable-market\{slug}.json -OutputCsv .\data\renewable-market\{slug}.csv
.\skills\renewable-market-research\scripts\validate_market_integrity.ps1 -MarketJson .\data\renewable-market\{slug}.json -DepthDir .\data\renewable-market\depth -CandidatePool .\data\renewable-market\{slug}-candidate_project_pool.json -ProjectLedger .\data\renewable-market\{slug}-project_ledger.json -ProjectCards .\data\renewable-market\{slug}-project_cards.json -EvidenceTable .\data\renewable-market\{slug}-evidence_table.json -FullReport .\data\renewable-market\{slug}-report.md -Output .\data\renewable-market\{slug}-integrity.json
```

Do not require WSL, Git Bash, `make.sh`, or Bash-only syntax for the standard workflow.

## Multi-Agent Harness Rules

When running long-form market research, use a harness-based multi-agent file workflow.

Default long-form profile is Heavy Workflow. Use Lite or Standard only when the user asks for speed or a smaller deliverable.

### Required Skills (when available)

1. `effective-harnesses`
   - Manage feature decomposition, task status, recovery points, and validation state.
   - Maintain `feature_list.json` and `agent-progress.md`.
2. `renewable-market-research`
   - Run market research file mode.
   - Produce depth JSON files, master JSON, CSV, project timeline CSV, full report, lite report, and PDFs.
3. `company-research`
   - Support owner/developer/competitor/EPC/logistics/crane/financing/partner analysis.

### Agent Roles and File Ownership

Main agent responsibilities:
- initialize harness and schemas
- create/update build scripts
- assign worker modules
- normalize worker outputs
- merge depth files
- build and maintain the canonical project pipeline ledger
- produce master JSON, CSV, timeline CSV, markdown reports, and PDFs
- rerun summary/conclusion backpropagation after downstream section updates
- run validations and final business judgment

Heavy Workflow uses the V4 chapter-agent profile for full reports: at least 15 logical agents, with a target topology of 20 roles. Workers may be real child agents when the host supports that pattern, or sequential lanes when it does not. The final aggregation, canonical ledger, synthesis integration, executive summary refresh, and final report assembly remain single-owner tasks under the main agent. Critical chapters require a separate verification artifact before release.

Worker agent responsibilities:
- only the assigned research module
- only the assigned `data/renewable-market/depth/*.json` files
- only evidence-backed findings

Worker agents MUST NOT:
- edit master JSON
- edit final Markdown reports
- edit PDF outputs
- edit build scripts
- edit harness files
- edit other workers' depth files

### Required Evidence and Facts Schema

Every key fact must include:
- `statement`
- `sources[]` with `url`, `title`, `publisher`, `accessedAt`, `sourceLanguage`, `collectionMethod`
- `confidence`
- `uncertainty`

Facts schema:

```json
{
  "topic": "...",
  "facts": [
    {
      "statement": "...",
      "sources": [],
      "confidence": "high | medium | low",
      "uncertainty": "..."
    }
  ]
}
```

Project pipeline timeline schema:

```json
{
  "project": "...",
  "stage": "...",
  "auctionDate": "...",
  "ppaDate": "...",
  "fidDate": "...",
  "constructionStart": "...",
  "codOrTargetCod": "...",
  "timingConfidence": "...",
  "timingUncertainty": "..."
}
```

### Required Outputs (Kazakhstan wind example)

- `data/renewable-market/index.json`
- `data/renewable-market/kazakhstan-wind.json`
- `data/renewable-market/kazakhstan-wind.csv`
- `data/renewable-market/kazakhstan-wind-pipeline-ledger.json`
- `data/renewable-market/kazakhstan-wind-integrity.json`
- `data/renewable-market/kazakhstan-wind-project-timeline.csv`
- `data/renewable-market/kazakhstan-wind-report.md`
- `data/renewable-market/kazakhstan-wind-lite.md`
- `data/renewable-market/kazakhstan-wind-report.pdf`
- `data/renewable-market/kazakhstan-wind-lite.pdf`

### Main-Agent Normalization Layer

Main agent should implement/maintain:
- `normalize_sources`
- `normalize_facts`
- `humanize_value`
- `dedupe_projects`
- `merge_project_aliases`
- `build_pipeline_ledger`
- `policy_legal_backtrace`
- `refresh_summary_from_latest_ledger`
- `project_timeline_records`
- `validate_depth_files`
- `build_search_plan`
- `validate_search_coverage`
- `validate_market_integrity`

### Report Quality Gates

- Markdown/CSV/PDF must be human-readable outputs, not raw JSON object dumps.
- Standard and Deep full reports must follow the V4 0-16 chapter structure in `references/full-report-v4.md`; a 6-section compressed structure is acceptable only for Lite mode.
- Report-body project pipeline must be rendered as project cards grouped by status/evidence stage, not as a large table.
- Regional benchmark sections are omitted by default and included only when the user explicitly requests a benchmark.
- Do not render raw structures such as `{\"claim\": ...}` or `{\"sources\": ...}` directly in reports.
- Keep structured evidence in JSON/depth files only.
- Missing values must be `unavailable` or `not found`.
- Any inference must be marked as `assumption`.
- Never fabricate sources.

### Acceptance Commands

Use commands like:

```text
uv run python scripts/build_kazakhstan_wind_outputs.py
uv run python -m json.tool data/renewable-market/index.json
uv run python -m json.tool data/renewable-market/kazakhstan-wind.json
uv run python skills/renewable-market-research/scripts/search_orchestration.py validate --plan data/renewable-market/kazakhstan-wind-search-plan.json --depth-dir data/renewable-market/depth --output data/renewable-market/kazakhstan-wind-search-coverage.json
uv run python skills/renewable-market-research/scripts/validate_market_integrity.py data/renewable-market/kazakhstan-wind.json --depth-dir data/renewable-market/depth --output data/renewable-market/kazakhstan-wind-integrity.json
```

And verify:
- all depth JSON files parse
- master JSON parses
- rich project-card fields found in depth files are propagated into the master JSON or explicitly marked unavailable
- CSV opens
- canonical pipeline ledger exists and duplicate candidates are resolved or explicitly watchlisted/rejected
- project timeline CSV exists
- full and lite Markdown reports exist
- PDFs exist when PDF toolchain is available
- executive summary was refreshed after the latest project ledger and synthesis updates
- reports do not contain raw JSON object artifacts
