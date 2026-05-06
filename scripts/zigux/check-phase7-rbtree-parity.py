#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase7_rbtree.json"
HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase7_rbtree_c_harness.c"
ARTIFACT_DIFF = ROOT / "scripts" / "zigux" / "artifact_diff.py"
SOURCE = ROOT / "lib" / "rbtree.c"


def find_compiler(explicit: str | None) -> str:
    if explicit:
        return explicit
    for candidate in ("gcc", "cc", "clang"):
        path = shutil.which(candidate)
        if path:
            return path
    raise FileNotFoundError("no C compiler found on PATH")


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def write_host_shims(root: Path) -> None:
    asm_dir = root / "asm"
    asm_dir.mkdir(parents=True, exist_ok=True)
    (asm_dir / "types.h").write_text(
        "\n".join(
            [
                "#ifndef __ZIGUX_HOST_ASM_TYPES_H__",
                "#define __ZIGUX_HOST_ASM_TYPES_H__",
                "typedef signed char __s8;",
                "typedef unsigned char __u8;",
                "typedef signed short __s16;",
                "typedef unsigned short __u16;",
                "typedef signed int __s32;",
                "typedef unsigned int __u32;",
                "typedef signed long long __s64;",
                "typedef unsigned long long __u64;",
                "#endif",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (asm_dir / "posix_types.h").write_text('#include <asm-generic/posix_types.h>\n', encoding="utf-8")
    (asm_dir / "bitsperlong.h").write_text('#define __BITS_PER_LONG (__CHAR_BIT__ * __SIZEOF_LONG__)\n', encoding="utf-8")


def include_flags(shim_dir: Path) -> list[str]:
    return [
        "-I",
        str(shim_dir),
        "-I",
        str(ROOT / "tools" / "include"),
        "-I",
        str(ROOT / "tools" / "include" / "uapi"),
    ]


def compile_and_run(exe: Path, actual: Path, compiler: str, flags: list[str]) -> None:
    compile_cmd = [
        compiler,
        "-std=gnu11",
        "-Wall",
        "-Wextra",
        "-Wno-type-limits",
        "-Wno-int-to-pointer-cast",
        "-Wno-pointer-to-int-cast",
        "-o",
        str(exe),
    ]
    compile_cmd.extend(flags)
    compile_cmd.extend([str(HARNESS), str(SOURCE)])
    run(compile_cmd, cwd=str(ROOT))
    result = run([str(exe)], cwd=str(ROOT), capture_output=True)
    actual.write_text(result.stdout, encoding="utf-8")


def run_self_test() -> None:
    case_count = 0

    assert SOURCE == ROOT / "lib" / "rbtree.c"
    case_count += 1

    assert find_compiler("/tmp/phase7-custom-cc") == "/tmp/phase7-custom-cc"
    case_count += 1

    with mock.patch("shutil.which", return_value=None):
        try:
            find_compiler(None)
        except FileNotFoundError:
            pass
        else:
            raise AssertionError("expected FileNotFoundError when no compiler is discoverable")
    case_count += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_rbtree_checker_selftest_") as tmp_dir_str:
        shim_root = Path(tmp_dir_str) / "shim"
        write_host_shims(shim_root)
        types_text = (shim_root / "asm" / "types.h").read_text(encoding="utf-8")
        posix_text = (shim_root / "asm" / "posix_types.h").read_text(encoding="utf-8")
        bits_text = (shim_root / "asm" / "bitsperlong.h").read_text(encoding="utf-8")
        assert "__ZIGUX_HOST_ASM_TYPES_H__" in types_text
        assert "typedef unsigned long long __u64;" in types_text
        assert posix_text == "#include <asm-generic/posix_types.h>\n"
        assert bits_text == "#define __BITS_PER_LONG (__CHAR_BIT__ * __SIZEOF_LONG__)\n"
    case_count += 1

    shim_dir = Path("/tmp/phase7-selftest-shim")
    assert include_flags(shim_dir) == [
        "-I",
        str(shim_dir),
        "-I",
        str(ROOT / "tools" / "include"),
        "-I",
        str(ROOT / "tools" / "include" / "uapi"),
    ]
    case_count += 1

    print("PHASE7_RBTREE_PARITY_SELF_TEST=pass")
    print(f"PHASE7_RBTREE_PARITY_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and check the Phase 7 rbtree parity fixture.")
    parser.add_argument("--refresh", action="store_true", help="Refresh the committed JSON fixture from the C harness.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-test cases without compiling the C parity harness.")
    parser.add_argument("--cc", help="Explicit C compiler path to use.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    compiler = find_compiler(args.cc)

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_rbtree_parity_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        shim_dir = tmp_dir / "shim"
        write_host_shims(shim_dir)

        exe = tmp_dir / "phase7_rbtree_c_harness"
        actual = tmp_dir / "phase7_rbtree.actual.json"

        compile_and_run(exe, actual, compiler, include_flags(shim_dir))

        if args.refresh:
            FIXTURE.write_text(actual.read_text(encoding="utf-8"), encoding="utf-8")
            print("PHASE7_RBTREE_PARITY_REFRESH=pass")
            print(f"FIXTURE={FIXTURE}")
            return 0

        diff_cmd = [sys.executable, str(ARTIFACT_DIFF), "--mode", "json", str(FIXTURE), str(actual)]
        run(diff_cmd, cwd=str(ROOT))
        print("PHASE7_RBTREE_PARITY=pass")
        print(f"FIXTURE={FIXTURE}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
