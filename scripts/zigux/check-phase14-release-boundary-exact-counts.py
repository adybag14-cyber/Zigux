#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=release_boundary_exact_counts

Fail-closed checker for the shared Phase 14 release-boundary exact counts.
This packet keeps the shared smoke release note aligned with the roadmap and freeze map.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=release_boundary_exact_counts"
REQUIRED_COUNTS = {
    "PHASE14_ROADMAP_ANCHOR_COUNT": 4,
    "PHASE14_STUDY_ONLY_ANCHOR_COUNT": 2,
    "PHASE14_FREEZE_IN_C_GOVERNED_COUNT": 2,
    "PHASE14_SHARED_SMOKE_GATE_COUNT": 1,
    "PHASE14_ACTIVE_DELIVERY_GATE_COUNT": 0,
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


def check(root: Path) -> list[str]:
    errors: list[str] = []

    release_path = root / "Documentation/zigux/phase14-release-boundary-survey.md"
    smoke_path = root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
    freeze_map_path = root / "Documentation/zigux/freeze-map.md"
    roadmap_path = root / "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md"

    for path in (release_path, smoke_path, freeze_map_path, roadmap_path):
        if not path.exists():
            errors.append(f"missing file: {path.relative_to(root).as_posix()}")
    if errors:
        return errors

    release_text = read_text(release_path)
    smoke_text = read_text(smoke_path)
    freeze_map_text = read_text(freeze_map_path)
    roadmap_text = read_text(roadmap_path)

    if MARKER not in read_text(Path(__file__)):
        errors.append("checker marker missing from checker source")

    for marker, expected in REQUIRED_COUNTS.items():
        line = f"- `{marker}={expected}`"
        if line not in release_text:
            errors.append(f"missing exact-count marker in {release_path.relative_to(root).as_posix()}: {marker}={expected}")

    if "- `PHASE14_ANCHOR_PACKET_COUNT=4`" not in smoke_text:
        errors.append("shared smoke survey drifted from the four-anchor packet count")

    roadmap_anchors = extract_bullets(roadmap_text, "Primary Linux anchors:")
    if roadmap_anchors != ROADMAP_PHASE14_ANCHORS:
        errors.append("roadmap Phase 14 anchor list drifted from the four-anchor shared smoke packet")

    freeze_in_c = extract_bullets(freeze_map_text, "Active freeze-in-C targets for the current product plan:")
    if freeze_in_c != FREEZE_IN_C_ANCHORS:
        errors.append("freeze-map freeze-in-C anchors drifted from the expected four-entry governance set")

    boundary_study_only = extract_bullets(freeze_map_text, "Boundary-study-only targets before any direct port decision:")
    if boundary_study_only != BOUNDARY_STUDY_ONLY_ANCHORS:
        errors.append("freeze-map boundary-study-only anchors drifted from the expected two-entry Phase 14 set")

    return errors


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        checker_path = root / "scripts/zigux/check-phase14-release-boundary-exact-counts.py"
        write_text(checker_path, Path(__file__).read_text(encoding="utf-8"))
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
        expected_smoke_text = "# Phase 14 End-to-End Smoke Survey\n- `PHASE14_ANCHOR_PACKET_COUNT=4`\n"
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
                "## Phase 14: Core-Adjacent Bounded Internals",
                "Primary Linux anchors:",
                "- kernel/workqueue.c",
                "- kernel/trace/ring_buffer.c",
                "- net/core/skbuff.c",
                "- kernel/rcu/tree.c",
                "",
            ]
        )
        write_text(root / "Documentation/zigux/phase14-release-boundary-survey.md", expected_release_text)
        write_text(root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md", expected_smoke_text)
        write_text(root / "Documentation/zigux/freeze-map.md", expected_freeze_map_text)
        write_text(root / "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md", expected_roadmap_text)

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
                "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
                "- `PHASE14_SHARED_SMOKE_GATE_COUNT=2`",
            ),
        )
        errors = check(root)
        if not any("PHASE14_SHARED_SMOKE_GATE_COUNT=1" in error for error in errors):
            print("self-test expected count-marker failure when release-boundary counts drifted", file=sys.stderr)
            return 1
        write_text(release_path, expected_release_text)

        smoke_path = root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
        write_text(
            smoke_path,
            read_text(smoke_path).replace(
                "- `PHASE14_ANCHOR_PACKET_COUNT=4`",
                "- `PHASE14_ANCHOR_PACKET_COUNT=3`",
            ),
        )
        errors = check(root)
        if not any("shared smoke survey drifted from the four-anchor packet count" in error for error in errors):
            print("self-test expected failure when shared smoke anchor count drifted", file=sys.stderr)
            return 1
        write_text(smoke_path, expected_smoke_text)

        roadmap_path = root / "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md"
        write_text(
            roadmap_path,
            "\n".join(
                [
                    "## Phase 14: Core-Adjacent Bounded Internals",
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
