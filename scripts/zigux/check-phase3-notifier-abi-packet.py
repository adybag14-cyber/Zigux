#!/usr/bin/env python3
"""Fail-close the current Phase 3 notifier ABI packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ABI_HEADER_PATH = Path("include/zigux/abi.h")
ABI_BINDING_PATH = Path("zigux/bindings/abi.zig")
NOTIFIER_BINDING_PATH = Path("zigux/bindings/notifier_abi.zig")
LAYOUT_ASSERT_PATH = Path("zigux/helpers/layout_assert.zig")
TEST_PATH = Path("zigux/tests/phase3_notifier_abi_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_notifier_abi_packet_build.zig")
MANIFEST_PATH = Path("zigux/tests/phase3_notifier_abi_packet_manifest.json")

COMPILE_ROUTE = (
    "zig build phase3-notifier-abi-packet-test --build-file "
    "zigux/tests/phase3_notifier_abi_packet_build.zig"
)

EXPECTED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-notifier-abi-packet",
    "status": "shared_notifier_binding_present",
    "scope": "shared notifier result and layout compile replay through the bounded ABI binding surface",
    "next_safe_step": "keep the shared notifier binding bounded to its compile route and truthful packet inventory before widening broader shared Phase 3 reminder surfaces",
}

REQUIRED_MARKERS = {
    ABI_HEADER_PATH: (
        "#define ZIGUX_NOTIFIER_DONE 0U",
        "#define ZIGUX_NOTIFIER_OK 1U",
        "#define ZIGUX_NOTIFIER_STOP 2U",
        "struct zigux_notifier_block {",
        "uintptr_t notifier_call;",
        "uintptr_t next;",
        "int32_t priority;",
        "static inline int zigux_notifier_chain_has_nonincreasing_priority(",
    ),
    ABI_BINDING_PATH: (
        'const notifier_abi = @import("notifier_abi.zig");',
        "pub const NOTIFIER_DONE: u32 = 0;",
        "pub const NOTIFIER_OK: u32 = 1;",
        "pub const NOTIFIER_STOP: u32 = 2;",
        "pub const NotifierResult = notifier_abi.NotifierResult;",
        "pub const NotifierBlock = notifier_abi.NotifierBlock;",
        "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {",
    ),
    NOTIFIER_BINDING_PATH: (
        "pub const NotifierResult = enum(u32) {",
        "done = 0,",
        "ok = 1,",
        "stop = 2,",
        "pub const NotifierBlock = extern struct {",
        "notifier_call: usize,",
        "next: usize,",
        "priority: i32,",
        "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {",
    ),
    LAYOUT_ASSERT_PATH: (
        "pub fn expectLayout(comptime T: type, size: usize, alignment: usize) LayoutError!void {",
        "pub fn expectFieldLayout(",
    ),
    TEST_PATH: (
        'const abi = @import("abi_bindings");',
        'const layout_assert = @import("layout_assert");',
        'test "notifier binding keeps shared result values aligned" {',
        'test "notifier binding keeps published layout explicit" {',
        'test "notifier binding chain helper stays aligned with shared abi helper" {',
        'test "notifier binding preserves pointer-width links" {',
        "std.mem.alignForward(usize, raw_size, @alignOf(usize));",
        'layout_assert.expectFieldLayout(abi.NotifierBlock, "priority", @sizeOf(usize) * 2);',
        "abi.chainHasNonincreasingPriority(&head)",
        "const middle_ptr: *const abi.NotifierBlock = @ptrFromInt(head.next);",
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../bindings/abi.zig"),',
        '.root_source_file = b.path("../helpers/layout_assert.zig"),',
        '.root_source_file = b.path("phase3_notifier_abi_packet.zig"),',
        'root_module.addImport("abi_bindings", abi_bindings);',
        'root_module.addImport("layout_assert", layout_assert);',
        '"phase3-notifier-abi-packet-test"',
        '"Run the Phase 3 notifier ABI packet self-check"',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-notifier-abi-packet"',
        '"status": "shared_notifier_binding_present"',
        '"zigux/bindings/notifier_abi.zig"',
        '"zigux/helpers/layout_assert.zig"',
        '"scripts/zigux/check-phase3-notifier-abi-packet.py"',
        '"python3 scripts/zigux/check-phase3-notifier-abi-packet.py --self-test"',
        f'"{COMPILE_ROUTE}"',
        '"scripts/zigux/check-phase3-abi.py"',
        '"scripts/zigux/validate-phase3.py"',
    ),
}

SAMPLE_FILES = {
    path: "\n".join(markers) + "\n" for path, markers in REQUIRED_MARKERS.items()
}
SAMPLE_FILES[MANIFEST_PATH] = """{
  "phase": "Phase 3",
  "lane": "abi-runtime",
  "slug": "phase3-notifier-abi-packet",
  "status": "shared_notifier_binding_present",
  "scope": "shared notifier result and layout compile replay through the bounded ABI binding surface",
  "packet_files": [
    "include/zigux/abi.h",
    "zigux/bindings/abi.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/layout_assert.zig",
    "zigux/tests/phase3_notifier_abi_packet.zig",
    "zigux/tests/phase3_notifier_abi_packet_build.zig",
    "zigux/tests/phase3_notifier_abi_packet_manifest.json",
    "scripts/zigux/check-phase3-notifier-abi-packet.py"
  ],
  "replay_routes": [
    "python3 scripts/zigux/check-phase3-notifier-abi-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-notifier-abi-packet.py",
    "zig build phase3-notifier-abi-packet-test --build-file zigux/tests/phase3_notifier_abi_packet_build.zig"
  ],
  "repo_reality_gaps": [
    "scripts/zigux/check-phase3-abi.py",
    "scripts/zigux/validate-phase3.py"
  ],
  "next_safe_step": "keep the shared notifier binding bounded to its compile route and truthful packet inventory before widening broader shared Phase 3 reminder surfaces"
}
"""

SELF_TEST_CASES = (
    (ABI_HEADER_PATH, "#define ZIGUX_NOTIFIER_STOP 2U"),
    (ABI_BINDING_PATH, "pub const NotifierBlock = notifier_abi.NotifierBlock;"),
    (NOTIFIER_BINDING_PATH, "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {"),
    (LAYOUT_ASSERT_PATH, "pub fn expectFieldLayout("),
    (TEST_PATH, 'test "notifier binding preserves pointer-width links" {'),
    (BUILD_PATH, 'root_module.addImport("layout_assert", layout_assert);'),
    (MANIFEST_PATH, '"scripts/zigux/validate-phase3.py"'),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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
            for field, expected in EXPECTED_MANIFEST_FIELDS.items():
                actual = manifest.get(field)
                if actual != expected:
                    issues.append(
                        "phase3_notifier_abi_packet_manifest.json wrong "
                        f"{field}: {actual!r} != {expected!r}"
                    )

            packet_files = manifest.get("packet_files")
            replay_routes = manifest.get("replay_routes")
            repo_reality_gaps = manifest.get("repo_reality_gaps")
            if not isinstance(packet_files, list):
                issues.append("phase3_notifier_abi_packet_manifest.json packet_files is not a list")
            if not isinstance(replay_routes, list):
                issues.append("phase3_notifier_abi_packet_manifest.json replay_routes is not a list")
            if not isinstance(repo_reality_gaps, list):
                issues.append("phase3_notifier_abi_packet_manifest.json repo_reality_gaps is not a list")
    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, text in SAMPLE_FILES.items():
        _write(root / relative_path, text)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_notifier_abi_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_NOTIFIER_ABI_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_NOTIFIER_ABI_PACKET_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_NOTIFIER_ABI_PACKET_SELF_TEST=pass")
    print(f"PHASE3_NOTIFIER_ABI_PACKET_SELF_TEST_CASES={len(SELF_TEST_CASES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 notifier ABI packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 notifier ABI packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_NOTIFIER_ABI_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / TEST_PATH}")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
