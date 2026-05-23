#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_README_REL = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
FREEZE_MAP_REL = "Documentation/zigux/freeze-map.md"
STUDY_ONLY_REL = "Documentation/zigux/phase15-study-only-anchor-accounting.md"

REQUIRED_FILES = (
    DOCS_README_REL,
    REVIEW_CHECKLIST_REL,
    FREEZE_MAP_REL,
    STUDY_ONLY_REL,
)

DOCS_README_MARKERS = (
    "Phase 15 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "without implying any Architecture Council approval for a freeze-map status change",
    "keep the current docs-root reminder narrowed to truthfulness maintenance rather than a fresh freeze-map status change claim",
)

REVIEW_CHECKLIST_MARKERS = (
    "if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?",
    "if the change touches the shared Phase 15 governance packet",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
)

FREEZE_MAP_MARKERS = (
    "# Zigux Freeze Map",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "shared reminder surfaces that summarize freeze posture",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
)

STUDY_ONLY_MARKERS = (
    "# Phase 15 Study-Only Anchor Accounting",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "this note is an inventory and handoff surface, not an approval record",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
    "any future status-bucket change for either anchor must update the freeze map, the Phase 15 governance note, the parity scorecard, and this study-only accounting note together",
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
        (DOCS_README_REL, DOCS_README_MARKERS),
        (REVIEW_CHECKLIST_REL, REVIEW_CHECKLIST_MARKERS),
        (FREEZE_MAP_REL, FREEZE_MAP_MARKERS),
        (STUDY_ONLY_REL, STUDY_ONLY_MARKERS),
    ):
        text = _read(root / rel)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel}:{marker}")

    return failures


def _seed(root: Path) -> None:
    _write(
        root / DOCS_README_REL,
        """# Zigux Documentation

Phase 15 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-freeze-map-governance.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/review-checklist.md`
without implying any Architecture Council approval for a freeze-map status change
keep the current docs-root reminder narrowed to truthfulness maintenance rather than a fresh freeze-map status change claim
""",
    )
    _write(
        root / REVIEW_CHECKLIST_REL,
        """# Zigux Review Checklist

- if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?
- if the change touches the shared Phase 15 governance packet, do `Documentation/zigux/freeze-map.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, and `Documentation/zigux/review-checklist.md` still agree on the current maintenance-mode governance packet?
""",
    )
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
        root / STUDY_ONLY_REL,
        """# Phase 15 Study-Only Anchor Accounting

## Study-Only Anchor Inventory
### `kernel/workqueue.c`

### `kernel/trace/ring_buffer.c`

## Accounting Rules
- this note is an inventory and handoff surface, not an approval record
- if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it
- any future status-bucket change for either anchor must update the freeze map, the Phase 15 governance note, the parity scorecard, and this study-only accounting note together
""",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_freeze_map_owner_packet_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        cases = (
            (DOCS_README_REL, DOCS_README_MARKERS[3]),
            (REVIEW_CHECKLIST_REL, REVIEW_CHECKLIST_MARKERS[0]),
            (FREEZE_MAP_REL, FREEZE_MAP_MARKERS[3]),
            (STUDY_ONLY_REL, STUDY_ONLY_MARKERS[4]),
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

    print("PHASE15_FREEZE_MAP_OWNER_PACKET_SELF_TEST=pass")
    print(f"PHASE15_FREEZE_MAP_OWNER_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 freeze-map owner surfaces stay aligned."
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
        help="run synthetic fixture coverage for the freeze-map owner packet guard",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 freeze-map owner packet check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
