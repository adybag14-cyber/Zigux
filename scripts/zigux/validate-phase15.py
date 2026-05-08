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
    BUILD_PATH,
    MAKEFILE_PATH,
    WORKFLOW_PATH,
)

README_MARKERS = (
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "make -C zigux phase15-validate",
    "make -C zigux phase15",
)

READINESS_NOTE_MARKERS = (
    "PHASE15_LANE_KEY=P15-L01",
    "shared replay surface is green on current `master`",
    CHECKER_ONE,
    CHECKER_TWO,
    "phase15-deep-core-status-change-blocker",
    "make -C zigux phase15-validate",
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
    'b.step("test", "Run Phase 15 governance tests")',
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
    makefile = read_text(root, MAKEFILE_PATH)
    workflow = read_text(root, WORKFLOW_PATH)
    build = read_text(root, BUILD_PATH)

    require_markers(readme, README_MARKERS, "docs_readme", failures)
    require_markers(readiness_note, READINESS_NOTE_MARKERS, "readiness_note", failures)
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
        gap = remaining_gaps[0]
        if gap.get("id") != "phase15-deep-core-status-change-blocker":
            failures.append(f"manifest:remaining_gap_id:{gap.get('id')}")

    next_step = manifest.get("next_step", "")
    for marker in (
        "maintenance mode",
        "shared Phase 15 replay drifts again",
        "two dedicated `phase15-validate` checker routes",
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
    ):
        if marker not in readiness_test:
            failures.append(f"readiness_test:missing:{marker}")

    return failures


def seed_fixture_tree(root: Path) -> None:
    write_text(root / README_PATH, "\n".join(README_MARKERS) + "\n")
    write_text(root / REVIEW_CHECKLIST_PATH, "# fixture\n")
    write_text(root / READINESS_NOTE_PATH, "\n".join(READINESS_NOTE_MARKERS) + "\n")
    write_text(root / READINESS_TEST_PATH, "\n".join((CHECKER_ONE, CHECKER_TWO, "phase15-validate", "phase15_build.zig", "phase15-deep-core-status-change-blocker")) + "\n")
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
                    "phase15_scripts_alignment_checker_present": True,
                    "phase15_review_process_handoff_checker_present": True,
                    "shared_ci_phase15_present": True,
                    "deep_core_status_change_ready": False,
                },
                "remaining_gaps": [
                    {
                        "id": "phase15-deep-core-status-change-blocker",
                    }
                ],
                "next_step": "Keep the Phase 15 governance lane in maintenance mode unless the shared Phase 15 replay drifts again or one of the two dedicated `phase15-validate` checker routes disappears.",
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

        makefile_path = root / MAKEFILE_PATH
        baseline_makefile = read_text(root, MAKEFILE_PATH)
        validator_self_test_marker = f"$(PYTHON) {VALIDATOR_PATH} --self-test"
        validator_run_marker = f"$(PYTHON) {VALIDATOR_PATH}"
        makefile_path.write_text(
            baseline_makefile.replace(validator_self_test_marker, "$(PYTHON) scripts/zigux/validate-phase15-missing.py --self-test", 1).replace(
                validator_run_marker,
                "$(PYTHON) scripts/zigux/validate-phase15-missing.py",
                1,
            ),
            encoding="utf-8",
        )
        assert_only(
            validate(root),
            [
                f"makefile:missing:{validator_self_test_marker}",
                f"makefile:missing:{validator_run_marker}",
            ],
            "missing_makefile_validator",
        )
        makefile_path.write_text(baseline_makefile, encoding="utf-8")
        case_count += 1

        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(read_text(root, MANIFEST_PATH))
        manifest["repo_evidence"]["phase15_validate_target_present"] = False
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert_only(validate(root), ["manifest:repo_evidence:phase15_validate_target_present"], "missing_manifest_validate_target")
        seed_fixture_tree(root)
        case_count += 1

        workflow_path = root / WORKFLOW_PATH
        baseline_workflow = read_text(root, WORKFLOW_PATH)
        workflow_path.write_text(baseline_workflow.replace("run: make -C zigux phase15-validate", "run: make -C zigux phase15-check", 1), encoding="utf-8")
        assert_only(validate(root), ["workflow:missing:run: make -C zigux phase15-validate"], "missing_workflow_validate")
        workflow_path.write_text(baseline_workflow, encoding="utf-8")
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