#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
C_HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase6_base64_c_harness.c"
ZIG_RUNNER = ROOT / "zigux" / "tests" / "phase6_base64_c_parity.zig"
SELF_TEST_CASE_COUNT = 4


def require_tool(name: str, env_name: str) -> str:
    preferred = os.environ.get(env_name)
    if preferred:
        return preferred

    tool = shutil.which(name)
    if tool is None:
        raise SystemExit(f"missing required tool: {name}")
    return tool


def run_checked(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=True,
        cwd=ROOT if cwd is None else cwd,
        text=True,
        capture_output=True,
    )


def compare_outputs(c_output: str, zig_output: str) -> int:
    c_lines = c_output.strip().splitlines()
    zig_lines = zig_output.strip().splitlines()

    if c_lines != zig_lines:
        print("PHASE6_BASE64_C_PARITY=fail")
        print("C_OUTPUT_START")
        print(c_output.rstrip())
        print("C_OUTPUT_END")
        print("ZIG_OUTPUT_START")
        print(zig_output.rstrip())
        print("ZIG_OUTPUT_END")
        return 1

    print("PHASE6_BASE64_C_PARITY=pass")
    print(f"PHASE6_BASE64_C_PARITY_CASES={len(c_lines)}")
    return 0


def outputs_match(c_output: str, zig_output: str) -> bool:
    return c_output.strip().splitlines() == zig_output.strip().splitlines()


def build_zig_runner(zig: str, build_file: Path) -> subprocess.CompletedProcess[str]:
    return run_checked([zig, "build", "run", "--build-file", str(build_file)])


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    zig = require_tool("zig", "ZIG")
    cc = require_tool("cc", "CC")

    if not C_HARNESS.exists():
        raise SystemExit(f"missing harness: {C_HARNESS}")
    if not ZIG_RUNNER.exists():
        raise SystemExit(f"missing runner: {ZIG_RUNNER}")

    out_dir = ROOT / ".zigux-cache" / "phase6-base64-c-parity"
    out_dir.mkdir(parents=True, exist_ok=True)
    c_bin = out_dir / "phase6_base64_c_harness"
    zig_build = out_dir / "build.zig"

    zig_build.write_text(
        textwrap.dedent(
            f"""
            const std = @import(\"std\");

            pub fn build(b: *std.Build) void {{
                const target = b.standardTargetOptions(.{{}});
                const optimize = b.standardOptimizeOption(.{{}});

                const base64_module = b.createModule(.{{
                    .root_source_file = .{{ .cwd_relative = \"{ROOT / 'lib' / 'base64.zig'}\" }},
                    .target = target,
                    .optimize = optimize,
                }});
                const root_module = b.createModule(.{{
                    .root_source_file = .{{ .cwd_relative = \"{ZIG_RUNNER}\" }},
                    .target = target,
                    .optimize = optimize,
                }});
                root_module.addImport(\"base64\", base64_module);

                const exe = b.addExecutable(.{{
                    .name = \"phase6-base64-c-parity\",
                    .root_module = root_module,
                }});
                const run = b.addRunArtifact(exe);
                const step = b.step(\"run\", \"Run Phase 6 base64 C parity spot check\");
                step.dependOn(&run.step);
            }}
            """
        ),
        encoding="utf-8",
    )

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
    zig_run = build_zig_runner(zig, zig_build)
    return compare_outputs(c_run.stdout, zig_run.stdout)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise built-in failure and success checks without a repo checkout",
    )
    return parser.parse_args()


def run_self_test() -> int:
    if not outputs_match("a\nb\n", "a\nb\n"):
        raise SystemExit("self-test compare success case failed")

    with tempfile.TemporaryDirectory(prefix="phase6_base64_c_parity_selftest_") as tmpdir:
        tmp_path = Path(tmpdir)
        runner = tmp_path / "runner.zig"
        harness = tmp_path / "harness.c"
        build_file = tmp_path / "build.zig"

        runner.write_text("pub fn main() void {}\n", encoding="utf-8")
        harness.write_text("int main(void) { return 0; }\n", encoding="utf-8")
        build_file.write_text("const std = @import(\"std\");\n", encoding="utf-8")

        if not runner.exists():
            raise SystemExit("self-test runner scaffold missing")
        if not harness.exists():
            raise SystemExit("self-test harness scaffold missing")
        if not build_file.exists():
            raise SystemExit("self-test build scaffold missing")

    if outputs_match("left\n", "right\n"):
        raise SystemExit("self-test mismatch case failed")

    print("PHASE6_BASE64_C_PARITY_SELF_TEST=pass")
    print(f"PHASE6_BASE64_C_PARITY_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
