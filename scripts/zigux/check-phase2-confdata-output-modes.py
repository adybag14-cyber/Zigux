#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CONFDATA_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"

INLINE_CONFIG = """CONFIG_ALPHA=y
CONFIG_BETA=m
CONFIG_COUNT=7
CONFIG_NAME=\"zigux\\\"bridge\\\\\"
CONFIG_EMPTY=
CONFIG_EXPLICIT_N=n
# CONFIG_DEBUG is not set
"""

EXPECTED_OUTPUTS = {
    "json": "{\"counts\":{\"set\":6,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"tristate\",\"value\":\"m\"},{\"name\":\"CONFIG_COUNT\",\"kind\":\"value\",\"value\":\"7\"},{\"name\":\"CONFIG_NAME\",\"kind\":\"string\",\"value\":\"zigux\\\"bridge\\\\\"},{\"name\":\"CONFIG_EMPTY\",\"kind\":\"value\",\"value\":\"\"},{\"name\":\"CONFIG_EXPLICIT_N\",\"kind\":\"tristate\",\"value\":\"n\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"}]}\n",
    "auto.conf": "CONFIG_ALPHA=y\nCONFIG_BETA=m\nCONFIG_COUNT=7\nCONFIG_NAME=\"zigux\\\"bridge\\\\\"\nCONFIG_EMPTY=\nCONFIG_EXPLICIT_N=n\n",
    "autoconf.h": "#define CONFIG_ALPHA 1\n#define CONFIG_BETA_MODULE 1\n#define CONFIG_COUNT 7\n#define CONFIG_NAME \"zigux\\\"bridge\\\\\"\n#define CONFIG_EMPTY \n",
}

EXPECTED_SELF_TEST_CASE_COUNT = 5


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    found = shutil.which("zig")
    if found:
        return found
    raise SystemExit("zig not found; pass --zig or add zig to PATH")


def compile_bridge(zig: str, output: Path) -> None:
    run([zig, "build-exe", str(CONFDATA_BRIDGE), "-femit-bin=" + str(output)], cwd=str(ROOT))


def bridge_command(exe: Path, mode: str, config: Path) -> list[str]:
    if mode == "json":
        return [str(exe), str(config)]
    return [str(exe), mode, str(config)]


def check_mode_output(mode: str, expected: str, actual: str, repeat: str, *, emit: bool = True) -> None:
    if actual != expected:
        if emit:
            print("PHASE2_CONFDATA_OUTPUT_MODE_GATE=fail")
            print(f"CONFDATA_OUTPUT_MODE_EXPECTED_MISMATCH={mode}")
        raise SystemExit(1)
    if repeat != actual:
        if emit:
            print("PHASE2_CONFDATA_OUTPUT_MODE_GATE=fail")
            print(f"CONFDATA_OUTPUT_MODE_REPEAT_MISMATCH={mode}")
        raise SystemExit(1)


def run_gate(zig: str) -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_confdata_output_modes_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        exe = tmp_dir / ("confdata-bridge.exe" if sys.platform == "win32" else "confdata-bridge")
        config = tmp_dir / "inline.config"
        config.write_text(INLINE_CONFIG, encoding="utf-8", newline="\n")
        compile_bridge(zig, exe)
        for mode, expected in EXPECTED_OUTPUTS.items():
            cmd = bridge_command(exe, mode, config)
            actual = run(cmd, cwd=str(ROOT), capture_output=True).stdout
            repeat = run(cmd, cwd=str(ROOT), capture_output=True).stdout
            check_mode_output(mode, expected, actual, repeat)
    print("PHASE2_CONFDATA_OUTPUT_MODE_GATE=pass")
    print(f"PHASE2_CONFDATA_OUTPUT_MODE_COUNT={len(EXPECTED_OUTPUTS)}")
    return 0


def run_self_test() -> int:
    checks = 0
    assert bridge_command(Path("bridge"), "json", Path("input.config")) == ["bridge", "input.config"]
    checks += 1
    assert bridge_command(Path("bridge"), "auto.conf", Path("input.config")) == ["bridge", "auto.conf", "input.config"]
    checks += 1
    assert set(EXPECTED_OUTPUTS) == {"json", "auto.conf", "autoconf.h"}
    checks += 1
    check_mode_output("json", EXPECTED_OUTPUTS["json"], EXPECTED_OUTPUTS["json"], EXPECTED_OUTPUTS["json"])
    checks += 1
    try:
        check_mode_output("auto.conf", "expected", "actual", "actual", emit=False)
    except SystemExit as exc:
        assert exc.code == 1
        checks += 1
    else:
        raise AssertionError("expected output mismatch did not fail")

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CONFDATA_OUTPUT_MODE_SELF_TEST=pass")
    print(f"PHASE2_CONFDATA_OUTPUT_MODE_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check deterministic confdata_bridge output modes.")
    parser.add_argument("--zig", help="Explicit zig executable path")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    return run_gate(find_zig(args.zig))


if __name__ == "__main__":
    raise SystemExit(main())
