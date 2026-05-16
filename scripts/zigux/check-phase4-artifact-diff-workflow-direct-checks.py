#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SURVEY_PATH = (
    ROOT / "Documentation" / "zigux" / "phase4-artifact-diff-tooling-survey.md"
)

EXPECTED_WORKFLOW_DIRECT_CHECKS = [
    "artifact_diff_self_test",
    "contract_self_test",
    "contract_replay",
    "determinism_self_test",
    "determinism_replay",
]

EXPECTED_DIRECT_REPLAY_MARKERS = {
    "artifact_diff_self_test": "- `python3 scripts/zigux/artifact_diff.py --self-test`",
    "contract_self_test": "- `python3 scripts/zigux/check-artifact-diff-contract.py --self-test`",
    "contract_replay": "- `python3 scripts/zigux/check-artifact-diff-contract.py`",
    "determinism_self_test": (
        "- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test`"
    ),
    "determinism_replay": "- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py`",
}

EXPECTED_SELF_TEST_CASES = [
    "catalog_shape",
    "marker_round_trip",
    "marker_order_drift",
    "marker_duplicate_drift",
    "replay_marker_round_trip",
    "replay_marker_missing_drift",
]


def extract_markdown_marker_value(text: str, prefix: str) -> str:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("- `") and line.endswith("`"):
            line = line[3:-1]
        if line.startswith(prefix):
            return line[len(prefix) :]
    raise AssertionError(f"missing marker line with prefix {prefix!r}")


def parse_direct_checks(text: str) -> list[str]:
    value = extract_markdown_marker_value(
        text, "PHASE4_ARTIFACT_DIFF_WORKFLOW_DIRECT_CHECKS="
    )
    checks = [] if not value else value.split(",")
    if len(checks) != len(EXPECTED_WORKFLOW_DIRECT_CHECKS):
        raise AssertionError(
            "workflow direct-check count drifted: "
            f"expected {len(EXPECTED_WORKFLOW_DIRECT_CHECKS)}, got {len(checks)} "
            f"from {checks}"
        )
    if len(set(checks)) != len(checks):
        raise AssertionError(f"workflow direct-check catalog contains duplicates: {checks}")
    if checks != EXPECTED_WORKFLOW_DIRECT_CHECKS:
        raise AssertionError(
            "workflow direct-check catalog drifted: "
            f"expected {EXPECTED_WORKFLOW_DIRECT_CHECKS}, got {checks}"
        )
    return checks


def assert_replay_markers(text: str) -> None:
    missing = [
        marker
        for marker in EXPECTED_DIRECT_REPLAY_MARKERS.values()
        if marker not in text
    ]
    if missing:
        raise AssertionError(f"workflow direct replay markers missing: {missing}")


def run_self_test() -> int:
    if len(set(EXPECTED_WORKFLOW_DIRECT_CHECKS)) != len(EXPECTED_WORKFLOW_DIRECT_CHECKS):
        raise AssertionError(
            "expected workflow direct checks must stay unique: "
            f"{EXPECTED_WORKFLOW_DIRECT_CHECKS}"
        )
    if len(set(EXPECTED_SELF_TEST_CASES)) != len(EXPECTED_SELF_TEST_CASES):
        raise AssertionError(
            f"workflow direct-check self-test cases must stay unique: {EXPECTED_SELF_TEST_CASES}"
        )

    covered_cases: list[str] = []
    covered_cases.append("catalog_shape")

    round_trip_text = "\n".join(
        [
            (
                "- `PHASE4_ARTIFACT_DIFF_WORKFLOW_DIRECT_CHECKS="
                + ",".join(EXPECTED_WORKFLOW_DIRECT_CHECKS)
                + "`"
            ),
            *EXPECTED_DIRECT_REPLAY_MARKERS.values(),
        ]
    )
    parse_direct_checks(round_trip_text)
    covered_cases.append("marker_round_trip")

    try:
        parse_direct_checks(
            round_trip_text.replace(
                "artifact_diff_self_test,contract_self_test",
                "contract_self_test,artifact_diff_self_test",
                1,
            )
        )
    except AssertionError:
        covered_cases.append("marker_order_drift")
    else:
        raise AssertionError("expected marker_order_drift to fail closed")

    try:
        parse_direct_checks(
            round_trip_text.replace(
                "contract_self_test",
                "artifact_diff_self_test",
                1,
            )
        )
    except AssertionError:
        covered_cases.append("marker_duplicate_drift")
    else:
        raise AssertionError("expected marker_duplicate_drift to fail closed")

    assert_replay_markers(round_trip_text)
    covered_cases.append("replay_marker_round_trip")

    try:
        assert_replay_markers(
            round_trip_text.replace(
                EXPECTED_DIRECT_REPLAY_MARKERS["determinism_replay"],
                "",
                1,
            )
        )
    except AssertionError:
        covered_cases.append("replay_marker_missing_drift")
    else:
        raise AssertionError("expected replay_marker_missing_drift to fail closed")

    if covered_cases != EXPECTED_SELF_TEST_CASES:
        raise AssertionError(
            "workflow direct-check self-test catalog drifted: "
            f"expected {EXPECTED_SELF_TEST_CASES}, got {covered_cases}"
        )

    print("PHASE4_ARTIFACT_DIFF_WORKFLOW_DIRECT_CHECKS_SELF_TEST=pass")
    print(
        "PHASE4_ARTIFACT_DIFF_WORKFLOW_DIRECT_CHECKS_SELF_TEST_CASE_COUNT="
        f"{len(EXPECTED_SELF_TEST_CASES)}"
    )
    print(
        "PHASE4_ARTIFACT_DIFF_WORKFLOW_DIRECT_CHECKS_SELF_TEST_CASES="
        + ",".join(EXPECTED_SELF_TEST_CASES)
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check the Phase 4 artifact-diff workflow-direct-check catalog and replay "
            "surface."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in workflow direct-check checker self-tests.",
    )
    parser.add_argument(
        "--survey-path",
        type=Path,
        default=DEFAULT_SURVEY_PATH,
        help="Path to phase4-artifact-diff-tooling-survey.md.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    run_self_test()
    survey_text = args.survey_path.read_text(encoding="utf-8")
    checks = parse_direct_checks(survey_text)
    assert_replay_markers(survey_text)

    print("PHASE4_ARTIFACT_DIFF_WORKFLOW_DIRECT_CHECKS=pass")
    print(
        "PHASE4_ARTIFACT_DIFF_WORKFLOW_DIRECT_CHECK_COUNT="
        f"{len(checks)}"
    )
    print(
        "PHASE4_ARTIFACT_DIFF_WORKFLOW_DIRECT_CHECKS_LIST="
        + ",".join(checks)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
