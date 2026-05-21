#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

DECISION_TEMPLATE_PATH = Path(
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md"
)
DECISION_TEMPLATE_MANIFEST_PATH = Path(
    "zigux/tests/phase15_architecture_council_decision_record_template_manifest.json"
)
REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
REVIEW_PROCESS_MANIFEST_PATH = Path(
    "zigux/tests/phase15_architecture_council_review_process_manifest.json"
)
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
INDEFINITE_C_POLICY_PATH = Path("Documentation/zigux/phase15-indefinite-c-policy.md")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")

EXPECTED_LANE_KEY = "P15-L08"
EXPECTED_PHASE = "Phase 15"
REQUIRED_INDEFINITE_C_MARKERS = (
    "required approver set",
    "automatic return-to-blocked trigger",
    "trigger-specific evidence refresh",
    "parity scorecard link or blocker record",
)
REQUIRED_HANDOFF_MARKERS = (
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(_read_text(path))


def _find_line(text: str, marker: str) -> str | None:
    for line in text.splitlines():
        if marker in line:
            return line
    return None


def _check_marker_block(
    text: str, markers: list[str] | tuple[str, ...], failures: list[str], prefix: str
) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{prefix}:missing:{marker}")


def collect_failures(root: Path) -> list[str]:
    template = _read_text(root / DECISION_TEMPLATE_PATH)
    template_manifest = _read_manifest(root / DECISION_TEMPLATE_MANIFEST_PATH)
    review_process = _read_text(root / REVIEW_PROCESS_PATH)
    review_process_manifest = _read_manifest(root / REVIEW_PROCESS_MANIFEST_PATH)
    review_checklist = _read_text(root / REVIEW_CHECKLIST_PATH)
    indefinite_c_policy = _read_text(root / INDEFINITE_C_POLICY_PATH)
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)

    failures: list[str] = []

    if template_manifest.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append("template_manifest:lane_key_drift")
    if template_manifest.get("phase") != EXPECTED_PHASE:
        failures.append("template_manifest:phase_drift")
    if template_manifest.get("template_path") != DECISION_TEMPLATE_PATH.as_posix():
        failures.append("template_manifest:template_path_drift")

    if review_process_manifest.get("decision_record_template") != DECISION_TEMPLATE_PATH.as_posix():
        failures.append("review_process_manifest:template_path_drift")

    if DECISION_TEMPLATE_PATH.as_posix() not in review_process:
        failures.append("review_process:missing_template_path")

    boundary_rule = review_process_manifest.get("review_checklist_boundary_rule")
    if boundary_rule and boundary_rule not in review_process:
        failures.append("review_process:missing_checklist_boundary_rule")

    checklist_prompt = review_process_manifest.get("review_checklist_entry_prompt")
    checklist_line = _find_line(review_checklist, checklist_prompt or "")
    if checklist_prompt and checklist_line is None:
        failures.append("review_checklist:missing_entry_prompt")
    elif checklist_line is not None:
        for marker in (
            "Documentation/zigux/phase15-architecture-council-review-process.md",
            "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
            "owners of the exact Architecture Council field inventory",
            "stay-in-C closeout record",
            "reopen-evidence details",
        ):
            if marker not in checklist_line:
                failures.append(f"review_checklist:missing_boundary_marker:{marker}")

    stay_in_c_boundary = review_process_manifest.get(
        "review_checklist_stay_in_c_policy_boundary_rule"
    )
    if checklist_line is not None and stay_in_c_boundary and stay_in_c_boundary not in checklist_line:
        failures.append("review_checklist:missing_stay_in_c_boundary_rule")

    supporting_artifacts = template_manifest.get("supporting_artifacts", [])
    for rel in supporting_artifacts:
        if not (root / rel).exists():
            failures.append(f"template_supporting_artifact:missing_file:{rel}")
    _check_marker_block(
        template, template_manifest.get("record_metadata_fields", []), failures, "template_record"
    )
    _check_marker_block(
        template,
        template_manifest.get("anchor_and_ownership_fields", []),
        failures,
        "template_anchor",
    )
    _check_marker_block(
        template,
        template_manifest.get("validation_and_evidence_fields", []),
        failures,
        "template_validation",
    )
    _check_marker_block(
        template,
        template_manifest.get("stay_in_c_closeout_fields", []),
        failures,
        "template_stay_in_c",
    )
    _check_marker_block(
        template,
        template_manifest.get("reopen_evidence_fields", []),
        failures,
        "template_reopen",
    )
    _check_marker_block(
        template,
        template_manifest.get("supporting_context_fields", []),
        failures,
        "template_context",
    )
    _check_marker_block(
        template,
        template_manifest.get("review_outcome_fields", []),
        failures,
        "template_outcome",
    )
    _check_marker_block(
        template,
        template_manifest.get("usage_rules_required_terms", []),
        failures,
        "template_usage_rule",
    )

    _check_marker_block(
        indefinite_c_policy, REQUIRED_INDEFINITE_C_MARKERS, failures, "indefinite_c_policy"
    )
    _check_marker_block(handoff_note, REQUIRED_HANDOFF_MARKERS, failures, "handoff")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_template_manifest() -> str:
    return json.dumps(
        {
            "lane_key": "P15-L08",
            "phase": "Phase 15",
            "template_path": "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
            "surveyed_commit_mode": "dated_master_readback",
            "surveyed_commit_placeholder": "current-master-readback-YYYY-MM-DD",
            "supporting_artifacts": [
                "Documentation/zigux/phase15-freeze-map-governance.md",
                "Documentation/zigux/phase15-parity-scorecard.md",
                "Documentation/zigux/phase15-architecture-council-review-process.md",
                "Documentation/zigux/phase15-indefinite-c-policy.md",
                "Documentation/zigux/phase15-governance-lane-sequencing.md",
                "Documentation/zigux/phase15-study-only-anchor-accounting.md",
                "Documentation/zigux/review-checklist.md",
            ],
            "record_metadata_fields": [
                "DECISION_RECORD_ID=<replace-with-stable-id>",
                "decision record ID:",
                "PHASE=Phase 15",
                "LANE_KEY=P15-L08",
                "PHASE15_PROVENANCE_MODE=dated_master_readback",
                "SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD",
                "exact-head provenance exception note:",
                "REVIEW_STATUS=<blocked_review|stay_in_c|approved_status_bucket_change>",
            ],
            "anchor_and_ownership_fields": [
                "exact Linux anchor path:",
                "roadmap phase:",
                "lane owner:",
                "current status bucket:",
                "requested decision bucket:",
                "required approver set:",
                "rollback owner:",
            ],
            "validation_and_evidence_fields": [
                "validation gate summary:",
                "evidence archive path:",
                "latest blocker disposition:",
                "benchmark notes:",
                "replay command:",
                "rollback threshold:",
            ],
            "stay_in_c_closeout_fields": [
                "retained `freeze_in_c` decision:",
                "the current blocker:",
                "the required approver set:",
                "`retired_from_active_discussion` state:",
                "automatic return-to-blocked trigger:",
                "the reopen triggers:",
                "the trigger-specific evidence refresh:",
                "the evidence archive path that will be refreshed before any later reopen request:",
            ],
            "reopen_evidence_fields": [
                "the exact reopen trigger being exercised:",
                "refreshed evidence by path:",
                "the blocker disposition being challenged:",
                "the narrower seam or policy change that makes the new review safe to consider:",
            ],
            "supporting_context_fields": [
                "governance lane sequencing link or explicit scope note:",
                "study-only anchor accounting link or explicit freeze-map-anchor confirmation:",
                "parity scorecard link or blocker record:",
                "indefinite-C policy link or explicit non-applicability note:",
                "explicit non-goals:",
                "written rationale:",
            ],
            "review_outcome_fields": [
                "closeout result:",
                "follow-up owner:",
                "next bounded step:",
            ],
            "usage_rules_required_terms": [
                "Prefer the dated master readback form",
                "Only record an exact head",
                "Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review",
                "keep the request blocked and leave the C implementation as the product source of truth",
                "A stay-in-C closeout must keep the retained `freeze_in_c` decision",
                "A reopen request must cite the exact reopen trigger being exercised",
            ],
        },
        indent=2,
    ) + "\n"


def _sample_review_process_manifest() -> str:
    return json.dumps(
        {
            "decision_record_template": "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
            "review_checklist_entry_prompt": "if a freeze-map anchor is entering Architecture Council status review",
            "review_checklist_boundary_rule": "`Documentation/zigux/review-checklist.md` keeps the shared entry-review and closeout prompts explicit, but the exact Architecture Council field inventory stays owned by this note and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
            "review_checklist_stay_in_c_policy_boundary_rule": "`Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording",
        },
        indent=2,
    ) + "\n"


def _sample_template() -> str:
    return """# Phase 15 Architecture Council Decision Record Template

Use this template when a freeze-map anchor enters Architecture Council status review.

This is a review packet template, not approval by itself.

## Record Metadata

- `DECISION_RECORD_ID=<replace-with-stable-id>`
- decision record ID:
- `PHASE=Phase 15`
- `LANE_KEY=P15-L08`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- `SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`
- exact-head provenance exception note:
- `REVIEW_STATUS=<blocked_review|stay_in_c|approved_status_bucket_change>`

## Anchor And Ownership

- exact Linux anchor path:
- roadmap phase:
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

- retained `freeze_in_c` decision:
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

- governance lane sequencing link or explicit scope note:
- study-only anchor accounting link or explicit freeze-map-anchor confirmation:
- parity scorecard link or blocker record:
- indefinite-C policy link or explicit non-applicability note:
- explicit non-goals:
- written rationale:

## Review Outcome

- closeout result:
- follow-up owner:
- next bounded step:

## Usage Rules

- Prefer the dated master readback form for parked governance and stay-in-C review packets.
- Only record an exact head when the linked review needs it to anchor a named published decision, and explain that exception in the exact-head provenance note.
- Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.
- If any required field above cannot be stated honestly, keep the request blocked and leave the C implementation as the product source of truth.
- A stay-in-C closeout must keep the retained `freeze_in_c` decision, the current blocker, the required approver set, the automatic return-to-blocked trigger, `retired_from_active_discussion` state, reopen triggers, trigger-specific evidence refresh, and the evidence archive path that will be refreshed before any later reopen request explicit.
- A reopen request must cite the exact reopen trigger being exercised, refreshed evidence by path, the blocker disposition being challenged, and the narrower seam or policy change that makes the new review safe to consider.
"""


def _sample_review_process() -> str:
    return """# Phase 15 Architecture Council Review Process

- `Documentation/zigux/review-checklist.md` keeps the shared entry-review and closeout prompts explicit, but the exact Architecture Council field inventory stays owned by this note and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording
"""


def _sample_review_checklist() -> str:
    return """# Zigux Review Checklist

- if a freeze-map anchor is entering Architecture Council status review, does this checklist keep the shared entry-review prompt explicit while `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-architecture-council-decision-record-template.md` remain the owners of the exact Architecture Council field inventory, stay-in-C closeout record, and reopen-evidence details, and `Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording?
"""


def _sample_indefinite_c_policy() -> str:
    return """# Phase 15 Indefinite-C Policy

- required approver set
- automatic return-to-blocked trigger
- trigger-specific evidence refresh
- parity scorecard link or blocker record
"""


def _sample_handoff_note() -> str:
    return """# Phase 15 Handoff Next Steps Survey

- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-tests-readme-alignment.py`
"""


def _seed_repo(root: Path) -> None:
    _write(root / DECISION_TEMPLATE_PATH, _sample_template())
    _write(root / DECISION_TEMPLATE_MANIFEST_PATH, _sample_template_manifest())
    _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
    _write(root / REVIEW_PROCESS_MANIFEST_PATH, _sample_review_process_manifest())
    _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
    _write(root / INDEFINITE_C_POLICY_PATH, _sample_indefinite_c_policy())
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
    for rel in (
        "Documentation/zigux/phase15-freeze-map-governance.md",
        "Documentation/zigux/phase15-parity-scorecard.md",
        "Documentation/zigux/phase15-governance-lane-sequencing.md",
        "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    ):
        _write(root / rel, "# fixture\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_decision_template_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_repo(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        broken_template_root = root / "broken_template"
        _seed_repo(broken_template_root)
        _write(
            broken_template_root / DECISION_TEMPLATE_PATH,
            _sample_template().replace("- rollback owner:\n", "", 1),
        )
        failures = collect_failures(broken_template_root)
        expected = ["template_anchor:missing:rollback owner:"]
        if failures != expected:
            raise AssertionError(f"unexpected rollback-owner failure: {failures}")

        broken_rule_root = root / "broken_rule"
        _seed_repo(broken_rule_root)
        _write(
            broken_rule_root / DECISION_TEMPLATE_PATH,
            _sample_template().replace(
                "- Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(broken_rule_root)
        expected = [
            "template_usage_rule:missing:Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected study-only rule failure: {failures}")

        broken_checklist_root = root / "broken_checklist"
        _seed_repo(broken_checklist_root)
        _write(broken_checklist_root / REVIEW_CHECKLIST_PATH, "# Zigux Review Checklist\n")
        failures = collect_failures(broken_checklist_root)
        expected = ["review_checklist:missing_entry_prompt"]
        if failures != expected:
            raise AssertionError(f"unexpected checklist-prompt failure: {failures}")

        broken_policy_root = root / "broken_policy"
        _seed_repo(broken_policy_root)
        _write(
            broken_policy_root / INDEFINITE_C_POLICY_PATH,
            _sample_indefinite_c_policy().replace("- automatic return-to-blocked trigger\n", "", 1),
        )
        failures = collect_failures(broken_policy_root)
        expected = ["indefinite_c_policy:missing:automatic return-to-blocked trigger"]
        if failures != expected:
            raise AssertionError(f"unexpected policy failure: {failures}")

        broken_handoff_root = root / "broken_handoff"
        _seed_repo(broken_handoff_root)
        _write(
            broken_handoff_root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(broken_handoff_root)
        expected = [
            "handoff:missing:`Documentation/zigux/phase15-architecture-council-decision-record-template.md`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected handoff failure: {failures}")

    print("PHASE15_DECISION_RECORD_TEMPLATE_SELF_TEST=pass")
    print("PHASE15_DECISION_RECORD_TEMPLATE_SELF_TEST_CASES=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 decision-record template stays aligned with the current governance packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run synthetic self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 decision-record template check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
