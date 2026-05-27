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
DECISION_INDEX_PATH = Path("Documentation/zigux/phase15-architecture-council-decision-index.md")
INDEFINITE_C_POLICY_PATH = Path("Documentation/zigux/phase15-indefinite-c-policy.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
MANIFEST_PATH = Path("zigux/tests/phase15_architecture_council_review_process_manifest.json")
TEST_PATH = Path("zigux/tests/phase15_architecture_council_review_process.zig")
BUILD_GATE_PATH = Path("zigux/tests/phase15_architecture_council_review_process_build.zig")
CHECKER_PATH = Path("scripts/zigux/check-phase15-architecture-council-packet.py")

EXPECTED_LANE_KEY = "P15-L08"
EXPECTED_PHASE = "Phase 15"
EXPECTED_SURVEYED_COMMIT = "current-master-readback-2026-05-26"

REQUIRED_NOTE_MARKERS = (
    "PHASE15_STATUS=architecture_council_review_process_landed",
    "PHASE15_LANE_KEY=P15-L08",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
    "`zigux/tests/phase15_architecture_council_review_process.zig`",
    "`zigux/tests/phase15_architecture_council_review_process_build.zig`",
    "exact Architecture Council field inventory stays owned by this note and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-index.md` keeps the current Architecture Council decision inventory explicit, recording that no freeze-map anchor has an approved status change or stay-in-C closeout record on current `master` until a future decision record lands",
)

DECISION_INDEX_REQUIRED_MARKERS = (
    "PHASE15_STATUS=architecture_council_decision_index_landed",
    "PHASE15_LANE_KEY=P15-L09",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "approved status-bucket changes recorded on current `master`: none",
    "stay-in-C closeout decision records recorded on current `master`: none",
    "no freeze-map anchor has an Architecture Council approval for a status change on current `master`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay outside this index until the freeze map changes",
)


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
    failures: list[str] = []
    required_paths = (
        REVIEW_PROCESS_PATH,
        DECISION_RECORD_TEMPLATE_PATH,
        DECISION_INDEX_PATH,
        INDEFINITE_C_POLICY_PATH,
        REVIEW_CHECKLIST_PATH,
        MANIFEST_PATH,
        TEST_PATH,
        BUILD_GATE_PATH,
        CHECKER_PATH,
    )
    for rel in required_paths:
        if not (root / rel).exists():
            failures.append(f"missing_required_path:{rel}")
    if failures:
        return failures

    review_process = _read_text(root / REVIEW_PROCESS_PATH)
    decision_record_template = _read_text(root / DECISION_RECORD_TEMPLATE_PATH)
    decision_index = _read_text(root / DECISION_INDEX_PATH)
    indefinite_c_policy = _read_text(root / INDEFINITE_C_POLICY_PATH)
    review_checklist = _read_text(root / REVIEW_CHECKLIST_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append(f"lane_key:{manifest.get('lane_key')!r}")
    if manifest.get("phase") != EXPECTED_PHASE:
        failures.append(f"phase:{manifest.get('phase')!r}")
    if manifest.get("surveyed_commit") != EXPECTED_SURVEYED_COMMIT:
        failures.append(f"surveyed_commit:{manifest.get('surveyed_commit')!r}")
    if manifest.get("review_process_note") != str(REVIEW_PROCESS_PATH):
        failures.append("review_process_note")
    if manifest.get("decision_record_template") != str(DECISION_RECORD_TEMPLATE_PATH):
        failures.append("decision_record_template")
    if manifest.get("indefinite_c_policy_note") != str(INDEFINITE_C_POLICY_PATH):
        failures.append("indefinite_c_policy_note")
    if manifest.get("build_gate") != str(BUILD_GATE_PATH):
        failures.append("build_gate")

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in review_process:
            failures.append(f"missing_note_marker:{marker}")
    if EXPECTED_SURVEYED_COMMIT not in review_process:
        failures.append("surveyed_commit_note_marker")

    for marker in DECISION_INDEX_REQUIRED_MARKERS:
        if marker not in decision_index:
            failures.append(f"missing_decision_index_marker:{marker}")

    for marker in manifest.get("required_review_fields", []):
        if marker not in review_process:
            failures.append(f"missing_review_process_required_field:{marker}")
        if marker not in decision_record_template:
            failures.append(f"missing_decision_record_required_field:{marker}")

    for marker in manifest.get("stay_in_c_closeout_fields", []):
        if marker not in review_process:
            failures.append(f"missing_review_process_closeout_field:{marker}")
        if marker not in decision_record_template:
            failures.append(f"missing_decision_record_closeout_field:{marker}")

    for marker in manifest.get("reopen_evidence_fields", []):
        if marker not in review_process:
            failures.append(f"missing_review_process_reopen_field:{marker}")
        if marker not in decision_record_template:
            failures.append(f"missing_decision_record_reopen_field:{marker}")

    for marker in manifest.get("supporting_context_fields", []):
        if marker not in review_process:
            failures.append(f"missing_review_process_supporting_context_field:{marker}")
        if marker not in decision_record_template:
            failures.append(f"missing_decision_record_supporting_context_field:{marker}")

    for marker in manifest.get("review_outcome_fields", []):
        if marker not in review_process:
            failures.append(f"missing_review_process_review_outcome_field:{marker}")
        if marker not in decision_record_template:
            failures.append(f"missing_decision_record_review_outcome_field:{marker}")

    for marker in manifest.get("review_outcome_markers", []):
        if marker not in review_process:
            failures.append(f"missing_review_process_review_outcome_marker:{marker}")

    for marker in manifest.get("study_only_anchor_review_markers", []):
        if marker not in review_process:
            failures.append(f"missing_study_only_boundary_marker:{marker}")

    checklist_prompt = _line_containing(
        review_checklist,
        manifest.get("review_checklist_entry_prompt", ""),
    )
    if checklist_prompt is None:
        failures.append("missing_review_checklist_entry_prompt")
    else:
        for marker in (
            manifest.get("review_process_note", ""),
            manifest.get("decision_record_template", ""),
            manifest.get("review_checklist_stay_in_c_policy_boundary_rule", ""),
        ):
            if marker and marker not in checklist_prompt:
                failures.append(f"missing_review_checklist_boundary_marker:{marker}")

        for marker in manifest.get("review_checklist_entry_prompt_required_markers", []):
            if marker not in checklist_prompt:
                failures.append(f"missing_review_checklist_required_marker:{marker}")

    for marker in manifest.get("indefinite_c_policy_required_markers", []):
        if marker not in indefinite_c_policy:
            failures.append(f"missing_indefinite_c_policy_marker:{marker}")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest() -> str:
    payload = {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
        "surveyed_commit_mode": "dated_master_readback",
        "review_process_note": str(REVIEW_PROCESS_PATH),
        "decision_record_template": str(DECISION_RECORD_TEMPLATE_PATH),
        "indefinite_c_policy_note": str(INDEFINITE_C_POLICY_PATH),
        "build_gate": str(BUILD_GATE_PATH),
        "review_checklist_entry_prompt": "if a freeze-map anchor is entering Architecture Council status review",
        "review_checklist_stay_in_c_policy_boundary_rule": "`Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording",
        "review_checklist_entry_prompt_required_markers": [
            "required approver set",
            "rollback owner",
            "evidence archive path",
            "retained blocker posture",
            "trigger-specific evidence refresh",
            "return-to-blocked wording",
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
        "study_only_anchor_review_markers": [
            "`kernel/workqueue.c`",
            "`kernel/trace/ring_buffer.c`",
            "remain boundary-study context routed through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
            "not candidates for a freeze-in-C status review through this note",
        ],
        "indefinite_c_policy_required_markers": [
            "required approver set",
            "automatic return-to-blocked trigger",
            "trigger-specific evidence refresh",
            "governance lane sequencing link or explicit scope note",
            "study-only anchor accounting link or explicit freeze-map-anchor confirmation",
            "parity scorecard link or blocker record",
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def _sample_review_process() -> str:
    return """# Phase 15 Architecture Council Review Process

This note records the bounded Phase 15 review-policy packet for freeze-map anchors that remain in C indefinitely.

## Status

- `PHASE15_STATUS=architecture_council_review_process_landed`
- `PHASE15_LANE_KEY=P15-L08`
- `PHASE15_SLICE=stay-in-c-review-field-inventory`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-26`
- `PHASE15_PACKET_OWNER=Architecture Council`
- `PHASE15_PACKET_VALIDATION_GATE=python3 scripts/zigux/check-phase15-review-process-handoff.py && zig test zigux/tests/phase15_architecture_council_review_process.zig && zig build test --build-file zigux/tests/phase15_architecture_council_review_process_build.zig`
- `PHASE15_PACKET_ROLLBACK_OWNER=Architecture Council`

## Current Phase 15 posture

- `scripts/zigux/check-phase15-review-process-handoff.py`
- `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- `zigux/tests/phase15_architecture_council_review_process.zig`
- `zigux/tests/phase15_architecture_council_review_process_build.zig`
- the exact Architecture Council field inventory stays owned by this note and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `Documentation/zigux/phase15-architecture-council-decision-index.md` keeps the current Architecture Council decision inventory explicit, recording that no freeze-map anchor has an approved status change or stay-in-C closeout record on current `master` until a future decision record lands

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

Study-only freeze-map anchors stay outside this Architecture Council status-review packet until the freeze map itself changes.

`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain boundary-study context routed through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`, not candidates for a freeze-in-C status review through this note, unless the freeze map and supporting governance packet are explicitly updated first.

## Review outcomes

- keep the anchor in `freeze_in_c`
- reopen review later with narrower evidence
- approve a status-bucket change in a separately linked decision record

- closeout result
- follow-up owner
- next bounded step

## Stay-In-C closeout rule

- the retained `freeze_in_c` decision
- the current blocker
- the required approver set
- governance lane sequencing link or explicit scope note
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
"""


def _sample_decision_record_template() -> str:
    return """# Phase 15 Architecture Council Decision Record Template

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
"""


def _sample_decision_index() -> str:
    return """# Phase 15 Architecture Council Decision Index

## Status

- `PHASE15_STATUS=architecture_council_decision_index_landed`
- `PHASE15_LANE_KEY=P15-L09`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`

## Current decision inventory

- approved status-bucket changes recorded on current `master`: none
- stay-in-C closeout decision records recorded on current `master`: none
- no freeze-map anchor has an Architecture Council approval for a status change on current `master`

## Index rules

- every future Architecture Council decision record must route back through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, and `Documentation/zigux/phase15-parity-scorecard.md`
- `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay outside this index until the freeze map changes
"""


def _sample_indefinite_c_policy() -> str:
    return """# Phase 15 Indefinite-C Policy

- the decision record ID, lane owner, required approver set, and rollback owner
- the automatic return-to-blocked trigger, retained `retired_from_active_discussion` state, reopen triggers, and trigger-specific evidence refresh
- the governance lane sequencing link or explicit scope note, the study-only anchor accounting link or explicit freeze-map-anchor confirmation, parity scorecard link or blocker record, explicit non-goals, and written rationale for why the anchor remains in C
"""


def _sample_review_checklist() -> str:
    return """# Zigux Review Checklist

- if a freeze-map anchor is entering Architecture Council status review, does this checklist keep the shared entry-review prompt explicit, including the required approver set, rollback owner, and evidence archive path, while `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-architecture-council-decision-record-template.md` remain the owners of the exact Architecture Council field inventory, stay-in-C closeout record, and reopen-evidence details, and `Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording?
"""


def _sample_test_file() -> str:
    return """const std = @import("std");

test "placeholder focused review-process replay exists" {
    try std.testing.expect(true);
}
"""


def _sample_build_gate() -> str:
    return """const std = @import("std");

pub fn build(b: *std.Build) void {
    const review_process_module = b.createModule(.{
        .root_source_file = b.path("phase15_architecture_council_review_process.zig"),
    });
    const review_process_tests = b.addTest(.{
        .name = "phase15-architecture-council-review-process-tests",
        .root_module = review_process_module,
    });
    const run_review_process_tests = b.addRunArtifact(review_process_tests);
    const test_step = b.step("test", "Run the focused Phase 15 Architecture Council review-process test");
    test_step.dependOn(&run_review_process_tests.step);
}
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_architecture_council_packet_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(root / DECISION_RECORD_TEMPLATE_PATH, _sample_decision_record_template())
        _write(root / DECISION_INDEX_PATH, _sample_decision_index())
        _write(root / INDEFINITE_C_POLICY_PATH, _sample_indefinite_c_policy())
        _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
        _write(root / MANIFEST_PATH, _sample_manifest())
        _write(root / TEST_PATH, _sample_test_file())
        _write(root / BUILD_GATE_PATH, _sample_build_gate())
        _write(root / CHECKER_PATH, "# fixture\n")

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        cases = (
            (REVIEW_PROCESS_PATH, "- roadmap phase\n", ["missing_review_process_required_field:roadmap phase"]),
            (DECISION_RECORD_TEMPLATE_PATH, "- next bounded step:\n", ["missing_decision_record_review_outcome_field:next bounded step"]),
            (DECISION_INDEX_PATH, "- approved status-bucket changes recorded on current `master`: none\n", ["missing_decision_index_marker:approved status-bucket changes recorded on current `master`: none"]),
            (INDEFINITE_C_POLICY_PATH, "parity scorecard link or blocker record", ["missing_indefinite_c_policy_marker:parity scorecard link or blocker record"]),
            (REVIEW_CHECKLIST_PATH, "retained blocker posture", ["missing_review_checklist_boundary_marker:`Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording", "missing_review_checklist_required_marker:retained blocker posture"]),
        )

        for rel, marker, expected in cases:
            case_root = root / f"case_{case_count}"
            _write(case_root / REVIEW_PROCESS_PATH, _sample_review_process())
            _write(case_root / DECISION_RECORD_TEMPLATE_PATH, _sample_decision_record_template())
            _write(case_root / DECISION_INDEX_PATH, _sample_decision_index())
            _write(case_root / INDEFINITE_C_POLICY_PATH, _sample_indefinite_c_policy())
            _write(case_root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
            _write(case_root / MANIFEST_PATH, _sample_manifest())
            _write(case_root / TEST_PATH, _sample_test_file())
            _write(case_root / BUILD_GATE_PATH, _sample_build_gate())
            _write(case_root / CHECKER_PATH, "# fixture\n")
            text = _read_text(case_root / rel)
            _write(case_root / rel, text.replace(marker, "", 1))
            failures = collect_failures(case_root)
            if failures != expected:
                raise AssertionError(f"unexpected failures for {rel}: {failures}")
            case_count += 1

    print("PHASE15_ARCHITECTURE_COUNCIL_PACKET_SELF_TEST=pass")
    print(f"PHASE15_ARCHITECTURE_COUNCIL_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the core Phase 15 Architecture Council packet stays aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the Zigux Phase 15 governance packet",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run synthetic fixture coverage for the Phase 15 Architecture Council packet checker",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 Architecture Council packet check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
