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

NOTE_MARKERS = (
    "## Trigger Conditions",
    "## Required Review Packet",
    "## Decision Buckets",
    "## Reopen Trigger Catalog",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
    "Keep the Phase 15 governance lane in maintenance mode.",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "## Next bounded step",
    "shared-summaries",
    "broader scripts-root or tests-root reminder drift routed through the shared-summary companion lane",
)

POLICY_MARKERS = (
    "required approver set",
    "retained discussion state",
    "named reopen-trigger catalog item",
    "trigger-specific evidence refresh",
    "There is no silent exception path around the indefinite-C policy.",
    "The only allowed exception is an Architecture Council reopen request",
    "the existing blocker remains recorded",
    "narrower_followup_answers_blocker",
    "evidence_packet_stale_or_contradictory",
    "ownership_or_validation_changed",
)

LANE_NOTE_MARKERS = (
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "scripts/zigux/validate-phase15.py",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
)

VALIDATOR_MARKERS = (
    "scripts/zigux/check-phase15-review-process-handoff.py",
)

SCRIPTS_README_MARKERS = (
    "check-phase15-review-process-handoff.py",
)

TESTS_README_PACKET_MARKERS = (
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "without implying any Architecture Council approval for a freeze-map status change",
)

REQUIRED_REVIEW_PACKET_FIELDS = (
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

TRIGGER_CONDITIONS = (
    "freeze-map list change",
    "freeze-map status-bucket change",
    "bounded dual-implementation request for a deep-core study target",
    "contradictory validation needing a written council decision",
)

REOPEN_TRIGGER_CATALOG = (
    "narrower_followup_answers_blocker",
    "evidence_packet_stale_or_contradictory",
    "ownership_or_validation_changed",
)

DECISION_BUCKETS = (
    "keep_in_c",
    "study_only_followup",
    "bounded_dual_implementation",
    "defer_or_reject",
)

HANDOFF_REPLAY_COMMANDS = (
    "make -C zigux phase15-validate",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "make -C zigux phase15",
)

HANDOFF_NEXT_STEP_MARKERS = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "shared-summaries",
    "broader scripts-root or tests-root reminder drift routed through the shared-summary companion lane",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _require_text_markers(text: str, markers: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            issues.append(f"{prefix}:missing:{marker}")


def _require_items(items: list[str], markers: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for marker in markers:
        if marker not in items:
            issues.append(f"{prefix}:missing:{marker}")


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

    _require_text_markers(_read(root / NOTE_PATH), NOTE_MARKERS, "note", issues)
    _require_text_markers(_read(root / POLICY_PATH), POLICY_MARKERS, "policy", issues)
    _require_text_markers(_read(root / LANE_NOTE_PATH), LANE_NOTE_MARKERS, "lane_note", issues)
    _require_text_markers(_read(root / VALIDATOR_PATH), VALIDATOR_MARKERS, "validator", issues)
    _require_text_markers(_read(root / SCRIPTS_README_PATH), SCRIPTS_README_MARKERS, "scripts_readme", issues)
    _require_text_markers(_read(root / TESTS_README_PATH), TESTS_README_PACKET_MARKERS, "tests_readme", issues)

    manifest = json.loads(_read(root / MANIFEST_PATH))
    if manifest.get("current_approval_state") != "no_freeze_map_status_change_approved":
        issues.append("manifest:approval_state_mismatch")

    _require_items(
        manifest.get("required_review_packet_fields", []),
        REQUIRED_REVIEW_PACKET_FIELDS,
        "manifest_required_review_packet_fields",
        issues,
    )
    _require_items(
        manifest.get("trigger_conditions", []),
        TRIGGER_CONDITIONS,
        "manifest_trigger_conditions",
        issues,
    )
    _require_items(
        manifest.get("reopen_trigger_catalog", []),
        REOPEN_TRIGGER_CATALOG,
        "manifest_reopen_trigger_catalog",
        issues,
    )
    _require_items(
        manifest.get("decision_buckets", []),
        DECISION_BUCKETS,
        "manifest_decision_buckets",
        issues,
    )

    handoff = manifest.get("handoff")
    if not isinstance(handoff, dict):
        issues.append("manifest:missing:handoff")
        return issues
    if handoff.get("current_mode") != "maintenance_mode":
        issues.append("manifest:handoff_current_mode_mismatch")
    _require_items(
        handoff.get("replay_commands", []),
        HANDOFF_REPLAY_COMMANDS,
        "manifest_handoff_replay_commands",
        issues,
    )
    next_step = handoff.get("next_step")
    if not isinstance(next_step, str):
        issues.append("manifest:missing:handoff.next_step")
    else:
        _require_text_markers(next_step, HANDOFF_NEXT_STEP_MARKERS, "manifest_handoff_next_step", issues)

    return issues


def _seed_fixture_tree(root: Path) -> None:
    _write(
        root / NOTE_PATH,
        "\n".join(
            (
                "# Phase 15 Architecture Council Review Process Survey",
                "## Trigger Conditions",
                "## Required Review Packet",
                "## Decision Buckets",
                "## Reopen Trigger Catalog",
                "no Architecture Council approval is currently recorded for a freeze-map status change",
                "Keep the Phase 15 governance lane in maintenance mode.",
                "Documentation/zigux/phase15-readiness-gate-survey.md",
                "Documentation/zigux/phase15-handoff-next-steps-survey.md",
                "Documentation/zigux/phase15-governance-lane-sequencing.md",
                "## Next bounded step",
                "shared-summaries",
                "broader scripts-root or tests-root reminder drift routed through the shared-summary companion lane",
            )
        )
        + "\n",
    )
    _write(root / POLICY_PATH, "\n".join(POLICY_MARKERS) + "\n")
    _write(root / LANE_NOTE_PATH, "\n".join(LANE_NOTE_MARKERS) + "\n")
    _write(root / VALIDATOR_PATH, "\n".join(VALIDATOR_MARKERS) + "\n")
    _write(root / SCRIPTS_README_PATH, "\n".join(SCRIPTS_README_MARKERS) + "\n")
    _write(root / TESTS_README_PATH, "\n".join(TESTS_README_PACKET_MARKERS) + "\n")
    _write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "current_approval_state": "no_freeze_map_status_change_approved",
                "required_review_packet_fields": list(REQUIRED_REVIEW_PACKET_FIELDS),
                "trigger_conditions": list(TRIGGER_CONDITIONS),
                "reopen_trigger_catalog": list(REOPEN_TRIGGER_CATALOG),
                "decision_buckets": list(DECISION_BUCKETS),
                "handoff": {
                    "current_mode": "maintenance_mode",
                    "replay_commands": list(HANDOFF_REPLAY_COMMANDS),
                    "next_step": " ".join(HANDOFF_NEXT_STEP_MARKERS),
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
        _assert_only(validate(root), [], "baseline")
        case_count += 1

        note_path = root / NOTE_PATH
        note_text = _read(note_path)
        _write(note_path, note_text.replace("## Decision Buckets\n", "", 1))
        _assert_only(validate(root), ["note:missing:## Decision Buckets"], "missing_note_marker")
        _seed_fixture_tree(root)
        case_count += 1

        tests_readme_path = root / TESTS_README_PATH
        tests_readme_text = _read(tests_readme_path)
        _write(tests_readme_path, tests_readme_text.replace("Documentation/zigux/freeze-map.md\n", "", 1))
        _assert_only(
            validate(root),
            ["tests_readme:missing:Documentation/zigux/freeze-map.md"],
            "missing_tests_freeze_map",
        )
        _seed_fixture_tree(root)
        case_count += 1

        tests_readme_text = _read(root / TESTS_README_PATH)
        _write(
            root / TESTS_README_PATH,
            tests_readme_text.replace("Documentation/zigux/phase15-freeze-map-governance.md\n", "", 1),
        )
        _assert_only(
            validate(root),
            ["tests_readme:missing:Documentation/zigux/phase15-freeze-map-governance.md"],
            "missing_tests_freeze_governance",
        )
        _seed_fixture_tree(root)
        case_count += 1

        tests_readme_text = _read(root / TESTS_README_PATH)
        _write(
            root / TESTS_README_PATH,
            tests_readme_text.replace("Documentation/zigux/phase15-parity-scorecard.md\n", "", 1),
        )
        _assert_only(
            validate(root),
            ["tests_readme:missing:Documentation/zigux/phase15-parity-scorecard.md"],
            "missing_tests_parity_scorecard",
        )
        _seed_fixture_tree(root)
        case_count += 1

        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["required_review_packet_fields"].remove("required approver set")
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["manifest_required_review_packet_fields:missing:required approver set"],
            "missing_manifest_field",
        )
        _seed_fixture_tree(root)
        case_count += 1

        (root / TESTS_README_PATH).unlink()
        _assert_only(
            validate(root),
            [f"missing_file:{TESTS_README_PATH}"],
            "missing_tests_file",
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
        f"{len(NOTE_MARKERS) + len(POLICY_MARKERS) + len(LANE_NOTE_MARKERS) + len(VALIDATOR_MARKERS) + len(SCRIPTS_README_MARKERS) + len(TESTS_README_PACKET_MARKERS) + len(REQUIRED_REVIEW_PACKET_FIELDS) + len(TRIGGER_CONDITIONS) + len(REOPEN_TRIGGER_CATALOG) + len(DECISION_BUCKETS) + len(HANDOFF_REPLAY_COMMANDS) + len(HANDOFF_NEXT_STEP_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
