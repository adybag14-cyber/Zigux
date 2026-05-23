#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
STUDY_ONLY_ACCOUNTING_PATH = Path(
    "Documentation/zigux/phase15-study-only-anchor-accounting.md"
)
PARITY_SCORECARD_PATH = Path("Documentation/zigux/phase15-parity-scorecard.md")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")

REQUIRED_PATHS = (
    FREEZE_MAP_PATH,
    STUDY_ONLY_ACCOUNTING_PATH,
    PARITY_SCORECARD_PATH,
    HANDOFF_NOTE_PATH,
)

FREEZE_MAP_MARKERS = (
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "shared reminder surfaces that summarize freeze posture",
    "route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
)

STUDY_ONLY_ACCOUNTING_MARKERS = (
    "PHASE15_STATUS=study_only_accounting_slice_landed",
    "PHASE15_LANE_KEY=P15-L05",
    "PHASE15_SLICE=study-only-anchor-accounting",
    "current-master-readback-2026-05-20",
    "### `kernel/workqueue.c`",
    "### `kernel/trace/ring_buffer.c`",
    "tracked outside the freeze-in-C scorecard and outside blocked status-change rows",
    "this note is an inventory and handoff surface, not an approval record",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
)

PARITY_SCORECARD_MARKERS = (
    "study-only anchors tracked outside this scorecard: `2`",
    "study-only anchors remain outside this scorecard until a lane asks for a status-bucket review",
)

HANDOFF_NOTE_MARKERS = (
    "keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`",
    "if future work touches `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, keep it study-only unless a smaller-than-boundary seam is explicitly recorded in the governance packet",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    packets = (
        (FREEZE_MAP_PATH, FREEZE_MAP_MARKERS),
        (STUDY_ONLY_ACCOUNTING_PATH, STUDY_ONLY_ACCOUNTING_MARKERS),
        (PARITY_SCORECARD_PATH, PARITY_SCORECARD_MARKERS),
        (HANDOFF_NOTE_PATH, HANDOFF_NOTE_MARKERS),
    )
    for rel, markers in packets:
        text = _read(root / rel)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel}:{marker}")

    return failures


def _sample_freeze_map() -> str:
    return """# Zigux Freeze Map

## Study / Boundary Only
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

## Governance For Freeze-Map Changes
- shared reminder surfaces that summarize freeze posture, especially `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`, must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md` when they summarize that boundary set
- study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md` so the `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` inventory does not drift from this file
"""


def _sample_study_only_accounting() -> str:
    return """# Phase 15 Study-Only Anchor Accounting

## Status

- `PHASE15_STATUS=study_only_accounting_slice_landed`
- `PHASE15_LANE_KEY=P15-L05`
- `PHASE15_SLICE=study-only-anchor-accounting`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-20`

## Study-Only Anchor Inventory

### `kernel/workqueue.c`
- current Phase 15 role: tracked outside the freeze-in-C scorecard and outside blocked status-change rows

### `kernel/trace/ring_buffer.c`
- current Phase 15 role: tracked outside the freeze-in-C scorecard and outside blocked status-change rows

## Accounting Rules

- this note is an inventory and handoff surface, not an approval record
- if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it
"""


def _sample_parity_scorecard() -> str:
    return """# Phase 15 Parity Scorecard

## Aggregate Metrics

- study-only anchors tracked outside this scorecard: `2`

## Accounting Rules

- study-only anchors remain outside this scorecard until a lane asks for a status-bucket review
"""


def _sample_handoff_note() -> str:
    return """# Phase 15 Handoff Next Steps Survey

## Current governance posture to preserve

- keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`

## Next bounded future targets

5. if future work touches `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, keep it study-only unless a smaller-than-boundary seam is explicitly recorded in the governance packet
"""


def _seed(root: Path) -> None:
    _write(root / FREEZE_MAP_PATH, _sample_freeze_map())
    _write(root / STUDY_ONLY_ACCOUNTING_PATH, _sample_study_only_accounting())
    _write(root / PARITY_SCORECARD_PATH, _sample_parity_scorecard())
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_study_only_anchor_accounting_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        cases = (
            (FREEZE_MAP_PATH, FREEZE_MAP_MARKERS[3]),
            (STUDY_ONLY_ACCOUNTING_PATH, STUDY_ONLY_ACCOUNTING_MARKERS[3]),
            (PARITY_SCORECARD_PATH, PARITY_SCORECARD_MARKERS[0]),
            (HANDOFF_NOTE_PATH, HANDOFF_NOTE_MARKERS[1]),
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

    print("PHASE15_STUDY_ONLY_ANCHOR_ACCOUNTING_SELF_TEST=pass")
    print(f"PHASE15_STUDY_ONLY_ANCHOR_ACCOUNTING_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Phase 15 study-only anchor accounting packet stays aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the Zigux Phase 15 governance files",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run synthetic fixture coverage for the study-only accounting guard",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_STUDY_ONLY_ANCHOR_ACCOUNTING=pass")
    print(f"PHASE15_STUDY_ONLY_ANCHOR_ACCOUNTING_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print("PHASE15_STUDY_ONLY_ANCHOR_ACCOUNTING_ANCHOR_COUNT=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
