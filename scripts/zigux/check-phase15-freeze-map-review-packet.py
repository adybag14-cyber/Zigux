#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

FREEZE_MAP_REL = "Documentation/zigux/freeze-map.md"
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
FREEZE_GOVERNANCE_REL = "Documentation/zigux/phase15-freeze-map-governance.md"
REVIEW_PROCESS_REL = "Documentation/zigux/phase15-architecture-council-review-process.md"
DECISION_TEMPLATE_REL = (
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md"
)
INDEFINITE_C_POLICY_REL = "Documentation/zigux/phase15-indefinite-c-policy.md"

REQUIRED_FILES = (
    FREEZE_MAP_REL,
    REVIEW_CHECKLIST_REL,
    FREEZE_GOVERNANCE_REL,
    REVIEW_PROCESS_REL,
    DECISION_TEMPLATE_REL,
    INDEFINITE_C_POLICY_REL,
)

FREEZE_MAP_MARKERS = (
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "keep the exact Linux anchor path, current roadmap phase, lane owner, rollback owner, current status bucket, requested decision bucket, decision record ID, required approver set, validation gate summary, evidence archive path, latest blocker disposition, automatic return-to-blocked trigger, benchmark notes, replay command, rollback threshold, `retired_from_active_discussion` state, reopen triggers, trigger-specific evidence refresh, parity scorecard link or blocker record, indefinite-C policy link or non-applicability note, governance lane sequencing link or explicit scope note, study-only anchor accounting link or explicit freeze-map-anchor confirmation, explicit non-goals, and written rationale explicit beside those minimum lane fields",
)

REVIEW_CHECKLIST_MARKERS = (
    "if a freeze-map anchor is entering Architecture Council status review",
    "`Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-architecture-council-decision-record-template.md` remain the owners of the exact Architecture Council field inventory, stay-in-C closeout record, and reopen-evidence details",
    "`Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording",
)

FREEZE_GOVERNANCE_MARKERS = (
    "freeze-map status-change requests must keep the root policy layer aligned with the broader Architecture Council review packet fields",
    "required approver set, evidence archive path, latest blocker disposition, replay command, rollback threshold, `retired_from_active_discussion`, reopen triggers, trigger-specific evidence refresh, parity scorecard link or blocker record, indefinite-C policy link or non-applicability note, explicit non-goals, and written rationale",
    "there is no silent exception path around the stay-in-C policy; only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review",
)

REVIEW_FIELDS = (
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
)

STAY_IN_C_CLOSEOUT_FIELDS = (
    "the retained `freeze_in_c` decision",
    "the current blocker",
    "the required approver set",
    "`retired_from_active_discussion` state",
    "the automatic return-to-blocked trigger",
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

DECISION_TEMPLATE_CLOSEOUT_FIELDS = (
    "- the retained `freeze_in_c` decision:",
    "- the current blocker:",
    "- the required approver set:",
    "- `retired_from_active_discussion` state:",
    "- automatic return-to-blocked trigger:",
    "- the reopen triggers:",
    "- the trigger-specific evidence refresh:",
    "- the evidence archive path that will be refreshed before any later reopen request:",
)

INDEFINITE_C_POLICY_MARKERS = (
    "Those ownership, validation, and rollback fields stay coupled to `Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "required approver set",
    "automatic return-to-blocked trigger",
    "trigger-specific evidence refresh",
    "parity scorecard link or blocker record",
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
        (REVIEW_CHECKLIST_REL, REVIEW_CHECKLIST_MARKERS),
        (FREEZE_GOVERNANCE_REL, FREEZE_GOVERNANCE_MARKERS),
        (INDEFINITE_C_POLICY_REL, INDEFINITE_C_POLICY_MARKERS),
    ):
        text = _read(root / rel)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel}:{marker}")

    review_process = _read(root / REVIEW_PROCESS_REL)
    decision_template = _read(root / DECISION_TEMPLATE_REL)

    for field in REVIEW_FIELDS:
        if field not in review_process:
            failures.append(f"missing_review_field:{REVIEW_PROCESS_REL}:{field}")
        if field not in decision_template:
            failures.append(f"missing_review_field:{DECISION_TEMPLATE_REL}:{field}")

    for field in STAY_IN_C_CLOSEOUT_FIELDS:
        if field not in review_process:
            failures.append(f"missing_closeout_field:{REVIEW_PROCESS_REL}:{field}")

    for field in DECISION_TEMPLATE_CLOSEOUT_FIELDS:
        if field not in decision_template:
            failures.append(f"missing_closeout_field:{DECISION_TEMPLATE_REL}:{field}")

    for field in REOPEN_EVIDENCE_FIELDS:
        if field not in review_process:
            failures.append(f"missing_reopen_field:{REVIEW_PROCESS_REL}:{field}")
        if field not in decision_template:
            failures.append(f"missing_reopen_field:{DECISION_TEMPLATE_REL}:{field}")

    return failures


def _seed(root: Path) -> None:
    _write(
        root / FREEZE_MAP_REL,
        """# Zigux Freeze Map

- freeze-map status-change requests must route through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, and keep the exact Linux anchor path, current roadmap phase, lane owner, rollback owner, current status bucket, requested decision bucket, decision record ID, required approver set, validation gate summary, evidence archive path, latest blocker disposition, automatic return-to-blocked trigger, benchmark notes, replay command, rollback threshold, `retired_from_active_discussion` state, reopen triggers, trigger-specific evidence refresh, parity scorecard link or blocker record, indefinite-C policy link or non-applicability note, governance lane sequencing link or explicit scope note, study-only anchor accounting link or explicit freeze-map-anchor confirmation, explicit non-goals, and written rationale explicit beside those minimum lane fields
""",
    )
    _write(
        root / REVIEW_CHECKLIST_REL,
        """# Zigux Review Checklist

- if a freeze-map anchor is entering Architecture Council status review, does this checklist keep the shared entry-review prompt explicit while `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-architecture-council-decision-record-template.md` remain the owners of the exact Architecture Council field inventory, stay-in-C closeout record, and reopen-evidence details, and `Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording?
""",
    )
    _write(
        root / FREEZE_GOVERNANCE_REL,
        """# Phase 15 Freeze-Map Governance

- freeze-map status-change requests must keep the root policy layer aligned with the broader Architecture Council review packet fields, including required approver set, evidence archive path, latest blocker disposition, replay command, rollback threshold, `retired_from_active_discussion`, reopen triggers, trigger-specific evidence refresh, parity scorecard link or blocker record, indefinite-C policy link or non-applicability note, explicit non-goals, and written rationale
- there is no silent exception path around the stay-in-C policy; only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review
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

If a freeze-in-C review closes without a status change, the closeout record must keep all of the following explicit:
- the retained `freeze_in_c` decision
- the current blocker
- the required approver set
- `retired_from_active_discussion` state
- the automatic return-to-blocked trigger
- the reopen triggers
- the trigger-specific evidence refresh
- the evidence archive path that will be refreshed before any later reopen request

A later reopen request must not rely on generic intent alone. It must cite:
- the exact reopen trigger being exercised
- refreshed evidence by path
- the blocker disposition being challenged
- the narrower seam or policy change that makes the new review safe to consider
""",
    )
    _write(
        root / DECISION_TEMPLATE_REL,
        """# Phase 15 Architecture Council Decision Record Template

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
- governance lane sequencing link or explicit scope note:
- study-only anchor accounting link or explicit freeze-map-anchor confirmation:
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
""",
    )
    _write(
        root / INDEFINITE_C_POLICY_REL,
        """# Phase 15 Indefinite-C Policy

Those ownership, validation, and rollback fields stay coupled to `Documentation/zigux/phase15-architecture-council-decision-record-template.md` so the stay-in-C closeout record reuses the same reviewable ownership vocabulary as the broader Phase 15 governance packet.

- the decision record ID, lane owner, required approver set, and rollback owner
- the automatic return-to-blocked trigger, retained `retired_from_active_discussion` state, reopen triggers, and trigger-specific evidence refresh
- the parity scorecard link or blocker record, explicit non-goals, and written rationale for why the anchor remains in C
""",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_freeze_map_review_packet_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        cases = (
            (FREEZE_MAP_REL, FREEZE_MAP_MARKERS[5], f"missing_marker:{FREEZE_MAP_REL}:{FREEZE_MAP_MARKERS[5]}"),
            (
                REVIEW_CHECKLIST_REL,
                REVIEW_CHECKLIST_MARKERS[1],
                f"missing_marker:{REVIEW_CHECKLIST_REL}:{REVIEW_CHECKLIST_MARKERS[1]}",
            ),
            (
                FREEZE_GOVERNANCE_REL,
                FREEZE_GOVERNANCE_MARKERS[0],
                f"missing_marker:{FREEZE_GOVERNANCE_REL}:{FREEZE_GOVERNANCE_MARKERS[0]}",
            ),
            (
                REVIEW_PROCESS_REL,
                "- rollback owner\n",
                f"missing_review_field:{REVIEW_PROCESS_REL}:rollback owner",
            ),
            (
                DECISION_TEMPLATE_REL,
                "- the evidence archive path that will be refreshed before any later reopen request:\n",
                f"missing_closeout_field:{DECISION_TEMPLATE_REL}:- the evidence archive path that will be refreshed before any later reopen request:",
            ),
            (
                INDEFINITE_C_POLICY_REL,
                INDEFINITE_C_POLICY_MARKERS[0],
                f"missing_marker:{INDEFINITE_C_POLICY_REL}:{INDEFINITE_C_POLICY_MARKERS[0]}",
            ),
        )

        for rel, marker, expected in cases:
            case_root = root / f"case_{case_count}"
            _seed(case_root)
            text = _read(case_root / rel)
            _write(case_root / rel, text.replace(marker, "", 1))
            failures = collect_failures(case_root)
            if failures != [expected]:
                raise AssertionError(f"unexpected failures for {rel}: {failures}")
            case_count += 1

    print("PHASE15_FREEZE_MAP_REVIEW_PACKET_SELF_TEST=pass")
    print(f"PHASE15_FREEZE_MAP_REVIEW_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that the Phase 15 docs-root freeze-governance packet keeps the "
            "freeze map, review checklist, review-process note, decision-record template, "
            "freeze-governance note, and indefinite-C policy aligned."
        )
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

    print("Phase 15 freeze-map review packet check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
