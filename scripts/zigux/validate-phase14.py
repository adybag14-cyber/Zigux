#!/usr/bin/env python3
"""PHASE14_VALIDATE_PACKET=shared_smoke

Fail-closed validator for the shared Phase 14 smoke packet.
This packet is a study-only validation, smoke, and full-bundle replay surface on master.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

MARKER = "PHASE14_VALIDATE_PACKET=shared_smoke"
DOCS_ROOT_CHECKER_MARKER = "PHASE14_CHECK_PACKET=docs_root_smoke_summary"
CHECKER_MARKER = "PHASE14_CHECK_PACKET=rollback_threshold_sequencing"
RELEASE_BOUNDARY_CHECKER_MARKER = "PHASE14_CHECK_PACKET=release_boundary_exact_counts"
EXPECTED_LANE_KEY = "P14-L07"
TRACEABILITY_PATH = "Documentation/zigux/phase14-core-boundary-traceability.md"
TRACEABILITY_TITLE = "# Phase 14 Core Boundary Traceability"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
RCU_SURVEY_PATH = "Documentation/zigux/phase14-rcu-tree-survey.md"
RCU_MANIFEST_PATH = "zigux/tests/phase14_rcu_tree_manifest.json"
EXPECTED_ROADMAP_RISK_BUNDLE = [
    "hidden runtime behavior",
    "memory-ordering mistakes",
    "overpromising full parity",
    "deep-core scope creep",
]
EXPECTED_PRODUCTIZATION = {
    "named_owner": "Core-Adjacent Pod",
    "status_bucket": "study_only",
    "validation_gate": "make -C zigux phase14-validate && make -C zigux phase14-smoke && make -C zigux phase14-test && make -C zigux phase14",
    "rollback_owner": "keep the freeze-map anchors in C and reopen only with stronger evidence",
    "review_blocker_status": "blocked_on_stay_in_c_evidence",
    "transfer_rationale": "transfer ZAR runtime research into explicit reviewability evidence instead of widening Phase 14 into a deep-core port",
    "roadmap_risk_bundle": EXPECTED_ROADMAP_RISK_BUNDLE,
    "fallback_path": "Keep kernel/workqueue.c, net/core/skbuff.c, kernel/trace/ring_buffer.c, and kernel/rcu/tree.c as the source of truth and keep the shared smoke packet limited to survey-backed reviewability evidence.",
}
TRACEABILITY_MANIFEST_PATHS = [
    "zigux/tests/phase14_workqueue_bridge_manifest.json",
    "zigux/tests/phase14_ring_buffer_manifest.json",
    "zigux/tests/phase14_skbuff_bridge_manifest.json",
    RCU_MANIFEST_PATH,
]
REQUIRED_COMMANDS = [
    "make -C zigux phase14-validate",
    "make -C zigux phase14-smoke",
    "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all",
    "make -C zigux phase14-test",
    "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
    "make -C zigux phase14",
]
COMPILE_MATRIX_ROWS = [
    ("phase14-workqueue-bridge-tests", "phase14_workqueue_bridge.zig", "full_bundle_only"),
    ("phase14-skbuff-bridge-tests", "phase14_skbuff_bridge.zig", "full_bundle_only"),
    ("phase14-ring-buffer-survey-tests", "phase14_ring_buffer_survey.zig", "full_bundle_only"),
    ("phase14-rcu-tree-survey-tests", "phase14_rcu_tree_survey.zig", "full_bundle_only"),
    ("phase14-end-to-end-smoke-tests", "phase14_end_to_end_smoke_survey.zig", "focused_and_full_bundle"),
]
REQUIRED_COMPILE_SHARDS = [
    {"label": label, "root_source": root_source, "coverage": coverage}
    for label, root_source, coverage in COMPILE_MATRIX_ROWS
]
REQUIRED_SURFACES = {
    "Documentation/zigux/README.md": "Phase 14 notes",
    "Documentation/zigux/phase14-release-boundary-survey.md": "PHASE14_RELEASE_BOUNDARY=present",
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md": "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate",
    TRACEABILITY_PATH: TRACEABILITY_TITLE,
    "Documentation/zigux/freeze-map.md": "kernel/workqueue.c",
    "Documentation/zigux/review-checklist.md": "shared Phase 14 smoke packet",
    "scripts/zigux/README.md": "Phase 14 flow",
    "scripts/zigux/validate-phase14.py": MARKER,
    "scripts/zigux/check-phase14-docs-root-smoke-summary.py": DOCS_ROOT_CHECKER_MARKER,
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py": CHECKER_MARKER,
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py": RELEASE_BOUNDARY_CHECKER_MARKER,
    "zigux/tests/README.md": "keep the current Phase 14 smoke packet reviewable",
    "zigux/tests/phase14_build.zig": "phase14-smoke",
    "zigux/Makefile": "phase14: phase14-validate phase14-smoke phase14-test",
    "zigux/tests/phase14_workqueue_bridge.zig": "phase14 workqueue bridge manifest records the boundary-map foothold and remaining gap",
    "zigux/tests/phase14_skbuff_bridge.zig": "phase14 skbuff bridge manifest records the boundary-map foothold and frozen ownership gap",
    "zigux/tests/phase14_workqueue_bridge_manifest.json": "phase14-workqueue-live-execution-blocker",
    "zigux/tests/phase14_skbuff_bridge_manifest.json": "phase14-skbuff-live-ownership-blocker",
    "zigux/tests/phase14_end_to_end_smoke_survey.zig": "phase14 shared smoke survey confirms the current packet surfaces",
    "zigux/tests/phase14_end_to_end_smoke_manifest.json": "phase14_shared_smoke_packet",
    "zigux/tests/phase14_ring_buffer_manifest.json": "phase14-ring-buffer-zig-port-blocker",
    "zigux/tests/phase14_ring_buffer_survey.zig": "phase 14 ring-buffer survey manifest records the study-only gap without inventing a port",
    RCU_MANIFEST_PATH: "phase14-rcu-tree-bridge-blocker",
    "zigux/tests/phase14_rcu_tree_survey.zig": "phase 14 rcu tree survey manifest records the freeze-boundary gap without inventing a bridge",
    WORKFLOW_PATH: "Run focused Phase 14 smoke shard",
    "kernel/workqueue_bridge.zig": "pub const WorkqueueBridgeLab",
    "net/core/skbuff_bridge.zig": "pub const SkbuffBridgeLab",
    "kernel/rcu/tree_bridge.zig": "pub const RcuTreeBridgeLab",
}
EXPECTED_SURFACE_PATHS = set(REQUIRED_SURFACES)
REQUIRED_WORKFLOW_STEP_NAMES = [
    "Validate Phase 14 shared smoke packet",
    "Run focused Phase 14 smoke shard",
    "Run Phase 14 internal bridge tests",
]
WORKFLOW_WRAPPER_COUNT_MESSAGES = {
    "run: make -C zigux phase14-validate": "phase14 workflow validate wrapper count drifted from the current one-step packet",
    "run: make -C zigux phase14-smoke": "phase14 workflow smoke wrapper count drifted from the current one-step packet",
    "run: make -C zigux phase14-test": "phase14 workflow full-bundle wrapper count drifted from the current one-step packet",
}
FORBIDDEN_DIRECT_WORKFLOW_RUNS = [
    "run: python3 scripts/zigux/validate-phase14.py",
    "run: zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all",
    "run: zig build test --build-file zigux/tests/phase14_build.zig --summary all",
    "run: zig build test --build-file zigux/tests/phase14_build.zig",
]
RCU_REQUIRED_NOTE_MARKERS = [
    "- status bucket: `freeze_in_c`",
    "- blocker status: `blocked_on_stay_in_c_evidence`",
    "- rollback owner: `Repo Tooling Pod`",
    "- Architecture Council reopen record linked from the reviewable packet",
    "- parity scorecard evidence and benchmark notes attached to the same review packet",
    "- validation replay command and evidence archive path recorded beside the latest blocker disposition",
    "- any `kernel/rcu/tree_bridge.zig` claim or status review that lacks the Architecture Council reopen record",
    "- missing parity scorecard evidence, benchmark notes, or replay command in the active review packet",
    "- freeze-map, survey note, or manifest drift that drops the blocked bridge disposition or rollback owner",
]
RCU_REQUIRED_GAP_STATUSES = {
    "phase14-rcu-tree-rollback-threshold-guardrail": "starter_landed",
    "phase14-rcu-tree-bridge-blocker": "blocked_on_stay_in_c_evidence",
}

def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def load_json_file(path: Path) -> dict:
    return json.loads(read_text(path))

def blocked_gap_id(manifest: dict) -> str | None:
    for gap in manifest.get("gaps", []):
        status = str(gap.get("status", ""))
        if status.startswith("blocked"):
            gap_id = gap.get("id")
            if isinstance(gap_id, str):
                return gap_id
    return None

def ready_next_gap_id(manifest: dict) -> str | None:
    for gap in manifest.get("gaps", []):
        if gap.get("status") == "ready_next":
            gap_id = gap.get("id")
            if isinstance(gap_id, str):
                return gap_id
    return None

def gap_status(manifest: dict, gap_id: str) -> str | None:
    for gap in manifest.get("gaps", []):
        if gap.get("id") == gap_id:
            status = gap.get("status")
            if isinstance(status, str):
                return status
            return None
    return None

def compile_matrix_note_row(label: str, root_source: str, coverage: str) -> str:
    return f"- `{label}`: root `{root_source}`, coverage `{coverage}`"

def traceability_expected_markers(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    markers = [
        TRACEABILITY_TITLE,
        "- validator entrypoint: `make -C zigux phase14-validate`",
        "- convenience target: `make -C zigux phase14`",
    ]
    for manifest_rel_path in TRACEABILITY_MANIFEST_PATHS:
        manifest_path = root / manifest_rel_path
        if not manifest_path.exists():
            errors.append(f"missing file: {manifest_rel_path}")
            continue
        try:
            manifest = load_json_file(manifest_path)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid json in {manifest_rel_path}: {exc}")
            continue
        lane_key = manifest.get("lane_key")
        surveyed_commit = manifest.get("surveyed_commit")
        if not isinstance(lane_key, str):
            errors.append(f"missing lane_key in {manifest_rel_path}")
        if not isinstance(surveyed_commit, str):
            errors.append(f"missing surveyed_commit in {manifest_rel_path}")
        blocked_gap = blocked_gap_id(manifest)
        if blocked_gap is None:
            errors.append(f"missing blocked gap in {manifest_rel_path}")
        ready_next_gap = ready_next_gap_id(manifest)
        markers.append(
            f"- ready-next gap: `{ready_next_gap}`"
            if ready_next_gap is not None
            else "- ready-next gap: none currently recorded"
        )
        markers.append(f"- manifest: `{manifest_rel_path}`")
        if isinstance(lane_key, str):
            markers.append(f"- lane key: `{lane_key}`")
        if isinstance(surveyed_commit, str):
            markers.append(f"- surveyed commit: `{surveyed_commit}`")
        if blocked_gap is not None:
            markers.append(f"- blocked gap: `{blocked_gap}`")
    return markers, errors

def check_traceability_note(root: Path) -> list[str]:
    traceability_path = root / TRACEABILITY_PATH
    if not traceability_path.exists():
        return [f"missing file: {TRACEABILITY_PATH}"]
    text = read_text(traceability_path)
    expected_markers, marker_errors = traceability_expected_markers(root)
    errors = list(marker_errors)
    for marker, expected_count in Counter(expected_markers).items():
        actual_count = text.count(marker)
        if actual_count != expected_count:
            if actual_count == 0:
                errors.append(f"missing marker in {TRACEABILITY_PATH}: {marker}")
            else:
                errors.append(
                    f"marker count drift in {TRACEABILITY_PATH}: {marker} "
                    f"(expected {expected_count}, found {actual_count})"
                )
    return errors

def check_rcu_rollback_threshold(root: Path) -> list[str]:
    errors: list[str] = []
    survey_path = root / RCU_SURVEY_PATH
    if not survey_path.exists():
        errors.append(f"missing file: {RCU_SURVEY_PATH}")
    else:
        survey_text = read_text(survey_path)
        for marker in RCU_REQUIRED_NOTE_MARKERS:
            if marker not in survey_text:
                errors.append(f"missing marker in {RCU_SURVEY_PATH}: {marker}")
                continue
            actual_count = survey_text.count(marker)
            if actual_count != 1:
                errors.append(
                    f"marker count drift in {RCU_SURVEY_PATH}: {marker} "
                    f"(expected 1, found {actual_count})"
                )

    manifest_path = root / RCU_MANIFEST_PATH
    if not manifest_path.exists():
        errors.append(f"missing file: {RCU_MANIFEST_PATH}")
        return errors

    try:
        manifest = load_json_file(manifest_path)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid json in {RCU_MANIFEST_PATH}: {exc}")
        return errors

    for gap_id, expected_status in RCU_REQUIRED_GAP_STATUSES.items():
        actual_status = gap_status(manifest, gap_id)
        if actual_status != expected_status:
            errors.append(
                f"phase14 rcu rollback-threshold gap drift for {gap_id} "
                f"(expected {expected_status}, found {actual_status})"
            )
    return errors

def run_checker(root: Path, rel_path: str, missing_message: str, failure_message: str) -> list[str]:
    checker = root / rel_path
    if not checker.exists():
        return [missing_message]
    result = subprocess.run(
        [sys.executable, str(checker)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return []
    stderr = [line.strip() for line in result.stderr.splitlines() if line.strip()]
    stdout = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if stderr:
        return stderr
    if stdout:
        return stdout
    return [failure_message]

def collect_manifest_surface_markers(manifest: dict) -> tuple[dict[str, str], Counter[str], list[str]]:
    raw_surfaces = manifest.get("surfaces", [])
    if not isinstance(raw_surfaces, list):
        return {}, Counter(), ["phase14 manifest surfaces payload is not a list"]
    surfaces: dict[str, str] = {}
    surface_counts: Counter[str] = Counter()
    errors: list[str] = []
    for surface in raw_surfaces:
        if not isinstance(surface, dict):
            errors.append("phase14 manifest surface entry is not an object")
            continue
        path = surface.get("path")
        if not isinstance(path, str):
            errors.append("phase14 manifest surface entry is missing a string path")
            continue
        surface_counts[path] += 1
        required_marker = surface.get("required_marker")
        if not isinstance(required_marker, str):
            errors.append(f"phase14 manifest surface missing string required_marker for {path}")
            continue
        surfaces[path] = required_marker
    return surfaces, surface_counts, errors

def check_manifest_productization(manifest: dict) -> list[str]:
    productization = manifest.get("productization")
    if not isinstance(productization, dict):
        return ["phase14 shared smoke manifest productization payload is not an object"]

    errors: list[str] = []
    for key, expected_value in EXPECTED_PRODUCTIZATION.items():
        if productization.get(key) != expected_value:
            errors.append(
                f"phase14 shared smoke manifest productization.{key} drifted from the current study-only packet"
            )
    return errors

def check_compile_matrix(root: Path) -> list[str]:
    errors: list[str] = []
    smoke_note_text = read_text(root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md")
    build_text = read_text(root / "zigux/tests/phase14_build.zig")
    workflow_text = read_text(root / WORKFLOW_PATH)

    if smoke_note_text.count("coverage `focused_and_full_bundle`") != 1:
        errors.append("phase14 smoke note focused compile-shard count drifted from the current one-shard packet")
    if smoke_note_text.count("coverage `full_bundle_only`") != 4:
        errors.append("phase14 smoke note full-bundle-only compile count drifted from the current four-artifact packet")
    if build_text.count("b.addTest(.") != 0 and build_text.count("b.addTest(."):
        pass
    if build_text.count("b.addTest(.") != 0:
        pass
    if build_text.count("b.addTest(.{") != 5:
        errors.append("phase14 build bundle no longer declares the current five compile artifacts")
    if build_text.count("b.addRunArtifact(") != 5:
        errors.append("phase14 build bundle no longer wires the current five compile-artifact runs")

    forbidden_smoke_dependencies = [
        "smoke_step.dependOn(&run_phase14_workqueue_bridge_tests.step);",
        "smoke_step.dependOn(&run_phase14_skbuff_bridge_tests.step);",
        "smoke_step.dependOn(&run_phase14_ring_buffer_survey_tests.step);",
        "smoke_step.dependOn(&run_phase14_rcu_tree_survey_tests.step);",
    ]
    if any(marker in build_text for marker in forbidden_smoke_dependencies):
        errors.append("phase14 smoke shard stopped being dedicated to the shared end-to-end smoke survey")

    for step_name in REQUIRED_WORKFLOW_STEP_NAMES:
        if workflow_text.count(step_name) != 1:
            errors.append(f"phase14 workflow step count drifted for {step_name}")
    for run_marker, error_message in WORKFLOW_WRAPPER_COUNT_MESSAGES.items():
        if workflow_text.count(run_marker) != 1:
            errors.append(error_message)
    if any(marker in workflow_text for marker in FORBIDDEN_DIRECT_WORKFLOW_RUNS):
        errors.append("phase14 workflow reintroduced direct phase14 validator or zig-build commands outside the wrapper routes")

    for label, root_source, coverage in COMPILE_MATRIX_ROWS:
        row = compile_matrix_note_row(label, root_source, coverage)
        if row not in smoke_note_text:
            errors.append(f"missing compile-matrix row in Documentation/zigux/phase14-end-to-end-smoke-survey.md: {row}")
        if label not in build_text:
            errors.append(f"missing compile-artifact label in zigux/tests/phase14_build.zig: {label}")
        if root_source not in build_text:
            errors.append(f"missing compile-artifact root in zigux/tests/phase14_build.zig: {root_source}")
    return errors

def check(root: Path) -> list[str]:
    manifest_path = root / "zigux/tests/phase14_end_to_end_smoke_manifest.json"
    if not manifest_path.exists():
        return [f"missing file: {manifest_path.as_posix()}"]

    errors: list[str] = []
    errors.extend(run_checker(root, "scripts/zigux/check-phase14-docs-root-smoke-summary.py", "missing file: scripts/zigux/check-phase14-docs-root-smoke-summary.py", "phase14 docs-root smoke-summary checker failed without output"))
    errors.extend(run_checker(root, "scripts/zigux/check-phase14-rollback-threshold-sequencing.py", "missing file: scripts/zigux/check-phase14-rollback-threshold-sequencing.py", "phase14 rollback-threshold sequencing checker failed without output"))
    errors.extend(run_checker(root, "scripts/zigux/check-phase14-release-boundary-exact-counts.py", "missing file: scripts/zigux/check-phase14-release-boundary-exact-counts.py", "phase14 release-boundary exact-counts checker failed without output"))

    try:
        manifest = load_json_file(manifest_path)
    except json.JSONDecodeError as exc:
        return [f"invalid json in {manifest_path.as_posix()}: {exc}"]

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        errors.append("phase14 shared smoke manifest lane_key drifted from the current shared-lane owner")
    if manifest.get("commands") != REQUIRED_COMMANDS:
        errors.append("phase14 manifest commands drifted from the shared validate/smoke/test packet")
    if manifest.get("compile_shards") != REQUIRED_COMPILE_SHARDS:
        errors.append("phase14 manifest compile_shards drifted from the current five-row compile packet")

    errors.extend(check_manifest_productization(manifest))

    surfaces, surface_counts, surface_errors = collect_manifest_surface_markers(manifest)
    errors.extend(surface_errors)
    unexpected_surface_paths = sorted(set(surface_counts) - EXPECTED_SURFACE_PATHS)
    for path in unexpected_surface_paths:
        errors.append(f"unexpected manifest surface in zigux/tests/phase14_end_to_end_smoke_manifest.json: {path}")
    for path, count in surface_counts.items():
        if count != 1:
            errors.append(f"phase14 manifest surface count drift for {path} (expected 1, found {count})")
    for path, marker in REQUIRED_SURFACES.items():
        if surfaces.get(path) != marker:
            errors.append(f"manifest surface drift for {path}")

    for rel_path, marker in REQUIRED_SURFACES.items():
        path = root / rel_path
        if not path.exists():
            errors.append(f"missing file: {rel_path}")
            continue
        if marker not in read_text(path):
            errors.append(f"missing marker in {rel_path}: {marker}")

    errors.extend(check_compile_matrix(root))
    errors.extend(check_traceability_note(root))
    errors.extend(check_rcu_rollback_threshold(root))
    return errors

def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest = {
            "lane_key": EXPECTED_LANE_KEY,
            "phase": "Phase 14",
            "packet_name": "phase14_shared_smoke_packet",
            "focus": "study_only_shared_smoke_packet",
            "rollback_owner": "keep the freeze-map anchors in C and reopen only with stronger evidence",
            "productization": dict(EXPECTED_PRODUCTIZATION),
            "commands": REQUIRED_COMMANDS,
            "compile_shards": REQUIRED_COMPILE_SHARDS,
            "surfaces": [{"path": path, "required_marker": marker} for path, marker in REQUIRED_SURFACES.items()],
            "blocked_anchors": ["kernel/workqueue.c","kernel/trace/ring_buffer.c","kernel/rcu/tree.c","net/core/skbuff.c"],
        }
        write_text(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json", json.dumps(manifest, indent=2) + "\n")
        anchor_manifests = {
            "zigux/tests/phase14_workqueue_bridge_manifest.json": {"lane_key": "P14-L04", "surveyed_commit": "9b98d3b9c812840bf279508030be0b8de093736c", "gaps": [{"id": "phase14-workqueue-live-execution-blocker", "status": "blocked_on_stay_in_c_evidence"}]},
            "zigux/tests/phase14_ring_buffer_manifest.json": {"lane_key": "P14-L08", "surveyed_commit": "946d5c73fdb763ba860a20879b05da54e1896e8c", "gaps": [{"id": "phase14-ring-buffer-zig-port-blocker", "status": "blocked_on_stay_in_c_evidence"}]},
            "zigux/tests/phase14_skbuff_bridge_manifest.json": {"lane_key": "P14-L12", "surveyed_commit": "synthetic-skbuff-commit", "gaps": [{"id": "phase14-skbuff-live-ownership-blocker", "status": "blocked_on_stay_in_c_evidence"}]},
            RCU_MANIFEST_PATH: {"lane_key": "P14-L13", "surveyed_commit": "synthetic-rcu-commit", "gaps": [{"id": "phase14-rcu-tree-rollback-threshold-guardrail", "status": "starter_landed"}, {"id": "phase14-rcu-tree-bridge-blocker", "status": "blocked_on_stay_in_c_evidence"}]},
        }
        for rel_path, data in anchor_manifests.items():
            write_text(root / rel_path, json.dumps(data, indent=2) + "\n")
        traceability_markers, traceability_errors = traceability_expected_markers(root)
        if traceability_errors:
            for error in traceability_errors:
                print(error, file=sys.stderr)
            return 1
        write_text(root / TRACEABILITY_PATH, "\n".join(traceability_markers) + "\n")
        placeholder_text = {
            "Documentation/zigux/README.md": "Phase 14 notes\nDocumentation/zigux/phase14-core-boundary-traceability.md\nmake -C zigux phase14-validate\n",
            "Documentation/zigux/phase14-release-boundary-survey.md": "PHASE14_RELEASE_BOUNDARY=present\nDocumentation/zigux/phase14-core-boundary-traceability.md\nmake -C zigux phase14-smoke\nmake -C zigux phase14-test\nmake -C zigux phase14\n",
            "Documentation/zigux/freeze-map.md": "kernel/workqueue.c\n",
            "Documentation/zigux/review-checklist.md": "shared Phase 14 smoke packet\n",
            