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
FOCUSED_REPLAY_PATH = Path("zigux/tests/phase15_architecture_council_review_process.zig")
FOCUSED_BUILD_PATH = Path("zigux/tests/phase15_architecture_council_review_process_build.zig")
REVIEW_PROCESS_CHECKER_PATH = Path("scripts/zigux/check-phase15-review-process-handoff.py")
HANDOFF_CHECKER_PATH = Path("scripts/zigux/check-phase15-handoff-note-alignment.py")
CHECKER_PATH = Path("scripts/zigux/check-phase15-architecture-council-decision-record-template.py")

EXPECTED_LANE_KEY = "P15-L08"
EXPECTED_PHASE = "Phase 15"
EXPECTED_SURVEYED_COMMIT = "current-master-readback-2026-05-23"

REQUIRED_TEMPLATE_METADATA_MARKERS = (
    "`DECISION_RECORD_ID=<replace-with-stable-id>`",
    "decision record ID:",
    "`PHASE=Phase 15`",
    "`LANE_KEY=P15-L08`",
    "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
    "`SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`",
    "exact-head provenance exception note:",
    "`REVIEW_STATUS=<blocked_review|stay_in_c|approved_status_bucket_change>`",
)

REQUIRED_TEMPLATE_SECTION_HEADINGS = (
    "## Record Metadata",
    "## Anchor And Ownership",
    "## Validation And Evidence",
    "## Stay-In-C Closeout",
    "## Reopen Evidence",
    "## Supporting Context",
    "## Review Outcome",
    "## Usage Rules",
)

REQUIRED_TEMPLATE_RULES = (
    "Prefer the dated master readback form for parked governance and stay-in-C review packets.",
    "Only record an exact head when the linked review needs it to anchor a named published decision",
    "Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.",
    "If any required field above cannot be stated honestly, keep the request blocked and leave the C implementation as the product source of truth.",
    "A stay-in-C closeout must keep the retained `freeze_in_c` decision, the current blocker, the required approver set, the governance lane sequencing link or explicit scope note, the automatic return-to-blocked trigger, `retired_from_active_discussion` state, reopen triggers, trigger-specific evidence refresh, and the evidence archive path that will be refreshed before any later reopen request explicit.",
    "A reopen request must cite the exact reopen trigger being exercised, refreshed evidence by path, the blocker disposition being challenged, and the narrower seam or policy change that makes the new review safe to consider.",
)

def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

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
    required_paths = (
        REVIEW_PROCESS_PATH,
        DECISION_RECORD_TEMPLATE_PATH,
        INDEFINITE_C_POLICY_PATH,
        REVIEW_CHECKLIST_PATH,
        HANDOFF_NOTE_PATH,
        SHARED_GAP_NOTE_PATH,
        MANIFEST_PATH,
        FOCUSED_REPLAY_PATH,
        FOCUSED_BUILD_PATH,
        REVIEW_PROCESS_CHECKER_PATH,
        HANDOFF_CHECKER_PATH,
    )
    for path in required_paths:
        if not (root / path).exists():
            failures.append(f"missing_required_path:{path.as_posix()}")
    if failures:
        return failures

    review_process = _read_text(root / REVIEW_PROCESS_PATH)
    template = _read_text(root / DECISION_RECORD_TEMPLATE_PATH)
    indefinite_c_policy = _read_text(root / INDEFINITE_C_POLICY_PATH)
    review_checklist = _read_text(root / REVIEW_CHECKLIST_PATH)
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)
    shared_gap_note = _read_text(root / SHARED_GAP_NOTE_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append(f"manifest:lane_key:{manifest.get('lane_key')!r}")
    if manifest.get("phase") != EXPECTED_PHASE:
        failures.append(f"manifest:phase:{manifest.get('phase')!r}")
    if manifest.get("surveyed_commit") != EXPECTED_SURVEYED_COMMIT:
        failures.append(f"manifest:surveyed_commit:{manifest.get('surveyed_commit')!r}")
    if manifest.get("review_process_note") != REVIEW_PROCESS_PATH.as_posix():
        failures.append("manifest:review_process_note")
    if manifest.get("decision_record_template") != DECISION_RECORD_TEMPLATE_PATH.as_posix():
        failures.append("manifest:decision_record_template")
    if manifest.get("indefinite_c_policy_note") != INDEFINITE_C_POLICY_PATH.as_posix():
        failures.append("manifest:indefinite_c_policy_note")
    if manifest.get("handoff_note") != HANDOFF_NOTE_PATH.as_posix():
        failures.append("manifest:handoff_note")
    if manifest.get("shared_summary_gap_note") != SHARED_GAP_NOTE_PATH.as_posix():
        failures.append("manifest:shared_summary_gap_note")
    if manifest.get("checker") != REVIEW_PROCESS_CHECKER_PATH.as_posix():
        failures.append("manifest:checker")
    if manifest.get("build_gate") != FOCUSED_BUILD_PATH.as_posix():
        failures.append("manifest:build_gate")

    for marker in REQUIRED_TEMPLATE_METADATA_MARKERS:
        if marker not in template:
            failures.append(f"template:missing_metadata_marker:{marker}")

    for heading in REQUIRED_TEMPLATE_SECTION_HEADINGS:
        if heading not in template:
            failures.append(f"template:missing_section_heading:{heading}")

    for marker in REQUIRED_TEMPLATE_RULES:
        if marker not in template:
            failures.append(f"template:missing_usage_rule:{marker}")

    for field_group in (
        "required_review_fields",
        "stay_in_c_closeout_fields",
        "reopen_evidence_fields",
        "supporting_context_fields",
        "review_outcome_fields",
    ):
        values = manifest.get(field_group)
        if not values:
            failures.append(f"manifest:missing_field_group:{field_group}")
            continue
        for field in values:
            if field not in template:
                failures.append(f"template:missing_field:{field_group}:{field}")

    for field_group in (
        "review_outcome_markers",
        "decision_record_template_required_markers",
    ):
        values = manifest.get(field_group)
        if not values:
            failures.append(f"manifest:missing_marker_group:{field_group}")
            continue
        for marker in values:
            if marker not in template:
                failures.append(f"template:missing_marker:{field_group}:{marker}")

    study_only_rule = manifest.get("decision_record_template_study_only_rule")
    if not study_only_rule:
        failures.append("manifest:missing_decision_record_template_study_only_rule")
    elif study_only_rule not in template:
        failures.append("template:missing_study_only_rule")

    for marker in (
        EXPECTED_SURVEYED_COMMIT,
        f"`{DECISION_RECORD_TEMPLATE_PATH.as_posix()}`",
        "defaults that record to dated-master-readback provenance",
        "the exact Architecture Council field inventory stays owned by this note and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    ):
        if marker not in review_process:
            failures.append(f"review_process:missing_marker:{marker}")

    entry_prompt = _line_containing(review_checklist, manifest.get("review_checklist_entry_prompt", ""))
    if entry_prompt is None:
        failures.append("review_checklist:missing_entry_prompt")
    else:
        for marker in (
            f"`{REVIEW_PROCESS_PATH.as_posix()}`",
            f"`{DECISION_RECORD_TEMPLATE_PATH.as_posix()}`",
            "owners of the exact Architecture Council field inventory",
            "stay-in-C closeout record",
            "reopen-evidence details",
        ):
            if marker not in entry_prompt:
                failures.append(f"review_checklist:missing_prompt_boundary:{marker}")
        stay_in_c_boundary = manifest.get("review_checklist_stay_in_c_policy_boundary_rule")
        if stay_in_c_boundary not in entry_prompt:
            failures.append("review_checklist:missing_stay_in_c_boundary")
        for marker in manifest.get("review_checklist_entry_prompt_required_markers", []):
            if marker not in entry_prompt:
                failures.append(f"review_checklist:missing_prompt_marker:{marker}")

    required_policy_line = (
        "Those ownership, validation, and rollback fields stay coupled to "
        "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`"
    )
    if required_policy_line not in indefinite_c_policy:
        failures.append("indefinite_c_policy:missing_template_coupling_line")
    for marker in manifest.get("indefinite_c_policy_required_markers", []):
        if marker not in indefinite_c_policy:
            failures.append(f"indefinite_c_policy:missing_required_marker:{marker}")

    for marker in (
        f"`{DECISION_RECORD_TEMPLATE_PATH.as_posix()}`",
        f"`{FOCUSED_BUILD_PATH.as_posix()}`",
    ):
        if marker not in handoff_note:
            failures.append(f"handoff_note:missing_marker:{marker}")

    if (
        f"`{DECISION_RECORD_TEMPLATE_PATH.as_posix()}`"
        not in shared_gap_note
    ):
        failures.append("shared_gap_note:missing_template_path")
    if (
        f"`{HANDOFF_CHECKER_PATH.as_posix()}`"
        not in shared_gap_note
    ):
        failures.append("shared_gap_note:missing_handoff_checker_path")

    return failures

def _sample_manifest() -> str:
    return json.dumps(
        {
            "lane_key": EXPECTED_LANE_KEY,
            "phase": EXPECTED_PHASE,
            "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
            "surveyed_commit_mode": "dated_master_readback",
            "review_process_note": REVIEW_PROCESS_PATH.as_posix(),
            "decision_record_template": DECISION_RECORD_TEMPLATE_PATH.as_posix(),
            "indefinite_c_policy_note": INDEFINITE_C_POLICY_PATH.as_posix(),
            "handoff_note": HANDOFF_NOTE_PATH.as_posix(),
            "shared_summary_gap_note": SHARED_GAP_NOTE_PATH.as_posix(),
            "checker": REVIEW_PROCESS_CHECKER_PATH.as_posix(),
            "build_gate": FOCUSED_BUILD_PATH.as_posix(),
            "review_checklist_entry_prompt": "if a freeze-map anchor is entering Architecture Council status review",
            "review_checklist_stay_in_c_policy_boundary_rule": "`Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording",
            "review_checklist_entry_prompt_required_markers": ["required approver set", "rollback owner", "evidence archive path"],
            "required_review_fields": ["exact Linux anchor path", "roadmap phase", "decision record ID", "lane owner", "current status bucket", "requested decision bucket", "required approver set", "rollback owner", "validation gate summary", "evidence archive path", "latest blocker disposition", "benchmark notes", "replay command", "rollback threshold", "automatic return-to-blocked trigger", "`retired_from_active_discussion` state", "reopen triggers", "trigger-specific evidence refresh", "parity scorecard link or blocker record", "indefinite-C policy link or explicit non-applicability note", "explicit non-goals", "written rationale"],
            "stay_in_c_closeout_fields": ["the retained `freeze_in_c` decision", "the current blocker", "the required approver set", "governance lane sequencing link or explicit scope note", "`retired_from_active_discussion` state", "automatic return-to-blocked trigger", "the reopen triggers", "trigger-specific evidence refresh", "the evidence archive path that will be refreshed before any later reopen request"],
            "reopen_evidence_fields": ["the exact reopen trigger being exercised", "refreshed evidence by path", "the blocker disposition being challenged", "the narrower seam or policy change that makes the new review safe to consider"],
            "supporting_context_fields": ["governance lane sequencing link or explicit scope note", "study-only anchor accounting link or explicit freeze-map-anchor confirmation"],
            "review_outcome_fields": ["closeout result", "follow-up owner", "next bounded step"],
            "review_outcome_markers": ["keep the anchor in `freeze_in_c`", "reopen review later with narrower evidence", "approve a status-bucket change in a separately linked decision record"],
            "decision_record_template_required_markers": ["`PHASE15_PROVENANCE_MODE=dated_master_readback`", "`SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`", "exact-head provenance exception note:", "Prefer the dated master readback form for parked governance and stay-in-C review packets.", "Only record an exact head when the linked review needs it to anchor a named published decision"],
            "decision_record_template_study_only_rule": "Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.",
            "indefinite_c_policy_required_markers": ["required approver set", "automatic return-to-blocked trigger", "trigger-specific evidence refresh", "parity scorecard link or blocker record"]
        },
        indent=2,
    ) + "\n"

def _sample_review_process() -> str:
    return (
        "# Phase 15 Architecture Council Review Process\n\n"
        f"- surveyed against dated current-master readback marker `{EXPECTED_SURVEYED_COMMIT}`\n"
        "- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`\n"
        "- defaults that record to dated-master-readback provenance\n"
        "- the exact Architecture Council field inventory stays owned by this note and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`\n"
    )

def _sample_template() -> str:
    lines = ["# Phase 15 Architecture Council Decision Record Template", ""]
    lines.extend(REQUIRED_TEMPLATE_SECTION_HEADINGS)
    lines.append("")
    lines.extend(REQUIRED_TEMPLATE_METADATA_MARKERS)
    lines.append("")
    lines.extend(REQUIRED_TEMPLATE_RULES)
    lines.append("")
    manifest = _read_manifest_from_text(_sample_manifest())
    for group in ("required_review_fields", "stay_in_c_closeout_fields", "reopen_evidence_fields", "supporting_context_fields", "review_outcome_fields", "review_outcome_markers", "decision_record_template_required_markers"):
        lines.extend(manifest[group])
    lines.append(manifest["decision_record_template_study_only_rule"])
    return "\n".join(lines) + "\n"

def _read_manifest_from_text(text: str) -> dict:
    return json.loads(text)

def _sample_review_checklist() -> str:
    return (
        "# Zigux Review Checklist\n\n"
        "* if a freeze-map anchor is entering Architecture Council status review or recording a stay-in-C closeout, does this checklist keep the shared entry-review and closeout prompts explicit, including the required approver set, rollback owner, and evidence archive path, while `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-architecture-council-decision-record-template.md` remain the owners of the exact Architecture Council field inventory, stay-in-C closeout record, and reopen-evidence details, and `Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording?\n"
    )

def _sample_indefinite_c_policy() -> str:
    manifest = _read_manifest_from_text(_sample_manifest())
    return (
        "# Phase 15 Indefinite-C Policy\n\n"
        "Those ownership, validation, and rollback fields stay coupled to `Documentation/zigux/phase15-architecture-council-decision-record-template.md` so the stay-in-C closeout record reuses the same reviewable ownership vocabulary as the broader Phase 15 governance packet.\n"
        + "\n".join(f"- {marker}" for marker in manifest["indefinite_c_policy_required_markers"])
        + "\n"
    )

def _sample_handoff_note() -> str:
    return (
        "# Phase 15 Handoff Next Steps Survey\n\n"
        "- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`\n"
        "- `zigux/tests/phase15_architecture_council_review_process_build.zig`\n"
    )

def _sample_shared_gap_note() -> str:
    return (
        "# Phase 15 Shared Summary Gap\n\n"
        "- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`\n"
        "- `scripts/zigux/check-phase15-handoff-note-alignment.py`\n"
    )

def _seed(root: Path) -> None:
    _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
    _write(root / DECISION_RECORD_TEMPLATE_PATH, _sample_template())
    _write(root / INDEFINITE_C_POLICY_PATH, _sample_indefinite_c_policy())
    _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
    _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
    _write(root / SHARED_GAP_NOTE_PATH, _sample_shared_gap_note())
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / FOCUSED_REPLAY_PATH, "const std = @import(\"std\");\n")
    _write(root / FOCUSED_BUILD_PATH, "const std = @import(\"std\");\n")
    _write(root / REVIEW_PROCESS_CHECKER_PATH, "#!/usr/bin/env python3\n")
    _write(root / HANDOFF_CHECKER_PATH, "#!/usr/bin/env python3\n")

def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_decision_record_template_") as tmp_dir:
        root = Path(tmp_dir)
        _seed(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_template_rule = root / "missing_template_rule"
        _seed(missing_template_rule)
        _write(missing_template_rule / DECISION_RECORD_TEMPLATE_PATH, _sample_template().replace("If any required field above cannot be stated honestly, keep the request blocked and leave the C implementation as the product source of truth.\n", "", 1))
        failures = collect_failures(missing_template_rule)
        expected = ["template:missing_usage_rule:If any required field above cannot be stated honestly, keep the request blocked and leave the C implementation as the product source of truth."]
        if failures != expected:
            raise AssertionError(f"unexpected missing-template-rule failure: {failures}")

        missing_checklist_boundary = root / "missing_checklist_boundary"
        _seed(missing_checklist_boundary)
        _write(missing_checklist_boundary / REVIEW_CHECKLIST_PATH, _sample_review_checklist().replace("owners of the exact Architecture Council field inventory, stay-in-C closeout record, and reopen-evidence details, and `Documentation/zigux/phase15-indefinite-c-policy.md` remains the dedicated stay-in-C policy companion for retained blocker posture, trigger-specific evidence refresh, and return-to-blocked wording?", "owners of the exact Architecture Council field inventory?", 1))
        failures = collect_failures(missing_checklist_boundary)
        expected = ["review_checklist:missing_prompt_boundary:stay-in-C closeout record", "review_checklist:missing_prompt_boundary:reopen-evidence details", "review_checklist:missing_stay_in_c_boundary"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-checklist-boundary failure: {failures}")

        missing_policy_coupling = root / "missing_policy_coupling"
        _seed(missing_policy_coupling)
        _write(missing_policy_coupling / INDEFINITE_C_POLICY_PATH, "# Phase 15 Indefinite-C Policy\n\n- required approver set\n- automatic return-to-blocked trigger\n- trigger-specific evidence refresh\n- parity scorecard link or blocker record\n")
        failures = collect_failures(missing_policy_coupling)
        expected = ["indefinite_c_policy:missing_template_coupling_line"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-policy-coupling failure: {failures}")

        missing_handoff_template = root / "missing_handoff_template"
        _seed(missing_handoff_template)
        _write(missing_handoff_template / HANDOFF_NOTE_PATH, "# Phase 15 Handoff Next Steps Survey\n\n- `zigux/tests/phase15_architecture_council_review_process_build.zig`\n")
        failures = collect_failures(missing_handoff_template)
        expected = ["handoff_note:missing_marker:`Documentation/zigux/phase15-architecture-council-decision-record-template.md`"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-handoff-template failure: {failures}")

    print("PHASE15_ARCHITECTURE_COUNCIL_DECISION_RECORD_TEMPLATE_SELF_TEST=pass")
    print("PHASE15_ARCHITECTURE_COUNCIL_DECISION_RECORD_TEMPLATE_SELF_TEST_CASE_COUNT=5")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description="Verify that the Phase 15 Architecture Council decision-record template stays aligned with the landed governance packet.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("PHASE15_ARCHITECTURE_COUNCIL_DECISION_RECORD_TEMPLATE=pass")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
