#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
C_HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase6_bsearch_c_harness.c"
ZIG_RUNNER = ROOT / "zigux" / "tests" / "phase6_bsearch_c_parity.zig"


def require_tool(name: str, env_name: str) -> str:
    preferred = os.environ.get(env_name)
    if preferred:
        return preferred

    tool = shutil.which(name)
    if tool is None:
        raise SystemExit(f"missing required tool: {name}")
    return tool


def run_checked(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def main() -> int:
    zig = require_tool("zig", "ZIG")
    cc = require_tool("cc", "CC")

    if not C_HARNESS.exists():
        raise SystemExit(f"missing harness: {C_HARNESS}")
    if not ZIG_RUNNER.exists():
        raise SystemExit(f"missing runner: {ZIG_RUNNER}")

    out_dir = ROOT / ".zigux-cache" / "phase6-bsearch-c-parity"
    out_dir.mkdir(parents=True, exist_ok=True)
    c_bin = out_dir / "phase6_bsearch_c_harness"
    zig_build = out_dir / "build.zig"

    zig_build.write_text(
        textwrap.dedent(
            f"""
            const std = @import("std");

            pub fn build(b: *std.Build) void {{
                const target = b.standardTargetOptions(.{{}});
                const optimize = b.standardOptimizeOption(.{{}});

                const bsearch_module = b.createModule(.{{
                    .root_source_file = .{{ .cwd_relative = "{ROOT / 'lib' / 'bsearch.zig'}" }},
                    .target = target,
                    .optimize = optimize,
                }});
                const root_module = b.createModule(.{{
                    .root_source_file = .{{ .cwd_relative = "{ZIG_RUNNER}" }},
                    .target = target,
                    .optimize = optimize,
                }});
                root_module.addImport("bsearch", bsearch_module);

                const exe = b.addExecutable(.{{
                    .name = "phase6-bsearch-c-parity",
                    .root_module = root_module,
                }});
                const run = b.addRunArtifact(exe);
                const step = b.step("run", "Run Phase 6 bsearch C parity spot check");
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
    zig_run = run_checked([zig, "build", "run", "--build-file", str(zig_build)])

    c_lines = sorted(c_run.stdout.strip().splitlines())
    zig_lines = sorted(zig_run.stdout.strip().splitlines())

    if c_lines != zig_lines:
        print("PHASE6_BSEARCH_C_PARITY=fail")
        print("C_OUTPUT_START")
        print(c_run.stdout.rstrip())
        print("C_OUTPUT_END")
        print("ZIG_OUTPUT_START")
        print(zig_run.stdout.rstrip())
        print("ZIG_OUTPUT_END")
        return 1

    print("PHASE6_BSEARCH_C_PARITY=pass")
    print(f"PHASE6_BSEARCH_C_PARITY_CASES={len(c_lines)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
