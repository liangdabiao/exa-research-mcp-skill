# Search Orchestration and Coverage Gates

This skill uses a lightweight Python orchestration layer to keep long-form market research search coverage complete without turning the repository into a fixed crawler.

## Borrowed Pattern

The external `search-layer` project demonstrates several useful ideas for search completeness:

- classify the search intent before choosing a tool lane;
- expand one user question into multiple subqueries;
- run multiple search lanes instead of trusting one provider;
- deduplicate and rank by keyword match, freshness, and authority;
- keep fallback behavior explicit so one provider failure does not block the run;
- validate outputs with code instead of relying on chat memory.

For this repository, adapt those ideas to renewable-market research rather than copying provider-specific code. Search runs in two stages:

1. **Recall Mode**: maximize candidate discovery through dynamic frontier expansion. Search broadly, extract new entry names from results, enqueue them in `search_frontier.json`, and write every project-like lead to `candidate_project_pool.json`. Do not decide truth or discard early-stage items in this stage.
2. **Verification Mode**: turn the candidate pool into ledger-grade records. Merge aliases, classify status, verify source traces, backtrace laws/tariffs, and compute capacity totals from the ledger.

The standard tool lanes are:

1. Exa semantic search for broad discovery.
2. Exa fetch for known URL extraction.
3. Exa deep search only for complex comparison/status/exploratory gaps when quota allows.
4. Sanitized Chrome MCP for dynamic pages, tables, maps, official PDFs, and visual verification.
5. General browser/search fallback only when the previous lanes are insufficient.

The search plan also requires explicit search passes, not just tool lanes:

- `english-broad`: English discovery and source mapping.
- `official-language`: country official/local language search.
- `china-capital-local-language`: Chinese capital, EPC/OEM/developer/financier terms plus local project names.
- `new-entrant`: new SPVs, new developers, recent awards, corporate offtakers, and first-time market actors.
- `source-backtrace`: reverse target/tariff/capacity claims to original law, decree, order, auction, regulator, or grid documents.
- `anomaly-hunter`: transliterations, misspellings, renamed phases, map/table/PDF-only mentions, and records outside known developer patterns.
- `chrome-verification`: browser verification for dynamic, PDF, table, map, or bot-sensitive sources discovered by Exa or general search.

For confirmed-pipeline critical fields, only `chrome-mcp`, `exa-fetch`, or `manual-file` count as final verification. `exa-search` is discovery-only for those fields. This means Recall Mode may accept weak or partial leads, but Verification Mode must keep them out of confirmed ledger totals until field-level support exists.

Exa search boundary is not a completion condition. If Exa reports search boundary, quota boundary, no more results, or unreliable extraction for dynamic/PDF/table/map sources, the runner must hand off candidate URLs to `chrome-verification` or record `tool_unavailable=chrome-mcp` with affected fields and `verification_status=pending` or `blocked`. Without one of those outcomes, project ledger release and full-report release remain blocked.

## Dynamic Search Frontier

Recall Mode must not assume entry names are complete at initialization. The scheduler or equivalent runner should maintain these files:

| File | Purpose |
|---|---|
| `seed_entities.json` | Fixed seed templates, runtime known projects, and historical baseline entries. |
| `search_frontier.json` | Dynamic queue of all seed, historical, authority-source, and newly discovered entries. |
| `discovered_entries.json` | New entities extracted from every search result before dedupe/enqueue. |
| `authority_sources.json` | Enumerated government, IFI, developer, OEM/EPC, Chinese, and local-language source pools. |
| `search_coverage_matrix.md` | Human-readable coverage matrix by entry/source category. |
| `frontier_convergence.json` | Machine-readable convergence state and stop-condition evidence. |

Fixed seed templates cover entry types, not complete names: country plus wind project, wind farm, PPA, auction, developer, turbine supplier, EPC, IFI, transmission, grid connection, BESS, local-language templates, and Chinese-language templates. Historical names from prior reports may be loaded as baseline seeds, but they are not trusted facts; every baseline seed must be searched or classified.

Every search result must be mined for new entries. Extract project names, developers, SPVs, OEMs, EPCs, lenders, law/decree IDs, offtakers, grid entities, regions, authority-source pages, supply-chain/logistics/local-manufacturing signals, adjacent-opportunity signals, and macro-energy background. Add each non-duplicate entry to `search_frontier.json` with aliases, source, origin, search round, `priority_level`, `wind_linkage`, `expansion_allowed`, `expansion_depth`, `defer_reason`, `promote_reason`, generated queries, status, classification, and parent entry IDs.

Recall Mode admission is intentionally loose. If a lead contains a project name plus any one or more of capacity, actor, location, agreement, decree, news, financing, PPA/grid clue, OEM/EPC clue, or adjacent wind-opportunity clue, record it in the candidate pool with sources and uncertainty. Do not delete it because it is weak, early-stage, duplicated, or contradicted.

## Frontier Priority Boundary

High recall must be bounded by priority rather than early deletion. The scheduler records broad discoveries, but only wind-relevant entries keep expanding:

| Priority | Scope | Expansion rule | Convergence/report treatment |
|---|---|---|---|
| P0 | Wind projects, developers, SPVs, capacity, status, OEM, EPC, PPA, and project finance | Auto-expand until searched, classified, or explicitly deferred | Blocks Verification Mode while pending; candidate pool and ledger treatment required |
| P1 | Policy, tariff, grid, offtaker, decree, auction, and PPA context tied to wind | Auto-expand while linked to wind project value, bankability, grid access, or revenue | Blocks Verification Mode while pending; informs policy/PPA/tariff sections |
| P2 | Supply chain, local manufacturing, logistics, and financial-institution background | One-hop expansion only unless promoted by direct wind linkage | Preserved as enabler context; does not block convergence by default |
| P3 | BESS, solar hybrid, hydrogen, ammonia, methanol, carbon certificates, I-REC, CBAM, and industrial green-power demand | Expand only when the source shows impact on wind configuration, interconnection, PPA/tariff, offtake, procurement, or OEM opportunity | Preserved as adjacent-opportunity evidence; does not become a standalone market report |
| P4 | Broad power-sector, gas, coal, hydro, desalination, and macro-energy context without wind linkage | Defer by default; do not expand | Keep out of the report body unless later promoted by wind-linked evidence |

Promotion requires a source-level reason. A P2/P3/P4 entry may move up only when evidence links it to wind capacity, project status, PPA/tariff, grid, offtake, procurement, OEM/EPC, or project finance. Verification Mode cannot fix infinite frontier drift; this priority gate must run before scheduling follow-up searches.

## P0/P1 Execution And Evaluation Gate

P0/P1 entries require role-separated execution and evaluation before ledger admission. This is a hard gate for ledger build and final reporting, not a reason to delete candidates during Recall Mode.

Each P0/P1 frontier entry must carry:

- `evaluation_required: true`
- `executor_role`
- `evaluator_role`
- `execution_artifact`
- `evaluation_artifact`
- `evaluation_status`

`executor_role` must differ from `evaluator_role`. If the host supports real child agents, use separate agents. If it does not, run separate executor and evaluator passes in the same session and write separate artifacts. P2/P3/P4 entries use `evaluation_required: false` and `evaluation_status: not_required` unless promoted to P0/P1.

Allowed P0/P1 evaluation outcomes:

- `passed`: may enter the appropriate ledger status when evidence/source requirements are also met.
- `passed_with_gaps`: may enter watchlist/unresolved or downgraded fields, but not confirmed capacity totals.
- `blocked`: must remain unresolved/rejected/watchlist with a blocker reason; it cannot enter confirmed totals.
- `pending`: cannot enter the ledger except as an explicitly pending candidate.

## Minimum Recall Rounds

Recall Mode must run at least five rounds:

1. Fixed seed template search: country plus wind/project/PPA/auction/developer/OEM/EPC/IFI/grid/BESS.
2. Historical baseline and authority-source enumeration.
3. Entity expansion search for newly extracted projects, companies, SPVs, decree IDs, regions, and institutions.
4. Reverse-source search from OEM, EPC, IFI, Chinese-language, and local-language sources.
5. Alias, anomaly, source-backtrace, and remaining P0/P1 high-priority frontier search.

After round five, continue searching until all P0/P1 high-priority frontier entries are searched, classified, or explicitly deferred; all baseline seeds are classified; all authority source categories are attempted; and two consecutive post-minimum rounds produce zero new P0/P1 entries. P2/P3/P4 entries may remain deferred without blocking Verification Mode unless they are promoted.

## Verification Categories

Verification Mode must classify every candidate into exactly one ledger treatment:

- `operational`
- `financing_closed`
- `under_construction`
- `ppa_signed`
- `decree_backed`
- `mou_or_early_stage`
- `watchlist`
- `duplicate`
- `rejected`
- `unresolved`

The goal is not merely to find projects. It is to reconcile contested naming, status, legal basis, and capacity so cases such as renamed phases, developer portfolio claims, decree-only projects, and duplicate aliases are carried into the ledger with an explicit decision.

## Planning Script

Use `scripts/search_orchestration.py` to generate a deterministic search plan. It does not call external APIs; it creates the dimensions, recall entry categories, dynamic frontier contract, query variants, intended freshness, domain boosts, scoring weights, output files, workflow phases, and minimum evidence gates that workers or a JS scheduler must satisfy.

Regional/peer-country benchmark is excluded by default. Add `--include-benchmark` only when the user explicitly asks for regional comparison.

The standard plan includes depth lanes needed for the V4 0-16 full report in `references/full-report-v4.md`, including report scope/evidence rules, market key indicators/time series, capacity segmentation, full project ledger, project cards, developer/decision-right structure, turbine-fit inference, OEM panorama, EPC/finance/O&M/supply chain, localization, logistics/installation, grid/storage/curtailment, tariff/bankability, procurement-window status, risk matrix, and source-to-final evidence.

For wind-market tasks, the search plan must preserve benchmark-style breadth while final reporting remains ledger-constrained. Broad discovery should surface the full project universe, market participants, OEM/EPC/finance actors, and adjacent opportunity signals. The final report should then separate confirmed pipeline, watchlist, duplicate/merged, rejected, unresolved, official targets, and optimistic scenarios instead of treating all discovered records as confirmed capacity.

Adjacent lanes for storage, solar PV, green hydrogen, ammonia, methanol, I-REC, CBAM, or industrial green-power demand should collect only the facts that affect wind project value, PPA/tariff economics, interconnection, procurement route, OEM opportunity, or sales entry.

Example:

```text
python skills/renewable-market-research/scripts/search_orchestration.py plan \
  --country Kazakhstan \
  --technology wind \
  --audience "Mingyang OEM commercial entry" \
  --official-languages "Kazakh,Russian" \
  --known-projects "Sho'rkul,Zhanatas,Arkalyk" \
  --slug kazakhstan-wind \
  --output data/renewable-market/kazakhstan-wind-search-plan.json
```

Windows PowerShell:

```powershell
.\skills\renewable-market-research\scripts\search_orchestration.ps1 plan `
  --country Kazakhstan `
  --technology wind `
  --audience "Mingyang OEM commercial entry" `
  --official-languages "Kazakh,Russian" `
  --known-projects "Sho'rkul,Zhanatas,Arkalyk" `
  --slug kazakhstan-wind `
  --output data\renewable-market\kazakhstan-wind-search-plan.json
```

When explicitly requested:

```text
python skills/renewable-market-research/scripts/search_orchestration.py plan \
  --country Kazakhstan \
  --technology wind \
  --include-benchmark \
  --output data/renewable-market/kazakhstan-wind-search-plan.json
```

## Worker Execution Contract

For each plan dimension, the worker should:

- run the listed query variants;
- use Exa first, then Chrome MCP for source verification and dynamic/PDF/table evidence;
- write only its assigned `data/renewable-market/depth/<dimension>.json` file;
- include `topic`, `facts`, `sources`, `confidence`, and `uncertainty`;
- record `collectionMethod` as `exa-search`, `exa-fetch`, `exa-deep-search`, `chrome-mcp`, or `general-web-search`;
- record `searchPass` or `searchPasses` for the search pass that found or verified the record;
- record `criticalFieldVerification` for confirmed-pipeline fields verified by Chrome MCP or original-file fetch;
- stop only when the dimension meets the plan's minimum evidence gate, completes required search passes, or records remaining gaps with confidence downgrades.

In Recall Mode, workers must also:

- write every project-like lead to `candidate_project_pool.json` directly or produce depth records that the main agent can merge into it;
- mark the `recallEntryCategory` and `frontierEntityId` that found the lead, such as `project`, `developer`, `spv`, `oem`, `epc`, `finance`, `law_decree`, `offtaker`, `grid_entity`, `region`, `authority_source`, or `adjacent_opportunity`;
- include enough candidate keys for later merging: name/alias, capacity if present, actor, location, source URL, and uncertainty;
- extract new entry names from every result and append them to `discovered_entries.json` for frontier dedupe/enqueue;
- avoid final confirmation language unless the field already has `chrome-mcp`, `exa-fetch`, or `manual-file` support.

In Verification Mode, source-specific workers should produce `source_trace.json` entries and ledger-ready evidence grades. Government/legal, IFI/finance, developer, OEM/EPC, local-language, and Chinese-language verification should each either confirm the field, create a contradiction, or record why public evidence is unavailable.

## Scheduler Gates

Keep these as hard gates for a JS scheduler or equivalent deterministic runner, not as long prose in the main skill prompt:

- `entity_extraction_gate`: every search result is scanned for project, company, SPV, law/decree, region, authority-source, and institution names.
- `alias_expansion_gate`: each material entry receives English, local-language, Russian when relevant, Chinese, transliteration, SPV, and decree/order variants where discoverable.
- `frontier_priority_gate`: every frontier entry receives P0/P1/P2/P3/P4, wind linkage, expansion allowance, expansion depth, defer reason, and promotion reason.
- `wind_relevance_gate`: adjacent P3 entries expand only with explicit wind-opportunity impact; P4 macro background is deferred by default.
- `expansion_depth_gate`: P0/P1 entries may continue to convergence, P2 and linked P3 are one-hop unless promoted, and P4 does not expand.
- `frontier_expansion_gate`: every new non-duplicate entry is recorded, but only entries allowed by the priority, wind-relevance, and depth gates are enqueued for a later search round.
- `p0_p1_execution_evaluation_gate`: P0/P1 entries require executor/evaluator role separation, execution artifact, evaluation artifact, and `evaluation_status` of `passed` or `passed_with_gaps` before ledger admission. P2-P4 do not require this unless promoted.
- `historical_entry_retention_gate`: baseline entries must be classified as confirmed, watchlist, duplicate, rejected, unresolved, or explicitly deferred.
- `authority_source_gate`: government/legal, IFI/DFI, developer, OEM/EPC, Chinese, and local-language source categories must each be attempted.
- `minimum_recall_round_gate`: Verification Mode is blocked until at least five Recall Mode rounds are complete.
- `frontier_exhaustion_gate`: after round five, Recall continues until all P0/P1 frontier entries are processed and two consecutive expansion rounds add zero P0/P1 entries.
- `verification_gate`: ledger-admitted projects must have `sourceTrace`, `evidenceGrade`, field-level verification for present critical fields, and P0/P1 execution/evaluation status that permits ledger admission.
- `exa_boundary_chrome_handoff_gate`: Exa search/quota/no-more-results boundary triggers Chrome verification or an explicit Chrome-unavailable gap record; it does not release the run by itself.
- `capacity_sum_gate`: installed, confirmed pipeline, watchlist, unresolved, and opportunity MW totals must be computed from `project_ledger`, not manually in report prose.
- `duplicate_gate`: aliases and renamed phases must merge or receive explicit duplicate/rejected decisions.
- `opportunity_gate`: OEM opportunity tables may include only projects where OEM is TBD, unconfirmed, undisclosed, or covered by a non-final framework.
- `project_ledger_schema_gate`: every ledger project must satisfy `schema/project-ledger.schema.json`.
- `capacity_reconciliation_gate`: confirmed capacity, opportunity MW, and watchlist capacity must be recalculated from `project_ledger`; national targets remain separate.
- `project_card_completeness_gate`: every key project card must satisfy `schema/project-card.schema.json`; unknown values may be marked as pending/unavailable, but fields cannot disappear.
- `evidence_boundary_gate`: every key conclusion must have conclusion-level evidence in `schema/evidence-table.schema.json`, especially project stage, capacity, OEM, tariff, financing, PPA/offtaker, procurement window, and Mingyang relevance.
- `source_trace_evidence_boundary_gate`: source_trace and evidence_table must exist before detailed project cards and report prose.
- `no_strategy_recommendation_gate`: full report prose cannot contain strategy-action language such as building a factory, must enter, recommended bid, binding an EPC, or investing resources.
- `baseline_inheritance_gate`: all baseline/candidate projects must flow into confirmed, watchlist, duplicate, rejected, or unresolved outcomes.
- `lite_from_full_gate`: lite report is extracted from the validated full-report artifacts, not generated directly from raw notes.
- `v4_minimum_agent_topology_gate`: V4 full reports default to `v4-heavy-chapter-agent` with at least 15 logical agents and a target topology of 20 roles; collapsed sequential execution must be recorded if real child agents are unavailable.
- `chapter_work_verification_gate`: every V4 chapter needs a writer owner and reviewer pass; Chapters 1, 3, 4, 5, 6, 9, 13, 14, and 16 also need an independent verification artifact before release.

## V4 Full Report Generation Pipeline

Do not let the writer jump directly from search notes to `{slug}-report.md`. The deterministic runner must enforce this order:

```text
1. candidate_project_pool
2. source_trace / evidence_table
3. project_ledger
4. capacity_reconciliation
5. participant_ledger
6. oem_competition_matrix
7. procurement_window_table
8. detailed_project_cards
9. full_report
10. lite_report
```

Current search strategy should remain high-recall but bounded: search broadly, write all leads into `candidate_project_pool`, then stop expansion when P0/P1 convergence rules pass. Do not add new open-ended search lanes to fix V4 report quality; the main bottleneck is now ledger admission, card completeness, evidence boundaries, and capacity reconciliation.

## V4 Agent Profile

The V4 full report has two schedules:

- Artifact order: the 10-step generation pipeline above.
- Role ownership: `v4-heavy-chapter-agent`, with at least 15 logical agents and a target topology of 20 roles.

The generated plan must expose `v4FullReportAgentProfile`, `v4AgentTopology`, `v4ChapterVerificationPolicy`, and `v4ChapterAgentPlan`. Use the plan to assign chapter writers, the delayed Chapter 1 summary worker, the independent `verification_agent`, and the independent `reflection_reviewer`.

Critical chapters requiring work/verification separation are 1, 3, 4, 5, 6, 9, 13, 14, and 16. All chapters require reviewer pass; critical chapters also require a separate verification artifact in `data/renewable-market/chapter_verification/`.

## Coverage Validation

After workers finish, validate search completeness before writing reports:

```text
python skills/renewable-market-research/scripts/search_orchestration.py validate \
  --plan data/renewable-market/kazakhstan-wind-search-plan.json \
  --depth-dir data/renewable-market/depth \
  --output data/renewable-market/kazakhstan-wind-search-coverage.json
```

The validation report checks that:

- every planned dimension has a depth JSON file;
- depth files are JSON arrays;
- records include required evidence fields;
- each dimension has the minimum record count and unique source URL count;
- collection methods are observable for coverage review.
- required search passes such as official-language, Chinese-capital/local-name, new-entrant, source-backtrace, anomaly-hunter, and Chrome verification are observable where the plan requires them.
- dynamic frontier, authority-source, and baseline coverage are represented in the candidate pool or documented as no-find/gap notes when a scheduler performs the broader gate check.

A `needs-work` validation result does not mean the run failed; it means the main agent must either assign gap-search workers or explicitly document why evidence is unavailable.

If validation says a required pass is missing, do not write final high-confidence conclusions for that dimension. Either run a focused gap-search worker or record a visible limitation in `index.json`, synthesis, and the report confidence notes.

## Scoring and Ranking Guidance

Use the plan's `scoringWeights` to prioritize candidate evidence:

- status/news dimensions emphasize freshness;
- comparison dimensions emphasize keyword match plus authority;
- exploratory dimensions emphasize authoritative institutional sources;
- resource-style searches emphasize exact-match official sources.

Authority boosts are only hints. Do not suppress contradictory sources. Preserve disagreements in `uncertainty` and in the final report's confidence notes.
