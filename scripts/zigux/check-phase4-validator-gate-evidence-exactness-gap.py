#!/usr/bin/env python3
"""Check that the current Phase 4 validator exactness gap stays explicitly bounded."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent

VALIDATOR_REL = Path("scripts/zigux/validate-phase4.py")
GATE_EVIDENCE_REL = Path("Documentation/zigux/phase4-gate-evidence.md")
GATE_CHECKER_REL = Path("scripts/zigux/check-phase4-gate-evidence.py")

EXPECTED_SELF_TEST_CASE_COUNT = 33
EXPECTED_SHIPPED_TARGET_COUNT = 19
SELF_TEST_CASES = [
    "baseline_round_trip",
    "shipped_target_count_drift",
    "missing_exact_readback_heading",
    "validator_blob_pin_drift",
    "phase4_build_manifest_blob_pin_drift",
    "phase4_build_survey_blob_pin_drift",
    "phase9_build_manifest_blob_pin_drift",
    "phase9_build_survey_blob_pin_drift",
    "doc_readme_blob_pin_drift",
    "script_readme_blob_pin_drift",
    "tests_readme_blob_pin_drift",
    "gate_evidence_self_test_case_count_drift",
    "gate_evidence_self_test_cases_drift",
    "shared_validator_reruns_gate_evidence_self_test_drift",
    "shared_validator_expected_target_count_drift",
    "shared_validator_expected_self_test_case_count_drift",
    "runtime_atomic64_survey_packet_presence_drift",
    "bitmap_diff_survey_replay_marker_drift",
    "kprobe_gap_packet_presence_drift",
    "kprobe_owner_drift",
    "kprobe_validation_entrypoint_drift",
    "kprobe_next_step_drift",
    "perf_baseline_packet_presence_drift",
    "perf_baseline_note_split_marker_drift",
    "perf_baseline_owner_drift",
    "perf_baseline_shared_promotion_status_drift",
    "test_fsmount_gap_packet_presence_drift",
    "test_fsmount_threshold_posture_drift",
    "test_fsmount_owner_drift",
    "test_fsmount_validation_entrypoint_drift",
    "test_fsmount_linux_style_wrapper_drift",
    "test_fsmount_next_step_drift",
    "missing_note_file",
]
SELF_TEST_CASES_LINE = "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES)

VALIDATOR_PREFIX_MARKERS = [
    '"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",',
    '"PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=",',
    '"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=",',
    '"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",',
]

EXACT_NOTE_LINES = [
    f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}",
    SELF_TEST_CASES_LINE,
    f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}",
    (
        "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="
        f"{EXPECTED_SELF_TEST_CASE_COUNT}"
    ),
]

EXACT_CHECKER_MARKERS = [
    f"EXPECTED_SHIPPED_TARGET_COUNT = {EXPECTED_SHIPPED_TARGET_COUNT}",
    f"EXPECTED_SELF_TEST_CASE_COUNT = {EXPECTED_SELF_TEST_CASE_COUNT}",
    "SELF_TEST_CASES = [",
    '"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}"',
    'f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}"',
    '"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="',
    'f"{EXPECTED_SELF_TEST_CASE_COUNT}"',
]


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def validate_root(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in (VALIDATOR_REL, GATE_EVIDENCE_REL, GATE_CHECKER_REL):
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel.as_posix()}")

    if failures:
        return failures

    validator_text = read_text(root, VALIDATOR_REL)
    note_text = read_text(root, GATE_EVIDENCE_REL)
    checker_text = read_text(root, GATE_CHECKER_REL)

    for marker in VALIDATOR_PREFIX_MARKERS:
        if marker not in validator_text:
            failures.append(f"validator_prefix:{marker}")

    for line in EXACT_NOTE_LINES:
        if f"- `{line}`" not in note_text:
            failures.append(f"gate_evidence:{line}")

    for marker in EXACT_CHECKER_MARKERS:
        if marker not in checker_text:
            failures.append(f"gate_checker:{marker}")

    return failures


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _baseline_validator() -> str:
    return (
        "REQUIRED_GATE_EVIDENCE_MARKERS = [\n"
        '    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",\n'
        '    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=",\n'
        '    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=",\n'
        '    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",\n'
        "]\n"
    )


def _baseline_note() -> str:
    lines = "\n".join(f"- `{line}`" for line in EXACT_NOTE_LINES)
    return "## Exact Readback Evidence\n" + lines + "\n"


def _baseline_checker() -> str:
    return (
        f"EXPECTED_SHIPPED_TARGET_COUNT = {EXPECTED_SHIPPED_TARGET_COUNT}\n"
        f"EXPECTED_SELF_TEST_CASE_COUNT = {EXPECTED_SELF_TEST_CASE_COUNT}\n"
        "SELF_TEST_CASES = [\n"
        '    "baseline_round_trip",\n'
        "]\n"
        'line_a = f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}"\n'
        'line_b = f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}"\n'
        'line_c = (\n'
        '    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="\n'
        '    f"{EXPECTED_SELF_TEST_CASE_COUNT}"\n'
        ')\n'
    )


def self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        _write(root / VALIDATOR_REL, _baseline_validator())
        _write(root / GATE_EVIDENCE_REL, _baseline_note())
        _write(root / GATE_CHECKER_REL, _baseline_checker())

        failures = validate_root(root)
        if failures:
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST=fail")
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST_FAILURES_START")
            for item in failures:
                print(item)
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST_FAILURES_END")
            return 1

        validator_path = root / VALIDATOR_REL
        note_path = root / GATE_EVIDENCE_REL
        checker_path = root / GATE_CHECKER_REL
        original_validator = validator_path.read_text(encoding="utf-8")
        original_note = note_path.read_text(encoding="utf-8")
        original_checker = checker_path.read_text(encoding="utf-8")

        validator_path.write_text(
            original_validator.replace(
                '"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",\n',
                '"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=33",\n',
                1,
            ),
            encoding="utf-8",
        )
        failures = validate_root(root)
        if 'validator_prefix:"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",' not in failures:
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST=fail")
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST_FAILURES_START")
            for item in failures:
                print(item)
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST_FAILURES_END")
            return 1
        validator_path.write_text(original_validator, encoding="utf-8")

        note_path.write_text(
            original_note.replace(
                f"- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={EXPECTED_SHIPPED_TARGET_COUNT}`",
                "- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=18`",
                1,
            ),
            encoding="utf-8",
        )
        failures = validate_root(root)
        if (
            "gate_evidence:PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT="
            f"{EXPECTED_SHIPPED_TARGET_COUNT}"
            not in failures
        ):
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST=fail")
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST_FAILURES_START")
            for item in failures:
                print(item)
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST_FAILURES_END")
            return 1
        note_path.write_text(original_note, encoding="utf-8")

        checker_path.write_text(
            original_checker.replace(
                f"EXPECTED_SELF_TEST_CASE_COUNT = {EXPECTED_SELF_TEST_CASE_COUNT}",
                "EXPECTED_SELF_TEST_CASE_COUNT = 32",
                1,
            ),
            encoding="utf-8",
        )
        failures = validate_root(root)
        if f"gate_checker:EXPECTED_SELF_TEST_CASE_COUNT = {EXPECTED_SELF_TEST_CASE_COUNT}" not in failures:
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST=fail")
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST_FAILURES_START")
            for item in failures:
                print(item)
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST_FAILURES_END")
            return 1
        checker_path.write_text(original_checker, encoding="utf-8")

    print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    failures = validate_root(args.root)
    if failures:
        print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_CHECK=fail")
        print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_FAILURES_START")
        for item in failures:
            print(item)
        print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_FAILURES_END")
        return 1

    print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
