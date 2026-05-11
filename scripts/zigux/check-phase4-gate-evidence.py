#!/usr/bin/env python3
"""Validate the current Phase 4 exact-readback evidence note."""

from __future__ import annotations

import argparse
import hashlib
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
GATE_EVIDENCE_REL = Path("Documentation/zigux/phase4-gate-evidence.md")
EXPECTED_SHIPPED_TARGET_COUNT = 16
EXPECTED_SELF_TEST_CASE_COUNT = 21
SELF_TEST_CASES = [
    "baseline_round_trip",
    "shipped_target_count_drift",
    "missing_exact_readback_heading",
    "validator_blob_pin_drift",
    "phase4_build_manifest_blob_pin_drift",
    "phase4_build_survey_blob_pin_drift",
    "phase9_build_manifest_blob_pin_drift",
    "phase9_build_survey_blob_pin_drift",
    "gate_evidence_self_test_case_count_drift",
    "gate_evidence_self_test_cases_drift",
    "shared_validator_reruns_gate_evidence_self_test_drift",
    "shared_validator_expected_target_count_drift",
    "shared_validator_expected_self_test_case_count_drift",
    "bitmap_diff_survey_replay_marker_drift",
    "kprobe_gap_packet_presence_drift",
    "perf_baseline_packet_presence_drift",
    "perf_baseline_note_split_marker_drift",
    "perf_baseline_owner_drift",
    "perf_baseline_shared_promotion_status_drift",
    "test_fsmount_gap_packet_presence_drift",
    "missing_note_file",
]
SELF_TEST_CASES_LINE = (
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES)
)

REQUIRED_STATUS_MARKERS = [
    "PHASE4_EVIDENCE_DATE=",
    "PHASE4_EVIDENCE_MODE=github_connector_readback",
    "PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions",
    "PHASE4_EXACT_READBACK_REF=master",
    "PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=",
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=",
    "PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true",
    "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true",
    "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",
    "PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true",
    "PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true",
    "PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true",
]

EXACT_STATUS_LINES = [
    "PHASE4_EXACT_READBACK_REF=master",
    f"PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}",
    f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}",
    SELF_TEST_CASES_LINE,
    "PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true",
    "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true",
    "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true",
    f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}",
    (
        "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="
        f"{EXPECTED_SELF_TEST_CASE_COUNT}"
    ),
    "PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true",
    "PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true",
    "PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true",
]

REQUIRED_PROSE_MARKERS = [
    "## Exact Readback Evidence",
    "## Current Conclusion",
    "`scripts/zigux/check-phase4-gate-evidence.py` remains the dedicated exact-readback checker for this narrower rollback-ownership packet.",
    "`zigux/tests/phase4_perf_baseline_manifest.json` and `zigux/tests/phase4_perf_baseline_survey.zig` also remain shipped on `master` as the dedicated local-only perf-baseline posture packet",
    "shared CI perf coverage stays out of scope.",
    "Validation and Perf Team stays named as the decision owner",
    "phase4-bitmap-live-helper-replay-tests",
    "shared CI perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.",
]

REQUIRED_SELF_TEST_CASE_MARKERS = [
    "baseline_round_trip",
    "shipped_target_count_drift",
    "validator_blob_pin_drift",
    "phase4_build_manifest_blob_pin_drift",
    "phase4_build_survey_blob_pin_drift",
    "missing_note_file",
]

BLOB_TARGETS = {
    "PHASE4_VALIDATION_MATRIX_BLOB_SHA": "Documentation/zigux/phase4-validation-matrix.md",
    "PHASE4_VALIDATOR_BLOB_SHA": "scripts/zigux/validate-phase4.py",
    "PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA": "scripts/zigux/check-phase4-gate-evidence.py",
    "PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA": "scripts/zigux/check-phase4-workflow-route-counts.py",
    "PHASE4_ARTIFACT_DIFF_DOC_BLOB_SHA": "Documentation/zigux/artifact-diff.md",
    "PHASE4_ARTIFACT_DIFF_CONTRACT_CHECKER_BLOB_SHA": "scripts/zigux/check-artifact-diff-contract.py",
    "PHASE4_BUILD_BLOB_SHA": "zigux/tests/phase4_build.zig",
    "PHASE4_MAKEFILE_BLOB_SHA": "zigux/Makefile",
    "PHASE4_WORKFLOW_BLOB_SHA": ".github/workflows/zigux-bootstrap.yml",
    "PHASE4_DOC_README_BLOB_SHA": "Documentation/zigux/README.md",
    "PHASE4_SCRIPT_README_BLOB_SHA": "scripts/zigux/README.md",
    "PHASE4_TESTS_README_BLOB_SHA": "zigux/tests/README.md",
    "PHASE4_ATOMIC64_DIFF_BLOB_SHA": "zigux/tests/atomic64_diff.zig",
    "PHASE4_RUNTIME_ATOMIC64_DIFF_BLOB_SHA": "zigux/tests/runtime_atomic64_diff.zig",
    "PHASE4_BITMAP_DIFF_BLOB_SHA": "zigux/tests/bitmap_diff.zig",
    "PHASE4_BITMAP_LIVE_HELPER_REPLAY_BLOB_SHA": "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA": "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA": "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA": "Documentation/zigux/review-checklist.md",
}


def git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("utf-8")
    return hashlib.sha1(header + payload).hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def exact_status_line_count(text: str, status_line: str) -> int:
    return sum(1 for line in text.splitlines() if line == f"- `{status_line}`")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing marker: {old}")
    return text.replace(old, new, 1)


def validate_root(root: Path) -> list[str]:
    gate_evidence_path = root / GATE_EVIDENCE_REL
    if not gate_evidence_path.exists():
        return [f"file:{GATE_EVIDENCE_REL.as_posix()}"]

    text = read_text(gate_evidence_path)
    failures: list[str] = []

    for marker in REQUIRED_STATUS_MARKERS:
        if marker not in text:
            failures.append(f"missing_status_marker:{marker}")

    for status_line in EXACT_STATUS_LINES:
        count = exact_status_line_count(text, status_line)
        if count != 1:
            failures.append(f"status_exact_count:{status_line}:{count}")

    for marker in REQUIRED_PROSE_MARKERS:
        if marker not in text:
            failures.append(f"missing_prose_marker:{marker}")

    for marker in REQUIRED_SELF_TEST_CASE_MARKERS:
        if marker not in text:
            failures.append(f"missing_self_test_case:{marker}")

    for key, relative_path in BLOB_TARGETS.items():
        target = root / relative_path
        if not target.exists():
            failures.append(f"file:{relative_path}")
            continue
        digest = git_blob_sha1(target.read_bytes())
        marker = f"- `{key}={digest}`"
        if marker not in text:
            failures.append(f"blob_pin_mismatch:{key}:{digest}")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_tree(root: Path) -> None:
    for relative_path in BLOB_TARGETS.values():
        write_text(root / relative_path, f"fixture for {relative_path}\n")

    blob_pin_lines = [
        f"- `{key}={git_blob_sha1((root / relative_path).read_bytes())}`"
        for key, relative_path in BLOB_TARGETS.items()
    ]

    gate_evidence = "\n".join(
        [
            "# Phase 4 Gate Evidence",
            "",
            "## Status",
            "- `PHASE4_EVIDENCE_DATE=2026-05-11`",
            "- `PHASE4_EVIDENCE_MODE=github_connector_readback`",
            "- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`",
            "- `PHASE4_EXACT_READBACK_REF=master`",
            *blob_pin_lines,
            f"- `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}`",
            f"- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}`",
            f"- `{SELF_TEST_CASES_LINE}`",
            "- `PHASE4_SEPARATE_GATE_EVIDENCE_CHECKER_PRESENT=true`",
            "- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true`",
            "- `PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true`",
            f"- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}`",
            (
                "- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="
                f"{EXPECTED_SELF_TEST_CASE_COUNT}`"
            ),
            "- `PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true`",
            "- `PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true`",
            "- `PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true`",
            "",
            "## Exact Readback Evidence",
            "- `scripts/zigux/check-phase4-gate-evidence.py` remains the dedicated exact-readback checker for this narrower rollback-ownership packet.",
            "- `zigux/tests/phase4_perf_baseline_manifest.json` and `zigux/tests/phase4_perf_baseline_survey.zig` also remain shipped on `master` as the dedicated local-only perf-baseline posture packet while shared CI perf coverage stays out of scope.",
            "- `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` remain the manifest-backed runtime atomic64 survey pair, and `phase4-runtime-atomic64-diff-survey-tests` plus `phase4-bitmap-live-helper-replay-tests` stay wired through the shared Phase 4 build entrypoint.",
            "",
            "## Current Conclusion",
            "- shared CI perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.",
            "- `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `Documentation/zigux/phase4-validation-matrix.md` now all mirror that local-only split and the current decision-owner packet: the Validation and Perf Team stays named as the decision owner for any broader shared-CI perf promotion, while the ABI and Runtime Team plus Shared Subsystems Pod stay named as coordination owners for that policy call.",
        ]
    )
    write_text(root / GATE_EVIDENCE_REL, gate_evidence + "\n")


def expect_failure(
    root: Path,
    gate_evidence_path: Path,
    description: str,
    *,
    exact_failure: str | None = None,
    prefix_failure: str | None = None,
) -> bool:
    failures = validate_root(root)
    if exact_failure is not None and exact_failure not in failures:
        print("PHASE4_GATE_EVIDENCE_SELF_TEST=fail")
        print(f"expected {description} failure: {exact_failure}")
        print("\n".join(failures))
        return False
    if prefix_failure is not None and not any(
        entry.startswith(prefix_failure) for entry in failures
    ):
        print("PHASE4_GATE_EVIDENCE_SELF_TEST=fail")
        print(f"expected {description} failure prefix: {prefix_failure}")
        print("\n".join(failures))
        return False
    return True


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_gate_evidence_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_tree(root)
        gate_evidence_path = root / GATE_EVIDENCE_REL
        original_note = read_text(gate_evidence_path)

        failures = validate_root(root)
        if failures:
            print("PHASE4_GATE_EVIDENCE_SELF_TEST=fail")
            print("\n".join(failures))
            return 1
        case_count += 1

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                f"PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}",
                f"PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT - 1}",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "shipped target count drift",
            exact_failure=(
                "status_exact_count:"
                f"PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}:0"
            ),
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(original_note, "## Exact Readback Evidence", "## Readback Evidence"),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "exact readback heading drift",
            exact_failure="missing_prose_marker:## Exact Readback Evidence",
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        validator_path = root / "scripts/zigux/validate-phase4.py"
        original_validator = read_text(validator_path)
        validator_path.write_text("drifted validator fixture\n", encoding="utf-8")
        if not expect_failure(
            root,
            gate_evidence_path,
            "validator blob pin drift",
            prefix_failure="blob_pin_mismatch:PHASE4_VALIDATOR_BLOB_SHA:",
        ):
            return 1
        case_count += 1
        validator_path.write_text(original_validator, encoding="utf-8")

        manifest_path = root / "zigux/tests/phase4_runtime_atomic64_diff_manifest.json"
        original_manifest = read_text(manifest_path)
        manifest_path.write_text("manifest drift\n", encoding="utf-8")
        if not expect_failure(
            root,
            gate_evidence_path,
            "runtime manifest blob drift",
            prefix_failure="blob_pin_mismatch:PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA:",
        ):
            return 1
        case_count += 1
        manifest_path.write_text(original_manifest, encoding="utf-8")

        survey_path = root / "zigux/tests/phase4_runtime_atomic64_diff_survey.zig"
        original_survey = read_text(survey_path)
        survey_path.write_text("survey drift\n", encoding="utf-8")
        if not expect_failure(
            root,
            gate_evidence_path,
            "runtime survey blob drift",
            prefix_failure="blob_pin_mismatch:PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA:",
        ):
            return 1
        case_count += 1
        survey_path.write_text(original_survey, encoding="utf-8")

        build_path = root / "zigux/tests/phase4_build.zig"
        original_build = read_text(build_path)
        build_path.write_text("phase4 build drift\n", encoding="utf-8")
        if not expect_failure(
            root,
            gate_evidence_path,
            "phase4 build blob drift",
            prefix_failure="blob_pin_mismatch:PHASE4_BUILD_BLOB_SHA:",
        ):
            return 1
        case_count += 1
        build_path.write_text(original_build, encoding="utf-8")

        checklist_path = root / "Documentation/zigux/review-checklist.md"
        original_checklist = read_text(checklist_path)
        checklist_path.write_text("review checklist drift\n", encoding="utf-8")
        if not expect_failure(
            root,
            gate_evidence_path,
            "review checklist blob drift",
            prefix_failure="blob_pin_mismatch:PHASE4_RUNTIME_ATOMIC64_REVIEW_CHECKLIST_BLOB_SHA:",
        ):
            return 1
        case_count += 1
        checklist_path.write_text(original_checklist, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}",
                f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT - 1}",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "self-test count drift",
            exact_failure=(
                "status_exact_count:"
                f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}:0"
            ),
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                SELF_TEST_CASES_LINE,
                SELF_TEST_CASES_LINE.replace(
                    "missing_note_file", "missing_note_file_drifted", 1
                ),
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "self-test case catalog drift",
            exact_failure=f"status_exact_count:{SELF_TEST_CASES_LINE}:0",
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true",
                "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=false",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "shared validator rerun self-test drift",
            exact_failure=(
                "status_exact_count:PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_SELF_TEST=true:0"
            ),
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}",
                f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT - 1}",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "shared validator expected target count drift",
            exact_failure=(
                "status_exact_count:"
                f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}:0"
            ),
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                (
                    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="
                    f"{EXPECTED_SELF_TEST_CASE_COUNT}"
                ),
                (
                    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="
                    f"{EXPECTED_SELF_TEST_CASE_COUNT - 1}"
                ),
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "shared validator expected self-test count drift",
            exact_failure=(
                "status_exact_count:"
                "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="
                f"{EXPECTED_SELF_TEST_CASE_COUNT}:0"
            ),
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                "phase4-bitmap-live-helper-replay-tests",
                "phase4-bitmap-live-helper-replay-drift",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "bitmap replay marker drift",
            exact_failure="missing_prose_marker:phase4-bitmap-live-helper-replay-tests",
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                "PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true",
                "PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=false",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "kprobe packet presence drift",
            exact_failure="status_exact_count:PHASE4_SHARED_KPROBE_SURVEY_PACKET_PRESENT=true:0",
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                "PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true",
                "PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=false",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "perf baseline packet presence drift",
            exact_failure=(
                "status_exact_count:PHASE4_SHARED_PERF_BASELINE_SURVEY_PACKET_PRESENT=true:0"
            ),
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                "shared CI perf coverage stays out of scope.",
                "shared CI perf coverage is promoted here.",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "perf baseline split-marker drift",
            exact_failure="missing_prose_marker:shared CI perf coverage stays out of scope.",
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                "Validation and Perf Team stays named as the decision owner",
                "Tooling and Validation Team stays named as the decision owner",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "perf baseline owner drift",
            exact_failure=(
                "missing_prose_marker:Validation and Perf Team stays named as the decision owner"
            ),
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                "shared CI perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.",
                "shared CI perf thresholds for the shipped atomic64 and bitmap rollback gates are promoted.",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "shared perf promotion status drift",
            exact_failure=(
                "missing_prose_marker:shared CI perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved."
            ),
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.write_text(
            replace_once(
                original_note,
                "PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true",
                "PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=false",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            gate_evidence_path,
            "test_fsmount packet presence drift",
            exact_failure=(
                "status_exact_count:PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true:0"
            ),
        ):
            return 1
        case_count += 1
        gate_evidence_path.write_text(original_note, encoding="utf-8")

        gate_evidence_path.unlink()
        if not expect_failure(
            root,
            gate_evidence_path,
            "missing note",
            exact_failure=f"file:{GATE_EVIDENCE_REL.as_posix()}",
        ):
            return 1
        case_count += 1

    if case_count != EXPECTED_SELF_TEST_CASE_COUNT:
        print("PHASE4_GATE_EVIDENCE_SELF_TEST=fail")
        print(
            "unexpected self-test case count "
            f"{case_count} != {EXPECTED_SELF_TEST_CASE_COUNT}"
        )
        return 1

    print("PHASE4_GATE_EVIDENCE_SELF_TEST=pass")
    print(f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 4 gate-evidence note."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in coverage checks in a temporary workspace.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate_root(ROOT)
    if failures:
        print("PHASE4_GATE_EVIDENCE_CHECK=fail")
        print("MISSING_PHASE4_GATE_EVIDENCE_MARKERS_START")
        for item in failures:
            print(item)
        print("MISSING_PHASE4_GATE_EVIDENCE_MARKERS_END")
        return 1

    print("PHASE4_GATE_EVIDENCE_CHECK=pass")
    print(f"PHASE4_GATE_EVIDENCE_BLOB_PIN_COUNT={len(BLOB_TARGETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
