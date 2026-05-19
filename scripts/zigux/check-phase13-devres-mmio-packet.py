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
    "Current repo reality for this lane stays intentionally narrow:",
    "`Documentation/zigux/phase13-devres-survey.md` now records the current DMA and scatterlist boundary",
    "`lib/devres.zig` and `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig` now provide one pure helper-first `dmam_alloc_coherent()` planning surface",
    "`scripts/zigux/check-phase13-devres-packet-alignment.py` stays in the same repo-reality gaps bucket",
    "`zigux/tests/phase13_devres_dma_coherent.zig` plus `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `lib/devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist.zig` keep the current packet helper-first and planning-only",
    "The bounded current evidence is the survey note, the planner note and manifest, the new pure `dmam_alloc_coherent()` helper plus replay, the direct DMA-boundary replay, and the helper-first scatterlist helper plus replay",
]

PLANNER_NOTE_MARKERS = [
    "# Phase 13 devres dmam_alloc_coherent Planner",
    "lands one pure `dmam_alloc_coherent()` planning surface in `lib/devres.zig`",
    "routes `planManagedDmamAllocCoherent(...)` through `planManagedReleaseRecordLifetime(...)`",
    "accepts already-decided allocation inputs",
    "retains detach-time cleanup ownership on success",
    "failed allocation frees the release record",
    "does not claim live DMA allocation side effects",
    "dma_map_*",
    "dma_unmap_*",
    "dma_sync_*",
    "dma_mmap_*",
    "dma_map_sgtable()",
    "struct scatterlist",
    "sg_table",
    "sg_*",
    "zig test --dep devres -Mroot=zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig -Mdevres=lib/devres.zig",
    "zig test zigux/tests/phase13_devres_dma_coherent.zig",
]

DMA_REPLAY_MARKERS = [
    'test "phase13 devres dma coherent replay records blocked dma and scatterlist boundaries" {',
    'try requireContains(manifest, "\\\"id\\\": \\\"phase13-devres-live-dmam-alloc-side-effects\\\"");',
    'try requireContains(manifest, "\\\"id\\\": \\\"phase13-devres-live-scatterlist-ownership\\\"");',
    'test "phase13 devres dma coherent replay anchors the current slice reality" {',
    'try requireContains(slice, "`zigux/tests/phase13_devres_dma_coherent.zig` plus `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `lib/devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist.zig` keep the current packet helper-first and planning-only");',
    'test "phase13 devres dma coherent replay keeps missing checker surfaces framed as gaps" {',
    'try requireContains(slice, "the older direct devres replay, reviewability gate, manifest-backed packet, and packet-alignment checker remain repo-reality gaps");',
    'try requireContains(slice, "the broader direct helper packet stays an explicit repo-reality gap");',
    'test "phase13 devres dma coherent replay anchors the survey-side scatterlist boundary" {',
    'try requireContains(survey, "helper-first scatterlist helper and replay");',
    'try requireContains(survey, "blocked `phase13-devres-live-scatterlist-ownership`");',
    'try requireContains(survey, "blocked `phase13-devres-live-sg-table-lifecycle`");',
    'test "phase13 devres dma coherent replay keeps scatterlist helper evidence helper-first" {',
    'try requireContains(helper, ".provides_scatterlist_lifetime_planning = true");',
    'try requireContains(helper, "pub fn planManagedScatterlistMap");',
    'try requireContains(replay, "phase13 devres scatterlist release matching stays exact across original and mapped counts");',
]

PLANNER_REPLAY_MARKERS = [
    'test "phase13 devres descriptor records helper-first dmam_alloc_coherent planning" {',
    'test "phase13 devres exposes shared release-record lifetime planning" {',
    'test "phase13 devres retains detach-time cleanup ownership when planned coherent allocation succeeds" {',
    'test "phase13 devres drops detach-time cleanup ownership when planned coherent allocation fails" {',
    'test "phase13 devres rejects coherent planning when the release record cannot be allocated" {',
    'test "phase13 devres dmam_alloc_coherent planner manifest records the landed helper-first dma scope" {',
    'try requireContains(manifest, "\\\"lane_key\\\": \\\"P13-L08\\\"");',
    'try requireContains(manifest, "\\\"status\\\": \\\"starter_landed\\\"");',
    'try requireContains(manifest, "planManagedReleaseRecordLifetime");',
    'test "phase13 devres dmam_alloc_coherent planner note keeps the helper-first dma slice bounded" {',
    'test "phase13 devres dmam_alloc_coherent planner note preserves standalone replay handles" {',
    'test "phase13 devres slice note records the narrow landed dmam planner without claiming the broader packet" {',
    'test "phase13 devres survey records the landed dmam planner and keeps the blocked dma boundaries explicit" {',
]

PLANNER_MANIFEST_MARKERS = [
    '"lane_key": "P13-L08"',
    '"phase": "Phase 13"',
    '"anchor": "lib/devres.c"',
    '"packet": "phase13-devres-dmam-alloc-coherent-planner"',
    '"status": "starter_landed"',
    '"adjacent_evidence": [',
    '"lib/devres.zig"',
    '"Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md"',
    '"zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig"',
    '"zigux/tests/phase13_devres_dma_coherent.zig"',
    '"required_markers": [',
    '"pure `dmam_alloc_coherent()` planning surface"',
    '"planManagedDmamAllocCoherent"',
    '"planManagedReleaseRecordLifetime"',
    '"detach-time cleanup ownership on success"',
    '"failed allocation frees the release record"',
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

        seed_fixture_tree(root)
        write_text(
            root / SLICE_PATH,
            "\n".join(
                marker
                for marker in SLICE_MARKERS
                if marker
                != "The bounded current evidence is the survey note, the planner note and manifest, the new pure `dmam_alloc_coherent()` helper plus replay, the direct DMA-boundary replay, and the helper-first scatterlist helper plus replay"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "slice:missing_marker:The bounded current evidence is the survey note, the planner note and manifest, the new pure `dmam_alloc_coherent()` helper plus replay, the direct DMA-boundary replay, and the helper-first scatterlist helper plus replay"
            ],
            "slice_missing_current_evidence_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / PLANNER_NOTE_PATH,
            "\n".join(
                marker
                for marker in PLANNER_NOTE_MARKERS
                if marker != "routes `planManagedDmamAllocCoherent(...)` through `planManagedReleaseRecordLifetime(...)`"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "planner_note:missing_marker:routes `planManagedDmamAllocCoherent(...)` through `planManagedReleaseRecordLifetime(...)`"
            ],
            "planner_note_missing_release_record_route_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / DMA_REPLAY_PATH,
            "\n".join(
                marker
                for marker in DMA_REPLAY_MARKERS
                if marker != 'try requireContains(survey, "blocked `phase13-devres-live-sg-table-lifecycle`");'
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                'dma_replay:missing_marker:try requireContains(survey, "blocked `phase13-devres-live-sg-table-lifecycle`");'
            ],
            "dma_replay_missing_sg_table_boundary_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / PLANNER_REPLAY_PATH,
            "\n".join(
                marker
                for marker in PLANNER_REPLAY_MARKERS
                if marker != 'try requireContains(manifest, "\\\"status\\\": \\\"starter_landed\\\"");'
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ['planner_replay:missing_marker:try requireContains(manifest, "\\\"status\\\": \\\"starter_landed\\\"");'],
            "planner_replay_missing_status_failed",
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