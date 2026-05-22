#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

FREEZE_MAP_REL = "Documentation/zigux/freeze-map.md"
FREEZE_MAP_GOVERNANCE_REL = "Documentation/zigux/phase15-freeze-map-governance.md"
REVIEW_PROCESS_REL = "Documentation/zigux/phase15-architecture-council-review-process.md"
DECISION_TEMPLATE_REL = (
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md"
)
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
INDEFINITE_C_POLICY_REL = "Documentation/zigux/phase15-indefinite-c-policy.md"

REQUIRED_FILES = (
    FREEZE_MAP_REL,
    FREEZE_MAP_GOVERNANCE_REL,
    REVIEW_PROCESS_REL,
    DECISION_TEMPLATE_REL,
    REVIEW_CHECKLIST_REL,
    INDEFINITE_C_POLICY_REL,
)

FREEZE_MAP_MARKERS = (
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "required approver set",
    "evidence archive path",
    "latest blocker disposition",
    "automatic return-to-blocked trigger",
    "retired_from_active_discussion",
    "reopen triggers",
    "trigger-specific evidence refresh",
    "written rationale explicit beside those minimum lane fields",
)

FREEZE_MAP_GOVERNANCE_MARKERS = (
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`Documentation/zigux/phase15-shared-summary-gap.md`",
    "required approver set",
    "evidence archive path",
    "latest blocker disposition",
    "replay command",
    "rollback threshold",
    "retired_from_active_discussion",
    "reopen triggers",
    "trigger-specific evidence refresh",
    "explicit non-goals",
    "written rationale",
)

REVIEW_PROCESS_MARKERS = (
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
    "governance lane sequencing link or explicit scope note",
    "study-only anchor accounting link or explicit freeze-map-anchor confirmation",
    "explicit non-goals",
    "written rationale",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain boundary-study context",
)

DECISION_TEMPLATE_MARKERS = (
    "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
    "`SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`",
    "exact Linux anchor path:",
    "roadmap phase:",
    "decision record ID:",
    "lane owner:",
    "current status bucket:",
    "requested decision bucket:",
    "required approver set:",
    "rollback owner:",
    "validation gate summary:",
    "evidence archive path:",
    "latest blocker disposition:",
    "benchmark notes:",
    "replay command:",
    "rollback threshold:",
    "automatic return-to-blocked trigger:",
    "`retired_from_active_discussion` state:",
    "reopen triggers:",
    "trigger-specific evidence refresh:",
    "the exact reopen trigger being exercised:",
    "refreshed evidence by path:",
    "the blocker disposition being challenged:",
    "the narrower seam or policy change that makes the new review safe to consider:",
    "governance lane sequencing link or explicit scope note:",
    "study-only anchor accounting link or explicit freeze-map-anchor confirmation:",
    "parity scorecard link or blocker record:",
    "indefinite-C policy link or explicit non-applicability note:",
    "explicit non-goals:",
    "written rationale:",
    "Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review",
)

REVIEW_CHECKLIST_ENTRY_PROMPT = (
    "if a freeze-map anchor is entering Architecture Council status review"
)

REVIEW_CHECKLIST_PROMPT_MARKERS = (
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "owners of the exact Architecture Council field inventory",
    "stay-in-C closeout record",
    "reopen-evidence details",
    "`Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion",
)

INDEFINITE_C_POLICY_MARKERS = (
    "required approver set",
    "automatic return-to-blocked trigger",
    "trigger-specific evidence refresh",
    "parity scorecard link or blocker record",
    "explicit decision to keep the anchor in C",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _line_containing(text: str, marker: str) -> str | None:
    for line in text.splitlines():
        if marker in line:
            return line
    return None


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    marker_sets = (
        (FREEZE_MAP_REL, FREEZE_MAP_MARKERS),
        (FREEZE_MAP_GOVERNANCE_REL, FREEZE_MAP_GOVERNANCE_MARKERS),
        (REVIEW_PROCESS_REL, REVIEW_PROCESS_MARKERS),
        (DECISION_TEMPLATE_REL, DECISION_TEMPLATE_MARKERS),
        (INDEFINITE_C_POLICY_REL, INDEFINITE_C_POLICY_MARKERS),
    )

    for rel, markers in marker_sets:
        text = _read(root / rel)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel}:{marker}")

    checklist_text = _read(root / REVIEW_CHECKLIST_REL)
    checklist_line = _line_containing(checklist_text, REVIEW_CHECKLIST_ENTRY_PROMPT)
    if checklist_line is None:
        failures.append(
            "missing_marker:Documentation/zigux/review-checklist.md:"
            + REVIEW_CHECKLIST_ENTRY_PROMPT
        )
    else:
        for marker in REVIEW_CHECKLIST_PROMPT_MARKERS:
            if marker not in checklist_line:
                failures.append(
                    f"missing_prompt_marker:Documentation/zigux/review-checklist.md:{marker}"
                )

    return failures


def _seed(root: Path) -> None:
    _write(
        root / FREEZE_MAP_REL,
        """# Zigux Freeze Map

## Governance For Freeze-Map Changes
- freeze-map status-change requests must route through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, and keep the exact Linux anchor path, current roadmap phase, lane owner, rollback owner, current status bucket, requested decision bucket, decision record ID, required approver set, validation gate summary, evidence archive path, latest blocker disposition, automatic return-to-blocked trigger, benchmark notes, replay command, rollback threshold, `retired_from_active_discussion` state, reopen triggers, trigger-specific evidence refresh, parity scorecard link or blocker record, indefinite-C policy link or non-applicability note, governance lane sequencing link or explicit scope note, study-only anchor accounting link or explicit freeze-map-anchor confirmation, explicit non-goals, and written rationale explicit beside those minimum lane fields
""",
    )
    _write(
        root / FREEZE_MAP_GOVERNANCE_REL,
        """# Phase 15 Freeze-Map Governance

- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-shared-summary-gap.md`

Freeze-map status-change requests must keep the root policy layer aligned with the broader Architecture Council review packet fields, including required approver set, evidence archive path, latest blocker disposition, replay command, rollback threshold, `retired_from_active_discussion`, reopen triggers, trigger-specific evidence refresh, parity scorecard link or blocker record, indefinite-C policy link or non-applicability note, explicit non-goals, and written rationale.
""",
    )
    _write(
        root / REVIEW_PROCESS_REL,
        """# Phase 15 Architecture Council Review Process

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
- governance lane sequencing link or explicit scope note
- study-only anchor accounting link or explicit freeze-map-anchor confirmation
- explicit non-goals
- written rationale

`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain boundary-study context routed through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`, not candidates for a freeze-in-C status review through this note, unless the freeze map and supporting governance packet are explicitly updated first.
""",
    )
    _write(
        root / DECISION_TEMPLATE_REL,
        """# Phase 15 Architecture Council Decision Record Template

- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- `SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`
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
- the exact reopen trigger being exercised:
- refreshed evidence by path:
- the blocker disposition being challenged:
- the narrower seam or policy change that makes the new review safe to consider:
- governance lane sequencing link or explicit scope note:
- study-only anchor accounting link or explicit freeze-map-anchor confirmation:
- parity scorecard link or blocker record:
- indefinite-C policy link or explicit non-applicability note:
- explicit non-goals:
- written rationale:

- Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.
""",
    )
    _write(
        root / REVIEW_CHECKLIST_REL,
        """# Zigux Review Checklist

- if a freeze-map anchor is entering Architecture Council status review, does this checklist keep the shared entry-review prompt explicit, including the required approver set, rollback owner, and evidence archive path, while `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-architecture-council-decision-record-template.md` remain the owners of the exact Architecture Council field inventory, stay-in-C closeout record, and reopen-evidence details, and `Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording?
""",
    )
    _write(
        root / INDEFINITE_C_POLICY_REL,
        """# Phase 15 Indefinite-C Policy

- the decision record ID, lane owner, required approver set, and rollback owner
- the automatic return-to-blocked trigger, retained `retired_from_active_discussion` state, reopen triggers, and trigger-specific evidence refresh
- the parity scorecard link or blocker record, explicit non-goals, and written rationale for why the anchor remains in C
- a closed stay-in-C record is an explicit decision to keep the anchor in C until narrower evidence exists
""",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_freeze_map_review_boundaries_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        cases = (
            (FREEZE_MAP_REL, FREEZE_MAP_MARKERS[0], "missing freeze-map review-process path"),
            (
                FREEZE_MAP_GOVERNANCE_REL,
                FREEZE_MAP_GOVERNANCE_MARKERS[7],
                "missing freeze-map governance evidence archive field",
            ),
            (
                REVIEW_PROCESS_REL,
                REVIEW_PROCESS_MARKERS[10],
                "missing review-process latest blocker disposition field",
            ),
            (
                DECISION_TEMPLATE_REL,
                DECISION_TEMPLATE_MARKERS[20],
                "missing decision-template reopen trigger field",
            ),
            (
                INDEFINITE_C_POLICY_REL,
                INDEFINITE_C_POLICY_MARKERS[3],
                "missing indefinite-C parity-scorecard marker",
            ),
        )

        for rel, marker, label in cases:
            case_root = root / f"case_{case_count}"
            _seed(case_root)
            text = _read(case_root / rel)
            _write(case_root / rel, text.replace(marker, "", 1))
            failures = collect_failures(case_root)
            expected = [f"missing_marker:{rel}:{marker}"]
            if failures != expected:
                raise AssertionError(f"{label}: unexpected failures {failures}")
            case_count += 1

        case_root = root / f"case_{case_count}"
        _seed(case_root)
        text = _read(case_root / REVIEW_CHECKLIST_REL)
        _write(
            case_root / REVIEW_CHECKLIST_REL,
            text.replace(
                "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
                "",
                1,
            ),
        )
        failures = collect_failures(case_root)
        expected = [
            "missing_prompt_marker:Documentation/zigux/review-checklist.md:`Documentation/zigux/phase15-architecture-council-decision-record-template.md`"
        ]
        if failures != expected:
            raise AssertionError(f"missing checklist prompt marker: unexpected failures {failures}")
        case_count += 1

    print("PHASE15_FREEZE_MAP_REVIEW_BOUNDARIES_SELF_TEST=pass")
    print(f"PHASE15_FREEZE_MAP_REVIEW_BOUNDARIES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that the Phase 15 freeze-map packet keeps Architecture Council "
            "review-boundary wording aligned across the root governance docs."
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
        help="run synthetic fixture coverage for the freeze-map review-boundary guard",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 freeze-map review-boundary check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
