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
        ".touches_live_mmio = false",
        "pub fn planDeviceTreeIomap",
    ],
    NOTE_PATH: [
        "pure `devm_of_iomap()` planning surface",
        "translated size is preserved when a requested region is denied as busy",
        "requested region is released again when remap later fails",
        "requested non-posted mapping type stays attached to the planning surface",
        "devm_ioremap_np()",
        "devm_iounmap()",
    ],
    MANIFEST_PATH: [
        "\"packet\": \"phase13-devres-iomap-planner\"",
        "\"status\": \"starter_landed\"",
        "\"translation_miss_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
        "\"request_region_denial_owner\": \"zigux/tests/phase13_devres_iomap_planner.zig\"",
        "\"id\": \"phase13-devres-missing-devm-ioremap-np-surface\"",
        "\"id\": \"phase13-devres-live-mmio-mapping-state\"",
    ],
    REPLAY_PATH: [
        "phase13 devres descriptor records helper-first iomap planning",
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
