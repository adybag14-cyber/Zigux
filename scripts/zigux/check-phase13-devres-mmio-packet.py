#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SLICE_PATH = Path("Documentation/zigux/phase13-devres-slice.md")
SURVEY_PATH = Path("Documentation/zigux/phase13-devres-survey.md")
IOUNMAP_NOTE_PATH = Path("Documentation/zigux/phase13-devres-iounmap-planner.md")
IOUNMAP_MANIFEST_PATH = Path("zigux/tests/phase13_devres_iounmap_planner_manifest.json")
IOUNMAP_REPLAY_PATH = Path("zigux/tests/phase13_devres_iounmap_planner.zig")
IOMAP_NOTE_PATH = Path("Documentation/zigux/phase13-devres-iomap-planner.md")
IOMAP_MANIFEST_PATH = Path("zigux/tests/phase13_devres_iomap_planner_manifest.json")
IOMAP_REPLAY_PATH = Path("zigux/tests/phase13_devres_iomap_planner.zig")
HELPER_PATH = Path("lib/devres.zig")
DMA_BOUNDARY_CHECKER_PATH = Path("scripts/zigux/check-phase13-devres-dma-boundary.py")
IOUNMAP_CHECKER_PATH = Path("scripts/zigux/check-phase13-devres-iounmap-planner.py")
IOMAP_CHECKER_PATH = Path("scripts/zigux/check-phase13-devres-iomap-planner.py")
CURRENT_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase13-devres-current-packet.py")

REQUIRED_FILES = [
    SLICE_PATH,
    SURVEY_PATH,
    IOUNMAP_NOTE_PATH,
    IOUNMAP_MANIFEST_PATH,
    IOUNMAP_REPLAY_PATH,
    IOMAP_NOTE_PATH,
    IOMAP_MANIFEST_PATH,
    IOMAP_REPLAY_PATH,
    HELPER_PATH,
    DMA_BOUNDARY_CHECKER_PATH,
    IOUNMAP_CHECKER_PATH,
    IOMAP_CHECKER_PATH,
    CURRENT_PACKET_CHECKER_PATH,
]

DIRECT_PACKET_GAP_PATHS = [
    Path("zigux/tests/phase13_devres.zig"),
    Path("zigux/tests/phase13_devres_reviewability.zig"),
    Path("zigux/tests/phase13_devres_manifest.json"),
    Path("scripts/zigux/check-phase13-devres-packet.py"),
    Path("scripts/zigux/check-phase13-devres-packet-alignment.py"),
]

SLICE_MARKERS = [
    "# Phase 13 devres Slice",
    "`Documentation/zigux/phase13-devres-iounmap-planner.md`",
    "`zigux/tests/phase13_devres_iounmap_planner.zig`",
    "`scripts/zigux/check-phase13-devres-dma-boundary.py`",
    "`scripts/zigux/check-phase13-devres-iounmap-planner.py`",
    "`Documentation/zigux/phase13-devres-iomap-planner.md`",
    "`zigux/tests/phase13_devres_iomap_planner.zig`",
    "`scripts/zigux/check-phase13-devres-iomap-planner.py`",
    "current packet helper-first, planning-only, and MMIO-bounded",
]

SURVEY_MARKERS = [
    "# Phase 13 devres DMA, scatterlist, and MMIO Boundary Survey",
    "helper-first iomap planning evidence",
    "`Documentation/zigux/phase13-devres-iounmap-planner.md` records a landed pure `devm_iounmap()` cleanup planning surface",
    "`zigux/tests/phase13_devres_iounmap_planner_manifest.json` marks the packet as `starter_landed`",
    "`Documentation/zigux/phase13-devres-iomap-planner.md` records a landed pure `devm_of_iomap()` planning surface",
    "`zigux/tests/phase13_devres_iomap_planner_manifest.json` marks the packet as `starter_landed`",
    "helper-first iomap planning through `planDeviceTreeIomap(...)`",
    "helper-side iomap cleanup handoff in `lib/devres.zig`",
    "`.provides_of_iomap_cleanup_handoff_planning = true` and `planDeviceTreeIomapCleanupHandoff(...)`",
    "`scripts/zigux/check-phase13-devres-dma-boundary.py`",
    "`zigux/tests/phase13_devres.zig`",
    "`zigux/tests/phase13_devres_reviewability.zig`",
    "`zigux/tests/phase13_devres_manifest.json`",
    "`scripts/zigux/check-phase13-devres-packet.py`",
    "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
    "blocked `phase13-devres-missing-devm-ioremap-np-surface`",
    "blocked `phase13-devres-missing-devm-arch-phys-wc-add-surface`",
    "blocked `phase13-devres-missing-devm-arch-io-reserve-memtype-wc-surface`",
    "blocked `phase13-devres-live-mmio-mapping-state`",
    "blocked `phase13-devres-live-device-tree-walks`",
    "blocked `phase13-devres-live-arch-memtype-mutation`",
]

IOUNMAP_NOTE_MARKERS = [
    "# Phase 13 devres iounmap Planner",
    "pure `devm_iounmap()` cleanup planning surface",
    "planManagedIounmapCleanup(...)",
    "tracked mapping owner generates cleanup work",
    "warn-on-release-miss outcome",
    "devm_ioremap_np()",
    "devm_of_iomap()",
    "devm_arch_phys_wc_add()",
    "devm_arch_io_reserve_memtype_wc()",
]

IOUNMAP_MANIFEST_MARKERS = [
    "\"packet\": \"phase13-devres-iounmap-planner\"",
    "\"status\": \"starter_landed\"",
    "\"iounmap_cleanup_owner\": \"zigux/tests/phase13_devres_iounmap_planner.zig\"",
    "\"warn_on_release_miss_owner\": \"zigux/tests/phase13_devres_iounmap_planner.zig\"",
    "\"id\": \"phase13-devres-missing-devm-ioremap-np-surface\"",
    "\"id\": \"phase13-devres-missing-devm-arch-phys-wc-add-surface\"",
    "\"id\": \"phase13-devres-missing-devm-arch-io-reserve-memtype-wc-surface\"",
    "\"id\": \"phase13-devres-live-mmio-mapping-state\"",
    "\"id\": \"phase13-devres-live-device-tree-walks\"",
    "\"id\": \"phase13-devres-live-arch-memtype-mutation\"",
]

IOUNMAP_REPLAY_MARKERS = [
    "phase13 devres descriptor records helper-first iounmap cleanup planning",
    "phase13 devres iounmap planner manifest records the landed helper-first mmio scope",
    "phase13 devres iounmap planner note keeps the helper-first mmio slice bounded",
    "phase13 devres iounmap planner checker stays packet-local",
]

IOMAP_NOTE_MARKERS = [
    "# Phase 13 devres iomap Planner",
    "pure `devm_of_iomap()` planning surface",
    "planDeviceTreeIomap(...)",
    "translated size is preserved when a requested region is denied as busy",
    "requested region is released again when remap later fails",
    "requested non-posted mapping type stays attached to the planning surface",
    "successful helper-first remap hands off to `devm_iounmap()` cleanup planning",
    "cleanup handoff consumes the matching release record or still warns when the release record is missing",
    "devm_ioremap_np()",
    "devm_iounmap()",
    "devm_arch_phys_wc_add()",
    "devm_arch_io_reserve_memtype_wc()",
]

IOMAP_MANIFEST_MARKERS = [
    "\"packet\": \"phase13-devres-iomap-planner\"",
    "\"status\": \"starter_landed\"",
    "\"translation_miss_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
    "\"request_region_denial_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
    "\"nonposted_wrapper_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
    "\"remap_failure_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
    "\"cleanup_handoff_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
    "\"cleanup_release_miss_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
    "planDeviceTreeIomapCleanupHandoff",
    "\"id\": \"phase13-devres-missing-devm-ioremap-np-surface\"",
    "\"id\": \"phase13-devres-missing-devm-arch-phys-wc-add-surface\"",
    "\"id\": \"phase13-devres-missing-devm-arch-io-reserve-memtype-wc-surface\"",
    "\"id\": \"phase13-devres-live-mmio-mapping-state\"",
    "\"id\": \"phase13-devres-live-device-tree-walks\"",
    "\"id\": \"phase13-devres-live-arch-memtype-mutation\"",
]

IOMAP_REPLAY_MARKERS = [
    "phase13 devres descriptor records helper-first iomap planning",
    "phase13 devres iomap cleanup handoff materializes helper-first iounmap cleanup after successful remap",
    "phase13 devres iomap cleanup handoff keeps missing release records warnable",
    "phase13 devres iomap planner manifest records the landed helper-first mmio scope",
    "phase13 devres iomap planner note keeps the helper-first mmio slice bounded",
    "phase13 devres iomap planner checker stays packet-local",
]

HELPER_REQUIRED_MARKERS = [
    ".provides_of_iomap_planning = true",
    ".provides_of_iomap_cleanup_handoff_planning = true",
    ".provides_iounmap_cleanup_planning = true",
    ".touches_live_mmio = false",
    "pub fn planDeviceTreeIomap",
    "pub fn planDeviceTreeIomapCleanupHandoff",
    "pub fn planManagedIounmapCleanup",
]

HELPER_FORBIDDEN_MARKERS = [
    "devm_iounmap(",
    "devm_ioremap_np(",
    "devm_of_iomap(",
    "devm_arch_phys_wc_add(",
    "devm_arch_io_reserve_memtype_wc(",
]

DMA_BOUNDARY_CHECKER_MARKERS = [
    "HELPER_PATH = Path(\"lib/devres.zig\")",
    "SURVEY_PATH = Path(\"Documentation/zigux/phase13-devres-survey.md\")",
    "DMA_REPLAY_PATH = Path(\"zigux/tests/phase13_devres_dma_coherent.zig\")",
    "SCATTERLIST_NOTE_PATH = Path(\"Documentation/zigux/phase13-devres-scatterlist-planner.md\")",
    "SCATTERLIST_MANIFEST_PATH = Path(\"zigux/tests/phase13_devres_scatterlist_planner_manifest.json\")",
    "SCATTERLIST_HELPER_PATH = Path(\"lib/devres_scatterlist.zig\")",
    "SCATTERLIST_REPLAY_PATH = Path(\"zigux/tests/phase13_devres_scatterlist.zig\")",
    "PHASE13_DEVRES_DMA_BOUNDARY_SELF_TEST=pass",
    "PHASE13_DEVRES_DMA_BOUNDARY=pass",
]

IOUNMAP_CHECKER_MARKERS = [
    "HELPER_PATH = Path(\"lib/devres.zig\")",
    "NOTE_PATH = Path(\"Documentation/zigux/phase13-devres-iounmap-planner.md\")",
    "MANIFEST_PATH = Path(\"zigux/tests/phase13_devres_iounmap_planner_manifest.json\")",
    "REPLAY_PATH = Path(\"zigux/tests/phase13_devres_iounmap_planner.zig\")",
    "PHASE13_DEVRES_IOUNMAP_PLANNER_SELF_TEST=pass",
    "PHASE13_DEVRES_IOUNMAP_PLANNER=pass",
]

IOMAP_CHECKER_MARKERS = [
    "HELPER_PATH = Path(\"lib/devres.zig\")",
    "NOTE_PATH = Path(\"Documentation/zigux/phase13-devres-iomap-planner.md\")",
    "MANIFEST_PATH = Path(\"zigux/tests/phase13_devres_iomap_planner_manifest.json\")",
    "REPLAY_PATH = Path(\"zigux/tests/phase13_devres_iomap_planner.zig\")",
    "PHASE13_DEVRES_IOMAP_PLANNER_SELF_TEST=pass",
    "PHASE13_DEVRES_IOMAP_PLANNER=pass",
]

CURRENT_PACKET_CHECKER_MARKERS = [
    "MMIO_PACKET_CHECKER_PATH = Path(\"scripts/zigux/check-phase13-devres-mmio-packet.py\")",
    "PHASE13_DEVRES_CURRENT_PACKET_SELF_TEST=pass",
    "PHASE13_DEVRES_CURRENT_PACKET=pass",
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

    issues.extend(
        f"unexpected_file:{rel.as_posix()}"
        for rel in DIRECT_PACKET_GAP_PATHS
        if (root / rel).exists()
    )

    checks = [
        (SLICE_PATH, SLICE_MARKERS, "slice"),
        (SURVEY_PATH, SURVEY_MARKERS, "survey"),
        (IOUNMAP_NOTE_PATH, IOUNMAP_NOTE_MARKERS, "iounmap_note"),
        (IOUNMAP_MANIFEST_PATH, IOUNMAP_MANIFEST_MARKERS, "iounmap_manifest"),
        (IOUNMAP_REPLAY_PATH, IOUNMAP_REPLAY_MARKERS, "iounmap_replay"),
        (IOMAP_NOTE_PATH, IOMAP_NOTE_MARKERS, "iomap_note"),
        (IOMAP_MANIFEST_PATH, IOMAP_MANIFEST_MARKERS, "iomap_manifest"),
        (IOMAP_REPLAY_PATH, IOMAP_REPLAY_MARKERS, "iomap_replay"),
        (HELPER_PATH, HELPER_REQUIRED_MARKERS, "helper"),
        (DMA_BOUNDARY_CHECKER_PATH, DMA_BOUNDARY_CHECKER_MARKERS, "dma_boundary_checker"),
        (IOUNMAP_CHECKER_PATH, IOUNMAP_CHECKER_MARKERS, "iounmap_checker"),
        (IOMAP_CHECKER_PATH, IOMAP_CHECKER_MARKERS, "iomap_checker"),
        (CURRENT_PACKET_CHECKER_PATH, CURRENT_PACKET_CHECKER_MARKERS, "current_packet_checker"),
    ]
    for rel, markers, prefix in checks:
        issues.extend(collect_missing(read_text(root / rel), markers, prefix))

    issues.extend(collect_unexpected(read_text(root / HELPER_PATH), HELPER_FORBIDDEN_MARKERS, "helper_mmio_absence"))
    return issues


def seed_fixture_tree(root: Path) -> None:
    writes = {
        SLICE_PATH: "\n".join(SLICE_MARKERS) + "\n",
        SURVEY_PATH: "\n".join(SURVEY_MARKERS) + "\n",
        IOUNMAP_NOTE_PATH: "\n".join(IOUNMAP_NOTE_MARKERS) + "\n",
        IOUNMAP_MANIFEST_PATH: "\n".join(IOUNMAP_MANIFEST_MARKERS) + "\n",
        IOUNMAP_REPLAY_PATH: "\n".join(IOUNMAP_REPLAY_MARKERS) + "\n",
        IOMAP_NOTE_PATH: "\n".join(IOMAP_NOTE_MARKERS) + "\n",
        IOMAP_MANIFEST_PATH: "\n".join(IOMAP_MANIFEST_MARKERS) + "\n",
        IOMAP_REPLAY_PATH: "\n".join(IOMAP_REPLAY_MARKERS) + "\n",
        HELPER_PATH: "\n".join(HELPER_REQUIRED_MARKERS) + "\n",
        DMA_BOUNDARY_CHECKER_PATH: "\n".join(DMA_BOUNDARY_CHECKER_MARKERS) + "\n",
        IOUNMAP_CHECKER_PATH: "\n".join(IOUNMAP_CHECKER_MARKERS) + "\n",
        IOMAP_CHECKER_PATH: "\n".join(IOMAP_CHECKER_MARKERS) + "\n",
        CURRENT_PACKET_CHECKER_PATH: "\n".join(CURRENT_PACKET_CHECKER_MARKERS) + "\n",
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
        write_text(root / DIRECT_PACKET_GAP_PATHS[0], "stale direct packet surface\n")
        assert_only(
            validate(root),
            [f"unexpected_file:{DIRECT_PACKET_GAP_PATHS[0].as_posix()}"],
            "unexpected_direct_packet_file_failed",
        )
        case_count += 1
        (root / DIRECT_PACKET_GAP_PATHS[0]).unlink()

        seed_fixture_tree(root)
        (root / DMA_BOUNDARY_CHECKER_PATH).unlink()
        assert_only(
            validate(root),
            [f"missing_file:{DMA_BOUNDARY_CHECKER_PATH.as_posix()}"],
            "missing_dma_boundary_checker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / SLICE_PATH,
            "\n".join(
                marker
                for marker in SLICE_MARKERS
                if marker != "`scripts/zigux/check-phase13-devres-dma-boundary.py`"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "slice:missing_marker:`scripts/zigux/check-phase13-devres-dma-boundary.py`",
            ],
            "missing_slice_dma_boundary_checker_marker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        (root / IOMAP_NOTE_PATH).unlink()
        assert_only(
            validate(root),
            [f"missing_file:{IOMAP_NOTE_PATH.as_posix()}"],
            "missing_iomap_note_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / SURVEY_PATH,
            "\n".join(
                marker
                for marker in SURVEY_MARKERS
                if marker != "`.provides_of_iomap_cleanup_handoff_planning = true` and `planDeviceTreeIomapCleanupHandoff(...)`"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "survey:missing_marker:`.provides_of_iomap_cleanup_handoff_planning = true` and `planDeviceTreeIomapCleanupHandoff(...)`",
            ],
            "missing_survey_cleanup_handoff_marker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / IOUNMAP_MANIFEST_PATH,
            "\n".join(
                marker
                for marker in IOUNMAP_MANIFEST_MARKERS
                if marker != "\"id\": \"phase13-devres-live-device-tree-walks\""
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "iounmap_manifest:missing_marker:\"id\": \"phase13-devres-live-device-tree-walks\"",
            ],
            "missing_iounmap_device_tree_marker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / IOMAP_MANIFEST_PATH,
            "\n".join(
                marker
                for marker in IOMAP_MANIFEST_MARKERS
                if marker != "\"cleanup_handoff_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\""
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "iomap_manifest:missing_marker:\"cleanup_handoff_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
            ],
            "missing_iomap_cleanup_handoff_owner_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / IOMAP_MANIFEST_PATH,
            "\n".join(
                marker
                for marker in IOMAP_MANIFEST_MARKERS
                if marker != "\"nonposted_wrapper_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\""
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "iomap_manifest:missing_marker:\"nonposted_wrapper_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
            ],
            "missing_iomap_nonposted_wrapper_owner_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / IOMAP_MANIFEST_PATH,
            "\n".join(
                marker
                for marker in IOMAP_MANIFEST_MARKERS
                if marker != "\"id\": \"phase13-devres-live-arch-memtype-mutation\""
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "iomap_manifest:missing_marker:\"id\": \"phase13-devres-live-arch-memtype-mutation\"",
            ],
            "missing_iomap_arch_memtype_marker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        (root / IOMAP_MANIFEST_PATH).unlink()
        assert_only(
            validate(root),
            [f"missing_file:{IOMAP_MANIFEST_PATH.as_posix()}"],
            "missing_iomap_manifest_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / CURRENT_PACKET_CHECKER_PATH,
            "\n".join(
                marker
                for marker in CURRENT_PACKET_CHECKER_MARKERS
                if marker != "MMIO_PACKET_CHECKER_PATH = Path(\"scripts/zigux/check-phase13-devres-mmio-packet.py\")"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "current_packet_checker:missing_marker:MMIO_PACKET_CHECKER_PATH = Path(\"scripts/zigux/check-phase13-devres-mmio-packet.py\")",
            ],
            "missing_current_packet_mmio_link_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / HELPER_PATH,
            "\n".join(
                marker for marker in HELPER_REQUIRED_MARKERS if marker != ".provides_of_iomap_cleanup_handoff_planning = true"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ["helper:missing_marker:.provides_of_iomap_cleanup_handoff_planning = true"],
            "missing_helper_cleanup_handoff_flag_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / HELPER_PATH, "\n".join(HELPER_REQUIRED_MARKERS + ["devm_iounmap("]) + "\n")
        assert_only(
            validate(root),
            ["helper_mmio_absence:unexpected_marker:devm_iounmap("],
            "unexpected_live_iounmap_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / HELPER_PATH, "\n".join(HELPER_REQUIRED_MARKERS + ["devm_ioremap_np("]) + "\n")
        assert_only(
            validate(root),
            ["helper_mmio_absence:unexpected_marker:devm_ioremap_np("],
            "unexpected_live_mmio_failed",
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
