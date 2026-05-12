#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

NOTE_PATH = "Documentation/zigux/phase15-architecture-council-review-process.md"
POLICY_PATH = "Documentation/zigux/phase15-indefinite-c-policy.md"
MANIFEST_PATH = "zigux/tests/phase15_architecture_council_review_process_manifest.json"
LANE_NOTE_PATH = "Documentation/zigux/phase15-governance-lane-sequencing.md"
VALIDATOR_PATH = "scripts/zigux/validate-phase15.py"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"

REQUIRED_NOTE_MARKERS = (
    "## Trigger Conditions",
    "## Required Review Packet",
    "## Decision Buckets",
    "## Reopen Trigger Catalog",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
    "Keep the Phase 15 governance lane in maintenance mode.",
)

CURRENT_APPROVAL_POSTURE_MARKERS = (
    "the current bounded evidence is the freeze map, this review-process note, the review checklist hook, and `Documentation/zigux/phase15-parity-scorecard.md`",
)

NOTE_REPLAY_ROUTE_MARKERS = (
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "make -C zigux phase15",
)

NOTE_MAINTENANCE_PACKET_MARKERS = (
    "Documentation/zigux/README.md",
    "phase15-docs-readme-maintenance-note-undercount",
    "The review-checklist maintenance packet is already closed",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
)

NOTE_NEXT_STEP_MARKERS = (
    "## Next bounded step",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "broader scripts-root or tests-root reminder drift routed through the shared-summary companion lane",
)

POLICY_FIELD_SYNC_MARKERS = (
    "required approver set",
    "retained discussion state",
    "named reopen-trigger catalog item",
    "trigger-specific evidence refresh",
)

POLICY_EXCEPTION_POSTURE_MARKERS = (
    "There is no silent exception path around the indefinite-C policy.",
    "The only allowed exception is an Architecture Council reopen request",
    "the existing blocker remains recorded",
)

POLICY_REOPEN_TRIGGER_MARKERS = (
    "narrower_followup_answers_blocker",
    "evidence_packet_stale_or_contradictory",
    "ownership_or_validation_changed",
)

REQUIRED_MANIFEST_FIELDS = (
    "linux anchor path",
    "phase",
    "current status bucket",
    "requested decision bucket",
    "decision record ID",
    "owner",
    "required approver set",
    "rollback owner",
    "validation gate summary",
    "evidence archive path",
    "latest blocker disposition",
    "benchmark notes",
    "replay command",
    "rollback threshold",
    "retained discussion state",
    "reopen triggers",
    "parity scorecard link or blocker record",
    "indefinite-C policy link or non-applicability note",
    "explicit non-goals",
    "written rationale",
)

REQUIRED_TRIGGER_CONDITIONS = (
    "freeze-map list change",
    "freeze-map status-bucket change",
    "bounded dual-implementation request for a deep-core study target",
    "contradictory validation needing a written council decision",
)

REQUIRED_REOPEN_TRIGGERS = (
    "narrower_followup_answers_blocker",
    "evidence_packet_stale_or_contradictory",
    "ownership_or_validation_changed",
)

REQUIRED_DECISION_BUCKETS = (
    "keep_in_c",
    "study_only_followup",
    "bounded_dual_implementation",
    "defer_or_reject",
)

HANDOFF_ROUTE_MARKERS = (
    "make -C zigux phase15-validate",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "make -C zigux phase15",
)

CURRENT_REPO_HANDOFF_MARKERS = (
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "scripts/zigux/validate-phase15.py",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
)

NEXT_STEP_DOCS_ROOT_UNDERCOUNT_MARKERS = (
    "## Next bounded step",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "broader scripts-root or tests-root reminder drift routed through the shared-summary companion lane",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _require_markers_present(text: str, markers: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            issue = f"{prefix}:missing:{marker}"
            if issue not in issues:
                issues.append(issue)


def _require_items_present(values: list[str], markers: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for marker in markers:
        if marker not in values:
            issue = f"{prefix}:missing:{marker}"
            if issue not in issues:
                issues.append(issue)


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    required_files = (
        NOTE_PATH,
        POLICY_PATH,
        MANIFEST_PATH,
        LANE_NOTE_PATH,
        VALIDATOR_PATH,
        SCRIPTS_README_PATH,
        TESTS_README_PATH,
    )
    for rel in required_files:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")
    if issues:
        return issues

    note = _read(root / NOTE_PATH)
    policy = _read(root / POLICY_PATH)
    lane_note = _read(root / LANE_NOTE_PATH)
    validator = _read(root / VALIDATOR_PATH)
    scripts_readme = _read(root / SCRIPTS_README_PATH)
    tests_readme = _read(root / TESTS_README_PATH)
    manifest = json.loads(_read(root / MANIFEST_PATH))

    _require_markers_present(note, REQUIRED_NOTE_MARKERS, "note", issues)
    _require_markers_present(note, CURRENT_APPROVAL_POSTURE_MARKERS, "note", issues)
    _require_markers_present(note, NOTE_REPLAY_ROUTE_MARKERS, "note", issues)
    _require_markers_present(note, NOTE_MAINTENANCE_PACKET_MARKERS, "note", issues)
    _require_markers_present(note, NOTE_NEXT_STEP_MARKERS, "note", issues)
    _require_markers_present(policy, POLICY_FIELD_SYNC_MARKERS, "policy", issues)
    _require_markers_present(policy, POLICY_EXCEPTION_POSTURE_MARKERS, "policy", issues)
    _require_markers_present(policy, POLICY_REOPEN_TRIGGER_MARKERS, "policy", issues)
    _require_markers_present(lane_note, CURRENT_REPO_HANDOFF_MARKERS, "lane_note", issues)
    _require_markers_present(validator, ("scripts/zigux/check-phase15-review-process-handoff.py",), "validator", issues)
    _require_markers_present(scripts_readme, ("check-phase15-review-process-handoff.py",), "scripts_readme", issues)
    _require_markers_present(tests_readme, ("scripts/zigux/check-phase15-review-process-handoff.py",), "tests_readme", issues)

    if manifest.get("current_approval_state") != "no_freeze_map_status_change_approved":
        issues.append("manifest:approval_state_mismatch")

    _require_items_present(
        manifest.get("required_review_packet_fields", []),
        REQUIRED_MANIFEST_FIELDS,
        "manifest_required_review_packet_fields",
        issues,
    )
    _require_items_present(
        manifest.get("trigger_conditions", []),
        REQUIRED_TRIGGER_CONDITIONS,
        "manifest_trigger_conditions",
        issues,
    )
    _require_items_present(
        manifest.get("reopen_trigger_catalog", []),
        REQUIRED_REOPEN_TRIGGERS,
        "manifest_reopen_trigger_catalog",
        issues,
    )
    _require_items_present(
        manifest.get("decision_buckets", []),
        REQUIRED_DECISION_BUCKETS,
        "manifest_decision_buckets",
        issues,
    )

    handoff = manifest.get("handoff")
    if not isinstance(handoff, dict):
        issues.append("manifest:missing:handoff")
        return issues

    if handoff.get("current_mode") != "maintenance_mode":
        issues.append("manifest:handoff_current_mode_mismatch")

    replay_commands = handoff.get("replay_commands")
    if not isinstance(replay_commands, list):
        issues.append("manifest:missing:handoff.replay_commands")
    else:
        _require_items_present(replay_commands, HANDOFF_ROUTE_MARKERS, "manifest_handoff_replay_commands", issues)

    next_step = handoff.get("next_step")
    if not isinstance(next_step, str):
        issues.append("manifest:missing:handoff.next_step")
    else:
        _require_markers_present(
            next_step,
            NEXT_STEP_DOCS_ROOT_UNDERCOUNT_MARKERS,
            "manifest_handoff_next_step",
            issues,
        )

    return issues


def _seed_fixture_tree(root: Path) -> None:
    _write(
        root / NOTE_PATH,
        "\n".join(
            (
                "# Phase 15 Architecture Council Review Process Survey",
                "",
                "## Trigger Conditions",
                "## Required Review Packet",
                "## Decision Buckets",
                "## Reopen Trigger Catalog",
                "## Current Approval Posture",
                "- the current bounded evidence is the freeze map, this review-process note, the review checklist hook, and `Documentation/zigux/phase15-parity-scorecard.md`",
                "## Gates",
                "- make -C zigux phase15-validate",
                "- make -C zigux phase15-test",
                "- zig build test --build-file zigux/tests/phase15_build.zig",
                "- make -C zigux phase15",
                "- no Architecture Council approval is currently recorded for a freeze-map status change",
                "- Keep the Phase 15 governance lane in maintenance mode.",
                "- Documentation/zigux/README.md",
                "- phase15-docs-readme-maintenance-note-undercount",
                "- The review-checklist maintenance packet is already closed",
                "- Documentation/zigux/phase15-readiness-gate-survey.md",
                "- Documentation/zigux/phase15-handoff-next-steps-survey.md",
                "- Documentation/zigux/phase15-governance-lane-sequencing.md",
                "## Next bounded step",
                "- Documentation/zigux/README.md keeps the compact Phase 15 reminder.",
                "- Documentation/zigux/phase15-readiness-gate-survey.md, Documentation/zigux/phase15-handoff-next-steps-survey.md, and Documentation/zigux/phase15-governance-lane-sequencing.md remain the parked maintenance-note trio.",
                "- broader scripts-root or tests-root reminder drift routed through the shared-summary companion lane",
                "",
            )
        ),
    )
    _write(
        root / POLICY_PATH,
        "\n".join(
            (
                "# Phase 15 Indefinite-C Policy",
                "",
                "- required approver set",
                "- retained discussion state",
                "- named reopen-trigger catalog item",
                "- trigger-specific evidence refresh",
                "- There is no silent exception path around the indefinite-C policy.",
                "- The only allowed exception is an Architecture Council reopen request",
                "- the existing blocker remains recorded",
                "- narrower_followup_answers_blocker",
                "- evidence_packet_stale_or_contradictory",
                "- ownership_or_validation_changed",
                "",
            )
        ),
    )
    _write(
        root / LANE_NOTE_PATH,
        "\n".join(
            (
                "# Phase 15 Governance Lane Sequencing",
                "- Documentation/zigux/phase15-governance-lane-sequencing.md",
                "- scripts/zigux/validate-phase15.py",
                "- scripts/zigux/README.md",
                "- zigux/tests/README.md",
                "",
            )
        ),
    )
    _write(
        root / VALIDATOR_PATH,
        "scripts/zigux/check-phase15-review-process-handoff.py\n",
    )
    _write(
        root / SCRIPTS_README_PATH,
        "check-phase15-review-process-handoff.py\n",
    )
    _write(
        root / TESTS_README_PATH,
        "scripts/zigux/check-phase15-review-process-handoff.py\n",
    )
    _write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "current_approval_state": "no_freeze_map_status_change_approved",
                "required_review_packet_fields": list(REQUIRED_MANIFEST_FIELDS),
                "trigger_conditions": list(REQUIRED_TRIGGER_CONDITIONS),
                "reopen_trigger_catalog": list(REQUIRED_REOPEN_TRIGGERS),
                "decision_buckets": list(REQUIRED_DECISION_BUCKETS),
                "handoff": {
                    "current_mode": "maintenance_mode",
                    "replay_commands": list(HANDOFF_ROUTE_MARKERS),
                    "next_step": (
                        "## Next bounded step\n"
                        "stay in maintenance mode unless a named reopen trigger or deep-core blocker posture change fires first; "
                        "if one same-lane reviewer-facing truthfulness repair is still needed before then, start with Documentation/zigux/README.md, "
                        "because the compact Phase 15 docs-root reminder there still omits Documentation/zigux/phase15-readiness-gate-survey.md, "
                        "Documentation/zigux/phase15-handoff-next-steps-survey.md, and Documentation/zigux/phase15-governance-lane-sequencing.md, "
                        "while broader scripts-root or tests-root reminder drift routed through the shared-summary companion lane"
                    ),
                },
            },
            indent=2,
        )
        + "\n",
    )


def _assert_only(issues: list[str], expected: list[str], label: str) -> None:
    if issues != expected:
        got = ",".join(issues) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"phase15-review-process-handoff-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_review_process_handoff_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_fixture_tree(root)
        _assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        note_path = root / NOTE_PATH
        note_text = _read(note_path)
        missing_note_marker = "## Decision Buckets"
        _write(root / NOTE_PATH, note_text.replace(missing_note_marker + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"note:missing:{missing_note_marker}"],
            "missing_note_marker_guard_failed",
        )
        _write(root / NOTE_PATH, note_text)
        case_count += 1

        current_approval_marker = "and `Documentation/zigux/phase15-parity-scorecard.md`"
        _write(root / NOTE_PATH, note_text.replace(f" {current_approval_marker}", "", 1))
        _assert_only(
            validate(root),
            [f"note:missing:{CURRENT_APPROVAL_POSTURE_MARKERS[0]}"],
            "missing_current_approval_marker_guard_failed",
        )
        _write(root / NOTE_PATH, note_text)
        case_count += 1

        missing_note_route_marker = "make -C zigux phase15-validate"
        _write(root / NOTE_PATH, note_text.replace(missing_note_route_marker + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"note:missing:{missing_note_route_marker}"],
            "missing_note_route_guard_failed",
        )
        _write(root / NOTE_PATH, note_text)
        case_count += 1

        missing_note_packet_marker = "Documentation/zigux/README.md"
        _write(root / NOTE_PATH, note_text.replace(missing_note_packet_marker, ""))
        _assert_only(
            validate(root),
            [f"note:missing:{missing_note_packet_marker}"],
            "missing_note_packet_marker_guard_failed",
        )
        _write(root / NOTE_PATH, note_text)
        case_count += 1

        missing_note_readiness_marker = "Documentation/zigux/phase15-readiness-gate-survey.md"
        _write(root / NOTE_PATH, note_text.replace(missing_note_readiness_marker, ""))
        _assert_only(
            validate(root),
            [f"note:missing:{missing_note_readiness_marker}"],
            "missing_note_readiness_marker_guard_failed",
        )
        _write(root / NOTE_PATH, note_text)
        case_count += 1

        missing_note_next_step_heading = "## Next bounded step"
        _write(root / NOTE_PATH, note_text.replace(missing_note_next_step_heading + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"note:missing:{missing_note_next_step_heading}"],
            "missing_note_next_step_heading_guard_failed",
        )
        _write(root / NOTE_PATH, note_text)
        case_count += 1

        missing_note_companion_lane_marker = (
            "broader scripts-root or tests-root reminder drift routed through the shared-summary companion lane"
        )
        _write(root / NOTE_PATH, note_text.replace(f"- {missing_note_companion_lane_marker}\n", "", 1))
        _assert_only(
            validate(root),
            [f"note:missing:{missing_note_companion_lane_marker}"],
            "missing_note_companion_lane_marker_guard_failed",
        )
        _write(root / NOTE_PATH, note_text)
        case_count += 1

        policy_path = root / POLICY_PATH
        policy_text = _read(policy_path)
        missing_policy_marker = "required approver set"
        _write(root / POLICY_PATH, policy_text.replace(f"- {missing_policy_marker}\n", "", 1))
        _assert_only(
            validate(root),
            [f"policy:missing:{missing_policy_marker}"],
            "missing_policy_field_guard_failed",
        )
        _write(root / POLICY_PATH, policy_text)
        case_count += 1

        missing_policy_exception_marker = "The only allowed exception is an Architecture Council reopen request"
        _write(root / POLICY_PATH, policy_text.replace(f"- {missing_policy_exception_marker}\n", "", 1))
        _assert_only(
            validate(root),
            [f"policy:missing:{missing_policy_exception_marker}"],
            "missing_policy_exception_guard_failed",
        )
        _write(root / POLICY_PATH, policy_text)
        case_count += 1

        manifest_path = root / MANIFEST_PATH
        manifest_data = json.loads(_read(manifest_path))
        manifest_data["reopen_trigger_catalog"].remove("ownership_or_validation_changed")
        _write(root / MANIFEST_PATH, json.dumps(manifest_data, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["manifest_reopen_trigger_catalog:missing:ownership_or_validation_changed"],
            "missing_reopen_trigger_guard_failed",
        )
        _seed_fixture_tree(root)
        case_count += 1

        manifest_data = json.loads(_read(root / MANIFEST_PATH))
        manifest_data["handoff"]["replay_commands"].remove("make -C zigux phase15-validate")
        _write(root / MANIFEST_PATH, json.dumps(manifest_data, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["manifest_handoff_replay_commands:missing:make -C zigux phase15-validate"],
            "missing_validate_route_guard_failed",
        )
        _seed_fixture_tree(root)
        case_count += 1

        manifest_data = json.loads(_read(root / MANIFEST_PATH))
        manifest_data["handoff"]["next_step"] = manifest_data["handoff"]["next_step"].replace(
            "Documentation/zigux/README.md, ",
            "",
            1,
        )
        _write(root / MANIFEST_PATH, json.dumps(manifest_data, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["manifest_handoff_next_step:missing:Documentation/zigux/README.md"],
            "missing_docs_readme_next_step_guard_failed",
        )
        _seed_fixture_tree(root)
        case_count += 1

        manifest_data = json.loads(_read(root / MANIFEST_PATH))
        manifest_data["handoff"]["next_step"] = manifest_data["handoff"]["next_step"].replace(
            "Documentation/zigux/phase15-readiness-gate-survey.md, ",
            "",
            1,
        )
        _write(root / MANIFEST_PATH, json.dumps(manifest_data, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["manifest_handoff_next_step:missing:Documentation/zigux/phase15-readiness-gate-survey.md"],
            "missing_readiness_next_step_guard_failed",
        )
        _seed_fixture_tree(root)
        case_count += 1

        manifest_data = json.loads(_read(root / MANIFEST_PATH))
        manifest_data["handoff"]["next_step"] = manifest_data["handoff"]["next_step"].replace(
            "Documentation/zigux/phase15-handoff-next-steps-survey.md, and ",
            "",
            1,
        )
        _write(root / MANIFEST_PATH, json.dumps(manifest_data, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["manifest_handoff_next_step:missing:Documentation/zigux/phase15-handoff-next-steps-survey.md"],
            "missing_handoff_next_step_guard_failed",
        )
        _seed_fixture_tree(root)
        case_count += 1

        manifest_data = json.loads(_read(root / MANIFEST_PATH))
        manifest_data["handoff"]["next_step"] = manifest_data["handoff"]["next_step"].replace(
            "Documentation/zigux/phase15-governance-lane-sequencing.md",
            "",
            1,
        )
        _write(root / MANIFEST_PATH, json.dumps(manifest_data, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["manifest_handoff_next_step:missing:Documentation/zigux/phase15-governance-lane-sequencing.md"],
            "missing_lane_note_next_step_guard_failed",
        )
        _seed_fixture_tree(root)
        case_count += 1

        (root / TESTS_README_PATH).unlink()
        _assert_only(
            validate(root),
            [f"missing_file:{TESTS_README_PATH}"],
            "missing_tests_readme_guard_failed",
        )
        case_count += 1

        _seed_fixture_tree(root)
        (root / POLICY_PATH).unlink()
        _assert_only(
            validate(root),
            [f"missing_file:{POLICY_PATH}"],
            "missing_policy_file_guard_failed",
        )
        case_count += 1

    print("PHASE15_REVIEW_PROCESS_HANDOFF_SELF_TEST=pass")
    print(f"PHASE15_REVIEW_PROCESS_HANDOFF_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the dedicated Phase 15 Architecture Council review-process handoff aligned."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        print("PHASE15_REVIEW_PROCESS_HANDOFF=fail")
        print("PHASE15_REVIEW_PROCESS_HANDOFF_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE15_REVIEW_PROCESS_HANDOFF_ISSUES_END")
        return 1

    print("PHASE15_REVIEW_PROCESS_HANDOFF=pass")
    print(
        "PHASE15_REVIEW_PROCESS_HANDOFF_MARKER_COUNT="
        f"{len(REQUIRED_NOTE_MARKERS) + len(CURRENT_APPROVAL_POSTURE_MARKERS) + len(NOTE_REPLAY_ROUTE_MARKERS) + len(NOTE_MAINTENANCE_PACKET_MARKERS) + len(NOTE_NEXT_STEP_MARKERS) + len(POLICY_FIELD_SYNC_MARKERS) + len(POLICY_EXCEPTION_POSTURE_MARKERS) + len(POLICY_REOPEN_TRIGGER_MARKERS) + len(REQUIRED_MANIFEST_FIELDS) + len(REQUIRED_TRIGGER_CONDITIONS) + len(REQUIRED_REOPEN_TRIGGERS) + len(REQUIRED_DECISION_BUCKETS) + len(HANDOFF_ROUTE_MARKERS) + len(CURRENT_REPO_HANDOFF_MARKERS) + len(NEXT_STEP_DOCS_ROOT_UNDERCOUNT_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
