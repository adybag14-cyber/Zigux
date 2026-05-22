#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path.cwd()
CHECKER_REL = Path("scripts/zigux/check-phase4-artifact-diff-validator-replays.py")
NOTE_REL = Path("Documentation/zigux/artifact-diff.md")
SURVEY_REL = Path("Documentation/zigux/phase4-artifact-diff-tooling-survey.md")
MATRIX_REL = Path("Documentation/zigux/phase4-validation-matrix.md")

NOTE_MARKERS = (
    "`scripts/zigux/check-phase4-artifact-diff-validator-replays.py`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7`",
    "`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=14`",
)

SURVEY_MARKERS = (
    "`scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test`",
    "`scripts/zigux/check-phase4-artifact-diff-validator-replays.py`",
    "validator-replay checker",
    "shared validator packet",
)

MATRIX_MARKERS = (
    "### `scripts/zigux/check-phase4-artifact-diff-validator-replays.py`",
    "bounded validator-first artifact-diff replay inventory",
    "`python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test`",
    "`python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py`",
)

CHECKER_MARKERS = (
    'EXPECTED_ARTIFACT_DIFF_NOTE_MARKERS = [',
    '"`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_SELF_TEST_CASE_COUNT=14`",',
    '"`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_MARKER_COUNT=7`",',
    '"`PHASE4_ARTIFACT_DIFF_VALIDATOR_REPLAYS_WORKFLOW_MARKER_COUNT=14`",',
    'EXPECTED_SELF_TEST_CASES = [',
    '"validator_marker_round_trip",',
    '"artifact_diff_note_marker_drift",',
)

SELF_TEST_CASES = (
    "round_trip",
    "note_marker_drift",
    "survey_marker_drift",
    "matrix_marker_drift",
    "checker_marker_drift",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the landed Phase 4 artifact-diff validator-replay "
            "checker stays aligned with its current documentation and survey "
            "surfaces."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing required file: {rel.as_posix()}") from exc


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required markers: {missing}")


def check(root: Path) -> None:
    require_markers(read_text(root, NOTE_REL), NOTE_MARKERS, NOTE_REL.as_posix())
    require_markers(read_text(root, SURVEY_REL), SURVEY_MARKERS, SURVEY_REL.as_posix())
    require_markers(read_text(root, MATRIX_REL), MATRIX_MARKERS, MATRIX_REL.as_posix())
    require_markers(read_text(root, CHECKER_REL), CHECKER_MARKERS, CHECKER_REL.as_posix())


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_root(root: Path) -> None:
    write_text(root / NOTE_REL, "\n".join(NOTE_MARKERS) + "\n")
    write_text(root / SURVEY_REL, "\n".join(SURVEY_MARKERS) + "\n")
    write_text(root / MATRIX_REL, "\n".join(MATRIX_MARKERS) + "\n")
    write_text(root / CHECKER_REL, "\n".join(CHECKER_MARKERS) + "\n")


def expect_failure(root: Path, label: str) -> str:
    try:
        check(root)
    except RuntimeError:
        return label
    raise AssertionError(f"expected {label} to fail")


def run_self_test() -> int:
    covered: list[str] = []
    with tempfile.TemporaryDirectory(prefix="phase4_artifact_diff_validator_surface_") as tmp_dir:
        root = Path(tmp_dir)

        fixture_root(root)
        check(root)
        covered.append("round_trip")

        fixture_root(root)
        write_text(
            root / NOTE_REL,
            "\n".join(marker for marker in NOTE_MARKERS if "MARKER_COUNT=7" not in marker) + "\n",
        )
        covered.append(expect_failure(root, "note_marker_drift"))

        fixture_root(root)
        write_text(
            root / SURVEY_REL,
            "\n".join(marker for marker in SURVEY_MARKERS if "--self-test" not in marker) + "\n",
        )
        covered.append(expect_failure(root, "survey_marker_drift"))

        fixture_root(root)
        write_text(
            root / MATRIX_REL,
            "\n".join(
                marker
                for marker in MATRIX_MARKERS
                if "bounded validator-first artifact-diff replay inventory" not in marker
            )
            + "\n",
        )
        covered.append(expect_failure(root, "matrix_marker_drift"))

        fixture_root(root)
        write_text(
            root / CHECKER_REL,
            "\n".join(marker for marker in CHECKER_MARKERS if '"artifact_diff_note_marker_drift"' not in marker) + "\n",
        )
        covered.append(expect_failure(root, "checker_marker_drift"))

    if tuple(covered) != SELF_TEST_CASES:
        raise AssertionError(
            f"self-test catalog drifted: expected {SELF_TEST_CASES}, got {tuple(covered)}"
        )

    print("PHASE4_ARTIFACT_DIFF_VALIDATOR_SURFACE_ALIGNMENT_SELF_TEST=pass")
    print(
        "PHASE4_ARTIFACT_DIFF_VALIDATOR_SURFACE_ALIGNMENT_SELF_TEST_CASE_COUNT="
        f"{len(SELF_TEST_CASES)}"
    )
    print(
        "PHASE4_ARTIFACT_DIFF_VALIDATOR_SURFACE_ALIGNMENT_SELF_TEST_CASES="
        + ",".join(SELF_TEST_CASES)
    )
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_ARTIFACT_DIFF_VALIDATOR_SURFACE_ALIGNMENT=fail: {exc}")
        return 1

    print("PHASE4_ARTIFACT_DIFF_VALIDATOR_SURFACE_ALIGNMENT=pass")
    print("PHASE4_ARTIFACT_DIFF_VALIDATOR_SURFACE_ALIGNMENT_FILE_COUNT=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
