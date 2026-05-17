#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tempfile
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
    "validator_target_missing",
]


def assert_markers(text: str, markers: list[str], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise AssertionError(f"{label} markers missing: {missing}")


def read_validator_text(path: Path, display_path: str | None = None) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        label = display_path
        if label is None:
            try:
                label = path.relative_to(ROOT).as_posix()
            except ValueError:
                label = path.as_posix()
        raise RuntimeError(
            "current tree is missing the historical validator replay target: "
            f"{label}"
        ) from exc


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

    with tempfile.TemporaryDirectory(prefix="phase4-validator-replays-") as tmp:
        missing_root = Path(tmp)
        missing_target = missing_root / "scripts" / "zigux" / "validate-phase4.py"
        try:
            read_validator_text(
                missing_target,
                display_path="scripts/zigux/validate-phase4.py",
            )
        except RuntimeError as exc:
            expected = (
                "current tree is missing the historical validator replay target: "
                "scripts/zigux/validate-phase4.py"
            )
            if str(exc) != expected:
                raise AssertionError(
                    "missing validator target message drifted: "
                    f"expected {expected!r}, got {str(exc)!r}"
                ) from exc
            covered_cases.append("validator_target_missing")
        else:
            raise AssertionError("expected validator_target_missing to fail closed")

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

    try:
        run_self_test()
        validator_text = read_validator_text(VALIDATOR)
        assert_markers(
            validator_text,
            EXPECTED_VALIDATOR_REPLAY_MARKERS,
            "validator_surface",
        )
    except RuntimeError as exc:
        print(f"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS=fail: {exc}", file=sys.stderr)
        return 1

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
