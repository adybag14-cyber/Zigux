#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

READINESS_NOTE_PATH = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase15_readiness_gate_manifest.json")
GAP_MATRIX_PATH = Path("zigux/tests/phase15_readiness_gap_matrix.json")
CHECKER_PATH = Path("scripts/zigux/check-phase15-readiness-gate-packet.py")
ARCHITECTURE_COUNCIL_CHECKER_PATH = Path("scripts/zigux/check-phase15-architecture-council-packet.py")
DECISION_INDEX_CHECKER_PATH = Path("scripts/zigux/check-phase15-architecture-council-decision-index.py")
SCRIPTS_CHECKER_PATH = Path("scripts/zigux/check-phase15-scripts-readme-alignment.py")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
BUILD_PATH = Path("zigux/tests/phase15_build.zig")
DECISION_INDEX_MANIFEST_PATH = Path("zigux/tests/phase15_architecture_council_decision_index_manifest.json")
DECISION_INDEX_REPLAY_PATH = Path("zigux/tests/phase15_architecture_council_decision_index.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

EXPECTED_LANE_KEY = "P15-L04"
EXPECTED_PHASE = "Phase 15"
EXPECTED_SURVEYED_COMMIT = "current-master-readback-2026-05-27"
EXPECTED_GAP_MATRIX_LANE_KEY = "P15-L01"
EXPECTED_DIRECT_PACKET_PATHS = [
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-parity-scorecard-survey.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-architecture-council-decision-index.md",
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
    "scripts/zigux/check-phase15-architecture-council-packet.py",
    "scripts/zigux/check-phase15-architecture-council-decision-index.py",
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
    "zigux/tests/phase15_architecture_council_decision_index_manifest.json",
    "zigux/tests/phase15_architecture_council_decision_index.zig",
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
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_readiness_gap_matrix.json",
]
EXPECTED_MISSING_BROADER_PATHS = []
EXPECTED_BLOCKED_BROADER_ROUTES = {
    "makefile_path": "zigux/Makefile",
    "missing_make_targets": ["phase15-validate", "phase15-test", "phase15"],
    "workflow_path": ".github/workflows/zigux-bootstrap.yml",
    "missing_workflow_phase15_route": True,
}
EXPECTED_PHASE15_VALIDATE_CHECKERS = [
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "scripts/zigux/check-phase15-architecture-council-packet.py",
    "scripts/zigux/check-phase15-architecture-council-decision-index.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
    "scripts/zigux/check-phase15-handoff-note-alignment.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
    "scripts/zigux/check-phase15-readiness-gate-packet.py",
]
EXPECTED_REPO_EVIDENCE = {
    "phase15_readiness_packet_checker_present": True,
    "phase15_architecture_council_packet_checker_present": True,
    "phase15_architecture_council_decision_index_checker_present": True,
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
    "phase15_decision_index_manifest_present": True,
    "phase15_decision_index_replay_present": True,
    "phase15_build_zig_present": True,
    "phase15_gap_matrix_present": True,
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
    "PHASE15_LANE_KEY=P15-L04",
    "PHASE15_SLICE=validator_first_readiness_packet",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "the governance packet is materially landed and reviewable",
    "the dedicated validator now exists as a directly readable maintenance gate",
    "the dedicated Architecture Council packet checker now exists as a directly readable maintenance gate within the broader validator-first reminder family",
    "the dedicated shared-build companion is now directly readable current-master evidence",
    "the roadmap-versus-ledger gap matrix now keeps the remaining readiness requirements explicit",
    "`scripts/zigux/check-phase15-architecture-council-packet.py`",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_freeze_map_governance.zig`",
    "`zigux/tests/phase15_build.zig`",
    "`zigux/tests/phase15_readiness_gap_matrix.json`",
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


def _placeholder_for(rel: str) -> str:
    if rel.endswith(".py"):
        return "#!/usr/bin/env python3\n"
    if rel.endswith(".json"):
        return "{}\n"
    if rel.endswith(".md"):
        return f"# Placeholder for {rel}\n"
    if rel.endswith(".zig"):
        return 'const std = @import("std");\n\ntest "placeholder" {\n    try std.testing.expect(true);\n}\n'
    return "\n"


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
    for rel in (
        READINESS_NOTE_PATH,
        MANIFEST_PATH,
        GAP_MATRIX_PATH,
        CHECKER_PATH,
        ARCHITECTURE_COUNCIL_CHECKER_PATH,
        DECISION_INDEX_CHECKER_PATH,
        SCRIPTS_CHECKER_PATH,
        VALIDATOR_PATH,
        MAKEFILE_PATH,
        WORKFLOW_PATH,
    ):
        if not (root / rel).exists():
            failures.append(f"missing_required_path:{rel}")
    if failures:
        return failures

    note = _read_text(root / READINESS_NOTE_PATH)
    manifest = json.loads(_read_text(root / MANIFEST_PATH))
    gap_matrix = json.loads(_read_text(root / GAP_MATRIX_PATH))

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append(f"lane_key:{manifest.get('lane_key')!r}")
    if manifest.get("phase") != EXPECTED_PHASE:
        failures.append(f"phase:{manifest.get('phase')!r}")
    if manifest.get("surveyed_commit") != EXPECTED_SURVEYED_COMMIT:
        failures.append(f"surveyed_commit:{manifest.get('surveyed_commit')!r}")
    if manifest.get("readiness_packet_checker") != str(CHECKER_PATH):
        failures.append("readiness_packet_checker")
    if manifest.get("roadmap_ledger_gap_matrix") != str(GAP_MATRIX_PATH):
        failures.append("roadmap_ledger_gap_matrix")
    if manifest.get("direct_packet_paths") != EXPECTED_DIRECT_PACKET_PATHS:
        failures.append("direct_packet_paths")
    if manifest.get("still_missing_broader_paths") != EXPECTED_MISSING_BROADER_PATHS:
        failures.append("still_missing_broader_paths")
    if manifest.get("blocked_broader_routes") != EXPECTED_BLOCKED_BROADER_ROUTES:
        failures.append("blocked_broader_routes")
    if manifest.get("phase15_validate_checkers") != EXPECTED_PHASE15_VALIDATE_CHECKERS:
        failures.append("phase15_validate_checkers")

    repo_evidence = manifest.get("repo_evidence", {})
    for key, expected in EXPECTED_REPO_EVIDENCE.items():
        if repo_evidence.get(key) != expected:
            failures.append(f"repo_evidence:{key}:{repo_evidence.get(key)!r}")

    for rel in EXPECTED_DIRECT_PACKET_PATHS:
        if not (root / rel).exists():
            failures.append(f"missing_direct_packet_path:{rel}")

    if gap_matrix.get("lane_key") != EXPECTED_GAP_MATRIX_LANE_KEY:
        failures.append(f"gap_matrix_lane_key:{gap_matrix.get('lane_key')!r}")
    if gap_matrix.get("phase") != EXPECTED_PHASE:
        failures.append(f"gap_matrix_phase:{gap_matrix.get('phase')!r}")
    if gap_matrix.get("surveyed_commit") != EXPECTED_SURVEYED_COMMIT:
        failures.append(f"gap_matrix_surveyed_commit:{gap_matrix.get('surveyed_commit')!r}")

    for target in EXPECTED_BLOCKED_BROADER_ROUTES["missing_make_targets"]:
        if _makefile_has_target(root, target):
            failures.append(f"unexpected_make_target:{target}")
    if _workflow_has_phase15_route(root) != (
        not EXPECTED_BLOCKED_BROADER_ROUTES["missing_workflow_phase15_route"]
    ):
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
- `PHASE15_LANE_KEY=P15-L04`
- `PHASE15_SLICE=validator_first_readiness_packet`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-27`
- role: keep the current Phase 15 governance packet honest now that the dedicated validator exists as a directly readable maintenance gate, the shared build companion is materialized, the roadmap-versus-ledger gap matrix is materialized, and the broader route and workflow companions still remain blocked on current `master`

This survey keeps those six truths together:
- the governance packet is materially landed and reviewable
- the dedicated validator now exists as a directly readable maintenance gate
- the dedicated Architecture Council packet checker now exists as a directly readable maintenance gate within the broader validator-first reminder family
- the dedicated shared-build companion is now directly readable current-master evidence
- the roadmap-versus-ledger gap matrix now keeps the remaining readiness requirements explicit
- the broader make-wrapper and workflow companions still block any claim that the larger Phase 15 replay route is one-command or shared-CI ready

- `scripts/zigux/check-phase15-architecture-council-packet.py`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_freeze_map_governance.zig`
- `zigux/tests/phase15_build.zig`
- `zigux/tests/phase15_readiness_gap_matrix.json`
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
        "roadmap_ledger_gap_matrix": str(GAP_MATRIX_PATH),
        "direct_packet_paths": EXPECTED_DIRECT_PACKET_PATHS,
        "still_missing_broader_paths": EXPECTED_MISSING_BROADER_PATHS,
        "blocked_broader_routes": EXPECTED_BLOCKED_BROADER_ROUTES,
        "repo_evidence": EXPECTED_REPO_EVIDENCE,
        "phase15_validate_checkers": EXPECTED_PHASE15_VALIDATE_CHECKERS,
    }
    return json.dumps(payload, indent=2) + "\n"


def _sample_gap_matrix() -> str:
    payload = {
        "lane_key": EXPECTED_GAP_MATRIX_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit_mode": "dated_master_readback",
        "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
        "scope": "tranche readiness gate survey remaining readiness gaps vs roadmap and ledger",
        "roadmap_required_features": [
            {"requirement": "freeze map"},
            {"requirement": "Architecture Council review process"},
            {"requirement": "parity scorecard"},
            {"requirement": "policy for code that remains in C indefinitely"},
        ],
        "ledger_anchors": [
            {"anchor": "docs(zigux): add documentation root, review checklist, and freeze map"},
        ],
        "remaining_readiness_gaps": [
            {"gap": "missing_make_routes"},
            {"gap": "missing_workflow_route"},
            {"gap": "no_architecture_council_status_change_approval"},
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def write_fixture_root(root: Path) -> None:
    _write(root / READINESS_NOTE_PATH, _sample_note())
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / GAP_MATRIX_PATH, _sample_gap_matrix())
    _write(root / MAKEFILE_PATH, "phase2-toolchain:\n\t@true\n")
    _write(
        root / WORKFLOW_PATH,
        "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - run: python3 scripts/zigux/check-phase15-readiness-gate-packet.py\n",
    )

    for rel in EXPECTED_DIRECT_PACKET_PATHS:
        if rel in {str(MANIFEST_PATH), str(GAP_MATRIX_PATH)}:
            continue
        _write(root / rel, _placeholder_for(rel))
    for rel in EXPECTED_PHASE15_VALIDATE_CHECKERS:
        _write(root / rel, _placeholder_for(rel))


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
        (build_root / BUILD_PATH).unlink()
        failures = collect_failures(build_root)
        if failures != [f"missing_direct_packet_path:{BUILD_PATH}"]:
            raise AssertionError(f"unexpected build-path failure: {failures}")

        decision_index_checker_root = base / "decision_index_checker"
        write_fixture_root(decision_index_checker_root)
        (decision_index_checker_root / DECISION_INDEX_CHECKER_PATH).unlink()
        failures = collect_failures(decision_index_checker_root)
        if failures != [f"missing_required_path:{DECISION_INDEX_CHECKER_PATH}"]:
            raise AssertionError(
                f"unexpected decision-index-checker failure: {failures}"
            )

        decision_index_manifest_root = base / "decision_index_manifest"
        write_fixture_root(decision_index_manifest_root)
        (decision_index_manifest_root / DECISION_INDEX_MANIFEST_PATH).unlink()
        failures = collect_failures(decision_index_manifest_root)
        if failures != [f"missing_direct_packet_path:{DECISION_INDEX_MANIFEST_PATH}"]:
            raise AssertionError(
                f"unexpected decision-index-manifest failure: {failures}"
            )

        make_root = base / "make"
        write_fixture_root(make_root)
        _write(make_root / MAKEFILE_PATH, "phase15-validate:\n\t@true\n")
        failures = collect_failures(make_root)
        if failures != ["unexpected_make_target:phase15-validate"]:
            raise AssertionError(f"unexpected make-target failure: {failures}")

        workflow_root = base / "workflow"
        write_fixture_root(workflow_root)
        _write(
            workflow_root / WORKFLOW_PATH,
            "jobs:\n  bootstrap:\n    steps:\n      - run: make -C zigux phase15-validate\n",
        )
        failures = collect_failures(workflow_root)
        if failures != ["unexpected_workflow_route"]:
            raise AssertionError(f"unexpected workflow-route failure: {failures}")

        lane_root = base / "lane"
        write_fixture_root(lane_root)
        _write(
            lane_root / GAP_MATRIX_PATH,
            _sample_gap_matrix().replace('"lane_key": "P15-L01"', '"lane_key": "P15-L99"', 1),
        )
        failures = collect_failures(lane_root)
        if failures != ["gap_matrix_lane_key:'P15-L99'"]:
            raise AssertionError(f"unexpected gap-matrix lane failure: {failures}")

    print("PHASE15_VALIDATION_SELF_TEST=pass")
    print("PHASE15_VALIDATION_SELF_TEST_CASES=7")
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
    print(
        "PHASE15_VALIDATION_BLOCKED_ROUTE_COUNT="
        f"{len(EXPECTED_BLOCKED_BROADER_ROUTES['missing_make_targets']) + int(EXPECTED_BLOCKED_BROADER_ROUTES['missing_workflow_phase15_route'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())