#!/usr/bin/env python3
"""Plan and validate renewable-market research search coverage.

This helper does not call external search APIs. It creates a deterministic,
file-mode search plan that workers can execute with Exa, Chrome MCP, or other
host search tools, then validates depth JSON files against that plan.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DIMENSIONS = [
    {
        "id": "demand-load-gap",
        "intent": "status",
        "freshness": "py",
        "focus": "electricity demand, peak load, generation, consumption, imports, exports, deficits",
        "patterns": [
            "{country} electricity demand peak load generation consumption import export {year}",
            "{country} power deficit industrial demand mining oil gas data center green hydrogen forecast",
            "{country} electricity demand forecast 2030 power balance report",
        ],
        "domainBoost": ["iea.org", "enerdata.net", "worldbank.org", "stat.gov.kz", "kegoc.kz"],
    },
    {
        "id": "market-key-indicators-timeseries",
        "intent": "status",
        "freshness": "pm",
        "focus": "generation, YoY change, latest quarterly/monthly data, wind/solar three-year trends, installed capacity, imports/exports, and market dashboard indicators",
        "patterns": [
            "{country} electricity generation year on year Q1 wind solar generation statistics {year}",
            "{country} renewable energy statistics wind solar generation 3 year trend installed capacity",
            "{country} energy ministry statistics electricity generation imports exports peak load quarterly report",
        ],
        "domainBoost": ["energy.gov.kz", "stat.gov.kz", "iea.org", "ember-climate.org", "irena.org"],
    },
    {
        "id": "power-mix-replacement",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "current generation mix, retirements, coal/gas limits, hydro flexibility, wind/solar complementarity",
        "patterns": [
            "{country} power generation mix coal gas hydro wind solar retirement plan",
            "{country} coal power plant retirement renewable target wind share",
            "{country} hydro flexibility wind solar complementarity grid balancing",
        ],
        "domainBoost": ["irena.org", "iea.org", "ember-climate.org", "energycharter.org"],
    },
    {
        "id": "grid-storage-transmission",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "grid topology, substations, high-voltage lines, curtailment, storage, cross-border corridors",
        "patterns": [
            "{country} wind grid connection transmission substations storage curtailment",
            "{country} KEGOC transmission investment plan renewable integration",
            "{country} cross-border electricity transmission green corridor wind solar storage",
        ],
        "domainBoost": ["kegoc.kz", "adb.org", "ebrd.com", "worldbank.org", "usaid.gov"],
    },
    {
        "id": "policy-ppa-economics",
        "intent": "status",
        "freshness": "py",
        "focus": "FIT, auctions, PPA, offtaker credit, tariffs, FX, guarantees, tax, land, localization, IRR/ROE",
        "patterns": [
            "{country} renewable energy auction wind tariff PPA offtaker currency guarantee",
            "{country} wind power PPA auction results tariff FIT local content tax land policy",
            "{country} renewable project IRR ROE wind financing assumptions",
        ],
        "domainBoost": ["rfc.kz", "korem.kz", "adilet.zan.kz", "ifc.org", "ebrd.com"],
    },
    {
        "id": "auction-tariff-comparison",
        "intent": "status",
        "freshness": "py",
        "focus": "project-level auction/PPA winning tariffs, award dates, PPA tenor, currency, indexation, capacity, sponsor, and comparable bid history",
        "patterns": [
            "{country} renewable auction results wind tariff cents kWh PPA project sponsor capacity",
            "{country} {technology} winning tariff PPA price auction award date developer",
            "{country} wind solar auction tariff comparison project PPA tenor currency indexation",
        ],
        "domainBoost": ["korem.kz", "rfc.kz", "energy.gov.kz", "masdar.ae", "acwapower.com"],
    },
    {
        "id": "project-pipeline-layered",
        "intent": "status",
        "freshness": "pm",
        "focus": "operational, construction, awarded/PPA, MOU/framework, early-stage wind projects",
        "patterns": [
            "{country} wind farm project pipeline operational construction PPA MOU capacity MW",
            "{country} wind power auction awarded PPA signed construction COD developer",
            "site:acwapower.com {country} wind project PPA construction COD",
        ],
        "domainBoost": ["acwapower.com", "masdar.ae", "totalenergies.com", "eni.com", "powerchina.cn"],
    },
    {
        "id": "owners-partners-routes",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "state entities, IPPs, Chinese developers, industrial offtakers, offices, partnerships",
        "patterns": [
            "{country} wind power developer IPP owner Samruk KEGOC offtaker partnership",
            "{country} ACWA Masdar TotalEnergies ENI China Energy PowerChina wind portfolio",
            "{country} corporate PPA mining metallurgy oil gas renewable electricity wind",
        ],
        "domainBoost": ["samruk-energy.kz", "samruk-kazyna.kz", "kegoc.kz", "acwapower.com"],
    },
    {
        "id": "anchor-developer-deep-dives",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "material owner/developer deep dives: ACWA, Masdar, TotalEnergies, state entities, portfolios, financials, people, partners, IRR assumptions, and China cooperation",
        "patterns": [
            "{country} ACWA Power Masdar wind solar portfolio financial results key people partnerships China EPC",
            "{country} renewable developer project portfolio revenue profit ROE PE investor presentation",
            "{country} Masdar TotalEnergies ACWA project SPV PPA financing EPC operation update",
        ],
        "domainBoost": ["acwapower.com", "masdar.ae", "totalenergies.com", "londonstockexchange.com", "argaam.com"],
    },
    {
        "id": "competitor-oem-landscape",
        "intent": "comparison",
        "freshness": "py",
        "focus": "full OEM/supplier panorama, turbine platform, capacity, rotor, hub height, product roadmap, market share trend, climate adaptation, localization, owner/EPC ties",
        "patterns": [
            "{country} wind turbine supplier Goldwind Envision SANY Mingyang Vestas GE Nordex project",
            "{country} wind farm turbine model rotor diameter hub height low temperature dust",
            "{country} wind OEM localization manufacturing tower blade nacelle",
            "{country} wind turbine market share BNEF supplier ranking product roadmap",
        ],
        "domainBoost": ["goldwind.com", "envision-group.com", "myse.com.cn", "sanyglobal.com", "vestas.com"],
    },
    {
        "id": "epc-om-logistics-lifting",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "EPC, O&M, oversized logistics routes, ports, rail/road corridors, border crossings, component dimensions/weights, heavy lifting, cranes, installation windows",
        "patterns": [
            "{country} wind farm EPC O&M logistics heavy lift crane transport route China",
            "{country} oversized cargo wind turbine blade nacelle tower rail road border crossing",
            "{country} Mammoet Sarens wind turbine installation crane project",
            "{country} wind turbine blade transport route port railway road heavy lift 4000 km 30 days",
        ],
        "domainBoost": ["mammoet.com", "sarens.com", "powerchina.cn", "ceec.net.cn"],
    },
    {
        "id": "localization-supply-chain",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "tower, blade, nacelle, BESS, converter manufacturing, local content, JV/service centers",
        "patterns": [
            "{country} wind tower blade nacelle manufacturing localization local content",
            "{country} battery energy storage manufacturing converter renewable supply chain",
            "{country} wind turbine service center training center spare parts joint venture",
        ],
        "domainBoost": ["invest.gov.kz", "kazakhinvest.gov.kz", "astanatimes.com"],
    },
    {
        "id": "esg-land-community",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "land acquisition, community, biodiversity, birds, ESIA, cultural heritage, IFI standards",
        "patterns": [
            "{country} wind farm ESIA bird migration biodiversity community land acquisition",
            "{country} wind project environmental social impact assessment cultural heritage",
            "{country} wind farm IFC EBRD environmental social action plan",
        ],
        "domainBoost": ["ebrd.com", "ifc.org", "adb.org", "worldbank.org"],
    },
    {
        "id": "carbon-greenpower-hydrogen",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "I-REC, carbon credits, CBAM, green hydrogen/ammonia, industrial decarbonization, corporate PPA",
        "patterns": [
            "{country} I-REC renewable energy certificate wind corporate PPA carbon credit",
            "{country} CBAM mining metallurgy green electricity renewable PPA",
            "{country} green hydrogen ammonia wind solar project industrial decarbonization",
        ],
        "domainBoost": ["irecstandard.org", "hydrogencouncil.com", "ebrd.com", "worldbank.org"],
    },
    {
        "id": "china-finance-ecosystem",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "Chinese developers, EPCs, financiers, Sinosure, policy banks, BRI and industrial cooperation",
        "patterns": [
            "{country} China wind project EPC developer financing Sinosure Exim Bank CDB",
            "{country} Belt and Road renewable wind power China Energy PowerChina Goldwind",
            "{country} China Kazakhstan industrial capacity cooperation renewable energy wind",
        ],
        "domainBoost": ["powerchina.cn", "ceec.net.cn", "sinosure.com.cn", "eximbank.gov.cn"],
    },
    {
        "id": "chinese-developer-deep-dives",
        "intent": "exploratory",
        "freshness": "py",
        "focus": "Chinese developers and entrants: listed code, revenue, profit, margin, team, Sinosure/policy-bank financing, local portfolio, EPC/OEM roles",
        "patterns": [
            "{country} SANY renewable wind project revenue profit gross margin listed code",
            "{country} China renewable developer Sinosure financing team project portfolio EPC",
            "{country} CEEC PowerChina SANY Universal Energy AMEA Voltalia wind solar project financing",
        ],
        "domainBoost": ["sanyglobal.com", "powerchina.cn", "ceec.net.cn", "sinosure.com.cn", "eximbank.gov.cn"],
    },
    {
        "id": "local-language-china-capital-trace",
        "intent": "exploratory",
        "freshness": "pm",
        "focus": "Chinese capital plus official-language project names, translated names, SPVs, EPC notices, and local aliases",
        "patterns": [
            "{country} {technology} China capital EPC local project name {official_languages}",
            "{country} {technology} PowerChina CEEC Goldwind SANY Envision Chinese financing {official_languages}",
            "{known_projects} {country} {technology} local language name Chinese EPC financing",
        ],
        "domainBoost": ["powerchina.cn", "ceec.net.cn", "goldwind.com", "sanyglobal.com", "invest.gov.kz"],
    },
    {
        "id": "new-entrant-hunter",
        "intent": "news",
        "freshness": "pm",
        "focus": "new entrants, newly awarded developers, recent SPVs, local partners, corporate offtakers, and first-time market actors",
        "patterns": [
            "{country} {technology} new entrant developer awarded project PPA {year}",
            "{country} {technology} newly registered SPV renewable project local partner {official_languages}",
            "{country} {technology} first project market entry IPP EPC OEM {year}",
        ],
        "domainBoost": ["invest.gov.kz", "korem.kz", "rfc.kz", "acwapower.com", "masdar.ae"],
    },
    {
        "id": "policy-law-backtrace",
        "intent": "resource",
        "freshness": "py",
        "focus": "trace policy targets, auction numbers, tariffs, and capacity goals back to original laws, decrees, orders, and regulator documents",
        "patterns": [
            "{country} renewable energy target decree law order number {year}",
            "{country} {technology} auction tariff regulation decree original law {official_languages}",
            "{country} renewable capacity target 2030 legal basis regulator decree PDF",
        ],
        "domainBoost": ["adilet.zan.kz", "korem.kz", "rfc.kz", "energy.gov.kz", "gov.kz"],
    },
    {
        "id": "anomaly-hunter",
        "intent": "exploratory",
        "freshness": "pm",
        "focus": "odd spellings, transliterations, map/table/PDF-only mentions, local-language names, and projects outside the known developer pattern",
        "patterns": [
            "{country} {technology} farm transliteration misspelling local language PDF map",
            "{country} {technology} {official_languages} site:gov.kz filetype:pdf",
            "{known_projects} alternative spelling renamed project phase {country} {technology}",
        ],
        "domainBoost": ["gov.kz", "adilet.zan.kz", "kegoc.kz", "wikimapia.org"],
    },
    {
        "id": "regional-benchmark",
        "intent": "comparison",
        "freshness": "py",
        "focus": "peer market comparison and resource allocation priority",
        "patterns": [
            "{country} vs Uzbekistan wind market comparison renewable auction grid PPA",
            "{country} Azerbaijan Mongolia Saudi wind market comparison OEM opportunity",
            "Central Asia wind power market comparison Kazakhstan Uzbekistan Azerbaijan Mongolia",
        ],
        "domainBoost": ["irena.org", "iea.org", "ebrd.com", "adb.org"],
    },
    {
        "id": "mingyang-entry-strategy",
        "intent": "comparison",
        "freshness": "py",
        "focus": "turbine supply, hybrid systems, co-development, EPC consortium, O&M, storage, localization, 12/36/60 month actions",
        "patterns": [
            "{country} wind OEM market entry strategy turbine supply EPC O&M localization",
            "{country} wind solar storage integrated solution opportunity industrial PPA",
            "Mingyang {country} wind turbine opportunity partnership localization",
        ],
        "domainBoost": ["myse.com.cn", "invest.gov.kz", "kegoc.kz", "acwapower.com"],
    },
]

TOOL_LANES = [
    {
        "id": "exa-search",
        "priority": 1,
        "use": "broad semantic discovery with category filters and highlighted snippets",
        "record": {"collectionMethod": "exa-search", "requiredFields": ["title", "url", "publisher", "accessedAt"]},
    },
    {
        "id": "exa-fetch",
        "priority": 2,
        "use": "full-text extraction for known official URLs and PDFs indexed by Exa",
        "record": {"collectionMethod": "exa-fetch", "requiredFields": ["title", "url", "publisher", "accessedAt"]},
    },
    {
        "id": "exa-deep-search",
        "priority": 3,
        "use": "selective cross-source synthesis for complex comparison, status, and exploratory gaps when quota allows",
        "record": {"collectionMethod": "exa-deep-search", "requiredFields": ["title", "url", "publisher", "accessedAt"]},
    },
    {
        "id": "chrome-mcp",
        "priority": 4,
        "use": "sanitized human-browser verification for dynamic pages, tables, maps, PDFs, downloads, and bot-sensitive pages",
        "record": {"collectionMethod": "chrome-mcp", "requiredFields": ["title", "url", "publisher", "accessedAt"]},
    },
    {
        "id": "general-web-search",
        "priority": 5,
        "use": "last-resort fallback when Exa and Chrome MCP are unavailable or insufficient",
        "record": {"collectionMethod": "general-web-search", "requiredFields": ["title", "url", "publisher", "accessedAt"]},
    },
]

EXA_BOUNDARY_CHROME_HANDOFF_POLICY = {
    "trigger": [
        "exa search boundary reached",
        "exa quota boundary reached",
        "exa no-more-results condition reported",
        "exa cannot reliably extract dynamic, PDF, table, map, or JavaScript-rendered evidence",
    ],
    "requiredAction": (
        "Enter chrome-verification lane for candidate official/developer/regulator/PDF/table/map URLs, "
        "or record chrome-mcp as unavailable with affected fields and pending verification status."
    ),
    "notACompletionCondition": "Exa boundary is not search completion and cannot by itself release project_ledger or full_report.",
    "acceptedOutcomes": [
        "chrome-mcp verification records written",
        "exa-fetch/manual-file verification records written for source types that do not need browser rendering",
        "tool_unavailable=chrome-mcp with affected_fields and verification_status=pending_or_blocked",
    ],
    "blocks": ["project_ledger_release", "capacity_reconciliation_final", "full_report_release", "lite_report_release"],
}

MINIMUM_RECALL_ROUNDS = 5
FRONTIER_STALL_ROUNDS = 2

FRONTIER_ENTITY_TYPES = [
    "project",
    "developer",
    "spv",
    "oem",
    "epc",
    "finance",
    "law_decree",
    "offtaker",
    "grid_entity",
    "region",
    "authority_source",
    "adjacent_opportunity",
    "supply_chain",
    "logistics",
    "local_manufacturing",
    "macro_energy",
]

FRONTIER_SEARCH_STATUSES = [
    "pending",
    "searched",
    "expanded",
    "deferred",
    "classified",
]

FRONTIER_CLASSIFICATIONS = [
    "candidate",
    "confirmed",
    "watchlist",
    "duplicate",
    "rejected",
    "unresolved",
    "deferred",
]

HIGH_PRIORITY_FRONTIER_LEVELS = ["P0", "P1"]
EVALUATION_REQUIRED_PRIORITY_LEVELS = ["P0", "P1"]
FRONTIER_EVALUATION_STATUSES = [
    "not_required",
    "pending",
    "passed",
    "passed_with_gaps",
    "blocked",
]

FRONTIER_PRIORITY_LEVELS = [
    {
        "id": "P0",
        "label": "wind-project-commercial-core",
        "includes": "Wind projects, developers, SPVs, capacity, status, OEM, EPC, PPA, and project finance.",
        "expansionPolicy": "Auto-expand until searched, classified, or explicitly deferred with reason.",
        "blocksVerificationMode": True,
        "maxExpansionDepth": 99,
    },
    {
        "id": "P1",
        "label": "wind-policy-grid-revenue-context",
        "includes": "Policy, tariff, grid, offtaker, decree, auction, and PPA context tied to wind.",
        "expansionPolicy": "Auto-expand while linked to wind project value, bankability, grid access, or revenue.",
        "blocksVerificationMode": True,
        "maxExpansionDepth": 3,
    },
    {
        "id": "P2",
        "label": "wind-market-enablers",
        "includes": "Supply chain, local manufacturing, logistics, and financial-institution background.",
        "expansionPolicy": "One-hop expansion only unless promoted to P0/P1 by direct wind linkage.",
        "blocksVerificationMode": False,
        "maxExpansionDepth": 1,
    },
    {
        "id": "P3",
        "label": "adjacent-opportunity-conditional",
        "includes": "BESS, solar hybrid, hydrogen, ammonia, methanol, carbon certificates, I-REC, CBAM, and industrial green-power demand.",
        "expansionPolicy": "Expand only when the entry changes wind configuration, interconnection, PPA/tariff, offtake, procurement, or OEM opportunity.",
        "blocksVerificationMode": False,
        "maxExpansionDepth": 1,
    },
    {
        "id": "P4",
        "label": "macro-background-deferred",
        "includes": "Broad power-sector, gas, coal, hydro, desalination, and macro-energy context without a wind opportunity link.",
        "expansionPolicy": "Record as deferred background; do not expand and do not place in the report body by default.",
        "blocksVerificationMode": False,
        "maxExpansionDepth": 0,
    },
]

FRONTIER_BOUNDARY_POLICY = {
    "principle": "High recall is bounded high recall: discover broadly, but only wind-relevant frontier entries keep expanding.",
    "highPriorityLevels": HIGH_PRIORITY_FRONTIER_LEVELS,
    "automaticExpansion": ["P0", "P1"],
    "boundedExpansion": {"P2": "one-hop only", "P3": "one-hop only after explicit wind linkage"},
    "defaultDeferred": ["P4"],
    "promotionRule": "Promote P2/P3 entries to P0/P1 only when a source links them to wind project capacity/status, PPA/tariff, grid, offtake, procurement, OEM/EPC, or project finance.",
    "reportRule": "P4 background and unlinked P3 adjacent topics stay out of the report body unless synthesis proves direct wind relevance.",
}

P0_P1_EXECUTION_EVALUATION_POLICY = {
    "requiredForPriorityLevels": EVALUATION_REQUIRED_PRIORITY_LEVELS,
    "notRequiredForPriorityLevels": ["P2", "P3", "P4"],
    "principle": "P0/P1 entries require role-separated execution and evaluation before ledger admission; P2-P4 do not unless promoted.",
    "roleSeparation": "executor_role must differ from evaluator_role. If the host cannot spawn real child agents, run the two roles as separate passes and write separate artifacts.",
    "requiredBeforeLedgerAdmission": [
        "executor_role is assigned",
        "evaluator_role is assigned",
        "executor_role != evaluator_role",
        "execution_artifact is present",
        "evaluation_artifact is present",
        "evaluation_status is passed or passed_with_gaps",
    ],
    "ledgerAdmissionRule": {
        "passed": "may enter the appropriate ledger status when source/evidence requirements are also met",
        "passed_with_gaps": "may enter watchlist/unresolved or downgraded fields, but not confirmed capacity totals",
        "blocked": "must remain unresolved/rejected/watchlist with blocker reason; cannot enter confirmed totals",
        "pending": "cannot enter the ledger except as an explicitly pending candidate",
    },
    "allowedEvaluationStatuses": FRONTIER_EVALUATION_STATUSES,
}

PRIORITY_MAX_EXPANSION_DEPTH = {
    "P0": 99,
    "P1": 3,
    "P2": 1,
    "P3": 1,
    "P4": 0,
}

P0_ENTITY_TYPES = {"project", "developer", "spv", "oem", "epc"}
P1_ENTITY_TYPES = {"law_decree", "offtaker", "grid_entity", "region", "authority_source"}
P2_ENTITY_TYPES = {"finance", "supply_chain", "logistics", "local_manufacturing"}
P3_ENTITY_TYPES = {"adjacent_opportunity"}
P4_ENTITY_TYPES = {"macro_energy"}

WIND_LINKAGE_TERMS = {
    "wind",
    "wind farm",
    "wind power",
    "wind project",
    "wind turbine",
    "turbine",
    "ppa",
    "epc",
    "oem",
    "cod",
    "mw",
    "gw",
    "grid connection",
    "interconnection",
    "project finance",
    "financial close",
    "offtake",
}

ADJACENT_TERMS = {
    "bess",
    "battery",
    "storage",
    "solar",
    "pv",
    "hybrid",
    "hydrogen",
    "ammonia",
    "methanol",
    "i-rec",
    "irec",
    "cbam",
    "carbon certificate",
    "green power",
}

P2_TERMS = {
    "supply chain",
    "manufacturing",
    "localization",
    "localisation",
    "factory",
    "blade",
    "tower",
    "nacelle",
    "logistics",
    "transport",
    "port",
    "rail",
    "crane",
    "heavy lift",
}

P4_TERMS = {
    "gas",
    "coal",
    "oil",
    "thermal",
    "hydro",
    "desalination",
    "water",
    "macro",
    "power sector",
    "energy sector",
}

FRONTIER_ENTITY_CONTRACT = {
    "requiredFields": [
        "entity_id",
        "name",
        "aliases",
        "entity_type",
        "language",
        "source_found",
        "origin",
        "country",
        "search_priority",
        "priority_level",
        "wind_linkage",
        "expansion_allowed",
        "expansion_depth",
        "max_expansion_depth",
        "defer_reason",
        "promote_reason",
        "evaluation_required",
        "role_separation_required",
        "executor_role",
        "evaluator_role",
        "execution_artifact",
        "evaluation_artifact",
        "evaluation_status",
        "evaluation_notes",
        "ledger_admission_blocked_reason",
        "search_round",
        "queries_generated",
        "search_status",
        "classification",
        "parent_entity_ids",
    ],
    "entityTypes": FRONTIER_ENTITY_TYPES,
    "searchStatuses": FRONTIER_SEARCH_STATUSES,
    "classifications": FRONTIER_CLASSIFICATIONS,
    "priorityLevels": FRONTIER_PRIORITY_LEVELS,
    "highPriorityLevels": HIGH_PRIORITY_FRONTIER_LEVELS,
    "boundaryPolicy": FRONTIER_BOUNDARY_POLICY,
    "executionEvaluationPolicy": P0_P1_EXECUTION_EVALUATION_POLICY,
    "evaluationStatuses": FRONTIER_EVALUATION_STATUSES,
    "notes": [
        "Search entry names are not assumed complete at initialization.",
        "Every discovered project, developer, SPV, OEM, EPC, lender, law/decree, offtaker, grid entity, region, authority source, and adjacent-opportunity signal is recorded unless it is a normalized duplicate.",
        "P0/P1 entries expand automatically and block Verification Mode while pending; P2 is one-hop; P3 requires explicit wind linkage; P4 is deferred background by default.",
        "P0/P1 entries also require role-separated execution and evaluation artifacts before ledger admission; P2-P4 do not unless promoted.",
    ],
}

FIXED_SEED_TEMPLATES = [
    {
        "id": "country-wind-project",
        "entryType": "project",
        "patterns": [
            "{country} wind project",
            "{country} wind farm",
            "{country} wind power project",
        ],
    },
    {
        "id": "policy-commercial",
        "entryType": "law_decree",
        "patterns": [
            "{country} renewable auction wind",
            "{country} PPA wind",
            "{country} wind energy investment agreement",
            "{country} wind decree law order",
        ],
    },
    {
        "id": "market-actors",
        "entryType": "developer",
        "patterns": [
            "{country} wind developer",
            "{country} wind turbine supplier",
            "{country} EPC wind",
            "{country} IFI wind",
        ],
    },
    {
        "id": "grid-adjacent",
        "entryType": "grid_entity",
        "patterns": [
            "{country} transmission wind",
            "{country} grid connection wind",
            "{country} wind BESS",
        ],
    },
    {
        "id": "chinese-language-generic",
        "entryType": "authority_source",
        "patterns": [
            "{country_zh} wind project",
            "{country_zh} wind PPA",
            "{country_zh} wind presidential decree",
            "{country_zh} wind Chinese EPC",
            "{country_zh} wind Chinese OEM",
        ],
    },
    {
        "id": "local-language-generic",
        "entryType": "authority_source",
        "patterns": [
            "{country} wind official language project",
            "{country} wind local ministry",
            "{country} wind local legal database",
        ],
    },
]

RECALL_ENTRY_CATEGORIES = [
    {
        "id": "project",
        "purpose": "Start from generic country/technology project templates and expand with discovered project names.",
        "minimumOutput": "candidate records or explicit no-find/gap note",
    },
    {
        "id": "developer",
        "purpose": "Expand developers discovered from project, authority-source, and portfolio results.",
        "minimumOutput": "developer-project leads or explicit no-find/gap note",
    },
    {
        "id": "oem",
        "purpose": "Find turbine awards, shortlists, framework deals, and unallocated MW from discovered OEM names.",
        "minimumOutput": "OEM/project or OEM-opportunity leads or explicit no-find/gap note",
    },
    {
        "id": "epc",
        "purpose": "Find EPC awards, construction roles, grid works, and logistics traces from discovered EPC names.",
        "minimumOutput": "EPC/project leads or explicit no-find/gap note",
    },
    {
        "id": "finance",
        "purpose": "Find bankability, financial close, guarantees, and lender project lists from discovered finance entities.",
        "minimumOutput": "finance/project leads or explicit no-find/gap note",
    },
    {
        "id": "policy",
        "purpose": "Find legal basis, auctions, PPAs, grid rules, and tariff authority from generic templates and discovered decree IDs.",
        "minimumOutput": "policy/project or policy-target leads or explicit no-find/gap note",
    },
    {
        "id": "local-language",
        "purpose": "Catch ministry, regulator, legal, grid, and media records missed in English using local-language aliases.",
        "minimumOutput": "local-language leads or explicit no-find/gap note",
    },
    {
        "id": "chinese-language",
        "purpose": "Catch Chinese EPC/OEM/developer/finance records and Chinese project aliases.",
        "minimumOutput": "Chinese-language leads or explicit no-find/gap note",
    },
    {
        "id": "adjacent-opportunity",
        "purpose": "Capture adjacent facts only when they change wind value, grid/PPA, procurement, or OEM opportunity.",
        "minimumOutput": "wind-relevant adjacent-opportunity leads or explicit no-find/gap note",
    },
]

AUTHORITY_SOURCE_CATEGORIES = [
    {
        "id": "government-legal",
        "examples": ["legal database", "energy ministry", "president office", "investment ministry", "PPP project database", "auction notice"],
        "requiredTreatment": "attempt source enumeration and record no-find/gap if unavailable",
    },
    {
        "id": "ifi-dfi",
        "examples": ["ADB country project list", "AIIB project list", "EBRD project summary", "IFC disclosure", "MIGA guarantees", "World Bank project portal"],
        "requiredTreatment": "attempt source enumeration and record no-find/gap if unavailable",
    },
    {
        "id": "developer-portfolio",
        "examples": ["developer portfolio pages", "project pages", "investor presentations"],
        "requiredTreatment": "attempt source enumeration and record no-find/gap if unavailable",
    },
    {
        "id": "oem-epc",
        "examples": ["OEM project references", "EPC press releases", "construction award pages"],
        "requiredTreatment": "attempt source enumeration and record no-find/gap if unavailable",
    },
    {
        "id": "chinese-source",
        "examples": ["Chinese EPC pages", "Chinese OEM pages", "Chinese finance and insurer notices"],
        "requiredTreatment": "attempt source enumeration and record no-find/gap if unavailable",
    },
    {
        "id": "local-language-source",
        "examples": ["local ministry pages", "local media", "local regulator, grid, and legal pages"],
        "requiredTreatment": "attempt source enumeration and record no-find/gap if unavailable",
    },
]

RECALL_ROUNDS = [
    {
        "round": 1,
        "name": "fixed-seed-template-search",
        "goal": "Search generic country plus wind/project/PPA/auction/developer/OEM/EPC/IFI/grid/BESS templates.",
        "outputs": ["seed_entities", "candidate_project_pool", "discovered_entries"],
    },
    {
        "round": 2,
        "name": "baseline-and-authority-enumeration",
        "goal": "Search historical baseline entries and authority source categories.",
        "outputs": ["search_frontier", "authority_sources", "discovered_entries"],
    },
    {
        "round": 3,
        "name": "entity-expansion-search",
        "goal": "Search newly extracted projects, companies, SPVs, decree IDs, regions, and institutions from rounds 1-2.",
        "outputs": ["search_frontier", "candidate_project_pool", "discovered_entries"],
    },
    {
        "round": 4,
        "name": "reverse-source-search",
        "goal": "Reverse-search from OEM, EPC, IFI, Chinese-language, and local-language sources to find hidden projects.",
        "outputs": ["source_trace", "authority_sources", "discovered_entries"],
    },
    {
        "round": 5,
        "name": "alias-anomaly-backtrace-search",
        "goal": "Search aliases, anomalies, source backtraces, and remaining P0/P1 high-priority frontier entries.",
        "outputs": ["search_frontier", "frontier_convergence", "contradiction_queue"],
    },
]

FRONTIER_CONVERGENCE_POLICY = {
    "minimumRecallRounds": MINIMUM_RECALL_ROUNDS,
    "stallRoundsAfterMinimum": FRONTIER_STALL_ROUNDS,
    "requiredBeforeVerification": [
        "completedRecallRounds >= 5",
        "all P0/P1 high-priority frontier entries are searched, classified, or explicitly deferred with reason",
        "all baseline seed entities are classified",
        "all authority source categories are attempted",
        "two consecutive post-minimum expansion rounds produce zero new high-priority entries",
    ],
    "highPriorityLevels": HIGH_PRIORITY_FRONTIER_LEVELS,
    "boundedPriorityTreatment": {
        "P2": "may remain deferred after one-hop treatment and does not block verification unless promoted",
        "P3": "must show wind linkage before expansion and does not block verification unless promoted",
        "P4": "deferred background; does not block verification or report generation",
    },
    "notAStopCondition": "The model feeling that enough sources were searched.",
}

LEDGER_STATUSES = [
    "operational",
    "financing_closed",
    "under_construction",
    "ppa_signed",
    "decree_backed",
    "mou_or_early_stage",
    "watchlist",
    "duplicate",
    "rejected",
    "unresolved",
]

FULL_REPORT_ARCHITECTURE = {
    "id": "v4-country-wind-market-status",
    "reference": "skills/renewable-market-research/references/full-report-v4.md",
    "positioning": (
        "Country wind-market status master report; not a strategy recommendation memo "
        "and not the lite delivery version."
    ),
    "recommendationPolicy": (
        "Keep go/no-go, factory-build, bid-pricing, and recommended Mingyang/MySE actions "
        "out of the full report. Put recommendations in a separate executive/action brief "
        "only when requested."
    ),
    "chapters": [
        "0. Report scope and evidence rules",
        "1. Executive summary",
        "2. National power fundamentals",
        "3. Policy, permitting, development flow, and PPA mechanism",
        "4. Market capacity definitions and project segmentation",
        "5. Full project ledger",
        "6. Key project cards",
        "7. Developers, owners, and decision-right structure",
        "8. Wind resource, geography, and turbine-fit inference",
        "9. OEM competition landscape",
        "10. EPC, financiers, O&M, and supply-chain network",
        "11. Localization and industrial policy status",
        "12. Grid, storage, interconnection, and curtailment constraints",
        "13. Tariff, project economics, and bankability status",
        "14. Procurement window and decision-chain status",
        "15. Risk matrix and constraint conditions",
        "16. Data-source and conclusion-confidence appendix",
    ],
    "ledgerRequiredFieldsReference": "full-report-v4.md#5-full-project-ledger",
    "projectCardRequiredFieldsReference": "full-report-v4.md#6-key-project-cards",
}

V4_FULL_REPORT_AGENT_PROFILE = {
    "id": "v4-heavy-chapter-agent",
    "defaultFor": [
        "V4 full country wind-market status reports",
        "benchmark-surpassing country wind-market reports",
        "full wind-market assessment with project ledger, project cards, and evidence table",
    ],
    "minimumLogicalAgents": 15,
    "targetLogicalRoles": 20,
    "realChildAgentsPreferred": True,
    "fallback": (
        "If real child agents are unavailable, run the same roles as separate sequential lanes, "
        "write each role artifact, and record agentMode=collapsed-sequential. Do not fall back "
        "to the 10-agent Standard profile for V4 full reports unless the user explicitly asks "
        "for a smaller run."
    ),
    "nonNegotiableRules": [
        "The 10-step artifact pipeline controls generation order.",
        "The chapter-agent plan controls ownership, chapter drafting, and verification separation.",
        "Critical chapters need independent verification artifacts before full_report release.",
        "Chapter 1 executive summary is written only after Chapters 2-16 and all gates are current.",
    ],
}

V4_AGENT_TOPOLOGY = [
    {
        "order": 1,
        "role": "main_orchestrator_integrator",
        "type": "orchestrator",
        "owns": ["run state", "task split", "artifact order", "master JSON", "canonical ledger", "final integration"],
    },
    {
        "order": 2,
        "role": "chapter_0_scope_evidence_worker",
        "type": "chapter_writer",
        "owns": ["Chapter 0", "capacity definitions", "stage definitions", "confidence rules"],
    },
    {
        "order": 3,
        "role": "chapter_2_market_fundamentals_worker",
        "type": "chapter_writer",
        "owns": ["Chapter 2", "power fundamentals", "demand/load gap", "market indicators"],
    },
    {
        "order": 4,
        "role": "chapter_3_policy_permitting_worker",
        "type": "chapter_writer",
        "owns": ["Chapter 3", "policy", "permitting", "PPA mechanism", "development flow"],
    },
    {
        "order": 5,
        "role": "chapter_4_capacity_segmentation_worker",
        "type": "chapter_writer",
        "owns": ["Chapter 4", "capacity segmentation", "confirmed/opportunity/watchlist totals"],
    },
    {
        "order": 6,
        "role": "chapter_5_project_ledger_worker",
        "type": "chapter_writer",
        "owns": ["Chapter 5", "full project ledger", "ledger table"],
    },
    {
        "order": 7,
        "role": "chapter_6_project_cards_worker",
        "type": "chapter_writer",
        "owns": ["Chapter 6", "complete project cards", "project-card appendix"],
    },
    {
        "order": 8,
        "role": "chapter_7_owner_decision_worker",
        "type": "chapter_writer",
        "owns": ["Chapter 7", "developers", "owners", "SPVs", "decision rights"],
    },
    {
        "order": 9,
        "role": "chapter_8_wind_resource_turbine_fit_worker",
        "type": "chapter_writer",
        "owns": ["Chapter 8", "wind resource", "geography", "turbine-fit inference"],
    },
    {
        "order": 10,
        "role": "chapter_9_oem_competition_worker",
        "type": "chapter_writer",
        "owns": ["Chapter 9", "OEM competition", "locked/shortlisted/unallocated OEM MW"],
    },
    {
        "order": 11,
        "role": "chapter_10_epc_finance_om_supply_worker",
        "type": "chapter_writer",
        "owns": ["Chapter 10", "EPC", "financiers", "O&M", "supply-chain network"],
    },
    {
        "order": 12,
        "role": "chapter_11_localization_worker",
        "type": "chapter_writer",
        "owns": ["Chapter 11", "localization", "industrial policy", "service/manufacturing footprint"],
    },
    {
        "order": 13,
        "role": "chapter_12_grid_storage_worker",
        "type": "chapter_writer",
        "owns": ["Chapter 12", "grid", "storage", "interconnection", "curtailment"],
    },
    {
        "order": 14,
        "role": "chapter_13_tariff_bankability_worker",
        "type": "chapter_writer",
        "owns": ["Chapter 13", "tariff", "project economics", "bankability"],
    },
    {
        "order": 15,
        "role": "chapter_14_procurement_window_worker",
        "type": "chapter_writer",
        "owns": ["Chapter 14", "procurement window", "decision chain", "Mingyang factual relevance"],
    },
    {
        "order": 16,
        "role": "chapter_15_risk_matrix_worker",
        "type": "chapter_writer",
        "owns": ["Chapter 15", "risk matrix", "constraint conditions"],
    },
    {
        "order": 17,
        "role": "chapter_16_evidence_appendix_worker",
        "type": "chapter_writer",
        "owns": ["Chapter 16", "source table", "conclusion-confidence appendix", "pending verification"],
    },
    {
        "order": 18,
        "role": "chapter_1_executive_summary_worker",
        "type": "chapter_writer",
        "owns": ["Chapter 1", "executive summary", "backpropagation after Chapters 2-16"],
    },
    {
        "order": 19,
        "role": "verification_agent",
        "type": "independent_verifier",
        "owns": ["critical field verification", "source audit", "chapter verification artifacts"],
    },
    {
        "order": 20,
        "role": "reflection_reviewer",
        "type": "independent_reviewer",
        "owns": ["stage review", "chapter review", "critical blockers", "gap tasks"],
    },
]

V4_CHAPTER_VERIFICATION_POLICY = {
    "allChaptersRequireReviewerPass": True,
    "criticalFieldVerificationChapters": ["1", "3", "4", "5", "6", "9", "13", "14", "16"],
    "rule": (
        "Every chapter has a writer owner and reviewer pass. Critical chapters also require "
        "a separate verification_agent artifact before final full_report release."
    ),
}

V4_CHAPTER_AGENT_PLAN = [
    {
        "chapter": "0",
        "title": "Report scope and evidence rules",
        "writerRole": "chapter_0_scope_evidence_worker",
        "writerOutput": "data/renewable-market/report_chapters/{slug}-chapter-00-scope-evidence.md",
        "startsAfter": ["source_trace_evidence_table"],
        "verificationMode": "review_only",
        "verifierRole": "reflection_reviewer",
    },
    {
        "chapter": "2",
        "title": "National power fundamentals",
        "writerRole": "chapter_2_market_fundamentals_worker",
        "writerOutput": "data/renewable-market/report_chapters/{slug}-chapter-02-power-fundamentals.md",
        "startsAfter": ["source_trace_evidence_table"],
        "verificationMode": "review_only",
        "verifierRole": "reflection_reviewer",
    },
    {
        "chapter": "3",
        "title": "Policy, permitting, development flow, and PPA mechanism",
        "writerRole": "chapter_3_policy_permitting_worker",
        "writerOutput": "data/renewable-market/report_chapters/{slug}-chapter-03-policy-ppa.md",
        "startsAfter": ["source_trace_evidence_table"],
        "verificationMode": "field_verification",
        "verifierRole": "verification_agent",
    },
    {
        "chapter": "4",
        "title": "Market capacity definitions and project segmentation",
        "writerRole": "chapter_4_capacity_segmentation_worker",
        "writerOutput": "data/renewable-market/report_chapters/{slug}-chapter-04-capacity-segmentation.md",
        "startsAfter": ["project_ledger", "capacity_reconciliation"],
        "verificationMode": "field_verification",
        "verifierRole": "verification_agent",
    },
    {
        "chapter": "5",
        "title": "Full project ledger",
        "writerRole": "chapter_5_project_ledger_worker",
        "writerOutput": "data/renewable-market/report_chapters/{slug}-chapter-05-project-ledger.md",
        "startsAfter": ["project_ledger", "capacity_reconciliation"],
        "verificationMode": "field_verification",
        "verifierRole": "verification_agent",
    },
    {
        "chapter": "6",
        "title": "Key project cards",
        "writerRole": "chapter_6_project_cards_worker",
        "writerOutput": "data/renewable-market/report_chapters/{slug}-chapter-06-project-cards.md",
        "startsAfter": ["detailed_project_cards"],
        "verificationMode": "field_verification",
        "verifierRole": "verification_agent",
    },
    {
        "chapter": "7",
        "title": "Developers, owners, and decision-right structure",
        "writerRole": "chapter_7_owner_decision_worker",
        "writerOutput": "data/renewable-market/report_chapters/{slug}-chapter-07-owner-decision.md",
        "startsAfter": ["participant_ledger"],
        "verificationMode": "review_only",
        "verifierRole": "reflection_reviewer",
    },
    {
        "chapter": "8",
        "title": "Wind resource, geography, and turbine-fit inference",
        "writerRole": "chapter_8_wind_resource_turbine_fit_worker",
        "writerOutput": "data/renewable-market/report_chapters/{slug}-chapter-08-turbine-fit.md",
        "startsAfter": ["project_ledger", "detailed_project_cards"],
        "verificationMode": "review_only",
        "verifierRole": "reflection_reviewer",
    },
    {
        "chapter": "9",
        "title": "OEM competition landscape",
        "writerRole": "chapter_9_oem_competition_worker",
        "writerOutput": "data/renewable-market/report_chapters/{slug}-chapter-09-oem-competition.md",
        "startsAfter": ["oem_competition_matrix"],
        "verificationMode": "field_verification",
        "verifierRole": "verification_agent",
    },
    {
        "chapter": "10",
        "title": "EPC, financiers, O&M, and supply-chain network",
        "writerRole": "chapter_10_epc_finance_om_supply_worker",
        "writerOutput": "data/renewable-market/report_chapters/{slug}-chapter-10-epc-finance-om.md",
        "startsAfter": ["participant_ledger"],
        "verificationMode": "review_only",
        "verifierRole": "reflection_reviewer",
    },
    {
        "chapter": "11",
        "title": "Localization and industrial policy status",
        "writerRole": "chapter_11_localization_worker",
        "writerOutput": "data/renewable-market/report_chapters/{slug}-chapter-11-localization.md",
        "startsAfter": ["participant_ledger"],
        "verificationMode": "review_only",
        "verifierRole": "reflection_reviewer",
    },
    {
        "chapter": "12",
        "title": "Grid, storage, interconnection, and curtailment constraints",
        "writerRole": "chapter_12_grid_storage_worker",
        "writerOutput": "data/renewable-market/report_chapters/{slug}-chapter-12-grid-storage.md",
        "startsAfter": ["project_ledger", "detailed_project_cards"],
        "verificationMode": "review_only",
        "verifierRole": "reflection_reviewer",
    },
    {
        "chapter": "13",
        "title": "Tariff, project economics, and bankability status",
        "writerRole": "chapter_13_tariff_bankability_worker",
        "writerOutput": "data/renewable-market/report_chapters/{slug}-chapter-13-tariff-bankability.md",
        "startsAfter": ["project_ledger", "participant_ledger"],
        "verificationMode": "field_verification",
        "verifierRole": "verification_agent",
    },
    {
        "chapter": "14",
        "title": "Procurement window and decision-chain status",
        "writerRole": "chapter_14_procurement_window_worker",
        "writerOutput": "data/renewable-market/report_chapters/{slug}-chapter-14-procurement-window.md",
        "startsAfter": ["procurement_window_table"],
        "verificationMode": "field_verification",
        "verifierRole": "verification_agent",
    },
    {
        "chapter": "15",
        "title": "Risk matrix and constraint conditions",
        "writerRole": "chapter_15_risk_matrix_worker",
        "writerOutput": "data/renewable-market/report_chapters/{slug}-chapter-15-risk-matrix.md",
        "startsAfter": ["risk_matrix", "project_ledger"],
        "verificationMode": "review_only",
        "verifierRole": "reflection_reviewer",
    },
    {
        "chapter": "16",
        "title": "Data-source and conclusion-confidence appendix",
        "writerRole": "chapter_16_evidence_appendix_worker",
        "writerOutput": "data/renewable-market/report_chapters/{slug}-chapter-16-evidence-confidence.md",
        "startsAfter": ["source_trace_evidence_table"],
        "verificationMode": "field_verification",
        "verifierRole": "verification_agent",
    },
    {
        "chapter": "1",
        "title": "Executive summary",
        "writerRole": "chapter_1_executive_summary_worker",
        "writerOutput": "data/renewable-market/report_chapters/{slug}-chapter-01-executive-summary.md",
        "startsAfter": ["chapters_2_to_16_current", "capacity_reconciliation", "full_report_no_strategy_scan"],
        "verificationMode": "field_verification",
        "verifierRole": "verification_agent",
    },
]

V4_REPORT_GENERATION_PIPELINE = [
    {
        "order": 1,
        "id": "candidate_project_pool",
        "output": "candidate_project_pool.json",
        "gate": "baseline_inheritance_gate",
    },
    {
        "order": 2,
        "id": "source_trace_evidence_table",
        "output": "source_trace.json + evidence_table.json",
        "gate": "source_trace_evidence_boundary_gate",
    },
    {
        "order": 3,
        "id": "project_ledger",
        "output": "project_ledger.json or {slug}-pipeline-ledger.json",
        "gate": "project_ledger_schema_gate",
    },
    {
        "order": 4,
        "id": "capacity_reconciliation",
        "output": "capacity_reconciliation.json/md",
        "gate": "capacity_reconciliation_gate",
    },
    {
        "order": 5,
        "id": "participant_ledger",
        "output": "participant_ledger.json",
        "gate": "participant_project_linkage_gate",
    },
    {
        "order": 6,
        "id": "oem_competition_matrix",
        "output": "oem_competition.json",
        "gate": "oem_opportunity_consistency_gate",
    },
    {
        "order": 7,
        "id": "procurement_window_table",
        "output": "procurement_window.json",
        "gate": "procurement_window_gate",
    },
    {
        "order": 8,
        "id": "detailed_project_cards",
        "output": "project_cards.json",
        "gate": "project_card_completeness_gate",
    },
    {
        "order": 9,
        "id": "full_report",
        "output": "{slug}-report.md",
        "gate": "no_strategy_recommendation_gate",
    },
    {
        "order": 10,
        "id": "lite_report",
        "output": "{slug}-lite.md",
        "gate": "lite_from_full_gate",
    },
]

WORKFLOW_PHASES = [
    {
        "id": "phase-0-initialize",
        "name": "Initialize",
        "output": "normalized scope, country, time window, target company, report mode",
    },
    {
        "id": "phase-1-broad-recall",
        "name": "Broad Recall",
        "output": "candidate_project_pool.json",
    },
    {
        "id": "phase-2-anchor-expansion",
        "name": "Anchor Expansion",
        "output": "developer_project_map.json",
    },
    {
        "id": "phase-3-source-specific-verification",
        "name": "Source-Specific Verification",
        "output": "source_trace.json",
    },
    {
        "id": "phase-4-ledger-build",
        "name": "Ledger Build",
        "output": "project_ledger JSON/CSV before any report prose",
    },
    {
        "id": "phase-5-reconciliation",
        "name": "Reconciliation",
        "output": "capacity_reconciliation.md and contradiction_queue.json",
    },
    {
        "id": "phase-6-commercial-synthesis",
        "name": "Commercial Synthesis",
        "output": "participant map, OEM/EPC competition, finance/risk view, procurement-window and factual relevance view",
    },
    {
        "id": "phase-7-report-generation",
        "name": "Report Generation",
        "output": "V4 full report, lite report, optional executive/action brief, PDF when available",
    },
]

SCHEDULER_GATES = {
    "entity_extraction_gate": {
        "rule": "Every search result must be scanned for project, developer, SPV, OEM, EPC, finance, law/decree, offtaker, grid, region, authority-source, supply-chain/logistics/local-manufacturing, adjacent-opportunity, and macro-energy entities.",
        "writes": "discovered_entries.json",
    },
    "alias_expansion_gate": {
        "rule": "Each material entity should receive English, local-language, Russian when relevant, Chinese, transliteration, SPV, and decree/order variants where discoverable.",
        "writes": "search_frontier.json aliases",
    },
    "frontier_priority_gate": {
        "rule": "Each frontier entry must be assigned P0/P1/P2/P3/P4 plus wind_linkage, expansion_allowed, expansion_depth, defer_reason, and promote_reason before scheduling another search.",
        "priorityLevels": FRONTIER_PRIORITY_LEVELS,
        "highPriorityLevels": HIGH_PRIORITY_FRONTIER_LEVELS,
    },
    "wind_relevance_gate": {
        "rule": "P3 adjacent entries expand only when they affect wind configuration, interconnection, PPA/tariff, offtake, procurement, OEM/EPC opportunity, or project finance; P4 macro background is deferred by default.",
        "writes": "search_frontier.json defer_reason/promote_reason",
    },
    "expansion_depth_gate": {
        "rule": "P0/P1 entries may continue until convergence; P2 and linked P3 entries are one-hop unless promoted; P4 entries do not expand.",
        "maxExpansionDepth": PRIORITY_MAX_EXPANSION_DEPTH,
    },
    "frontier_expansion_gate": {
        "rule": "Every new non-duplicate entity is recorded, but only entries allowed by frontier_priority_gate, wind_relevance_gate, and expansion_depth_gate are enqueued for a later search round.",
        "writes": "search_frontier.json",
    },
    "p0_p1_execution_evaluation_gate": {
        "rule": "P0/P1 entries must have role-separated execution and evaluation before ledger admission; P2-P4 do not require this unless promoted to P0/P1.",
        "requiredPriorityLevels": EVALUATION_REQUIRED_PRIORITY_LEVELS,
        "requiredBeforeLedgerAdmission": P0_P1_EXECUTION_EVALUATION_POLICY["requiredBeforeLedgerAdmission"],
        "allowedEvaluationStatuses": ["passed", "passed_with_gaps"],
        "roleSeparation": "executor_role != evaluator_role",
        "writes": ["execution_artifact", "evaluation_artifact", "source_trace.json"],
    },
    "historical_entry_retention_gate": {
        "rule": "Baseline seed entities from prior reports must be searched or explicitly classified; they must not silently disappear.",
        "allowedClassifications": ["confirmed", "watchlist", "duplicate", "rejected", "unresolved", "deferred"],
    },
    "authority_source_gate": {
        "rule": "Government/legal, IFI/DFI, developer, OEM/EPC, Chinese, and local-language authority source categories must each be attempted or documented as unavailable.",
        "requiredAuthorityCategories": [category["id"] for category in AUTHORITY_SOURCE_CATEGORIES],
    },
    "minimum_recall_round_gate": {
        "rule": "Verification Mode cannot begin before at least five Recall Mode rounds are complete.",
        "minimumRecallRounds": MINIMUM_RECALL_ROUNDS,
    },
    "frontier_exhaustion_gate": {
        "rule": "After round five, continue recall until all P0/P1 frontier entries are searched/classified/deferred, all baseline seeds are classified, all authority categories are attempted, and two consecutive rounds produce zero new P0/P1 entries.",
        "stallRoundsAfterMinimum": FRONTIER_STALL_ROUNDS,
        "highPriorityLevels": HIGH_PRIORITY_FRONTIER_LEVELS,
    },
    "verification_gate": {
        "rule": "Ledger-admitted projects require sourceTrace, evidenceGrade, field-level verification for present critical fields, and P0/P1 execution/evaluation status passed or passed_with_gaps.",
        "verifiedMethods": ["chrome-mcp", "exa-fetch", "manual-file"],
        "p0p1EvaluationStatusesAllowedForLedger": ["passed", "passed_with_gaps"],
        "confirmedTotalsRequire": ["evaluation_status == passed", "confirmed_pipeline_eligibility == true"],
    },
    "exa_boundary_chrome_handoff_gate": {
        "rule": "When Exa reaches search/quota/no-more-results boundary or cannot reliably extract a dynamic/PDF/table/map source, the run must enter chrome-verification lane or record chrome-mcp as unavailable with affected fields. Exa boundary is not a completion condition.",
        "policy": EXA_BOUNDARY_CHROME_HANDOFF_POLICY,
        "requiresOneOf": [
            "collectionMethod == chrome-mcp",
            "collectionMethod in [exa-fetch, manual-file] for non-browser source extraction",
            "tool_unavailable == chrome-mcp with affected_fields and verification_status",
        ],
        "blocks": EXA_BOUNDARY_CHROME_HANDOFF_POLICY["blocks"],
    },
    "capacity_sum_gate": {
        "rule": "Capacity totals must be computed from project_ledger, not manually copied into report prose.",
    },
    "project_ledger_schema_gate": {
        "rule": "Every ledger project must include the V4 full project ledger fields, including Project ID, Alias Group ID, capacity MW, Opportunity MW, status basis, count flags, owner/SPV/equity, OEM/procurement/turbine, EPC/O&M, financiers, PPA/offtaker, tariff, COD/timeline, next milestone, decision maker, key evidence, field confidence, pending verification, Mingyang relevance, and main risks.",
        "schema": "skills/renewable-market-research/schema/project-ledger.schema.json",
        "blocks": ["capacity_reconciliation", "project_cards", "full_report"],
    },
    "capacity_reconciliation_gate": {
        "rule": "Confirmed capacity, opportunity MW, and watchlist capacity must be recalculated from project_ledger. National targets are reported separately and must not be mixed into project pipeline capacity.",
        "formula": {
            "confirmedCapacityMW": "sum(capacityMW where countedInConfirmedCapacity == true)",
            "opportunityCapacityMW": "sum(opportunityMW where countedInOpportunityCapacity == true)",
            "watchlistCapacityMW": "sum(capacityMW where projectStage == watchlist)",
            "nationalTargetCapacityMW": "separate policy/target field, never included in pipeline totals",
        },
        "validator": "scripts/validate_market_integrity.py --project-ledger ...",
        "blocks": ["full_report", "lite_report"],
    },
    "project_card_completeness_gate": {
        "rule": "Every key project card must preserve the complete V4 modules. Unknown values may be written as pending verification/unavailable, but fields cannot disappear.",
        "schema": "skills/renewable-market-research/schema/project-card.schema.json",
        "requiredModules": [
            "basicInformation",
            "ownerStructure",
            "technicalPlan",
            "commercialStructure",
            "financingStructure",
            "developmentFlow",
            "engineeringSupplyChain",
            "omArrangement",
            "currentProgress",
            "decisionChain",
            "mingyangRelevance",
            "risksAndConstraints",
            "evidenceBoundary",
        ],
        "blocks": ["full_report"],
    },
    "evidence_boundary_gate": {
        "rule": "Key conclusions must have conclusion-level evidence records, especially project stage, capacity, OEM award/status, tariff, financing close, PPA signing, procurement window, and Mingyang relevance.",
        "schema": "skills/renewable-market-research/schema/evidence-table.schema.json",
        "blocks": ["full_report", "lite_report", "executive_brief"],
    },
    "source_trace_evidence_boundary_gate": {
        "rule": "Before project ledger, derived judgments, project cards, or report prose, source_trace.json must link critical claims back to source/depth records and evidence_table.json must carry conclusion-level evidence boundaries.",
        "requires": ["source_trace.json", "evidence_table.json"],
        "blocks": [
            "project_ledger",
            "capacity_reconciliation",
            "participant_ledger",
            "oem_competition_matrix",
            "procurement_window_table",
            "detailed_project_cards",
            "full_report",
            "lite_report",
        ],
    },
    "participant_project_linkage_gate": {
        "rule": "Participant ledger entries must tie owners, developers, EPCs, financiers, O&M actors, and channel actors to project role, MW exposure, procurement influence, evidence confidence, and pending verification. Generic company profiles do not pass.",
        "blocks": ["full_report"],
    },
    "oem_opportunity_consistency_gate": {
        "rule": "OEM competition and opportunity tables must reconcile with project_ledger OEM/procurement fields and cannot count locked/awarded OEM MW as unallocated opportunity MW.",
        "blocks": ["procurement_window_table", "full_report"],
    },
    "procurement_window_gate": {
        "rule": "Procurement-window records must name project, capacity, Opportunity MW, current stage, OEM status, RFQ/tender/NTP timing when known, decision maker, influencer, confidence, and pending verification.",
        "blocks": ["full_report"],
    },
    "no_strategy_recommendation_gate": {
        "rule": "Full report text must not contain final decision or action language such as should build factory, must enter, recommended bid, must bind EPC, or should invest resources. Rewrite as factual status, relevance, or pending verification.",
        "blockedPatterns": ["应当建厂", "必须进入", "建议报价", "必须绑定", "应该投入资源"],
        "blocks": ["full_report_release"],
    },
    "baseline_inheritance_gate": {
        "rule": "Every candidate or historical baseline project must flow into confirmed, watchlist, duplicate, rejected, or unresolved outcomes. No candidate may silently disappear.",
        "validator": "scripts/validate_market_integrity.py --candidate-pool ... --project-ledger ...",
        "blocks": ["project_ledger_release", "full_report"],
    },
    "lite_from_full_gate": {
        "rule": "Lite report must be derived from the validated full-report artifacts and cannot bypass the project ledger, project cards, capacity reconciliation, or evidence table.",
        "blocks": ["lite_report_release"],
    },
    "v4_minimum_agent_topology_gate": {
        "rule": "V4 full reports default to the v4-heavy-chapter-agent profile with at least 15 logical agents. If real child agents are unavailable, the same roles must be run as separate sequential lanes with artifacts and agentMode=collapsed-sequential.",
        "profile": V4_FULL_REPORT_AGENT_PROFILE["id"],
        "minimumLogicalAgents": V4_FULL_REPORT_AGENT_PROFILE["minimumLogicalAgents"],
        "targetLogicalRoles": V4_FULL_REPORT_AGENT_PROFILE["targetLogicalRoles"],
        "blocks": ["evidence_collection", "chapter_drafting", "full_report_release"],
    },
    "chapter_work_verification_gate": {
        "rule": "Every V4 chapter must have a writer owner and reviewer pass. Critical chapters need a separate verification_agent artifact before final full_report release.",
        "criticalFieldVerificationChapters": V4_CHAPTER_VERIFICATION_POLICY["criticalFieldVerificationChapters"],
        "requires": ["writerOutput", "verifierRole", "verificationMode", "chapter_review_or_verification_artifact"],
        "blocks": ["full_report_release"],
    },
    "duplicate_gate": {
        "rule": "Aliases and renamed phases must be merged or given explicit duplicate/rejected decisions.",
    },
    "opportunity_gate": {
        "rule": "OEM opportunity tables may include only projects where OEM is TBD, unconfirmed, undisclosed, or non-final framework.",
    },
    "full_report_v4_gate": {
        "rule": "Full reports must follow the V4 0-16 country wind-market status structure, can be written only after the V4 pipeline artifacts pass gates, and must keep recommendations out of the full report.",
        "reference": FULL_REPORT_ARCHITECTURE["reference"],
        "pipeline": V4_REPORT_GENERATION_PIPELINE,
        "requires": [
            "report scope and evidence rules",
            "full project ledger",
            "key project cards",
            "procurement-window and decision-chain status",
            "source-confidence appendix",
        ],
    },
}

INTENT_WEIGHTS = {
    "status": {"freshness": 0.45, "authority": 0.35, "keyword": 0.20},
    "news": {"freshness": 0.60, "authority": 0.25, "keyword": 0.15},
    "comparison": {"freshness": 0.20, "authority": 0.40, "keyword": 0.40},
    "exploratory": {"freshness": 0.20, "authority": 0.50, "keyword": 0.30},
    "resource": {"freshness": 0.10, "authority": 0.40, "keyword": 0.50},
}


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "market"


def render_query_with_context(
    pattern: str,
    country: str,
    technology: str,
    year: int,
    audience: str,
    official_languages: list[str],
    known_projects: list[str],
) -> str:
    language_text = ", ".join(official_languages) if official_languages else "official language"
    project_text = ", ".join(known_projects) if known_projects else "known project names"
    query = pattern.format(
        country=country,
        technology=technology,
        year=year,
        audience=audience,
        official_languages=language_text,
        known_projects=project_text,
    ).strip()
    if technology.lower() not in query.lower():
        query = f"{query} {technology}"
    return query


def required_passes_for_dimension(dimension_id: str) -> list[str]:
    passes = ["english-broad", "official-language"]
    if "policy" in dimension_id:
        passes.append("source-backtrace")
    if dimension_id in {"market-key-indicators-timeseries", "auction-tariff-comparison"}:
        passes.extend(["source-backtrace", "chrome-verification"])
    if dimension_id in {"project-pipeline-layered", "owners-partners-routes", "china-finance-ecosystem"}:
        passes.append("china-capital-local-language")
    if dimension_id in {"anchor-developer-deep-dives", "chinese-developer-deep-dives"}:
        passes.extend(["official-language", "chrome-verification"])
    if dimension_id in {"competitor-oem-landscape", "epc-om-logistics-lifting"}:
        passes.append("chrome-verification")
    if dimension_id == "local-language-china-capital-trace":
        passes.extend(["china-capital-local-language", "chrome-verification"])
    if dimension_id == "new-entrant-hunter":
        passes.extend(["new-entrant", "official-language"])
    if dimension_id == "policy-law-backtrace":
        passes.extend(["source-backtrace", "chrome-verification"])
    if dimension_id == "anomaly-hunter":
        passes.extend(["anomaly-hunter", "official-language"])
    return list(dict.fromkeys(passes))


def render_seed_templates(
    country: str,
    technology: str,
    official_languages: list[str],
) -> list[dict[str, Any]]:
    country_zh_placeholder = f"{country} Chinese-language"
    context = {
        "country": country,
        "country_zh": country_zh_placeholder,
        "technology": technology,
        "official_languages": ", ".join(official_languages) if official_languages else "official language",
    }
    rendered = []
    for template in FIXED_SEED_TEMPLATES:
        item = dict(template)
        item["queries"] = [pattern.format(**context) for pattern in template["patterns"]]
        rendered.append(item)
    return rendered


def normalize_entity_key(value: str, entity_type: str) -> str:
    text = value.lower().replace("’", "'").replace("`", "'").replace("ʻ", "'").replace("ʼ", "'")
    text = re.sub(r"[^a-z0-9]+", "", text)
    return f"{entity_type}:{text}"


def expand_aliases(name: str) -> list[str]:
    aliases = {name.strip()}
    normalized_apostrophe = name.replace("’", "'").replace("`", "'").replace("ʻ", "'").replace("ʼ", "'")
    aliases.add(normalized_apostrophe)
    aliases.add(normalized_apostrophe.replace("'", ""))
    aliases.add(normalized_apostrophe.replace("'", "’"))
    return sorted(alias for alias in aliases if alias)


def generate_entity_queries(name: str, entity_type: str, country: str, technology: str) -> list[str]:
    if entity_type == "law_decree":
        return [
            f"{name} {country} {technology} decree",
            f"{name} {country} renewable energy law",
            f"site:lex.uz {name} {technology}",
        ]
    if entity_type == "finance":
        return [
            f"{name} {country} {technology} project finance",
            f"{name} {country} wind project",
            f"{name} {country} renewable energy investment",
        ]
    if entity_type in {"developer", "oem", "epc"}:
        return [
            f"{name} {country} {technology} project",
            f"{name} {country} wind portfolio",
            f"{name} {country} wind PPA EPC OEM",
        ]
    if entity_type in {"offtaker", "grid_entity"}:
        return [
            f"{name} {country} {technology} PPA grid connection",
            f"{name} {country} wind offtake transmission interconnection",
            f"{name} {country} renewable energy grid",
        ]
    if entity_type in {"supply_chain", "logistics", "local_manufacturing"}:
        return [
            f"{name} {country} {technology} supply chain logistics",
            f"{name} {country} wind turbine local manufacturing",
            f"{name} {country} wind EPC transport route",
        ]
    if entity_type == "adjacent_opportunity":
        return [
            f"{name} {country} wind hybrid PPA grid",
            f"{name} {country} wind BESS offtake procurement",
            f"{name} {country} renewable energy wind opportunity",
        ]
    if entity_type == "macro_energy":
        return [
            f"{name} {country} wind market impact",
            f"{name} {country} renewable energy wind relevance",
        ]
    return [
        f"{name} {country} {technology} project",
        f"{name} wind project PPA {country}",
        f"{name} {country} MW {technology}",
    ]


def has_any_term(text: str, terms: set[str]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def detect_wind_linkage(name: str, entity_type: str, context_text: str) -> str:
    context = f"{name} {context_text}".lower()
    negative_wind_linkage = bool(
        re.search(r"\b(?:without|no|not|unrelated to)\b.{0,60}\bwind\b", context)
    )
    has_wind_term = has_any_term(context, WIND_LINKAGE_TERMS)
    has_capacity_signal = bool(re.search(r"\b\d+(?:\.\d+)?\s*(?:mw|gw)\b", context))
    has_commercial_signal = any(term in context for term in ["ppa", "tariff", "auction", "offtake", "financial close"])
    if entity_type in P3_ENTITY_TYPES and negative_wind_linkage:
        return "none"
    if entity_type in P0_ENTITY_TYPES and (has_wind_term or has_capacity_signal or has_commercial_signal):
        return "direct"
    if entity_type in P1_ENTITY_TYPES and (has_wind_term or has_commercial_signal):
        return "contextual"
    if entity_type in P2_ENTITY_TYPES and (has_wind_term or has_capacity_signal):
        return "enabling"
    if entity_type in P3_ENTITY_TYPES and (
        has_wind_term
        or any(term in context for term in ["hybrid", "grid", "ppa", "offtake", "curtailment", "procurement"])
    ):
        return "conditional"
    return "none"


def local_context_for_entity(text: str, name: str, window: int = 160) -> str:
    lowered_text = text.lower()
    lowered_name = name.lower()
    index = lowered_text.find(lowered_name)
    if index < 0:
        index = lowered_text.find(lowered_name.replace("-", " "))
    if index < 0:
        return text[: window * 2]
    start = max(0, index - window)
    end = min(len(text), index + len(name) + window)
    return text[start:end]


def recommended_executor_role(entity_type: str) -> str:
    if entity_type in {"project", "spv"}:
        return "pipeline_worker"
    if entity_type == "developer":
        return "owner_developer_worker"
    if entity_type == "oem":
        return "oem_competitor_worker"
    if entity_type == "epc":
        return "epc_logistics_localization_worker"
    if entity_type == "finance":
        return "finance_bankability_worker"
    if entity_type in {"law_decree", "authority_source"}:
        return "policy_law_tariff_worker"
    if entity_type in {"offtaker", "grid_entity"}:
        return "grid_storage_worker"
    if entity_type == "region":
        return "pipeline_worker"
    if entity_type in {"supply_chain", "local_manufacturing", "logistics"}:
        return "epc_logistics_localization_worker"
    if entity_type == "adjacent_opportunity":
        return "adjacent_opportunity_worker"
    return "market_indicators_worker"


def build_execution_evaluation_fields(priority_level: str, entity_type: str) -> dict[str, Any]:
    evaluation_required = priority_level in EVALUATION_REQUIRED_PRIORITY_LEVELS
    executor_role = recommended_executor_role(entity_type) if evaluation_required else ""
    evaluator_role = "verification_agent" if evaluation_required else ""
    return {
        "evaluation_required": evaluation_required,
        "role_separation_required": evaluation_required,
        "executor_role": executor_role,
        "evaluator_role": evaluator_role,
        "execution_artifact": "",
        "evaluation_artifact": "",
        "evaluation_status": "pending" if evaluation_required else "not_required",
        "evaluation_notes": "",
        "ledger_admission_blocked_reason": (
            "P0/P1 entries require role-separated execution and evaluation artifacts before ledger admission."
            if evaluation_required
            else ""
        ),
    }


def build_frontier_priority_fields(
    name: str,
    entity_type: str,
    context_text: str,
    search_round: int,
    expansion_depth: int | None = None,
) -> dict[str, Any]:
    wind_linkage = detect_wind_linkage(name, entity_type, context_text)
    if entity_type in P4_ENTITY_TYPES:
        priority_level = "P4"
    elif entity_type in P3_ENTITY_TYPES:
        priority_level = "P3"
    elif entity_type == "finance":
        priority_level = "P0" if wind_linkage in {"direct", "contextual", "enabling"} else "P2"
    elif entity_type in P0_ENTITY_TYPES:
        priority_level = "P0" if wind_linkage in {"direct", "contextual", "enabling"} else "P2"
    elif entity_type in P1_ENTITY_TYPES:
        priority_level = "P1" if wind_linkage != "none" or entity_type in {"law_decree", "authority_source"} else "P2"
    elif entity_type in P2_ENTITY_TYPES:
        priority_level = "P2"
    else:
        priority_level = "P2"

    depth = expansion_depth if expansion_depth is not None else max(search_round - 1, 0)
    max_depth = PRIORITY_MAX_EXPANSION_DEPTH[priority_level]
    expansion_allowed = priority_level in {"P0", "P1"} or (
        priority_level == "P2" and depth < max_depth
    ) or (
        priority_level == "P3" and wind_linkage != "none" and depth < max_depth
    )
    search_priority = "high" if priority_level in HIGH_PRIORITY_FRONTIER_LEVELS else "medium"
    if priority_level == "P3":
        search_priority = "low" if expansion_allowed else "deferred"
    if priority_level == "P4":
        search_priority = "deferred"

    defer_reason = ""
    if not expansion_allowed:
        if priority_level == "P3":
            defer_reason = "Adjacent topic lacks an explicit wind-opportunity linkage."
        elif priority_level == "P4":
            defer_reason = "Macro-energy background is outside the wind-market report body by default."
        elif depth >= max_depth:
            defer_reason = f"{priority_level} expansion depth limit reached."

    promote_reason = ""
    if priority_level in {"P0", "P1"} and wind_linkage != "none":
        promote_reason = f"{wind_linkage} wind linkage found in source context."
    elif priority_level == "P3" and expansion_allowed:
        promote_reason = "Adjacent topic is linked to wind configuration, grid, PPA, offtake, procurement, or OEM opportunity."

    execution_evaluation_fields = build_execution_evaluation_fields(priority_level, entity_type)
    return {
        "search_priority": search_priority,
        "priority_level": priority_level,
        "wind_linkage": wind_linkage,
        "expansion_allowed": expansion_allowed,
        "expansion_depth": depth,
        "max_expansion_depth": max_depth,
        "defer_reason": defer_reason,
        "promote_reason": promote_reason,
        **execution_evaluation_fields,
    }


def build_runtime_seed_entities(
    country: str,
    technology: str,
    known_projects: list[str],
) -> list[dict[str, Any]]:
    entities = []
    for index, name in enumerate(known_projects, start=1):
        priority_fields = build_frontier_priority_fields(
            name,
            "project",
            f"{country} {technology} runtime known project seed",
            search_round=1,
            expansion_depth=0,
        )
        entities.append(
            {
                "entity_id": f"SEED-{index:04d}",
                "name": name,
                "aliases": expand_aliases(name),
                "entity_type": "project",
                "language": "unknown",
                "source_found": ["--known-projects"],
                "origin": "runtime-seed",
                "country": country,
                **priority_fields,
                "search_round": 1,
                "queries_generated": generate_entity_queries(name, "project", country, technology),
                "search_status": "pending",
                "classification": "candidate",
                "parent_entity_ids": [],
            }
        )
    return entities


def classify_entity_name(name: str) -> str:
    upper_name = name.upper()
    lowered_name = name.lower()
    finance_terms = {"ADB", "AIIB", "EBRD", "IFC", "MIGA", "JICA", "FMO", "DEG", "SCB", "SMBC", "SINOSURE"}
    if re.fullmatch(r"(?:PP|PQ|UP)[-\s]?\d+", upper_name):
        return "law_decree"
    if upper_name in finance_terms:
        return "finance"
    if any(term in lowered_name for term in ADJACENT_TERMS):
        return "adjacent_opportunity"
    if any(term in lowered_name for term in ["grid", "transmission", "interconnection", "substation"]):
        return "grid_entity"
    if any(term in lowered_name for term in ["offtaker", "offtake", "buyer", "uzenergosotish"]):
        return "offtaker"
    if any(term in lowered_name for term in ["logistics", "transport", "port", "rail", "crane", "heavy lift"]):
        return "logistics"
    if any(term in lowered_name for term in ["manufacturing", "factory", "localization", "localisation"]):
        return "local_manufacturing"
    if any(term in lowered_name for term in P2_TERMS):
        return "supply_chain"
    if any(term in lowered_name for term in P4_TERMS):
        return "macro_energy"
    return "project"


def extract_frontier_entities_from_text(
    text: str,
    country: str,
    technology: str,
    search_round: int,
    source_found: str,
) -> list[dict[str, Any]]:
    stopwords = {
        "Wind",
        "Project",
        "Power",
        "Farm",
        "PPA",
        "EPC",
        "COD",
        "MW",
        "GW",
        "PP",
        "PQ",
        "UP",
        "Uzbekistan",
        "Green",
    }
    candidates: list[str] = []
    candidates.extend(re.findall(r"\b(?:PP|PQ|UP)[-\s]?\d+\b", text))
    phrase_candidates = re.findall(
        r"\b[A-Z][A-Za-z0-9'’`ʻʼ-]{2,}(?:\s+[A-Z][A-Za-z0-9'’`ʻʼ-]{2,}){0,2}\b",
        text,
    )
    candidates.extend(phrase_candidates)
    for phrase in phrase_candidates:
        for part in phrase.split():
            if part not in stopwords and len(part) > 2:
                candidates.append(part)
    candidates.extend(re.findall(r"\b[A-Z]{2,10}\b", text))

    seen: set[str] = set()
    entities = []
    for raw_name in candidates:
        name = raw_name.strip()
        if not name or name in stopwords:
            continue
        entity_type = classify_entity_name(name)
        key = normalize_entity_key(name, entity_type)
        if key in seen:
            continue
        seen.add(key)
        entity_id = f"ENT-{len(entities) + 1:04d}"
        display_name = name.replace(" ", "-") if entity_type == "law_decree" else name
        local_context = local_context_for_entity(text, name)
        priority_fields = build_frontier_priority_fields(
            display_name,
            entity_type,
            local_context,
            search_round=search_round,
        )
        entities.append(
            {
                "entity_id": entity_id,
                "name": display_name,
                "aliases": expand_aliases(name),
                "entity_type": entity_type,
                "language": "unknown",
                "source_found": [source_found],
                "origin": "extracted",
                "country": country,
                **priority_fields,
                "search_round": search_round,
                "queries_generated": generate_entity_queries(name, entity_type, country, technology),
                "search_status": "pending",
                "classification": "candidate",
                "parent_entity_ids": [],
            }
        )
    return entities


def build_plan(
    country: str,
    technology: str,
    audience: str,
    output_slug: str | None,
    official_languages: list[str] | None = None,
    known_projects: list[str] | None = None,
    include_benchmark: bool = False,
) -> dict[str, Any]:
    year = datetime.now(timezone.utc).year
    slug = output_slug or f"{slugify(country)}-{slugify(technology)}"
    official_languages = official_languages or []
    known_projects = known_projects or []
    runtime_seed_entities = build_runtime_seed_entities(country, technology, known_projects)
    dimensions = []
    for dimension in DIMENSIONS:
        if dimension["id"] == "regional-benchmark" and not include_benchmark:
            continue
        intent = dimension["intent"]
        queries = [
            render_query_with_context(pattern, country, technology, year, audience, official_languages, known_projects)
            for pattern in dimension["patterns"]
        ]
        dimensions.append(
            {
                "id": dimension["id"],
                "intent": intent,
                "freshness": dimension["freshness"],
                "focus": dimension["focus"],
                "queries": queries,
                "domainBoost": dimension["domainBoost"],
                "scoringWeights": INTENT_WEIGHTS[intent],
                "depthFile": f"data/renewable-market/depth/{dimension['id']}.json",
                "minimumEvidence": {
                    "records": 3,
                    "uniqueUrls": 3,
                    "collectionMethods": ["exa-search"],
                    "preferredVerificationMethods": ["chrome-mcp"],
                    "requiredPasses": required_passes_for_dimension(dimension["id"]),
                    "requiredFields": ["topic", "facts", "sources", "confidence", "uncertainty"],
                },
            }
        )
    return {
        "version": "1.0",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "country": country,
        "technology": technology,
        "audience": audience,
        "officialLanguages": official_languages,
        "knownProjects": known_projects,
        "includeBenchmark": include_benchmark,
        "slug": slug,
        "toolLanes": TOOL_LANES,
        "workflowPhases": WORKFLOW_PHASES,
        "fullReportArchitecture": FULL_REPORT_ARCHITECTURE,
        "fullReportGenerationPipeline": V4_REPORT_GENERATION_PIPELINE,
        "v4FullReportAgentProfile": V4_FULL_REPORT_AGENT_PROFILE,
        "v4AgentTopology": V4_AGENT_TOPOLOGY,
        "v4ChapterVerificationPolicy": V4_CHAPTER_VERIFICATION_POLICY,
        "v4ChapterAgentPlan": V4_CHAPTER_AGENT_PLAN,
        "seedEntitiesPath": f"data/renewable-market/{slug}-seed_entities.json",
        "searchFrontierPath": f"data/renewable-market/{slug}-search_frontier.json",
        "discoveredEntriesPath": f"data/renewable-market/{slug}-discovered_entries.json",
        "authoritySourceRegistryPath": f"data/renewable-market/{slug}-authority_sources.json",
        "searchCoverageMatrixPath": f"data/renewable-market/{slug}-search_coverage_matrix.md",
        "frontierConvergenceReportPath": f"data/renewable-market/{slug}-frontier_convergence.json",
        "frontierExecutionReviewPath": f"data/renewable-market/{slug}-frontier_execution_review.json",
        "recallMode": {
            "minimumRecallRounds": MINIMUM_RECALL_ROUNDS,
            "frontierStallRoundsAfterMinimum": FRONTIER_STALL_ROUNDS,
            "candidatePool": f"data/renewable-market/{slug}-candidate_project_pool.json",
            "entryCategories": RECALL_ENTRY_CATEGORIES,
            "fixedSeedTemplates": render_seed_templates(country, technology, official_languages),
            "runtimeSeedEntities": runtime_seed_entities,
            "recallRounds": RECALL_ROUNDS,
            "frontierEntityContract": FRONTIER_ENTITY_CONTRACT,
            "frontierPriorityLevels": FRONTIER_PRIORITY_LEVELS,
            "frontierBoundaryPolicy": FRONTIER_BOUNDARY_POLICY,
            "highPriorityFrontierLevels": HIGH_PRIORITY_FRONTIER_LEVELS,
            "p0p1ExecutionEvaluationPolicy": P0_P1_EXECUTION_EVALUATION_POLICY,
            "authoritySourceCategories": AUTHORITY_SOURCE_CATEGORIES,
            "frontierConvergencePolicy": FRONTIER_CONVERGENCE_POLICY,
            "admissionRule": (
                "Record any lead with a project name plus at least one capacity, actor, location, "
                "agreement, decree, news, financing, PPA/grid, OEM/EPC, or adjacent-opportunity clue."
            ),
            "doNotRejectDuringRecall": True,
            "initialRunState": {
                "completedRecallRounds": 0,
                "canEnterVerificationMode": False,
                "blockedBy": ["minimum_recall_round_gate"],
                "blockingFrontierPriorityLevels": HIGH_PRIORITY_FRONTIER_LEVELS,
                "blockingFrontierStatuses": ["pending"],
            },
        },
        "verificationMode": {
            "sourceTrace": f"data/renewable-market/{slug}-source_trace.json",
            "frontierExecutionReview": f"data/renewable-market/{slug}-frontier_execution_review.json",
            "ledgerStatuses": LEDGER_STATUSES,
            "verifiedMethods": ["chrome-mcp", "exa-fetch", "manual-file"],
            "exaBoundaryChromeHandoffPolicy": EXA_BOUNDARY_CHROME_HANDOFF_POLICY,
            "canEnterVerificationMode": {
                "requires": FRONTIER_CONVERGENCE_POLICY["requiredBeforeVerification"],
                "minimumRecallRounds": MINIMUM_RECALL_ROUNDS,
            },
            "ledgerAdmissionRequires": P0_P1_EXECUTION_EVALUATION_POLICY["requiredBeforeLedgerAdmission"],
            "rule": "V4 full reports are generated from the reconciled ledger and rich master JSON, not raw recall notes.",
        },
        "schedulerGates": SCHEDULER_GATES,
        "dimensions": dimensions,
        "outputs": {
            "index": "data/renewable-market/index.json",
            "seedEntities": f"data/renewable-market/{slug}-seed_entities.json",
            "searchFrontier": f"data/renewable-market/{slug}-search_frontier.json",
            "discoveredEntries": f"data/renewable-market/{slug}-discovered_entries.json",
            "authoritySourceRegistry": f"data/renewable-market/{slug}-authority_sources.json",
            "candidateProjectPool": f"data/renewable-market/{slug}-candidate_project_pool.json",
            "developerProjectMap": f"data/renewable-market/{slug}-developer_project_map.json",
            "sourceTrace": f"data/renewable-market/{slug}-source_trace.json",
            "frontierExecutionReview": f"data/renewable-market/{slug}-frontier_execution_review.json",
            "mainJson": f"data/renewable-market/{slug}.json",
            "pipelineLedger": f"data/renewable-market/{slug}-pipeline-ledger.json",
            "projectLedger": f"data/renewable-market/{slug}-project_ledger.json",
            "projectCards": f"data/renewable-market/{slug}-project_cards.json",
            "participantLedger": f"data/renewable-market/{slug}-participant_ledger.json",
            "oemCompetition": f"data/renewable-market/{slug}-oem_competition.json",
            "procurementWindow": f"data/renewable-market/{slug}-procurement_window.json",
            "evidenceTable": f"data/renewable-market/{slug}-evidence_table.json",
            "riskMatrix": f"data/renewable-market/{slug}-risk_matrix.json",
            "trackingWatchlist": f"data/renewable-market/{slug}-tracking_watchlist.json",
            "v4AgentPlan": f"data/renewable-market/{slug}-v4_agent_plan.json",
            "chapterDraftsDir": "data/renewable-market/report_chapters/",
            "chapterVerificationDir": "data/renewable-market/chapter_verification/",
            "projectsCsv": f"data/renewable-market/{slug}.csv",
            "timelineCsv": f"data/renewable-market/{slug}-project-timeline.csv",
            "capacityReconciliationMd": f"data/renewable-market/{slug}-capacity_reconciliation.md",
            "contradictionQueue": f"data/renewable-market/{slug}-contradiction_queue.json",
            "searchCoverageMatrix": f"data/renewable-market/{slug}-search_coverage_matrix.md",
            "frontierConvergenceReport": f"data/renewable-market/{slug}-frontier_convergence.json",
            "fullReportMd": f"data/renewable-market/{slug}-report.md",
            "liteReportMd": f"data/renewable-market/{slug}-lite.md",
            "fullReportPdf": f"data/renewable-market/{slug}-report.pdf",
            "liteReportPdf": f"data/renewable-market/{slug}-lite.pdf",
        },
    }


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


SOURCE_REQUIRED_FIELD_ALIASES = [
    ("url",),
    ("title",),
    ("publisher",),
    ("accessedAt", "accessed_at"),
    ("sourceLanguage", "source_language"),
    ("collectionMethod", "collection_method"),
]


def get_any(mapping: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    for alias in aliases:
        value = mapping.get(alias)
        if value not in (None, "", []):
            return value
    return None


def source_urls(record: dict[str, Any]) -> list[str]:
    urls = []
    sources = record.get("sources", [])
    if isinstance(sources, list):
        for source in sources:
            if isinstance(source, dict) and source.get("url"):
                urls.append(str(source["url"]))
    facts = record.get("facts", [])
    if isinstance(facts, list):
        for fact in facts:
            if isinstance(fact, dict):
                fact_sources = fact.get("sources", [])
                if isinstance(fact_sources, list):
                    for source in fact_sources:
                        if isinstance(source, dict) and source.get("url"):
                            urls.append(str(source["url"]))
    return urls



def source_missing_fields(record: dict[str, Any]) -> list[str]:
    issues = []
    sources = record.get("sources", [])
    if isinstance(sources, list):
        for source_index, source in enumerate(sources):
            if isinstance(source, dict):
                missing = []
                for aliases in SOURCE_REQUIRED_FIELD_ALIASES:
                    if get_any(source, aliases) is None and get_any(record, aliases) is None:
                        missing.append("/".join(aliases))
                if missing:
                    issues.append(f"source {source_index} missing fields: {', '.join(missing)}")
    facts = record.get("facts", [])
    if isinstance(facts, list):
        for fact_index, fact in enumerate(facts):
            if not isinstance(fact, dict):
                continue
            fact_sources = fact.get("sources", [])
            if isinstance(fact_sources, list):
                for source_index, source in enumerate(fact_sources):
                    if isinstance(source, dict):
                        missing = []
                        for aliases in SOURCE_REQUIRED_FIELD_ALIASES:
                            if get_any(source, aliases) is None and get_any(fact, aliases) is None and get_any(record, aliases) is None:
                                missing.append("/".join(aliases))
                        if missing:
                            issues.append(
                                f"fact {fact_index} source {source_index} missing fields: {', '.join(missing)}"
                            )
    return issues


def record_search_passes(record: dict[str, Any]) -> list[str]:
    passes: list[str] = []
    for key in ("searchPass", "search_pass"):
        value = record.get(key)
        if isinstance(value, str) and value:
            passes.append(value)
    for key in ("searchPasses", "search_passes", "coverageTags", "coverage_tags"):
        value = record.get(key)
        if isinstance(value, list):
            passes.extend(str(item) for item in value if item)
        elif isinstance(value, str) and value:
            passes.append(value)
    return passes


def record_collection_methods(record: dict[str, Any]) -> list[str]:
    methods: list[str] = []
    method = get_any(record, ("collectionMethod", "collection_method"))
    if isinstance(method, str) and method:
        methods.append(method)
    sources = record.get("sources", [])
    if isinstance(sources, list):
        for source in sources:
            if isinstance(source, dict):
                source_method = get_any(source, ("collectionMethod", "collection_method"))
                if isinstance(source_method, str) and source_method:
                    methods.append(source_method)
    facts = record.get("facts", [])
    if isinstance(facts, list):
        for fact in facts:
            if not isinstance(fact, dict):
                continue
            fact_sources = fact.get("sources", [])
            if isinstance(fact_sources, list):
                for source in fact_sources:
                    if isinstance(source, dict):
                        source_method = get_any(source, ("collectionMethod", "collection_method"))
                        if isinstance(source_method, str) and source_method:
                            methods.append(source_method)
    if not methods and isinstance(record.get("notes"), str) and "chrome" in record["notes"].lower():
        methods.append("chrome-mcp")
    return methods


def record_unavailable_tools(record: dict[str, Any]) -> list[str]:
    unavailable: list[str] = []
    for key in ("tool_unavailable", "toolUnavailable", "unavailableTool", "unavailable_tool"):
        value = record.get(key)
        if isinstance(value, str) and value:
            unavailable.append(value)
        elif isinstance(value, list):
            unavailable.extend(str(item) for item in value if item)
    tools = record.get("tools", {})
    if isinstance(tools, dict):
        for tool_name, status in tools.items():
            if isinstance(status, str) and status.lower() in {"unavailable", "blocked", "missing"}:
                unavailable.append(str(tool_name))
            elif isinstance(status, dict):
                tool_status = str(status.get("status", "")).lower()
                if tool_status in {"unavailable", "blocked", "missing"}:
                    unavailable.append(str(tool_name))
    notes = str(record.get("notes", "")).lower()
    if "chrome" in notes and any(term in notes for term in ("unavailable", "not available", "blocked", "missing")):
        unavailable.append("chrome-mcp")
    return unavailable


def record_missing_fields(record: dict[str, Any], fields: list[str]) -> list[str]:
    missing = []
    for field in fields:
        value = record.get(field)
        if value in (None, "", []):
            missing.append(field)
    return missing


def validate_depth_file(path: Path, minimum: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "status": "missing", "records": 0, "uniqueUrls": 0, "issues": ["file not found"]}
    data = load_json(path)
    if not isinstance(data, list):
        return {"path": str(path), "status": "invalid", "records": 0, "uniqueUrls": 0, "issues": ["depth file must be a JSON array"]}

    required_fields = minimum.get("requiredFields", [])
    urls: set[str] = set()
    methods: Counter[str] = Counter()
    search_passes: Counter[str] = Counter()
    unavailable_tools: Counter[str] = Counter()
    issues = []
    for index, record in enumerate(data):
        if not isinstance(record, dict):
            issues.append(f"record {index} is not an object")
            continue
        missing = record_missing_fields(record, required_fields)
        if missing:
            issues.append(f"record {index} missing fields: {', '.join(missing)}")
        for source_issue in source_missing_fields(record):
            issues.append(f"record {index} {source_issue}")
        urls.update(source_urls(record))
        for method in record_collection_methods(record):
            methods[method] += 1
        for tool in record_unavailable_tools(record):
            unavailable_tools[tool] += 1
        for search_pass in record_search_passes(record):
            search_passes[search_pass] += 1

    min_records = int(minimum.get("records", 0))
    min_urls = int(minimum.get("uniqueUrls", 0))
    required_methods = minimum.get("collectionMethods", [])
    required_passes = minimum.get("requiredPasses", [])
    if len(data) < min_records:
        issues.append(f"record count {len(data)} below minimum {min_records}")
    if len(urls) < min_urls:
        issues.append(f"unique URL count {len(urls)} below minimum {min_urls}")
    missing_methods = [method for method in required_methods if methods.get(method, 0) == 0]
    if missing_methods:
        issues.append(f"missing required collection methods: {', '.join(missing_methods)}")
    missing_passes = [search_pass for search_pass in required_passes if search_passes.get(search_pass, 0) == 0]
    if missing_passes:
        issues.append(f"missing required search passes: {', '.join(missing_passes)}")
    if "chrome-verification" in required_passes and methods.get("chrome-mcp", 0) == 0 and unavailable_tools.get("chrome-mcp", 0) == 0:
        issues.append(
            "chrome-verification required but no chrome-mcp collectionMethod or tool_unavailable=chrome-mcp record found"
        )

    status = "pass" if not issues else "needs-work"
    return {
        "path": str(path),
        "status": status,
        "records": len(data),
        "uniqueUrls": len(urls),
        "collectionMethods": dict(methods),
        "unavailableTools": dict(unavailable_tools),
        "searchPasses": dict(search_passes),
        "issues": issues,
    }


def validate_plan(plan_path: Path, depth_dir: Path) -> dict[str, Any]:
    plan = load_json(plan_path)
    dimensions = plan.get("dimensions", [])
    results = []
    for dimension in dimensions:
        if not isinstance(dimension, dict):
            continue
        depth_file = Path(str(dimension.get("depthFile", "")))
        if not depth_file.is_absolute():
            depth_file = depth_dir / depth_file.name
        results.append(validate_depth_file(depth_file, dimension.get("minimumEvidence", {})))
    summary = Counter(result["status"] for result in results)
    return {
        "plan": str(plan_path),
        "depthDir": str(depth_dir),
        "validatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": dict(summary),
        "dimensions": results,
        "overallStatus": "pass" if summary and set(summary) == {"pass"} else "needs-work",
    }


def write_json(data: dict[str, Any], output: Path | None) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def split_csv_arg(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan or validate renewable market search coverage.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="Generate a dimension-level search plan JSON.")
    plan_parser.add_argument("--country", required=True)
    plan_parser.add_argument("--technology", required=True)
    plan_parser.add_argument("--audience", default="commercial-entry")
    plan_parser.add_argument("--slug")
    plan_parser.add_argument("--official-languages", help="Comma-separated official/local languages to force into search passes.")
    plan_parser.add_argument("--known-projects", help="Comma-separated seed project names for alias and anomaly searches.")
    plan_parser.add_argument("--include-benchmark", action="store_true", help="Include regional/peer-country benchmark dimension only when explicitly requested.")
    plan_parser.add_argument("--output", type=Path)

    validate_parser = subparsers.add_parser("validate", help="Validate depth JSON coverage against a search plan.")
    validate_parser.add_argument("--plan", required=True, type=Path)
    validate_parser.add_argument("--depth-dir", default=Path("data/renewable-market/depth"), type=Path)
    validate_parser.add_argument("--output", type=Path)

    extract_parser = subparsers.add_parser(
        "extract-frontier",
        help="Extract candidate frontier entities from a text fixture or extracted source text.",
    )
    extract_parser.add_argument("--country", required=True)
    extract_parser.add_argument("--technology", required=True)
    extract_parser.add_argument("--round", default=1, type=int)
    extract_parser.add_argument("--source", default="manual-fixture")
    extract_input = extract_parser.add_mutually_exclusive_group(required=True)
    extract_input.add_argument("--text")
    extract_input.add_argument("--input", type=Path)
    extract_parser.add_argument("--output", type=Path)

    args = parser.parse_args()
    if args.command == "plan":
        data = build_plan(
            args.country,
            args.technology,
            args.audience,
            args.slug,
            split_csv_arg(args.official_languages),
            split_csv_arg(args.known_projects),
            args.include_benchmark,
        )
        write_json(data, args.output)
        return 0
    if args.command == "validate":
        data = validate_plan(args.plan, args.depth_dir)
        write_json(data, args.output)
        return 0 if data["overallStatus"] == "pass" else 1
    if args.command == "extract-frontier":
        text = args.text if args.text is not None else args.input.read_text(encoding="utf-8-sig")
        data = {
            "country": args.country,
            "technology": args.technology,
            "searchRound": args.round,
            "sourceFound": args.source,
            "entities": extract_frontier_entities_from_text(
                text,
                args.country,
                args.technology,
                args.round,
                args.source,
            ),
        }
        write_json(data, args.output)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
