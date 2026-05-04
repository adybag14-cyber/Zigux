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
HELPER_SOURCE = ROOT / "lib" / "bsearch.zig"
ZIG_RUNNER = ROOT / "zigux" / "tests" / "phase6_bsearch_c_parity.zig"
EXPECTED_SORTED_LINES = sorted(
    [
        "u32-hit\t3\t0",
        "u32-hit\t21\t3",
        "u32-hit\t89\t6",
        "u32-miss\t0\tnull",
        "u32-miss\t15\tnull",
        "u32-miss\t90\tnull",
        "singleton-hit\t21\t0",
        "singleton-miss\t20\tnull",
        "empty-miss\t21\tnull",
        "descending-hit\t34\t2",
        "descending-miss\t20\tnull",
        "duplicate-hit-begin\t7\tfound",
        "duplicate-hit-middle\t7\tfound",
        "duplicate-hit-end\t18\tfound",
        "raw-hit\t34\t4",
        "raw-miss\t20\tnull",
        "raw-descending-hit\t34\t2",
        "runtime-typed-hit\t55\t5",
        "runtime-typed-hit\t34\t2",
        "runtime-typed-miss-ascending\t20\tnull",
        "runtime-typed-miss-descending\t20\tnull",
        "runtime-raw-hit\t55\t5",
        "runtime-raw-hit\t34\t2",
        "runtime-raw-miss-ascending\t20\tnull",
        "runtime-raw-miss-descending\t20\tnull",
        "sym-hit\tkmalloc\t0x1400",
        "sym-miss\tvfree\tnull",
        "mutable-hit\t34\t35",
        "raw-mutable-hit\t34\t35",
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

            const bsearch_module = b.createModule(.{{
                .root_source_file = .{{ .cwd_relative = \"{HELPER_SOURCE}\" }},
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


def assert_equal(label: str, actual, expected) -> None:
    if actual != expected:
        raise SystemExit(f"phase6-bsearch-c-parity:self-test:{label}:expected={expected!r}:actual={actual!r}")


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


def validate_expected_surface(lines: list[str], label: str) -> None:
    if lines != EXPECTED_SORTED_LINES:
        raise SystemExit(
            f"phase6-bsearch-c-parity:{label}:unexpected_output:expected={EXPECTED_SORTED_LINES!r}:actual={lines!r}"
        )


def validate_matching_surface(c_lines: list[str], zig_lines: list[str], label: str) -> None:
    if c_lines != zig_lines:
        raise SystemExit(
            f"phase6-bsearch-c-parity:{label}:c_output_mismatch:expected={c_lines!r}:actual={zig_lines!r}"
        )


def collect_failures(c_lines: list[str], zig_lines: list[str]) -> list[str]:
    failures: list[str] = []
    for label, lines in (("c", c_lines), ("zig", zig_lines)):
        try:
            validate_expected_surface(lines, label)
        except SystemExit as exc:
            failures.append(str(exc))
    try:
        validate_matching_surface(c_lines, zig_lines, "c-vs-zig")
    except SystemExit as exc:
        failures.append(str(exc))
    return failures


def run_self_test() -> int:
    assert_equal("require_tool_env", require_tool("zig", "PHASE6_SELFTEST_TOOL"), "/tmp/zig-self-test")
    expect_system_exit(
        "missing_harness",
        lambda: validate_required_path(Path("/tmp/phase6-missing-harness.c"), "harness"),
        "missing harness: /tmp/phase6-missing-harness.c",
    )
    expect_system_exit(
        "missing_helper_source",
        lambda: validate_required_path(Path("/tmp/phase6-missing-bsearch.zig"), "helper source"),
        "missing helper source: /tmp/phase6-missing-bsearch.zig",
    )
    expect_system_exit(
        "missing_runner",
        lambda: validate_required_path(Path("/tmp/phase6-missing-runner.zig"), "runner"),
        "missing runner: /tmp/phase6-missing-runner.zig",
    )
    build_text = build_zig_build_text()
    descending_runtime_lines = {
        "descending-hit\t34\t2",
        "descending-miss\t20\tnull",
        "runtime-typed-hit\t34\t2",
        "runtime-typed-miss-descending\t20\tnull",
        "runtime-raw-hit\t34\t2",
        "runtime-raw-miss-descending\t20\tnull",
    }
    aggregate_failures = collect_failures(
        ["u32-hit\t3\t0", "runtime-raw-hit\t34\tnull"],
        ["u32-hit\t3\t0", "runtime-raw-hit\t34\t2", "unexpected-extra\t999\tnull"],
    )
    assert_equal(
        "build_text_paths_and_failure_aggregation",
        'root_module.addImport("bsearch", bsearch_module);' in build_text
        and str(HELPER_SOURCE) in build_text
        and str(ZIG_RUNNER) in build_text
        and len(EXPECTED_SORTED_LINES) == 29
        and descending_runtime_lines.issubset(EXPECTED_SORTED_LINES)
        and sorted_lines("mutable-hit\t34\t35\nascending-hit\t34\t4\n") == ["ascending-hit\t34\t4", "mutable-hit\t34\t35"]
        and len(aggregate_failures) == 3
        and aggregate_failures[0].startswith("phase6-bsearch-c-parity:c:unexpected_output:")
        and aggregate_failures[1].startswith("phase6-bsearch-c-parity:zig:unexpected_output:")
        and aggregate_failures[2]
        == "phase6-bsearch-c-parity:c-vs-zig:c_output_mismatch:"
        "expected=['u32-hit\\t3\\t0', 'runtime-raw-hit\\t34\\tnull']:"
        "actual=['u32-hit\\t3\\t0', 'runtime-raw-hit\\t34\\t2', 'unexpected-extra\\t999\\tnull']",
        True,
    )

    validate_expected_surface(EXPECTED_SORTED_LINES, "self-test-positive")
    unexpected_lines = EXPECTED_SORTED_LINES + ["unexpected-extra\t999\tnull"]
    expect_system_exit(
        "unexpected_case",
        lambda: validate_expected_surface(unexpected_lines, "self-test-unexpected-case"),
        "phase6-bsearch-c-parity:self-test-unexpected-case:unexpected_output:"
        f"expected={EXPECTED_SORTED_LINES!r}:actual={unexpected_lines!r}",
    )
    missing_runtime_raw_descending = [
        line for line in EXPECTED_SORTED_LINES if line != "runtime-raw-miss-descending\t20\tnull"
    ]
    expect_system_exit(
        "missing_case",
        lambda: validate_expected_surface(missing_runtime_raw_descending, "self-test-missing-case"),
        "phase6-bsearch-c-parity:self-test-missing-case:unexpected_output:"
        f"expected={EXPECTED_SORTED_LINES!r}:actual={missing_runtime_raw_descending!r}",
    )
    expect_system_exit(
        "mismatch_surface",
        lambda: validate_matching_surface(
            ["u32-hit\t3\t0", "runtime-raw-hit\t34\t2"],
            ["u32-hit\t3\t0", "runtime-raw-hit\t34\tnull"],
            "self-test-mismatch",
        ),
        "phase6-bsearch-c-parity:self-test-mismatch:c_output_mismatch:"
        "expected=['u32-hit\\t3\\t0', 'runtime-raw-hit\\t34\\t2']:"
        "actual=['u32-hit\\t3\\t0', 'runtime-raw-hit\\t34\\tnull']",
    )
    print("PHASE6_BSEARCH_C_PARITY_SELF_TEST=pass")
    print("PHASE6_BSEARCH_C_PARITY_SELF_TEST_CASE_COUNT=7")
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
    validate_required_path(HELPER_SOURCE, "helper source")
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
    failures = collect_failures(c_lines, zig_lines)

    if failures:
        print("PHASE6_BSEARCH_C_PARITY=fail")
        for failure in failures:
            print(failure)
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
