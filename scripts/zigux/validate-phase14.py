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
TRACEABILITY_MANIFEST_PATHS = [
    "zigux/tests/phase14_workqueue_bridge_manifest.json",
    "zigux/tests/phase14_ring_buffer_manifest.json",
    "zigux/tests/phase14_skbuff_bridge_manifest.json",
    "zigux/tests/phase14_rcu_tree_manifest.json",
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
    "zigux/tests/phase14_workqueue_bridge.zig": "phase14 workqueue bridge manifest records the boundary-map foothold and remaining gap",
    "zigux/tests/phase14_skbuff_bridge.zig": "phase14 skbuff bridge manifest records the boundary-map foothold and frozen ownership gap",
    "zigux/tests/phase14_workqueue_bridge_manifest.json": "phase14-workqueue-live-execution-blocker",
    "zigux/tests/phase14_skbuff_bridge_manifest.json": "phase14-skbuff-live-ownership-blocker",
    "zigux/tests/phase14_end_to_end_smoke_survey.zig": "phase14 shared smoke survey confirms the current packet surfaces",
    "zigux/tests/phase14_end_to_end_smoke_manifest.json": "phase14_shared_smoke_packet",
    "zigux/tests/phase14_ring_buffer_manifest.json": "phase14-ring-buffer-zig-port-blocker",
    "zigux/tests/phase14_ring_buffer_survey.zig": "phase 14 ring-buffer survey manifest records the study-only gap without inventing a port",
    "zigux/tests/phase14_rcu_tree_manifest.json": "phase14-rcu-tree-bridge-blocker",
    "zigux/tests/phase14_rcu_tree_survey.zig": "phase 14 rcu tree survey manifest records the freeze-boundary gap without inventing a bridge",
    ".github/workflows/zigux-bootstrap.yml": "Run focused Phase 14 smoke shard",
    "kernel/workqueue_bridge.zig": "pub const WorkqueueBridgeLab",
    "net/core/skbuff_bridge.zig": "pub const SkbuffBridgeLab",
}
REQUIRED_FILE_MARKERS = {
    "Documentation/zigux/README.md": [
        "Phase 14 notes",
        "Documentation/zigux/phase14-core-boundary-traceability.md",
        "make -C zigux phase14-validate",
    ],
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md": [
        "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate",
        "PHASE14_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase14.py",
        "Documentation/zigux/phase14-core-boundary-traceability.md",
        "PHASE14_COMPILE_ARTIFACT_COUNT=5",
        "PHASE14_FOCUSED_SHARD_COUNT=1",
        "PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT=4",
    ],
    "Documentation/zigux/phase14-release-boundary-survey.md": [
        "PHASE14_RELEASE_BOUNDARY=present",
        "Documentation/zigux/phase14-core-boundary-traceability.md",
        "make -C zigux phase14-smoke",
        "make -C zigux phase14-test",
        "make -C zigux phase14",
    ],
    "Documentation/zigux/freeze-map.md": ["kernel/workqueue.c"],
    "Documentation/zigux/review-checklist.md": [
        "shared Phase 14 smoke packet",
        "Documentation/zigux/phase14-core-boundary-traceability.md",
        "scripts/zigux/validate-phase14.py",
        "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
        "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
        "make -C zigux phase14-validate",
        "kernel/workqueue.c",
        "kernel/trace/ring_buffer.c",
        "kernel/rcu/tree.c",
        "net/core/skbuff.c",
    ],
    TRACEABILITY_PATH: [TRACEABILITY_TITLE],
    "scripts/zigux/README.md": [
        "python3 scripts/zigux/validate-phase14.py",
        "make -C zigux phase14-validate",
        "Documentation/zigux/phase14-core-boundary-traceability.md",
    ],
    "scripts/zigux/validate-phase14.py": [MARKER],
    "scripts/zigux/check-phase14-docs-root-smoke-summary.py": [DOCS_ROOT_CHECKER_MARKER],
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py": [CHECKER_MARKER],
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py": [RELEASE_BOUNDARY_CHECKER_MARKER],
    "zigux/tests/README.md": [
        "keep the current Phase 14 smoke packet reviewable through",
        "scripts/zigux/validate-phase14.py",
        "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
        "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
        "make -C zigux phase14-validate",
        "make -C zigux phase14-smoke",
        "make -C zigux phase14-test",
        "make -C zigux phase14",
    ],
    "zigux/tests/phase14_build.zig": [
        "phase14-smoke",
        "smoke_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);",
        "test_step.dependOn(&run_phase14_workqueue_bridge_tests.step);",
        "test_step.dependOn(&run_phase14_skbuff_bridge_tests.step);",
        "test_step.dependOn(&run_phase14_ring_buffer_survey_tests.step);",
        "test_step.dependOn(&run_phase14_rcu_tree_survey_tests.step);",
        "test_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);",
    ],
    "zigux/tests/phase14_workqueue_bridge.zig": [
        "phase14 workqueue bridge manifest records the boundary-map foothold and remaining gap",
    ],
    "zigux/tests/phase14_skbuff_bridge.zig": [
        "phase14 skbuff bridge manifest records the boundary-map foothold and frozen ownership gap",
    ],
    "zigux/tests/phase14_workqueue_bridge_manifest.json": ["phase14-workqueue-live-execution-blocker"],
    "zigux/tests/phase14_skbuff_bridge_manifest.json": ["phase14-skbuff-live-ownership-blocker"],
    "zigux/tests/phase14_end_to_end_smoke_survey.zig": [
        "make -C zigux phase14-validate",
        "phase14: phase14-validate phase14-smoke phase14-test",
        "Documentation/zigux/phase14-core-boundary-traceability.md",
        "phase14 shared smoke survey confirms the current packet surfaces",
    ],
    "zigux/tests/phase14_end_to_end_smoke_manifest.json": ["phase14_shared_smoke_packet"],
    "zigux/tests/phase14_ring_buffer_manifest.json": ["phase14-ring-buffer-zig-port-blocker"],
    "zigux/tests/phase14_ring_buffer_survey.zig": [
        "phase 14 ring-buffer survey manifest records the study-only gap without inventing a port",
    ],
    "zigux/tests/phase14_rcu_tree_manifest.json": ["phase14-rcu-tree-bridge-blocker"],
    "zigux/tests/phase14_rcu_tree_survey.zig": [
        "phase 14 rcu tree survey manifest records the freeze-boundary gap without inventing a bridge",
    ],
    "zigux/Makefile": [
        "phase14-validate:",
        "phase14: phase14-validate phase14-smoke phase14-test",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 14 shared smoke packet",
        "Run focused Phase 14 smoke shard",
        "make -C zigux phase14-validate",
        "make -C zigux phase14-smoke",
    ],
    "kernel/workqueue_bridge.zig": ["pub const WorkqueueBridgeLab"],
    "net/core/skbuff_bridge.zig": ["pub const SkbuffBridgeLab"],
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
        markers.append(f"- manifest: `{manifest_rel_path}`")
        if isinstance(lane_key, str):
            markers.append(f"- lane key: `{lane_key}`")
        if isinstance(surveyed_commit, str):
            markers.append(f"- surveyed commit: `{surveyed_commit}`")
        if ready_next_gap is None:
            markers.append("- ready-next gap: none currently recorded")
        else:
            markers.append(f"- ready-next gap: `{ready_next_gap}`")
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
        if expected_count == 1:
            if actual_count == 0:
                errors.append(f"missing marker in {TRACEABILITY_PATH}: {marker}")
            continue
        if actual_count != expected_count:
            errors.append(
                f"marker count drift in {TRACEABILITY_PATH}: {marker} "
                f"(expected {expected_count}, found {actual_count})"
            )
    return errors


def check_compile_matrix(root: Path) -> list[str]:
    errors: list[str] = []
    smoke_note_path = root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
    build_path = root / "zigux/tests/phase14_build.zig"
    if not smoke_note_path.exists():
        return [f"missing file: {smoke_note_path.relative_to(root).as_posix()}"]
    if not build_path.exists():
        return [f"missing file: {build_path.relative_to(root).as_posix()}"]
    smoke_note_text = read_text(smoke_note_path)
    build_text = read_text(build_path)
    if smoke_note_text.count("coverage `focused_and_full_bundle`") != 1:
        errors.append("phase14 smoke note focused compile-shard count drifted from the current one-shard packet")
    if smoke_note_text.count("coverage `full_bundle_only`") != 4:
        errors.append("phase14 smoke note full-bundle-only compile count drifted from the current four-artifact packet")
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
    for marker in forbidden_smoke_dependencies:
        if marker in build_text:
            errors.append("phase14 smoke shard stopped being dedicated to the shared end-to-end smoke survey")
            break
    for label, root_source, coverage in COMPILE_MATRIX_ROWS:
        row = compile_matrix_note_row(label, root_source, coverage)
        if row not in smoke_note_text:
            errors.append(f"missing compile-matrix row in Documentation/zigux/phase14-end-to-end-smoke-survey.md: {row}")
        if label not in build_text:
            errors.append(f"missing compile-artifact label in zigux/tests/phase14_build.zig: {label}")
        if root_source not in build_text:
            errors.append(f"missing compile-artifact root in zigux/tests/phase14_build.zig: {root_source}")
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
    surfaces = {
        surface.get("path"): surface.get("required_marker")
        for surface in manifest.get("surfaces", [])
        if isinstance(surface, dict)
    }
    for path, marker in REQUIRED_SURFACES.items():
        if surfaces.get(path) != marker:
            errors.append(f"manifest surface drift for {path}")
    for rel_path, markers in REQUIRED_FILE_MARKERS.items():
        path = root / rel_path
        if not path.exists():
            errors.append(f"missing file: {rel_path}")
            continue
        text = read_text(path)
        for marker in markers:
            if marker not in text:
                errors.append(f"missing marker in {rel_path}: {marker}")
    errors.extend(check_compile_matrix(root))
    errors.extend(check_traceability_note(root))
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
            "surfaces": [{"path": path, "required_marker": marker} for path, marker in REQUIRED_SURFACES.items()],
            "blocked_anchors": [
                "kernel/workqueue.c",
                "kernel/trace/ring_buffer.c",
                "kernel/rcu/tree.c",
                "net/core/skbuff.c",
            ],
        }
        write_text(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json", json.dumps(manifest, indent=2) + "\n")
        write_text(root / "scripts/zigux/check-phase14-docs-root-smoke-summary.py", f"#!/usr/bin/env python3\n\"\"\"{DOCS_ROOT_CHECKER_MARKER}\"\"\"\nraise SystemExit(0)\n")
        write_text(root / "scripts/zigux/check-phase14-rollback-threshold-sequencing.py", f"#!/usr/bin/env python3\n\"\"\"{CHECKER_MARKER}\"\"\"\nraise SystemExit(0)\n")
        write_text(root / "scripts/zigux/check-phase14-release-boundary-exact-counts.py", f"#!/usr/bin/env python3\n\"\"\"{RELEASE_BOUNDARY_CHECKER_MARKER}\"\"\"\nraise SystemExit(0)\n")
        anchor_manifests = {
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
                "surveyed_commit": "f05e02445443e7743c3675a6f8ca4f70f6e736fb",
                "gaps": [{"id": "phase14-skbuff-live-ownership-blocker", "status": "blocked_on_stay_in_c_evidence"}],
            },
            "zigux/tests/phase14_rcu_tree_manifest.json": {
                "lane_key": "P14-L16",
                "surveyed_commit": "4c889233d157960514b241bcd5aff7cac5fda312",
                "gaps": [{"id": "phase14-rcu-tree-bridge-blocker", "status": "blocked_on_stay_in_c_evidence"}],
            },
            "zigux/tests/phase14_workqueue_bridge_manifest.json": {
                "lane_key": "P14-L04",
                "surveyed_commit": "9e278f632d6d5097cb8cfc2dc61744ae105baa8c",
                "gaps": [{"id": "phase14-workqueue-live-execution-blocker", "status": "blocked_on_stay_in_c_evidence"}],
            },
        }
        for rel_path, data in anchor_manifests.items():
            write_text(root / rel_path, json.dumps(data, indent=2) + "\n")
        expected_traceability_markers, traceability_errors = traceability_expected_markers(root)
        if traceability_errors:
            for error in traceability_errors:
                print(error, file=sys.stderr)
            return 1
        write_text(root / TRACEABILITY_PATH, "\n".join(expected_traceability_markers) + "\n")
        for rel_path, markers in REQUIRED_FILE_MARKERS.items():
            path = root / rel_path
            if path.exists():
                continue
            write_text(path, "\n".join(markers) + "\n")
        matrix_lines = [
            "# Phase 14 End-to-End Smoke Survey",
            "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate",
            "PHASE14_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase14.py",
            "Documentation/zigux/phase14-core-boundary-traceability.md",
            "PHASE14_COMPILE_ARTIFACT_COUNT=5",
            "PHASE14_FOCUSED_SHARD_COUNT=1",
            "PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT=4",
        ]
        matrix_lines.extend(compile_matrix_note_row(*row) for row in COMPILE_MATRIX_ROWS)
        write_text(root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md", "\n".join(matrix_lines) + "\n")
        build_lines = [
            'const smoke_step = b.step("phase14-smoke", "Run the focused Phase 14 end-to-end smoke survey")',
            "smoke_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);",
            "test_step.dependOn(&run_phase14_workqueue_bridge_tests.step);",
            "test_step.dependOn(&run_phase14_skbuff_bridge_tests.step);",
            "test_step.dependOn(&run_phase14_ring_buffer_survey_tests.step);",
            "test_step.dependOn(&run_phase14_rcu_tree_survey_tests.step);",
            "test_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);",
        ]
        for label, root_source, _coverage in COMPILE_MATRIX_ROWS:
            build_lines.append("b.addTest(.{")
            buildLines.append("b.addRunArtifact(")
            build_lines.append(label)
            build_lines.append(root_source)
        write_text(root / "zigux/tests/phase14_build.zig", "\n".join(build_lines) + "\n")
        errors = check(root)
        if errors:
            print("self-test expected success but failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        broken_smoke_note = root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
        broken_smoke_note.write_text(
            broken_smoke_note.read_text(encoding="utf-8").replace(
                compile_matrix_note_row(*COMPILE_MATRIX_ROWS[0]) + "\n", "", 1
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not any("missing compile-matrix row" in error for error in errors):
            print("self-test expected compile-matrix row failure", file=sys.stderr)
            return 1
        write_text(broken_smoke_note, "\n".join(matrix_lines) + "\n")
        broken_build = root / "zigux/tests/phase14_build.zig"
        broken_build.write_text(
            broken_build.read_text(encoding="utf-8").replace(
                "smoke_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);\n",
                "smoke_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);\nsmoke_step.dependOn(&run_phase14_workqueue_bridge_tests.step);\n",
                1,
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not any("phase14 smoke shard stopped being dedicated" in error for error in errors):
            print("self-test expected dedicated smoke-shard failure", file=sys.stderr)
            return 1
        write_text(root / "zigux/tests/phase14_build.zig", "\n".join(build_lines) + "\n")
        broken_traceability = root / TRACEABILITY_PATH
        broken_traceability.write_text(
            broken_traceability.read_text(encoding="utf-8").replace("- lane key: `P14-L08`\n", "", 1),
            encoding="utf-8",
        )
        errors = check(root)
        if not any(
            "missing marker in Documentation/zigux/phase14-core-boundary-traceability.md: - lane key: `P14-L08`" in error
            for error in errors
        ):
            print("self-test expected traceability failure", file=sys.stderr)
            return 1
        write_text(root / TRACEABILITY_PATH, "\n".join(expected_traceability_markers) + "\n")
        broken_manifest = load_json_file(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json")
        broken_manifest["lane_key"] = "P14-L99"
        write_text(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json", json.dumps(broken_manifest, indent=2) + "\n")
        errors = check(root)
        if not any("phase14 shared smoke manifest lane_key drifted from the current shared-lane owner" in error for error in errors):
            print("self-test expected manifest lane_key failure", file=sys.stderr)
            return 1
        write_text(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json", json.dumps(manifest, indent=2) + "\n")
        broken_manifest = load_json_file(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json")
        broken_manifest["commands"] = REQUIRED_COMMANDS[:-1]
        write_text(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json", json.dumps(broken_manifest, indent=2) + "\n")
        errors = check(root)
        if not any("phase14 manifest commands drifted from the shared validate/smoke/test packet" in error for error in errors):
            print("self-test expected manifest commands failure", file=sys.stderr)
            return 1
        write_text(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json", json.dumps(manifest, indent=2) + "\n")
        broken_manifest = load_json_file(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json")
        broken_manifest["surfaces"] = [
            surface
            for surface in broken_manifest["surfaces"]
            if surface.get("path") != "scripts/zigux/check-phase14-docs-root-smoke-summary.py"
        ]
        write_text(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json", json.dumps(broken_manifest, indent=2) + "\n")
        errors = check(root)
        if not any("manifest surface drift for scripts/zigux/check-phase14-docs-root-smoke-summary.py" in error for error in errors):
            print("self-test expected manifest surface failure", file=sys.stderr)
            return 1
        write_text(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json", json.dumps(manifest, indent=2) + "\n")
        broken_docs_root = root / "Documentation/zigux/README.md"
        broken_docs_root.write_text(
            broken_docs_root.read_text(encoding="utf-8").replace("make -C zigux phase14-validate\n", "", 1),
            encoding="utf-8",
        )
        errors = check(root)
        if not any("missing marker in Documentation/zigux/README.md: make -C zigux phase14-validate" in error for error in errors):
            print("self-test expected docs-root marker failure", file=sys.stderr)
            return 1
        write_text(root / "Documentation/zigux/README.md", "\n".join(REQUIRED_FILE_MARKERS["Documentation/zigux/README.md"]) + "\n")
        broken_checker = root / "scripts/zigux/check-phase14-docs-root-smoke-summary.py"
        broken_checker.write_text(
            "#!/usr/bin/env python3\n"
            f"\"\"\"{DOCS_ROOT_CHECKER_MARKER}\"\"\"\n"
            "import sys\n"
            "print('phase14 docs-root smoke summary checker forced failure', file=sys.stderr)\n"
            "raise SystemExit(1)\n",
            encoding="utf-8",
        )
        errors = check(root)
        if "phase14 docs-root smoke summary checker forced failure" not in errors:
            print("self-test expected docs-root checker subprocess failure", file=sys.stderr)
            return 1
        broken_checker.write_text(
            "#!/usr/bin/env python3\n"
            f"\"\"\"{DOCS_ROOT_CHECKER_MARKER}\"\"\"\n"
            "raise SystemExit(1)\n",
            encoding="utf-8",
        )
        errors = check(root)
        if "phase14 docs-root smoke-summary checker failed without output" not in errors:
            print("self-test expected docs-root checker silent subprocess failure", file=sys.stderr)
            return 1
        write_text(root / "scripts/zigux/check-phase14-docs-root-smoke-summary.py", f"#!/usr/bin/env python3\n\"\"\"{DOCS_ROOT_CHECKER_MARKER}\"\"\"\nraise SystemExit(0)\n")
        broken_rollback_checker = root / "scripts/zigux/check-phase14-rollback-threshold-sequencing.py"
        broken_rollback_checker.write_text(
            "#!/usr/bin/env python3\n"
            f"\"\"\"{CHECKER_MARKER}\"\"\"\n"
            "import sys\n"
            "print('phase14 rollback-threshold sequencing checker forced failure', file=sys.stderr)\n"
            "raise SystemExit(1)\n",
            encoding="utf-8",
        )
        errors = check(root)
        if "phase14 rollback-threshold sequencing checker forced failure" not in errors:
            print("self-test expected rollback-threshold checker subprocess failure", file=sys.stderr)
            return 1
        broken_rollback_checker.write_text(
            "#!/usr/bin/env python3\n"
            f"\"\"\"{CHECKER_MARKER}\"\"\"\n"
            "raise SystemExit(1)\n",
            encoding="utf-8",
        )
        errors = check(root)
        if "phase14 rollback-threshold sequencing checker failed without output" not in errors:
            print("self-test expected rollback-threshold checker silent subprocess failure", file=sys.stderr)
            return 1
        write_text(root / "scripts/zigux/check-phase14-rollback-threshold-sequencing.py", f"#!/usr/bin/env python3\n\"\"\"{CHECKER_MARKER}\"\"\"\nraise SystemExit(0)\n")
        missing_rollback_checker = root / "scripts/zigux/check-phase14-rollback-threshold-sequencing.py"
        missing_rollback_checker.unlink()
        errors = check(root)
        if "missing file: scripts/zigux/check-phase14-rollback-threshold-sequencing.py" not in errors:
            print("self-test expected missing rollback-threshold checker failure", file=sys.stderr)
            return 1
        write_text(root / "scripts/zigux/check-phase14-rollback-threshold-sequencing.py", f"#!/usr/bin/env python3\n\"\"\"{CHECKER_MARKER}\"\"\"\nraise SystemExit(0)\n")
        broken_release_boundary_checker = root / "scripts/zigux/check-phase14-release-boundary-exact-counts.py"
        broken_release_boundary_checker.write_text(
            "#!/usr/bin/env python3\n"
            f"\"\"\"{RELEASE_BOUNDARY_CHECKER_MARKER}\"\"\"\n"
            "import sys\n"
            "print('phase14 release-boundary exact-counts checker forced failure', file=sys.stderr)\n"
            "raise SystemExit(1)\n",
            encoding="utf-8",
        )
        errors = check(root)
        if "phase14 release-boundary exact-counts checker forced failure" not in errors:
            print("self-test expected release-boundary checker subprocess failure", file=sys.stderr)
            return 1
        broken_release_boundary_checker.write_text(
            "#!/usr/bin/env python3\n"
            f"\"\"\"{RELEASE_BOUNDARY_CHECKER_MARKER}\"\"\"\n"
            "raise SystemExit(1)\n",
            encoding="utf-8",
        )
        errors = check(root)
        if "phase14 release-boundary exact-counts checker failed without output" not in errors:
            print("self-test expected release-boundary checker silent subprocess failure", file=sys.stderr)
            return 1
        write_text(root / "scripts/zigux/check-phase14-release-boundary-exact-counts.py", f"#!/usr/bin/env python3\n\"\"\"{RELEASE_BOUNDARY_CHECKER_MARKER}\"\"\"\nraise SystemExit(0)\n")
        missing_release_boundary_checker = root / "scripts/zigux/check-phase14-release-boundary-exact-counts.py"
        missing_release_boundary_checker.unlink()
        errors = check(root)
        if "missing file: scripts/zigux/check-phase14-release-boundary-exact-counts.py" not in errors:
            print("self-test expected missing release-boundary checker failure", file=sys.stderr)
            return 1
        write_text(root / "scripts/zigux/check-phase14-release-boundary-exact-counts.py", f"#!/usr/bin/env python3\n\"\"\"{RELEASE_BOUNDARY_CHECKER_MARKER}\"\"\"\nraise SystemExit(0)\n")
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
