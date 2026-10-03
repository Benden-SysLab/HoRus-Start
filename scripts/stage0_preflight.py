#!/usr/bin/env python3
"""Prepare the external SSH identity used by the HoRus-Start playbooks."""

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path


def ssh_identity():
    key_dir = Path(os.environ.get("HORUS_SSH_KEY_DIR", "~/.ssh/horus/horus-pmx-node")).expanduser()
    key_name = os.environ.get("HORUS_SSH_KEY_NAME", "horus-pmx-cluster")
    private_key = key_dir / key_name
    public_key = key_dir / (key_name + ".pub")
    created = []

    if not private_key.exists() and not public_key.exists():
        key_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        temporary_key = key_dir / (key_name + ".bootstrap-tmp")
        try:
            command = ["ssh-keygen", "-t", "ed25519", "-f", str(temporary_key),
                       "-N", "", "-C", "horus-pmx-cluster@horus"]
            result = subprocess.run(
                subprocess.list2cmdline(command) if os.name == "nt" else command,
                shell=os.name == "nt", capture_output=True, text=True
            )
            if result.returncode != 0 or not temporary_key.is_file():
                raise RuntimeError(result.stderr.strip() or "ssh-keygen failed")
            public = subprocess.run(
                ["ssh-keygen", "-y", "-f", str(temporary_key)],
                check=True, capture_output=True, text=True
            ).stdout.strip()
            if not public:
                raise RuntimeError("ssh-keygen returned an empty public key")
            temporary_key.replace(private_key)
            public_key.write_text(public + "\n", encoding="utf-8")
            if os.name != "nt":
                private_key.chmod(0o600)
                public_key.chmod(0o644)
            created.append(str(private_key))
        finally:
            temporary_key.unlink(missing_ok=True)
            Path(str(temporary_key) + ".pub").unlink(missing_ok=True)

    if not private_key.is_file() or not public_key.is_file() or public_key.stat().st_size == 0:
        raise RuntimeError(f"Incomplete SSH key pair: {private_key} / {public_key}")
    return created


def main():
    repo = Path(__file__).resolve().parent.parent
    report_path = repo / "runtime" / "reports" / "stage0.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    created = []
    errors = []
    try:
        created = ssh_identity()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        errors.append(str(exc))
    report = {
        "api_version": "v1",
        "schema_version": "1.0",
        "producer": "stage0_readiness_gate",
        "resource_type": "report",
        "stage": 0,
        "status": "WAITING_USER_INPUT" if errors else "READY",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "checks": {"ssh_identity": "FAIL" if errors else "PASS"},
        "generated_templates": created,
        "blocking_items": errors,
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"[STAGE 0] {report['status']}: {report_path}")
    for error in errors:
        print(f"[STAGE 0] {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
