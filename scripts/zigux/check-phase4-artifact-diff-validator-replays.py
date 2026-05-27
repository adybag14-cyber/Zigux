#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_REL = Path("scripts/zigux/validate-phase4.py")
NOTE_REL = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
ARTIFACT_DIFF_NOTE_REL = Path("Documentation/zigux/artifact-diff.md")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

EXPECTED_VALIDATOR_REPLAY_MARKERS = [
    'CheckSpec(\n        "phase4-artifact-diff-helper-self-test",\n        ("python", "scripts/zigux/artifact_diff.py", "--self-test"),\n    ),',
    'CheckSpec(\n        "phase4-artifact-diff-contract-self-test",\n        ("python", "scripts/zigux/check-artifact-diff-contract.py", "--self-test"),\n    ),',
    'CheckSpec(\n        "phase4-artifact-diff-contract",\n        ("python", "scripts/zigux/check-artifact-diff-contract.py"),\n    ),',
    'CheckSpec(\n        "phase4-artifact-diff-determinism-self-test",\n        ("python", "scripts/zigux/check-phase4-artifact-diff-determinism.py", "--self-test"),\n    ),',
    'CheckSpec(\n        "phase4-artifact-diff-determinism",\n        ("python", "scripts/zigux/check-phase4-artifact-diff-determinism.py"),\n    ),',
    'CheckSpec(\n        "phase4-artifact-diff-validator-replays-self-test",\n        ("python", "scripts/zigux/check-phase4-artifact-diff-validator-replays.py", "--self-test"),\n    ),',
    'CheckSpec(\n        "phase4-artifact-diff-validator-replays",\n        ("python", "scripts/zigux/check-phase4-artifact-diff-validator-replays.py"),\n    ),',
]

EXPECTED_VALIDATOR_OUTPUT_MARKERS = [
    '"phase4-artifact-diff-contract-self-test": (',
    '"ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass",',
    '"ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=24",',
    '"ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES="',
    '"phase4-artifact-diff-contract": (',
    '"ARTIFACT_DIFF_CONTRACT=pass",',
    '"ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=25",',
    '"ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=5",',
    '"ARTIFACT_DIFF_CONTRACT_CASE_COUNT=30",',
    '"phase4-artifact-diff-determinism-self-test": (',
    '"PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST=pass",',
    '"PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT=13",',
    '"PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES="',
    '"phase4-artifact-diff-determinism": (',
    '"PHASE4_ARTIFACT_DIFF_DETERMINISM=pass",',
    '"PHASE4_ARTIFACT_DIFF_DETERMINISM_DIRECT_PACKET_MEMBERS=11",',
    '"PHASE4_ARTIFACT_DIFF_DETERMINISM_AUTH_MISSING_BROADER_COMPANIONS=0",',
    '"phase4-artifact-diff-validator-replays-self-test": (',
    '"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST=pass",',
    '"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14",',
    '"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASES="',
    '"phase4-artifact-diff-validator-replays": (',
    '"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS=pass",',
    '"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MODE=validator_present",',
    '"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7",',
    '"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKERS="',
    '"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=14",',
]

EXPECTED_REPO_REALITY_HANDOFF_MARKERS = [
    "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
    "Direct authenticated contents reads in this runtime now return `scripts/zigux/validate-phase4.py` directly, while `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still flap on that same route; public raw fallback rereads continue to return the full set on current `master`, matching the broader review packet's recovered note-and-checker companions.",
    "The remaining shared reminder follow-up from the older mixed-readback packet is now narrower: `zigux/tests/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `scripts/zigux/check-phase4-tests-readme-packet.py` should align on the recovered note pair, the returned helper-contract and checker packet, the direct local-only perf packet, the roadmap-backed `atomic64_diff` pair, the directly returned validator, and the still-public-raw-returned build and bitmap replay companions, while exact blob-pin refresh for that broader packet remains the remaining authenticated-readback gap in this handoff.",
    "`Documentation/zigux/artifact-diff.md`",
    "`scripts/zigux/check-artifact-diff-contract.py`",
    "`scripts/zigux/validate-phase4.py`",
]

EXPECTED_ARTIFACT_DIFF_NOTE_MARKERS = [
    "`scripts/zigux/check-phase4-artifact-diff-validator-replays.py`",
    "validator hook set explicit or falls back to the narrower repo-reality handoff markers when exact validator readback is unavailable",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASES=catalog_shape,validator_marker_round_trip,validator_helper_marker_drift,validator_marker_drift,validator_replay_marker_drift,repo_reality_handoff_round_trip,repo_reality_handoff_drift,repo_reality_handoff_note_missing,workflow_marker_round_trip,workflow_make_route_marker_drift,workflow_marker_drift,workflow_missing,artifact_diff_note_round_trip,artifact_diff_note_marker_drift`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=14`",
]

EXPECTED_WORKFLOW_REPLAY_MARKERS = [
    "- name: Run Phase 4 artifact-diff contract make route",
    "run: make -C zigux phase4-artifact-diff-contract",
    "- name: Self-test current Phase 4 artifact-diff helper",
    "run: python3 scripts/zigux/artifact_diff.py --self-test",
    "- name: Self-test current Phase 4 artifact-diff contract checker",
    "run: python3 scripts/zigux/check-artifact-diff-contract.py --self-test",
    "- name: Check current Phase 4 artifact-diff contract packet",
    "run: python3 scripts/zigux/check-artifact-diff-contract.py",
    "- name: Self-test current Phase 4 artifact-diff determinism checker",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "- name: Check current Phase 4 artifact-diff determinism packet",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "- name: Self-test current Phase 4 artifact-diff validator replay checker",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test",
    "- name: Check current Phase 4 artifact-diff validator replay packet",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
]

EXPECTED_SELF_TEST_CASES = [
    "catalog_shape",
    "validator_marker_round_trip",
    "validator_helper_marker_drift",
    "validator_marker_drift",
    "validator_replay_marker_drift",
    "repo_reality_handoff_round_trip",
    "repo_reality_handoff_drift",
    "repo_reality_handoff_note_missing",
    "workflow_marker_round_trip",
    "workflow_make_route_marker_drift",
    "workflow_marker_drift",
    "workflow_missing",
    "artifact_diff_note_round_trip",
    "artifact_diff_note_marker_drift",
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
    artifact_diff_note_text = read_text(
        root,
        ARTIFACT_DIFF_NOTE_REL,
        missing_label="the broader artifact-diff review note",
    )
    assert_markers(
        artifact_diff_note_text,
        EXPECTED_ARTIFACT_DIFF_NOTE_MARKERS,
        "artifact_diff_note_surface",
    )

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
            missing_label="the validator replay target",
        )
        assert_markers(
            validator_text,
            EXPECTED_VALIDATOR_REPLAY_MARKERS,
            "validator_surface",
        )
        assert_markers(
            validator_text,
            EXPECTED_VALIDATOR_OUTPUT_MARKERS,
            "validator_output_marker_surface",
        )
        return "validator_present", EXPECTED_VALIDATOR_REPLAY_MARKERS

    note_text = read_text(
        root,
        NOTE_REL,
        missing_label="the Phase 4 repo-reality handoff note",
    )
    assert_markers(
        note_text,
        EXPECTED_REPO_REALITY_HANDOFF_MARKERS,
        "repo_reality_handoff_surface",
    )
    return "repo_reality_handoff", EXPECTED_REPO_REALITY_HANDOFF_MARKERS


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


def make_artifact_diff_note_fixture(root: Path) -> None:
    write(
        root / ARTIFACT_DIFF_NOTE_REL,
        "\n".join(
            [
                "# Zigux Artifact-Diff Notes",
                *EXPECTED_ARTIFACT_DIFF_NOTE_MARKERS,
            ]
        )
        + "\n",
    )


def make_validator_fixture(root: Path) -> None:
    write(
        root / VALIDATOR_REL,
        "\n".join([
            *EXPECTED_VALIDATOR_REPLAY_MARKERS,
            *EXPECTED_VALIDATOR_OUTPUT_MARKERS,
        ]) + "\n",
    )
    write(root / NOTE_REL, "# note placeholder\n")
    make_artifact_diff_note_fixture(root)
    make_workflow_fixture(root)


def make_repo_reality_handoff_fixture(root: Path) -> None:
    write(
        root / NOTE_REL,
        "\n".join(
            [
                "# Phase 4 Reversible Delivery Evidence",
                *EXPECTED_REPO_REALITY_HANDOFF_MARKERS,
            ]
        )
        + "\n",
    )
    make_artifact_diff_note_fixture(root)
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
        write(root / VALIDATOR_REL, "\n".join(EXPECTED_VALIDATOR_REPLAY_MARKERS[1:] + EXPECTED_VALIDATOR_OUTPUT_MARKERS) + "\n")
        try:
            check(root)
        except AssertionError:
            covered_cases.append("validator_helper_marker_drift")
        else:
            raise AssertionError("expected validator_helper_marker_drift to fail closed")

        make_validator_fixture(root)
        write(root / VALIDATOR_REL, EXPECTED_VALIDATOR_REPLAY_MARKERS[0] + "\n")
        try:
            check(root)
        except AssertionError:
            covered_cases.append("validator_marker_drift")
        else:
            raise AssertionError("expected validator_marker_drift to fail closed")

        make_validator_fixture(root)
        trimmed_markers = [
            marker
            for marker in EXPECTED_VALIDATOR_REPLAY_MARKERS + EXPECTED_VALIDATOR_OUTPUT_MARKERS
            if marker != '"PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKERS="'
        ]
        write(root / VALIDATOR_REL, "\n".join(trimmed_markers) + "\n")
        try:
            check(root)
        except AssertionError:
            covered_cases.append("validator_replay_marker_drift")
        else:
            raise AssertionError("expected validator_replay_marker_drift to fail closed")

        root = Path(tmp)
        for rel in (VALIDATOR_REL, NOTE_REL):
            path = root / rel
            if path.exists():
                path.unlink()
        make_repo_reality_handoff_fixture(root)
        mode, markers = check(root)
        if (
            mode != "repo_reality_handoff"
            or markers != EXPECTED_REPO_REALITY_HANDOFF_MARKERS
        ):
            raise AssertionError("repo_reality_handoff_round_trip")
        covered_cases.append("repo_reality_handoff_round_trip")

        make_repo_reality_handoff_fixture(root)
        write(root / NOTE_REL, EXPECTED_REPO_REALITY_HANDOFF_MARKERS[1] + "\n")
        try:
            check(root)
        except AssertionError:
            covered_cases.append("repo_reality_handoff_drift")
        else:
            raise AssertionError("expected repo_reality_handoff_drift to fail closed")

        note_path = root / NOTE_REL
        if note_path.exists():
            note_path.unlink()
        try:
            check(root)
        except RuntimeError as exc:
            expected = (
                "current tree is missing the Phase 4 repo-reality handoff "
                f"note: {NOTE_REL.as_posix()}"
            )
            if str(exc) != expected:
                raise AssertionError(
                    "repo-reality handoff note missing message drifted: "
                    f"expected {expected!r}, got {str(exc)!r}"
                ) from exc
            covered_cases.append("repo_reality_handoff_note_missing")
        else:
            raise AssertionError("expected repo_reality_handoff_note_missing to fail closed")

        make_repo_reality_handoff_fixture(root)
        mode, markers = check(root)
        if (
            mode != "repo_reality_handoff"
            or markers != EXPECTED_REPO_REALITY_HANDOFF_MARKERS
        ):
            raise AssertionError("workflow_marker_round_trip")
        covered_cases.append("workflow_marker_round_trip")

        make_repo_reality_handoff_fixture(root)
        write(root / WORKFLOW_REL, "\n".join(EXPECTED_WORKFLOW_REPLAY_MARKERS[2:]) + "\n")
        try:
            check(root)
        except AssertionError:
            covered_cases.append("workflow_make_route_marker_drift")
        else:
            raise AssertionError("expected workflow_make_route_marker_drift to fail closed")

        make_repo_reality_handoff_fixture(root)
        write(root / WORKFLOW_REL, EXPECTED_WORKFLOW_REPLAY_MARKERS[0] + "\n")
        try:
            check(root)
        except AssertionError:
            covered_cases.append("workflow_marker_drift")
        else:
            raise AssertionError("expected workflow_marker_drift to fail closed")

        make_repo_reality_handoff_fixture(root)
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

        make_validator_fixture(root)
        mode, markers = check(root)
        if mode != "validator_present" or markers != EXPECTED_VALIDATOR_REPLAY_MARKERS:
            raise AssertionError("artifact_diff_note_round_trip")
        covered_cases.append("artifact_diff_note_round_trip")

        make_validator_fixture(root)
        write(root / ARTIFACT_DIFF_NOTE_REL, EXPECTED_ARTIFACT_DIFF_NOTE_MARKERS[0] + "\n")
        try:
            check(root)
        except AssertionError:
            covered_cases.append("artifact_diff_note_marker_drift")
        else:
            raise AssertionError("expected artifact_diff_note_marker_drift to fail closed")

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
            "keeps the shipped validator hook set explicit or keeps the current repo-reality "
            "handoff truthful when exact validator readback is unavailable."
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
