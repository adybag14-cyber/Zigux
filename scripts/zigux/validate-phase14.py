#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
BUILD_TEST_NAME_RE = re.compile(r'\.name = "(phase14-[^"]+)"')
BUILD_DEPEND_STEP_RE = re.compile(r"test_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")

FILES = [
    "scripts/zigux/validate-phase14.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "Documentation/zigux/phase14-workqueue-bridge-survey.md",
    "Documentation/zigux/phase14-skbuff-bridge-survey.md",
    "Documentation/zigux/phase14-ring-buffer-survey.md",
    "Documentation/zigux/phase14-rcu-tree-survey.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/freeze-map.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase14_build.zig",
    "zigux/tests/phase14_end_to_end_smoke_manifest.json",
    "zigux/tests/phase14_end_to_end_smoke_survey.zig",
    "zigux/tests/phase14_workqueue_bridge_manifest.json",
    "zigux/tests/phase14_skbuff_bridge_manifest.json",
    "zigux/tests/phase14_ring_buffer_manifest.json",
    "zigux/tests/phase14_rcu_tree_manifest.json",
]

MAKE_MARKERS = [
    "PHONY += phase14-validate phase14-smoke phase14-test phase14",
    "phase14-validate:",
    "scripts/zigux/validate-phase14.py",
    "phase14-smoke:",
    "$(ZIG) build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all",
    "phase14-test:",
    "$(ZIG) build test --build-file zigux/tests/phase14_build.zig --summary all",
    "phase14: phase14-validate phase14-test",
]

WORKFLOW_MARKERS = [
    "Validate Phase 14 shared smoke packet",
    "make -C zigux phase14-validate",
    "Run Phase 14 smoke shard",
    "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all",
    "Run Phase 14 internal bridge tests",
    "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
]

SCRIPT_README_MARKERS = [
    "Current bootstrap helpers",
    "`validate-phase14.py`",
    "Phase 14 flow",
    "`Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/freeze-map.md`",
    "`make -C zigux phase14-validate`",
    "`make -C zigux phase14-smoke`",
    "`zigux/tests/phase14_build.zig`",
    "shared Phase 14 smoke packet",
    "focused smoke-shard replay contract",
    "stay-in-C boundary",
]

RELEASE_MARKERS = [
    "PHASE14_STATUS=active",
    "PHASE14_SLICE=end-to-end-smoke-verification",
    "PHASE14_SMOKE_VALIDATOR=present",
    "PHASE14_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase14.py",
    "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate",
    "PHASE14_BUILD_ENTRYPOINT=zig build test --build-file zigux/tests/phase14_build.zig --summary all",
    "PHASE14_COMBINED_ENTRYPOINT=make -C zigux phase14",
    "PHASE14_ANCHOR_PACKET_COUNT=4",
    "PHASE14_COMPILE_ARTIFACT_COUNT=5",
    "PHASE14_FOCUSED_SHARD_COUNT=1",
    "PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT=4",
    "PHASE14_STAY_IN_C_BOUNDARY=explicit",
    "PHASE14_STATUS_CHANGE_CLAIM=no",
    "scripts/zigux/validate-phase14.py",
    "scripts/zigux/README.md",
    "phase14_workqueue_bridge_manifest.json",
    "phase14_skbuff_bridge_manifest.json",
    "phase14_ring_buffer_manifest.json",
    "phase14_rcu_tree_manifest.json",
]

CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 14 smoke packet, do `scripts/zigux/validate-phase14.py`, `scripts/zigux/README.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_build.zig`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, and the four Phase 14 anchor-local manifests plus survey notes still agree on the same exact validator-backed smoke commands, the same focused `phase14-smoke` shard commands, ready-next versus blocked posture, stay-in-C boundary, named owner, validation gate, rollback owner, and explicit ZAR-to-product transfer rationale?",
]

BUILD_MARKERS = [
    "phase14-workqueue-bridge-tests",
    "phase14-skbuff-bridge-tests",
    "phase14-ring-buffer-survey-tests",
    "phase14-rcu-tree-survey-tests",
    "phase14-end-to-end-smoke-tests",
    "test_step.dependOn(&run_phase14_workqueue_bridge_tests.step);",
    "test_step.dependOn(&run_phase14_skbuff_bridge_tests.step);",
    "test_step.dependOn(&run_phase14_ring_buffer_survey_tests.step);",
    "test_step.dependOn(&run_phase14_rcu_tree_survey_tests.step);",
    "test_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);",
]

EXPECTED_BUILD_TEST_NAMES = [
    "phase14-workqueue-bridge-tests",
    "phase14-skbuff-bridge-tests",
    "phase14-ring-buffer-survey-tests",
    "phase14-rcu-tree-survey-tests",
    "phase14-end-to-end-smoke-tests",
]

EXPECTED_ANCHOR_LANES = [
    ("P14-L01", "kernel/workqueue.c"),
    ("P14-L11", "net/core/skbuff.c"),
    ("P14-L06", "kernel/trace/ring_buffer.c"),
    ("P14-L14", "kernel/rcu/tree.c"),
]

EXPECTED_COMPILE_SHARDS = [
    {
        "artifact_name": "phase14-workqueue-bridge-tests",
        "root_source_file": "phase14_workqueue_bridge.zig",
        "coverage_mode": "full_bundle_only",
        "dedicated_step": "",
        "bridge_import": "workqueue_bridge",
        "bridge_source_file": "../../kernel/workqueue_bridge.zig",
    },
    {
        "artifact_name": "phase14-skbuff-bridge-tests",
        "root_source_file": "phase14_skbuff_bridge.zig",
        "coverage_mode": "full_bundle_only",
        "dedicated_step": "",
        "bridge_import": "skbuff_bridge",
        "bridge_source_file": "../../net/core/skbuff_bridge.zig",
    },
    {
        "artifact_name": "phase14-ring-buffer-survey-tests",
        "root_source_file": "phase14_ring_buffer_survey.zig",
        "coverage_mode": "full_bundle_only",
        "dedicated_step": "",
        "bridge_import": "",
        "bridge_source_file": "",
    },
    {
        "artifact_name": "phase14-rcu-tree-survey-tests",
        "root_source_file": "phase14_rcu_tree_survey.zig",
        "coverage_mode": "full_bundle_only",
        "dedicated_step": "",
        "bridge_import": "",
        "bridge_source_file": "",
    },
    {
        "artifact_name": "phase14-end-to-end-smoke-tests",
        "root_source_file": "phase14_end_to_end_smoke_survey.zig",
        "coverage_mode": "focused_and_full_bundle",
        "dedicated_step": "phase14-smoke",
        "bridge_import": "",
        "bridge_source_file": "",
    },
]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path: str) -> dict[str, object]:
    return json.loads(text(path))


missing_files = [path for path in FILES if not (ROOT / path).exists()]
if missing_files:
    print("PHASE14_VALIDATION=fail")
    print("MISSING_PHASE14_FILES_START")
    for path in missing_files:
        print(path)
    print("MISSING_PHASE14_FILES_END")
    sys.exit(1)

missing: list[str] = []
for name, source, markers in [
    ("scripts_readme", text("scripts/zigux/README.md"), SCRIPT_README_MARKERS),
    ("make", text("zigux/Makefile"), MAKE_MARKERS),
    ("workflow", text(".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS),
    ("survey", text("Documentation/zigux/phase14-end-to-end-smoke-survey.md"), RELEASE_MARKERS),
    ("checklist", text("Documentation/zigux/review-checklist.md"), CHECKLIST_MARKERS),
    ("build", text("zigux/tests/phase14_build.zig"), BUILD_MARKERS),
]:
    for marker in markers:
        if marker not in source:
            missing.append(f"{name}:{marker}")

freeze_map_text = text("Documentation/zigux/freeze-map.md")
for marker in [
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
    "net/core/skbuff.c",
    "kernel/rcu/tree.c",
    "Architecture Council",
]:
    if marker not in freeze_map_text:
        missing.append(f"freeze_map:{marker}")

manifest = load_json("zigux/tests/phase14_end_to_end_smoke_manifest.json")
if manifest.get("lane_key") != "P14-L03":
    missing.append(f'manifest:lane_key={manifest.get("lane_key")}')
if manifest.get("phase") != "Phase 14":
    missing.append(f'manifest:phase={manifest.get("phase")}')
if manifest.get("surveyed_commit") != "fde3ff965b744814385845a4d1fa85b1a52c69a9":
    missing.append(f'manifest:surveyed_commit={manifest.get("surveyed_commit")}')
