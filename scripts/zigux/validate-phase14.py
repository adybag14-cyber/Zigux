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
BUILD_SMOKE_DEPEND_STEP_RE = re.compile(r"phase14_smoke_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")

FILES = [
    "scripts/zigux/validate-phase14.py",
    "scripts/zigux/check-phase14-docs-root-smoke-summary.py",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "Documentation/zigux/phase14-release-boundary-survey.md",
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
    "zigux/tests/phase14_rcu_tree_survey.zig",
    "zigux/tests/phase14_workqueue_bridge_manifest.json",
    "zigux/tests/phase14_skbuff_bridge_manifest.json",
    "zigux/tests/phase14_ring_buffer_manifest.json",
    "zigux/tests/phase14_rcu_tree_manifest.json",
]

MAKE_MARKERS = [
    "PHONY += phase14-validate phase14-smoke phase14-test phase14",
    "phase14-validate:",
    "scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test",
    "scripts/zigux/check-phase14-docs-root-smoke-summary.py",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
    "scripts/zigux/validate-phase14.py",
    "phase14-smoke:",
    "$(ZIG) build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all",
    "phase14-test:",
    "$(ZIG) build test --build-file zigux/tests/phase14_build.zig --summary all",
    "phase14: phase14-validate phase14-test",
]

MAKE_EXACT_COUNT_MARKERS = [
    "PHONY += phase14-validate phase14-smoke phase14-test phase14",
    "phase14-validate:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py",
    "phase14-smoke:",
    "cd $(ZIGUX_ROOT) && $(ZIG) build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all",
    "phase14-test:",
    "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase14_build.zig --summary all",
    "phase14: phase14-validate phase14-test",
]

WORKFLOW_MARKERS = [
    "Validate Phase 14 shared smoke packet",
    "make -C zigux phase14-validate",
    "Run Phase 14 smoke shard",
    "make -C zigux phase14-smoke",
    "Run Phase 14 internal bridge tests",
    "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
]

SCRIPT_README_MARKERS = [
    "Current bootstrap helpers",
    "`validate-phase14.py`",
    "Phase 14 flow",
    "`Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
    "`Documentation/zigux/phase14-release-boundary-survey.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/freeze-map.md`",
    "`zigux/tests/phase14_end_to_end_smoke_manifest.json`",
    "`make -C zigux phase14-validate`",
    "`make -C zigux phase14-smoke`",
    "`zigux/tests/phase14_build.zig`",
    "shared Phase 14 smoke packet",
    "focused smoke-shard replay contract",
    "stay-in-C boundary",
    "roadmap risk bundle",
    "hidden runtime behavior",
    "memory-ordering mistakes",
    "overpromising full parity",
    "deep-core scope creep",
    "rollback threshold",
    "fallback path",
    "automatic return-to-blocked trigger catalog",
    "four-anchor boundary map",
    "bounded concurrency-audit scope",
    "`make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>`",
    "`make -C zigux phase14-smoke ZIG=<attached-zig-path>`",
    "`make -C zigux phase14-test ZIG=<attached-zig-path>`",
    "`make -C zigux phase14 ZIG=<attached-zig-path>`",
    "when `zig` is not on `PATH`",
]

DOCS_ROOT_EXACT_LINE_MARKERS = [
    "- `Documentation/zigux/phase14-release-boundary-survey.md` and `Documentation/zigux/phase14-end-to-end-smoke-survey.md` now make the roadmap's core-adjacent sequencing step explicit from the docs root, so release-facing review no longer jumps directly from the active Phase 13 helper tranche to the Phase 15 governance packet.",
    "- the current Phase 14 release reading is intentionally boundary-only: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay in study-only posture, while `kernel/rcu/tree.c` and `net/core/skbuff.c` remain blocked under the Phase 15 freeze-in-C governance packet rather than being treated as an active release lane.",
    "- `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_rcu_tree_survey.zig`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `make -C zigux phase14`, and `zigux/tests/phase14_build.zig` now provide one validator-backed shared smoke gate for that study-only four-anchor packet; it stays a reviewability lane rather than a closure or active subsystem delivery claim.",
]

SCRIPT_README_EXACT_LINE_MARKERS = [
    "- `check-phase14-docs-root-smoke-summary.py`",
    "- `check-phase14-docs-root-smoke-summary.py --self-test` and `check-phase14-docs-root-smoke-summary.py` keep the docs-root Phase 14 smoke summary and the shared smoke survey fail-closed around the same validator-backed `phase14-validate`, focused `phase14-smoke`, and study-only reviewability wording before the broader shared validator runs.",
    "- `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, and `zigux/tests/phase14_end_to_end_smoke_survey.zig` keep the exact rollback threshold, automatic return-to-blocked trigger list, and ZAR-to-product transfer rationale visible from the docs root rather than relying on run memory.",
    "- attached-toolchain fallback commands stay explicit in the scripts index too: `make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>`, `make -C zigux phase14-smoke ZIG=<attached-zig-path>`, `make -C zigux phase14-test ZIG=<attached-zig-path>`, and `make -C zigux phase14 ZIG=<attached-zig-path>`.",
]

RELEASE_MARKERS = [
    "PHASE14_STATUS=active",
    "PHASE14_SLICE=end-to-end-smoke-verification",
    "PHASE14_SHARED_LANE=P14-L01",
    "PHASE14_SMOKE_VALIDATOR=present",
    "PHASE14_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase14.py",
    "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate",
    "PHASE14_BUILD_ENTRYPOINT=zig build test --build-file zigux/tests/phase14_build.zig --summary all",
    "PHASE14_COMBINED_ENTRYPOINT=make -C zigux phase14",
    "PHASE14_ANCHOR_PACKET_COUNT=4",
    "PHASE14_COMPILE_ARTIFACT_COUNT=5",
    "PHASE14_FOCUSED_SHARD_COUNT=1",
    "PHASE14_ANCHOR_LOCAL_STEP_COUNT=0",
    "PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT=4",
    "PHASE14_FULL_BUNDLE_DEPENDENCY_COUNT=5",
    "PHASE14_FOCUSED_SHARD_DEPENDENCY_COUNT=1",
    "PHASE14_FOCUSED_SHARD_ONLY_ARTIFACT=phase14-end-to-end-smoke-tests",
    "PHASE14_STAY_IN_C_BOUNDARY=explicit",
    "PHASE14_REVIEW_BLOCKER_STATUS=blocked_on_stay_in_c_evidence",
    "PHASE14_STATUS_CHANGE_CLAIM=no",
    "PHASE14_BOUNDARY_MAP=shared-anchor-packet-bundle",
    "PHASE14_CONCURRENCY_AUDIT_SCOPE=anchor-local-packets-only",
    "PHASE14_ATTACHED_TOOLCHAIN_FALLBACK=ZIG=<attached-zig-path>",
    "scripts/zigux/validate-phase14.py",
    "scripts/zigux/check-phase14-docs-root-smoke-summary.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "phase14_workqueue_bridge_manifest.json",
    "phase14_skbuff_bridge_manifest.json",
    "phase14_ring_buffer_manifest.json",
    "phase14_rcu_tree_manifest.json",
]

RELEASE_BOUNDARY_MARKERS = [
    "PHASE14_RELEASE_BOUNDARY=present",
    "PHASE14_SHARED_REPLAY_PRESENT=yes",
    "PHASE14_RELEASE_CLOSED=no",
    "shared smoke packet: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` now keep the four-anchor boundary map, the focused smoke shard, and the shared full-bundle replay explicit from a study-only posture",
    "compile-shard matrix: one focused `phase14-smoke` shard still covers only `phase14-end-to-end-smoke-tests`, while `phase14-workqueue-bridge-tests`, `phase14-skbuff-bridge-tests`, `phase14-ring-buffer-survey-tests`, and `phase14-rcu-tree-survey-tests` remain `full_bundle_only` under `zig build test --build-file zigux/tests/phase14_build.zig --summary all`",
    "combined shared replay entrypoint: `make -C zigux phase14` remains the published convenience route for the validator-backed smoke packet, so release-facing review and local replay still name the same one-command path as the shared smoke note and manifest instead of leaving that wrapper path implicit in `zigux/Makefile`",
    "PHASE14_SHARED_SMOKE_GATE_COUNT=1",
    "PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0",
    "Keep this lane parked unless the shared smoke packet or one of the four anchor-local Phase 14 manifests moves. If that happens, refresh this release-boundary reading and the docs-root Phase 14 summary so the release-facing story keeps matching the validator-backed smoke packet without widening it into a new active delivery claim.",
]

RELEASE_BOUNDARY_EXACT_COUNT_MARKERS = RELEASE_BOUNDARY_MARKERS

CHECKLIST_MARKERS = [
    "is there a stated rollback owner and fallback path?",
    "if the change touches the shared Phase 14 smoke packet, do `scripts/zigux/validate-phase14.py`, `scripts/zigux/README.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_build.zig`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, and the four Phase 14 anchor-local manifests plus survey notes still agree on the same exact validator-backed smoke commands, the same focused `phase14-smoke` shard commands, ready-next versus blocked posture, stay-in-C boundary, named owner, validation gate, rollback owner, rollback threshold, automatic return-to-blocked trigger catalog, roadmap risk bundle (`hidden runtime behavior`, `memory-ordering mistakes`, `overpromising full parity`, `deep-core scope creep`), and explicit ZAR-to-product transfer rationale?",
    "if the change touches the shared Phase 14 smoke packet, do the same shared smoke note, scripts index, and manifest-backed survey summary still keep the current four-anchor boundary map and bounded concurrency-audit scope explicit instead of leaving that roadmap evidence implicit behind the anchor list?",
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
SHARED_ROLLBACK_THRESHOLD_KEYS = {
    "status_bucket": "study_only",
    "review_blocker_status": "blocked_on_stay_in_c_evidence",
    "owner": "Core-Adjacent Pod",
    "rollback_owner": "Repo Tooling Pod",
}
RCU_TREE_ROLLBACK_THRESHOLD_KEYS = {
    "status_bucket": "freeze_in_c",
    "review_blocker_status": "blocked_on_stay_in_c_evidence",
    "owner": "Core-Adjacent Pod",
    "rollback_owner": "Repo Tooling Pod",
}
RCU_TREE_ROLLBACK_GUARDRAIL_GAP = "phase14-rcu-tree-rollback-threshold-guardrail"


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path: str, missing: list[str]) -> dict[str, object] | None:
    try:
        return json.loads(text(path))
    except json.JSONDecodeError as exc:
        missing.append(f"json_decode_error:{path}:{exc.lineno}:{exc.colno}")
        return None


def find_gap(manifest: dict[str, object], gap_id: str) -> dict[str, object] | None:
    for gap in manifest.get("gaps", []):
        if isinstance(gap, dict) and gap.get("id") == gap_id:
            return gap
    return None


def expect_marker(source_name: str, source_text: str, marker: str, missing: list[str]) -> None:
    if marker not in source_text:
        missing.append(f"{source_name}:{marker}")


def expect_exact_count(
    source_name: str,
    source_text: str,
    marker: str,
    expected_count: int,
    missing: list[str],
) -> None:
    actual_count = source_text.count(marker)
    if actual_count != expected_count:
        missing.append(f"{source_name}:count={actual_count}:{marker}")


def expect_exact_line_count(
    source_name: str,
    source_text: str,
    marker: str,
    expected_count: int,
    missing: list[str],
) -> None:
    actual_count = sum(1 for line in source_text.splitlines() if line.strip() == marker)
    if actual_count != expected_count:
        missing.append(f"{source_name}:line_count={actual_count}:{marker}")


missing_files = [path for path in FILES if not (ROOT / path).exists()]
if missing_files:
    print("PHASE14_VALIDATION=fail")
    print("MISSING_PHASE14_FILES_START")
    for path in missing_files:
        print(path)
    print("MISSING_PHASE14_FILES_END")
    sys.exit(1)

missing: list[str] = []
docs_root_text = text("Documentation/zigux/README.md")
scripts_readme_text = text("scripts/zigux/README.md")
survey_note = text("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
release_boundary_text = text("Documentation/zigux/phase14-release-boundary-survey.md")
make_text = text("zigux/Makefile")

for name, source, markers in [
    ("scripts_readme", scripts_readme_text, SCRIPT_README_MARKERS),
    ("workflow", text(".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS),
    ("survey", survey_note, RELEASE_MARKERS),
    ("release_boundary", release_boundary_text, RELEASE_BOUNDARY_MARKERS),
    ("checklist", text("Documentation/zigux/review-checklist.md"), CHECKLIST_MARKERS),
    ("build", text("zigux/tests/phase14_build.zig"), BUILD_MARKERS),
]:
    for marker in markers:
        expect_marker(name, source, marker, missing)

for marker in DOCS_ROOT_EXACT_LINE_MARKERS:
    expect_exact_line_count("docs_root", docs_root_text, marker, 1, missing)

for marker in SCRIPT_README_EXACT_LINE_MARKERS:
    expect_exact_line_count("scripts_readme", scripts_readme_text, marker, 1, missing)

for marker in MAKE_EXACT_COUNT_MARKERS:
    expect_exact_line_count("make", make_text, marker, 1, missing)

for marker in RELEASE_BOUNDARY_EXACT_COUNT_MARKERS:
    expect_exact_count("release_boundary", release_boundary_text, marker, 1, missing)

freeze_map_text = text("Documentation/zigux/freeze-map.md")
for marker in FREEZE_MAP_MARKERS:
    expect_marker("freeze_map", freeze_map_text, marker, missing)

manifest = load_json("zigux/tests/phase14_end_to_end_smoke_manifest.json", missing)
if not isinstance(manifest, dict):
    manifest = {}
    missing.append("manifest:unreadable")
if manifest.get("lane_key") != "P14-L01":
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

rollback_threshold = manifest.get("rollback_threshold")
if not isinstance(rollback_threshold, dict):
    missing.append("manifest:rollback_threshold")
    rollback_threshold = {}
else:
    for key, value in SHARED_ROLLBACK_THRESHOLD_KEYS.items():
        if rollback_threshold.get(key) != value:
            missing.append(f"manifest:rollback_threshold:{key}={rollback_threshold.get(key)}")
    fallback_path = rollback_threshold.get("fallback_path")
    if not isinstance(fallback_path, str) or "source of truth" not in fallback_path:
        missing.append("manifest:rollback_threshold:fallback_path")
    required_evidence = rollback_threshold.get("required_evidence")
    if not isinstance(required_evidence, list) or len(required_evidence) != 3:
        missing.append("manifest:rollback_threshold:required_evidence")
    else:
        for item in required_evidence:
            if not isinstance(item, str) or item not in survey_note:
                missing.append(f"survey:rollback_required_evidence:{item}")
    rollback_triggers = rollback_threshold.get("rollback_triggers")
    if not isinstance(rollback_triggers, list) or len(rollback_triggers) != 4:
        missing.append("manifest:rollback_threshold:rollback_triggers")
    else:
        for item in rollback_triggers:
            if not isinstance(item, str) or item not in survey_note:
                missing.append(f"survey:rollback_trigger:{item}")

shared_smoke_surfaces = manifest.get("shared_smoke_surfaces")
if not isinstance(shared_smoke_surfaces, list) or len(shared_smoke_surfaces) != 15:
    missing.append("manifest:shared_smoke_surfaces")

smoke_commands = manifest.get("smoke_commands")
if not isinstance(smoke_commands, list) or len(smoke_commands) != 3:
    missing.append("manifest:smoke_commands")

smoke_shard_commands = manifest.get("smoke_shard_commands")
if not isinstance(smoke_shard_commands, list) or len(smoke_shard_commands) != 2:
    missing.append("manifest:smoke_shard_commands")

attached_toolchain_commands = manifest.get("attached_toolchain_commands")
if not isinstance(attached_toolchain_commands, list) or len(attached_toolchain_commands) != 4:
    missing.append("manifest:attached_toolchain_commands")
    attached_toolchain_commands = []

survey_summary = manifest.get("survey_summary")
required_summary_keys = [
    "phase14_validate_script_present",
    "phase14_validate_entrypoint_present",
    "phase14_build_has_shared_smoke_step",
    "phase14_build_has_smoke_shard_step",
    "phase14_build_full_bundle_routes_all_compile_artifacts",
    "phase14_build_smoke_shard_routes_only_smoke_survey",
    "phase14_make_target_present",
    "phase14_make_smoke_target_present",
    "workflow_runs_phase14_validate",
    "workflow_runs_phase14_build",
    "workflow_runs_phase14_smoke_shard",
    "workflow_runs_phase14_smoke_wrapper",
    "review_checklist_has_phase14_smoke_prompt",
    "review_checklist_has_productization_prompt",
    "review_checklist_has_risk_bundle_prompt",
    "review_checklist_has_rollback_threshold_prompt",
    "review_checklist_has_fallback_path_prompt",
    "review_checklist_has_return_to_blocked_trigger_prompt",
    "review_checklist_has_boundary_map_prompt",
    "review_checklist_has_concurrency_audit_prompt",
    "smoke_note_records_owner_and_rollback",
    "smoke_note_records_risk_bundle",
    "smoke_note_records_review_blocker_status",
    "smoke_note_records_rollback_threshold",
    "smoke_note_records_fallback_path",
    "smoke_note_records_return_to_blocked_triggers",
    "smoke_note_records_transfer_rationale",
    "smoke_note_records_boundary_map",
    "smoke_note_records_concurrency_audit_scope",
    "scripts_readme_records_rollback_threshold",
    "scripts_readme_records_fallback_path",
    "scripts_readme_records_return_to_blocked_triggers",
    "scripts_readme_records_boundary_map",
    "scripts_readme_records_concurrency_audit_scope",
    "release_boundary_note_records_shared_smoke_packet",
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
actual_smoke_depend_steps = BUILD_SMOKE_DEPEND_STEP_RE.findall(build_text)
expected_build_test_names: list[str] = []
focused_shard_count = 0
full_bundle_only_count = 0
anchor_local_step_count = 0

if isinstance(smoke_commands, list):
    for command in smoke_commands:
        if isinstance(command, str) and command and command not in survey_note:
            missing.append(f"survey:smoke_command:{command}")

if isinstance(smoke_shard_commands, list):
    for command in smoke_shard_commands:
        if isinstance(command, str) and command and command not in survey_note:
            missing.append(f"survey:smoke_shard_command:{command}")

for command in attached_toolchain_commands:
    if isinstance(command, str) and command:
        if command not in survey_note:
            missing.append(f"survey:attached_toolchain_command:{command}")
        if command not in scripts_readme_text:
            missing.append(f"scripts_readme:attached_toolchain_command:{command}")

if "`make -C zigux phase14-test ZIG=<attached-zig-path>`" in survey_note:
    if "`make -C zigux phase14-test ZIG=<attached-zig-path>`" not in scripts_readme_text:
        missing.append("scripts_readme:phase14_test_attached_toolchain_command")

for index, shard in enumerate(compile_shards):
    if not isinstance(shard, dict):
        missing.append(f"manifest:compile_shards:{index}:shape")
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
    if dedicated_step and artifact_name != "phase14-end-to-end-smoke-tests":
        anchor_local_step_count += 1
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

    if bridge_import:
        if bridge_import not in build_text:
            missing.append(f"phase14_build:bridge_import:{bridge_import}")
        if bridge_source_file not in build_text:
            missing.append(f"phase14_build:bridge_source_file:{bridge_source_file}")

if surveyed_commit and surveyed_commit not in survey_note:
    missing.append("survey:surveyed_commit")
expected_provenance_line = f"- survey provenance captured against verified `master` head `{surveyed_commit}`"
if expected_provenance_line not in survey_note:
    missing.append("survey:provenance_line")
expected_verified_head_line = f"- verified `master` head: `{surveyed_commit}`"
if expected_verified_head_line not in survey_note:
    missing.append("survey:verified_master_head_line")
expected_manifest_commit_line = f"- shared smoke manifest surveyed commit: `{surveyed_commit}`"
if expected_manifest_commit_line not in survey_note:
    missing.append("survey:shared_manifest_commit_line")
for key, value in PRODUCTIZATION_KEYS.items():
    if value not in survey_note:
        missing.append(f"survey:productization:{key}")
if "ZAR runtime research" not in survey_note:
    missing.append("survey:transfer_rationale")
review_blocker_status = rollback_threshold.get("review_blocker_status")
if isinstance(review_blocker_status, str):
    expected_review_blocker_marker = f"PHASE14_REVIEW_BLOCKER_STATUS={review_blocker_status}"
    if expected_review_blocker_marker not in survey_note:
        missing.append("survey:review_blocker_status")
    if review_blocker_status not in survey_note:
        missing.append("survey:review_blocker_status_productization")

expected_compile_count_marker = f"PHASE14_COMPILE_ARTIFACT_COUNT={len(expected_build_test_names)}"
expected_focused_count_marker = f"PHASE14_FOCUSED_SHARD_COUNT={focused_shard_count}"
expected_anchor_local_step_count_marker = f"PHASE14_ANCHOR_LOCAL_STEP_COUNT={anchor_local_step_count}"
expected_full_bundle_count_marker = f"PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT={full_bundle_only_count}"
for marker in [
    expected_compile_count_marker,
    expected_focused_count_marker,
    expected_anchor_local_step_count_marker,
    expected_full_bundle_count_marker,
]:
    if marker not in survey_note:
        missing.append(f"survey:{marker}")

if actual_build_test_names != expected_build_test_names:
    missing.append("phase14_build:build_test_names_mismatch")
if len(actual_depend_steps) != len(expected_build_test_names):
    missing.append("phase14_build:depend_step_count_mismatch")
expected_run_symbols = [
    "run_phase14_workqueue_bridge_tests",
    "run_phase14_skbuff_bridge_tests",
    "run_phase14_ring_buffer_survey_tests",
    "run_phase14_rcu_tree_survey_tests",
    "run_phase14_end_to_end_smoke_tests",
]
if actual_depend_steps != expected_run_symbols:
    missing.append("phase14_build:full_bundle_route_mismatch")
if actual_smoke_depend_steps != ["run_phase14_end_to_end_smoke_tests"]:
    missing.append("phase14_build:smoke_route_mismatch")
if focused_shard_count != 1:
    missing.append(f"manifest:focused_shard_count={focused_shard_count}")
if anchor_local_step_count != 0:
    missing.append(f"manifest:anchor_local_step_count={anchor_local_step_count}")
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
    anchor_manifest = load_json(manifest_path, missing)
    if not isinstance(anchor_manifest, dict):
        missing.append(f"{manifest_path}:unreadable")
        anchor_manifest = {}
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
    if manifest_path == "zigux/tests/phase14_rcu_tree_manifest.json":
        rollback_threshold = anchor_manifest.get("rollback_threshold")
        if not isinstance(rollback_threshold, dict):
            missing.append(f"{manifest_path}:rollback_threshold")
        else:
            for key, value in RCU_TREE_ROLLBACK_THRESHOLD_KEYS.items():
                if rollback_threshold.get(key) != value:
                    missing.append(f"{manifest_path}:rollback_threshold:{key}={rollback_threshold.get(key)}")
            required_evidence = rollback_threshold.get("required_evidence")
            if not isinstance(required_evidence, list) or len(required_evidence) != 3:
                missing.append(f"{manifest_path}:rollback_threshold:required_evidence")
            else:
                for item in required_evidence:
                    if not isinstance(item, str) or item not in anchor_survey_note:
                        missing.append(f"{survey_note_path}:rollback_required_evidence:{item}")
            rollback_triggers = rollback_threshold.get("rollback_triggers")
            if not isinstance(rollback_triggers, list) or len(rollback_triggers) != 4:
                missing.append(f"{manifest_path}:rollback_threshold:rollback_triggers")
            else:
                for item in rollback_triggers:
                    if not isinstance(item, str) or item not in anchor_survey_note:
                        missing.append(f"{survey_note_path}:rollback_trigger:{item}")

        expected_rcu_lane_marker = f"PHASE14_LANE_KEY={lane_key}"
        if expected_rcu_lane_marker not in anchor_survey_note:
            missing.append(f"{survey_note_path}:lane_key_marker")
        expected_rcu_commit_marker = f"PHASE14_SURVEYED_COMMIT={packet_commit}"
        if expected_rcu_commit_marker not in anchor_survey_note:
            missing.append(f"{survey_note_path}:surveyed_commit_marker")
        if "PHASE14_STATUS=freeze_in_c" not in anchor_survey_note:
            missing.append(f"{survey_note_path}:status_bucket_marker")

        guardrail_gap = find_gap(anchor_manifest, RCU_TREE_ROLLBACK_GUARDRAIL_GAP)
        if not isinstance(guardrail_gap, dict) or guardrail_gap.get("status") != "starter_landed":
            missing.append(f"{manifest_path}:guardrail:{RCU_TREE_ROLLBACK_GUARDRAIL_GAP}")

if missing:
    print("PHASE14_VALIDATION=fail")
    print("MISSING_PHASE14_MARKERS_START")
    for item in missing:
        print(item)
    print("MISSING_PHASE14_MARKERS_END")
    sys.exit(1)

print("PHASE14_VALIDATION=pass")
print(f"PHASE14_REQUIRED_FILE_COUNT={len(FILES)}")
print(f"PHASE14_REQUIRED_MARKER_COUNT={len(MAKE_MARKERS) + len(WORKFLOW_MARKERS) + len(SCRIPT_README_MARKERS) + len(RELEASE_MARKERS) + len(RELEASE_BOUNDARY_MARKERS) + len(CHECKLIST_MARKERS) + len(BUILD_MARKERS)}")
print(f"PHASE14_ANCHOR_PACKET_COUNT={len(anchor_packets)}")
print(f"PHASE14_BUILD_TEST_COUNT={len(expected_build_test_names)}")
print(f"PHASE14_BUILD_DEPEND_STEP_COUNT={len(actual_depend_steps)}")
print(f"PHASE14_COMPILE_ARTIFACT_COUNT={len(expected_build_test_names)}")
print(f"PHASE14_FOCUSED_SHARD_COUNT={focused_shard_count}")
print(f"PHASE14_ANCHOR_LOCAL_STEP_COUNT={anchor_local_step_count}")
print(f"PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT={full_bundle_only_count}")
print(f"PHASE14_DOCS_ROOT_EXACT_LINE_MARKER_COUNT={len(DOCS_ROOT_EXACT_LINE_MARKERS)}")
print(f"PHASE14_SCRIPTS_README_EXACT_LINE_MARKER_COUNT={len(SCRIPT_README_EXACT_LINE_MARKERS)}")
print(f"PHASE14_MAKE_EXACT_COUNT_MARKER_COUNT={len(MAKE_EXACT_COUNT_MARKERS)}")
