#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase7_cmdline.json"
HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase7_cmdline_c_harness.c"
SOURCE = ROOT / "lib" / "cmdline.c"
SELF_TEST_PAYLOAD_ENV = "PHASE7_CMDLINE_PARITY_SELFTEST_PAYLOAD"


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
                "#ifndef fallthrough",
                "#define fallthrough __attribute__((__fallthrough__))",
                "#endif",
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
                "static inline bool __zigux_is_base_digit(char ch, unsigned int base)",
                "{",
                "    int digit = __zigux_digit_value(ch);",
                "    return digit >= 0 && (unsigned int)digit < base;",
                "}",
                "static inline unsigned long long simple_strtoull(const char *cp, char **endp, unsigned int base)",
                "{",
                "    const char *cursor = cp;",
                "    unsigned long long value = 0;",
                "    int digit = -1;",
                "    if (base == 0) {",
                "        if (cursor[0] == '0' && (cursor[1] == 'x' || cursor[1] == 'X') && __zigux_is_base_digit(cursor[2], 16)) {",
                "            base = 16;",
                "            cursor += 2;",
                "        } else if (cursor[0] == '0') {",
                "            base = 8;",
                "        } else {",
                "            base = 10;",
                "        }",
                "    } else if (base == 16 && cursor[0] == '0' && (cursor[1] == 'x' || cursor[1] == 'X') && __zigux_is_base_digit(cursor[2], 16)) {",
                "        cursor += 2;",
                "    }",
                "    while ((digit = __zigux_digit_value(*cursor)) >= 0 && digit < (int)base) {",
                "        value = (value * base) + (unsigned int)digit;",
                "        cursor++;",
                "    }",
                "    if (cursor == cp) {",
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


def validate_required_path(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"missing {label}: {path}")


def validate_required_paths(
    *, fixture: Path = FIXTURE, harness: Path = HARNESS, source: Path = SOURCE
) -> None:
    validate_required_path(fixture, "fixture")
    validate_required_path(harness, "harness")
    validate_required_path(source, "source")


def compile_and_run(
    exe: Path,
    actual: Path,
    compiler: str,
    include_root: Path,
    *,
    harness: Path = HARNESS,
    source: Path = SOURCE,
    cwd: Path = ROOT,
    env: dict[str, str] | None = None,
) -> None:
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
        str(harness),
        str(source),
    ]
    run(compile_cmd, cwd=str(cwd), env=env)
    result = run([str(exe)], cwd=str(cwd), capture_output=True, env=env)
    actual.write_text(result.stdout, encoding="utf-8")


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def render_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def write_fake_compiler(path: Path) -> None:
    path.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "import os\n"
        "import sys\n"
        "out = Path(sys.argv[sys.argv.index('-o') + 1])\n"
        f"payload = os.environ[{SELF_TEST_PAYLOAD_ENV!r}]\n"
        "out.write_text(\n"
        "    '#!/usr/bin/env python3\\n'\n"
        "    'import sys\\n'\n"
        "    'sys.stdout.write(' + repr(payload) + ')\\n',\n"
        "    encoding='utf-8',\n"
        ")\n"
        "out.chmod(0o755)\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_cmdline_parity_selftest_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        fixture = tmp_dir / "expected.json"
        harness = tmp_dir / "fixture.c"
        source = tmp_dir / "source.c"
        fake_compiler = tmp_dir / "fake-cc"
        payload = {
            "parse_option_str": {
                "assignment_not_bare": False,
                "exact_bare_option": True,
            },
            "next_arg": {
                "quoted_value": {
                    "param": "foo",
                    "value": "bar baz",
                    "remaining": "",
                },
                "empty_value": {
                    "param": "foo",
                    "value": "",
                    "remaining": "",
                },
            },
        }
        fixture.write_text(render_json(payload), encoding="utf-8")
        harness.write_text("/* self-test fixture */\n", encoding="utf-8")
        source.write_text("/* self-test source */\n", encoding="utf-8")
        write_fake_compiler(fake_compiler)

        shim_dir = tmp_dir / "shim"
        write_host_shims(shim_dir)
        validate_required_paths(fixture=fixture, harness=harness, source=source)

        env = os.environ.copy()
        env[SELF_TEST_PAYLOAD_ENV] = render_json(payload)
        actual = tmp_dir / "actual.json"
        exe = tmp_dir / "phase7_cmdline_selftest"
        compile_and_run(
            exe,
            actual,
            str(fake_compiler),
            shim_dir,
            harness=harness,
            source=source,
            cwd=tmp_dir,
            env=env,
        )
        if load_json(actual) != load_json(fixture):
            raise SystemExit("phase7-cmdline-parity-self-test:baseline_failed")

        drift_actual = tmp_dir / "drift.json"
        drift_exe = tmp_dir / "phase7_cmdline_selftest_drift"
        env[SELF_TEST_PAYLOAD_ENV] = render_json(
            {
                "parse_option_str": {
                    "assignment_not_bare": False,
                    "exact_bare_option": False,
                },
                "next_arg": payload["next_arg"],
            }
        )
        compile_and_run(
            drift_exe,
            drift_actual,
            str(fake_compiler),
            shim_dir,
            harness=harness,
            source=source,
            cwd=tmp_dir,
            env=env,
        )
        if load_json(drift_actual) == load_json(fixture):
            raise SystemExit("phase7-cmdline-parity-self-test:parse_option_str_drift_not_detected")

        next_arg_drift_actual = tmp_dir / "next_arg_drift.json"
        next_arg_drift_exe = tmp_dir / "phase7_cmdline_selftest_next_arg_drift"
        env[SELF_TEST_PAYLOAD_ENV] = render_json(
            {
                "parse_option_str": payload["parse_option_str"],
                "next_arg": {
                    "quoted_value": {
                        "param": "foo",
                        "value": "bar baz",
                        "remaining": "",
                    },
                    "empty_value": {
                        "param": "foo",
                        "value": "",
                        "remaining": "still here",
                    },
                },
            }
        )
        compile_and_run(
            next_arg_drift_exe,
            next_arg_drift_actual,
            str(fake_compiler),
            shim_dir,
            harness=harness,
            source=source,
            cwd=tmp_dir,
            env=env,
        )
        if load_json(next_arg_drift_actual) == load_json(fixture):
            raise SystemExit("phase7-cmdline-parity-self-test:next_arg_drift_not_detected")

        fixture.unlink()
        try:
            validate_required_paths(fixture=fixture, harness=harness, source=source)
        except FileNotFoundError as exc:
            if str(exc) != f"missing fixture: {fixture}":
                raise SystemExit(
                    "phase7-cmdline-parity-self-test:missing_fixture_guard_shape"
                ) from exc
        else:
            raise SystemExit("phase7-cmdline-parity-self-test:missing_fixture_guard_not_detected")

    print("PHASE7_CMDLINE_PARITY_SELF_TEST=pass")
    print("PHASE7_CMDLINE_PARITY_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate and check the Phase 7 cmdline parity fixture."
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh the committed JSON fixture from the C harness.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Exercise the checker with a synthetic no-compiler fixture.",
    )
    parser.add_argument("--cc", help="Explicit C compiler path to use.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        validate_required_paths()
    except FileNotFoundError as exc:
        print("PHASE7_CMDLINE_PARITY=fail")
        print(str(exc))
        return 1

    compiler = find_compiler(args.cc)

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_cmdline_parity_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        shim_dir = tmp_dir / "shim"
        write_host_shims(shim_dir)

        exe = tmp_dir / "phase7_cmdline_c_harness"
        actual = tmp_dir / "phase7_cmdline.actual.json"
        compile_and_run(exe, actual, compiler, shim_dir)

        actual_json = load_json(actual)
        normalized = render_json(actual_json)

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