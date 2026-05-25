#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

DOCS_README_REL = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
FREEZE_MAP_REL = "Documentation/zigux/freeze-map.md"
STUDY_ONLY_REL = "Documentation/zigux/phase15-study-only-anchor-accounting.md"
LANE_SEQ_REL = "Documentation/zigux/phase15-governance-lane-sequencing.md"
SHARED_GAP_REL = "Documentation/zigux/phase15-shared-summary-gap.md"

REQUIRED_FILES = (
    DOCS_README_REL,
    REVIEW_CHECKLIST_REL,
    FREEZE_MAP_REL,
    STUDY_ONLY_REL,
    LANE_SEQ_REL,
    SHARED_GAP_REL,
)

DOCS_README_MARKERS = (
    "Phase 15 notes",
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/check-phase15-scripts-readme-alignment.py`",
    "`zigux/tests/phase15_build.zig`",
    "without implying any Architecture Council approval for a freeze-map status change",
    "`make -C zigux phase15` reruns the same parked governance packet",
    "no Architecture Council approval is recorded yet for a freeze-map status change",
)

REVIEW_CHECKLIST_MARKERS = (
    "if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?",
    "if the change touches the shared Phase 15 governance packet",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit as study-only boundary anchors rather than delivery-ready runtime evidence",
)

FREEZE_MAP_MARKERS = (
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "shared reminder surfaces that summarize freeze posture",
    "`Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`",
    "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
)

STUDY_ONLY_MARKERS = (
    "# Phase 15 Study-Only Anchor Accounting",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "this note is an inventory and handoff surface, not an approval record",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
    "no Architecture Council approval is currently recorded for a deep-core status change",
)

LANE_SEQ_MARKERS = (
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory",
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces",
    "`zigux/tests/phase15_build.zig`",
    "the dedicated-build companion still remains a repo-reality gap on current `master`",
)

SHARED_GAP_MARKERS = (
    "- `Documentation/zigux/README.md`",
    "- `Documentation/zigux/review-checklist.md`",
    "- `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "if docs-root, checklist, scripts-root, tests-root, the Architecture Council review-process owner note, the decision-record template, readiness note, handoff note, the checklist-specific study-only anchor summary boundary, or adjacent stay-in-C wording drifts, fix only the smallest truthful reminder surface instead of widening into freeze-map approval or deep-core implementation claims",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


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
        (LANE_SEQ_REL, LANE_SEQ_MARKERS),
        (SHARED_GAP_REL, SHARED_GAP_MARKERS),
    ):
        text = _read(root / rel)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel}:{marker}")

    return failures


def _sample_docs_readme() -> str:
    return """# Zigux Documentation

Phase 15 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-freeze-map-governance.md` - `Documentation/zigux/phase15-architecture-council-review-process.md` - `Documentation/zigux/phase15-parity-scorecard-survey.md` - `Documentation/zigux/phase15-parity-scorecard.md` - `Documentation/zigux/phase15-indefinite-c-policy.md` - `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_build.zig`, `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, and `zigux/Makefile` keep the current parked governance packet reviewable without implying any Architecture Council approval for a freeze-map status change.
- `make -C zigux phase15` reruns the same parked governance packet, and no Architecture Council approval is recorded yet for a freeze-map status change.
"""


def _sample_review_checklist() -> str:
    return """# Zigux Review Checklist

  * if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?
  * if the change touches the shared Phase 15 governance packet, do `Documentation/zigux/freeze-map.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, and `Documentation/zigux/review-checklist.md` still agree on the current maintenance-mode governance packet, keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit as study-only boundary anchors rather than delivery-ready runtime evidence, and avoid implying any Architecture Council approval or freeze-map status change that the current packet does not record?
"""


def _sample_freeze_map() -> str:
    return """# Zigux Freeze Map

## Study / Boundary Only
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

## Governance For Freeze-Map Changes
- shared reminder surfaces that summarize freeze posture, especially `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`, must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md` when they summarize that boundary set
- study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md` so the `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` inventory does not drift from this file
"""


def _sample_study_only() -> str:
    return """# Phase 15 Study-Only Anchor Accounting

## Current Repo Reality
- no Architecture Council approval is currently recorded for a deep-core status change

## Study-Only Anchor Inventory
### `kernel/workqueue.c`
- posture: `study_only`

### `kernel/trace/ring_buffer.c`
- posture: `study_only`

## Accounting Rules
- this note is an inventory and handoff surface, not an approval record
- if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it
"""


def _sample_lane_seq() -> str:
    return """# Phase 15 Governance Lane Sequencing

- current repo reality: the core Phase 15 governance notes are landed, the dedicated review-process manifest is landed, the dedicated governance-lane sequencing manifest plus focused replay are landed, the focused parity-scorecard machine-readable companion plus focused replay are landed, the dedicated handoff manifest plus focused handoff-specific replay plus focused handoff-note checker are landed, the focused indefinite-C lane-owner companion is landed, the focused review-checklist study-only alignment checker is landed, the dedicated validator-first companion `scripts/zigux/validate-phase15.py` is directly materialized, the dedicated deep-core blocker survey is now landed, but the dedicated-build companion still remains a repo-reality gap on current `master`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory that stays outside the freeze-in-C scorecard and blocked status-change rows
- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces that may summarize the parked packet, but they do not own freeze-map status decisions themselves
- `zigux/tests/phase15_build.zig`
"""


def _sample_shared_gap() -> str:
    return """# Phase 15 Shared Summary Gap

## Current shared-summary watchpoints
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`

## Recovery rule
- if docs-root, checklist, scripts-root, tests-root, the Architecture Council review-process owner note, the decision-record template, readiness note, handoff note, the checklist-specific study-only anchor summary boundary, or adjacent stay-in-C wording drifts, fix only the smallest truthful reminder surface instead of widening into freeze-map approval or deep-core implementation claims
"""


def _seed(root: Path) -> None:
    _write(root / DOCS_README_REL, _sample_docs_readme())
    _write(root / REVIEW_CHECKLIST_REL, _sample_review_checklist())
    _write(root / FREEZE_MAP_REL, _sample_freeze_map())
    _write(root / STUDY_ONLY_REL, _sample_study_only())
    _write(root / LANE_SEQ_REL, _sample_lane_seq())
    _write(root / SHARED_GAP_REL, _sample_shared_gap())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_docs_root_freeze_boundaries_") as tmp_dir:
        root = Path(tmp_dir)
        _seed(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        cases = (
            (DOCS_README_REL, "`zigux/tests/phase15_build.zig`"),
            (REVIEW_CHECKLIST_REL, REVIEW_CHECKLIST_MARKERS[0]),
            (FREEZE_MAP_REL, "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`"),
            (STUDY_ONLY_REL, "this note is an inventory and handoff surface, not an approval record"),
            (LANE_SEQ_REL, "`Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory"),
            (SHARED_GAP_REL, "- `Documentation/zigux/review-checklist.md`"),
        )

        for rel, marker in cases:
            case_root = root / f"case_{case_count}"
            _seed(case_root)
            _write(case_root / rel, _read(case_root / rel).replace(marker, "", 1))
            failures = collect_failures(case_root)
            expected = [f"missing_marker:{rel}:{marker}"]
            if failures != expected:
                raise AssertionError(f"unexpected failures for {rel}: {failures}")
            case_count += 1

    print("PHASE15_DOCS_ROOT_FREEZE_BOUNDARIES_SELF_TEST=pass")
    print(f"PHASE15_DOCS_ROOT_FREEZE_BOUNDARIES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 docs-root freeze-boundary packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run synthetic fixture coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 docs-root freeze-boundary check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
