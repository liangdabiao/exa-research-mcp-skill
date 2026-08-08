# File-Mode Research Workflow

## Architecture

```text
User request
  -> main session decomposes dimensions and manages files
  -> seed_entities.json initializes fixed, baseline, and authority-source entries
  -> search_frontier.json tracks pending, searched, expanded, deferred, and classified entries
  -> child/sidecar researchers run high-recall frontier searches for at least five rounds
  -> each search result is mined into discovered_entries.json
  -> all project-like leads enter candidate_project_pool.json
  -> source-specific workers verify and grade candidate fields
  -> each researcher writes JSON files, then replies DONE only
  -> main session merges JSON into a rich master JSON
  -> main session derives the canonical project ledger from the validated master JSON
  -> main session updates synthesis from the master JSON plus ledger, then writes MD/PDF reports
  -> main session reruns summary/conclusion backpropagation before release
```

The main session owns orchestration, schema, master JSON aggregation, deduplication, canonical project ledger, source-to-final continuity, report writing, and validation. Research workers own one narrow dimension and must not stream raw pages back into chat.

For wind-market work, file mode should maximize search breadth while keeping final judgment narrow. Workers may discover many project-like records and adjacent opportunity facts, but the main session must first preserve them in `candidate_project_pool.json`, then classify them through the master JSON and ledger before any final count, MW total, participant ranking, procurement-window statement, or separate sales action is written.

## Two-Stage Search Discipline

Use two modes instead of mixing discovery and verification:

1. **Recall Mode**: search broadly by fixed templates, historical baseline entries, authority-source entries, and dynamically discovered project, developer, SPV, OEM, EPC, finance, policy/legal, region, local-language, Chinese-language, and adjacent-opportunity entries. Do not reject or delete early-stage, weak, duplicate, or contradictory leads during recall.
2. **Verification Mode**: use source-specific workers to verify government/legal, IFI/finance, developer, OEM/EPC, local-language, and Chinese-language evidence. Merge aliases and classify every candidate into the ledger.

Recall is allowed to be messy, but its frontier must be bounded. P0 wind project/commercial-core and P1 policy/grid/revenue entries expand automatically; P2 enablers get one-hop expansion; P3 adjacent topics expand only with explicit wind impact; P4 macro background is deferred. Ledger admission is not loose. Final reports may cite watchlist and unresolved candidates only as clearly labeled uncertainty or appendix material.

## Tool Priority

1. **Exa semantic search/fetch/deep search** when available.
   - Search: broad discovery and category filtering.
   - Fetch: known URL full-text extraction.
   - Deep search: cross-source synthesis when API quota allows.
   - Prefer highlighted/limited output, for example `maxCharacters` around 3000 per result when supported.
2. **Chrome MCP / direct browser** for dynamic pages, official PDFs, tables, maps, ecommerce listings, dashboards, and pages Exa cannot extract. When the user confirms Chrome MCP is sanitized/configured, treat it as a first-class human-browser verification tool, not merely a debug check. Use it to verify Exa-discovered official URLs, PDF tables, map-only project mentions, regulator databases, and local-language pages.
3. **Browser or general web search with proxy** as last resort when Exa and Chrome MCP are unavailable or insufficient.

Useful Exa-style categories:

| Category | Use | Example query |
|---|---|---|
| `news` | project updates and policy changes | `ACWA Power Uzbekistan wind farm update` |
| `research paper` | institutional reports and outlooks | `IRENA Uzbekistan renewable outlook` |
| `company` | developer/vendor profiles | `SANY Renewable Energy overseas Uzbekistan` |
| `financial report` | financing and annual reports | `ADB Uzbekistan wind financing loan` |

## Dimension Split

For a comprehensive country/technology task, use enough dimensions to cover standard lanes plus blind-spot hunters. For commercial-entry tasks, use a demand-first order (demand gap -> replacement space -> grid delivery -> project conversion paths):

| Dimension | Search target | Example |
|---|---|---|
| demand-load-gap | power demand growth, peak, imports/exports, deficit | `Kazakhstan electricity demand peak load import export trend` |
| market-key-indicators-timeseries | generation YoY, Q1/monthly data, wind/solar three-year trends, installed capacity, imports/exports | `Kazakhstan wind solar generation Q1 YoY statistics` |
| power-mix-replacement | current mix, retirements, thermal limits | `Kazakhstan coal retirement plan gas constraints power mix` |
| grid-storage | storage, transmission, grid bottlenecks | `Kazakhstan wind grid curtailment storage transmission plan` |
| policy-ppa-economics | auction/FIT/PPA/tariff/FX/IRR | `Kazakhstan renewable auction tariff PPA currency risk` |
| auction-tariff-comparison | project-level winning tariffs, PPA tenor, currency/indexation, award dates | `Kazakhstan wind auction winning tariff PPA cents kWh` |
| project-pipeline | all known projects and statuses | `Uzbekistan wind farm list capacity MW 2026` |
| policy-plans | targets, laws, auctions, tariffs | `Uzbekistan renewable energy target 2030` |
| developers | sponsor portfolio by company | `ACWA Power Uzbekistan portfolio wind` |
| anchor-developer-deep-dives | material developer financials, portfolio, people, partners, China cooperation, IRR assumptions | `ACWA Power Uzbekistan portfolio financials key people China EPC` |
| financing | IFI/commercial/project finance | `ADB EBRD AIIB Uzbekistan wind loan` |
| technology-epc | turbines, modules, batteries, EPC, full OEM panorama and product roadmap | `Uzbekistan wind turbine Goldwind Envision BNEF market share` |
| grid-storage | storage, transmission, grid bottlenecks | `Uzbekistan renewable grid storage transmission` |
| logistics-installation | route length/time, component dimensions/weights, crane/heavy-lift, ports/rail/road/borders | `Uzbekistan wind turbine blade transport route heavy lift crane` |
| environment-social | ESIA, land, community, biodiversity | `Zarafshan wind farm environmental impact ESIA` |
| carbon-hydrogen | I-REC, carbon, CBAM, green H2 | `Uzbekistan green hydrogen I-REC carbon CBAM` |
| china-participation | Chinese OEM/EPC/developer role | `POWERCHINA Uzbekistan wind solar EPC Goldwind` |
| chinese-developer-deep-dives | Chinese developer financials, listed code, team, Sinosure/policy-bank structures | `SANY Uzbekistan wind project revenue profit Sinosure` |
| local-language-china-capital-trace | Chinese capital plus local-language project names, SPVs, EPC notices, aliases | `Kazakhstan wind PowerChina local project name Kazakh Russian` |
| new-entrant-hunter | newly awarded developers, SPVs, first-time market actors, corporate offtakers | `Kazakhstan wind new entrant SPV PPA 2026` |
| policy-law-backtrace | reverse targets, tariffs, auctions, and capacity numbers to original laws/decrees/orders | `Kazakhstan renewable target 2030 decree order number` |
| anomaly-hunter | misspellings, transliterations, table/PDF/map-only mentions, renamed phases | `Kazakhstan wind local language misspelling PDF map` |
| regional-benchmark | optional only when the user explicitly asks to compare neighboring markets | `Uzbekistan Kazakhstan wind market comparison` |
| entry-strategy | OEM/system/developer/EPC/O&M/localization pathways | `Kazakhstan wind OEM localization manufacturing opportunities` |

## Dynamic Frontier Split

For a national wind-market run, assign workers or sequential lanes from `search_frontier.json`. Initial entries come from fixed seed templates, historical baseline seeds, and authority-source categories; later entries are extracted from search results.

| Frontier source | Required output |
|---|---|
| fixed seed templates | generic country + wind/project/PPA/auction/developer/OEM/EPC/IFI/grid/BESS search results |
| baseline seeds | every historical project, developer, SPV, OEM, EPC, finance, law/decree, region, grid/offtaker entry classified or deferred |
| authority sources | government/legal, IFI/DFI, developer, OEM/EPC, Chinese, and local-language source pools attempted |
| discovered entries | new project, company, SPV, law/decree, region, institution, supply-chain/logistics/local-manufacturing, macro-energy, and authority-source names recorded with P0-P4 priority |
| adjacent opportunity | BESS, solar hybrid, hydrogen, I-REC, CBAM, and industrial offtake only when they change wind value, grid/PPA, procurement, or OEM opportunity |

Each frontier source must output candidate/frontier records or an explicit no-find/gap note. All project-like records flow into `data/renewable-market/{slug}-candidate_project_pool.json`.

Use this priority boundary before scheduling follow-up searches:

| Priority | Meaning | Worker treatment |
|---|---|---|
| P0 | Wind project, developer, SPV, capacity, status, OEM, EPC, PPA, project finance | Search and expand until processed |
| P1 | Policy, tariff, grid, offtaker, decree, auction, PPA context | Search and expand while linked to wind economics or delivery |
| P2 | Supply chain, local manufacturing, logistics, finance background | One-hop only unless promoted by direct wind evidence |
| P3 | Storage, solar, hydrogen, ammonia, methanol, carbon/I-REC/CBAM, industrial offtake | Expand only if the source states a wind opportunity impact |
| P4 | Broad energy macro without wind linkage | Record as deferred background; do not expand |

P0/P1 entries also require execution/evaluation separation before ledger admission. Assign `executor_role` and a different `evaluator_role`. The executor writes the collection/synthesis artifact; the evaluator writes an independent verification artifact and sets `evaluation_status`. P2/P3/P4 do not need this hard gate unless promoted to P0/P1.

## Child Agent Prompt Template

For V4 full reports, use child agents whenever the host supports delegated or parallel agents. If the host cannot spawn real child agents, run the same role prompts as separate sequential lanes and record `agentMode=collapsed-sequential`. For Lite/Standard reductions, use child agents only when the scope warrants them or the user asks.

```text
Task: Research [dimension or recall entry category] for [country] [technology].
Tools: Prefer Exa semantic search/fetch/deep-search if available; fall back to browser/search.
Output file: data/renewable-market/depth/[dimension].json

Write an array of records. Each record must include:
- topic/project/company
- key facts with numbers and dates when available
- project or participant linkage when relevant: project name, MW, actor role, procurement influence, OEM/EPC/finance tie, and sales relevance
- source title, url, publisher, accessedAt
- sourceLanguage and collectionMethod
- recallEntryCategory when the record came from a Recall Mode entry point
- frontierEntityId when the record came from `search_frontier.json`
- priority_level, wind_linkage, expansion_allowed, defer_reason, and promote_reason when the record creates or updates a frontier entry
- for P0/P1 frontier entries: evaluation_required, executor_role, evaluator_role, execution_artifact, evaluation_artifact, evaluation_status, and evaluation_notes
- searchPass or searchPasses
- sourceTrace note explaining how this record should map into the canonical ledger or policy/legal backtrace
- criticalFieldVerification for confirmed-pipeline fields verified by Chrome MCP or original-file fetch
- confidence: high/medium/low
- uncertainty: what is estimated or unavailable
- notes/gaps

If the assigned dimension finds storage, solar PV, hydrogen, ammonia, methanol, I-REC, CBAM, or industrial offtake facts, record how the fact changes a wind project, portfolio, PPA/tariff, interconnection, procurement route, OEM opportunity, or sales entry. If there is no wind-market implication, mark it as adjacent context.

During Recall Mode, do not discard weak, early-stage, duplicate, contradictory, or unverified project-like leads. If the record has a project name plus at least one capacity, actor, location, agreement, decree, news, financing, PPA/grid, OEM/EPC, or adjacent-opportunity clue, preserve it for the candidate pool.

Every search result must also be scanned for new frontier entries: project names, developers, SPVs, OEMs, EPCs, lenders, law/decree IDs, offtakers, grid entities, regions, authority-source pages, supply-chain/logistics/local-manufacturing signals, adjacent-opportunity signals, and macro-energy background. Write those to `discovered_entries.json` so the scheduler can dedupe, prioritize, and enqueue only entries allowed by the frontier boundary.

Do not return raw search results in chat. After writing and validating JSON, reply only: DONE.
Do not stop until mandatory search passes for the dimension are complete. Record remaining gaps instead of silently stopping.
```

## Convergence Rule

Per dimension:

```text
Round 1: Fixed seed template search for country + wind/project/PPA/auction/developer/OEM/EPC/IFI/grid/BESS.
Round 2: Historical baseline and authority-source enumeration.
Round 3: Entity expansion search for newly extracted projects, companies, SPVs, decree IDs, regions, and institutions.
Round 4: Reverse-source search from OEM, EPC, IFI, Chinese-language, and local-language sources.
Round 5: Alias, anomaly, source-backtrace, and remaining P0/P1 high-priority frontier search.
```

Do not stop before five Recall Mode rounds are complete. After round five, continue until all P0/P1 frontier entries are searched, classified, or explicitly deferred; all baseline seed entities are classified; all authority source categories are attempted; and two consecutive expansion rounds add zero P0/P1 entries. P2/P3/P4 entries do not block convergence unless promoted by evidence that they affect wind capacity, project status, PPA/tariff, grid, offtake, procurement, OEM/EPC, or project finance.

Record convergence in `index.json` and `{slug}-frontier_convergence.json` with `rounds`, `newRecords`, `newHighPriorityEntries`, `stalledRounds`, `searchPasses`, `stoppedReason`, and `remainingGaps`.

## Master JSON and Canonical Project Ledger

Before report writing, merge all project-like records into `candidate_project_pool.json`, then into the rich `{slug}.json`. This master JSON is the report-ready data source and must preserve rich card fields from depth records, including annual generation, annual CO2 reduction, investment, turbine model/count/specs, storage, coordinates, site area, logistics, jobs/community/ESG, and personnel/developer data when found.

After the master JSON is complete, derive `{slug}-pipeline-ledger.json` from it.

Each canonical project should include:

- canonical project ID and canonical English name;
- official-language names, Chinese names, transliterations, and known aliases;
- dedupe key and duplicate-resolution notes;
- merged depth records and sourceTrace entries;
- criticalFieldVerification for present key fields, using `chrome-mcp`, `exa-fetch`, or `manual-file`;
- for P0/P1 candidates, role-separated execution/evaluation metadata from `frontier_execution_review.json`;
- evidence layers such as `mou-framework`, `ppa-signed`, `financing-closed`, `construction-started`, or `cod-operational`;
- ledger status as `operational`, `financing_closed`, `under_construction`, `ppa_signed`, `decree_backed`, `mou_or_early_stage`, `watchlist`, `duplicate`, `rejected`, or `unresolved`;
- evidence grade;
- confirmed-pipeline eligibility and exclusion reason when not eligible.

No chapter may maintain an independent project list after aggregation. Chapters read rich report fields from the master JSON and use the ledger for canonical IDs, status buckets, dedupe decisions, and watchlist/rejected/unresolved state. If a new chapter discovers a project candidate, alias, or richer field, it must update the candidate pool and master JSON first, refresh the ledger, then refresh synthesis and summary.

P0/P1 ledger admission:

- `passed`: may enter the appropriate ledger status when all other source/evidence gates pass.
- `passed_with_gaps`: may enter watchlist/unresolved or downgraded fields, but not confirmed capacity totals.
- `blocked` or `pending`: cannot enter confirmed totals and must carry a blocker/gap reason.

## Critical Field Verification

For confirmed-pipeline projects, field-level verification is mandatory. `exa-search` can discover a field, but it cannot be the final verification method.

Verify present critical fields with `chrome-mcp`, `exa-fetch`, or `manual-file`:

- project name/alias;
- capacity;
- status/evidence stage;
- owner/developer/SPV;
- location;
- COD or target COD;
- PPA;
- financing/investment;
- EPC/OEM/turbine;
- construction start.

Record the verification in `criticalFieldVerification`, `sourceTrace`, `sources`, or `evidence` with a field name and `collectionMethod`. If a critical field cannot be verified from an original page/file/browser pass, either remove the field from final confirmed claims or downgrade it to watchlist/uncertainty.

## Safety Limits

- Use file mode for all large evidence. Do not let 15+ logical roles stream evidence back to the main chat.
- Prefer 4-8 concurrent workers even when the logical role plan has 15+ agents. Queue additional chapter/research roles in batches to avoid WebSocket slow-consumer errors in some hosts.
- Store raw extracts sparingly; store source URLs and concise factual notes instead.
- If advanced Exa quota is exhausted, continue with basic search/fetch and Chrome MCP verification, then mark the limitation in `index.json`.
- On Windows native, workers should write JSON with Python or PowerShell-safe file operations; do not depend on Bash utilities.

## Chrome MCP Evidence Discipline

When using Chrome MCP as a human browser, record `collectionMethod: "chrome-mcp"` or mention Chrome MCP in `notes`. Keep only distilled facts, source URL, title, publisher, accessed date, and confidence in JSON. Do not persist cookies, credentials, private account data, or unrelated browsing history.
