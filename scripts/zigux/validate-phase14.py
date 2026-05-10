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

EXPECTED_PRODUCTIZATION = {
    "named_owner": "Core-Adjacent Pod",
    "status_bucket": "study_only",
    "validation_gate": "make -C zigux phase14-validate && make -C zigux phase14-smoke && make -C zigux phase14-test && make -C zigux phase14",
    "rollback_owner": "keep the freeze-map anchors in C and reopen only with stronger evidence",
    "review_blocker_status": "blocked_on_stay_in_c_evidence",
    "transfer_rationale": "transfer ZAR runtime research into explicit reviewability evidence instead of widening Phase 14 into a deep-core port",
    "roadmap_risk_bundle": [
        "hidden runtime behavior",
        "memory-ordering mistakes",
        "overpromising full parity",
        "deep-core scope creep",
    ],
    "fallback_path": "Keep kernel/workqueue.c, net/core/skbuff.c, kernel/trace/ring_buffer.c, and kernel/rcu/tree.c as the source of truth and keep the shared smoke packet limited to survey-backed reviewability evidence.",
}

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

TRACEABILITY_EXPECTATIONS = [
    (
        "zigux/tests/phase14_workqueue_bridge_manifest.json",
        "P14-L04",
        "phase14-workqueue-live-execution-blocker",
    ),
    (
        "zigux/tests/phase14_ring_buffer_manifest.json",
        "P14-L08",
        "phase14-ring-buffer-zig-port-blocker",
    ),
    (
        "zigux/tests/phase14_skbuff_bridge_manifest.json",
        "P14-L12",
        "phase14-skbuff-live-ownership-blocker",
    ),
    (
        RCU_MANIFEST_PATH,
        "P14-L13",
        "phase14-rcu-tree-bridge-blocker",
    ),
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


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(read_text(path))


def compile_matrix_note_row(label: str, root_source: str, coverage: str) -> str:
    return f"- `{label}`: root `{root_source}`, coverage `{coverage}`"


def blocked_gap_id(manifest: dict) -> str | None:
    for gap in manifest.get("gaps", []):
        if str(gap.get("status", "")).startswith("blocked"):
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


def run_checker(root: Path, rel_path: str, marker: str) -> list[str]:
    path = root / rel_path
    if not path.exists():
        return [f"missing file: {rel_path}"]
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return []
    return [
        line
        for line in (result.stderr.splitlines() + result.stdout.splitlines())
        if line.strip()
    ] or [f"{marker} checker failed without output"]


def check_traceability(root: Path) -> list[str]:
    errors: list[str] = []
    path = root / TRACEABILITY_PATH
    if not path.exists():
        return [f"missing file: {TRACEABILITY_PATH}"]
    text = read_text(path)
    for marker in [
        TRACEABILITY_TITLE,
        "- validator entrypoint: `make -C zigux phase14-validate`",
        "- convenience target: `make -C zigux phase14`",
    ]:
        if marker not in text:
            errors.append(f"missing marker in {TRACEABILITY_PATH}: {marker}")
    for rel_path, lane_key, blocked_gap in TRACEABILITY_EXPECTATIONS:
        manifest = load_json(root / rel_path)
        surveyed_commit = manifest.get("surveyed_commit")
        ready_gap = ready_next_gap_id(manifest)
        expected_markers = [
            f"- manifest: `{rel_path}`",
            f"- lane key: `{lane_key}`",
            f"- blocked gap: `{blocked_gap}`",
            (
                f"- ready-next gap: `{ready_gap}`"
                if ready_gap is not None
                else "- ready-next gap: none currently recorded"
            ),
        ]
        if isinstance(surveyed_commit, str):
            expected_markers.append(f"- surveyed commit: `{surveyed_commit}`")
        for marker in expected_markers:
            if marker not in text:
                errors.append(f"missing marker in {TRACEABILITY_PATH}: {marker}")
    return errors


def check_rcu(root: Path) -> list[str]:
    errors: list[str] = []
    note = root / RCU_SURVEY_PATH
    if not note.exists():
        return [f"missing file: {RCU_SURVEY_PATH}"]
    note_text = read_text(note)
    for marker in RCU_REQUIRED_NOTE_MARKERS:
        if note_text.count(marker) != 1:
            errors.append(f"missing marker in {RCU_SURVEY_PATH}: {marker}")
    manifest = load_json(root / RCU_MANIFEST_PATH)
    required_statuses = {
        "phase14-rcu-tree-rollback-threshold-guardrail": "starter_landed",
        "phase14-rcu-tree-bridge-blocker": "blocked_on_stay_in_c_evidence",
    }
    for gap_id, expected_status in required_statuses.items():
        actual = None
        for gap in manifest.get("gaps", []):
            if gap.get("id") == gap_id:
                actual = gap.get("status")
                break
        if actual != expected_status:
            errors.append(
                f"phase14 rcu rollback-threshold gap drift for {gap_id} "
                f"(expected {expected_status}, found {actual})"
            )
    return errors


def check_compile_matrix(root: Path) -> list[str]:
    errors: list[str] = []
    smoke_note = read_text(root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md")
    build_text = read_text(root / "zigux/tests/phase14_build.zig")
    workflow_text = read_text(root / WORKFLOW_PATH)

    if smoke_note.count("coverage `focused_and_full_bundle`") != 1:
        errors.append("phase14 smoke note focused compile-shard count drifted from the current one-shard packet")
    if smoke_note.count("coverage `full_bundle_only`") != 4:
        errors.append("phase14 smoke note full-bundle-only compile count drifted from the current four-artifact packet")
    if build_text.count("b.addTest(.{") != 5:
        errors.append("phase14 build bundle no longer declares the current five compile artifacts")
    if build_text.count("b.addRunArtifact(") != 5:
        errors.append("phase14 build bundle no longer wires the current five compile-artifact runs")

    for forbidden in [
        "smoke_step.dependOn(&run_phase14_workqueue_bridge_tests.step);",
        "smoke_step.dependOn(&run_phase14_skbuff_bridge_tests.step);",
        "smoke_step.dependOn(&run_phase14_ring_buffer_survey_tests.step);",
        "smoke_step.dependOn(&run_phase14_rcu_tree_survey_tests.step);",
    ]:
        if forbidden in build_text:
            errors.append("phase14 smoke shard stopped being dedicated to the shared end-to-end smoke survey")
            break

    for step_name in [
        "Validate Phase 14 shared smoke packet",
        "Run focused Phase 14 smoke shard",
        "Run Phase 14 internal bridge tests",
    ]:
        if workflow_text.count(step_name) != 1:
            errors.append(f"phase14 workflow step count drifted for {step_name}")

    for wrapper, message in {
        "run: make -C zigux phase14-validate": "phase14 workflow validate wrapper count drifted from the current one-step packet",
        "run: make -C zigux phase14-smoke": "phase14 workflow smoke wrapper count drifted from the current one-step packet",
        "run: make -C zigux phase14-test": "phase14 workflow full-bundle wrapper count drifted from the current one-step packet",
    }.items():
        if workflow_text.count(wrapper) != 1:
            errors.append(message)

    for forbidden_run in [
        "run: python3 scripts/zigux/validate-phase14.py",
        "run: zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all",
        "run: zig build test --build-file zigux/tests/phase14_build.zig --summary all",
        "run: zig build test --build-file zigux/tests/phase14_build.zig",
    ]:
        if forbidden_run in workflow_text:
            errors.append("phase14 workflow reintroduced direct phase14 validator or zig-build commands outside the wrapper routes")
            break

    for label, root_source, coverage in COMPILE_MATRIX_ROWS:
        row = compile_matrix_note_row(label, root_source, coverage)
        if row not in smoke_note:
            errors.append(f"missing compile-matrix row in Documentation/zigux/phase14-end-to-end-smoke-survey.md: {row}")
        if label not in build_text:
            errors.append(f"missing compile-artifact label in zigux/tests/phase14_build.zig: {label}")
        if root_source not in build_text:
            errors.append(f"missing compile-artifact root in zigux/tests/phase14_build.zig: {root_source}")
    return errors


def check(root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(run_checker(root, "scripts/zigux/check-phase14-docs-root-smoke-summary.py", "docs-root"))
    errors.extend(run_checker(root, "scripts/zigux/check-phase14-rollback-threshold-sequencing.py", "rollback-threshold"))
    errors.extend(run_checker(root, "scripts/zigux/check-phase14-release-boundary-exact-counts.py", "release-boundary"))

    manifest_path = root / "zigux/tests/phase14_end_to_end_smoke_manifest.json"
    if not manifest_path.exists():
        return errors + [f"missing file: {manifest_path.as_posix()}"]
    manifest = load_json(manifest_path)

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        errors.append("phase14 shared smoke manifest lane_key drifted from the current shared-lane owner")
    if manifest.get("commands") != REQUIRED_COMMANDS:
        errors.append("phase14 manifest commands drifted from the shared validate/smoke/test packet")
    if manifest.get("compile_shards") != REQUIRED_COMPILE_SHARDS:
        errors.append("phase14 manifest compile_shards drifted from the current five-row compile packet")
    if manifest.get("productization") != EXPECTED_PRODUCTIZATION:
        errors.append("phase14 shared smoke manifest productization drifted from the current study-only packet")

    surfaces = manifest.get("surfaces")
    if not isinstance(surfaces, list):
        errors.append("phase14 manifest surfaces payload is not a list")
    else:
        found = {entry.get("path"): entry.get("required_marker") for entry in surfaces if isinstance(entry, dict)}
        counts = Counter(entry.get("path") for entry in surfaces if isinstance(entry, dict))
        for path, marker in REQUIRED_SURFACES.items():
            if found.get(path) != marker:
                errors.append(f"manifest surface drift for {path}")
        for path, count in counts.items():
            if count != 1:
                errors.append(f"phase14 manifest surface count drift for {path} (expected 1, found {count})")

    for rel_path, marker in REQUIRED_SURFACES.items():
        path = root / rel_path
        if not path.exists():
            errors.append(f"missing file: {rel_path}")
            continue
        if marker not in read_text(path):
            errors.append(f"missing marker in {rel_path}: {marker}")

    errors.extend(check_compile_matrix(root))
    errors.extend(check_traceability(root))
    errors.extend(check_rcu(root))
    return errors


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        manifest = {
            "lane_key": EXPECTED_LANE_KEY,
            "phase": "Phase 14",
            "packet_name": "phase14_shared_smoke_packet",
            "focus": "study_only_shared_smoke_packet",
            "rollback_owner": EXPECTED_PRODUCTIZATION["rollback_owner"],
            "productization": EXPECTED_PRODUCTIZATION,
            "commands": REQUIRED_COMMANDS,
            "compile_shards": REQUIRED_COMPILE_SHARDS,
            "surfaces": [{"path": path, "required_marker": marker} for path, marker in REQUIRED_SURFACES.items()],
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
                "lane_key": "P14-L04",
                "surveyed_commit": "9b98d3b9c812840bf279508030be0b8de093736c",
                "gaps": [{"id": "phase14-workqueue-live-execution-blocker", "status": "blocked_on_stay_in_c_evidence"}],
            },
            "zigux/tests/phase14_ring_buffer_manifest.json": {
                "lane_key": "P14-L08",
                "surveyed_commit": "946d5c73fdb763ba860a20879b05da54e1896e8c",
                "gaps": [{"id": "phase14-ring-buffer-zig-port-blocker", "status": "blocked_on_stay_in_c_evidence"}],
            },
            "zigux/tests/phase14_skbuff_bridge_manifest.json": {
                "lane_key": "P14-L12",
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

        traceability_lines = [
            TRACEABILITY_TITLE,
            "- validator entrypoint: `make -C zigux phase14-validate`",
            "- convenience target: `make -C zigux phase14`",
        ]
        for rel_path, lane_key, blocked_gap in TRACEABILITY_EXPECTATIONS:
            manifest_data = load_json(root / rel_path)
            traceability_lines.extend(
                [
                    f"- manifest: `{rel_path}`",
                    f"- lane key: `{lane_key}`",
                    f"- surveyed commit: `{manifest_data['surveyed_commit']}`",
                    "- ready-next gap: none currently recorded",
                    f"- blocked gap: `{blocked_gap}`",
                ]
            )
        write_text(root / TRACEABILITY_PATH, "\n".join(traceability_lines) + "\n")

        support_files = {
            "Documentation/zigux/README.md": "Phase 14 notes\n",
            "Documentation/zigux/phase14-release-boundary-survey.md": "PHASE14_RELEASE_BOUNDARY=present\n",
            "Documentation/zigux/freeze-map.md": "kernel/workqueue.c\n",
            "Documentation/zigux/review-checklist.md": "shared Phase 14 smoke packet\n",
            "Documentation/zigux/phase14-rcu-tree-survey.md": "\n".join(["# Phase 14 RCU Tree Survey"] + RCU_REQUIRED_NOTE_MARKERS) + "\n",
            "scripts/zigux/README.md": "Phase 14 flow\n",
            "scripts/zigux/check-phase14-docs-root-smoke-summary.py": f"#!/usr/bin/env python3\n\"\"\"{DOCS_ROOT_CHECKER_MARKER}\"\"\"\nraise SystemExit(0)\n",
            "scripts/zigux/check-phase14-rollback-threshold-sequencing.py": f"#!/usr/bin/env python3\n\"\"\"{CHECKER_MARKER}\"\"\"\nraise SystemExit(0)\n",
            "scripts/zigux/check-phase14-release-boundary-exact-counts.py": f"#!/usr/bin/env python3\n\"\"\"{RELEASE_BOUNDARY_CHECKER_MARKER}\"\"\"\nraise SystemExit(0)\n",
            "zigux/tests/README.md": "keep the current Phase 14 smoke packet reviewable\n",
            "zigux/tests/phase14_workqueue_bridge.zig": "phase14 workqueue bridge manifest records the boundary-map foothold and remaining gap\n",
            "zigux/tests/phase14_skbuff_bridge.zig": "phase14 skbuff bridge manifest records the boundary-map foothold and frozen ownership gap\n",
            "zigux/tests/phase14_end_to_end_smoke_survey.zig": "phase14 shared smoke survey confirms the current packet surfaces\n",
            "zigux/tests/phase14_ring_buffer_survey.zig": "phase 14 ring-buffer survey manifest records the study-only gap without inventing a port\n",
            "zigux/tests/phase14_rcu_tree_survey.zig": "phase 14 rcu tree survey manifest records the freeze-boundary gap without inventing a bridge\n",
            "kernel/workqueue_bridge.zig": "pub const WorkqueueBridgeLab = struct {};\n",
            "net/core/skbuff_bridge.zig": "pub const SkbuffBridgeLab = struct {};\n",
            "kernel/rcu/tree_bridge.zig": "pub const RcuTreeBridgeLab = struct {};\n",
            WORKFLOW_PATH: "\n".join(
                [
                    "Validate Phase 14 shared smoke packet",
                    "run: make -C zigux phase14-validate",
                    "Run focused Phase 14 smoke shard",
                    "run: make -C zigux phase14-smoke",
                    "Run Phase 14 internal bridge tests",
                    "run: make -C zigux phase14-test",
                ]
            )
            + "\n",
            "zigux/Makefile": "phase14: phase14-validate phase14-smoke phase14-test\n",
            "zigux/tests/phase14_build.zig": "\n".join(
                [
                    *["b.addTest(.{" for _ in range(5)],
                    *["b.addRunArtifact(" for _ in range(5)],
                    'const smoke_step = b.step("phase14-smoke", "Run the focused Phase 14 end-to-end smoke survey")',
                    "smoke_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);",
                    'const test_step = b.step("test", "Run Phase 14 bounded internal bridge tests")',
                    "test_step.dependOn(&run_phase14_workqueue_bridge_tests.step);",
                    "test_step.dependOn(&run_phase14_skbuff_bridge_tests.step);",
                    "test_step.dependOn(&run_phase14_ring_buffer_survey_tests.step);",
                    "test_step.dependOn(&run_phase14_rcu_tree_survey_tests.step);",
                    "test_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);",
                    "phase14-workqueue-bridge-tests",
                    "phase14_workqueue_bridge.zig",
                    "phase14-skbuff-bridge-tests",
                    "phase14_skbuff_bridge.zig",
                    "phase14-ring-buffer-survey-tests",
                    "phase14_ring_buffer_survey.zig",
                    "phase14-rcu-tree-survey-tests",
                    "phase14_rcu_tree_survey.zig",
                    "phase14-end-to-end-smoke-tests",
                    "phase14_end_to_end_smoke_survey.zig",
                ]
            )
            + "\n",
        }
        for rel_path, text in support_files.items():
            write_text(root / rel_path, text)
        write_text(root / "scripts/zigux/validate-phase14.py", read_text(Path(__file__)))

        smoke_lines = [
            "# Phase 14 End-to-End Smoke Survey",
            "PHASE14_VALIDATE_SELF_TEST=python3 scripts/zigux/validate-phase14.py --self-test",
            "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate",
            "PHASE14_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase14.py",
            "PHASE14_BUILD_ENTRYPOINT=zig build test --build-file zigux/tests/phase14_build.zig --summary all",
            "PHASE14_SHARED_SURFACE_COUNT=28",
            "PHASE14_DOC_SURFACE_COUNT=6",
            "PHASE14_SCRIPT_SURFACE_COUNT=5",
            "PHASE14_TEST_SURFACE_COUNT=12",
            "PHASE14_BRIDGE_ROOT_SURFACE_COUNT=3",
            "PHASE14_WORKFLOW_SURFACE_COUNT=1",
            "PHASE14_MAKEFILE_SURFACE_COUNT=1",
            "PHASE14_COMPILE_ARTIFACT_COUNT=5",
            "PHASE14_FOCUSED_SHARD_COUNT=1",
            "PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT=4",
            "kernel/rcu/tree_bridge.zig",
            "This wrapper first runs `python3 scripts/zigux/validate-phase14.py --self-test` and then the shared packet validator.",
            "`Documentation/zigux/phase14-ring-buffer-survey.md` and `zigux/tests/phase14_ring_buffer_manifest.json` agree on lane `P14-L08`",
            "Documentation/zigux/phase14-core-boundary-traceability.md",
        ]
        smoke_lines.extend(compile_matrix_note_row(*row) for row in COMPILE_MATRIX_ROWS)
        write_text(root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md", "\n".join(smoke_lines) + "\n")

        errors = check(root)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1

        broken = load_json(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json")
        broken["compile_shards"] = broken["compile_shards"][:-1]
        write_text(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json", json.dumps(broken, indent=2) + "\n")
        errors = check(root)
        if "phase14 manifest compile_shards drifted from the current five-row compile packet" not in errors:
            print("self-test expected compile_shards drift failure", file=sys.stderr)
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
