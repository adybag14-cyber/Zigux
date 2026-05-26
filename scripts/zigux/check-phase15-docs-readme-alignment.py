#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_README_PATH = Path("Documentation/zigux/README.md")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
SHARED_GAP_NOTE_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
LANE_SEQ_NOTE_PATH = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")

DOCS_REQUIRED_MARKERS = (
    "Phase 14 notes",
    "`Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
    "Phase 15 notes",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`Documentation/zigux/phase15-shared-summary-gap.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`scripts/zigux/check-phase15-docs-readme-alignment.py`",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_build.zig`",
)

DOCS_FORBIDDEN_MARKERS = ()

HANDOFF_REQUIRED_MARKERS = (
    "`Documentation/zigux/README.md`, which now carries a dedicated Phase 15 reminder and should be reread with `scripts/zigux/check-phase15-docs-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the directly materialized governance packet whenever broad docs-root wording drifts",
    "keep the landed docs-root Phase 15 reminder surface `Documentation/zigux/README.md` aligned with `scripts/zigux/check-phase15-docs-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the directly materialized governance packet, and treat it as a shared-summary follow-through surface now that the dedicated wording exists there while wrapper-route and shared-CI gaps remain tracked separately",
)

SHARED_GAP_REQUIRED_MARKERS = (
    "## Current shared-summary watchpoints",
    "`Documentation/zigux/README.md` now carries the broad Phase 15 reminder surface and should be reread with `scripts/zigux/check-phase15-docs-readme-alignment.py`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, and the directly materialized governance packet whenever that docs-root summary drifts",
    "if docs-root, checklist, scripts-root, tests-root, the Architecture Council review-process owner note, the decision-record template, readiness note, handoff note, the checklist-specific study-only anchor summary boundary, or adjacent stay-in-C wording drifts, fix only the smallest truthful reminder surface instead of widening into freeze-map approval or deep-core implementation claims",
)

LANE_SEQ_REQUIRED_MARKERS = (
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces that may summarize the parked packet, but they do not own freeze-map status decisions themselves",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in (
        DOCS_README_PATH,
        HANDOFF_NOTE_PATH,
        SHARED_GAP_NOTE_PATH,
        LANE_SEQ_NOTE_PATH,
    ):
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    docs_readme = _read(root / DOCS_README_PATH)
    handoff_note = _read(root / HANDOFF_NOTE_PATH)
    shared_gap_note = _read(root / SHARED_GAP_NOTE_PATH)
    lane_seq_note = _read(root / LANE_SEQ_NOTE_PATH)

    for marker in DOCS_REQUIRED_MARKERS:
        if marker not in docs_readme:
            failures.append(f"docs_readme:missing:{marker}")

    for marker in DOCS_FORBIDDEN_MARKERS:
        if marker in docs_readme:
            failures.append(f"docs_readme:unexpected_phase15_marker:{marker}")

    for marker in HANDOFF_REQUIRED_MARKERS:
        if marker not in handoff_note:
            failures.append(f"handoff:missing:{marker}")

    for marker in SHARED_GAP_REQUIRED_MARKERS:
        if marker not in shared_gap_note:
            failures.append(f"shared_gap:missing:{marker}")

    for marker in LANE_SEQ_REQUIRED_MARKERS:
        if marker not in lane_seq_note:
            failures.append(f"lane_seq:missing:{marker}")

    return failures


def _sample_docs_readme() -> str:
    return """# Zigux Documentation

Phase 14 notes
- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`

Phase 15 notes
- `Documentation/zigux/phase15-readiness-gate-survey.md`
- `Documentation/zigux/phase15-governance-lane-sequencing.md`
- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- `Documentation/zigux/phase15-shared-summary-gap.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- `scripts/zigux/check-phase15-docs-readme-alignment.py`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
"""


def _sample_handoff_note() -> str:
    return """# Phase 15 Handoff Next Steps Survey

- `Documentation/zigux/README.md`, which now carries a dedicated Phase 15 reminder and should be reread with `scripts/zigux/check-phase15-docs-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the directly materialized governance packet whenever broad docs-root wording drifts
- keep the landed docs-root Phase 15 reminder surface `Documentation/zigux/README.md` aligned with `scripts/zigux/check-phase15-docs-readme-alignment.py`, `Documentation/zigux/phase15-shared-summary-gap.md`, and the directly materialized governance packet, and treat it as a shared-summary follow-through surface now that the dedicated wording exists there while wrapper-route and shared-CI gaps remain tracked separately
"""


def _sample_shared_gap_note() -> str:
    return """# Phase 15 Shared Summary Gap

## Current shared-summary watchpoints

- `Documentation/zigux/README.md` now carries the broad Phase 15 reminder surface and should be reread with `scripts/zigux/check-phase15-docs-readme-alignment.py`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, and the directly materialized governance packet whenever that docs-root summary drifts

## Recovery rule

- if docs-root, checklist, scripts-root, tests-root, the Architecture Council review-process owner note, the decision-record template, readiness note, handoff note, the checklist-specific study-only anchor summary boundary, or adjacent stay-in-C wording drifts, fix only the smallest truthful reminder surface instead of widening into freeze-map approval or deep-core implementation claims
"""


def _sample_lane_seq_note() -> str:
    return """# Phase 15 Governance Lane Sequencing

- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces that may summarize the parked packet, but they do not own freeze-map status decisions themselves
"""


def _seed(root: Path) -> None:
    _write(root / DOCS_README_PATH, _sample_docs_readme())
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
    _write(root / SHARED_GAP_NOTE_PATH, _sample_shared_gap_note())
    _write(root / LANE_SEQ_NOTE_PATH, _sample_lane_seq_note())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_docs_readme_landed_") as tmp_dir:
        root = Path(tmp_dir)
        _seed(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        missing_phase15_root = root / "missing_phase15"
        _seed(missing_phase15_root)
        _write(
            missing_phase15_root / DOCS_README_PATH,
            _sample_docs_readme().replace("- `Documentation/zigux/phase15-handoff-next-steps-survey.md`\n", "", 1),
        )
        failures = collect_failures(missing_phase15_root)
        expected = ["docs_readme:missing:`Documentation/zigux/phase15-handoff-next-steps-survey.md`"]
        if failures != expected:
            raise AssertionError(f"unexpected missing Phase 15 marker failure: {failures}")
        case_count += 1

        missing_handoff_root = root / "missing_handoff"
        _seed(missing_handoff_root)
        _write(
            missing_handoff_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                HANDOFF_REQUIRED_MARKERS[0] + "\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_handoff_root)
        expected = [f"handoff:missing:{HANDOFF_REQUIRED_MARKERS[0]}"]
        if failures != expected:
            raise AssertionError(f"unexpected handoff failure: {failures}")
        case_count += 1

        missing_shared_gap_root = root / "missing_shared_gap"
        _seed(missing_shared_gap_root)
        _write(
            missing_shared_gap_root / SHARED_GAP_NOTE_PATH,
            _sample_shared_gap_note().replace(
                "- `Documentation/zigux/README.md` now carries the broad Phase 15 reminder surface and should be reread with `scripts/zigux/check-phase15-docs-readme-alignment.py`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, and the directly materialized governance packet whenever that docs-root summary drifts\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_shared_gap_root)
        expected = [f"shared_gap:missing:{SHARED_GAP_REQUIRED_MARKERS[1]}"]
        if failures != expected:
            raise AssertionError(f"unexpected shared-gap failure: {failures}")
        case_count += 1

    print("PHASE15_DOCS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE15_DOCS_README_ALIGNMENT_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the docs-root Phase 15 reminder state matches the current shared-summary gap posture."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 docs README alignment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
