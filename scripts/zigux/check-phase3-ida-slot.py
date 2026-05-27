#!/usr/bin/env python3
"""Fail-close the current Phase 3 ida-slot starter-plus-dump packet."""

from __future__ import annotations

import argparse
import difflib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


HELPER_PATH = Path("zigux/helpers/ida_slot_view.zig")
STARTER_CHECK_PATH = Path("scripts/zigux/check-phase3-ida-slot-starter-packet.py")
DUMP_PATH = Path("zigux/tests/phase3_ida_slot_dump.zig")
DUMP_BUILD_PATH = Path("zigux/tests/phase3_ida_slot_dump_build.zig")
EXPECTED_PATH = Path("zigux/tests/fixtures/phase3_ida_slot/expected.json")
C_HARNESS_PATH = Path("zigux/tests/fixtures/phase3_ida_slot/phase3_ida_slot_c_harness.c")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_ida_slot_manifest.json")

REQUIRED_MARKERS = {
    HELPER_PATH: (
        "pub const inline_bit_capacity: usize = @bitSizeOf(usize) - 1;",
        "pub fn fromInlineMask(mask: usize) MakeInlineMaskError!SlotView {",
        "pub fn fromUnexpectedError(code: isize) SlotView {",
    ),
    DUMP_PATH: (
        'const ida_slot_view = @import("ida_slot_view");',
        '.unexpected_err => "unexpected_err",',
        'try writeCase(writer, "unexpected_err", ida_slot_view.fromUnexpectedError(-22).rawValue(), false);',
    ),
    DUMP_BUILD_PATH: (
        '.root_source_file = b.path("../helpers/ida_slot_view.zig"),',
        '"phase3-ida-slot-dump"',
    ),
    C_HARNESS_PATH: (
        '#define INLINE_BIT_CAPACITY ((unsigned)(sizeof(uintptr_t) * 8U - 1U))',
        'return "unexpected_err";',
        'write_case("unexpected_err", (uintptr_t)(intptr_t)-22, false);',
    ),
    EXPECTED_PATH: (
        '"inline_bit_capacity": 63',
        '"name": "inline_top"',
        '"unexpected_error": -22',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-ida-slot"',
        '"status": "starter_and_dump_packet_present"',
        '"python3 scripts/zigux/check-phase3-ida-slot.py --repo-root . --zig zig --cc gcc"',
    ),
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)


def resolve_tool(explicit: str | None, env_name: str, default: str) -> str:
    if explicit:
        return explicit
    return os.environ.get(env_name, default)


def diff_json(label: str, expected: object, actual: object) -> str:
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


def run_starter_checker(repo_root: Path) -> None:
    result = run(
        [sys.executable, str(repo_root / STARTER_CHECK_PATH), "--repo-root", str(repo_root)],
        cwd=repo_root,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "starter checker failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def run_zig_dump(repo_root: Path, zig: str) -> object:
    result = run(
        [zig, "build", "phase3-ida-slot-dump", "--build-file", str(repo_root / DUMP_BUILD_PATH)],
        cwd=repo_root,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "zig dump failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return json.loads(result.stdout)


def run_c_harness(repo_root: Path, cc: str) -> object:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_ida_slot_c_") as temp_dir:
        binary = Path(temp_dir) / "phase3_ida_slot_c_harness"
        compile_result = run(
            [cc, "-std=c11", "-Wall", "-Wextra", "-pedantic", "-o", str(binary), str(repo_root / C_HARNESS_PATH)],
            cwd=repo_root,
        )
        if compile_result.returncode != 0:
            raise RuntimeError(
                "c harness compile failed:\n"
                f"stdout:\n{compile_result.stdout}\n"
                f"stderr:\n{compile_result.stderr}"
            )
        run_result = run([str(binary)], cwd=repo_root)
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
        if not path.exists():
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        text = read_text(path)
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")

    if issues or skip_exec:
        return issues

    expected = json.loads(read_text(repo_root / EXPECTED_PATH))
    try:
        run_starter_checker(repo_root)
        zig_actual = run_zig_dump(repo_root, zig)
        c_actual = run_c_harness(repo_root, cc)
    except Exception as exc:
        issues.append(str(exc))
        return issues

    if zig_actual != expected:
        issues.append(diff_json("zig-dump", expected, zig_actual))
    if c_actual != expected:
        issues.append(diff_json("c-harness", expected, c_actual))
    if zig_actual != c_actual:
        issues.append(diff_json("zig-vs-c", zig_actual, c_actual))
    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_ida_slot_") as temp_dir:
        root = Path(temp_dir)
        for relative_path, markers in REQUIRED_MARKERS.items():
            path = root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(markers) + "\n", encoding="utf-8")
        issues = validate_repo(root, zig="zig", cc="gcc", skip_exec=True)
        if issues:
            print("PHASE3_IDA_SLOT_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

    print("PHASE3_IDA_SLOT_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current Phase 3 ida-slot starter-plus-dump packet.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--zig")
    parser.add_argument("--cc")
    parser.add_argument("--skip-exec", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    zig = resolve_tool(args.zig, "ZIG", "zig")
    cc = resolve_tool(args.cc, "CC", "gcc")
    issues = validate_repo(args.repo_root, zig, cc, skip_exec=args.skip_exec)
    if issues:
        print("PHASE3_IDA_SLOT=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / DUMP_PATH}")
    print(f"validated {args.repo_root / EXPECTED_PATH}")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
