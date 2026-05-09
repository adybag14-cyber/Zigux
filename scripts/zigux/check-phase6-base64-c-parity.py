#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
C_HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase6_base64_c_harness.c"
HELPER_SOURCE = ROOT / "lib" / "base64.zig"
FIXTURE_SOURCE = ROOT / "zigux" / "tests" / "fixtures" / "phase6_base64_vectors.zig"
ZIG_RUNNER = ROOT / "zigux" / "tests" / "phase6_base64_c_parity.zig"
EXPECTED_SORTED_LINES = sorted(
    [
        "encode\tstd-pad-f\tZg==",
        "encode\tstd-no-pad-fo\tZm8",
        "encode\tstd-pad-hello\tSGVsbG8sIHdvcmxkIQ==",
        "encode\turlsafe-pad-variant\tAPv_f4A=",
        "encode\timap-no-pad-variant\tAPv,f4A",
        "chars\tstd-pad-f\t4",
        "chars\tstd-no-pad-fo\t3",
        "chars\tstd-pad-hello\t20",
        "chars\turlsafe-pad-variant\t8",
        "chars\timap-no-pad-variant\t7",
        "decode\tstd-pad-foobar\t666f6f626172",
        "decode\tstd-no-pad-hello\t48656c6c6f2c20776f726c6421",
        "decode\turlsafe-pad-variant\t00fbff7f80",
        "decode\timap-no-pad-variant\t00fbff7f80",
        "bytes\tstd-pad-foobar\t6",
        "bytes\tstd-no-pad-hello\t13",
        "bytes\turlsafe-pad-variant\t5",
        "bytes\timap-no-pad-variant\t5",
        "invalid\tstd-pad-noncanonical-pair\treject",
        "invalid\turlsafe-pad-noncanonical-pair\treject",
        "invalid\timap-pad-noncanonical-triple\treject",
        "invalid\tstd-no-pad-noncanonical-pair\treject",
        "invalid\tstd-no-pad-noncanonical-triple\treject",
        "invalid\timap-no-pad-padding-reject\treject",
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
        const std = @import(\"std\");

        pub fn build(b: *std.Build) void {{
            const target = b.standardTargetOptions(.{{}});
            const optimize = b.standardOptimizeOption(.{{}});

            const helper_module = b.createModule(.{{
                .root_source_file = .{{ .cwd_relative = \"{HELPER_SOURCE}\" }},
                .target = target,
                .optimize = optimize,
            }});
            const fixture_module = b.createModule(.{{
                .root_source_file = .{{ .cwd_relative = \"{FIXTURE_SOURCE}\" }},
                .target = target,
                .optimize = optimize,
            }});
            const root_module = b.createModule(.{{
                .root_source_file = .{{ .cwd_relative = \"{ZIG_RUNNER}\" }},
                .target = target,
                .optimize = optimize,
            }});
            root_module.addImport(\"base64\", helper_module);
            root_module.addImport(\"phase6_base64_vectors\", fixture_module);

            const exe = b.addExecutable(.{{
                .name = \"phase6-base64-c-parity\",
                .root_module = root_module,
            }});
            const run = b.addRunArtifact(exe);
            const step = b.step(\"run\", \"Run Phase 6 base64 C parity spot check\");
            step.dependOn(&run.step);
        }}
        """
    )


def sorted_lines(stdout: str) -> list[str]:
    return sorted(line for line in stdout.strip().splitlines() if line)


def validate_expected_surface(lines: list[str], label: str) -> None:
    if lines != EXPECTED_SORTED_LINES:
        raise SystemExit(
            f"phase6-base64-c-parity:{label}:unexpected_output:"
            f"expected={EXPECTED_SORTED_LINES!r}:actual={lines!r}"
        )


def validate_matching_surface(c_lines: list[str], zig_lines: list[str], label: str) -> None:
    if c_lines != zig_lines:
        raise SystemExit(
            f"phase6-base64-c-parity:{label}:c_output_mismatch:"
            f"expected={c_lines!r}:actual={zig_lines!r}"
        )


def run_self_test() -> int:
    os.environ["PHASE6_SELFTEST_TOOL"] = "/tmp/zig-self-test"
    if require_tool("zig", "PHASE6_SELFTEST_TOOL") != "/tmp/zig-self-test":
        raise SystemExit("phase6-base64-c-parity:self-test:require_tool_failed")
    validate_expected_surface(EXPECTED_SORTED_LINES, "self-test-positive")
    try:
        validate_expected_surface(EXPECTED_SORTED_LINES[:-1], "self-test-missing-case")
    except SystemExit as exc:
        if "unexpected_output" not in str(exc):
            raise
    else:
        raise SystemExit("phase6-base64-c-parity:self-test:missing_failure")

    print("PHASE6_BASE64_C_PARITY_SELF_TEST=pass")
    print("PHASE6_BASE64_C_PARITY_SELF_TEST_CASE_COUNT=3")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded Phase 6 base64 C parity spot check.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in parity-script checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    zig = require_tool("zig", "ZIG")
    cc = require_tool("cc", "CC")

    validate_required_path(C_HARNESS, "harness")
    validate_required_path(HELPER_SOURCE, "helper source")
    validate_required_path(FIXTURE_SOURCE, "fixture source")
    validate_required_path(ZIG_RUNNER, "runner")

    out_dir = ROOT / ".zigux-cache" / "phase6-base64-c-parity"
    out_dir.mkdir(parents=True, exist_ok=True)
    c_bin = out_dir / "phase6_base64_c_harness"
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
    validate_expected_surface(c_lines, "c")
    validate_expected_surface(zig_lines, "zig")
    validate_matching_surface(c_lines, zig_lines, "c-vs-zig")

    print("PHASE6_BASE64_C_PARITY=pass")
    print(f"PHASE6_BASE64_C_PARITY_CASES={len(c_lines)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
