#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

MANIFEST_PATH = "zigux/tests/phase10_closure_manifest.json"
FREEZE_BOUNDARY_COMMAND = "python3 scripts/zigux/check-phase10-shared-freeze-boundary.py"
VALIDATION_COMMANDS = [
    FREEZE_BOUNDARY_COMMAND,
    "python3 scripts/zigux/validate-phase10.py",
    "python3 scripts/zigux/validate-phase10-closure.py",
]


def load_manifest(root: Path) -> tuple[dict[str, object] | None, list[str]]:
    path = root / MANIFEST_PATH
    if not path.exists():
        return None, [f"missing:{MANIFEST_PATH}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json:{MANIFEST_PATH}:{exc.lineno}:{exc.colno}"]
    if not isinstance(data, dict):
        return None, [f"invalid_manifest_root:{type(data).__name__}"]
    return data, []


def validate(root: Path) -> list[str]:
    manifest, issues = load_manifest(root)
    if issues or manifest is None:
        return issues

    exact_checks = manifest.get("exact_checks")
    if not isinstance(exact_checks, list):
        return ["closure_manifest:exact_checks:not_list"]

    missing: list[str] = []
    for command in VALIDATION_COMMANDS:
        if command not in exact_checks:
            missing.append(f"closure_manifest:exact_checks:missing:{command}")

    if manifest.get("freeze_boundary_status") != "aligned":
        missing.append(
            "closure_manifest:freeze_boundary_status="
            + repr(manifest.get("freeze_boundary_status"))
        )
    if manifest.get("freeze_status_change_claimed") is not False:
        missing.append(
            "closure_manifest:freeze_status_change_claimed="
            + repr(manifest.get("freeze_status_change_claimed"))
        )

    return missing


def write_manifest(root: Path, *, exact_checks: object, status: str = "aligned", claimed: object = False) -> None:
    path = root / MANIFEST_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "freeze_boundary_status": status,
                "freeze_status_change_claimed": claimed,
                "exact_checks": exact_checks,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def expect_issue(root: Path, expected: str) -> None:
    issues = validate(root)
    if expected not in issues:
        actual = ",".join(issues) if issues else "none"
        raise SystemExit(f"phase10-freeze-boundary-route-self-test:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_freeze_boundary_route_") as tmp_dir:
        root = Path(tmp_dir)
        write_manifest(root, exact_checks=VALIDATION_COMMANDS)
        baseline = validate(root)
        if baseline:
            raise SystemExit(
                "phase10-freeze-boundary-route-self-test:baseline_failed:"
                + ",".join(baseline)
            )

        write_manifest(root, exact_checks=VALIDATION_COMMANDS[1:])
        expect_issue(root, f"closure_manifest:exact_checks:missing:{FREEZE_BOUNDARY_COMMAND}")

        write_manifest(root, exact_checks="not-a-list")
        expect_issue(root, "closure_manifest:exact_checks:not_list")

        write_manifest(root, exact_checks=VALIDATION_COMMANDS, status="drifted")
        expect_issue(root, "closure_manifest:freeze_boundary_status='drifted'")

        write_manifest(root, exact_checks=VALIDATION_COMMANDS, claimed=True)
        expect_issue(root, "closure_manifest:freeze_status_change_claimed=True")

    print("PHASE10_FREEZE_BOUNDARY_ROUTE_SELF_TEST=pass")
    print("PHASE10_FREEZE_BOUNDARY_ROUTE_SELF_TEST_CASE_COUNT=4")
    return 0


if "--self-test" in sys.argv[1:]:
    sys.exit(run_self_test())

issues = validate(ROOT)
if issues:
    print("PHASE10_FREEZE_BOUNDARY_ROUTE=fail")
    print("PHASE10_FREEZE_BOUNDARY_ROUTE_ISSUES_START")
    for issue in issues:
        print(issue)
    print("PHASE10_FREEZE_BOUNDARY_ROUTE_ISSUES_END")
    sys.exit(1)

print("PHASE10_FREEZE_BOUNDARY_ROUTE=pass")
print(f"PHASE10_FREEZE_BOUNDARY_ROUTE_REQUIRED_COMMAND_COUNT={len(VALIDATION_COMMANDS)}")
