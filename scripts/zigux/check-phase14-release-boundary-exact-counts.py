#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=release_boundary_exact_counts

Fail-closed checker for the shared Phase 14 release-boundary exact counts.
This packet keeps the shared smoke release note aligned with the roadmap, freeze map,
and manifest anchor-governance split.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
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
            in error
            for error in errors
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
            in error
            for error in errors
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
            in error
            for error in errors
        ):
            print("self-test expected duplicate smoke-count failure", file=sys.stderr)
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
