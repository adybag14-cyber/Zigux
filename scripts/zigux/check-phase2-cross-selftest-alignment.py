#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
PHASE2_CROSS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
PHASE2_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2.py"
PHASE2_CLOSURE_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2-closure.py"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
README = ROOT / "scripts" / "zigux" / "README.md"
CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
TOOLCHAIN_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
TARGETS_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

EXPECTED_TARGETS = [
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
]

EXACT_WORKFLOW_RUN_COUNTS = {
    "python3 scripts/zigux/check-phase2-cross.py --self-test": 2,
    "python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}": 1,
}

EXACT_MAKEFILE_RUN_COUNTS = {
    "scripts/zigux/check-phase2-cross.py --self-test": 1,
    "scripts/zigux/check-phase2-cross.py": 1,
}

PHASE2_CROSS_CHECKER_MARKERS = [
    "parser.add_argument('--self-test'",
    "print('PHASE2_CROSS_SELF_TEST=pass')",
    "print('PHASE2_CROSS_SELF_TEST_CASE_COUNT=9')",
    "phase2-cross:tool_manifest_path_missing:",
    "phase2-cross:self-test:explicit_target_failure:",
    "phase2-cross:duplicate_tool:",
    "phase2-cross:duplicate_target:",
    "phase2-cross:duplicate_manifest_target:",
]

PHASE2_VALIDATOR_MARKERS = [
    "PHASE2_CROSS_ALIGNMENT_CHECKER",
    "PHASE2_CROSS_ALIGNMENT_REQUIRED_SOURCE_MARKERS",
    '"PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT=18"',
    '"workflow_matrix_targets=expected_exact_list"',
    "phase2_cross_alignment_checker",
    "str(PHASE2_CROSS_ALIGNMENT_CHECKER)",
]

PHASE2_CLOSURE_VALIDATOR_MARKERS = [
    "CHECK_PHASE2_CROSS_SELFTEST_ALIGNMENT = ROOT / 'scripts' / 'zigux' / 'check-phase2-cross-selftest-alignment.py'",
    "'PHASE2_CROSS_ALIGNMENT_SELF_TEST=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test'",
    "'PHASE2_CROSS_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py'",
    "'print(\"PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT=18\")'",
    "'workflow_matrix_targets=expected_exact_list'",
]

README_MARKERS = [
    "- `check-phase2-cross-selftest-alignment.py`",
    "check-phase2-cross.py --self-test",
    "check-phase2-cross.py",
    "duplicate tool entries",
    "duplicate manifest targets",
    "unexpected explicit targets",
]

TOOLCHAIN_NOTES_MARKERS = [
    "phase2_cross_targets.json",
    "separate from the `x86_64-linux` bootstrap archive pin",
]

CLOSURE_MARKERS = [
    "PHASE2_CROSS_TARGET_COUNT=3",
    "PHASE2_CROSS_SELF_TEST=python3 scripts/zigux/check-phase2-cross.py --self-test",
    "PHASE2_CROSS_GATE=python3 scripts/zigux/check-phase2-cross.py",
    "PHASE2_CROSS_MANIFEST_POLICY=check-phase2-cross.py rejects duplicate tool entries, duplicate requested targets, unexpected explicit targets, duplicate manifest targets, and manifest-count drift before live compile replay",
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


def extract_workflow_matrix_targets(text: str) -> list[str]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != "zig_target:":
            continue
        base_indent = len(line) - len(line.lstrip())
        targets: list[str] = []
        for follow in lines[index + 1:]:
            stripped = follow.strip()
            if not stripped:
                continue
            indent = len(follow) - len(follow.lstrip())
            if indent <= base_indent:
                break
            if stripped.startswith("- "):
                targets.append(stripped[2:].strip())
                continue
            break
        return targets
    return []


def validate_exact_workflow_runs(text: str) -> list[str]:
    issues: list[str] = []
    for command, expected_count in EXACT_WORKFLOW_RUN_COUNTS.items():
        expected_line = f"run: {command}"
        count = sum(1 for line in text.splitlines() if line.strip() == expected_line)
        if count != expected_count:
            issues.append(f"workflow_exact_run:{command}:count={count}:expected={expected_count}")
    workflow_matrix_targets = extract_workflow_matrix_targets(text)
    if workflow_matrix_targets != EXPECTED_TARGETS:
        issues.append("workflow_matrix_targets=expected_exact_list")
    return issues


def validate_exact_makefile_runs(text: str) -> list[str]:
    issues: list[str] = []
    stripped_lines = [line.strip() for line in text.splitlines()]
    for command, expected_count in EXACT_MAKEFILE_RUN_COUNTS.items():
        count = sum(1 for line in stripped_lines if line.endswith(command))
        if count != expected_count:
            issues.append(f"makefile_exact_run:{command}:count={count}:expected={expected_count}")
    return issues


def expect_exact_issue(label: str, issues: list[str], expected_issue: str) -> None:
    if issues != [expected_issue]:
        raise SystemExit(
            f"phase2-cross-alignment:self-test:{label}:expected={expected_issue!r}:actual={issues!r}"
        )


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
            "strategy:",
            "  matrix:",
            "    zig_target:",
            "      - x86_64-linux-musl",
            "      - aarch64-linux-musl",
            "      - riscv64-linux-musl",
            "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
            "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
            "run: python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}",
        ]
    )
    if validate_exact_workflow_runs(workflow_text):
        raise SystemExit("phase2-cross-alignment:self-test:workflow_counts")
    if extract_workflow_matrix_targets(workflow_text) != EXPECTED_TARGETS:
        raise SystemExit("phase2-cross-alignment:self-test:workflow_matrix_targets")

    bad_workflow = "\n".join(
        [
            "strategy:",
            "  matrix:",
            "    zig_target:",
            "      - x86_64-linux-musl",
            "      - aarch64-linux-musl",
            "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
            "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
            "run: python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}",
        ]
    )
    expect_exact_issue(
        "workflow_matrix_targets_failure",
        validate_exact_workflow_runs(bad_workflow),
        "workflow_matrix_targets=expected_exact_list",
    )

    bad_workflow_missing_matrix_run = "\n".join(
        [
            "strategy:",
            "  matrix:",
            "    zig_target:",
            "      - x86_64-linux-musl",
            "      - aarch64-linux-musl",
            "      - riscv64-linux-musl",
            "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
            "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
        ]
    )
    expect_exact_issue(
        "workflow_matrix_run_failure",
        validate_exact_workflow_runs(bad_workflow_missing_matrix_run),
        "workflow_exact_run:python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}:count=0:expected=1",
    )

    makefile_text = "\n".join(
        [
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
        ]
    )
    if validate_exact_makefile_runs(makefile_text):
        raise SystemExit("phase2-cross-alignment:self-test:makefile_counts")

    bad_makefile_missing_route = "\n".join(
        [
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test",
        ]
    )
    expect_exact_issue(
        "makefile_gate_missing_failure",
        validate_exact_makefile_runs(bad_makefile_missing_route),
        "makefile_exact_run:scripts/zigux/check-phase2-cross.py:count=0:expected=1",
    )

    bad_makefile_duplicate_route = "\n".join(
        [
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
        ]
    )
    expect_exact_issue(
        "makefile_gate_duplicate_failure",
        validate_exact_makefile_runs(bad_makefile_duplicate_route),
        "makefile_exact_run:scripts/zigux/check-phase2-cross.py:count=2:expected=1",
    )

    checker_text = "\n".join(PHASE2_CROSS_CHECKER_MARKERS)
    if validate_required_markers(
        checker_text,
        label="phase2_cross_checker",
        markers=PHASE2_CROSS_CHECKER_MARKERS,
    ):
        raise SystemExit("phase2-cross-alignment:self-test:checker_markers")
    expect_exact_issue(
        "checker_marker_failure",
        validate_required_markers(
            checker_text.replace(PHASE2_CROSS_CHECKER_MARKERS[0] + "\n", "", 1),
            label="phase2_cross_checker",
            markers=PHASE2_CROSS_CHECKER_MARKERS,
        ),
        f"phase2_cross_checker:missing_marker:{PHASE2_CROSS_CHECKER_MARKERS[0]}",
    )

    validator_text = "\n".join(PHASE2_VALIDATOR_MARKERS)
    expect_exact_issue(
        "validator_marker_failure",
        validate_required_markers(
            validator_text.replace(PHASE2_VALIDATOR_MARKERS[1], "", 1),
            label="phase2_validator",
            markers=PHASE2_VALIDATOR_MARKERS,
        ),
        f"phase2_validator:missing_marker:{PHASE2_VALIDATOR_MARKERS[1]}",
    )

    closure_validator_text = "\n".join(PHASE2_CLOSURE_VALIDATOR_MARKERS)
    expect_exact_issue(
        "closure_validator_marker_failure",
        validate_required_markers(
            closure_validator_text.replace(PHASE2_CLOSURE_VALIDATOR_MARKERS[0], "", 1),
            label="phase2_closure_validator",
            markers=PHASE2_CLOSURE_VALIDATOR_MARKERS,
        ),
        f"phase2_closure_validator:missing_marker:{PHASE2_CLOSURE_VALIDATOR_MARKERS[0]}",
    )

    readme_text = "\n".join(README_MARKERS)
    expect_exact_issue(
        "readme_marker_failure",
        validate_required_markers(
            readme_text.replace(README_MARKERS[0], "", 1),
            label="scripts_readme",
            markers=README_MARKERS,
        ),
        f"scripts_readme:missing_marker:{README_MARKERS[0]}",
    )

    closure_text = "\n".join(CLOSURE_MARKERS)
    expect_exact_issue(
        "closure_marker_failure",
        validate_required_markers(
            closure_text.replace(CLOSURE_MARKERS[0], "", 1),
            label="phase2_closure_doc",
            markers=CLOSURE_MARKERS,
        ),
        f"phase2_closure_doc:missing_marker:{CLOSURE_MARKERS[0]}",
    )

    toolchain_notes_text = "\n".join(TOOLCHAIN_NOTES_MARKERS)
    expect_exact_issue(
        "toolchain_notes_marker_failure",
        validate_required_markers(
            toolchain_notes_text.replace(TOOLCHAIN_NOTES_MARKERS[0], "", 1),
            label="toolchain_notes",
            markers=TOOLCHAIN_NOTES_MARKERS,
        ),
        f"toolchain_notes:missing_marker:{TOOLCHAIN_NOTES_MARKERS[0]}",
    )

    with tempfile.TemporaryDirectory(prefix="phase2_cross_alignment_selftest_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        manifest_path = tmp_root / "phase2_cross_targets.json"
        manifest_path.write_text(json.dumps(valid_targets), encoding="utf-8")
        round_trip = load_json_object(manifest_path, label="targets")
        if round_trip["targets"] != EXPECTED_TARGETS:
            raise SystemExit("phase2-cross-alignment:self-test:json_round_trip")

    print("PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass")
    print("PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT=18")
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
        PHASE2_CLOSURE_VALIDATOR,
        WORKFLOW,
        MAKEFILE,
        README,
        CLOSURE_DOC,
        TOOLCHAIN_NOTES,
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
            PHASE2_CLOSURE_VALIDATOR.read_text(encoding="utf-8"),
            label="phase2_closure_validator",
            markers=PHASE2_CLOSURE_VALIDATOR_MARKERS,
        )
    )
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
            TOOLCHAIN_NOTES.read_text(encoding="utf-8"),
            label="toolchain_notes",
            markers=TOOLCHAIN_NOTES_MARKERS,
        )
    )
    issues.extend(validate_exact_workflow_runs(WORKFLOW.read_text(encoding="utf-8")))
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
