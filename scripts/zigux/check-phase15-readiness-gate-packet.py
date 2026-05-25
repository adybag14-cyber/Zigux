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
REVIEW_CHECKLIST_CHECKER_PATH = Path("scripts/zigux/check-phase15-review-checklist-study-only-alignment.py")
HANDOFF_NOTE_CHECKER_PATH = Path("scripts/zigux/check-phase15-handoff-note-alignment.py")
SHARED_SUMMARY_CHECKER_PATH = Path("scripts/zigux/check-phase15-shared-summary-gap.py")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
TESTS_README_PATH = Path("zigux/tests/README.md")
REVIEW_PROCESS_MANIFEST_PATH = Path("zigux/tests/phase15_architecture_council_review_process_manifest.json")
REVIEW_PROCESS_REPLAY_PATH = Path("zigux/tests/phase15_architecture_council_review_process.zig")
REVIEW_PROCESS_BUILD_REPLAY_PATH = Path("zigux/tests/phase15_architecture_council_review_process_build.zig")
FREEZE_MAP_REPLAY_PATH = Path("zigux/tests/phase15_freeze_map_governance.zig")
GOVERNANCE_MANIFEST_PATH = Path("zigux/tests/phase15_governance_lane_sequencing_manifest.json")
GOVERNANCE_REPLAY_PATH = Path("zigux/tests/phase15_governance_lane_sequencing.zig")
PARITY_SCORECARD_JSON_PATH = Path("zigux/tests/phase15_parity_scorecard.json")
PARITY_SCORECARD_REPLAY_PATH = Path("zigux/tests/phase15_parity_scorecard.zig")
INDEFINITE_C_POLICY_JSON_PATH = Path("zigux/tests/phase15_indefinite_c_policy.json")
INDEFINITE_C_POLICY_REPLAY_PATH = Path("zigux/tests/phase15_indefinite_c_policy.zig")
HANDOFF_MANIFEST_PATH = Path("zigux/tests/phase15_handoff_next_steps_manifest.json")
HANDOFF_REPLAY_PATH = Path("zigux/tests/phase15_handoff_next_steps.zig")
LANE_OWNER_REPLAY_PATH = Path("zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig")
BUILD_ZIG_PATH = Path("zigux/tests/phase15_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

EXPECTED_LANE_KEY = "P15-L02"
EXPECTED_PHASE = "Phase 15"
EXPECTED_SURVEYED_COMMIT = "current-master-readback-2026-05-23"

EXPECTED_DIRECT_PACKET_PATHS = [
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
    "broader build and workflow companions still block any claim that the larger Phase 15 replay route is fully ready",
    "Although `zigux/Makefile` is present on current `master`, it still does not materialize dedicated `phase15*` wrapper routes",
    "ready for maintenance-mode truthfulness refreshes and direct validator-first replay only",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
)

BLOCKED_ROUTE_MARKERS = {
    "phase15-validate": "`make -C zigux phase15-validate` remains blocked route vocabulary rather than a directly readable shipped replay path",
    "phase15-test": "`make -C zigux phase15-test` remains blocked route vocabulary rather than a directly readable shipped replay path",
    "phase15": "`make -C zigux phase15` remains blocked route vocabulary rather than a directly readable shipped replay path",
}

WORKFLOW_BLOCKED_MARKER = "`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route"
WORKFLOW_PHASE15_MARKERS = (
    "validate-phase15.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "zigux/tests/phase15_build.zig",
)

REQUIRED_PATHS = (
    READINESS_NOTE_PATH,
    MANIFEST_PATH,
    SELF_PATH,
    DOCS_CHECKER_PATH,
    SCRIPTS_CHECKER_PATH,
    TESTS_CHECKER_PATH,
    REVIEW_PROCESS_CHECKER_PATH,
    REVIEW_CHECKLIST_CHECKER_PATH,
    HANDOFF_NOTE_CHECKER_PATH,
    SHARED_SUMMARY_CHECKER_PATH,
    VALIDATOR_PATH,
    TESTS_README_PATH,
    REVIEW_PROCESS_MANIFEST_PATH,
    REVIEW_PROCESS_REPLAY_PATH,
    REVIEW_PROCESS_BUILD_REPLAY_PATH,
    FREEZE_MAP_REPLAY_PATH,
    GOVERNANCE_MANIFEST_PATH,
    GOVERNANCE_REPLAY_PATH,
    PARITY_SCORECARD_JSON_PATH,
    PARITY_SCORECARD_REPLAY_PATH,
    INDEFINITE_C_POLICY_JSON_PATH,
    INDEFINITE_C_POLICY_REPLAY_PATH,
    HANDOFF_MANIFEST_PATH,
    HANDOFF_REPLAY_PATH,
    LANE_OWNER_REPLAY_PATH,
    MAKEFILE_PATH,
    WORKFLOW_PATH,
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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


def _observed_repo_evidence(root: Path) -> dict[str, bool]:
    phase15_validate_target_present = _makefile_has_target(root, "phase15-validate")
    phase15_test_target_present = _makefile_has_target(root, "phase15-test")
    phase15_aggregate_target_present = _makefile_has_target(root, "phase15")
    shared_ci_phase15_present = _workflow_has_phase15_route(root)

    return {
        "phase15_readiness_packet_checker_present": (root / SELF_PATH).exists(),
        "phase15_validator_script_present": (root / VALIDATOR_PATH).exists(),
        "phase15_docs_readme_checker_present": (root / DOCS_CHECKER_PATH).exists(),
        "phase15_scripts_readme_checker_present": (root / SCRIPTS_CHECKER_PATH).exists(),
        "phase15_tests_readme_checker_present": (root / TESTS_CHECKER_PATH).exists(),
        "phase15_review_checklist_study_only_alignment_checker_present": (root / REVIEW_CHECKLIST_CHECKER_PATH).exists(),
        "phase15_handoff_note_checker_present": (root / HANDOFF_NOTE_CHECKER_PATH).exists(),
        "phase15_governance_lane_manifest_present": (root / GOVERNANCE_MANIFEST_PATH).exists(),
        "phase15_governance_lane_replay_present": (root / GOVERNANCE_REPLAY_PATH).exists(),
        "phase15_handoff_manifest_present": (root / HANDOFF_MANIFEST_PATH).exists(),
        "phase15_review_process_build_replay_present": (root / REVIEW_PROCESS_BUILD_REPLAY_PATH).exists(),
        "phase15_build_zig_present": (root / BUILD_ZIG_PATH).exists(),
        "phase15_indefinite_c_lane_owner_alignment_present": (root / LANE_OWNER_REPLAY_PATH).exists(),
        "phase15_makefile_present": (root / MAKEFILE_PATH).exists(),
        "phase15_validate_target_present": phase15_validate_target_present,
        "phase15_test_target_present": phase15_test_target_present,
        "phase15_aggregate_target_present": phase15_aggregate_target_present,
        "shared_ci_phase15_present": shared_ci_phase15_present,
        "phase15_replay_green_on_current_master": False,
    }


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            failures.append(f"missing_required_path:{rel}")
    if failures:
        return failures

    note = _read_text(root / READINESS_NOTE_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append(f"readiness manifest lane key drifted from {EXPECTED_LANE_KEY}: {manifest.get('lane_key', '')}")
    if manifest.get("phase") != EXPECTED_PHASE:
        failures.append(f"readiness manifest phase drifted from {EXPECTED_PHASE}: {manifest.get('phase', '')}")
    if manifest.get("surveyed_commit") != EXPECTED_SURVEYED_COMMIT:
        failures.append(f"readiness manifest surveyed_commit drifted from {EXPECTED_SURVEYED_COMMIT}: {manifest.get('surveyed_commit', '')}")
    if manifest.get("surveyed_commit") not in note:
        failures.append("readiness note is missing the manifest surveyed_commit marker")
    if manifest.get("readiness_packet_checker") != str(SELF_PATH):
        failures.append("readiness manifest does not point at the focused readiness-packet checker")
    if f"`{SELF_PATH}`" not in note:
        failures.append("readiness note is missing the focused readiness-packet checker marker")

    if manifest.get("direct_packet_paths") != EXPECTED_DIRECT_PACKET_PATHS:
        failures.append("readiness manifest direct_packet_paths drifted from the current full readiness packet")
    if manifest.get("still_missing_broader_paths") != EXPECTED_MISSING_BROADER_PATHS:
        failures.append("readiness manifest still_missing_broader_paths drifted from the current blocked broader packet")
    if manifest.get("phase15_validate_checkers") != EXPECTED_PHASE15_VALIDATE_CHECKERS:
        failures.append("readiness manifest phase15_validate_checkers drifted from the current validator support packet")

    repo_evidence = manifest.get("repo_evidence")
    if repo_evidence != EXPECTED_REPO_EVIDENCE:
        failures.append("readiness manifest repo_evidence drifted from the current validator-first readiness posture")

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note:
            failures.append(f"readiness note is missing required marker: {marker}")

    for rel in EXPECTED_DIRECT_PACKET_PATHS:
        marker = f"`{rel}`"
        if marker not in note:
            failures.append(f"readiness note is missing direct-packet marker: {marker}")
        if not (root / rel).exists():
            failures.append(f"missing_direct_packet_path:{rel}")

    for rel in EXPECTED_MISSING_BROADER_PATHS:
        marker = f"`{rel}`"
        if marker not in note:
            failures.append(f"readiness note is missing blocked broader-path marker: {marker}")
        if (root / rel).exists():
            failures.append(f"readiness note still treats materialized broader path as blocked: {marker}")

    observed = _observed_repo_evidence(root)
    for key, expected in EXPECTED_REPO_EVIDENCE.items():
        if observed[key] != expected:
            failures.append(f"observed repo evidence drifted for {key}")

    for target, marker in BLOCKED_ROUTE_MARKERS.items():
        target_present = {
            "phase15-validate": observed["phase15_validate_target_present"],
            "phase15-test": observed["phase15_test_target_present"],
            "phase15": observed["phase15_aggregate_target_present"],
        }[target]
        if marker not in note:
            failures.append(f"readiness note is missing blocked route marker: {marker}")
        elif target_present:
            failures.append(f"readiness note still treats materialized Phase 15 make route as blocked: `make -C zigux {target}`")

    if WORKFLOW_BLOCKED_MARKER not in note:
        failures.append(f"readiness note is missing blocked workflow marker: {WORKFLOW_BLOCKED_MARKER}")
    elif observed["shared_ci_phase15_present"]:
        failures.append("readiness note still treats a materialized Phase 15 workflow route as absent from `.github/workflows/zigux-bootstrap.yml`")

    return failures


def _sample_note() -> str:
    direct_packet_lines = "\n".join(f"- `{path}`" for path in EXPECTED_DIRECT_PACKET_PATHS)
    broader_lines = "\n".join(f"- `{path}`" for path in EXPECTED_MISSING_BROADER_PATHS)
    blocked_route_lines = "\n".join(f"- {marker}" for marker in BLOCKED_ROUTE_MARKERS.values())
    return f"""# Phase 15 Readiness Gate Survey

This note records the current bounded readiness posture for the landed Phase 15 governance packet on `master`.

## Status

- `PHASE15_STATUS=readiness_gate_survey_landed`
- `PHASE15_LANE_KEY=P15-L02`
- `PHASE15_SLICE=validator_first_readiness_packet`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `{EXPECTED_SURVEYED_COMMIT}`

This note says the governance packet is materially landed and reviewable, the dedicated validator now exists as a directly readable maintenance gate, and broader build and workflow companions still block any claim that the larger Phase 15 replay route is fully ready.

## Current directly readable readiness packet

{direct_packet_lines}

## Current repo-reality gaps that still block broader readiness

{broader_lines}

Although `zigux/Makefile` is present on current `master`, it still does not materialize dedicated `phase15*` wrapper routes, so:
{blocked_route_lines}

{WORKFLOW_BLOCKED_MARKER}.

This packet is ready for maintenance-mode truthfulness refreshes and direct validator-first replay only, and no Architecture Council approval is currently recorded for a freeze-map status change.
"""


def _sample_manifest() -> str:
    payload = {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit_mode": "dated_master_readback",
        "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
        "readiness_packet_checker": str(SELF_PATH),
        "direct_packet_paths": EXPECTED_DIRECT_PACKET_PATHS,
        "still_missing_broader_paths": EXPECTED_MISSING_BROADER_PATHS,
        "repo_evidence": EXPECTED_REPO_EVIDENCE,
        "phase15_validate_checkers": EXPECTED_PHASE15_VALIDATE_CHECKERS,
    }
    return json.dumps(payload, indent=2) + "\n"


def _placeholder_for_path(path: str) -> str:
    if path.endswith(".py"):
        return "#!/usr/bin/env python3\n"
    if path.endswith(".json"):
        return "{}\n"
    if path.endswith(".zig"):
        return 'const std = @import("std");\n'
    if path.endswith(".md"):
        return f"# Placeholder for `{path}`\n"
    return "placeholder\n"


def _seed_repo(root: Path) -> None:
    _write(root / READINESS_NOTE_PATH, _sample_note())
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / MAKEFILE_PATH, "phase2-toolchain:\n\t@true\n")
    _write(
        root / WORKFLOW_PATH,
        "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - run: python3 scripts/zigux/check-phase15-readiness-gate-packet.py\n",
    )

    for rel in EXPECTED_DIRECT_PACKET_PATHS:
        path = root / rel
        if path.exists():
            continue
        _write(path, _placeholder_for_path(rel))


def run_self_test() -> int:
    case_count = 6
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_readiness_gate_") as tmp_dir:
        root = Path(tmp_dir) / "baseline"
        _seed_repo(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_direct_root = Path(tmp_dir) / "missing_direct"
        _seed_repo(missing_direct_root)
        (missing_direct_root / DOCS_CHECKER_PATH).unlink()
        failures = collect_failures(missing_direct_root)
        expected = [
            f"missing_required_path:{DOCS_CHECKER_PATH}",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-direct failure: {failures}")

        lane_drift_root = Path(tmp_dir) / "lane_drift"
        _seed_repo(lane_drift_root)
        _write(
            lane_drift_root / MANIFEST_PATH,
            _sample_manifest().replace('"lane_key": "P15-L02"', '"lane_key": "P15-L99"', 1),
        )
        failures = collect_failures(lane_drift_root)
        expected = ["readiness manifest lane key drifted from P15-L02: P15-L99"]
        if failures != expected:
            raise AssertionError(f"unexpected lane-drift failure: {failures}")

        broader_root = Path(tmp_dir) / "broader"
        _seed_repo(broader_root)
        _write(broader_root / BUILD_ZIG_PATH, 'const std = @import("std");\n')
        failures = collect_failures(broader_root)
        expected = [
            "readiness note still treats materialized broader path as blocked: `zigux/tests/phase15_build.zig`",
            "observed repo evidence drifted for phase15_build_zig_present",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected broader-path failure: {failures}")

        route_root = Path(tmp_dir) / "route"
        _seed_repo(route_root)
        _write(route_root / MAKEFILE_PATH, "phase15-validate:\n\t@true\n")
        failures = collect_failures(route_root)
        expected = [
            "observed repo evidence drifted for phase15_validate_target_present",
            "readiness note still treats materialized Phase 15 make route as blocked: `make -C zigux phase15-validate`",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected route failure: {failures}")

        validate_checkers_root = Path(tmp_dir) / "validate_checkers"
        _seed_repo(validate_checkers_root)
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
        expected = ["readiness manifest phase15_validate_checkers drifted from the current validator support packet"]
        if failures != expected:
            raise AssertionError(f"unexpected validate-checkers failure: {failures}")

    print("PHASE15_READINESS_GATE_PACKET_SELF_TEST=pass")
    print(f"PHASE15_READINESS_GATE_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 readiness-gate packet still matches the current full validator-first repo posture."
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
