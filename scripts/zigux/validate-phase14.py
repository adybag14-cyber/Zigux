#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
HEX40 = re.compile(r"^[0-9a-f]{40}$")
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

FREEZE_MAP_MARKERS = [
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
    "net/core/skbuff.c",
    "kernel/rcu/tree.c",
    "Architecture Council",
]

ALLOWED_COVERAGE_MODES = {"full_bundle_only", "focused_and_full_bundle"}
PRODUCTIZATION_KEYS = {
    "owner": "Core-Adjacent Pod",
    "status_bucket": "study_only",
    "validation_gate": "zig build test --build-file zigux/tests/phase14_build.zig --summary all && make -C zigux phase14",
    "rollback_owner": "Repo Tooling Pod",
}


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path: str) -> dict[str, object]:
    return json.loads(text(path))


def find_gap(manifest: dict[str, object], gap_id: str) -> dict[str, object] | None:
    for gap in manifest.get("gaps", []):
        if isinstance(gap, dict) and gap.get("id") == gap_id:
            return gap
    return None


def expect_marker(source_name: str, source_text: str, marker: str, missing: list[str]) -> None:
    if marker not in source_text:
        missing.append(f"{source_name}:{marker}")


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
        expect_marker(name, source, marker, missing)

freeze_map_text = text("Documentation/zigux/freeze-map.md")
for marker in FREEZE_MAP_MARKERS:
    expect_marker("freeze_map", freeze_map_text, marker, missing)

manifest = load_json("zigux/tests/phase14_end_to_end_smoke_manifest.json")
if manifest.get("lane_key") != "P14-L03":
    missing.append(f'manifest:lane_key={manifest.get("lane_key")}')
if manifest.get("phase") != "Phase 14":
    missing.append(f'manifest:phase={manifest.get("phase")}')
surveyed_commit = str(manifest.get("surveyed_commit", ""))
if not HEX40.fullmatch(surveyed_commit):
    missing.append("manifest:surveyed_commit")

productization = manifest.get("productization")
if not isinstance(productization, dict):
    missing.append("manifest:productization")
else:
    for key, value in PRODUCTIZATION_KEYS.items():
        if productization.get(key) != value:
            missing.append(f"manifest:productization:{key}={productization.get(key)}")
    transfer_rationale = productization.get("transfer_rationale")
    if not isinstance(transfer_rationale, str) or "ZAR runtime research" not in transfer_rationale:
        missing.append("manifest:productization:transfer_rationale")

shared_smoke_surfaces = manifest.get("shared_smoke_surfaces")
if not isinstance(shared_smoke_surfaces, list) or len(shared_smoke_surfaces) != 10:
    missing.append("manifest:shared_smoke_surfaces")

smoke_commands = manifest.get("smoke_commands")
if not isinstance(smoke_commands, list) or len(smoke_commands) != 3:
    missing.append("manifest:smoke_commands")

smoke_shard_commands = manifest.get("smoke_shard_commands")
if not isinstance(smoke_shard_commands, list) or len(smoke_shard_commands) != 2:
    missing.append("manifest:smoke_shard_commands")

survey_summary = manifest.get("survey_summary")
required_summary_keys = [
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
]
if not isinstance(survey_summary, dict):
    missing.append("manifest:survey_summary")
else:
    for key in required_summary_keys:
        if survey_summary.get(key) is not True:
            missing.append(f"manifest:survey_summary:{key}")

compile_shards = manifest.get("compile_shards")
if not isinstance(compile_shards, list) or len(compile_shards) != 5:
    missing.append("manifest:compile_shards")
    compile_shards = []

anchor_packets = manifest.get("anchor_packets")
if not isinstance(anchor_packets, list) or len(anchor_packets) != 4:
    missing.append("manifest:anchor_packets")
    anchor_packets = []

build_text = text("zigux/tests/phase14_build.zig")
actual_build_test_names = BUILD_TEST_NAME_RE.findall(build_text)
actual_depend_steps = BUILD_DEPEND_STEP_RE.findall(build_text)
expected_build_test_names: list[str] = []
focused_shard_count = 0
full_bundle_only_count = 0

for index, shard in enumerate(compile_shards):
    if not isinstance(shard, dict):
        missing.append(f"manifest:compile_shards:{index}")
        continue
    artifact_name = shard.get("artifact_name")
    root_source_file = shard.get("root_source_file")
    coverage_mode = shard.get("coverage_mode")
    dedicated_step = shard.get("dedicated_step")
    bridge_import = shard.get("bridge_import")
    bridge_source_file = shard.get("bridge_source_file")
    if not all(isinstance(item, str) for item in [artifact_name, root_source_file, coverage_mode, dedicated_step, bridge_import, bridge_source_file]):
        missing.append(f"manifest:compile_shards:{index}:shape")
        continue

    expected_build_test_names.append(artifact_name)
    if coverage_mode not in ALLOWED_COVERAGE_MODES:
        missing.append(f"manifest:compile_shards:{artifact_name}:coverage_mode={coverage_mode}")
    elif coverage_mode == "focused_and_full_bundle":
        focused_shard_count += 1
        if not dedicated_step:
            missing.append(f"manifest:compile_shards:{artifact_name}:dedicated_step")
    else:
        full_bundle_only_count += 1
        if dedicated_step:
            missing.append(f"manifest:compile_shards:{artifact_name}:unexpected_dedicated_step={dedicated_step}")

    if artifact_name not in build_text:
        missing.append(f"phase14_build:artifact_name:{artifact_name}")
    if root_source_file not in build_text:
        missing.append(f"phase14_build:root_source_file:{root_source_file}")
    if isinstance(smoke_commands, list):
        for command in smoke_commands:
            if isinstance(command, str) and command and command not in text("Documentation/zigux/phase14-end-to-end-smoke-survey.md"):
                missing.append(f"survey:smoke_command:{command}")
    if isinstance(smoke_shard_commands, list):
        for command in smoke_shard_commands:
            if isinstance(command, str) and command and command not in text("Documentation/zigux/phase14-end-to-end-smoke-survey.md"):
                missing.append(f"survey:smoke_shard_command:{command}")

    if bridge_import:
        if bridge_import not in build_text:
            missing.append(f"phase14_build:bridge_import:{bridge_import}")
        if bridge_source_file not in build_text:
            missing.append(f"phase14_build:bridge_source_file:{bridge_source_file}")

survey_note = text("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
if surveyed_commit and surveyed_commit not in survey_note:
    missing.append("survey:surveyed_commit")
for key, value in PRODUCTIZATION_KEYS.items():
    if value not in survey_note:
        missing.append(f"survey:productization:{key}")
if "ZAR runtime research" not in survey_note:
    missing.append("survey:transfer_rationale")

expected_compile_count_marker = f"PHASE14_COMPILE_ARTIFACT_COUNT={len(expected_build_test_names)}"
expected_focused_count_marker = f"PHASE14_FOCUSED_SHARD_COUNT={focused_shard_count}"
expected_full_bundle_count_marker = f"PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT={full_bundle_only_count}"
for marker in [
    expected_compile_count_marker,
    expected_focused_count_marker,
    expected_full_bundle_count_marker,
]:
    if marker not in survey_note:
        missing.append(f"survey:{marker}")

if actual_build_test_names != expected_build_test_names:
    missing.append("phase14_build:build_test_names_mismatch")
if len(actual_depend_steps) != len(expected_build_test_names):
    missing.append("phase14_build:depend_step_count_mismatch")
if focused_shard_count != 1:
    missing.append(f"manifest:focused_shard_count={focused_shard_count}")
if full_bundle_only_count != len(expected_build_test_names) - focused_shard_count:
    missing.append(f"manifest:full_bundle_only_count={full_bundle_only_count}")

for index, packet in enumerate(anchor_packets):
    if not isinstance(packet, dict):
        missing.append(f"manifest:anchor_packets:{index}")
        continue
    lane_key = packet.get("lane_key")
    anchor = packet.get("anchor")
    packet_commit = packet.get("surveyed_commit")
    manifest_path = packet.get("manifest_path")
    survey_note_path = packet.get("survey_note_path")
    ready_next_gap = packet.get("ready_next_gap")
    blocked_gap = packet.get("blocked_gap")
    if not all(isinstance(item, str) for item in [lane_key, anchor, packet_commit, manifest_path, survey_note_path, ready_next_gap, blocked_gap]):
        missing.append(f"manifest:anchor_packets:{index}:shape")
        continue
    if not HEX40.fullmatch(packet_commit):
        missing.append(f"manifest:anchor_packets:{lane_key}:surveyed_commit")
    anchor_manifest = load_json(manifest_path)
    if anchor_manifest.get("lane_key") != lane_key:
        missing.append(f"{manifest_path}:lane_key")
    if anchor_manifest.get("anchor") != anchor:
        missing.append(f"{manifest_path}:anchor")
    if anchor_manifest.get("surveyed_commit") != packet_commit:
        missing.append(f"{manifest_path}:surveyed_commit")
    if ready_next_gap:
        ready_gap = find_gap(anchor_manifest, ready_next_gap)
        if not isinstance(ready_gap, dict) or ready_gap.get("status") != "ready_next":
            missing.append(f"{manifest_path}:ready_next:{ready_next_gap}")
    blocked_gap_item = find_gap(anchor_manifest, blocked_gap)
    blocked_status = blocked_gap_item.get("status") if isinstance(blocked_gap_item, dict) else None
    if not isinstance(blocked_status, str) or not blocked_status.startswith("blocked_on_"):
        missing.append(f"{manifest_path}:blocked:{blocked_gap}")

    anchor_survey_note = text(survey_note_path)
    if anchor not in anchor_survey_note:
        missing.append(f"{survey_note_path}:anchor")
    if ready_next_gap and "Next bounded step" not in anchor_survey_note:
        missing.append(f"{survey_note_path}:next_bounded_step")
    if lane_key not in survey_note:
        missing.append(f"survey:anchor_lane_key:{lane_key}")
    if packet_commit not in survey_note:
        missing.append(f"survey:anchor_commit:{lane_key}")

if missing:
    print("PHASE14_VALIDATION=fail")
    print("MISSING_PHASE14_MARKERS_START")
    for item in missing:
        print(item)
    print("MISSING_PHASE14_MARKERS_END")
    sys.exit(1)

print("PHASE14_VALIDATION=pass")
print(f"PHASE14_REQUIRED_FILE_COUNT={len(FILES)}")
print(f"PHASE14_REQUIRED_MARKER_COUNT={len(MAKE_MARKERS) + len(WORKFLOW_MARKERS) + len(SCRIPT_README_MARKERS) + len(RELEASE_MARKERS) + len(CHECKLIST_MARKERS) + len(BUILD_MARKERS)}")
print(f"PHASE14_ANCHOR_PACKET_COUNT={len(anchor_packets)}")
print(f"PHASE14_BUILD_TEST_COUNT={len(expected_build_test_names)}")
print(f"PHASE14_BUILD_DEPEND_STEP_COUNT={len(actual_depend_steps)}")
print(f"PHASE14_COMPILE_ARTIFACT_COUNT={len(expected_build_test_names)}")
print(f"PHASE14_FOCUSED_SHARD_COUNT={focused_shard_count}")
print(f"PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT={full_bundle_only_count}")
