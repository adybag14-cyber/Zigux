#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

READINESS_NOTE_PATH = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase15_readiness_gate_manifest.json")
SELF_PATH = Path("scripts/zigux/check-phase15-readiness-gate-packet.py")
SCRIPTS_CHECKER_PATH = Path("scripts/zigux/check-phase15-scripts-readme-alignment.py")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
BUILD_ZIG_PATH = Path("zigux/tests/phase15_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
EXPECTED_LANE_KEY = "P15-L02"
EXPECTED_PHASE = "Phase 15"

REQUIRED_NOTE_MARKERS = (
    "PHASE15_STATUS=readiness_gate_survey_landed",
    "PHASE15_LANE_KEY=P15-L02",
    "PHASE15_SLICE=validator_first_readiness_packet",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "the governance packet is materially landed and reviewable",
    "the dedicated validator now exists as a directly readable maintenance gate",
    "the dedicated shared-build companion is now directly readable current-master evidence",
    "broader make-wrapper and workflow companions still block any claim that the larger Phase 15 replay route is one-command or shared-CI ready",
    "Although `zigux/Makefile` is present on current `master`, it still does not materialize dedicated `phase15*` wrapper routes",
    "ready for maintenance-mode truthfulness refreshes, direct validator-first replay, and shared-build companion review only",
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


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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
        SELF_PATH,
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
    manifest = _read_manifest(root / MANIFEST_PATH)

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append(f"readiness manifest lane key drifted from {EXPECTED_LANE_KEY}: {manifest.get('lane_key', '')}")
    if manifest.get("phase") != EXPECTED_PHASE:
        failures.append(f"readiness manifest phase drifted from {EXPECTED_PHASE}: {manifest.get('phase', '')}")
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
        marker = f"`{rel}`"
        if marker not in note:
            failures.append(f"readiness note is missing direct-packet marker: {marker}")
        if not (root / rel).exists():
            failures.append(f"direct_packet_path_missing:{rel}")

    for rel in manifest["still_missing_broader_paths"]:
        marker = f"`{rel}`"
        if marker not in note:
            failures.append(f"readiness note is missing blocked broader-path marker: {marker}")
        if (root / rel).exists():
            failures.append(f"readiness note still treats materialized broader path as blocked: {marker}")

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
            failures.append(f"readiness note still treats materialized Phase 15 make route as blocked: `make -C zigux {target}`")

    if WORKFLOW_BLOCKED_MARKER not in note:
        failures.append(f"readiness note is missing blocked workflow marker: {WORKFLOW_BLOCKED_MARKER}")
    elif shared_ci_phase15_present:
        failures.append("readiness note still treats a materialized Phase 15 workflow route as absent from `.github/workflows/zigux-bootstrap.yml`")

    repo_evidence = manifest["repo_evidence"]
    observed = {
        "phase15_readiness_packet_checker_present": (root / SELF_PATH).exists(),
        "phase15_validator_script_present": (root / VALIDATOR_PATH).exists(),
        "phase15_docs_readme_checker_present": (root / Path("scripts/zigux/check-phase15-docs-readme-alignment.py")).exists(),
        "phase15_scripts_readme_checker_present": (root / SCRIPTS_CHECKER_PATH).exists(),
        "phase15_tests_readme_checker_present": (root / Path("scripts/zigux/check-phase15-tests-readme-alignment.py")).exists(),
        "phase15_review_checklist_study_only_alignment_checker_present": (root / Path("scripts/zigux/check-phase15-review-checklist-study-only-alignment.py")).exists(),
        "phase15_handoff_note_checker_present": (root / Path("scripts/zigux/check-phase15-handoff-note-alignment.py")).exists(),
        "phase15_governance_lane_manifest_present": (root / Path("zigux/tests/phase15_governance_lane_sequencing_manifest.json")).exists(),
        "phase15_governance_lane_replay_present": (root / Path("zigux/tests/phase15_governance_lane_sequencing.zig")).exists(),
        "phase15_handoff_manifest_present": (root / Path("zigux/tests/phase15_handoff_next_steps_manifest.json")).exists(),
        "phase15_review_process_build_replay_present": (root / Path("zigux/tests/phase15_architecture_council_review_process_build.zig")).exists(),
        "phase15_build_zig_present": (root / BUILD_ZIG_PATH).exists(),
        "phase15_indefinite_c_lane_owner_alignment_present": (root / Path("zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig")).exists(),
        "phase15_makefile_present": (root / MAKEFILE_PATH).exists(),
        "phase15_validate_target_present": phase15_validate_target_present,
        "phase15_test_target_present": phase15_test_target_present,
        "phase15_aggregate_target_present": phase15_aggregate_target_present,
        "shared_ci_phase15_present": shared_ci_phase15_present,
        "phase15_replay_green_on_current_master": False,
    }
    for key, value in observed.items():
        if repo_evidence[key] != value:
            failures.append(f"readiness manifest {key} disagrees with repo reality")

    return failures


def _sample_note() -> str:
    return """# Phase 15 Readiness Gate Survey

- `PHASE15_STATUS=readiness_gate_survey_landed`
- `PHASE15_LANE_KEY=P15-L02`
- `PHASE15_SLICE=validator_first_readiness_packet`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-25`

This note says the governance packet is materially landed and reviewable, the dedicated validator now exists as a directly readable maintenance gate, the dedicated shared-build companion is now directly readable current-master evidence, and broader make-wrapper and workflow companions still block any claim that the larger Phase 15 replay route is one-command or shared-CI ready.

- `scripts/zigux/check-phase15-readiness-gate-packet.py`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
- `zigux/tests/phase15_readiness_gate_manifest.json`

Although `zigux/Makefile` is present on current `master`, it still does not materialize dedicated `phase15*` wrapper routes, so:
- `make -C zigux phase15-validate` remains blocked route vocabulary rather than a directly readable shipped replay path
- `make -C zigux phase15-test` remains blocked route vocabulary rather than a directly readable shipped replay path
- `make -C zigux phase15` remains blocked route vocabulary rather than a directly readable shipped replay path

`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route.

This packet is ready for maintenance-mode truthfulness refreshes, direct validator-first replay, and shared-build companion review only, and no Architecture Council approval is currently recorded for a freeze-map status change.
"""


def _sample_manifest() -> str:
    payload = {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit_mode": "dated_master_readback",
        "surveyed_commit": "current-master-readback-2026-05-25",
        "readiness_packet_checker": "scripts/zigux/check-phase15-readiness-gate-packet.py",
        "direct_packet_paths": [
            "scripts/zigux/check-phase15-readiness-gate-packet.py",
            "scripts/zigux/validate-phase15.py",
            "zigux/tests/phase15_build.zig",
            "zigux/tests/phase15_readiness_gate_manifest.json"
        ],
        "still_missing_broader_paths": [],
        "repo_evidence": {
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
            "phase15_build_zig_present": True,
            "phase15_indefinite_c_lane_owner_alignment_present": True,
            "phase15_makefile_present": True,
            "phase15_validate_target_present": False,
            "phase15_test_target_present": False,
            "phase15_aggregate_target_present": False,
            "shared_ci_phase15_present": False,
            "phase15_replay_green_on_current_master": False
        },
        "phase15_validate_checkers": [
            "scripts/zigux/check-phase15-docs-readme-alignment.py",
            "scripts/zigux/check-phase15-scripts-readme-alignment.py",
            "scripts/zigux/check-phase15-tests-readme-alignment.py",
            "scripts/zigux/check-phase15-review-process-handoff.py",
            "scripts/zigux/check-phase15-shared-summary-gap.py"
        ]
    }
    return json.dumps(payload, indent=2) + "\n"


def _seed_repo(root: Path) -> None:
    _write(root / READINESS_NOTE_PATH, _sample_note())
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / MAKEFILE_PATH, "phase2-toolchain:\n\t@true\n")
    _write(root / WORKFLOW_PATH, "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - run: python3 scripts/zigux/check-phase15-readiness-gate-packet.py\n")

    manifest = json.loads(_sample_manifest())
    for rel in manifest["direct_packet_paths"]:
        if rel == str(MANIFEST_PATH):
            continue
        _write(root / rel, _placeholder_for(rel))
    for rel in manifest["phase15_validate_checkers"]:
        _write(root / rel, _placeholder_for(rel))
    for rel in (
        "scripts/zigux/check-phase15-docs-readme-alignment.py",
        "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
        "scripts/zigux/check-phase15-handoff-note-alignment.py",
        "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
        "zigux/tests/phase15_governance_lane_sequencing.zig",
        "zigux/tests/phase15_handoff_next_steps_manifest.json",
        "zigux/tests/phase15_architecture_council_review_process_build.zig",
        "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    ):
        _write(root / rel, _placeholder_for(rel))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_readiness_gate_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_repo(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        scripts_checker_root = root / "scripts_checker"
        _seed_repo(scripts_checker_root)
        (scripts_checker_root / SCRIPTS_CHECKER_PATH).unlink()
        failures = collect_failures(scripts_checker_root)
        expected = [f"missing_required_path:{SCRIPTS_CHECKER_PATH}"]
        if failures != expected:
            raise AssertionError(f"unexpected scripts-checker failure: {failures}")

        lane_drift_root = root / "lane_drift"
        _seed_repo(lane_drift_root)
        _write(
            lane_drift_root / MANIFEST_PATH,
            _sample_manifest().replace('"lane_key": "P15-L02"', '"lane_key": "P15-L99"', 1),
        )
        failures = collect_failures(lane_drift_root)
        expected = ["readiness manifest lane key drifted from P15-L02: P15-L99"]
        if failures != expected:
            raise AssertionError(f"unexpected lane-drift failure: {failures}")

        direct_root = root / "direct_path"
        _seed_repo(direct_root)
        (direct_root / BUILD_ZIG_PATH).unlink()
        failures = collect_failures(direct_root)
        expected = [
            "direct_packet_path_missing:zigux/tests/phase15_build.zig",
            "readiness manifest phase15_build_zig_present disagrees with repo reality",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected direct-path failure: {failures}")

    print("PHASE15_READINESS_GATE_PACKET_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 readiness-gate packet still matches the current validator-first repo posture."
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
