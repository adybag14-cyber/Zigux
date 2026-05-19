#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

READINESS_NOTE_PATH = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase15_readiness_gate_manifest.json")
SELF_PATH = Path("scripts/zigux/check-phase15-readiness-gate-packet.py")
DOCS_CHECKER_PATH = Path("scripts/zigux/check-phase15-docs-readme-alignment.py")
SCRIPTS_CHECKER_PATH = Path("scripts/zigux/check-phase15-scripts-readme-alignment.py")
TESTS_CHECKER_PATH = Path("scripts/zigux/check-phase15-tests-readme-alignment.py")
REVIEW_PROCESS_CHECKER_PATH = Path("scripts/zigux/check-phase15-review-process-handoff.py")
SHARED_SUMMARY_CHECKER_PATH = Path("scripts/zigux/check-phase15-shared-summary-gap.py")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
HANDOFF_MANIFEST_PATH = Path("zigux/tests/phase15_handoff_next_steps_manifest.json")
BUILD_ZIG_PATH = Path("zigux/tests/phase15_build.zig")
INDEFINITE_C_LANE_OWNER_ALIGNMENT_PATH = Path("zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig")
GOVERNANCE_LANE_MANIFEST_PATH = Path("zigux/tests/phase15_governance_lane_sequencing_manifest.json")
GOVERNANCE_LANE_REPLAY_PATH = Path("zigux/tests/phase15_governance_lane_sequencing.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_NOTE_MARKERS = (
    "PHASE15_STATUS=readiness_gate_survey_landed",
    "PHASE15_LANE_KEY=arch-council",
    "PHASE15_SLICE=governance_packet_readiness_truthfulness",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "the governance packet is materially landed and reviewable",
    "the missing validator, build, and lane-owner companions still block any claim that the broader Phase 15 replay route is fully ready",
    "Although `zigux/Makefile` is present on current `master`, it still does not materialize dedicated `phase15*` wrapper routes",
    "ready for maintenance-mode truthfulness refreshes only",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
)

BLOCKED_ROUTE_MARKERS = {
    "phase15-validate": "`make -C zigux phase15-validate` remains blocked route vocabulary rather than a directly readable shipped replay path",
    "phase15-test": "`make -C zigux phase15-test` remains blocked route vocabulary rather than a directly readable shipped replay path",
    "phase15": "`make -C zigux phase15` remains blocked route vocabulary rather than a directly readable shipped replay path",
}

WORKFLOW_PHASE15_MARKERS = (
    "validate-phase15.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "zigux/tests/phase15_build.zig",
)

EXPECTED_VALIDATE_CHECKERS = [
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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
    note = _read_text(root / READINESS_NOTE_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)
    failures: list[str] = []

    if manifest["surveyed_commit"] not in note:
        failures.append("readiness note is missing the manifest surveyed_commit marker")
    if manifest["readiness_packet_checker"] != str(SELF_PATH):
        failures.append("readiness manifest does not point at the focused readiness-packet checker")
    if f"`{manifest['readiness_packet_checker']}`" not in note:
        failures.append("readiness note is missing the focused readiness-packet checker marker")

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note:
            failures.append(f"readiness note is missing required marker: {marker}")

    for rel in manifest["direct_packet_paths"]:
        if f"`{rel}`" not in note:
            failures.append(f"readiness note is missing direct-packet marker: `{rel}`")
        if not (root / rel).exists():
            failures.append(f"readiness note claims direct packet path is missing from repo: `{rel}`")

    for rel in manifest["still_missing_broader_paths"]:
        if f"`{rel}`" not in note:
            failures.append(f"readiness note is missing blocked broader-path marker: `{rel}`")
        if (root / rel).exists():
            failures.append(f"readiness note still treats materialized broader path as blocked: `{rel}`")

    phase15_validate_target_present = _makefile_has_target(root, "phase15-validate")
    phase15_test_target_present = _makefile_has_target(root, "phase15-test")
    phase15_aggregate_target_present = _makefile_has_target(root, "phase15")
    shared_ci_phase15_present = _workflow_has_phase15_route(root)

    for target, marker in BLOCKED_ROUTE_MARKERS.items():
        target_present = {
            "phase15-validate": phase15_validate_target_present,
            "phase15-test": phase15_test_target_present,
            "phase15": phase15_aggregate_target_present,
        }[target]
        if marker not in note:
            failures.append(f"readiness note is missing blocked route marker: {marker}")
        elif target_present:
            failures.append(
                f"readiness note still treats materialized Phase 15 make route as blocked: `make -C zigux {target}`"
            )

    repo_evidence = manifest["repo_evidence"]
    observed = {
        "phase15_readiness_packet_checker_present": (root / SELF_PATH).exists(),
        "phase15_validator_script_present": (root / VALIDATOR_PATH).exists(),
        "phase15_docs_readme_checker_present": (root / DOCS_CHECKER_PATH).exists(),
        "phase15_tests_readme_checker_present": (root / TESTS_CHECKER_PATH).exists(),
        "phase15_governance_lane_manifest_present": (root / GOVERNANCE_LANE_MANIFEST_PATH).exists(),
        "phase15_governance_lane_replay_present": (root / GOVERNANCE_LANE_REPLAY_PATH).exists(),
        "phase15_handoff_manifest_present": (root / HANDOFF_MANIFEST_PATH).exists(),
        "phase15_build_zig_present": (root / BUILD_ZIG_PATH).exists(),
        "phase15_indefinite_c_lane_owner_alignment_present": (root / INDEFINITE_C_LANE_OWNER_ALIGNMENT_PATH).exists(),
        "phase15_makefile_present": (root / MAKEFILE_PATH).exists(),
        "phase15_validate_target_present": phase15_validate_target_present,
        "phase15_test_target_present": phase15_test_target_present,
        "shared_ci_phase15_present": shared_ci_phase15_present,
    }
    for key, value in observed.items():
        if repo_evidence[key] != value:
            failures.append(f"readiness manifest {key} disagrees with repo reality")

    expected_replay_green = (
        observed["phase15_validator_script_present"]
        and observed["phase15_handoff_manifest_present"]
        and observed["phase15_build_zig_present"]
        and observed["phase15_indefinite_c_lane_owner_alignment_present"]
        and observed["phase15_validate_target_present"]
        and observed["phase15_test_target_present"]
        and observed["shared_ci_phase15_present"]
    )
    if repo_evidence["phase15_replay_green_on_current_master"] != expected_replay_green:
        failures.append("readiness manifest phase15_replay_green_on_current_master disagrees with the broader Phase 15 repo reality")

    if manifest["phase15_validate_checkers"] != EXPECTED_VALIDATE_CHECKERS:
        failures.append("readiness manifest validate-checker list drifted from the current maintenance-only packet")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_note() -> str:
    return """# Phase 15 Readiness Gate Survey

- `PHASE15_STATUS=readiness_gate_survey_landed`
- `PHASE15_LANE_KEY=arch-council`
- `PHASE15_SLICE=governance_packet_readiness_truthfulness`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-18`

This note says the governance packet is materially landed and reviewable, while the missing validator, build, and lane-owner companions still block any claim that the broader Phase 15 replay route is fully ready.

Current directly readable packet:
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-parity-scorecard-survey.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-governance-lane-sequencing.md`
- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- `Documentation/zigux/phase15-shared-summary-gap.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/check-phase15-docs-readme-alignment.py`
- `scripts/zigux/check-phase15-scripts-readme-alignment.py`
- `scripts/zigux/check-phase15-tests-readme-alignment.py`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-shared-summary-gap.py`
- `scripts/zigux/check-phase15-readiness-gate-packet.py`
- `zigux/tests/README.md`
- `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- `zigux/tests/phase15_architecture_council_review_process.zig`
- `zigux/tests/phase15_governance_lane_sequencing_manifest.json`
- `zigux/tests/phase15_governance_lane_sequencing.zig`
- `zigux/tests/phase15_parity_scorecard.json`
- `zigux/tests/phase15_parity_scorecard.zig`
- `zigux/tests/phase15_indefinite_c_policy.json`
- `zigux/tests/phase15_indefinite_c_policy.zig`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`
- `zigux/tests/phase15_handoff_next_steps.zig`
- `zigux/tests/phase15_readiness_gate_manifest.json`

Blocked broader paths:
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`

Although `zigux/Makefile` is present on current `master`, it still does not materialize dedicated `phase15*` wrapper routes, so:
- `make -C zigux phase15-validate` remains blocked route vocabulary rather than a directly readable shipped replay path
- `make -C zigux phase15-test` remains blocked route vocabulary rather than a directly readable shipped replay path
- `make -C zigux phase15` remains blocked route vocabulary rather than a directly readable shipped replay path

This packet is ready for maintenance-mode truthfulness refreshes only, and no Architecture Council approval is currently recorded for a freeze-map status change.
"""


def _sample_manifest() -> str:
    return json.dumps(
        {
            "surveyed_commit_mode": "dated_master_readback",
            "surveyed_commit": "current-master-readback-2026-05-18",
            "readiness_packet_checker": "scripts/zigux/check-phase15-readiness-gate-packet.py",
            "direct_packet_paths": [
                "Documentation/zigux/freeze-map.md",
                "Documentation/zigux/phase15-freeze-map-governance.md",
                "Documentation/zigux/phase15-parity-scorecard.md",
                "Documentation/zigux/phase15-parity-scorecard-survey.md",
                "Documentation/zigux/phase15-architecture-council-review-process.md",
                "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
                "Documentation/zigux/phase15-indefinite-c-policy.md",
                "Documentation/zigux/phase15-governance-lane-sequencing.md",
                "Documentation/zigux/phase15-handoff-next-steps-survey.md",
                "Documentation/zigux/phase15-shared-summary-gap.md",
                "Documentation/zigux/review-checklist.md",
                "scripts/zigux/check-phase15-docs-readme-alignment.py",
                "scripts/zigux/check-phase15-scripts-readme-alignment.py",
                "scripts/zigux/check-phase15-tests-readme-alignment.py",
                "scripts/zigux/check-phase15-review-process-handoff.py",
                "scripts/zigux/check-phase15-shared-summary-gap.py",
                "scripts/zigux/check-phase15-readiness-gate-packet.py",
                "zigux/tests/README.md",
                "zigux/tests/phase15_architecture_council_review_process_manifest.json",
                "zigux/tests/phase15_architecture_council_review_process.zig",
                "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
                "zigux/tests/phase15_governance_lane_sequencing.zig",
                "zigux/tests/phase15_parity_scorecard.json",
                "zigux/tests/phase15_parity_scorecard.zig",
                "zigux/tests/phase15_indefinite_c_policy.json",
                "zigux/tests/phase15_indefinite_c_policy.zig",
                "zigux/tests/phase15_handoff_next_steps_manifest.json",
                "zigux/tests/phase15_handoff_next_steps.zig",
                "zigux/tests/phase15_readiness_gate_manifest.json"
            ],
            "still_missing_broader_paths": [
                "scripts/zigux/validate-phase15.py",
                "zigux/tests/phase15_build.zig",
                "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig"
            ],
            "repo_evidence": {
                "phase15_readiness_packet_checker_present": true,
                "phase15_validator_script_present": false,
                "phase15_docs_readme_checker_present": true,
                "phase15_tests_readme_checker_present": true,
                "phase15_governance_lane_manifest_present": true,
                "phase15_governance_lane_replay_present": true,
                "phase15_handoff_manifest_present": true,
                "phase15_build_zig_present": false,
                "phase15_indefinite_c_lane_owner_alignment_present": false,
                "phase15_makefile_present": true,
                "phase15_validate_target_present": false,
                "phase15_test_target_present": false,
                "shared_ci_phase15_present": false,
                "phase15_replay_green_on_current_master": false
            },
            "phase15_validate_checkers": EXPECTED_VALIDATE_CHECKERS,
        },
        indent=2,
    ) + "\n"


def _seed_repo(root: Path) -> None:
    _write(root / READINESS_NOTE_PATH, _sample_note())
    _write(root / MANIFEST_PATH, _sample_manifest())
    for rel in (
        "Documentation/zigux/freeze-map.md",
        "Documentation/zigux/phase15-freeze-map-governance.md",
        "Documentation/zigux/phase15-parity-scorecard.md",
        "Documentation/zigux/phase15-parity-scorecard-survey.md",
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
        "Documentation/zigux/phase15-indefinite-c-policy.md",
        "Documentation/zigux/phase15-governance-lane-sequencing.md",
        "Documentation/zigux/phase15-handoff-next-steps-survey.md",
        "Documentation/zigux/phase15-shared-summary-gap.md",
        "Documentation/zigux/review-checklist.md",
        "scripts/zigux/check-phase15-docs-readme-alignment.py",
        "scripts/zigux/check-phase15-scripts-readme-alignment.py",
        "scripts/zigux/check-phase15-tests-readme-alignment.py",
        "scripts/zigux/check-phase15-review-process-handoff.py",
        "scripts/zigux/check-phase15-shared-summary-gap.py",
        "scripts/zigux/check-phase15-readiness-gate-packet.py",
        "zigux/tests/README.md",
        "zigux/tests/phase15_architecture_council_review_process_manifest.json",
        "zigux/tests/phase15_architecture_council_review_process.zig",
        "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
        "zigux/tests/phase15_governance_lane_sequencing.zig",
        "zigux/tests/phase15_parity_scorecard.json",
        "zigux/tests/phase15_parity_scorecard.zig",
        "zigux/tests/phase15_indefinite_c_policy.json",
        "zigux/tests/phase15_indefinite_c_policy.zig",
        "zigux/tests/phase15_handoff_next_steps_manifest.json",
        "zigux/tests/phase15_handoff_next_steps.zig",
        "zigux/Makefile",
    ):
        _write(root / rel, "present\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_readiness_gate_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_repo(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_direct_root = root / "missing_direct"
        _seed_repo(missing_direct_root)
        (missing_direct_root / "Documentation/zigux/freeze-map.md").unlink()
        failures = collect_failures(missing_direct_root)
        expected = ["readiness note claims direct packet path is missing from repo: `Documentation/zigux/freeze-map.md`"]
        if failures != expected:
            raise AssertionError(f"unexpected missing direct-path failure: {failures}")

        broader_root = root / "broader"
        _seed_repo(broader_root)
        _write(broader_root / "scripts/zigux/validate-phase15.py", "present\n")
        failures = collect_failures(broader_root)
        expected = [
            "readiness note still treats materialized broader path as blocked: `scripts/zigux/validate-phase15.py`",
            "readiness manifest phase15_validator_script_present disagrees with repo reality",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected broader-path failure: {failures}")

        handoff_root = root / "handoff"
        _seed_repo(handoff_root)
        (handoff_root / HANDOFF_MANIFEST_PATH).unlink()
        failures = collect_failures(handoff_root)
        expected = [
            "readiness note claims direct packet path is missing from repo: `zigux/tests/phase15_handoff_next_steps_manifest.json`",
            "readiness manifest phase15_handoff_manifest_present disagrees with repo reality",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected handoff-manifest failure: {failures}")

    print("PHASE15_READINESS_GATE_PACKET_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 readiness-gate packet still matches the current maintenance-only repo posture."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in synthetic self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 readiness-gate packet check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
