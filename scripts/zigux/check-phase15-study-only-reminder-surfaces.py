#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

FREEZE_MAP_REL = "Documentation/zigux/freeze-map.md"
DOCS_README_REL = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
STUDY_ONLY_REL = "Documentation/zigux/phase15-study-only-anchor-accounting.md"
LANE_SEQ_REL = "Documentation/zigux/phase15-governance-lane-sequencing.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
TESTS_README_REL = "zigux/tests/README.md"

REQUIRED_FILES = (
    FREEZE_MAP_REL,
    DOCS_README_REL,
    REVIEW_CHECKLIST_REL,
    STUDY_ONLY_REL,
    LANE_SEQ_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
)

FREEZE_MAP_MARKERS = (
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "shared reminder surfaces that summarize freeze posture",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
)

DOCS_README_MARKERS = (
    "keep the freeze-map boundary explicit here too",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "rather than Phase 9 runtime-substrate readiness cues",
)

REVIEW_CHECKLIST_MARKERS = (
    "if a shared reminder surface summarizes the study-only freeze-map anchors",
    "`Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence",
)

STUDY_ONLY_MARKERS = (
    "# Phase 15 Study-Only Anchor Accounting",
    "### `kernel/workqueue.c`",
    "### `kernel/trace/ring_buffer.c`",
    "- posture: `study_only`",
    "this note is an inventory and handoff surface, not an approval record",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
)

LANE_SEQ_MARKERS = (
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory",
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces",
    "but they do not own freeze-map status decisions themselves",
)

SCRIPTS_README_MARKERS = (
    "the current scripts-root governance reminder packet stays in maintenance-mode truthfulness work",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
)

TESTS_README_MARKERS = (
    "Keep the current bounded Phase 15 governance reminder explicit through",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "without implying any Architecture Council approval for a freeze-map status change or a returned validator-first build packet?",
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
        (DOCS_README_REL, DOCS_README_MARKERS),
        (REVIEW_CHECKLIST_REL, REVIEW_CHECKLIST_MARKERS),
        (STUDY_ONLY_REL, STUDY_ONLY_MARKERS),
        (LANE_SEQ_REL, LANE_SEQ_MARKERS),
        (SCRIPTS_README_REL, SCRIPTS_README_MARKERS),
        (TESTS_README_REL, TESTS_README_MARKERS),
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
""",
    )
    _write(
        root / DOCS_README_REL,
        """# Zigux Documentation

Phase 9 notes
* keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues.
""",
    )
    _write(
        root / REVIEW_CHECKLIST_REL,
        """# Zigux Review Checklist

- if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?
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
        root / SCRIPTS_README_REL,
        """# scripts/zigux

## Phase 15
- the current scripts-root governance reminder packet stays in maintenance-mode truthfulness work, keeping the landed freeze-map, readiness, handoff, parity, stay-in-C, study-only, and shared-summary surfaces aligned without implying Architecture Council approval or a deep-core port-readiness decision
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- no Architecture Council approval is currently recorded for a freeze-map status change
""",
    )
    _write(
        root / TESTS_README_REL,
        """# zigux/tests

## Phase 15 governance packet
Keep the current bounded Phase 15 governance reminder explicit through `Documentation/zigux/phase15-study-only-anchor-accounting.md`.

Tests-root reviewer prompt:
- Does the bounded Phase 15 reminder keep the directly readable governance packet aligned without implying any Architecture Council approval for a freeze-map status change or a returned validator-first build packet?
""",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_study_only_surfaces_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        cases = (
            (FREEZE_MAP_REL, FREEZE_MAP_MARKERS[2]),
            (DOCS_README_REL, DOCS_README_MARKERS[1]),
            (REVIEW_CHECKLIST_REL, REVIEW_CHECKLIST_MARKERS[2]),
            (STUDY_ONLY_REL, STUDY_ONLY_MARKERS[4]),
            (LANE_SEQ_REL, LANE_SEQ_MARKERS[0]),
            (SCRIPTS_README_REL, SCRIPTS_README_MARKERS[0]),
            (TESTS_README_REL, TESTS_README_MARKERS[2]),
        )

        case_count = 1
        for rel, marker in cases:
            case_root = root / f"case_{case_count}"
            _seed(case_root)
            _write(case_root / rel, _read(case_root / rel).replace(marker, "", 1))
            failures = collect_failures(case_root)
            expected = [f"missing_marker:{rel}:{marker}"]
            if failures != expected:
                raise AssertionError(f"unexpected failures for {rel}: {failures}")
            case_count += 1

    print("PHASE15_STUDY_ONLY_REMINDER_SURFACES_SELF_TEST=pass")
    print(f"PHASE15_STUDY_ONLY_REMINDER_SURFACES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 study-only reminder surfaces stay aligned with the freeze-map packet."
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

    print("Phase 15 study-only reminder surfaces check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
