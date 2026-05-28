#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HELPER_PATH = Path("lib/devres.zig")
NOTE_PATH = Path("Documentation/zigux/phase13-devres-iomap-planner.md")
MANIFEST_PATH = Path("zigux/tests/phase13_devres_iomap_planner_manifest.json")
REPLAY_PATH = Path("zigux/tests/phase13_devres_iomap_planner.zig")

REQUIRED_MARKERS = {
    HELPER_PATH: [
        ".provides_of_iomap_planning = true",
        ".provides_of_iomap_cleanup_handoff_planning = true",
        ".touches_live_mmio = false",
        "requires_nonposted_ioremap",
        "pub fn planDeviceTreeIomap",
        "pub fn planDeviceTreeIomapCleanupHandoff",
    ],
    NOTE_PATH: [
        "pure `devm_of_iomap()` planning surface",
        "translated size is preserved when a requested region is denied as busy",
        "requested region is released again when remap later fails",
        "requested non-posted mapping type stays attached to the planning surface",
        "translated helper-first remap would require the still-blocked `devm_ioremap_np()` wrapper",
        "successful helper-first remap hands off to `devm_iounmap()` cleanup planning",
        "cleanup handoff consumes the matching release record or still warns when the release record is missing",
        "devm_ioremap_np()",
        "devm_iounmap()",
        "devm_arch_phys_wc_add()",
        "devm_arch_io_reserve_memtype_wc()",
    ],
    MANIFEST_PATH: [
        "\"lane_key\": \"P13-L02\"",
        "\"phase\": \"Phase 13\"",
        "\"packet\": \"phase13-devres-iomap-planner\"",
        "\"status\": \"starter_landed\"",
        "\"translation_miss_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
        "\"request_region_denial_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
        "\"nonposted_wrapper_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
        "\"remap_failure_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
        "\"cleanup_handoff_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
        "\"cleanup_release_miss_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
        "planDeviceTreeIomapCleanupHandoff",
        "requires_nonposted_ioremap",
        "\"id\": \"phase13-devres-missing-devm-ioremap-np-surface\"",
        "\"id\": \"phase13-devres-missing-devm-arch-phys-wc-add-surface\"",
        "\"id\": \"phase13-devres-missing-devm-arch-io-reserve-memtype-wc-surface\"",
        "\"id\": \"phase13-devres-live-mmio-mapping-state\"",
        "\"id\": \"phase13-devres-live-device-tree-walks\"",
        "\"id\": \"phase13-devres-live-arch-memtype-mutation\"",
    ],
    REPLAY_PATH: [
        "phase13 devres descriptor records helper-first iomap planning",
        "phase13 devres iomap planning keeps the blocked non-posted wrapper requirement explicit",
        "phase13 devres iomap cleanup handoff materializes helper-first iounmap cleanup after successful remap",
        "phase13 devres iomap cleanup handoff keeps missing release records warnable",
        "phase13 devres iomap planner manifest records the landed helper-first mmio scope",
        "phase13 devres iomap planner note keeps the helper-first mmio slice bounded",
        "phase13 devres iomap planner checker stays packet-local",
    ],
}

FORBIDDEN_HELPER_MARKERS = [
    "devm_ioremap_np(",
    "devm_of_iomap(",
    "devm_arch_phys_wc_add(",
    "devm_arch_io_reserve_memtype_wc(",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in REQUIRED_MARKERS:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel.as_posix()}")
    if issues:
        return issues

    for rel, markers in REQUIRED_MARKERS.items():
        text = read_text(root / rel)
        for marker in markers:
            if marker not in text:
                issues.append(f"{rel.as_posix()}:missing_marker:{marker}")

    helper_text = read_text(root / HELPER_PATH)
    for marker in FORBIDDEN_HELPER_MARKERS:
        if marker in helper_text:
            issues.append(f"helper:unexpected_marker:{marker}")

    return issues


def seed_fixture_tree(root: Path) -> None:
    write_text(
        root / HELPER_PATH,
        "\n".join(REQUIRED_MARKERS[HELPER_PATH]) + "\n",
    )
    write_text(
        root / NOTE_PATH,
        "\n".join(REQUIRED_MARKERS[NOTE_PATH]) + "\n",
    )
    write_text(
        root / MANIFEST_PATH,
        "\n".join(REQUIRED_MARKERS[MANIFEST_PATH]) + "\n",
    )
    write_text(
        root / REPLAY_PATH,
        "\n".join(REQUIRED_MARKERS[REPLAY_PATH]) + "\n",
    )


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase13-devres-iomap-planner-") as tmp:
        root = Path(tmp)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        seed_fixture_tree(root)
        (root / NOTE_PATH).unlink()
        assert_only(
            validate(root),
            [f"missing_file:{NOTE_PATH.as_posix()}"],
            "missing_note_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / MANIFEST_PATH,
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS[MANIFEST_PATH]
                if marker != "\"remap_failure_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\""
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "zigux/tests/phase13_devres_iomap_planner_manifest.json:missing_marker:\"remap_failure_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
            ],
            "missing_remap_owner_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / MANIFEST_PATH,
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS[MANIFEST_PATH]
                if marker != "\"nonposted_wrapper_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\""
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "zigux/tests/phase13_devres_iomap_planner_manifest.json:missing_marker:\"nonposted_wrapper_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
            ],
            "missing_nonposted_owner_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / MANIFEST_PATH,
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS[MANIFEST_PATH]
                if marker != "\"cleanup_handoff_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\""
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "zigux/tests/phase13_devres_iomap_planner_manifest.json:missing_marker:\"cleanup_handoff_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
            ],
            "missing_cleanup_handoff_owner_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / HELPER_PATH,
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS[HELPER_PATH]
                if marker != ".provides_of_iomap_cleanup_handoff_planning = true"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "lib/devres.zig:missing_marker:.provides_of_iomap_cleanup_handoff_planning = true",
            ],
            "missing_helper_cleanup_handoff_flag_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / MANIFEST_PATH,
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS[MANIFEST_PATH]
                if marker != "\"lane_key\": \"P13-L02\""
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "zigux/tests/phase13_devres_iomap_planner_manifest.json:missing_marker:\"lane_key\": \"P13-L02\"",
            ],
            "missing_lane_key_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / MANIFEST_PATH,
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS[MANIFEST_PATH]
                if marker != "\"id\": \"phase13-devres-live-arch-memtype-mutation\""
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "zigux/tests/phase13_devres_iomap_planner_manifest.json:missing_marker:\"id\": \"phase13-devres-live-arch-memtype-mutation\"",
            ],
            "missing_arch_memtype_marker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / NOTE_PATH,
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS[NOTE_PATH]
                if marker != "translated helper-first remap would require the still-blocked `devm_ioremap_np()` wrapper"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "Documentation/zigux/phase13-devres-iomap-planner.md:missing_marker:translated helper-first remap would require the still-blocked `devm_ioremap_np()` wrapper",
            ],
            "missing_nonposted_note_marker_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / HELPER_PATH, "\n".join(REQUIRED_MARKERS[HELPER_PATH] + ["devm_ioremap_np("]) + "\n")
        assert_only(
            validate(root),
            ["helper:unexpected_marker:devm_ioremap_np("],
            "unexpected_live_mmio_failed",
        )
        case_count += 1

    print("PHASE13_DEVRES_IOMAP_PLANNER_SELF_TEST=pass")
    print(f"PHASE13_DEVRES_IOMAP_PLANNER_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        for issue in issues:
            print(issue)
        print("PHASE13_DEVRES_IOMAP_PLANNER=fail")
        return 1

    print("PHASE13_DEVRES_IOMAP_PLANNER=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
