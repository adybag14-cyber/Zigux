#!/usr/bin/env python3
"""Fail-close the returned Phase 3 helper-slice reminders in scripts/zigux/README.md."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SCRIPTS_README_PATH = Path("scripts/zigux/README.md")

BITMAP_CPUMASK_NOTE = Path("Documentation/zigux/phase3-bitmap-cpumask-slice.md")
BITMAP_VIEW = Path("zigux/helpers/bitmap_view.zig")
CPUMASK_VIEW = Path("zigux/helpers/cpumask_view.zig")
BITMAP_CPUMASK_STARTER = Path("zigux/tests/phase3_bitmap_cpumask_starter_packet.zig")
BITMAP_CPUMASK_STARTER_BUILD = Path(
    "zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig"
)
BITMAP_CPUMASK_MANIFEST = Path("zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json")
BITMAP_CPUMASK_CHECKER = Path("scripts/zigux/check-phase3-bitmap-cpumask.py")

LIST_HLIST_NOTE = Path("Documentation/zigux/phase3-list-hlist-slice.md")
LIST_VIEW = Path("zigux/helpers/list_view.zig")
HLIST_VIEW = Path("zigux/helpers/hlist_view.zig")
LIST_HLIST_STARTER = Path("zigux/tests/phase3_list_hlist_starter_packet.zig")
LIST_HLIST_STARTER_BUILD = Path("zigux/tests/phase3_list_hlist_starter_packet_build.zig")

REQUIRED_FILES = (
    BITMAP_CPUMASK_NOTE,
    BITMAP_VIEW,
    CPUMASK_VIEW,
    BITMAP_CPUMASK_STARTER,
    BITMAP_CPUMASK_STARTER_BUILD,
    BITMAP_CPUMASK_MANIFEST,
    BITMAP_CPUMASK_CHECKER,
    LIST_HLIST_NOTE,
    LIST_VIEW,
    HLIST_VIEW,
    LIST_HLIST_STARTER,
    LIST_HLIST_STARTER_BUILD,
)

REQUIRED_MARKERS = (
    "Documentation/zigux/phase3-bitmap-cpumask-slice.md",
    "zigux/helpers/bitmap_view.zig",
    "zigux/helpers/cpumask_view.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet.zig",
    "zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json",
    "scripts/zigux/check-phase3-bitmap-cpumask.py",
    "zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
    "Documentation/zigux/phase3-list-hlist-slice.md",
    "zigux/helpers/list_view.zig",
    "zigux/helpers/hlist_view.zig",
    "zigux/tests/phase3_list_hlist_starter_packet.zig",
    "zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig",
    "keep the returned bitmap/cpumask and list/hlist helper slices explicit from the scripts root without widening into exported ABI, scheduler-affinity, container-of, mutation, or broader subsystem-ownership claims",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _remove_exact_line(path: Path, marker: str) -> None:
    lines = _read(path).splitlines()
    for index, line in enumerate(lines):
        if line == marker:
            del lines[index]
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")

    readme_path = repo_root / SCRIPTS_README_PATH
    try:
        readme_text = _read(readme_path)
    except FileNotFoundError:
        return issues + [f"missing repo file: {SCRIPTS_README_PATH.as_posix()}"]

    for marker in REQUIRED_MARKERS:
        if marker not in readme_text:
            issues.append(f"missing scripts README marker: {marker}")

    return issues


def _populate_repo(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        _write(root / rel_path, rel_path.as_posix() + "\n")
    _write(root / SCRIPTS_README_PATH, "\n".join(REQUIRED_MARKERS) + "\n")


def _expect_missing_marker(root: Path, marker: str, message: str) -> int:
    readme = root / SCRIPTS_README_PATH
    _remove_exact_line(readme, marker)
    issues = validate_repo(root)
    expected = f"missing scripts README marker: {marker}"
    if expected not in issues:
        print("PHASE3_README_HELPER_SLICES_SELF_TEST=fail")
        print(message)
        return 1
    return 0


def _expect_missing_file(root: Path, rel_path: Path, message: str) -> int:
    (root / rel_path).unlink()
    issues = validate_repo(root)
    expected = f"missing repo file: {rel_path.as_posix()}"
    if expected not in issues:
        print("PHASE3_README_HELPER_SLICES_SELF_TEST=fail")
        print(message)
        return 1
    return 0


def run_self_test() -> int:
    readme_cases = (
        (
            "Documentation/zigux/phase3-bitmap-cpumask-slice.md",
            "expected missing bitmap/cpumask note README marker was not reported",
        ),
        (
            "zigux/helpers/bitmap_view.zig",
            "expected missing bitmap_view README marker was not reported",
        ),
        (
            "zigux/helpers/cpumask_view.zig",
            "expected missing cpumask_view README marker was not reported",
        ),
        (
            "zigux/tests/phase3_bitmap_cpumask_starter_packet.zig",
            "expected missing bitmap/cpumask starter README marker was not reported",
        ),
        (
            "zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json",
            "expected missing bitmap/cpumask manifest README marker was not reported",
        ),
        (
            "scripts/zigux/check-phase3-bitmap-cpumask.py",
            "expected missing bitmap/cpumask checker README marker was not reported",
        ),
        (
            "zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
            "expected missing bitmap/cpumask build-route README marker was not reported",
        ),
        (
            "Documentation/zigux/phase3-list-hlist-slice.md",
            "expected missing list/hlist note README marker was not reported",
        ),
        (
            "zigux/helpers/list_view.zig",
            "expected missing list_view README marker was not reported",
        ),
        (
            "zigux/helpers/hlist_view.zig",
            "expected missing hlist_view README marker was not reported",
        ),
        (
            "zigux/tests/phase3_list_hlist_starter_packet.zig",
            "expected missing list/hlist starter README marker was not reported",
        ),
        (
            "zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig",
            "expected missing list/hlist build-route README marker was not reported",
        ),
        (
            "keep the returned bitmap/cpumask and list/hlist helper slices explicit from the scripts root without widening into exported ABI, scheduler-affinity, container-of, mutation, or broader subsystem-ownership claims",
            "expected missing helper-slice boundary README marker was not reported",
        ),
    )
    file_cases = (
        (
            BITMAP_CPUMASK_NOTE,
            "expected missing bitmap/cpumask note file was not reported",
        ),
        (
            BITMAP_VIEW,
            "expected missing bitmap_view file was not reported",
        ),
        (
            CPUMASK_VIEW,
            "expected missing cpumask_view file was not reported",
        ),
        (
            BITMAP_CPUMASK_STARTER,
            "expected missing bitmap/cpumask starter file was not reported",
        ),
        (
            BITMAP_CPUMASK_STARTER_BUILD,
            "expected missing bitmap/cpumask starter build file was not reported",
        ),
        (
            BITMAP_CPUMASK_MANIFEST,
            "expected missing bitmap/cpumask manifest file was not reported",
        ),
        (
            BITMAP_CPUMASK_CHECKER,
            "expected missing bitmap/cpumask checker file was not reported",
        ),
        (
            LIST_HLIST_NOTE,
            "expected missing list/hlist note file was not reported",
        ),
        (
            LIST_VIEW,
            "expected missing list_view file was not reported",
        ),
        (
            HLIST_VIEW,
            "expected missing hlist_view file was not reported",
        ),
        (
            LIST_HLIST_STARTER,
            "expected missing list/hlist starter file was not reported",
        ),
        (
            LIST_HLIST_STARTER_BUILD,
            "expected missing list/hlist starter build file was not reported",
        ),
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_readme_helper_slices_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_README_HELPER_SLICES_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for marker, message in readme_cases:
            _populate_repo(root)
            if _expect_missing_marker(root, marker, message) != 0:
                return 1

        for rel_path, message in file_cases:
            _populate_repo(root)
            if _expect_missing_file(root, rel_path, message) != 0:
                return 1

    print("PHASE3_README_HELPER_SLICES_SELF_TEST=pass")
    print(
        "PHASE3_README_HELPER_SLICES_SELF_TEST_CASE_COUNT="
        f"{1 + len(readme_cases) + len(file_cases)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the returned Phase 3 helper-slice reminders in scripts/zigux/README.md."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains scripts/zigux/README.md",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_README_HELPER_SLICES=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {args.repo_root / SCRIPTS_README_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
