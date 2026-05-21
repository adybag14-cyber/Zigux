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

CURRENT_READBACK_MARKER = "current-master-readback-2026-05-20"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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
    shared_gap_note = _read_text(root / SHARED_GAP_NOTE_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)

    failures: list[str] = []

    manifest_expectations = (
        ("lane_key", "P15-L08"),
        ("phase", "Phase 15"),
        ("surveyed_commit", CURRENT_READBACK_MARKER),
        ("surveyed_commit_mode", "dated_master_readback"),
        ("review_process_note", REVIEW_PROCESS_PATH.as_posix()),
        ("decision_record_template", DECISION_RECORD_TEMPLATE_PATH.as_posix()),
        ("indefinite_c_policy_note", INDEFINITE_C_POLICY_PATH.as_posix()),
        ("handoff_note", HANDOFF_NOTE_PATH.as_posix()),
        ("shared_summary_gap_note", SHARED_GAP_NOTE_PATH.as_posix()),
        ("checker", "scripts/zigux/check-phase15-review-process-handoff.py"),
        ("build_gate", BUILD_GATE_PATH.as_posix()),
        (
            "review_checklist_entry_prompt",
            "if a freeze-map anchor is entering Architecture Council status review",
        ),
        (
            "review_checklist_boundary_rule",
            "`Documentation/zigux/review-checklist.md` keeps the shared entry-review and closeout prompts explicit, but the exact Architecture Council field inventory stays owned by this note and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
        ),
        (
            "review_checklist_stay_in_c_policy_boundary_rule",
            "`Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording",
        ),
        (
            "decision_record_template_study_only_rule",
            "Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.",
        ),
    )
    for key, expected in manifest_expectations:
        if manifest.get(key) != expected:
            failures.append(f"manifest field drifted: {key}")

    review_process_markers = (
        "PHASE15_STATUS=architecture_council_review_process_landed",
        "PHASE15_LANE_KEY=P15-L08",
        "PHASE15_SLICE=stay-in-c-review-field-inventory",
        "PHASE15_PROVENANCE_MODE=dated_master_readback",
        CURRENT_READBACK_MARKER,
        "no Architecture Council approval is currently recorded for a freeze-map status change",
        "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
        "`Documentation/zigux/phase15-indefinite-c-policy.md`",
        "`scripts/zigux/check-phase15-review-process-handoff.py`",
        "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
        "`zigux/tests/phase15_architecture_council_review_process.zig`",
        "`zigux/tests/phase15_architecture_council_review_process_build.zig`",
        "broader validator-first shared-summary surfaces remain gap-tracked",
        "governance lane sequencing link or explicit scope note",
        "study-only anchor accounting link or explicit freeze-map-anchor confirmation",
        "`kernel/workqueue.c`",
        "`kernel/trace/ring_buffer.c`",
        "not candidates for a freeze-in-C status review through this note",
    )
    for marker in review_process_markers:
        if marker not in review_process:
            failures.append(f"review-process note missing marker: {marker}")

    if manifest["decision_record_template"] not in review_process:
        failures.append("review-process note missing decision-record template path")
    if manifest["indefinite_c_policy_note"] not in review_process:
        failures.append("review-process note missing indefinite-C policy path")
    if manifest["review_checklist_boundary_rule"] not in review_process:
        failures.append("review-process note missing checklist boundary rule")
    if manifest["review_checklist_stay_in_c_policy_boundary_rule"] not in review_checklist:
        failures.append("review checklist missing stay-in-C boundary rule")

    for field in manifest["required_review_fields"]:
        if field not in review_process:
            failures.append(f"review-process note missing required field: {field}")
        if field not in decision_record_template:
            failures.append(f"decision-record template missing required field: {field}")

    for field in manifest["stay_in_c_closeout_fields"]:
        if field not in review_process:
            failures.append(f"review-process note missing closeout field: {field}")
        if field not in decision_record_template:
            failures.append(f"decision-record template missing closeout field: {field}")

    for field in manifest["reopen_evidence_fields"]:
        if field not in review_process:
            failures.append(f"review-process note missing reopen field: {field}")
        if field not in decision_record_template:
            failures.append(f"decision-record template missing reopen field: {field}")

    for field in manifest.get("supporting_context_fields", []):
        if field not in review_process:
            failures.append(f"review-process note missing supporting-context field: {field}")
        if field not in decision_record_template:
            failures.append(
                f"decision-record template missing supporting-context field: {field}"
            )

    for marker in manifest["decision_record_template_required_markers"]:
        if marker not in decision_record_template:
            failures.append(f"decision-record template missing marker: {marker}")

    for marker in manifest["indefinite_c_policy_required_markers"]:
        if marker not in indefinite_c_policy:
            failures.append(f"indefinite-C policy note missing marker: {marker}")

    for marker in manifest.get("study_only_anchor_review_markers", []):
        if marker not in review_process:
            failures.append(f"review-process note missing study-only marker: {marker}")
    if manifest["decision_record_template_study_only_rule"] not in decision_record_template:
        failures.append("decision-record template missing study-only rule")

    checklist_entry_prompt = _line_containing(
        review_checklist, manifest["review_checklist_entry_prompt"]
    )
    if checklist_entry_prompt is None:
        failures.append("review checklist missing Architecture Council entry-review prompt")
    else:
        checklist_expected_markers = (
            manifest["review_process_note"],
            manifest["decision_record_template"],
            "owners of the exact Architecture Council field inventory",
            "stay-in-C closeout record",
            "reopen-evidence details",
            manifest["review_checklist_stay_in_c_policy_boundary_rule"],
        )
        for marker in checklist_expected_markers:
            if marker not in checklist_entry_prompt:
                failures.append(f"review checklist entry prompt missing marker: {marker}")

    for marker in manifest["handoff_required_markers"]:
        if marker not in handoff_note:
            failures.append(f"handoff note missing marker: {marker}")

    for marker in manifest["shared_gap_expected_present_paths"]:
        if marker not in shared_gap_note:
            failures.append(f"shared-summary gap note missing present path: {marker}")
        repo_path = _marker_to_repo_path(marker)
        if repo_path is not None and not (root / repo_path).exists():
            failures.append(f"shared-summary gap present path missing from repo: {marker}")

    for marker in manifest["shared_gap_expected_missing_paths"]:
        if marker not in shared_gap_note:
            failures.append(f"shared-summary gap note missing blocked path: {marker}")
        repo_path = _marker_to_repo_path(marker)
        if repo_path is not None and (root / repo_path).exists():
            failures.append(f"shared-summary gap still treats shipped path as missing: {marker}")

    if not (root / TEST_PATH).exists():
        failures.append(f"missing focused replay file: {TEST_PATH.as_posix()}")
    if not (root / BUILD_GATE_PATH).exists():
        failures.append(f"missing build-gate file: {BUILD_GATE_PATH.as_posix()}")

    return failures


def _sample_manifest() -> str:
    return json.dumps(
        {
            "lane_key": "P15-L08",
            "phase": "Phase 15",
            "surveyed_commit": CURRENT_READBACK_MARKER,
            "surveyed_commit_mode": "dated_master_readback",
            "review_process_note": REVIEW_PROCESS_PATH.as_posix(),
            "decision_record_template": DECISION_RECORD_TEMPLATE_PATH.as_posix(),
            "indefinite_c_policy_note": INDEFINITE_C_POLICY_PATH.as_posix(),
            "handoff_note": HANDOFF_NOTE_PATH.as_posix(),
            "shared_summary_gap_note": SHARED_GAP_NOTE_PATH.as_posix(),
            "checker": "scripts/zigux/check-phase15-review-process-handoff.py",
            "build_gate": BUILD_GATE_PATH.as_posix(),
            "review_checklist_entry_prompt": "if a freeze-map anchor is entering Architecture Council status review",
            "review_checklist_boundary_rule": "`Documentation/zigux/review-checklist.md` keeps the shared entry-review and closeout prompts explicit, but the exact Architecture Council field inventory stays owned by this note and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
            "review_checklist_stay_in_c_policy_boundary_rule": "`Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording",
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
            "supporting_context_fields": [
                "governance lane sequencing link or explicit scope note",
                "study-only anchor accounting link or explicit freeze-map-anchor confirmation",
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
                "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
                "`zigux/tests/phase15_architecture_council_review_process_build.zig`",
                "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
                "`zigux/tests/phase15_handoff_next_steps.zig`",
                "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
                "`scripts/zigux/check-phase15-review-process-handoff.py`",
                "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
                "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
                "one focused review-process checker, one focused tests-readme checker, the shared-summary gap checker, and the focused handoff-note checker",
            ],
            "shared_gap_expected_present_paths": [
                "`Documentation/zigux/phase15-parity-scorecard-survey.md`",
                "`Documentation/zigux/phase15-readiness-gate-survey.md`",
                "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
                "`scripts/zigux/check-phase15-scripts-readme-alignment.py`",
                "`scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`",
                "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
                "`zigux/tests/phase15_freeze_map_governance.zig`",
                "`zigux/tests/phase15_parity_scorecard.zig`",
                "`zigux/tests/phase15_indefinite_c_policy.json`",
                "`zigux/tests/phase15_indefinite_c_policy.zig`",
                "`zigux/tests/phase15_architecture_council_review_process.zig`",
                "`zigux/tests/phase15_architecture_council_review_process_build.zig`",
                "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
                "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
                "`zigux/tests/phase15_handoff_next_steps.zig`",
                "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
                "`scripts/zigux/check-phase15-review-process-handoff.py`",
                "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
            ],
            "shared_gap_expected_missing_paths": [
                "`scripts/zigux/validate-phase15.py`",
                "`zigux/tests/phase15_build.zig`",
            ],
        },
        indent=2,
    ) + "\n"


def _sample_review_process() -> str:
    return f"""# Phase 15 Architecture Council Review Process

- `PHASE15_STATUS=architecture_council_review_process_landed`
- `PHASE15_LANE_KEY=P15-L08`
- `PHASE15_SLICE=stay-in-c-review-field-inventory`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `{CURRENT_READBACK_MARKER}`
- no Architecture Council approval is currently recorded for a freeze-map status change
- this note keeps the roadmap-required Architecture Council review-process surface honest on current `master`: the docs-root field inventory, the dedicated decision-record template, the dedicated review-process manifest, the focused review-process handoff checker, the focused Zig replay, and the focused build-file replay are landed, while the broader validator-first shared-summary surfaces remain gap-tracked by `Documentation/zigux/phase15-shared-summary-gap.md`

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
- governance lane sequencing link or explicit scope note
- study-only anchor accounting link or explicit freeze-map-anchor confirmation
- explicit non-goals
- written rationale

## Study-only boundary

`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain boundary-study context routed through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` and are not candidates for a freeze-in-C status review through this note.

## Stay-In-C closeout rule

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

## Current Phase 15 posture

- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- `zigux/tests/phase15_architecture_council_review_process.zig`
- `zigux/tests/phase15_architecture_council_review_process_build.zig`
- `Documentation/zigux/review-checklist.md` keeps the shared entry-review and closeout prompts explicit, but the exact Architecture Council field inventory stays owned by this note and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
"""


def _sample_decision_record_template() -> str:
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

- governance lane sequencing link or explicit scope note:
- study-only anchor accounting link or explicit freeze-map-anchor confirmation:
- parity scorecard link or blocker record:
- indefinite-C policy link or explicit non-applicability note:
- explicit non-goals:
- written rationale:

## Usage Rules

- Prefer the dated master readback form for parked governance and stay-in-C review packets.
- Only record an exact head when the linked review needs it to anchor a named published decision
- Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.
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

- if a freeze-map anchor is entering Architecture Council status review, does this checklist keep the shared entry-review prompt explicit, including the required approver set, while `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-architecture-council-decision-record-template.md` remain the owners of the exact Architecture Council field inventory, stay-in-C closeout record, and reopen-evidence details, and `Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording?
"""


def _sample_handoff_note() -> str:
    return """# Phase 15 Handoff Next Steps Survey

- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-shared-summary-gap.md`
- `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- `zigux/tests/phase15_architecture_council_review_process_build.zig`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`
- `zigux/tests/phase15_handoff_next_steps.zig`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-tests-readme-alignment.py`
- `scripts/zigux/check-phase15-handoff-note-alignment.py`
- one focused review-process checker, one focused tests-readme checker, the shared-summary gap checker, and the focused handoff-note checker
"""


def _sample_shared_gap_note() -> str:
    present = "\n".join(json.loads(_sample_manifest())["shared_gap_expected_present_paths"])
    missing = "\n".join(json.loads(_sample_manifest())["shared_gap_expected_missing_paths"])
    return f"""# Phase 15 Shared Summary Gap

{present}
{missing}
"""


def _seed(root: Path) -> None:
    _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
    _write(root / DECISION_RECORD_TEMPLATE_PATH, _sample_decision_record_template())
    _write(root / INDEFINITE_C_POLICY_PATH, _sample_indefinite_c_policy())
    _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
    _write(root / SHARED_GAP_NOTE_PATH, _sample_shared_gap_note())
    _write(root / MANIFEST_PATH, _sample_manifest())
    manifest = json.loads(_sample_manifest())
    for marker in manifest["shared_gap_expected_present_paths"]:
        repo_path = _marker_to_repo_path(marker)
        if repo_path is not None and repo_path not in {
            MANIFEST_PATH,
            REVIEW_PROCESS_PATH,
            DECISION_RECORD_TEMPLATE_PATH,
            INDEFINITE_C_POLICY_PATH,
            REVIEW_CHECKLIST_PATH,
            HANDOFF_NOTE_PATH,
            SHARED_GAP_NOTE_PATH,
        }:
            _write(root / repo_path, "present\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_arch_council_review_process_") as tmp_dir:
        root = Path(tmp_dir)
        _seed(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        cases = (
            (REVIEW_PROCESS_PATH, CURRENT_READBACK_MARKER),
            (DECISION_RECORD_TEMPLATE_PATH, "governance lane sequencing link or explicit scope note"),
            (REVIEW_CHECKLIST_PATH, "`Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording"),
            (HANDOFF_NOTE_PATH, "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`"),
            (SHARED_GAP_NOTE_PATH, "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`"),
        )

        for rel, marker in cases:
            case_root = root / f"case_{case_count}"
            _seed(case_root)
            text = _read_text(case_root / rel)
            _write(case_root / rel, text.replace(marker, "", 1))
            failures = collect_failures(case_root)
            if not failures:
                raise AssertionError(f"negative coverage did not trigger for {rel}: {marker}")
            case_count += 1

    print("PHASE15_ARCHITECTURE_COUNCIL_REVIEW_PROCESS_SELF_TEST=pass")
    print(f"PHASE15_ARCHITECTURE_COUNCIL_REVIEW_PROCESS_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 15 Architecture Council review-process packet for drift."
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

    print("Phase 15 Architecture Council review-process check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
