#!/usr/bin/env python3
"""Fail-close the current Phase 3 idr slot starter packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


XA_VALUE_PATH = Path("zigux/helpers/xa_value.zig")
XARRAY_SLOT_PATH = Path("zigux/helpers/xarray_slot_view.zig")
HELPER_PATH = Path("zigux/helpers/idr_slot_view.zig")
TEST_PATH = Path("zigux/tests/phase3_idr_slot_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_idr_slot_starter_packet_build.zig")

REQUIRED_MARKERS = {
    XA_VALUE_PATH: (
        "pub const value_tag_mask: usize = 0x1;",
        "pub const safe_inline_limit: usize = (err_ptr.err_floor >> 1) - 1;",
        "pub fn makeValue(value: usize) MakeValueError!usize {",
    ),
    XARRAY_SLOT_PATH: (
        "pub const SlotKind = enum {",
        "pub fn fromErrorCode(code: isize) SlotView {",
        "pub fn isTaggedInternalEntry(raw: usize) bool {",
    ),
    HELPER_PATH: (
        "pub const SlotKind = enum {",
        "pub fn fromInternalValue(value: usize) xa_value.MakeValueError!SlotView {",
        "pub fn isTaggedInternalEntry(raw: usize) bool {",
        'test "empty slots stay distinct from pointer and internal lanes" {',
        'test "xa_value-tagged entries stay internal instead of looking like mapped pointers" {',
        'test "err_ptr encodings stay separated from pointer-backed idr entries" {',
    ),
    TEST_PATH: (
        'test "idr slot view keeps empty slots explicit" {',
        'test "idr slot view keeps pointer lanes publishable without tagging drift" {',
        'test "idr slot view keeps xa_value entries in the internal lane" {',
        'test "idr slot view preserves err_ptr encodings as tagged error entries" {',
        'test "top err_ptr encoding never falls back into the pointer lane" {',
        "try testing.expect(idr_slot_view.isTaggedInternalEntry(raw));",
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../helpers/idr_slot_view.zig"),',
        '.root_source_file = b.path("phase3_idr_slot_starter_packet.zig"),',
        'idr_slot_view.addImport("xarray_slot_view", xarray_slot_view);',
        'idr_slot_view.addImport("xa_value", xa_value);',
        '"phase3-idr-slot-starter-packet-test"',
    ),
}

SAMPLE_FILES = {path: "\n".join(markers) + "\n" for path, markers in REQUIRED_MARKERS.items()}

SELF_TEST_CASES = (
    (HELPER_PATH, "pub const SlotKind = enum {"),
    (TEST_PATH, 'test "idr slot view keeps empty slots explicit" {'),
    (BUILD_PATH, '"phase3-idr-slot-starter-packet-test"'),
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
    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, text in SAMPLE_FILES.items():
        _write(root / relative_path, text)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_idr_slot_starter_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_IDR_SLOT_STARTER_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_IDR_SLOT_STARTER_PACKET_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_IDR_SLOT_STARTER_PACKET_SELF_TEST=pass")
    print(f"PHASE3_IDR_SLOT_STARTER_PACKET_SELF_TEST_CASES={len(SELF_TEST_CASES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 idr slot starter packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 idr slot starter packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_IDR_SLOT_STARTER_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / TEST_PATH}")
    print(f"validated {args.repo_root / BUILD_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
