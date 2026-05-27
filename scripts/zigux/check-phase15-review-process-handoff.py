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
SHARED_GAP_NOTE_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
MANIFEST_PATH = Path("zigux/tests/phase15_architecture_council_review_process_manifest.json")
TEST_PATH = Path("zigux/tests/phase15_architecture_council_review_process.zig")
BUILD_GATE_PATH = Path("zigux/tests/phase15_architecture_council_review_process_build.zig")
CURRENT_READBACK_MARKER = "current-master-readback-2026-05-26"
GOVERNANCE_SCOPE_FIELD = "governance lane sequencing link or explicit scope note"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _marker_to_repo_path(marker: str) -> Path | None:
    if marker.startswith("`") and marker.endswith("`") and "/" in marker:
        return Path(marker.strip("`"))
    return None


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
    gap_note = _read_text(root / SHARED_GAP_NOTE_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)

    failures: list[str] = []

    if manifest["surveyed_commit"] not in review_process:
        failures.append("review-process note is missing the manifest surveyed_commit marker")

    if manifest["decision_record_template"] not in review_process:
        failures.append("review-process note is missing the decision-record template path")

    if manifest["indefinite_c_policy_note"] not in review_process:
        failures.append("review-process note is missing the indefinite-C policy companion path")

    build_gate = manifest.get("build_gate")
    if build_gate is None:
        failures.append("review-process manifest is missing build_gate")
        build_gate_path = BUILD_GATE_PATH
    else:
        build_gate_path = Path(build_gate)
        if build_gate not in review_process:
            failures.append("review-process note is missing the focused build-file replay path")

    if manifest["decision_record_template"] not in handoff_note:
        failures.append("handoff note is missing the decision-record template path")

    if manifest["review_checklist_boundary_rule"] not in review_process:
        failures.append("review-process note is missing the review-checklist boundary rule")

    if manifest["handoff_note"] not in review_process:
        failures.append("review-process note is missing the handoff note path")

    if manifest["shared_summary_gap_note"] not in review_process:
        failures.append("review-process note is missing the shared-summary gap note path")

    for marker in (
        "PHASE15_STATUS=architecture_council_review_process_landed",
        "PHASE15_LANE_KEY=P15-L08",
        "PHASE15_PROVENANCE_MODE=dated_master_readback",
        "`scripts/zigux/check-phase15-review-process-handoff.py`",
        "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
        "`zigux/tests/phase15_architecture_council_review_process.zig`",
    ):
        if marker not in review_process:
            failures.append(f"review-process note is missing required marker: {marker}")

    review_process_required_metadata_markers = manifest.get(
        "review_process_required_metadata_markers"
    )
    if not review_process_required_metadata_markers:
        failures.append("review-process manifest is missing review_process_required_metadata_markers")
    else:
        for marker in review_process_required_metadata_markers:
            if marker not in review_process:
                failures.append(f"review-process note is missing metadata marker: {marker}")

    decision_record_template_metadata_markers = manifest.get(
        "decision_record_template_metadata_markers"
    )
    if not decision_record_template_metadata_markers:
        failures.append(
            "review-process manifest is missing decision_record_template_metadata_markers"
        )
    else:
        for marker in decision_record_template_metadata_markers:
            if marker not in decision_record_template:
                failures.append(f"decision-record template is missing metadata marker: {marker}")

    decision_record_template_section_headings = manifest.get(
        "decision_record_template_section_headings"
    )
    if not decision_record_template_section_headings:
        failures.append(
            "review-process manifest is missing decision_record_template_section_headings"
        )
    else:
        for heading in decision_record_template_section_headings:
            if heading not in decision_record_template:
                failures.append(
                    f"decision-record template is missing section heading: {heading}"
                )

    for field in manifest["required_review_fields"]:
        if field not in review_process:
            failures.append(f"review-process note is missing required review field: {field}")
        if field not in decision_record_template:
            failures.append(f"decision-record template is missing required review field: {field}")

    checklist_entry_prompt = _line_containing(
        review_checklist, manifest["review_checklist_entry_prompt"]
    )
    if checklist_entry_prompt is None:
        failures.append(
            "review checklist is missing the Phase 15 Architecture Council entry-review prompt"
        )
    else:
        checklist_expected_markers = (
            manifest["review_process_note"],
            manifest["decision_record_template"],
            "owners of the exact Architecture Council field inventory",
            "stay-in-C closeout record",
            "reopen-evidence details",
        )
        for marker in checklist_expected_markers:
            if marker not in checklist_entry_prompt:
                failures.append(
                    f"review checklist entry prompt is missing required boundary marker: {marker}"
                )
        if (
            manifest["review_checklist_stay_in_c_policy_boundary_rule"]
            not in checklist_entry_prompt
        ):
            failures.append(
                "review checklist entry prompt is missing required stay-in-C policy boundary marker"
            )

        entry_prompt_required_markers = manifest.get(
            "review_checklist_entry_prompt_required_markers"
        )
        if not entry_prompt_required_markers:
            failures.append(
                "review-process manifest is missing review_checklist_entry_prompt_required_markers"
            )
        else:
            for marker in entry_prompt_required_markers:
                if marker not in checklist_entry_prompt:
                    failures.append(
                        f"review checklist entry prompt is missing required explicit marker: {marker}"
                    )

    if GOVERNANCE_SCOPE_FIELD not in manifest["stay_in_c_closeout_fields"]:
        failures.append(
            "review-process manifest is missing stay-in-C closeout field: governance lane sequencing link or explicit scope note"
        )

    for field in manifest["stay_in_c_closeout_fields"]:
        if field not in review_process:
            failures.append(f"review-process note is missing stay-in-C closeout field: {field}")
        if field not in decision_record_template:
            failures.append(
                f"decision-record template is missing stay-in-C closeout field: {field}"
            )

    for field in manifest["reopen_evidence_fields"]:
        if field not in review_process:
            failures.append(f"review-process note is missing reopen-evidence field: {field}")
        if field not in decision_record_template:
            failures.append(
                f"decision-record template is missing reopen-evidence field: {field}"
            )

    for field in manifest.get("supporting_context_fields", []):
        if field not in review_process:
            failures.append(f"review-process note is missing supporting context field: {field}")
        if field not in decision_record_template:
            failures.append(
                f"decision-record template is missing supporting context field: {field}"
            )

    for field in manifest.get("review_outcome_fields", []):
        if field not in review_process:
            failures.append(f"review-process note is missing review outcome field: {field}")
        if field not in decision_record_template:
            failures.append(
                f"decision-record template is missing review outcome field: {field}"
            )

    for marker in manifest.get("review_outcome_markers", []):
        if marker not in review_process:
            failures.append(f"review-process note is missing review outcome marker: {marker}")

    for marker in manifest.get("study_only_anchor_review_markers", []):
        if marker not in review_process:
            failures.append(f"review-process note is missing study-only boundary marker: {marker}")

    study_only_template_rule = manifest.get("decision_record_template_study_only_rule")
    if study_only_template_rule is None:
        failures.append("review-process manifest is missing decision_record_template_study_only_rule")
    elif study_only_template_rule not in decision_record_template:
        failures.append("decision-record template is missing the study-only anchor boundary rule")

    for marker in manifest["indefinite_c_policy_required_markers"]:
        if marker not in indefinite_c_policy:
            failures.append(f"indefinite-C policy note is missing required marker: {marker}")

    for marker in manifest["decision_record_template_required_markers"]:
        if marker not in decision_record_template:
            failures.append(f"decision-record template is missing required marker: {marker}")

    for marker in manifest["handoff_required_markers"]:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing required marker: {marker}")

    for marker in manifest["shared_gap_expected_present_paths"]:
        if marker not in gap_note:
            failures.append(f"shared-summary gap note is missing newly landed path: {marker}")

        repo_path = _marker_to_repo_path(marker)
        if repo_path is not None and not (root / repo_path).exists():
            failures.append(
                f"shared-summary gap note claims materialized path is missing from repo: {marker}"
            )

    for path in manifest["shared_gap_expected_missing_paths"]:
        if path not in gap_note:
            failures.append(f"shared-summary gap note is missing still-blocked path: {path}")

    if not (root / TEST_PATH).exists():
        failures.append(
            "focused review-process Zig replay is missing from repo: `zigux/tests/phase15_architecture_council_review_process.zig`"
        )

    if not (root / build_gate_path).exists():
        failures.append(
            f"focused review-process build-file replay is missing from repo: `{build_gate_path.as_posix()}`"
        )

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest() -> str:
    return json.dumps(
        {
            "lane_key": "P15-L08",
            "phase": "Phase 15",
            "surveyed_commit": CURRENT_READBACK_MARKER,
            "surveyed_commit_mode": "dated_master_readback",
            "review_process_note": "Documentation/zigux/phase15-architecture-council-review-process.md",
            "decision_record_template": "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
            "indefinite_c_policy_note": "Documentation/zigux/phase15-indefinite-c-policy.md",
            "handoff_note": "Documentation/zigux/phase15-handoff-next-steps-survey.md",
            "shared_summary_gap_note": "Documentation/zigux/phase15-shared-summary-gap.md",
            "checker": "scripts/zigux/check-phase15-review-process-handoff.py",
            "build_gate": "zigux/tests/phase15_architecture_council_review_process_build.zig",
            "review_checklist_entry_prompt": "if a freeze-map anchor is entering Architecture Council status review",
            "review_checklist_boundary_rule": "`Documentation/zigux/review-checklist.md` keeps the shared entry-review and closeout prompts explicit, but the exact Architecture Council field inventory stays owned by this note and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
            "review_checklist_stay_in_c_policy_boundary_rule": "`Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording",
            "review_checklist_entry_prompt_required_markers": [
                "required approver set",
                "rollback owner",
                "evidence archive path",
                "retained blocker posture",
                "trigger-specific evidence refresh",
                "return-to-blocked wording",
            ],
            "review_process_required_metadata_markers": [
                "`PHASE15_PACKET_OWNER=Architecture Council`",
                "`PHASE15_PACKET_VALIDATION_GATE=python3 scripts/zigux/check-phase15-review-process-handoff.py && zig test zigux/tests/phase15_architecture_council_review_process.zig && zig build test --build-file zigux/tests/phase15_architecture_council_review_process_build.zig`",
                "`PHASE15_PACKET_ROLLBACK_OWNER=Architecture Council`",
            ],
            "decision_record_template_metadata_markers": [
                "`DECISION_RECORD_ID=<replace-with-stable-id>`",
                "decision record ID:",
                "`PHASE=Phase 15`",
                "`LANE_KEY=<replace-with-lane-key>`",
                "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
                "`SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`",
                "exact-head provenance exception note:",
                "`REVIEW_STATUS=<blocked_review|stay_in_c|approved_status_bucket_change>`",
            ],
            "decision_record_template_section_headings": [
                "## Record Metadata",
                "## Anchor And Ownership",
                "## Validation And Evidence",
                "## Stay-In-C Closeout",
                "## Reopen Evidence",
                "## Supporting Context",
                "## Review Outcome",
                "## Usage Rules",
            ],
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
                "governance lane sequencing link or explicit scope note",
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
            "supporting_context_fields": [
                "governance lane sequencing link or explicit scope note",
                "study-only anchor accounting link or explicit freeze-map-anchor confirmation",
            ],
            "review_outcome_fields": [
                "closeout result",
                "follow-up owner",
                "next bounded step",
            ],
            "review_outcome_markers": [
                "keep the anchor in `freeze_in_c`",
                "reopen review later with narrower evidence",
                "approve a status-bucket change in a separately linked decision record",
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
            "study_only_anchor_review_markers": [
                "`kernel/workqueue.c`",
                "`kernel/trace/ring_buffer.c`",
                "remain boundary-study context routed through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
                "not candidates for a freeze-in-C status review through this note",
            ],
            "decision_record_template_study_only_rule": "Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.",
            "handoff_required_markers": [
                "`Documentation/zigux/review-checklist.md`",
                "`Documentation/zigux/README.md`",
                "`Documentation/zigux/phase15-architecture-council-review-process.md`",
                "`Documentation/zigux/phase15-indefinite-c-policy.md`",
                "`Documentation/zigux/phase15-shared-summary-gap.md`",
                "`zigux/tests/phase15_freeze_map_governance.zig`",
                "`zigux/tests/phase15_parity_scorecard.json`",
                "`zigux/tests/phase15_parity_scorecard.zig`",
                "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
                "`zigux/tests/phase15_architecture_council_review_process_build.zig`",
                "`zigux/tests/phase15_governance_lane_sequencing_manifest.json`",
                "`zigux/tests/phase15_governance_lane_sequencing.zig`",
                "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
                "`zigux/tests/phase15_handoff_next_steps.zig`",
                "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
                "`scripts/zigux/check-phase15-docs-readme-alignment.py`",
                "`scripts/zigux/check-phase15-review-process-handoff.py`",
                "`scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`",
                "`scripts/zigux/check-phase15-readiness-gate-packet.py`",
                "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
                "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
                "`scripts/zigux/check-phase15-shared-summary-gap.py`",
                "`scripts/zigux/validate-phase15.py`",
                "one focused review-process checker, one focused review-checklist study-only checker, one focused readiness-packet checker, one focused tests-readme checker, the shared-summary gap checker, and the focused handoff-note checker",
            ],
            "shared_gap_expected_present_paths": [
                "`Documentation/zigux/phase15-architecture-council-review-process.md`",
                "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
                "`Documentation/zigux/phase15-parity-scorecard-survey.md`",
                "`Documentation/zigux/phase15-readiness-gate-survey.md`",
                "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
                "`scripts/zigux/check-phase15-docs-readme-alignment.py`",
                "`scripts/zigux/check-phase15-scripts-readme-alignment.py`",
                "`scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`",
                "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
                "`scripts/zigux/check-phase15-readiness-gate-packet.py`",
                "`scripts/zigux/check-phase15-shared-summary-gap.py`",
                "`zigux/tests/phase15_freeze_map_governance.zig`",
                "`zigux/tests/phase15_parity_scorecard.json`",
                "`zigux/tests/phase15_parity_scorecard.zig`",
                "`zigux/tests/phase15_indefinite_c_policy.json`",
                "`zigux/tests/phase15_indefinite_c_policy.zig`",
                "`zigux/tests/phase15_architecture_council_review_process.zig`",
                "`zigux/tests/phase15_architecture_council_review_process_build.zig`",
                "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
                "`zigux/tests/phase15_governance_lane_sequencing_manifest.json`",
                "`zigux/tests/phase15_governance_lane_sequencing.zig`",
                "`zigux/tests/phase15_readiness_gate_manifest.json`",
                "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
                "`zigux/tests/phase15_handoff_next_steps.zig`",
                "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
                "`scripts/zigux/check-phase15-review-process-handoff.py`",
                "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
                "`scripts/zigux/validate-phase15.py`",
            ],
            "shared_gap_expected_missing_paths": [
                "`zigux/tests/phase15_build.zig`",
            ],
        },
        indent=2,
    ) + "\n"


def _sample_review_process() -> str:
    return f"""# Phase 15 Architecture Council Review Process

- `PHASE15_STATUS=architecture_council_review_process_landed`
- `PHASE15_LANE_KEY=P15-L08`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `{CURRENT_READBACK_MARKER}`
- `PHASE15_PACKET_OWNER=Architecture Council`
- `PHASE15_PACKET_VALIDATION_GATE=python3 scripts/zigux/check-phase15-review-process-handoff.py && zig test zigux/tests/phase15_architecture_council_review_process.zig && zig build test --build-file zigux/tests/phase15_architecture_council_review_process_build.zig`
- `PHASE15_PACKET_ROLLBACK_OWNER=Architecture Council`
- this note keeps the docs-root field inventory, the dedicated decision-record template, the dedicated review-process manifest, the focused review-process handoff checker, the focused Zig replay, the focused build-file replay, and the stay-in-C policy companion explicit through `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_architecture_council_review_process.zig`, and `zigux/tests/phase15_architecture_council_review_process_build.zig`
- `Documentation/zigux/review-checklist.md` keeps the shared entry-review and closeout prompts explicit, but the exact Architecture Council field inventory stays owned by this note and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- the broader validator-first packet remains gap-tracked by `Documentation/zigux/phase15-shared-summary-gap.md`, and maintenance follow-through routes through `Documentation/zigux/phase15-handoff-next-steps-survey.md`

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

Study-only freeze-map anchors stay outside this Architecture Council status-review packet until the freeze map itself changes.

`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain boundary-study context routed through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`, not candidates for a freeze-in-C status review through this note, unless the freeze map and supporting governance packet are explicitly updated first.

The Architecture Council may close a request only in one of these bounded ways:
- keep the anchor in `freeze_in_c`
- reopen review later with narrower evidence
- approve a status-bucket change in a separately linked decision record

Every closeout record must also keep all of the following explicit in the linked decision record:
- closeout result
- follow-up owner
- next bounded step

If a freeze-in-C review closes without a status change, the closeout record must keep all of the following explicit:
- the retained `freeze_in_c` decision
- the current blocker
- the required approver set
- governance lane sequencing link or explicit scope note
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
"""


def _sample_decision_record_template() -> str:
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

- the retained `freeze_in_c` decision:
- the current blocker:
- the required approver set:
- governance lane sequencing link or explicit scope note:
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
"""


def _sample_indefinite_c_policy() -> str:
    return """# Phase 15 Indefinite-C Policy

- `PHASE15_STATUS=indefinite_c_policy_packet_landed`
- `PHASE15_LANE_KEY=P15-L13`
- current repo reality: the roadmap-required stay-in-C policy packet is landed and remains maintenance-only under the same blocked deep-core posture

- the decision record ID, lane owner, required approver set, and rollback owner
- the automatic return-to-blocked trigger, retained `retired_from_active_discussion` state, reopen triggers, and trigger-specific evidence refresh
- the parity scorecard link or blocker record, explicit non-goals, and written rationale for why the anchor remains in C
"""


def _sample_review_checklist() -> str:
    return """# Zigux Review Checklist

  * if a freeze-map anchor is entering Architecture Council status review, does this checklist keep the shared entry-review prompt explicit, including the required approver set, rollback owner, and evidence archive path, while `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-architecture-council-decision-record-template.md` remain the owners of the exact Architecture Council field inventory, stay-in-C closeout record, and reopen-evidence details, and `Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording?
"""


def _sample_handoff_note() -> str:
    return """# Phase 15 Handoff Next Steps Survey

- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-shared-summary-gap.md`
- `zigux/tests/phase15_freeze_map_governance.zig`
- `zigux/tests/phase15_parity_scorecard.json`
- `zigux/tests/phase15_parity_scorecard.zig`
- `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- `zigux/tests/phase15_architecture_council_review_process_build.zig`
- `zigux/tests/phase15_governance_lane_sequencing_manifest.json`
- `zigux/tests/phase15_governance_lane_sequencing.zig`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`
- `zigux/tests/phase15_handoff_next_steps.zig`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
- `scripts/zigux/check-phase15-docs-readme-alignment.py`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`
- `scripts/zigux/check-phase15-readiness-gate-packet.py`
- `scripts/zigux/check-phase15-tests-readme-alignment.py`
- `scripts/zigux/check-phase15-handoff-note-alignment.py`
- `scripts/zigux/check-phase15-shared-summary-gap.py`
- `scripts/zigux/validate-phase15.py`
- one focused review-process checker, one focused review-checklist study-only checker, one focused readiness-packet checker, one focused tests-readme checker, the shared-summary gap checker, and the focused handoff-note checker
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
"""


def _sample_gap_note() -> str:
    return """# Phase 15 Shared Summary Gap

- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `Documentation/zigux/phase15-parity-scorecard-survey.md`
- `Documentation/zigux/phase15-readiness-gate-survey.md`
- `Documentation/zigux/phase15-governance-lane-sequencing.md`
- `scripts/zigux/check-phase15-docs-readme-alignment.py`
- `scripts/zigux/check-phase15-scripts-readme-alignment.py`
- `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`
- `scripts/zigux/check-phase15-tests-readme-alignment.py`
- `scripts/zigux/check-phase15-readiness-gate-packet.py`
- `scripts/zigux/check-phase15-shared-summary-gap.py`
- `zigux/tests/phase15_freeze_map_governance.zig`
- `zigux/tests/phase15_parity_scorecard.json`
- `zigux/tests/phase15_parity_scorecard.zig`
- `zigux/tests/phase15_indefinite_c_policy.json`
- `zigux/tests/phase15_indefinite_c_policy.zig`
- `zigux/tests/phase15_architecture_council_review_process.zig`
- `zigux/tests/phase15_architecture_council_review_process_build.zig`
- `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- `zigux/tests/phase15_governance_lane_sequencing_manifest.json`
- `zigux/tests/phase15_governance_lane_sequencing.zig`
- `zigux/tests/phase15_readiness_gate_manifest.json`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`
- `zigux/tests/phase15_handoff_next_steps.zig`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-handoff-note-alignment.py`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
"""


def _sample_test_file() -> str:
    return """const std = @import(\"std\");

test \"placeholder focused review-process replay exists\" {
    try std.testing.expect(true);
}
"""


def _sample_build_gate() -> str:
    return """const std = @import(\"std\");

pub fn build(b: *std.Build) void {
    const review_process_module = b.createModule(.{
        .root_source_file = b.path(\"phase15_architecture_council_review_process.zig\"),
    });
    const review_process_tests = b.addTest(.{
        .name = \"phase15-architecture-council-review-process-tests\",
        .root_module = review_process_module,
    });
    const run_review_process_tests = b.addRunArtifact(review_process_tests);
    const test_step = b.step(\"test\", \"Run the focused Phase 15 Architecture Council review-process test\");
    test_step.dependOn(&run_review_process_tests.step);
}
"""


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_review_process_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(root / DECISION_RECORD_TEMPLATE_PATH, _sample_decision_record_template())
        _write(root / INDEFINITE_C_POLICY_PATH, _sample_indefinite_c_policy())
        _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
        _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(root / SHARED_GAP_NOTE_PATH, _sample_gap_note())
        _write(root / MANIFEST_PATH, _sample_manifest())
        _write(root / Path("scripts/zigux/check-phase15-review-process-handoff.py"), "# fixture\n")
        _write(root / Path("scripts/zigux/check-phase15-handoff-note-alignment.py"), "# fixture\n")
        _write(root / Path("scripts/zigux/check-phase15-review-checklist-study-only-alignment.py"), "# fixture\n")
        _write(root / Path("scripts/zigux/check-phase15-readiness-gate-packet.py"), "# fixture\n")
        _write(root / Path("scripts/zigux/check-phase15-scripts-readme-alignment.py"), "# fixture\n")
        _write(root / Path("scripts/zigux/check-phase15-tests-readme-alignment.py"), "# fixture\n")
        _write(root / Path("scripts/zigux/check-phase15-shared-summary-gap.py"), "# fixture\n")
        _write(root / Path("scripts/zigux/validate-phase15.py"), "# fixture\n")
        _write(root / TEST_PATH, _sample_test_file())
        _write(root / BUILD_GATE_PATH, _sample_build_gate())
        sample_manifest = json.loads(_sample_manifest())
        for marker in sample_manifest["shared_gap_expected_present_paths"]:
            repo_path = _marker_to_repo_path(marker)
            if repo_path is None or (root / repo_path).exists():
                continue
            _write(root / repo_path, "# fixture\n")

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        _write(
            root / REVIEW_PROCESS_PATH,
            _sample_review_process().replace("- roadmap phase\n", "", 1),
        )
        failures = collect_failures(root)
        if failures != ["review-process note is missing required review field: roadmap phase"]:
            raise AssertionError(f"unexpected roadmap-phase failure: {failures}")

        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        manifest_data = json.loads(_sample_manifest())
        manifest_data["stay_in_c_closeout_fields"] = [
            field
            for field in manifest_data["stay_in_c_closeout_fields"]
            if field != GOVERNANCE_SCOPE_FIELD
        ]
        _write(root / MANIFEST_PATH, json.dumps(manifest_data, indent=2) + "\n")
        failures = collect_failures(root)
        if failures != [
            "review-process manifest is missing stay-in-C closeout field: governance lane sequencing link or explicit scope note"
        ]:
            raise AssertionError(
                f"unexpected stay-in-c governance-manifest failure: {failures}"
            )

        _write(root / MANIFEST_PATH, _sample_manifest())
        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(
            root / REVIEW_PROCESS_PATH,
            _sample_review_process().replace(
                "- `PHASE15_PACKET_OWNER=Architecture Council`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        if failures != [
            "review-process note is missing metadata marker: `PHASE15_PACKET_OWNER=Architecture Council`"
        ]:
            raise AssertionError(f"unexpected review-process metadata failure: {failures}")

        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(
            root / DECISION_RECORD_TEMPLATE_PATH,
            _sample_decision_record_template().replace(
                "- `REVIEW_STATUS=<blocked_review|stay_in_c|approved_status_bucket_change>`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        if failures != [
            "decision-record template is missing metadata marker: `REVIEW_STATUS=<blocked_review|stay_in_c|approved_status_bucket_change>`"
        ]:
            raise AssertionError(f"unexpected review-status metadata failure: {failures}")

        _write(root / DECISION_RECORD_TEMPLATE_PATH, _sample_decision_record_template())
        _write(
            root / DECISION_RECORD_TEMPLATE_PATH,
            _sample_decision_record_template().replace("## Review Outcome\n\n", "", 1),
        )
        failures = collect_failures(root)
        if failures != ["decision-record template is missing section heading: ## Review Outcome"]:
            raise AssertionError(f"unexpected section-heading failure: {failures}")

        _write(root / DECISION_RECORD_TEMPLATE_PATH, _sample_decision_record_template())
        _write(
            root / REVIEW_PROCESS_PATH,
            _sample_review_process().replace(
                "- closeout result\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        if failures != ["review-process note is missing review outcome field: closeout result"]:
            raise AssertionError(f"unexpected review-outcome-note failure: {failures}")

        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(
            root / DECISION_RECORD_TEMPLATE_PATH,
            _sample_decision_record_template().replace("- follow-up owner:\n", "", 1),
        )
        failures = collect_failures(root)
        if failures != ["decision-record template is missing review outcome field: follow-up owner"]:
            raise AssertionError(f"unexpected review-outcome-template failure: {failures}")

        _write(root / DECISION_RECORD_TEMPLATE_PATH, _sample_decision_record_template())
        _write(
            root / REVIEW_PROCESS_PATH,
            _sample_review_process().replace(
                "- approve a status-bucket change in a separately linked decision record\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        if failures != [
            "review-process note is missing review outcome marker: approve a status-bucket change in a separately linked decision record"
        ]:
            raise AssertionError(f"unexpected review-outcome-marker failure: {failures}")

        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(
            root / REVIEW_PROCESS_PATH,
            _sample_review_process().replace(
                "- governance lane sequencing link or explicit scope note\n",
                "",
                2,
            ),
        )
        failures = collect_failures(root)
        if failures != [
            "review-process note is missing stay-in-C closeout field: governance lane sequencing link or explicit scope note",
            "review-process note is missing supporting context field: governance lane sequencing link or explicit scope note",
        ]:
            raise AssertionError(f"unexpected stay-in-c governance-note failure: {failures}")

        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(
            root / DECISION_RECORD_TEMPLATE_PATH,
            _sample_decision_record_template().replace(
                "- governance lane sequencing link or explicit scope note:\n",
                "",
                2,
            ),
        )
        failures = collect_failures(root)
        if failures != [
            "decision-record template is missing stay-in-C closeout field: governance lane sequencing link or explicit scope note",
            "decision-record template is missing supporting context field: governance lane sequencing link or explicit scope note",
        ]:
            raise AssertionError(f"unexpected stay-in-c governance-template failure: {failures}")

        _write(root / DECISION_RECORD_TEMPLATE_PATH, _sample_decision_record_template())
        _write(
            root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "- `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        if failures != [
            "handoff note is missing required marker: `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`"
        ]:
            raise AssertionError(f"unexpected handoff-checklist-study-only failure: {failures}")

        _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(
            root / HANDOFF_NOTE_PATH,
            _sample_handoff_note().replace(
                "- `scripts/zigux/check-phase15-shared-summary-gap.py`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        if failures != [
            "handoff note is missing required marker: `scripts/zigux/check-phase15-shared-summary-gap.py`"
        ]:
            raise AssertionError(f"unexpected handoff-shared-summary-gap failure: {failures}")

        _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(
            root / SHARED_GAP_NOTE_PATH,
            _sample_gap_note().replace(
                "- `scripts/zigux/check-phase15-shared-summary-gap.py`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        if failures != [
            "shared-summary gap note is missing newly landed path: `scripts/zigux/check-phase15-shared-summary-gap.py`"
        ]:
            raise AssertionError(f"unexpected shared-gap-shared-summary-checker failure: {failures}")

        _write(root / SHARED_GAP_NOTE_PATH, _sample_gap_note())
        _write(
            root / SHARED_GAP_NOTE_PATH,
            _sample_gap_note().replace(
                "- `zigux/tests/phase15_governance_lane_sequencing.zig`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        if failures != [
            "shared-summary gap note is missing newly landed path: `zigux/tests/phase15_governance_lane_sequencing.zig`"
        ]:
            raise AssertionError(f"unexpected shared-gap-governance-replay failure: {failures}")

        _write(root / SHARED_GAP_NOTE_PATH, _sample_gap_note())
        _write(
            root / SHARED_GAP_NOTE_PATH,
            _sample_gap_note().replace(
                "- `scripts/zigux/check-phase15-readiness-gate-packet.py`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        if failures != [
            "shared-summary gap note is missing newly landed path: `scripts/zigux/check-phase15-readiness-gate-packet.py`"
        ]:
            raise AssertionError(f"unexpected shared-gap-readiness-checker failure: {failures}")

        _write(root / SHARED_GAP_NOTE_PATH, _sample_gap_note())
        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(
                "required approver set, ",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        if failures != [
            "review checklist entry prompt is missing required explicit marker: required approver set"
        ]:
            raise AssertionError(f"unexpected checklist-required-approver failure: {failures}")

    print("PHASE15_REVIEW_PROCESS_HANDOFF_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 Architecture Council review-process packet and handoff note stay aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing Documentation/zigux, scripts/zigux, and zigux/tests",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic repo fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 review-process handoff check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())