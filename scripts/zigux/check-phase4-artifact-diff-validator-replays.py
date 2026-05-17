#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase4.py"

EXPECTED_VALIDATOR_REPLAY_MARKERS = [
    '("ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CHECK", ["scripts/zigux/check-phase4-artifact-diff-determinism.py", "--self-test"], "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass"),',
    '("ARTIFACT_DIFF_CONTRACT_SELF_TEST_CHECK", ["scripts/zigux/check-artifact-diff-contract.py", "--self-test"], "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass"),',
    '("ARTIFACT_DIFF_CONTRACT_CHECK", ["scripts/zigux/check-artifact-diff-contract.py"], "ARTIFACT_DIFF_CONTRACT=pass"),',
]

EXPECTED_SELF_TEST_CASES = [
    "catalog_shape",
    "validator_marker_round_trip",
    "validator_marker_drift",
]


def assert_markers(text: str, markers: list[str], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise AssertionError(f"{label} markers missing: {missing}")


def run_self_test() -> int:
    if len(set(EXPECTED_SELF_TEST_CASES)) != len(EXPECTED_SELF_TEST_CASES):
        raise AssertionError(
            f"self-test catalog must stay unique: {EXPECTED_SELF_TEST_CASES}"
        )

    covered_cases: list[str] = ["catalog_shape"]

    validator_text = "\n".join(EXPECTED_VALIDATOR_REPLAY_MARKERS)
    assert_markers(
        validator_text,
        EXPECTED_VALIDATOR_REPLAY_MARKERS,
        "validator_surface",
    )
    covered_cases.append("validator_marker_round_trip")

    try:
        assert_markers(
            EXPECTED_VALIDATOR_REPLAY_MARKERS[0],
            EXPECTED_VALIDATOR_REPLAY_MARKERS,
            "validator_surface",
        )
    except AssertionError:
        covered_cases.append("validator_marker_drift")
    else:
        raise AssertionError("expected validator_marker_drift to fail closed")

    if covered_cases != EXPECTED_SELF_TEST_CASES:
        raise AssertionError(
            f"self-test catalog drifted: expected {EXPECTED_SELF_TEST_CASES}, got {covered_cases}"
        )

    print("PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST=pass")
    print(
        "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT="
        f"{len(EXPECTED_SELF_TEST_CASES)}"
    )
    print(
        "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASES="
        + ",".join(EXPECTED_SELF_TEST_CASES)
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that validate-phase4.py keeps rerunning the shipped "
            "artifact-diff contract and determinism hooks."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker self-tests.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    run_self_test()
    validator_text = VALIDATOR.read_text(encoding="utf-8")
    assert_markers(
        validator_text,
        EXPECTED_VALIDATOR_REPLAY_MARKERS,
        "validator_surface",
    )

    print("PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS=pass")
    print(
        "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT="
        f"{len(EXPECTED_VALIDATOR_REPLAY_MARKERS)}"
    )
    print(
        "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKERS="
        + ",".join(
            [
                "ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CHECK",
                "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CHECK",
                "ARTIFACT_DIFF_CONTRACT_CHECK",
            ]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
