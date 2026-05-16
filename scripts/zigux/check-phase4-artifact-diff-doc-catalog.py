#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DOC = ROOT / "Documentation" / "zigux" / "artifact-diff.md"

REQUIRED_MARKERS = [
    "## Phase 4 Exact Check Packet",
    "- `python3 scripts/zigux/artifact_diff.py --self-test` is the direct helper replay",
    "- `python3 scripts/zigux/check-artifact-diff-contract.py --self-test` is the isolated checker replay",
    "- `python3 scripts/zigux/check-artifact-diff-contract.py` is the live outward contract replay",
    "- `ARTIFACT_DIFF_CONTRACT_BASE_CASES` must stay this exact base packet:",
    "- `ARTIFACT_DIFF_CONTRACT_REPEAT_CASES` must stay this exact repeat packet:",
    "- `ARTIFACT_DIFF_CONTRACT_CASES` must stay the ordered union of those base and repeat packets",
    "- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test` is the isolated catalog-drift replay",
    "- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py` is the live summary replay",
    "## Phase 4 Tooling Review Note",
    "- deterministic helper contract: `ARTIFACT_DIFF_RESULT_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL[,SHA256|EXPECTED_EXISTS|ACTUAL_EXISTS|EXPECTED_JSON_ERROR|ACTUAL_JSON_ERROR]`",
    "- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_JSON_INVALID` must prove malformed JSON fails without inventing digest or exists markers",
    "- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_MISSING` must prove missing-path failures emit only the EXISTS markers",
    "- deterministic helper catalog: `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT` and `ARTIFACT_DIFF_SELF_TEST_CASES` must stay aligned with the helper's published `--self-test` packet",
    "- deterministic checker catalog: `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT`, `ARTIFACT_DIFF_CONTRACT_BASE_CASES`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASES`, `ARTIFACT_DIFF_CONTRACT_CASE_COUNT`, and `ARTIFACT_DIFF_CONTRACT_CASES` must stay aligned with the published contract replay packet",
    "- deterministic checker self-test catalog: `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT` and `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES` must stay aligned with the isolated stale-catalog and review-note drift coverage",
    "- deterministic survey self-test catalog: `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT` and `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES` must stay aligned with the isolated phase4-use, survey-note, survey-replay, review-note, docs-root, scripts-root, helper-summary, and contract-catalog drift coverage",
]

SELF_TEST_CASES = [
    "round_trip",
    "missing_exact_check_header",
    "missing_helper_replay_marker",
    "missing_contract_base_catalog_marker",
    "missing_determinism_self_test_marker",
    "missing_result_lines_marker",
    "missing_json_invalid_marker",
    "missing_missing_path_marker",
    "missing_helper_catalog_marker",
    "missing_contract_catalog_marker",
    "missing_contract_selftest_catalog_marker",
    "missing_determinism_catalog_marker",
]

SAMPLE_DOC = """# Artifact Diff Policy

Current Phase 4 use
- `scripts/zigux/artifact_diff.py` stays the shared host-side comparison helper behind the committed artifact-check packets.

## Phase 4 Exact Check Packet

- `python3 scripts/zigux/artifact_diff.py --self-test` is the direct helper replay and must emit `ARTIFACT_DIFF_SELF_TEST=pass`, `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=19`, and this exact case packet: `text_pass`, `text_mismatch`, `json_pass`, `json_mismatch`, `json_invalid_expected`, `json_invalid_actual`, `json_invalid_both`, `json_missing_expected`, `json_missing_actual`, `json_missing_both`, `sha256_pass`, `sha256_drift`, `text_missing_expected`, `text_missing_actual`, `text_missing_both`, `sha256_missing_expected`, `sha256_missing_actual`, `sha256_missing_both`, and `invalid_mode_rejected`.
- `python3 scripts/zigux/check-artifact-diff-contract.py --self-test` is the isolated checker replay and must emit `ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass`, `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24`, and this exact self-test packet: `catalog_shape`, `review_note_marker_round_trip`, `review_note_owner_marker_drift`, `review_note_marker_drift`, `cli_help_round_trip`, `cli_help_line_drift`, `cli_missing_argument_parser_round_trip`, `cli_missing_argument_parser_stderr_drift`, `cli_invalid_mode_parser_round_trip`, `cli_invalid_mode_parser_stderr_drift`, `helper_summary_round_trip`, `contract_summary_round_trip`, `helper_summary_status_drift`, `helper_summary_count_drift`, `helper_summary_duplicate_case_drift`, `helper_summary_case_order_drift`, `contract_summary_status_drift`, `contract_summary_base_count_drift`, `contract_summary_base_case_order_drift`, `contract_summary_repeat_count_drift`, `contract_summary_repeat_case_order_drift`, `contract_summary_case_count_drift`, `contract_summary_duplicate_case_drift`, and `contract_summary_case_order_drift`.
- `python3 scripts/zigux/check-artifact-diff-contract.py` is the live outward contract replay and must rerun `python3 scripts/zigux/artifact_diff.py --self-test` twice, rerun `python3 scripts/zigux/artifact_diff.py -h` twice, rerun the missing-required-args parser failure twice, rerun the missing-actual-operand parser failure twice, rerun the invalid-mode parser failure twice, and then emit `ARTIFACT_DIFF_CONTRACT=pass`, `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=23`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=5`, and `ARTIFACT_DIFF_CONTRACT_CASE_COUNT=28`.
- `ARTIFACT_DIFF_CONTRACT_BASE_CASES` must stay this exact base packet: `helper_self_test`, `cli_help_output`, `cli_missing_required_args`, `cli_missing_actual_operand`, `cli_invalid_mode`, `text_pass`, `text_mismatch`, `text_missing_expected`, `text_missing_actual`, `text_missing_both`, `json_pass`, `json_mismatch`, `json_missing_expected`, `json_missing_actual`, `json_missing_both`, `json_invalid_expected`, `json_invalid_actual`, `json_invalid_both`, `sha256_pass`, `sha256_missing_expected`, `sha256_missing_actual`, `sha256_missing_both`, and `sha256_drift`.
- `ARTIFACT_DIFF_CONTRACT_REPEAT_CASES` must stay this exact repeat packet: `helper_self_test_repeat`, `cli_help_output_repeat`, `text_pass_repeat`, `json_mismatch_repeat`, and `sha256_drift_repeat`.
- `ARTIFACT_DIFF_CONTRACT_CASES` must stay the ordered union of those base and repeat packets, including the paired CLI help-output replays inside the same published contract catalog.
- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test` is the isolated catalog-drift replay and must emit `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass`, `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=25`, and this exact self-test packet: `catalog_shape`, `phase4_use_marker_round_trip`, `phase4_use_marker_drift`, `survey_note_marker_round_trip`, `survey_note_marker_drift`, `survey_replay_marker_round_trip`, `survey_replay_marker_drift`, `review_note_marker_round_trip`, `review_note_marker_drift`, `docs_root_marker_round_trip`, `docs_root_marker_drift`, `scripts_root_marker_round_trip`, `scripts_root_marker_drift`, `helper_summary_round_trip`, `helper_summary_count_drift`, `helper_summary_duplicate_case_drift`, `helper_summary_case_order_drift`, `contract_self_test_round_trip`, `contract_self_test_count_drift`, `contract_self_test_duplicate_case_drift`, `contract_self_test_missing_owner_review_note_drift`, `contract_self_test_case_order_drift`, `contract_summary_round_trip`, `contract_summary_case_count_drift`, and `contract_summary_case_order_drift`.
- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py` is the live summary replay and must rerun the helper self-test summary packet, the contract self-test summary packet, the full 28-case contract summary packet, the required Phase 4 use markers above, the required survey-note markers, the required review-note markers below, the required docs-root markers, and the required scripts-root markers before it emits `PHASE4_ARTIFACT_DIFF_DETERMINISM=pass`, `PHASE4_ARTIFACT_DIFF_HELPER_SELF_TEST_CASE_COUNT=19`, `PHASE4_ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24`, and `PHASE4_ARTIFACT_DIFF_CONTRACT_CASE_COUNT=28`.

## Phase 4 Tooling Review Note

- deterministic helper contract: `ARTIFACT_DIFF_RESULT_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL[,SHA256|EXPECTED_EXISTS|ACTUAL_EXISTS|EXPECTED_JSON_ERROR|ACTUAL_JSON_ERROR]`
- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_JSON_INVALID` must prove malformed JSON fails without inventing digest or exists markers
- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_MISSING` must prove missing-path failures emit only the EXISTS markers
- deterministic helper catalog: `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT` and `ARTIFACT_DIFF_SELF_TEST_CASES` must stay aligned with the helper's published `--self-test` packet
- deterministic checker catalog: `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT`, `ARTIFACT_DIFF_CONTRACT_BASE_CASES`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASES`, `ARTIFACT_DIFF_CONTRACT_CASE_COUNT`, and `ARTIFACT_DIFF_CONTRACT_CASES` must stay aligned with the published contract replay packet
- deterministic checker self-test catalog: `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT` and `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES` must stay aligned with the isolated stale-catalog and review-note drift coverage
- deterministic survey self-test catalog: `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT` and `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES` must stay aligned with the isolated phase4-use, survey-note, survey-replay, review-note, docs-root, scripts-root, helper-summary, and contract-catalog drift coverage
"""


def ensure_markers(text: str, markers: list[str]) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        joined = "\n".join(f"  - {marker}" for marker in missing)
        raise AssertionError(
            "artifact-diff doc is missing required Phase 4 catalog markers:\n" + joined
        )


def run_self_test() -> int:
    covered: list[str] = []

    ensure_markers(SAMPLE_DOC, REQUIRED_MARKERS)
    covered.append("round_trip")

    drift_cases = [
        ("missing_exact_check_header", "## Phase 4 Exact Check Packet"),
        (
            "missing_helper_replay_marker",
            "- `python3 scripts/zigux/artifact_diff.py --self-test` is the direct helper replay",
        ),
        (
            "missing_contract_base_catalog_marker",
            "- `ARTIFACT_DIFF_CONTRACT_BASE_CASES` must stay this exact base packet:",
        ),
        (
            "missing_determinism_self_test_marker",
            "- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test` is the isolated catalog-drift replay",
        ),
        (
            "missing_result_lines_marker",
            "- deterministic helper contract: `ARTIFACT_DIFF_RESULT_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL[,SHA256|EXPECTED_EXISTS|ACTUAL_EXISTS|EXPECTED_JSON_ERROR|ACTUAL_JSON_ERROR]`",
        ),
        (
            "missing_json_invalid_marker",
            "- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_JSON_INVALID` must prove malformed JSON fails without inventing digest or exists markers",
        ),
        (
            "missing_missing_path_marker",
            "- deterministic helper contract: `ARTIFACT_DIFF_SELF_TEST_MISSING` must prove missing-path failures emit only the EXISTS markers",
        ),
        (
            "missing_helper_catalog_marker",
            "- deterministic helper catalog: `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT` and `ARTIFACT_DIFF_SELF_TEST_CASES` must stay aligned with the helper's published `--self-test` packet",
        ),
        (
            "missing_contract_catalog_marker",
            "- deterministic checker catalog: `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT`, `ARTIFACT_DIFF_CONTRACT_BASE_CASES`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASES`, `ARTIFACT_DIFF_CONTRACT_CASE_COUNT`, and `ARTIFACT_DIFF_CONTRACT_CASES` must stay aligned with the published contract replay packet",
        ),
        (
            "missing_contract_selftest_catalog_marker",
            "- deterministic checker self-test catalog: `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT` and `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES` must stay aligned with the isolated stale-catalog and review-note drift coverage",
        ),
        (
            "missing_determinism_catalog_marker",
            "- deterministic survey self-test catalog: `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT` and `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES` must stay aligned with the isolated phase4-use, survey-note, survey-replay, review-note, docs-root, scripts-root, helper-summary, and contract-catalog drift coverage",
        ),
    ]

    for label, marker in drift_cases:
        try:
            ensure_markers(SAMPLE_DOC.replace(marker, "", 1), REQUIRED_MARKERS)
        except AssertionError:
            covered.append(label)
            continue
        raise AssertionError(f"expected self-test drift failure for {label}")

    if covered != SELF_TEST_CASES:
        raise AssertionError(f"self-test case drift: expected {SELF_TEST_CASES}, got {covered}")

    print("PHASE4_ARTIFACT_DIFF_DOC_CATALOG_SELF_TEST=pass")
    print(f"PHASE4_ARTIFACT_DIFF_DOC_CATALOG_SELF_TEST_CASE_COUNT={len(covered)}")
    print("PHASE4_ARTIFACT_DIFF_DOC_CATALOG_SELF_TEST_CASES=" + ",".join(covered))
    return 0


def run_live(doc_path: Path) -> int:
    ensure_markers(doc_path.read_text(encoding="utf-8"), REQUIRED_MARKERS)
    print("PHASE4_ARTIFACT_DIFF_DOC_CATALOG=pass")
    print(f"PHASE4_ARTIFACT_DIFF_DOC_CATALOG_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the published Phase 4 artifact-diff doc catalog markers."
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_DOC,
        help="Path to Documentation/zigux/artifact-diff.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run embedded catalog drift coverage.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    return run_live(args.doc)


if __name__ == "__main__":
    raise SystemExit(main())
