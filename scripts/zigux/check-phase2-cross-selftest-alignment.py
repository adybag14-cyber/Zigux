#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PHASE2_CROSS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
PHASE2_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2.py"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TARGETS_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

EXPECTED_TARGETS = [
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
]

EXACT_WORKFLOW_RUN_COUNTS = {
    "python3 scripts/zigux/check-phase2-cross.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py": 1,
    "python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}": 1,
}

EXACT_MAKEFILE_RUN_COUNTS = {
    "scripts/zigux/check-phase2-cross.py --self-test": 1,
    "scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test": 1,
    "scripts/zigux/check-phase2-cross-selftest-alignment.py": 1,
    "scripts/zigux/check-phase2-cross.py": 1,
}

WORKFLOW_SCOPE_REQUIRED_FRAGMENTS = [
    "scripts/zigux/install-zig\\.py",
    "scripts/zigux/check-phase2-cross\\.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment\\.py",
    "scripts/zigux/zig-toolchain-policy\\.json",
    "scripts/zigux/fixdep\\.zig",
    "zigux/tests/fixtures/phase2_cross_targets\\.json",
]

PHASE2_CROSS_CHECKER_MARKERS = [
    "EXPECTED_TARGETS = [",
    "EXPECTED_ZIG_TEST_FILES = [",
    'print("PHASE2_CROSS_SELF_TEST=pass")',
    'print(f"PHASE2_CROSS_TARGET_COUNT={len(targets)}")',
    'print(f"PHASE2_CROSS_FILE_COUNT={len(zig_test_files)}")',
]

PHASE2_VALIDATOR_MARKERS = [
    'ROOT / "scripts" / "zigux" / "check-phase2-cross.py"',
    'ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"',
    '"zigux/tests/fixtures/phase2_cross_targets.json"',
]

CLOSURE_MARKERS = [
    "shared cross compile self-test: `python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "shared cross compile gate: `python3 scripts/zigux/check-phase2-cross.py`",
    "shared cross-selftest alignment self-test: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`",
    "shared cross-selftest alignment gate: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "make -C zigux phase2-cross",
]

BOOTSTRAP_NOTES_MARKERS = [
    "shared cross selftest-alignment self-test: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`",
    "shared cross selftest-alignment gate: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "the three-target compile matrix in `zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the `x86_64-linux` bootstrap archive pin",
]

SCRIPTS_README_MARKERS = [
    "shared cross compile self-test: `python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "shared cross compile gate: `python3 scripts/zigux/check-phase2-cross.py`",
    "shared cross-selftest alignment self-test: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`",
    "shared cross-selftest alignment gate: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`",
]

TESTS_README_MARKERS = [
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "make -C zigux phase2-cross",
]

REVIEW_CHECKLIST_MARKERS = [
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
]


def load_json_object(path: Path, *, label: str) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"{label}:expected_object")
    return payload


def validate_targets_manifest(payload: dict[str, object]) -> list[str]:
    issues: list[str] = []
    if payload.get("phase") != "Phase 2":
        issues.append(f"targets:phase={payload.get('phase')!r}:expected='Phase 2'")
    if payload.get("status") != "closed":
        issues.append(f"targets:status={payload.get('status')!r}:expected='closed'")
    if payload.get("target_count") != len(EXPECTED_TARGETS):
        issues.append(
            f"targets:target_count={payload.get('target_count')!r}:expected={len(EXPECTED_TARGETS)}"
        )
    targets = payload.get("targets")
    if not isinstance(targets, list):
        issues.append("targets:targets:expected_list")
        return issues
    if targets != EXPECTED_TARGETS:
        issues.append("targets:targets=expected_exact_list")
    return issues


def validate_required_markers(text: str, *, label: str, markers: list[str]) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        if marker not in text:
            issues.append(f"{label}:missing_marker:{marker}")
    return issues


def validate_workflow_scope_fragments(text: str) -> list[str]:
    return validate_required_markers(
        text,
        label="workflow_scope",
        markers=WORKFLOW_SCOPE_REQUIRED_FRAGMENTS,
    )


def validate_exact_workflow_runs(text: str) -> list[str]:
    issues: list[str] = []
    for command, expected_count in EXACT_WORKFLOW_RUN_COUNTS.items():
        expected_line = f"run: {command}"
        count = sum(1 for line in text.splitlines() if line.strip() == expected_line)
        if count != expected_count:
            issues.append(f"workflow_exact_run:{command}:count={count}:expected={expected_count}")
    return issues


def validate_exact_makefile_runs(text: str) -> list[str]:
    issues: list[str] = []
    for command, expected_count in EXACT_MAKEFILE_RUN_COUNTS.items():
        count = sum(1 for line in text.splitlines() if line.strip().endswith(command))
        if count != expected_count:
            issues.append(f"makefile_exact_run:{command}:count={count}:expected={expected_count}")
    return issues


def run_self_test() -> int:
    valid_targets = {
        "phase": "Phase 2",
        "status": "closed",
        "target_count": 3,
        "targets": list(EXPECTED_TARGETS),
    }
    if validate_targets_manifest(valid_targets):
        raise SystemExit("phase2-cross-alignment:self-test:valid_targets_manifest")

    bad_count = dict(valid_targets)
    bad_count["target_count"] = 2
    issues = validate_targets_manifest(bad_count)
    if "targets:target_count=2:expected=3" not in issues:
        raise SystemExit("phase2-cross-alignment:self-test:target_count_mismatch")

    bad_targets = dict(valid_targets)
    bad_targets["targets"] = ["x86_64-linux-musl"]
    issues = validate_targets_manifest(bad_targets)
    if "targets:targets=expected_exact_list" not in issues:
        raise SystemExit("phase2-cross-alignment:self-test:target_list_mismatch")

    workflow_text = "\n".join(
        [
            "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
            "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
            "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
            "run: python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}",
        ]
    )
    if validate_exact_workflow_runs(workflow_text):
        raise SystemExit("phase2-cross-alignment:self-test:workflow_counts")

    bad_workflow = ""
    issues = validate_exact_workflow_runs(bad_workflow)
    if not any(issue.startswith("workflow_exact_run:") for issue in issues):
        raise SystemExit("phase2-cross-alignment:self-test:workflow_count_failure")

    scope_text = "\n".join(WORKFLOW_SCOPE_REQUIRED_FRAGMENTS)
    if validate_workflow_scope_fragments(scope_text):
        raise SystemExit("phase2-cross-alignment:self-test:workflow_scope")

    scope_issues = validate_workflow_scope_fragments("scripts/zigux/install-zig\\.py")
    if "workflow_scope:missing_marker:scripts/zigux/check-phase2-cross\\.py" not in scope_issues:
        raise SystemExit("phase2-cross-alignment:self-test:workflow_scope_failure")
    if "workflow_scope:missing_marker:scripts/zigux/zig-toolchain-policy\\.json" not in scope_issues:
        raise SystemExit("phase2-cross-alignment:self-test:workflow_scope_policy_failure")

    makefile_text = "\n".join(
        [
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
        ]
    )
    if validate_exact_makefile_runs(makefile_text):
        raise SystemExit("phase2-cross-alignment:self-test:makefile_counts")

    marker_issues = validate_required_markers(
        "alpha\nbeta\ngamma",
        label="sample",
        markers=["alpha", "gamma"],
    )
    if marker_issues:
        raise SystemExit("phase2-cross-alignment:self-test:marker_presence")

    marker_issues = validate_required_markers(
        "alpha\nbeta\ngamma",
        label="sample",
        markers=["delta"],
    )
    if marker_issues != ["sample:missing_marker:delta"]:
        raise SystemExit("phase2-cross-alignment:self-test:marker_failure_shape")

    bootstrap_issues = validate_required_markers(
        "\n".join(BOOTSTRAP_NOTES_MARKERS),
        label="phase2_bootstrap_notes",
        markers=BOOTSTRAP_NOTES_MARKERS,
    )
    if bootstrap_issues:
        raise SystemExit("phase2-cross-alignment:self-test:bootstrap_marker_presence")

    bootstrap_missing = validate_required_markers(
        "\n".join(BOOTSTRAP_NOTES_MARKERS[1:]),
        label="phase2_bootstrap_notes",
        markers=BOOTSTRAP_NOTES_MARKERS,
    )
    expected_bootstrap_issue = (
        "phase2_bootstrap_notes:missing_marker:"
        "shared cross selftest-alignment self-test: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`"
    )
    if bootstrap_missing != [expected_bootstrap_issue]:
        raise SystemExit("phase2-cross-alignment:self-test:bootstrap_marker_failure")

    tests_readme_issues = validate_required_markers(
        "\n".join(TESTS_README_MARKERS),
        label="phase2_tests_readme",
        markers=TESTS_README_MARKERS,
    )
    if tests_readme_issues:
        raise SystemExit("phase2-cross-alignment:self-test:tests_readme_marker_presence")

    tests_readme_missing = validate_required_markers(
        "\n".join(TESTS_README_MARKERS[:-1]),
        label="phase2_tests_readme",
        markers=TESTS_README_MARKERS,
    )
    expected_tests_issue = "phase2_tests_readme:missing_marker:make -C zigux phase2-cross"
    if tests_readme_missing != [expected_tests_issue]:
        raise SystemExit("phase2-cross-alignment:self-test:tests_readme_marker_failure")

    review_checklist_issues = validate_required_markers(
        "\n".join(REVIEW_CHECKLIST_MARKERS),
        label="phase2_review_checklist",
        markers=REVIEW_CHECKLIST_MARKERS,
    )
    if review_checklist_issues:
        raise SystemExit("phase2-cross-alignment:self-test:review_checklist_marker_presence")

    review_checklist_missing = validate_required_markers(
        "\n".join(REVIEW_CHECKLIST_MARKERS[:-1]),
        label="phase2_review_checklist",
        markers=REVIEW_CHECKLIST_MARKERS,
    )
    expected_review_checklist_issue = (
        "phase2_review_checklist:missing_marker:zigux/tests/fixtures/phase2_cross_targets.json"
    )
    if review_checklist_missing != [expected_review_checklist_issue]:
        raise SystemExit("phase2-cross-alignment:self-test:review_checklist_marker_failure")

    closure_missing = validate_required_markers(
        "\n".join(CLOSURE_MARKERS[:2] + CLOSURE_MARKERS[3:]),
        label="phase2_closure_doc",
        markers=CLOSURE_MARKERS,
    )
    expected_closure_issue = (
        "phase2_closure_doc:missing_marker:"
        "shared cross-selftest alignment self-test: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`"
    )
    if closure_missing != [expected_closure_issue]:
        raise SystemExit("phase2-cross-alignment:self-test:closure_marker_failure")

    with tempfile.TemporaryDirectory(prefix="phase2_cross_alignment_selftest_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        manifest_path = tmp_root / "phase2_cross_targets.json"
        manifest_path.write_text(json.dumps(valid_targets), encoding="utf-8")
        round_trip = load_json_object(manifest_path, label="targets")
        if round_trip["targets"] != EXPECTED_TARGETS:
            raise SystemExit("phase2-cross-alignment:self-test:json_round_trip")

    print("PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass")
    print("PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT=16")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 cross-target checker aligned with the shared validator and published closure packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in alignment checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    required_files = [
        PHASE2_CROSS_CHECKER,
        PHASE2_VALIDATOR,
        WORKFLOW,
        MAKEFILE,
        CLOSURE_DOC,
        BOOTSTRAP_NOTES,
        SCRIPTS_README,
        TESTS_README,
        REVIEW_CHECKLIST,
        TARGETS_MANIFEST,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
    if missing:
        print("PHASE2_CROSS_ALIGNMENT=fail")
        print("MISSING_PHASE2_CROSS_ALIGNMENT_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE2_CROSS_ALIGNMENT_FILES_END")
        return 1

    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    issues: list[str] = []
    issues.extend(
        validate_targets_manifest(load_json_object(TARGETS_MANIFEST, label="targets"))
    )
    issues.extend(
        validate_required_markers(
            PHASE2_CROSS_CHECKER.read_text(encoding="utf-8"),
            label="phase2_cross_checker",
            markers=PHASE2_CROSS_CHECKER_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            PHASE2_VALIDATOR.read_text(encoding="utf-8"),
            label="phase2_validator",
            markers=PHASE2_VALIDATOR_MARKERS,
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
            BOOTSTRAP_NOTES.read_text(encoding="utf-8"),
            label="phase2_bootstrap_notes",
            markers=BOOTSTRAP_NOTES_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            SCRIPTS_README.read_text(encoding="utf-8"),
            label="phase2_scripts_readme",
            markers=SCRIPTS_README_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            TESTS_README.read_text(encoding="utf-8"),
            label="phase2_tests_readme",
            markers=TESTS_README_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            REVIEW_CHECKLIST.read_text(encoding="utf-8"),
            label="phase2_review_checklist",
            markers=REVIEW_CHECKLIST_MARKERS,
        )
    )
    issues.extend(validate_exact_workflow_runs(workflow_text))
    issues.extend(validate_workflow_scope_fragments(workflow_text))
    issues.extend(validate_exact_makefile_runs(MAKEFILE.read_text(encoding="utf-8")))

    if issues:
        print("PHASE2_CROSS_ALIGNMENT=fail")
        print("INVALID_PHASE2_CROSS_ALIGNMENT_START")
        for item in issues:
            print(item)
        print("INVALID_PHASE2_CROSS_ALIGNMENT_END")
        return 1

    print("PHASE2_CROSS_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
