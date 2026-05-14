#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTE_PATH = ROOT / "Documentation" / "zigux" / "artifact-diff.md"

REQUIRED_MARKERS = [
    "- deterministic helper contract: `ARTIFACT_DIFF_RESULT_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL[,SHA256|EXPECTED_EXISTS|ACTUAL_EXISTS|EXPECTED_JSON_ERROR|ACTUAL_JSON_ERROR]`",
    "- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_JSON_INVALID` must prove malformed JSON fails without inventing digest or exists markers",
    "- `python3 scripts/zigux/artifact_diff.py --self-test` is the direct helper replay and must emit `ARTIFACT_DIFF_SELF_TEST=pass`, `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=19`, and this exact case packet: `text_pass`, `text_mismatch`, `json_pass`, `json_mismatch`, `json_invalid_expected`, `json_invalid_actual`, `json_invalid_both`, `json_missing_expected`, `json_missing_actual`, `json_missing_both`, `sha256_pass`, `sha256_drift`, `text_missing_expected`, `text_missing_actual`, `text_missing_both`, `sha256_missing_expected`, `sha256_missing_actual`, `sha256_missing_both`, and `invalid_mode_rejected`.",
    "- `python3 scripts/zigux/check-artifact-diff-contract.py --self-test` is the isolated checker replay and must emit `ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass`, `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24`, and this exact self-test packet: `catalog_shape`, `review_note_marker_round_trip`, `review_note_owner_marker_drift`, `review_note_marker_drift`, `cli_help_round_trip`, `cli_help_line_drift`, `cli_missing_argument_parser_round_trip`, `cli_missing_argument_parser_stderr_drift`, `cli_invalid_mode_parser_round_trip`, `cli_invalid_mode_parser_stderr_drift`, `helper_summary_round_trip`, `contract_summary_round_trip`, `helper_summary_status_drift`, `helper_summary_count_drift`, `helper_summary_duplicate_case_drift`, `helper_summary_case_order_drift`, `contract_summary_status_drift`, `contract_summary_base_count_drift`, `contract_summary_base_case_order_drift`, `contract_summary_repeat_count_drift`, `contract_summary_repeat_case_order_drift`, `contract_summary_case_count_drift`, `contract_summary_duplicate_case_drift`, and `contract_summary_case_order_drift`.",
    "- `python3 scripts/zigux/check-artifact-diff-contract.py` is the live outward contract replay and must rerun `python3 scripts/zigux/artifact_diff.py --self-test` twice, rerun `python3 scripts/zigux/artifact_diff.py -h` twice, rerun the missing-required-args parser failure twice, rerun the missing-actual-operand parser failure twice, rerun the invalid-mode parser failure twice, and then emit `ARTIFACT_DIFF_CONTRACT=pass`, `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=23`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=5`, and `ARTIFACT_DIFF_CONTRACT_CASE_COUNT=28`.",
    "- `ARTIFACT_DIFF_CONTRACT_BASE_CASES` must stay this exact base packet: `helper_self_test`, `cli_help_output`, `cli_missing_required_args`, `cli_missing_actual_operand`, `cli_invalid_mode`, `text_pass`, `text_mismatch`, `text_missing_expected`, `text_missing_actual`, `text_missing_both`, `json_pass`, `json_mismatch`, `json_missing_expected`, `json_missing_actual`, `json_missing_both`, `json_invalid_expected`, `json_invalid_actual`, `json_invalid_both`, `sha256_pass`, `sha256_missing_expected`, `sha256_missing_actual`, `sha256_missing_both`, and `sha256_drift`.",
    "- `ARTIFACT_DIFF_CONTRACT_REPEAT_CASES` must stay this exact repeat packet: `helper_self_test_repeat`, `cli_help_output_repeat`, `text_pass_repeat`, `json_mismatch_repeat`, and `sha256_drift_repeat`.",
    "- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test` is the isolated catalog-drift replay and must emit `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass`, `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=24`, and this exact self-test packet: `catalog_shape`, `phase4_use_marker_round_trip`, `phase4_use_marker_drift`, `survey_note_marker_round_trip`, `survey_note_marker_drift`, `survey_replay_marker_round_trip`, `survey_replay_marker_drift`, `review_note_marker_round_trip`, `review_note_marker_drift`, `docs_root_marker_round_trip`, `docs_root_marker_drift`, `scripts_root_marker_round_trip`, `scripts_root_marker_drift`, `helper_summary_round_trip`, `helper_summary_count_drift`, `helper_summary_case_order_drift`, `contract_self_test_round_trip`, `contract_self_test_count_drift`, `contract_self_test_duplicate_case_drift`, `contract_self_test_missing_owner_review_note_drift`, `contract_self_test_case_order_drift`, `contract_summary_round_trip`, `contract_summary_case_count_drift`, and `contract_summary_case_order_drift`.",
    "- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py` is the live summary replay and must rerun the helper self-test summary packet, the contract self-test summary packet, the full 28-case contract summary packet, the required Phase 4 use markers above, the required survey-note markers, the required review-note markers below, the required docs-root markers, and the required scripts-root markers before it emits `PHASE4_ARTIFACT_DIFF_DETERMINISM=pass`, `PHASE4_ARTIFACT_DIFF_HELPER_SELF_TEST_CASE_COUNT=19`, `PHASE4_ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24`, and `PHASE4_ARTIFACT_DIFF_CONTRACT_CASE_COUNT=28`.",
]

EXPECTED_SELF_TEST_CASES = [
    "round_trip",
    "result_lines_marker_drift",
    "json_invalid_marker_drift",
    "helper_catalog_drift",
    "contract_self_test_catalog_drift",
    "contract_catalog_drift",
    "repeat_packet_drift",
    "determinism_catalog_drift",
]


def validate_note_text(note_text: str) -> list[str]:
    return [marker for marker in REQUIRED_MARKERS if marker not in note_text]


def expect_fail(label: str, note_text: str, needle: str) -> None:
    failures = validate_note_text(note_text.replace(needle, "", 1))
    if needle not in failures:
        raise AssertionError(f"expected review-note drift for {label}")


def build_fixture_note() -> str:
    return "\n".join(["# Artifact Diff Policy", "", *REQUIRED_MARKERS]) + "\n"


def run_self_test() -> int:
    if len(set(EXPECTED_SELF_TEST_CASES)) != len(EXPECTED_SELF_TEST_CASES):
        raise AssertionError(
            f"review-note self-test cases must stay unique: {EXPECTED_SELF_TEST_CASES}"
        )

    with tempfile.TemporaryDirectory(prefix="zigux_phase4_artifact_note_") as tempdir:
        note_path = Path(tempdir) / "artifact-diff.md"
        note_path.write_text(build_fixture_note(), encoding="utf-8")
        note_text = note_path.read_text(encoding="utf-8")

        covered_cases: list[str] = []

        failures = validate_note_text(note_text)
        if failures:
            raise AssertionError(f"round-trip note markers missing: {failures}")
        covered_cases.append("round_trip")

        expect_fail(
            "result_lines_marker_drift",
            note_text,
            REQUIRED_MARKERS[0],
        )
        covered_cases.append("result_lines_marker_drift")

        expect_fail(
            "json_invalid_marker_drift",
            note_text,
            REQUIRED_MARKERS[1],
        )
        covered_cases.append("json_invalid_marker_drift")

        expect_fail(
            "helper_catalog_drift",
            note_text,
            REQUIRED_MARKERS[2],
        )
        covered_cases.append("helper_catalog_drift")

        expect_fail(
            "contract_self_test_catalog_drift",
            note_text,
            REQUIRED_MARKERS[3],
        )
        covered_cases.append("contract_self_test_catalog_drift")

        expect_fail(
            "contract_catalog_drift",
            note_text,
            REQUIRED_MARKERS[4],
        )
        covered_cases.append("contract_catalog_drift")

        expect_fail(
            "repeat_packet_drift",
            note_text,
            REQUIRED_MARKERS[6],
        )
        covered_cases.append("repeat_packet_drift")

        expect_fail(
            "determinism_catalog_drift",
            note_text,
            REQUIRED_MARKERS[8],
        )
        covered_cases.append("determinism_catalog_drift")

    if covered_cases != EXPECTED_SELF_TEST_CASES:
        raise AssertionError(
            f"review-note self-test catalog drifted: expected {EXPECTED_SELF_TEST_CASES}, got {covered_cases}"
        )

    print("PHASE4_ARTIFACT_DIFF_REVIEW_NOTE_SELF_TEST=pass")
    print(
        f"PHASE4_ARTIFACT_DIFF_REVIEW_NOTE_SELF_TEST_CASE_COUNT={len(EXPECTED_SELF_TEST_CASES)}"
    )
    print(
        "PHASE4_ARTIFACT_DIFF_REVIEW_NOTE_SELF_TEST_CASES="
        + ",".join(EXPECTED_SELF_TEST_CASES)
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 4 artifact-diff review note keeps the published contract packet explicit."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run isolated review-note checker self-tests.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    note_text = NOTE_PATH.read_text(encoding="utf-8")
    failures = validate_note_text(note_text)
    if failures:
        print("PHASE4_ARTIFACT_DIFF_REVIEW_NOTE=fail")
        print("PHASE4_ARTIFACT_DIFF_REVIEW_NOTE_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE4_ARTIFACT_DIFF_REVIEW_NOTE_FAILURES_END")
        return 1

    print("PHASE4_ARTIFACT_DIFF_REVIEW_NOTE=pass")
    print(f"PHASE4_ARTIFACT_DIFF_REVIEW_NOTE_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
