#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

READINESS_NOTE_PATH = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase15_readiness_gate_manifest.json")
GAP_MATRIX_PATH = Path("zigux/tests/phase15_readiness_gap_matrix.json")
SELF_PATH = Path("scripts/zigux/check-phase15-readiness-gate-packet.py")
SCRIPTS_CHECKER_PATH = Path("scripts/zigux/check-phase15-scripts-readme-alignment.py")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
BUILD_ZIG_PATH = Path("zigux/tests/phase15_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

EXPECTED_LANE_KEY = "P15-L04"
EXPECTED_PHASE = "Phase 15"
EXPECTED_GAP_MATRIX_LANE_KEY = "P15-L01"
EXPECTED_BLOCKED_BROADER_ROUTES = {
    "makefile_path": "zigux/Makefile",
    "missing_make_targets": ["phase15-validate", "phase15-test", "phase15"],
    "workflow_path": ".github/workflows/zigux-bootstrap.yml",
    "missing_workflow_phase15_route": True,
}
EXPECTED_ROADMAP_REQUIREMENTS = (
    "freeze map",
    "Architecture Council review process",
    "parity scorecard",
    "policy for code that remains in C indefinitely",
)
EXPECTED_LEDGER_ANCHOR = "docs(zigux): add documentation root, review checklist, and freeze map"
EXPECTED_REMAINING_GAPS = (
    "missing_make_routes",
    "missing_workflow_route",
    "no_architecture_council_status_change_approval",
)

REQUIRED_NOTE_MARKERS = (
    "PHASE15_STATUS=readiness_gate_survey_landed",
    "PHASE15_LANE_KEY=P15-L04",
    "PHASE15_SLICE=validator_first_readiness_packet",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "the governance packet is materially landed and reviewable",
    "the dedicated validator now exists as a directly readable maintenance gate",
    "the dedicated shared-build companion is now directly readable current-master evidence",
    "the roadmap-versus-ledger gap matrix now keeps the remaining readiness requirements explicit",
    "broader make-wrapper and workflow companions still block any claim that the larger Phase 15 replay route is one-command or shared-CI ready",
    "Although `zigux/Makefile` is present on current `master`, it still does not materialize dedicated `phase15*` wrapper routes",
    "ready for maintenance-mode truthfulness refreshes, direct validator-first replay, shared-build companion review, and explicit roadmap-versus-ledger gap accounting only",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
    "`zigux/tests/phase15_readiness_gap_matrix.json`",
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


def _read_json(path: Path) -> dict:
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


def _validate_gap_matrix(gap_matrix: dict, failures: list[str]) -> None:
    if gap_matrix.get("lane_key") != EXPECTED_GAP_MATRIX_LANE_KEY:
        failures.append(
            f"gap matrix lane key drifted from {EXPECTED_GAP_MATRIX_LANE_KEY}: {gap_matrix.get('lane_key', '')}"
        )
    if gap_matrix.get("phase") != EXPECTED_PHASE:
        failures.append(f"gap matrix phase drifted from {EXPECTED_PHASE}: {gap_matrix.get('phase', '')}")

    roadmap_rows = gap_matrix.get("roadmap_required_features", [])
    roadmap_requirements = tuple(row.get("requirement") for row in roadmap_rows)
    if roadmap_requirements != EXPECTED_ROADMAP_REQUIREMENTS:
        failures.append("gap matrix roadmap-required feature rows drifted from the Phase 15 requirement set")

    ledger_rows = gap_matrix.get("ledger_anchors", [])
    if len(ledger_rows) != 1 or ledger_rows[0].get("anchor") != EXPECTED_LEDGER_ANCHOR:
        failures.append("gap matrix ledger anchor rows drifted from the bootstrap ledger anchor")

    remaining_gaps = tuple(row.get("gap") for row in gap_matrix.get("remaining_readiness_gaps", []))
    if remaining_gaps != EXPECTED_REMAINING_GAPS:
        failures.append("gap matrix remaining-readiness gap rows drifted from current repo reality")

    blocked_gap_rows = {
        row.get("gap"): row for row in gap_matrix.get("remaining_readiness_gaps", [])
    }
    make_gap = blocked_gap_rows.get("missing_make_routes", {})
    if make_gap.get("blocked_routes") != EXPECTED_BLOCKED_BROADER_ROUTES["missing_make_targets"]:
        failures.append("gap matrix missing_make_routes blocked-route inventory drifted")
    workflow_gap = blocked_gap_rows.get("missing_workflow_route", {})
    if workflow_gap.get("path") != EXPECTED_BLOCKED_BROADER_ROUTES["workflow_path"]:
        failures.append("gap matrix missing_workflow_route path drifted")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in (
        READINESS_NOTE_PATH,
        MANIFEST_PATH,
        GAP_MATRIX_PATH,
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
    manifest = _read_json(root / MANIFEST_PATH)
    gap_matrix = _read_json(root / GAP_MATRIX_PATH)

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        failures.append(f"readiness manifest lane key drifted from {EXPECTED_LANE_KEY}: {manifest.get('lane_key', '')}")
    if manifest.get("phase") != EXPECTED_PHASE:
        failures.append(f"readiness manifest phase drifted from {EXPECTED_PHASE}: {manifest.get('phase', '')}")
    if manifest.get("surveyed_commit") not in note:
        failures.append("readiness note is missing the manifest surveyed_commit marker")
    if manifest.get("readiness_packet_checker") != str(SELF_PATH):
        failures.append("readiness manifest does not point at the focused readiness-packet checker")
    if manifest.get("roadmap_ledger_gap_matrix") != str(GAP_MATRIX_PATH):
        failures.append("readiness manifest does not point at the roadmap-versus-ledger gap matrix companion")
    if manifest.get("blocked_broader_routes") != EXPECTED_BLOCKED_BROADER_ROUTES:
        failures.append("readiness manifest blocked broader-route evidence drifted from the current validator-first packet")
    if f"`{manifest['readiness_packet_checker']}`" not in note:
        failures.append("readiness note is missing the focused readiness-packet checker marker")
    if f"`{manifest['roadmap_ledger_gap_matrix']}`" not in note:
        failures.append("readiness note is missing the roadmap-versus-ledger gap matrix marker")

    _validate_gap_matrix(gap_matrix, failures)
    if gap_matrix.get("surveyed_commit") != manifest.get("surveyed_commit"):
        failures.append("gap matrix surveyed_commit drifted from the readiness manifest")

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

    blocked_routes = manifest["blocked_broader_routes"]
    phase15_validate_target_present = _makefile_has_target(root, "phase15-validate")
    phase15_test_target_present = _makefile_has_target(root, "phase15-test")
    phase15_aggregate_target_present = _makefile_has_target(root, "phase15")
    shared_ci_phase15_present = _workflow_has_phase15_route(root)

    for target in blocked_routes["missing_make_targets"]:
        marker = BLOCKED_ROUTE_MARKERS[target]
        target_present = {
            "phase15-validate": phase15_validate_target_present,
            "phase15-test": phase15_test_target_present,
            "phase15": phase15_aggregate_target_present,
        }[target]
        if marker not in note:
            failures.append(f"readiness note is missing blocked route marker: {marker}")
        elif target_present:
            failures.append(f"readiness note still treats materialized Phase 15 make route as blocked: `make -C zigux {target}`")

    if blocked_routes["missing_workflow_phase15_route"]:
        if WORKFLOW_BLOCKED_MARKER not in note:
            failures.append(f"readiness note is missing blocked workflow marker: {WORKFLOW_BLOCKED_MARKER}")
        elif shared_ci_phase15_present:
            failures.append("readiness note still treats a materialized Phase 15 workflow route as absent from `.github/workflows/zigux-bootstrap.yml`")

    repo_evidence = manifest["repo_evidence"]
    observed = {
        "phase15_readiness_packet_checker_present": (root / SELF_PATH).exists(),
        "phase15_architecture_council_packet_checker_present": (root / Path("scripts/zigux/check-phase15-architecture-council-packet.py")).exists(),
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
        "phase15_gap_matrix_present": (root / GAP_MATRIX_PATH).exists(),
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
- `PHASE15_LANE_KEY=P15-L04`
- `PHASE15_SLICE=validator_first_readiness_packet`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-27`

This note says the governance packet is materially landed and reviewable, the dedicated validator now exists as a directly readable maintenance gate, the dedicated shared-build companion is now directly readable current-master evidence, the roadmap-versus-ledger gap matrix now keeps the remaining readiness requirements explicit, and broader make-wrapper and workflow companions still block any claim that the larger Phase 15 replay route is one-command or shared-CI ready.

- `scripts/zigux/check-phase15-readiness-gate-packet.py`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_freeze_map_governance.zig`
- `zigux/tests/phase15_build.zig`
- `zigux/tests/phase15_readiness_gate_manifest.json`
- `zigux/tests/phase15_readiness_gap_matrix.json`

Although `zigux/Makefile` is present on current `master`, it still does not materialize dedicated `phase15*` wrapper routes, so:
- `make -C zigux phase15-validate` remains blocked route vocabulary rather than a directly readable shipped replay path
- `make -C zigux phase15-test` remains blocked route vocabulary rather than a directly readable shipped replay path
- `make -C zigux phase15` remains blocked route vocabulary rather than a directly readable shipped replay path

`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route.

This packet is ready for maintenance-mode truthfulness refreshes, direct validator-first replay, shared-build companion review, and explicit roadmap-versus-ledger gap accounting only, and no Architecture Council approval is currently recorded for a freeze-map status change.
"""


def _sample_manifest() -> str:
    payload = {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit_mode": "dated_master_readback",
        "surveyed_commit": "current-master-readback-2026-05-27",
        "readiness_packet_checker": "scripts/zigux/check-phase15-readiness-gate-packet.py",
        "roadmap_ledger_gap_matrix": str(GAP_MATRIX_PATH),
        "direct_packet_paths": [
            "scripts/zigux/check-phase15-readiness-gate-packet.py",
            "scripts/zigux/validate-phase15.py",
            "zigux/tests/phase15_build.zig",
            "zigux/tests/phase15_readiness_gate_manifest.json",
            "zigux/tests/phase15_readiness_gap_matrix.json",
        ],
        "still_missing_broader_paths": [],
        "blocked_broader_routes": EXPECTED_BLOCKED_BROADER_ROUTES,
        "repo_evidence": {
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
        },
        "phase15_validate_checkers": [
            "scripts/zigux/check-phase15-docs-readme-alignment.py",
            "scripts/zigux/check-phase15-scripts-readme-alignment.py",
            "scripts/zigux/check-phase15-tests-readme-alignment.py",
            "scripts/zigux/check-phase15-architecture-council-packet.py",
            "scripts/zigux/check-phase15-review-process-handoff.py",
            "scripts/zigux/check-phase15-shared-summary-gap.py",
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def _sample_gap_matrix() -> str:
    payload = {
        "lane_key": EXPECTED_GAP_MATRIX_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit_mode": "dated_master_readback",
        "surveyed_commit": "current-master-readback-2026-05-27",
        "scope": "tranche readiness gate survey remaining readiness gaps vs roadmap and ledger",
        "roadmap_required_features": [
            {
                "requirement": "freeze map",
                "status": "landed_but_status_change_still_blocked",
                "evidence": [
                    "Documentation/zigux/freeze-map.md",
                    "Documentation/zigux/phase15-freeze-map-governance.md",
                ],
                "remaining_gap": "no Architecture Council approval is currently recorded for a freeze-map status change",
            },
            {
                "requirement": "Architecture Council review process",
                "status": "landed_but_no_reopen_decision_recorded",
                "evidence": [
                    "Documentation/zigux/phase15-architecture-council-review-process.md",
                    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
                    "Documentation/zigux/phase15-architecture-council-decision-index.md",
                ],
                "remaining_gap": "no reopen decision is currently recorded for a deep-core Phase 15 status change",
            },
            {
                "requirement": "parity scorecard",
                "status": "landed_but_not_shared_route_ready",
                "evidence": [
                    "Documentation/zigux/phase15-parity-scorecard.md",
                    "Documentation/zigux/phase15-parity-scorecard-survey.md",
                    "zigux/tests/phase15_parity_scorecard.json",
                    "zigux/tests/phase15_parity_scorecard.zig",
                ],
                "remaining_gap": "the broader Phase 15 replay route is still blocked on missing `phase15*` Makefile wrappers and a dedicated workflow route",
            },
            {
                "requirement": "policy for code that remains in C indefinitely",
                "status": "landed_but_not_one_command_or_ci_ready",
                "evidence": [
                    "Documentation/zigux/phase15-indefinite-c-policy.md",
                    "zigux/tests/phase15_indefinite_c_policy.json",
                    "zigux/tests/phase15_indefinite_c_policy.zig",
                ],
                "remaining_gap": "the indefinite-C policy is landed and replay-backed, but the broader reminder surface is still not one-command or shared-CI ready",
            },
        ],
        "ledger_anchors": [
            {
                "anchor": EXPECTED_LEDGER_ANCHOR,
                "status": "landed_and_materially_exceeded",
                "evidence": [
                    "Documentation/zigux/freeze-map.md",
                    "Documentation/zigux/review-checklist.md",
                    "Documentation/zigux/phase15-readiness-gate-survey.md",
                ],
                "remaining_gap": "none at the original docs-root anchor itself; the remaining readiness gaps now live in missing wrapper and workflow routes",
            }
        ],
        "remaining_readiness_gaps": [
            {
                "gap": "missing_make_routes",
                "status": "blocked",
                "path": "zigux/Makefile",
                "blocked_routes": ["phase15-validate", "phase15-test", "phase15"],
                "why_it_matters": "without dedicated wrapper routes, the broader Phase 15 replay packet is not one-command ready",
            },
            {
                "gap": "missing_workflow_route",
                "status": "blocked",
                "path": ".github/workflows/zigux-bootstrap.yml",
                "why_it_matters": "without a dedicated workflow route, the broader Phase 15 replay packet is not shared-CI ready",
            },
            {
                "gap": "no_architecture_council_status_change_approval",
                "status": "blocked",
                "paths": [
                    "Documentation/zigux/freeze-map.md",
                    "Documentation/zigux/phase15-architecture-council-review-process.md",
                ],
                "why_it_matters": "the landed governance packet still does not authorize a freeze-map status change or direct deep-core Zig delivery claim",
            },
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def _seed_repo(root: Path) -> None:
    _write(root / READINESS_NOTE_PATH, _sample_note())
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / GAP_MATRIX_PATH, _sample_gap_matrix())
    _write(root / MAKEFILE_PATH, "phase2-toolchain:\n\t@true\n")
    _write(root / WORKFLOW_PATH, "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - run: python3 scripts/zigux/check-phase15-readiness-gate-packet.py\n")

    manifest = json.loads(_sample_manifest())
    for rel in manifest["direct_packet_paths"]:
        if rel in {str(MANIFEST_PATH), str(GAP_MATRIX_PATH)}:
            continue
        _write(root / rel, _placeholder_for(rel))
    for rel in manifest["phase15_validate_checkers"]:
        _write(root / rel, _placeholder_for(rel))
    for rel in (
        "scripts/zigux/check-phase15-docs-readme-alignment.py",
        "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
        "scripts/zigux/check-phase15-handoff-note-alignment.py",
        "scripts/zigux/check-phase15-architecture-council-packet.py",
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

        matrix_root = root / "matrix"
        _seed_repo(matrix_root)
        (matrix_root / GAP_MATRIX_PATH).unlink()
        failures = collect_failures(matrix_root)
        expected = [f"missing_required_path:{GAP_MATRIX_PATH}"]
        if failures != expected:
            raise AssertionError(f"unexpected gap-matrix failure: {failures}")

        lane_drift_root = root / "lane_drift"
        _seed_repo(lane_drift_root)
        _write(
            lane_drift_root / GAP_MATRIX_PATH,
            _sample_gap_matrix().replace('"lane_key": "P15-L01"', '"lane_key": "P15-L99"', 1),
        )
        failures = collect_failures(lane_drift_root)
        expected = ["gap matrix lane key drifted from P15-L01: P15-L99"]
        if failures != expected:
            raise AssertionError(f"unexpected gap-matrix lane-drift failure: {failures}")

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
