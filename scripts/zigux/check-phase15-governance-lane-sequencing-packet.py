#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SEQUENCING_NOTE_PATH = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")
MANIFEST_PATH = Path("zigux/tests/phase15_governance_lane_sequencing_manifest.json")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

EXPECTED_LANE_KEY = "arch-council"
EXPECTED_PHASE = "Phase 15"
EXPECTED_NOTE_PATH = SEQUENCING_NOTE_PATH.as_posix()
EXPECTED_READINESS_MANIFEST = "zigux/tests/phase15_readiness_gate_manifest.json"
EXPECTED_SHARED_GAP_NOTE = "Documentation/zigux/phase15-shared-summary-gap.md"
EXPECTED_ROUTE_GAP_MARKERS = (
    "no dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`",
    "`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route name on current `master`",
)
EXPECTED_NOTE_MARKERS = (
    "PHASE15_STATUS=governance_lane_sequencing_packet_landed",
    "PHASE15_LANE_KEY=arch-council",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "`Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-freeze-map-governance.md` own the freeze anchor set",
    "`Documentation/zigux/phase15-deep-core-blocker-survey.md` owns the dedicated roadmap-versus-current-master crosswalk",
    "`Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-architecture-council-decision-record-template.md` own the Architecture Council request fields, stay-in-C closeout rule, and reopen-evidence rule",
    "`Documentation/zigux/phase15-architecture-council-decision-index.md` owns the explicit current Architecture Council decision inventory",
    "`scripts/zigux/check-phase15-architecture-council-packet.py` keeps the dedicated Architecture Council request packet aligned",
    "`Documentation/zigux/phase15-indefinite-c-policy.md` owns the stay-in-C policy vocabulary",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, and `zigux/tests/phase15_build.zig` are landed neighboring reminder and replay surfaces",
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces",
    "`scripts/zigux/validate-phase15.py` is the current directly readable validator-first maintenance gate",
    "`zigux/tests/phase15_governance_lane_sequencing_manifest.json` and `zigux/tests/phase15_governance_lane_sequencing.zig` keep this sequencing note's direct machine-readable inventory and focused replay explicit",
    "the validator-first replay and the dedicated shared-build replay are directly readable, while the broader Phase 15 make-wrapper and shared-CI routes still remain gap-tracked",
)
EXPECTED_VALIDATE_CHECKERS = (
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "scripts/zigux/check-phase15-architecture-council-packet.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
    "scripts/zigux/check-phase15-handoff-note-alignment.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
    "scripts/zigux/check-phase15-readiness-gate-packet.py",
)
EXPECTED_PRESENT_REPO_EVIDENCE = {
    "phase15_readiness_packet_checker_present": True,
    "phase15_architecture_council_packet_checker_present": True,
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
EXPECTED_BLOCKED_ROUTES = {
    "makefile_path": "zigux/Makefile",
    "missing_make_targets": ["phase15-validate", "phase15-test", "phase15"],
    "workflow_path": ".github/workflows/zigux-bootstrap.yml",
    "missing_workflow_phase15_route": True,
}
WORKFLOW_PHASE15_ROUTE_MARKERS = (
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "Phase 15 validate",
    "Phase 15 test",
    "Run current Phase 15",
)
MAKEFILE_PHASE15_TARGET_MARKERS = (
    "\nphase15-validate:",
    "\nphase15-test:",
    "\nphase15:",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _manifest_payload() -> dict[str, object]:
    return {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit": "current-master-readback-2026-05-27",
        "sequencing_note": EXPECTED_NOTE_PATH,
        "readiness_manifest": EXPECTED_READINESS_MANIFEST,
        "shared_summary_gap_note": EXPECTED_SHARED_GAP_NOTE,
        "direct_packet_paths": [
            "Documentation/zigux/README.md",
            "Documentation/zigux/review-checklist.md",
            "Documentation/zigux/freeze-map.md",
            "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
            "Documentation/zigux/phase15-freeze-map-governance.md",
            "Documentation/zigux/phase15-deep-core-blocker-survey.md",
            "Documentation/zigux/phase15-parity-scorecard.md",
            "zigux/tests/phase15_parity_scorecard.json",
            "zigux/tests/phase15_parity_scorecard.zig",
            "Documentation/zigux/phase15-architecture-council-review-process.md",
            "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
            "Documentation/zigux/phase15-architecture-council-decision-index.md",
            "Documentation/zigux/phase15-indefinite-c-policy.md",
            "Documentation/zigux/phase15-readiness-gate-survey.md",
            "Documentation/zigux/phase15-handoff-next-steps-survey.md",
            "Documentation/zigux/phase15-study-only-anchor-accounting.md",
            "Documentation/zigux/phase15-shared-summary-gap.md",
            "scripts/zigux/README.md",
            "zigux/tests/README.md",
            "scripts/zigux/validate-phase15.py",
            "scripts/zigux/check-phase15-architecture-council-packet.py",
            "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
            "zigux/tests/phase15_governance_lane_sequencing.zig",
            "zigux/tests/phase15_handoff_next_steps_manifest.json",
            "zigux/tests/phase15_handoff_next_steps.zig",
            "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
            "zigux/tests/phase15_build.zig",
            "scripts/zigux/check-phase15-handoff-note-alignment.py",
        ],
        "maintenance_replay_commands": [
            "python3 scripts/zigux/check-phase15-docs-readme-alignment.py",
            "python3 scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
            "python3 scripts/zigux/check-phase15-scripts-readme-alignment.py",
            "python3 scripts/zigux/check-phase15-tests-readme-alignment.py",
            "python3 scripts/zigux/check-phase15-architecture-council-packet.py",
            "python3 scripts/zigux/check-phase15-review-process-handoff.py",
            "python3 scripts/zigux/check-phase15-handoff-note-alignment.py",
            "python3 scripts/zigux/check-phase15-shared-summary-gap.py",
            "python3 scripts/zigux/validate-phase15.py",
            "zig build test --build-file zigux/tests/phase15_build.zig",
            "zig test zigux/tests/phase15_governance_lane_sequencing.zig",
        ],
        "blocked_broader_routes": EXPECTED_BLOCKED_ROUTES,
        "repo_evidence": EXPECTED_PRESENT_REPO_EVIDENCE,
        "phase15_validate_checkers": list(EXPECTED_VALIDATE_CHECKERS),
    }


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in (SEQUENCING_NOTE_PATH, MANIFEST_PATH, MAKEFILE_PATH, WORKFLOW_PATH):
        if not (root / rel).exists():
            failures.append(f"missing_required_path:{rel}")
    if failures:
        return failures

    sequencing_note = _read_text(root / SEQUENCING_NOTE_PATH)
    manifest = json.loads(_read_text(root / MANIFEST_PATH))
    makefile = _read_text(root / MAKEFILE_PATH)
    workflow = _read_text(root / WORKFLOW_PATH)

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append(f"lane_key:{manifest.get('lane_key')!r}")
    if manifest.get("phase") != EXPECTED_PHASE:
        failures.append(f"phase:{manifest.get('phase')!r}")
    if manifest.get("sequencing_note") != EXPECTED_NOTE_PATH:
        failures.append("manifest:sequencing_note_path")
    if manifest.get("readiness_manifest") != EXPECTED_READINESS_MANIFEST:
        failures.append("manifest:readiness_manifest_path")
    if manifest.get("shared_summary_gap_note") != EXPECTED_SHARED_GAP_NOTE:
        failures.append("manifest:shared_summary_gap_path")

    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str):
        failures.append("manifest:surveyed_commit")
    elif surveyed_commit not in sequencing_note:
        failures.append("sequencing_note:missing_surveyed_commit")

    for marker in EXPECTED_NOTE_MARKERS:
        if marker not in sequencing_note:
            failures.append(f"sequencing_note:missing_marker:{marker}")

    direct_packet_paths = manifest.get("direct_packet_paths")
    if not isinstance(direct_packet_paths, list) or not direct_packet_paths:
        failures.append("manifest:direct_packet_paths")
    else:
        for rel in direct_packet_paths:
            if not isinstance(rel, str):
                failures.append(f"manifest:bad_direct_path:{rel!r}")
                continue
            marker = f"`{rel}`"
            if marker not in sequencing_note:
                failures.append(f"sequencing_note:missing_direct_path:{marker}")
            if not (root / rel).exists():
                failures.append(f"repo:missing_direct_path:{rel}")

    maintenance_replay_commands = manifest.get("maintenance_replay_commands")
    if not isinstance(maintenance_replay_commands, list) or not maintenance_replay_commands:
        failures.append("manifest:maintenance_replay_commands")
    else:
        for command in maintenance_replay_commands:
            if not isinstance(command, str):
                failures.append(f"manifest:bad_replay_command:{command!r}")
                continue
            if command not in sequencing_note:
                failures.append(f"sequencing_note:missing_replay_command:{command}")

    blocked_routes = manifest.get("blocked_broader_routes")
    if blocked_routes != EXPECTED_BLOCKED_ROUTES:
        failures.append("manifest:blocked_broader_routes")

    repo_evidence = manifest.get("repo_evidence")
    if repo_evidence != EXPECTED_PRESENT_REPO_EVIDENCE:
        failures.append("manifest:repo_evidence")

    validate_checkers = manifest.get("phase15_validate_checkers")
    if validate_checkers != list(EXPECTED_VALIDATE_CHECKERS):
        failures.append("manifest:phase15_validate_checkers")
    else:
        for rel in validate_checkers:
            if not (root / rel).exists():
                failures.append(f"repo:missing_validate_checker:{rel}")

    for marker in EXPECTED_ROUTE_GAP_MARKERS:
        if marker not in sequencing_note:
            failures.append(f"sequencing_note:missing_route_gap:{marker}")

    for marker in MAKEFILE_PHASE15_TARGET_MARKERS:
        if marker in ("\n" + makefile):
            failures.append(f"makefile:unexpected_phase15_target:{marker.strip()}")

    for marker in WORKFLOW_PHASE15_ROUTE_MARKERS:
        if marker in workflow:
            failures.append(f"workflow:unexpected_phase15_route:{marker}")

    return failures


def _sample_manifest() -> str:
    return json.dumps(_manifest_payload(), indent=2) + "\n"


def _sample_sequencing_note() -> str:
    manifest = _manifest_payload()
    direct_paths = "\n".join(f"- `{path}`" for path in manifest["direct_packet_paths"])
    replay_commands = "\n".join(f"- `{command}`" for command in manifest["maintenance_replay_commands"])
    return f"""# Phase 15 Governance Lane Sequencing

## Status

- `PHASE15_STATUS=governance_lane_sequencing_packet_landed`
- `PHASE15_LANE_KEY=arch-council`
- `PHASE15_SLICE=architecture-council-governance-lane-boundaries`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `{manifest["surveyed_commit"]}`

## Lane inventory

- `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-freeze-map-governance.md` own the freeze anchor set
- `Documentation/zigux/phase15-deep-core-blocker-survey.md` owns the dedicated roadmap-versus-current-master crosswalk
- `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-parity-scorecard-survey.md`, `zigux/tests/phase15_parity_scorecard.json`, and `zigux/tests/phase15_parity_scorecard.zig` own blocked-posture accounting and the machine-readable parity-scorecard companion
- `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-architecture-council-decision-record-template.md` own the Architecture Council request fields, stay-in-C closeout rule, and reopen-evidence rule
- `Documentation/zigux/phase15-architecture-council-decision-index.md` owns the explicit current Architecture Council decision inventory
- `scripts/zigux/check-phase15-architecture-council-packet.py` keeps the dedicated Architecture Council request packet aligned
- `Documentation/zigux/phase15-indefinite-c-policy.md` owns the stay-in-C policy vocabulary
- `Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory
- `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, and `zigux/tests/phase15_build.zig` are landed neighboring reminder and replay surfaces
- `Documentation/zigux/phase15-shared-summary-gap.md` owns the broad reminder-surface drift tracking
- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces
- `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py` keeps the checklist-specific study-only anchor summary boundary aligned
- `scripts/zigux/validate-phase15.py` is the current directly readable validator-first maintenance gate
- `zigux/tests/phase15_governance_lane_sequencing_manifest.json` and `zigux/tests/phase15_governance_lane_sequencing.zig` keep this sequencing note's direct machine-readable inventory and focused replay explicit
- `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, and `scripts/zigux/check-phase15-handoff-note-alignment.py` keep the handoff-specific inventory and focused replay aligned
- the validator-first replay and the dedicated shared-build replay are directly readable, while the broader Phase 15 make-wrapper and shared-CI routes still remain gap-tracked

## Direct Packet Paths

{direct_paths}

## Current repo-reality gaps

- {EXPECTED_ROUTE_GAP_MARKERS[0]}
- {EXPECTED_ROUTE_GAP_MARKERS[1]}

## Maintenance-mode handoff

{replay_commands}
"""


def _sample_placeholder() -> str:
    return "present\n"


def _seed_repo(root: Path) -> None:
    _write_text(root / SEQUENCING_NOTE_PATH, _sample_sequencing_note())
    _write_text(root / MANIFEST_PATH, _sample_manifest())
    _write_text(root / MAKEFILE_PATH, "phase2-validate:\n\t@true\n")
    _write_text(
        root / WORKFLOW_PATH,
        "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - run: python3 scripts/zigux/check-phase15-governance-lane-sequencing-packet.py\n",
    )

    manifest = _manifest_payload()
    for rel in list(manifest["direct_packet_paths"]) + list(manifest["phase15_validate_checkers"]):
        path = root / rel
        if not path.exists():
            _write_text(path, _sample_placeholder())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_governance_lane_seq_packet_") as tmp_dir:
        base = Path(tmp_dir)

        baseline = base / "baseline"
        _seed_repo(baseline)
        failures = collect_failures(baseline)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        lane_drift = base / "lane_drift"
        _seed_repo(lane_drift)
        payload = _manifest_payload()
        payload["lane_key"] = "drifted-lane"
        _write_text(lane_drift / MANIFEST_PATH, json.dumps(payload, indent=2) + "\n")
        failures = collect_failures(lane_drift)
        if failures != ["lane_key:'drifted-lane'"]:
            raise AssertionError(f"unexpected lane drift failures: {failures}")
        case_count += 1

        missing_direct_marker = base / "missing_direct_marker"
        _seed_repo(missing_direct_marker)
        bad_note = _sample_sequencing_note().replace(
            "- `scripts/zigux/check-phase15-architecture-council-packet.py` keeps the dedicated Architecture Council request packet aligned\n",
            "",
            1,
        )
        _write_text(missing_direct_marker / SEQUENCING_NOTE_PATH, bad_note)
        failures = collect_failures(missing_direct_marker)
        expected = [
            "sequencing_note:missing_marker:`scripts/zigux/check-phase15-architecture-council-packet.py` keeps the dedicated Architecture Council request packet aligned",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected direct-marker failures: {failures}")
        case_count += 1

        missing_direct_path = base / "missing_direct_path"
        _seed_repo(missing_direct_path)
        (missing_direct_path / "zigux/tests/phase15_build.zig").unlink()
        failures = collect_failures(missing_direct_path)
        expected = ["repo:missing_direct_path:zigux/tests/phase15_build.zig"]
        if failures != expected:
            raise AssertionError(f"unexpected direct-path failures: {failures}")
        case_count += 1

        unexpected_target = base / "unexpected_target"
        _seed_repo(unexpected_target)
        _write_text(unexpected_target / MAKEFILE_PATH, "phase15-validate:\n\t@true\n")
        failures = collect_failures(unexpected_target)
        expected = ["makefile:unexpected_phase15_target:phase15-validate:"]
        if failures != expected:
            raise AssertionError(f"unexpected make target failures: {failures}")
        case_count += 1

        unexpected_workflow = base / "unexpected_workflow"
        _seed_repo(unexpected_workflow)
        _write_text(
            unexpected_workflow / WORKFLOW_PATH,
            "jobs:\n  bootstrap:\n    steps:\n      - run: make -C zigux phase15-validate\n",
        )
        failures = collect_failures(unexpected_workflow)
        expected = [
            "workflow:unexpected_phase15_route:make -C zigux phase15-validate",
            "workflow:unexpected_phase15_route:make -C zigux phase15",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected workflow failures: {failures}")
        case_count += 1

    print("PHASE15_GOVERNANCE_LANE_SEQUENCING_PACKET_SELF_TEST=pass")
    print(f"PHASE15_GOVERNANCE_LANE_SEQUENCING_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 governance-lane sequencing packet stays aligned with its current direct-readback owner surfaces."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run the synthetic self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 governance-lane sequencing packet check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
