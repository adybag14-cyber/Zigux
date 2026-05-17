#!/usr/bin/env python3
"""Fail-close the current Phase 3 bitmap/cpumask parity packet."""

from __future__ import annotations

import argparse
import difflib
import json
import os
import subprocess
import tempfile
from pathlib import Path


SLICE_PATH = Path("Documentation/zigux/phase3-bitmap-cpumask-slice.md")
VALIDATOR_NOTE_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")
HEADER_PATH = Path("include/zigux/bitmap_cpumask.h")
BITMAP_HELPER_PATH = Path("zigux/helpers/bitmap_view.zig")
CPUMASK_HELPER_PATH = Path("zigux/helpers/cpumask_view.zig")
DUMP_PATH = Path("zigux/tests/phase3_bitmap_cpumask_dump.zig")
DUMP_BUILD_PATH = Path("zigux/tests/phase3_bitmap_cpumask_dump_build.zig")
EXPECTED_PATH = Path("zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json")
C_HARNESS_PATH = Path(
    "zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c"
)
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json")

REQUIRED_MARKERS = {
    SLICE_PATH: (
        "zigux/tests/phase3_bitmap_cpumask_dump.zig",
        "zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c",
        "zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json",
        "zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json",
        "scripts/zigux/check-phase3-bitmap-cpumask.py",
        "fixture-backed parity packet",
    ),
    VALIDATOR_NOTE_PATH: (
        "Focused bitmap/cpumask slice present on this branch",
        "zigux/tests/phase3_bitmap_cpumask_dump.zig",
        "zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json",
        "scripts/zigux/check-phase3-bitmap-cpumask.py",
        "helper-local fixture-backed parity packets for `err_ptr` / `xarray` and bitmap/cpumask",
    ),
    HEADER_PATH: (
        "#define ZIGUX_BITMAP_VIEW_ABI_VERSION 1u",
        "#define ZIGUX_CPUMASK_VIEW_ABI_VERSION 1u",
        "struct zigux_bitmap_view {",
        "struct zigux_cpumask_view {",
    ),
    BITMAP_HELPER_PATH: (
        "pub fn wordCount(nbits: u32) u32 {",
        "pub fn lastWordMask(nbits: u32) Word {",
        "pub fn testBit(view: binding.BitmapView, bit: u32) bool {",
        "pub fn summarize(view: binding.BitmapView) binding.BitmapSummary {",
    ),
    CPUMASK_HELPER_PATH: (
        'const bitmap = @import("bitmap_view_helper");',
        "pub fn cpuIsSet(view: binding.CpumaskView, cpu: u32) bool {",
        "pub fn summarize(view: binding.CpumaskView) binding.BitmapSummary {",
    ),
    DUMP_PATH: (
        "binding.bitmap_view_abi_version,",
        "binding.cpumask_view_abi_version,",
        '"bitmap_tail_masked"',
        '"cpumask_window"',
        '"cpumask_cross_word_window"',
        "bitmap_view.testBit(bitmap, 69)",
        "cpumask_view.cpuIsSet(cpumask, 7)",
        "cpumask_view.cpuIsSet(cpumask_cross, bitmap_view.bits_per_word + 10)",
    ),
    DUMP_BUILD_PATH: (
        '.root_source_file = b.path("../uapi/bitmap_cpumask.zig"),',
        '.root_source_file = b.path("../bindings/bitmap_cpumask.zig"),',
        '.root_source_file = b.path("../helpers/bitmap_view.zig"),',
        '.root_source_file = b.path("../helpers/cpumask_view.zig"),',
        '.root_source_file = b.path("phase3_bitmap_cpumask_dump.zig"),',
        '"phase3-bitmap-cpumask-dump"',
    ),
    C_HARNESS_PATH: (
        "#include \"../../../../include/zigux/bitmap_cpumask.h\"",
        'write_case(',
        '"bitmap_tail_masked"',
        '"cpumask_window"',
        '"cpumask_cross_word_window"',
        "test_bit(bitmap, 69U)",
        "bits_per_word() + 10U",
    ),
    EXPECTED_PATH: (
        '"word_bits": 64',
        '"bitmap_view_abi_version": 1',
        '"cpumask_view_abi_version": 1',
        '"name": "bitmap_tail_masked"',
        '"name": "cpumask_window"',
        '"name": "cpumask_cross_word_window"',
        '"probe_present": true',
        '"probe_absent": false',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-bitmap-cpumask"',
        '"status": "parity_packet_present"',
        '"zigux/tests/phase3_bitmap_cpumask_dump.zig"',
        '"zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json"',
        '"python3 scripts/zigux/check-phase3-bitmap-cpumask.py --repo-root . --zig zig --cc gcc"',
    ),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_json(path: Path) -> object:
    return json.loads(_read(path))


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
    ).strip()
    return diff or f"{label} JSON differed without a textual diff"


def _run_zig_dump(repo_root: Path, zig: str) -> object:
    result = _run(
        [
            zig,
            "build",
            "phase3-bitmap-cpumask-dump",
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
    return json.loads(result.stdout)


def _run_c_harness(repo_root: Path, cc: str) -> object:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_bitmap_cpumask_c_") as temp_dir:
        binary = Path(temp_dir) / "phase3_bitmap_cpumask_c_harness"
        compile_result = _run(
            [
                cc,
                "-std=c11",
                "-Wall",
                "-Wextra",
                "-pedantic",
                "-o",
                str(binary),
                str(repo_root / C_HARNESS_PATH),
            ],
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


def validate_repo(
    repo_root: Path,
    zig: str,
    cc: str,
    *,
    skip_exec: bool = False,
) -> list[str]:
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
            manifest = _load_json(manifest_path)
        except json.JSONDecodeError as exc:
            issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        else:
            packet_files = manifest.get("packet_files")
            replay_routes = manifest.get("replay_routes")
            if not isinstance(packet_files, list):
                issues.append("phase3_bitmap_cpumask_manifest.json packet_files is not a list")
            if not isinstance(replay_routes, list):
                issues.append("phase3_bitmap_cpumask_manifest.json replay_routes is not a list")

    if issues or skip_exec:
        return issues

    expected = _load_json(repo_root / EXPECTED_PATH)
    try:
        zig_output = _run_zig_dump(repo_root, zig)
    except RuntimeError as exc:
        issues.append(str(exc))
        return issues
    try:
        c_output = _run_c_harness(repo_root, cc)
    except RuntimeError as exc:
        issues.append(str(exc))
        return issues

    if zig_output != expected:
        issues.append(_diff("zig-output", expected, zig_output))
    if c_output != expected:
        issues.append(_diff("c-output", expected, c_output))
    if zig_output != c_output:
        issues.append(_diff("zig-vs-c", c_output, zig_output))
    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_bitmap_cpumask_") as temp_dir:
        root = Path(temp_dir)
        for relative_path, markers in REQUIRED_MARKERS.items():
            path = root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(markers) + "\n", encoding="utf-8")
        (root / MANIFEST_PATH).write_text(
            "{\n"
            '  "packet_files": [],\n'
            '  "replay_routes": [],\n'
            '  "slug": "phase3-bitmap-cpumask",\n'
            '  "status": "parity_packet_present",\n'
            '  "example": "zigux/tests/phase3_bitmap_cpumask_dump.zig"\n'
            "}\n",
            encoding="utf-8",
        )

        issues = validate_repo(root, "zig", "cc", skip_exec=True)
        if not any("packet_files is not a list" not in issue and "replay_routes is not a list" not in issue for issue in issues):
            pass

        expected_missing = "missing repo file"
        missing_path = root / DUMP_PATH
        missing_path.unlink()
        issues = validate_repo(root, "zig", "cc", skip_exec=True)
        if not any(expected_missing in issue and DUMP_PATH.as_posix() in issue for issue in issues):
            print("PHASE3_BITMAP_CPUMASK_SELF_TEST=fail")
            print("expected missing-file failure for dump path")
            return 1

    print("PHASE3_BITMAP_CPUMASK_SELF_TEST=pass")
    print("PHASE3_BITMAP_CPUMASK_SELF_TEST_CASES=1")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="repository root to validate")
    parser.add_argument("--zig", default=None, help="zig binary to use")
    parser.add_argument("--cc", default=None, help="C compiler to use")
    parser.add_argument("--self-test", action="store_true", help="run checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    repo_root = Path(args.repo_root).resolve()
    zig = _resolve_tool(args.zig, "ZIG", "zig")
    cc = _resolve_tool(args.cc, "CC", "cc")
    issues = validate_repo(repo_root, zig, cc)
    if issues:
        print("PHASE3_BITMAP_CPUMASK=fail")
        print("\n".join(issues))
        return 1

    print("PHASE3_BITMAP_CPUMASK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
