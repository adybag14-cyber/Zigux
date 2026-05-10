#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=release_boundary_exact_counts

Fail-closed checker for the shared Phase 14 release-boundary exact counts.
This packet keeps the shared smoke release note aligned with the roadmap, freeze map,
manifest surface accounting, and manifest anchor-governance split.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=release_boundary_exact_counts"
PHASE14_SECTION_HEADING = "## Phase 14: Core-Adjacent Bounded Internals"
REQUIRED_COUNTS = {
    "PHASE14_ROADMAP_ANCHOR_COUNT": 4,
    "PHASE14_STUDY_ONLY_ANCHOR_COUNT": 2,
    "PHASE14_FREEZE_IN_C_GOVERNED_COUNT": 2,
    "PHASE14_SHARED_SMOKE_GATE_COUNT": 1,
    "PHASE14_ACTIVE_DELIVERY_GATE_COUNT": 0,
}
EXPECTED_SURFACE_COUNTS = {
    "PHASE14_SHARED_SURFACE_COUNT": 29,
    "PHASE14_DOC_SURFACE_COUNT": 6,
    "PHASE14_SCRIPT_SURFACE_COUNT": 5,
    "PHASE14_TEST_SURFACE_COUNT": 13,
    "PHASE14_BRIDGE_ROOT_SURFACE_COUNT": 3,
    "PHASE14_WORKFLOW_SURFACE_COUNT": 1,
    "PHASE14_MAKEFILE_SURFACE_COUNT": 1,
}
ROADMAP_PHASE14_ANCHORS = [
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
    "net/core/skbuff.c",
    "kernel/rcu/tree.c",
]
FREEZE_IN_C_ANCHORS = [
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
]
BOUNDARY_STUDY_ONLY_ANCHORS = [
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
]
MANIFEST_STUDY_ONLY_ANCHORS = [
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
]
MANIFEST_FREEZE_IN_C_ANCHORS = [
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
]
MANIFEST_BLOCKED_ANCHORS = [
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
]
SURFACE_CATEGORY_KEYS = {
    "Documentation/zigux/": "PHASE14_DOC_SURFACE_COUNT",
    "scripts/zigux/": "PHASE14_SCRIPT_SURFACE_COUNT",
    "zigux/tests/": "PHASE14_TEST_SURFACE_COUNT",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_bullets(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    in_section = False
    items: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == heading:
            in_section = True
            continue
        if not in_section:
            continue
        if items and stripped and not stripped.startswith("- "):
            break
        if stripped.startswith("- "):
            items.append(stripped[2:])
    return items


def extract_section(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    in_section = False
    collected: list[str] = []
    for line in lines:
        if line.strip() == heading:
            in_section = True
            collected.append(line)
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            collected.append(line)
    if not collected:
        return None
    return "\n".join(collected) + "\n"


def require_exact_line_count(errors: list[str], rel_path: str, text: str, line: str, label: str) -> None:
    actual_count = text.count(line)
    if actual_count != 1:
        errors.append(f"marker count drift in {rel_path}: {label} (expected 1, found {actual_count})")


def classify_surface_path(path: str) -> str | None:
    if path == ".github/workflows/zigux-bootstrap.yml":
        return "PHASE14_WORKFLOW_SURFACE_COUNT"
    if path == "zigux/Makefile":
        return "PHASE14_MAKEFILE_SURFACE_COUNT"
    if path.startswith("kernel/") or path.startswith("net/core/"):
        return "PHASE14_BRIDGE_ROOT_SURFACE_COUNT"
    for prefix, category in SURFACE_CATEGORY_KEYS.items():
        if path.startswith(prefix):
            return category
    return None


def collect_surface_counts(manifest: dict) -> tuple[Counter[str], list[str]]:
    errors: list[str] = []
    counts: Counter[str] = Counter()
    raw_surfaces = manifest.get("surfaces")
    if not isinstance(raw_surfaces, list):
        return counts, ["phase14 shared smoke manifest surfaces payload is not a list"]
    for surface in raw_surfaces:
        if not isinstance(surface, dict):
            errors.append("phase14 shared smoke manifest surface entry is not an object")
            continue
        path = surface.get("path")
        if not isinstance(path, str):
            errors.append("phase14 shared smoke manifest surface entry is missing a string path")
            continue
        category = classify_surface_path(path)
        if category is None:
            errors.append(f"phase14 shared smoke manifest surface escaped the expected categories: {path}")
            continue
        counts[category] += 1
    counts["PHASE14_SHARED_SURFACE_COUNT"] = sum(
        counts[key] for key in EXPECTED_SURFACE_COUNTS if key != "PHASE14_SHARED_SURFACE_COUNT"
    )
    return counts, errors


def check(root: Path) -> list[str]:
    errors: list[str] = []

    release_path = root / "Documentation/zigux/phase14-release-boundary-survey.md"
    smoke_path = root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
    freeze_map_path = root / "Documentation/zigux/freeze-map.md"
    roadmap_path = root / "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md"
    manifest_path = root / "zigux/tests/phase14_end_to_end_smoke_manifest.json"

    for path in (release_path, smoke_path, freeze_map_path, roadmap_path, manifest_path):
        if not path.exists():
            errors.append(f"missing file: {path.relative_to(root).as_posix()}")
    if errors:
        return errors

    release_text = read_text(release_path)
    smoke_text = read_text(smoke_path)
    freeze_map_text = read_text(freeze_map_path)
    roadmap_text = read_text(roadmap_path)
    try:
        manifest = json.loads(read_text(manifest_path))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid json in {manifest_path.relative_to(root).as_posix()}: {exc}")
        return errors

    if MARKER not in read_text(Path(__file__)):
        errors.append("checker marker missing from checker source")

    for marker, expected in REQUIRED_COUNTS.items():
        line = f"- `{marker}={expected}`"
        require_exact_line_count(
            errors,
            release_path.relative_to(root).as_posix(),
            release_text,
            line,
            f"{marker}={expected}",
        )

    require_exact_line_count(
        errors,
        smoke_path.relative_to(root).as_posix(),
        smoke_text,
        "- `PHASE14_ANCHOR_PACKET_COUNT=4`",
        "PHASE14_ANCHOR_PACKET_COUNT=4",
    )
    for marker, expected in EXPECTED_SURFACE_COUNTS.items():
        line = f"- `{marker}={expected}`"
        require_exact_line_count(
            errors,
            smoke_path.relative_to(root).as_posix(),
            smoke_text,
            line,
            f"{marker}={expected}",
        )

    phase14_section = extract_section(roadmap_text, PHASE14_SECTION_HEADING)
    if phase14_section is None:
        errors.append("missing Phase 14 roadmap section in zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")
    else:
        roadmap_anchors = extract_bullets(phase14_section, "Primary Linux anchors:")
        if roadmap_anchors != ROADMAP_PHASE14_ANCHORS:
            errors.append("roadmap Phase 14 anchor list drifted from the four-anchor shared smoke packet")

    freeze_in_c = extract_bullets(freeze_map_text, "Active freeze-in-C targets for the current product plan:")
    if freeze_in_c != FREEZE_IN_C_ANCHORS:
        errors.append("freeze-map freeze-in-C anchors drifted from the expected four-entry governance set")

    boundary_study_only = extract_bullets(freeze_map_text, "Boundary-study-only targets before any direct port decision:")
    if boundary_study_only != BOUNDARY_STUDY_ONLY_ANCHORS:
        errors.append("freeze-map boundary-study-only anchors drifted from the expected two-entry Phase 14 set")

    if manifest.get("study_only_anchors") != MANIFEST_STUDY_ONLY_ANCHORS:
        errors.append("phase14 manifest study_only_anchors drifted from the expected two-entry boundary-study-only set")

    if manifest.get("freeze_in_c_anchors") != MANIFEST_FREEZE_IN_C_ANCHORS:
        errors.append("phase14 manifest freeze_in_c_anchors drifted from the expected two-entry freeze-governed set")

    if manifest.get("blocked_anchors") != MANIFEST_BLOCKED_ANCHORS:
        errors.append("phase14 manifest blocked_anchors drifted from the combined study-only plus freeze-governed set")

    surface_counts, surface_errors = collect_surface_counts(manifest)
    errors.extend(surface_errors)
    for marker, expected in EXPECTED_SURFACE_COUNTS.items():
        actual = surface_counts.get(marker, 0)
        if actual != expected:
            errors.append(f"phase14 manifest {marker} drifted from the expected {expected} surface count (found {actual})")

    return errors


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        checker_path = root / "scripts/zigux/check-phase14-release-boundary-exact-counts.py"
        current_checker_path = Path(__file__)
        original_checker_source = current_checker_path.read_text(encoding="utf-8")
        write_text(checker_path, original_checker_source)
        expected_release_text = "\n".join(
            [
                "# Phase 14 Release Boundary Survey",
                "## Current release reading",
                "- `PHASE14_ROADMAP_ANCHOR_COUNT=4`",
                "- `PHASE14_STUDY_ONLY_ANCHOR_COUNT=2`",
                "- `PHASE14_FREEZE_IN_C_GOVERNED_COUNT=2`",
                "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
                "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
                "",
            ]
        )
        expected_smoke_text = "\n".join(
            [
                "# Phase 14 End-to-End Smoke Survey",
                "- `PHASE14_ANCHOR_PACKET_COUNT=4`",
                "- `PHASE14_SHARED_SURFACE_COUNT=29`",
                "- `PHASE14_DOC_SURFACE_COUNT=6`",
                "- `PHASE14_SCRIPT_SURFACE_COUNT=5`",
                "- `PHASE14_TEST_SURFACE_COUNT=13`",
                "- `PHASE14_BRIDGE_ROOT_SURFACE_COUNT=3`",
                "- `PHASE14_WORKFLOW_SURFACE_COUNT=1`",
                "- `PHASE14_MAKEFILE_SURFACE_COUNT=1`",
                "",
            ]
        )
        expected_freeze_map_text = "\n".join(
            [
                "# Freeze Map",
                "Active freeze-in-C targets for the current product plan:",
                "- kernel/sched/core.c",
                "- mm/page_alloc.c",
                "- kernel/rcu/tree.c",
                "- net/core/skbuff.c",
                "",
                "Boundary-study-only targets before any direct port decision:",
                "- kernel/workqueue.c",
                "- kernel/trace/ring_buffer.c",
                "",
            ]
        )
        expected_roadmap_text = "\n".join(
            [
                "## Phase 3: ABI and Interop Substrate",
                "Primary Linux anchors:",
                "- rust/exports.c",
                "- lib/bitmap.c",
                "- lib/rbtree.c",
                "- lib/cpumask.c",
                "",
                PHASE14_SECTION_HEADING,
                "Primary Linux anchors:",
                "- kernel/workqueue.c",
                "- kernel/trace/ring_buffer.c",
                "- net/core/skbuff.c",
                "- kernel/rcu/tree.c",
                "",
            ]
        )
        expected_manifest = {
            "study_only_anchors": [
                "kernel/workqueue.c",
                "kernel/trace/ring_buffer.c",
            ],
            "freeze_in_c_anchors": [
                "kernel/rcu/tree.c",
                "net/core/skbuff.c",
            ],
            "blocked_anchors": [
                "kernel/workqueue.c",
                "kernel/trace/ring_buffer.c",
                "kernel/rcu/tree.c",
                "net/core/skbuff.c",
            ],
            "surfaces": [
                {"path": "Documentation/zigux/README.md", "required_marker": "Phase 14 notes"},
                {"path": "Documentation/zigux/phase14-release-boundary-survey.md", "required_marker": "PHASE14_RELEASE_BOUNDARY=present"},
                {"path": "Documentation/zigux/phase14-end-to-end-smoke-survey.md", "required_marker": "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate"},
                {"path": "Documentation/zigux/phase14-core-boundary-traceability.md", "required_marker": "# Phase 14 Core Boundary Traceability"},
                {"path": "Documentation/zigux/freeze-map.md", "required_marker": "kernel/workqueue.c"},
                {"path": "Documentation/zigux/review-checklist.md", "required_marker": "shared Phase 14 smoke packet"},
                {"path": "scripts/zigux/README.md", "required_marker": "Phase 14 flow"},
                {"path": "scripts/zigux/validate-phase14.py", "required_marker": "PHASE14_VALIDATE_PACKET=shared_smoke"},
                {"path": "scripts/zigux/check-phase14-docs-root-smoke-summary.py", "required_marker": "PHASE14_CHECK_PACKET=docs_root_smoke_summary"},
                {"path": "scripts/zigux/check-phase14-rollback-threshold-sequencing.py", "required_marker": "PHASE14_CHECK_PACKET=rollback_threshold_sequencing"},
                {"path": "scripts/zigux/check-phase14-release-boundary-exact-counts.py", "required_marker": "PHASE14_CHECK_PACKET=release_boundary_exact_counts"},
                {"path": "zigux/tests/README.md", "required_marker": "keep the current Phase 14 smoke packet reviewable"},
                {"path": "zigux/tests/phase14_build.zig", "required_marker": "phase14-smoke"},
                {"path": "zigux/Makefile", "required_marker": "phase14: phase14-validate phase14-smoke phase14-test"},
                {"path": "zigux/tests/phase14_workqueue_bridge.zig", "required_marker": "phase14 workqueue bridge manifest records the boundary-map foothold and remaining gap"},
                {"path": "zigux/tests/phase14_workqueue_reviewability.zig", "required_marker": "phase14 workqueue reviewability guard keeps the shared reviewer surface aligned"},
                {"path": "zigux/tests/phase14_skbuff_bridge.zig", "required_marker": "phase14 skbuff bridge manifest records the boundary-map foothold and frozen ownership gap"},
                {"path": "zigux/tests/phase14_workqueue_bridge_manifest.json", "required_marker": "phase14-workqueue-live-execution-blocker"},
                {"path": "zigux/tests/phase14_skbuff_bridge_manifest.json", "required_marker": "phase14-skbuff-live-ownership-blocker"},
                {"path": "zigux/tests/phase14_end_to_end_smoke_survey.zig", "required_marker": "phase14 shared smoke survey confirms the current packet surfaces"},
                {"path": "zigux/tests/phase14_end_to_end_smoke_manifest.json", "required_marker": "phase14_shared_smoke_packet"},
                {"path": "zigux/tests/phase14_ring_buffer_manifest.json", "required_marker": "phase14-ring-buffer-zig-port-blocker"},
                {"path": "zigux/tests/phase14_ring_buffer_survey.zig", "required_marker": "phase 14 ring-buffer survey manifest records the study-only gap without inventing a port"},
                {"path": "zigux/tests/phase14_rcu_tree_manifest.json", "required_marker": "phase14-rcu-tree-bridge-blocker"},
                {"path": "zigux/tests/phase14_rcu_tree_survey.zig", "required_marker": "phase 14 rcu tree survey manifest records the freeze-boundary gap without inventing a bridge"},
                {"path": ".github/workflows/zigux-bootstrap.yml", "required_marker": "Run focused Phase 14 smoke shard"},
                {"path": "kernel/workqueue_bridge.zig", "required_marker": "pub const WorkqueueBridgeLab"},
                {"path": "net/core/skbuff_bridge.zig", "required_marker": "pub const SkbuffBridgeLab"},
                {"path": "kernel/rcu/tree_bridge.zig", "required_marker": "pub const RcuTreeBridgeLab"},
            ],
        }
        write_text(root / "Documentation/zigux/phase14-release-boundary-survey.md", expected_release_text)
        write_text(root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md", expected_smoke_text)
        write_text(root / "Documentation/zigux/freeze-map.md", expected_freeze_map_text)
        write_text(root / "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md", expected_roadmap_text)
        manifest_path = root / "zigux/tests/phase14_end_to_end_smoke_manifest.json"
        write_text(manifest_path, json.dumps(expected_manifest, indent=2) + "\n")

        errors = check(root)
        if errors:
            print("self-test expected success but failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1

        release_path = root / "Documentation/zigux/phase14-release-boundary-survey.md"
        write_text(
            release_path,
            read_text(release_path).replace(
                "- `PHASE14_ROADMAP_ANCHOR_COUNT=4`\n",
                "- `PHASE14_ROADMAP_ANCHOR_COUNT=4`\n- `PHASE14_ROADMAP_ANCHOR_COUNT=4`\n",
                1,
            ),
        )
        errors = check(root)
        if not any(
            "marker count drift in Documentation/zigux/phase14-release-boundary-survey.md: PHASE14_ROADMAP_ANCHOR_COUNT=4 (expected 1, found 2)"
            in error for error in errors
        ):
            print("self-test expected duplicate release-count failure", file=sys.stderr)
            return 1
        write_text(release_path, expected_release_text)

        write_text(
            release_path,
            read_text(release_path).replace(
                "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`\n",
                "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`\n- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`\n",
                1,
            ),
        )
        errors = check(root)
        if not any(
            "marker count drift in Documentation/zigux/phase14-release-boundary-survey.md: PHASE14_SHARED_SMOKE_GATE_COUNT=1 (expected 1, found 2)"
            in error for error in errors
        ):
            print("self-test expected duplicate shared-smoke gate count failure", file=sys.stderr)
            return 1
        write_text(release_path, expected_release_text)

        smoke_path = root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
        write_text(
            smoke_path,
            read_text(smoke_path).replace(
                "- `PHASE14_ANCHOR_PACKET_COUNT=4`\n",
                "- `PHASE14_ANCHOR_PACKET_COUNT=4`\n- `PHASE14_ANCHOR_PACKET_COUNT=4`\n",
                1,
            ),
        )
        errors = check(root)
        if not any(
            "marker count drift in Documentation/zigux/phase14-end-to-end-smoke-survey.md: PHASE14_ANCHOR_PACKET_COUNT=4 (expected 1, found 2)"
            in error for error in errors
        ):
            print("self-test expected duplicate smoke-count failure", file=sys.stderr)
            return 1
        write_text(smoke_path, expected_smoke_text)

        write_text(
            smoke_path,
            read_text(smoke_path).replace(
                "- `PHASE14_SHARED_SURFACE_COUNT=29`\n",
                "- `PHASE14_SHARED_SURFACE_COUNT=29`\n- `PHASE14_SHARED_SURFACE_COUNT=29`\n",
                1,
            ),
        )
        errors = check(root)
        if not any(
            "marker count drift in Documentation/zigux/phase14-end-to-end-smoke-survey.md: PHASE14_SHARED_SURFACE_COUNT=29 (expected 1, found 2)"
            in error for error in errors
        ):
            print("self-test expected duplicate shared-surface-count failure", file=sys.stderr)
            return 1
        write_text(smoke_path, expected_smoke_text)

        def expect_release_count_failure(old_line: str, new_line: str, expected_error: str, label: str) -> int:
            write_text(
                release_path,
                read_text(release_path).replace(old_line, new_line, 1),
            )
            errors = check(root)
            if not any(expected_error in error for error in errors):
                print(f"self-test expected failure when {label} drifted", file=sys.stderr)
                return 1
            write_text(release_path, expected_release_text)
            return 0

        release_count_cases = [
            (
                "- `PHASE14_ROADMAP_ANCHOR_COUNT=4`",
                "- `PHASE14_ROADMAP_ANCHOR_COUNT=3`",
                "PHASE14_ROADMAP_ANCHOR_COUNT=4",
                "roadmap anchor count marker",
            ),
            (
                "- `PHASE14_STUDY_ONLY_ANCHOR_COUNT=2`",
                "- `PHASE14_STUDY_ONLY_ANCHOR_COUNT=1`",
                "PHASE14_STUDY_ONLY_ANCHOR_COUNT=2",
                "study-only anchor count marker",
            ),
            (
                "- `PHASE14_FREEZE_IN_C_GOVERNED_COUNT=2`",
                "- `PHASE14_FREEZE_IN_C_GOVERNED_COUNT=1`",
                "PHASE14_FREEZE_IN_C_GOVERNED_COUNT=2",
                "freeze-in-C governed count marker",
            ),
            (
                "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
                "- `PHASE14_SHARED_SMOKE_GATE_COUNT=2`",
                "PHASE14_SHARED_SMOKE_GATE_COUNT=1",
                "shared smoke gate count marker",
            ),
            (
                "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
                "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=1`",
                "PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0",
                "active-delivery gate count marker",
            ),
        ]
        for old_line, new_line, expected_error, label in release_count_cases:
            if expect_release_count_failure(old_line, new_line, expected_error, label):
                return 1

        write_text(
            smoke_path,
            read_text(smoke_path).replace(
                "- `PHASE14_ANCHOR_PACKET_COUNT=4`",
                "- `PHASE14_ANCHOR_PACKET_COUNT=3`",
            ),
        )
        errors = check(root)
        if not any("marker count drift in Documentation/zigux/phase14-end-to-end-smoke-survey.md: PHASE14_ANCHOR_PACKET_COUNT=4 (expected 1, found 0)" in error for error in errors):
            print("self-test expected failure when shared smoke anchor count drifted", file=sys.stderr)
            return 1
        write_text(smoke_path, expected_smoke_text)

        write_text(
            smoke_path,
            read_text(smoke_path).replace(
                "- `PHASE14_DOC_SURFACE_COUNT=6`",
                "- `PHASE14_DOC_SURFACE_COUNT=5`",
            ),
        )
        errors = check(root)
        if not any("marker count drift in Documentation/zigux/phase14-end-to-end-smoke-survey.md: PHASE14_DOC_SURFACE_COUNT=6 (expected 1, found 0)" in error for error in errors):
            print("self-test expected failure when shared smoke docs surface count drifted", file=sys.stderr)
            return 1
        write_text(smoke_path, expected_smoke_text)

        roadmap_path = root / "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md"
        write_text(
            roadmap_path,
            "\n".join(
                [
                    "## Phase 3: ABI and Interop Substrate",
                    "Primary Linux anchors:",
                    "- rust/exports.c",
                    "- lib/bitmap.c",
                    "- lib/rbtree.c",
                    "- lib/cpumask.c",
                    "",
                ]
            ),
        )
        errors = check(root)
        if not any("missing Phase 14 roadmap section in zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md" in error for error in errors):
            print("self-test expected failure when the Phase 14 roadmap section was missing", file=sys.stderr)
            return 1
        write_text(roadmap_path, expected_roadmap_text)

        write_text(
            roadmap_path,
            "\n".join(
                [
                    "## Phase 3: ABI and Interop Substrate",
                    "Primary Linux anchors:",
                    "- rust/exports.c",
                    "- lib/bitmap.c",
                    "- lib/rbtree.c",
                    "- lib/cpumask.c",
                    "",
                    PHASE14_SECTION_HEADING,
                    "Primary Linux anchors:",
                    "- kernel/workqueue.c",
                    "- kernel/trace/ring_buffer.c",
                    "- kernel/rcu/tree.c",
                    "",
                ]
            ),
        )
        errors = check(root)
        if not any("roadmap Phase 14 anchor list drifted from the four-anchor shared smoke packet" in error for error in errors):
            print("self-test expected failure when an earlier roadmap anchor block masked a drifted Phase 14 section", file=sys.stderr)
            return 1
        write_text(roadmap_path, expected_roadmap_text)

        write_text(
            roadmap_path,
            "\n".join(
                [
                    "## Phase 3: ABI and Interop Substrate",
                    "Primary Linux anchors:",
                    "- rust/exports.c",
                    "- lib/bitmap.c",
                    "- lib/rbtree.c",
                    "- lib/cpumask.c",
                    "",
                    PHASE14_SECTION_HEADING,
                    "Primary Linux anchors:",
                    "- kernel/workqueue.c",
                    "- kernel/trace/ring_buffer.c",
                    "- kernel/rcu/tree.c",
                    "",
                ]
            ),
        )
        errors = check(root)
        if not any("roadmap Phase 14 anchor list drifted from the four-anchor shared smoke packet" in error for error in errors):
            print("self-test expected failure when roadmap anchor inventory drifted", file=sys.stderr)
            return 1
        write_text(roadmap_path, expected_roadmap_text)

        freeze_map_path = root / "Documentation/zigux/freeze-map.md"
        write_text(
            freeze_map_path,
            read_text(freeze_map_path).replace(
                "- net/core/skbuff.c",
                "- net/core/skbuff_fastpath.c",
                1,
            ),
        )
        errors = check(root)
        if not any("freeze-map freeze-in-C anchors drifted from the expected four-entry governance set" in error for error in errors):
            print("self-test expected failure when freeze-map freeze-in-C anchors drifted", file=sys.stderr)
            return 1
        write_text(freeze_map_path, expected_freeze_map_text)

        write_text(
            freeze_map_path,
            read_text(freeze_map_path).replace(
                "- kernel/trace/ring_buffer.c",
                "- kernel/trace/ring_buffer_iter.c",
                1,
            ),
        )
        errors = check(root)
        if not any("freeze-map boundary-study-only anchors drifted from the expected two-entry Phase 14 set" in error for error in errors):
            print("self-test expected failure when freeze-map boundary-study-only anchors drifted", file=sys.stderr)
            return 1
        write_text(freeze_map_path, expected_freeze_map_text)

        write_text(
            freeze_map_path,
            read_text(freeze_map_path).replace(
                "- kernel/workqueue.c\n",
                "- kernel/workqueue.c\n- kernel/workqueue.c\n",
                1,
            ),
        )
        errors = check(root)
        if not any("freeze-map boundary-study-only anchors drifted from the expected two-entry Phase 14 set" in error for error in errors):
            print("self-test expected failure when freeze-map boundary-study-only anchors duplicated", file=sys.stderr)
            return 1
        write_text(freeze_map_path, expected_freeze_map_text)

        manifest_data = json.loads(read_text(manifest_path))
        manifest_data["study_only_anchors"] = [
            "kernel/workqueue.c",
            "kernel/trace/ring_buffer_iter.c",
        ]
        write_text(manifest_path, json.dumps(manifest_data, indent=2) + "\n")
        errors = check(root)
        if not any("phase14 manifest study_only_anchors drifted from the expected two-entry boundary-study-only set" in error for error in errors):
            print("self-test expected failure when manifest study-only anchors drifted", file=sys.stderr)
            return 1
        write_text(manifest_path, json.dumps(expected_manifest, indent=2) + "\n")

        manifest_data = json.loads(read_text(manifest_path))
        manifest_data["freeze_in_c_anchors"] = [
            "kernel/rcu/tree.c",
            "net/core/skbuff_fastpath.c",
        ]
        write_text(manifest_path, json.dumps(manifest_data, indent=2) + "\n")
        errors = check(root)
        if not any("phase14 manifest freeze_in_c_anchors drifted from the expected two-entry freeze-governed set" in error for error in errors):
            print("self-test expected failure when manifest freeze-in-C anchors drifted", file=sys.stderr)
            return 1
        write_text(manifest_path, json.dumps(expected_manifest, indent=2) + "\n")

        manifest_data = json.loads(read_text(manifest_path))
        manifest_data["blocked_anchors"] = [
            "kernel/workqueue.c",
            "kernel/trace/ring_buffer.c",
            "kernel/rcu/tree.c",
            "net/core/skbuff_fastpath.c",
        ]
        write_text(manifest_path, json.dumps(manifest_data, indent=2) + "\n")
        errors = check(root)
        if not any("phase14 manifest blocked_anchors drifted from the combined study-only plus freeze-governed set" in error for error in errors):
            print("self-test expected failure when manifest blocked anchors drifted", file=sys.stderr)
            return 1
        write_text(manifest_path, json.dumps(expected_manifest, indent=2) + "\n")

        manifest_data = json.loads(read_text(manifest_path))
        manifest_data["surfaces"] = "not-a-list"
        write_text(manifest_path, json.dumps(manifest_data, indent=2) + "\n")
        errors = check(root)
        if "phase14 shared smoke manifest surfaces payload is not a list" not in errors:
            print("self-test expected non-list shared smoke manifest surfaces failure", file=sys.stderr)
            return 1
        write_text(manifest_path, json.dumps(expected_manifest, indent=2) + "\n")

        manifest_data = json.loads(read_text(manifest_path))
        manifest_data["surfaces"] = [17]
        write_text(manifest_path, json.dumps(manifest_data, indent=2) + "\n")
        errors = check(root)
        if "phase14 shared smoke manifest surface entry is not an object" not in errors:
            print("self-test expected non-object shared smoke manifest surfaces failure", file=sys.stderr)
            return 1
        write_text(manifest_path, json.dumps(expected_manifest, indent=2) + "\n")

        manifest_data = json.loads(read_text(manifest_path))
        manifest_data["surfaces"] = [{"required_marker": "Phase 14 notes"}]
        write_text(manifest_path, json.dumps(manifest_data, indent=2) + "\n")
        errors = check(root)
        if "phase14 shared smoke manifest surface entry is missing a string path" not in errors:
            print("self-test expected missing-path shared smoke manifest surface failure", file=sys.stderr)
            return 1
        write_text(manifest_path, json.dumps(expected_manifest, indent=2) + "\n")

        manifest_data = json.loads(read_text(manifest_path))
        manifest_data["surfaces"] = [
            surface for surface in manifest_data["surfaces"]
            if surface.get("path") != ".github/workflows/zigux-bootstrap.yml"
        ]
        write_text(manifest_path, json.dumps(manifest_data, indent=2) + "\n")
        errors = check(root)
        if not any("phase14 manifest PHASE14_SHARED_SURFACE_COUNT drifted from the expected 29 surface count (found 28)" in error for error in errors):
            print("self-test expected shared surface count drift failure when workflow surface disappeared", file=sys.stderr)
            return 1
        if not any("phase14 manifest PHASE14_WORKFLOW_SURFACE_COUNT drifted from the expected 1 surface count (found 0)" in error for error in errors):
            print("self-test expected workflow surface count drift failure", file=sys.stderr)
            return 1
        write_text(manifest_path, json.dumps(expected_manifest, indent=2) + "\n")

        manifest_data = json.loads(read_text(manifest_path))
        manifest_data["surfaces"] = manifest_data["surfaces"][:-1]
        write_text(manifest_path, json.dumps(manifest_data, indent=2) + "\n")
        errors = check(root)
        if not any("phase14 manifest PHASE14_SHARED_SURFACE_COUNT drifted from the expected 29 surface count (found 28)" in error for error in errors):
            print("self-test expected shared surface count drift failure", file=sys.stderr)
            return 1
        if not any("phase14 manifest PHASE14_BRIDGE_ROOT_SURFACE_COUNT drifted from the expected 3 surface count (found 2)" in error for error in errors):
            print("self-test expected bridge-root surface count drift failure", file=sys.stderr)
            return 1
        write_text(manifest_path, json.dumps(expected_manifest, indent=2) + "\n")

        manifest_data = json.loads(read_text(manifest_path))
        manifest_data["surfaces"].append(
            {
                "path": "zigux/helpers/phase14_extra_note.zig",
                "required_marker": "phase14 extra drift",
            }
        )
        write_text(manifest_path, json.dumps(manifest_data, indent=2) + "\n")
        errors = check(root)
        if "phase14 shared smoke manifest surface escaped the expected categories: zigux/helpers/phase14_extra_note.zig" not in errors:
            print("self-test expected uncategorized shared smoke manifest surface failure", file=sys.stderr)
            return 1
        write_text(manifest_path, json.dumps(expected_manifest, indent=2) + "\n")

        write_text(manifest_path, "{\n")
        errors = check(root)
        if not any("invalid json in zigux/tests/phase14_end_to_end_smoke_manifest.json:" in error for error in errors):
            print("self-test expected invalid shared smoke manifest json failure", file=sys.stderr)
            return 1
        write_text(manifest_path, json.dumps(expected_manifest, indent=2) + "\n")

        manifest_path.unlink()
        errors = check(root)
        if not any("missing file: zigux/tests/phase14_end_to_end_smoke_manifest.json" in error for error in errors):
            print("self-test expected missing shared smoke manifest failure", file=sys.stderr)
            return 1
        write_text(manifest_path, json.dumps(expected_manifest, indent=2) + "\n")

        release_path.unlink()
        errors = check(root)
        if not any("missing file: Documentation/zigux/phase14-release-boundary-survey.md" in error for error in errors):
            print("self-test expected missing release-boundary survey failure", file=sys.stderr)
            return 1
        write_text(release_path, expected_release_text)

        smoke_path.unlink()
        errors = check(root)
        if not any("missing file: Documentation/zigux/phase14-end-to-end-smoke-survey.md" in error for error in errors):
            print("self-test expected missing shared smoke survey failure", file=sys.stderr)
            return 1
        write_text(smoke_path, expected_smoke_text)

        freeze_map_path.unlink()
        errors = check(root)
        if not any("missing file: Documentation/zigux/freeze-map.md" in error for error in errors):
            print("self-test expected missing freeze-map failure", file=sys.stderr)
            return 1
        write_text(freeze_map_path, expected_freeze_map_text)

        roadmap_path.unlink()
        errors = check(root)
        if not any("missing file: zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md" in error for error in errors):
            print("self-test expected missing roadmap failure", file=sys.stderr)
            return 1
        write_text(roadmap_path, expected_roadmap_text)

        write_text(current_checker_path, original_checker_source.replace(MARKER, "PHASE14_CHECK_PACKET=broken_marker"))
        errors = check(root)
        if not any("checker marker missing from checker source" in error for error in errors):
            print("self-test expected checker-marker failure", file=sys.stderr)
            write_text(current_checker_path, original_checker_source)
            return 1
        write_text(current_checker_path, original_checker_source)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()

    errors = check(repo_root())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("phase14 release-boundary exact counts validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
