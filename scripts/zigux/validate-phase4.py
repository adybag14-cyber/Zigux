#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent

REQUIRED_FILES = [
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-remaining-gap-matrix.py",
    "scripts/zigux/check-phase4-workflow-route-counts.py",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/artifact-diff.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
    "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_diff_manifest.json",
    "zigux/tests/phase4_bitmap_diff_survey.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "zigux/tests/phase4_kprobe_example_survey.zig",
    "zigux/tests/phase4_test_fsmount_manifest.json",
    "zigux/tests/phase4_test_fsmount_survey.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/phase9_build.zig",
]

REQUIRED_MAKE_MARKERS = [
    "PHONY += phase4-validate",
    "phase4-validate:",
    "scripts/zigux/validate-phase4.py --self-test",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-workflow-route-counts.py",
    "phase4-test:",
    "zig build test --build-file zigux/tests/phase4_build.zig",
    "phase4-runtime-atomic64-diff:",
    "$(ZIG) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
    "phase4-runtime-atomic64-diff-survey",
    "phase4-bitmap-diff:",
    "$(ZIG) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
    "phase4-bitmap-diff-survey",
    "phase4-bitmap-live-helper-replay:",
    "$(ZIG) build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig",
    "phase4-perf-baseline-survey",
    "phase4-test-fsmount-survey",
    "phase4-kprobe-example-survey",
]

REQUIRED_WORKFLOW_MARKERS = [
    "python3 scripts/zigux/validate-phase4.py --self-test",
    "make -C zigux phase4-validate",
    "python3 scripts/zigux/validate-phase4.py",
    "python3 scripts/zigux/check-phase4-gate-evidence.py",
    "zig build test --build-file zigux/tests/phase4_build.zig",
]

REQUIRED_ARTIFACT_DOC_MARKERS = [
    "Current Phase 4 use",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_diff_survey.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/phase4-validation-matrix.md",
]

REQUIRED_GATE_EVIDENCE_MARKERS = [
    "PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions",
    "PHASE4_VALIDATOR_BLOB_SHA=",
    "PHASE4_BUILD_BLOB_SHA=",
    "PHASE4_MAKEFILE_BLOB_SHA=",
    "PHASE4_WORKFLOW_BLOB_SHA=",
    "PHASE4_DOC_README_BLOB_SHA=",
    "PHASE4_SCRIPT_README_BLOB_SHA=",
    "PHASE4_TESTS_README_BLOB_SHA=",
    "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=",
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=",
    "PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true",
    "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true",
    "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true",
    "PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true",
    "PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true",
    "PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true",
    "shared CI perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.",
]

REQUIRED_TESTS_README_MARKERS = [
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_diff_manifest.json",
    "zigux/tests/phase4_bitmap_diff_survey.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "zigux/tests/phase4_kprobe_example_survey.zig",
    "zig test zigux/tests/phase4_kprobe_example_survey.zig",
    "make -C zigux phase4-kprobe-example-survey",
    "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    "zigux/tests/phase4_test_fsmount_manifest.json",
    "zigux/tests/phase4_test_fsmount_survey.zig",
    "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-test-fsmount-survey",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "scripts/zigux/validate-phase4.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "scripts/zigux/check-phase4-workflow-route-counts.py",
]

REQUIRED_SCRIPT_README_MARKERS = [
    "Phase 4 flow",
    "validate-phase4.py",
    "check-artifact-diff-contract.py",
    "check-phase4-gate-evidence.py",
    "check-phase4-workflow-route-counts.py",
    "phase4_bitmap_diff_manifest.json",
    "phase4_bitmap_diff_survey.zig",
    "phase4_perf_baseline_manifest.json",
    "phase4_perf_baseline_survey.zig",
    "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
    "make -C zigux phase4-kprobe-example-survey",
    "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    "make -C zigux phase4-test-fsmount-survey",
    "approved local-only benchmark commands and acceptable limits",
    "shared-CI perf promotion",
]

REQUIRED_DOC_README_MARKERS = [
    "Phase 4 notes",
    "validate-phase4.py",
    "check-phase4-gate-evidence.py",
    "phase4-gate-evidence.md",
    "phase4-validation-matrix.md",
    "phase4_bitmap_diff_survey.zig",
    "approved local-only acceptable limits",
]

REQUIRED_REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 4 validation packet",
    "Documentation/zigux/phase4-validation-matrix.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "scripts/zigux/check-phase4-workflow-route-counts.py",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/validate-phase4.py",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/phase4_bitmap_diff_manifest.json",
    "zigux/tests/phase4_bitmap_diff_survey.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "pending shared-CI perf-promotion posture",
]

REQUIRED_PHASE4_MATRIX_MARKERS = [
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "scripts/zigux/check-phase4-workflow-route-counts.py",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "atomic64_diff.zig",
    "runtime_atomic64_diff.zig",
    "phase4_runtime_atomic64_diff_manifest.json",
    "phase4_runtime_atomic64_diff_survey.zig",
    "bitmap_diff.zig",
    "phase4_bitmap_diff_manifest.json",
    "phase4_bitmap_diff_survey.zig",
    "phase4_perf_baseline_manifest.json",
    "phase4_perf_baseline_survey.zig",
    "phase4_test_fsmount_manifest.json",
    "phase4_test_fsmount_survey.zig",
    "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-test-fsmount-survey",
    "reviewability_only_no_perf_threshold",
    "samples/vfs/test-fsmount.c",
    "rollback owner",
    "Lab And CI Matrix",
    "local-only acceptable limits are approved today",
    "Remaining Roadmap Gaps",
    "samples/zigux/kprobe_example.zig",
    "samples/zigux/test_fsmount.zig",
]

PHASE4_RUNTIME_ATOMIC64_PIN_TARGETS = {
    "phase4_build_blob_sha": "zigux/tests/phase4_build.zig",
    "phase4_validator_blob_sha": "scripts/zigux/validate-phase4.py",
    "phase4_validation_matrix_blob_sha": "Documentation/zigux/phase4-validation-matrix.md",
    "phase4_review_checklist_blob_sha": "Documentation/zigux/review-checklist.md",
    "phase9_build_blob_sha": "zigux/tests/phase9_build.zig",
}

REQUIRED_PHASE4_RUNTIME_ATOMIC64_REVERSIBLE_DELIVERY_MARKERS = [
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_build.zig",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
]

REQUIRED_PHASE4_RUNTIME_ATOMIC64_SURVEY_MARKERS = [
    'test "phase 4 atomic64 survey keeps wrapper handoff, owner map, and current local-only perf evidence explicit" {',
    'test "phase 4 atomic64 survey keeps the current roadmap gap summary reviewable" {',
    'test "phase 4 atomic64 survey keeps reversible delivery and next-step evidence explicit" {',
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
]

REQUIRED_PHASE4_PERF_BASELINE_MATRIX_ROW_MARKERS = [
    "`zigux/tests/phase4_perf_baseline_survey.zig` dedicated local survey that keeps the approved local benchmark commands and the approved local-only acceptable limits machine-checked for both landed rollback gates `Validation and Perf Team` `Validation and Perf Team`",
    "not on the shared workflow or validator packet yet; keep this survey local until any shared CI perf promotion is intentionally approved",
    "`zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` or `make -C zigux phase4-perf-baseline-survey`",
    "`local_only_commands_and_limits_approved_shared_ci_perf_promotion_pending`",
]

GENERIC_CHECKS = [
    ("ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CHECK", ["scripts/zigux/check-phase4-artifact-diff-determinism.py", "--self-test"], None),
    ("ARTIFACT_DIFF_CONTRACT_SELF_TEST_CHECK", ["scripts/zigux/check-artifact-diff-contract.py", "--self-test"], "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass"),
    ("ARTIFACT_DIFF_CONTRACT_CHECK", ["scripts/zigux/check-artifact-diff-contract.py"], "ARTIFACT_DIFF_CONTRACT=pass"),
    ("PHASE4_GATE_EVIDENCE_SELF_TEST_CHECK", ["scripts/zigux/check-phase4-gate-evidence.py", "--self-test"], "PHASE4_GATE_EVIDENCE_SELF_TEST=pass"),
    ("PHASE4_GATE_EVIDENCE_CHECK", ["scripts/zigux/check-phase4-gate-evidence.py"], "PHASE4_GATE_EVIDENCE_CHECK=pass"),
    ("PHASE4_REMAINING_GAP_MATRIX_SELF_TEST_CHECK", ["scripts/zigux/check-phase4-remaining-gap-matrix.py", "--self-test"], "PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=pass"),
    ("PHASE4_REMAINING_GAP_MATRIX_CHECK", ["scripts/zigux/check-phase4-remaining-gap-matrix.py"], "PHASE4_REMAINING_GAP_MATRIX_CHECK=pass"),
    ("PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST_CHECK", ["scripts/zigux/check-phase4-workflow-route-counts.py", "--self-test"], "PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass"),
    ("PHASE4_WORKFLOW_ROUTE_COUNTS_CHECK", ["scripts/zigux/check-phase4-workflow-route-counts.py"], "PHASE4_WORKFLOW_ROUTE_COUNTS=pass"),
]

MARKER_GROUPS = [
    ("make", "zigux/Makefile", REQUIRED_MAKE_MARKERS),
    ("workflow", ".github/workflows/zigux-bootstrap.yml", REQUIRED_WORKFLOW_MARKERS),
    ("artifact_doc", "Documentation/zigux/artifact-diff.md", REQUIRED_ARTIFACT_DOC_MARKERS),
    ("gate_evidence", "Documentation/zigux/phase4-gate-evidence.md", REQUIRED_GATE_EVIDENCE_MARKERS),
    ("tests_readme", "zigux/tests/README.md", REQUIRED_TESTS_README_MARKERS),
    ("script_readme", "scripts/zigux/README.md", REQUIRED_SCRIPT_README_MARKERS),
    ("doc_readme", "Documentation/zigux/README.md", REQUIRED_DOC_README_MARKERS),
    ("review_checklist", "Documentation/zigux/review-checklist.md", REQUIRED_REVIEW_CHECKLIST_MARKERS),
    ("phase4_matrix", "Documentation/zigux/phase4-validation-matrix.md", REQUIRED_PHASE4_MATRIX_MARKERS),
]

PLACEHOLDER_FILES = [
    "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
    "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_diff_manifest.json",
    "zigux/tests/phase4_bitmap_diff_survey.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "zigux/tests/phase4_kprobe_example_survey.zig",
    "zigux/tests/phase4_test_fsmount_manifest.json",
    "zigux/tests/phase4_test_fsmount_survey.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/phase9_build.zig",
]


def _git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _write_stub_checker(path: Path, lines: list[str]) -> None:
    body = ["#!/usr/bin/env python3", "import sys", "if '--self-test' in sys.argv:"]
    body.extend([f"    print({line!r})" for line in lines])
    body.append("    raise SystemExit(0)")
    body.extend([f"print({line!r})" for line in lines])
    _write(path, "\n".join(body) + "\n")


def _missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def _check_markers(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def required_marker_count() -> int:
    return sum(len(markers) for _, _, markers in MARKER_GROUPS)


def run_root_marker_checks(root: Path) -> list[str]:
    failures: list[str] = []
    for prefix, rel_path, markers in MARKER_GROUPS:
        failures.extend(_check_markers((root / rel_path).read_text(encoding="utf-8"), markers, prefix))
    return failures


def _run_python_script(root: Path, relative_path: str, *args: str) -> tuple[int, list[str]]:
    result = subprocess.run(
        [sys.executable, str(root / relative_path), *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout.splitlines()


def run_generic_checks(root: Path) -> list[str]:
    failures: list[str] = []
    for label, argv, pass_marker in GENERIC_CHECKS:
        code, lines = _run_python_script(root, argv[0], *argv[1:])
        if code != 0:
            failures.append(f"{label}:exit:{code}")
        elif pass_marker is not None and pass_marker not in lines:
            failures.append(f"{label}:missing_pass_marker")
    return failures


def run_phase4_runtime_atomic64_packet_check(root: Path) -> list[str]:
    manifest = json.loads((root / "zigux/tests/phase4_runtime_atomic64_diff_manifest.json").read_text(encoding="utf-8"))
    survey_text = (root / "zigux/tests/phase4_runtime_atomic64_diff_survey.zig").read_text(encoding="utf-8")
    failures: list[str] = []
    for field, rel_path in PHASE4_RUNTIME_ATOMIC64_PIN_TARGETS.items():
        expected = _git_blob_sha1((root / rel_path).read_bytes())
        actual = manifest.get(field)
        if actual != expected:
            failures.append(f"phase4_runtime_atomic64_packet:unexpected_manifest_sha:{field}:{actual}:{expected}")
        count = survey_text.count(expected)
        if count != 1:
            failures.append(f"phase4_runtime_atomic64_packet:survey_sha_exact_count:{field}:{count}")
    reversible_delivery_evidence = manifest.get("reversible_delivery_evidence")
    if not isinstance(reversible_delivery_evidence, str) or not reversible_delivery_evidence.strip():
        failures.append("phase4_runtime_atomic64_packet:missing_reversible_delivery_evidence")
    else:
        failures.extend(
            _check_markers(
                reversible_delivery_evidence,
                REQUIRED_PHASE4_RUNTIME_ATOMIC64_REVERSIBLE_DELIVERY_MARKERS,
                "phase4_runtime_atomic64_packet:reversible_delivery_evidence",
            )
        )
    failures.extend(
        _check_markers(
            survey_text,
            REQUIRED_PHASE4_RUNTIME_ATOMIC64_SURVEY_MARKERS,
            "phase4_runtime_atomic64_packet:survey_marker",
        )
    )
    return failures


def run_phase4_perf_baseline_matrix_check(root: Path) -> list[str]:
    matrix_text = (root / "Documentation/zigux/phase4-validation-matrix.md").read_text(encoding="utf-8")
    return _check_markers(
        matrix_text,
        REQUIRED_PHASE4_PERF_BASELINE_MATRIX_ROW_MARKERS,
        "phase4_perf_baseline_matrix",
    )


def validate_root(root: Path) -> list[str]:
    failures = [f"file:{item}" for item in _missing_files(root)]
    if failures:
        return failures
    failures.extend(run_root_marker_checks(root))
    failures.extend(run_generic_checks(root))
    failures.extend(run_phase4_runtime_atomic64_packet_check(root))
    failures.extend(run_phase4_perf_baseline_matrix_check(root))
    return failures


def _write_fixture_tree(root: Path) -> None:
    _write(root / "scripts/zigux/validate-phase4.py", Path(__file__).read_text(encoding="utf-8"))
    _write(root / "scripts/zigux/artifact_diff.py", "#!/usr/bin/env python3\nprint('ARTIFACT_DIFF_SELF_TEST=pass')\n")
    _write_stub_checker(root / "scripts/zigux/check-artifact-diff-contract.py", [
        "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass",
        "ARTIFACT_DIFF_CONTRACT=pass",
    ])
    _write_stub_checker(root / "scripts/zigux/check-phase4-artifact-diff-determinism.py", [
        "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass",
        "PHASE4_ARTIFACT_DIFF_DETERMINISM=pass",
    ])
    _write_stub_checker(root / "scripts/zigux/check-phase4-gate-evidence.py", [
        "PHASE4_GATE_EVIDENCE_SELF_TEST=pass",
        "PHASE4_GATE_EVIDENCE_CHECK=pass",
    ])
    _write_stub_checker(root / "scripts/zigux/check-phase4-remaining-gap-matrix.py", [
        "PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=pass",
        "PHASE4_REMAINING_GAP_MATRIX_CHECK=pass",
    ])
    _write_stub_checker(root / "scripts/zigux/check-phase4-workflow-route-counts.py", [
        "PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass",
        "PHASE4_WORKFLOW_ROUTE_COUNTS=pass",
    ])

    _write(root / "zigux/Makefile", "\n".join([
        "PHONY += phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4",
        "phase4-validate:",
        "\tpython3 scripts/zigux/validate-phase4.py --self-test",
        "\tpython3 scripts/zigux/check-artifact-diff-contract.py",
        "\tpython3 scripts/zigux/check-phase4-artifact-diff-determinism.py",
        "\tpython3 scripts/zigux/check-phase4-gate-evidence.py",
        "\tpython3 scripts/zigux/check-phase4-workflow-route-counts.py",
        "phase4-test:",
        "\tzig build test --build-file zigux/tests/phase4_build.zig",
        "phase4-runtime-atomic64-diff:",
        "\t$(ZIG) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
        "phase4-bitmap-diff:",
        "\t$(ZIG) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
        "phase4-bitmap-live-helper-replay:",
        "\t$(ZIG) build phase4-bitmap-live-helper-replay --build-file zigux/tests/phase4_build.zig",
    ]) + "\n")

    _write(root / ".github/workflows/zigux-bootstrap.yml", "\n".join([
        "make -C zigux phase4-validate",
        "python3 scripts/zigux/validate-phase4.py --self-test",
        "python3 scripts/zigux/validate-phase4.py",
        "python3 scripts/zigux/check-phase4-gate-evidence.py",
        "zig build test --build-file zigux/tests/phase4_build.zig",
    ]) + "\n")

    _write(root / "Documentation/zigux/artifact-diff.md", "\n".join([
        "# Artifact Diff Policy",
        "",
        "Current Phase 4 use",
        "- `scripts/zigux/check-artifact-diff-contract.py`",
        "- `scripts/zigux/check-phase4-artifact-diff-determinism.py`",
        "- `scripts/zigux/check-phase4-gate-evidence.py`",
        "- `zigux/tests/atomic64_diff.zig`",
        "- `zigux/tests/runtime_atomic64_diff.zig`",
        "- `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`",
        "- `zigux/tests/bitmap_diff.zig`",
        "- `zigux/tests/phase4_bitmap_diff_survey.zig`",
        "- `zigux/tests/phase4_bitmap_live_helper_replay.zig`",
        "- `scripts/zigux/validate-phase4.py`",
        "- `Documentation/zigux/phase4-validation-matrix.md`",
    ]) + "\n")

    _write(root / "Documentation/zigux/README.md", "\n".join([
        "# Zigux Documentation",
        "Phase 4 notes",
        "validate-phase4.py",
        "check-phase4-gate-evidence.py",
        "phase4-gate-evidence.md",
        "phase4-validation-matrix.md",
        "phase4_bitmap_diff_survey.zig",
        "approved local-only acceptable limits",
    ]) + "\n")

    _write(root / "scripts/zigux/README.md", "\n".join([
        "# scripts/zigux",
        "Phase 4 flow",
        "validate-phase4.py",
        "check-artifact-diff-contract.py",
        "check-phase4-gate-evidence.py",
        "check-phase4-workflow-route-counts.py",
        "phase4_bitmap_diff_manifest.json",
        "phase4_bitmap_diff_survey.zig",
        "phase4_perf_baseline_manifest.json",
        "phase4_perf_baseline_survey.zig",
        "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
        "make -C zigux phase4-kprobe-example-survey",
        "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
        "make -C zigux phase4-test-fsmount-survey",
        "approved local-only benchmark commands and acceptable limits",
        "shared-CI perf promotion",
    ]) + "\n")

    _write(root / "zigux/tests/README.md", "\n".join([
        "# zigux/tests",
        "zigux/tests/atomic64_diff.zig",
        "zigux/tests/runtime_atomic64_diff.zig",
        "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
        "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
        "zigux/tests/bitmap_diff.zig",
        "zigux/tests/phase4_bitmap_diff_manifest.json",
        "zigux/tests/phase4_bitmap_diff_survey.zig",
        "zigux/tests/phase4_bitmap_live_helper_replay.zig",
        "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
        "zigux/tests/phase4_kprobe_example_manifest.json",
        "zigux/tests/phase4_kprobe_example_survey.zig",
        "zig test zigux/tests/phase4_kprobe_example_survey.zig",
        "make -C zigux phase4-kprobe-example-survey",
        "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
        "zigux/tests/phase4_test_fsmount_manifest.json",
        "zigux/tests/phase4_test_fsmount_survey.zig",
        "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
        "make -C zigux phase4-test-fsmount-survey",
        "zigux/tests/phase4_perf_baseline_manifest.json",
        "zigux/tests/phase4_perf_baseline_survey.zig",
        "scripts/zigux/validate-phase4.py",
        "scripts/zigux/check-phase4-artifact-diff-determinism.py",
        "scripts/zigux/check-phase4-workflow-route-counts.py",
    ]) + "\n")

    _write(root / "Documentation/zigux/review-checklist.md", "\n".join([
        "# Zigux Review Checklist",
        "if the change touches the shared Phase 4 validation packet",
        "Documentation/zigux/phase4-validation-matrix.md",
        "Documentation/zigux/phase4-gate-evidence.md",
        "scripts/zigux/check-artifact-diff-contract.py",
        "scripts/zigux/check-phase4-artifact-diff-determinism.py",
        "scripts/zigux/check-phase4-workflow-route-counts.py",
        "scripts/zigux/check-phase4-gate-evidence.py",
        "scripts/zigux/validate-phase4.py",
        "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
        "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
        "zigux/tests/phase4_bitmap_diff_manifest.json",
        "zigux/tests/phase4_bitmap_diff_survey.zig",
        "zigux/tests/phase4_bitmap_live_helper_replay.zig",
        "zigux/tests/phase4_perf_baseline_manifest.json",
        "zigux/tests/phase4_perf_baseline_survey.zig",
        "pending shared-CI perf-promotion posture",
    ]) + "\n")

    _write(root / "Documentation/zigux/phase4-validation-matrix.md", "\n".join([
        "# Phase 4 Validation Matrix",
        "scripts/zigux/check-artifact-diff-contract.py",
        "scripts/zigux/check-phase4-artifact-diff-determinism.py",
        "scripts/zigux/check-phase4-workflow-route-counts.py",
        "scripts/zigux/check-phase4-gate-evidence.py",
        "atomic64_diff.zig",
        "runtime_atomic64_diff.zig",
        "phase4_runtime_atomic64_diff_manifest.json",
        "phase4_runtime_atomic64_diff_survey.zig",
        "bitmap_diff.zig",
        "phase4_bitmap_diff_manifest.json",
        "phase4_bitmap_diff_survey.zig",
        "phase4_perf_baseline_manifest.json",
        "phase4_perf_baseline_survey.zig",
        "`zigux/tests/phase4_perf_baseline_survey.zig` dedicated local survey that keeps the approved local benchmark commands and the approved local-only acceptable limits machine-checked for both landed rollback gates `Validation and Perf Team` `Validation and Perf Team`",
        "not on the shared workflow or validator packet yet; keep this survey local until any shared CI perf promotion is intentionally approved",
        "`zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` or `make -C zigux phase4-perf-baseline-survey`",
        "`local_only_commands_and_limits_approved_shared_ci_perf_promotion_pending`",
        "phase4_test_fsmount_manifest.json",
        "phase4_test_fsmount_survey.zig",
        "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
        "make -C zigux phase4-test-fsmount-survey",
        "reviewability_only_no_perf_threshold",
        "samples/vfs/test-fsmount.c",
        "rollback owner",
        "Lab And CI Matrix",
        "local-only acceptable limits are approved today",
        "Remaining Roadmap Gaps",
        "samples/zigux/kprobe_example.zig",
        "samples/zigux/test_fsmount.zig",
    ]) + "\n")

    for rel_path in PLACEHOLDER_FILES:
        _write(root / rel_path, f"placeholder for {rel_path}\n")

    phase4_build_sha = _git_blob_sha1((root / "zigux/tests/phase4_build.zig").read_bytes())
    validator_sha = _git_blob_sha1((root / "scripts/zigux/validate-phase4.py").read_bytes())
    matrix_sha = _git_blob_sha1((root / "Documentation/zigux/phase4-validation-matrix.md").read_bytes())
    review_checklist_sha = _git_blob_sha1((root / "Documentation/zigux/review-checklist.md").read_bytes())
    phase9_build_sha = _git_blob_sha1((root / "zigux/tests/phase9_build.zig").read_bytes())
    manifest = {
        "phase4_build_blob_sha": phase4_build_sha,
        "phase4_validator_blob_sha": validator_sha,
        "phase4_validation_matrix_blob_sha": matrix_sha,
        "phase4_review_checklist_blob_sha": review_checklist_sha,
        "phase9_build_blob_sha": phase9_build_sha,
        "reversible_delivery_evidence": (
            "keep zigux/tests/atomic64_diff.zig, zigux/tests/runtime_atomic64_diff.zig, "
            "zigux/tests/phase4_build.zig, scripts/zigux/validate-phase4.py, "
            "Documentation/zigux/phase4-gate-evidence.md, Documentation/zigux/review-checklist.md, "
            "Documentation/zigux/phase4-validation-matrix.md, zigux/tests/phase4_perf_baseline_manifest.json, "
            "and zigux/tests/phase4_perf_baseline_survey.zig aligned."
        ),
    }
    _write(root / "zigux/tests/phase4_runtime_atomic64_diff_manifest.json", json.dumps(manifest, indent=2) + "\n")
    _write(root / "zigux/tests/phase4_runtime_atomic64_diff_survey.zig", "\n".join([
        'const std = @import("std");',
        'test "phase 4 atomic64 survey keeps wrapper handoff, owner map, and current local-only perf evidence explicit" {',
        "    _ = std.testing.allocator;",
        "}",
        'test "phase 4 atomic64 survey keeps the current roadmap gap summary reviewable" {',
        "    _ = std.testing.allocator;",
        "}",
        'test "phase 4 atomic64 survey keeps reversible delivery and next-step evidence explicit" {',
        "    _ = std.testing.allocator;",
        "}",
        "// Documentation/zigux/phase4-gate-evidence.md",
        "// Documentation/zigux/review-checklist.md",
        "// Documentation/zigux/phase4-validation-matrix.md",
        "// zigux/tests/phase4_perf_baseline_manifest.json",
        "// zigux/tests/phase4_perf_baseline_survey.zig",
        f"// {phase4_build_sha}",
        f"// {validator_sha}",
        f"// {matrix_sha}",
        f"// {review_checklist_sha}",
        f"// {phase9_build_sha}",
        "",
    ]))

    blob_targets = {
        "PHASE4_VALIDATOR_BLOB_SHA": "scripts/zigux/validate-phase4.py",
        "PHASE4_BUILD_BLOB_SHA": "zigux/tests/phase4_build.zig",
        "PHASE4_MAKEFILE_BLOB_SHA": "zigux/Makefile",
        "PHASE4_WORKFLOW_BLOB_SHA": ".github/workflows/zigux-bootstrap.yml",
        "PHASE4_DOC_README_BLOB_SHA": "Documentation/zigux/README.md",
        "PHASE4_SCRIPT_README_BLOB_SHA": "scripts/zigux/README.md",
        "PHASE4_TESTS_README_BLOB_SHA": "zigux/tests/README.md",
        "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA": "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
        "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA": "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    }
    lines = [
        "# Phase 4 Gate Evidence",
        "",
        "## Status",
        "- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`",
        "- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=21`",
        "- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,...`",
        "- `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`",
        "- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`",
        "- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`",
        "- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=16`",
        "- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=21`",
        "- `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`",
        "- `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`",
        "- `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`",
        "- `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`",
    ]
    for marker, rel_path in blob_targets.items():
        lines.append(f"- `{marker}={_git_blob_sha1((root / rel_path).read_bytes())}`")
    lines.extend([
        "",
        "## Current Conclusion",
        "- shared CI perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.",
    ])
    _write(root / "Documentation/zigux/phase4-gate-evidence.md", "\n".join(lines) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_validator_") as tempdir:
        root = Path(tempdir)
        _write_fixture_tree(root)
        failures = validate_root(root)
        if failures:
            print("PHASE4_VALIDATOR_SELF_TEST=fail")
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_START")
            for item in failures:
                print(item)
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_END")
            return 1

        gate_evidence_path = root / "Documentation/zigux/phase4-gate-evidence.md"
        original_gate_evidence = gate_evidence_path.read_text(encoding="utf-8")
        gate_evidence_path.write_text(
            original_gate_evidence.replace(
                "- `PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        failures = validate_root(root)
        if "gate_evidence:PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true" not in failures:
            print("PHASE4_VALIDATOR_SELF_TEST=fail")
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_START")
            for item in failures:
                print(item)
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_END")
            return 1
        gate_evidence_path.write_text(original_gate_evidence, encoding="utf-8")

        gate_evidence_path.write_text(
            original_gate_evidence.replace(
                "- `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        failures = validate_root(root)
        if "gate_evidence:PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true" not in failures:
            print("PHASE4_VALIDATOR_SELF_TEST=fail")
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_START")
            for item in failures:
                print(item)
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_END")
            return 1
        gate_evidence_path.write_text(original_gate_evidence, encoding="utf-8")

        gate_evidence_path.write_text(
            original_gate_evidence.replace(
                "- `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        failures = validate_root(root)
        if "gate_evidence:PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true" not in failures:
            print("PHASE4_VALIDATOR_SELF_TEST=fail")
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_START")
            for item in failures:
                print(item)
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_END")
            return 1
        gate_evidence_path.write_text(original_gate_evidence, encoding="utf-8")

        matrix_path = root / "Documentation/zigux/phase4-validation-matrix.md"
        original_matrix = matrix_path.read_text(encoding="utf-8")

        matrix_path.write_text(
            original_matrix.replace(
                "make -C zigux phase4-test-fsmount-survey\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        failures = validate_root(root)
        if "phase4_matrix:make -C zigux phase4-test-fsmount-survey" not in failures:
            print("PHASE4_VALIDATOR_SELF_TEST=fail")
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_START")
            for item in failures:
                print(item)
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_END")
            return 1

        matrix_path.write_text(
            original_matrix.replace(
                "reviewability_only_no_perf_threshold",
                "shared_ci_perf_promoted",
                1,
            ),
            encoding="utf-8",
        )
        failures = validate_root(root)
        if "phase4_matrix:reviewability_only_no_perf_threshold" not in failures:
            print("PHASE4_VALIDATOR_SELF_TEST=fail")
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_START")
            for item in failures:
                print(item)
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_END")
            return 1
        matrix_path.write_text(original_matrix, encoding="utf-8")

        matrix_path.write_text(
            original_matrix.replace(
                "`local_only_commands_and_limits_approved_shared_ci_perf_promotion_pending`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        failures = validate_root(root)
        if "phase4_perf_baseline_matrix:`local_only_commands_and_limits_approved_shared_ci_perf_promotion_pending`" not in failures:
            print("PHASE4_VALIDATOR_SELF_TEST=fail")
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_START")
            for item in failures:
                print(item)
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_END")
            return 1
        matrix_path.write_text(original_matrix, encoding="utf-8")

        review_checklist_path = root / "Documentation/zigux/review-checklist.md"
        original_review_checklist = review_checklist_path.read_text(encoding="utf-8")
        review_checklist_path.write_text(
            original_review_checklist.replace(
                "zigux/tests/phase4_bitmap_live_helper_replay.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        failures = validate_root(root)
        if "review_checklist:zigux/tests/phase4_bitmap_live_helper_replay.zig" not in failures:
            print("PHASE4_VALIDATOR_SELF_TEST=fail")
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_START")
            for item in failures:
                print(item)
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_END")
            return 1
        review_checklist_path.write_text(original_review_checklist, encoding="utf-8")

        scripts_readme_path = root / "scripts/zigux/README.md"
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "Documentation/zigux/phase4-kprobe-example-gap-survey.md\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        failures = validate_root(root)
        if "script_readme:Documentation/zigux/phase4-kprobe-example-gap-survey.md" not in failures:
            print("PHASE4_VALIDATOR_SELF_TEST=fail")
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_START")
            for item in failures:
                print(item)
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_END")
            return 1
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "make -C zigux phase4-test-fsmount-survey\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        failures = validate_root(root)
        if "script_readme:make -C zigux phase4-test-fsmount-survey" not in failures:
            print("PHASE4_VALIDATOR_SELF_TEST=fail")
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_START")
            for item in failures:
                print(item)
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_END")
            return 1
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        remaining_gap_checker_path = root / "scripts/zigux/check-phase4-remaining-gap-matrix.py"
        original_remaining_gap_checker = remaining_gap_checker_path.read_text(encoding="utf-8")
        remaining_gap_checker_path.write_text(
            "#!/usr/bin/env python3\nprint('PHASE4_REMAINING_GAP_MATRIX_CHECK=pass')\n",
            encoding="utf-8",
        )
        failures = validate_root(root)
        if "PHASE4_REMAINING_GAP_MATRIX_SELF_TEST_CHECK:missing_pass_marker" not in failures:
            print("PHASE4_VALIDATOR_SELF_TEST=fail")
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_START")
            for item in failures:
                print(item)
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_END")
            return 1
        remaining_gap_checker_path.write_text(original_remaining_gap_checker, encoding="utf-8")

        makefile_path = root / "zigux/Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "phase4-runtime-atomic64-diff:\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        failures = validate_root(root)
        if "make:phase4-runtime-atomic64-diff:" not in failures:
            print("PHASE4_VALIDATOR_SELF_TEST=fail")
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_START")
            for item in failures:
                print(item)
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_END")
            return 1
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "$(ZIG) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
                "$(ZIG) build phase4-bitmap-diff-drifted --build-file zigux/tests/phase4_build.zig",
                1,
            ),
            encoding="utf-8",
        )
        failures = validate_root(root)
        if "make:$(ZIG) build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig" not in failures:
            print("PHASE4_VALIDATOR_SELF_TEST=fail")
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_START")
            for item in failures:
                print(item)
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_END")
            return 1
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "phase4-bitmap-live-helper-replay:\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        failures = validate_root(root)
        if "make:phase4-bitmap-live-helper-replay:" not in failures:
            print("PHASE4_VALIDATOR_SELF_TEST=fail")
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_START")
            for item in failures:
                print(item)
            print("PHASE4_VALIDATOR_SELF_TEST_FAILURES_END")
            return 1
    print("PHASE4_VALIDATOR_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the shared Phase 4 rollback-readiness packet.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated validator coverage in a temporary workspace.")
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

    failures = validate_root(ROOT)
    if failures:
        print("PHASE4_VALIDATION=fail")
        print("PHASE4_VALIDATION_FAILURES_START")
        for item in failures:
            print(item)
        print("PHASE4_VALIDATION_FAILURES_END")
        return 1

    print("PHASE4_VALIDATION=pass")
    print(f"PHASE4_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE4_REQUIRED_MARKER_COUNT={required_marker_count()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
