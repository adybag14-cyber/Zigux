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
from pathlib import Path

MARKER = "PHASE14_VALIDATE_PACKET=shared_smoke"
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
REQUIRED_SURFACES = {
    "Documentation/zigux/README.md": "Phase 14 notes",
    "Documentation/zigux/phase14-release-boundary-survey.md": "PHASE14_RELEASE_BOUNDARY=present",
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md": "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate",
    TRACEABILITY_PATH: TRACEABILITY_TITLE,
    "Documentation/zigux/freeze-map.md": "kernel/workqueue.c",
    "Documentation/zigux/review-checklist.md": "shared Phase 14 smoke packet",
    "scripts/zigux/README.md": "Phase 14 flow",
    "scripts/zigux/validate-phase14.py": MARKER,
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
    "zigux/tests/phase14_build.zig": ["phase14-smoke"],
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
        "make -C zigux phase14-validate",
    ],
    "kernel/workqueue_bridge.zig": ["pub const WorkqueueBridgeLab"],
    "net/core/skbuff_bridge.zig": ["pub const SkbuffBridgeLab"],
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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
    errors: list[str] = []
    traceability_path = root / TRACEABILITY_PATH
    if not traceability_path.exists():
        return [f"missing file: {TRACEABILITY_PATH}"]

    text = read_text(traceability_path)
    expected_markers, marker_errors = traceability_expected_markers(root)
    errors.extend(marker_errors)
    for marker in expected_markers:
        if marker not in text:
            errors.append(f"missing marker in {TRACEABILITY_PATH}: {marker}")
    return errors


def run_guardrail_checker(root: Path) -> list[str]:
    checker = root / "scripts/zigux/check-phase14-rollback-threshold-sequencing.py"
    if not checker.exists():
        return [f"missing file: {checker.relative_to(root).as_posix()}"]

    result = subprocess.run(
        [sys.executable, str(checker)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return []

    details: list[str] = []
    stderr = [line.strip() for line in result.stderr.splitlines() if line.strip()]
    stdout = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if stderr:
        details.extend(stderr)
    elif stdout:
        details.extend(stdout)
    else:
        details.append("phase14 rollback-threshold sequencing checker failed without output")
    return details


def run_release_boundary_checker(root: Path) -> list[str]:
    checker = root / "scripts/zigux/check-phase14-release-boundary-exact-counts.py"
    if not checker.exists():
        return [f"missing file: {checker.relative_to(root).as_posix()}"]

    result = subprocess.run(
        [sys.executable, str(checker)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return []

    details: list[str] = []
    stderr = [line.strip() for line in result.stderr.splitlines() if line.strip()]
    stdout = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if stderr:
        details.extend(stderr)
    elif stdout:
        details.extend(stdout)
    else:
        details.append("phase14 release-boundary exact-counts checker failed without output")
    return details


def check(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = root / "zigux/tests/phase14_end_to_end_smoke_manifest.json"
    if not manifest_path.exists():
        return [f"missing file: {manifest_path.as_posix()}"]

    errors.extend(run_guardrail_checker(root))
    errors.extend(run_release_boundary_checker(root))

    try:
        manifest = load_json_file(manifest_path)
    except json.JSONDecodeError as exc:
        return [f"invalid json in {manifest_path.as_posix()}: {exc}"]

    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        errors.append("phase14 shared smoke manifest lane_key drifted from the current shared-lane owner")

    commands = manifest.get("commands")
    if commands != REQUIRED_COMMANDS:
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

    errors.extend(check_traceability_note(root))

    return errors


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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
        write_text(
            root / "zigux/tests/phase14_end_to_end_smoke_manifest.json",
            json.dumps(manifest, indent=2) + "\n",
        )
        write_text(
            root / "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
            "#!/usr/bin/env python3\n"
            f"\"\"\"{CHECKER_MARKER}\"\"\"\n"
            "raise SystemExit(0)\n",
        )
        write_text(
            root / "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
            "#!/usr/bin/env python3\n"
            f"\"\"\"{RELEASE_BOUNDARY_CHECKER_MARKER}\"\"\"\n"
            "raise SystemExit(0)\n",
        )

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
                "gaps": [
                    {"id": "phase14-skbuff-live-ownership-blocker", "status": "blocked_on_stay_in_c_evidence"},
                ],
            },
            "zigux/tests/phase14_rcu_tree_manifest.json": {
                "lane_key": "P14-L16",
                "surveyed_commit": "4c889233d157960514b241bcd5aff7cac5fda312",
                "gaps": [
                    {"id": "phase14-rcu-tree-bridge-blocker", "status": "blocked_on_stay_in_c_evidence"},
                ],
            },
            "zigux/tests/phase14_workqueue_bridge_manifest.json": {
                "lane_key": "P14-L04",
                "surveyed_commit": "9e278f632d6d5097cb8cfc2dc61744ae105baa8c",
                "gaps": [
                    {"id": "phase14-workqueue-live-execution-blocker", "status": "blocked_on_stay_in_c_evidence"},
                ],
            },
        }
        for rel_path, data in anchor_manifests.items():
            write_text(root / rel_path, json.dumps(data, indent=2) + "\n")

        expected_markers, errors = traceability_expected_markers(root)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        write_text(root / TRACEABILITY_PATH, "\n".join(expected_markers) + "\n")

        for rel_path, markers in REQUIRED_FILE_MARKERS.items():
            path = root / rel_path
            if path.exists():
                continue
            write_text(path, "\n".join(markers) + "\n")

        errors = check(root)
        if errors:
            print("self-test expected success but failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1

        def expect_traceability_failure(missing_marker: str, expected_error: str, label: str) -> int:
            traceability_path = root / TRACEABILITY_PATH
            traceability_path.write_text(
                traceability_path.read_text(encoding="utf-8").replace(
                    f"{missing_marker}\n",
                    "",
                    1,
                ),
                encoding="utf-8",
            )
            errors = check(root)
            if not errors or not any(expected_error in error for error in errors):
                print(
                    f"self-test expected failure when {label} traceability marker drifted",
                    file=sys.stderr,
                )
                return 1
            write_text(root / TRACEABILITY_PATH, "\n".join(expected_markers) + "\n")
            return 0

        broken_path = root / TRACEABILITY_PATH
        broken_path.write_text(f"{TRACEABILITY_TITLE}\n", encoding="utf-8")
        errors = check(root)
        if not errors or not any(
            "missing marker in Documentation/zigux/phase14-core-boundary-traceability.md: - lane key: `P14-L04`" in error
            for error in errors
        ):
            print("self-test expected failure when workqueue traceability marker drifted", file=sys.stderr)
            return 1

        write_text(root / TRACEABILITY_PATH, "\n".join(expected_markers) + "\n")

        if expect_traceability_failure(
            "- lane key: `P14-L08`",
            "missing marker in Documentation/zigux/phase14-core-boundary-traceability.md: - lane key: `P14-L08`",
            "ring-buffer lane-key",
        ):
            return 1

        if expect_traceability_failure(
            "- ready-next gap: `phase14-ring-buffer-read-page-copy-followup`",
            "missing marker in Documentation/zigux/phase14-core-boundary-traceability.md: - ready-next gap: `phase14-ring-buffer-read-page-copy-followup`",
            "ring-buffer ready-next",
        ):
            return 1

        if expect_traceability_failure(
            "- surveyed commit: `f05e02445443e7743c3675a6f8ca4f70f6e736fb`",
            "missing marker in Documentation/zigux/phase14-core-boundary-traceability.md: - surveyed commit: `f05e02445443e7743c3675a6f8ca4f70f6e736fb`",
            "skbuff surveyed-commit",
        ):
            return 1

        if expect_traceability_failure(
            "- blocked gap: `phase14-rcu-tree-bridge-blocker`",
            "missing marker in Documentation/zigux/phase14-core-boundary-traceability.md: - blocked gap: `phase14-rcu-tree-bridge-blocker`",
            "rcu-tree blocked-gap",
        ):
            return 1

        broken_docs_root_path = root / "Documentation/zigux/README.md"
        broken_docs_root_path.write_text(
            broken_docs_root_path.read_text(encoding="utf-8").replace(
                "Documentation/zigux/phase14-core-boundary-traceability.md\n",
                "",
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "missing marker in Documentation/zigux/README.md: Documentation/zigux/phase14-core-boundary-traceability.md" in error
            for error in errors
        ):
            print("self-test expected failure when docs-root traceability marker drifted", file=sys.stderr)
            return 1

        write_text(
            broken_docs_root_path,
            "\n".join(REQUIRED_FILE_MARKERS["Documentation/zigux/README.md"]) + "\n",
        )

        broken_review_checklist_path = root / "Documentation/zigux/review-checklist.md"
        broken_review_checklist_path.write_text(
            broken_review_checklist_path.read_text(encoding="utf-8").replace(
                "shared Phase 14 smoke packet\n",
                "",
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "missing marker in Documentation/zigux/review-checklist.md: shared Phase 14 smoke packet" in error
            for error in errors
        ):
            print("self-test expected failure when review checklist marker drifted", file=sys.stderr)
            return 1

        write_text(
            broken_review_checklist_path,
            "\n".join(REQUIRED_FILE_MARKERS["Documentation/zigux/review-checklist.md"]) + "\n",
        )

        anchor_cases = [
            (
                "kernel/workqueue.c",
                "missing marker in Documentation/zigux/review-checklist.md: kernel/workqueue.c",
                "workqueue",
            ),
            (
                "kernel/trace/ring_buffer.c",
                "missing marker in Documentation/zigux/review-checklist.md: kernel/trace/ring_buffer.c",
                "ring-buffer",
            ),
            (
                "kernel/rcu/tree.c",
                "missing marker in Documentation/zigux/review-checklist.md: kernel/rcu/tree.c",
                "rcu-tree",
            ),
            (
                "net/core/skbuff.c",
                "missing marker in Documentation/zigux/review-checklist.md: net/core/skbuff.c",
                "skbuff",
            ),
        ]
        for anchor_marker, expected_error, label in anchor_cases:
            broken_review_checklist_path.write_text(
                broken_review_checklist_path.read_text(encoding="utf-8").replace(
                    f"{anchor_marker}\n",
                    "",
                    1,
                ),
                encoding="utf-8",
            )
            errors = check(root)
            if not errors or not any(expected_error in error for error in errors):
                print(
                    f"self-test expected failure when review checklist {label} anchor drifted",
                    file=sys.stderr,
                )
                return 1
            write_text(
                broken_review_checklist_path,
                "\n".join(REQUIRED_FILE_MARKERS["Documentation/zigux/review-checklist.md"]) + "\n",
            )

        broken_scripts_root_path = root / "scripts/zigux/README.md"
        broken_scripts_root_path.write_text(
            broken_scripts_root_path.read_text(encoding="utf-8").replace(
                "Documentation/zigux/phase14-core-boundary-traceability.md\n",
                "",
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "missing marker in scripts/zigux/README.md: Documentation/zigux/phase14-core-boundary-traceability.md" in error
            for error in errors
        ):
            print("self-test expected failure when scripts-root traceability marker drifted", file=sys.stderr)
            return 1

        write_text(
            broken_scripts_root_path,
            "\n".join(REQUIRED_FILE_MARKERS["scripts/zigux/README.md"]) + "\n",
        )

        broken_bridge_path = root / "kernel/workqueue_bridge.zig"
        broken_bridge_path.write_text(
            broken_bridge_path.read_text(encoding="utf-8").replace(
                "pub const WorkqueueBridgeLab",
                "pub const MissingWorkqueueBridgeLab",
            ),
            encoding="utf-8",
        )
        errors = check(root)
        if not errors or not any(
            "missing marker in kernel/workqueue_bridge.zig: pub const WorkqueueBridgeLab" in error
            for error in errors
        ):
            print("self-test expected failure when workqueue bridge marker drifted", file=sys.stderr)
            return 1

        write_text(
            broken_bridge_path,
            "\n".join(REQUIRED_FILE_MARKERS["kernel/workqueue_bridge.zig"]) + "\n",
        )

        broken_manifest_path = root / "zigux/tests/phase14_end_to_end_smoke_manifest.json"
        broken_manifest = json.loads(broken_manifest_path.read_text(encoding="utf-8"))
        for surface in broken_manifest["surfaces"]:
            if surface.get("path") == "Documentation/zigux/review-checklist.md":
                surface["required_marker"] = "shared Phase 14 packet"
                break
        broken_manifest_path.write_text(json.dumps(broken_manifest, indent=2) + "\n", encoding="utf-8")
        errors = check(root)
        if not errors or not any(
            "manifest surface drift for Documentation/zigux/review-checklist.md" in error
            for error in errors
        ):
            print("self-test expected failure when manifest review-checklist surface drifted", file=sys.stderr)
            return 1

        broken_manifest["lane_key"] = EXPECTED_LANE_KEY
        for surface in broken_manifest["surfaces"]:
            if surface.get("path") == "Documentation/zigux/review-checklist.md":
                surface["required_marker"] = REQUIRED_SURFACES["Documentation/zigux/review-checklist.md"]
                break
        broken_manifest_path.write_text(json.dumps(broken_manifest, indent=2) + "\n", encoding="utf-8")

        broken_manifest = json.loads(broken_manifest_path.read_text(encoding="utf-8"))
        broken_manifest["lane_key"] = "core-adjacent"
        broken_manifest_path.write_text(json.dumps(broken_manifest, indent=2) + "\n", encoding="utf-8")
        errors = check(root)
        if not errors or not any("lane_key drifted" in error for error in errors):
            print("self-test expected failure when manifest lane owner drifted", file=sys.stderr)
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
