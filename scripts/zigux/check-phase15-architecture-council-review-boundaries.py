#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
DECISION_TEMPLATE_PATH = Path(
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md"
)
DECISION_INDEX_PATH = Path("Documentation/zigux/phase15-architecture-council-decision-index.md")
STUDY_ONLY_ACCOUNTING_PATH = Path("Documentation/zigux/phase15-study-only-anchor-accounting.md")

FREEZE_IN_C_ANCHORS = (
    "`kernel/sched/core.c`",
    "`mm/page_alloc.c`",
    "`kernel/rcu/tree.c`",
    "`net/core/skbuff.c`",
)
STUDY_ONLY_ANCHORS = (
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
)
REQUIRED_REVIEW_FIELDS = (
    "exact Linux anchor path",
    "required approver set",
    "rollback owner",
    "validation gate summary",
    "evidence archive path",
    "rollback threshold",
    "`retired_from_active_discussion` state",
    "reopen triggers",
    "trigger-specific evidence refresh",
    "governance lane sequencing link or explicit scope note",
    "study-only anchor accounting link or explicit freeze-map-anchor confirmation",
    "written rationale",
)


def _read_text(root: Path, relative: Path) -> str:
    return (root / relative).read_text(encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    freeze_map = _read_text(root, FREEZE_MAP_PATH)
    review_checklist = _read_text(root, REVIEW_CHECKLIST_PATH)
    review_process = _read_text(root, REVIEW_PROCESS_PATH)
    decision_template = _read_text(root, DECISION_TEMPLATE_PATH)
    decision_index = _read_text(root, DECISION_INDEX_PATH)
    study_only_accounting = _read_text(root, STUDY_ONLY_ACCOUNTING_PATH)

    failures: list[str] = []

    for anchor in FREEZE_IN_C_ANCHORS:
        if anchor not in freeze_map:
            failures.append(f"freeze map is missing freeze-in-C anchor {anchor}")

    for anchor in STUDY_ONLY_ANCHORS:
        if anchor not in freeze_map:
            failures.append(f"freeze map is missing study-only anchor {anchor}")
        if anchor not in review_process:
            failures.append(f"review-process note is missing study-only boundary anchor {anchor}")
        if anchor not in decision_template:
            failures.append(f"decision-record template is missing study-only boundary anchor {anchor}")
        if anchor not in decision_index:
            failures.append(f"decision index is missing study-only boundary anchor {anchor}")
        if anchor not in study_only_accounting:
            failures.append(f"study-only accounting note is missing anchor {anchor}")

    for marker in (
        "`Documentation/zigux/phase15-architecture-council-review-process.md`",
        "`Documentation/zigux/phase15-freeze-map-governance.md`",
        "`Documentation/zigux/phase15-parity-scorecard.md`",
        "`Documentation/zigux/phase15-indefinite-c-policy.md`",
        "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
        "required approver set",
        "evidence archive path",
        "rollback threshold",
        "`retired_from_active_discussion` state",
        "trigger-specific evidence refresh",
    ):
        if marker not in freeze_map:
            failures.append(f"freeze map is missing Architecture Council boundary marker {marker}")

    checklist_prompt = (
        "if a freeze-map anchor is entering Architecture Council status review"
    )
    if checklist_prompt not in review_checklist:
        failures.append("review checklist is missing the Architecture Council entry-review prompt")
    for marker in (
        "`Documentation/zigux/phase15-architecture-council-review-process.md`",
        "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
        "owners of the exact Architecture Council field inventory",
        "stay-in-C closeout record",
        "reopen-evidence details",
        "`Documentation/zigux/phase15-indefinite-c-policy.md`",
        "retained blocker posture",
        "trigger-specific evidence refresh",
        "return-to-blocked wording",
        "`Documentation/zigux/freeze-map.md`",
        "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    ):
        if marker not in review_checklist:
            failures.append(f"review checklist is missing boundary marker {marker}")

    for marker in (
        "`PHASE15_STATUS=architecture_council_review_process_landed`",
        "`PHASE15_LANE_KEY=P15-L08`",
        "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
        "`Documentation/zigux/phase15-architecture-council-decision-index.md`",
        "no freeze-map anchor has an Architecture Council approval for a status change",
        "The Architecture Council may close a request only in one of these bounded ways:",
        "A closed stay-in-C record is not approval debt.",
    ):
        if marker not in review_process:
            failures.append(f"review-process note is missing marker {marker}")

    for field in REQUIRED_REVIEW_FIELDS:
        if field not in review_process:
            failures.append(f"review-process note is missing required review field {field}")
        if field not in decision_template:
            failures.append(f"decision-record template is missing required review field {field}")

    if (
        "not candidates for a freeze-in-C status review through this note"
        not in review_process
    ):
        failures.append("review-process note is missing the study-only exclusion rule")
    if (
        "Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`"
        not in decision_template
    ):
        failures.append("decision-record template is missing the study-only exclusion rule")

    for marker in (
        "`PHASE15_STATUS=architecture_council_decision_index_landed`",
        "`PHASE15_LANE_KEY=P15-L09`",
        "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
        "`scripts/zigux/check-phase15-architecture-council-decision-index.py`",
        "approved status-bucket changes recorded on current `master`: none",
        "stay-in-C closeout decision records recorded on current `master`: none",
        "no freeze-map anchor has an Architecture Council approval for a status change on current `master`",
        "until the freeze map changes, because they remain study-only anchors rather than freeze-in-C status-review records",
    ):
        if marker not in decision_index:
            failures.append(f"decision index is missing marker {marker}")

    for marker in (
        "`PHASE15_STATUS=study_only_accounting_slice_landed`",
        "`PHASE15_LANE_KEY=P15-L05`",
        "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
        "The roadmap keeps two deep-core areas in a narrower posture than the four freeze-in-C anchors",
        "### `kernel/workqueue.c`",
        "- posture: `study_only`",
        "### `kernel/trace/ring_buffer.c`",
    ):
        if marker not in study_only_accounting:
            failures.append(f"study-only accounting note is missing marker {marker}")

    return failures


def _write_text(root: Path, relative: Path, content: str) -> None:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    _write_text(
        root,
        FREEZE_MAP_PATH,
        """# Zigux Freeze Map

## Freeze In C Initially
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

## Study / Boundary Only
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

## Governance For Freeze-Map Changes
- freeze-map status-change requests must route through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- any lane that touches a listed anchor must declare required approver set, rollback owner, validation gate summary, evidence archive path, rollback threshold, `retired_from_active_discussion` state, reopen triggers, trigger-specific evidence refresh, and written rationale
- shared reminder surfaces that summarize freeze posture must route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md`
""",
    )
    _write_text(
        root,
        REVIEW_CHECKLIST_PATH,
        """# Zigux Review Checklist

* if a freeze-map anchor is entering Architecture Council status review, does this checklist keep the shared entry-review prompt explicit while `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-architecture-council-decision-record-template.md` remain the owners of the exact Architecture Council field inventory, stay-in-C closeout record, and reopen-evidence details, and `Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording?
* if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`?
""",
    )
    _write_text(
        root,
        REVIEW_PROCESS_PATH,
        """# Phase 15 Architecture Council Review Process

- `PHASE15_STATUS=architecture_council_review_process_landed`
- `PHASE15_LANE_KEY=P15-L08`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- this note exists beside `Documentation/zigux/phase15-architecture-council-decision-index.md`
- no freeze-map anchor has an Architecture Council approval for a status change

## Required review packet
- exact Linux anchor path
- required approver set
- rollback owner
- validation gate summary
- evidence archive path
- rollback threshold
- `retired_from_active_discussion` state
- reopen triggers
- trigger-specific evidence refresh
- governance lane sequencing link or explicit scope note
- study-only anchor accounting link or explicit freeze-map-anchor confirmation
- written rationale

## Study-only boundary
`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain boundary-study context routed through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`, not candidates for a freeze-in-C status review through this note.

## Review outcomes
The Architecture Council may close a request only in one of these bounded ways:
- keep the anchor in `freeze_in_c`
- reopen review later with narrower evidence
- approve a status-bucket change in a separately linked decision record

## Stay-in-C closeout rule
A closed stay-in-C record is not approval debt.
""",
    )
    _write_text(
        root,
        DECISION_TEMPLATE_PATH,
        """# Phase 15 Architecture Council Decision Record Template

## Record Metadata
- `PHASE15_PROVENANCE_MODE=dated_master_readback`

## Anchor And Ownership
- exact Linux anchor path:
- required approver set:
- rollback owner:

## Validation And Evidence
- validation gate summary:
- evidence archive path:
- rollback threshold:

## Stay-In-C Closeout
- `retired_from_active_discussion` state:
- reopen triggers:
- trigger-specific evidence refresh:
- governance lane sequencing link or explicit scope note:

## Supporting Context
- study-only anchor accounting link or explicit freeze-map-anchor confirmation:
- written rationale:

## Usage Rules
Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.
""",
    )
    _write_text(
        root,
        DECISION_INDEX_PATH,
        """# Phase 15 Architecture Council Decision Index

- `PHASE15_STATUS=architecture_council_decision_index_landed`
- `PHASE15_LANE_KEY=P15-L09`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- `scripts/zigux/check-phase15-architecture-council-decision-index.py`
- approved status-bucket changes recorded on current `master`: none
- stay-in-C closeout decision records recorded on current `master`: none
- no freeze-map anchor has an Architecture Council approval for a status change on current `master`
- `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay outside this index until the freeze map changes, because they remain study-only anchors rather than freeze-in-C status-review records
""",
    )
    _write_text(
        root,
        STUDY_ONLY_ACCOUNTING_PATH,
        """# Phase 15 Study-Only Anchor Accounting

- `PHASE15_STATUS=study_only_accounting_slice_landed`
- `PHASE15_LANE_KEY=P15-L05`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- The roadmap keeps two deep-core areas in a narrower posture than the four freeze-in-C anchors.

### `kernel/workqueue.c`
- posture: `study_only`

### `kernel/trace/ring_buffer.c`
- posture: `study_only`
""",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_arch_council_boundaries_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        bad_root = root / "broken"
        write_sample_root(bad_root)
        broken_template = (bad_root / DECISION_TEMPLATE_PATH).read_text(encoding="utf-8")
        (bad_root / DECISION_TEMPLATE_PATH).write_text(
            broken_template.replace(
                "study-only anchor accounting link or explicit freeze-map-anchor confirmation:\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        failures = collect_failures(bad_root)
        expected = [
            "decision-record template is missing required review field study-only anchor accounting link or explicit freeze-map-anchor confirmation"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected template failure set: {failures}")

    print("PHASE15_ARCHITECTURE_COUNCIL_REVIEW_BOUNDARIES_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that the Phase 15 Architecture Council boundary packet keeps "
            "freeze-map, review-process, template, decision-index, and study-only "
            "rules aligned."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing Documentation/zigux",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the checker against synthetic boundary fixtures",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a current-like sample root for focused validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"WROTE_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    result = {
        "status": "pass",
        "freeze_in_c_anchor_count": len(FREEZE_IN_C_ANCHORS),
        "study_only_anchor_count": len(STUDY_ONLY_ANCHORS),
        "required_review_field_count": len(REQUIRED_REVIEW_FIELDS),
    }
    print("PHASE15_ARCHITECTURE_COUNCIL_REVIEW_BOUNDARIES=pass")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())