#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIFF_NOTE_REL = Path("Documentation/zigux/artifact-diff.md")
TOOLING_SURVEY_REL = Path("Documentation/zigux/phase4-artifact-diff-tooling-survey.md")
VALIDATION_MATRIX_REL = Path("Documentation/zigux/phase4-validation-matrix.md")
VALIDATOR_REPLAYS_REL = Path("scripts/zigux/check-phase4-artifact-diff-validator-replays.py")
VALIDATOR_REL = Path("scripts/zigux/validate-phase4.py")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

EXPECTED_ARTIFACT_DIFF_NOTE_MARKERS = [
    "`scripts/zigux/check-phase4-artifact-diff-validator-replays.py`",
    "validator-route and workflow drift fail closed before the shared Phase 4 validator and Zig gates run.",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=14`",
]

EXPECTED_TOOLING_SURVEY_MARKERS = [
    "PHASE4_ARTIFACT_DIFF_TOOLING_STATUS=helper_contract_validator_and_owner_note_direct_readback_aligned_on_current_master",
    "That same direct packet now needs to keep the helper's exact output-contract lines pinned too",
    "`scripts/zigux/check-phase4-artifact-diff-validator-replays.py`",
    "`scripts/zigux/validate-phase4.py`",
    "`python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test`",
    "`python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=14`",
]

EXPECTED_VALIDATION_MATRIX_MARKERS = [
    "scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
    "scripts/zigux/validate-phase4.py",
    "python3 scripts/zigux/validate-phase4.py",
    "scripts/zigux/check-phase4-workflow-route-counts.py",
]

EXPECTED_VALIDATOR_REPLAYS_MARKERS = [
    'PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14',
    '"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT="',
    '"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT="',
    '"validator_marker_round_trip",',
    '"workflow_marker_round_trip",',
    '"artifact_diff_note_round_trip",',
]

EXPECTED_VALIDATOR_MARKERS = [
    'CheckSpec("phase4-artifact-diff-validator-replays-self-test", ("python", "scripts/zigux/check-phase4-artifact-diff-validator-replays.py", "--self-test"))',
    'CheckSpec("phase4-artifact-diff-validator-replays", ("python", "scripts/zigux/check-phase4-artifact-diff-validator-replays.py"))',
    '"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST=pass"',
    '"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14"',
    '"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS=pass"',
    '"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MODE=validator_present"',
    '"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7"',
    '"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=14"',
]

EXPECTED_WORKFLOW_MARKERS = [
    "- name: Self-test current Phase 4 artifact-diff validator replay checker",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test",
    "- name: Check current Phase 4 artifact-diff validator replay packet",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
]

EXPECTED_SELF_TEST_CASES = [
    "catalog_shape",
    "artifact_diff_note_round_trip",
    "artifact_diff_note_marker_drift",
    "tooling_survey_round_trip",
    "tooling_survey_marker_drift",
    "validation_matrix_round_trip",
    "validation_matrix_marker_drift",
    "validator_replays_round_trip",
    "validator_replays_marker_drift",
    "validator_round_trip",
    "validator_marker_drift",
    "workflow_round_trip",
    "workflow_marker_drift",
]


def assert_markers(text: str, markers: list[str], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise AssertionError(f"{label} markers missing: {missing}")


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing required file: {rel.as_posix()}") from exc


def check(root: Path) -> None:
    assert_markers(
        read_text(root, ARTIFACT_DIFF_NOTE_REL),
        EXPECTED_ARTIFACT_DIFF_NOTE_MARKERS,
        "artifact_diff_note_surface",
    )
    assert_markers(
        read_text(root, TOOLING_SURVEY_REL),
        EXPECTED_TOOLING_SURVEY_MARKERS,
        "tooling_survey_surface",
    )
    assert_markers(
        read_text(root, VALIDATION_MATRIX_REL),
        EXPECTED_VALIDATION_MATRIX_MARKERS,
        "validation_matrix_surface",
    )
    assert_markers(
        read_text(root, VALIDATOR_REPLAYS_REL),
        EXPECTED_VALIDATOR_REPLAYS_MARKERS,
        "validator_replays_surface",
    )
    assert_markers(
        read_text(root, VALIDATOR_REL),
        EXPECTED_VALIDATOR_MARKERS,
        "validator_surface",
    )
    assert_markers(
        read_text(root, WORKFLOW_REL),
        EXPECTED_WORKFLOW_MARKERS,
        "workflow_surface",
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture(root: Path) -> None:
    write_text(
        root / ARTIFACT_DIFF_NOTE_REL,
        "\n".join(["# note", *EXPECTED_ARTIFACT_DIFF_NOTE_MARKERS]) + "\n",
    )
    write_text(
        root / TOOLING_SURVEY_REL,
        "\n".join(["# survey", *EXPECTED_TOOLING_SURVEY_MARKERS]) + "\n",
    )
    write_text(
        root / VALIDATION_MATRIX_REL,
        "\n".join(["# matrix", *EXPECTED_VALIDATION_MATRIX_MARKERS]) + "\n",
    )
    write_text(
        root / VALIDATOR_REPLAYS_REL,
        "\n".join(["# checker", *EXPECTED_VALIDATOR_REPLAYS_MARKERS]) + "\n",
    )
    write_text(
        root / VALIDATOR_REL,
        "\n".join(["# validator", *EXPECTED_VALIDATOR_MARKERS]) + "\n",
    )
    write_text(
        root / WORKFLOW_REL,
        "\n".join(["name: zigux-bootstrap", *EXPECTED_WORKFLOW_MARKERS]) + "\n",
    )


def run_self_test() -> int:
    covered_cases: list[str] = ["catalog_shape"]

    with tempfile.TemporaryDirectory(prefix="phase4-validator-surface-alignment-") as tmp:
        root = Path(tmp)

        make_fixture(root)
        check(root)
        covered_cases.append("artifact_diff_note_round_trip")

        make_fixture(root)
        write_text(root / ARTIFACT_DIFF_NOTE_REL, EXPECTED_ARTIFACT_DIFF_NOTE_MARKERS[0] + "\n")
        try:
            check(root)
        except AssertionError:
            covered_cases.append("artifact_diff_note_marker_drift")
        else:
            raise AssertionError("expected artifact_diff_note_marker_drift to fail closed")

        make_fixture(root)
        check(root)
        covered_cases.append("tooling_survey_round_trip")

        make_fixture(root)
        write_text(root / TOOLING_SURVEY_REL, EXPECTED_TOOLING_SURVEY_MARKERS[0] + "\n")
        try:
            check(root)
        except AssertionError:
            covered_cases.append("tooling_survey_marker_drift")
        else:
            raise AssertionError("expected tooling_survey_marker_drift to fail closed")

        make_fixture(root)
        check(root)
        covered_cases.append("validation_matrix_round_trip")

        make_fixture(root)
        write_text(root / VALIDATION_MATRIX_REL, EXPECTED_VALIDATION_MATRIX_MARKERS[0] + "\n")
        try:
            check(root)
        except AssertionError:
            covered_cases.append("validation_matrix_marker_drift")
        else:
            raise AssertionError("expected validation_matrix_marker_drift to fail closed")

        make_fixture(root)
        check(root)
        covered_cases.append("validator_replays_round_trip")

        make_fixture(root)
        write_text(root / VALIDATOR_REPLAYS_REL, EXPECTED_VALIDATOR_REPLAYS_MARKERS[0] + "\n")
        try:
            check(root)
        except AssertionError:
            covered_cases.append("validator_replays_marker_drift")
        else:
            raise AssertionError("expected validator_replays_marker_drift to fail closed")

        make_fixture(root)
        check(root)
        covered_cases.append("validator_round_trip")

        make_fixture(root)
        write_text(root / VALIDATOR_REL, EXPECTED_VALIDATOR_MARKERS[0] + "\n")
        try:
            check(root)
        except AssertionError:
            covered_cases.append("validator_marker_drift")
        else:
            raise AssertionError("expected validator_marker_drift to fail closed")

        make_fixture(root)
        check(root)
        covered_cases.append("workflow_round_trip")

        make_fixture(root)
        write_text(root / WORKFLOW_REL, EXPECTED_WORKFLOW_MARKERS[0] + "\n")
        try:
            check(root)
        except AssertionError:
            covered_cases.append("workflow_marker_drift")
        else:
            raise AssertionError("expected workflow_marker_drift to fail closed")

    if covered_cases != EXPECTED_SELF_TEST_CASES:
        raise AssertionError(
            f"self-test catalog drifted: expected {EXPECTED_SELF_TEST_CASES}, got {covered_cases}"
        )

    print("PHASE4_ARTIFACT_DIFF_VALIDATOR_SURFACE_ALIGNMENT_SELF_TEST=pass")
    print(
        "PHASE4_ARTIFACT_DIFF_VALIDATOR_SURFACE_ALIGNMENT_SELF_TEST_CASE_COUNT="
        f"{len(EXPECTED_SELF_TEST_CASES)}"
    )
    print(
        "PHASE4_ARTIFACT_DIFF_VALIDATOR_SURFACE_ALIGNMENT_SELF_TEST_CASES="
        + ",".join(EXPECTED_SELF_TEST_CASES)
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the current Phase 4 artifact-diff note, survey, matrix, "
            "validator-replay checker, shared validator, and bootstrap workflow stay aligned."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        run_self_test()
        check(args.root.resolve())
    except (AssertionError, RuntimeError) as exc:
        print(f"PHASE4_ARTIFACT_DIFF_VALIDATOR_SURFACE_ALIGNMENT=fail: {exc}", file=sys.stderr)
        return 1

    print("PHASE4_ARTIFACT_DIFF_VALIDATOR_SURFACE_ALIGNMENT=pass")
    print("PHASE4_ARTIFACT_DIFF_VALIDATOR_SURFACE_ALIGNMENT_REQUIRED_FILE_COUNT=6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
