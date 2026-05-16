#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_README_PATH = Path("Documentation/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
GAP_NOTE_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")

DOCS_README_OVERCLAIM_MARKERS = (
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-parity-scorecard-survey.md`",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_build.zig`",
)

MISSING_PATHS = (
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard-survey.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
)

REQUIRED_NOTE_MARKERS = (
    "`Documentation/zigux/README.md`",
    "`zigux/tests/README.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`scripts/zigux/check-phase15-shared-summary-gap.py`",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_build.zig`",
)

TESTS_README_PHASE15_MARKER = "Phase 15 review packet"
HANDOFF_NOTE_MARKER = "PHASE15_STATUS=handoff_next_steps_survey_landed"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing file: {path}") from exc


def collect_gap_failures(root: Path) -> list[str]:
    docs_readme = _read_text(root / DOCS_README_PATH)
    tests_readme = _read_text(root / TESTS_README_PATH)
    gap_note = _read_text(root / GAP_NOTE_PATH)
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)

    failures: list[str] = []

    for marker in DOCS_README_OVERCLAIM_MARKERS:
        if marker not in docs_readme:
            failures.append(
                "docs-root Phase 15 overclaim marker disappeared and the gap note needs refresh: "
                + marker
            )

    if TESTS_README_PHASE15_MARKER in tests_readme:
        failures.append(
            "tests-root Phase 15 packet marker now exists, so the shared-summary gap note must be narrowed: "
            + TESTS_README_PHASE15_MARKER
        )

    for relative_path in MISSING_PATHS:
        if (root / relative_path).exists():
            failures.append(
                f"previously missing Phase 15 path now exists and the gap note must be refreshed: {relative_path}"
            )

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in gap_note:
            failures.append(f"gap note is missing required marker: {marker}")

    if HANDOFF_NOTE_MARKER not in handoff_note:
        failures.append(
            "handoff note is missing the landed status marker: " + HANDOFF_NOTE_MARKER
        )

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_docs_readme() -> str:
    return """# Zigux Documentation

Phase 15 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-freeze-map-governance.md` - `Documentation/zigux/phase15-architecture-council-review-process.md` - `Documentation/zigux/phase15-parity-scorecard-survey.md` - `Documentation/zigux/phase15-parity-scorecard.md` - `Documentation/zigux/phase15-indefinite-c-policy.md` - `Documentation/zigux/phase15-readiness-gate-survey.md` - `Documentation/zigux/phase15-handoff-next-steps-survey.md` - `Documentation/zigux/phase15-governance-lane-sequencing.md` - `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-shared-summary-gap.py`, `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_build.zig`
"""


def _sample_tests_readme() -> str:
    return """# zigux/tests

Phase 13 review packet
  * `Documentation/zigux/phase13-contributor-workflow-guide.md`
"""


def _sample_gap_note() -> str:
    return """# Phase 15 Shared Summary Gap

`Documentation/zigux/README.md`
`zigux/tests/README.md`
`Documentation/zigux/phase15-freeze-map-governance.md`
`Documentation/zigux/phase15-parity-scorecard.md`
`Documentation/zigux/phase15-study-only-anchor-accounting.md`
`Documentation/zigux/phase15-handoff-next-steps-survey.md`
`scripts/zigux/check-phase15-shared-summary-gap.py`
`scripts/zigux/validate-phase15.py`
`zigux/tests/phase15_build.zig`
"""


def _sample_handoff_note() -> str:
    return """# Phase 15 Handoff Next Steps Survey

PHASE15_STATUS=handoff_next_steps_survey_landed
"""


def _seed_missing_layout(root: Path) -> None:
    _write(root / DOCS_README_PATH, _sample_docs_readme())
    _write(root / TESTS_README_PATH, _sample_tests_readme())
    _write(root / GAP_NOTE_PATH, _sample_gap_note())
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
    _write(root / "Documentation/zigux/phase15-freeze-map-governance.md", "freeze-map packet\n")
    _write(root / "Documentation/zigux/phase15-parity-scorecard.md", "scorecard packet\n")
    _write(root / "Documentation/zigux/phase15-study-only-anchor-accounting.md", "study-only packet\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _seed_missing_layout(root)
        if collect_gap_failures(root):
            raise AssertionError("baseline missing-layout fixture should pass")

        materialized_root = root / "materialized"
        _seed_missing_layout(materialized_root)
        _write(materialized_root / "zigux/tests/phase15_build.zig", "test {}\n")
        failures = collect_gap_failures(materialized_root)
        if len(failures) != 1 or "zigux/tests/phase15_build.zig" not in failures[0]:
            raise AssertionError(f"materialized-path failure missing expected marker: {failures}")

        tests_root = root / "tests-root"
        _seed_missing_layout(tests_root)
        _write(tests_root / TESTS_README_PATH, "# zigux/tests\n\nPhase 15 review packet\n")
        failures = collect_gap_failures(tests_root)
        if len(failures) != 1 or TESTS_README_PHASE15_MARKER not in failures[0]:
            raise AssertionError(f"tests-root failure missing expected marker: {failures}")

        note_root = root / "note"
        _seed_missing_layout(note_root)
        _write(
            note_root / GAP_NOTE_PATH,
            _sample_gap_note().replace("`zigux/tests/phase15_build.zig`\n", ""),
        )
        failures = collect_gap_failures(note_root)
        if len(failures) != 1 or "`zigux/tests/phase15_build.zig`" not in failures[0]:
            raise AssertionError(f"gap-note marker failure missing expected marker: {failures}")

        handoff_root = root / "handoff"
        _seed_missing_layout(handoff_root)
        _write(handoff_root / HANDOFF_NOTE_PATH, "# Phase 15 Handoff Next Steps Survey\n")
        failures = collect_gap_failures(handoff_root)
        if len(failures) != 1 or HANDOFF_NOTE_MARKER not in failures[0]:
            raise AssertionError(f"handoff-note marker failure missing expected marker: {failures}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that the Phase 15 shared-summary gap note still matches the current docs-root, "
            "tests-root, handoff-note, and repo-reality drift."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing Documentation/zigux, scripts/zigux, and zigux/tests",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic repo layouts",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        failures = collect_gap_failures(args.root)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 shared-summary gap check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
