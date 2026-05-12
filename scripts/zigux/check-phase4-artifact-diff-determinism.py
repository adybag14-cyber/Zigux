#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIFF = ROOT / "scripts" / "zigux" / "artifact_diff.py"
ARTIFACT_DIFF_CONTRACT = ROOT / "scripts" / "zigux" / "check-artifact-diff-contract.py"
ARTIFACT_DIFF_NOTE = ROOT / "Documentation" / "zigux" / "artifact-diff.md"
DOCS_ROOT_NOTE = ROOT / "Documentation" / "zigux" / "README.md"
SCRIPTS_ROOT_NOTE = ROOT / "scripts" / "zigux" / "README.md"

EXPECTED_HELPER_SELF_TEST_CASES = [
    "text_pass",
    "text_mismatch",
    "json_pass",
    "json_mismatch",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
    "sha256_pass",
    "sha256_drift",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "sha256_missing_expected",
    "sha256_missing_actual",
    "sha256_missing_both",
    "invalid_mode_rejected",
]
EXPECTED_CONTRACT_SELF_TEST_CASES = [
    "catalog_shape",
    "review_note_marker_round_trip",
    "review_note_owner_marker_drift",
    "review_note_marker_drift",
    "helper_summary_round_trip",
    "contract_summary_round_trip",
    "helper_summary_status_drift",
    "helper_summary_count_drift",
    "helper_summary_duplicate_case_drift",
    "helper_summary_case_order_drift",
    "contract_summary_status_drift",
    "contract_summary_base_count_drift",
    "contract_summary_base_case_order_drift",
    "contract_summary_repeat_count_drift",
    "contract_summary_repeat_case_order_drift",
    "contract_summary_case_count_drift",
    "contract_summary_duplicate_case_drift",
    "contract_summary_case_order_drift",
]
EXPECTED_CONTRACT_CASES = [
    "helper_self_test",
    "helper_self_test_repeat",
    "cli_help_output",
    "cli_help_output_repeat",
    "cli_missing_required_args",
    "cli_missing_actual_operand",
    "cli_invalid_mode",
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
EXPECTED_SELF_TEST_CASES = [
    "catalog_shape",
    "phase4_use_marker_round_trip",
    "phase4_use_marker_drift",
    "review_note_marker_round_trip",
    "review_note_marker_drift",
    "docs_root_marker_round_trip",
    "docs_root_marker_drift",
    "scripts_root_marker_round_trip",
    "scripts_root_marker_drift",
    "helper_summary_round_trip",
    "helper_summary_count_drift",
    "helper_summary_case_order_drift",
    "contract_self_test_round_trip",
    "contract_self_test_count_drift",
    "contract_self_test_missing_owner_review_note_drift",
    "contract_self_test_case_order_drift",
    "contract_summary_round_trip",
    "contract_summary_case_count_drift",
    "contract_summary_case_order_drift",
]
REQUIRED_PHASE4_USE_MARKERS = [
    "- `scripts/zigux/artifact_diff.py` stays the shared host-side comparison helper behind the committed artifact-check packets.",
    "- `scripts/zigux/check-artifact-diff-contract.py` reruns the bounded helper self-test, CLI help output, missing-required-args, missing-actual-operand, and invalid-mode parser coverage plus the text, JSON, SHA-256, missing-path, malformed-input, and repeat-run cases so the helper's outward contract stays deterministic before the broader Phase 4 validator and Zig gates run.",
    "- `scripts/zigux/check-phase4-artifact-diff-determinism.py` rechecks the helper and contract summary catalogs together so case-count, case-order, and repeat-case drift fail closed before the shared Phase 4 validator and Zig gates run.",
]
REQUIRED_REVIEW_NOTE_MARKERS = [
    "- deterministic survey entrypoint: `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py` must keep the helper self-test catalog, the contract summary catalog, and the repeat-case packet aligned with this note and the shared validator packet",
    "- deterministic survey self-test catalog: `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT` and `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES` must stay aligned with the isolated phase4-use, review-note, helper-summary, and contract-catalog drift coverage",
]
REQUIRED_DOCS_ROOT_MARKERS = [
    "- `python3 scripts/zigux/validate-phase4.py` keeps the shared `scripts/zigux/check-artifact-diff-contract.py` contract replay, the dedicated `scripts/zigux/check-phase4-artifact-diff-determinism.py` deterministic catalog checker, the dedicated `scripts/zigux/check-phase4-workflow-route-counts.py` workflow-route-count checker, the dedicated `scripts/zigux/check-phase4-gate-evidence.py` exact-readback gate, the live `zigux/tests/atomic64_diff.zig` roadmap wrapper, its shared `zigux/tests/runtime_atomic64_diff.zig` backing replay, the manifest-backed runtime atomic64 handoff pair `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` plus `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, the manifest-backed bitmap rollback survey pair `zigux/tests/phase4_bitmap_diff_manifest.json` plus `zigux/tests/phase4_bitmap_diff_survey.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` wired through the shared `zigux/tests/phase4_build.zig` entrypoint, `zigux/Makefile`, `make -C zigux phase4-validate`, `make -C zigux phase4-runtime-atomic64-diff-survey`, `make -C zigux phase4-bitmap-diff-survey`, `make -C zigux phase4-bitmap-diff`, `make -C zigux phase4-bitmap-live-helper-replay`, `make -C zigux phase4`, and the bootstrap workflow.",
]
REQUIRED_SCRIPTS_ROOT_MARKERS = [
    "Phase 4 flow - `validate-phase4.py` checks that the shared Phase 4 rollback-readiness packet stays aligned across `scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/check-phase4-artifact-diff-determinism.py`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, `zigux/tests/bitmap_diff.zig`, `zigux/tests/phase4_bitmap_diff_manifest.json`, `zigux/tests/phase4_bitmap_diff_survey.zig`, `zigux/tests/phase4_bitmap_live_helper_replay.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, `zigux/tests/phase4_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` before the rollback and survey replays run.",
]


def extract_output_value(lines: list[str], prefix: str) -> str:
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix) :]
    raise AssertionError(f"missing output line with prefix {prefix!r}: {lines}")


def parse_case_catalog(lines: list[str], count_prefix: str, list_prefix: str) -> list[str]:
    count_text = extract_output_value(lines, count_prefix)
    try:
        expected_count = int(count_text)
    except ValueError as exc:
        raise AssertionError(
            f"invalid integer for {count_prefix!r}: {count_text!r}"
        ) from exc
    cases_text = extract_output_value(lines, list_prefix)
    cases = [] if not cases_text else cases_text.split(",")
    if len(cases) != expected_count:
        raise AssertionError(
            f"count/list drift for {count_prefix!r} and {list_prefix!r}: count={expected_count} cases={cases}"
        )
    if len(set(cases)) != len(cases):
        raise AssertionError(f"duplicate cases in {list_prefix!r}: {cases}")
    return cases


def assert_markers(text: str, markers: list[str], label: str) -> None:
    missing_markers = [marker for marker in markers if marker not in text]
    if missing_markers:
        raise AssertionError(f"{label} markers missing: {missing_markers}")


def assert_helper_summary(lines: list[str]) -> None:
    if extract_output_value(lines, "ARTIFACT_DIFF_SELF_TEST=") != "pass":
        raise AssertionError(f"unexpected helper self-test status: {lines}")
    cases = parse_case_catalog(
        lines,
        "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=",
        "ARTIFACT_DIFF_SELF_TEST_CASES=",
    )
    if cases != EXPECTED_HELPER_SELF_TEST_CASES:
        raise AssertionError(
            f"helper self-test catalog drifted: expected {EXPECTED_HELPER_SELF_TEST_CASES}, got {cases}"
        )


def assert_contract_self_test_summary(lines: list[str]) -> None:
    if extract_output_value(lines, "ARTIFACT_DIFF_CONTRACT_SELF_TEST=") != "pass":
        raise AssertionError(f"unexpected contract self-test status: {lines}")
    cases = parse_case_catalog(
        lines,
        "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=",
        "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=",
    )
    if cases != EXPECTED_CONTRACT_SELF_TEST_CASES:
        raise AssertionError(
            f"contract self-test catalog drifted: expected {EXPECTED_CONTRACT_SELF_TEST_CASES}, got {cases}"
        )


def assert_contract_summary(lines: list[str]) -> None:
    if extract_output_value(lines, "ARTIFACT_DIFF_CONTRACT=") != "pass":
        raise AssertionError(f"unexpected contract summary status: {lines}")
    cases = parse_case_catalog(
        lines,
        "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=",
        "ARTIFACT_DIFF_CONTRACT_CASES=",
    )
    if cases != EXPECTED_CONTRACT_CASES:
        raise AssertionError(
            f"contract catalog drifted: expected {EXPECTED_CONTRACT_CASES}, got {cases}"
        )


def expect_assertion(label: str, callback) -> None:
    try:
        callback()
    except AssertionError:
        return
    raise AssertionError(f"expected AssertionError for self-test case {label}")


def run_lines(argv: list[str]) -> list[str]:
    completed = subprocess.run(
        [sys.executable, *argv],
        check=False,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"unexpected exit {completed.returncode} for {argv}: {completed.stdout.splitlines()} stderr={completed.stderr!r}"
        )
    return completed.stdout.splitlines()


def run_self_test() -> int:
    if len(set(EXPECTED_SELF_TEST_CASES)) != len(EXPECTED_SELF_TEST_CASES):
        raise AssertionError(
            f"determinism self-test cases must stay unique: {EXPECTED_SELF_TEST_CASES}"
        )
    covered_cases: list[str] = []

    covered_cases.append("catalog_shape")

    phase4_use_text = "\n".join(REQUIRED_PHASE4_USE_MARKERS)
    assert_markers(phase4_use_text, REQUIRED_PHASE4_USE_MARKERS, "phase4_use")
    covered_cases.append("phase4_use_marker_round_trip")

    expect_assertion(
        "phase4_use_marker_drift",
        lambda: assert_markers(REQUIRED_PHASE4_USE_MARKERS[0], REQUIRED_PHASE4_USE_MARKERS, "phase4_use"),
    )
    covered_cases.append("phase4_use_marker_drift")

    review_note_text = "\n".join(REQUIRED_REVIEW_NOTE_MARKERS)
    assert_markers(review_note_text, REQUIRED_REVIEW_NOTE_MARKERS, "review_note")
    covered_cases.append("review_note_marker_round_trip")

    expect_assertion(
        "review_note_marker_drift",
        lambda: assert_markers(REQUIRED_REVIEW_NOTE_MARKERS[0], REQUIRED_REVIEW_NOTE_MARKERS, "review_note"),
    )
    covered_cases.append("review_note_marker_drift")

    docs_root_text = "\n".join(REQUIRED_DOCS_ROOT_MARKERS)
    assert_markers(docs_root_text, REQUIRED_DOCS_ROOT_MARKERS, "docs_root")
    covered_cases.append("docs_root_marker_round_trip")

    expect_assertion(
        "docs_root_marker_drift",
        lambda: assert_markers("", REQUIRED_DOCS_ROOT_MARKERS, "docs_root"),
    )
    covered_cases.append("docs_root_marker_drift")

    scripts_root_text = "\n".join(REQUIRED_SCRIPTS_ROOT_MARKERS)
    assert_markers(scripts_root_text, REQUIRED_SCRIPTS_ROOT_MARKERS, "scripts_root")
    covered_cases.append("scripts_root_marker_round_trip")

    expect_assertion(
        "scripts_root_marker_drift",
        lambda: assert_markers("", REQUIRED_SCRIPTS_ROOT_MARKERS, "scripts_root"),
    )
    covered_cases.append("scripts_root_marker_drift")

    helper_lines = [
        "ARTIFACT_DIFF_SELF_TEST=pass",
        "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=19",
        "ARTIFACT_DIFF_SELF_TEST_CASES=" + ",".join(EXPECTED_HELPER_SELF_TEST_CASES),
    ]
    assert_helper_summary(helper_lines)
    covered_cases.append("helper_summary_round_trip")

    bad_helper_count = helper_lines.copy()
    bad_helper_count[1] = "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=18"
    expect_assertion(
        "helper_summary_count_drift",
        lambda: assert_helper_summary(bad_helper_count),
    )
    covered_cases.append("helper_summary_count_drift")

    bad_helper_order = helper_lines.copy()
    bad_helper_order[2] = "ARTIFACT_DIFF_SELF_TEST_CASES=" + ",".join(
        ["text_mismatch", "text_pass", *EXPECTED_HELPER_SELF_TEST_CASES[2:]]
    )
    expect_assertion(
        "helper_summary_case_order_drift",
        lambda: assert_helper_summary(bad_helper_order),
    )
    covered_cases.append("helper_summary_case_order_drift")

    contract_self_test_lines = [
        "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass",
        f"ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT={len(EXPECTED_CONTRACT_SELF_TEST_CASES)}",
        "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=" + ",".join(EXPECTED_CONTRACT_SELF_TEST_CASES),
    ]
    assert_contract_self_test_summary(contract_self_test_lines)
    covered_cases.append("contract_self_test_round_trip")

    bad_contract_self_test_count = contract_self_test_lines.copy()
    bad_contract_self_test_count[1] = (
        "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT="
        f"{len(EXPECTED_CONTRACT_SELF_TEST_CASES) - 1}"
    )
    expect_assertion(
        "contract_self_test_count_drift",
        lambda: assert_contract_self_test_summary(bad_contract_self_test_count),
    )
    covered_cases.append("contract_self_test_count_drift")

    bad_contract_self_test_missing_owner = contract_self_test_lines.copy()
    bad_contract_self_test_missing_owner[2] = (
        "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=" + ",".join(
            [
                "catalog_shape",
                "review_note_marker_round_trip",
                "review_note_marker_drift",
                *EXPECTED_CONTRACT_SELF_TEST_CASES[3:],
            ]
        )
    )
    expect_assertion(
        "contract_self_test_missing_owner_review_note_drift",
        lambda: assert_contract_self_test_summary(
            bad_contract_self_test_missing_owner
        ),
    )
    covered_cases.append("contract_self_test_missing_owner_review_note_drift")

    bad_contract_self_test_order = contract_self_test_lines.copy()
    bad_contract_self_test_order[2] = "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES=" + ",".join(
        ["review_note_marker_round_trip", "catalog_shape", *EXPECTED_CONTRACT_SELF_TEST_CASES[2:]]
    )
    expect_assertion(
        "contract_self_test_case_order_drift",
        lambda: assert_contract_self_test_summary(bad_contract_self_test_order),
    )
    covered_cases.append("contract_self_test_case_order_drift")

    contract_lines = [
        "ARTIFACT_DIFF_CONTRACT=pass",
        "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=23",
        "ARTIFACT_DIFF_CONTRACT_BASE_CASES=" + ",".join(
            [
                case
                for case in EXPECTED_CONTRACT_CASES
                if case
                not in {
                    "helper_self_test_repeat",
                    "cli_help_output_repeat",
                    "text_pass_repeat",
                    "json_mismatch_repeat",
                    "sha256_drift_repeat",
                }
            ]
        ),
        "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=5",
        "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES=helper_self_test_repeat,cli_help_output_repeat,text_pass_repeat,json_mismatch_repeat,sha256_drift_repeat",
        f"ARTIFACT_DIFF_CONTRACT_CASE_COUNT={len(EXPECTED_CONTRACT_CASES)}",
        "ARTIFACT_DIFF_CONTRACT_CASES=" + ",".join(EXPECTED_CONTRACT_CASES),
    ]
    assert_contract_summary(contract_lines)
    covered_cases.append("contract_summary_round_trip")

    bad_contract_count = contract_lines.copy()
    bad_contract_count[5] = "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=27"
    expect_assertion(
        "contract_summary_case_count_drift",
        lambda: assert_contract_summary(bad_contract_count),
    )
    covered_cases.append("contract_summary_case_count_drift")

    bad_contract_order = contract_lines.copy()
    bad_contract_order[6] = "ARTIFACT_DIFF_CONTRACT_CASES=" + ",".join(
        ["helper_self_test_repeat", "helper_self_test", *EXPECTED_CONTRACT_CASES[2:]]
    )
    expect_assertion(
        "contract_summary_case_order_drift",
        lambda: assert_contract_summary(bad_contract_order),
    )
    covered_cases.append("contract_summary_case_order_drift")

    if covered_cases != EXPECTED_SELF_TEST_CASES:
        raise AssertionError(
            f"determinism self-test catalog drifted: expected {EXPECTED_SELF_TEST_CASES}, got {covered_cases}"
        )

    print("PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass")
    print(
        f"PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT={len(EXPECTED_SELF_TEST_CASES)}"
    )
    print(
        "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES="
        + ",".join(EXPECTED_SELF_TEST_CASES)
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shared Phase 4 artifact-diff helper and checker summaries stay deterministic."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in determinism checker self-tests.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    run_self_test()
    note_text = ARTIFACT_DIFF_NOTE.read_text(encoding="utf-8")
    assert_markers(note_text, REQUIRED_PHASE4_USE_MARKERS, "phase4_use")
    assert_markers(note_text, REQUIRED_REVIEW_NOTE_MARKERS, "review_note")

    docs_root_text = DOCS_ROOT_NOTE.read_text(encoding="utf-8")
    assert_markers(docs_root_text, REQUIRED_DOCS_ROOT_MARKERS, "docs_root")

    scripts_root_text = SCRIPTS_ROOT_NOTE.read_text(encoding="utf-8")
    assert_markers(scripts_root_text, REQUIRED_SCRIPTS_ROOT_MARKERS, "scripts_root")

    helper_lines = run_lines([str(ARTIFACT_DIFF), "--self-test"])
    assert_helper_summary(helper_lines)

    contract_self_test_lines = run_lines([str(ARTIFACT_DIFF_CONTRACT), "--self-test"])
    assert_contract_self_test_summary(contract_self_test_lines)

    contract_lines = run_lines([str(ARTIFACT_DIFF_CONTRACT)])
    assert_contract_summary(contract_lines)

    print("PHASE4_ARTIFACT_DIFF_DETERMINISM=pass")
    print(f"PHASE4_ARTIFACT_DIFF_HELPER_SELF_TEST_CASE_COUNT={len(EXPECTED_HELPER_SELF_TEST_CASES)}")
    print(
        f"PHASE4_ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT={len(EXPECTED_CONTRACT_SELF_TEST_CASES)}"
    )
    print(f"PHASE4_ARTIFACT_DIFF_CONTRACT_CASE_COUNT={len(EXPECTED_CONTRACT_CASES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
