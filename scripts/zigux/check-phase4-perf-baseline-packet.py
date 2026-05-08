#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parent

MANIFEST_PATH = Path("zigux/tests/phase4_perf_baseline_manifest.json")
SURVEY_PATH = Path("zigux/tests/phase4_perf_baseline_survey.zig")

EXPECTED_TOP_LEVEL = {
    "lane_key": "P4-L20",
    "phase": "Phase 4",
    "owner": "Validation and Perf Team",
    "rollback_owner": "Validation and Perf Team",
}

EXPECTED_SUMMARY = {
    "phase4_build_step_present": True,
    "phase4_validation_matrix_present": True,
    "shared_phase4_test_step_includes_survey": False,
    "benchmark_command_unapproved": False,
    "acceptable_limit_unapproved": False,
    "atomic64_benchmark_command_approved": True,
    "atomic64_acceptable_limit_approved": True,
    "bitmap_benchmark_command_approved": True,
    "bitmap_acceptable_limit_approved": True,
}

EXPECTED_GAP_IDS = [
    "phase4-perf-baseline-survey-manifest",
    "phase4-perf-baseline-survey-gate",
    "phase4-perf-baseline-atomic64-command-evidence",
    "phase4-perf-baseline-atomic64-command",
    "phase4-perf-baseline-atomic64-acceptable-limit",
    "phase4-perf-baseline-bitmap-command-evidence",
    "phase4-perf-baseline-bitmap-command",
    "phase4-perf-baseline-bitmap-acceptable-limit",
]

EXPECTED_BENCHMARK_COMMANDS = {
    "phase4-perf-baseline-atomic64-command": (
        "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig"
    ),
    "phase4-perf-baseline-bitmap-command": (
        "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig"
    ),
}

EXPECTED_COMMAND_EVIDENCE = {
    "atomic64": {
        "evidence_status": "benchmark_command_approved",
        "benchmark_command": "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
        "acceptable_limit_status": "approved_local_only",
        "acceptable_limit_metric": "median_elapsed_ns",
        "acceptable_limit_iterations": 4,
        "acceptable_limit_sample_count": 7,
        "acceptable_limit_max_elapsed_ns": 8192,
        "deterministic_replays": [
            {
                "iterations": 1,
                "checksum": 3626254113632800175,
                "final_counter": 130322557735600377,
            },
            {
                "iterations": 4,
                "checksum": 9210681150676220922,
                "final_counter": 130322557735600376,
            },
        ],
    },
    "bitmap": {
        "evidence_status": "benchmark_command_approved",
        "benchmark_command": "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
        "acceptable_limit_status": "approved_local_only",
        "acceptable_limit_metric": "median_elapsed_ns",
        "acceptable_limit_iterations": 4,
        "acceptable_limit_sample_count": 7,
        "acceptable_limit_max_elapsed_ns": 131072,
        "deterministic_replays": [
            {
                "iterations": 1,
                "checksum": 5216946504564592253,
                "final_first_set": 0,
                "final_first_zero": 109,
                "final_weight": 1005,
                "final_nth_seven": 123,
            },
            {
                "iterations": 4,
                "checksum": 7942141539243507472,
                "final_first_set": 0,
                "final_first_zero": 109,
                "final_weight": 1005,
                "final_nth_seven": 123,
            },
        ],
    },
}

EXPECTED_SURVEY_MARKERS = [
    "test \"phase4 perf baseline survey manifest keeps the current benchmark-command posture explicit\"",
    "phase4_perf_baseline_manifest.json",
    "benchmark_command_approved",
    "approved_local_only",
    "median_elapsed_ns",
    "8192",
    "131072",
    "3626254113632800175",
    "9210681150676220922",
    "5216946504564592253",
    "7942141539243507472",
    "phase4-perf-baseline-atomic64-command",
    "phase4-perf-baseline-bitmap-command",
    "starter_landed_count",
]


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_top_level(manifest: dict) -> list[str]:
    problems: list[str] = []
    for field, expected in EXPECTED_TOP_LEVEL.items():
        if manifest.get(field) != expected:
            problems.append(f"top_level:{field}:{manifest.get(field)}:{expected}")
    return problems


def _validate_summary(manifest: dict) -> list[str]:
    problems: list[str] = []
    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        return ["summary:missing"]
    for field, expected in EXPECTED_SUMMARY.items():
        if summary.get(field) != expected:
            problems.append(f"summary:{field}:{summary.get(field)}:{expected}")
    return problems


def _validate_command_evidence(manifest: dict) -> list[str]:
    problems: list[str] = []
    evidence = manifest.get("command_evidence")
    if not isinstance(evidence, dict):
        return ["command_evidence:missing"]

    for key, expected in EXPECTED_COMMAND_EVIDENCE.items():
        packet = evidence.get(key)
        if not isinstance(packet, dict):
            problems.append(f"command_evidence:{key}:missing")
            continue

        for field, expected_value in expected.items():
            if field == "deterministic_replays":
                actual_replays = packet.get(field)
                if actual_replays != expected_value:
                    problems.append(f"command_evidence:{key}:{field}:drift")
                continue
            if packet.get(field) != expected_value:
                problems.append(
                    f"command_evidence:{key}:{field}:{packet.get(field)}:{expected_value}"
                )
    return problems


def _validate_gaps(manifest: dict) -> list[str]:
    problems: list[str] = []
    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        return ["gaps:missing"]

    seen_ids = [gap.get("id") for gap in gaps if isinstance(gap, dict)]
    if seen_ids != EXPECTED_GAP_IDS:
        problems.append(f"gaps:id_order:{seen_ids}:{EXPECTED_GAP_IDS}")

    for gap in gaps:
        if not isinstance(gap, dict):
            problems.append("gaps:non_object")
            continue
        gap_id = gap.get("id")
        if gap.get("status") != "starter_landed":
            problems.append(f"gaps:{gap_id}:status:{gap.get('status')}:starter_landed")
        why_now = gap.get("why_now")
        if not isinstance(why_now, str) or not why_now.strip():
            problems.append(f"gaps:{gap_id}:why_now")
        expected_command = EXPECTED_BENCHMARK_COMMANDS.get(gap_id)
        actual_command = gap.get("benchmark_command")
        if expected_command is None:
            if actual_command is not None:
                problems.append(f"gaps:{gap_id}:benchmark_command:{actual_command}:null")
        elif actual_command != expected_command:
            problems.append(
                f"gaps:{gap_id}:benchmark_command:{actual_command}:{expected_command}"
            )
    return problems


def _validate_survey_text(survey_text: str) -> list[str]:
    problems: list[str] = []
    for marker in EXPECTED_SURVEY_MARKERS:
        if marker not in survey_text:
            problems.append(f"survey:{marker}")
    return problems


def validate_root(root: Path) -> list[str]:
    problems: list[str] = []

    manifest_path = root / MANIFEST_PATH
    survey_path = root / SURVEY_PATH

    if not manifest_path.exists():
        problems.append(f"missing:{MANIFEST_PATH.as_posix()}")
        return problems
    if not survey_path.exists():
        problems.append(f"missing:{SURVEY_PATH.as_posix()}")
        return problems

    manifest = _read_json(manifest_path)
    survey_text = survey_path.read_text(encoding="utf-8")

    problems.extend(_validate_top_level(manifest))
    problems.extend(_validate_summary(manifest))
    problems.extend(_validate_command_evidence(manifest))
    problems.extend(_validate_gaps(manifest))
    problems.extend(_validate_survey_text(survey_text))
    return problems


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build_fixture_tree(root: Path) -> None:
    manifest = {
        "lane_key": "P4-L20",
        "phase": "Phase 4",
        "owner": "Validation and Perf Team",
        "rollback_owner": "Validation and Perf Team",
        "surveyed_gates": [
            {
                "surface": "zigux/tests/atomic64_diff.zig",
                "gate_owner": "ABI and Runtime Team",
                "gate_rollback_owner": "ABI and Runtime Team",
                "threshold_posture": "threshold_pending_until_runtime_atomic64_scope_widens",
            },
            {
                "surface": "zigux/tests/bitmap_diff.zig",
                "gate_owner": "Shared Subsystems Pod",
                "gate_rollback_owner": "Shared Subsystems Pod",
                "threshold_posture": "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
            },
        ],
        "survey_summary": EXPECTED_SUMMARY,
        "command_evidence": EXPECTED_COMMAND_EVIDENCE,
        "gaps": [
            {
                "id": gap_id,
                "status": "starter_landed",
                "kind": "perf_packet",
                "zigux_destination": "zigux/tests/phase4_perf_baseline_manifest.json",
                "benchmark_command": EXPECTED_BENCHMARK_COMMANDS.get(gap_id),
                "why_now": f"{gap_id} stays reviewable inside the dedicated Phase 4 perf-baseline packet.",
            }
            for gap_id in EXPECTED_GAP_IDS
        ],
    }
    _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")

    survey = "\n".join(EXPECTED_SURVEY_MARKERS) + "\n"
    _write(root / SURVEY_PATH, survey)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase4_perf_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_fixture_tree(root)
        assert validate_root(root) == []

        bad_root = Path(tmp_dir) / "bad"
        build_fixture_tree(bad_root)
        manifest = _read_json(bad_root / MANIFEST_PATH)
        manifest["command_evidence"]["atomic64"]["acceptable_limit_sample_count"] = 6
        _write(bad_root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        assert validate_root(bad_root) == [
            "command_evidence:atomic64:acceptable_limit_sample_count:6:7"
        ]

    print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=pass")
    print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST_CASE_COUNT=2")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the dedicated Phase 4 perf-baseline manifest and survey packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root containing zigux/tests/phase4_perf_baseline_* files.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    problems = validate_root(args.root)
    if problems:
        print("PHASE4_PERF_BASELINE_PACKET=fail")
        print("PHASE4_PERF_BASELINE_PACKET_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE4_PERF_BASELINE_PACKET_PROBLEMS_END")
        return 1

    print("PHASE4_PERF_BASELINE_PACKET=pass")
    print(f"PHASE4_PERF_BASELINE_GAP_COUNT={len(EXPECTED_GAP_IDS)}")
    print(f"PHASE4_PERF_BASELINE_SURVEY_MARKER_COUNT={len(EXPECTED_SURVEY_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
