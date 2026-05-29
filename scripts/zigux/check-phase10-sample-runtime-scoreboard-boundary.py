"""Validate Phase 10 sample/runtime scoreboard boundary evidence."""
from __future__ import annotations

import argparse
import copy
import json
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent
MANIFEST_PATH = "zigux/tests/phase10_closure_manifest.json"

REQUIRED_REFERENCE_SAMPLE_EVIDENCE = [
    "samples/zigux",
    "zigux/tests/phase5_build.zig",
    "Documentation/zigux/review-checklist.md",
]

REQUIRED_RUNTIME_STARTER_EVIDENCE = [
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "Documentation/zigux/phase9-runtime-trace-events-survey.md",
    "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
    "Documentation/zigux/phase9-runtime-bitmap-survey.md",
    "Documentation/zigux/phase9-runtime-bitmap-module-slice.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase9-review-checklist-phase-boundaries.py",
    "scripts/zigux/check-phase9-trace-events-runtime-packet.py",
    "samples/zigux/README.md",
    "samples/zigux/runtime_bitmap.zig",
    "samples/zigux/runtime_bitmap_direct_init_contract.zig",
    "samples/zigux/runtime_bitmap_cold_stage_guard.zig",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_bitmap_top_bit_contract.zig",
    "samples/zigux/runtime_trace_events.zig",
    "samples/zigux/runtime_trace_events_unregistered_gate.zig",
    "samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
    "samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
    "samples/zigux/runtime_trace_events_reinit_rollback_guard.zig",
    "samples/zigux/runtime_trace_events_reinit_reexit_guard.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase9_build.zig",
    "zigux/tests/runtime_loader_allocator_init_flow.zig",
    "zigux/kernel/runtime_loader.zig",
    "zigux/kernel/runtime_loader_contract.zig",
    "zigux/kernel/runtime_loader_command_env_boundary_guard.zig",
    "zigux/tests/runtime_bitmap_manifest.json",
    "zigux/tests/runtime_bitmap_survey.zig",
    "zigux/tests/runtime_bitmap_module.zig",
    "zigux/tests/runtime_bitmap_diff.zig",
    "zigux/tests/runtime_trace_events_loader_substrate_drift.zig",
    "zigux/tests/runtime_trace_events_manifest.json",
    "zigux/tests/runtime_trace_events_survey.zig",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require_evidence(drift: list[str], prefix: str, actual: object, required: list[str]) -> None:
    if not isinstance(actual, list) or not actual:
        drift.append(f"{prefix}:evidence:missing")
        return
    for item in required:
        if item not in actual:
            drift.append(f"{prefix}:evidence:{item!r}:missing")


def collect_drift(manifest: dict) -> list[str]:
    drift: list[str] = []
    boundary = manifest.get("cross_phase_scoreboard_boundary")
    if not isinstance(boundary, dict):
        return ["cross_phase_scoreboard_boundary:missing"]

    reference_samples = boundary.get("reference_samples")
    if not isinstance(reference_samples, dict):
        drift.append("cross_phase_scoreboard_boundary:reference_samples:missing")
    else:
        status = reference_samples.get("status")
        if status != "out_of_scope":
            drift.append(f"cross_phase_scoreboard_boundary:reference_samples:status:{status!r}!='out_of_scope'")
        require_evidence(
            drift,
            "cross_phase_scoreboard_boundary:reference_samples",
            reference_samples.get("evidence"),
            REQUIRED_REFERENCE_SAMPLE_EVIDENCE,
        )

    runtime_starters = boundary.get("runtime_starters")
    if not isinstance(runtime_starters, dict):
        drift.append("cross_phase_scoreboard_boundary:runtime_starters:missing")
    else:
        status = runtime_starters.get("status")
        if status != "out_of_scope":
            drift.append(f"cross_phase_scoreboard_boundary:runtime_starters:status:{status!r}!='out_of_scope'")
        require_evidence(
            drift,
            "cross_phase_scoreboard_boundary:runtime_starters",
            runtime_starters.get("evidence"),
            REQUIRED_RUNTIME_STARTER_EVIDENCE,
        )

    return drift


def validate(root: Path) -> tuple[list[str], list[str]]:
    manifest_path = root / MANIFEST_PATH
    if not manifest_path.exists():
        return ([MANIFEST_PATH], [])
    return ([], collect_drift(read_json(manifest_path)))


def fixture_manifest() -> dict:
    return {
        "cross_phase_scoreboard_boundary": {
            "reference_samples": {
                "status": "out_of_scope",
                "evidence": list(REQUIRED_REFERENCE_SAMPLE_EVIDENCE),
            },
            "runtime_starters": {
                "status": "out_of_scope",
                "evidence": list(REQUIRED_RUNTIME_STARTER_EVIDENCE),
            },
        }
    }


def write_manifest(root: Path, manifest: dict) -> None:
    manifest_path = root / MANIFEST_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def expect_contains(items: list[str], expected: str) -> None:
    if expected not in items:
        actual = ",".join(items) if items else "none"
        raise SystemExit(f"phase10-sample-runtime-scoreboard-boundary-self-test:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_sample_runtime_boundary_") as tmp_dir:
        root = Path(tmp_dir)
        manifest = fixture_manifest()
        write_manifest(root, manifest)
        missing_files, drift = validate(root)
        if missing_files or drift:
            raise SystemExit(
                "phase10-sample-runtime-scoreboard-boundary-self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:drift={','.join(drift) or 'none'}"
            )

        cases = 0
        broken = copy.deepcopy(manifest)
        broken["cross_phase_scoreboard_boundary"]["reference_samples"]["status"] = "starter_landed"
        write_manifest(root, broken)
        expect_contains(
            validate(root)[1],
            "cross_phase_scoreboard_boundary:reference_samples:status:'starter_landed'!='out_of_scope'",
        )
        cases += 1

        broken = copy.deepcopy(manifest)
        broken["cross_phase_scoreboard_boundary"]["reference_samples"]["evidence"].remove("samples/zigux")
        write_manifest(root, broken)
        expect_contains(validate(root)[1], "cross_phase_scoreboard_boundary:reference_samples:evidence:'samples/zigux':missing")
        cases += 1

        broken = copy.deepcopy(manifest)
        broken["cross_phase_scoreboard_boundary"]["runtime_starters"]["status"] = "starter_landed"
        write_manifest(root, broken)
        expect_contains(
            validate(root)[1],
            "cross_phase_scoreboard_boundary:runtime_starters:status:'starter_landed'!='out_of_scope'",
        )
        cases += 1

        broken = copy.deepcopy(manifest)
        broken["cross_phase_scoreboard_boundary"]["runtime_starters"]["evidence"].remove(
            "zigux/tests/runtime_trace_events_survey.zig"
        )
        write_manifest(root, broken)
        expect_contains(
            validate(root)[1],
            "cross_phase_scoreboard_boundary:runtime_starters:evidence:'zigux/tests/runtime_trace_events_survey.zig':missing",
        )
        cases += 1

    print("PHASE10_SAMPLE_RUNTIME_SCOREBOARD_BOUNDARY_SELF_TEST=pass")
    print(f"PHASE10_SAMPLE_RUNTIME_SCOREBOARD_BOUNDARY_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Phase 10 sample/runtime scoreboard boundary evidence.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()

    missing_files, drift = validate(args.repo_root)
    if missing_files:
        print("PHASE10_SAMPLE_RUNTIME_SCOREBOARD_BOUNDARY=fail")
        print("MISSING_PHASE10_SAMPLE_RUNTIME_SCOREBOARD_BOUNDARY_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_SAMPLE_RUNTIME_SCOREBOARD_BOUNDARY_FILES_END")
        return 1
    if drift:
        print("PHASE10_SAMPLE_RUNTIME_SCOREBOARD_BOUNDARY=fail")
        print("PHASE10_SAMPLE_RUNTIME_SCOREBOARD_BOUNDARY_DRIFT_START")
        for item in drift:
            print(item)
        print("PHASE10_SAMPLE_RUNTIME_SCOREBOARD_BOUNDARY_DRIFT_END")
        return 1

    print("PHASE10_SAMPLE_RUNTIME_SCOREBOARD_BOUNDARY=pass")
    print(f"PHASE10_SAMPLE_RUNTIME_REFERENCE_SAMPLE_EVIDENCE_COUNT={len(REQUIRED_REFERENCE_SAMPLE_EVIDENCE)}")
    print(f"PHASE10_SAMPLE_RUNTIME_RUNTIME_STARTER_EVIDENCE_COUNT={len(REQUIRED_RUNTIME_STARTER_EVIDENCE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
