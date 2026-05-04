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
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase7_argv_split.json"
HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase7_argv_split_c_harness.c"
SOURCE = ROOT / "lib" / "argv_split.c"
SELF_TEST_PAYLOAD_ENV = "PHASE7_ARGV_SPLIT_PARITY_SELFTEST_PAYLOAD"


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
    (linux_dir / "kernel.h").write_text(
        "\n".join(
            [
                "#ifndef __ZIGUX_HOST_LINUX_KERNEL_H__",
                "#define __ZIGUX_HOST_LINUX_KERNEL_H__",
                "#include <stdbool.h>",
                "#include <stddef.h>",
                "#include <stdint.h>",
                "#endif",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (linux_dir / "slab.h").write_text(
        "\n".join(
            [
                "#ifndef __ZIGUX_HOST_LINUX_SLAB_H__",
                "#define __ZIGUX_HOST_LINUX_SLAB_H__",
                "#include <stddef.h>",
                "#include <stdint.h>",
                "#include <stdlib.h>",
                "#include <string.h>",
                "typedef unsigned int gfp_t;",
                "#define KMALLOC_MAX_SIZE ((size_t)1 << 20)",
                "static inline char *kstrndup(const char *src, size_t maxlen, gfp_t gfp)",
                "{",
                "    size_t used = strnlen(src, maxlen);",
                "    char *copy = (char *)malloc(used + 1);",
                "    (void)gfp;",
                "    if (!copy)",
                "        return NULL;",
                "    memcpy(copy, src, used);",
                "    copy[used] = '\\0';",
                "    return copy;",
                "}",
                "static inline void *kmalloc_array(size_t n, size_t size, gfp_t gfp)",
                "{",
                "    (void)gfp;",
                "    if (size != 0 && n > ((size_t)-1) / size)",
                "        return NULL;",
                "    return calloc(n, size);",
                "}",
                "static inline void kfree(void *ptr)",
                "{",
                "    free(ptr);",
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


def validate_required_paths(*, fixture: Path = FIXTURE, harness: Path = HARNESS, source: Path = SOURCE) -> None:
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
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_argv_split_parity_selftest_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        fixture = tmp_dir / "expected.json"
        harness = tmp_dir / "fixture.c"
        source = tmp_dir / "source.c"
        fake_compiler = tmp_dir / "fake-cc"
        payload = {
            "blank_input": {"argc": 0, "argv": []},
            "first_nul_stops": {"argc": 2, "argv": ["root=/dev/vda", "rw"]},
            "leading_nul_stays_empty": {"argc": 0, "argv": []},
            "quote_characters_stay_literal": {
                "argc": 3,
                "argv": ['root=\"/dev/sda', '1\"', "single"],
            },
            "whitespace_collapse": {
                "argc": 3,
                "argv": ["init=/init", "console=ttyS0", "panic=-1"],
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
        exe = tmp_dir / "phase7_argv_split_selftest"
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
            raise SystemExit("phase7-argv-split-parity-self-test:baseline_failed")

        drift_actual = tmp_dir / "drift.json"
        drift_exe = tmp_dir / "phase7_argv_split_selftest_drift"
        env[SELF_TEST_PAYLOAD_ENV] = render_json(
            {
                **payload,
                "quote_characters_stay_literal": {
                    "argc": 2,
                    "argv": ['root=\"/dev/sda 1\"', "single"],
                },
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
            raise SystemExit("phase7-argv-split-parity-self-test:quote_drift_not_detected")

        nul_drift_actual = tmp_dir / "nul-drift.json"
        nul_drift_exe = tmp_dir / "phase7_argv_split_selftest_nul_drift"
        env[SELF_TEST_PAYLOAD_ENV] = render_json(
            {
                **payload,
                "leading_nul_stays_empty": {"argc": 1, "argv": ["ignored"]},
            }
        )
        compile_and_run(
            nul_drift_exe,
            nul_drift_actual,
            str(fake_compiler),
            shim_dir,
            harness=harness,
            source=source,
            cwd=tmp_dir,
            env=env,
        )
        if load_json(nul_drift_actual) == load_json(fixture):
            raise SystemExit("phase7-argv-split-parity-self-test:nul_drift_not_detected")

        fixture.unlink()
        try:
            validate_required_paths(fixture=fixture, harness=harness, source=source)
        except FileNotFoundError as exc:
            if str(exc) != f"missing fixture: {fixture}":
                raise SystemExit(
                    "phase7-argv-split-parity-self-test:missing_fixture_guard_shape"
                ) from exc
        else:
            raise SystemExit("phase7-argv-split-parity-self-test:missing_fixture_guard_not_detected")

    print("PHASE7_ARGV_SPLIT_PARITY_SELF_TEST=pass")
    print("PHASE7_ARGV_SPLIT_PARITY_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate and check the Phase 7 argv_split parity fixture."
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
        print("PHASE7_ARGV_SPLIT_PARITY=fail")
        print(str(exc))
        return 1

    compiler = find_compiler(args.cc)

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_argv_split_parity_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        shim_dir = tmp_dir / "shim"
        write_host_shims(shim_dir)

        exe = tmp_dir / "phase7_argv_split_c_harness"
        actual = tmp_dir / "phase7_argv_split.actual.json"
        compile_and_run(exe, actual, compiler, shim_dir)

        actual_json = load_json(actual)
        normalized = render_json(actual_json)

        if args.refresh:
            FIXTURE.write_text(normalized, encoding="utf-8")
            print("PHASE7_ARGV_SPLIT_PARITY_REFRESH=pass")
            print(f"FIXTURE={FIXTURE}")
            return 0

        expected_json = load_json(FIXTURE)
        if actual_json != expected_json:
            print("PHASE7_ARGV_SPLIT_PARITY=fail")
            print(f"FIXTURE={FIXTURE}")
            print(f"ACTUAL={actual}")
            return 1

        print("PHASE7_ARGV_SPLIT_PARITY=pass")
        print(f"FIXTURE={FIXTURE}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())