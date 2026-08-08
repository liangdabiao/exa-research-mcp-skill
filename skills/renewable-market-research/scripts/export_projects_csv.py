#!/usr/bin/env python3
"""Export renewable market project rows from main JSON to CSV."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

COLUMNS = [
    "id",
    "name",
    "capacityMW",
    "status",
    "developer",
    "developerCountry",
    "location",
    "cod",
    "investmentUSD",
    "turbineModel",
    "turbineCount",
    "annualGenerationGWh",
    "annualCO2ReductionTonnes",
    "ppaDuration",
    "storageMWh",
    "epc",
]


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: export_projects_csv.py <market.json> <projects.csv>", file=sys.stderr)
        return 2

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    data = json.loads(input_path.read_text(encoding="utf-8"))
    projects = data.get("projects", [])
    if not isinstance(projects, list):
        raise TypeError("Expected top-level 'projects' to be a list")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for project in projects:
            if not isinstance(project, dict):
                continue
            writer.writerow({column: project.get(column, "") for column in COLUMNS})

    print(f"Exported {len(projects)} projects to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
