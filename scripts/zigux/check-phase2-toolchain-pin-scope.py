#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import tempfile


ROOT = Path(__file__).resolve().parents[2]

POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
README = ROOT / "scripts" / "zigux" / "README.md"
CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
PHASE2_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2.py"

EXPECTED_PIN_TARGETS = [
    "x86_64-linux",
]

ARCHIVE_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

EXACT_WORKFLOW_RUN_COUNTS = {
    "python3 scripts/zigux/install-zig.py --dest .zig-toolchain": 2,
    "python3 scripts/zigux/check-zig-toolchain.py": 2,
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
}

WORKFLOW_FORBIDDEN_FRAGMENTS = [
    "scripts/zigux/install-zig.py --system",
    "scripts/zigux/install-zig.py --arch",
    "scripts/zigux/check-zig-toolchain.py --system",
    "scripts/zigux/check-zig-toolchain.py --arch",
]

README_MARKERS = [
    "check-phase2-toolchain-pin-scope.py --self-test",
    "check-phase2-toolchain-pin-scope.py",
    "x86_64-linux bootstrap host target",
    "cross-target compile matrix stays a separate Phase 2 surface",
]

CLOSURE_MARKERS = [
    "PHASE2_TOOLCHAIN_PIN_TARGET_COUNT=1",
    "PHASE2_TOOLCHAIN_PIN_TARGETS=x86_64-linux",
    "PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "PHASE2_TOOLCHAIN_PIN_SCOPE_GATE=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "PHASE2_TOOLCHAIN_PIN_SCOPE_POLICY=current archive sha pin stays limited to the bootstrap host target until another bootstrap runner target is explicitly wired",
]

PHASE2_VALIDATOR_MARKERS = [
    "TOOLCHAIN_PIN_SCOPE_CHECKER = ROOT / \"scripts\" / \"zigux\" / \"check-phase2-toolchain-pin-scope.py\"",
    "\"PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass\"",
    "\"PHASE2_TOOLCHAIN_PIN_SCOPE=pass\"",
    "str(TOOLCHAIN_PIN_SCOPE_CHECKER)",
]


def load_json_object(path: Path, *, label: str) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"{label}:expected_object")
    return payload


def validate_policy(payload: dict[str, object]) -> list[str]:
    issues: list[str] = []
    if payload.get("phase") != "Phase 2":
        issues.append(f"policy:phase={payload.get('phase')!r}:expected='Phase 2'")

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append("policy:archive_sha256:expected_object")
        return issues

    keys = list(archive_sha256.keys())
    if keys != EXPECTED_PIN_TARGETS:
        issues.append(f"policy:archive_sha256_keys={keys!r}:expected={EXPECTED_PIN_TARGETS!r}")

    for target_key, digest in archive_sha256.items():
        if not isinstance(digest, str) or not ARCHIVE_SHA256_RE.fullmatch(digest.lower()):
            issues.append(f"policy:archive_sha256:{target_key}:expected_sha256_hex")
    return issues


def validate_required_markers(text: str, *, label: str, markers: list[str]) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        if marker not in text:
            issues.append(f"{label}:missing_marker:{marker}")
    return issues


def validate_exact_workflow_runs(text: str) -> list[str]:
    issues: list[str] = []
    lines = [line.strip() for line in text.splitlines()]
    for command, expected_count in EXACT_WORKFLOW_RUN_COUNTS.items():
        expected_line = f"run: {command}"
        count = sum(1 for line in lines if line == expected_line)
        if count != expected_count:
            issues.append(f"workflow_exact_run:{command}:count={count}:expected={expected_count}")
    for fragment in WORKFLOW_FORBIDDEN_FRAGMENTS:
        if fragment in text:
            issues.append(f"workflow_forbidden_fragment:{fragment}")
    return issues


def run_self_test() -> int:
    valid_policy = {
        "phase": "Phase 2",
        "archive_sha256": {
            "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
        },
    }
    if validate_policy(valid_policy):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:valid_policy")

    bad_phase = dict(valid_policy)
    bad_phase["phase"] = "Phase 3"
    issues = validate_policy(bad_phase)
    if "policy:phase='Phase 3':expected='Phase 2'" not in issues:
        raise SystemExit("phase2-toolchain-pin-scope:self-test:phase_mismatch")

    bad_keys = {
        "phase": "Phase 2",
        "archive_sha256": {
            "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
            "aarch64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
        },
    }
    issues = validate_policy(bad_keys)
    if not any(issue.startswith("policy:archive_sha256_keys=") for issue in issues):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:key_mismatch")

    bad_digest = {
        "phase": "Phase 2",
        "archive_sha256": {
            "x86_64-linux": "not-a-digest",
        },
    }
    issues = validate_policy(bad_digest)
    if "policy:archive_sha256:x86_64-linux:expected_sha256_hex" not in issues:
        raise SystemExit("phase2-toolchain-pin-scope:self-test:digest_shape")

    workflow_text = "\n".join(
        [
            "run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
            "run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
            "run: python3 scripts/zigux/check-zig-toolchain.py",
            "run: python3 scripts/zigux/check-zig-toolchain.py",
            "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
            "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
        ]
    )
    if validate_exact_workflow_runs(workflow_text):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:workflow_counts")

    issues = validate_exact_workflow_runs("run: python3 scripts/zigux/check-zig-toolchain.py --arch x86_64")
    if not any(issue.startswith("workflow_forbidden_fragment:") for issue in issues):
        raise SystemExit("phase2-toolchain-pin-scope:self-test:workflow_forbidden_fragment")

    marker_issues = validate_required_markers(
        "alpha\nbeta\ngamma",
        label="sample",
        markers=["alpha", "gamma"],
    )
    if marker_issues:
        raise SystemExit("phase2-toolchain-pin-scope:self-test:marker_presence")

    marker_issues = validate_required_markers(
        "alpha\nbeta\ngamma",
        label="sample",
        markers=["delta"],
    )
    if marker_issues != ["sample:missing_marker:delta"]:
        raise SystemExit("phase2-toolchain-pin-scope:self-test:marker_failure_shape")

    with tempfile.TemporaryDirectory(prefix="phase2_toolchain_pin_scope_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        manifest_path = tmp_root / "toolchain.json"
        manifest_path.write_text(json.dumps(valid_policy), encoding="utf-8")
        round_trip = load_json_object(manifest_path, label="policy")
        if round_trip["archive_sha256"] != valid_policy["archive_sha256"]:
            raise SystemExit("phase2-toolchain-pin-scope:self-test:json_round_trip")

    print("PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass")
    print("PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST_CASE_COUNT=8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 bootstrap archive pin limited to the current workflow host target until new runner evidence lands."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in pin-scope checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    required_files = [
        POLICY,
        WORKFLOW,
        README,
        CLOSURE_DOC,
        PHASE2_VALIDATOR,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
    if missing:
        print("PHASE2_TOOLCHAIN_PIN_SCOPE=fail")
        print("MISSING_PHASE2_TOOLCHAIN_PIN_SCOPE_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE2_TOOLCHAIN_PIN_SCOPE_FILES_END")
        return 1

    issues: list[str] = []
    issues.extend(validate_policy(load_json_object(POLICY, label="policy")))
    issues.extend(
        validate_required_markers(
            README.read_text(encoding="utf-8"),
            label="scripts_readme",
            markers=README_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            CLOSURE_DOC.read_text(encoding="utf-8"),
            label="phase2_closure_doc",
            markers=CLOSURE_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            PHASE2_VALIDATOR.read_text(encoding="utf-8"),
            label="phase2_validator",
            markers=PHASE2_VALIDATOR_MARKERS,
        )
    )
    issues.extend(validate_exact_workflow_runs(WORKFLOW.read_text(encoding="utf-8")))

    if issues:
        print("PHASE2_TOOLCHAIN_PIN_SCOPE=fail")
        print("INVALID_PHASE2_TOOLCHAIN_PIN_SCOPE_START")
        for item in issues:
            print(item)
        print("INVALID_PHASE2_TOOLCHAIN_PIN_SCOPE_END")
        return 1

    print("PHASE2_TOOLCHAIN_PIN_SCOPE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
