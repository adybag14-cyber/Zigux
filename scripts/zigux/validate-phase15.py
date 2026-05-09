#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[1] if len(SELF_PATH.parents) > 1 else SELF_PATH.parent

MARKER = "PHASE15_CHECK_PACKET=readiness_gate_validator"
README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
READINESS_NOTE_PATH = "Documentation/zigux/phase15-readiness-gate-survey.md"
MANIFEST_PATH = "zigux/tests/phase15_readiness_gate_manifest.json"
READINESS_TEST_PATH = "zigux/tests/phase15_readiness_gate.zig"
SCORECARD_NOTE_PATH = "Documentation/zigux/phase15-parity-scorecard.md"
SCORECARD_MANIFEST_PATH = "zigux/tests/phase15_parity_scorecard.json"
SCORECARD_TEST_PATH = "zigux/tests/phase15_parity_scorecard.zig"
BUILD_PATH = "zigux/tests/phase15_build.zig"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
CHECKER_ONE = "scripts/zigux/check-phase15-scripts-readme-alignment.py"
CHECKER_TWO = "scripts/zigux/check-phase15-review-process-handoff.py"
VALIDATOR_PATH = "scripts/zigux/validate-phase15.py"

REQUIRED_FILES = (
    README_PATH,
    REVIEW_CHECKLIST_PATH,
    READINESS_NOTE_PATH,
    MANIFEST_PATH,
    READINESS_TEST_PATH,
    SCORECARD_NOTE_PATH,
    SCORECARD_MANIFEST_PATH,
    SCORECARD_TEST_PATH,
    BUILD_PATH,
    MAKEFILE_PATH,
    WORKFLOW_PATH,
)

README_MARKERS = (
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "make -C zigux phase15-validate",
    "make -C zigux phase15",
)

READINESS_NOTE_MARKERS = (
    "PHASE15_LANE_KEY=P15-L01",
    "shared replay surface is still bounded on current `master`",
    CHECKER_ONE,
    CHECKER_TWO,
    ".github/workflows/zigux-bootstrap.yml",
    "phase15-deep-core-status-change-blocker",
    "no narrower shared-summary follow-through remains open on current owner mapping",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "make -C zigux phase15",
)

MAKEFILE_MARKERS = (
    "PHONY += phase15-validate phase15-test phase15",
    "phase15-validate:",
    f"$(PYTHON) {VALIDATOR_PATH} --self-test",
    f"$(PYTHON) {VALIDATOR_PATH}",
    f"$(PYTHON) {CHECKER_ONE} --self-test",
    f"$(PYTHON) {CHECKER_ONE}",
    f"$(PYTHON) {CHECKER_TWO} --self-test",
    f"$(PYTHON) {CHECKER_TWO}",
    "phase15-test:",
    "phase15: phase15-validate phase15-test",
)

WORKFLOW_MARKERS = (
    "- name: Validate Phase 15 governance packet",
    "run: make -C zigux phase15-validate",
    "- name: Run Phase 15 governance tests",
    "run: make -C zigux phase15-test",
)

BUILD_MARKERS = (
    'b.path("phase15_readiness_gate.zig")',
    'b.path("phase15_parity_scorecard.zig")',
    'b.step("test", "Run Phase 15 governance tests")',
)

SCORECARD_NOTE_MARKERS = (
    "`PHASE15_LANE_KEY=P15-L12`",
    "required review-process review-packet fields tracked in the manifest: `20`",
    "required review-process ownership-evidence fields tracked in the manifest: `15`",
    "active freeze-in-C anchor count: `4`",
    "total tracked line count across those anchors: `31,437`",
    "reserved decision-record templates: `4`",
    "blocked status-change anchors: `4`",
    "review-packet fields mirrored from the Architecture Council packet: `20`",
    "ownership-evidence fields mirrored from the Architecture Council packet: `15`",
    "check-phase15-review-process-handoff.py",
    "make -C zigux phase15-validate",
)


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(text: str, markers: tuple[str, ...], label: str, failures: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}:missing:{marker}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    if MARKER not in SELF_PATH.read_text(encoding="utf-8"):
        failures.append("validator_source:missing:packet_marker")

    readme = read_text(root, README_PATH)
    readiness_note = read_text(root, READINESS_NOTE_PATH)
    scorecard_note = read_text(root, SCORECARD_NOTE_PATH)
    makefile = read_text(root, MAKEFILE_PATH)
    workflow = read_text(root, WORKFLOW_PATH)
    build = read_text(root, BUILD_PATH)

    require_markers(readme, README_MARKERS, "docs_readme", failures)
    require_markers(readiness_note, READINESS_NOTE_MARKERS, "readiness_note", failures)
    require_markers(scorecard_note, SCORECARD_NOTE_MARKERS, "scorecard_note", failures)
    require_markers(makefile, MAKEFILE_MARKERS, "makefile", failures)
    require_markers(workflow, WORKFLOW_MARKERS, "workflow", failures)
    require_markers(build, BUILD_MARKERS, "build", failures)

    try:
        manifest = json.loads(read_text(root, MANIFEST_PATH))
    except json.JSONDecodeError as exc:
        failures.append(f"manifest:invalid_json:{exc}")
        return failures

    if manifest.get("lane_key") != "P15-L01":
        failures.append(f"manifest:lane_key:{manifest.get('lane_key')}")
    if manifest.get("phase") != "Phase 15":
        failures.append(f"manifest:phase:{manifest.get('phase')}")

    repo_evidence = manifest.get("repo_evidence")
    if not isinstance(repo_evidence, dict):
        failures.append("manifest:missing:repo_evidence")
    else:
        for key in (
            "freeze_map_present",
            "review_checklist_present",
            "review_process_present",
            "parity_scorecard_present",
            "indefinite_c_policy_present",
            "handoff_next_steps_present",
            "phase15_build_present",
            "phase15_make_target_present",
            "phase15_validate_target_present",
            "phase15_test_target_present",
            "phase15_scripts_alignment_checker_present",
            "phase15_review_process_handoff_checker_present",
            "shared_ci_phase15_present",
        ):
            if repo_evidence.get(key) is not True:
                failures.append(f"manifest:repo_evidence:{key}")
        if repo_evidence.get("deep_core_status_change_ready") is not False:
            failures.append("manifest:repo_evidence:deep_core_status_change_ready")

    remaining_gaps = manifest.get("remaining_gaps")
    if not isinstance(remaining_gaps, list) or len(remaining_gaps) != 1:
        failures.append("manifest:remaining_gaps")
    else:
        saw_status_change_blocker = False
        for gap in remaining_gaps:
            gap_id = gap.get("id")
            if gap_id == "phase15-deep-core-status-change-blocker":
                saw_status_change_blocker = True
                if gap.get("status") != "blocked_on_stay_in_c_evidence":
                    failures.append(f"manifest:remaining_gap_status:{gap.get('status')}")
                if gap.get("zigux_destination") != "Documentation/zigux/phase15-parity-scorecard.md":
                    failures.append(f"manifest:remaining_gap_destination:{gap.get('zigux_destination')}")
            else:
                failures.append(f"manifest:remaining_gap_id:{gap_id}")
        if not saw_status_change_blocker:
            failures.append("manifest:missing:phase15-deep-core-status-change-blocker")

    next_step = manifest.get("next_step", "")
    for marker in (
        "maintenance mode",
        "shared Phase 15 replay drifts again",
        "two dedicated `phase15-validate` checker routes",
        "make -C zigux phase15-test",
        "zigux/tests/phase15_handoff_next_steps_manifest.json",
        "zigux/tests/phase15_readiness_gate_manifest.json",
    ):
        if marker not in next_step:
            failures.append(f"manifest:next_step:missing:{marker}")

    readiness_test = read_text(root, READINESS_TEST_PATH)
    for marker in (
        CHECKER_ONE,
        CHECKER_TWO,
        "phase15-validate",
        "phase15_build.zig",
        "phase15-deep-core-status-change-blocker",
        "zigux/tests/phase15_handoff_next_steps_manifest.json",
        "zigux/tests/phase15_readiness_gate_manifest.json",
    ):
        if marker not in readiness_test:
            failures.append(f"readiness_test:missing:{marker}")

    scorecard_test = read_text(root, SCORECARD_TEST_PATH)
    for marker in (
        "phase15_parity_scorecard.json",
        "phase15-parity-scorecard.md",
        "required review-process review-packet fields tracked in the manifest: `20`",
        "required review-process ownership-evidence fields tracked in the manifest: `15`",
        "phase15-review-process-field-coverage-metrics",
        "phase15-aggregate-scorecard-metrics",
    ):
        if marker not in scorecard_test:
            failures.append(f"scorecard_test:missing:{marker}")

    try:
        scorecard_manifest = json.loads(read_text(root, SCORECARD_MANIFEST_PATH))
    except json.JSONDecodeError as exc:
        failures.append(f"scorecard_manifest:invalid_json:{exc}")
        return failures

    if scorecard_manifest.get("lane_key") != "P15-L12":
        failures.append(f"scorecard_manifest:lane_key:{scorecard_manifest.get('lane_key')}")
    if scorecard_manifest.get("phase") != "Phase 15":
        failures.append(f"scorecard_manifest:phase:{scorecard_manifest.get('phase')}")

    review_process = scorecard_manifest.get("review_process")
    if not isinstance(review_process, dict):
        failures.append("scorecard_manifest:review_process")
    else:
        if review_process.get("required_record_field_count") != 20:
            failures.append("scorecard_manifest:required_record_field_count")
        if len(review_process.get("required_record_fields", [])) != 20:
            failures.append("scorecard_manifest:required_record_fields")
        if review_process.get("ownership_evidence_field_count") != 15:
            failures.append("scorecard_manifest:ownership_evidence_field_count")
        if len(review_process.get("ownership_evidence_fields", [])) != 15:
            failures.append("scorecard_manifest:ownership_evidence_fields")
        if len(review_process.get("reopen_trigger_catalog", [])) != 3:
            failures.append("scorecard_manifest:reopen_trigger_catalog")

    metrics = scorecard_manifest.get("metrics")
    if not isinstance(metrics, dict):
        failures.append("scorecard_manifest:metrics")
    else:
        expected_metrics = {
            "active_freeze_in_c_anchor_count": 4,
            "total_tracked_line_count": 31437,
            "anchors_with_phase14_blocker_evidence": 2,
            "anchors_without_phase14_blocker_evidence": 2,
            "architecture_council_owned_anchor_count": 2,
            "specialist_lane_owned_anchor_count": 2,
            "reserved_decision_record_template_count": 4,
            "blocked_status_change_anchor_count": 4,
            "review_packet_field_count": 20,
            "ownership_evidence_field_count": 15,
        }
        for key, expected_value in expected_metrics.items():
            if metrics.get(key) != expected_value:
                failures.append(f"scorecard_manifest:metrics:{key}")

    anchors = scorecard_manifest.get("anchors")
    if not isinstance(anchors, list) or len(anchors) != 4:
        failures.append("scorecard_manifest:anchors")

    repo_evidence = scorecard_manifest.get("repo_evidence")
    if not isinstance(repo_evidence, dict):
        failures.append("scorecard_manifest:repo_evidence")
    else:
        for key in (
            "freeze_map_present",
            "review_checklist_present",
            "phase15_scorecard_note_present",
            "phase15_scorecard_test_present",
            "phase15_scorecard_manifest_present",
            "phase15_build_present",
            "phase15_make_target_present",
        ):
            if repo_evidence.get(key) is not True:
                failures.append(f"scorecard_manifest:repo_evidence:{key}")

    return failures


def seed_fixture_tree(root: Path) -> None:
    write_text(root / README_PATH, "\n".join(README_MARKERS) + "\n")
    write_text(root / REVIEW_CHECKLIST_PATH, "# fixture\n")
    write_text(root / READINESS_NOTE_PATH, "\n".join(READINESS_NOTE_MARKERS) + "\n")
    write_text(
        root / READINESS_TEST_PATH,
        "\n".join(
            (
                CHECKER_ONE,
                CHECKER_TWO,
                "phase15-validate",
                "phase15_build.zig",
                "phase15-deep-core-status-change-blocker",
                "zigux/tests/phase15_handoff_next_steps_manifest.json",
                "zigux/tests/phase15_readiness_gate_manifest.json",
            )
        )
        + "\n",
    )
    write_text(root / SCORECARD_NOTE_PATH, "\n".join(SCORECARD_NOTE_MARKERS) + "\n")
    write_text(
        root / SCORECARD_TEST_PATH,
        "\n".join(
            (
                "phase15_parity_scorecard.json",
                "phase15-parity-scorecard.md",
                "required review-process review-packet fields tracked in the manifest: `20`",
                "required review-process ownership-evidence fields tracked in the manifest: `15`",
                "phase15-review-process-field-coverage-metrics",
                "phase15-aggregate-scorecard-metrics",
            )
        )
        + "\n",
    )
    write_text(root / BUILD_PATH, "\n".join(BUILD_MARKERS) + "\n")
    write_text(root / MAKEFILE_PATH, "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(root / WORKFLOW_PATH, "\n".join(WORKFLOW_MARKERS) + "\n")
    write_text(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "lane_key": "P15-L01",
                "phase": "Phase 15",
                "repo_evidence": {
                    "freeze_map_present": True,
                    "review_checklist_present": True,
                    "review_process_present": True,
                    "parity_scorecard_present": True,
                    "indefinite_c_policy_present": True,
                    "handoff_next_steps_present": True,
                    "phase15_build_present": True,
                    "phase15_make_target_present": True,
                    "phase15_validate_target_present": True,
                    "phase15_test_target_present": True,
                    "phase15_scripts_alignment_checker_present": True,
                    "phase15_review_process_handoff_checker_present": True,
                    "shared_ci_phase15_present": True,
                    "deep_core_status_change_ready": False,
                },
                "remaining_gaps": [
                    {
                        "id": "phase15-deep-core-status-change-blocker",
                        "status": "blocked_on_stay_in_c_evidence",
                        "zigux_destination": "Documentation/zigux/phase15-parity-scorecard.md",
                    }
                ],
                "next_step": "Keep the Phase 15 governance lane in maintenance mode unless the shared Phase 15 replay drifts again, one of the two dedicated `phase15-validate` checker routes disappears, `make -C zigux phase15-test` disappears, or the explicit `zigux/tests/phase15_handoff_next_steps_manifest.json` plus `zigux/tests/phase15_readiness_gate_manifest.json` pair drops out of the parked readiness packet.",
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / SCORECARD_MANIFEST_PATH,
        json.dumps(
            {
                "lane_key": "P15-L12",
                "phase": "Phase 15",
                "review_process": {
                    "required_record_field_count": 20,
                    "required_record_fields": [f"field-{index}" for index in range(20)],
                    "ownership_evidence_field_count": 15,
                    "ownership_evidence_fields": [f"ownership-{index}" for index in range(15)],
                    "reopen_trigger_catalog": [
                        "narrower_followup_answers_blocker",
                        "evidence_packet_stale_or_contradictory",
                        "ownership_or_validation_changed",
                    ],
                },
                "metrics": {
                    "active_freeze_in_c_anchor_count": 4,
                    "total_tracked_line_count": 31437,
                    "anchors_with_phase14_blocker_evidence": 2,
                    "anchors_without_phase14_blocker_evidence": 2,
                    "architecture_council_owned_anchor_count": 2,
                    "specialist_lane_owned_anchor_count": 2,
                    "reserved_decision_record_template_count": 4,
                    "blocked_status_change_anchor_count": 4,
                    "review_packet_field_count": 20,
                    "ownership_evidence_field_count": 15,
                },
                "anchors": [
                    {"path": "kernel/sched/core.c"},
                    {"path": "mm/page_alloc.c"},
                    {"path": "kernel/rcu/tree.c"},
                    {"path": "net/core/skbuff.c"},
                ],
                "repo_evidence": {
                    "freeze_map_present": True,
                    "review_checklist_present": True,
                    "phase15_scorecard_note_present": True,
                    "phase15_scorecard_test_present": True,
                    "phase15_scorecard_manifest_present": True,
                    "phase15_build_present": True,
                    "phase15_make_target_present": True,
                },
            },
            indent=2,
        )
        + "\n",
    )


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected}, got {actual}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_validate_") as tmp_dir:
        root = Path(tmp_dir)
        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline")
        case_count += 1

        note_path = root / READINESS_NOTE_PATH
        baseline_note = read_text(root, READINESS_NOTE_PATH)
        note_path.write_text(baseline_note.replace(CHECKER_TWO, "scripts/zigux/missing.py", 1), encoding="utf-8")
        assert_only(validate(root), [f"readiness_note:missing:{CHECKER_TWO}"], "missing_note_checker")
        note_path.write_text(baseline_note, encoding="utf-8")
        case_count += 1

        note_path.write_text(
            baseline_note.replace(".github/workflows/zigux-bootstrap.yml", ".github/workflows/phase15-missing.yml", 1),
            encoding="utf-8",
        )
        assert_only(
            validate(root),
            ["readiness_note:missing:.github/workflows/zigux-bootstrap.yml"],
            "missing_note_workflow_anchor",
        )
        note_path.write_text(baseline_note, encoding="utf-8")
        case_count += 1

        note_path.write_text(
            baseline_note.replace("make -C zigux phase15-test", "make -C zigux phase15-check", 1),
            encoding="utf-8",
        )
        assert_only(
            validate(root),
            ["readiness_note:missing:make -C zigux phase15-test"],
            "missing_note_make_test_route",
        )
        note_path.write_text(baseline_note, encoding="utf-8")
        case_count += 1

        makefile_path = root / MAKEFILE_PATH
        baseline_makefile = read_text(root, MAKEFILE_PATH)
        makefile_path.write_text(baseline_makefile.replace(f"$(PYTHON) {CHECKER_TWO} --self-test", "$(PYTHON) scripts/zigux/missing.py --self-test", 1), encoding="utf-8")
        assert_only(validate(root), [f"makefile:missing:$(PYTHON) {CHECKER_TWO} --self-test"], "missing_makefile_checker")
        makefile_path.write_text(baseline_makefile, encoding="utf-8")
        case_count += 1

        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(read_text(root, MANIFEST_PATH))
        manifest["repo_evidence"]["phase15_validate_target_present"] = False
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert_only(validate(root), ["manifest:repo_evidence:phase15_validate_target_present"], "missing_manifest_validate_target")
        seed_fixture_tree(root)
        case_count += 1

        manifest = json.loads(read_text(root, MANIFEST_PATH))
        manifest["repo_evidence"]["phase15_test_target_present"] = False
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert_only(validate(root), ["manifest:repo_evidence:phase15_test_target_present"], "missing_manifest_test_target")
        seed_fixture_tree(root)
        case_count += 1

        manifest = json.loads(read_text(root, MANIFEST_PATH))
        manifest["remaining_gaps"] = []
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert_only(validate(root), ["manifest:remaining_gaps"], "missing_manifest_readiness_gap")
        seed_fixture_tree(root)
        case_count += 1

        workflow_path = root / WORKFLOW_PATH
        baseline_workflow = read_text(root, WORKFLOW_PATH)
        workflow_path.write_text(baseline_workflow.replace("run: make -C zigux phase15-validate", "run: make -C zigux phase15-check", 1), encoding="utf-8")
        assert_only(validate(root), ["workflow:missing:run: make -C zigux phase15-validate"], "missing_workflow_validate")
        workflow_path.write_text(baseline_workflow, encoding="utf-8")
        case_count += 1

        scorecard_note_path = root / SCORECARD_NOTE_PATH
        baseline_scorecard_note = read_text(root, SCORECARD_NOTE_PATH)
        scorecard_note_path.write_text(
            baseline_scorecard_note.replace(
                "required review-process review-packet fields tracked in the manifest: `20`",
                "required review-process review-packet fields tracked in the manifest: `19`",
                1,
            ),
            encoding="utf-8",
        )
        assert_only(
            validate(root),
            ["scorecard_note:missing:required review-process review-packet fields tracked in the manifest: `20`"],
            "missing_scorecard_review_field_marker",
        )
        scorecard_note_path.write_text(baseline_scorecard_note, encoding="utf-8")
        case_count += 1

        scorecard_manifest_path = root / SCORECARD_MANIFEST_PATH
        scorecard_manifest = json.loads(read_text(root, SCORECARD_MANIFEST_PATH))
        scorecard_manifest["metrics"]["review_packet_field_count"] = 19
        write_text(scorecard_manifest_path, json.dumps(scorecard_manifest, indent=2) + "\n")
        assert_only(
            validate(root),
            ["scorecard_manifest:metrics:review_packet_field_count"],
            "mismatched_scorecard_metric",
        )
        seed_fixture_tree(root)
        case_count += 1

        baseline_makefile = read_text(root, MAKEFILE_PATH)
        makefile_path.write_text(
            baseline_makefile.replace(f"$(PYTHON) {VALIDATOR_PATH} --self-test", "$(PYTHON) scripts/zigux/missing-validator.py --self-test", 1),
            encoding="utf-8",
        )
        assert_only(
            validate(root),
            [f"makefile:missing:$(PYTHON) {VALIDATOR_PATH} --self-test"],
            "missing_makefile_validator_selftest",
        )
        makefile_path.write_text(baseline_makefile, encoding="utf-8")
        case_count += 1

        print("PHASE15_VALIDATE_SELF_TEST=pass")
        print(f"PHASE15_VALIDATE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the landed Phase 15 readiness-gate packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run fixture-backed self-test coverage.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE15_VALIDATE=fail")
        print("PHASE15_VALIDATE_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE15_VALIDATE_FAILURES_END")
        return 1

    print("PHASE15_VALIDATE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
