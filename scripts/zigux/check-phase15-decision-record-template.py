#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
DECISION_RECORD_TEMPLATE_PATH = Path(
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md"
)
INDEFINITE_C_POLICY_PATH = Path("Documentation/zigux/phase15-indefinite-c-policy.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase15_architecture_council_review_process_manifest.json")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _line_containing(text: str, marker: str) -> str | None:
    for line in text.splitlines():
        if marker in line:
            return line
    return None


def collect_failures(root: Path) -> list[str]:
    review_process = _read_text(root / REVIEW_PROCESS_PATH)
    decision_record_template = _read_text(root / DECISION_RECORD_TEMPLATE_PATH)
    indefinite_c_policy = _read_text(root / INDEFINITE_C_POLICY_PATH)
    review_checklist = _read_text(root / REVIEW_CHECKLIST_PATH)
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)

    failures: list[str] = []

    if manifest["surveyed_commit"] not in review_process:
        failures.append("review-process note is missing the manifest surveyed_commit marker")

    if manifest["decision_record_template"] not in review_process:
        failures.append("review-process note is missing the decision-record template path")

    if manifest["decision_record_template"] not in handoff_note:
        failures.append("handoff note is missing the decision-record template path")

    if manifest["review_checklist_boundary_rule"] not in review_process:
        failures.append("review-process note is missing the review-checklist boundary rule")

    checklist_entry_prompt = _line_containing(
        review_checklist, manifest["review_checklist_entry_prompt"]
    )
    if checklist_entry_prompt is None:
        failures.append(
            "review checklist is missing the Phase 15 Architecture Council entry-review prompt"
        )
    else:
        for field in manifest["required_review_fields"]:
            if field not in checklist_entry_prompt:
                failures.append(
                    f"review checklist entry prompt is missing required review field: {field}"
                )

    for field in manifest["required_review_fields"]:
        if field not in decision_record_template:
            failures.append(f"decision-record template is missing required review field: {field}")

    for field in manifest["stay_in_c_closeout_fields"]:
        if field not in decision_record_template:
            failures.append(
                f"decision-record template is missing stay-in-C closeout field: {field}"
            )

    for field in manifest["reopen_evidence_fields"]:
        if field not in decision_record_template:
            failures.append(
                f"decision-record template is missing reopen-evidence field: {field}"
            )

    for marker in manifest["decision_record_template_required_markers"]:
        if marker not in decision_record_template:
            failures.append(f"decision-record template is missing required marker: {marker}")

    for marker in manifest["indefinite_c_policy_required_markers"]:
        if marker not in indefinite_c_policy:
            failures.append(f"indefinite-C policy note is missing required marker: {marker}")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest() -> str:
    return json.dumps(
        {
            "lane_key": "P15-L08",
            "phase": "Phase 15",
            "surveyed_commit": "current-master-readback-2026-05-19",
            "review_process_note": "Documentation/zigux/phase15-architecture-council-review-process.md",
            "decision_record_template": "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
            "indefinite_c_policy_note": "Documentation/zigux/phase15-indefinite-c-policy.md",
            "handoff_note": "Documentation/zigux/phase15-handoff-next-steps-survey.md",
            "shared_summary_gap_note": "Documentation/zigux/phase15-shared-summary-gap.md",
            "checker": "scripts/zigux/check-phase15-review-process-handoff.py",
            "build_gate": "zigux/tests/phase15_architecture_council_review_process_build.zig",
            "review_checklist_entry_prompt": "if a freeze-map anchor is entering Architecture Council status review",
            "review_checklist_boundary_rule": "`Documentation/zigux/review-checklist.md` keeps the shared entry-review and closeout prompts explicit, but the exact Architecture Council field inventory stays owned by this note and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
            "required_review_fields": [
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
            ],
            "stay_in_c_closeout_fields": [
                "the retained `freeze_in_c` decision",
                "the current blocker",
                "the required approver set",
                "`retired_from_active_discussion` state",
                "the automatic return-to-blocked trigger",
                "the reopen triggers",
                "the trigger-specific evidence refresh",
                "the evidence archive path that will be refreshed before any later reopen request",
            ],
            "reopen_evidence_fields": [
                "the exact reopen trigger being exercised",
                "refreshed evidence by path",
                "the blocker disposition being challenged",
                "the narrower seam or policy change that makes the new review safe to consider",
            ],
            "indefinite_c_policy_required_markers": [
                "required approver set",
                "automatic return-to-blocked trigger",
                "trigger-specific evidence refresh",
                "parity scorecard link or blocker record",
            ],
            "decision_record_template_required_markers": [
                "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
                "`SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`",
                "exact-head provenance exception note:",
                "Prefer the dated master readback form for parked governance and stay-in-C review packets.",
                "Only record an exact head when the linked review needs it to anchor a named published decision",
            ],
        },
        indent=2,
    ) + "\n"


def _sample_review_process() -> str:
    return """# Phase 15 Architecture Council Review Process

- `PHASE15_STATUS=architecture_council_review_process_landed`
- `PHASE15_LANE_KEY=P15-L08`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-19`

This note exists beside `Documentation/zigux/phase15-architecture-council-decision-record-template.md`.
`Documentation/zigux/review-checklist.md` keeps the shared entry-review and closeout prompts explicit, but the exact Architecture Council field inventory stays owned by this note and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
"""


def _sample_decision_template() -> str:
    return """# Phase 15 Architecture Council Decision Record Template

- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- `SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`
- exact-head provenance exception note:

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
- automatic return-to-blocked trigger:

## Stay-In-C Closeout

- the retained `freeze_in_c` decision:
- the current blocker:
- the required approver set:
- `retired_from_active_discussion` state:
- the automatic return-to-blocked trigger:
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
- Only record an exact head when the linked review needs it to anchor a named published decision
"""


def _sample_indefinite_c_policy() -> str:
    return """# Phase 15 Indefinite C Policy

- required approver set
- automatic return-to-blocked trigger
- trigger-specific evidence refresh
- parity scorecard link or blocker record
"""


def _sample_review_checklist() -> str:
    return """# Zigux Review Checklist

- if a freeze-map anchor is entering Architecture Council status review, are the exact Linux anchor path, roadmap phase, decision record ID, lane owner, current status bucket, requested decision bucket, required approver set, rollback owner, validation gate summary, evidence archive path, latest blocker disposition, benchmark notes, replay command, rollback threshold, automatic return-to-blocked trigger, `retired_from_active_discussion` state, reopen triggers, trigger-specific evidence refresh, parity scorecard link or blocker record, indefinite-C policy link or explicit non-applicability note, explicit non-goals, and written rationale explicit?
"""


def _sample_handoff_note() -> str:
    return """# Phase 15 Handoff Next Steps Survey

- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
"""


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15-decision-template-") as tmp:
        root = Path(tmp)
        _write(root / MANIFEST_PATH, _sample_manifest())
        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(root / DECISION_RECORD_TEMPLATE_PATH, _sample_decision_template())
        _write(root / INDEFINITE_C_POLICY_PATH, _sample_indefinite_c_policy())
        _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
        _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())

        failures = collect_failures(root)
        if failures:
            for failure in failures:
                print(f"SELFTEST_FAILURE: {failure}")
            return 1

        broken_template = _sample_decision_template().replace("decision record ID", "record id", 1)
        _write(root / DECISION_RECORD_TEMPLATE_PATH, broken_template)
        failures = collect_failures(root)
        if not any("decision-record template is missing required review field: decision record ID" == failure for failure in failures):
            print("SELFTEST_FAILURE: negative coverage for missing decision record field did not trigger")
            return 1

    print("PHASE15_DECISION_RECORD_TEMPLATE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 15 decision-record template packet for drift."
    )
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument(
        "--self-test", action="store_true", help="Run the built-in checker self-test"
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("Phase 15 decision-record template check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
