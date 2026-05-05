#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BITMAP_BENCH_ROUTE = "zig build phase4-bitmap-bench --build-file zigux/tests/phase4_build.zig"

REQUIRED_FILES = [
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-kprobe-example-packet.py",
    "scripts/zigux/check-phase4-workflow-route-counts.py",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/artifact-diff.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "samples/kprobes/Makefile",
    "samples/kprobes/kprobe_example.c",
    "samples/vfs/Makefile",
    "samples/vfs/test-fsmount.c",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "zigux/tests/phase4_kprobe_example_survey.zig",
    "zigux/tests/phase4_test_fsmount_manifest.json",
    "zigux/tests/phase4_test_fsmount_survey.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_build.zig",
]

MAKE_LINES = [
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-kprobe-example-packet.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-kprobe-example-packet.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py",
]

BUILD_MARKERS = [
    "phase4_runtime_atomic64_diff_survey.zig",
    "phase4_test_fsmount_survey.zig",
    "phase4_kprobe_example_survey.zig",
    "phase4_perf_baseline_survey.zig",
    "phase4-runtime-atomic64-diff-tests",
    "phase4-test-fsmount-survey-tests",
    "phase4-kprobe-example-survey-tests",
    "phase4-perf-baseline-survey-tests",
    "phase4-bitmap-diff-tests",
]

MATRIX_MARKERS = [
    "phase4_kprobe_example_manifest.json",
    "phase4_kprobe_example_survey.zig",
    "phase4-kprobe-example-survey-tests",
    "zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig",
    "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
    "c_anchor_only_until_kprobe_example_starter_lands",
    "samples/zigux/kprobe_example.zig",
    "phase4_test_fsmount_survey.zig",
    "phase4_perf_baseline_manifest.json",
    "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land",
    "threshold_pending_until_runtime_atomic64_scope_widens",
    "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
    BITMAP_BENCH_ROUTE,
    "benchmark command is still unapproved for both landed gates",
    "acceptable limit is still unapproved for both landed gates",
]

BITMAP_MATRIX_MARKERS = [
    "zero-nbits helper calls as explicit no-op rollback checks",
    "zero-length range edits from populated anchors measurable",
]

README_MARKERS = [
    "check-phase4-kprobe-example-packet.py",
    "check-phase4-workflow-route-counts.py",
    "phase4-kprobe-example-survey",
    "phase4-kprobe-example-survey-tests",
    "still-absent `samples/zigux/kprobe_example.zig` sample explicitly survey-only",
    "phase4-perf-baseline-survey-tests",
]

SCRIPTS_README_BITMAP_ROUTE_MARKERS = [
    "make -C zigux phase4-bitmap-diff",
    "phase4-bitmap-diff-tests",
]

ATOMIC64_DOCS_README_MARKERS = [
    "make -C zigux phase4-runtime-atomic64-diff",
    "phase4-runtime-atomic64-diff-tests",
    "phase4-runtime-atomic64-diff-survey-tests",
]

ATOMIC64_SCRIPTS_README_MARKERS = [
    "phase4-runtime-atomic64-diff",
    "phase4-runtime-atomic64-diff-tests",
    "phase4-runtime-atomic64-diff-survey-tests",
]

TESTS_README_MARKERS = [
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "zigux/tests/phase4_kprobe_example_survey.zig",
    "make -C zigux phase4-kprobe-example-survey",
    "phase4-kprobe-example-survey-tests",
    "c_anchor_only_until_kprobe_example_starter_lands",
]

GATE_EVIDENCE_TARGETS = {
    "PHASE4_VALIDATION_MATRIX_BLOB_SHA": "Documentation/zigux/phase4-validation-matrix.md",
    "PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA": "scripts/zigux/check-phase4-gate-evidence.py",
    "PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA": "scripts/zigux/check-phase4-workflow-route-counts.py",
    "PHASE4_VALIDATOR_BLOB_SHA": "scripts/zigux/validate-phase4.py",
    "PHASE4_BUILD_BLOB_SHA": "zigux/tests/phase4_build.zig",
    "PHASE4_MAKEFILE_BLOB_SHA": "zigux/Makefile",
    "PHASE4_WORKFLOW_BLOB_SHA": ".github/workflows/zigux-bootstrap.yml",
    "PHASE4_KPROBE_EXAMPLE_MANIFEST_BLOB_SHA": "zigux/tests/phase4_kprobe_example_manifest.json",
    "PHASE4_KPROBE_EXAMPLE_SURVEY_BLOB_SHA": "zigux/tests/phase4_kprobe_example_survey.zig",
    "PHASE4_TEST_FSMOUNT_MANIFEST_BLOB_SHA": "zigux/tests/phase4_test_fsmount_manifest.json",
    "PHASE4_TEST_FSMOUNT_SURVEY_BLOB_SHA": "zigux/tests/phase4_test_fsmount_survey.zig",
    "PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA": "zigux/tests/phase4_perf_baseline_manifest.json",
    "PHASE4_PERF_BASELINE_SURVEY_BLOB_SHA": "zigux/tests/phase4_perf_baseline_survey.zig",
    "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA": "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA": "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "PHASE4_DOC_README_BLOB_SHA": "Documentation/zigux/README.md",
    "PHASE4_SCRIPT_README_BLOB_SHA": "scripts/zigux/README.md",
    "PHASE4_TESTS_README_BLOB_SHA": "zigux/tests/README.md",
}

ATOMIC64_GATE_EVIDENCE_MARKERS = [
    "make -C zigux phase4-runtime-atomic64-diff",
    "phase4-runtime-atomic64-diff-tests",
    "phase4-runtime-atomic64-diff-survey-tests",
    "runtime_atomic64_diff.zig` remains the single replay body",
]

BITMAP_GATE_EVIDENCE_MARKERS = [
    "the refreshed bitmap row still treats the 115-bit fill as resolved parity rather than an open survey-only mismatch",
    BITMAP_BENCH_ROUTE,
]

ARTIFACT_DIFF_NOTE_MARKERS = [
    "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=18",
    "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT=23",
    "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT=4",
    "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=27",
]

GATE_EVIDENCE_STATUS_MARKERS = [
    "PHASE4_GATE_EVIDENCE_SELF_TEST=pass",
    "PHASE4_GATE_EVIDENCE_CHECK=pass",
    "PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass",
    "PHASE4_WORKFLOW_ROUTE_COUNTS=pass",
    "PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT=5",
    "PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_CHECK_COUNT=36",
]

EXACT_GATE_EVIDENCE_WORKFLOW_ROUTE_STATUS_MARKERS = [
    "PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass",
    "PHASE4_WORKFLOW_ROUTE_COUNTS=pass",
    "PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT=5",
    "PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_CHECK_COUNT=36",
]

GATE_EVIDENCE_TARGET_COUNT_STATUS_LINE = "- `PHASE4_GATE_EVIDENCE_TARGET_COUNT=18`"

GATE_EVIDENCE_WORKFLOW_ROUTE_NOTE_MARKERS = [
    "`PHASE4_GATE_EVIDENCE_TARGET_COUNT=18` continues to describe the narrower gate-evidence-checker-enforced blob target set",
    "the dedicated workflow-route checker file itself",
]

RUNTIME_ATOMIC64_MATRIX_NOTE_MARKERS = [
    "reversible-delivery evidence",
    "`lib/atomic64_test.c` anchor",
    "shared `phase4_build.zig` entrypoint",
]

PERF_BASELINE_SURVEYED_GATE_EXPECTATIONS = {
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

PERF_BASELINE_PENDING_PLAN_EXPECTATIONS = {
    "zigux/tests/atomic64_diff.zig": {
        "gate_owner": "ABI and Runtime Team",
        "gate_rollback_owner": "ABI and Runtime Team",
        "threshold_posture": "threshold_pending_until_runtime_atomic64_scope_widens",
        "current_correctness_replay": "make -C zigux phase4-runtime-atomic64-diff",
        "threshold_ready_surface": "post-selftest replay explicit for the current rollback gate",
        "benchmark_command": "unapproved_until_runtime_atomic64_scope_widens",
        "acceptable_limit": "unapproved_until_runtime_atomic64_scope_widens",
        "next_threshold_step": "broader atomic64 benchmark entrypoint",
        "status": "pending_scope_widening",
        "why_not_approved_yet": "post-selftest replay explicit",
    },
    "zigux/tests/bitmap_diff.zig": {
        "gate_owner": "Shared Subsystems Pod",
        "gate_rollback_owner": "Shared Subsystems Pod",
        "threshold_posture": "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        "current_correctness_replay": "make -C zigux phase4-bitmap-diff",
        "threshold_ready_surface": "runThresholdReplay() as the deterministic bitmap threshold batch",
        "benchmark_command": "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        "acceptable_limit": "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        "next_threshold_step": "isolated bitmap benchmark route",
        "status": "pending_bounded_benchmark",
        "why_not_approved_yet": "deterministic threshold replay batch ready",
        "benchmark_route": BITMAP_BENCH_ROUTE,
    },
}


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def read_json(root: Path, rel: str) -> object:
    return json.loads(read_text(root, rel))


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def missing_text(text: str, prefix: str, markers: list[str]) -> list[str]:
    return [f"{prefix}:{m}" for m in markers if m not in text]


def exact_count_mismatches(
    text: str,
    prefix: str,
    markers: list[str],
    expected_count: int = 1,
) -> list[str]:
    mismatches: list[str] = []
    for marker in markers:
        actual_count = text.count(marker)
        if actual_count != expected_count:
            mismatches.append(f"{prefix}:{marker}:{actual_count}")
    return mismatches


def find_gap_by_id(manifest: object, gap_id: str) -> dict[str, object] | None:
    if not isinstance(manifest, dict):
        return None
    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        return None
    for gap in gaps:
        if isinstance(gap, dict) and gap.get("id") == gap_id:
            return gap
    return None


def find_entry_by_surface(entries: object, surface: str) -> dict[str, object] | None:
    if not isinstance(entries, list):
        return None
    for entry in entries:
        if isinstance(entry, dict) and entry.get("surface") == surface:
            return entry
    return None


def validate_perf_baseline_manifest(manifest: object) -> list[str]:
    missing: list[str] = []
    if not isinstance(manifest, dict):
        return ["perf_manifest:dict"]
    if manifest.get("lane_key") != "P4-L20":
        missing.append("perf_manifest:lane_key")

    surveyed_gates = manifest.get("surveyed_gates")
    if not isinstance(surveyed_gates, list):
        missing.append("perf_manifest:surveyed_gates")
    else:
        for surface, expected in PERF_BASELINE_SURVEYED_GATE_EXPECTATIONS.items():
            gate = find_entry_by_surface(surveyed_gates, surface)
            if gate is None:
                missing.append(f"perf_manifest:surveyed_gate:{surface}")
                continue
            for field, value in expected.items():
                if gate.get(field) != value:
                    missing.append(f"perf_manifest:surveyed_gate:{surface}:{field}")

    pending_plans = manifest.get("pending_threshold_plans")
    if not isinstance(pending_plans, list):
        missing.append("perf_manifest:pending_threshold_plans")
    else:
        for surface, expected in PERF_BASELINE_PENDING_PLAN_EXPECTATIONS.items():
            plan = find_entry_by_surface(pending_plans, surface)
            if plan is None:
                missing.append(f"perf_manifest:pending_plan:{surface}")
                continue
            for field in (
                "gate_owner",
                "gate_rollback_owner",
                "threshold_posture",
                "current_correctness_replay",
                "benchmark_command",
                "acceptable_limit",
                "status",
            ):
                if plan.get(field) != expected[field]:
                    missing.append(f"perf_manifest:pending_plan:{surface}:{field}")
            for field in ("threshold_ready_surface", "next_threshold_step", "why_not_approved_yet"):
                value = plan.get(field)
                if not isinstance(value, str) or expected[field] not in value:
                    missing.append(f"perf_manifest:pending_plan:{surface}:{field}")
            benchmark_route = expected.get("benchmark_route")
            if isinstance(benchmark_route, str):
                for field in ("next_threshold_step", "why_not_approved_yet"):
                    value = plan.get(field)
                    if not isinstance(value, str) or benchmark_route not in value:
                        missing.append(
                            f"perf_manifest:pending_plan:{surface}:{field}:benchmark_route"
                        )

    return missing


def validate_root(root: Path) -> list[str]:
    missing = [f"file:{p}" for p in REQUIRED_FILES if not (root / p).exists()]
    artifact_diff_note = read_text(root, "Documentation/zigux/artifact-diff.md")
    makefile = read_text(root, "zigux/Makefile")
    workflow = read_text(root, ".github/workflows/zigux-bootstrap.yml")
    matrix = read_text(root, "Documentation/zigux/phase4-validation-matrix.md")
    docs_readme = read_text(root, "Documentation/zigux/README.md")
    scripts_readme = read_text(root, "scripts/zigux/README.md")
    tests_readme = read_text(root, "zigux/tests/README.md")
    gate_evidence = read_text(root, "Documentation/zigux/phase4-gate-evidence.md")
    build = read_text(root, "zigux/tests/phase4_build.zig")
    kprobe_survey = read_text(root, "zigux/tests/phase4_kprobe_example_survey.zig")
    kprobe_manifest = read_json(root, "zigux/tests/phase4_kprobe_example_manifest.json")
    perf_manifest = read_json(root, "zigux/tests/phase4_perf_baseline_manifest.json")
    fsmount_manifest = read_json(root, "zigux/tests/phase4_test_fsmount_manifest.json")
    runtime_manifest = read_json(root, "zigux/tests/phase4_runtime_atomic64_diff_manifest.json")

    for line in MAKE_LINES:
        if makefile.splitlines().count(line) != 1:
            missing.append(f"make:{line}")

    missing.extend(missing_text(workflow, "workflow", ["Validate Phase 4 diff gates", "Run Phase 4 diff tests"]))
    missing.extend(missing_text(artifact_diff_note, "artifact_diff_note", ARTIFACT_DIFF_NOTE_MARKERS))
    missing.extend(missing_text(build, "build", BUILD_MARKERS))
    missing.extend(missing_text(matrix, "matrix", MATRIX_MARKERS))
    missing.extend(missing_text(matrix, "matrix_bitmap", BITMAP_MATRIX_MARKERS))
    missing.extend(missing_text(docs_readme, "docs_readme", README_MARKERS))
    missing.extend(missing_text(docs_readme, "docs_readme_atomic64", ATOMIC64_DOCS_README_MARKERS))
    missing.extend(missing_text(scripts_readme, "scripts_readme", README_MARKERS[:-1]))
    missing.extend(missing_text(scripts_readme, "scripts_readme_atomic64", ATOMIC64_SCRIPTS_README_MARKERS))
    missing.extend(
        exact_count_mismatches(
            scripts_readme,
            "scripts_readme_bitmap_exact",
            SCRIPTS_README_BITMAP_ROUTE_MARKERS,
        )
    )
    missing.extend(missing_text(tests_readme, "tests_readme", TESTS_README_MARKERS))
    missing.extend(missing_text(gate_evidence, "gate_evidence_atomic64", ATOMIC64_GATE_EVIDENCE_MARKERS))
    missing.extend(missing_text(gate_evidence, "gate_evidence_bitmap", BITMAP_GATE_EVIDENCE_MARKERS))
    missing.extend(missing_text(gate_evidence, "gate_evidence_status", GATE_EVIDENCE_STATUS_MARKERS))
    missing.extend(
        exact_count_mismatches(
            gate_evidence,
            "gate_evidence_workflow_status_exact",
            EXACT_GATE_EVIDENCE_WORKFLOW_ROUTE_STATUS_MARKERS,
        )
    )
    if GATE_EVIDENCE_TARGET_COUNT_STATUS_LINE not in gate_evidence:
        missing.append(f"gate_evidence_status:{GATE_EVIDENCE_TARGET_COUNT_STATUS_LINE}")
    missing.extend(
        exact_count_mismatches(
            gate_evidence,
            "gate_evidence_status_exact",
            [GATE_EVIDENCE_TARGET_COUNT_STATUS_LINE],
        )
    )
    missing.extend(
        missing_text(
            gate_evidence,
            "gate_evidence_workflow_route_note",
            GATE_EVIDENCE_WORKFLOW_ROUTE_NOTE_MARKERS,
        )
    )
    missing.extend(
        exact_count_mismatches(
            gate_evidence,
            "gate_evidence_workflow_route_note_exact",
            GATE_EVIDENCE_WORKFLOW_ROUTE_NOTE_MARKERS,
        )
    )
    missing.extend(
        missing_text(
            kprobe_survey,
            "kprobe_survey",
            [
                "phase4_kprobe_example_manifest.json",
                "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
                "phase4-kprobe-example-survey-tests",
                "samples/zigux/kprobe_example.zig",
                "shared validator now fails closed on the kprobe survey packet itself",
            ],
        )
    )

    if not isinstance(kprobe_manifest, dict) or kprobe_manifest.get("shared_build_replay") != "phase4-kprobe-example-survey-tests":
        missing.append("kprobe_manifest:shared_build_replay")
    if kprobe_manifest.get("threshold_posture") != "c_anchor_only_until_kprobe_example_starter_lands":
        missing.append("kprobe_manifest:threshold_posture")
    missing.extend(validate_perf_baseline_manifest(perf_manifest))
    if not isinstance(fsmount_manifest, dict) or fsmount_manifest.get("anchor") != "samples/vfs/test-fsmount.c":
        missing.append("fsmount_manifest:anchor")
    if not isinstance(runtime_manifest, dict) or runtime_manifest.get("anchor") != "lib/atomic64_test.c":
        missing.append("runtime_manifest:anchor")

    runtime_matrix_note_gap = find_gap_by_id(runtime_manifest, "phase4-validation-matrix-note")
    if runtime_matrix_note_gap is None:
        missing.append("runtime_manifest:phase4-validation-matrix-note")
    else:
        if runtime_matrix_note_gap.get("status") != "starter_landed":
            missing.append("runtime_manifest:phase4-validation-matrix-note-status")
        if runtime_matrix_note_gap.get("zigux_destination") != "Documentation/zigux/phase4-validation-matrix.md":
            missing.append("runtime_manifest:phase4-validation-matrix-note-destination")
        why_now = runtime_matrix_note_gap.get("why_now")
        if not isinstance(why_now, str):
            missing.append("runtime_manifest:phase4-validation-matrix-note-why-now")
        else:
            missing.extend(
                missing_text(
                    why_now,
                    "runtime_manifest_matrix_note",
                    RUNTIME_ATOMIC64_MATRIX_NOTE_MARKERS,
                )
            )

    if 'obj-$(CONFIG_SAMPLE_KPROBES) += kprobe_example.o' not in read_text(root, "samples/kprobes/Makefile"):
        missing.append("kprobe_anchor:makefile")
    if 'static char symbol[KSYM_NAME_LEN] = "kernel_clone";' not in read_text(root, "samples/kprobes/kprobe_example.c"):
        missing.append("kprobe_anchor:symbol")

    if "shared validator now fails closed on the kprobe survey packet itself" not in gate_evidence:
        missing.append("gate_evidence:kprobe_note")
    for marker, rel in GATE_EVIDENCE_TARGETS.items():
        expected = blob_sha((root / rel).read_bytes())
        if f"{marker}={expected}" not in gate_evidence:
            missing.append(f"gate_evidence:{marker}:{expected}")

    return missing


def write_fixture_tree(root: Path) -> None:
    files = {
        "scripts/zigux/artifact_diff.py": "print('ARTIFACT_DIFF_SELF_TEST=pass')\n",
        "scripts/zigux/check-artifact-diff-contract.py": "# ok\n",
        "scripts/zigux/check-phase4-gate-evidence.py": "# ok\n",
        "scripts/zigux/check-phase4-kprobe-example-packet.py": "# ok\n",
        "scripts/zigux/check-phase4-workflow-route-counts.py": "# ok\n",
        "scripts/zigux/validate-phase4.py": "# placeholder\n",
        "Documentation/zigux/artifact-diff.md": "\n".join(
            ["Current Phase 4 use", *ARTIFACT_DIFF_NOTE_MARKERS]
        )
        + "\n",
        "Documentation/zigux/phase4-validation-matrix.md": "\n".join(MATRIX_MARKERS + BITMAP_MATRIX_MARKERS) + "\n",
        "Documentation/zigux/README.md": "\n".join(README_MARKERS + ATOMIC64_DOCS_README_MARKERS) + "\n",
        "scripts/zigux/README.md": "\n".join(
            README_MARKERS[:-1]
            + ATOMIC64_SCRIPTS_README_MARKERS
            + SCRIPTS_README_BITMAP_ROUTE_MARKERS
        )
        + "\n",
        "zigux/tests/README.md": "\n".join(TESTS_README_MARKERS) + "\n",
        "zigux/Makefile": "\n".join(MAKE_LINES) + "\n",
        ".github/workflows/zigux-bootstrap.yml": "Validate Phase 4 diff gates\nRun Phase 4 diff tests\n",
        "samples/kprobes/Makefile": "obj-$(CONFIG_SAMPLE_KPROBES) += kprobe_example.o\n",
        "samples/kprobes/kprobe_example.c": 'static char symbol[KSYM_NAME_LEN] = "kernel_clone";\n',
        "samples/vfs/Makefile": "userprogs-always-y += test-fsmount\n",
        "samples/vfs/test-fsmount.c": "test-fsmount\n",
        "zigux/tests/atomic64_diff.zig": "atomic64\n",
        "zigux/tests/runtime_atomic64_diff.zig": "runtime atomic64 diff gate keeps post-selftest replay explicit\n",
        "zigux/tests/phase4_runtime_atomic64_diff_manifest.json": json.dumps(
            {
                "anchor": "lib/atomic64_test.c",
                "gaps": [
                    {
                        "id": "phase4-validation-matrix-note",
                        "status": "starter_landed",
                        "zigux_destination": "Documentation/zigux/phase4-validation-matrix.md",
                        "why_now": "The validation matrix already names the reversible-delivery evidence that keeps the current `lib/atomic64_test.c` anchor plus the shared `phase4_build.zig` entrypoint explicit.",
                    }
                ],
            }
        ),
        "zigux/tests/phase4_runtime_atomic64_diff_survey.zig": "phase4-runtime-atomic64-diff-survey-tests\n",
        "zigux/tests/phase4_kprobe_example_manifest.json": json.dumps({"shared_build_replay": "phase4-kprobe-example-survey-tests", "threshold_posture": "c_anchor_only_until_kprobe_example_starter_lands"}),
        "zigux/tests/phase4_kprobe_example_survey.zig": "\n".join([
            "phase4_kprobe_example_manifest.json",
            "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
            "phase4-kprobe-example-survey-tests",
            "samples/zigux/kprobe_example.zig",
            "shared validator now fails closed on the kprobe survey packet itself",
        ]) + "\n",
        "zigux/tests/phase4_test_fsmount_manifest.json": json.dumps({"anchor": "samples/vfs/test-fsmount.c"}),
        "zigux/tests/phase4_test_fsmount_survey.zig": "phase4-test-fsmount-survey-tests\n",
        "zigux/tests/phase4_perf_baseline_manifest.json": json.dumps(
            {
                "lane_key": "P4-L20",
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
                "pending_threshold_plans": [
                    {
                        "surface": "zigux/tests/atomic64_diff.zig",
                        "gate_owner": "ABI and Runtime Team",
                        "gate_rollback_owner": "ABI and Runtime Team",
                        "threshold_posture": "threshold_pending_until_runtime_atomic64_scope_widens",
                        "current_correctness_replay": "make -C zigux phase4-runtime-atomic64-diff",
                        "threshold_ready_surface": "zigux/tests/runtime_atomic64_diff.zig keeps the post-selftest replay explicit for the current rollback gate",
                        "benchmark_command": "unapproved_until_runtime_atomic64_scope_widens",
                        "acceptable_limit": "unapproved_until_runtime_atomic64_scope_widens",
                        "next_threshold_step": "ABI and Runtime Team needs one broader atomic64 benchmark entrypoint beyond the current isolated replay before approving one benchmark command and one acceptable limit.",
                        "status": "pending_scope_widening",
                        "why_not_approved_yet": "The live atomic64 gate is still a bounded rollback-readiness slice, and zigux/tests/runtime_atomic64_diff.zig now keeps the post-selftest replay explicit.",
                    },
                    {
                        "surface": "zigux/tests/bitmap_diff.zig",
                        "gate_owner": "Shared Subsystems Pod",
                        "gate_rollback_owner": "Shared Subsystems Pod",
                        "threshold_posture": "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
                        "current_correctness_replay": "make -C zigux phase4-bitmap-diff",
                        "threshold_ready_surface": "zigux/tests/bitmap_diff.zig exposes runThresholdReplay() as the deterministic bitmap threshold batch for future perf-baseline work",
                        "benchmark_command": "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
                        "acceptable_limit": "unapproved_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
                        "next_threshold_step": "Shared Subsystems Pod now has one isolated bitmap benchmark route at `zig build phase4-bitmap-bench --build-file zigux/tests/phase4_build.zig`, and next needs to approve one benchmark command and one acceptable limit for that isolated bitmap benchmark route.",
                        "status": "pending_bounded_benchmark",
                        "why_not_approved_yet": "The live bitmap gate still carries a bounded correctness-first rollback packet, and zigux/tests/bitmap_diff.zig now keeps one deterministic threshold replay batch ready for the new isolated `zig build phase4-bitmap-bench --build-file zigux/tests/phase4_build.zig` route, but no benchmark command or acceptable limit is approved for that route yet.",
                    },
                ],
            }
        ),
        "zigux/tests/phase4_perf_baseline_survey.zig": "phase4-perf-baseline-survey-tests\n",
        "zigux/tests/bitmap_diff.zig": "bitmap\n",
        "zigux/tests/phase4_build.zig": "\n".join(BUILD_MARKERS) + "\n",
    }
    for rel, content in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    evidence = [
        "PHASE4_EVIDENCE_MODE=github_connector_readback",
        "PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions",
        *BITMAP_GATE_EVIDENCE_MARKERS,
        "shared validator now fails closed on the kprobe survey packet itself",
        "make -C zigux phase4-runtime-atomic64-diff",
        "phase4-runtime-atomic64-diff-tests",
        "phase4-runtime-atomic64-diff-survey-tests",
        "runtime_atomic64_diff.zig` remains the single replay body",
        *GATE_EVIDENCE_STATUS_MARKERS,
        GATE_EVIDENCE_TARGET_COUNT_STATUS_LINE,
        "`PHASE4_GATE_EVIDENCE_TARGET_COUNT=18` continues to describe the narrower gate-evidence-checker-enforced blob target set, which now includes the dedicated workflow-route checker file itself.",
    ]
    for marker, rel in GATE_EVIDENCE_TARGETS.items():
        evidence.append(f"{marker}={blob_sha((root / rel).read_bytes())}")
    (root / "Documentation/zigux/phase4-gate-evidence.md").write_text("\n".join(evidence) + "\n", encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_") as tmp:
        root = Path(tmp)
        write_fixture_tree(root)
        assert not validate_root(root), validate_root(root)

        survey = root / "zigux/tests/phase4_kprobe_example_survey.zig"
        survey.write_text(survey.read_text(encoding="utf-8").replace("phase4-kprobe-example-survey-tests\n", ""), encoding="utf-8")
        missing = validate_root(root)
        assert "kprobe_survey:phase4-kprobe-example-survey-tests" in missing, missing

        write_fixture_tree(root)
        docs_readme = root / "Documentation/zigux/README.md"
        docs_readme.write_text(
            docs_readme.read_text(encoding="utf-8").replace("make -C zigux phase4-runtime-atomic64-diff\n", "", 1),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert "docs_readme_atomic64:make -C zigux phase4-runtime-atomic64-diff" in missing, missing

        write_fixture_tree(root)
        scripts_readme = root / "scripts/zigux/README.md"
        scripts_readme.write_text(
            scripts_readme.read_text(encoding="utf-8").replace(
                "make -C zigux phase4-bitmap-diff\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "scripts_readme_bitmap_exact:make -C zigux phase4-bitmap-diff:0"
            in missing
        ), missing

        write_fixture_tree(root)
        runtime_manifest = root / "zigux/tests/phase4_runtime_atomic64_diff_manifest.json"
        runtime_manifest.write_text(
            runtime_manifest.read_text(encoding="utf-8").replace(
                "shared `phase4_build.zig` entrypoint",
                "shared entrypoint",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "runtime_manifest_matrix_note:shared `phase4_build.zig` entrypoint"
            in missing
        ), missing

        write_fixture_tree(root)
        matrix = root / "Documentation/zigux/phase4-validation-matrix.md"
        matrix.write_text(
            matrix.read_text(encoding="utf-8").replace(
                "zero-nbits helper calls as explicit no-op rollback checks\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "matrix_bitmap:zero-nbits helper calls as explicit no-op rollback checks"
            in missing
        ), missing

        write_fixture_tree(root)
        makefile = root / "zigux/Makefile"
        makefile.write_text(
            makefile.read_text(encoding="utf-8").replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "make:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test"
            in missing
        ), missing

        write_fixture_tree(root)
        makefile = root / "zigux/Makefile"
        makefile.write_text(
            makefile.read_text(encoding="utf-8").replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "make:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py"
            in missing
        ), missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "the refreshed bitmap row still treats the 115-bit fill as resolved parity rather than an open survey-only mismatch\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "gate_evidence_bitmap:the refreshed bitmap row still treats the 115-bit fill as resolved parity rather than an open survey-only mismatch"
            in missing
        ), missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                f"{BITMAP_BENCH_ROUTE}\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            f"gate_evidence_bitmap:{BITMAP_BENCH_ROUTE}" in missing
        ), missing

        write_fixture_tree(root)
        artifact_diff_note = root / "Documentation/zigux/artifact-diff.md"
        artifact_diff_note.write_text(
            artifact_diff_note.read_text(encoding="utf-8").replace(
                "ARTIFACT_DIFF_CONTRACT_CASE_COUNT=27\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "artifact_diff_note:ARTIFACT_DIFF_CONTRACT_CASE_COUNT=27" in missing
        ), missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "runtime_atomic64_diff.zig` remains the single replay body\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "gate_evidence_atomic64:runtime_atomic64_diff.zig` remains the single replay body"
            in missing
        ), missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        old = "PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=" + blob_sha((root / "scripts/zigux/check-phase4-gate-evidence.py").read_bytes())
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(old, "PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=deadbeef", 1),
            encoding="utf-8",
        )
        missing = validate_root(root)
        expected = "gate_evidence:PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA:" + blob_sha((root / "scripts/zigux/check-phase4-gate-evidence.py").read_bytes())
        assert expected in missing, missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        old = "PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=" + blob_sha((root / "scripts/zigux/check-phase4-workflow-route-counts.py").read_bytes())
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(old, "PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=deadbeef", 1),
            encoding="utf-8",
        )
        missing = validate_root(root)
        expected = "gate_evidence:PHASE4_WORKFLOW_ROUTE_CHECKER_BLOB_SHA:" + blob_sha((root / "scripts/zigux/check-phase4-workflow-route-counts.py").read_bytes())
        assert expected in missing, missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "PHASE4_TESTS_README_BLOB_SHA=",
                "PHASE4_TESTS_README_BLOB_MISSING=",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert "gate_evidence:PHASE4_TESTS_README_BLOB_SHA:" in " ".join(missing), missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA=",
                "PHASE4_PERF_BASELINE_MANIFEST_BLOB_MISSING=",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert "gate_evidence:PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA:" in " ".join(missing), missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT=5\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "gate_evidence_workflow_status_exact:PHASE4_WORKFLOW_ROUTE_COUNTS_REQUIRED_FILE_COUNT=5:0"
            in missing
        ), missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "PHASE4_WORKFLOW_ROUTE_COUNTS=pass\n",
                "PHASE4_WORKFLOW_ROUTE_COUNTS=pass\nPHASE4_WORKFLOW_ROUTE_COUNTS=pass\n",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "gate_evidence_workflow_status_exact:PHASE4_WORKFLOW_ROUTE_COUNTS=pass:2"
            in missing
        ), missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "PHASE4_GATE_EVIDENCE_TARGET_COUNT=18\n",
                "",
                1,
            ).replace(
                "- `PHASE4_GATE_EVIDENCE_TARGET_COUNT=18`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert "gate_evidence_status:- `PHASE4_GATE_EVIDENCE_TARGET_COUNT=18`" in missing, missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "- `PHASE4_GATE_EVIDENCE_TARGET_COUNT=18`\n",
                "- `PHASE4_GATE_EVIDENCE_TARGET_COUNT=18`\n- `PHASE4_GATE_EVIDENCE_TARGET_COUNT=18`\n",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "gate_evidence_status_exact:- `PHASE4_GATE_EVIDENCE_TARGET_COUNT=18`:2"
            in missing
        ), missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "the dedicated workflow-route checker file itself",
                "the dedicated workflow-route checker file itself and again the dedicated workflow-route checker file itself",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "gate_evidence_workflow_route_note_exact:the dedicated workflow-route checker file itself:2"
            in missing
        ), missing

        write_fixture_tree(root)
        gate_evidence = root / "Documentation/zigux/phase4-gate-evidence.md"
        gate_evidence.write_text(
            gate_evidence.read_text(encoding="utf-8").replace(
                "the dedicated workflow-route checker file itself",
                "the dedicated workflow checker artifact",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "gate_evidence_workflow_route_note:the dedicated workflow-route checker file itself"
            in missing
        ), missing

        write_fixture_tree(root)
        perf_manifest = root / "zigux/tests/phase4_perf_baseline_manifest.json"
        perf_manifest.write_text(
            perf_manifest.read_text(encoding="utf-8").replace(
                "post-selftest replay explicit for the current rollback gate",
                "rollback gate summary",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "perf_manifest:pending_plan:zigux/tests/atomic64_diff.zig:threshold_ready_surface"
            in missing
        ), missing

        write_fixture_tree(root)
        perf_manifest = root / "zigux/tests/phase4_perf_baseline_manifest.json"
        perf_manifest.write_text(
            perf_manifest.read_text(encoding="utf-8").replace(
                BITMAP_BENCH_ROUTE,
                "zig build phase4-bitmap-bench --build-file zigux/tests/phase4_placeholder.zig",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "perf_manifest:pending_plan:zigux/tests/bitmap_diff.zig:next_threshold_step:benchmark_route"
            in missing
        ), missing

        write_fixture_tree(root)
        perf_manifest = root / "zigux/tests/phase4_perf_baseline_manifest.json"
        perf_manifest.write_text(
            perf_manifest.read_text(encoding="utf-8").replace(
                BITMAP_BENCH_ROUTE,
                "zig build phase4-bitmap-bench --build-file zigux/tests/phase4_placeholder.zig",
                2,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "perf_manifest:pending_plan:zigux/tests/bitmap_diff.zig:why_not_approved_yet:benchmark_route"
            in missing
        ), missing

        write_fixture_tree(root)
        perf_manifest = root / "zigux/tests/phase4_perf_baseline_manifest.json"
        perf_manifest.write_text(
            perf_manifest.read_text(encoding="utf-8").replace(
                "threshold_pending_until_runtime_atomic64_scope_widens",
                "threshold_pending_until_runtime_atomic64_shift",
                1,
            ),
            encoding="utf-8",
        )
        missing = validate_root(root)
        assert (
            "perf_manifest:surveyed_gate:zigux/tests/atomic64_diff.zig:threshold_posture"
            in missing
        ), missing

    print("PHASE4_VALIDATOR_SELF_TEST=pass")
    return 0


def required_marker_count() -> int:
    return (
        len(MAKE_LINES)
        + len(BUILD_MARKERS)
        + len(MATRIX_MARKERS)
        + len(BITMAP_MATRIX_MARKERS)
        + len(README_MARKERS)
        + len(ATOMIC64_DOCS_README_MARKERS)
        + len(README_MARKERS[:-1])
        + len(ATOMIC64_SCRIPTS_README_MARKERS)
        + len(SCRIPTS_README_BITMAP_ROUTE_MARKERS)
        + len(TESTS_README_MARKERS)
        + len(GATE_EVIDENCE_TARGETS)
        + len(ATOMIC64_GATE_EVIDENCE_MARKERS)
        + len(BITMAP_GATE_EVIDENCE_MARKERS)
        + len(ARTIFACT_DIFF_NOTE_MARKERS)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Phase 4 diff bundle.")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()

    missing = validate_root(ROOT)
    if missing:
        print("PHASE4_VALIDATION=fail")
        print("MISSING_PHASE4_MARKERS_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE4_MARKERS_END")
        return 1

    print("PHASE4_VALIDATION=pass")
    print(f"PHASE4_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE4_REQUIRED_MARKER_COUNT={required_marker_count()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
