#!/usr/bin/env python3
"""Guard the current bounded Phase 13 devres lifetime packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path("/workspace")

SLICE_PATH = Path("Documentation/zigux/phase13-devres-slice.md")
SURVEY_PATH = Path("Documentation/zigux/phase13-devres-survey.md")
PLANNER_NOTE_PATH = Path("Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md")
PLANNER_REPLAY_PATH = Path("zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig")
PLANNER_MANIFEST_PATH = Path("zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json")
DMA_REPLAY_PATH = Path("zigux/tests/phase13_devres_dma_coherent.zig")
SCATTERLIST_HELPER_PATH = Path("lib/devres_scatterlist.zig")
SCATTERLIST_REPLAY_PATH = Path("zigux/tests/phase13_devres_scatterlist.zig")

REQUIRED_FILES = [
    SLICE_PATH,
    SURVEY_PATH,
    PLANNER_NOTE_PATH,
    PLANNER_REPLAY_PATH,
    PLANNER_MANIFEST_PATH,
    DMA_REPLAY_PATH,
    SCATTERLIST_HELPER_PATH,
    SCATTERLIST_REPLAY_PATH,
]

SLICE_MARKERS = [
    "# Phase 13 devres Slice",
    "`Documentation/zigux/phase13-devres-survey.md` now records the current DMA and scatterlist boundary",
    "`lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, and `zigux/tests/phase13_devres_manifest.json` remain repo-reality gaps",
    "`scripts/zigux/check-phase13-devres-packet-alignment.py` stays in the same repo-reality gaps bucket",
    "`zigux/tests/phase13_devres_dma_coherent.zig` plus `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `lib/devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist.zig` keep the current packet helper-first and planning-only",
    "The bounded current evidence is the survey note, the direct DMA-boundary replay, the planning-only `dmam_alloc_coherent()` note and manifest, and the helper-first scatterlist helper plus replay",
    "compare those survey, planner, replay, and helper surfaces together on current `master` before widening anything else",
]

SURVEY_MARKERS = [
    "# Phase 13 devres DMA and scatterlist Boundary Survey",
    "reviewed against live `master` `master-readback-2026-05-18`",
    "the docs-side devres slice note, the planning-only `dmam_alloc_coherent()` note and manifest, the direct DMA-boundary replay, the helper-first scatterlist helper and replay, and the roadmap-backed `lib/devres.c` anchor",
    "`lib/devres_scatterlist.zig` now provides a helper-first scatterlist lifetime planner",
    "`zigux/tests/phase13_devres_scatterlist.zig` replays that scatterlist helper surface directly",
    "current `master` does not ship `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_manifest.json`, or `scripts/zigux/check-phase13-devres-packet-alignment.py`",
    "blocked `phase13-devres-live-dmam-alloc-side-effects`",
    "blocked `phase13-devres-live-scatterlist-ownership`",
    "blocked `phase13-devres-live-sg-table-lifecycle`",
    "blocked `phase13-devres-generic-dma-map-family`",
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

PLANNER_REPLAY_MARKERS = [
    'test "phase13 devres dmam_alloc_coherent planner manifest records planning-only dma scope" {',
    '"phase13-devres-dmam-alloc-coherent-planner"',
    '"planning_only"',
    '"phase13-devres-live-dmam-alloc-side-effects"',
    '"blocked_on_dma_state"',
    '"phase13-devres-live-scatterlist-ownership"',
    '"blocked_on_scatterlist_state"',
    'test "phase13 devres dmam_alloc_coherent planner note keeps the slice helper-first and bounded" {',
    '"detach-time cleanup intent"',
    '"`lib/devres.zig` itself remains an explicit repo-reality gap"',
    'test "phase13 devres dmam_alloc_coherent planner note preserves standalone replay handles" {',
]

PLANNER_MANIFEST_MARKERS = [
    '"lane_key": "P13-L08"',
    '"phase": "Phase 13"',
    '"surveyed_commit": "master-readback-2026-05-17"',
    '"anchor": "lib/devres.c"',
    '"packet": "phase13-devres-dmam-alloc-coherent-planner"',
    '"status": "planning_only"',
    '"Documentation/zigux/phase13-devres-slice.md"',
    '"Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md"',
    '"zigux/tests/phase13_devres_dma_coherent.zig"',
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
    '"id": "phase13-devres-live-dmam-alloc-side-effects"',
    '"status": "blocked_on_dma_state"',
    '"id": "phase13-devres-live-scatterlist-ownership"',
    '"status": "blocked_on_scatterlist_state"',
]

DMA_REPLAY_MARKERS = [
    'test "phase13 devres dma coherent replay records blocked dma and scatterlist boundaries" {',
    '"phase13-devres-dmam-alloc-coherent-planner"',
    '"phase13-devres-live-dmam-alloc-side-effects"',
    '"blocked_on_dma_state"',
    '"phase13-devres-live-scatterlist-ownership"',
    '"blocked_on_scatterlist_state"',
    'test "phase13 devres dma coherent replay anchors the current slice reality" {',
    '"`Documentation/zigux/phase13-devres-survey.md`"',
    '"`lib/devres.zig`"',
    '"repo-reality gaps"',
    'test "phase13 devres dma coherent replay keeps missing checker surfaces framed as gaps" {',
    '"`scripts/zigux/check-phase13-devres-packet-alignment.py`"',
    '"paired survey, helper, manifest, and broader direct replay packet"',
    'test "phase13 devres dma coherent replay anchors the survey-side scatterlist boundary" {',
    '"helper-first scatterlist helper and replay"',
    '"blocked `phase13-devres-live-sg-table-lifecycle`"',
    '"blocked `phase13-devres-generic-dma-map-family`"',
    'test "phase13 devres dma coherent replay keeps scatterlist helper evidence helper-first" {',
    '".provides_scatterlist_lifetime_planning = true"',
    '"phase13 devres scatterlist release matching stays exact across original and mapped counts"',
]

SCATTERLIST_HELPER_MARKERS = [
    "pub const ModuleDescriptor = struct {",
    "provides_scatterlist_lifetime_planning: bool,",
    "touches_live_dma: bool,",
    "touches_live_scatterlist: bool,",
    "pub const ManagedScatterlistMapResult = struct {",
    "pub const ManagedScatterlistUnmapPlan = struct {",
    '.name = "devres_scatterlist_helper",',
    '.anchor = "lib/devres.c",',
    ".provides_scatterlist_lifetime_planning = true,",
    ".touches_live_dma = false,",
    ".touches_live_scatterlist = false,",
    "pub fn planManagedScatterlistMap(",
    "pub fn planManagedScatterlistUnmap(",
    ".warns_on_release_miss = !release_matches,",
]

SCATTERLIST_REPLAY_MARKERS = [
    'test "phase13 devres descriptor records helper-first scatterlist planning" {',
    'test "phase13 devres retains the release record when helper-first scatterlist planning succeeds" {',
    'test "phase13 devres frees the scatterlist release record when no mapped segments are returned" {',
    'test "phase13 devres frees the scatterlist release record when mapped segments exceed the original count" {',
    'test "phase13 devres rejects scatterlist planning when the release record cannot be allocated" {',
    'test "phase13 devres scatterlist release matching stays exact across original and mapped counts" {',
    'try std.testing.expect(descriptor.provides_scatterlist_lifetime_planning);',
    "try std.testing.expect(!descriptor.touches_live_dma);",
    "try std.testing.expect(!descriptor.touches_live_scatterlist);",
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
        (SURVEY_PATH, SURVEY_MARKERS, "survey"),
        (PLANNER_NOTE_PATH, PLANNER_NOTE_MARKERS, "planner_note"),
        (PLANNER_REPLAY_PATH, PLANNER_REPLAY_MARKERS, "planner_replay"),
        (PLANNER_MANIFEST_PATH, PLANNER_MANIFEST_MARKERS, "planner_manifest"),
        (DMA_REPLAY_PATH, DMA_REPLAY_MARKERS, "dma_replay"),
        (SCATTERLIST_HELPER_PATH, SCATTERLIST_HELPER_MARKERS, "scatterlist_helper"),
        (SCATTERLIST_REPLAY_PATH, SCATTERLIST_REPLAY_MARKERS, "scatterlist_replay"),
    ]

    for rel, markers, prefix in checks:
        issues.extend(collect_missing(read_text(root / rel), markers, prefix))
    return issues


def seed_fixture_tree(root: Path) -> None:
    writes = {
        SLICE_PATH: "\n".join(SLICE_MARKERS) + "\n",
        SURVEY_PATH: "\n".join(SURVEY_MARKERS) + "\n",
        PLANNER_NOTE_PATH: "\n".join(PLANNER_NOTE_MARKERS) + "\n",
        PLANNER_REPLAY_PATH: "\n".join(PLANNER_REPLAY_MARKERS) + "\n",
        PLANNER_MANIFEST_PATH: "\n".join(PLANNER_MANIFEST_MARKERS) + "\n",
        DMA_REPLAY_PATH: "\n".join(DMA_REPLAY_MARKERS) + "\n",
        SCATTERLIST_HELPER_PATH: "\n".join(SCATTERLIST_HELPER_MARKERS) + "\n",
        SCATTERLIST_REPLAY_PATH: "\n".join(SCATTERLIST_REPLAY_MARKERS) + "\n",
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
    with tempfile.TemporaryDirectory(prefix="phase13-devres-shared-lifetime-packet-") as tmp:
        root = Path(tmp)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        seed_fixture_tree(root)
        (root / SURVEY_PATH).unlink()
        assert_only(
            validate(root),
            [f"missing_file:{SURVEY_PATH.as_posix()}"],
            "missing_survey_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / SLICE_PATH,
            "\n".join(
                marker
                for marker in SLICE_MARKERS
                if marker != "compare those survey, planner, replay, and helper surfaces together on current `master` before widening anything else"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "slice:missing_marker:compare those survey, planner, replay, and helper surfaces together on current `master` before widening anything else"
            ],
            "slice_missing_next_step_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / DMA_REPLAY_PATH,
            "\n".join(
                marker
                for marker in DMA_REPLAY_MARKERS
                if marker != '"blocked `phase13-devres-live-sg-table-lifecycle`"'
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ['dma_replay:missing_marker:"blocked `phase13-devres-live-sg-table-lifecycle`"'],
            "dma_replay_missing_sg_table_gap_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / SCATTERLIST_HELPER_PATH,
            "\n".join(
                marker
                for marker in SCATTERLIST_HELPER_MARKERS
                if marker != ".touches_live_scatterlist = false,"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ["scatterlist_helper:missing_marker:.touches_live_scatterlist = false,"],
            "scatterlist_helper_missing_boundary_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
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
            "planner_manifest_missing_scatterlist_blocker_failed",
        )
        case_count += 1

    print("PHASE13_DEVRES_SHARED_LIFETIME_PACKET_SELF_TEST=pass")
    print(f"PHASE13_DEVRES_SHARED_LIFETIME_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Phase 13 devres lifetime packet stays explicit."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        for issue in issues:
            print(issue)
        print("PHASE13_DEVRES_SHARED_LIFETIME_PACKET=fail")
        return 1

    print("PHASE13_DEVRES_SHARED_LIFETIME_PACKET=pass")
    print(f"PHASE13_DEVRES_SHARED_LIFETIME_PACKET_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE13_DEVRES_SHARED_LIFETIME_PACKET_MARKER_COUNT="
        + str(
            len(SLICE_MARKERS)
            + len(SURVEY_MARKERS)
            + len(PLANNER_NOTE_MARKERS)
            + len(PLANNER_REPLAY_MARKERS)
            + len(PLANNER_MANIFEST_MARKERS)
            + len(DMA_REPLAY_MARKERS)
            + len(SCATTERLIST_HELPER_MARKERS)
            + len(SCATTERLIST_REPLAY_MARKERS)
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
