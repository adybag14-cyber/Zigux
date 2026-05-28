#!/usr/bin/env python3
"""Fail-close the current Phase 3 ida range starter-plus-dump packet."""

from __future__ import annotations

import argparse
import difflib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


DOC_PATH = Path("Documentation/zigux/phase3-ida-range-slice.md")
BITMAP_HELPER_PATH = Path("zigux/helpers/ida_bitmap_view.zig")
ALLOC_HELPER_PATH = Path("zigux/helpers/ida_alloc_view.zig")
HELPER_PATH = Path("zigux/helpers/ida_range_view.zig")
STARTER_TEST_PATH = Path("zigux/tests/phase3_ida_range_starter_packet.zig")
STARTER_BUILD_PATH = Path("zigux/tests/phase3_ida_range_starter_packet_build.zig")
STARTER_CHECK_PATH = Path("scripts/zigux/check-phase3-ida-range-starter-packet.py")
DUMP_PATH = Path("zigux/tests/phase3_ida_range_dump.zig")
DUMP_BUILD_PATH = Path("zigux/tests/phase3_ida_range_dump_build.zig")
EXPECTED_PATH = Path("zigux/tests/fixtures/phase3_ida_range/expected.json")
C_HARNESS_PATH = Path("zigux/tests/fixtures/phase3_ida_range/phase3_ida_range_c_harness.c")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_ida_range_manifest.json")

REQUIRED_MARKERS = {
    DOC_PATH: (
        "# Phase 3 ida-range Slice",
        "`zigux/helpers/ida_range_view.zig`",
        "`zigux/tests/phase3_ida_range_dump.zig`",
        "`scripts/zigux/check-phase3-ida-range.py`",
        "`python3 scripts/zigux/check-phase3-ida-range.py --repo-root . --zig zig --cc gcc`",
        "helper-local ida range packet",
    ),
    HELPER_PATH: (
        "pub const ClampedWindow = struct {",
        "pub const RangeSummary = struct {",
        "pub fn firstAllocatedInRange(self: RangeView, alloc_range: AllocationRange) ?Selection {",
        "pub fn summarize(self: RangeView, alloc_range: AllocationRange) ?RangeSummary {",
    ),
    STARTER_TEST_PATH: (
        'test "ida range starter packet keeps partial allocation counting explicit" {',
        'test "ida range starter packet keeps ordered-range failure explicit" {',
    ),
    STARTER_BUILD_PATH: (
        '.root_source_file = b.path("../helpers/ida_range_view.zig"),',
        '"phase3-ida-range-starter-packet-test"',
    ),
    STARTER_CHECK_PATH: (
        "PHASE3_IDA_RANGE_STARTER_PACKET_SELF_TEST=pass",
        "Validate the current Phase 3 ida range starter packet.",
    ),
    DUMP_PATH: (
        'const ida_range_view = @import("ida_range_view");',
        '"clamped_ceiling_full"',
        '"clear_middle_window"',
        '"unordered_window"',
    ),
    DUMP_BUILD_PATH: (
        '.root_source_file = b.path("../helpers/ida_range_view.zig"),',
        '.root_source_file = b.path("phase3_ida_range_dump.zig"),',
        '"phase3-ida-range-dump"',
    ),
    C_HARNESS_PATH: (
        "#define BITMAP_BITS (BITMAP_LONGS * WORD_BITS)",
        'write_case("clamped_floor_partial", floor_words, 1024, 1000, 1027, true);',
        'write_case("unordered_window", clear_words, 0, 17, 12, false);',
    ),
    EXPECTED_PATH: (
        '"name": "clamped_ceiling_full"',
        '"id": 3070',
        '"name": "unordered_window"',
        '"summary": null',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-ida-range"',
        '"status": "starter_and_dump_packet_present"',
        '"zigux/tests/phase3_ida_range_dump.zig"',
        '"scripts/zigux/check-phase3-ida-range.py"',
    ),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)


def _resolve_tool(explicit: str | None, env_name: str, default: str) -> str:
    if explicit:
        return explicit
    return os.environ.get(env_name, default)


def _diff(label: str, expected: object, actual: object) -> str:
    expected_text = json.dumps(expected, indent=2, sort_keys=True) + "\n"
    actual_text = json.dumps(actual, indent=2, sort_keys=True) + "\n"
    diff = "".join(
        difflib.unified_diff(
            expected_text.splitlines(keepends=True),
            actual_text.splitlines(keepends=True),
            fromfile=f"{label}-expected",
            tofile=f"{label}-actual",
        )
    )
    return diff.strip() or f"{label} JSON differed without a textual diff"


def _run_starter_checker(repo_root: Path) -> None:
    result = _run(
        [sys.executable, str(repo_root / STARTER_CHECK_PATH), "--repo-root", str(repo_root)],
        cwd=repo_root,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "starter checker failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def _run_starter_build(repo_root: Path, zig: str) -> None:
    result = _run(
        [
            zig,
            "build",
            "phase3-ida-range-starter-packet-test",
            "--build-file",
            str(repo_root / STARTER_BUILD_PATH),
        ],
        cwd=repo_root,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "starter build failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def _run_zig_dump(repo_root: Path, zig: str) -> object:
    result = _run(
        [
            zig,
            "build",
            "phase3-ida-range-dump",
            "--build-file",
            str(repo_root / DUMP_BUILD_PATH),
        ],
        cwd=repo_root,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "zig dump failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    payload = result.stdout.strip() or result.stderr.strip()
    return json.loads(payload)


def _run_c_harness(repo_root: Path, cc: str) -> object:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_ida_range_c_") as temp_dir:
        binary = Path(temp_dir) / "phase3_ida_range_c_harness"
        compile_result = _run(
            [cc, "-std=c11", "-Wall", "-Wextra", "-pedantic", "-o", str(binary), str(repo_root / C_HARNESS_PATH)],
            cwd=repo_root,
        )
        if compile_result.returncode != 0:
            raise RuntimeError(
                "c harness compile failed:\n"
                f"stdout:\n{compile_result.stdout}\n"
                f"stderr:\n{compile_result.stderr}"
            )
        run_result = _run([str(binary)], cwd=repo_root)
        if run_result.returncode != 0:
            raise RuntimeError(
                "c harness run failed:\n"
                f"stdout:\n{run_result.stdout}\n"
                f"stderr:\n{run_result.stderr}"
            )
        return json.loads(run_result.stdout)


def validate_repo(repo_root: Path, zig: str, cc: str, *, skip_exec: bool = False) -> list[str]:
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

    if issues or skip_exec:
        return issues

    expected = json.loads(_read(repo_root / EXPECTED_PATH))
    try:
        _run_starter_checker(repo_root)
        _run_starter_build(repo_root, zig)
        zig_actual = _run_zig_dump(repo_root, zig)
        c_actual = _run_c_harness(repo_root, cc)
    except Exception as exc:
        issues.append(str(exc))
        return issues

    if zig_actual != expected:
        issues.append(_diff("zig-dump", expected, zig_actual))
    if c_actual != expected:
        issues.append(_diff("c-harness", expected, c_actual))
    if zig_actual != c_actual:
        issues.append(_diff("zig-vs-c", zig_actual, c_actual))

    return issues


SELF_TEST_CASES = (
    (DOC_PATH, "`python3 scripts/zigux/check-phase3-ida-range.py --repo-root . --zig zig --cc gcc`"),
    (HELPER_PATH, "pub const RangeSummary = struct {"),
    (DUMP_PATH, '"unordered_window"'),
    (EXPECTED_PATH, '"name": "clamped_ceiling_full"'),
)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_ida_range_") as temp_dir:
        root = Path(temp_dir)
        files_to_copy = (
            DOC_PATH,
            BITMAP_HELPER_PATH,
            ALLOC_HELPER_PATH,
            HELPER_PATH,
            STARTER_TEST_PATH,
            STARTER_BUILD_PATH,
            STARTER_CHECK_PATH,
            DUMP_PATH,
            DUMP_BUILD_PATH,
            EXPECTED_PATH,
            C_HARNESS_PATH,
            MANIFEST_PATH,
        )
        source_root = Path(__file__).resolve().parents[2]
        for relative_path in files_to_copy:
            _write(root / relative_path, _read(source_root / relative_path))

        issues = validate_repo(root, zig="zig", cc="gcc", skip_exec=True)
        if issues:
            print("PHASE3_IDA_RANGE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            for copy_path in files_to_copy:
                _write(root / copy_path, _read(source_root / copy_path))
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root, zig="zig", cc="gcc", skip_exec=True)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_IDA_RANGE_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_IDA_RANGE_SELF_TEST=pass")
    print(f"PHASE3_IDA_RANGE_SELF_TEST_CASES={len(SELF_TEST_CASES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 ida range starter-plus-dump packet."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--zig")
    parser.add_argument("--cc")
    parser.add_argument("--skip-exec", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    zig = _resolve_tool(args.zig, "ZIG", "zig")
    cc = _resolve_tool(args.cc, "CC", "gcc")
    issues = validate_repo(args.repo_root, zig, cc, skip_exec=args.skip_exec)
    if issues:
        print("PHASE3_IDA_RANGE=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / STARTER_CHECK_PATH}")
    print(f"validated {args.repo_root / DUMP_PATH}")
    print(f"validated {args.repo_root / EXPECTED_PATH}")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
