#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

FREEZE_MAP_REL = "Documentation/zigux/freeze-map.md"
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
STUDY_ONLY_REL = "Documentation/zigux/phase15-study-only-anchor-accounting.md"
LANE_SEQ_REL = "Documentation/zigux/phase15-governance-lane-sequencing.md"
SHARED_GAP_REL = "Documentation/zigux/phase15-shared-summary-gap.md"

REQUIRED_FILES = (
    FREEZE_MAP_REL,
    REVIEW_CHECKLIST_REL,
    STUDY_ONLY_REL,
    LANE_SEQ_REL,
    SHARED_GAP_REL,
)

FREEZE_MAP_MARKERS = (
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "shared reminder surfaces that summarize freeze posture",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
)

REVIEW_CHECKLIST_MARKERS = (
    "if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?",
    "if the change touches the shared Phase 15 governance packet",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit as study-only boundary anchors rather than delivery-ready runtime evidence",
)

STUDY_ONLY_MARKERS = (
    "# Phase 15 Study-Only Anchor Accounting",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "posture: `study_only`",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
    "this note is an inventory and handoff surface, not an approval record",
)

LANE_SEQ_MARKERS = (
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory",
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces",
)

SHARED_GAP_MARKERS = (
    "`Documentation/zigux/review-checklist.md`",
    "if docs-root, checklist, scripts-root, tests-root, the Architecture Council review-process owner note, the decision-record template, readiness note, handoff note, the checklist-specific study-only anchor summary boundary, or adjacent stay-in-C wording drifts",
    "the materialized governance packet above, the Architecture Council review-process owner note, the decision-record template, the dedicated readiness manifest, the dedicated governance-lane sequencing manifest plus focused replay, the dedicated handoff manifest, the checklist-specific study-only anchor summary boundary, or the stay-in-C companion changes enough to force a smaller shared-summary refresh",
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
        (REVIEW_CHECKLIST_REL, REVIEW_CHECKLIST_MARKERS),
        (STUDY_ONLY_REL, STUDY_ONLY_MARKERS),
        (LANE_SEQ_REL, LANE_SEQ_MARKERS),
        (SHARED_GAP_REL, SHARED_GAP_MARKERS),
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
- shared reminder surfaces that summarize freeze posture, especially `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`, must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md` when they summarize that boundary set
- study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md` so the `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` inventory does not drift from this file
""",
    )
    _write(
        root / REVIEW_CHECKLIST_REL,
        """# Zigux Review Checklist

- if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?
- if the change touches the shared Phase 15 governance packet, do `Documentation/zigux/freeze-map.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, and `Documentation/zigux/review-checklist.md` still agree on the current maintenance-mode governance packet, keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit as study-only boundary anchors rather than delivery-ready runtime evidence, and avoid implying any Architecture Council approval or freeze-map status change that the current packet does not record?
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
    _write(
        root / LANE_SEQ_REL,
        """# Phase 15 Governance Lane Sequencing

- `Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory that stays outside the freeze-in-C scorecard and blocked status-change rows
- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces that may summarize the parked packet, but they do not own freeze-map status decisions themselves
""",
    )
    _write(
        root / SHARED_GAP_REL,
        """# Phase 15 Shared Summary Gap

## Current shared-summary watchpoints
- `Documentation/zigux/review-checklist.md`

## Recovery rule
- if docs-root, checklist, scripts-root, tests-root, the Architecture Council review-process owner note, the decision-record template, readiness note, handoff note, the checklist-specific study-only anchor summary boundary, or adjacent stay-in-C wording drifts, fix only the smallest truthful reminder surface instead of widening into freeze-map approval or deep-core implementation claims

## Next bounded step
- keep this note parked unless the materialized governance packet above, the Architecture Council review-process owner note, the decision-record template, the dedicated readiness manifest, the dedicated governance-lane sequencing manifest plus focused replay, the dedicated handoff manifest, the checklist-specific study-only anchor summary boundary, or the stay-in-C companion changes enough to force a smaller shared-summary refresh
""",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_review_checklist_study_only_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        cases = (
            (FREEZE_MAP_REL, FREEZE_MAP_MARKERS[2]),
            (REVIEW_CHECKLIST_REL, REVIEW_CHECKLIST_MARKERS[0]),
            (STUDY_ONLY_REL, STUDY_ONLY_MARKERS[4]),
            (LANE_SEQ_REL, LANE_SEQ_MARKERS[1]),
            (SHARED_GAP_REL, SHARED_GAP_MARKERS[1]),
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

    print("PHASE15_REVIEW_CHECKLIST_STUDY_ONLY_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE15_REVIEW_CHECKLIST_STUDY_ONLY_ALIGNMENT_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 review checklist stays aligned with freeze-map study-only boundaries."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the Zigux governance docs",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run synthetic fixture coverage for the checklist study-only boundary guard",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 review-checklist study-only alignment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
