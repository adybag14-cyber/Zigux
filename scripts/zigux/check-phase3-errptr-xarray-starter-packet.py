#!/usr/bin/env python3
"""Fail-close the current Phase 3 err_ptr/xarray starter packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SLICE_PATH = Path("Documentation/zigux/phase3-errptr-xarray-slice.md")
VALIDATOR_NOTE_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")
ERR_PTR_PATH = Path("zigux/helpers/err_ptr.zig")
XA_VALUE_PATH = Path("zigux/helpers/xa_value.zig")
TEST_PATH = Path("zigux/tests/phase3_errptr_xarray_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_errptr_xarray_starter_packet_build.zig")

REQUIRED_MARKERS = {
    SLICE_PATH: (
        "zigux/helpers/err_ptr.zig",
        "zigux/helpers/xa_value.zig",
        "zigux/tests/phase3_errptr_xarray_starter_packet.zig",
        "zigux/tests/phase3_errptr_xarray_starter_packet_build.zig",
        "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
        "rejects values that would enter the `err_ptr` band",
        "It is one helper-local interop proof layered beside the existing `dev_t` starter packet.",
    ),
    VALIDATOR_NOTE_PATH: (
        "one bounded `dev_t` starter packet plus one focused helper-local `err_ptr` / `xarray` interop slice",
        "Documentation/zigux/phase3-errptr-xarray-slice.md",
        "zigux/helpers/err_ptr.zig",
        "zigux/helpers/xa_value.zig",
        "zigux/tests/phase3_errptr_xarray_starter_packet.zig",
        "zigux/tests/phase3_errptr_xarray_starter_packet_build.zig",
        "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    ),
    ERR_PTR_PATH: (
        "pub const max_errno: usize = 4095;",
        "pub const err_floor: usize = @bitCast(-@as(isize, @intCast(max_errno)));",
        "pub fn fromErrorCode(code: isize) usize {",
        "pub fn isErrValue(raw: usize) bool {",
        "pub fn toErrorCode(raw: usize) isize {",
    ),
    XA_VALUE_PATH: (
        "const err_ptr = @import(\"err_ptr\");",
        "pub const value_tag_mask: usize = 0x1;",
        "pub const safe_inline_limit: usize = (err_ptr.err_floor >> 1) - 1;",
        "ValueWouldOverlapErrPtr",
        "return (value << 1) | value_tag_mask;",
        "return (raw & value_tag_mask) == value_tag_mask and !err_ptr.isErrValue(raw);",
    ),
    TEST_PATH: (
        "test \"err_ptr encodes the Linux error band as a tagged pointer-sized value\" {",
        "test \"xa_value round-trips a bounded inline value without entering the err_ptr band\" {",
        "test \"xa_value rejects inline values that would overlap err_ptr encodings\" {",
        "test \"safe inline limit stays below the err_ptr floor\" {",
        "try testing.expectError(",
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../helpers/err_ptr.zig"),',
        '.root_source_file = b.path("../helpers/xa_value.zig"),',
        '.root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),',
        'xa_value.addImport("err_ptr", err_ptr);',
        '"phase3-errptr-xarray-starter-packet-test"',
    ),
}

SAMPLE_FILES = {path: "\n".join(markers) + "\n" for path, markers in REQUIRED_MARKERS.items()}

SELF_TEST_CASES = (
    (SLICE_PATH, "rejects values that would enter the `err_ptr` band"),
    (VALIDATOR_NOTE_PATH, "Documentation/zigux/phase3-errptr-xarray-slice.md"),
    (ERR_PTR_PATH, "pub fn isErrValue(raw: usize) bool {"),
    (XA_VALUE_PATH, "ValueWouldOverlapErrPtr"),
    (TEST_PATH, "test \"safe inline limit stays below the err_ptr floor\" {"),
    (BUILD_PATH, '"phase3-errptr-xarray-starter-packet-test"'),
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
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_errptr_xarray_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST=pass")
    print(f"PHASE3_ERRPTR_XARRAY_STARTER_PACKET_SELF_TEST_CASES={len(SELF_TEST_CASES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 err_ptr/xarray starter packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 err_ptr/xarray starter packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ERRPTR_XARRAY_STARTER_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / TEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
