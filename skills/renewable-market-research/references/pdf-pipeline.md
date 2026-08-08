# Report and PDF Pipeline

## Full Report

Default target: the V4 0-16 chapter structure in `references/full-report-v4.md`. Use the Lite Report for short delivery summaries; the Full Report is the country wind-market status master report.

Quality target: retain benchmark-style breadth while using the verified ledger to prevent overcounting. A stronger report is not the one with the most project names; it is the one that preserves discovered breadth, assigns every project candidate to confirmed/watchlist/duplicate/rejected/unresolved, ties participants to project roles, and clearly separates verified facts, assumptions, and pending verification.

The full report is not a strategy recommendation memo. Do not use it to decide whether to enter a market, build a factory, price a bid, or prescribe Mingyang/MySE actions. When Mingyang/MySE is in scope, express only factual relevance: Opportunity MW, unallocated OEM status, procurement window, decision maker, influencers, technical fit, relationship evidence, risk, and pending verification.

Required V4 sections:

0. Report scope and evidence rules
1. Executive summary
2. National power fundamentals
3. Policy, permitting, development flow, and PPA mechanism
4. Market capacity definitions and project segmentation
5. Full project ledger
6. Key project cards
7. Developers, owners, and decision-right structure
8. Wind resource, geography, and turbine-fit inference
9. OEM competition landscape
10. EPC, financiers, O&M, and supply-chain network
11. Localization and industrial policy status
12. Grid, storage, interconnection, and curtailment constraints
13. Tariff, project economics, and bankability status
14. Procurement window and decision-chain status
15. Risk matrix and constraint conditions
16. Data-source and conclusion-confidence appendix

Do not include a default `Regional benchmark comparison` section. Add a regional or peer-country benchmark only when the user explicitly asks for it.

Do not promote storage, solar PV, hydrogen, ammonia, methanol, or industrial green-power topics into independent main lines unless they affect wind project value, PPA/tariff economics, interconnection, procurement route, OEM opportunity, or sales entry. When included, explicitly state the wind-market implication.

## Executive Summary Timestamp

The executive summary must include a clear time anchor:

- report date;
- data cutoff date;
- `This-week / latest major updates` bullets when recent project, policy, tariff, grid, or developer facts changed;
- whether the update changed confirmed pipeline, opportunity MW, watchlist, procurement window, or evidence confidence.

Do not freeze the executive summary before the final ledger, tariff comparison, policy backtrace, and developer deep dives are current.

## Market Key Indicators

Include key indicators in Chapter 2 and capacity/opportunity indicators in Chapter 4. Aim for about 15-20 rows when evidence exists.

Indicators should include, where available:

- total generation and year-on-year change;
- latest quarterly or monthly generation data such as Q1;
- electricity demand, peak load, imports/exports, deficit or surplus;
- wind generation, solar generation, and three-year trend;
- installed wind/solar/renewable capacity;
- confirmed project pipeline MW, all-phase pipeline MW, watchlist MW;
- auction/PPA capacity and weighted/representative tariffs;
- curtailment, grid expansion, storage, or reserve-margin indicators;
- carbon, I-REC, green-hydrogen, CBAM, or corporate-PPA metrics when material.

If a value is unavailable, write `not found` or `unavailable` and keep the source gap visible.

## Lite Report

Default target: 3-4 pages or concise MD.

Purpose: a polished delivery summary with enough structure to be useful while reserving deeper internal analysis for the full report.

Include:

- Cover/title and short executive summary
- Policy/planning snapshot
- In-construction/signed/project pipeline essentials as cards
- Forecast and opportunity summary
- Key risks and caveats

Reduce or omit:

- project-level ROI and detailed sponsor financial model
- full Chinese company matrix
- detailed turbine/module/battery specifications
- carbon/hydrogen/CBAM deep analysis
- ESIA and community-impact details unless material to the client decision
- regional benchmark deep dive

If operational projects are excluded from the lite version, still summarize total operational capacity and state the filtering rule.

## Project Pipeline Cards

In the full report, Chapter 5 is the full project ledger and Chapter 6 is the key project-card section. Use the validated master JSON as the source for rich card fields, cross-read the matching depth records, and use the canonical project ledger only for identity, status grouping, dedupe, and watchlist/rejected/unresolved decisions.

Before writing cards, read the `sourceTrace` or `mergedFromDepthRecords` references for each project and compare the depth records against the master JSON. If depth contains annual generation, annual CO2 reduction, investment, turbine model/count/specs, storage, coordinates, logistics, community impact, biodiversity/bird protection, jobs/local employment, or personnel/developer data that is missing from the master JSON, update the master JSON and rerun integrity validation before report writing.

Each project card should include:

- project name plus local/translated alias when material;
- status bucket, evidence stage, and status basis;
- capacity, coordinates, site area/land footprint, location, owner/developer/SPV;
- COD or target COD, PPA/auction/financing/construction milestones when verified;
- technology route, hub height, rotor/blade diameter, turbine model/count, storage/hybrid notes when material;
- annual generation, annual emission reduction, jobs/local employment, and investment when verified;
- bird/biodiversity protection, land/community impacts, ESIA constraints, and mitigation status when material;
- Opportunity MW, Mingyang/MySE factual relevance, relevance rationale, and pending verification when in scope;
- confidence, uncertainty, and critical-field verification note;
- source references or evidence IDs.
- procurement window, likely decision maker, influencers, tender route, current OEM status, shortlist clues, and bankability constraint when evidence supports them.

Use compact grouping before cards:

- `Confirmed / operational or COD`;
- `Under construction / financing closed`;
- `Awarded or PPA signed`;
- `MOU / framework / watchlist`.

Tables are allowed in Chapter 5 because the full project ledger is a required table. Do not replace Chapter 6 project cards with only a dense project table.

## Deep-Dive Chapter Requirements

Use dedicated deep-dive chapters or subsections when an owner/developer, Chinese entrant, OEM, logistics route, localization issue, grid constraint, procurement window, or tariff issue materially affects the current market-status description.

Anchor developer deep dives should include:

- basic entity profile, ownership, financial metrics, listed ticker if applicable, revenue/profit/ROE/PE where public;
- full local project portfolio, status, partners, financing, and ownership/SPV structure;
- key people or management contacts when public and relevant;
- China cooperation matrix and procurement/EPC/OEM ties;
- project economics or IRR/return assumptions only when sourced or clearly marked as assumptions;
- current operating status and recent updates.
- project-linked procurement influence: which MW the developer controls, current OEM ties, EPC/finance constraints, likely tender timing, and decision-chain role.

Chinese developer/entrant deep dives should include listed code, revenue/profit/margin when public, team/local presence, financing or Sinosure/policy-bank structures, and project-level role.

Equipment supplier panorama should include as complete an OEM/supplier list as feasible for the market, not just a top-five table. Segment OEMs into awarded/supplied, framework-agreement, shortlisted or likely entrant, absent/displaced, and unknown. Include tied project MW, turbine/platform specifications, hub height, rotor diameter, power class, climate/logistics suitability, product roadmap, relationship strength, and market-share trend from BNEF or other credible sources when available.

Logistics and installation should include route length, transit time, ports/rail/road/border crossings, component dimensions/weights, heavy-lift and crane suppliers, seasonal/weather limits, abnormal-load permits, and installation risks.

Auction/PPA tariff comparison belongs in Chapter 13 when auctions or PPAs are material. Compare project names, award dates, tariff currency and units, PPA tenor, sponsor, capacity, indexation/FX risk if known, and confidence/source notes.

Chapter 14 must include a procurement-window and decision-chain table with: project, capacity, Opportunity MW, current stage, OEM status, RFQ/tender/NTP timing, decision maker, influencer, and pending verification. Avoid generic market-potential summaries and do not insert recommended sales actions into the full report. Put recommendations into a separate executive brief or action memo only when requested.

## Report Format Requirements

Default final package:

1. Markdown (`.md`) remains the source-of-truth authoring format because it is easy to review, diff, cite, and reuse.
2. HTML (`.html`) is the layout-control format for card layout, table alignment, typography, page breaks, and print styles.
3. PDF (`.pdf`) should normally be rendered from the controlled HTML file, not directly from raw Markdown.

Recommended fonts:

- Chinese: `Microsoft YaHei`, `微软雅黑`, fallback `SimHei`, `SimSun`, sans-serif.
- English/Latin: `Times New Roman`, Times, serif.
- Tables may use the same family but must define explicit `font-family`, `font-size`, `line-height`, `border-collapse`, widths, and page-break behavior.

## Markdown-to-HTML-to-PDF Decision

Prefer option 2: **write Markdown first, convert to controlled HTML, then render PDF from HTML**.

Why:

- Markdown is easier for research agents to edit, review, cite, and compare in git.
- HTML gives stronger control over project-card layout, table alignment, fonts, page breaks, headers, footers, captions, and print CSS.
- The same Markdown can generate both internal reports and lighter delivery versions.
- Review gates can be applied to Markdown before layout polishing.

Use option 1, direct HTML authoring, only when:

- the report is a highly designed executive deck,
- complex layout cannot be represented cleanly in Markdown,
- the HTML template is stable and the writer can preserve citations and evidence IDs, or
- final visual fidelity is more important than text-review simplicity.

Recommended pipeline:

```text
{slug}-report.md
  -> markdown-to-html renderer with controlled template/CSS
  -> {slug}-report.html
  -> browser/Playwright/WeasyPrint/Pandoc HTML print
  -> {slug}-report.pdf
```

CSS baseline:

```css
body {
  font-family: "Times New Roman", "Microsoft YaHei", "微软雅黑", serif;
}
:lang(zh), .zh {
  font-family: "Microsoft YaHei", "微软雅黑", "SimHei", sans-serif;
}
:lang(en), .en {
  font-family: "Times New Roman", Times, serif;
}
table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  page-break-inside: auto;
}
.project-card {
  border: 1px solid #d0d7de;
  border-radius: 8px;
  padding: 10px 12px;
  margin: 10px 0;
  page-break-inside: avoid;
}
.project-card h3 {
  margin: 0 0 6px;
}
.project-card .meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 4px 12px;
}
th, td {
  border: 1px solid #d0d7de;
  padding: 6px 8px;
  vertical-align: top;
  word-break: break-word;
}
tr {
  page-break-inside: avoid;
}
```

## MD-to-PDF Pipeline

Use the local project pipeline if present. A proven pipeline can be:

```text
source.md
  -> reformat_parse.py -> content.json
  -> palette.py -> tokens.json
  -> render_body.py -> body.pdf
  -> cover.py -> cover.html
  -> render_cover.js -> cover.pdf
  -> merge.py -> final.pdf
```

If these scripts are absent, choose an available renderer such as Pandoc, Playwright HTML print, WeasyPrint, ReportLab, or a repository-native pipeline. Prefer HTML-to-PDF rendering when table alignment and typography matter. On Windows native, run each step directly from PowerShell with `py -3 script.py` or `node script.js`; do not require `make.sh` or Bash.

## Chinese and English Font Handling

ReportLab/HTML renderers may fail with Chinese glyphs unless fonts are explicitly configured. For final report output, prefer Microsoft YaHei for Chinese and Times New Roman for English/Latin text. On Windows, use fonts such as:

```json
{
  "font_display_rl": "Microsoft YaHei",
  "font_body_rl": "Microsoft YaHei",
  "font_english_rl": "Times New Roman",
  "font_paths": {
    "Microsoft YaHei": "C:/Windows/Fonts/msyh.ttc",
    "SimSun": "C:/Windows/Fonts/simsun.ttc",
    "SimHei": "C:/Windows/Fonts/simhei.ttf"
  }
}
```

On Linux/macOS, detect available CJK fonts and update the renderer tokens accordingly. If PDF layout becomes unreliable, deliver the MD files and explain that MD is the source of truth.

## Validation

- Confirm full and lite MD files exist and are non-empty.
- Confirm PDFs exist only if rendering was requested and the PDF stack is available. On Windows, also confirm the renderer can access configured CJK fonts.
- Open or inspect PDF metadata/size when possible.
- Record skipped PDF rendering in `index.json` with the environment reason.
