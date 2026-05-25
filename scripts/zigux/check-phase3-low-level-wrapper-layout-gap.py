#!/usr/bin/env python3
"""Guard the current Phase 3 low-level-wrapper shared-build layout gap."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


LAYOUT_TEST_PATH = Path("zigux/tests/phase3_low_level_wrappers.zig")
DEDICATED_BUILD_PATH = Path("zigux/tests/phase3_low_level_wrappers_build.zig")
SHARED_BUILD_PATH = Path("zigux/tests/build.zig")

REQUIRED_LAYOUT_TEST_MARKERS = (
    'const layout_assert = @import("layout_assert");',
    'test "phase3 low-level wrappers keep helper-local MMIO layout assertions explicit" {',
    "try layout_assert.assertMmioRangeLayout();",
)

REQUIRED_DEDICATED_BUILD_MARKERS = (
    '.root_source_file = b.path("../helpers/layout_assert.zig"),',
    'layout_assert.addImport("abi_bindings", abi_bindings);',
    'root_module.addImport("layout_assert", layout_assert);',
    '"phase3-low-level-wrappers-test"',
)

REQUIRED_SHARED_SEGMENT_MARKERS = (
    "fn addPhase3LowLevelWrappers(",
    '.root_source_file = b.path("../helpers/atomic.zig"),',
    '.root_source_file = b.path("../helpers/barrier.zig"),',
    '.root_source_file = b.path("../helpers/mmio.zig"),',
    'root_module.addImport("atomic", atomic);',
    'root_module.addImport("barrier", barrier);',
    'root_module.addImport("mmio", mmio);',
    'root_module.addImport("unsafe_policy", unsafe_policy);',
    'root_module.addImport("narrow", narrow);',
)

FORBIDDEN_SHARED_SEGMENT_MARKERS = (
    '.root_source_file = b.path("../helpers/layout_assert.zig"),',
    'layout_assert.addImport("abi_bindings", abi_bindings);',
    'root_module.addImport("layout_assert", layout_assert);',
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _segment(text: str, start: str, end: str) -> str | None:
    start_index = text.find(start)
    if start_index == -1:
        return None
    end_index = text.find(end, start_index)
    if end_index == -1:
        return None
    return text[start_index:end_index]


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    try:
        layout_text = _read(repo_root / LAYOUT_TEST_PATH)
    except FileNotFoundError:
        issues.append(f"missing repo file: {LAYOUT_TEST_PATH.as_posix()}")
        layout_text = ""
    for marker in REQUIRED_LAYOUT_TEST_MARKERS:
        if marker not in layout_text:
            issues.append(f"missing {LAYOUT_TEST_PATH.as_posix()} marker: {marker}")

    try:
        dedicated_text = _read(repo_root / DEDICATED_BUILD_PATH)
    except FileNotFoundError:
        issues.append(f"missing repo file: {DEDICATED_BUILD_PATH.as_posix()}")
        dedicated_text = ""
    for marker in REQUIRED_DEDICATED_BUILD_MARKERS:
        if marker not in dedicated_text:
            issues.append(f"missing {DEDICATED_BUILD_PATH.as_posix()} marker: {marker}")

    try:
        shared_text = _read(repo_root / SHARED_BUILD_PATH)
    except FileNotFoundError:
        issues.append(f"missing repo file: {SHARED_BUILD_PATH.as_posix()}")
        return issues

    shared_segment = _segment(
        shared_text,
        "fn addPhase3LowLevelWrappers(",
        "fn addPhase3AbiDump(",
    )
    if shared_segment is None:
        issues.append(
            "could not isolate zigux/tests/build.zig addPhase3LowLevelWrappers segment"
        )
        return issues

    for marker in REQUIRED_SHARED_SEGMENT_MARKERS:
        if marker not in shared_segment:
            issues.append(f"missing shared low-level-wrapper build marker: {marker}")
    for marker in FORBIDDEN_SHARED_SEGMENT_MARKERS:
        if marker in shared_segment:
            issues.append(
                "shared low-level-wrapper build unexpectedly already wires layout_assert: "
                f"{marker}"
            )

    return issues


def _populate_repo(root: Path) -> None:
    _write(root / LAYOUT_TEST_PATH, "\n".join(REQUIRED_LAYOUT_TEST_MARKERS) + "\n")
    _write(root / DEDICATED_BUILD_PATH, "\n".join(REQUIRED_DEDICATED_BUILD_MARKERS) + "\n")
    shared_lines = list(REQUIRED_SHARED_SEGMENT_MARKERS) + [
        "fn addPhase3AbiDump(",
    ]
    _write(root / SHARED_BUILD_PATH, "\n".join(shared_lines) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(
        prefix="zigux_phase3_low_level_wrapper_layout_gap_"
    ) as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_LOW_LEVEL_WRAPPER_LAYOUT_GAP_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        marker_cases = (
            (LAYOUT_TEST_PATH, REQUIRED_LAYOUT_TEST_MARKERS[0]),
            (LAYOUT_TEST_PATH, REQUIRED_LAYOUT_TEST_MARKERS[2]),
            (DEDICATED_BUILD_PATH, REQUIRED_DEDICATED_BUILD_MARKERS[0]),
            (DEDICATED_BUILD_PATH, REQUIRED_DEDICATED_BUILD_MARKERS[2]),
            (SHARED_BUILD_PATH, REQUIRED_SHARED_SEGMENT_MARKERS[1]),
            (SHARED_BUILD_PATH, REQUIRED_SHARED_SEGMENT_MARKERS[5]),
        )
        for relative_path, marker in marker_cases:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, ""), encoding="utf-8")
            issues = validate_repo(root)
            if relative_path == SHARED_BUILD_PATH:
                expected = f"missing shared low-level-wrapper build marker: {marker}"
            else:
                expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_LOW_LEVEL_WRAPPER_LAYOUT_GAP_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

        for marker in FORBIDDEN_SHARED_SEGMENT_MARKERS:
            _populate_repo(root)
            path = root / SHARED_BUILD_PATH
            path.write_text(_read(path).replace("fn addPhase3AbiDump(", marker + "\nfn addPhase3AbiDump("), encoding="utf-8")
            issues = validate_repo(root)
            expected = (
                "shared low-level-wrapper build unexpectedly already wires layout_assert: "
                f"{marker}"
            )
            if expected not in issues:
                print("PHASE3_LOW_LEVEL_WRAPPER_LAYOUT_GAP_SELF_TEST=fail")
                print(f"expected forbidden-marker issue was not reported: {expected}")
                return 1

    print("PHASE3_LOW_LEVEL_WRAPPER_LAYOUT_GAP_SELF_TEST=pass")
    print("PHASE3_LOW_LEVEL_WRAPPER_LAYOUT_GAP_SELF_TEST_CASE_COUNT=9")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 low-level-wrapper shared-build layout gap packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 low-level-wrapper packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_LOW_LEVEL_WRAPPER_LAYOUT_GAP=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {LAYOUT_TEST_PATH.as_posix()}")
    print(f"validated {DEDICATED_BUILD_PATH.as_posix()}")
    print(f"validated {SHARED_BUILD_PATH.as_posix()}")
    print("PHASE3_LOW_LEVEL_WRAPPER_LAYOUT_GAP=pass")
    print(
        "PHASE3_LOW_LEVEL_WRAPPER_LAYOUT_GAP_STATUS="
        "dedicated_layout_route_present_shared_tests_root_gap_still_explicit"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
