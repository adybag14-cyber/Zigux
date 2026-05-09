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
    ("phase14-workqueue-reviewability-tests", "phase14_workqueue_reviewability.zig", "full_bundle_only"),
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
    "zigux/tests/phase14_workqueue_reviewability.zig": "phase14 workqueue reviewability guard keeps the shared reviewer surface aligned",
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


def check_compile_matrix(root: Path) -> list[str]:
    errors: list[str] = []
    smoke_note_text = read_text(root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md")
    build_text = read_text(root / "zigux/tests/phase14_build.zig")
    workflow_text = read_text(root / WORKFLOW_PATH)

    if smoke_note_text.count("coverage `focused_and_full_bundle`") != 1:
        errors.append("phase14 smoke note focused compile-shard count drifted from the current one-shard packet")
    if smoke_note_text.count("coverage `full_bundle_only`") != 5:
        errors.append("phase14 smoke note full-bundle-only compile count drifted from the current five-artifact packet")
    if build_text.count("b.addTest(.") != 0 and build_text.count("b.addTest(."):
        pass
    if build_text.count("b.addTest(.") != 0:
        pass
    if build_text.count("b.addTest(.{") != 6:
        errors.append("phase14 build bundle no longer declares the current six compile artifacts")
    if build_text.count("b.addRunArtifact(") != 6:
        errors.append("phase14 build bundle no longer wires the current six compile-artifact runs")

    forbidden_smoke_dependencies = [
        "smoke_step.dependOn(&run_phase14_workqueue_bridge_tests.step);",
        "smoke_step.dependOn(&run_phase14_workqueue_reviewability_tests.step);",
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
    if "test_step.dependOn(&run_phase14_workqueue_reviewability_tests.step);" not in build_text:
        errors.append("missing compile-artifact dependency in zigux/tests/phase14_build.zig: phase14_workqueue_reviewability")
    return errors


def check(root: Path) -> list[str]:
    manifest_path = root / "zigux/tests/phase14_end_to_end_smoke_manifest.json"
    if not manifest_path.exists():
        return [f"missing file: {manifest_path.as_posix()}"]

    errors: list[str] = []
    errors.extend(
        run_checker(
            root,
            "scripts/zigux/check-phase14-docs-root-smoke-summary.py",
            "missing file: scripts/zigux/check-phase14-docs-root-smoke-summary.py",
            "phase14 docs-root smoke-summary checker failed without output",
        )
    )
    errors.extend(
        run_checker(
            root,
            "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
            "missing file: scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
            "phase14 rollback-threshold sequencing checker failed without output",
        )
    )
    errors.extend(
        run_checker(
            root,
            "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
            "missing file: scripts/zigux/check-phase14-release-boundary-exact-counts.py",
            "phase14 release-boundary exact-counts checker failed without output",
        )
    )

    try:
        manifest = load_json_file(manifest_path)
    except json.JSONDecodeError as exc:
        return [f"invalid json in {manifest_path.as_posix()}: {exc}"]

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        errors.append("phase14 shared smoke manifest lane_key drifted from the current shared-lane owner")
    if manifest.get("commands") != REQUIRED_COMMANDS:
        errors.append("phase14 manifest commands drifted from the shared validate/smoke/test packet")
    if manifest.get("compile_shards") != REQUIRED_COMPILE_SHARDS:
        errors.append("phase14 manifest compile_shards drifted from the current six-row compile packet")

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
            "commands": REQUIRED_COMMANDS,
            "compile_shards": REQUIRED_COMPILE_SHARDS,
            "surfaces": [
                {"path": path, "required_marker": marker}
                for path, marker in REQUIRED_SURFACES.items()
            ],
            "blocked_anchors": [
                "kernel/workqueue.c",
                "kernel/trace/ring_buffer.c",
                "kernel/rcu/tree.c",
                "net/core/skbuff.c",
            ],
        }
        write_text(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json", json.dumps(manifest, indent=2) + "\n")

        anchor_manifests = {
            "zigux/tests/phase14_workqueue_bridge_manifest.json": {
                "lane_key": "P14-L02",
                "surveyed_commit": "9b98d3b9c812840bf279508030be0b8de093736c",
                "gaps": [{"id": "phase14-workqueue-live-execution-blocker", "status": "blocked_on_stay_in_c_evidence"}],
            },
            "zigux/tests/phase14_ring_buffer_manifest.json": {
                "lane_key": "P14-L08",
                "surveyed_commit": "946d5c73fdb763ba860a20879b05da54e1896e8c",
                "gaps": [
                    {"id": "phase14-ring-buffer-read-page-copy-followup", "status": "ready_next"},
                    {"id": "phase14-ring-buffer-zig-port-blocker", "status": "blocked_on_stay_in_c_evidence"},
                ],
            },
            "zigux/tests/phase14_skbuff_bridge_manifest.json": {
                "lane_key": "P14-L11",
                "surveyed_commit": "synthetic-skbuff-commit",
                "gaps": [{"id": "phase14-skbuff-live-ownership-blocker", "status": "blocked_on_stay_in_c_evidence"}],
            },
            RCU_MANIFEST_PATH: {
                "lane_key": "P14-L13",
                "surveyed_commit": "synthetic-rcu-commit",
                "gaps": [
                    {"id": "phase14-rcu-tree-rollback-threshold-guardrail", "status": "starter_landed"},
                    {"id": "phase14-rcu-tree-bridge-blocker", "status": "blocked_on_stay_in_c_evidence"},
                ],
            },
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
            RCU_SURVEY_PATH: "\n".join([
                "# Phase 14 RCU Tree Survey",
                "## Rollback threshold",
                "- status bucket: `freeze_in_c`",
                "- blocker status: `blocked_on_stay_in_c_evidence`",
                "- rollback owner: `Repo Tooling Pod`",
                "- Architecture Council reopen record linked from the reviewable packet",
                "- parity scorecard evidence and benchmark notes attached to the same review packet",
                "- validation replay command and evidence archive path recorded beside the latest blocker disposition",
                "- any `kernel/rcu/tree_bridge.zig` claim or status review that lacks the Architecture Council reopen record",
                "- missing parity scorecard evidence, benchmark notes, or replay command in the active review packet",
                "- freeze-map, survey note, or manifest drift that drops the blocked bridge disposition or rollback owner",
            ]) + "\n",
            "scripts/zigux/README.md": "Phase 14 flow\npython3 scripts/zigux/validate-phase14.py\nmake -C zigux phase14-validate\nDocumentation/zigux/phase14-core-boundary-traceability.md\n",
            "scripts/zigux/check-phase14-docs-root-smoke-summary.py": f"#!/usr/bin/env python3\n\"\"\"{DOCS_ROOT_CHECKER_MARKER}\"\"\"\nraise SystemExit(0)\n",
            "scripts/zigux/check-phase14-rollback-threshold-sequencing.py": f"#!/usr/bin/env python3\n\"\"\"{CHECKER_MARKER}\"\"\"\nraise SystemExit(0)\n",
            "scripts/zigux/check-phase14-release-boundary-exact-counts.py": f"#!/usr/bin/env python3\n\"\"\"{RELEASE_BOUNDARY_CHECKER_MARKER}\"\"\"\nraise SystemExit(0)\n",
            "zigux/tests/README.md": "keep the current Phase 14 smoke packet reviewable\n",
            "zigux/tests/phase14_workqueue_bridge.zig": "phase14 workqueue bridge manifest records the boundary-map foothold and remaining gap\n",
            "zigux/tests/phase14_workqueue_reviewability.zig": "phase14 workqueue reviewability guard keeps the shared reviewer surface aligned\n",
            "zigux/tests/phase14_skbuff_bridge.zig": "phase14 skbuff bridge manifest records the boundary-map foothold and frozen ownership gap\n",
            "zigux/tests/phase14_end_to_end_smoke_survey.zig": "phase14 shared smoke survey confirms the current packet surfaces\n",
            "zigux/tests/phase14_ring_buffer_survey.zig": "phase 14 ring-buffer survey manifest records the study-only gap without inventing a port\n",
            "zigux/tests/phase14_rcu_tree_survey.zig": "phase 14 rcu tree survey manifest records the freeze-boundary gap without inventing a bridge\n",
            "kernel/workqueue_bridge.zig": "pub const WorkqueueBridgeLab = struct {};\n",
            "net/core/skbuff_bridge.zig": "pub const SkbuffBridgeLab = struct {};\n",
            "kernel/rcu/tree_bridge.zig": "pub const RcuTreeBridgeLab = struct {};\n",
            WORKFLOW_PATH: "\n".join([
                "Validate Phase 14 shared smoke packet",
                "run: make -C zigux phase14-validate",
                "Run focused Phase 14 smoke shard",
                "run: make -C zigux phase14-smoke",
                "Run Phase 14 internal bridge tests",
                "run: make -C zigux phase14-test",
            ]) + "\n",
            "zigux/Makefile": "\n".join([
                "phase14-validate:",
                "\tpython3 scripts/zigux/validate-phase14.py --self-test",
                "phase14-smoke:",
                "\t$(ZIG) build phase14-smoke --build-file zigux/tests/phase14_build.zig",
                "phase14-test:",
                "\t$(ZIG) build test --build-file zigux/tests/phase14_build.zig",
                "phase14: phase14-validate phase14-smoke phase14-test",
                "scripts/zigux/check-phase14-docs-root-smoke-summary.py",
                "zigux/tests/phase14_build.zig",
            ]) + "\n",
            "zigux/tests/phase14_build.zig": "\n".join([
                'const smoke_step = b.step("phase14-smoke", "Run the focused Phase 14 end-to-end smoke survey")',
                "smoke_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);",
                'const test_step = b.step("test", "Run Phase 14 bounded internal bridge tests")',
                "test_step.dependOn(&run_phase14_workqueue_bridge_tests.step);",
                "test_step.dependOn(&run_phase14_workqueue_reviewability_tests.step);",
                "test_step.dependOn(&run_phase14_skbuff_bridge_tests.step);",
                "test_step.dependOn(&run_phase14_ring_buffer_survey_tests.step);",
                "test_step.dependOn(&run_phase14_rcu_tree_survey_tests.step);",
                "test_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);",
                *["b.addTest(.{" for _ in range(6)],
                *["b.addRunArtifact(" for _ in range(6)],
                "phase14-workqueue-bridge-tests",
                "phase14_workqueue_bridge.zig",
                "phase14-workqueue-reviewability-tests",
                "phase14_workqueue_reviewability.zig",
                "phase14-skbuff-bridge-tests",
                "phase14_skbuff_bridge.zig",
                "phase14-ring-buffer-survey-tests",
                "phase14_ring_buffer_survey.zig",
                "phase14-rcu-tree-survey-tests",
                "phase14_rcu_tree_survey.zig",
                "phase14-end-to-end-smoke-tests",
                "phase14_end_to_end_smoke_survey.zig",
            ]) + "\n",
        }

        for rel_path, text in placeholder_text.items():
            write_text(root / rel_path, text)

        write_text(root / "scripts/zigux/validate-phase14.py", read_text(Path(__file__)))

        smoke_note_lines = [
            "# Phase 14 End-to-End Smoke Survey",
            "PHASE14_VALIDATE_SELF_TEST=python3 scripts/zigux/validate-phase14.py --self-test",
            "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate",
            "PHASE14_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase14.py",
            "PHASE14_BUILD_ENTRYPOINT=zig build test --build-file zigux/tests/phase14_build.zig --summary all",
            "PHASE14_SHARED_SURFACE_COUNT=29",
            "PHASE14_DOC_SURFACE_COUNT=6",
            "PHASE14_SCRIPT_SURFACE_COUNT=5",
            "PHASE14_TEST_SURFACE_COUNT=13",
            "PHASE14_BRIDGE_ROOT_SURFACE_COUNT=3",
            "PHASE14_WORKFLOW_SURFACE_COUNT=1",
            "PHASE14_MAKEFILE_SURFACE_COUNT=1",
            "PHASE14_COMPILE_ARTIFACT_COUNT=6",
            "PHASE14_FOCUSED_SHARD_COUNT=1",
            "PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT=5",
            "kernel/rcu/tree_bridge.zig",
            "This wrapper first runs `python3 scripts/zigux/validate-phase14.py --self-test` and then the shared packet validator.",
            "`Documentation/zigux/phase14-ring-buffer-survey.md` and `zigux/tests/phase14_ring_buffer_manifest.json` agree on lane `P14-L08`",
            "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate",
            "PHASE14_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase14.py",
            "Documentation/zigux/phase14-core-boundary-traceability.md",
            "zigux/tests/phase14_workqueue_reviewability.zig",
        ]
        smoke_note_lines.extend(compile_matrix_note_row(*row) for row in COMPILE_MATRIX_ROWS)
        write_text(root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md", "\n".join(smoke_note_lines) + "\n")

        errors = check(root)
        if errors:
            print("self-test expected success but failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1

        broken = load_json_file(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json")
        broken["compile_shards"] = REQUIRED_COMPILE_SHARDS[:-1]
        write_text(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json", json.dumps(broken, indent=2) + "\n")
        errors = check(root)
        if "phase14 manifest compile_shards drifted from the current six-row compile packet" not in errors:
            print("self-test expected compile-shard drift failure", file=sys.stderr)
            return 1

        write_text(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json", json.dumps(manifest, indent=2) + "\n")
        build_path = root / "zigux/tests/phase14_build.zig"
        build_path.write_text(build_path.read_text(encoding="utf-8").replace("b.addRunArtifact(\n", "", 1), encoding="utf-8")
        errors = check(root)
        if "phase14 build bundle no longer wires the current six compile-artifact runs" not in errors:
            print("self-test expected build run-count failure", file=sys.stderr)
            return 1

        write_text(root / "zigux/tests/phase14_build.zig", placeholder_text["zigux/tests/phase14_build.zig"])
        rcu_survey_path = root / RCU_SURVEY_PATH
        rcu_survey_path.write_text(
            rcu_survey_path.read_text(encoding="utf-8").replace(
                "- rollback owner: `Repo Tooling Pod`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not any(
            "missing marker in Documentation/zigux/phase14-rcu-tree-survey.md: - rollback owner: `Repo Tooling Pod`"
            in error
            for error in errors
        ):
            print("self-test expected rcu rollback-owner failure", file=sys.stderr)
            return 1

        write_text(root / RCU_SURVEY_PATH, placeholder_text[RCU_SURVEY_PATH])
        broken_rcu_manifest = load_json_file(root / RCU_MANIFEST_PATH)
        for gap in broken_rcu_manifest["gaps"]:
            if gap.get("id") == "phase14-rcu-tree-rollback-threshold-guardrail":
                gap["status"] = "blocked_on_stay_in_c_evidence"
        write_text(root / RCU_MANIFEST_PATH, json.dumps(broken_rcu_manifest, indent=2) + "\n")
        errors = check(root)
        if not any(
            "phase14 rcu rollback-threshold gap drift for phase14-rcu-tree-rollback-threshold-guardrail"
            in error
            for error in errors
        ):
            print("self-test expected rcu rollback-threshold manifest failure", file=sys.stderr)
            return 1

        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the built-in validator self-test")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    errors = check(repo_root())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("phase14 shared smoke packet validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
