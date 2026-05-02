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
C_HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase6_base64_c_harness.c"
CASE_GENERATOR = ROOT / "zigux" / "tests" / "phase6_base64_c_casegen.zig"
GENERATED_INCLUDE = ROOT / "zigux" / "tests" / "fixtures" / "phase6_base64_c_generated_cases.inc"
ZIG_RUNNER = ROOT / "zigux" / "tests" / "phase6_base64_c_parity.zig"
EXPECTED_SORTED_LINES = sorted(
    [
        "dec\timap\t0\t3\tok\tok",
        "dec\tstd\t1\t3\tok\tok",
        "enc\tstd\t1\tTWFu\tok",
    ]
)


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

            const base64_module = b.createModule(.{{
                .root_source_file = .{{ .cwd_relative = "{ROOT / 'lib' / 'base64.zig'}" }},
                .target = target,
                .optimize = optimize,
            }});
            const root_module = b.createModule(.{{
                .root_source_file = .{{ .cwd_relative = "{ZIG_RUNNER}" }},
                .target = target,
                .optimize = optimize,
            }});
            root_module.addImport("base64", base64_module);

            const exe = b.addExecutable(.{{
                .name = "phase6-base64-c-parity",
                .root_module = root_module,
            }});
            const run = b.addRunArtifact(exe);
            const step = b.step("run", "Run Phase 6 base64 C parity spot check");
            step.dependOn(&run.step);
        }}
        """
    )


def sorted_lines(stdout: str) -> list[str]:
    return sorted(stdout.strip().splitlines())


def assert_equal(label: str, actual, expected) -> None:
    if actual != expected:
        raise SystemExit(f"phase6-base64-c-parity:self-test:{label}:expected={expected!r}:actual={actual!r}")


def expect_system_exit(label: str, callback, expected_message: str) -> None:
    try:
        callback()
    except SystemExit as exc:
        actual_message = str(exc)
        if actual_message != expected_message:
            raise SystemExit(
                f"phase6-base64-c-parity:self-test:{label}:expected={expected_message!r}:actual={actual_message!r}"
            ) from exc
        return
    raise SystemExit(
        f"phase6-base64-c-parity:self-test:{label}:missing_system_exit:{expected_message!r}"
    )


def validate_expected_surface(lines: list[str], label: str) -> None:
    if lines != EXPECTED_SORTED_LINES:
        raise SystemExit(
            f"phase6-base64-c-parity:{label}:unexpected_output:expected={EXPECTED_SORTED_LINES!r}:actual={lines!r}"
        )


def run_self_test() -> int:
    assert_equal("require_tool_env", require_tool("zig", "PHASE6_SELFTEST_TOOL"), "/tmp/zig-self-test")
    expect_system_exit(
        "missing_harness",
        lambda: validate_required_path(Path("/tmp/phase6-missing-harness.c"), "harness"),
        "missing harness: /tmp/phase6-missing-harness.c",
    )
    expect_system_exit(
        "missing_case_generator",
        lambda: validate_required_path(Path("/tmp/phase6-missing-casegen.zig"), "case generator"),
        "missing case generator: /tmp/phase6-missing-casegen.zig",
    )
    expect_system_exit(
        "missing_runner",
        lambda: validate_required_path(Path("/tmp/phase6-missing-runner.zig"), "runner"),
        "missing runner: /tmp/phase6-missing-runner.zig",
    )
    build_text = build_zig_build_text()
    assert_equal(
        "build_text",
        'root_module.addImport("base64", base64_module);' in build_text
        and str(ROOT / "lib" / "base64.zig") in build_text
        and str(ZIG_RUNNER) in build_text,
        True,
    )
    validate_expected_surface(
        sorted_lines("dec\tstd\t1\t3\tok\tok\nenc\tstd\t1\tTWFu\tok\ndec\timap\t0\t3\tok\tok\n"),
        "self-test-positive",
    )
    unexpected_lines = EXPECTED_SORTED_LINES + ["unexpected-extra\tstd\t1\tbogus\tok"]
    expect_system_exit(
        "unexpected_case",
        lambda: validate_expected_surface(unexpected_lines, "self-test-unexpected-case"),
        "phase6-base64-c-parity:self-test-unexpected-case:unexpected_output:"
        f"expected={EXPECTED_SORTED_LINES!r}:actual={unexpected_lines!r}",
    )

    print("PHASE6_BASE64_C_PARITY_SELF_TEST=pass")
    print("PHASE6_BASE64_C_PARITY_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded Phase 6 base64 C parity spot check.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in parity-script checks")
    args = parser.parse_args()

    if args.self_test:
        os.environ["PHASE6_SELFTEST_TOOL"] = "/tmp/zig-self-test"
        return run_self_test()

    zig = require_tool("zig", "ZIG")
    cc = require_tool("cc", "CC")

    validate_required_path(C_HARNESS, "harness")
    validate_required_path(CASE_GENERATOR, "case generator")
    validate_required_path(ZIG_RUNNER, "runner")

    out_dir = ROOT / ".zigux-cache" / "phase6-base64-c-parity"
    out_dir.mkdir(parents=True, exist_ok=True)
    c_bin = out_dir / "phase6_base64_c_harness"
    zig_build = out_dir / "build.zig"

    generated_cases = run_checked([zig, "run", str(CASE_GENERATOR)]).stdout
    GENERATED_INCLUDE.write_text(generated_cases, encoding="utf-8")

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
        print("PHASE6_BASE64_C_PARITY=fail")
        print("C_OUTPUT_START")
        print(c_run.stdout.rstrip())
        print("C_OUTPUT_END")
        print("ZIG_OUTPUT_START")
        print(zig_run.stdout.rstrip())
        print("ZIG_OUTPUT_END")
        return 1

    print("PHASE6_BASE64_C_PARITY=pass")
    print(f"PHASE6_BASE64_C_PARITY_CASES={len(c_lines)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
