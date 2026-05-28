#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
FREEZE_MAP_REL = "Documentation/zigux/freeze-map.md"
FREEZE_GOVERNANCE_REL = "Documentation/zigux/phase15-freeze-map-governance.md"
REVIEW_PROCESS_REL = "Documentation/zigux/phase15-architecture-council-review-process.md"
DECISION_TEMPLATE_REL = "Documentation/zigux/phase15-architecture-council-decision-record-template.md"
INDEFINITE_C_POLICY_REL = "Documentation/zigux/phase15-indefinite-c-policy.md"

REQUIRED_FILES = (
    REVIEW_CHECKLIST_REL,
    FREEZE_MAP_REL,
    FREEZE_GOVERNANCE_REL,
    REVIEW_PROCESS_REL,
    DECISION_TEMPLATE_REL,
    INDEFINITE_C_POLICY_REL,
)

REVIEW_CHECKLIST_MARKERS = (
    "if a freeze-map anchor is entering Architecture Council status review or recording a stay-in-C closeout",
    "required approver set",
    "rollback owner",
    "evidence archive path",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "stay-in-C closeout record",
    "trigger-specific evidence refresh",
    "return-to-blocked wording",
)

FREEZE_MAP_MARKERS = (
    "freeze-map status-change requests must route through `Documentation/zigux/phase15-architecture-council-review-process.md`",
    "required approver set",
    "evidence archive path",
    "rollback threshold",
    "`retired_from_active_discussion` state",
    "trigger-specific evidence refresh",
    "indefinite-C policy link or non-applicability note",
)

FREEZE_GOVERNANCE_MARKERS = (
    "freeze-map status-change requests must keep the root policy layer aligned with the broader Architecture Council review packet fields",
    "required approver set",
    "evidence archive path",
    "replay command",
    "rollback threshold",
    "`retired_from_active_discussion`",
    "trigger-specific evidence refresh",
    "explicit non-goals",
    "written rationale",
)

REVIEW_PROCESS_MARKERS = (
    "Any freeze-map anchor entering Architecture Council status review must keep all of the following explicit:",
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
    "If one of those fields cannot be stated honestly, the request stays blocked",
)

DECISION_TEMPLATE_MARKERS = (
    "- exact Linux anchor path:",
    "- roadmap phase:",
    "- lane owner:",
    "- current status bucket:",
    "- requested decision bucket:",
    "- required approver set:",
    "- rollback owner:",
    "- validation gate summary:",
    "- evidence archive path:",
    "- latest blocker disposition:",
    "- benchmark notes:",
    "- replay command:",
    "- rollback threshold:",
    "- `retired_from_active_discussion` state:",
    "- automatic return-to-blocked trigger:",
    "- the reopen triggers:",
    "- the trigger-specific evidence refresh:",
    "- governance lane sequencing link or explicit scope note:",
    "- study-only anchor accounting link or explicit freeze-map-anchor confirmation:",
    "- parity scorecard link or blocker record:",
    "- indefinite-C policy link or explicit non-applicability note:",
    "- explicit non-goals:",
    "- written rationale:",
    "Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.",
    "If any required field above cannot be stated honestly, keep the request blocked and leave the C implementation as the product source of truth.",
)

INDEFINITE_C_POLICY_MARKERS = (
    "Those ownership, validation, and rollback fields stay coupled to `Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "decision record ID, lane owner, required approver set, and rollback owner",
    "validation gate summary, benchmark-notes status, replay command, latest blocker disposition, and evidence archive path",
    "automatic return-to-blocked trigger, retained `retired_from_active_discussion` state, reopen triggers, and trigger-specific evidence refresh",
    "governance lane sequencing link or explicit scope note, the study-only anchor accounting link or explicit freeze-map-anchor confirmation, parity scorecard link or blocker record, explicit non-goals, and written rationale",
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
        (REVIEW_CHECKLIST_REL, REVIEW_CHECKLIST_MARKERS),
        (FREEZE_MAP_REL, FREEZE_MAP_MARKERS),
        (FREEZE_GOVERNANCE_REL, FREEZE_GOVERNANCE_MARKERS),
        (REVIEW_PROCESS_REL, REVIEW_PROCESS_MARKERS),
        (DECISION_TEMPLATE_REL, DECISION_TEMPLATE_MARKERS),
        (INDEFINITE_C_POLICY_REL, INDEFINITE_C_POLICY_MARKERS),
    ):
        text = _read(root / rel)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel}:{marker}")

    return failures


def _seed(root: Path) -> None:
    _write(
        root / REVIEW_CHECKLIST_REL,
        """# Zigux Review Checklist

- if a freeze-map anchor is entering Architecture Council status review or recording a stay-in-C closeout, does this checklist keep the shared entry-review and closeout prompts explicit, including the required approver set, rollback owner, and evidence archive path, while `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-architecture-council-decision-record-template.md` remain the owners of the exact Architecture Council field inventory, stay-in-C closeout record, and reopen-evidence details, and `Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording?
""",
    )
    _write(
        root / FREEZE_MAP_REL,
        """# Zigux Freeze Map

- freeze-map status-change requests must route through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, and keep the required approver set, evidence archive path, rollback threshold, `retired_from_active_discussion` state, trigger-specific evidence refresh, and indefinite-C policy link or non-applicability note explicit.
""",
    )
    _write(
        root / FREEZE_GOVERNANCE_REL,
        """# Phase 15 Freeze-Map Governance

- freeze-map status-change requests must keep the root policy layer aligned with the broader Architecture Council review packet fields, including required approver set, evidence archive path, replay command, rollback threshold, `retired_from_active_discussion`, trigger-specific evidence refresh, explicit non-goals, and written rationale.
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

If one of those fields cannot be stated honestly, the request stays blocked and the C implementation remains the product source of truth.
""",
    )
    _write(
        root / DECISION_TEMPLATE_REL,
        """# Phase 15 Architecture Council Decision Record Template

- exact Linux anchor path:
- roadmap phase:
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
- `retired_from_active_discussion` state:
- automatic return-to-blocked trigger:
- the reopen triggers:
- the trigger-specific evidence refresh:
- governance lane sequencing link or explicit scope note:
- study-only anchor accounting link or explicit freeze-map-anchor confirmation:
- parity scorecard link or blocker record:
- indefinite-C policy link or explicit non-applicability note:
- explicit non-goals:
- written rationale:

- Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.
- If any required field above cannot be stated honestly, keep the request blocked and leave the C implementation as the product source of truth.
""",
    )
    _write(
        root / INDEFINITE_C_POLICY_REL,
        """# Phase 15 Indefinite-C Policy

Those ownership, validation, and rollback fields stay coupled to `Documentation/zigux/phase15-architecture-council-decision-record-template.md` so the stay-in-C closeout record reuses the same reviewable ownership vocabulary as the broader Phase 15 governance packet.

- the decision record ID, lane owner, required approver set, and rollback owner
- the validation gate summary, benchmark-notes status, replay command, latest blocker disposition, and evidence archive path
- the automatic return-to-blocked trigger, retained `retired_from_active_discussion` state, reopen triggers, and trigger-specific evidence refresh
- the governance lane sequencing link or explicit scope note, the study-only anchor accounting link or explicit freeze-map-anchor confirmation, parity scorecard link or blocker record, explicit non-goals, and written rationale for why the anchor remains in C
""",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_review_checklist_freeze_prompts_") as tmp_dir:
        root = Path(tmp_dir)
        _seed(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        cases = (
            (REVIEW_CHECKLIST_REL, REVIEW_CHECKLIST_MARKERS[0]),
            (FREEZE_MAP_REL, FREEZE_MAP_MARKERS[2]),
            (FREEZE_GOVERNANCE_REL, FREEZE_GOVERNANCE_MARKERS[4]),
            (REVIEW_PROCESS_REL, REVIEW_PROCESS_MARKERS[8]),
            (DECISION_TEMPLATE_REL, DECISION_TEMPLATE_MARKERS[13]),
            (INDEFINITE_C_POLICY_REL, INDEFINITE_C_POLICY_MARKERS[3]),
        )

        for rel, marker in cases:
            case_root = root / f"case_{case_count}"
            _seed(case_root)
            text = _read(case_root / rel)
            _write(case_root / rel, text.replace(marker, "", 1))
            failures = collect_failures(case_root)
            expected = [f"missing_marker:{rel}:{marker}"]
            if failures != expected:
                raise AssertionError(f"unexpected failures for {rel}: {failures}")
            case_count += 1

    print("PHASE15_REVIEW_CHECKLIST_FREEZE_PROMPTS_SELF_TEST=pass")
    print(f"PHASE15_REVIEW_CHECKLIST_FREEZE_PROMPTS_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 review checklist keeps the freeze-review and stay-in-C closeout prompts aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the Phase 15 governance docs",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run synthetic fixture coverage for the review-checklist freeze prompt guard",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 review-checklist freeze prompt alignment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
