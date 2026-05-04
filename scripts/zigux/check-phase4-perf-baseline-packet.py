#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/phase4-validation-matrix.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "scripts/zigux/README.md",
    "zigux/Makefile",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/bitmap_diff.zig",
]

MANIFEST_EXPECTATIONS = {
    "lane_key": "P4-L20",
    "phase": "Phase 4",
    "owner": "Validation and Perf Team",
    "rollback_owner": "Validation and Perf Team",
}

EXPECTED_SURVEYED_GATES = {
    "zigux/tests/atomic64_diff.zig": {
        "gate_owner": "ABI and Runtime Team",
        "gate_rollback_owner": "ABI and Runtime Team",
        "threshold_posture": "threshold_pending_until_runtime_atomic64_scope_widens",
    },
    "zigux/tests/bitmap_diff.zig": {
        "gate_owner": "Shared Subsystems Pod",
        "gate_rollback_owner": "Shared Subsystems Pod",
        "threshold_posture": "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
    },
}

EXPECTED_PENDING_PLANS = {
    "zigux/tests/atomic64_diff.zig": {
        "current_correctness_replay": "make -C zigux phase4-runtime-atomic64-diff",
        "benchmark_command": "unapproved_until_runtime_atomic64_scope_widens",
        "acceptable_limit": "unapproved_until_runtime_atomic64_scope_widens",
        "status": "pending_scope_widening",
    },
    "zigux/tests/bitmap_diff.zig": {
        "current_correctness_replay": "make -C zigux phase4-bitmap-diff",
        "benchmark_command": "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        "acceptable_limit": "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        "status": "pending_bounded_benchmark",
    },
}

SURVEY_MARKERS = [
    'const current_surveyed_commit = "',
    "phase4_perf_baseline_manifest.json",
    "make -C zigux phase4-runtime-atomic64-diff",
    "make -C zigux phase4-bitmap-diff",
    "unapproved_until_runtime_atomic64_scope_widens",
    "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
    "threshold_pending_until_runtime_atomic64_scope_widens",
    "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
]

VALIDATOR_MARKERS = [
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "phase4-perf-baseline-survey-tests",
]

MAKE_MARKERS = [
    "phase4-perf-baseline-survey",
    "phase4-validate",
]

BUILD_MARKERS = [
    "phase4_perf_baseline_survey.zig",
    "phase4-perf-baseline-survey-tests",
    '"phase4-perf-baseline-survey"',
]

MATRIX_MARKERS = [
    "phase4_perf_baseline_manifest.json",
    "phase4_perf_baseline_survey.zig",
    "phase4-perf-baseline-survey-tests",
    "make -C zigux phase4-perf-baseline-survey",
    "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land",
    "benchmark command and acceptable limit are still unapproved for both landed gates",
]

GATE_EVIDENCE_MARKERS = [
    "PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA=",
    "PHASE4_PERF_BASELINE_SURVEY_BLOB_SHA=",
    "make -C zigux phase4-runtime-atomic64-diff",
    "make -C zigux phase4-bitmap-diff",
    "pending threshold-plan record per shipped rollback gate",
]

SCRIPTS_README_MARKERS = [
    "make -C zigux phase4-perf-baseline-survey",
    "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land",
    "validate-phase4.py",
]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def missing_text(text: str, prefix: str, markers: list[str]) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def collect_missing() -> list[str]:
    missing = [f"file:{path}" for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        return missing

    manifest = json.loads(read_text("zigux/tests/phase4_perf_baseline_manifest.json"))
    survey = read_text("zigux/tests/phase4_perf_baseline_survey.zig")
    validator = read_text("scripts/zigux/validate-phase4.py")
    makefile = read_text("zigux/Makefile")
    build = read_text("zigux/tests/phase4_build.zig")
    matrix = read_text("Documentation/zigux/phase4-validation-matrix.md")
    gate_evidence = read_text("Documentation/zigux/phase4-gate-evidence.md")
    scripts_readme = read_text("scripts/zigux/README.md")
    runtime_manifest = json.loads(
        read_text("zigux/tests/phase4_runtime_atomic64_diff_manifest.json")
    )

    for key, expected in MANIFEST_EXPECTATIONS.items():
        if manifest.get(key) != expected:
            missing.append(
                f"manifest:{key}:expected={expected}:actual={manifest.get(key)}"
            )

    surveyed_gates = manifest.get("surveyed_gates")
    if not isinstance(surveyed_gates, list):
        missing.append("manifest:surveyed_gates")
    else:
        gate_map = {
            gate.get("surface"): gate
            for gate in surveyed_gates
            if isinstance(gate, dict) and isinstance(gate.get("surface"), str)
        }
        for surface, expected in EXPECTED_SURVEYED_GATES.items():
            gate = gate_map.get(surface)
            if gate is None:
                missing.append(f"manifest:surveyed_gate:{surface}")
                continue
            for key, value in expected.items():
                if gate.get(key) != value:
                    missing.append(
                        f"manifest:surveyed_gate:{surface}:{key}:expected={value}:actual={gate.get(key)}"
                    )

    pending_plans = manifest.get("pending_threshold_plans")
    if not isinstance(pending_plans, list):
        missing.append("manifest:pending_threshold_plans")
    else:
        plan_map = {
            plan.get("surface"): plan
            for plan in pending_plans
            if isinstance(plan, dict) and isinstance(plan.get("surface"), str)
        }
        for surface, expected in EXPECTED_PENDING_PLANS.items():
            plan = plan_map.get(surface)
            if plan is None:
                missing.append(f"manifest:pending_plan:{surface}")
                continue
            for key, value in expected.items():
                if plan.get(key) != value:
                    missing.append(
                        f"manifest:pending_plan:{surface}:{key}:expected={value}:actual={plan.get(key)}"
                    )

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        missing.append("manifest:survey_summary")
    else:
        for key in (
            "phase4_build_present",
            "phase4_validator_present",
            "phase4_validation_matrix_present",
            "benchmark_command_unapproved",
            "acceptable_limit_unapproved",
        ):
            if summary.get(key) is not True:
                missing.append(f"manifest:survey_summary:{key}")

    threshold_plan = runtime_manifest.get("threshold_plan")
    if not isinstance(threshold_plan, dict) or threshold_plan.get(
        "benchmark_command"
    ) != "unapproved_until_runtime_atomic64_scope_widens":
        missing.append("runtime_manifest:threshold_plan:benchmark_command")

    missing.extend(missing_text(survey, "survey", SURVEY_MARKERS))
    missing.extend(missing_text(validator, "validator", VALIDATOR_MARKERS))
    missing.extend(missing_text(makefile, "make", MAKE_MARKERS))
    missing.extend(missing_text(build, "build", BUILD_MARKERS))
    missing.extend(missing_text(matrix, "matrix", MATRIX_MARKERS))
    missing.extend(missing_text(gate_evidence, "gate_evidence", GATE_EVIDENCE_MARKERS))
    missing.extend(
        missing_text(scripts_readme, "scripts_readme", SCRIPTS_README_MARKERS)
    )
    return missing


def expect_contains(label: str, missing: list[str], expected_item: str) -> None:
    if expected_item not in missing:
        actual = ",".join(missing) if missing else "none"
        raise SystemExit(
            f"phase4-perf-baseline-self-test:{label}:expected_missing:{expected_item}:actual:{actual}"
        )


def run_self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory(prefix="zigux_phase4_perf_") as tmp:
        root = Path(tmp)

        def write(rel: str, content: str) -> None:
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

        manifest = {
            **MANIFEST_EXPECTATIONS,
            "surveyed_commit": "3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3",
            "surveyed_gates": [
                {"surface": surface, **values}
                for surface, values in EXPECTED_SURVEYED_GATES.items()
            ],
            "pending_threshold_plans": [
                {"surface": surface, **values}
                for surface, values in EXPECTED_PENDING_PLANS.items()
            ],
            "survey_summary": {
                "phase4_build_present": True,
                "phase4_validator_present": True,
                "phase4_validation_matrix_present": True,
                "benchmark_command_unapproved": True,
                "acceptable_limit_unapproved": True,
            },
            "gaps": [],
        }

        file_map = {
            "scripts/zigux/check-phase4-perf-baseline-packet.py": "# fixture\n",
            "scripts/zigux/validate-phase4.py": "\n".join(VALIDATOR_MARKERS) + "\n",
            "Documentation/zigux/phase4-validation-matrix.md": "\n".join(MATRIX_MARKERS) + "\n",
            "Documentation/zigux/phase4-gate-evidence.md": "\n".join(GATE_EVIDENCE_MARKERS) + "\n",
            "scripts/zigux/README.md": "\n".join(SCRIPTS_README_MARKERS) + "\n",
            "zigux/Makefile": "\n".join(MAKE_MARKERS) + "\n",
            "zigux/tests/phase4_build.zig": "\n".join(BUILD_MARKERS) + "\n",
            "zigux/tests/phase4_perf_baseline_manifest.json": json.dumps(manifest) + "\n",
            "zigux/tests/phase4_perf_baseline_survey.zig": "\n".join(SURVEY_MARKERS) + "\n",
            "zigux/tests/phase4_runtime_atomic64_diff_manifest.json": json.dumps(
                {
                    "threshold_plan": {
                        "benchmark_command": "unapproved_until_runtime_atomic64_scope_widens"
                    }
                }
            )
            + "\n",
            "zigux/tests/atomic64_diff.zig": "atomic64\n",
            "zigux/tests/bitmap_diff.zig": "bitmap\n",
        }
        for rel, content in file_map.items():
            write(rel, content)

        global ROOT
        old_root = ROOT
        ROOT = root
        try:
            missing = collect_missing()
            if missing:
                raise SystemExit(
                    "phase4-perf-baseline-self-test:unexpected_failures:"
                    + ",".join(missing)
                )

            write("scripts/zigux/README.md", "")
            missing = collect_missing()
            expect_contains(
                "scripts_readme_detection",
                missing,
                "scripts_readme:make -C zigux phase4-perf-baseline-survey",
            )

            write(
                "scripts/zigux/README.md",
                "\n".join(SCRIPTS_README_MARKERS) + "\n",
            )
            broken = manifest.copy()
            broken["lane_key"] = "wrong"
            write(
                "zigux/tests/phase4_perf_baseline_manifest.json",
                json.dumps(broken) + "\n",
            )
            missing = collect_missing()
            expect_contains(
                "manifest_detection",
                missing,
                "manifest:lane_key:expected=P4-L20:actual=wrong",
            )
        finally:
            ROOT = old_root

    print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST=pass")
    print("PHASE4_PERF_BASELINE_PACKET_SELF_TEST_CASE_COUNT=2")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())


missing = collect_missing()
if missing:
    print("PHASE4_PERF_BASELINE_PACKET=fail")
    print("PHASE4_PERF_BASELINE_PACKET_MISSING_START")
    for item in missing:
        print(item)
    print("PHASE4_PERF_BASELINE_PACKET_MISSING_END")
    sys.exit(1)

print("PHASE4_PERF_BASELINE_PACKET=pass")
print(f"PHASE4_PERF_BASELINE_PACKET_FILE_COUNT={len(REQUIRED_FILES)}")
print(f"PHASE4_PERF_BASELINE_PACKET_SURVEY_MARKER_COUNT={len(SURVEY_MARKERS)}")
print(f"PHASE4_PERF_BASELINE_PACKET_GATE_EVIDENCE_MARKER_COUNT={len(GATE_EVIDENCE_MARKERS)}")