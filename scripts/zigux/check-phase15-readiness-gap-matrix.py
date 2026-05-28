#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

READINESS_NOTE_PATH = Path("Documentation/zigux/phase15-readiness-gate-survey.md")
READINESS_MANIFEST_PATH = Path("zigux/tests/phase15_readiness_gate_manifest.json")
GAP_MATRIX_PATH = Path("zigux/tests/phase15_readiness_gap_matrix.json")
READINESS_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase15-readiness-gate-packet.py")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase15.py")
BUILD_PATH = Path("zigux/tests/phase15_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

EXPECTED_MATRIX_LANE_KEY = "P15-L01"
EXPECTED_READINESS_LANE_KEY = "P15-L04"
EXPECTED_PHASE = "Phase 15"
EXPECTED_SURVEYED_COMMIT = "current-master-readback-2026-05-27"
EXPECTED_LEDGER_ANCHOR = "docs(zigux): add documentation root, review checklist, and freeze map"
EXPECTED_ROADMAP_REQUIREMENTS = (
    "freeze map",
    "Architecture Council review process",
    "parity scorecard",
    "policy for code that remains in C indefinitely",
)
EXPECTED_REMAINING_GAPS = (
    "missing_make_routes",
    "missing_workflow_route",
    "no_architecture_council_status_change_approval",
)
EXPECTED_BLOCKED_MAKE_TARGETS = ["phase15-validate", "phase15-test", "phase15"]
EXPECTED_WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
EXPECTED_MAKEFILE_PATH = "zigux/Makefile"

REQUIRED_NOTE_MARKERS = (
    "the roadmap-versus-ledger gap matrix now keeps the remaining readiness requirements explicit",
    "`zigux/tests/phase15_readiness_gap_matrix.json`",
    "the roadmap-required freeze map is landed and reviewable",
    "the roadmap-required Architecture Council review process is landed and reviewable",
    "the roadmap-required parity scorecard is landed and replay-backed",
    "the roadmap-required policy for code that remains in C indefinitely is landed and replay-backed",
    "the ledger's original docs-root and freeze-map anchor is satisfied and materially exceeded",
    "`make -C zigux phase15-validate` remains blocked route vocabulary",
    "`make -C zigux phase15-test` remains blocked route vocabulary",
    "`make -C zigux phase15` remains blocked route vocabulary",
    "`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
)

WORKFLOW_PHASE15_MARKERS = (
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "validate-phase15.py",
    "phase15_build.zig",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(_read_text(path))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _placeholder_for(rel: str) -> str:
    if rel.endswith(".py"):
        return "#!/usr/bin/env python3\n"
    if rel.endswith(".json"):
        return "{}\n"
    if rel.endswith(".zig"):
        return 'const std = @import("std");\n\ntest "placeholder" {\n    try std.testing.expect(true);\n}\n'
    if rel.endswith(".md"):
        return f"# Placeholder for {rel}\n"
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

    required_paths = (
        READINESS_NOTE_PATH,
        READINESS_MANIFEST_PATH,
        GAP_MATRIX_PATH,
        READINESS_PACKET_CHECKER_PATH,
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

    note = _read_text(root / READINESS_NOTE_PATH)
    readiness_manifest = _read_json(root / READINESS_MANIFEST_PATH)
    gap_matrix = _read_json(root / GAP_MATRIX_PATH)

    if gap_matrix.get("lane_key") != EXPECTED_MATRIX_LANE_KEY:
        failures.append(f"gap_matrix_lane_key:{gap_matrix.get('lane_key')!r}")
    if gap_matrix.get("phase") != EXPECTED_PHASE:
        failures.append(f"gap_matrix_phase:{gap_matrix.get('phase')!r}")
    if gap_matrix.get("surveyed_commit") != EXPECTED_SURVEYED_COMMIT:
        failures.append(f"gap_matrix_surveyed_commit:{gap_matrix.get('surveyed_commit')!r}")

    if readiness_manifest.get("lane_key") != EXPECTED_READINESS_LANE_KEY:
        failures.append(f"readiness_manifest_lane_key:{readiness_manifest.get('lane_key')!r}")
    if readiness_manifest.get("phase") != EXPECTED_PHASE:
        failures.append(f"readiness_manifest_phase:{readiness_manifest.get('phase')!r}")
    if readiness_manifest.get("surveyed_commit") != EXPECTED_SURVEYED_COMMIT:
        failures.append(
            f"readiness_manifest_surveyed_commit:{readiness_manifest.get('surveyed_commit')!r}"
        )
    if readiness_manifest.get("roadmap_ledger_gap_matrix") != str(GAP_MATRIX_PATH):
        failures.append("readiness_manifest_gap_matrix_path")
    if readiness_manifest.get("readiness_packet_checker") != str(READINESS_PACKET_CHECKER_PATH):
        failures.append("readiness_manifest_checker_path")

    roadmap_requirements = tuple(
        row.get("requirement") for row in gap_matrix.get("roadmap_required_features", [])
    )
    if roadmap_requirements != EXPECTED_ROADMAP_REQUIREMENTS:
        failures.append("roadmap_required_features")

    ledger_rows = gap_matrix.get("ledger_anchors", [])
    if len(ledger_rows) != 1 or ledger_rows[0].get("anchor") != EXPECTED_LEDGER_ANCHOR:
        failures.append("ledger_anchors")

    remaining_gaps = tuple(
        row.get("gap") for row in gap_matrix.get("remaining_readiness_gaps", [])
    )
    if remaining_gaps != EXPECTED_REMAINING_GAPS:
        failures.append("remaining_readiness_gaps")

    blocked_gap_rows = {row.get("gap"): row for row in gap_matrix.get("remaining_readiness_gaps", [])}
    make_gap = blocked_gap_rows.get("missing_make_routes", {})
    if make_gap.get("path") != EXPECTED_MAKEFILE_PATH:
        failures.append("missing_make_routes_path")
    if make_gap.get("blocked_routes") != EXPECTED_BLOCKED_MAKE_TARGETS:
        failures.append("missing_make_routes_blocked_routes")

    workflow_gap = blocked_gap_rows.get("missing_workflow_route", {})
    if workflow_gap.get("path") != EXPECTED_WORKFLOW_PATH:
        failures.append("missing_workflow_route_path")

    approval_gap = blocked_gap_rows.get("no_architecture_council_status_change_approval", {})
    approval_paths = approval_gap.get("paths", [])
    if "Documentation/zigux/freeze-map.md" not in approval_paths:
        failures.append("approval_gap_freeze_map_path")
    if "Documentation/zigux/phase15-architecture-council-review-process.md" not in approval_paths:
        failures.append("approval_gap_review_process_path")

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note:
            failures.append(f"missing_note_marker:{marker}")
    if EXPECTED_SURVEYED_COMMIT not in note:
        failures.append("missing_note_surveyed_commit")
    if "`scripts/zigux/check-phase15-readiness-gate-packet.py`" not in note:
        failures.append("missing_note_readiness_checker")
    if "`scripts/zigux/validate-phase15.py`" not in note:
        failures.append("missing_note_validator")
    if "`zigux/tests/phase15_build.zig`" not in note:
        failures.append("missing_note_build")

    for rel in readiness_manifest.get("direct_packet_paths", []):
        if rel == str(GAP_MATRIX_PATH):
            if f"`{rel}`" not in note:
                failures.append(f"missing_direct_packet_marker:{rel}")
            if not (root / rel).exists():
                failures.append(f"missing_direct_packet_path:{rel}")

    repo_evidence = readiness_manifest.get("repo_evidence", {})
    observed_makefile = (root / MAKEFILE_PATH).exists()
    observed_build = (root / BUILD_PATH).exists()
    observed_gap_matrix = (root / GAP_MATRIX_PATH).exists()
    if repo_evidence.get("phase15_makefile_present") != observed_makefile:
        failures.append("repo_evidence_makefile_present")
    if repo_evidence.get("phase15_build_zig_present") != observed_build:
        failures.append("repo_evidence_build_zig_present")
    if repo_evidence.get("phase15_gap_matrix_present") != observed_gap_matrix:
        failures.append("repo_evidence_gap_matrix_present")

    phase15_validate_target_present = _makefile_has_target(root, "phase15-validate")
    phase15_test_target_present = _makefile_has_target(root, "phase15-test")
    phase15_aggregate_target_present = _makefile_has_target(root, "phase15")
    shared_ci_phase15_present = _workflow_has_phase15_route(root)

    if repo_evidence.get("phase15_validate_target_present") != phase15_validate_target_present:
        failures.append("repo_evidence_phase15_validate_target_present")
    if repo_evidence.get("phase15_test_target_present") != phase15_test_target_present:
        failures.append("repo_evidence_phase15_test_target_present")
    if repo_evidence.get("phase15_aggregate_target_present") != phase15_aggregate_target_present:
        failures.append("repo_evidence_phase15_aggregate_target_present")
    if repo_evidence.get("shared_ci_phase15_present") != shared_ci_phase15_present:
        failures.append("repo_evidence_shared_ci_phase15_present")

    for target in EXPECTED_BLOCKED_MAKE_TARGETS:
        if _makefile_has_target(root, target):
            failures.append(f"unexpected_make_target:{target}")
    if shared_ci_phase15_present:
        failures.append("unexpected_workflow_route")

    return failures


def _sample_note() -> str:
    return """# Phase 15 Readiness Gate Survey

- `PHASE15_STATUS=readiness_gate_survey_landed`
- `PHASE15_LANE_KEY=P15-L04`
- `PHASE15_SLICE=validator_first_readiness_packet`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-27`

This note says the roadmap-versus-ledger gap matrix now keeps the remaining readiness requirements explicit.

- the roadmap-required freeze map is landed and reviewable
- the roadmap-required Architecture Council review process is landed and reviewable
- the roadmap-required parity scorecard is landed and replay-backed
- the roadmap-required policy for code that remains in C indefinitely is landed and replay-backed
- the ledger's original docs-root and freeze-map anchor is satisfied and materially exceeded
- `zigux/tests/phase15_readiness_gap_matrix.json`
- `scripts/zigux/check-phase15-readiness-gate-packet.py`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`

`make -C zigux phase15-validate` remains blocked route vocabulary
`make -C zigux phase15-test` remains blocked route vocabulary
`make -C zigux phase15` remains blocked route vocabulary
`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route
no Architecture Council approval is currently recorded for a freeze-map status change
"""


def _sample_manifest() -> str:
    payload = {
        "lane_key": EXPECTED_READINESS_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit_mode": "dated_master_readback",
        "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
        "readiness_packet_checker": str(READINESS_PACKET_CHECKER_PATH),
        "roadmap_ledger_gap_matrix": str(GAP_MATRIX_PATH),
        "direct_packet_paths": [
            str(READINESS_PACKET_CHECKER_PATH),
            str(VALIDATOR_PATH),
            str(BUILD_PATH),
            str(READINESS_MANIFEST_PATH),
            str(GAP_MATRIX_PATH),
        ],
        "still_missing_broader_paths": [],
        "blocked_broader_routes": {
            "makefile_path": EXPECTED_MAKEFILE_PATH,
            "missing_make_targets": EXPECTED_BLOCKED_MAKE_TARGETS,
            "workflow_path": EXPECTED_WORKFLOW_PATH,
            "missing_workflow_phase15_route": True,
        },
        "repo_evidence": {
            "phase15_makefile_present": True,
            "phase15_build_zig_present": True,
            "phase15_gap_matrix_present": True,
            "phase15_validate_target_present": False,
            "phase15_test_target_present": False,
            "phase15_aggregate_target_present": False,
            "shared_ci_phase15_present": False,
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def _sample_gap_matrix() -> str:
    payload = {
        "lane_key": EXPECTED_MATRIX_LANE_KEY,
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
        "ledger_anchors": [{"anchor": EXPECTED_LEDGER_ANCHOR}],
        "remaining_readiness_gaps": [
            {
                "gap": "missing_make_routes",
                "path": EXPECTED_MAKEFILE_PATH,
                "blocked_routes": EXPECTED_BLOCKED_MAKE_TARGETS,
            },
            {
                "gap": "missing_workflow_route",
                "path": EXPECTED_WORKFLOW_PATH,
            },
            {
                "gap": "no_architecture_council_status_change_approval",
                "paths": [
                    "Documentation/zigux/freeze-map.md",
                    "Documentation/zigux/phase15-architecture-council-review-process.md",
                ],
            },
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def write_sample_root(root: Path) -> None:
    _write(root / READINESS_NOTE_PATH, _sample_note())
    _write(root / READINESS_MANIFEST_PATH, _sample_manifest())
    _write(root / GAP_MATRIX_PATH, _sample_gap_matrix())
    _write(root / READINESS_PACKET_CHECKER_PATH, _placeholder_for(str(READINESS_PACKET_CHECKER_PATH)))
    _write(root / VALIDATOR_PATH, _placeholder_for(str(VALIDATOR_PATH)))
    _write(root / BUILD_PATH, _placeholder_for(str(BUILD_PATH)))
    _write(root / MAKEFILE_PATH, "phase2-toolchain:\n\t@true\n")
    _write(root / WORKFLOW_PATH, "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n      - run: python3 scripts/zigux/check-phase15-readiness-gate-packet.py\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_readiness_gap_matrix_") as tmp_dir:
        root = Path(tmp_dir)

        baseline = root / "baseline"
        write_sample_root(baseline)
        failures = collect_failures(baseline)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_matrix = root / "missing_matrix"
        write_sample_root(missing_matrix)
        (missing_matrix / GAP_MATRIX_PATH).unlink()
        failures = collect_failures(missing_matrix)
        expected = [f"missing_required_path:{GAP_MATRIX_PATH}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-matrix failure: {failures}")

        lane_drift = root / "lane_drift"
        write_sample_root(lane_drift)
        _write(
            lane_drift / GAP_MATRIX_PATH,
            _sample_gap_matrix().replace('"lane_key": "P15-L01"', '"lane_key": "P15-L99"', 1),
        )
        failures = collect_failures(lane_drift)
        expected = ["gap_matrix_lane_key:'P15-L99'"]
        if failures != expected:
            raise AssertionError(f"unexpected lane-drift failure: {failures}")

        unexpected_make = root / "unexpected_make"
        write_sample_root(unexpected_make)
        _write(unexpected_make / MAKEFILE_PATH, "phase15-validate:\n\t@true\n")
        failures = collect_failures(unexpected_make)
        expected = [
            "repo_evidence_phase15_validate_target_present",
            "unexpected_make_target:phase15-validate",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected make-target failure: {failures}")

        unexpected_workflow = root / "unexpected_workflow"
        write_sample_root(unexpected_workflow)
        _write(
            unexpected_workflow / WORKFLOW_PATH,
            "jobs:\n  bootstrap:\n    steps:\n      - run: make -C zigux phase15-validate\n",
        )
        failures = collect_failures(unexpected_workflow)
        expected = [
            "repo_evidence_shared_ci_phase15_present",
            "unexpected_workflow_route",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected workflow failure: {failures}")

    print("PHASE15_READINESS_GAP_MATRIX_SELF_TEST=pass")
    print("PHASE15_READINESS_GAP_MATRIX_SELF_TEST_CASES=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 readiness gap matrix still matches the current validator-first repo posture."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument(
        "--self-test", action="store_true", help="run the built-in synthetic self-test"
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a marker-faithful sample root for focused checker replay",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE15_READINESS_GAP_MATRIX_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = collect_failures(args.root)
    if failures:
        print("PHASE15_READINESS_GAP_MATRIX=fail")
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_READINESS_GAP_MATRIX=pass")
    print(f"PHASE15_READINESS_GAP_MATRIX_REQUIREMENT_COUNT={len(EXPECTED_ROADMAP_REQUIREMENTS)}")
    print(f"PHASE15_READINESS_GAP_MATRIX_GAP_COUNT={len(EXPECTED_REMAINING_GAPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
