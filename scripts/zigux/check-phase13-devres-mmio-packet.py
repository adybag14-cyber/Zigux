#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SLICE_PATH = Path("Documentation/zigux/phase13-devres-slice.md")
SURVEY_PATH = Path("Documentation/zigux/phase13-devres-survey.md")
PLANNER_NOTE_PATH = Path("Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md")
SCATTERLIST_SLICE_PATH = Path("Documentation/zigux/phase13-devres-scatterlist-slice.md")
SCATTERLIST_PLANNER_NOTE_PATH = Path("Documentation/zigux/phase13-devres-scatterlist-planner.md")
PLANNER_MANIFEST_PATH = Path("zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json")
SCATTERLIST_PLANNER_MANIFEST_PATH = Path("zigux/tests/phase13_devres_scatterlist_planner_manifest.json")
PLANNER_REPLAY_PATH = Path("zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig")
DMA_REPLAY_PATH = Path("zigux/tests/phase13_devres_dma_coherent.zig")
HELPER_PATH = Path("lib/devres.zig")
SCATTERLIST_HELPER_PATH = Path("lib/devres_scatterlist.zig")
SCATTERLIST_REPLAY_PATH = Path("zigux/tests/phase13_devres_scatterlist.zig")
SCATTERLIST_BUILD_PATH = Path("zigux/tests/phase13_devres_scatterlist_build.zig")

REQUIRED_FILES = [
    SLICE_PATH,
    SURVEY_PATH,
    PLANNER_NOTE_PATH,
    SCATTERLIST_SLICE_PATH,
    SCATTERLIST_PLANNER_NOTE_PATH,
    PLANNER_MANIFEST_PATH,
    SCATTERLIST_PLANNER_MANIFEST_PATH,
    PLANNER_REPLAY_PATH,
    DMA_REPLAY_PATH,
    HELPER_PATH,
    SCATTERLIST_HELPER_PATH,
    SCATTERLIST_REPLAY_PATH,
    SCATTERLIST_BUILD_PATH,
]

SLICE_MARKERS = [
    "# Phase 13 devres Slice",
    "`Documentation/zigux/phase13-devres-survey.md` now records the current DMA and scatterlist boundary",
    "`lib/devres.zig` and `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig` now provide one pure helper-first `dmam_alloc_coherent()` planning surface",
    "`scripts/zigux/check-phase13-devres-packet-alignment.py` stays in the same repo-reality gaps bucket",
    "`zigux/tests/phase13_devres_dma_coherent.zig` plus `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-planner.md`, `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist_build.zig`, and `scripts/zigux/check-phase13-devres-mmio-packet.py` keep the current packet helper-first and planning-only",
    "The bounded current evidence is the survey note, the `dmam_alloc_coherent()` planner note and manifest, the new pure `dmam_alloc_coherent()` helper plus replay, the direct DMA-boundary replay, the dedicated helper-first scatterlist planner note, manifest, helper, replay, scatterlist build shard, and the dedicated `scripts/zigux/check-phase13-devres-mmio-packet.py` guard, while the broader direct helper packet stays an explicit repo-reality gap.",
]

SURVEY_MARKERS = [
    "# Phase 13 devres DMA, scatterlist, and MMIO Boundary Survey",
    "This document records the bounded `P13-L01` survey lane around the current `lib/devres.c` helper packet on `master`: the shipped DMA and scatterlist boundary evidence, plus the still-missing MMIO and iomap safety gaps that remain open against the Phase 13 roadmap.",
    "`zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json` marks the packet as `starter_landed`",
    "`lib/devres.zig` ships a pure `dmam_alloc_coherent()` planning surface through `DevresHelperLab.descriptor()`, `planManagedReleaseRecordLifetime(...)`, `planManagedDmamAllocCoherent(...)`, and `planManagedDmamFreeCoherent(...)`, while keeping `.touches_live_dma = false` and `.touches_live_scatterlist = false`.",
    "`zigux/tests/phase13_devres_dma_coherent.zig` continues to fail closed on generic DMA and scatterlist ownership boundaries beside the new helper-first planner.",
    "`lib/devres_scatterlist.zig` ships helper-first scatterlist lifetime planning through `planManagedScatterlistMap(...)`, `scatterlistReleaseMatches(...)`, and `planManagedScatterlistUnmap(...)`, and `zigux/tests/phase13_devres_scatterlist.zig` replays retained-release-record success, freed-release-record fallback, release-record-allocation failure, exact release-match behavior, and the dedicated planner note or manifest packet without widening into live DMA mapping or `sg_table` lifecycle control.",
    "there are no `devm_iounmap(`, `devm_ioremap_np(`, `devm_of_iomap(`, `devm_arch_phys_wc_add(`, or `devm_arch_io_reserve_memtype_wc(` markers in the live helper file.",
    "`zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_manifest.json`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` remain absent",
    "blocked `phase13-devres-live-dmam-alloc-side-effects`",
    "blocked `phase13-devres-live-scatterlist-ownership`",
    "blocked `phase13-devres-live-sg-table-lifecycle`",
    "blocked `phase13-devres-generic-dma-map-family`",
    "blocked `phase13-devres-missing-devm-iounmap-surface`",
    "blocked `phase13-devres-missing-devm-ioremap-np-surface`",
    "blocked `phase13-devres-missing-devm-of-iomap-surface`",
    "blocked `phase13-devres-missing-devm-arch-phys-wc-add-surface`",
    "blocked `phase13-devres-missing-devm-arch-io-reserve-memtype-wc-surface`",
    "blocked `phase13-devres-live-mmio-mapping-state`",
    "blocked `phase13-devres-live-device-tree-walks`",
    "blocked `phase13-devres-live-arch-memtype-mutation`",
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

SCATTERLIST_PLANNER_NOTE_MARKERS = [
    "# Phase 13 devres scatterlist Planner",
    "lands one pure scatterlist lifetime planning surface in `lib/devres_scatterlist.zig`",
    "routes `planManagedScatterlistMap(...)` through one helper-local release-record outcome so retained cleanup ownership stays reviewable as its own shared helper step",
    "records whether a successful planned scatterlist map retains detach-time unmap ownership on success",
    "records whether impossible over-mapped scatterlist results free the release record and avoid retaining detach-time unmap ownership",
    "routes `planManagedScatterlistUnmap(...)` through exact original-entry and mapped-entry matching so release drift stays reviewable without claiming live unmap side effects",
    "records whether a release-count mismatch surfaces a warn-on-release-miss outcome without claiming live unmap side effects",
    "exposes `scatterlistReleaseMatches(...)` as the helper-first exact-match check rather than folding that policy into broader runtime ownership",
    "`zigux/tests/phase13_devres_scatterlist_planner_manifest.json`",
    "does not claim live DMA mapping side effects, scatterlist ownership mutation, IOMMU state, DMA attributes, or wider devres group teardown behavior",
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

SCATTERLIST_PLANNER_MANIFEST_MARKERS = [
    '"lane_key": "P13-L08"',
    '"phase": "Phase 13"',
    '"anchor": "lib/devres.c"',
    '"packet": "phase13-devres-scatterlist-planner"',
    '"status": "starter_landed"',
    '"Documentation/zigux/phase13-devres-scatterlist-planner.md"',
    '"zigux/tests/phase13_devres_scatterlist_planner_manifest.json"',
    '"overmapped_request_owner": "zigux/tests/phase13_devres_scatterlist.zig"',
    '"warn_on_release_miss_owner": "zigux/tests/phase13_devres_scatterlist.zig"',
    '"planManagedScatterlistMap"',
    '"scatterlistReleaseMatches"',
    '"planManagedScatterlistUnmap"',
    '"impossible over-mapped scatterlist results free the release record"',
    '"warn-on-release-miss outcome"',
    '"id": "phase13-devres-live-scatterlist-ownership"',
    '"id": "phase13-devres-live-sg-table-lifecycle"',
    '"id": "phase13-devres-generic-dma-map-family"',
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
    'try requireContains(slice, "`zigux/tests/phase13_devres_dma_coherent.zig` plus `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-planner.md`, `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist_build.zig`, and `scripts/zigux/check-phase13-devres-mmio-packet.py` keep the current packet helper-first and planning-only");',
]

HELPER_REQUIRED_MARKERS = [
    "pub const ModuleDescriptor = struct {",
    ".provides_dmam_alloc_coherent_planning = true",
    ".touches_live_dma = false",
    ".touches_live_scatterlist = false",
    "pub fn planManagedDmamAllocCoherent",
    "pub fn planManagedDmamFreeCoherent",
]

HELPER_FORBIDDEN_MARKERS = [
    "devm_iounmap(",
    "devm_ioremap_np(",
    "devm_of_iomap(",
    "devm_arch_phys_wc_add(",
    "devm_arch_io_reserve_memtype_wc(",
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
    'test "phase13 devres frees the scatterlist release record when mapped segments exceed the original count" {',
    'test "phase13 devres rejects scatterlist planning when the release record cannot be allocated" {',
    'test "phase13 devres scatterlist release matching stays exact across original and mapped counts" {',
    'test "phase13 devres scatterlist unmap planning warns when release counts drift" {',
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


def collect_unexpected(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:unexpected_marker:{marker}" for marker in markers if marker in text]


def validate(root: Path) -> list[str]:
    issues = [f"missing_file:{rel.as_posix()}" for rel in REQUIRED_FILES if not (root / rel).exists()]
    if issues:
        return issues

    checks = [
        (SLICE_PATH, SLICE_MARKERS, "slice"),
        (SURVEY_PATH, SURVEY_MARKERS, "survey"),
        (PLANNER_NOTE_PATH, PLANNER_NOTE_MARKERS, "planner_note"),
        (SCATTERLIST_SLICE_PATH, SCATTERLIST_SLICE_MARKERS, "scatterlist_slice"),
        (SCATTERLIST_PLANNER_NOTE_PATH, SCATTERLIST_PLANNER_NOTE_MARKERS, "scatterlist_planner_note"),
        (PLANNER_MANIFEST_PATH, PLANNER_MANIFEST_MARKERS, "planner_manifest"),
        (SCATTERLIST_PLANNER_MANIFEST_PATH, SCATTERLIST_PLANNER_MANIFEST_MARKERS, "scatterlist_planner_manifest"),
        (PLANNER_REPLAY_PATH, PLANNER_REPLAY_MARKERS, "planner_replay"),
        (DMA_REPLAY_PATH, DMA_REPLAY_MARKERS, "dma_replay"),
        (HELPER_PATH, HELPER_REQUIRED_MARKERS, "helper"),
        (SCATTERLIST_HELPER_PATH, SCATTERLIST_HELPER_MARKERS, "scatterlist_helper"),
        (SCATTERLIST_REPLAY_PATH, SCATTERLIST_REPLAY_MARKERS, "scatterlist_replay"),
        (SCATTERLIST_BUILD_PATH, SCATTERLIST_BUILD_MARKERS, "scatterlist_build"),
    ]

    for rel, markers, prefix in checks:
        issues.extend(collect_missing(read_text(root / rel), markers, prefix))

    issues.extend(
        collect_unexpected(read_text(root / HELPER_PATH), HELPER_FORBIDDEN_MARKERS, "helper_mmio_absence")
    )
    return issues


def seed_fixture_tree(root: Path) -> None:
    writes = {
        SLICE_PATH: "\n".join(SLICE_MARKERS) + "\n",
        SURVEY_PATH: "\n".join(SURVEY_MARKERS) + "\n",
        PLANNER_NOTE_PATH: "\n".join(PLANNER_NOTE_MARKERS) + "\n",
        SCATTERLIST_SLICE_PATH: "\n".join(SCATTERLIST_SLICE_MARKERS) + "\n",
        SCATTERLIST_PLANNER_NOTE_PATH: "\n".join(SCATTERLIST_PLANNER_NOTE_MARKERS) + "\n",
        PLANNER_MANIFEST_PATH: "\n".join(PLANNER_MANIFEST_MARKERS) + "\n",
        SCATTERLIST_PLANNER_MANIFEST_PATH: "\n".join(SCATTERLIST_PLANNER_MANIFEST_MARKERS) + "\n",
        PLANNER_REPLAY_PATH: "\n".join(PLANNER_REPLAY_MARKERS) + "\n",
        DMA_REPLAY_PATH: "\n".join(DMA_REPLAY_MARKERS) + "\n",
        HELPER_PATH: "\n".join(HELPER_REQUIRED_MARKERS) + "\n",
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
                != "The bounded current evidence is the survey note, the `dmam_alloc_coherent()` planner note and manifest, the new pure `dmam_alloc_coherent()` helper plus replay, the direct DMA-boundary replay, the dedicated helper-first scatterlist planner note, manifest, helper, replay, scatterlist build shard, and the dedicated `scripts/zigux/check-phase13-devres-mmio-packet.py` guard, while the broader direct helper packet stays an explicit repo-reality gap."
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "slice:missing_marker:The bounded current evidence is the survey note, the `dmam_alloc_coherent()` planner note and manifest, the new pure `dmam_alloc_coherent()` helper plus replay, the direct DMA-boundary replay, the dedicated helper-first scatterlist planner note, manifest, helper, replay, scatterlist build shard, and the dedicated `scripts/zigux/check-phase13-devres-mmio-packet.py` guard, while the broader direct helper packet stays an explicit repo-reality gap."
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
                if marker != "blocked `phase13-devres-missing-devm-of-iomap-surface`"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ["survey:missing_marker:blocked `phase13-devres-missing-devm-of-iomap-surface`"],
            "survey_missing_iomap_gap_failed",
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
            root / SCATTERLIST_PLANNER_NOTE_PATH,
            "\n".join(
                marker
                for marker in SCATTERLIST_PLANNER_NOTE_MARKERS
                if marker != "records whether a release-count mismatch surfaces a warn-on-release-miss outcome without claiming live unmap side effects"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "scatterlist_planner_note:missing_marker:records whether a release-count mismatch surfaces a warn-on-release-miss outcome without claiming live unmap side effects"
            ],
            "scatterlist_planner_note_missing_warn_marker_failed",
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
            root / SCATTERLIST_PLANNER_MANIFEST_PATH,
            "\n".join(
                marker
                for marker in SCATTERLIST_PLANNER_MANIFEST_MARKERS
                if marker != '"warn_on_release_miss_owner": "zigux/tests/phase13_devres_scatterlist.zig"'
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                'scatterlist_planner_manifest:missing_marker:"warn_on_release_miss_owner": "zigux/tests/phase13_devres_scatterlist.zig"'
            ],
            "scatterlist_planner_manifest_missing_warn_owner_failed",
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
            root / HELPER_PATH,
            "\n".join(HELPER_REQUIRED_MARKERS + ["devm_of_iomap("]) + "\n",
        )
        assert_only(
            validate(root),
            ["helper_mmio_absence:unexpected_marker:devm_of_iomap("],
            "helper_unexpected_iomap_surface_failed",
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
                != 'test "phase13 devres scatterlist unmap planning warns when release counts drift" {'
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                'scatterlist_replay:missing_marker:test "phase13 devres scatterlist unmap planning warns when release counts drift" {'
            ],
            "scatterlist_replay_missing_warn_test_failed",
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
            + len(SCATTERLIST_PLANNER_NOTE_MARKERS)
            + len(PLANNER_MANIFEST_MARKERS)
            + len(SCATTERLIST_PLANNER_MANIFEST_MARKERS)
            + len(PLANNER_REPLAY_MARKERS)
            + len(DMA_REPLAY_MARKERS)
            + len(HELPER_REQUIRED_MARKERS)
            + len(HELPER_FORBIDDEN_MARKERS)
            + len(SCATTERLIST_HELPER_MARKERS)
            + len(SCATTERLIST_REPLAY_MARKERS)
            + len(SCATTERLIST_BUILD_MARKERS)
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
