#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


FREEZE_MAP_REL = "Documentation/zigux/freeze-map.md"
STUDY_ONLY_REL = "Documentation/zigux/phase15-study-only-anchor-accounting.md"
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
LANE_SEQ_REL = "Documentation/zigux/phase15-governance-lane-sequencing.md"
HANDOFF_REL = "Documentation/zigux/phase15-handoff-next-steps-survey.md"
SHARED_GAP_REL = "Documentation/zigux/phase15-shared-summary-gap.md"
TESTS_README_REL = "zigux/tests/README.md"
VALIDATOR_REL = "scripts/zigux/validate-phase15.py"

REQUIRED_FILES = (
    FREEZE_MAP_REL,
    STUDY_ONLY_REL,
    REVIEW_CHECKLIST_REL,
    LANE_SEQ_REL,
    HANDOFF_REL,
    SHARED_GAP_REL,
    TESTS_README_REL,
    VALIDATOR_REL,
)

EXPECTED_STUDY_ONLY_ANCHORS = [
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
]

FREEZE_MAP_MARKERS = (
    "## Study / Boundary Only",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "shared reminder surfaces that summarize freeze posture",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
)

STUDY_ONLY_MARKERS = (
    "PHASE15_STATUS=study_only_accounting_slice_landed",
    "PHASE15_SLICE=study-only-anchor-accounting",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "boundary-study target first, not a rewrite target",
    "tracked outside the freeze-in-C scorecard",
    "this note is an inventory and handoff surface, not an approval record",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
    "no Architecture Council approval is currently recorded for a deep-core status change",
    "a direct Zigux bridge for `kernel/workqueue.c`",
    "a direct Zigux bridge for `kernel/trace/ring_buffer.c`",
)

REVIEW_CHECKLIST_MARKERS = (
    "if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?",
)

LANE_SEQ_MARKERS = (
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory",
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces that may summarize the parked packet, but they do not own freeze-map status decisions themselves",
)

HANDOFF_MARKERS = (
    "keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`",
    "if future work touches `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, keep it study-only unless a smaller-than-boundary seam is explicitly recorded in the governance packet",
)

SHARED_GAP_MARKERS = (
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "if docs-root, checklist, scripts-root, tests-root, the Architecture Council review-process owner note, the decision-record template, the Architecture Council decision index, the deep-core blocker survey, the Architecture Council packet checker, readiness note, handoff note, the checklist-specific study-only anchor summary boundary, or adjacent stay-in-C wording drifts",
)

TESTS_README_MARKERS = (
    "Keep the current bounded Phase 9 reminder packet explicit through `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, and `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`.",
    "keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than runtime-substrate readiness proof in the tests root",
)

VALIDATOR_MARKERS = (
    "\"Documentation/zigux/phase15-study-only-anchor-accounting.md\"",
    "\"scripts/zigux/check-phase15-review-checklist-study-only-alignment.py\"",
    "\"phase15_review_checklist_study_only_alignment_checker_present\": True",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _extract_listed_anchors(text: str, heading: str, prefix: str) -> list[str]:
    anchors: list[str] = []
    in_section = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == heading:
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if in_section and stripped.startswith(prefix) and stripped.endswith("`"):
            anchors.append(stripped[len(prefix) : -1])
    return anchors


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    for rel, markers in (
        (FREEZE_MAP_REL, FREEZE_MAP_MARKERS),
        (STUDY_ONLY_REL, STUDY_ONLY_MARKERS),
        (REVIEW_CHECKLIST_REL, REVIEW_CHECKLIST_MARKERS),
        (LANE_SEQ_REL, LANE_SEQ_MARKERS),
        (HANDOFF_REL, HANDOFF_MARKERS),
        (SHARED_GAP_REL, SHARED_GAP_MARKERS),
        (TESTS_README_REL, TESTS_README_MARKERS),
        (VALIDATOR_REL, VALIDATOR_MARKERS),
    ):
        text = _read(root / rel)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel}:{marker}")

    freeze_map_anchors = _extract_listed_anchors(
        _read(root / FREEZE_MAP_REL), "## Study / Boundary Only", "- `"
    )
    if freeze_map_anchors != EXPECTED_STUDY_ONLY_ANCHORS:
        failures.append(
            f"study_only_anchor_mismatch:{FREEZE_MAP_REL}:{freeze_map_anchors!r}"
        )

    study_only_anchors = _extract_listed_anchors(
        _read(root / STUDY_ONLY_REL), "## Study-Only Anchor Inventory", "### `"
    )
    if study_only_anchors != EXPECTED_STUDY_ONLY_ANCHORS:
        failures.append(
            f"study_only_anchor_mismatch:{STUDY_ONLY_REL}:{study_only_anchors!r}"
        )

    return failures


def write_sample_root(root: Path) -> None:
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

## Status

- `PHASE15_STATUS=study_only_accounting_slice_landed`
- `PHASE15_SLICE=study-only-anchor-accounting`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- roadmap rule: boundary-study target first, not a rewrite target
- current role: tracked outside the freeze-in-C scorecard

## Study-Only Anchor Inventory

### `kernel/workqueue.c`
- posture: `study_only`

### `kernel/trace/ring_buffer.c`
- posture: `study_only`

## Accounting Rules

- this note is an inventory and handoff surface, not an approval record
- if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it
- no Architecture Council approval is currently recorded for a deep-core status change

## Non-Goals

- a direct Zigux bridge for `kernel/workqueue.c`
- a direct Zigux bridge for `kernel/trace/ring_buffer.c`
""",
    )
    _write(
        root / REVIEW_CHECKLIST_REL,
        """# Zigux Review Checklist

- if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?
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
        root / HANDOFF_REL,
        """# Phase 15 Handoff Next Steps Survey

## Current governance posture to preserve

- keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`

## Next bounded future targets

- if future work touches `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, keep it study-only unless a smaller-than-boundary seam is explicitly recorded in the governance packet
""",
    )
    _write(
        root / SHARED_GAP_REL,
        """# Phase 15 Shared Summary Gap

## Current shared-summary watchpoints

- `Documentation/zigux/phase15-study-only-anchor-accounting.md`

## Recovery rule

- if docs-root, checklist, scripts-root, tests-root, the Architecture Council review-process owner note, the decision-record template, the Architecture Council decision index, the deep-core blocker survey, the Architecture Council packet checker, readiness note, handoff note, the checklist-specific study-only anchor summary boundary, or adjacent stay-in-C wording drifts, fix only the smallest truthful reminder surface instead of widening into freeze-map approval or deep-core implementation claims
""",
    )
    _write(
        root / TESTS_README_REL,
        """# zigux/tests

- Keep the current bounded Phase 9 reminder packet explicit through `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, and `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`.
- keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than runtime-substrate readiness proof in the tests root
""",
    )
    _write(
        root / VALIDATOR_REL,
        """#!/usr/bin/env python3
EXPECTED_DIRECT_PACKET_PATHS = [
    \"Documentation/zigux/phase15-study-only-anchor-accounting.md\",
]
EXPECTED_PHASE15_VALIDATE_CHECKERS = [
    \"scripts/zigux/check-phase15-review-checklist-study-only-alignment.py\",
]
EXPECTED_REPO_EVIDENCE = {
    \"phase15_review_checklist_study_only_alignment_checker_present\": True,
}
""",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(
        prefix="phase15_study_only_anchor_accounting_"
    ) as tmpdir:
        root = Path(tmpdir)
        write_sample_root(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline sample should pass: {failures}")
        case_count += 1

        cases = (
            (STUDY_ONLY_REL, STUDY_ONLY_MARKERS[5]),
            (REVIEW_CHECKLIST_REL, REVIEW_CHECKLIST_MARKERS[0]),
            (LANE_SEQ_REL, LANE_SEQ_MARKERS[0]),
            (TESTS_README_REL, TESTS_README_MARKERS[1]),
            (VALIDATOR_REL, VALIDATOR_MARKERS[2]),
        )
        for rel, marker in cases:
            case_root = root / f"case_{case_count}"
            write_sample_root(case_root)
            text = _read(case_root / rel)
            _write(case_root / rel, text.replace(marker, "", 1))
            failures = collect_failures(case_root)
            expected = [f"missing_marker:{rel}:{marker}"]
            if failures != expected:
                raise AssertionError(
                    f"unexpected failures for {rel}: {failures} != {expected}"
                )
            case_count += 1

    print("PHASE15_STUDY_ONLY_ANCHOR_ACCOUNTING_SELF_TEST=pass")
    print(f"PHASE15_STUDY_ONLY_ANCHOR_ACCOUNTING_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Phase 15 study-only anchor accounting packet."
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
        help="run synthetic fixture coverage for the study-only accounting checker",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a sample current-like tree for focused replay validation",
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
    print(
        "PHASE15_STUDY_ONLY_ANCHOR_ACCOUNTING_ANCHOR_COUNT="
        f"{len(EXPECTED_STUDY_ONLY_ANCHORS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
