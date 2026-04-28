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
if manifest.get("surveyed_commit") != "b9ee21faa08430c19e03f5628009a9c35b0cfe5c":
    missing.append(f'manifest:surveyed_commit={manifest.get("surveyed_commit")}')

shared_smoke_surfaces = manifest.get("shared_smoke_surfaces")
if not isinstance(shared_smoke_surfaces, list):
    missing.append("manifest:shared_smoke_surfaces")
else:
    for required_surface in [
        "scripts/zigux/validate-phase14.py",
        "scripts/zigux/README.md",
        "zigux/tests/phase14_end_to_end_smoke_manifest.json",
        "zigux/tests/phase14_end_to_end_smoke_survey.zig",
        "zigux/tests/phase14_build.zig",
        "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
        "Documentation/zigux/review-checklist.md",
        "Documentation/zigux/freeze-map.md",
    ]:
        if required_surface not in shared_smoke_surfaces:
            missing.append(f"manifest:shared_smoke_surface:{required_surface}")

anchor_packets = manifest.get("anchor_packets")
if not isinstance(anchor_packets, list) or len(anchor_packets) != 4:
    missing.append("manifest:anchor_packets")
else:
    for (lane_key, anchor), packet in zip(EXPECTED_ANCHOR_LANES, anchor_packets):
        if not isinstance(packet, dict):
            missing.append(f"manifest:anchor_packet:{lane_key}")
            continue
        if packet.get("lane_key") != lane_key:
            missing.append(f'manifest:{lane_key}:lane_key={packet.get("lane_key")}')
        if packet.get("anchor") != anchor:
            missing.append(f'manifest:{lane_key}:anchor={packet.get("anchor")}')

smoke_note_text = text("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
if isinstance(anchor_packets, list):
    for packet in anchor_packets:
        if isinstance(packet, dict):
            lane_key = packet.get("lane_key")
            if isinstance(lane_key, str) and lane_key not in smoke_note_text:
                missing.append(f"smoke_note:lane_key:{lane_key}")

smoke_commands = manifest.get("smoke_commands")
expected_smoke_commands = [
    "make -C zigux phase14-validate",
    "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
    "make -C zigux phase14",
]
if smoke_commands != expected_smoke_commands:
    missing.append("manifest:smoke_commands")

smoke_shard_commands = manifest.get("smoke_shard_commands")
expected_smoke_shard_commands = [
    "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all",
    "make -C zigux phase14-smoke",
]
if smoke_shard_commands != expected_smoke_shard_commands:
    missing.append("manifest:smoke_shard_commands")

compile_shards = manifest.get("compile_shards")
if compile_shards != EXPECTED_COMPILE_SHARDS:
    missing.append("manifest:compile_shards")
elif isinstance(compile_shards, list):
    focused_shard_count = sum(
        1
        for shard in compile_shards
        if isinstance(shard, dict) and shard.get("coverage_mode") == "focused_and_full_bundle"
    )
    full_bundle_only_count = sum(
        1
        for shard in compile_shards
        if isinstance(shard, dict) and shard.get("coverage_mode") == "full_bundle_only"
    )
    dedicated_step_count = sum(
        1
        for shard in compile_shards
        if isinstance(shard, dict) and bool(shard.get("dedicated_step"))
    )
    if len(compile_shards) != 5:
        missing.append(f"manifest:compile_artifact_count={len(compile_shards)}")
    if focused_shard_count != 1:
        missing.append(f"manifest:focused_shard_count={focused_shard_count}")
    if full_bundle_only_count != 4:
        missing.append(f"manifest:full_bundle_only_artifact_count={full_bundle_only_count}")
    if dedicated_step_count != focused_shard_count:
        missing.append(f"manifest:dedicated_step_count={dedicated_step_count}")
    if f"PHASE14_COMPILE_ARTIFACT_COUNT={len(compile_shards)}" not in smoke_note_text:
        missing.append("smoke_note:compile_artifact_count")
    if f"PHASE14_FOCUSED_SHARD_COUNT={focused_shard_count}" not in smoke_note_text:
        missing.append("smoke_note:focused_shard_count")
    if f"PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT={full_bundle_only_count}" not in smoke_note_text:
        missing.append("smoke_note:full_bundle_only_artifact_count")
    if "only the shared smoke survey has a dedicated shard today" not in smoke_note_text:
        missing.append("smoke_note:focused_shard_boundary")
    if "four anchor-local artifacts still replay only through the broader `test` bundle" not in smoke_note_text:
        missing.append("smoke_note:full_bundle_boundary")

summary = manifest.get("survey_summary")
if not isinstance(summary, dict):
    missing.append("manifest:survey_summary")
else:
    for key in [
        "phase14_validate_script_present",
        "phase14_validate_entrypoint_present",
        "phase14_build_has_shared_smoke_step",
        "phase14_build_has_smoke_shard_step",
        "phase14_make_target_present",
        "phase14_make_smoke_target_present",
        "workflow_runs_phase14_validate",
        "workflow_runs_phase14_build",
        "workflow_runs_phase14_smoke_shard",
        "review_checklist_has_phase14_smoke_prompt",
        "review_checklist_has_productization_prompt",
        "smoke_note_records_owner_and_rollback",
        "smoke_note_records_transfer_rationale",
        "freeze_map_lists_workqueue_c",
        "freeze_map_lists_skbuff_c",
        "freeze_map_lists_ring_buffer_c",
        "freeze_map_lists_tree_c",
    ]:
        if summary.get(key) is not True:
            missing.append(f"manifest:survey_summary:{key}={summary.get(key)}")

build_text = text("zigux/tests/phase14_build.zig")
build_names = BUILD_TEST_NAME_RE.findall(build_text)
if build_names != EXPECTED_BUILD_TEST_NAMES:
    missing.append("build:test_names")
depend_steps = BUILD_DEPEND_STEP_RE.findall(build_text)
if len(depend_steps) != 5:
    missing.append(f"build:depend_step_count={len(depend_steps)}")
for shard in EXPECTED_COMPILE_SHARDS:
    artifact_name = shard["artifact_name"]
    root_source_file = shard["root_source_file"]
    bridge_import = shard["bridge_import"]
    bridge_source_file = shard["bridge_source_file"]
    if artifact_name not in build_text:
        missing.append(f"build:compile_shard:artifact_name:{artifact_name}")
    if root_source_file not in build_text:
        missing.append(f"build:compile_shard:root_source_file:{root_source_file}")
    if bridge_import and bridge_import not in build_text:
        missing.append(f"build:compile_shard:bridge_import:{bridge_import}")
    if bridge_source_file and bridge_source_file not in build_text:
        missing.append(f"build:compile_shard:bridge_source_file:{bridge_source_file}")
if build_text.count('b.step("phase14-smoke"') != 1:
    missing.append("build:focused_smoke_step")
if build_text.count('b.step("test"') != 1:
    missing.append("build:test_bundle_step")
if build_text.count('phase14-smoke", "Run Phase 14 shared smoke survey only') != 1:
    missing.append("build:focused_smoke_step_label")

for manifest_path, lane_key, anchor in [
    ("zigux/tests/phase14_workqueue_bridge_manifest.json", "P14-L01", "kernel/workqueue.c"),
    ("zigux/tests/phase14_skbuff_bridge_manifest.json", "P14-L11", "net/core/skbuff.c"),
    ("zigux/tests/phase14_ring_buffer_manifest.json", "P14-L06", "kernel/trace/ring_buffer.c"),
    ("zigux/tests/phase14_rcu_tree_manifest.json", "P14-L14", "kernel/rcu/tree.c"),
]:
    anchor_manifest = load_json(manifest_path)
    if anchor_manifest.get("phase") != "Phase 14":
        missing.append(f"{manifest_path}:phase")
    if anchor_manifest.get("lane_key") != lane_key:
        missing.append(f"{manifest_path}:lane_key")
    if anchor_manifest.get("anchor") != anchor:
        missing.append(f"{manifest_path}:anchor")
    if isinstance(anchor_packets, list):
        matching_shared_packet = next(
            (
                packet
                for packet in anchor_packets
                if isinstance(packet, dict) and packet.get("manifest_path") == manifest_path
            ),
            None,
        )
        if isinstance(matching_shared_packet, dict) and matching_shared_packet.get("surveyed_commit") != anchor_manifest.get("surveyed_commit"):
            missing.append(f"{manifest_path}:surveyed_commit")
        if isinstance(matching_shared_packet, dict):
            ready_next_gap = matching_shared_packet.get("ready_next_gap")
            if isinstance(ready_next_gap, str) and ready_next_gap:
                if not any(
                    isinstance(gap, dict)
                    and gap.get("id") == ready_next_gap
                    and gap.get("status") == "ready_next"
                    for gap in anchor_manifest.get("gaps", [])
                    if isinstance(anchor_manifest.get("gaps"), list)
                ):
                    missing.append(f"{manifest_path}:ready_next_gap")

if missing:
    print("PHASE14_VALIDATION=fail")
    print("PHASE14_VALIDATION_MISSING_START")
    for item in missing:
        print(item)
    print("PHASE14_VALIDATION_MISSING_END")
    sys.exit(1)

print("PHASE14_VALIDATION=pass")
print(f"PHASE14_REQUIRED_FILE_COUNT={len(FILES)}")
print(
    "PHASE14_REQUIRED_MARKER_COUNT="
    f"{len(MAKE_MARKERS) + len(WORKFLOW_MARKERS) + len(SCRIPT_README_MARKERS) + len(RELEASE_MARKERS) + len(CHECKLIST_MARKERS) + len(BUILD_MARKERS)}"
)
print(f"PHASE14_BUILD_TEST_COUNT={len(build_names)}")
print(f"PHASE14_BUILD_DEPEND_STEP_COUNT={len(depend_steps)}")
