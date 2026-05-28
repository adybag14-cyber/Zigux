#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

FREEZE_MAP_REL = "Documentation/zigux/freeze-map.md"
HANDOFF_NOTE_REL = "Documentation/zigux/phase15-handoff-next-steps-survey.md"
SHARED_GAP_REL = "Documentation/zigux/phase15-shared-summary-gap.md"
STUDY_ONLY_REL = "Documentation/zigux/phase15-study-only-anchor-accounting.md"

REQUIRED_FILES = (
    FREEZE_MAP_REL,
    HANDOFF_NOTE_REL,
    SHARED_GAP_REL,
    STUDY_ONLY_REL,
)

FREEZE_MAP_MARKERS = (
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`Documentation/zigux/phase15-shared-summary-gap.md`",
    "must keep the directly materialized validator, tests-root reminder, and shared build companion aligned as landed governance evidence while describing only the still-missing dedicated `phase15*` wrapper routes and shared-CI companions as repo-reality gaps on current `master`",
    "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
)

HANDOFF_NOTE_MARKERS = (
    "`Documentation/zigux/phase15-shared-summary-gap.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "keep the two roadmap study-only anchors parked",
    "treat broader docs-root, checklist, scripts-root, tests-root, and dedicated-build Phase 15 wording drift as truthfulness gaps, not as already-landed evidence",
    "if the freeze-map anchor set or any blocker disposition changes, reopen `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, and `Documentation/zigux/phase15-parity-scorecard.md` before widening this note",
)

SHARED_GAP_MARKERS = (
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "if docs-root, checklist, scripts-root, tests-root, the Architecture Council review-process owner note, the decision-record template, the Architecture Council decision index, the deep-core blocker survey, the Architecture Council packet checker, readiness note, handoff note, the checklist-specific study-only anchor summary boundary, or adjacent stay-in-C wording drifts, fix only the smallest truthful reminder surface instead of widening into freeze-map approval or deep-core implementation claims",
    "the stay-in-C companion changes enough to force a smaller shared-summary refresh",
)

STUDY_ONLY_MARKERS = (
    "# Phase 15 Study-Only Anchor Accounting",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "posture: `study_only`",
    "this note is an inventory and handoff surface, not an approval record",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    for rel, markers in (
        (FREEZE_MAP_REL, FREEZE_MAP_MARKERS),
        (HANDOFF_NOTE_REL, HANDOFF_NOTE_MARKERS),
        (SHARED_GAP_REL, SHARED_GAP_MARKERS),
        (STUDY_ONLY_REL, STUDY_ONLY_MARKERS),
    ):
        text = _read(root / rel)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel}:{marker}")

    return failures


def _seed(root: Path) -> None:
    _write(
        root / FREEZE_MAP_REL,
        """# Zigux Freeze Map

## Study / Boundary Only
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

## Governance For Freeze-Map Changes
- shared Phase 15 handoff and gap notes, especially `Documentation/zigux/phase15-handoff-next-steps-survey.md` and `Documentation/zigux/phase15-shared-summary-gap.md`, must keep the directly materialized validator, tests-root reminder, and shared build companion aligned as landed governance evidence while describing only the still-missing dedicated `phase15*` wrapper routes and shared-CI companions as repo-reality gaps on current `master`
- study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md` so the `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` inventory does not drift from this file
""",
    )
    _write(
        root / HANDOFF_NOTE_REL,
        """# Phase 15 Handoff Next Steps Survey

- `Documentation/zigux/phase15-shared-summary-gap.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- keep the two roadmap study-only anchors parked
- treat broader docs-root, checklist, scripts-root, tests-root, and dedicated-build Phase 15 wording drift as truthfulness gaps, not as already-landed evidence
- if the freeze-map anchor set or any blocker disposition changes, reopen `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, and `Documentation/zigux/phase15-parity-scorecard.md` before widening this note
""",
    )
    _write(
        root / SHARED_GAP_REL,
        """# Phase 15 Shared Summary Gap

- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- if docs-root, checklist, scripts-root, tests-root, the Architecture Council review-process owner note, the decision-record template, the Architecture Council decision index, the deep-core blocker survey, the Architecture Council packet checker, readiness note, handoff note, the checklist-specific study-only anchor summary boundary, or adjacent stay-in-C wording drifts, fix only the smallest truthful reminder surface instead of widening into freeze-map approval or deep-core implementation claims
- the stay-in-C companion changes enough to force a smaller shared-summary refresh
""",
    )
    _write(
        root / STUDY_ONLY_REL,
        """# Phase 15 Study-Only Anchor Accounting

## Study-Only Anchor Inventory

### `kernel/workqueue.c`
- posture: `study_only`

### `kernel/trace/ring_buffer.c`
- posture: `study_only`

## Accounting Rules
- this note is an inventory and handoff surface, not an approval record
- if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it
""",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_freeze_map_handoff_gap_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        cases = (
            (FREEZE_MAP_REL, FREEZE_MAP_MARKERS[0]),
            (HANDOFF_NOTE_REL, HANDOFF_NOTE_MARKERS[2]),
            (SHARED_GAP_REL, SHARED_GAP_MARKERS[2]),
            (STUDY_ONLY_REL, STUDY_ONLY_MARKERS[5]),
        )

        for rel, marker in cases:
            case_root = root / f"case_{case_count}"
            _seed(case_root)
            text = _read(case_root / rel)
            _write(case_root / rel, text.replace(marker, "", 1))
            failures = collect_failures(case_root)
            expected = [f"missing_marker:{rel}:{marker}"]
            if failures != expected:
                raise AssertionError(f"unexpected failures for {rel}: {failures}")
            case_count += 1

    print("PHASE15_FREEZE_MAP_HANDOFF_GAP_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE15_FREEZE_MAP_HANDOFF_GAP_ALIGNMENT_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 freeze-map gap posture stays aligned with the handoff, shared-gap, and study-only notes."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the Zigux Phase 15 governance docs",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run synthetic fixture coverage for the freeze-map handoff-gap guard",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 freeze-map handoff-gap alignment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
