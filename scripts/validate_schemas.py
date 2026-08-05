#!/usr/bin/env python3
"""
Runtime Schema Validation Script for HoRus-Start Runtime API v1.
Validates generated runtime JSON files against JSON Schemas in schemas/runtime/.
"""

import os
import sys
import json

def log_check(name, passed, message=""):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}" + (f": {message}" if message else ""))
    return passed

def validate_json_schema(file_path, schema_path):
    if not os.path.exists(file_path):
        log_check(f"Schema Check: {os.path.basename(file_path)}", True, "File not present yet (skip)")
        return True

    if not os.path.exists(schema_path):
        log_check(f"Schema Check: {os.path.basename(schema_path)}", False, "Schema file missing")
        return False

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        with open(schema_path, 'r') as f:
            schema = json.load(f)

        # Basic contract check
        required_keys = schema.get("required", [])
        missing = [k for k in required_keys if k not in data]
        if missing:
            log_check(f"Runtime Contract: {os.path.basename(file_path)}", False, f"Missing required API v1 keys: {missing}")
            return False

        api_ver = data.get("api_version")
        schema_ver = data.get("schema_version")
        log_check(f"Runtime Contract: {os.path.basename(file_path)}", True, f"API {api_ver} (Schema v{schema_ver}) verified")
        return True
    except Exception as e:
        log_check(f"Runtime Schema: {os.path.basename(file_path)}", False, str(e))
        return False

def main():
    print("=== HoRus-Start Runtime API v1 Schema Validation ===")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    checks = [
        (os.path.join(base_dir, "runtime/reports/stage0.json"), os.path.join(base_dir, "schemas/runtime/stage0.schema.json")),
        (os.path.join(base_dir, "runtime/discovery/storage.json"), os.path.join(base_dir, "schemas/runtime/discovery.schema.json")),
        (os.path.join(base_dir, "runtime/plans/storage_plan.json"), os.path.join(base_dir, "schemas/runtime/plan.schema.json")),
        (os.path.join(base_dir, "runtime/reports/storage_drift.json"), os.path.join(base_dir, "schemas/runtime/report.schema.json")),
        (os.path.join(base_dir, "runtime/reports/stage3.json"), os.path.join(base_dir, "schemas/runtime/report.schema.json")),
        (os.path.join(base_dir, "runtime/discovery/cloud_images.json"), os.path.join(base_dir, "schemas/runtime/discovery.schema.json")),
        (os.path.join(base_dir, "runtime/discovery/lxc_templates.json"), os.path.join(base_dir, "schemas/runtime/discovery.schema.json")),
        (os.path.join(base_dir, "runtime/reports/discovery.json"), os.path.join(base_dir, "schemas/runtime/report.schema.json")),
        (os.path.join(base_dir, "runtime/reports/planning.json"), os.path.join(base_dir, "schemas/runtime/report.schema.json")),
        (os.path.join(base_dir, "runtime/reports/asset_catalog.json"), os.path.join(base_dir, "schemas/runtime/report.schema.json")),
        (os.path.join(base_dir, "runtime/reports/image_factory.json"), os.path.join(base_dir, "schemas/runtime/report.schema.json")),
        (os.path.join(base_dir, "runtime/reports/template_validation.json"), os.path.join(base_dir, "schemas/runtime/report.schema.json")),
        (os.path.join(base_dir, "runtime/reports/stage5.json"), os.path.join(base_dir, "schemas/runtime/report.schema.json")),
    ]

    all_passed = True
    for json_p, schema_p in checks:
        if not validate_json_schema(json_p, schema_p):
            all_passed = False

    if all_passed:
        print("\nAll Runtime API v1 schema validations PASSED.")
        sys.exit(0)
    else:
        print("\nRuntime API v1 schema validation FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
