#!/usr/bin/env python3
"""Fail-closed validator for the shipped Phase 2 closure packet."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    ".github/workflows/zigux-bootstrap.yml",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/zig-toolchain-policy.json",
    "scripts/zigux/fixdep.zig",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
]

PHASE2_DOC_ROOT_REQUIRED_MARKERS = [
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
]

PHASE2_TOOLCHAIN_NOTES_REQUIRED_MARKERS = [
    "scripts/zigux/zig-toolchain-policy.json",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test",
    "python3 scripts/zigux/check-phase2-tool-manifest-packets.py",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "python3 scripts/zigux/check-fixdep-diff.py",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
    "when `ZIG` is unset, `zigux/Makefile` reuses that repo-local `.zig-toolchain` install",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-validate",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2",
    "current pinned Zig channel:",
    "current minimum Zig version:",
    "current pinned bootstrap archive target:",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
]

PHASE2_CLOSURE_REQUIRED_MARKERS = [
    "PHASE2_STATUS=closed",
    "PHASE2_TOOL_COUNT=6",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "PHASE2_CROSS_TARGET_COUNT=3",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test",
    "python3 scripts/zigux/check-phase2-tool-manifest-packets.py",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "python3 scripts/zigux/check-fixdep-diff.py",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
]

PHASE2_CHECKLIST_REQUIRED_MARKERS = [
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "make -C zigux phase2-validate",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2",
]

PHASE2_SCRIPTS_README_REQUIRED_MARKERS = [
    "validate-phase2-closure.py",
    "check-phase2-fixdep-gate.py",
    "check-fixdep-diff.py",
    "fixdep.zig",
    "check-phase2-tool-manifest-packets.py --self-test",
    "check-phase2-tool-manifest-packets.py",
    "check-phase2-tests-readme-alignment.py",
    "check-phase2-cross-selftest-alignment.py --self-test",
    "check-phase2-cross-selftest-alignment.py",
    "check-phase2-kconfig-selftest-alignment.py --self-test",
    "check-phase2-kconfig-selftest-alignment.py",
    "check-phase2-toolchain-pin-scope.py --self-test",
    "check-phase2-toolchain-pin-scope.py",
    "phase2_artifact_tools_manifest.json",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-validate",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2",
]

PHASE2_TESTS_README_REQUIRED_MARKERS = [
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zig test scripts/zigux/fixdep.zig",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
]

EXACT_MAKEFILE_RUN_COUNTS = {
    "phase2-toolchain:": 1,
    "phase2-validate: phase2-toolchain": 1,
    "phase2-tools:": 1,
    "phase2-kconfig:": 1,
    "phase2-cross:": 1,
    "phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross": 1,
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
    "python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-tool-manifest-packets.py": 1,
    "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-fixdep-gate.py": 1,
    "python3 scripts/zigux/check-fixdep-diff.py --self-test": 1,
    "python3 scripts/zigux/check-fixdep-diff.py": 1,
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py": 1,
    "python3 scripts/zigux/validate-phase2-closure.py": 1,
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py": 1,
    "python3 scripts/zigux/check-phase2-cross.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py": 1,
    "python3 scripts/zigux/check-genksyms-crc-diff.py": 1,
    "python3 scripts/zigux/check-mk-elfconfig-diff.py": 1,
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py": 1,
    "python3 scripts/zigux/check-kconfig-bridge.py --self-test": 1,
    "python3 scripts/zigux/check-kconfig-bridge.py": 1,
}

EXACT_WORKFLOW_RUN_COUNTS = {
    "run: python3 scripts/zigux/validate-phase2.py": 1,
    "run: python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase2-tool-manifest-packets.py": 1,
    "run: python3 scripts/zigux/validate-phase2-closure.py": 1,
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py": 1,
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py": 1,
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
    "run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py": 1,
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py": 1,
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test": 1,
    "run: python3 scripts/zigux/check-genksyms-bridge.py": 1,
    "run: python3 scripts/zigux/check-genksyms-crc-diff.py": 1,
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test": 1,
    "run: python3 scripts/zigux/check-kconfig-bridge.py": 1,
    "run: python3 scripts/zigux/check-mk-elfconfig-diff.py --self-test": 1,
    "run: python3 scripts/zigux/check-mk-elfconfig-diff.py": 1,
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test": 1,
    "run: python3 scripts/zigux/install-zig.py --self-test": 1,
}


def repo_root_from_script(script_path: Path) -> Path:
    return script_path.resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_files(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"required_file:{relative}")
    return errors


def require_markers(name: str, text: str, markers: list[str]) -> list[str]:
    errors: list[str] = []
    for marker in markers:
        if marker not in text:
            errors.append(f"{name}:missing_marker:{marker}")
    return errors


def count_marker_lines(text: str, marker: str) -> int:
    count = 0
    self_test_variant = f"{marker} --self-test"
    for line in text.splitlines():
        stripped = line.strip()
        if marker not in stripped:
            continue
        if not marker.endswith("--self-test") and self_test_variant in stripped:
            continue
        count += 1
    return count


def require_exact_counts(name: str, text: str, counts: dict[str, int]) -> list[str]:
    errors: list[str] = []
    for marker, expected in counts.items():
        actual = count_marker_lines(text, marker)
        if actual != expected:
            errors.append(f"{name}:count:{marker}:expected={expected}:actual={actual}")
    return errors


def validate_toolchain_policy(root: Path, notes_text: str) -> list[str]:
    errors: list[str] = []
    policy_path = root / "scripts/zigux/zig-toolchain-policy.json"
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"toolchain_policy:invalid_json:{exc.msg}"]

    if policy.get("phase") != "Phase 2":
        errors.append("toolchain_policy:phase")

    channel = policy.get("channel")
    minimum_version = policy.get("minimum_version")
    if not channel:
        errors.append("toolchain_policy:channel")
    if not minimum_version:
        errors.append("toolchain_policy:minimum_version")
    if channel and f"current pinned Zig channel: `{channel}`" not in notes_text:
        errors.append("toolchain_notes:channel")
    if minimum_version and f"current minimum Zig version: `{minimum_version}`" not in notes_text:
        errors.append("toolchain_notes:minimum_version")

    archive_sha = policy.get("archive_sha256", {})
    if "x86_64-linux" not in archive_sha:
        errors.append("toolchain_policy:x86_64-linux")
    if "current pinned bootstrap archive target: `x86_64-linux`" not in notes_text:
        errors.append("toolchain_notes:x86_64-linux")

    approval = policy.get("approval_policy", {})
    for key in (
        "shared_phase2_checklist_ack_required",
        "fresh_bootstrap_runner_evidence_required",
        "separate_cross_target_expansion_approval_required",
    ):
        if approval.get(key) is not True:
            errors.append(f"toolchain_policy:approval:{key}")
    return errors


def validate(root: Path) -> list[str]:
    errors = require_files(root)
    if errors:
        return errors

    docs_root_text = read_text(root / "Documentation/zigux/README.md")
    notes_text = read_text(root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
    closure_text = read_text(root / "Documentation/zigux/phase2-closure.md")
    checklist_text = read_text(root / "Documentation/zigux/review-checklist.md")
    scripts_readme_text = read_text(root / "scripts/zigux/README.md")
    tests_readme_text = read_text(root / "zigux/tests/README.md")
    makefile_text = read_text(root / "zigux/Makefile")
    workflow_text = read_text(root / ".github/workflows/zigux-bootstrap.yml")

    errors.extend(require_markers("docs_root", docs_root_text, PHASE2_DOC_ROOT_REQUIRED_MARKERS))
    errors.extend(require_markers("toolchain_notes", notes_text, PHASE2_TOOLCHAIN_NOTES_REQUIRED_MARKERS))
    errors.extend(require_markers("closure", closure_text, PHASE2_CLOSURE_REQUIRED_MARKERS))
    errors.extend(require_markers("checklist", checklist_text, PHASE2_CHECKLIST_REQUIRED_MARKERS))
    errors.extend(require_markers("scripts_readme", scripts_readme_text, PHASE2_SCRIPTS_README_REQUIRED_MARKERS))
    errors.extend(require_markers("tests_readme", tests_readme_text, PHASE2_TESTS_README_REQUIRED_MARKERS))
    errors.extend(require_exact_counts("makefile", makefile_text, EXACT_MAKEFILE_RUN_COUNTS))
    errors.extend(require_exact_counts("workflow", workflow_text, EXACT_WORKFLOW_RUN_COUNTS))
    errors.extend(validate_toolchain_policy(root, notes_text))
    return errors


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    for relative in REQUIRED_FILES:
        write(root / relative, "")

    write(root / "Documentation/zigux/README.md", "\n".join(PHASE2_DOC_ROOT_REQUIRED_MARKERS) + "\n")
    write(root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md", "\n".join(PHASE2_TOOLCHAIN_NOTES_REQUIRED_MARKERS + [
        "current pinned Zig channel: `0.17.0-dev.87+9b177a7d2`",
        "current minimum Zig version: `0.17.0-dev.87+9b177a7d2`",
        "current pinned bootstrap archive target: `x86_64-linux`",
    ]) + "\n")
    write(root / "Documentation/zigux/phase2-closure.md", "\n".join(PHASE2_CLOSURE_REQUIRED_MARKERS) + "\n")
    write(root / "Documentation/zigux/review-checklist.md", "\n".join(PHASE2_CHECKLIST_REQUIRED_MARKERS) + "\n")
    write(root / "scripts/zigux/README.md", "\n".join(PHASE2_SCRIPTS_README_REQUIRED_MARKERS) + "\n")
    write(root / "zigux/tests/README.md", "\n".join(PHASE2_TESTS_README_REQUIRED_MARKERS) + "\n")
    write(
        root / "zigux/Makefile",
        "\n".join(marker for marker, count in EXACT_MAKEFILE_RUN_COUNTS.items() for _ in range(count)) + "\n",
    )
    write(
        root / ".github/workflows/zigux-bootstrap.yml",
        "\n".join(marker for marker, count in EXACT_WORKFLOW_RUN_COUNTS.items() for _ in range(count)) + "\n",
    )
    write(
        root / "scripts/zigux/zig-toolchain-policy.json",
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "fixture"},
                "approval_policy": {
                    "shared_phase2_checklist_ack_required": True,
                    "fresh_bootstrap_runner_evidence_required": True,
                    "separate_cross_target_expansion_approval_required": True,
                },
            },
            indent=2,
        )
        + "\n",
    )
    for relative in (
        "scripts/zigux/validate-phase2.py",
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-fixdep-diff.py",
        "scripts/zigux/check-phase2-tool-manifest-packets.py",
        "scripts/zigux/check-phase2-tests-readme-alignment.py",
        "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
        "scripts/zigux/check-genksyms-bridge.py",
        "scripts/zigux/check-phase2-cross-selftest-alignment.py",
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "scripts/zigux/check-phase2-toolchain-pin-scope.py",
        "scripts/zigux/fixdep.zig",
        "zigux/tests/fixtures/phase2_tool_manifest.json",
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
        "zigux/tests/fixtures/phase2_cross_targets.json",
    ):
        write(root / relative, "fixture\n")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase2-closure-selftest-") as temp_dir:
        root = Path(temp_dir)
        build_self_test_fixture(root)

        baseline_errors = validate(root)
        cases += 1
        if baseline_errors:
            print("phase2_closure_selftest:baseline_failed")
            for error in baseline_errors:
                print(error)
            return 1

        missing_notes_file_root = root / "missing_notes_file"
        build_self_test_fixture(missing_notes_file_root)
        (missing_notes_file_root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md").unlink()
        cases += 1
        missing_notes_file_errors = validate(missing_notes_file_root)
        expected_notes_file_error = "required_file:Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
        if expected_notes_file_error not in missing_notes_file_errors:
            print("phase2_closure_selftest:missing_notes_file_not_detected")
            for error in missing_notes_file_errors:
                print(error)
            return 1

        missing_phase2_validator_root = root / "missing_phase2_validator"
        build_self_test_fixture(missing_phase2_validator_root)
        (missing_phase2_validator_root / "scripts/zigux/validate-phase2.py").unlink()
        cases += 1
        missing_phase2_validator_errors = validate(missing_phase2_validator_root)
        expected_phase2_validator_error = "required_file:scripts/zigux/validate-phase2.py"
        if expected_phase2_validator_error not in missing_phase2_validator_errors:
            print("phase2_closure_selftest:missing_phase2_validator_not_detected")
            for error in missing_phase2_validator_errors:
                print(error)
            return 1

        missing_note_root = root / "missing_note"
        build_self_test_fixture(missing_note_root)
        notes_path = missing_note_root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
        notes_path.write_text(
            notes_path.read_text(encoding="utf-8").replace(
                "zigux/tests/fixtures/phase2_artifact_tools_manifest.json", "", 1
            ),
            encoding="utf-8",
        )
        cases += 1
        missing_note_errors = validate(missing_note_root)
        expected_note_error = "toolchain_notes:missing_marker:zigux/tests/fixtures/phase2_artifact_tools_manifest.json"
        if expected_note_error not in missing_note_errors:
            print("phase2_closure_selftest:missing_note_anchor_not_detected")
            for error in missing_note_errors:
                print(error)
            return 1

        missing_closure_fixdep_root = root / "missing_closure_fixdep"
        build_self_test_fixture(missing_closure_fixdep_root)
        closure_path = missing_closure_fixdep_root / "Documentation/zigux/phase2-closure.md"
        closure_path.write_text(
            closure_path.read_text(encoding="utf-8").replace(
                "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test", "", 1
            ),
            encoding="utf-8",
        )
        cases += 1
        missing_closure_fixdep_errors = validate(missing_closure_fixdep_root)
        expected_closure_fixdep_error = (
            "closure:missing_marker:python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test"
        )
        if expected_closure_fixdep_error not in missing_closure_fixdep_errors:
            print("phase2_closure_selftest:missing_closure_fixdep_marker_not_detected")
            for error in missing_closure_fixdep_errors:
                print(error)
            return 1

        missing_workflow_root = root / "missing_workflow"
        build_self_test_fixture(missing_workflow_root)
        workflow_path = missing_workflow_root / ".github/workflows/zigux-bootstrap.yml"
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "run: python3 scripts/zigux/validate-phase2-closure.py", "", 1
            ),
            encoding="utf-8",
        )
        cases += 1
        missing_workflow_errors = validate(missing_workflow_root)
        expected_workflow_error = (
            "workflow:count:run: python3 scripts/zigux/validate-phase2-closure.py:expected=1:actual=0"
        )
        if expected_workflow_error not in missing_workflow_errors:
            print("phase2_closure_selftest:missing_workflow_hook_not_detected")
            for error in missing_workflow_errors:
                print(error)
            return 1

        missing_makefile_root = root / "missing_makefile"
        build_self_test_fixture(missing_makefile_root)
        makefile_path = missing_makefile_root / "zigux/Makefile"
        makefile_path.write_text(
            makefile_path.read_text(encoding="utf-8").replace(
                "python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test", "", 1
            ),
            encoding="utf-8",
        )
        cases += 1
        missing_makefile_errors = validate(missing_makefile_root)
        expected_makefile_error = (
            "makefile:count:python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test:expected=1:actual=0"
        )
        if expected_makefile_error not in missing_makefile_errors:
            print("phase2_closure_selftest:missing_makefile_hook_not_detected")
            for error in missing_makefile_errors:
                print(error)
            return 1

    print("PHASE2_CLOSURE_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_SELF_TEST_CASE_COUNT={cases}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    root = args.root if args.root is not None else repo_root_from_script(Path(__file__))
    errors = validate(root)
    if errors:
        for error in errors:
            print(error)
        return 1

    print("PHASE2_CLOSURE_VALIDATE=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
