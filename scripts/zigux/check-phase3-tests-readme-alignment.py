#!/usr/bin/env python3
"""Fail-close the current Phase 3 tests-root README packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


TESTS_README_PATH = Path("zigux/tests/README.md")
BUILD_PATH = Path("zigux/tests/build.zig")

REQUIRED_FILES = (
    Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"),
    Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    Path("zigux/helpers/xarray_slot_view.zig"),
    Path("zigux/helpers/atomic.zig"),
    Path("zigux/helpers/barrier.zig"),
    Path("zigux/helpers/mmio.zig"),
    Path("zigux/tests/phase3_xarray_slot_starter_packet.zig"),
    Path("zigux/tests/phase3_low_level_wrappers.zig"),
    Path("zigux/tests/phase3_low_level_wrappers_build.zig"),
)

README_MARKERS = (
    "the directly readable `xarray_slot` starter packet",
    "one focused low-level-wrapper packet",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "zigux/helpers/xarray_slot_view.zig",
    "zigux/helpers/atomic.zig",
    "zigux/helpers/barrier.zig",
    "zigux/helpers/mmio.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/build.zig",
    "zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "instead of presenting the broader validator, catalog, IDR, or IDA packet as shipped tests-root evidence",
)

BUILD_MARKERS = (
    "fn addPhase3XarraySlotStarterPacket(",
    "fn addPhase3LowLevelWrappers(",
    '"phase3-xarray-slot-starter-packet"',
    '"phase3-low-level-wrappers"',
    "phase3_test_step.dependOn(&phase3_xarray_slot_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_low_level_wrappers.step);",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(root: Path) -> list[str]:
    issues: list[str] = []

    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")

    readme_path = root / TESTS_README_PATH
    try:
        readme_text = _read(readme_path)
    except FileNotFoundError:
        issues.append(f"missing repo file: {TESTS_README_PATH.as_posix()}")
    else:
        for marker in README_MARKERS:
            if marker not in readme_text:
                issues.append(f"missing tests README marker: {marker}")

    build_path = root / BUILD_PATH
    try:
        build_text = _read(build_path)
    except FileNotFoundError:
        issues.append(f"missing repo file: {BUILD_PATH.as_posix()}")
    else:
        for marker in BUILD_MARKERS:
            if marker not in build_text:
                issues.append(f"missing build marker: {marker}")

    return issues


def _populate_repo(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        _write(root / rel_path, rel_path.as_posix() + "\n")

    _write(root / TESTS_README_PATH, "\n".join(README_MARKERS) + "\n")
    _write(root / BUILD_PATH, "\n".join(BUILD_MARKERS) + "\n")


def _remove_marker(path: Path, marker: str) -> None:
    path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")


def run_self_test() -> int:
    cases: tuple[tuple[str, str, str], ...] = (
        ("readme", "the directly readable `xarray_slot` starter packet", "expected xarray-slot reminder drift was not reported"),
        ("readme", "one focused low-level-wrapper packet", "expected low-level-wrapper reminder drift was not reported"),
        ("readme", "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md", "expected low-level-wrapper survey note marker drift was not reported"),
        ("readme", "zigux/helpers/xarray_slot_view.zig", "expected xarray-slot helper marker drift was not reported"),
        ("readme", "zigux/helpers/atomic.zig", "expected atomic helper marker drift was not reported"),
        ("readme", "zigux/tests/phase3_xarray_slot_starter_packet.zig", "expected xarray-slot replay marker drift was not reported"),
        ("readme", "zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig", "expected xarray-slot route marker drift was not reported"),
        ("readme", "zigux/tests/phase3_low_level_wrappers.zig", "expected low-level-wrapper replay marker drift was not reported"),
        ("readme", "zigux/tests/phase3_low_level_wrappers_build.zig", "expected low-level-wrapper build marker drift was not reported"),
        ("readme", "scripts/zigux/validate-phase3-low-level-wrapper-survey.py", "expected low-level-wrapper validator marker drift was not reported"),
        ("readme", "instead of presenting the broader validator, catalog, IDR, or IDA packet as shipped tests-root evidence", "expected narrowed repo-gap summary drift was not reported"),
        ("build", "fn addPhase3XarraySlotStarterPacket(", "expected xarray-slot build helper drift was not reported"),
        ("build", "fn addPhase3LowLevelWrappers(", "expected low-level-wrapper build helper drift was not reported"),
        ("build", '"phase3-xarray-slot-starter-packet"', "expected xarray-slot build step drift was not reported"),
        ("build", '"phase3-low-level-wrappers"', "expected low-level-wrapper build step drift was not reported"),
        ("build", "phase3_test_step.dependOn(&phase3_xarray_slot_starter_packet.step);", "expected xarray-slot shared phase3 bundle drift was not reported"),
        ("build", "phase3_test_step.dependOn(&phase3_low_level_wrappers.step);", "expected low-level-wrapper shared phase3 bundle drift was not reported"),
    )

    file_cases: tuple[tuple[Path, str], ...] = (
        (Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"), "expected low-level-wrapper survey note file drift was not reported"),
        (Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"), "expected low-level-wrapper survey validator file drift was not reported"),
        (Path("zigux/helpers/xarray_slot_view.zig"), "expected xarray-slot helper file drift was not reported"),
        (Path("zigux/helpers/atomic.zig"), "expected atomic helper file drift was not reported"),
        (Path("zigux/helpers/barrier.zig"), "expected barrier helper file drift was not reported"),
        (Path("zigux/helpers/mmio.zig"), "expected MMIO helper file drift was not reported"),
        (Path("zigux/tests/phase3_xarray_slot_starter_packet.zig"), "expected xarray-slot replay file drift was not reported"),
        (Path("zigux/tests/phase3_low_level_wrappers.zig"), "expected low-level-wrapper replay file drift was not reported"),
        (Path("zigux/tests/phase3_low_level_wrappers_build.zig"), "expected low-level-wrapper build file drift was not reported"),
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_tests_readme_alignment_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_TESTS_README_ALIGNMENT_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for area, marker, message in cases:
            _populate_repo(root)
            target = root / (TESTS_README_PATH if area == "readme" else BUILD_PATH)
            _remove_marker(target, marker)
            issues = validate_repo(root)
            expected = f"missing {'tests README' if area == 'readme' else 'build'} marker: {marker}"
            if expected not in issues:
                print("PHASE3_TESTS_README_ALIGNMENT_SELF_TEST=fail")
                print(message)
                return 1

        for rel_path, message in file_cases:
            _populate_repo(root)
            (root / rel_path).unlink()
            issues = validate_repo(root)
            expected = f"missing repo file: {rel_path.as_posix()}"
            if expected not in issues:
                print("PHASE3_TESTS_README_ALIGNMENT_SELF_TEST=fail")
                print(message)
                return 1

    print("PHASE3_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print(
        "PHASE3_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT="
        f"{1 + len(cases) + len(file_cases)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 tests-root README packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="repository root that contains the shared Phase 3 tests-root surfaces",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.root)
    if issues:
        print("PHASE3_TESTS_README_ALIGNMENT=fail")
        print("\n".join(issues))
        return 1

    print("PHASE3_TESTS_README_ALIGNMENT=pass")
    print(f"PHASE3_TESTS_README_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES) + 2}")
    print(
        "PHASE3_TESTS_README_ALIGNMENT_REQUIRED_MARKER_COUNT="
        f"{len(README_MARKERS) + len(BUILD_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
