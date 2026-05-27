#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SEQUENCING_NOTE_PATH = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")
MANIFEST_PATH = Path("zigux/tests/phase15_governance_lane_sequencing_manifest.json")
FREEZE_GOVERNANCE_PATH = Path("Documentation/zigux/phase15-freeze-map-governance.md")
REVIEW_PROCESS_PATH = Path("Documentation/zigux/phase15-architecture-council-review-process.md")
INDEFINITE_C_POLICY_PATH = Path("Documentation/zigux/phase15-indefinite-c-policy.md")
STUDY_ONLY_PATH = Path("Documentation/zigux/phase15-study-only-anchor-accounting.md")
READINESS_PATH = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
HANDOFF_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
SHARED_GAP_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
DOCS_README_PATH = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
BUILD_PATH = Path("zigux/tests/phase15_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

EXPECTED_LANE_KEY = "arch-council"
EXPECTED_PHASE = "Phase 15"
EXPECTED_ROUTE_GAP_MARKERS = (
    "no dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`",
    "`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route name on current `master`",
)
EXPECTED_REQUIRED_MARKERS = (
    "PHASE15_STATUS=governance_lane_sequencing_packet_landed",
    "PHASE15_LANE_KEY=arch-council",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "`Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-freeze-map-governance.md` own the freeze anchor set",
    "`Documentation/zigux/phase15-deep-core-blocker-survey.md` owns the dedicated roadmap-versus-current-master crosswalk",
    "`Documentation/zigux/phase15-architecture-council-review-process.md` owns the Architecture Council request fields, stay-in-C closeout rule, and reopen-evidence rule",
    "`Documentation/zigux/phase15-indefinite-c-policy.md` owns the stay-in-C policy vocabulary",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, and `zigux/tests/phase15_build.zig` are landed neighboring reminder and replay surfaces",
    "`scripts/zigux/validate-phase15.py` is the current directly readable validator-first maintenance gate",
    "`zigux/tests/phase15_governance_lane_sequencing_manifest.json` and `zigux/tests/phase15_governance_lane_sequencing.zig` keep this sequencing note's direct machine-readable inventory and focused replay explicit",
    "the validator-first replay and the dedicated shared-build replay are directly readable, while the broader Phase 15 make-wrapper and shared-CI routes still remain gap-tracked",
)
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


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    required_paths = (
        SEQUENCING_NOTE_PATH,
        MANIFEST_PATH,
        FREEZE_GOVERNANCE_PATH,
        REVIEW_PROCESS_PATH,
        INDEFINITE_C_POLICY_PATH,
        STUDY_ONLY_PATH,
        READINESS_PATH,
        HANDOFF_PATH,
        SHARED_GAP_PATH,
        DOCS_README_PATH,
        REVIEW_CHECKLIST_PATH,
        SCRIPTS_README_PATH,
        TESTS_README_PATH,
        VALIDATOR_PATH,
        BUILD_PATH,
        MAKEFILE_PATH,
        WORKFLOW_PATH,
    )
    for rel in required_paths:
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
    surveyed_commit = manifest.get("surveyed_commit")
    if surveyed_commit is None:
        failures.append("surveyed_commit:missing")
    elif surveyed_commit not in sequencing_note:
        failures.append("sequencing_note:missing_surveyed_commit")

    if manifest.get("sequencing_note") != SEQUENCING_NOTE_PATH.as_posix():
        failures.append("manifest:sequencing_note_path")
    if manifest.get("readiness_manifest") != "zigux/tests/phase15_readiness_gate_manifest.json":
        failures.append("manifest:readiness_manifest_path")
    if manifest.get("shared_summary_gap_note") != SHARED_GAP_PATH.as_posix():
        failures.append("manifest:shared_summary_gap_path")

    for marker in EXPECTED_REQUIRED_MARKERS:
        if marker not in sequencing_note:
            failures.append(f"sequencing_note:missing_marker:{marker}")

    direct_packet_paths = manifest.get("direct_packet_paths")
    if not isinstance(direct_packet_paths, list) or not direct_packet_paths:
        failures.append("manifest:direct_packet_paths")
    else:
        for rel in direct_packet_paths:
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
            if command not in sequencing_note:
                failures.append(f"sequencing_note:missing_replay_command:{command}")

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
    payload = {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit": "current-master-readback-2026-05-25",
        "sequencing_note": SEQUENCING_NOTE_PATH.as_posix(),
        "readiness_manifest": "zigux/tests/phase15_readiness_gate_manifest.json",
        "shared_summary_gap_note": SHARED_GAP_PATH.as_posix(),
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
            "Documentation/zigux/phase15-indefinite-c-policy.md",
            "Documentation/zigux/phase15-readiness-gate-survey.md",
            "Documentation/zigux/phase15-handoff-next-steps-survey.md",
            "Documentation/zigux/phase15-study-only-anchor-accounting.md",
            "Documentation/zigux/phase15-shared-summary-gap.md",
            "scripts/zigux/README.md",
            "zigux/tests/README.md",
            "scripts/zigux/validate-phase15.py",
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
            "python3 scripts/zigux/check-phase15-review-process-handoff.py",
            "python3 scripts/zigux/check-phase15-handoff-note-alignment.py",
            "python3 scripts/zigux/check-phase15-shared-summary-gap.py",
            "python3 scripts/zigux/validate-phase15.py",
            "zig build test --build-file zigux/tests/phase15_build.zig",
            "zig test zigux/tests/phase15_governance_lane_sequencing.zig",
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def _sample_sequencing_note() -> str:
    return """# Phase 15 Governance Lane Sequencing

## Status

- `PHASE15_STATUS=governance_lane_sequencing_packet_landed`
- `PHASE15_LANE_KEY=arch-council`
- `PHASE15_SLICE=architecture-council-governance-lane-boundaries`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-25`

## Lane inventory

- `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-freeze-map-governance.md` own the freeze anchor set
- `Documentation/zigux/phase15-deep-core-blocker-survey.md` owns the dedicated roadmap-versus-current-master crosswalk
- `Documentation/zigux/phase15-architecture-council-review-process.md` owns the Architecture Council request fields, stay-in-C closeout rule, and reopen-evidence rule
- `Documentation/zigux/phase15-indefinite-c-policy.md` owns the stay-in-C policy vocabulary
- `Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory
- `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, and `zigux/tests/phase15_build.zig` are landed neighboring reminder and replay surfaces
- `scripts/zigux/validate-phase15.py` is the current directly readable validator-first maintenance gate
- `zigux/tests/phase15_governance_lane_sequencing_manifest.json` and `zigux/tests/phase15_governance_lane_sequencing.zig` keep this sequencing note's direct machine-readable inventory and focused replay explicit
- the validator-first replay and the dedicated shared-build replay are directly readable, while the broader Phase 15 make-wrapper and shared-CI routes still remain gap-tracked

## Current repo-reality gaps

- no dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`
- `.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route name on current `master`

## Maintenance-mode handoff

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/freeze-map.md`
- `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-deep-core-blocker-survey.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `zigux/tests/phase15_parity_scorecard.json`
- `zigux/tests/phase15_parity_scorecard.zig`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-readiness-gate-survey.md`
- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- `Documentation/zigux/phase15-shared-summary-gap.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_governance_lane_sequencing_manifest.json`
- `zigux/tests/phase15_governance_lane_sequencing.zig`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`
- `zigux/tests/phase15_handoff_next_steps.zig`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
- `zigux/tests/phase15_build.zig`
- `scripts/zigux/check-phase15-handoff-note-alignment.py`
- `python3 scripts/zigux/check-phase15-docs-readme-alignment.py`
- `python3 scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`
- `python3 scripts/zigux/check-phase15-scripts-readme-alignment.py`
- `python3 scripts/zigux/check-phase15-tests-readme-alignment.py`
- `python3 scripts/zigux/check-phase15-review-process-handoff.py`
- `python3 scripts/zigux/check-phase15-handoff-note-alignment.py`
- `python3 scripts/zigux/check-phase15-shared-summary-gap.py`
- `python3 scripts/zigux/validate-phase15.py`
- `zig build test --build-file zigux/tests/phase15_build.zig`
- `zig test zigux/tests/phase15_governance_lane_sequencing.zig`
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
    for rel in (
        FREEZE_GOVERNANCE_PATH,
        REVIEW_PROCESS_PATH,
        INDEFINITE_C_POLICY_PATH,
        STUDY_ONLY_PATH,
        READINESS_PATH,
        HANDOFF_PATH,
        SHARED_GAP_PATH,
        DOCS_README_PATH,
        REVIEW_CHECKLIST_PATH,
        SCRIPTS_README_PATH,
        TESTS_README_PATH,
        VALIDATOR_PATH,
        BUILD_PATH,
        Path("Documentation/zigux/freeze-map.md"),
        Path("Documentation/zigux/phase15-deep-core-blocker-survey.md"),
        Path("Documentation/zigux/phase15-parity-scorecard.md"),
        Path("zigux/tests/phase15_parity_scorecard.json"),
        Path("zigux/tests/phase15_parity_scorecard.zig"),
        Path("zigux/tests/phase15_governance_lane_sequencing.zig"),
        Path("zigux/tests/phase15_handoff_next_steps_manifest.json"),
        Path("zigux/tests/phase15_handoff_next_steps.zig"),
        Path("zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig"),
        Path("scripts/zigux/check-phase15-review-checklist-study-only-alignment.py"),
        Path("scripts/zigux/check-phase15-handoff-note-alignment.py"),
    ):
        if not (root / rel).exists():
            _write_text(root / rel, _sample_placeholder())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_governance_lane_seq_") as tmp_dir:
        base = Path(tmp_dir)

        baseline = base / "baseline"
        _seed_repo(baseline)
        failures = collect_failures(baseline)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        lane_drift = base / "lane_drift"
        _seed_repo(lane_drift)
        _write_text(
            lane_drift / MANIFEST_PATH,
            _sample_manifest().replace('"lane_key": "arch-council"', '"lane_key": "drifted-lane"', 1),
        )
        failures = collect_failures(lane_drift)
        if failures != ["lane_key:'drifted-lane'"]:
            raise AssertionError(f"unexpected lane drift failures: {failures}")
        case_count += 1

        missing_build_marker = base / "missing_build_marker"
        _seed_repo(missing_build_marker)
        _write_text(
            missing_build_marker / SEQUENCING_NOTE_PATH,
            _sample_sequencing_note().replace(
                "- `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, and `zigux/tests/phase15_build.zig` are landed neighboring reminder and replay surfaces\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_build_marker)
        expected = [
            "sequencing_note:missing_marker:`Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, and `zigux/tests/phase15_build.zig` are landed neighboring reminder and replay surfaces"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected build-marker failures: {failures}")
        case_count += 1

        unexpected_target = base / "unexpected_target"
        _seed_repo(unexpected_target)
        _write_text(unexpected_target / MAKEFILE_PATH, "phase15-validate:\n\t@true\n")
        failures = collect_failures(unexpected_target)
        expected = ["makefile:unexpected_phase15_target:phase15-validate:"]
        if failures != expected:
            raise AssertionError(f"unexpected make target failures: {failures}")
        case_count += 1

        missing_direct_path = base / "missing_direct_path"
        _seed_repo(missing_direct_path)
        (missing_direct_path / BUILD_PATH).unlink()
        failures = collect_failures(missing_direct_path)
        expected = ["missing_required_path:zigux/tests/phase15_build.zig"]
        if failures != expected:
            raise AssertionError(f"unexpected direct-path failures: {failures}")
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
