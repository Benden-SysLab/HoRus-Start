#!/usr/bin/env python3
"""Validate local reports produced by the active bootstrap pipeline."""

import json
import sys
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent
    reports = root / "runtime" / "reports"
    stage0 = reports / "stage0.json"
    if stage0.exists():
        schema = json.loads((root / "schemas" / "runtime" / "stage0.schema.json").read_text(encoding="utf-8"))
        report = json.loads(stage0.read_text(encoding="utf-8"))
        missing = set(schema["required"]) - set(report)
        if missing:
            raise ValueError(f"stage0.json: missing fields {sorted(missing)}")
        if report["api_version"] != "v1" or report["schema_version"] != "1.0":
            raise ValueError("stage0.json: unsupported report version")
        if report["status"] not in ("READY", "WAITING_USER_INPUT", "FAILED"):
            raise ValueError("stage0.json: invalid status")
        if report["checks"].get("ssh_identity") not in ("PASS", "FAIL"):
            raise ValueError("stage0.json: invalid SSH identity check")
        print("[PASS] stage0.json")
    else:
        print("[SKIP] stage0.json has not been generated")

    for stage in (1, 2):
        path = reports / f"stage{stage}.json"
        if not path.exists():
            print(f"[SKIP] {path.name} has not been generated")
            continue
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("status") != "COMPLETED" or not isinstance(report.get("nodes"), dict):
            raise ValueError(f"{path.name}: expected COMPLETED status and nodes object")
        print(f"[PASS] {path.name}: {len(report['nodes'])} nodes")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        sys.exit(1)
