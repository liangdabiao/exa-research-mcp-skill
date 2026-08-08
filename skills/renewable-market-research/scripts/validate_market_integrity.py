#!/usr/bin/env python3
"""Validate source-to-final integrity for renewable market JSON outputs."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

SOURCE_FIELD_ALIASES = [
    ("url",),
    ("title",),
    ("publisher",),
    ("accessedAt", "accessed_at"),
    ("sourceLanguage", "source_language"),
    ("collectionMethod", "collection_method"),
]

PROJECT_NAME_FIELDS = ("canonicalName", "canonical_name", "project_name", "name")
PROJECT_ID_FIELDS = ("canonicalProjectId", "canonical_project_id", "id", "project_id")
DEDUP_FIELD_ALIASES = ("dedupeKey", "dedupe_key")
SOURCE_TRACE_ALIASES = ("sourceTrace", "source_trace")
NAME_VARIANT_ALIASES = ("nameVariants", "name_variants", "aliases")
VERIFIED_COLLECTION_METHODS = {"chrome-mcp", "exa-fetch", "manual-file"}
CRITICAL_FIELD_VERIFICATION_ALIASES = ("criticalFieldVerification", "critical_field_verification")
UNKNOWN_ALLOWED_MARKERS = {"待核", "待核实", "未公开", "未披露", "not found", "unavailable", "not applicable", "unknown"}
V4_LEDGER_REQUIRED_FIELDS = [
    "projectId",
    "aliasGroupId",
    "canonicalProjectName",
    "capacityMW",
    "opportunityMW",
    "projectStage",
    "statusBasis",
    "countedInConfirmedCapacity",
    "countedInOpportunityCapacity",
    "sponsorOwner",
    "spv",
    "equityStructure",
    "oem",
    "procurementStatus",
    "turbineModel",
    "epc",
    "omParty",
    "financiers",
    "ppaOfftaker",
    "tariff",
    "codTimeline",
    "nextMilestone",
    "decisionMaker",
    "keyEvidence",
    "fieldConfidence",
    "pendingVerification",
    "mingyangRelevance",
    "mainRisks",
]
V4_PROJECT_CARD_REQUIRED_PATHS = [
    "basicInformation.projectName",
    "basicInformation.capacityMW",
    "basicInformation.location",
    "basicInformation.stage",
    "basicInformation.cod",
    "ownerStructure.developer",
    "ownerStructure.spv",
    "ownerStructure.equity",
    "ownerStructure.governmentCounterparty",
    "technicalPlan.oem",
    "technicalPlan.turbineModel",
    "technicalPlan.turbineCount",
    "technicalPlan.bess",
    "technicalPlan.transmissionLine",
    "commercialStructure.ppa",
    "commercialStructure.offtaker",
    "commercialStructure.tariff",
    "commercialStructure.tenor",
    "commercialStructure.guarantee",
    "financingStructure.totalInvestment",
    "financingStructure.lenders",
    "financingStructure.financialCloseStatus",
    "developmentFlow.land",
    "developmentFlow.esia",
    "developmentFlow.interconnection",
    "developmentFlow.constructionPermit",
    "developmentFlow.electricityLicense",
    "engineeringSupplyChain.epc",
    "engineeringSupplyChain.logistics",
    "engineeringSupplyChain.lifting",
    "engineeringSupplyChain.localizationRequirements",
    "omArrangement.omParty",
    "omArrangement.serviceTenor",
    "omArrangement.spareParts",
    "omArrangement.localServiceBase",
    "currentProgress.latestEvent",
    "currentProgress.nextNode",
    "currentProgress.procurementWindow",
    "decisionChain.decisionMaker",
    "decisionChain.influencers",
    "decisionChain.mdbGovernmentEpcRoles",
    "mingyangRelevance.opportunityMW",
    "mingyangRelevance.relevanceRationale",
    "mingyangRelevance.pendingVerification",
    "risksAndConstraints.grid",
    "risksAndConstraints.land",
    "risksAndConstraints.esg",
    "risksAndConstraints.financing",
    "risksAndConstraints.competition",
    "evidenceBoundary.verifiedFacts",
    "evidenceBoundary.reasonableAssumptions",
    "evidenceBoundary.pendingVerification",
]
V4_EVIDENCE_REQUIRED_FIELDS = [
    "projectStage",
    "capacityMW",
    "oem",
    "tariff",
    "financing",
    "ppaOfftaker",
    "procurementWindow",
    "mingyangRelevance",
]
NO_STRATEGY_PATTERNS = [
    "应当建厂",
    "建议建厂",
    "必须进入",
    "建议报价",
    "必须绑定",
    "应绑定",
    "应该投入资源",
    "应投入资源",
    "must enter",
    "should enter",
    "must build",
    "should build",
    "build a factory",
    "recommended bid",
    "must bind",
]
CRITICAL_PROJECT_FIELDS = [
    ("project_name", ("project_name", "name", "canonicalName", "canonical_name"), ("project", "name", "alias")),
    ("capacity_mw", ("capacityMW", "capacity_mw"), ("capacity", "mw")),
    ("status", ("status", "pipelineBucket", "pipeline_bucket", "evidenceStage", "evidence_stage"), ("status", "stage", "bucket")),
    ("owner_developer", ("developer", "owner_developer", "ownerDeveloper", "sponsor", "spv"), ("owner", "developer", "sponsor", "spv")),
    ("location", ("location", "region", "site"), ("location", "region", "site")),
    ("cod_or_target_cod", ("cod", "codOrTargetCod", "cod_or_target_cod", "targetCod", "target_cod"), ("cod", "commercial operation", "target cod")),
    ("ppa", ("ppaType", "ppa_type", "ppaDuration", "ppa_duration", "ppaDate", "ppa_date"), ("ppa",)),
    ("financing", ("financing", "investmentUSD", "investment_usd", "financingClosed", "financing_closed"), ("financing", "investment", "loan")),
    ("epc_oem", ("epc", "turbineModel", "turbine_model", "turbineCount", "turbine_count"), ("epc", "oem", "turbine")),
    ("construction", ("constructionStart", "construction_start"), ("construction", "start")),
]
RICH_PROJECT_FIELDS = [
    ("annualGenerationGWh", ("annualGenerationGWh", "annual_generation_gwh", "annualGeneration", "annual_generation")),
    (
        "annualCO2ReductionTonnes",
        ("annualCO2ReductionTonnes", "annual_co2_reduction_tonnes", "co2ReductionTonnes", "co2_reduction_tonnes"),
    ),
    ("investmentUSD", ("investmentUSD", "investment_usd", "investment", "capexUSD", "capex_usd")),
    ("turbineModel", ("turbineModel", "turbine_model", "oemModel", "oem_model")),
    ("turbineCount", ("turbineCount", "turbine_count", "numberOfTurbines", "number_of_turbines")),
    ("storageMWh", ("storageMWh", "storage_mwh", "bessMWh", "bess_mwh")),
    ("coordinates", ("coordinates", "coordinate", "latLon", "lat_lon")),
    ("siteAreaHa", ("siteAreaHa", "site_area_ha", "landAreaHa", "land_area_ha")),
    ("hubHeightM", ("hubHeightM", "hub_height_m", "hubHeight", "hub_height")),
    ("rotorDiameterM", ("rotorDiameterM", "rotor_diameter_m", "rotorDiameter", "rotor_diameter")),
    ("bladeLengthM", ("bladeLengthM", "blade_length_m", "bladeLength", "blade_length")),
    ("technologyRoute", ("technologyRoute", "technology_route", "technology")),
    (
        "jobsOrLocalEmployment",
        ("jobsOrLocalEmployment", "jobs_or_local_employment", "localEmployment", "local_employment", "jobs"),
    ),
    (
        "biodiversityBirdProtection",
        (
            "biodiversityBirdProtection",
            "biodiversity_bird_protection",
            "birdProtection",
            "bird_protection",
            "biodiversity",
        ),
    ),
    (
        "communityLandImpact",
        ("communityLandImpact", "community_land_impact", "communityImpact", "community_impact", "landImpact", "land_impact"),
    ),
    ("logisticsRoute", ("logisticsRoute", "logistics_route", "transportRoute", "transport_route")),
    ("keyPeople", ("keyPeople", "key_people", "personnel", "management")),
    ("currentOemStatus", ("currentOemStatus", "current_oem_status", "oemStatus", "oem_status")),
    ("oemShortlist", ("oemShortlist", "oem_shortlist", "shortlistedOems", "shortlisted_oems")),
    ("procurementWindow", ("procurementWindow", "procurement_window", "decisionWindow", "decision_window")),
    ("decisionMaker", ("decisionMaker", "decision_maker", "procurementDecisionMaker", "procurement_decision_maker")),
    ("procurementInfluencers", ("procurementInfluencers", "procurement_influencers", "influencers")),
    ("likelyTenderRoute", ("likelyTenderRoute", "likely_tender_route", "tenderRoute", "tender_route")),
    ("bankabilityConstraint", ("bankabilityConstraint", "bankability_constraint")),
    ("salesEntryPoint", ("salesEntryPoint", "sales_entry_point", "entryPoint", "entry_point")),
    ("adjacentOpportunityImpact", ("adjacentOpportunityImpact", "adjacent_opportunity_impact")),
]
REPORT_READY_PROJECT_FIELDS = [
    ("annualGenerationGWh", ("annualGenerationGWh", "annual_generation_gwh", "annualGeneration", "annual_generation")),
    (
        "annualCO2ReductionTonnes",
        ("annualCO2ReductionTonnes", "annual_co2_reduction_tonnes", "co2ReductionTonnes", "co2_reduction_tonnes"),
    ),
    ("investmentUSD", ("investmentUSD", "investment_usd", "investment", "capexUSD", "capex_usd")),
    ("turbineModel", ("turbineModel", "turbine_model", "oemModel", "oem_model")),
    ("turbineCount", ("turbineCount", "turbine_count", "numberOfTurbines", "number_of_turbines")),
    ("storageMWh", ("storageMWh", "storage_mwh", "bessMWh", "bess_mwh")),
]
RICH_FIELD_CONTAINER_ALIASES = (
    "cardFields",
    "card_fields",
    "projectCard",
    "project_card",
    "reportCard",
    "report_card",
    "technicalSpecs",
    "technical_specs",
    "projectDetails",
    "project_details",
)
FIELD_AVAILABILITY_ALIASES = (
    "fieldAvailability",
    "field_availability",
    "missingRichFields",
    "missing_rich_fields",
    "richFieldGaps",
    "rich_field_gaps",
    "reportCardGaps",
    "report_card_gaps",
    "remainingGaps",
    "remaining_gaps",
)
DEPTH_PROJECT_NAME_FIELDS = (
    "project",
    "projectName",
    "project_name",
    "canonicalName",
    "canonical_name",
    "name",
    "topic",
)
UNAVAILABLE_MARKERS = {"unavailable", "not found", "unknown", "n/a", "na", "none", "null", "not applicable"}
LEGAL_BASIS_FIELDS = (
    "legalBasis",
    "legal_basis",
    "lawNumber",
    "law_number",
    "decreeNumber",
    "decree_number",
    "orderNumber",
    "order_number",
    "originalLegalSource",
    "original_legal_source",
)


def get_any(mapping: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    for alias in aliases:
        value = mapping.get(alias)
        if value not in (None, "", []):
            return value
    return None


def as_list(value: Any) -> list[Any]:
    if value in (None, "", []):
        return []
    if isinstance(value, list):
        return value
    return [value]


def has_value(value: Any) -> bool:
    if value in (None, "", []):
        return False
    if isinstance(value, str) and value.strip().lower() in UNAVAILABLE_MARKERS:
        return False
    if isinstance(value, dict):
        return any(has_value(item) for item in value.values())
    if isinstance(value, list):
        return any(has_value(item) for item in value)
    return True


def read_json_file(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def nested_get(mapping: dict[str, Any], dotted_path: str) -> Any:
    current: Any = mapping
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def present_or_unknown(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return False
        return True
    if isinstance(value, list):
        return True
    if isinstance(value, dict):
        return True
    return True


def as_number(value: Any) -> float:
    if value in (None, "", []):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
        if match:
            return float(match.group(0))
    return 0.0


def normalize_stage(value: Any) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def collect_v4_ledger_projects(ledger: Any) -> list[dict[str, Any]]:
    if isinstance(ledger, list):
        return [item for item in ledger if isinstance(item, dict)]
    if isinstance(ledger, dict):
        for key in ("projects", "projectLedger", "project_ledger", "items"):
            value = ledger.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def collect_v4_project_cards(cards: Any) -> list[dict[str, Any]]:
    if isinstance(cards, list):
        return [item for item in cards if isinstance(item, dict)]
    if isinstance(cards, dict):
        for key in ("projectCards", "project_cards", "cards", "items"):
            value = cards.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def collect_v4_evidence_items(evidence_table: Any) -> list[dict[str, Any]]:
    if isinstance(evidence_table, list):
        return [item for item in evidence_table if isinstance(item, dict)]
    if isinstance(evidence_table, dict):
        for key in ("items", "evidence", "evidenceTable", "evidence_table", "conclusions"):
            value = evidence_table.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def append_warning(result: dict[str, Any], message: str) -> None:
    result.setdefault("warnings", []).append(message)
    result.setdefault("counts", {})["warnings"] = len(result.get("warnings", []))


def add_gate_gap(result: dict[str, Any], key: str, gap: dict[str, Any], warning: str | None = None) -> None:
    result.setdefault(key, []).append(gap)
    if warning:
        append_warning(result, warning)


def get_nested_any(mapping: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    value = get_any(mapping, aliases)
    if value is not None:
        return value
    for container_alias in RICH_FIELD_CONTAINER_ALIASES:
        container = mapping.get(container_alias)
        if isinstance(container, dict):
            value = get_any(container, aliases)
            if value is not None:
                return value
    return None


def find_alias_value(value: Any, aliases: tuple[str, ...], depth: int = 0) -> Any:
    if depth > 4:
        return None
    if isinstance(value, dict):
        direct = get_any(value, aliases)
        if direct is not None:
            return direct
        for child_key, child_value in value.items():
            if child_key in {"sources", "evidence", "sourceTrace", "source_trace"}:
                continue
            found = find_alias_value(child_value, aliases, depth + 1)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value:
            found = find_alias_value(item, aliases, depth + 1)
            if found is not None:
                return found
    return None


def normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).lower()
    text = re.sub(r"[\W_]+", " ", text, flags=re.UNICODE)
    for word in ("wind", "solar", "farm", "power", "plant", "project", "phase", "llp", "llc", "jsc", "spv"):
        text = re.sub(rf"\b{word}\b", " ", text)
    return re.sub(r"\s+", "", text)


def project_name(project: dict[str, Any]) -> str:
    return str(get_any(project, PROJECT_NAME_FIELDS) or "")


def project_id(project: dict[str, Any], index: int) -> str:
    return str(get_any(project, PROJECT_ID_FIELDS) or f"index-{index}")


def capacity_bucket(value: Any) -> str:
    try:
        return str(round(float(value)))
    except (TypeError, ValueError):
        return "unknown"


def dedupe_key(project: dict[str, Any]) -> str:
    explicit = get_any(project, DEDUP_FIELD_ALIASES)
    if explicit:
        return str(explicit)
    name_key = normalize_text(project_name(project))
    location_key = normalize_text(project.get("location"))
    capacity_key = capacity_bucket(project.get("capacityMW", project.get("capacity_mw")))
    developer_key = normalize_text(project.get("developer", project.get("owner_developer")))
    return "|".join([name_key, location_key, capacity_key, developer_key])


def collect_sources(record: dict[str, Any]) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    for key in ("sources", "evidence"):
        value = record.get(key)
        if isinstance(value, list):
            sources.extend(item for item in value if isinstance(item, dict))
    facts = record.get("facts")
    if isinstance(facts, list):
        for fact in facts:
            if isinstance(fact, dict) and isinstance(fact.get("sources"), list):
                sources.extend(item for item in fact["sources"] if isinstance(item, dict))
    return sources


def collect_verification_entries(record: dict[str, Any]) -> list[dict[str, Any]]:
    entries = collect_sources(record)
    for key in SOURCE_TRACE_ALIASES:
        value = record.get(key)
        if isinstance(value, list):
            entries.extend(item for item in value if isinstance(item, dict))
        elif isinstance(value, dict):
            entries.append(value)
    verification = get_any(record, CRITICAL_FIELD_VERIFICATION_ALIASES)
    if isinstance(verification, dict):
        for field, value in verification.items():
            for item in as_list(value):
                if isinstance(item, dict):
                    enriched = dict(item)
                    enriched["_verificationField"] = field
                    entries.append(enriched)
                else:
                    entries.append({"_verificationField": field, "value": item})
    return entries


def entry_collection_method(entry: dict[str, Any]) -> str:
    return str(
        get_any(
            entry,
            ("collectionMethod", "collection_method", "verificationMethod", "verification_method", "method"),
        )
        or ""
    )


def entry_verified_fields(entry: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for key in (
        "_verificationField",
        "verifiedField",
        "verified_field",
        "field",
        "fact",
        "claim",
    ):
        value = entry.get(key)
        if isinstance(value, str):
            values.append(value)
    for key in ("verifiedFields", "verified_fields", "fields", "facts"):
        value = entry.get(key)
        if isinstance(value, list):
            values.extend(str(item) for item in value if item)
        elif isinstance(value, str):
            values.append(value)
    return values


def field_is_present(record: dict[str, Any], aliases: tuple[str, ...]) -> bool:
    return get_any(record, aliases) is not None


def rich_field_present(record: dict[str, Any], aliases: tuple[str, ...]) -> bool:
    return has_value(get_nested_any(record, aliases))


def field_marked_unavailable(record: dict[str, Any], label: str, aliases: tuple[str, ...]) -> bool:
    labels = {normalize_text(label), *(normalize_text(alias) for alias in aliases)}
    for container_alias in FIELD_AVAILABILITY_ALIASES:
        value = record.get(container_alias)
        if isinstance(value, dict):
            for key, item in value.items():
                if normalize_text(key) in labels:
                    if item in (None, "", []):
                        return True
                    if isinstance(item, str) and item.strip().lower() in UNAVAILABLE_MARKERS:
                        return True
                    if isinstance(item, dict):
                        status = str(get_any(item, ("status", "value", "note", "reason")) or "").lower()
                        if any(marker in status for marker in UNAVAILABLE_MARKERS):
                            return True
                    return True
        elif isinstance(value, list):
            for item in value:
                item_text = normalize_text(json.dumps(item, ensure_ascii=False) if isinstance(item, dict) else item)
                if any(field_label and field_label in item_text for field_label in labels):
                    return True
        elif isinstance(value, str):
            item_text = normalize_text(value)
            if any(field_label and field_label in item_text for field_label in labels):
                return True
    return False


def collect_name_values(value: Any) -> list[str]:
    names: list[str] = []
    if isinstance(value, str) and value.strip():
        names.append(value)
    elif isinstance(value, dict):
        for key in ("value", "name", "alias", "project", "projectName", "project_name", "canonicalName", "canonical_name"):
            item = value.get(key)
            if isinstance(item, str) and item.strip():
                names.append(item)
    elif isinstance(value, list):
        for item in value:
            names.extend(collect_name_values(item))
    return names


def project_alias_values(project: dict[str, Any]) -> list[str]:
    names = [project_name(project)]
    for alias_group in (NAME_VARIANT_ALIASES, ("aliases", "projectAliases", "project_aliases")):
        value = get_any(project, alias_group)
        names.extend(collect_name_values(value))
    for field in PROJECT_ID_FIELDS:
        item = project.get(field)
        if isinstance(item, str) and item.strip():
            names.append(item)
    return [name for name in names if name]


def depth_record_names(record: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for field in DEPTH_PROJECT_NAME_FIELDS:
        value = record.get(field)
        if isinstance(value, str) and value.strip():
            names.append(value)
    for alias_group in (NAME_VARIANT_ALIASES, ("aliases", "projectAliases", "project_aliases")):
        names.extend(collect_name_values(get_any(record, alias_group)))
    return names


def iter_json_records(value: Any, location: str = "$", depth: int = 0) -> list[tuple[dict[str, Any], str]]:
    if depth > 4:
        return []
    records: list[tuple[dict[str, Any], str]] = []
    if isinstance(value, list):
        for index, item in enumerate(value):
            item_location = f"{location}[{index}]"
            if isinstance(item, dict):
                records.append((item, item_location))
                for key in ("records", "projects", "items", "findings", "data"):
                    if key in item:
                        records.extend(iter_json_records(item[key], f"{item_location}.{key}", depth + 1))
            elif isinstance(item, list):
                records.extend(iter_json_records(item, item_location, depth + 1))
    elif isinstance(value, dict):
        records.append((value, location))
        for key in ("records", "projects", "items", "findings", "data"):
            if key in value:
                records.extend(iter_json_records(value[key], f"{location}.{key}", depth + 1))
    return records


def collect_depth_records(depth_dir: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    warnings: list[str] = []
    if not depth_dir.exists():
        return records, [f"depth directory does not exist: {depth_dir}"]
    for path in sorted(depth_dir.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            warnings.append(f"depth file {path} is not valid JSON: {exc}")
            continue
        for record, location in iter_json_records(data):
            enriched = dict(record)
            enriched["_depthFile"] = str(path)
            enriched["_depthLocation"] = location
            records.append(enriched)
    return records, warnings


def build_project_match_index(projects: list[Any]) -> list[dict[str, Any]]:
    index: list[dict[str, Any]] = []
    for project_index, project in enumerate(projects):
        if not isinstance(project, dict):
            continue
        keys = {normalize_text(name) for name in project_alias_values(project)}
        keys = {key for key in keys if key}
        index.append(
            {
                "project": project,
                "projectId": project_id(project, project_index),
                "projectName": project_name(project),
                "keys": keys,
            }
        )
    return index


def match_depth_record_to_project(record: dict[str, Any], project_index: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = {normalize_text(name) for name in depth_record_names(record)}
    candidates = {candidate for candidate in candidates if candidate}
    if not candidates:
        trace = record.get("sourceTrace") or record.get("source_trace")
        if isinstance(trace, str):
            candidates.add(normalize_text(trace))
    for candidate in candidates:
        for item in project_index:
            if candidate in item["keys"]:
                return item
    for candidate in candidates:
        if len(candidate) < 5:
            continue
        for item in project_index:
            if any(len(key) >= 5 and (candidate in key or key in candidate) for key in item["keys"]):
                return item
    return None


def validate_depth_propagation(projects: list[Any], depth_dir: Path) -> tuple[list[dict[str, Any]], list[str], list[dict[str, Any]]]:
    gaps: list[dict[str, Any]] = []
    warnings: list[str] = []
    unmatched_records: list[dict[str, Any]] = []
    depth_records, depth_warnings = collect_depth_records(depth_dir)
    warnings.extend(depth_warnings)
    project_index = build_project_match_index(projects)

    for record in depth_records:
        rich_values = []
        for label, aliases in RICH_PROJECT_FIELDS:
            value = find_alias_value(record, aliases)
            if has_value(value):
                rich_values.append((label, aliases, value))
        if not rich_values:
            continue
        matched = match_depth_record_to_project(record, project_index)
        if matched is None:
            unmatched_records.append(
                {
                    "depthFile": record.get("_depthFile"),
                    "location": record.get("_depthLocation"),
                    "recordNames": depth_record_names(record),
                    "fields": [label for label, _, _ in rich_values],
                }
            )
            continue
        project = matched["project"]
        for label, aliases, value in rich_values:
            if not rich_field_present(project, aliases):
                gaps.append(
                    {
                        "projectId": matched["projectId"],
                        "projectName": matched["projectName"],
                        "field": label,
                        "depthFile": record.get("_depthFile"),
                        "depthLocation": record.get("_depthLocation"),
                        "depthValue": value,
                    }
                )
    return gaps, warnings, unmatched_records


def verified_entry_matches_field(
    entry: dict[str, Any],
    label: str,
    aliases: tuple[str, ...],
    keywords: tuple[str, ...],
) -> bool:
    method = entry_collection_method(entry).lower()
    if method not in VERIFIED_COLLECTION_METHODS:
        return False
    field_text = " ".join(entry_verified_fields(entry)).lower()
    if any(token in field_text for token in ("all-critical-fields", "all critical fields")):
        return True
    candidates = [label, *aliases, *keywords]
    normalized = re.sub(r"[\W_]+", " ", field_text)
    return any(re.sub(r"[\W_]+", " ", candidate.lower()).strip() in normalized for candidate in candidates)


def critical_field_verified(record: dict[str, Any], label: str, aliases: tuple[str, ...], keywords: tuple[str, ...]) -> bool:
    return any(verified_entry_matches_field(entry, label, aliases, keywords) for entry in collect_verification_entries(record))


def is_confirmed_pipeline_record(project: dict[str, Any]) -> bool:
    eligible = get_any(project, ("confirmedPipelineEligible", "confirmed_pipeline_eligible"))
    if isinstance(eligible, bool):
        return eligible
    bucket = str(get_any(project, ("pipelineBucket", "pipeline_bucket", "status", "evidenceStage", "evidence_stage")) or "").lower()
    confirmed_tokens = (
        "operational",
        "under_construction",
        "awarded",
        "ppa",
        "financing_closed",
        "financing-closed",
        "construction",
        "cod",
    )
    return any(token in bucket for token in confirmed_tokens) and "watchlist" not in bucket and "rejected" not in bucket


def source_missing_fields(source: dict[str, Any], parent: dict[str, Any]) -> list[str]:
    missing = []
    for aliases in SOURCE_FIELD_ALIASES:
        if get_any(source, aliases) is None and get_any(parent, aliases) is None:
            missing.append("/".join(aliases))
    return missing


def looks_like_policy_target(record: dict[str, Any]) -> bool:
    text = json.dumps(record, ensure_ascii=False).lower()
    indicators = ("target", "2030", "2040", "mw", "gw", "auction", "tariff", "capacity", "目标", "法令", "拍卖", "电价")
    return any(indicator in text for indicator in indicators)


def has_legal_basis(record: dict[str, Any]) -> bool:
    if get_any(record, LEGAL_BASIS_FIELDS) is not None:
        return True
    for source in collect_sources(record):
        source_type = str(get_any(source, ("sourceType", "source_type")) or "").lower()
        title = str(source.get("title", "")).lower()
        if source_type in {"official", "regulator", "auction_document"}:
            return True
        if any(token in title for token in ("law", "decree", "order", "regulation", "resolution")):
            return True
    return False


def validate_market(data: dict[str, Any], depth_dir: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    duplicate_candidates: list[dict[str, Any]] = []
    critical_field_gaps: list[dict[str, Any]] = []
    report_card_field_gaps: list[dict[str, Any]] = []
    depth_propagation_gaps: list[dict[str, Any]] = []
    unmatched_depth_rich_records: list[dict[str, Any]] = []

    projects = data.get("projects", [])
    if not isinstance(projects, list):
        errors.append("top-level projects must be a list")
        projects = []

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, project in enumerate(projects):
        if not isinstance(project, dict):
            warnings.append(f"project {index} is not an object")
            continue
        name = project_name(project)
        pid = project_id(project, index)
        if not name:
            warnings.append(f"project {pid} missing canonical project name")
        if get_any(project, NAME_VARIANT_ALIASES) is None:
            warnings.append(f"project {pid} missing nameVariants/aliases for local-language and translated names")
        if get_any(project, SOURCE_TRACE_ALIASES) is None:
            warnings.append(f"project {pid} missing sourceTrace/source_trace linking depth records to canonical record")
        if get_any(project, ("duplicateCheckNotes", "duplicate_check_notes")) is None:
            warnings.append(f"project {pid} missing duplicateCheckNotes/duplicate_check_notes")

        sources = collect_sources(project)
        if not sources:
            warnings.append(f"project {pid} has no project-level sources/evidence")
        for source_index, source in enumerate(sources):
            missing = source_missing_fields(source, project)
            if missing:
                warnings.append(f"project {pid} source {source_index} missing fields: {', '.join(missing)}")
        if is_confirmed_pipeline_record(project):
            for label, aliases, keywords in CRITICAL_PROJECT_FIELDS:
                if field_is_present(project, aliases) and not critical_field_verified(project, label, aliases, keywords):
                    critical_field_gaps.append({"projectId": pid, "projectName": name, "field": label})
                    warnings.append(
                        "project "
                        f"{pid} confirmed critical field {label} lacks chrome-mcp/exa-fetch/manual-file verification"
                    )
            for label, aliases in REPORT_READY_PROJECT_FIELDS:
                if not rich_field_present(project, aliases) and not field_marked_unavailable(project, label, aliases):
                    report_card_field_gaps.append({"projectId": pid, "projectName": name, "field": label})
                    warnings.append(
                        "project "
                        f"{pid} confirmed report-card field {label} is missing from main JSON and not marked unavailable"
                    )
        groups[dedupe_key(project)].append({"id": pid, "name": name, "index": index})

    for key, members in groups.items():
        if key and len(members) > 1:
            duplicate_candidates.append({"dedupeKey": key, "members": members})
            warnings.append(f"duplicate candidate group needs merge/rejection decision: {key}")

    for section_name in ("nationalPlans", "policyFramework", "forecasts"):
        section = data.get(section_name, [])
        if not isinstance(section, list):
            continue
        for index, record in enumerate(section):
            if isinstance(record, dict) and looks_like_policy_target(record) and not has_legal_basis(record):
                warnings.append(f"{section_name}[{index}] has target-like data without legalBasis/decree/order backtrace")

    metadata = data.get("metadata", {})
    if isinstance(metadata, dict):
        source_to_final = metadata.get("sourceToFinal") or metadata.get("source_to_final")
        if not isinstance(source_to_final, dict):
            warnings.append("metadata missing sourceToFinal/source_to_final handoff state")
        else:
            for field in ("pipelineLedger", "pipelineLedgerUpdatedAt", "summaryBackpropagationAt", "finalClaimsCheckedAgainstLedger"):
                if source_to_final.get(field) in (None, "", []):
                    warnings.append(f"metadata.sourceToFinal missing {field}")

    if depth_dir is not None:
        depth_propagation_gaps, depth_warnings, unmatched_depth_rich_records = validate_depth_propagation(projects, depth_dir)
        warnings.extend(depth_warnings)
        for gap in depth_propagation_gaps:
            warnings.append(
                "depth rich field was not propagated to main JSON: "
                f"{gap['projectId']} {gap['field']} from {gap['depthFile']}"
            )
        for record in unmatched_depth_rich_records:
            warnings.append(
                "depth rich record could not be matched to a main JSON project: "
                f"{record['depthFile']} {record['location']} fields={','.join(record['fields'])}"
            )

    status = (
        "pass"
        if not errors
        and not duplicate_candidates
        and not critical_field_gaps
        and not report_card_field_gaps
        and not depth_propagation_gaps
        else "needs-review"
    )
    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "duplicateCandidates": duplicate_candidates,
        "criticalFieldGaps": critical_field_gaps,
        "reportCardFieldGaps": report_card_field_gaps,
        "depthPropagationGaps": depth_propagation_gaps,
        "unmatchedDepthRichRecords": unmatched_depth_rich_records,
        "counts": {
            "projects": len(projects),
            "warnings": len(warnings),
            "errors": len(errors),
            "duplicateCandidateGroups": len(duplicate_candidates),
            "criticalFieldGaps": len(critical_field_gaps),
            "reportCardFieldGaps": len(report_card_field_gaps),
            "depthPropagationGaps": len(depth_propagation_gaps),
            "unmatchedDepthRichRecords": len(unmatched_depth_rich_records),
        },
    }


def validate_project_ledger_gate(result: dict[str, Any], ledger: Any) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    projects = collect_v4_ledger_projects(ledger)
    if not projects:
        gap = {"gate": "project_ledger_schema_gate", "issue": "project ledger has no projects array"}
        add_gate_gap(result, "projectLedgerFieldGaps", gap, "project ledger has no projects array")
        return gaps
    for index, project in enumerate(projects):
        pid = str(project.get("projectId") or project.get("canonicalProjectId") or project.get("id") or f"index-{index}")
        for field in V4_LEDGER_REQUIRED_FIELDS:
            if field not in project or not present_or_unknown(project.get(field)):
                gap = {"projectId": pid, "field": field}
                gaps.append(gap)
                add_gate_gap(
                    result,
                    "projectLedgerFieldGaps",
                    gap,
                    f"project ledger {pid} missing required V4 field {field}",
                )
    return gaps


def validate_project_card_completeness_gate(result: dict[str, Any], cards_data: Any) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    cards = collect_v4_project_cards(cards_data)
    if not cards:
        gap = {"gate": "project_card_completeness_gate", "issue": "project cards file has no cards array"}
        add_gate_gap(result, "projectCardCompletenessGaps", gap, "project cards file has no cards array")
        return gaps
    for index, card in enumerate(cards):
        pid = str(card.get("projectId") or card.get("id") or f"index-{index}")
        for path in V4_PROJECT_CARD_REQUIRED_PATHS:
            if not present_or_unknown(nested_get(card, path)):
                gap = {"projectId": pid, "fieldPath": path}
                gaps.append(gap)
                add_gate_gap(
                    result,
                    "projectCardCompletenessGaps",
                    gap,
                    f"project card {pid} missing required V4 field {path}",
                )
    return gaps


def ledger_capacity_reconciliation(ledger: Any) -> dict[str, float]:
    projects = collect_v4_ledger_projects(ledger)
    confirmed = 0.0
    opportunity = 0.0
    watchlist = 0.0
    for project in projects:
        capacity = as_number(project.get("capacityMW") or project.get("capacity_mw"))
        opportunity_mw = as_number(project.get("opportunityMW") or project.get("opportunity_mw"))
        stage = normalize_stage(project.get("projectStage") or project.get("pipelineBucket") or project.get("status"))
        if project.get("countedInConfirmedCapacity") is True:
            confirmed += capacity
        if project.get("countedInOpportunityCapacity") is True:
            opportunity += opportunity_mw
        if "watchlist" in stage:
            watchlist += capacity
    return {
        "computedConfirmedCapacityMW": confirmed,
        "computedOpportunityCapacityMW": opportunity,
        "computedWatchlistCapacityMW": watchlist,
    }


def validate_capacity_reconciliation_gate(result: dict[str, Any], ledger: Any, tolerance: float = 0.1) -> dict[str, float]:
    computed = ledger_capacity_reconciliation(ledger)
    declared = ledger.get("capacityReconciliation") if isinstance(ledger, dict) else None
    if not isinstance(declared, dict):
        add_gate_gap(
            result,
            "capacityReconciliationGaps",
            {"issue": "ledger missing capacityReconciliation object", **computed},
            "ledger missing capacityReconciliation object",
        )
        return computed
    expected_fields = [
        ("confirmedCapacityMW", "computedConfirmedCapacityMW"),
        ("opportunityCapacityMW", "computedOpportunityCapacityMW"),
        ("watchlistCapacityMW", "computedWatchlistCapacityMW"),
    ]
    for declared_field, computed_field in expected_fields:
        if declared_field not in declared:
            add_gate_gap(
                result,
                "capacityReconciliationGaps",
                {"field": declared_field, "issue": "missing", "computed": computed[computed_field]},
                f"capacity reconciliation missing {declared_field}",
            )
            continue
        declared_value = as_number(declared.get(declared_field))
        if abs(declared_value - computed[computed_field]) > tolerance:
            add_gate_gap(
                result,
                "capacityReconciliationGaps",
                {
                    "field": declared_field,
                    "declared": declared_value,
                    "computed": computed[computed_field],
                },
                f"capacity reconciliation mismatch for {declared_field}: declared {declared_value}, computed {computed[computed_field]}",
            )
    result["computedCapacityReconciliation"] = computed
    return computed


def validate_evidence_boundary_gate(result: dict[str, Any], evidence_table: Any) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    items = collect_v4_evidence_items(evidence_table)
    if not items:
        gap = {"gate": "evidence_boundary_gate", "issue": "evidence table has no conclusion evidence items"}
        add_gate_gap(result, "evidenceBoundaryGaps", gap, "evidence table has no conclusion evidence items")
        return gaps
    related_fields = {normalize_text(item.get("relatedField") or item.get("related_field")) for item in items}
    related_fields.update(normalize_text(item.get("conclusionType") or item.get("conclusion_type")) for item in items)
    for field in V4_EVIDENCE_REQUIRED_FIELDS:
        key = normalize_text(field)
        if not any(key in related or related in key for related in related_fields if related):
            gap = {"relatedField": field}
            gaps.append(gap)
            add_gate_gap(
                result,
                "evidenceBoundaryGaps",
                gap,
                f"evidence table missing conclusion-level evidence for {field}",
            )
    for index, item in enumerate(items):
        for required in (
            "conclusion",
            "conclusionType",
            "source",
            "sourceGrade",
            "directlyProves",
            "confidence",
            "relatedField",
            "pendingVerificationAction",
        ):
            if required not in item or not present_or_unknown(item.get(required)):
                gap = {"itemIndex": index, "field": required}
                gaps.append(gap)
                add_gate_gap(
                    result,
                    "evidenceBoundaryGaps",
                    gap,
                    f"evidence table item {index} missing {required}",
                )
    return gaps


def validate_no_strategy_recommendation_gate(result: dict[str, Any], report_text: str) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    lowered = report_text.lower()
    for pattern in NO_STRATEGY_PATTERNS:
        if pattern.lower() in lowered:
            gap = {"pattern": pattern}
            gaps.append(gap)
            add_gate_gap(
                result,
                "strategyRecommendationGaps",
                gap,
                f"full report contains strategy/recommendation phrase blocked by V4: {pattern}",
            )
    return gaps


def collect_candidate_records(candidate_pool: Any) -> list[dict[str, Any]]:
    if isinstance(candidate_pool, list):
        return [item for item in candidate_pool if isinstance(item, dict)]
    if isinstance(candidate_pool, dict):
        for key in ("candidates", "projects", "items", "candidateProjectPool", "candidate_project_pool"):
            value = candidate_pool.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def candidate_names(record: dict[str, Any]) -> list[str]:
    names = []
    for key in ("projectName", "project_name", "name", "canonicalProjectName", "canonicalName", "project"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            names.append(value)
    for key in ("aliases", "projectAliases", "project_aliases", "nameVariants", "name_variants"):
        names.extend(collect_name_values(record.get(key)))
    return names


def ledger_outcome_names(ledger: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(ledger, dict):
        containers = [ledger.get("projects")]
        containers.extend(
            ledger.get(key)
            for key in (
                "watchlist",
                "duplicate",
                "duplicates",
                "duplicateCandidates",
                "rejected",
                "rejectedClaims",
                "unresolved",
            )
        )
    else:
        containers = [ledger]
    for container in containers:
        for item in as_list(container):
            if isinstance(item, dict):
                for name in candidate_names(item):
                    key = normalize_text(name)
                    if key:
                        names.add(key)
                for field in ("projectId", "canonicalProjectId", "id", "aliasGroupId"):
                    value = item.get(field)
                    if value:
                        names.add(normalize_text(value))
    return names


def validate_baseline_inheritance_gate(result: dict[str, Any], candidate_pool: Any, ledger: Any) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    candidates = collect_candidate_records(candidate_pool)
    if not candidates:
        append_warning(result, "candidate pool is empty or missing; baseline_inheritance_gate could not verify recall retention")
        return gaps
    outcome_names = ledger_outcome_names(ledger)
    for index, candidate in enumerate(candidates):
        names = [normalize_text(name) for name in candidate_names(candidate)]
        names = [name for name in names if name]
        if not names:
            continue
        if not any(name in outcome_names for name in names):
            gap = {"candidateIndex": index, "candidateNames": candidate_names(candidate)}
            gaps.append(gap)
            add_gate_gap(
                result,
                "baselineInheritanceGaps",
                gap,
                f"candidate pool record {index} did not flow into confirmed/watchlist/duplicate/rejected/unresolved ledger outcomes",
            )
    return gaps


def update_v4_gate_status(result: dict[str, Any]) -> None:
    gate_keys = [
        "projectLedgerFieldGaps",
        "projectCardCompletenessGaps",
        "capacityReconciliationGaps",
        "evidenceBoundaryGaps",
        "strategyRecommendationGaps",
        "baselineInheritanceGaps",
    ]
    result["v4GateSummary"] = {key: len(result.get(key, [])) for key in gate_keys}
    if any(result["v4GateSummary"].values()):
        result["status"] = "needs-review"
    result.setdefault("counts", {}).update(result["v4GateSummary"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate renewable market source-to-final integrity.")
    parser.add_argument("market_json", type=Path)
    parser.add_argument("--depth-dir", type=Path, help="Depth JSON directory used to verify rich-field propagation.")
    parser.add_argument("--project-ledger", type=Path, help="V4 project_ledger.json or {slug}-pipeline-ledger.json.")
    parser.add_argument("--project-cards", type=Path, help="V4 project_cards.json with full project-card modules.")
    parser.add_argument("--evidence-table", type=Path, help="V4 evidence_table.json with conclusion-level evidence.")
    parser.add_argument("--candidate-pool", type=Path, help="candidate_project_pool.json for baseline inheritance checks.")
    parser.add_argument("--full-report", type=Path, help="Full report Markdown/HTML text for no-strategy recommendation checks.")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on warnings as well as errors.")
    args = parser.parse_args()

    data = json.loads(args.market_json.read_text(encoding="utf-8-sig"))
    result = validate_market(data, args.depth_dir)

    ledger_data: Any | None = None
    if args.project_ledger:
        ledger_data = read_json_file(args.project_ledger)
        validate_project_ledger_gate(result, ledger_data)
        validate_capacity_reconciliation_gate(result, ledger_data)
    if args.project_cards:
        validate_project_card_completeness_gate(result, read_json_file(args.project_cards))
    if args.evidence_table:
        validate_evidence_boundary_gate(result, read_json_file(args.evidence_table))
    if args.full_report:
        validate_no_strategy_recommendation_gate(result, args.full_report.read_text(encoding="utf-8-sig"))
    if args.candidate_pool:
        if ledger_data is None:
            append_warning(result, "candidate pool was provided without --project-ledger; baseline_inheritance_gate skipped")
        else:
            validate_baseline_inheritance_gate(result, read_json_file(args.candidate_pool), ledger_data)
    update_v4_gate_status(result)

    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")

    if (
        result["errors"]
        or result["duplicateCandidates"]
        or result["criticalFieldGaps"]
        or result["reportCardFieldGaps"]
        or result["depthPropagationGaps"]
        or result.get("projectLedgerFieldGaps")
        or result.get("projectCardCompletenessGaps")
        or result.get("capacityReconciliationGaps")
        or result.get("evidenceBoundaryGaps")
        or result.get("strategyRecommendationGaps")
        or result.get("baselineInheritanceGaps")
        or (args.strict and result["warnings"])
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
