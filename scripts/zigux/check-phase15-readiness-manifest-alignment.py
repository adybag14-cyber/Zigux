#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

READINESS_NOTE_PATH = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase15_readiness_gate_manifest.json")
READINESS_CHECKER_REL = "scripts/zigux/check-phase15-readiness-gate-packet.py"
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
BUILD_PATH = Path("zigux/tests/phase15_build.zig")

EXPECTED_LANE_KEY = "P15-L02"
EXPECTED_PHASE = "Phase 15"
EXPECTED_SURVEYED_COMMIT = "current-master-readback-2026-05-23"

EXPECTED_DIRECT_PACKET_PATHS = (
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
)

EXPECTED_PHASE15_VALIDATE_CHECKERS = (
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
)

EXPECTED_MISSING_BROADER_PATHS = ("zigux/tests/phase15_build.zig",)

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
    "`scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`",
    "`scripts/zigux/check-phase15-handoff-note-alignment.py`",
    "`scripts/zigux/check-phase15-readiness-gate-packet.py`",
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
    text = _read_text(path)
    return any(marker in text for marker in WORKFLOW_PHASE15_MARKERS)


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    required_paths = (
        READINESS_NOTE_PATH,
        MANIFEST_PATH,
        VALIDATOR_PATH,
        MAKEFILE_PATH,
        WORKFLOW_PATH,
    )
    for rel in required_paths:
        if not (root / rel).exists():
            failures.append(f"missing_required_path:{rel.as_posix()}")
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
    if manifest.get("readiness_packet_checker") != READINESS_CHECKER_REL:
        failures.append("readiness_packet_checker")
    if tuple(manifest.get("direct_packet_paths", ())) != EXPECTED_DIRECT_PACKET_PATHS:
        failures.append("direct_packet_paths")
    if tuple(manifest.get("still_missing_broader_paths", ())) != EXPECTED_MISSING_BROADER_PATHS:
        failures.append("still_missing_broader_paths")
    if tuple(manifest.get("phase15_validate_checkers", ())) != EXPECTED_PHASE15_VALIDATE_CHECKERS:
        failures.append("phase15_validate_checkers")

    repo_evidence = manifest.get("repo_evidence", {})
    for key, expected in EXPECTED_REPO_EVIDENCE.items():
        if repo_evidence.get(key) != expected:
            failures.append(f"repo_evidence:{key}:{repo_evidence.get(key)!r}")

    if EXPECTED_SURVEYED_COMMIT not in note:
        failures.append("missing_note_marker:surveyed_commit")
    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note:
            failures.append(f"missing_note_marker:{marker}")

    for rel in EXPECTED_DIRECT_PACKET_PATHS:
        marker = f"`{rel}`"
        if marker not in note:
            failures.append(f"missing_direct_packet_marker:{marker}")

    for rel in EXPECTED_PHASE15_VALIDATE_CHECKERS:
        marker = f"`{rel}`"
        if marker not in note:
            failures.append(f"missing_validate_checker_marker:{marker}")

    for rel in EXPECTED_MISSING_BROADER_PATHS:
        marker = f"`{rel}`"
        if marker not in note:
            failures.append(f"missing_gap_marker:{marker}")
        if (root / rel).exists():
            failures.append(f"unexpected_materialized_path:{rel}")

    if _makefile_has_target(root, "phase15-validate"):
        failures.append("unexpected_make_target:phase15-validate")
    if _makefile_has_target(root, "phase15-test"):
        failures.append("unexpected_make_target:phase15-test")
    if _makefile_has_target(root, "phase15"):
        failures.append("unexpected_make_target:phase15")
    if _workflow_has_phase15_route(root):
        failures.append("unexpected_workflow_route")

    return failures


def _sample_note() -> str:
    direct_paths = "\n".join(f"- `{rel}`" for rel in EXPECTED_DIRECT_PACKET_PATHS)
    validate_checkers = ", ".join(f"`{rel}`" for rel in EXPECTED_PHASE15_VALIDATE_CHECKERS)
    return f"""# Phase 15 Readiness Gate Survey

This note records the current bounded readiness posture for the landed Phase 15 governance packet on `master`.

## Status

- `PHASE15_STATUS=readiness_gate_survey_landed`
- `PHASE15_LANE_KEY=P15-L02`
- `PHASE15_SLICE=validator_first_readiness_packet`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `{EXPECTED_SURVEYED_COMMIT}`
- role: keep the current Phase 15 governance packet honest now that the dedicated validator exists as a directly readable maintenance gate, while the broader build and route companions still remain blocked on current `master`

This survey keeps those two truths together:

- the governance packet is materially landed and reviewable
- the dedicated validator now exists as a directly readable maintenance gate
- the broader build and workflow companions still block any claim that the larger Phase 15 replay route is fully ready

## Current directly readable readiness packet

{direct_paths}

The current readiness checker packet includes {validate_checkers}, and `python3 scripts/zigux/validate-phase15.py` keeps that broader maintenance replay anchored to the same landed Phase 15 packet.

## Current repo-reality gaps that still block broader readiness

- `zigux/tests/phase15_build.zig`

Although `zigux/Makefile` is present on current `master`, it still does not materialize dedicated `phase15*` wrapper routes, so:

- `make -C zigux phase15-validate` remains blocked route vocabulary rather than a directly readable shipped replay path
- `make -C zigux phase15-test` remains blocked route vocabulary rather than a directly readable shipped replay path
- `make -C zigux phase15` remains blocked route vocabulary rather than a directly readable shipped replay path

`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route, so shared CI coverage for the broader Phase 15 replay packet remains absent rather than directly readable current-master evidence.

- no Architecture Council approval is currently recorded for a freeze-map status change
"""


def _sample_manifest() -> str:
    payload = {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit_mode": "dated_master_readback",
        "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
        "readiness_packet_checker": READINESS_CHECKER_REL,
        "direct_packet_paths": list(EXPECTED_DIRECT_PACKET_PATHS),
        "still_missing_broader_paths": list(EXPECTED_MISSING_BROADER_PATHS),
        "repo_evidence": EXPECTED_REPO_EVIDENCE,
        "phase15_validate_checkers": list(EXPECTED_PHASE15_VALIDATE_CHECKERS),
    }
    return json.dumps(payload, indent=2) + "\n"


def _seed_fixture_root(root: Path) -> None:
    _write(root / READINESS_NOTE_PATH, _sample_note())
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / VALIDATOR_PATH, "#!/usr/bin/env python3\n")
    _write(root / MAKEFILE_PATH, "phase2-toolchain:\n\t@true\n")
    _write(
        root / WORKFLOW_PATH,
        "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - run: python3 scripts/zigux/check-phase15-readiness-gate-packet.py\n",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_readiness_gate_") as tmp_dir:
        base = Path(tmp_dir)

        root = base / "baseline"
        _seed_fixture_root(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        manifest_list_root = base / "manifest_list_missing"
        _seed_fixture_root(manifest_list_root)
        payload = json.loads(_read_text(manifest_list_root / MANIFEST_PATH))
        payload["phase15_validate_checkers"] = [
            rel for rel in EXPECTED_PHASE15_VALIDATE_CHECKERS
            if rel != "scripts/zigux/check-phase15-review-process-handoff.py"
        ]
        _write(manifest_list_root / MANIFEST_PATH, json.dumps(payload, indent=2) + "\n")
        failures = collect_failures(manifest_list_root)
        if failures != ["phase15_validate_checkers"]:
            raise AssertionError(f"unexpected manifest-list failure: {failures}")
        case_count += 1

        note_marker_root = base / "note_marker_missing"
        _seed_fixture_root(note_marker_root)
        note_without_handoff_checker = _sample_note().replace(
            "- `scripts/zigux/check-phase15-handoff-note-alignment.py`\n", "", 1
        ).replace(
            "`scripts/zigux/check-phase15-handoff-note-alignment.py`, ", "", 1
        )
        _write(
            note_marker_root / READINESS_NOTE_PATH,
            note_without_handoff_checker,
        )
        failures = collect_failures(note_marker_root)
        expected = [
            "missing_note_marker:`scripts/zigux/check-phase15-handoff-note-alignment.py`",
            "missing_direct_packet_marker:`scripts/zigux/check-phase15-handoff-note-alignment.py`",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected note-marker failure: {failures}")
        case_count += 1

        workflow_root = base / "workflow_route_present"
        _seed_fixture_root(workflow_root)
        _write(
            workflow_root / WORKFLOW_PATH,
            "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - run: make -C zigux phase15-validate\n",
        )
        failures = collect_failures(workflow_root)
        if failures != ["unexpected_workflow_route"]:
            raise AssertionError(f"unexpected workflow-route failure: {failures}")
        case_count += 1

        build_root = base / "build_present"
        _seed_fixture_root(build_root)
        _write(build_root / BUILD_PATH, "const std = @import(\"std\");\n")
        failures = collect_failures(build_root)
        if failures != ["unexpected_materialized_path:zigux/tests/phase15_build.zig"]:
            raise AssertionError(f"unexpected build-path failure: {failures}")
        case_count += 1

    print("PHASE15_READINESS_GATE_PACKET_SELF_TEST=pass")
    print(f"PHASE15_READINESS_GATE_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 readiness note and manifest stay aligned with the landed governance packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the Phase 15 readiness note and manifest",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run synthetic readiness-packet fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_READINESS_GATE_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
