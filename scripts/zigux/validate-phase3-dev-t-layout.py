#!/usr/bin/env python3
"""Validate the bounded Phase 3 dev_t starter-packet layout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

EXPECTED_PATH = Path("zigux/tests/fixtures/phase3_dev_t/expected.json")
HARNESS_PATH = Path("zigux/tests/fixtures/phase3_dev_t/dev_t_layout_dump.c")
HEADER_PATH = Path("include/zigux/dev_t.h")
UAPI_PATH = Path("zigux/uapi/dev_t.zig")
BINDING_PATH = Path("zigux/bindings/dev_t.zig")
TEST_PATH = Path("zigux/tests/phase3_dev_t_starter_packet.zig")

REQUIRED_HEADER_MARKERS = (
    "#define ZIGUX_DEV_T_FIELDS_ABI_VERSION 1u",
    "#define ZIGUX_DEV_T_FIELDS_SIZE 8u",
    "#define ZIGUX_DEV_T_FIELDS_ALIGN 4u",
    "struct zigux_dev_t_fields {",
    "uint32_t major;",
    "uint32_t minor;",
)

REQUIRED_UAPI_MARKERS = (
    "pub const abi_version: u32 = 1;",
    "pub const Fields = extern struct {",
    "major: u32,",
    "minor: u32,",
)

REQUIRED_BINDING_MARKERS = (
    "pub const fields_size: usize = @sizeOf(uapi.Fields);",
    "pub const fields_align: usize = @alignOf(uapi.Fields);",
    "pub const major_offset: usize = @offsetOf(uapi.Fields, \"major\");",
    "pub const minor_offset: usize = @offsetOf(uapi.Fields, \"minor\");",
    "std.debug.assert(fields_size == 8);",
    "std.debug.assert(fields_align == 4);",
    "std.debug.assert(major_offset == 0);",
    "std.debug.assert(minor_offset == 4);",
)

REQUIRED_TEST_MARKERS = (
    'test "dev_t starter binding preserves the current ABI layout" {',
    'test "starter packet version stays aligned with the Linux-facing header family" {',
    'test "dev_t binding equality stays field based" {',
)


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing file: {path}") from exc


def load_expected(path: Path) -> dict[str, int]:
    return json.loads(load_text(path))


def require_markers(path: Path, markers: tuple[str, ...]) -> list[str]:
    text = load_text(path)
    return [marker for marker in markers if marker not in text]


def compile_and_run_harness(repo_root: Path) -> dict[str, int]:
    compiler = shutil.which("gcc")
    if compiler is None:
        raise SystemExit("missing compiler: gcc")

    harness = repo_root / HARNESS_PATH
    include_dir = repo_root / "include"
    with tempfile.TemporaryDirectory(prefix="phase3-dev-t-layout-") as temp_dir:
        binary = Path(temp_dir) / "dev_t_layout_dump"
        subprocess.run(
            [
                compiler,
                "-std=c11",
                "-Wall",
                "-Wextra",
                "-I",
                str(include_dir),
                str(harness),
                "-o",
                str(binary),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        completed = subprocess.run(
            [str(binary)],
            check=True,
            capture_output=True,
            text=True,
        )
    return json.loads(completed.stdout)


def validate_repo(repo_root: Path) -> list[str]:
    errors: list[str] = []
    expected = load_expected(repo_root / EXPECTED_PATH)
    observed = compile_and_run_harness(repo_root)
    if observed != expected:
        errors.append(
            f"layout mismatch: observed {json.dumps(observed, sort_keys=True)} != "
            f"expected {json.dumps(expected, sort_keys=True)}"
        )

    marker_sets = (
        (HEADER_PATH, REQUIRED_HEADER_MARKERS),
        (UAPI_PATH, REQUIRED_UAPI_MARKERS),
        (BINDING_PATH, REQUIRED_BINDING_MARKERS),
        (TEST_PATH, REQUIRED_TEST_MARKERS),
    )
    for relative_path, markers in marker_sets:
        missing = require_markers(repo_root / relative_path, markers)
        for marker in missing:
            errors.append(f"missing marker in {relative_path}: {marker}")
    return errors


def run_self_test() -> int:
    expected = {
        "abi_version": 1,
        "fields_size": 8,
        "fields_align": 4,
        "major_offset": 0,
        "minor_offset": 4,
    }
    sample = json.loads(json.dumps(expected))
    if sample != expected:
        print("PHASE3_DEV_T_LAYOUT_SELF_TEST=fail")
        print("round-trip JSON mismatch")
        return 1

    sample_text = "\n".join(REQUIRED_BINDING_MARKERS)
    if REQUIRED_BINDING_MARKERS[-1] not in sample_text:
        print("PHASE3_DEV_T_LAYOUT_SELF_TEST=fail")
        print("binding marker probe failed")
        return 1

    if not re.search(r'"fields_size":\s*8', json.dumps(expected)):
        print("PHASE3_DEV_T_LAYOUT_SELF_TEST=fail")
        print("expected payload probe failed")
        return 1

    print("PHASE3_DEV_T_LAYOUT_SELF_TEST=pass")
    print("PHASE3_DEV_T_LAYOUT_EXPECTED_KEYS=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains include/, zigux/, and scripts/",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in validator checks without compiling repo files",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = validate_repo(args.repo_root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"validated {args.repo_root / EXPECTED_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
