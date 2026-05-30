#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
CONFDATA_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"

CONFIG_SAMPLE = """CONFIG_ALPHA=y
CONFIG_BETA=m
CONFIG_COUNT=7
CONFIG_NAME=\"zigux\\\"bridge\\\\\"
CONFIG_EMPTY=
CONFIG_EXPLICIT_N=n
# CONFIG_DEBUG is not set
"""

EXPECTED_AUTO_CONF = """CONFIG_ALPHA=y
CONFIG_BETA=m
CONFIG_COUNT=7
CONFIG_NAME=\"zigux\\\"bridge\\\\\"
CONFIG_EMPTY=
CONFIG_EXPLICIT_N=n
"""

EXPECTED_AUTOCONF_HEADER = """#define CONFIG_ALPHA 1
#define CONFIG_BETA_MODULE 1
#define CONFIG_COUNT 7
#define CONFIG_NAME \"zigux\\\"bridge\\\\\"
#define CONFIG_EMPTY 
"""

MODE_EXPECTATIONS = {
    "auto.conf": EXPECTED_AUTO_CONF,
    "autoconf.h": EXPECTED_AUTOCONF_HEADER,
}

EXPECTED_SELF_TEST_CASE_COUNT = 4


def run(cmd: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    zig = shutil.which("zig")
    if zig:
        return zig
    raise SystemExit("ZIG_NOT_FOUND")


def compile_tool(zig: str, output: Path) -> None:
    if not CONFDATA_BRIDGE.exists():
        raise SystemExit(f"CONFDATA_BRIDGE_NOT_FOUND={CONFDATA_BRIDGE}")
    run([zig, "build-exe", str(CONFDATA_BRIDGE), "-O", "Debug", "-femit-bin=" + str(output)], cwd=ROOT)


def unified_diff(expected: str, actual: str, *, label: str) -> str:
    return "".join(
        difflib.unified_diff(
            expected.splitlines(keepends=True),
            actual.splitlines(keepends=True),
            fromfile=f"expected/{label}",
            tofile=f"actual/{label}",
        )
    )


def check_exact_output(label: str, expected: str, actual: str, *, emit_diff: bool = True) -> None:
    if actual != expected:
        if emit_diff:
            print(f"CONFDATA_OUTPUT_MODE_DIFF=fail mode={label}")
            print(unified_diff(expected, actual, label=label), end="")
        raise SystemExit(1)


def run_output_mode_checks(zig: str) -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_confdata_output_modes_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        exe = tmp_dir / ("confdata-bridge.exe" if sys.platform == "win32" else "confdata-bridge")
        config = tmp_dir / "sample.config"
        config.write_text(CONFIG_SAMPLE, encoding="utf-8", newline="\n")

        compile_tool(zig, exe)
        for mode, expected in MODE_EXPECTATIONS.items():
            first = run([str(exe), mode, str(config)], cwd=ROOT).stdout
            second = run([str(exe), mode, str(config)], cwd=ROOT).stdout
            check_exact_output(mode, expected, first)
            check_exact_output(mode + ":repeat", expected, second)
    print("CONFDATA_OUTPUT_MODES=pass")
    print(f"CONFDATA_OUTPUT_MODE_CASES={len(MODE_EXPECTATIONS)}")
    return 0


def run_self_test() -> int:
    checks_run = 0
    if sorted(MODE_EXPECTATIONS) != ["auto.conf", "autoconf.h"]:
        raise AssertionError("mode expectation packet drifted")
    checks_run += 1

    check_exact_output("auto.conf", EXPECTED_AUTO_CONF, EXPECTED_AUTO_CONF)
    checks_run += 1

    check_exact_output("autoconf.h", EXPECTED_AUTOCONF_HEADER, EXPECTED_AUTOCONF_HEADER)
    checks_run += 1

    try:
        check_exact_output("auto.conf", EXPECTED_AUTO_CONF, EXPECTED_AUTO_CONF + "CONFIG_DEBUG=n\n", emit_diff=False)
    except SystemExit as exc:
        if exc.code != 1:
            raise
    else:
        raise AssertionError("diff failure path did not trip")
    checks_run += 1

    if checks_run != EXPECTED_SELF_TEST_CASE_COUNT:
        print("CONFDATA_OUTPUT_MODE_SELF_TEST=fail")
        print(f"CONFDATA_OUTPUT_MODE_SELF_TEST_CASE_COUNT_ACTUAL={checks_run}")
        print(f"CONFDATA_OUTPUT_MODE_SELF_TEST_CASE_COUNT_EXPECTED={EXPECTED_SELF_TEST_CASE_COUNT}")
        return 1
    print("CONFDATA_OUTPUT_MODE_SELF_TEST=pass")
    print(f"CONFDATA_OUTPUT_MODE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check confdata_bridge auto.conf and autoconf.h output modes.")
    parser.add_argument("--zig", help="Explicit zig executable path")
    parser.add_argument("--self-test", action="store_true", help="Run checker-internal assertions without compiling Zig.")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    return run_output_mode_checks(find_zig(args.zig))


if __name__ == "__main__":
    raise SystemExit(main())
