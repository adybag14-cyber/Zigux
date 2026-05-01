#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase7_cmdline.json"
HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase7_cmdline_c_harness.c"
SOURCE = ROOT / "lib" / "cmdline.c"


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
    linux_dir = root / "linux"
    linux_dir.mkdir(parents=True, exist_ok=True)
    (linux_dir / "export.h").write_text(
        "\n".join(
            [
                "#ifndef __ZIGUX_HOST_LINUX_EXPORT_H__",
                "#define __ZIGUX_HOST_LINUX_EXPORT_H__",
                "#define EXPORT_SYMBOL(symbol)",
                "#define EXPORT_SYMBOL_GPL(symbol)",
                "#endif",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (linux_dir / "string.h").write_text(
        "\n".join(
            [
                "#ifndef __ZIGUX_HOST_LINUX_STRING_H__",
                "#define __ZIGUX_HOST_LINUX_STRING_H__",
                "#include <string.h>",
                "#endif",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (linux_dir / "ctype.h").write_text(
        "\n".join(
            [
                "#ifndef __ZIGUX_HOST_LINUX_CTYPE_H__",
                "#define __ZIGUX_HOST_LINUX_CTYPE_H__",
                "#include <ctype.h>",
                "#endif",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (linux_dir / "kernel.h").write_text(
        "\n".join(
            [
                "#ifndef __ZIGUX_HOST_LINUX_KERNEL_H__",
                "#define __ZIGUX_HOST_LINUX_KERNEL_H__",
                "#include <ctype.h>",
                "#include <stdbool.h>",
                "#include <stddef.h>",
                "#include <stdint.h>",
                "static inline int __zigux_digit_value(char ch)",
                "{",
                "    if (ch >= '0' && ch <= '9')",
                "        return ch - '0';",
                "    if (ch >= 'a' && ch <= 'f')",
                "        return ch - 'a' + 10;",
                "    if (ch >= 'A' && ch <= 'F')",
                "        return ch - 'A' + 10;",
                "    return -1;",
                "}",
                "static inline unsigned long long simple_strtoull(const char *cp, char **endp, unsigned int base)",
                "{",
                "    const char *cursor = cp;",
                "    unsigned long long value = 0;",
                "    int digit = -1;",
                "    if (base == 0) {",
                "        if (cursor[0] == '0' && (cursor[1] == 'x' || cursor[1] == 'X')) {",
                "            base = 16;",
                "            cursor += 2;",
                "        } else if (cursor[0] == '0') {",
                "            base = 8;",
                "        } else {",
                "            base = 10;",
                "        }",
                "    } else if (base == 16 && cursor[0] == '0' && (cursor[1] == 'x' || cursor[1] == 'X')) {",
                "        cursor += 2;",
                "    }",
                "    while ((digit = __zigux_digit_value(*cursor)) >= 0 && digit < (int)base) {",
                "        value = (value * base) + (unsigned int)digit;",
                "        cursor++;",
                "    }",
                "    if (cursor == cp || (cursor == cp + 2 && base == 16 && cp[0] == '0' && (cp[1] == 'x' || cp[1] == 'X'))) {",
                "        if (endp)",
                "            *endp = (char *)cp;",
                "        return 0;",
                "    }",
                "    if (endp)",
                "        *endp = (char *)cursor;",
                "    return value;",
                "}",
                "static inline unsigned long simple_strtoul(const char *cp, char **endp, unsigned int base)",
                "{",
                "    return (unsigned long)simple_strtoull(cp, endp, base);",
                "}",
                "static inline long simple_strtol(const char *cp, char **endp, unsigned int base)",
                "{",
                "    if (*cp == '-')",
                "        return -(long)simple_strtoul(cp + 1, endp, base);",
                "    return (long)simple_strtoul(cp, endp, base);",
                "}",
                "static inline char *skip_spaces(const char *str)",
                "{",
                "    while (*str && isspace((unsigned char)*str))",
                "        ++str;",
                "    return (char *)str;",
                "}",
                "#endif",
                "",
            ]
        ),
        encoding="utf-8",
    )


def compile_and_run(exe: Path, actual: Path, compiler: str, include_root: Path) -> None:
    compile_cmd = [
        compiler,
        "-std=gnu11",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-I",
        str(include_root),
        "-o",
        str(exe),
        str(HARNESS),
        str(SOURCE),
    ]
    run(compile_cmd, cwd=str(ROOT))
    result = run([str(exe)], cwd=str(ROOT), capture_output=True)
    actual.write_text(result.stdout, encoding="utf-8")


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate and check the Phase 7 cmdline parity fixture."
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh the committed JSON fixture from the C harness.",
    )
    parser.add_argument("--cc", help="Explicit C compiler path to use.")
    args = parser.parse_args()

    compiler = find_compiler(args.cc)

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_cmdline_parity_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        shim_dir = tmp_dir / "shim"
        write_host_shims(shim_dir)

        exe = tmp_dir / "phase7_cmdline_c_harness"
        actual = tmp_dir / "phase7_cmdline.actual.json"
        compile_and_run(exe, actual, compiler, shim_dir)

        actual_json = load_json(actual)
        normalized = json.dumps(actual_json, indent=2, sort_keys=True) + "\n"

        if args.refresh:
            FIXTURE.write_text(normalized, encoding="utf-8")
            print("PHASE7_CMDLINE_PARITY_REFRESH=pass")
            print(f"FIXTURE={FIXTURE}")
            return 0

        expected_json = load_json(FIXTURE)
        if actual_json != expected_json:
            print("PHASE7_CMDLINE_PARITY=fail")
            print(f"FIXTURE={FIXTURE}")
            print(f"ACTUAL={actual}")
            return 1

        print("PHASE7_CMDLINE_PARITY=pass")
        print(f"FIXTURE={FIXTURE}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
