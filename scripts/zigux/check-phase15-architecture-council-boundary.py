#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
DECISION_TEMPLATE_PATH = Path(
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md"
)
STUDY_ONLY_ACCOUNTING_PATH = Path(
    "Documentation/zigux/phase15-study-only-anchor-accounting.md"
)

FROZEN_ANCHORS = (
    "`kernel/sched/core.c`",
    "`mm/page_alloc.c`",
    "`kernel/rcu/tree.c`",
    "`net/core/skbuff.c`",
)
STUDY_ONLY_ANCHORS = (
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
)
REQUIRED_STATUS_REVIEW_FIELDS = (
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
REOPEN_FIELDS = (
    "the exact reopen trigger being exercised",
    "refreshed evidence by path",
    "the blocker disposition being challenged",
    "the narrower seam or policy change that makes the new review safe to consider",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _line_containing(text: str, marker: str) -> str | None:
    for line in text.splitlines():
        if marker in line:
            return line
    return None


def collect_failures(root: Path) -> list[str]:
    freeze_map = _read_text(root / FREEZE_MAP_PATH)
    review_checklist = _read_text(root / REVIEW_CHECKLIST_PATH)
    review_process = _read_text(root / REVIEW_PROCESS_PATH)
    decision_template = _read_text(root / DECISION_TEMPLATE_PATH)
    study_only_accounting = _read_text(root / STUDY_ONLY_ACCOUNTING_PATH)

    failures: list[str] = []

    for marker in (
        "`Documentation/zigux/phase15-architecture-council-review-process.md`",
        "`Documentation/zigux/phase15-freeze-map-governance.md`",
        "`Documentation/zigux/phase15-parity-scorecard.md`",
        "`Documentation/zigux/phase15-indefinite-c-policy.md`",
        "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
        "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    ):
        if marker not in freeze_map:
            failures.append(f"freeze map is missing required governance route marker: {marker}")

    for anchor in FROZEN_ANCHORS:
        if anchor not in freeze_map:
            failures.append(f"freeze map is missing freeze-in-C anchor: {anchor}")

    for anchor in STUDY_ONLY_ANCHORS:
        if anchor not in freeze_map:
            failures.append(f"freeze map is missing study-only anchor: {anchor}")
        if anchor not in study_only_accounting:
            failures.append(f"study-only accounting note is missing study-only anchor: {anchor}")

    checklist_prompt = _line_containing(
        review_checklist,
        "if a freeze-map anchor is entering Architecture Council status review",
    )
    if checklist_prompt is None:
        failures.append(
            "review checklist is missing the Architecture Council status-review prompt"
        )
    else:
        for field in REQUIRED_STATUS_REVIEW_FIELDS:
            if field not in checklist_prompt:
                failures.append(
                    f"review checklist prompt is missing required status-review field: {field}"
                )

    for field in REQUIRED_STATUS_REVIEW_FIELDS:
        if field not in review_process:
            failures.append(f"review-process note is missing required status-review field: {field}")
        if field not in decision_template:
            failures.append(
                f"decision-record template is missing required status-review field: {field}"
            )

    for field in STAY_IN_C_CLOSEOUT_FIELDS:
        if field not in review_process:
            failures.append(f"review-process note is missing stay-in-C closeout field: {field}")
        if field not in decision_template:
            failures.append(
                f"decision-record template is missing stay-in-C closeout field: {field}"
            )

    for field in REOPEN_FIELDS:
        if field not in review_process:
            failures.append(f"review-process note is missing reopen field: {field}")
        if field not in decision_template:
            failures.append(f"decision-record template is missing reopen field: {field}")

    for marker in (
        "`PHASE15_STATUS=architecture_council_review_process_landed`",
        "`PHASE15_LANE_KEY=P15-L08`",
        "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
        "no Architecture Council approval is currently recorded for a freeze-map status change",
        "This note does not define an exception path outside those reviewable outcomes.",
    ):
        if marker not in review_process:
            failures.append(f"review-process note is missing required marker: {marker}")

    for marker in (
        "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
        "`SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`",
        "exact-head provenance exception note:",
        "`REVIEW_STATUS=<blocked_review|stay_in_c|approved_status_bucket_change>`",
        "Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.",
        "Only record an exact head when the linked review needs it to anchor a named published decision",
    ):
        if marker not in decision_template:
            failures.append(f"decision-record template is missing required marker: {marker}")

    if (
        "there is no silent exception path around the stay-in-C policy"
        not in freeze_map
    ):
        failures.append("freeze map is missing the no-silent-exception rule")

    if "route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md`" not in freeze_map:
        failures.append("freeze map is missing the study-only route-back rule")

    if "tracked outside the freeze-in-C scorecard" not in study_only_accounting:
        failures.append(
            "study-only accounting note is missing the outside-the-scorecard posture"
        )

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_freeze_map() -> str:
    return """# Zigux Freeze Map

- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`
- freeze-map status-change requests must route through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- shared reminder surfaces that summarize freeze posture, especially `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`, must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md` when they summarize that boundary set
- there is no silent exception path around the stay-in-C policy; only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review
"""


def _sample_review_checklist() -> str:
    return """# Zigux Review Checklist

- if a freeze-map anchor is entering Architecture Council status review, are the exact Linux anchor path, roadmap phase, decision record ID, lane owner, current status bucket, requested decision bucket, required approver set, rollback owner, validation gate summary, evidence archive path, latest blocker disposition, benchmark notes, replay command, rollback threshold, automatic return-to-blocked trigger, `retired_from_active_discussion` state, reopen triggers, trigger-specific evidence refresh, parity scorecard link or blocker record, indefinite-C policy link or explicit non-applicability note, explicit non-goals, and written rationale explicit?
"""


def _sample_review_process() -> str:
    return """# Phase 15 Architecture Council Review Process

- `PHASE15_STATUS=architecture_council_review_process_landed`
- `PHASE15_LANE_KEY=P15-L08`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- no Architecture Council approval is currently recorded for a freeze-map status change

Any freeze-map anchor entering Architecture Council status review must keep all of the following explicit:
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

If a freeze-in-C review closes without a status change, the closeout record must keep all of the following explicit:
- the retained `freeze_in_c` decision
- the current blocker
- the required approver set
- `retired_from_active_discussion` state
- automatic return-to-blocked trigger
- the reopen triggers
- the trigger-specific evidence refresh
- the evidence archive path that will be refreshed before any later reopen request

A later reopen request must not rely on generic intent alone. It must cite:
- the exact reopen trigger being exercised
- refreshed evidence by path
- the blocker disposition being challenged
- the narrower seam or policy change that makes the new review safe to consider

This note does not define an exception path outside those reviewable outcomes.
"""


def _sample_decision_template() -> str:
    return """# Phase 15 Architecture Council Decision Record Template

- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- `SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`
- exact-head provenance exception note:
- `REVIEW_STATUS=<blocked_review|stay_in_c|approved_status_bucket_change>`

- exact Linux anchor path:
- roadmap phase:
- decision record ID:
- lane owner:
- current status bucket:
- requested decision bucket:
- required approver set:
- rollback owner:
- validation gate summary:
- evidence archive path:
- latest blocker disposition:
- benchmark notes:
- replay command:
- rollback threshold:
- automatic return-to-blocked trigger:
- `retired_from_active_discussion` state:
- reopen triggers:
- trigger-specific evidence refresh:
- parity scorecard link or blocker record:
- indefinite-C policy link or explicit non-applicability note:
- explicit non-goals:
- written rationale:

- the retained `freeze_in_c` decision:
- the current blocker:
- the required approver set:
- `retired_from_active_discussion` state:
- automatic return-to-blocked trigger:
- the reopen triggers:
- the trigger-specific evidence refresh:
- the evidence archive path that will be refreshed before any later reopen request:

- the exact reopen trigger being exercised:
- refreshed evidence by path:
- the blocker disposition being challenged:
- the narrower seam or policy change that makes the new review safe to consider:

- Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.
- Only record an exact head when the linked review needs it to anchor a named published decision, and explain that exception in the exact-head provenance note.
"""


def _sample_study_only_accounting() -> str:
    return """# Phase 15 Study-Only Anchor Accounting

- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`
- current Phase 15 role: tracked outside the freeze-in-C scorecard and outside blocked status-change rows
"""


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_arch_council_boundary_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / FREEZE_MAP_PATH, _sample_freeze_map())
        _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(root / DECISION_TEMPLATE_PATH, _sample_decision_template())
        _write(root / STUDY_ONLY_ACCOUNTING_PATH, _sample_study_only_accounting())

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        _write(
            root / FREEZE_MAP_PATH,
            _sample_freeze_map().replace(
                "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
                "`Documentation/zigux/missing-template.md`",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "freeze map is missing required governance route marker: `Documentation/zigux/phase15-architecture-council-decision-record-template.md`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected freeze-map governance failure: {failures}")

        _write(root / FREEZE_MAP_PATH, _sample_freeze_map())
        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace("requested decision bucket, ", "", 1),
        )
        failures = collect_failures(root)
        expected = [
            "review checklist prompt is missing required status-review field: requested decision bucket"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected checklist failure: {failures}")

        _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
        _write(
            root / REVIEW_PROCESS_PATH,
            _sample_review_process().replace("written rationale\n", "", 1),
        )
        failures = collect_failures(root)
        expected = [
            "review-process note is missing required status-review field: written rationale"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected review-process failure: {failures}")

        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(
            root / DECISION_TEMPLATE_PATH,
            _sample_decision_template().replace(
                "exact-head provenance exception note:\n", "", 1
            ),
        )
        failures = collect_failures(root)
        expected = [
            "decision-record template is missing required marker: exact-head provenance exception note:"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected decision-template failure: {failures}")

        _write(root / DECISION_TEMPLATE_PATH, _sample_decision_template())
        _write(
            root / STUDY_ONLY_ACCOUNTING_PATH,
            _sample_study_only_accounting().replace("`kernel/trace/ring_buffer.c`\n", "", 1),
        )
        failures = collect_failures(root)
        expected = [
            "study-only accounting note is missing study-only anchor: `kernel/trace/ring_buffer.c`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected study-only accounting failure: {failures}")

    print("PHASE15_ARCHITECTURE_COUNCIL_BOUNDARY_SELF_TEST=pass")
    print("PHASE15_ARCHITECTURE_COUNCIL_BOUNDARY_SELF_TEST_CASES=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that the Phase 15 Architecture Council status-review boundary stays "
            "aligned across the freeze map, review checklist, review-process note, "
            "decision-record template, and study-only accounting note."
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
        help="exercise the checker against synthetic fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 Architecture Council boundary check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
