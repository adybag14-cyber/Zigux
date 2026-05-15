#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT = 33
PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT = 19
PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT = 33
PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE = (
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,shipped_target_count_drift,"
    "missing_exact_readback_heading,validator_blob_pin_drift,phase4_build_manifest_blob_pin_drift,"
    "phase4_build_survey_blob_pin_drift,phase9_build_manifest_blob_pin_drift,phase9_build_survey_blob_pin_drift,"
    "doc_readme_blob_pin_drift,script_readme_blob_pin_drift,tests_readme_blob_pin_drift,"
    "gate_evidence_self_test_case_count_drift,gate_evidence_self_test_cases_drift,"
    "shared_validator_reruns_gate_evidence_self_test_drift,shared_validator_expected_target_count_drift,"
    "shared_validator_expected_self_test_case_count_drift,runtime_atomic64_survey_packet_presence_drift,"
    "bitmap_diff_survey_replay_marker_drift,kprobe_gap_packet_presence_drift,kprobe_owner_drift,"
    "kprobe_validation_entrypoint_drift,kprobe_next_step_drift,perf_baseline_packet_presence_drift,"
    "perf_baseline_note_split_marker_drift,perf_baseline_owner_drift,"
    "perf_baseline_shared_promotion_status_drift,test_fsmount_gap_packet_presence_drift,"
    "test_fsmount_threshold_posture_drift,test_fsmount_owner_drift,test_fsmount_validation_entrypoint_drift,"
    "test_fsmount_linux_style_wrapper_drift,test_fsmount_next_step_drift,missing_note_file"
)

EXPECTED_GATE_EVIDENCE_LINES = [
    f"- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}`",
    f"- `{PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE}`",
    (
        "- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT="
        f"{PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT}`"
    ),
    (
        "- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="
        f"{PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}`"
    ),
]

EXPECTED_VALIDATOR_MARKERS = [
    f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT = {PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}",
    (
        "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT = "
        f"{PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT}"
    ),
    (
        "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT = "
        f"{PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}"
    ),
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE = (",
    f'    f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={{PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}}"',
    "    PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE,",
    (
        "    f\"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT="
        "{PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT}\""
    ),
    (
        "    f\"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="
        "{PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}\""
    ),
]

FORBIDDEN_VALIDATOR_MARKERS = [
    '    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",',
    '    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=",',
    '    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=",',
    '    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",',
    '        "- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=21`",',
    '        "- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,...`",',
    '        "- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=16`",',
    '        "- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=21`",',
]


def check_validator_text(validator_text: str) -> list[str]:
    failures: list[str] = []
    for marker in EXPECTED_VALIDATOR_MARKERS:
        if marker not in validator_text:
            failures.append(f"validator:missing_exact_marker:{marker}")
    for marker in FORBIDDEN_VALIDATOR_MARKERS:
        if marker in validator_text:
            failures.append(f"validator:stale_prefix_marker:{marker}")
    return failures


def check_gate_evidence_text(gate_evidence_text: str) -> list[str]:
    failures: list[str] = []
    for marker in EXPECTED_GATE_EVIDENCE_LINES:
        if marker not in gate_evidence_text:
            failures.append(f"gate_evidence:missing_exact_marker:{marker}")
    return failures


def validate_root(root: Path) -> list[str]:
    validator_path = root / "scripts/zigux/validate-phase4.py"
    gate_evidence_path = root / "Documentation/zigux/phase4-gate-evidence.md"
    failures: list[str] = []

    if not validator_path.exists():
        failures.append(f"validator:missing_file:{validator_path}")
    if not gate_evidence_path.exists():
        failures.append(f"gate_evidence:missing_file:{gate_evidence_path}")
    if failures:
        return failures

    failures.extend(check_validator_text(validator_path.read_text(encoding="utf-8")))
    failures.extend(check_gate_evidence_text(gate_evidence_path.read_text(encoding="utf-8")))
    return failures


def write_fixture_root(root: Path) -> None:
    validator_path = root / "scripts/zigux/validate-phase4.py"
    validator_path.parent.mkdir(parents=True, exist_ok=True)
    validator_path.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT = {PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}",
                (
                    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT = "
                    f"{PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT}"
                ),
                (
                    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT = "
                    f"{PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}"
                ),
                "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE = (",
                f'    "{PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE}"',
                ")",
                "REQUIRED_GATE_EVIDENCE_MARKERS = [",
                '    f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}"',
                "    PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE,",
                (
                    "    f\"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT="
                    "{PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT}\""
                ),
                (
                    "    f\"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="
                    "{PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}\""
                ),
                "]",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    gate_evidence_path = root / "Documentation/zigux/phase4-gate-evidence.md"
    gate_evidence_path.parent.mkdir(parents=True, exist_ok=True)
    gate_evidence_path.write_text(
        "\n".join(
            [
                "# Phase 4 Gate Evidence",
                *EXPECTED_GATE_EVIDENCE_LINES,
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase4-validator-gate-evidence-exactness-") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_root(root)

        baseline_failures = validate_root(root)
        if baseline_failures:
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_SELF_TEST=fail")
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_FAILURES_START")
            for failure in baseline_failures:
                print(failure)
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_FAILURES_END")
            return 1

        validator_path = root / "scripts/zigux/validate-phase4.py"
        gate_evidence_path = root / "Documentation/zigux/phase4-gate-evidence.md"
        original_validator = validator_path.read_text(encoding="utf-8")
        original_gate_evidence = gate_evidence_path.read_text(encoding="utf-8")

        validator_path.write_text(
            original_validator.replace(
                '    f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}"',
                '    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT="',
                1,
            ),
            encoding="utf-8",
        )
        failures = validate_root(root)
        if not any(
            failure == 'validator:stale_prefix_marker:    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",'
            or failure.startswith("validator:missing_exact_marker:")
            for failure in failures
        ):
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_SELF_TEST=fail")
            print("EXPECTED_PREFIX_ONLY_VALIDATOR_DRIFT")
            return 1
        validator_path.write_text(original_validator, encoding="utf-8")

        gate_evidence_path.write_text(
            original_gate_evidence.replace(
                f"- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}`",
                f"- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT - 1}`",
                1,
            ),
            encoding="utf-8",
        )
        failures = validate_root(root)
        if (
            "gate_evidence:missing_exact_marker:"
            f"- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}`"
            not in failures
        ):
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_SELF_TEST=fail")
            print("EXPECTED_GATE_EVIDENCE_COUNT_DRIFT")
            return 1
        gate_evidence_path.write_text(original_gate_evidence, encoding="utf-8")

        gate_evidence_path.write_text(
            original_gate_evidence.replace(
                f"- `{PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE}`",
                "- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip`",
                1,
            ),
            encoding="utf-8",
        )
        failures = validate_root(root)
        if (
            "gate_evidence:missing_exact_marker:" f"- `{PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE}`"
            not in failures
        ):
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_SELF_TEST=fail")
            print("EXPECTED_GATE_EVIDENCE_CASES_DRIFT")
            return 1

    print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail closed when scripts/zigux/validate-phase4.py drifts away from the exact "
            "Phase 4 gate-evidence case counts and shipped self-test catalog."
        )
    )
    parser.add_argument(
        "repo_root",
        nargs="?",
        default=".",
        help="Path to the Zigux repository root. Defaults to the current directory.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run focused checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    failures = validate_root(Path(args.repo_root).resolve())
    if failures:
        print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_CHECK=fail")
        print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_FAILURES_END")
        return 1

    print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
