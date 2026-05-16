#!/usr/bin/env python3
"""Fail-closed checker for the Phase 13 devres DMA/scatterlist boundary packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HELPER_PATH = Path("lib/devres.zig")
SURVEY_PATH = Path("Documentation/zigux/phase13-devres-survey.md")
DMA_REPLAY_PATH = Path("zigux/tests/phase13_devres_dma_coherent.zig")

HELPER_BLOCKED_MARKERS = [
    "dmam_alloc_",
    "dma_map_",
    "dma_unmap_",
    "dma_map_sgtable(",
    "struct scatterlist",
    "sg_table",
    "sg_",
]

SURVEY_MARKERS = [
    "helper-only DMA/scatterlist boundary",
    "helper-source readback on current `master` shows",
    "live DMA-backed helpers",
    "live scatterlist ownership",
    "dmam_alloc_*",
    "dma_unmap_*",
    "sg_table",
]

REPLAY_MARKERS = [
    'test "phase13 devres coherent-dma boundary helper surface exposes no dma or scatterlist ownership markers" {',
    'const helper = @embedFile("../../lib/devres.zig");',
    'try requireAbsent(helper, "dmam_alloc_");',
    'try requireAbsent(helper, "dma_map_");',
    'try requireAbsent(helper, "dma_unmap_");',
    'try requireAbsent(helper, "dma_map_sgtable(");',
    'try requireAbsent(helper, "struct scatterlist");',
    'try requireAbsent(helper, "sg_table");',
    'try requireAbsent(helper, "sg_");',
    'try requireContains(survey, "helper-source readback on current `master` shows");',
    'try requireContains(survey, "live DMA-backed helpers");',
    'try requireContains(survey, "live scatterlist ownership");',
    'try requireContains(survey, "dmam_alloc_*");',
    'try requireContains(survey, "dma_unmap_*");',
    'try requireContains(survey, "sg_table");',
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

    helper = root / HELPER_PATH
    survey = root / SURVEY_PATH
    replay = root / DMA_REPLAY_PATH

    expected_paths = (
        ("helper", HELPER_PATH, helper),
        ("survey", SURVEY_PATH, survey),
        ("dma_replay", DMA_REPLAY_PATH, replay),
    )
    for _, relative_path, full_path in expected_paths:
        if not full_path.exists():
            errors.append(f"missing:{relative_path.as_posix()}")

    if errors:
        return errors

    helper_text = read_text(helper)
    survey_text = read_text(survey)
    replay_text = read_text(replay)

    require_absent(helper_text, "helper", HELPER_BLOCKED_MARKERS, errors)
    require_markers(survey_text, "survey", SURVEY_MARKERS, errors)
    require_markers(replay_text, "dma_replay", REPLAY_MARKERS, errors)

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
    write_text(root / DMA_REPLAY_PATH, "\n".join(REPLAY_MARKERS) + "\n")


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
        (root / DMA_REPLAY_PATH).unlink()
        assert_only(
            validate(root),
            [f"missing:{DMA_REPLAY_PATH.as_posix()}"],
            "missing_dma_replay_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / HELPER_PATH, 'pub fn bad() void { _ = "dma_map_sgtable("; }\n')
        assert_only(
            validate(root),
            [
                "helper:unexpected_marker:dma_map_",
                "helper:unexpected_marker:dma_map_sgtable(",
            ],
            "helper_unexpected_marker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / SURVEY_PATH, "broken\n")
        assert_only(
            validate(root),
            [f"survey:missing_marker:{marker}" for marker in SURVEY_MARKERS],
            "survey_missing_markers_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / DMA_REPLAY_PATH,
            "\n".join(marker for marker in REPLAY_MARKERS if marker != 'try requireAbsent(helper, "sg_table");') + "\n",
        )
        assert_only(
            validate(root),
            ['dma_replay:missing_marker:try requireAbsent(helper, "sg_table");'],
            "dma_replay_missing_marker_failed",
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
