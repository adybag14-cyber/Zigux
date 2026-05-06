#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
HARNESS_REL = Path("zigux/tests/fixtures/phase1_helpers_c_harness.c")
ARTIFACT_DIFF_REL = Path("scripts/zigux/artifact_diff.py")

SOURCE_RELS = [
    HARNESS_REL,
    Path("tools/lib/argv_split.c"),
    Path("tools/lib/bitmap.c"),
    Path("tools/lib/cmdline.c"),
    Path("tools/lib/ctype.c"),
    Path("tools/lib/find_bit.c"),
    Path("tools/lib/hweight.c"),
    Path("tools/lib/list_sort.c"),
    Path("tools/lib/slab.c"),
    Path("tools/lib/str_error_r.c"),
    Path("tools/lib/string.c"),
    Path("tools/lib/rbtree.c"),
    Path("tools/lib/vsprintf.c"),
    Path("tools/lib/zalloc.c"),
]


def fixture_path(root: Path) -> Path:
    return root / FIXTURE_REL


def harness_path(root: Path) -> Path:
    return root / HARNESS_REL


def artifact_diff_path(root: Path) -> Path:
    return root / ARTIFACT_DIFF_REL


def source_paths(root: Path) -> list[Path]:
    return [root / rel for rel in SOURCE_RELS]


def collect_input_issues(root: Path, source_rels: list[Path] | None = None) -> list[str]:
    rels = source_rels or SOURCE_RELS
    missing: list[str] = []
    seen: set[Path] = set()
    duplicates: list[Path] = []

    required_paths = [FIXTURE_REL, HARNESS_REL, ARTIFACT_DIFF_REL]
    for rel in required_paths:
        if not (root / rel).exists():
            missing.append(f"missing:{rel.as_posix()}")

    for rel in rels:
        if rel in seen and rel not in duplicates:
            duplicates.append(rel)
        seen.add(rel)
        if not (root / rel).exists():
            missing.append(f"missing:{rel.as_posix()}")

    for rel in duplicates:
        missing.append(f"duplicate_source:{rel.as_posix()}")

    return missing


def make_self_test_root(root: Path) -> None:
    for rel in [FIXTURE_REL, HARNESS_REL, ARTIFACT_DIFF_REL, *SOURCE_RELS]:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("// fixture\n", encoding="utf-8")


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
    linux_dir = root / "linux"
    urcu_dir = root / "urcu"
    asm_dir.mkdir(parents=True, exist_ok=True)
    linux_dir.mkdir(parents=True, exist_ok=True)
    urcu_dir.mkdir(parents=True, exist_ok=True)
    (asm_dir / "types.h").write_text(
        "\n".join([
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
        ]),
        encoding="utf-8",
    )
    (asm_dir / "posix_types.h").write_text('#include <asm-generic/posix_types.h>\n', encoding="utf-8")
    (asm_dir / "bitsperlong.h").write_text('#define __BITS_PER_LONG (__CHAR_BIT__ * __SIZEOF_LONG__)\n', encoding="utf-8")
    (linux_dir / "slab.h").write_text(
        "\n".join([
            "#ifndef __ZIGUX_HOST_LINUX_SLAB_H__",
            "#define __ZIGUX_HOST_LINUX_SLAB_H__",
            "#include <linux/types.h>",
            "#include <linux/gfp.h>",
            "void *kmalloc(size_t size, gfp_t gfp);",
            "void kfree(void *p);",
            "void *kmalloc_array(size_t n, size_t size, gfp_t gfp);",
            "extern int kmalloc_nr_allocated;",
            "extern int kmalloc_verbose;",
            "static inline bool slab_is_available(void) { return true; }",
            "#endif",
            "",
        ]),
        encoding="utf-8",
    )
    (urcu_dir / "uatomic.h").write_text(
        "\n".join([
            "#ifndef __ZIGUX_HOST_URCU_UATOMIC_H__",
            "#define __ZIGUX_HOST_URCU_UATOMIC_H__",
            "#define uatomic_inc(ptr) (++(*(ptr)))",
            "#define uatomic_dec(ptr) (--(*(ptr)))",
            "#endif",
            "",
        ]),
        encoding="utf-8",
    )


def include_flags(shim_dir: Path) -> list[str]:
    return [
        "-I", str(shim_dir),
        "-I", str(ROOT / "tools" / "include"),
        "-I", str(ROOT / "tools" / "include" / "uapi"),
    ]


def windows_to_wsl(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(":").lower()
    tail = resolved.as_posix().split(":", 1)[1]
    return f"/mnt/{drive}{tail}"


def run_windows_wsl_compile(
    tmp_dir: Path,
    exe: Path,
    actual: Path,
    compiler: str,
    flags: list[str],
    sources: list[Path],
) -> None:
    script_path = tmp_dir / "run_phase1_parity.sh"
    script_lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
    ]

    quoted = [shlex.quote(compiler), "-std=gnu11", "-Wall", "-Wextra", "-Wno-type-limits", "-Wno-int-to-pointer-cast", "-Wno-pointer-to-int-cast", "-o", shlex.quote(windows_to_wsl(exe))]
    index = 0
    while index < len(flags):
        item = flags[index]
        quoted.append(shlex.quote(item))
        if item == "-I":
            index += 1
            quoted.append(shlex.quote(windows_to_wsl(Path(flags[index]))))
        index += 1
    quoted.extend(shlex.quote(windows_to_wsl(path)) for path in sources)
    script_lines.append(" ".join(quoted))
    script_lines.append(f'{shlex.quote(windows_to_wsl(exe))} > {shlex.quote(windows_to_wsl(actual))}')
    with script_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(script_lines) + "\n")
    run(["wsl", "bash", windows_to_wsl(script_path)], cwd=str(ROOT))


def compile_and_run(
    tmp_dir: Path,
    exe: Path,
    actual: Path,
    compiler: str,
    flags: list[str],
    sources: list[Path],
) -> None:
    if os.name == "nt" and shutil.which("wsl"):
        run_windows_wsl_compile(tmp_dir, exe, actual, compiler, flags, sources)
        return

    compile_cmd = [compiler, "-std=gnu11", "-Wall", "-Wextra", "-Wno-type-limits", "-Wno-int-to-pointer-cast", "-Wno-pointer-to-int-cast", "-o", str(exe)]
    compile_cmd.extend(flags)
    compile_cmd.extend(str(path) for path in sources)
    run(compile_cmd, cwd=str(ROOT))
    result = run([str(exe)], cwd=str(ROOT), capture_output=True)
    actual.write_text(result.stdout, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_parity_selftest_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        make_self_test_root(tmp_root)

        assert collect_input_issues(tmp_root) == []

        (tmp_root / FIXTURE_REL).unlink()
        assert collect_input_issues(tmp_root) == [f"missing:{FIXTURE_REL.as_posix()}"]
        make_self_test_root(tmp_root)

        (tmp_root / HARNESS_REL).unlink()
        missing_harness = collect_input_issues(tmp_root)
        assert f"missing:{HARNESS_REL.as_posix()}" in missing_harness
        make_self_test_root(tmp_root)

        (tmp_root / ARTIFACT_DIFF_REL).unlink()
        missing_artifact_diff = collect_input_issues(tmp_root)
        assert f"missing:{ARTIFACT_DIFF_REL.as_posix()}" in missing_artifact_diff
        make_self_test_root(tmp_root)

        (tmp_root / Path("tools/lib/bitmap.c")).unlink()
        missing_source = collect_input_issues(tmp_root)
        assert f"missing:tools/lib/bitmap.c" in missing_source
        make_self_test_root(tmp_root)

        (tmp_root / Path("tools/lib/find_bit.c")).unlink()
        missing_source = collect_input_issues(tmp_root)
        assert f"missing:tools/lib/find_bit.c" in missing_source
        make_self_test_root(tmp_root)

        (tmp_root / Path("tools/lib/string.c")).unlink()
        missing_source = collect_input_issues(tmp_root)
        assert f"missing:tools/lib/string.c" in missing_source
        make_self_test_root(tmp_root)

        (tmp_root / Path("tools/lib/rbtree.c")).unlink()
        missing_source = collect_input_issues(tmp_root)
        assert f"missing:tools/lib/rbtree.c" in missing_source
        make_self_test_root(tmp_root)

        duplicate_sources = SOURCE_RELS + [Path("tools/lib/string.c")]
        duplicate_issues = collect_input_issues(tmp_root, duplicate_sources)
        assert "duplicate_source:tools/lib/string.c" in duplicate_issues

    print("PHASE1_PARITY_SELF_TEST=pass")
    print("PHASE1_PARITY_SELF_TEST_CASE_COUNT=9")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and check Phase 1 helper parity fixtures.")
    parser.add_argument("--refresh", action="store_true", help="Refresh the committed JSON fixture from current C outputs.")
    parser.add_argument("--cc", help="Explicit C compiler path to use.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-test cases without compiling the live helper packet.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    input_issues = collect_input_issues(ROOT)
    if input_issues:
        print("PHASE1_PARITY=fail")
        print("PHASE1_PARITY_INPUT_ISSUES_START")
        for issue in input_issues:
            print(issue)
        print("PHASE1_PARITY_INPUT_ISSUES_END")
        return 1

    compiler = args.cc or os.environ.get("CC") or ("gcc" if os.name == "nt" and shutil.which("wsl") else find_compiler(None))

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_parity_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        shim_dir = tmp_dir / "shim"
        write_host_shims(shim_dir)

        exe = tmp_dir / ("phase1_helpers_c_harness.exe" if os.name == "nt" else "phase1_helpers_c_harness")
        actual = tmp_dir / "phase1_helpers.actual.json"

        compile_and_run(tmp_dir, exe, actual, compiler, include_flags(shim_dir), source_paths(ROOT))

        if args.refresh:
            fixture_path(ROOT).write_text(actual.read_text(encoding="utf-8"), encoding="utf-8")
            print("PHASE1_PARITY_REFRESH=pass")
            print(f"FIXTURE={fixture_path(ROOT)}")
            return 0

        diff_cmd = [sys.executable, str(artifact_diff_path(ROOT)), "--mode", "json", str(fixture_path(ROOT)), str(actual)]
        run(diff_cmd, cwd=str(ROOT))
        print("PHASE1_PARITY=pass")
        print(f"FIXTURE={fixture_path(ROOT)}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
