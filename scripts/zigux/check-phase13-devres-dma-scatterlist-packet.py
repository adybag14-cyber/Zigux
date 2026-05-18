#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

CHECK_NAME = "PHASE13_DEVRES_DMA_SCATTERLIST_PACKET"

REQUIRED_MARKERS = {
    "Documentation/zigux/phase13-devres-survey.md": [
        "PHASE13_SLICE=devres-dma-scatterlist-boundary-survey",
        "phase13-devres-dmam-alloc-coherent-planner-note",
        "phase13-devres-dmam-alloc-coherent-planner-manifest",
        "phase13-devres-scatterlist-helper",
        "phase13-devres-scatterlist-replay",
        "blocked `phase13-devres-live-scatterlist-ownership`",
    ],
    "Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md": [
        "pure `dmam_alloc_coherent()` planning surface",
        "detach-time cleanup intent",
        "avoid retaining detach-time cleanup ownership",
        "does not treat the replay as proof",
        "dma_map_*",
        "dma_unmap_*",
        "dma_sync_*",
        "dma_mmap_*",
        "dma_map_sgtable()",
        "struct scatterlist",
        "sg_table",
        "sg_*",
    ],
    "zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json": [
        '"lane_key": "P13-L08"',
        '"packet": "phase13-devres-dmam-alloc-coherent-planner"',
        '"status": "planning_only"',
        '"id": "phase13-devres-live-dmam-alloc-side-effects"',
        '"status": "blocked_on_dma_state"',
        '"id": "phase13-devres-live-scatterlist-ownership"',
        '"status": "blocked_on_scatterlist_state"',
    ],
    "zigux/tests/phase13_devres_dma_coherent.zig": [
        'test "phase13 devres dma coherent replay records blocked dma and scatterlist boundaries"',
        'test "phase13 devres dma coherent replay anchors the current slice reality"',
        'test "phase13 devres dma coherent replay keeps missing checker surfaces framed as gaps"',
        'test "phase13 devres dma coherent replay keeps the planner note helper-first"',
    ],
    "lib/devres_scatterlist.zig": [
        "provides_scatterlist_lifetime_planning = true",
        "touches_live_dma = false",
        "touches_live_scatterlist = false",
        "pub fn planManagedScatterlistMap",
        "pub fn planManagedScatterlistUnmap",
    ],
    "zigux/tests/phase13_devres_scatterlist.zig": [
        'test "phase13 devres descriptor records helper-first scatterlist planning"',
        'test "phase13 devres retains the release record when helper-first scatterlist planning succeeds"',
        'test "phase13 devres rejects scatterlist planning when the release record cannot be allocated"',
        'test "phase13 devres scatterlist release matching stays exact across original and mapped counts"',
    ],
}


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        file_path = root / relative_path
        if not file_path.is_file():
            failures.append(f"missing:{relative_path}")
            continue

        text = file_path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"missing-marker:{relative_path}:{marker}")
    return failures


def write_file(root: Path, relative_path: str, content: str) -> None:
    file_path = root / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


def seed_valid_tree(root: Path) -> None:
    write_file(
        root,
        "Documentation/zigux/phase13-devres-survey.md",
        "\n".join(
            [
                "# Survey",
                "PHASE13_SLICE=devres-dma-scatterlist-boundary-survey",
                "- phase13-devres-dmam-alloc-coherent-planner-note",
                "- phase13-devres-dmam-alloc-coherent-planner-manifest",
                "- phase13-devres-scatterlist-helper",
                "- phase13-devres-scatterlist-replay",
                "- blocked `phase13-devres-live-scatterlist-ownership`",
            ]
        )
        + "\n",
    )
    write_file(
        root,
        "Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md",
        "\n".join(
            [
                "# Planner",
                "pure `dmam_alloc_coherent()` planning surface",
                "detach-time cleanup intent",
                "avoid retaining detach-time cleanup ownership",
                "does not treat the replay as proof",
                "dma_map_*",
                "dma_unmap_*",
                "dma_sync_*",
                "dma_mmap_*",
                "dma_map_sgtable()",
                "struct scatterlist",
                "sg_table",
                "sg_*",
            ]
        )
        + "\n",
    )
    write_file(
        root,
        "zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json",
        "\n".join(
            [
                "{",
                '  "lane_key": "P13-L08",',
                '  "packet": "phase13-devres-dmam-alloc-coherent-planner",',
                '  "status": "planning_only",',
                '  "blocked_boundaries": [',
                '    { "id": "phase13-devres-live-dmam-alloc-side-effects", "status": "blocked_on_dma_state" },',
                '    { "id": "phase13-devres-live-scatterlist-ownership", "status": "blocked_on_scatterlist_state" }',
                "  ]",
                "}",
            ]
        )
        + "\n",
    )
    write_file(
        root,
        "zigux/tests/phase13_devres_dma_coherent.zig",
        "\n".join(
            [
                'test "phase13 devres dma coherent replay records blocked dma and scatterlist boundaries" {}',
                'test "phase13 devres dma coherent replay anchors the current slice reality" {}',
                'test "phase13 devres dma coherent replay keeps missing checker surfaces framed as gaps" {}',
                'test "phase13 devres dma coherent replay keeps the planner note helper-first" {}',
            ]
        )
        + "\n",
    )
    write_file(
        root,
        "lib/devres_scatterlist.zig",
        "\n".join(
            [
                "pub const descriptor = .{",
                "    .provides_scatterlist_lifetime_planning = true,",
                "    .touches_live_dma = false,",
                "    .touches_live_scatterlist = false,",
                "};",
                "pub fn planManagedScatterlistMap() void {}",
                "pub fn planManagedScatterlistUnmap() void {}",
            ]
        )
        + "\n",
    )
    write_file(
        root,
        "zigux/tests/phase13_devres_scatterlist.zig",
        "\n".join(
            [
                'test "phase13 devres descriptor records helper-first scatterlist planning" {}',
                'test "phase13 devres retains the release record when helper-first scatterlist planning succeeds" {}',
                'test "phase13 devres rejects scatterlist planning when the release record cannot be allocated" {}',
                'test "phase13 devres scatterlist release matching stays exact across original and mapped counts" {}',
            ]
        )
        + "\n",
    )


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase13_dma_scatterlist_checker_"))
    try:
        seed_valid_tree(tmpdir)

        cases = 0
        if validate(tmpdir):
            raise AssertionError("expected seeded packet to pass")
        cases += 1

        survey_missing = tmpdir / "Documentation/zigux/phase13-devres-survey.md"
        survey_backup = survey_missing.read_text(encoding="utf-8")
        survey_missing.write_text(survey_backup.replace("phase13-devres-scatterlist-replay", ""), encoding="utf-8")
        failures = validate(tmpdir)
        if not any("phase13-devres-scatterlist-replay" in failure for failure in failures):
            raise AssertionError("expected survey marker failure")
        survey_missing.write_text(survey_backup, encoding="utf-8")
        cases += 1

        manifest = tmpdir / "zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json"
        manifest_backup = manifest.read_text(encoding="utf-8")
        manifest.write_text(manifest_backup.replace("blocked_on_scatterlist_state", "planning_only"), encoding="utf-8")
        failures = validate(tmpdir)
        if not any("blocked_on_scatterlist_state" in failure for failure in failures):
            raise AssertionError("expected manifest failure")
        manifest.write_text(manifest_backup, encoding="utf-8")
        cases += 1

        helper = tmpdir / "lib/devres_scatterlist.zig"
        helper_backup = helper.read_text(encoding="utf-8")
        helper.write_text(helper_backup.replace("touches_live_scatterlist = false", "touches_live_scatterlist = true"), encoding="utf-8")
        failures = validate(tmpdir)
        if not any("touches_live_scatterlist = false" in failure for failure in failures):
            raise AssertionError("expected helper flag failure")
        helper.write_text(helper_backup, encoding="utf-8")
        cases += 1

        scatterlist_test = tmpdir / "zigux/tests/phase13_devres_scatterlist.zig"
        scatterlist_test_backup = scatterlist_test.read_text(encoding="utf-8")
        scatterlist_test.write_text(
            scatterlist_test_backup.replace(
                'test "phase13 devres scatterlist release matching stays exact across original and mapped counts" {}',
                "",
            ),
            encoding="utf-8",
        )
        failures = validate(tmpdir)
        if not any("release matching stays exact" in failure for failure in failures):
            raise AssertionError("expected scatterlist replay failure")
        cases += 1

        print(f"{CHECK_NAME}_SELF_TEST=pass")
        print(f"{CHECK_NAME}_SELF_TEST_CASES={cases}")
        return 0
    finally:
        shutil.rmtree(tmpdir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check the current Phase 13 devres DMA/scatterlist packet.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("Phase 13 devres DMA/scatterlist packet check passed.")
    print(f"{CHECK_NAME}_REQUIRED_PATH_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
