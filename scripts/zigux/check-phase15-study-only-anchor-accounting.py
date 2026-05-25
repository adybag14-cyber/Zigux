#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

STUDY_ONLY_NOTE_REL = Path("Documentation/zigux/phase15-study-only-anchor-accounting.md")
FREEZE_MAP_REL = Path("Documentation/zigux/freeze-map.md")
FREEZE_GOVERNANCE_REL = Path("Documentation/zigux/phase15-freeze-map-governance.md")
PARITY_SCORECARD_REL = Path("Documentation/zigux/phase15-parity-scorecard.md")
HANDOFF_REL = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
SHARED_SUMMARY_REL = Path("Documentation/zigux/phase15-shared-summary-gap.md")

STUDY_ONLY_ANCHORS = (
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
)

REQUIRED_NOTE_MARKERS = (
    "PHASE15_STATUS=study_only_accounting_slice_landed",
    "PHASE15_LANE_KEY=P15-L05",
    "PHASE15_SLICE=study-only-anchor-accounting",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "current-master-readback-2026-05-23",
    "the Phase 15 freeze-map governance note",
    "the parity scorecard",
    "the governance-lane sequencing note",
    "the handoff-next-steps survey",
    "the shared-summary gap note",
    "the landed validator-first maintenance gate",
    "no Architecture Council approval is currently recorded for a deep-core status change",
    "the current governance packet is still blocker-accounting and handoff truthfulness, not port-readiness",
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

PARITY_SCORECARD_MARKERS = (
    "- study-only anchors tracked outside this scorecard: `2`",
    "- study-only anchors remain outside this scorecard until a lane asks for a status-bucket review",
)

HANDOFF_MARKERS = (
    "- keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`",
    "if future work touches `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, keep it study-only unless a smaller-than-boundary seam is explicitly recorded in the governance packet",
)

SHARED_SUMMARY_MARKERS = (
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "if docs-root, checklist, scripts-root, tests-root, the Architecture Council review-process owner note, the decision-record template, readiness note, handoff note, the checklist-specific study-only anchor summary boundary, or adjacent stay-in-C wording drifts, fix only the smallest truthful reminder surface instead of widening into freeze-map approval or deep-core implementation claims",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    required_files = (
        STUDY_ONLY_NOTE_REL,
        FREEZE_MAP_REL,
        FREEZE_GOVERNANCE_REL,
        PARITY_SCORECARD_REL,
        HANDOFF_REL,
        SHARED_SUMMARY_REL,
    )
    for rel in required_files:
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    study_only_note = _read(root / STUDY_ONLY_NOTE_REL)
    freeze_map = _read(root / FREEZE_MAP_REL)
    freeze_governance = _read(root / FREEZE_GOVERNANCE_REL)
    parity_scorecard = _read(root / PARITY_SCORECARD_REL)
    handoff = _read(root / HANDOFF_REL)
    shared_summary = _read(root / SHARED_SUMMARY_REL)

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in study_only_note:
            failures.append(f"study_only_note:missing:{marker}")

    for anchor in STUDY_ONLY_ANCHORS:
        if f"`{anchor}`" not in study_only_note:
            failures.append(f"study_only_note:missing_anchor:`{anchor}`")
        if anchor not in freeze_map:
            failures.append(f"freeze_map:missing_anchor:{anchor}")
        if anchor not in handoff:
            failures.append(f"handoff:missing_anchor:{anchor}")

    for marker in FREEZE_MAP_MARKERS:
        if marker not in freeze_map:
            failures.append(f"freeze_map:missing:{marker}")

    for marker in FREEZE_GOVERNANCE_MARKERS:
        if marker not in freeze_governance:
            failures.append(f"freeze_governance:missing:{marker}")

    for marker in PARITY_SCORECARD_MARKERS:
        if marker not in parity_scorecard:
            failures.append(f"parity_scorecard:missing:{marker}")

    for marker in HANDOFF_MARKERS:
        if marker not in handoff:
            failures.append(f"handoff:missing:{marker}")

    for marker in SHARED_SUMMARY_MARKERS:
        if marker not in shared_summary:
            failures.append(f"shared_summary:missing:{marker}")

    return failures


def _sample_study_only_note() -> str:
    return """# Phase 15 Study-Only Anchor Accounting

## Status

- `PHASE15_STATUS=study_only_accounting_slice_landed`
- `PHASE15_LANE_KEY=P15-L05`
- `PHASE15_SLICE=study-only-anchor-accounting`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-23`
- scope: keep the two roadmap-backed study-only anchors explicit beside the freeze map, the Phase 15 freeze-map governance note, the parity scorecard, the governance-lane sequencing note, the handoff-next-steps survey, the shared-summary gap note, and the landed validator-first maintenance gate without claiming a status-bucket review, a direct Zigux bridge, or an Architecture Council approval path

The roadmap keeps two deep-core areas in a narrower posture than the four freeze-in-C anchors: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only until years of narrower evidence justify anything stronger.

## Current Repo Reality

- no Architecture Council approval is currently recorded for a deep-core status change
- the current governance packet is still blocker-accounting and handoff truthfulness, not port-readiness

## Accounting Rules

- if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it
- if a future scorecard or governance note changes the reported study-only count, this note must reconcile the same anchor set directly instead of leaving the count implicit
- if the governance-lane sequencing note, handoff-next-steps survey, shared-summary gap note, or landed tests-root reminder changes how the study-only anchors are summarized, this note must stay aligned with that same two-anchor inventory and maintenance boundary

## Study-Only Anchor Inventory

### `kernel/workqueue.c`
- posture: `study_only`

### `kernel/trace/ring_buffer.c`
- posture: `study_only`

References:
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-governance-lane-sequencing.md`
- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- `Documentation/zigux/phase15-shared-summary-gap.md`
- `scripts/zigux/validate-phase15.py`
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

- reopen only when one of the packet-local conditions below becomes true:
  - the freeze-in-C or study-only anchor set changes in `Documentation/zigux/freeze-map.md`
- next future target: stay in maintenance mode unless one of those packet-local reopen conditions fires; if a future truthfulness drift is freeze-map-local, reread `Documentation/zigux/phase15-study-only-anchor-accounting.md` together with the wider packet
"""


def _sample_parity_scorecard() -> str:
    return """# Phase 15 Parity Scorecard

## Aggregate Metrics

- study-only anchors tracked outside this scorecard: `2`

## Accounting Rules

- study-only anchors remain outside this scorecard until a lane asks for a status-bucket review
"""


def _sample_handoff() -> str:
    return """# Phase 15 Handoff Next Steps Survey

## Current governance posture to preserve

- keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`

## Next bounded future targets

5. if future work touches `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, keep it study-only unless a smaller-than-boundary seam is explicitly recorded in the governance packet
"""


def _sample_shared_summary() -> str:
    return """# Phase 15 Shared Summary Gap

## Current shared-summary watchpoints

- `Documentation/zigux/phase15-study-only-anchor-accounting.md`

## Recovery rule

- if docs-root, checklist, scripts-root, tests-root, the Architecture Council review-process owner note, the decision-record template, readiness note, handoff note, the checklist-specific study-only anchor summary boundary, or adjacent stay-in-C wording drifts, fix only the smallest truthful reminder surface instead of widening into freeze-map approval or deep-core implementation claims

## Current governance posture to preserve

- keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`
"""


def _seed(root: Path) -> None:
    _write(root / STUDY_ONLY_NOTE_REL, _sample_study_only_note())
    _write(root / FREEZE_MAP_REL, _sample_freeze_map())
    _write(root / FREEZE_GOVERNANCE_REL, _sample_freeze_governance())
    _write(root / PARITY_SCORECARD_REL, _sample_parity_scorecard())
    _write(root / HANDOFF_REL, _sample_handoff())
    _write(root / SHARED_SUMMARY_REL, _sample_shared_summary())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_study_only_accounting_") as tmpdir:
        root = Path(tmpdir)

        _seed(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        missing_note_marker = root / "missing_note_marker"
        _seed(missing_note_marker)
        _write(
            missing_note_marker / STUDY_ONLY_NOTE_REL,
            _sample_study_only_note().replace(
                "- `PHASE15_LANE_KEY=P15-L05`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_note_marker)
        expected = ["study_only_note:missing:PHASE15_LANE_KEY=P15-L05"]
        if failures != expected:
            raise AssertionError(f"unexpected note-marker failure: {failures}")
        case_count += 1

        missing_freeze_anchor = root / "missing_freeze_anchor"
        _seed(missing_freeze_anchor)
        _write(
            missing_freeze_anchor / FREEZE_MAP_REL,
            _sample_freeze_map().replace("- `kernel/workqueue.c`\n", "", 1),
        )
        failures = collect_failures(missing_freeze_anchor)
        expected = [
            "freeze_map:missing_anchor:kernel/workqueue.c",
            "freeze_map:missing:- `kernel/workqueue.c`",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected freeze-anchor failure: {failures}")
        case_count += 1

        missing_scorecard_count = root / "missing_scorecard_count"
        _seed(missing_scorecard_count)
        _write(
            missing_scorecard_count / PARITY_SCORECARD_REL,
            _sample_parity_scorecard().replace(
                "- study-only anchors tracked outside this scorecard: `2`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_scorecard_count)
        expected = [
            "parity_scorecard:missing:- study-only anchors tracked outside this scorecard: `2`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected scorecard failure: {failures}")
        case_count += 1

        missing_handoff_rule = root / "missing_handoff_rule"
        _seed(missing_handoff_rule)
        _write(
            missing_handoff_rule / HANDOFF_REL,
            _sample_handoff().replace(
                "5. if future work touches `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, keep it study-only unless a smaller-than-boundary seam is explicitly recorded in the governance packet\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_handoff_rule)
        expected = [
            "handoff:missing:if future work touches `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, keep it study-only unless a smaller-than-boundary seam is explicitly recorded in the governance packet"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected handoff-rule failure: {failures}")
        case_count += 1

        missing_shared_summary = root / "missing_shared_summary"
        _seed(missing_shared_summary)
        _write(
            missing_shared_summary / SHARED_SUMMARY_REL,
            _sample_shared_summary().replace(
                "`Documentation/zigux/phase15-study-only-anchor-accounting.md`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_shared_summary)
        expected = [
            "shared_summary:missing:`Documentation/zigux/phase15-study-only-anchor-accounting.md`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected shared-summary failure: {failures}")
        case_count += 1

        missing_governance_note = root / "missing_governance_note"
        _seed(missing_governance_note)
        _write(
            missing_governance_note / STUDY_ONLY_NOTE_REL,
            _sample_study_only_note().replace(
                "the governance-lane sequencing note, ",
                "",
                1,
            ).replace(
                "- if the governance-lane sequencing note, handoff-next-steps survey, shared-summary gap note, or landed tests-root reminder changes how the study-only anchors are summarized, this note must stay aligned with that same two-anchor inventory and maintenance boundary\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_governance_note)
        expected = [
            "study_only_note:missing:the governance-lane sequencing note",
            "study_only_note:missing:if the governance-lane sequencing note, handoff-next-steps survey, shared-summary gap note, or landed tests-root reminder changes how the study-only anchors are summarized, this note must stay aligned with that same two-anchor inventory and maintenance boundary",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected governance-note failure: {failures}")
        case_count += 1

    print("PHASE15_STUDY_ONLY_ANCHOR_ACCOUNTING_SELF_TEST=pass")
    print(f"PHASE15_STUDY_ONLY_ANCHOR_ACCOUNTING_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 study-only anchor accounting note stays aligned with the freeze-map governance packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the Phase 15 documentation packet",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the synthetic study-only anchor accounting self-test",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 study-only anchor accounting check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
