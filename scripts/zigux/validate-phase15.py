#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

READINESS_NOTE_PATH = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase15_readiness_gate_manifest.json")
CHECKER_PATH = Path("scripts/zigux/check-phase15-readiness-gate-packet.py")
SCRIPTS_CHECKER_PATH = Path("scripts/zigux/check-phase15-scripts-readme-alignment.py")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
BUILD_PATH = Path("zigux/tests/phase15_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

EXPECTED_LANE_KEY = "P15-L02"
EXPECTED_PHASE = "Phase 15"
EXPECTED_SURVEYED_COMMIT = "current-master-readback-2026-05-25"
EXPECTED_DIRECT_PACKET_PATHS = [
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-parity-scorecard-survey.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-deep-core-blocker-survey.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-shared-summary-gap.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
    "scripts/zigux/check-phase15-handoff-note-alignment.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
    "scripts/zigux/check-phase15-readiness-gate-packet.py",
    "scripts/zigux/validate-phase15.py",
    "zigux/tests/README.md",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_architecture_council_review_process_build.zig",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_parity_scorecard.json",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
]
EXPECTED_MISSING_BROADER_PATHS = [
    "zigux/tests/phase15_build.zig",
]
EXPECTED_PHASE15_VALIDATE_CHECKERS = [
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
]
EXPECTED_REPO_EVIDENCE = {
    "phase15_readiness_packet_checker_present": True,
    "phase15_validator_script_present": True,
    "phase15_docs_readme_checker_present": True,
    "phase15_scripts_readme_checker_present": True,
    "phase15_tests_readme_checker_present": True,
    "phase15_review_checklist_study_only_alignment_checker_present": True,
    "phase15_handoff_note_checker_present": True,
    "phase15_governance_lane_manifest_present": True,
    "phase15_governance_lane_replay_present": True,
    "phase15_handoff_manifest_present": True,
    "phase15_review_process_build_replay_present": True,
    "phase15_build_zig_present": False,
    "phase15_indefinite_c_lane_owner_alignment_present": True,
    "phase15_makefile_present": True,
    "phase15_validate_target_present": False,
    "phase15_test_target_present": False,
    "phase15_aggregate_target_present": False,
    "shared_ci_phase15_present": False,
    "phase15_replay_green_on_current_master": False,
}
REQUIRED_NOTE_MARKERS = (
    "PHASE15_STATUS=readiness_gate_survey_landed",
    "PHASE15_LANE_KEY=P15-L02",
    "PHASE15_SLICE=validator_first_readiness_packet",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "the governance packet is materially landed and reviewable",
    "the dedicated validator now exists as a directly readable maintenance gate",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_freeze_map_governance.zig`",
    "`zigux/tests/phase15_build.zig`",
    "`make -C zigux phase15-validate` remains blocked route vocabulary",
    "`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
)
WORKFLOW_PHASE15_MARKERS = (
    "validate-phase15.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "zigux/tests/phase15_build.zig",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _makefile_has_target(root: Path, target: str) -> bool:
    path = root / MAKEFILE_PATH
    if not path.exists():
        return False
    return f"\n{target}:" in ("\n" + _read_text(path))


def _workflow_has_phase15_route(root: Path) -> bool:
    path = root / WORKFLOW_PATH
    if not path.exists():
        return False
    workflow = _read_text(path)
    return any(marker in workflow for marker in WORKFLOW_PHASE15_MARKERS)


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in (READINESS_NOTE_PATH, MANIFEST_PATH, CHECKER_PATH, SCRIPTS_CHECKER_PATH, VALIDATOR_PATH, MAKEFILE_PATH, WORKFLOW_PATH):
        if not (root / rel).exists():
            failures.append(f"missing_required_path:{rel}")
    if failures:
        return failures

    note = _read_text(root / READINESS_NOTE_PATH)
    manifest = json.loads(_read_text(root / MANIFEST_PATH))

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append(f"lane_key:{manifest.get('lane_key')!r}")
    if manifest.get("phase") != EXPECTED_PHASE:
        failures.append(f"phase:{manifest.get('phase')!r}")
    if manifest.get("surveyed_commit") != EXPECTED_SURVEYED_COMMIT:
        failures.append(f"surveyed_commit:{manifest.get('surveyed_commit')!r}")
    if manifest.get("readiness_packet_checker") != str(CHECKER_PATH):
        failures.append("readiness_packet_checker")
    if manifest.get("direct_packet_paths") != EXPECTED_DIRECT_PACKET_PATHS:
        failures.append("direct_packet_paths")
    if manifest.get("still_missing_broader_paths") != EXPECTED_MISSING_BROADER_PATHS:
        failures.append("still_missing_broader_paths")
    if manifest.get("phase15_validate_checkers") != EXPECTED_PHASE15_VALIDATE_CHECKERS:
        failures.append("phase15_validate_checkers")

    repo_evidence = manifest.get("repo_evidence", {})
    for key, expected in EXPECTED_REPO_EVIDENCE.items():
        if repo_evidence.get(key) != expected:
            failures.append(f"repo_evidence:{key}:{repo_evidence.get(key)!r}")

    if (root / BUILD_PATH).exists():
        failures.append(f"unexpected_materialized_path:{BUILD_PATH}")
    if _makefile_has_target(root, "phase15-validate"):
        failures.append("unexpected_make_target:phase15-validate")
    if _makefile_has_target(root, "phase15-test"):
        failures.append("unexpected_make_target:phase15-test")
    if _makefile_has_target(root, "phase15"):
        failures.append("unexpected_make_target:phase15")
    if _workflow_has_phase15_route(root):
        failures.append("unexpected_workflow_route")

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note:
            failures.append(f"missing_note_marker:{marker}")
    if EXPECTED_SURVEYED_COMMIT not in note:
        failures.append("surveyed_commit_note_marker")

    return failures


def _sample_note() -> str:
    return """# Phase 15 Readiness Gate Survey

This note records the current bounded readiness posture for the landed Phase 15 governance packet on `master`.

## Status

- `PHASE15_STATUS=readiness_gate_survey_landed`
- `PHASE15_LANE_KEY=P15-L02`
- `PHASE15_SLICE=validator_first_readiness_packet`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-25`
- role: keep the current Phase 15 governance packet honest now that the dedicated validator exists as a directly readable maintenance gate, while the broader build and route companions still remain blocked on current `master`

This survey keeps those two truths together:
- the governance packet is materially landed and reviewable
- the dedicated validator now exists as a directly readable maintenance gate
- the broader build and workflow companions still block any claim that the larger Phase 15 replay route is fully ready

- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_freeze_map_governance.zig`
- `zigux/tests/phase15_build.zig`
- `make -C zigux phase15-validate` remains blocked route vocabulary
- `.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route
- no Architecture Council approval is currently recorded for a freeze-map status change
"""


def _sample_manifest() -> str:
    payload = {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit_mode": "dated_master_readback",
        "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
        "readiness_packet_checker": str(CHECKER_PATH),
        "direct_packet_paths": EXPECTED_DIRECT_PACKET_PATHS,
        "still_missing_broader_paths": EXPECTED_MISSING_BROADER_PATHS,
        "repo_evidence": EXPECTED_REPO_EVIDENCE,
        "phase15_validate_checkers": EXPECTED_PHASE15_VALIDATE_CHECKERS,
    }
    return json.dumps(payload, indent=2) + "\n"


def write_fixture_root(root: Path) -> None:
    _write(root / READINESS_NOTE_PATH, _sample_note())
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / CHECKER_PATH, "#!/usr/bin/env python3\n")
    _write(root / SCRIPTS_CHECKER_PATH, "#!/usr/bin/env python3\n")
    _write(root / VALIDATOR_PATH, "#!/usr/bin/env python3\n")
    _write(root / MAKEFILE_PATH, "phase2-toolchain:\n\t@true\n")
    _write(root / WORKFLOW_PATH, "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - run: python3 scripts/zigux/check-phase15-readiness-gate-packet.py\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_validate_") as tmp_dir:
        base = Path(tmp_dir)

        root = base / "baseline"
        write_fixture_root(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        build_root = base / "build"
        write_fixture_root(build_root)
        _write(build_root / BUILD_PATH, "const std = @import(\"std\");\n")
        failures = collect_failures(build_root)
        if failures != [f"unexpected_materialized_path:{BUILD_PATH}"]:
            raise AssertionError(f"unexpected build-path failure: {failures}")

        make_root = base / "make"
        write_fixture_root(make_root)
        _write(make_root / MAKEFILE_PATH, "phase15-validate:\n\t@true\n")
        failures = collect_failures(make_root)
        if failures != ["unexpected_make_target:phase15-validate"]:
            raise AssertionError(f"unexpected make-target failure: {failures}")

        workflow_root = base / "workflow"
        write_fixture_root(workflow_root)
        _write(workflow_root / WORKFLOW_PATH, "jobs:\n  bootstrap:\n    steps:\n      - run: make -C zigux phase15-validate\n")
        failures = collect_failures(workflow_root)
        if failures != ["unexpected_workflow_route"]:
            raise AssertionError(f"unexpected workflow-route failure: {failures}")

        lane_root = base / "lane"
        write_fixture_root(lane_root)
        _write(lane_root / MANIFEST_PATH, _sample_manifest().replace('"lane_key": "P15-L02"', '"lane_key": "P15-L99"', 1))
        failures = collect_failures(lane_root)
        if failures != ["lane_key:'P15-L99'"]:
            raise AssertionError(f"unexpected lane drift failure: {failures}")

        scripts_root = base / "scripts_checker"
        write_fixture_root(scripts_root)
        (scripts_root / SCRIPTS_CHECKER_PATH).unlink()
        failures = collect_failures(scripts_root)
        if failures != [f"missing_required_path:{SCRIPTS_CHECKER_PATH}"]:
            raise AssertionError(f"unexpected scripts-checker failure: {failures}")

        validate_checkers_root = base / "validate_checkers"
        write_fixture_root(validate_checkers_root)
        _write(
            validate_checkers_root / MANIFEST_PATH,
            _sample_manifest().replace(
                '  "phase15_validate_checkers": [\n'
                '    "scripts/zigux/check-phase15-docs-readme-alignment.py",\n'
                '    "scripts/zigux/check-phase15-scripts-readme-alignment.py",\n'
                '    "scripts/zigux/check-phase15-tests-readme-alignment.py",\n'
                '    "scripts/zigux/check-phase15-review-process-handoff.py",\n'
                '    "scripts/zigux/check-phase15-shared-summary-gap.py"\n'
                "  ]\n",
                '  "phase15_validate_checkers": [\n'
                '    "scripts/zigux/check-phase15-scripts-readme-alignment.py",\n'
                '    "scripts/zigux/check-phase15-tests-readme-alignment.py",\n'
                '    "scripts/zigux/check-phase15-review-process-handoff.py",\n'
                '    "scripts/zigux/check-phase15-shared-summary-gap.py"\n'
                "  ]\n",
                1,
            ),
        )
        failures = collect_failures(validate_checkers_root)
        if failures != ["phase15_validate_checkers"]:
            raise AssertionError(f"unexpected validate-checkers failure: {failures}")

    print("PHASE15_VALIDATION_SELF_TEST=pass")
    print("PHASE15_VALIDATION_SELF_TEST_CASES=6")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 15 readiness packet at the validator-first boundary."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run the synthetic validator self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        print("PHASE15_VALIDATION=fail")
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_VALIDATION=pass")
    print(f"PHASE15_VALIDATION_DIRECT_PATH_COUNT={len(EXPECTED_DIRECT_PACKET_PATHS)}")
    print(f"PHASE15_VALIDATION_BLOCKED_PATH_COUNT={len(EXPECTED_MISSING_BROADER_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
