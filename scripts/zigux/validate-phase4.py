#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/artifact-diff.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/phase4_build.zig",
]

REQUIRED_MAKE_MARKERS = [
    "PHONY += phase4-validate phase4-test",
    "phase4-validate:",
    "scripts/zigux/validate-phase4.py",
    "phase4-test:",
    "zigux/tests/phase4_build.zig",
]
REQUIRED_WORKFLOW_MARKERS = [
    "python3 scripts/zigux/validate-phase4.py",
    "python3 scripts/zigux/validate-phase4.py --self-test",
    "zig build test --build-file zigux/tests/phase4_build.zig",
]
REQUIRED_DOC_MARKERS = [
    "Current Phase 4 use",
    "scripts/zigux/artifact_diff.py",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/phase4_build.zig",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/phase4-validation-matrix.md",
]
REQUIRED_PHASE4_GATE_EVIDENCE_MARKERS = [
    "PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions",
    "PHASE4_VALIDATOR_BLOB_SHA=",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true",
    "PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false",
    "PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false",
]
REQUIRED_TESTS_README_MARKERS = [
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_build.zig",
    "scripts/zigux/validate-phase4.py",
]
REQUIRED_SCRIPT_README_MARKERS = [
    "validate-phase4.py",
    "atomic64_diff.zig",
    "runtime_atomic64_diff.zig",
    "Phase 4 flow",
    "phase4_build.zig",
    "phase4-validation-matrix.md",
]
REQUIRED_DOC_README_MARKERS = [
    "Phase 4 notes",
    "validate-phase4.py",
    "phase4-validation-matrix.md",
    "atomic64_diff.zig",
    "runtime_atomic64_diff.zig",
]
REQUIRED_PHASE4_MATRIX_MARKERS = [
    "atomic64_diff.zig",
    "runtime_atomic64_diff.zig",
    "phase4_runtime_atomic64_diff_manifest.json",
    "phase4_runtime_atomic64_diff_survey.zig",
    "bitmap_diff.zig",
    "phase4_bitmap_live_helper_replay.zig",
    "rollback owner",
    "Lab And CI Matrix",
    "threshold posture",
    "zig build test --build-file zigux/tests/phase4_build.zig",
    "Remaining Roadmap Gaps",
    "samples/zigux/kprobe_example.zig",
    "samples/kprobes/kprobe_example.c",
    "samples/zigux/test_fsmount.zig",
    "samples/vfs/test-fsmount.c",
    "hard perf thresholds and acceptable limits for the atomic64 and bitmap gates remain intentionally unapproved",
]
REQUIRED_PHASE4_BUILD_MARKERS = [
    "atomic64_diff.zig",
    "phase4_runtime_atomic64_diff_survey.zig",
    "bitmap_diff.zig",
    "phase4_bitmap_live_helper_replay.zig",
    "phase4-runtime-atomic64-diff-tests",
    "phase4-runtime-atomic64-diff-survey-tests",
    "phase4-bitmap-diff-tests",
    "phase4-bitmap-live-helper-replay-tests",
]
EXACT_ONCE_TESTS_README_MARKERS = [
    "scripts/zigux/validate-phase4.py",
    "zigux/tests/bitmap_diff.zig",
]
EXACT_ONCE_SCRIPT_README_MARKERS = [
    "Phase 4 flow",
    "phase4-validation-matrix.md",
]
EXACT_ONCE_DOC_README_MARKERS = [
    "Phase 4 notes",
    "validate-phase4.py",
    "phase4-validation-matrix.md",
    "runtime_atomic64_diff.zig",
]
EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES = [
    "helper_self_test",
    "helper_self_test_repeat",
    "cli_missing_required_args",
    "cli_missing_actual_operand",
    "text_pass",
    "text_pass_repeat",
    "text_mismatch",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "json_pass",
    "json_mismatch",
    "json_mismatch_repeat",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
    "sha256_pass",
    "sha256_missing_expected",
    "sha256_missing_actual",
    "sha256_missing_both",
    "sha256_drift",
    "sha256_drift_repeat",
]
EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES = [
    "helper_self_test_repeat",
    "text_pass_repeat",
    "json_mismatch_repeat",
    "sha256_drift_repeat",
]
EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES = [
    case
    for case in EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES
    if case not in EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES
]


def _missing_files(root: Path) -> list[str]:
    missing = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(rel)
    return missing


def _count_marker(text: str, marker: str) -> int:
    return text.count(marker)


def _require_exact_once(text: str, marker: str, prefix: str, missing_markers: list[str]) -> None:
    count = _count_marker(text, marker)
    if count != 1:
        missing_markers.append(f"{prefix}:exact_once:{marker}:{count}")


def _line_value(lines: list[str], prefix: str) -> str | None:
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix):]
    return None


def _expected_case_line(cases: list[str]) -> str:
    return ",".join(cases)


def validate_root(root: Path) -> list[str]:
    missing_markers: list[str] = []

    makefile = (root / "zigux/Makefile").read_text(encoding="utf-8")
    workflow = (root / ".github/workflows/zigux-bootstrap.yml").read_text(encoding="utf-8")
    artifact_doc = (root / "Documentation/zigux/artifact-diff.md").read_text(encoding="utf-8")
    phase4_gate_evidence = (root / "Documentation/zigux/phase4-gate-evidence.md").read_text(encoding="utf-8")
    tests_readme = (root / "zigux/tests/README.md").read_text(encoding="utf-8")
    script_readme = (root / "scripts/zigux/README.md").read_text(encoding="utf-8")
    doc_readme = (root / "Documentation/zigux/README.md").read_text(encoding="utf-8")
    phase4_matrix = (root / "Documentation/zigux/phase4-validation-matrix.md").read_text(encoding="utf-8")
    phase4_build = (root / "zigux/tests/phase4_build.zig").read_text(encoding="utf-8")

    for marker in REQUIRED_MAKE_MARKERS:
        if marker not in makefile:
            missing_markers.append(f"make:{marker}")
    for marker in REQUIRED_WORKFLOW_MARKERS:
        if marker not in workflow:
            missing_markers.append(f"workflow:{marker}")
    for marker in REQUIRED_DOC_MARKERS:
        if marker not in artifact_doc:
            missing_markers.append(f"doc:{marker}")
    for marker in REQUIRED_PHASE4_GATE_EVIDENCE_MARKERS:
        if marker not in phase4_gate_evidence:
            missing_markers.append(f"gate_evidence:{marker}")
    for marker in REQUIRED_TESTS_README_MARKERS:
        if marker not in tests_readme:
            missing_markers.append(f"tests_readme:{marker}")
    for marker in REQUIRED_SCRIPT_README_MARKERS:
        if marker not in script_readme:
            missing_markers.append(f"script_readme:{marker}")
    for marker in REQUIRED_DOC_README_MARKERS:
        if marker not in doc_readme:
            missing_markers.append(f"doc_readme:{marker}")
    for marker in REQUIRED_PHASE4_MATRIX_MARKERS:
        if marker not in phase4_matrix:
            missing_markers.append(f"phase4_matrix:{marker}")
    for marker in REQUIRED_PHASE4_BUILD_MARKERS:
        if marker not in phase4_build:
            missing_markers.append(f"phase4_build:{marker}")

    _require_exact_once(artifact_doc, "Current Phase 4 use", "doc", missing_markers)
    for marker in EXACT_ONCE_TESTS_README_MARKERS:
        _require_exact_once(tests_readme, marker, "tests_readme", missing_markers)
    for marker in EXACT_ONCE_SCRIPT_README_MARKERS:
        _require_exact_once(script_readme, marker, "script_readme", missing_markers)
    for marker in EXACT_ONCE_DOC_README_MARKERS:
        _require_exact_once(doc_readme, marker, "doc_readme", missing_markers)

    return missing_markers


def run_artifact_diff_contract_check(root: Path) -> list[str]:
    checker = root / "scripts/zigux/check-artifact-diff-contract.py"
    result = subprocess.run(
        [sys.executable, str(checker)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return [f"artifact_diff_contract:exit:{result.returncode}"]

    lines = result.stdout.splitlines()
    if "ARTIFACT_DIFF_CONTRACT=pass" not in lines:
        return ["artifact_diff_contract:missing_pass_marker"]

    base_case_count = _line_value(lines, "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=")
    if base_case_count is None:
        return ["artifact_diff_contract:missing_base_case_count_marker"]
    if base_case_count != str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES)):
        return [f"artifact_diff_contract:unexpected_base_case_count:{base_case_count}"]

    base_cases = _line_value(lines, "ARTIFACT_DIFF_CONTRACT_BASE_CASES=")
    if base_cases is None:
        return ["artifact_diff_contract:missing_base_cases_marker"]
    if base_cases != _expected_case_line(EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES):
        return [f"artifact_diff_contract:unexpected_base_cases:{base_cases}"]

    repeat_case_count = _line_value(lines, "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=")
    if repeat_case_count is None:
        return ["artifact_diff_contract:missing_repeat_case_count_marker"]
    if repeat_case_count != str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES)):
        return [f"artifact_diff_contract:unexpected_repeat_case_count:{repeat_case_count}"]

    repeat_cases = _line_value(lines, "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=")
    if repeat_cases is None:
        return ["artifact_diff_contract:missing_repeat_cases_marker"]
    if repeat_cases != _expected_case_line(EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES):
        return [f"artifact_diff_contract:unexpected_repeat_cases:{repeat_cases}"]

    case_count = _line_value(lines, "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=")
    if case_count is None:
        return ["artifact_diff_contract:missing_case_count_marker"]
    if case_count != str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES)):
        return [f"artifact_diff_contract:unexpected_case_count:{case_count}"]

    cases = _line_value(lines, "ARTIFACT_DIFF_CONTRACT_CASES=")
    if cases is None:
        return ["artifact_diff_contract:missing_cases_marker"]
    if cases != _expected_case_line(EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES):
        return [f"artifact_diff_contract:unexpected_cases:{cases}"]

    return []


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _write_contract_checker_fixture(
    path: Path,
    *,
    base_case_count: str | None,
    base_cases: list[str] | None,
    repeat_case_count: str | None,
    repeat_cases: list[str] | None,
    case_count: str | None,
    cases: list[str] | None,
    include_pass: bool = True,
) -> None:
    lines = ["#!/usr/bin/env python3"]
    if include_pass:
        lines.append("print('ARTIFACT_DIFF_CONTRACT=pass')")
    if base_case_count is not None:
        lines.append(f"print('ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT={base_case_count}')")
    if base_cases is not None:
        lines.append("print('ARTIFACT_DIFF_CONTRACT_BASE_CASES=" + ",".join(base_cases) + "')")
    if repeat_case_count is not None:
        lines.append(f"print('ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT={repeat_case_count}')")
    if repeat_cases is not None:
        lines.append("print('ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=" + ",".join(repeat_cases) + "')")
    if case_count is not None:
        lines.append(f"print('ARTIFACT_DIFF_CONTRACT_CASE_COUNT={case_count}')")
    if cases is not None:
        lines.append("print('ARTIFACT_DIFF_CONTRACT_CASES=" + ",".join(cases) + "')")
    _write(path, "\n".join(lines) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_validator_selftest_") as tmp_dir_str:
        root = Path(tmp_dir_str)

        _write(root / "scripts/zigux/artifact_diff.py", "# placeholder\n")
        _write_contract_checker_fixture(
            root / "scripts/zigux/check-artifact-diff-contract.py",
            base_case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES)),
            base_cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES,
            repeat_case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES)),
            repeat_cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES,
            case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES)),
            cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES,
        )
        _write(root / "scripts/zigux/validate-phase4.py", "# placeholder\n")
        _write(
            root / "Documentation/zigux/artifact-diff.md",
            "\n".join(
                [
                    "# Artifact Diff Policy",
                    "",
                    "Current Phase 4 use",
                    "- `scripts/zigux/artifact_diff.py` stays the shared host-side comparison helper.",
                    "- `zigux/tests/atomic64_diff.zig` remains in the packet as the roadmap-named wrapper.",
                    "- `zigux/tests/runtime_atomic64_diff.zig` remains in the packet as the shared replay body.",
                    "- `zigux/tests/bitmap_diff.zig` remains in the packet.",
                    "- `zigux/tests/phase4_bitmap_live_helper_replay.zig` remains in the packet.",
                    "- `zigux/tests/phase4_build.zig` remains in the packet.",
                    "- `scripts/zigux/validate-phase4.py` remains in the packet.",
                    "- `Documentation/zigux/phase4-validation-matrix.md` remains in the packet.",
                    "",
                ]
            )
            + "\n",
        )
        _write(
            root / "Documentation/zigux/phase4-gate-evidence.md",
            "\n".join(
                [
                    "# Phase 4 Gate Evidence",
                    "",
                    "- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`",
                    "- `PHASE4_VALIDATOR_BLOB_SHA=placeholder`",
                    "- `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` stays in the packet.",
                    "- `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` stays in the packet.",
                    "- `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`",
                    "- `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false`",
                    "- `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false`",
                    "",
                ]
            )
            + "\n",
        )
        _write(
            root / "Documentation/zigux/phase4-validation-matrix.md",
            "\n".join(
                [
                    "# Phase 4 Validation Matrix",
                    "",
                    "atomic64_diff.zig",
                    "runtime_atomic64_diff.zig",
                    "phase4_runtime_atomic64_diff_manifest.json",
                    "phase4_runtime_atomic64_diff_survey.zig",
                    "bitmap_diff.zig",
                    "phase4_bitmap_live_helper_replay.zig",
                    "rollback owner",
                    "Lab And CI Matrix",
                    "threshold posture",
                    "zig build test --build-file zigux/tests/phase4_build.zig",
                    "Remaining Roadmap Gaps",
                    "samples/zigux/kprobe_example.zig",
                    "samples/kprobes/kprobe_example.c",
                    "samples/zigux/test_fsmount.zig",
                    "samples/vfs/test-fsmount.c",
                    "hard perf thresholds and acceptable limits for the atomic64 and bitmap gates remain intentionally unapproved",
                    "",
                ]
            ),
        )
        _write(
            root / "zigux/Makefile",
            "\n".join(
                [
                    "PHONY += phase4-validate phase4-test",
                    "phase4-validate:",
                    "\tpython3 scripts/zigux/validate-phase4.py",
                    "phase4-test:",
                    "\tzig build test --build-file zigux/tests/phase4_build.zig",
                    "",
                ]
            ),
        )
        _write(
            root / ".github/workflows/zigux-bootstrap.yml",
            "\n".join(
                [
                    "jobs:",
                    "  bootstrap:",
                    "    steps:",
                    "      - name: Validate Phase 4 diff gates",
                    "        run: python3 scripts/zigux/validate-phase4.py",
                    "      - name: Self-test Phase 4 validator",
                    "        run: python3 scripts/zigux/validate-phase4.py --self-test",
                    "      - name: Run Phase 4 diff tests",
                    "        run: zig build test --build-file zigux/tests/phase4_build.zig",
                    "",
                ]
            ),
        )
        _write(root / "zigux/tests/atomic64_diff.zig", "// wrapper gate\n")
        _write(root / "zigux/tests/runtime_atomic64_diff.zig", "// runtime gate\n")
        _write(root / "zigux/tests/phase4_runtime_atomic64_diff_manifest.json", "{}\n")
        _write(root / "zigux/tests/phase4_runtime_atomic64_diff_survey.zig", "// survey gate\n")
        _write(root / "zigux/tests/bitmap_diff.zig", "// bitmap gate\n")
        _write(root / "zigux/tests/phase4_bitmap_live_helper_replay.zig", "// helper replay gate\n")
        _write(
            root / "zigux/tests/phase4_build.zig",
            "\n".join(
                [
                    "atomic64_diff.zig",
                    "phase4_runtime_atomic64_diff_survey.zig",
                    "bitmap_diff.zig",
                    "phase4_bitmap_live_helper_replay.zig",
                    "phase4-runtime-atomic64-diff-tests",
                    "phase4-runtime-atomic64-diff-survey-tests",
                    "phase4-bitmap-diff-tests",
                    "phase4-bitmap-live-helper-replay-tests",
                    "",
                ]
            ),
        )
        _write(
            root / "zigux/tests/README.md",
            "\n".join(
                [
                    "zigux/tests/atomic64_diff.zig",
                    "zigux/tests/runtime_atomic64_diff.zig",
                    "zigux/tests/bitmap_diff.zig",
                    "zigux/tests/phase4_build.zig",
                    "scripts/zigux/validate-phase4.py",
                    "",
                ]
            ),
        )
        _write(
            root / "scripts/zigux/README.md",
            "\n".join(
                [
                    "validate-phase4.py",
                    "atomic64_diff.zig",
                    "runtime_atomic64_diff.zig",
                    "Phase 4 flow",
                    "phase4_build.zig",
                    "phase4-validation-matrix.md",
                    "",
                ]
            ),
        )
        _write(
            root / "Documentation/zigux/README.md",
            "\n".join(
                [
                    "Phase 4 notes",
                    "validate-phase4.py",
                    "phase4-validation-matrix.md",
                    "atomic64_diff.zig",
                    "runtime_atomic64_diff.zig",
                    "",
                ]
            ),
        )

        assert _missing_files(root) == []
        assert validate_root(root) == []
        assert run_artifact_diff_contract_check(root) == []

        _write_contract_checker_fixture(
            root / "scripts/zigux/check-artifact-diff-contract.py",
            base_case_count="20",
            base_cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES,
            repeat_case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES)),
            repeat_cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES,
            case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES)),
            cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES,
        )
        assert run_artifact_diff_contract_check(root) == [
            "artifact_diff_contract:unexpected_base_case_count:20"
        ]

        _write_contract_checker_fixture(
            root / "scripts/zigux/check-artifact-diff-contract.py",
            base_case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES)),
            base_cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES[1:],
            repeat_case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES)),
            repeat_cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES,
            case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES)),
            cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES,
        )
        assert run_artifact_diff_contract_check(root) == [
            "artifact_diff_contract:unexpected_base_cases:"
            + _expected_case_line(EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES[1:])
        ]

        _write_contract_checker_fixture(
            root / "scripts/zigux/check-artifact-diff-contract.py",
            base_case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES)),
            base_cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES,
            repeat_case_count="3",
            repeat_cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES,
            case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES)),
            cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES,
        )
        assert run_artifact_diff_contract_check(root) == [
            "artifact_diff_contract:unexpected_repeat_case_count:3"
        ]

        _write_contract_checker_fixture(
            root / "scripts/zigux/check-artifact-diff-contract.py",
            base_case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES)),
            base_cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES,
            repeat_case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES)),
            repeat_cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES[1:],
            case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES)),
            cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES,
        )
        assert run_artifact_diff_contract_check(root) == [
            "artifact_diff_contract:unexpected_repeat_cases:"
            + _expected_case_line(EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES[1:])
        ]

        _write_contract_checker_fixture(
            root / "scripts/zigux/check-artifact-diff-contract.py",
            base_case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES)),
            base_cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES,
            repeat_case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES)),
            repeat_cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES,
            case_count="24",
            cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES,
        )
        assert run_artifact_diff_contract_check(root) == [
            "artifact_diff_contract:unexpected_case_count:24"
        ]

        _write_contract_checker_fixture(
            root / "scripts/zigux/check-artifact-diff-contract.py",
            base_case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES)),
            base_cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES,
            repeat_case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES)),
            repeat_cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES,
            case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES)),
            cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES[1:],
        )
        assert run_artifact_diff_contract_check(root) == [
            "artifact_diff_contract:unexpected_cases:"
            + _expected_case_line(EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES[1:])
        ]

        _write_contract_checker_fixture(
            root / "scripts/zigux/check-artifact-diff-contract.py",
            base_case_count=None,
            base_cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_BASE_CASES,
            repeat_case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES)),
            repeat_cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_REPEAT_CASES,
            case_count=str(len(EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES)),
            cases=EXPECTED_ARTIFACT_DIFF_CONTRACT_CASES,
        )
        assert run_artifact_diff_contract_check(root) == [
            "artifact_diff_contract:missing_base_case_count_marker"
        ]

    print("PHASE4_VALIDATE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 4 rollback-readiness packet.")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run isolated Phase 4 validator coverage in a temporary workspace.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = _missing_files(ROOT)
    if missing:
        print("PHASE4_VALIDATION=fail")
        print("MISSING_PHASE4_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE4_FILES_END")
        return 1

    missing_markers = validate_root(ROOT)
    if missing_markers:
        print("PHASE4_VALIDATION=fail")
        print("MISSING_PHASE4_MARKERS_START")
        for marker in missing_markers:
            print(marker)
        print("MISSING_PHASE4_MARKERS_END")
        return 1

    contract_failures = run_artifact_diff_contract_check(ROOT)
    if contract_failures:
        print("PHASE4_VALIDATION=fail")
        print("ARTIFACT_DIFF_CONTRACT_CHECK_START")
        for item in contract_failures:
            print(item)
        print("ARTIFACT_DIFF_CONTRACT_CHECK_END")
        return 1

    print("PHASE4_VALIDATION=pass")
    print(f"PHASE4_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE4_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_MAKE_MARKERS) + len(REQUIRED_WORKFLOW_MARKERS) + len(REQUIRED_DOC_MARKERS) + len(REQUIRED_PHASE4_GATE_EVIDENCE_MARKERS) + len(REQUIRED_TESTS_README_MARKERS) + len(REQUIRED_SCRIPT_README_MARKERS) + len(REQUIRED_DOC_README_MARKERS) + len(REQUIRED_PHASE4_MATRIX_MARKERS) + len(REQUIRED_PHASE4_BUILD_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
