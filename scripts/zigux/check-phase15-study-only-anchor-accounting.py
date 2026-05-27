#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

STUDY_ONLY_NOTE_REL = Path("Documentation/zigux/phase15-study-only-anchor-accounting.md")
FREEZE_MAP_REL = Path("Documentation/zigux/freeze-map.md")
FREEZE_GOVERNANCE_REL = Path("Documentation/zigux/phase15-freeze-map-governance.md")
PARITY_SCORECARD_JSON_REL = Path("zigux/tests/phase15_parity_scorecard.json")
HANDOFF_REL = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
SHARED_SUMMARY_REL = Path("Documentation/zigux/phase15-shared-summary-gap.md")
LANE_SEQUENCING_REL = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")

REQUIRED_FILES = (
    STUDY_ONLY_NOTE_REL,
    FREEZE_MAP_REL,
    FREEZE_GOVERNANCE_REL,
    PARITY_SCORECARD_JSON_REL,
    HANDOFF_REL,
    SHARED_SUMMARY_REL,
    LANE_SEQUENCING_REL,
)

STUDY_ONLY_ANCHORS = (
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
)

REQUIRED_NOTE_MARKERS = (
    "PHASE15_STATUS=study_only_accounting_slice_landed",
    "PHASE15_LANE_KEY=P15-L05",
    "PHASE15_SLICE=study-only-anchor-accounting",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "current-master-readback-2026-05-25",
    "the governance-lane sequencing note",
    "the handoff-next-steps survey",
    "the shared-summary gap note",
    "the current `scripts/zigux/validate-phase15.py` maintenance gate is directly materialized beside the same packet, but it does not by itself change the study-only posture",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
    "if a future scorecard or governance note changes the reported study-only count, this note must reconcile the same anchor set directly instead of leaving the count implicit",
    "if the governance-lane sequencing note, handoff-next-steps survey, shared-summary gap note, or landed tests-root reminder changes how the study-only anchors are summarized, this note must stay aligned with that same two-anchor inventory and maintenance boundary",
)

FREEZE_MAP_MARKERS = (
    "- `kernel/workqueue.c`",
    "- `kernel/trace/ring_buffer.c`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
)

FREEZE_GOVERNANCE_MARKERS = (
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "the freeze-in-C or study-only anchor set changes in `Documentation/zigux/freeze-map.md`",
)

HANDOFF_MARKERS = (
    "- keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`",
    "if future work touches `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, keep it study-only unless a smaller-than-boundary seam is explicitly recorded in the governance packet",
)

SHARED_SUMMARY_MARKERS = (
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "the checklist-specific study-only anchor summary boundary",
)

LANE_SEQUENCING_MARKERS = (
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory",
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces",
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

    study_only_note = _read(root / STUDY_ONLY_NOTE_REL)
    freeze_map = _read(root / FREEZE_MAP_REL)
    freeze_governance = _read(root / FREEZE_GOVERNANCE_REL)
    parity_scorecard = json.loads(_read(root / PARITY_SCORECARD_JSON_REL))
    handoff = _read(root / HANDOFF_REL)
    shared_summary = _read(root / SHARED_SUMMARY_REL)
    lane_sequencing = _read(root / LANE_SEQUENCING_REL)

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in study_only_note:
            failures.append(f"study_only_note:missing:{marker}")

    for anchor in STUDY_ONLY_ANCHORS:
        quoted = f"`{anchor}`"
        if quoted not in study_only_note:
            failures.append(f"study_only_note:missing_anchor:{quoted}")
        if anchor not in freeze_map:
            failures.append(f"freeze_map:missing_anchor:{anchor}")
        if anchor not in handoff:
            failures.append(f"handoff:missing_anchor:{anchor}")
        if anchor not in lane_sequencing:
            failures.append(f"lane_sequencing:missing_anchor:{anchor}")

    for marker in FREEZE_MAP_MARKERS:
        if marker not in freeze_map:
            failures.append(f"freeze_map:missing:{marker}")

    for marker in FREEZE_GOVERNANCE_MARKERS:
        if marker not in freeze_governance:
            failures.append(f"freeze_governance:missing:{marker}")

    metrics = parity_scorecard.get("metrics", {})
    if metrics.get("study_only_anchors_tracked_outside_scorecard") != 2:
        failures.append(
            "parity_scorecard_json:study_only_anchors_tracked_outside_scorecard"
        )

    for marker in HANDOFF_MARKERS:
        if marker not in handoff:
            failures.append(f"handoff:missing:{marker}")

    for marker in SHARED_SUMMARY_MARKERS:
        if marker not in shared_summary:
            failures.append(f"shared_summary:missing:{marker}")

    for marker in LANE_SEQUENCING_MARKERS:
        if marker not in lane_sequencing:
            failures.append(f"lane_sequencing:missing:{marker}")

    return failures


def _sample_study_only_note() -> str:
    return """# Phase 15 Study-Only Anchor Accounting

## Status

- `PHASE15_STATUS=study_only_accounting_slice_landed`
- `PHASE15_LANE_KEY=P15-L05`
- `PHASE15_SLICE=study-only-anchor-accounting`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-25`
- scope: keep the two roadmap-backed study-only anchors explicit beside the freeze map, the Phase 15 freeze-map governance note, the parity scorecard, the governance-lane sequencing note, the handoff-next-steps survey, the shared-summary gap note, and the landed validator-first maintenance gate without claiming a status-bucket review, a direct Zigux bridge, or an Architecture Council approval path

## Current Repo Reality

- the current `scripts/zigux/validate-phase15.py` maintenance gate is directly materialized beside the same packet, but it does not by itself change the study-only posture

## Accounting Rules

- if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it
- if a future scorecard or governance note changes the reported study-only count, this note must reconcile the same anchor set directly instead of leaving the count implicit
- if the governance-lane sequencing note, handoff-next-steps survey, shared-summary gap note, or landed tests-root reminder changes how the study-only anchors are summarized, this note must stay aligned with that same two-anchor inventory and maintenance boundary

## Study-Only Anchor Inventory

### `kernel/workqueue.c`
- posture: `study_only`

### `kernel/trace/ring_buffer.c`
- posture: `study_only`
"""


def _sample_freeze_map() -> str:
    return """# Zigux Freeze Map

## Study / Boundary Only
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

## Governance For Freeze-Map Changes
- shared reminder surfaces that summarize freeze posture, especially `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`, must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md` when they summarize that boundary set
"""


def _sample_freeze_governance() -> str:
    return """# Phase 15 Freeze-Map Governance

## Maintenance-Mode Handoff

- reopen only when one of these packet-local conditions becomes true:
  - the freeze-in-C or study-only anchor set changes in `Documentation/zigux/freeze-map.md`
- next future target: stay in maintenance mode unless one of those packet-local reopen conditions fires; if a future truthfulness drift is freeze-map-local, reread `Documentation/zigux/phase15-study-only-anchor-accounting.md` together with the wider packet
"""


def _sample_parity_scorecard_json() -> str:
    return json.dumps(
        {
            "metrics": {
                "study_only_anchors_tracked_outside_scorecard": 2,
            }
        },
        indent=2,
    ) + "\n"


def _sample_handoff() -> str:
    return """# Phase 15 Handoff Next Steps Survey

## Current governance posture to preserve

- keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`

## Next bounded future targets

6. if future work touches `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, keep it study-only unless a smaller-than-boundary seam is explicitly recorded in the governance packet
"""


def _sample_shared_summary() -> str:
    return """# Phase 15 Shared Summary Gap

## Current shared-summary watchpoints

- `Documentation/zigux/phase15-study-only-anchor-accounting.md`

## Recovery rule

- if docs-root, checklist, scripts-root, tests-root, the Architecture Council review-process owner note, the decision-record template, readiness note, handoff note, the checklist-specific study-only anchor summary boundary, or adjacent stay-in-C wording drifts, fix only the smallest truthful reminder surface instead of widening into freeze-map approval or deep-core implementation claims
"""


def _sample_lane_sequencing() -> str:
    return """# Phase 15 Governance Lane Sequencing

## Lane inventory

- `Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory that stays outside the freeze-in-C scorecard and blocked status-change rows
- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces that may summarize the parked packet, but they do not own freeze-map status decisions themselves
- the two parked study-only anchors remain `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`
"""


def write_sample_root(root: Path) -> None:
    _write(root / STUDY_ONLY_NOTE_REL, _sample_study_only_note())
    _write(root / FREEZE_MAP_REL, _sample_freeze_map())
    _write(root / FREEZE_GOVERNANCE_REL, _sample_freeze_governance())
    _write(root / PARITY_SCORECARD_JSON_REL, _sample_parity_scorecard_json())
    _write(root / HANDOFF_REL, _sample_handoff())
    _write(root / SHARED_SUMMARY_REL, _sample_shared_summary())
    _write(root / LANE_SEQUENCING_REL, _sample_lane_sequencing())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_study_only_accounting_") as tmpdir:
        root = Path(tmpdir)
        write_sample_root(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        cases = (
            (
                STUDY_ONLY_NOTE_REL,
                "study_only_note:missing:PHASE15_LANE_KEY=P15-L05",
                "`PHASE15_LANE_KEY=P15-L05`\n",
            ),
            (
                FREEZE_MAP_REL,
                "freeze_map:missing_anchor:kernel/workqueue.c",
                "`kernel/workqueue.c`\n",
            ),
            (
                PARITY_SCORECARD_JSON_REL,
                "parity_scorecard_json:study_only_anchors_tracked_outside_scorecard",
                '"study_only_anchors_tracked_outside_scorecard": 2',
            ),
            (
                HANDOFF_REL,
                "handoff:missing:- keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`",
                "- keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`\n",
            ),
            (
                SHARED_SUMMARY_REL,
                "shared_summary:missing:`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
                "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
            ),
            (
                LANE_SEQUENCING_REL,
                "lane_sequencing:missing:`Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory",
                "`Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory",
            ),
        )

        for rel, expected_failure, needle in cases:
            case_root = root / f"case_{case_count}"
            write_sample_root(case_root)
            text = _read(case_root / rel)
            _write(case_root / rel, text.replace(needle, "", 1))
            failures = collect_failures(case_root)
            if expected_failure not in failures:
                raise AssertionError(f"missing expected failure {expected_failure}: {failures}")
            case_count += 1

    print("PHASE15_STUDY_ONLY_ANCHOR_ACCOUNTING_SELF_TEST=pass")
    print(f"PHASE15_STUDY_ONLY_ANCHOR_ACCOUNTING_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 study-only anchor accounting packet stays aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the Phase 15 governance packet",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run synthetic self-tests for the study-only accounting checker",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal passing sample root for the checker",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE15_STUDY_ONLY_ANCHOR_ACCOUNTING_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_STUDY_ONLY_ANCHOR_ACCOUNTING=pass")
    print(f"PHASE15_STUDY_ONLY_ANCHOR_ACCOUNTING_REQUIRED_PATH_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE15_STUDY_ONLY_ANCHOR_ACCOUNTING_ANCHOR_COUNT={len(STUDY_ONLY_ANCHORS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
