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
CURRENT_READBACK_MARKER = "current-master-readback-2026-05-19"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _marker_to_repo_path(marker: str) -> Path | None:
    if marker.startswith("`") and marker.endswith("`") and "/" in marker:
        return Path(marker.strip("`"))
    return None


def collect_failures(root: Path) -> list[str]:
    review_process = _read_text(root / REVIEW_PROCESS_PATH)
    decision_record_template = _read_text(root / DECISION_RECORD_TEMPLATE_PATH)
    indefinite_c_policy = _read_text(root / INDEFINITE_C_POLICY_PATH)
    review_checklist = _read_text(root / REVIEW_CHECKLIST_PATH)
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)
    shared_gap_note = _read_text(root / SHARED_GAP_NOTE_PATH)
    review_process_test = _read_text(root / TEST_PATH)
    build_gate = _read_text(root / BUILD_GATE_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)

    failures: list[str] = []

    manifest_expectations = (
        ("lane_key", "P15-L08"),
        ("phase", "Phase 15"),
        ("surveyed_commit", CURRENT_READBACK_MARKER),
        ("surveyed_commit_mode", "dated_master_readback"),
        (
            "review_process_note",
            "Documentation/zigux/phase15-architecture-council-review-process.md",
        ),
        (
            "decision_record_template",
            "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
        ),
        ("indefinite_c_policy_note", "Documentation/zigux/phase15-indefinite-c-policy.md"),
        ("handoff_note", "Documentation/zigux/phase15-handoff-next-steps-survey.md"),
        ("shared_summary_gap_note", "Documentation/zigux/phase15-shared-summary-gap.md"),
        ("checker", "scripts/zigux/check-phase15-review-process-handoff.py"),
        ("build_gate", "zigux/tests/phase15_architecture_council_review_process_build.zig"),
    )
    for key, expected in manifest_expectations:
        if manifest.get(key) != expected:
            failures.append(f"review-process manifest field {key} drifted from current packet")

    review_process_markers = (
        "PHASE15_STATUS=architecture_council_review_process_landed",
        "PHASE15_LANE_KEY=P15-L08",
        "PHASE15_PROVENANCE_MODE=dated_master_readback",
        CURRENT_READBACK_MARKER,
        "no Architecture Council approval is currently recorded for a freeze-map status change",
        "`scripts/zigux/check-phase15-review-process-handoff.py`",
        "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
        "`zigux/tests/phase15_architecture_council_review_process.zig`",
        "`zigux/tests/phase15_architecture_council_review_process_build.zig`",
        "broader validator-first shared-summary surfaces remain gap-tracked",
        "focused review-process replay",
        "focused build-file replay",
        "defaults that record to dated-master-readback provenance",
        "the Architecture Council request fields, stay-in-C closeout rule, and reopen-evidence rule explicit",
    )
    for marker in review_process_markers:
        if marker not in review_process:
            failures.append(f"review-process note is missing required marker: {marker}")

    if manifest["decision_record_template"] not in review_process:
        failures.append("review-process note is missing the decision-record template path")
    if manifest["indefinite_c_policy_note"] not in review_process:
        failures.append("review-process note is missing the indefinite-C policy companion path")
    if manifest["review_checklist_boundary_rule"] not in review_process:
        failures.append("review-process note is missing the review-checklist boundary rule")

    for field in manifest["required_review_fields"]:
        if field not in review_process:
            failures.append(f"review-process note is missing required review field: {field}")
        if field not in decision_record_template:
            failures.append(f"decision-record template is missing required review field: {field}")

    checklist_prompt = manifest["review_checklist_entry_prompt"]
    if checklist_prompt not in review_checklist:
        failures.append(
            "review checklist is missing the Phase 15 Architecture Council entry-review prompt"
        )

    for field in manifest["stay_in_c_closeout_fields"]:
        if field not in review_process:
            failures.append(f"review-process note is missing stay-in-C closeout field: {field}")
        if field not in decision_record_template:
            failures.append(f"decision-record template is missing stay-in-C closeout field: {field}")

    for field in manifest["reopen_evidence_fields"]:
        if field not in review_process:
            failures.append(f"review-process note is missing reopen-evidence field: {field}")
        if field not in decision_record_template:
            failures.append(f"decision-record template is missing reopen-evidence field: {field}")

    for marker in manifest["decision_record_template_required_markers"]:
        if marker not in decision_record_template:
            failures.append(f"decision-record template is missing required marker: {marker}")

    for marker in manifest["indefinite_c_policy_required_markers"]:
        if marker not in indefinite_c_policy:
            failures.append(f"indefinite-C policy note is missing required marker: {marker}")

    handoff_markers = (
        "`Documentation/zigux/phase15-architecture-council-review-process.md`",
        "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
        "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
        "`zigux/tests/phase15_architecture_council_review_process_build.zig`",
        "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
        "`scripts/zigux/check-phase15-review-process-handoff.py`",
        "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
        "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
    )
    for marker in handoff_markers:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing required marker: {marker}")

    for marker in manifest["shared_gap_expected_present_paths"]:
        if marker not in shared_gap_note:
            failures.append(f"shared-summary gap note is missing materialized path: {marker}")
        repo_path = _marker_to_repo_path(marker)
        if repo_path is not None and not (root / repo_path).exists():
            failures.append(f"shared-summary gap note claims materialized path is missing from repo: {marker}")

    for marker in manifest["shared_gap_expected_missing_paths"]:
        if marker not in shared_gap_note:
            failures.append(f"shared-summary gap note is missing still-blocked path: {marker}")

    test_markers = (
        "phase 15 review-process note stays aligned with the focused replay packet",
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        "zigux/tests/phase15_architecture_council_review_process_build.zig",
        "scripts/zigux/check-phase15-review-process-handoff.py",
        "current-master-readback-2026-05-19",
    )
    for marker in test_markers:
        if marker not in review_process_test:
            failures.append(f"focused review-process Zig replay is missing required marker: {marker}")

    build_gate_markers = (
        "phase15_architecture_council_review_process.zig",
        "phase15-architecture-council-review-process-tests",
        "Run the focused Phase 15 Architecture Council review-process test",
        "test_step.dependOn",
    )
    for marker in build_gate_markers:
        if marker not in build_gate:
            failures.append(f"focused review-process build gate is missing required marker: {marker}")

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
            "shared_gap_expected_present_paths": [
                "`Documentation/zigux/phase15-parity-scorecard-survey.md`",
                "`Documentation/zigux/phase15-readiness-gate-survey.md`",
                "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
                "`scripts/zigux/check-phase15-scripts-readme-alignment.py`",
                "`scripts/zigux/check-phase15-tests-readme-alignment.py`",
                "`zigux/tests/phase15_freeze_map_governance.zig`",
                "`zigux/tests/phase15_parity_scorecard.zig`",
                "`zigux/tests/phase15_indefinite_c_policy.json`",
                "`zigux/tests/phase15_indefinite_c_policy.zig`",
                "`zigux/tests/phase15_architecture_council_review_process.zig`",
                "`zigux/tests/phase15_architecture_council_review_process_build.zig`",
                "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
                "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
                "`scripts/zigux/check-phase15-review-process-handoff.py`",
                "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
            ],
            "shared_gap_expected_missing_paths": [
                "`scripts/zigux/validate-phase15.py`",
                "`zigux/tests/phase15_build.zig`",
                "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
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
- no Architecture Council approval is currently recorded for a freeze-map status change
- this note keeps the roadmap-required Architecture Council review-process surface honest on current `master`: the docs-root field inventory, the dedicated decision-record template, the dedicated review-process manifest, the focused review-process handoff checker, the focused Zig replay, and the focused build-file replay are landed, while the broader validator-first shared-summary surfaces remain gap-tracked by `Documentation/zigux/phase15-shared-summary-gap.md`

This note exists beside `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_architecture_council_review_process.zig`, and `zigux/tests/phase15_architecture_council_review_process_build.zig`.

`Documentation/zigux/review-checklist.md` keeps the shared entry-review and closeout prompts explicit, but the exact Architecture Council field inventory stays owned by this note and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`

This note keeps the focused review-process replay and focused build-file replay explicit.

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
- the automatic return-to-blocked trigger
- the reopen triggers
- the trigger-specific evidence refresh
- the evidence archive path that will be refreshed before any later reopen request

A later reopen request must not rely on generic intent alone. It must cite:
- the exact reopen trigger being exercised
- refreshed evidence by path
- the blocker disposition being challenged
- the narrower seam or policy change that makes the new review safe to consider

This note keeps the Architecture Council request fields, stay-in-C closeout rule, and reopen-evidence rule explicit.
The dedicated decision-record template defaults that record to dated-master-readback provenance before any exact-head exception is used.
"""


def _sample_decision_record_template() -> str:
    return """# Phase 15 Architecture Council Decision Record Template

- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- `SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`
- exact-head provenance exception note:

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
- the automatic return-to-blocked trigger:
- the reopen triggers:
- the trigger-specific evidence refresh:
- the evidence archive path that will be refreshed before any later reopen request:

- the exact reopen trigger being exercised:
- refreshed evidence by path:
- the blocker disposition being challenged:
- the narrower seam or policy change that makes the new review safe to consider:

- Prefer the dated master readback form for parked governance and stay-in-C review packets.
- Only record an exact head when the linked review needs it to anchor a named published decision.
"""


def _sample_indefinite_c_policy() -> str:
    return """# Phase 15 Indefinite-C Policy

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

- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- `zigux/tests/phase15_architecture_council_review_process_build.zig`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-tests-readme-alignment.py`
- `scripts/zigux/check-phase15-handoff-note-alignment.py`
"""


def _sample_shared_gap_note() -> str:
    return """# Phase 15 Shared Summary Gap

- `Documentation/zigux/phase15-parity-scorecard-survey.md`
- `Documentation/zigux/phase15-readiness-gate-survey.md`
- `Documentation/zigux/phase15-governance-lane-sequencing.md`
- `scripts/zigux/check-phase15-scripts-readme-alignment.py`
- `scripts/zigux/check-phase15-tests-readme-alignment.py`
- `zigux/tests/phase15_freeze_map_governance.zig`
- `zigux/tests/phase15_parity_scorecard.zig`
- `zigux/tests/phase15_indefinite_c_policy.json`
- `zigux/tests/phase15_indefinite_c_policy.zig`
- `zigux/tests/phase15_architecture_council_review_process.zig`
- `zigux/tests/phase15_architecture_council_review_process_build.zig`
- `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-handoff-note-alignment.py`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
"""


def _sample_test_file() -> str:
    return """const std = @import(\"std\");

test \"phase 15 review-process note stays aligned with the focused replay packet\" {
    try std.testing.expectEqualStrings(
        \"Documentation/zigux/phase15-architecture-council-review-process.md\",
        \"Documentation/zigux/phase15-architecture-council-review-process.md\",
    );
    try std.testing.expectEqualStrings(
        \"zigux/tests/phase15_architecture_council_review_process_build.zig\",
        \"zigux/tests/phase15_architecture_council_review_process_build.zig\",
    );
    try std.testing.expectEqualStrings(
        \"scripts/zigux/check-phase15-review-process-handoff.py\",
        \"scripts/zigux/check-phase15-review-process-handoff.py\",
    );
    try std.testing.expectEqualStrings(
        \"current-master-readback-2026-05-19\",
        \"current-master-readback-2026-05-19\",
    );
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
    with tempfile.TemporaryDirectory(prefix="phase15_review_process_note_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(root / DECISION_RECORD_TEMPLATE_PATH, _sample_decision_record_template())
        _write(root / INDEFINITE_C_POLICY_PATH, _sample_indefinite_c_policy())
        _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
        _write(root / HANDOFF_NOTE_PATH, _sample_handoff_note())
        _write(root / SHARED_GAP_NOTE_PATH, _sample_shared_gap_note())
        _write(root / MANIFEST_PATH, _sample_manifest())
        _write(root / TEST_PATH, _sample_test_file())
        _write(root / BUILD_GATE_PATH, _sample_build_gate())
        _write(root / Path("scripts/zigux/check-phase15-review-process-handoff.py"), "# fixture\n")
        _write(root / Path("scripts/zigux/check-phase15-scripts-readme-alignment.py"), "# fixture\n")
        _write(root / Path("scripts/zigux/check-phase15-tests-readme-alignment.py"), "# fixture\n")
        _write(root / Path("scripts/zigux/check-phase15-handoff-note-alignment.py"), "# fixture\n")
        _write(root / Path("Documentation/zigux/phase15-parity-scorecard-survey.md"), "# fixture\n")
        _write(root / Path("Documentation/zigux/phase15-readiness-gate-survey.md"), "# fixture\n")
        _write(root / Path("Documentation/zigux/phase15-governance-lane-sequencing.md"), "# fixture\n")
        _write(root / Path("zigux/tests/phase15_freeze_map_governance.zig"), "// fixture\n")
        _write(root / Path("zigux/tests/phase15_parity_scorecard.zig"), "// fixture\n")
        _write(root / Path("zigux/tests/phase15_indefinite_c_policy.json"), "{}\n")
        _write(root / Path("zigux/tests/phase15_indefinite_c_policy.zig"), "// fixture\n")
        _write(root / Path("zigux/tests/phase15_handoff_next_steps_manifest.json"), "{}\n")

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        _write(
            root / REVIEW_PROCESS_PATH,
            _sample_review_process().replace(
                "- no Architecture Council approval is currently recorded for a freeze-map status change\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "review-process note is missing required marker: no Architecture Council approval is currently recorded for a freeze-map status change"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected no-approval failure: {failures}")

        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(
            root / REVIEW_PROCESS_PATH,
            _sample_review_process().replace("`zigux/tests/phase15_architecture_council_review_process_build.zig`", "", 1),
        )
        failures = collect_failures(root)
        expected = [
            "review-process note is missing required marker: `zigux/tests/phase15_architecture_council_review_process_build.zig`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected build-gate marker failure: {failures}")

        _write(root / REVIEW_PROCESS_PATH, _sample_review_process())
        _write(
            root / SHARED_GAP_NOTE_PATH,
            _sample_shared_gap_note().replace("- `zigux/tests/phase15_build.zig`\n", "", 1),
        )
        failures = collect_failures(root)
        expected = [
            "shared-summary gap note is missing still-blocked path: `zigux/tests/phase15_build.zig`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected shared-gap failure: {failures}")

    print("PHASE15_ARCHITECTURE_COUNCIL_REVIEW_PROCESS_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 15 Architecture Council review-process note packet for drift."
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

    print("Phase 15 Architecture Council review-process check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
