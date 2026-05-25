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
C_HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase6_bsearch_c_harness.c"
ZIG_RUNNER = ROOT / "zigux" / "tests" / "phase6_bsearch_c_parity.zig"
EXPECTED_CASE_COUNT = 17
REQUIRED_OUTPUT_LINES = (
    "descending-hit\t34\t2",
    "descending-miss\t20\tnull",
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

            const bsearch_module = b.createModule(.{{
                .root_source_file = .{{ .cwd_relative = \"{ROOT / 'lib' / 'bsearch.zig'}\" }},
                .target = target,
                .optimize = optimize,
            }});
            const root_module = b.createModule(.{{
                .root_source_file = .{{ .cwd_relative = \"{ZIG_RUNNER}\" }},
                .target = target,
                .optimize = optimize,
            }});
            root_module.addImport(\"bsearch\", bsearch_module);

            const exe = b.addExecutable(.{{
                .name = \"phase6-bsearch-c-parity\",
                .root_module = root_module,
            }});
            const run = b.addRunArtifact(exe);
            const step = b.step(\"run\", \"Run Phase 6 bsearch C parity spot check\");
            step.dependOn(&run.step);
        }}
        """
    )


def sorted_lines(stdout: str) -> list[str]:
    return sorted(stdout.strip().splitlines())


def require_expected_output(lines: list[str]) -> None:
    if len(lines) != EXPECTED_CASE_COUNT:
        raise SystemExit(
            f"phase6-bsearch-c-parity:expected_case_count:expected={EXPECTED_CASE_COUNT}:actual={len(lines)}"
        )
    for marker in REQUIRED_OUTPUT_LINES:
        if marker not in lines:
            raise SystemExit(f"phase6-bsearch-c-parity:missing_output_line:{marker}")


def assert_equal(label: str, actual, expected) -> None:
    if actual != expected:
        raise SystemExit(
            f"phase6-bsearch-c-parity:self-test:{label}:expected={expected!r}:actual={actual!r}"
        )


def expect_system_exit(label: str, callback, expected_message: str) -> None:
    try:
        callback()
    except SystemExit as exc:
        actual_message = str(exc)
        if actual_message != expected_message:
            raise SystemExit(
                f"phase6-bsearch-c-parity:self-test:{label}:expected={expected_message!r}:actual={actual_message!r}"
            ) from exc
        return
    raise SystemExit(
        f"phase6-bsearch-c-parity:self-test:{label}:missing_system_exit:{expected_message!r}"
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
        'root_module.addImport("bsearch", bsearch_module);' in build_text,
        True,
    )
    assert_equal("build_text_runner", str(ZIG_RUNNER) in build_text, True)
    assert_equal(
        "sorted_lines",
        sorted_lines("u32-hit\t21\t3\nu32-hit\t3\t0\n"),
        ["u32-hit\t21\t3", "u32-hit\t3\t0"],
    )

    expected_lines = [
        "descending-hit\t34\t2",
        "descending-miss\t20\tnull",
        "duplicate-hit-begin\t7\tfound",
        "duplicate-hit-end\t18\tfound",
        "duplicate-hit-middle\t7\tfound",
        "empty-miss\t21\tnull",
        "mutable-hit\t21\t22",
        "singleton-hit\t21\t0",
        "singleton-miss\t20\tnull",
        "sym-hit\tkmalloc\t0x1400",
        "sym-miss\tvfree\tnull",
        "u32-hit\t21\t3",
        "u32-hit\t3\t0",
        "u32-hit\t89\t6",
        "u32-miss\t0\tnull",
        "u32-miss\t15\tnull",
        "u32-miss\t90\tnull",
    ]
    require_expected_output(expected_lines)
    expect_system_exit(
        "missing_descending_marker",
        lambda: require_expected_output(expected_lines[1:]),
        "phase6-bsearch-c-parity:expected_case_count:expected=17:actual=16",
    )
    expect_system_exit(
        "wrong_case_count",
        lambda: require_expected_output(expected_lines + ["extra\tcase\t0"]),
        "phase6-bsearch-c-parity:expected_case_count:expected=17:actual=18",
    )

    print("PHASE6_BSEARCH_C_PARITY_SELF_TEST=pass")
    print("PHASE6_BSEARCH_C_PARITY_SELF_TEST_CASE_COUNT=9")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded Phase 6 bsearch C parity spot check.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in parity-script checks")
    args = parser.parse_args()

    if args.self_test:
        os.environ["PHASE6_SELFTEST_TOOL"] = "/tmp/zig-self-test"
        return run_self_test()

    zig = require_tool("zig", "ZIG")
    cc = require_tool("cc", "CC")

    validate_required_path(C_HARNESS, "harness")
    validate_required_path(ZIG_RUNNER, "runner")

    out_dir = ROOT / ".zigux-cache" / "phase6-bsearch-c-parity"
    out_dir.mkdir(parents=True, exist_ok=True)
    c_bin = out_dir / "phase6_bsearch_c_harness"
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

    require_expected_output(c_lines)
    require_expected_output(zig_lines)

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
