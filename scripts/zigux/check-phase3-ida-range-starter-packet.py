#!/usr/bin/env python3
"""Fail-close the current Phase 3 ida range starter packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SLICE_PATH = Path("Documentation/zigux/phase3-ida-range-slice.md")
HELPER_PATH = Path("zigux/helpers/ida_range_view.zig")
TEST_PATH = Path("zigux/tests/phase3_ida_range_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_ida_range_starter_packet_build.zig")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_ida_range_manifest.json")

STARTER_BUILD_ROUTE = (
    "zig build phase3-ida-range-starter-packet-test --build-file "
    "zigux/tests/phase3_ida_range_starter_packet_build.zig"
)

REQUIRED_MARKERS = {
    SLICE_PATH: (
        "zigux/helpers/ida_range_view.zig",
        "zigux/tests/phase3_ida_range_starter_packet.zig",
        "zigux/tests/fixtures/phase3_ida_range_manifest.json",
        "scripts/zigux/check-phase3-ida-range-starter-packet.py",
        "python3 scripts/zigux/check-phase3-ida-range-starter-packet.py --self-test",
        "python3 scripts/zigux/check-phase3-ida-range-starter-packet.py",
        STARTER_BUILD_ROUTE,
        "helper-local ida range packet",
    ),
    HELPER_PATH: (
        "pub const ClampedWindow = struct {",
        "pub const RangeSummary = struct {",
        "pub fn firstAllocatedInRange(self: RangeView, alloc_range: AllocationRange) ?Selection {",
        "pub fn summarize(self: RangeView, alloc_range: AllocationRange) ?RangeSummary {",
        'test "ida range view counts partial allocation windows" {',
    ),
    TEST_PATH: (
        'test "ida range starter packet keeps clamped window geometry explicit" {',
        'test "ida range starter packet keeps partial allocation counting explicit" {',
        'test "ida range starter packet keeps ceiling clamping and full windows explicit" {',
        'test "ida range starter packet keeps clear windows distinct from invalid ones" {',
        'test "ida range starter packet keeps ordered-range failure explicit" {',
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../helpers/ida_range_view.zig"),',
        '.root_source_file = b.path("phase3_ida_range_starter_packet.zig"),',
        'root_module.addImport("ida_range_view", ida_range_view);',
        '"phase3-ida-range-starter-packet-test"',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-ida-range"',
        '"status": "starter_and_dump_packet_present"',
        '"zigux/tests/phase3_ida_range_starter_packet.zig"',
        '"zigux/tests/phase3_ida_range_dump.zig"',
        '"python3 scripts/zigux/check-phase3-ida-range-starter-packet.py --self-test"',
        STARTER_BUILD_ROUTE,
        '"repo_reality_gaps": []',
    ),
}

REQUIRED_PACKET_FILES = (
    "Documentation/zigux/phase3-ida-range-slice.md",
    "zigux/helpers/ida_bitmap_view.zig",
    "zigux/helpers/ida_alloc_view.zig",
    "zigux/helpers/ida_range_view.zig",
    "zigux/tests/phase3_ida_range_starter_packet.zig",
    "zigux/tests/phase3_ida_range_starter_packet_build.zig",
    "scripts/zigux/check-phase3-ida-range-starter-packet.py",
    "zigux/tests/phase3_ida_range_dump.zig",
    "zigux/tests/phase3_ida_range_dump_build.zig",
    "zigux/tests/fixtures/phase3_ida_range/phase3_ida_range_c_harness.c",
    "zigux/tests/fixtures/phase3_ida_range/expected.json",
    "zigux/tests/fixtures/phase3_ida_range_manifest.json",
    "scripts/zigux/check-phase3-ida-range.py",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-ida-range-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-ida-range-starter-packet.py",
    STARTER_BUILD_ROUTE,
    "python3 scripts/zigux/check-phase3-ida-range.py --self-test",
    "python3 scripts/zigux/check-phase3-ida-range.py --repo-root . --zig zig --cc gcc",
    "zig build phase3-ida-range-dump --build-file zigux/tests/phase3_ida_range_dump_build.zig",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")

    manifest_path = repo_root / MANIFEST_PATH
    if manifest_path.exists():
        try:
            manifest = json.loads(_read(manifest_path))
        except json.JSONDecodeError as exc:
            issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        else:
            packet_files = manifest.get("packet_files")
            replay_routes = manifest.get("replay_routes")
            repo_reality_gaps = manifest.get("repo_reality_gaps")
            if not isinstance(packet_files, list):
                issues.append("phase3_ida_range_manifest.json packet_files is not a list")
            if not isinstance(replay_routes, list):
                issues.append("phase3_ida_range_manifest.json replay_routes is not a list")
            if not isinstance(repo_reality_gaps, list):
                issues.append("phase3_ida_range_manifest.json repo_reality_gaps is not a list")
            elif repo_reality_gaps:
                issues.append(
                    "phase3_ida_range_manifest.json repo_reality_gaps should stay empty once the helper-local packet is present"
                )
            if isinstance(packet_files, list):
                for required_path in REQUIRED_PACKET_FILES:
                    if required_path not in packet_files:
                        issues.append(
                            "phase3_ida_range_manifest.json missing packet_files entry: "
                            f"{required_path}"
                        )
            if isinstance(replay_routes, list):
                for route in REQUIRED_REPLAY_ROUTES:
                    if route not in replay_routes:
                        issues.append(
                            "phase3_ida_range_manifest.json missing replay route: "
                            f"{route}"
                        )
    return issues


def _populate_repo(root: Path) -> None:
    files = {
        path: "\n".join(markers) + "\n" for path, markers in REQUIRED_MARKERS.items()
    }
    files[MANIFEST_PATH] = """{
  "phase": "Phase 3",
  "lane": "helper-interop",
  "slug": "phase3-ida-range",
  "status": "starter_and_dump_packet_present",
  "scope": "helper-local ida range occupancy summaries layered on the landed ida allocation packet",
  "packet_files": [
    "Documentation/zigux/phase3-ida-range-slice.md",
    "zigux/helpers/ida_bitmap_view.zig",
    "zigux/helpers/ida_alloc_view.zig",
    "zigux/helpers/ida_range_view.zig",
    "zigux/tests/phase3_ida_range_starter_packet.zig",
    "zigux/tests/phase3_ida_range_starter_packet_build.zig",
    "scripts/zigux/check-phase3-ida-range-starter-packet.py",
    "zigux/tests/phase3_ida_range_dump.zig",
    "zigux/tests/phase3_ida_range_dump_build.zig",
    "zigux/tests/fixtures/phase3_ida_range/phase3_ida_range_c_harness.c",
    "zigux/tests/fixtures/phase3_ida_range/expected.json",
    "zigux/tests/fixtures/phase3_ida_range_manifest.json",
    "scripts/zigux/check-phase3-ida-range.py"
  ],
  "replay_routes": [
    "python3 scripts/zigux/check-phase3-ida-range-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-ida-range-starter-packet.py",
    "zig build phase3-ida-range-starter-packet-test --build-file zigux/tests/phase3_ida_range_starter_packet_build.zig",
    "python3 scripts/zigux/check-phase3-ida-range.py --self-test",
    "python3 scripts/zigux/check-phase3-ida-range.py --repo-root . --zig zig --cc gcc",
    "zig build phase3-ida-range-dump --build-file zigux/tests/phase3_ida_range_dump_build.zig"
  ],
  "repo_reality_gaps": [],
  "next_safe_step": "keep the helper-local ida range packet honest before widening into ida policy or shared ABI surfaces"
}
"""
    for relative_path, text in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


SELF_TEST_CASES = (
    (SLICE_PATH, "zigux/tests/fixtures/phase3_ida_range_manifest.json"),
    (HELPER_PATH, "pub fn summarize(self: RangeView, alloc_range: AllocationRange) ?RangeSummary {"),
    (TEST_PATH, 'test "ida range starter packet keeps partial allocation counting explicit" {'),
    (BUILD_PATH, '"phase3-ida-range-starter-packet-test"'),
    (MANIFEST_PATH, '"status": "starter_and_dump_packet_present"'),
)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_ida_range_starter_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_IDA_RANGE_STARTER_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_IDA_RANGE_STARTER_PACKET_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_IDA_RANGE_STARTER_PACKET_SELF_TEST=pass")
    print(f"PHASE3_IDA_RANGE_STARTER_PACKET_SELF_TEST_CASES={len(SELF_TEST_CASES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 ida range starter packet."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_IDA_RANGE_STARTER_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / TEST_PATH}")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
