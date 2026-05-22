#!/usr/bin/env python3
"""Fail-closed checker for the Phase 13 devres DMA/scatterlist boundary packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HELPER_PATH = Path("lib/devres.zig")
SURVEY_PATH = Path("Documentation/zigux/phase13-devres-survey.md")
DMA_REPLAY_PATH = Path("zigux/tests/phase13_devres_dma_coherent.zig")
SCATTERLIST_NOTE_PATH = Path("Documentation/zigux/phase13-devres-scatterlist-planner.md")
SCATTERLIST_MANIFEST_PATH = Path("zigux/tests/phase13_devres_scatterlist_planner_manifest.json")
SCATTERLIST_HELPER_PATH = Path("lib/devres_scatterlist.zig")
SCATTERLIST_REPLAY_PATH = Path("zigux/tests/phase13_devres_scatterlist.zig")

REQUIRED_FILES = [
    HELPER_PATH,
    SURVEY_PATH,
    DMA_REPLAY_PATH,
    SCATTERLIST_NOTE_PATH,
    SCATTERLIST_MANIFEST_PATH,
    SCATTERLIST_HELPER_PATH,
    SCATTERLIST_REPLAY_PATH,
]

HELPER_BLOCKED_MARKERS = [
    "dmam_alloc_coherent(",
    "dmam_free_coherent(",
    "dma_map_",
    "dma_unmap_",
    "dma_sync_",
    "dma_mmap_",
    "dma_map_sgtable()",
    "struct scatterlist",
    "sg_table",
    "sg_init_table(",
]

SURVEY_MARKERS = [
    "helper-first scatterlist helper and replay",
    "helper-source readback shows `lib/devres.zig` still omits",
    "`Documentation/zigux/phase13-devres-scatterlist-planner.md` records a landed pure scatterlist lifetime planning surface",
    "`zigux/tests/phase13_devres_scatterlist_planner_manifest.json` marks the packet as `starter_landed`",
    "blocked `phase13-devres-live-scatterlist-ownership`",
    "blocked `phase13-devres-live-sg-table-lifecycle`",
    "blocked `phase13-devres-generic-dma-map-family`",
    "`dmam_alloc_coherent()`",
    "`dmam_free_coherent()`",
    "`dma_sync_*`",
    "`dma_mmap_*`",
    "`dma_map_sgtable()`",
    "`sg_table`",
    "`lib/devres_scatterlist.zig` ships a pure scatterlist lifetime planning surface",
]

DMA_REPLAY_MARKERS = [
    'test "phase13 devres dma coherent replay records blocked dma and scatterlist boundaries" {',
    'test "phase13 devres dma coherent replay proves lib/devres stays planning-only at the boundary" {',
    'test "phase13 devres dma coherent replay anchors the survey-side scatterlist boundary" {',
    'test "phase13 devres dma coherent replay keeps scatterlist helper evidence helper-first" {',
    'try requireAbsent(helper, "dmam_alloc_coherent(");',
    'try requireAbsent(helper, "dmam_free_coherent(");',
    'try requireAbsent(helper, "dma_map_");',
    'try requireAbsent(helper, "dma_unmap_");',
    'try requireAbsent(helper, "dma_sync_");',
    'try requireAbsent(helper, "dma_mmap_");',
    'try requireAbsent(helper, "dma_map_sgtable()");',
    'try requireAbsent(helper, "struct scatterlist");',
    'try requireAbsent(helper, "sg_table");',
    'try requireAbsent(helper, "sg_init_table(");',
    'try requireContains(survey, "helper-first scatterlist helper and replay");',
    'try requireContains(survey, "helper-source readback shows `lib/devres.zig` still omits");',
    'try requireContains(survey, "`dmam_alloc_coherent()`");',
    'try requireContains(survey, "`dmam_free_coherent()`");',
    'try requireContains(survey, "`dma_map_sgtable()`");',
    'try requireContains(survey, "`sg_table`");',
]

SCATTERLIST_NOTE_MARKERS = [
    "pure scatterlist lifetime planning surface",
    "planManagedScatterlistMap(...)",
    "scatterlistReleaseMatches(...)",
    "planManagedScatterlistUnmap(...)",
    "retains detach-time unmap ownership on success",
    "failed mapping frees the release record",
    "warn-on-release-miss outcome",
    "dma_map_sgtable()",
    "sg_table",
]

SCATTERLIST_MANIFEST_MARKERS = [
    '"packet": "phase13-devres-scatterlist-planner"',
    '"status": "starter_landed"',
    '"scatterlist_lifetime_owner": "zigux/tests/phase13_devres_scatterlist.zig"',
    '"validation_guard": "scripts/zigux/check-phase13-devres-scatterlist-planner.py"',
    '"id": "phase13-devres-live-scatterlist-ownership"',
    '"id": "phase13-devres-live-sg-table-lifecycle"',
    '"id": "phase13-devres-generic-dma-map-family"',
]

SCATTERLIST_HELPER_MARKERS = [
    ".provides_scatterlist_lifetime_planning = true",
    ".touches_live_dma = false",
    ".touches_live_scatterlist = false",
    "pub fn planManagedScatterlistMap",
    "pub fn scatterlistReleaseMatches",
    "pub fn planManagedScatterlistUnmap",
]

SCATTERLIST_REPLAY_MARKERS = [
    "phase13 devres descriptor records helper-first scatterlist planning",
    "phase13 devres scatterlist planner manifest records the dedicated helper-first packet",
    "phase13 devres scatterlist planner note keeps the helper-first scatterlist slice bounded",
    "phase13 devres scatterlist planner checker stays packet-local",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_markers(text: str, label: str, markers: list[str], errors: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"{label}:missing_marker:{marker}")


def require_absent(text: str, label: str, markers: list[str], errors: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"{label}:unexpected_marker:{marker}")


def validate(root: Path) -> list[str]:
    errors: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            errors.append(f"missing:{relative_path.as_posix()}")

    if errors:
        return errors

    require_absent(read_text(root / HELPER_PATH), "helper", HELPER_BLOCKED_MARKERS, errors)
    require_markers(read_text(root / SURVEY_PATH), "survey", SURVEY_MARKERS, errors)
    require_markers(read_text(root / DMA_REPLAY_PATH), "dma_replay", DMA_REPLAY_MARKERS, errors)
    require_markers(read_text(root / SCATTERLIST_NOTE_PATH), "scatterlist_note", SCATTERLIST_NOTE_MARKERS, errors)
    require_markers(
        read_text(root / SCATTERLIST_MANIFEST_PATH),
        "scatterlist_manifest",
        SCATTERLIST_MANIFEST_MARKERS,
        errors,
    )
    require_markers(
        read_text(root / SCATTERLIST_HELPER_PATH),
        "scatterlist_helper",
        SCATTERLIST_HELPER_MARKERS,
        errors,
    )
    require_markers(
        read_text(root / SCATTERLIST_REPLAY_PATH),
        "scatterlist_replay",
        SCATTERLIST_REPLAY_MARKERS,
        errors,
    )

    return errors


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def seed_fixture_tree(root: Path) -> None:
    write_text(
        root / HELPER_PATH,
        "\n".join(
            [
                "pub fn planManagedIoremapResource() void {}",
                "pub fn planDeviceTreeIomap() void {}",
                "pub fn planArchIoReserveMemtypeWc() void {}",
            ]
        )
        + "\n",
    )
    write_text(root / SURVEY_PATH, "\n".join(SURVEY_MARKERS) + "\n")
    write_text(root / DMA_REPLAY_PATH, "\n".join(DMA_REPLAY_MARKERS) + "\n")
    write_text(root / SCATTERLIST_NOTE_PATH, "\n".join(SCATTERLIST_NOTE_MARKERS) + "\n")
    write_text(root / SCATTERLIST_MANIFEST_PATH, "\n".join(SCATTERLIST_MANIFEST_MARKERS) + "\n")
    write_text(root / SCATTERLIST_HELPER_PATH, "\n".join(SCATTERLIST_HELPER_MARKERS) + "\n")
    write_text(root / SCATTERLIST_REPLAY_PATH, "\n".join(SCATTERLIST_REPLAY_MARKERS) + "\n")


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="zigux_phase13_devres_dma_boundary_") as temp_dir:
        root = Path(temp_dir)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        seed_fixture_tree(root)
        (root / SCATTERLIST_NOTE_PATH).unlink()
        assert_only(
            validate(root),
            [f"missing:{SCATTERLIST_NOTE_PATH.as_posix()}"],
            "missing_scatterlist_note_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / HELPER_PATH, 'pub fn bad() void { _ = "dma_map_sgtable()"; }\n')
        assert_only(
            validate(root),
            [
                "helper:unexpected_marker:dma_map_",
                "helper:unexpected_marker:dma_map_sgtable()",
            ],
            "helper_unexpected_marker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / SCATTERLIST_MANIFEST_PATH, "broken\n")
        assert_only(
            validate(root),
            [f"scatterlist_manifest:missing_marker:{marker}" for marker in SCATTERLIST_MANIFEST_MARKERS],
            "scatterlist_manifest_missing_markers_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / SCATTERLIST_REPLAY_PATH,
            "\n".join(
                marker
                for marker in SCATTERLIST_REPLAY_MARKERS
                if marker != "phase13 devres scatterlist planner checker stays packet-local"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "scatterlist_replay:missing_marker:phase13 devres scatterlist planner checker stays packet-local"
            ],
            "scatterlist_replay_missing_marker_failed",
        )
        case_count += 1

    print("PHASE13_DEVRES_DMA_BOUNDARY_SELF_TEST=pass")
    print(f"PHASE13_DEVRES_DMA_BOUNDARY_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = validate(args.root)
    if errors:
        for error in errors:
            print(error)
        return 1

    print("PHASE13_DEVRES_DMA_BOUNDARY=pass")
    print(f"PHASE13_DEVRES_DMA_BOUNDARY_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
