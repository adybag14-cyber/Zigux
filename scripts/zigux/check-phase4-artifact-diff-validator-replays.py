#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_REL = Path("scripts/zigux/validate-phase4.py")
NOTE_REL = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

EXPECTED_VALIDATOR_REPLAY_MARKERS = [
    '("ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CHECK", ["scripts/zigux/check-phase4-artifact-diff-determinism.py", "--self-test"], "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass"),',
    '("ARTIFACT_DIFF_CONTRACT_SELF_TEST_CHECK", ["scripts/zigux/check-artifact-diff-contract.py", "--self-test"], "ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass"),',
    '("ARTIFACT_DIFF_CONTRACT_CHECK", ["scripts/zigux/check-artifact-diff-contract.py"], "ARTIFACT_DIFF_CONTRACT=pass"),',
]

EXPECTED_HISTORICAL_GAP_MARKERS = [
    "The broader Phase 4 validator, build, and bitmap replay companions are still repo-reality gaps in this run",
    "The remaining shared reminder follow-up from the older mixed-readback packet is now narrower: `zigux/tests/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/README.md` now align on the recovered note pair, the returned helper-contract and checker packet, the direct local-only perf packet, and the roadmap-backed `atomic64_diff` pair, while the validator, build, and bitmap replay companions remain the only authenticated-readback gaps in this handoff.",
    "`Documentation/zigux/artifact-diff.md`",
    "`scripts/zigux/check-artifact-diff-contract.py`",
    "`scripts/zigux/validate-phase4.py`",
]

EXPECTED_WORKFLOW_REPLAY_MARKERS = [
    "run: python3 scripts/zigux/artifact_diff.py --self-test",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
]

EXPECTED_SELF_TEST_CASES = [
    "catalog_shape",
    "validator_marker_round_trip",
    "validator_marker_drift",
    "historical_gap_marker_round_trip",
    "historical_gap_marker_drift",
    "historical_gap_note_missing",
    "workflow_marker_round_trip",
    "workflow_marker_drift",
    "workflow_missing",
]


def assert_markers(text: str, markers: list[str], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise AssertionError(f"{label} markers missing: {missing}")


def read_text(root: Path, rel: Path, *, missing_label: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"current tree is missing {missing_label}: {rel.as_posix()}") from exc


def check(root: Path) -> tuple[str, list[str]]:
    workflow_text = read_text(
        root,
        WORKFLOW_REL,
        missing_label="the Phase 4 bootstrap workflow",
    )
    assert_markers(
        workflow_text,
        EXPECTED_WORKFLOW_REPLAY_MARKERS,
        "workflow_surface",
    )

    validator_path = root / VALIDATOR_REL
    if validator_path.exists():
        validator_text = read_text(
            root,
            VALIDATOR_REL,
            missing_label="the historical validator replay target",
        )
        assert_markers(
            validator_text,
            EXPECTED_VALIDATOR_REPLAY_MARKERS,
            "validator_surface",
        )
        return "validator_present", EXPECTED_VALIDATOR_REPLAY_MARKERS

    note_text = read_text(
        root,
        NOTE_REL,
        missing_label="the Phase 4 historical validator handoff note",
    )
    assert_markers(
        note_text,
        EXPECTED_HISTORICAL_GAP_MARKERS,
        "historical_gap_surface",
    )
    return "historical_target_missing", EXPECTED_HISTORICAL_GAP_MARKERS


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_workflow_fixture(root: Path) -> None:
    write(
        root / WORKFLOW_REL,
        "\n".join(
            [
                "name: zigux-bootstrap",
                *EXPECTED_WORKFLOW_REPLAY_MARKERS,
            ]
        )
        + "\n",
    )


def make_validator_fixture(root: Path) -> None:
    write(
        root / VALIDATOR_REL,
        "\n".join(EXPECTED_VALIDATOR_REPLAY_MARKERS) + "\n",
    )
    write(root / NOTE_REL, "# note placeholder\n")
    make_workflow_fixture(root)


def make_historical_gap_fixture(root: Path) -> None:
    write(
        root / NOTE_REL,
        "\n".join(
            [
                "# Phase 4 Reversible Delivery Evidence",
                *EXPECTED_HISTORICAL_GAP_MARKERS,
            ]
        )
        + "\n",
    )
    make_workflow_fixture(root)


def run_self_test() -> int:
    if len(set(EXPECTED_SELF_TEST_CASES)) != len(EXPECTED_SELF_TEST_CASES):
        raise AssertionError(
            f"self-test catalog must stay unique: {EXPECTED_SELF_TEST_CASES}"
        )

    covered_cases: list[str] = ["catalog_shape"]

    with tempfile.TemporaryDirectory(prefix="phase4-validator-replays-") as tmp:
        root = Path(tmp)

        make_validator_fixture(root)
        mode, markers = check(root)
        if mode != "validator_present" or markers != EXPECTED_VALIDATOR_REPLAY_MARKERS:
            raise AssertionError("validator_marker_round_trip")
        covered_cases.append("validator_marker_round_trip")

        make_validator_fixture(root)
        write(root / VALIDATOR_REL, EXPECTED_VALIDATOR_REPLAY_MARKERS[0] + "\n")
        try:
            check(root)
        except AssertionError:
            covered_cases.append("validator_marker_drift")
        else:
            raise AssertionError("expected validator_marker_drift to fail closed")

        root = Path(tmp)
        for rel in (VALIDATOR_REL, NOTE_REL):
            path = root / rel
            if path.exists():
                path.unlink()
        make_historical_gap_fixture(root)
        mode, markers = check(root)
        if (
            mode != "historical_target_missing"
            or markers != EXPECTED_HISTORICAL_GAP_MARKERS
        ):
            raise AssertionError("historical_gap_marker_round_trip")
        covered_cases.append("historical_gap_marker_round_trip")

        make_historical_gap_fixture(root)
        write(root / NOTE_REL, EXPECTED_HISTORICAL_GAP_MARKERS[1] + "\n")
        try:
            check(root)
        except AssertionError:
            covered_cases.append("historical_gap_marker_drift")
        else:
            raise AssertionError("expected historical_gap_marker_drift to fail closed")

        note_path = root / NOTE_REL
        if note_path.exists():
            note_path.unlink()
        try:
            check(root)
        except RuntimeError as exc:
            expected = (
                "current tree is missing the Phase 4 historical validator handoff "
                f"note: {NOTE_REL.as_posix()}"
            )
            if str(exc) != expected:
                raise AssertionError(
                    "historical gap note missing message drifted: "
                    f"expected {expected!r}, got {str(exc)!r}"
                ) from exc
            covered_cases.append("historical_gap_note_missing")
        else:
            raise AssertionError("expected historical_gap_note_missing to fail closed")

        make_historical_gap_fixture(root)
        mode, markers = check(root)
        if (
            mode != "historical_target_missing"
            or markers != EXPECTED_HISTORICAL_GAP_MARKERS
        ):
            raise AssertionError("workflow_marker_round_trip")
        covered_cases.append("workflow_marker_round_trip")

        make_historical_gap_fixture(root)
        write(root / WORKFLOW_REL, EXPECTED_WORKFLOW_REPLAY_MARKERS[0] + "\n")
        try:
            check(root)
        except AssertionError:
            covered_cases.append("workflow_marker_drift")
        else:
            raise AssertionError("expected workflow_marker_drift to fail closed")

        make_historical_gap_fixture(root)
        workflow_path = root / WORKFLOW_REL
        if workflow_path.exists():
            workflow_path.unlink()
        try:
            check(root)
        except RuntimeError as exc:
            expected = (
                "current tree is missing the Phase 4 bootstrap workflow: "
                f"{WORKFLOW_REL.as_posix()}"
            )
            if str(exc) != expected:
                raise AssertionError(
                    "workflow missing message drifted: "
                    f"expected {expected!r}, got {str(exc)!r}"
                ) from exc
            covered_cases.append("workflow_missing")
        else:
            raise AssertionError("expected workflow_missing to fail closed")

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
            "Check that the Phase 4 artifact-diff validator replay surface either "
            "keeps the shipped validator hooks or explicitly stays historical in "
            "the current repo-reality handoff."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to inspect.",
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
        mode, markers = check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS=fail: {exc}", file=sys.stderr)
        return 1
    except AssertionError as exc:
        print(f"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS=fail: {exc}", file=sys.stderr)
        return 1

    print("PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS=pass")
    print(f"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MODE={mode}")
    print(
        "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT="
        f"{len(markers)}"
    )
    print(
        "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKERS="
        + ",".join(markers)
    )
    print(
        "PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT="
        f"{len(EXPECTED_WORKFLOW_REPLAY_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
