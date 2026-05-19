#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
DECISION_TEMPLATE_PATH = Path(
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md"
)
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")

REQUIRED_REVIEW_FIELDS = (
    "exact Linux anchor path",
    "roadmap phase",
    "decision record ID",
    "lane owner",
    "current status bucket",
    "requested decision bucket",
    "required approver set",
    "rollback owner",
    "validation gate summary",
    "evidence archive path",
    "latest blocker disposition",
    "benchmark notes",
    "replay command",
    "rollback threshold",
    "automatic return-to-blocked trigger",
    "`retired_from_active_discussion` state",
    "reopen triggers",
    "trigger-specific evidence refresh",
    "parity scorecard link or blocker record",
    "indefinite-C policy link or explicit non-applicability note",
    "explicit non-goals",
    "written rationale",
)

STAY_IN_C_CLOSEOUT_FIELDS = (
    "the retained `freeze_in_c` decision",
    "the current blocker",
    "the required approver set",
    "`retired_from_active_discussion` state",
    "automatic return-to-blocked trigger",
    "the reopen triggers",
    "the trigger-specific evidence refresh",
    "the evidence archive path that will be refreshed before any later reopen request",
)

REOPEN_EVIDENCE_FIELDS = (
    "the exact reopen trigger being exercised",
    "refreshed evidence by path",
    "the blocker disposition being challenged",
    "the narrower seam or policy change that makes the new review safe to consider",
)

TEMPLATE_REQUIRED_MARKERS = (
    "`DECISION_RECORD_ID=<replace-with-stable-id>`",
    "`PHASE=Phase 15`",
    "`LANE_KEY=P15-L08`",
    "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
    "`SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`",
    "exact-head provenance exception note:",
    "`REVIEW_STATUS=<blocked_review|stay_in_c|approved_status_bucket_change>`",
    "Prefer the dated master readback form for parked governance and stay-in-C review packets.",
    "Only record an exact head when the linked review needs it to anchor a named published decision",
    "Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.",
    "If any required field above cannot be stated honestly, keep the request blocked and leave the C implementation as the product source of truth.",
)

FREEZE_MAP_GOVERNANCE_MARKERS = (
    "freeze-map status-change requests must route through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "decision record ID",
    "required approver set",
    "automatic return-to-blocked trigger",
    "`retired_from_active_discussion` state",
    "parity scorecard link or blocker record",
    "indefinite-C policy link or non-applicability note",
)

CHECKLIST_ENTRY_PROMPT = (
    "if a freeze-map anchor is entering Architecture Council status review"
)
CHECKLIST_BOUNDARY_MARKERS = (
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "owners of the exact Architecture Council field inventory",
    "stay-in-C closeout record",
    "reopen-evidence details",
)


def _read_text(root: Path, relative: Path) -> str:
    return (root / relative).read_text(encoding="utf-8")


def _line_containing(text: str, marker: str) -> str | None:
    for line in text.splitlines():
        if marker in line:
            return line
    return None


def collect_failures(root: Path) -> list[str]:
    review_process = _read_text(root, REVIEW_PROCESS_PATH)
    decision_template = _read_text(root, DECISION_TEMPLATE_PATH)
    review_checklist = _read_text(root, REVIEW_CHECKLIST_PATH)
    freeze_map = _read_text(root, FREEZE_MAP_PATH)

    failures: list[str] = []

    for marker in TEMPLATE_REQUIRED_MARKERS:
        if marker not in decision_template:
            failures.append(f"decision-record template is missing required marker: {marker}")

    for field in REQUIRED_REVIEW_FIELDS:
        if field not in review_process:
            failures.append(f"review-process note is missing required review field: {field}")
        if field not in decision_template:
            failures.append(f"decision-record template is missing required review field: {field}")

    for field in STAY_IN_C_CLOSEOUT_FIELDS:
        if field not in review_process:
            failures.append(f"review-process note is missing stay-in-C closeout field: {field}")
        if field not in decision_template:
            failures.append(
                f"decision-record template is missing stay-in-C closeout field: {field}"
            )

    for field in REOPEN_EVIDENCE_FIELDS:
        if field not in review_process:
            failures.append(f"review-process note is missing reopen-evidence field: {field}")
        if field not in decision_template:
            failures.append(
                f"decision-record template is missing reopen-evidence field: {field}"
            )

    for marker in FREEZE_MAP_GOVERNANCE_MARKERS:
        if marker not in freeze_map:
            failures.append(f"freeze map is missing governance marker: {marker}")

    checklist_line = _line_containing(review_checklist, CHECKLIST_ENTRY_PROMPT)
    if checklist_line is None:
        failures.append(
            "review checklist is missing the Architecture Council entry-review prompt"
        )
    else:
        for marker in CHECKLIST_BOUNDARY_MARKERS:
            if marker not in checklist_line:
                failures.append(
                    f"review checklist entry prompt is missing boundary marker: {marker}"
                )

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_files(root: Path) -> None:
    _write(
        root / REVIEW_PROCESS_PATH,
        """# Phase 15 Architecture Council Review Process

## Required review packet

- exact Linux anchor path
- roadmap phase
- decision record ID
- lane owner
- current status bucket
- requested decision bucket
- required approver set
- rollback owner
- validation gate summary
- evidence archive path
- latest blocker disposition
- benchmark notes
- replay command
- rollback threshold
- automatic return-to-blocked trigger
- `retired_from_active_discussion` state
- reopen triggers
- trigger-specific evidence refresh
- parity scorecard link or blocker record
- indefinite-C policy link or explicit non-applicability note
- explicit non-goals
- written rationale

## Stay-in-C closeout rule

- the retained `freeze_in_c` decision
- the current blocker
- the required approver set
- `retired_from_active_discussion` state
- the automatic return-to-blocked trigger
- the reopen triggers
- the trigger-specific evidence refresh
- the evidence archive path that will be refreshed before any later reopen request

## Reopen evidence rule

- the exact reopen trigger being exercised
- refreshed evidence by path
- the blocker disposition being challenged
- the narrower seam or policy change that makes the new review safe to consider
""",
    )
    _write(
        root / DECISION_TEMPLATE_PATH,
        """# Phase 15 Architecture Council Decision Record Template

- `DECISION_RECORD_ID=<replace-with-stable-id>`
- `PHASE=Phase 15`
- `LANE_KEY=P15-L08`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- `SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`
- exact-head provenance exception note:
- `REVIEW_STATUS=<blocked_review|stay_in_c|approved_status_bucket_change>`

## Anchor And Ownership

- exact Linux anchor path:
- roadmap phase:
- decision record ID:
- lane owner:
- current status bucket:
- requested decision bucket:
- required approver set:
- rollback owner:

## Validation And Evidence

- validation gate summary:
- evidence archive path:
- latest blocker disposition:
- benchmark notes:
- replay command:
- rollback threshold:

## Stay-In-C Closeout

- the retained `freeze_in_c` decision:
- the current blocker:
- the required approver set:
- `retired_from_active_discussion` state:
- automatic return-to-blocked trigger:
- the reopen triggers:
- the trigger-specific evidence refresh:
- the evidence archive path that will be refreshed before any later reopen request:

## Reopen Evidence

- the exact reopen trigger being exercised:
- refreshed evidence by path:
- the blocker disposition being challenged:
- the narrower seam or policy change that makes the new review safe to consider:

## Supporting Context

- parity scorecard link or blocker record:
- indefinite-C policy link or explicit non-applicability note:
- explicit non-goals:
- written rationale:

## Usage Rules

- Prefer the dated master readback form for parked governance and stay-in-C review packets.
- Only record an exact head when the linked review needs it to anchor a named published decision, and explain that exception in the exact-head provenance note.
- Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.
- If any required field above cannot be stated honestly, keep the request blocked and leave the C implementation as the product source of truth.
""",
    )
    _write(
        root / REVIEW_CHECKLIST_PATH,
        """# Zigux Review Checklist

- if a freeze-map anchor is entering Architecture Council status review, does this checklist keep the shared entry-review prompt explicit while `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-architecture-council-decision-record-template.md` remain the owners of the exact Architecture Council field inventory, stay-in-C closeout record, and reopen-evidence details?
""",
    )
    _write(
        root / FREEZE_MAP_PATH,
        """# Zigux Freeze Map

- freeze-map status-change requests must route through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, and keep the exact Linux anchor path, current roadmap phase, lane owner, rollback owner, current status bucket, requested decision bucket, decision record ID, required approver set, validation gate summary, evidence archive path, latest blocker disposition, automatic return-to-blocked trigger, benchmark notes, replay command, rollback threshold, `retired_from_active_discussion` state, reopen triggers, trigger-specific evidence refresh, parity scorecard link or blocker record, indefinite-C policy link or non-applicability note, explicit non-goals, and written rationale explicit beside those minimum lane fields
""",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _sample_files(root)
        failures = collect_failures(root)
        if failures:
            print("PHASE15_DECISION_RECORD_TEMPLATE_ALIGNMENT_SELF_TEST=fail")
            for failure in failures:
                print(f" - {failure}")
            return 1
    print("PHASE15_DECISION_RECORD_TEMPLATE_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE15_DECISION_RECORD_TEMPLATE_ALIGNMENT_REQUIRED_FIELD_COUNT={len(REQUIRED_REVIEW_FIELDS)}")
    print(f"PHASE15_DECISION_RECORD_TEMPLATE_ALIGNMENT_CLOSEOUT_FIELD_COUNT={len(STAY_IN_C_CLOSEOUT_FIELDS)}")
    print(f"PHASE15_DECISION_RECORD_TEMPLATE_ALIGNMENT_REOPEN_FIELD_COUNT={len(REOPEN_EVIDENCE_FIELDS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 15 Architecture Council decision-record template aligned with the live governance packet."
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        print("PHASE15_DECISION_RECORD_TEMPLATE_ALIGNMENT=fail")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("PHASE15_DECISION_RECORD_TEMPLATE_ALIGNMENT=pass")
    print(f"PHASE15_DECISION_RECORD_TEMPLATE_ALIGNMENT_REQUIRED_FIELD_COUNT={len(REQUIRED_REVIEW_FIELDS)}")
    print(f"PHASE15_DECISION_RECORD_TEMPLATE_ALIGNMENT_CLOSEOUT_FIELD_COUNT={len(STAY_IN_C_CLOSEOUT_FIELDS)}")
    print(f"PHASE15_DECISION_RECORD_TEMPLATE_ALIGNMENT_REOPEN_FIELD_COUNT={len(REOPEN_EVIDENCE_FIELDS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
