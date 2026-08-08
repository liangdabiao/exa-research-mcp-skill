# Renewable Market Research Upgrade Plan

## Phase 1: Repository Audit

Current assets:

- `SKILL.md`: main portable skill definition with file-mode market research, standard workflow, output paths, validation, and multi-agent harness rules.
- `agents/openai.yaml`: Codex/OpenAI UI metadata and Exa/Chrome MCP dependencies.
- `references/data-model.md`: market JSON, depth JSON, CSV, and index examples.
- `references/file-mode-research.md`: worker collection workflow, source priority, convergence, and child-agent prompt template.
- `references/search-orchestration.md`: deterministic search-plan and coverage validation guidance.
- `references/pdf-pipeline.md`: full/lite report sections and PDF-generation caveats.
- `references/windows-native.md`: Windows-native Python/PowerShell operating rules.
- `scripts/`: Python and PowerShell helpers for search orchestration and project CSV export.

What works well:

- The skill already supports stateful file-mode research instead of one-shot chat reports.
- Existing references require citations, confidence notes, uncertainty notes, and source URLs.
- Search orchestration and coverage validation are already separated from final writing.
- The project pipeline is already treated as structured data and can be exported to CSV.
- Windows-native operation is explicitly supported.

New usage feedback to address:

- Project pipeline data can scatter across dimensions if no canonical ledger is enforced.
- Executive summaries can become stale after downstream chapters update.
- Search can miss projects when local-language, Chinese-capital, new-entrant, legal-backtrace, or anomaly-hunter passes are not mandatory.
- Same-name/different-source records need executable dedupe review, not only cross-reference awareness.
- Confirmed-pipeline critical fields must be verified by Chrome MCP or original-file fetch, not by Exa search snippets alone.
- Full reports should preserve the V4 0-16 country wind-market status depth instead of collapsing into a 6-section compressed report.
- Project pipeline cards need richer card fields: coordinates, land footprint, turbine specs, generation, CO2 reduction, jobs, biodiversity, and community impacts when evidence exists.

Gaps to close:

- Add explicit workflow modes for lite, standard, and deep market intelligence.
- Separate writer, reviewer, synthesis, and executive roles.
- Formalize review gates so unsupported claims cannot enter final outputs.
- Add machine-readable schemas for findings, evidence, projects, decisions, reviews, and reports.
- Add role prompts that produce repeatable structured outputs.
- Make product-fit, sales-action, and executive judgment first-class deliverables.
- Add HTML-first PDF guidance so tables and fonts can be controlled reliably.

## Phase 2: Workflow Layer

Add reusable workflow documents and role prompts:

- `workflow.md`
- `agent_roles.md`
- `review_gates.md`
- `prompts/*.md`

Backward compatibility requirement: keep the existing depth JSON, master JSON, CSV, full report, lite report, and PDF outputs. The workflow layer should guide when and how those outputs are produced, not replace them.

## Phase 3: Structured Schemas

Add JSON schemas under `schema/` for:

- evidence records
- findings
- projects
- decisions
- reviews
- reports

Each agent output should remain machine-readable and include `agent_name`, `task_scope`, `findings`, `evidence`, `confidence`, `uncertainty`, `rejected_claims`, `business_implications`, and `next_questions`.

## Phase 4: Review Gates

Create explicit gates for:

1. Evidence quality.
2. Contradictions and duplicate project logic.
3. Business usefulness.
4. Executive compression.

## Phase 5: Workflow Modes

Define:

- Lite Workflow for quick market checks.
- Standard Workflow for country-level wind/renewable reports.
- Deep Workflow for strategic questions with multiple review loops and assumption registers.

## Phase 6: Skill Definition Update

Update `SKILL.md` so the skill is positioned as a decision workflow for evidence-based renewable market judgment, project pipeline verification, product-fit analysis, and sales-action generation—not merely a report generator.

## Phase 7: Example Run

Add `examples/kazakhstan_2026_2030/` with goal, scope, and expected outputs for evaluating whether Kazakhstan's 2026-2030 wind market is worth Mingyang/MySE resource allocation.

## Validation Checklist

- Run the Codex skill validator for the skill directory.
- Validate all JSON schema files with `python3 -m json.tool`.
- Confirm portable `SKILL.md` frontmatter contains only `name` and `description`.
- Confirm OpenAI metadata stays aligned with the skill definition.
- Confirm no workflow instruction requires Bash-only tooling for normal operation.

## Remaining TODOs

- Add optional helper scripts for Markdown-to-HTML conversion and HTML-to-PDF rendering if future users want an executable pipeline.
- Add sample JSON outputs for a completed Kazakhstan run after real evidence collection is performed.
- Expand project-level validation beyond duplicate candidates to check status conflicts, COD conflicts, phase boundaries, and confirmed-pipeline eligibility.

## Implementation Status

- Phase 1 was performed as an audit before modifications: existing skill files, references, scripts, metadata, and output model were inspected and summarized above.
- Existing skill capabilities were preserved: file-mode collection, depth JSON, master JSON, CSV export, full/lite Markdown reports, optional PDF outputs, search planning, coverage validation, and Windows-native operation remain part of the workflow.
- New workflow files are additive and do not replace the legacy research-output contract.
- Agent prompts now include explicit allowed and prohibited actions.
- Final conclusions must pass the Evidence Gate and Contradiction Gate before synthesis or executive compression.
- The Kazakhstan example is scoped to Kazakhstan 2026-2030; peer-country comparison is not part of the default scope.
- Search orchestration now includes official-language, Chinese-capital/local-name, new-entrant, policy-law-backtrace, and anomaly-hunter passes.
- Source-to-final continuity now requires a canonical project ledger, integrity validation, and final summary backpropagation.
- Integrity validation now fails confirmed-pipeline records whose present critical fields lack `chrome-mcp`, `exa-fetch`, or `manual-file` verification.
- Report guidance now requires the V4 0-16 full report structure with scope/evidence rules, capacity definitions, full project ledger, key project cards, developer/decision-right structure, turbine-fit inference, OEM panorama, EPC/finance/O&M/supply chain, localization, grid/storage/curtailment, tariff/bankability, procurement-window status, risks, and source-confidence appendix.
- Search orchestration now includes market key indicators/time series, auction tariff comparison, anchor developer deep dives, and Chinese developer deep dives as default non-benchmark dimensions.
