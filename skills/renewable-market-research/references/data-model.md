# Renewable Market Data Model

## Directory Layout

```text
data/renewable-market/
├── index.json
├── {country}-{technology}.json
├── {country}-{technology}.csv
├── depth/
│   ├── project-pipeline.json
│   ├── ifi-financing.json
│   ├── technology-epc.json
│   └── carbon-hydrogen.json
├── {country}-{technology}-report.md
├── {country}-{technology}-lite.md
├── {country}-{technology}-report.pdf
└── {country}-{technology}-lite.pdf
```

Also produce:

- `{country}-{technology}-pipeline-ledger.json`: compact canonical project registry for identity, dedupe, evidence layers, and confirmed/watchlist/rejected state.
- `{country}-{technology}-project_ledger.json`: V4 full project ledger using `schema/project-ledger.schema.json`; this is the report database core.
- `{country}-{technology}-project_cards.json`: complete V4 project cards using `schema/project-card.schema.json`; report prose may summarize, but this file must preserve all card fields.
- `{country}-{technology}-evidence_table.json`: conclusion-level evidence table using `schema/evidence-table.schema.json`; this is required for evidence-boundary checks.
- `{country}-{technology}-participant_ledger.json`, `{country}-{technology}-oem_competition.json`, `{country}-{technology}-procurement_window.json`, `{country}-{technology}-risk_matrix.json`, and `{country}-{technology}-tracking_watchlist.json` when enough data exists.
- `{country}-{technology}-integrity.json`: output from `scripts/validate_market_integrity.py`.

## File Roles and Source Priority

| File | Role | Enough to write final reports? |
|---|---|---|
| `{slug}.json` | Rich master data source. It must preserve the full schema fields needed for project cards, market indicators, developer deep dives, OEM/specs, logistics, policy, tariff, carbon, and conclusions. | Yes. This is the primary report source after validation. |
| `depth/*.json` | Detailed per-dimension evidence and raw structured findings. Use it to cross-read card/chapter details and backfill the master JSON. | Yes as fallback/evidence, but normalize into `{slug}.json` before final writing. |
| `{slug}-pipeline-ledger.json` | Canonical project registry for dedupe, aliases, evidence layers, confirmed/watchlist/rejected decisions, and source-trace control. | No. It is intentionally compact and must not replace the rich master JSON for report cards. |
| `{slug}-project_ledger.json` | V4 full ledger with capacity MW, Opportunity MW, count flags, owner/SPV/equity, OEM/procurement/turbine, EPC/O&M, finance, PPA/tariff, COD, evidence, confidence, pending verification, and Mingyang relevance. | Yes for ledger tables and capacity reconciliation. |
| `{slug}-project_cards.json` | Complete project-card objects. Unknown values are allowed only as explicit `待核`, `unavailable`, `not found`, or equivalent markers. | Yes for Chapter 6/project-card appendix. |
| `{slug}-evidence_table.json` | Conclusion-level evidence records linking claims to source grade, direct proof, confidence, related field, and pending verification action. | Yes for Chapter 16/source-confidence appendix. |

Source priority for writing reports:

1. Read `{slug}.json` for report-ready fields.
2. Cross-read the matching `depth/*.json` records named in `sourceTrace` or `mergedFromDepthRecords`.
3. Use `{slug}-pipeline-ledger.json` only for canonical project identity, status grouping, dedupe decisions, evidence layers, and watchlist/rejected state.
4. Use `{slug}-project_ledger.json`, `{slug}-project_cards.json`, and `{slug}-evidence_table.json` as the V4 gate artifacts before final report prose is released.

## V4 Gate Artifacts

The full report generation order is fixed:

```text
candidate_project_pool
  -> source_trace / evidence_table
  -> project_ledger
  -> capacity_reconciliation
  -> participant_ledger
  -> oem_competition_matrix
  -> procurement_window_table
  -> detailed_project_cards
  -> full_report
  -> lite_report
```

Do not let an agent write `{slug}-report.md` directly from notes or depth files. The report writer reads the gate artifacts and expresses the current market status; it does not become the database.

For V4 full reports, also generate or maintain these agent-control artifacts:

- `{slug}-v4_agent_plan.json`: copied or distilled from the generated plan's `v4FullReportAgentProfile`, `v4AgentTopology`, `v4ChapterVerificationPolicy`, and `v4ChapterAgentPlan`.
- `report_chapters/{slug}-chapter-*.md`: per-chapter writer outputs before final assembly.
- `chapter_verification/{slug}-chapter-*-verification.json`: independent verification outputs for critical chapters 1, 3, 4, 5, 6, 9, 13, 14, and 16.

The validator can enforce the V4 gates:

```text
python skills/renewable-market-research/scripts/validate_market_integrity.py data/renewable-market/{slug}.json --depth-dir data/renewable-market/depth --candidate-pool data/renewable-market/{slug}-candidate_project_pool.json --project-ledger data/renewable-market/{slug}-project_ledger.json --project-cards data/renewable-market/{slug}-project_cards.json --evidence-table data/renewable-market/{slug}-evidence_table.json --full-report data/renewable-market/{slug}-report.md --output data/renewable-market/{slug}-integrity.json
```

The `v4GateSummary` in `{slug}-integrity.json` must show zero gaps before release, or the report must explicitly remain in draft/gap status.

## Rich Field Propagation Contract

During aggregation, every rich project field found in depth records must be propagated into the matching project in `{slug}.json`, or explicitly marked as `not found`, `unavailable`, or `not applicable` with a gap note. This applies especially to:

- `annualGenerationGWh`, `annualCO2ReductionTonnes`, `investmentUSD`;
- `turbineModel`, `turbineCount`, `hubHeightM`, `rotorDiameterM`, `bladeLengthM`;
- `storageMWh`, coordinates, site area, technology route;
- logistics route, jobs/local employment, biodiversity/bird protection, community/land impact;
- key people and developer/deep-dive fields when project-specific;
- procurement and sales-opportunity fields such as currentOemStatus, oemShortlist, procurementWindow, decisionMaker, procurementInfluencers, likelyTenderRoute, bankabilityConstraint, salesEntryPoint, and adjacentOpportunityImpact.

Run `scripts/validate_market_integrity.py --depth-dir data/renewable-market/depth` before report writing. A `depthPropagationGaps` or `reportCardFieldGaps` result means the master JSON is not report-ready.

## `index.json`

```json
{
  "version": "1.0",
  "lastUpdated": "2026-05-16T16:35:00+08:00",
  "markets": [
    {
      "slug": "uzbekistan-wind",
      "country": "uzbekistan",
      "technology": "wind",
      "status": "collected",
      "mainData": "data/renewable-market/uzbekistan-wind.json",
      "csv": "data/renewable-market/uzbekistan-wind.csv",
      "fullReport": "data/renewable-market/uzbekistan-wind-report.md",
      "liteReport": "data/renewable-market/uzbekistan-wind-lite.md",
      "fullPdf": "data/renewable-market/uzbekistan-wind-report.pdf",
      "litePdf": "data/renewable-market/uzbekistan-wind-lite.pdf",
      "coverage": {
        "projectPipeline": "high",
        "policy": "medium",
        "financing": "high",
        "technology": "medium"
      },
      "convergence": [
        {
          "dimension": "ifi-financing",
          "rounds": 5,
          "newRecords": 28,
          "stoppedReason": "3 consecutive rounds without material new records",
          "remainingGaps": ["commercial bank tranche details not fully public"]
        }
      ]
    }
  ]
}
```

## Main JSON Schema

```json
{
  "metadata": {
    "country": "uzbekistan",
    "technology": "wind",
    "lastUpdated": "2026-05-16T16:35:00+08:00",
    "dataSources": [{"name": "ADB", "url": "https://..."}],
    "projectCount": 25,
    "confirmedPipelineMW": 17000,
    "allPhasesMW": 25000,
    "sourceToFinal": {
      "pipelineLedger": "data/renewable-market/uzbekistan-wind-pipeline-ledger.json",
      "pipelineLedgerUpdatedAt": "2026-05-16T16:35:00+08:00",
      "summaryBackpropagationAt": "2026-05-16T18:10:00+08:00",
      "finalClaimsCheckedAgainstLedger": true,
      "remainingContinuityGaps": []
    },
    "note": "Collection status and caveats"
  },
  "projects": [
    {
      "id": "uzbekistan-wind-001",
      "name": "Zarafshan Wind Farm",
      "canonicalName": "Zarafshan Wind Farm",
      "nameVariants": [
        {"language": "en", "value": "Zarafshan Wind Farm", "sourceUrl": "https://..."}
      ],
      "dedupeKey": "zarafshan|navoi-tamdy|522|masdar",
      "capacityMW": 521.7,
      "status": "operational",
      "developer": "Masdar",
      "developerCountry": "UAE",
      "location": "Navoi region, Tamdy district",
      "coordinates": {"lat": null, "lon": null},
      "siteAreaHa": null,
      "cod": "2024-12-14",
      "ppaType": "Government PPA",
      "ppaDuration": 25,
      "investmentUSD": 593400000,
      "turbineModel": "Goldwind GW155-4.5MW",
      "turbineCount": 111,
      "hubHeightM": null,
      "rotorDiameterM": null,
      "bladeLengthM": null,
      "technologyRoute": "onshore wind",
      "epc": "POWERCHINA/SEPCOIII",
      "annualGenerationGWh": 1100,
      "annualCO2ReductionTonnes": 1100000,
      "jobsOrLocalEmployment": null,
      "biodiversityBirdProtection": "unavailable",
      "communityLandImpact": "unavailable",
      "storageMWh": null,
      "currentOemStatus": "awarded to Goldwind",
      "oemShortlist": ["Goldwind"],
      "procurementWindow": "closed",
      "decisionMaker": "developer/SPV procurement team",
      "procurementInfluencers": ["EPC", "lenders", "offtaker"],
      "likelyTenderRoute": "awarded package",
      "bankabilityConstraint": "MDB/owner technical acceptance",
      "salesEntryPoint": "closed project; use as reference case for future owner pipeline",
      "adjacentOpportunityImpact": [
        {
          "topic": "storage / solar / green hydrogen / ammonia / methanol / industrial offtake if relevant",
          "impactOnWindOpportunity": "explain only when it changes PPA value, interconnection, procurement scope, OEM opportunity, or sales entry",
          "sourceUrl": "https://..."
        }
      ],
      "financing": "ADB $95M, EBRD $74M, IFC $42M...",
      "sources": [
        {
          "url": "https://...",
          "title": "Source title",
          "publisher": "Publisher",
          "accessedAt": "2026-05-16",
          "sourceLanguage": "en",
          "collectionMethod": "exa-fetch"
        }
      ],
      "sourceTrace": [
        {
          "depthFile": "data/renewable-market/depth/project-pipeline-layered.json",
          "recordIndex": 0,
          "fact": "capacity and COD",
          "sourceUrl": "https://..."
        }
      ],
      "criticalFieldVerification": {
        "capacity_mw": {
          "sourceUrl": "https://...",
          "collectionMethod": "exa-fetch",
          "verifiedAt": "2026-05-16",
          "note": "Capacity verified from owner/MDB/original file text."
        },
        "status": {
          "sourceUrl": "https://...",
          "collectionMethod": "chrome-mcp",
          "verifiedAt": "2026-05-16",
          "note": "Operational/construction/PPA status verified from original page/PDF/table."
        },
        "cod_or_target_cod": {
          "sourceUrl": "https://...",
          "collectionMethod": "chrome-mcp",
          "verifiedAt": "2026-05-16",
          "note": "COD or target COD verified; unresolved conflicts remain in uncertainty."
        }
      },
      "duplicateCheckNotes": "Merged English and local-language references; no separate phase boundary found.",
      "confidence": "high",
      "evidenceStage": "ppa-signed",
      "mingyangOpportunityWindow": "Medium-term turbine + EPC consortium window",
      "uncertainty": "SPV equity split not fully disclosed",
      "lastVerified": "2026-05-16"
    }
  ],
  "demandLoadGap": [],
  "nationalPlans": [],
  "policyFramework": [],
  "forecasts": [],
  "developers": [],
  "financing": [],
  "technology": [],
  "environmentSocial": [],
  "carbonHydrogen": [],
  "risks": [],
  "entryStrategy": []
}
```

## Canonical Project Ledger

Use `{slug}-pipeline-ledger.json` as the canonical registry for project identity, deduplication, evidence layers, and confirmed/watchlist/rejected decisions. Do not use it as the only source for final project cards; final card fields must come from the validated `{slug}.json` and cross-checked `depth/*.json`.

```json
{
  "version": "1.0",
  "slug": "uzbekistan-wind",
  "updatedAt": "2026-05-16T16:35:00+08:00",
  "sourceDepthFiles": [
    "data/renewable-market/depth/project-pipeline-layered.json",
    "data/renewable-market/depth/local-language-china-capital-trace.json",
    "data/renewable-market/depth/anomaly-hunter.json"
  ],
  "projects": [
    {
      "canonicalProjectId": "uzbekistan-wind-001",
      "canonicalName": "Zarafshan Wind Farm",
      "nameVariants": [
        {"language": "en", "value": "Zarafshan Wind Farm", "sourceUrl": "https://..."},
        {"language": "local", "value": "local-language project name if found", "sourceUrl": "https://..."},
        {"language": "zh", "value": "Chinese translated/project name if found", "sourceUrl": "https://..."}
      ],
      "dedupeKey": "zarafshan|navoi-tamdy|522|masdar",
      "cardFields": {
        "coordinates": {"lat": null, "lon": null},
        "siteAreaHa": null,
        "hubHeightM": null,
        "rotorDiameterM": null,
        "bladeLengthM": null,
        "technologyRoute": "onshore wind",
        "annualGenerationGWh": null,
        "annualCO2ReductionTonnes": null,
        "jobsOrLocalEmployment": null,
        "biodiversityBirdProtection": "unavailable",
        "communityLandImpact": "unavailable",
        "currentOemStatus": "awarded / undecided / framework / unknown",
        "procurementWindow": "closed / 2026-2027 / not found",
        "salesEntryPoint": "project-specific route if relevant"
      },
      "mergedFromDepthRecords": [
        {"depthFile": "project-pipeline-layered.json", "recordIndex": 0},
        {"depthFile": "local-language-china-capital-trace.json", "recordIndex": 2}
      ],
      "sourceTrace": [
        {"fact": "capacityMW", "sourceUrl": "https://...", "sourceLanguage": "en", "collectionMethod": "exa-fetch"}
      ],
      "criticalFieldVerification": {
        "capacity_mw": {"collectionMethod": "exa-fetch", "sourceUrl": "https://...", "verifiedAt": "2026-05-16"},
        "status": {"collectionMethod": "chrome-mcp", "sourceUrl": "https://...", "verifiedAt": "2026-05-16"}
      },
      "pipelineBucket": "cod-operational",
      "confirmedPipelineEligible": true,
      "evidenceLayers": ["owner-announcement", "financing-closed", "cod-operational"],
      "duplicateResolution": "merged",
      "exclusionReason": null,
      "remainingGaps": []
    }
  ],
  "duplicateCandidates": [],
  "watchlist": [],
  "rejectedClaims": []
}
```

Reports, CSV exports, timelines, and executive summaries should read rich project fields from the validated master JSON. Use the ledger to keep canonical IDs, status buckets, duplicate decisions, and watchlist/rejected records consistent. If a later chapter discovers a new project, alias, or richer project field, update the master JSON first, rebuild/refresh the ledger, then refresh synthesis and summary.

## Depth File Record Shape

Depth files are arrays. Keep them narrow and source-rich:

```json
[
  {
    "dimension": "ifi-financing",
    "topic": "Zarafshan Wind Farm financing",
    "project": "Zarafshan Wind Farm",
    "company": "Masdar",
    "amountUSD": 95000000,
    "facts": ["ADB committed ...", "Loan tenor ..."],
    "sources": [
      {
        "title": "...",
        "url": "https://...",
        "publisher": "ADB",
        "accessedAt": "2026-05-16",
        "sourceLanguage": "en",
        "collectionMethod": "exa-search"
      }
    ],
    "searchPasses": ["english-broad", "chrome-verification"],
    "sourceTrace": "Candidate maps to canonical project ID uzbekistan-wind-001 after alias/dedupe review.",
    "confidence": "high",
    "uncertainty": "Public source lacks complete term-sheet details",
    "evidenceStage": "financing-closed",
    "notes": "Any conflict or gap"
  }
]
```

## CSV Columns

Use this exact order for project export:

```text
id,name,capacityMW,status,developer,developerCountry,location,cod,investmentUSD,turbineModel,turbineCount,annualGenerationGWh,annualCO2ReductionTonnes,ppaDuration,storageMWh,epc
```
