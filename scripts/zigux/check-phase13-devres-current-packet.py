#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SLICE_PATH = Path("Documentation/zigux/phase13-devres-slice.md")
SURVEY_PATH = Path("Documentation/zigux/phase13-devres-survey.md")
HELPER_PATH = Path("lib/devres.zig")
SCATTERLIST_HELPER_PATH = Path("lib/devres_scatterlist.zig")
DMA_NOTE_PATH = Path("Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md")
DMA_MANIFEST_PATH = Path("zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json")
DMA_REPLAY_PATH = Path("zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig")
DMA_REPLAY_BUILD_PATH = Path("zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig")
DMA_CHECKER_PATH = Path("scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py")
DMA_BOUNDARY_CHECKER_PATH = Path("scripts/zigux/check-phase13-devres-dma-boundary.py")
SCATTERLIST_NOTE_PATH = Path("Documentation/zigux/phase13-devres-scatterlist-planner.md")
SCATTERLIST_MANIFEST_PATH = Path("zigux/tests/phase13_devres_scatterlist_planner_manifest.json")
SCATTERLIST_REPLAY_PATH = Path("zigux/tests/phase13_devres_scatterlist.zig")
SCATTERLIST_BUILD_PATH = Path("zigux/tests/phase13_devres_scatterlist_build.zig")
SCATTERLIST_CHECKER_PATH = Path("scripts/zigux/check-phase13-devres-scatterlist-planner.py")
IOUNMAP_NOTE_PATH = Path("Documentation/zigux/phase13-devres-iounmap-planner.md")
IOUNMAP_MANIFEST_PATH = Path("zigux/tests/phase13_devres_iounmap_planner_manifest.json")
IOUNMAP_REPLAY_PATH = Path("zigux/tests/phase13_devres_iounmap_planner.zig")
IOUNMAP_CHECKER_PATH = Path("scripts/zigux/check-phase13-devres-iounmap-planner.py")
IOMAP_NOTE_PATH = Path("Documentation/zigux/phase13-devres-iomap-planner.md")
IOMAP_MANIFEST_PATH = Path("zigux/tests/phase13_devres_iomap_planner_manifest.json")
IOMAP_REPLAY_PATH = Path("zigux/tests/phase13_devres_iomap_planner.zig")
IOMAP_CHECKER_PATH = Path("scripts/zigux/check-phase13-devres-iomap-planner.py")
MMIO_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase13-devres-mmio-packet.py")

REQUIRED_FILES = [
    SLICE_PATH,
    SURVEY_PATH,
    HELPER_PATH,
    SCATTERLIST_HELPER_PATH,
    DMA_NOTE_PATH,
    DMA_MANIFEST_PATH,
    DMA_REPLAY_PATH,
    DMA_REPLAY_BUILD_PATH,
    DMA_CHECKER_PATH,
    DMA_BOUNDARY_CHECKER_PATH,
    SCATTERLIST_NOTE_PATH,
    SCATTERLIST_MANIFEST_PATH,
    SCATTERLIST_REPLAY_PATH,
    SCATTERLIST_BUILD_PATH,
    SCATTERLIST_CHECKER_PATH,
    IOUNMAP_NOTE_PATH,
    IOUNMAP_MANIFEST_PATH,
    IOUNMAP_REPLAY_PATH,
    IOUNMAP_CHECKER_PATH,
    IOMAP_NOTE_PATH,
    IOMAP_MANIFEST_PATH,
    IOMAP_REPLAY_PATH,
    IOMAP_CHECKER_PATH,
    MMIO_PACKET_CHECKER_PATH,
]

SLICE_MARKERS = [
    "`scripts/zigux/check-phase13-devres-current-packet.py` keeps the same-lane survey, planner, helper, replay, and checker surfaces aligned before widening into any missing non-posted or arch-memtype helper work",
    "the dedicated packet checkers, and the new current-packet checker",
    "rerun `python3 scripts/zigux/check-phase13-devres-current-packet.py` before widening anything else",
]

SURVEY_MARKERS = [
    "the dedicated current-packet checker",
    "`scripts/zigux/check-phase13-devres-current-packet.py` now fail-closes across the slice, survey, helper, planner, replay, and existing checker surfaces",
    "scripts/zigux/check-phase13-devres-current-packet.py",
    "landed `phase13-devres-current-packet-checker`",
    "Only rematerialize a helper-first non-posted or arch-memtype planner if `scripts/zigux/check-phase13-devres-current-packet.py`",
    "one helper-local arch-WC release-record foothold",
    "`.provides_arch_phys_wc_add_planning = true`, `planManagedArchPhysWcAdd(...)`",
]

HELPER_MARKERS = [
    ".provides_dmam_alloc_coherent_planning = true",
    ".provides_release_record_lifetime_planning = true",
    ".provides_release_call_planning = true",
    ".provides_dmam_detach_cleanup_transition_planning = true",
    ".provides_of_iomap_planning = true",
    ".provides_of_iomap_cleanup_handoff_planning = true",
    ".provides_iounmap_cleanup_planning = true",
    ".provides_arch_phys_wc_add_planning = true",
    ".touches_live_dma = false",
    ".touches_live_scatterlist = false",
    ".touches_live_mmio = false",
    "pub fn planManagedDmamAllocCoherent",
    "pub fn planManagedDmamDetachCleanup(",
    "pub fn planDeviceTreeIomap(",
    "pub fn planDeviceTreeIomapCleanupHandoff(",
    "pub fn planManagedIounmapCleanup(",
    "pub fn planManagedArchPhysWcAdd(",
]

SCATTERLIST_HELPER_MARKERS = [
    ".provides_scatterlist_lifetime_planning = true",
    ".touches_live_dma = false",
    ".touches_live_scatterlist = false",
    "pub fn planManagedScatterlistMap",
    "pub fn scatterlistReleaseMatches",
    "pub fn planManagedScatterlistUnmap",
]

FORBIDDEN_HELPER_MARKERS = [
    "devm_ioremap_np(",
    "devm_of_iomap(",
    "devm_arch_phys_wc_add(",
    "devm_arch_io_reserve_memtype_wc(",
]

FORBIDDEN_SCATTERLIST_HELPER_MARKERS = [
    "dma_map_sg(",
    "dma_unmap_sg(",
    "dma_map_sgtable(",
    "sg_alloc_table(",
    "sg_free_table(",
]

PATH_MARKERS = {
    DMA_NOTE_PATH: [
        "pure `dmam_alloc_coherent()` planning surface",
        "`scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py` is the packet-local fail-closed checker",
    ],
    DMA_MANIFEST_PATH: [
        "\"packet\": \"phase13-devres-dmam-alloc-coherent-planner\"",
        "\"status\": \"starter_landed\"",
    ],
    DMA_REPLAY_PATH: [
        "phase13 devres descriptor records helper-first dmam_alloc_coherent planning",
        "phase13 devres dmam_alloc_coherent checker stays packet-local",
    ],
    DMA_REPLAY_BUILD_PATH: [
        "phase13-devres-dmam-alloc-zero-size-replay",
        "Run the Phase 13 devres zero-size replay",
        "../../lib/devres.zig",
        "phase13_devres_dmam_alloc_zero_size_replay.zig",
    ],
    DMA_CHECKER_PATH: [
        "PHASE13_DEVRES_DMAM_ALLOC_COHERENT_PLANNER_SELF_TEST=pass",
        "PHASE13_DEVRES_DMAM_ALLOC_COHERENT_PLANNER=pass",
    ],
    DMA_BOUNDARY_CHECKER_PATH: [
        "PHASE13_DEVRES_DMA_BOUNDARY_SELF_TEST=pass",
        "PHASE13_DEVRES_DMA_BOUNDARY=pass",
        "DMA_REPLAY_BUILD_PATH = Path(\"zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig\")",
        "SCATTERLIST_BUILD_PATH = Path(\"zigux/tests/phase13_devres_scatterlist_build.zig\")",
    ],
    SCATTERLIST_NOTE_PATH: [
        "pure scatterlist lifetime planning surface",
        "`scripts/zigux/check-phase13-devres-scatterlist-planner.py` is the packet-local validation guard",
    ],
    SCATTERLIST_MANIFEST_PATH: [
        "\"packet\": \"phase13-devres-scatterlist-planner\"",
        "\"status\": \"starter_landed\"",
    ],
    SCATTERLIST_REPLAY_PATH: [
        "phase13 devres descriptor records helper-first scatterlist planning",
        "phase13 devres scatterlist planner checker stays packet-local",
    ],
    SCATTERLIST_BUILD_PATH: [
        "phase13-devres-scatterlist-tests",
        "Run Phase 13 devres scatterlist helper tests",
        "../../lib/devres_scatterlist.zig",
        "phase13_devres_scatterlist.zig",
    ],
    SCATTERLIST_CHECKER_PATH: [
        "PHASE13_DEVRES_SCATTERLIST_PLANNER_SELF_TEST=pass",
        "PHASE13_DEVRES_SCATTERLIST_PLANNER=pass",
    ],
    IOUNMAP_NOTE_PATH: [
        "pure `devm_iounmap()` cleanup planning surface",
        "`scripts/zigux/check-phase13-devres-iounmap-planner.py` is the packet-local fail-closed checker",
    ],
    IOUNMAP_MANIFEST_PATH: [
        "\"packet\": \"phase13-devres-iounmap-planner\"",
        "\"status\": \"starter_landed\"",
    ],
    IOUNMAP_REPLAY_PATH: [
        "phase13 devres descriptor records helper-first iounmap cleanup planning",
        "phase13 devres iounmap planner checker stays packet-local",
    ],
    IOUNMAP_CHECKER_PATH: [
        "PHASE13_DEVRES_IOUNMAP_PLANNER_SELF_TEST=pass",
        "PHASE13_DEVRES_IOUNMAP_PLANNER=pass",
    ],
    IOMAP_NOTE_PATH: [
        "pure `devm_of_iomap()` planning surface",
        "`scripts/zigux/check-phase13-devres-iomap-planner.py` is the packet-local fail-closed checker",
    ],
    IOMAP_MANIFEST_PATH: [
        "\"packet\": \"phase13-devres-iomap-planner\"",
        "\"status\": \"starter_landed\"",
    ],
    IOMAP_REPLAY_PATH: [
        "phase13 devres descriptor records helper-first iomap planning",
        "phase13 devres iomap planner checker stays packet-local",
    ],
    IOMAP_CHECKER_PATH: [
        "PHASE13_DEVRES_IOMAP_PLANNER_SELF_TEST=pass",
        "PHASE13_DEVRES_IOMAP_PLANNER=pass",
    ],
    MMIO_PACKET_CHECKER_PATH: [
        "PHASE13_DEVRES_MMIO_PACKET_SELF_TEST=pass",
        "PHASE13_DEVRES_MMIO_PACKET=pass",
    ],
}


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

    issues.extend(collect_missing(read_text(root / SLICE_PATH), SLICE_MARKERS, "slice"))
    issues.extend(collect_missing(read_text(root / SURVEY_PATH), SURVEY_MARKERS, "survey"))
    issues.extend(collect_missing(read_text(root / HELPER_PATH), HELPER_MARKERS, "helper"))
    issues.extend(collect_missing(read_text(root / SCATTERLIST_HELPER_PATH), SCATTERLIST_HELPER_MARKERS, "scatterlist_helper"))
    issues.extend(collect_unexpected(read_text(root / HELPER_PATH), FORBIDDEN_HELPER_MARKERS, "helper_scope"))
    issues.extend(collect_unexpected(read_text(root / SCATTERLIST_HELPER_PATH), FORBIDDEN_SCATTERLIST_HELPER_MARKERS, "scatterlist_helper_scope"))

    for rel, markers in PATH_MARKERS.items():
        issues.extend(collect_missing(read_text(root / rel), markers, rel.as_posix()))

    return issues


def seed_fixture_tree(root: Path) -> None:
    write_text(root / SLICE_PATH, "\n".join(SLICE_MARKERS) + "\n")
    write_text(root / SURVEY_PATH, "\n".join(SURVEY_MARKERS) + "\n")
    write_text(root / HELPER_PATH, "\n".join(HELPER_MARKERS) + "\n")
    write_text(root / SCATTERLIST_HELPER_PATH, "\n".join(SCATTERLIST_HELPER_MARKERS) + "\n")
    for rel, markers in PATH_MARKERS.items():
        write_text(root / rel, "\n".join(markers) + "\n")


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_devres_current_packet_") as temp_dir:
        root = Path(temp_dir)

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
        write_text(root / SLICE_PATH, "\n".join(SLICE_MARKERS[:-1]) + "\n")
        assert_only(
            validate(root),
            ["slice:missing_marker:rerun `python3 scripts/zigux/check-phase13-devres-current-packet.py` before widening anything else"],
            "missing_slice_marker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / HELPER_PATH, "\n".join(HELPER_MARKERS + ["devm_ioremap_np("]) + "\n")
        assert_only(
            validate(root),
            ["helper_scope:unexpected_marker:devm_ioremap_np("],
            "unexpected_helper_scope_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / DMA_CHECKER_PATH,
            "PHASE13_DEVRES_DMAM_ALLOC_COHERENT_PLANNER_SELF_TEST=pass\n",
        )
        assert_only(
            validate(root),
            [f"{DMA_CHECKER_PATH.as_posix()}:missing_marker:PHASE13_DEVRES_DMAM_ALLOC_COHERENT_PLANNER=pass"],
            "missing_dma_checker_marker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / DMA_BOUNDARY_CHECKER_PATH,
            "\n".join(
                marker
                for marker in PATH_MARKERS[DMA_BOUNDARY_CHECKER_PATH]
                if marker != "SCATTERLIST_BUILD_PATH = Path(\"zigux/tests/phase13_devres_scatterlist_build.zig\")"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                f"{DMA_BOUNDARY_CHECKER_PATH.as_posix()}:missing_marker:SCATTERLIST_BUILD_PATH = Path(\"zigux/tests/phase13_devres_scatterlist_build.zig\")"
            ],
            "missing_dma_boundary_marker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        (root / SCATTERLIST_BUILD_PATH).unlink()
        assert_only(
            validate(root),
            [f"missing_file:{SCATTERLIST_BUILD_PATH.as_posix()}"],
            "missing_scatterlist_build_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / MMIO_PACKET_CHECKER_PATH,
            "PHASE13_DEVRES_MMIO_PACKET_SELF_TEST=pass\n",
        )
        assert_only(
            validate(root),
            [f"{MMIO_PACKET_CHECKER_PATH.as_posix()}:missing_marker:PHASE13_DEVRES_MMIO_PACKET=pass"],
            "missing_mmio_checker_marker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / HELPER_PATH,
            "\n".join(marker for marker in HELPER_MARKERS if marker != ".provides_arch_phys_wc_add_planning = true") + "\n",
        )
        assert_only(
            validate(root),
            ["helper:missing_marker:.provides_arch_phys_wc_add_planning = true"],
            "missing_arch_wc_helper_marker_failed",
        )
        case_count += 1

    print("PHASE13_DEVRES_CURRENT_PACKET_SELF_TEST=pass")
    print(f"PHASE13_DEVRES_CURRENT_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on the shipped Phase 13 devres current-packet surfaces before widening into new helper work."
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
        print("PHASE13_DEVRES_CURRENT_PACKET=fail")
        return 1

    print("PHASE13_DEVRES_CURRENT_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())