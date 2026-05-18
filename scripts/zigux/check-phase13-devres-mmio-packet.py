#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SLICE_PATH = Path("Documentation/zigux/phase13-devres-slice.md")
PLANNER_NOTE_PATH = Path("Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md")
DMA_REPLAY_PATH = Path("zigux/tests/phase13_devres_dma_coherent.zig")
PLANNER_REPLAY_PATH = Path("zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig")
PLANNER_MANIFEST_PATH = Path("zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json")

REQUIRED_FILES = [
    SLICE_PATH,
    PLANNER_NOTE_PATH,
    DMA_REPLAY_PATH,
    PLANNER_REPLAY_PATH,
    PLANNER_MANIFEST_PATH,
]

SLICE_MARKERS = [
    "# Phase 13 devres Slice",
    "`Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, and `zigux/tests/phase13_devres_manifest.json` remain repo-reality gaps rather than described here as shipped current-`master` evidence",
    "`scripts/zigux/check-phase13-devres-packet-alignment.py` stays in the same repo-reality gaps bucket",
    "older `scripts/zigux/check-phase13-devres-packet.py` wording should stay treated as stale history rather than as the active checker label",
    "`zigux/tests/phase13_devres_dma_coherent.zig` now materializes one direct replay surface for the planning-only DMA and scatterlist boundary",
    "bounded current evidence is the direct DMA-boundary replay plus the planner note",
]

PLANNER_NOTE_MARKERS = [
    "# Phase 13 devres dmam_alloc_coherent Planner",
    "pure `dmam_alloc_coherent()` planning surface",
    "detach-time cleanup intent",
    "`zigux/tests/phase13_devres_dma_coherent.zig` materialized on current `master`",
    "`lib/devres.zig` itself remains an explicit repo-reality gap",
    "does not treat the replay as proof",
    "dma_map_*",
    "dma_unmap_*",
    "dma_sync_*",
    "dma_mmap_*",
    "dma_map_sgtable()",
    "struct scatterlist",
    "sg_table",
    "sg_*",
    "zig test zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig",
    "zig test zigux/tests/phase13_devres_dma_coherent.zig",
]

DMA_REPLAY_MARKERS = [
    'test "phase13 devres dma coherent replay records blocked dma and scatterlist boundaries" {',
    'phase13-devres-dmam-alloc-coherent-planner',
    'phase13-devres-live-dmam-alloc-side-effects',
    'blocked_on_dma_state',
    'phase13-devres-live-scatterlist-ownership',
    'blocked_on_scatterlist_state',
    'test "phase13 devres dma coherent replay anchors the current slice reality" {',
    'try requireContains(slice, "`zigux/tests/phase13_devres_dma_coherent.zig` now materializes one direct replay surface");',
    'try requireContains(slice, "`lib/devres.zig`");',
    'try requireContains(slice, "repo-reality gaps");',
    'test "phase13 devres dma coherent replay keeps missing checker surfaces framed as gaps" {',
    'try requireContains(slice, "`scripts/zigux/check-phase13-devres-packet-alignment.py`");',
    'try requireContains(slice, "paired survey, helper, manifest, and broader direct replay packet");',
    'test "phase13 devres dma coherent replay keeps the planner note helper-first" {',
    'try requireContains(note, "pure `dmam_alloc_coherent()` planning surface");',
    'try requireContains(note, "`lib/devres.zig` itself remains an explicit repo-reality gap");',
    'try requireContains(note, "does not treat the replay as proof");',
]

PLANNER_REPLAY_MARKERS = [
    'test "phase13 devres dmam_alloc_coherent planner manifest records planning-only dma scope" {',
    'P13-L08',
    'phase13-devres-dmam-alloc-coherent-planner',
    'planning_only',
    'try requireContains(manifest, "Documentation/zigux/phase13-devres-slice.md");',
    'try requireContains(manifest, "Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md");',
    'try requireContains(manifest, "zigux/tests/phase13_devres_dma_coherent.zig");',
    'test "phase13 devres dmam_alloc_coherent planner note keeps the slice helper-first and bounded" {',
    'try requireContains(note, "detach-time cleanup intent");',
    'try requireContains(note, "dma_map_sgtable()");',
    'try requireContains(note, "struct scatterlist");',
    'test "phase13 devres dmam_alloc_coherent planner note preserves standalone replay handles" {',
    'try requireContains(note, "zig test zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig");',
    'try requireContains(note, "zig test zigux/tests/phase13_devres_dma_coherent.zig");',
]

PLANNER_MANIFEST_MARKERS = [
    '"lane_key": "P13-L08"',
    '"phase": "Phase 13"',
    '"surveyed_commit": "master-readback-2026-05-17"',
    '"anchor": "lib/devres.c"',
    '"packet": "phase13-devres-dmam-alloc-coherent-planner"',
    '"status": "planning_only"',
    '"adjacent_evidence": [',
    '"Documentation/zigux/phase13-devres-slice.md"',
    '"Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md"',
    '"zigux/tests/phase13_devres_dma_coherent.zig"',
    '"required_markers": [',
    '"pure `dmam_alloc_coherent()` planning surface"',
    '"detach-time cleanup intent"',
    '"avoid retaining detach-time cleanup ownership"',
    '"dma_map_*"',
    '"dma_unmap_*"',
    '"dma_sync_*"',
    '"dma_mmap_*"',
    '"dma_map_sgtable()"',
    '"struct scatterlist"',
    '"sg_table"',
    '"sg_*"',
    '"blocked_boundaries": [',
    '"id": "phase13-devres-live-dmam-alloc-side-effects"',
    '"status": "blocked_on_dma_state"',
    '"id": "phase13-devres-live-scatterlist-ownership"',
    '"status": "blocked_on_scatterlist_state"',
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_missing(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:missing_marker:{marker}" for marker in markers if marker not in text]


def validate(root: Path) -> list[str]:
    issues = [f"missing_file:{rel.as_posix()}" for rel in REQUIRED_FILES if not (root / rel).exists()]
    if issues:
        return issues

    checks = [
        (SLICE_PATH, SLICE_MARKERS, "slice"),
        (PLANNER_NOTE_PATH, PLANNER_NOTE_MARKERS, "planner_note"),
        (DMA_REPLAY_PATH, DMA_REPLAY_MARKERS, "dma_replay"),
        (PLANNER_REPLAY_PATH, PLANNER_REPLAY_MARKERS, "planner_replay"),
        (PLANNER_MANIFEST_PATH, PLANNER_MANIFEST_MARKERS, "planner_manifest"),
    ]

    for rel, markers, prefix in checks:
        issues.extend(collect_missing(read_text(root / rel), markers, prefix))
    return issues


def seed_fixture_tree(root: Path) -> None:
    writes = {
        SLICE_PATH: "\n".join(SLICE_MARKERS) + "\n",
        PLANNER_NOTE_PATH: "\n".join(PLANNER_NOTE_MARKERS) + "\n",
        DMA_REPLAY_PATH: "\n".join(DMA_REPLAY_MARKERS) + "\n",
        PLANNER_REPLAY_PATH: "\n".join(PLANNER_REPLAY_MARKERS) + "\n",
        PLANNER_MANIFEST_PATH: "\n".join(PLANNER_MANIFEST_MARKERS) + "\n",
    }
    for rel, text in writes.items():
        write_text(root / rel, text)


def assert_only(got: list[str], want: list[str], label: str) -> None:
    if got != want:
        got_text = ",".join(got) or "none"
        want_text = ",".join(want) or "none"
        raise AssertionError(f"{label}: got={got_text} want={want_text}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase13-devres-mmio-packet-") as tmp:
        root = Path(tmp)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        seed_fixture_tree(root)
        (root / PLANNER_MANIFEST_PATH).unlink()
        assert_only(
            validate(root),
            [f"missing_file:{PLANNER_MANIFEST_PATH.as_posix()}"],
            "missing_manifest_failed",
        )
        case_count += 1

        seed_fixtureTree = seed_fixture_tree
        seed_fixtureTree(root)
        write_text(
            root / SLICE_PATH,
            "\n".join(
                marker
                for marker in SLICE_MARKERS
                if marker != "bounded current evidence is the direct DMA-boundary replay plus the planner note"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ["slice:missing_marker:bounded current evidence is the direct DMA-boundary replay plus the planner note"],
            "slice_missing_current_evidence_failed",
        )
        case_count += 1

        seed_fixtureTree(root)
        write_text(
            root / PLANNER_NOTE_PATH,
            "\n".join(
                marker
                for marker in PLANNER_NOTE_MARKERS
                if marker != "`lib/devres.zig` itself remains an explicit repo-reality gap"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ["planner_note:missing_marker:`lib/devres.zig` itself remains an explicit repo-reality gap"],
            "planner_note_missing_gap_failed",
        )
        case_count += 1

        seed_fixtureTree(root)
        write_text(
            root / DMA_REPLAY_PATH,
            "\n".join(
                marker
                for marker in DMA_REPLAY_MARKERS
                if marker != 'try requireContains(slice, "`scripts/zigux/check-phase13-devres-packet-alignment.py`");'
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ['dma_replay:missing_marker:try requireContains(slice, "`scripts/zigux/check-phase13-devres-packet-alignment.py`");'],
            "dma_replay_missing_gap_marker_failed",
        )
        case_count += 1

        seed_fixtureTree(root)
        write_text(
            root / PLANNER_REPLAY_PATH,
            "\n".join(
                marker
                for marker in PLANNER_REPLAY_MARKERS
                if marker != 'planning_only'
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ['planner_replay:missing_marker:planning_only'],
            "planner_replay_missing_status_failed",
        )
        case_count += 1

        seed_fixtureTree(root)
        write_text(
            root / PLANNER_MANIFEST_PATH,
            "\n".join(
                marker
                for marker in PLANNER_MANIFEST_MARKERS
                if marker != '"id": "phase13-devres-live-scatterlist-ownership"'
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ['planner_manifest:missing_marker:"id": "phase13-devres-live-scatterlist-ownership"'],
            "planner_manifest_missing_scatterlist_failed",
        )
        case_count += 1

    print("PHASE13_DEVRES_MMIO_PACKET_SELF_TEST=pass")
    print(f"PHASE13_DEVRES_MMIO_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current bounded Phase 13 devres MMIO packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        for issue in issues:
            print(issue)
        print("PHASE13_DEVRES_MMIO_PACKET=fail")
        return 1

    print("PHASE13_DEVRES_MMIO_PACKET=pass")
    print(f"PHASE13_DEVRES_MMIO_PACKET_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE13_DEVRES_MMIO_PACKET_MARKER_COUNT="
        + str(
            len(SLICE_MARKERS)
            + len(PLANNER_NOTE_MARKERS)
            + len(DMA_REPLAY_MARKERS)
            + len(PLANNER_REPLAY_MARKERS)
            + len(PLANNER_MANIFEST_MARKERS)
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())