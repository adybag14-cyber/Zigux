#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SLICE_PATH = Path("Documentation/zigux/phase13-devres-slice.md")
SURVEY_PATH = Path("Documentation/zigux/phase13-devres-survey.md")
PLANNER_NOTE_PATH = Path("Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md")
SCATTERLIST_SLICE_PATH = Path("Documentation/zigux/phase13-devres-scatterlist-slice.md")
PLANNER_MANIFEST_PATH = Path("zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json")
PLANNER_REPLAY_PATH = Path("zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig")
DMA_REPLAY_PATH = Path("zigux/tests/phase13_devres_dma_coherent.zig")
SCATTERLIST_HELPER_PATH = Path("lib/devres_scatterlist.zig")
SCATTERLIST_REPLAY_PATH = Path("zigux/tests/phase13_devres_scatterlist.zig")
SCATTERLIST_BUILD_PATH = Path("zigux/tests/phase13_devres_scatterlist_build.zig")

REQUIRED_FILES = [
    SLICE_PATH,
    SURVEY_PATH,
    PLANNER_NOTE_PATH,
    SCATTERLIST_SLICE_PATH,
    PLANNER_MANIFEST_PATH,
    PLANNER_REPLAY_PATH,
    DMA_REPLAY_PATH,
    SCATTERLIST_HELPER_PATH,
    SCATTERLIST_REPLAY_PATH,
    SCATTERLIST_BUILD_PATH,
]

SLICE_MARKERS = [
    "# Phase 13 devres Slice",
    "`Documentation/zigux/phase13-devres-survey.md` now records the current DMA and scatterlist boundary",
    "`lib/devres.zig` and `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig` now provide one pure helper-first `dmam_alloc_coherent()` planning surface",
    "`scripts/zigux/check-phase13-devres-packet-alignment.py` stays in the same repo-reality gaps bucket",
    "`zigux/tests/phase13_devres_dma_coherent.zig` plus `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `lib/devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist.zig` keep the current packet helper-first and planning-only",
    "The bounded current evidence is the survey note, the planner note and manifest, the new pure `dmam_alloc_coherent()` helper plus replay, the direct DMA-boundary replay, and the helper-first scatterlist helper plus replay",
]

SURVEY_MARKERS = [
    "# Phase 13 devres DMA and scatterlist Boundary Survey",
    "`zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json` marks the packet as `starter_landed`",
    "`lib/devres.zig` now ships a pure `dmam_alloc_coherent()` planning surface through `DevresHelperLab.descriptor()`, `planManagedReleaseRecordLifetime(...)`, and `planManagedDmamAllocCoherent(...)`",
    "`zigux/tests/phase13_devres_dma_coherent.zig` continues to fail-close on generic DMA and scatterlist ownership boundaries beside the new helper-first planner",
    "`lib/devres_scatterlist.zig` and `zigux/tests/phase13_devres_scatterlist.zig` keep the helper-first scatterlist lifetime slice reviewable",
    "blocked `phase13-devres-live-dmam-alloc-side-effects`",
    "blocked `phase13-devres-live-scatterlist-ownership`",
    "blocked `phase13-devres-live-sg-table-lifecycle`",
    "blocked `phase13-devres-generic-dma-map-family`",
]

PLANNER_NOTE_MARKERS = [
    "# Phase 13 devres dmam_alloc_coherent Planner",
    "lands one pure `dmam_alloc_coherent()` planning surface in `lib/devres.zig`",
    "routes `planManagedDmamAllocCoherent(...)` through `planManagedReleaseRecordLifetime(...)`",
    "accepts already-decided allocation inputs rather than talking to live hardware state",
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
]

SCATTERLIST_SLICE_MARKERS = [
    "# Phase 13 devres scatterlist helper slice",
    "This slice adds one helper-first scatterlist planner beside the existing `lib/devres.zig` and `lib/devres_dma_coherent.zig` packet.",
    "- Zigux helper: `lib/devres_scatterlist.zig`",
    "- focused replay: `zigux/tests/phase13_devres_scatterlist.zig`",
    "keep one reviewable scatterlist bookkeeping foothold without widening into live DMA-backed execution or live `sg_*` traversal",
    "`DevresScatterlistHelper.descriptor()` names the same `lib/devres.c` anchor while keeping `touches_live_dma = false` and `touches_live_scatterlist = false`",
    "`planManagedScatterlistMap()` models a helper-first retained-record decision around original segment count, mapped segment count, and detach-time unmap readiness",
    "`planManagedScatterlistUnmap()` keeps the release match exact across original and mapped segment counts so the detach bookkeeping surface stays reviewable",
    "no live `dma_map_sgtable()` or `dma_unmap_sgtable()` execution",
    "no `struct scatterlist`, `sg_table`, or `sg_*` iteration helpers",
]

PLANNER_MANIFEST_MARKERS = [
    '"lane_key": "P13-L08"',
    '"phase": "Phase 13"',
    '"anchor": "lib/devres.c"',
    '"packet": "phase13-devres-dmam-alloc-coherent-planner"',
    '"status": "starter_landed"',
    '"lib/devres.zig"',
    '"planManagedDmamAllocCoherent"',
    '"planManagedReleaseRecordLifetime"',
    '"id": "phase13-devres-live-dmam-alloc-side-effects"',
    '"status": "blocked_on_dma_state"',
    '"id": "phase13-devres-live-scatterlist-ownership"',
    '"status": "blocked_on_scatterlist_state"',
]

PLANNER_REPLAY_MARKERS = [
    'test "phase13 devres descriptor records helper-first dmam_alloc_coherent planning" {',
    'test "phase13 devres dmam_alloc_coherent planner manifest records the landed helper-first dma scope" {',
    'try requireContains(manifest, "\\\"status\\\": \\\"starter_landed\\\"");',
    'try requireContains(manifest, "planManagedReleaseRecordLifetime");',
]

DMA_REPLAY_MARKERS = [
    'test "phase13 devres dma coherent replay records blocked dma and scatterlist boundaries" {',
    'test "phase13 devres dma coherent replay anchors the current slice reality" {',
    'try requireContains(slice, "`zigux/tests/phase13_devres_dma_coherent.zig` plus `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `lib/devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist.zig` keep the current packet helper-first and planning-only");',
]

SCATTERLIST_HELPER_MARKERS = [
    "pub const ModuleDescriptor = struct {",
    ".provides_scatterlist_lifetime_planning = true",
    ".touches_live_dma = false",
    ".touches_live_scatterlist = false",
    "pub fn planManagedScatterlistMap",
    "pub fn planManagedScatterlistUnmap",
    "warns_on_release_miss",
]

SCATTERLIST_REPLAY_MARKERS = [
    'test "phase13 devres descriptor records helper-first scatterlist planning" {',
    'test "phase13 devres retains the release record when helper-first scatterlist planning succeeds" {',
    'test "phase13 devres rejects scatterlist planning when the release record cannot be allocated" {',
    'test "phase13 devres scatterlist release matching stays exact across original and mapped counts" {',
]

SCATTERLIST_BUILD_MARKERS = [
    'const devres_scatterlist_module = b.createModule(.{',
    '.root_source_file = b.path("../../lib/devres_scatterlist.zig"),',
    'const phase13_devres_scatterlist_module = b.createModule(.{',
    '.root_source_file = b.path("phase13_devres_scatterlist.zig"),',
    'phase13_devres_scatterlist_module.addImport("devres_scatterlist", devres_scatterlist_module);',
    '.name = "phase13-devres-scatterlist-tests",',
    'const test_step = b.step("test", "Run Phase 13 devres scatterlist helper tests");',
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
        (SCATTERLIST_SLICE_PATH, SCATTERLIST_SLICE_MARKERS, "scatterlist_slice"),
        (PLANNER_MANIFEST_PATH, PLANNER_MANIFEST_MARKERS, "planner_manifest"),
        (PLANNER_REPLAY_PATH, PLANNER_REPLAY_MARKERS, "planner_replay"),
        (DMA_REPLAY_PATH, DMA_REPLAY_MARKERS, "dma_replay"),
        (SCATTERLIST_HELPER_PATH, SCATTERLIST_HELPER_MARKERS, "scatterlist_helper"),
        (SCATTERLIST_REPLAY_PATH, SCATTERLIST_REPLAY_MARKERS, "scatterlist_replay"),
        (SCATTERLIST_BUILD_PATH, SCATTERLIST_BUILD_MARKERS, "scatterlist_build"),
    ]

    for rel, markers, prefix in checks:
        issues.extend(collect_missing(read_text(root / rel), markers, prefix))
    return issues


def seed_fixture_tree(root: Path) -> None:
    writes = {
        SLICE_PATH: "\n".join(SLICE_MARKERS) + "\n",
        SURVEY_PATH: "\n".join(SURVEY_MARKERS) + "\n",
        PLANNER_NOTE_PATH: "\n".join(PLANNER_NOTE_MARKERS) + "\n",
        SCATTERLIST_SLICE_PATH: "\n".join(SCATTERLIST_SLICE_MARKERS) + "\n",
        PLANNER_MANIFEST_PATH: "\n".join(PLANNER_MANIFEST_MARKERS) + "\n",
        PLANNER_REPLAY_PATH: "\n".join(PLANNER_REPLAY_MARKERS) + "\n",
        DMA_REPLAY_PATH: "\n".join(DMA_REPLAY_MARKERS) + "\n",
        SCATTERLIST_HELPER_PATH: "\n".join(SCATTERLIST_HELPER_MARKERS) + "\n",
        SCATTERLIST_REPLAY_PATH: "\n".join(SCATTERLIST_REPLAY_MARKERS) + "\n",
        SCATTERLIST_BUILD_PATH: "\n".join(SCATTERLIST_BUILD_MARKERS) + "\n",
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
            "slice_missing_evidence_summary_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / SURVEY_PATH,
            "\n".join(
                marker
                for marker in SURVEY_MARKERS
                if marker != "blocked `phase13-devres-live-sg-table-lifecycle`"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ["survey:missing_marker:blocked `phase13-devres-live-sg-table-lifecycle`"],
            "survey_missing_sgtable_boundary_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / PLANNER_NOTE_PATH,
            "\n".join(
                marker
                for marker in PLANNER_NOTE_MARKERS
                if marker != "does not claim live DMA allocation side effects"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ["planner_note:missing_marker:does not claim live DMA allocation side effects"],
            "planner_note_missing_dma_boundary_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / SCATTERLIST_SLICE_PATH,
            "\n".join(
                marker
                for marker in SCATTERLIST_SLICE_MARKERS
                if marker != "- Zigux helper: `lib/devres_scatterlist.zig`"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ["scatterlist_slice:missing_marker:- Zigux helper: `lib/devres_scatterlist.zig`"],
            "scatterlist_slice_missing_helper_anchor_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / PLANNER_MANIFEST_PATH,
            "\n".join(
                marker
                for marker in PLANNER_MANIFEST_MARKERS
                if marker != '"status": "starter_landed"'
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ['planner_manifest:missing_marker:"status": "starter_landed"'],
            "planner_manifest_missing_status_failed",
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
            [
                'planner_replay:missing_marker:try requireContains(manifest, "\\\"status\\\": \\\"starter_landed\\\"");'
            ],
            "planner_replay_missing_status_assertion_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / SCATTERLIST_HELPER_PATH,
            "\n".join(
                marker
                for marker in SCATTERLIST_HELPER_MARKERS
                if marker != "pub fn planManagedScatterlistUnmap"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ["scatterlist_helper:missing_marker:pub fn planManagedScatterlistUnmap"],
            "scatterlist_helper_missing_unmap_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / SCATTERLIST_REPLAY_PATH,
            "\n".join(
                marker
                for marker in SCATTERLIST_REPLAY_MARKERS
                if marker
                != 'test "phase13 devres scatterlist release matching stays exact across original and mapped counts" {'
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                'scatterlist_replay:missing_marker:test "phase13 devres scatterlist release matching stays exact across original and mapped counts" {'
            ],
            "scatterlist_replay_missing_release_match_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / SCATTERLIST_BUILD_PATH,
            "\n".join(
                marker
                for marker in SCATTERLIST_BUILD_MARKERS
                if marker != 'const test_step = b.step("test", "Run Phase 13 devres scatterlist helper tests");'
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                'scatterlist_build:missing_marker:const test_step = b.step("test", "Run Phase 13 devres scatterlist helper tests");'
            ],
            "scatterlist_build_missing_test_step_failed",
        )
        case_count += 1

    print("PHASE13_DEVRES_MMIO_PACKET_SELF_TEST=pass")
    print(f"PHASE13_DEVRES_MMIO_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current bounded Phase 13 devres MMIO and DMA boundary packet."
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
            + len(SURVEY_MARKERS)
            + len(PLANNER_NOTE_MARKERS)
            + len(SCATTERLIST_SLICE_MARKERS)
            + len(PLANNER_MANIFEST_MARKERS)
            + len(PLANNER_REPLAY_MARKERS)
            + len(DMA_REPLAY_MARKERS)
            + len(SCATTERLIST_HELPER_MARKERS)
            + len(SCATTERLIST_REPLAY_MARKERS)
            + len(SCATTERLIST_BUILD_MARKERS)
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())