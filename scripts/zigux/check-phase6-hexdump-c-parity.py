#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
C_HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase6_hexdump_c_harness.c"
ZIG_RUNNER = ROOT / "zigux" / "tests" / "phase6_hexdump_c_parity.zig"
ZIG_HELPER = ROOT / "lib" / "hexdump.zig"


def require_tool(name: str, env_name: str) -> str:
    preferred = os.environ.get(env_name)
    if preferred:
        return preferred

    tool = shutil.which(name)
    if tool is None:
        raise SystemExit(f"missing required tool: {name}")
    return tool


def validate_required_path(path: Path, label: str) -> None:
    if not path.exists():
        raise SystemExit(f"missing {label}: {path}")


def run_checked(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def build_zig_build_text() -> str:
    return textwrap.dedent(
        f"""
        const std = @import("std");

        pub fn build(b: *std.Build) void {{
            const target = b.standardTargetOptions(.{{}});
            const optimize = b.standardOptimizeOption(.{{}});

            const hexdump_module = b.createModule(.{{
                .root_source_file = .{{ .cwd_relative = "{ZIG_HELPER}" }},
                .target = target,
                .optimize = optimize,
            }});
            const root_module = b.createModule(.{{
                .root_source_file = .{{ .cwd_relative = "{ZIG_RUNNER}" }},
                .target = target,
                .optimize = optimize,
            }});
            root_module.addImport("hexdump", hexdump_module);

            const exe = b.addExecutable(.{{
                .name = "phase6-hexdump-c-parity",
                .root_module = root_module,
            }});
            const run = b.addRunArtifact(exe);
            const step = b.step("run", "Run Phase 6 hexdump C parity spot check");
            step.dependOn(&run.step);
        }}
        """
    )


def sorted_lines(stdout: str) -> list[str]:
    return sorted(line for line in stdout.strip().splitlines() if line)


def assert_equal(label: str, actual, expected) -> None:
    if actual != expected:
        raise SystemExit(
            f"phase6-hexdump-c-parity:self-test:{label}:expected={expected!r}:actual={actual!r}"
        )


def expect_system_exit(label: str, callback, expected_message: str) -> None:
    try:
        callback()
    except SystemExit as exc:
        actual_message = str(exc)
        if actual_message != expected_message:
            raise SystemExit(
                f"phase6-hexdump-c-parity:self-test:{label}:expected={expected_message!r}:actual={actual_message!r}"
            ) from exc
        return
    raise SystemExit(
        f"phase6-hexdump-c-parity:self-test:{label}:missing_system_exit:{expected_message!r}"
    )


def run_self_test() -> int:
    assert_equal("require_tool_env", require_tool("zig", "PHASE6_SELFTEST_TOOL"), "/tmp/zig-self-test")
    expect_system_exit(
        "missing_harness",
        lambda: validate_required_path(Path("/tmp/phase6-missing-harness.c"), "harness"),
        "missing harness: /tmp/phase6-missing-harness.c",
    )
    expect_system_exit(
        "missing_runner",
        lambda: validate_required_path(Path("/tmp/phase6-missing-runner.zig"), "runner"),
        "missing runner: /tmp/phase6-missing-runner.zig",
    )
    build_text = build_zig_build_text()
    assert_equal(
        "build_text_import",
        'root_module.addImport("hexdump", hexdump_module);' in build_text,
        True,
    )
    assert_equal("build_text_runner", str(ZIG_RUNNER) in build_text, True)
    assert_equal(
        "sorted_lines",
        sorted_lines("dump\tplain\t47\tabc\nhex-to-bin\tzero\t0\n"),
        ["dump\tplain\t47\tabc", "hex-to-bin\tzero\t0"],
    )

    print("PHASE6_HEXDUMP_C_PARITY_SELF_TEST=pass")
    print("PHASE6_HEXDUMP_C_PARITY_SELF_TEST_CASE_COUNT=6")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded Phase 6 hexdump C parity spot check.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in parity-script checks")
    args = parser.parse_args()

    if args.self_test:
        os.environ["PHASE6_SELFTEST_TOOL"] = "/tmp/zig-self-test"
        return run_self_test()

    zig = require_tool("zig", "ZIG")
    cc = require_tool("cc", "CC")

    validate_required_path(C_HARNESS, "harness")
    validate_required_path(ZIG_RUNNER, "runner")
    validate_required_path(ZIG_HELPER, "hexdump helper")

    out_dir = ROOT / ".zigux-cache" / "phase6-hexdump-c-parity"
    out_dir.mkdir(parents=True, exist_ok=True)
    c_bin = out_dir / "phase6_hexdump_c_harness"
    zig_build = out_dir / "build.zig"

    zig_build.write_text(build_zig_build_text(), encoding="utf-8")

    run_checked(
        [
            cc,
            "-std=c99",
            "-O2",
            "-Wall",
            "-Wextra",
            "-pedantic",
            "-o",
            str(c_bin),
            str(C_HARNESS),
        ]
    )

    c_run = run_checked([str(c_bin)])
    zig_run = run_checked([zig, "build", "run", "--build-file", str(zig_build)])

    c_lines = sorted_lines(c_run.stdout)
    zig_lines = sorted_lines(zig_run.stdout)

    if c_lines != zig_lines:
        print("PHASE6_HEXDUMP_C_PARITY=fail")
        print("C_OUTPUT_START")
        print(c_run.stdout.rstrip())
        print("C_OUTPUT_END")
        print("ZIG_OUTPUT_START")
        print(zig_run.stdout.rstrip())
        print("ZIG_OUTPUT_END")
        return 1

    print("PHASE6_HEXDUMP_C_PARITY=pass")
    print(f"PHASE6_HEXDUMP_C_PARITY_CASES={len(c_lines)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
