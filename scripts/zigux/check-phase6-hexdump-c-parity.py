#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path


def derive_root(script_path: Path) -> Path:
    resolved = script_path.resolve()
    return resolved.parents[2] if len(resolved.parents) > 2 else resolved.parent


SCRIPT_PATH = Path(__file__).resolve()
ROOT = derive_root(SCRIPT_PATH)
C_HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase6_hexdump_c_harness.c"
HELPER_SOURCE = ROOT / "lib" / "hexdump.zig"
FIXTURE_SOURCE = ROOT / "zigux" / "tests" / "fixtures" / "phase6_hexdump_vectors.zig"
ZIG_RUNNER = ROOT / "zigux" / "tests" / "phase6_hexdump_c_parity.zig"
EXPECTED_SORTED_LINES = sorted(
    [
        "bin2hex\tlower\tbe32db7b",
        "bin2hex\tupper\tBE32DB7B",
        "bin2hex\tappend-mixed\tbe32DB7B",
        "dump\tascii rowsize-16 group-1\t65\tbe 32 db 7b 0a 18 93 b2 70 ba c4 24 7d 83 34 9b  .2.{....p..$}.4.",
        "dump\tascii rowsize-16 group-2\t57\t32be 7bdb 180a b293 ba70 24c4 837d 9b34  .2.{....p..$}.4.",
        "dump\tascii rowsize-16 group-4\t53\t7bdb32be b293180a 24c4ba70 9b34837d  .2.{....p..$}.4.",
        "dump\tascii rowsize-16 group-8\t51\tb293180a7bdb32be 9b34837d24c4ba70  .2.{....p..$}.4.",
        "dump\tascii rowsize-32 group-2\t113\t32be 7bdb 180a b293 ba70 24c4 837d 9b34 9ca6 ad31 0f9c e9ac d14c 9919 b143 0caf  .2.{....p..$}.4...1.....L...C...",
        "dump\tnormalized rowsize and groupsize fallback\t61\tbe 32 db 7b 0a 18 93 b2 70 ba c4 24              .2.{....p..$",
        "dump\tplain rowsize-16 group-1\t47\tbe 32 db 7b 0a 18 93 b2 70 ba c4 24 7d 83 34 9b",
        "dump\tplain rowsize-16 group-2\t39\t32be 7bdb 180a b293 ba70 24c4 837d 9b34",
        "dump\tplain rowsize-16 group-4\t35\t7bdb32be b293180a 24c4ba70 9b34837d",
        "dump\tplain rowsize-16 group-8\t33\tb293180a7bdb32be 9b34837d24c4ba70",
        "hex2bin\tmixed-case\tbe32db7b",
        "hexToBin\t0\t0",
        "hexToBin\t9\t9",
        "hexToBin\tA\t10",
        "hexToBin\tF\t15",
        "hexToBin\ta\t10",
        "hexToBin\tf\t15",
        "hexToBin\tg\t-1",
        "length\tascii rowsize-16 group-1\t65",
        "length\tascii rowsize-16 group-4\t53",
        "length\tnormalized rowsize and groupsize fallback\t65",
        "length\tplain rowsize-16 group-8\t33",
        "overflow\tgrouped plain buffer truncates deterministically\t39\t32be 7bdb 180a b293",
        "overflow\tnormalized ascii buffer truncates after fallback formatting\t64\tbe 32 db 7b",
        "overflow\tshort ascii buffer truncates but stays NUL terminated\t53\tbe 32 d",
        "overflow\tzero-sized caller buffer reports required ascii length\t65\t",
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

            const hexdump_module = b.createModule(.{{
                .root_source_file = .{{ .cwd_relative = \"{HELPER_SOURCE}\" }},
                .target = target,
                .optimize = optimize,
            }});
            const fixtures_module = b.createModule(.{{
                .root_source_file = .{{ .cwd_relative = \"{FIXTURE_SOURCE}\" }},
                .target = target,
                .optimize = optimize,
            }});
            const root_module = b.createModule(.{{
                .root_source_file = .{{ .cwd_relative = \"{ZIG_RUNNER}\" }},
                .target = target,
                .optimize = optimize,
            }});
            root_module.addImport(\"hexdump\", hexdump_module);
            root_module.addImport(\"phase6_hexdump_vectors\", fixtures_module);

            const exe = b.addExecutable(.{{
                .name = \"phase6-hexdump-c-parity\",
                .root_module = root_module,
            }});
            const run = b.addRunArtifact(exe);
            const step = b.step(\"run\", \"Run Phase 6 hexdump C parity spot check\");
            step.dependOn(&run.step);
        }}
        """
    )


def sorted_lines(stdout: str) -> list[str]:
    return sorted(stdout.strip("\n").splitlines())


def assert_equal(label: str, actual, expected) -> None:
    if actual != expected:
        raise SystemExit(f"phase6-hexdump-c-parity:self-test:{label}:expected={expected!r}:actual={actual!r}")


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


def validate_expected_surface(lines: list[str], label: str) -> None:
    if lines != EXPECTED_SORTED_LINES:
        raise SystemExit(
            f"phase6-hexdump-c-parity:{label}:unexpected_output:expected={EXPECTED_SORTED_LINES!r}:actual={lines!r}"
        )


def validate_matching_surface(c_lines: list[str], zig_lines: list[str], label: str) -> None:
    if c_lines != zig_lines:
        raise SystemExit(
            f"phase6-hexdump-c-parity:{label}:c_output_mismatch:expected={c_lines!r}:actual={zig_lines!r}"
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
    expect_system_exit(
        "missing_harness",
        lambda: validate_required_path(Path("/tmp/phase6-missing-harness.c"), "harness"),
        "missing harness: /tmp/phase6-missing-harness.c",
    )
    expect_system_exit(
        "missing_helper_source",
        lambda: validate_required_path(Path("/tmp/phase6-missing-helper.zig"), "helper source"),
        "missing helper source: /tmp/phase6-missing-helper.zig",
    )
    expect_system_exit(
        "missing_runner",
        lambda: validate_required_path(Path("/tmp/phase6-missing-runner.zig"), "runner"),
        "missing runner: /tmp/phase6-missing-runner.zig",
    )
    expect_system_exit(
        "missing_fixture_source",
        lambda: validate_required_path(Path("/tmp/phase6-missing-fixture.zig"), "fixture source"),
        "missing fixture source: /tmp/phase6-missing-fixture.zig",
    )
    build_text = build_zig_build_text()
    aggregate_failures = collect_failures(
        ["hexToBin\tA\t10", "length\tplain\t33"],
        ["hexToBin\tA\t10", "length\tplain\t34", "unexpected-extra\tbogus\t0\t"],
    )
    assert_equal(
        "tool_env_build_text_root_derivation_aggregation_and_normalization",
        require_tool("zig", "PHASE6_SELFTEST_TOOL") == "/tmp/zig-self-test"
        and 'root_module.addImport("hexdump", hexdump_module);' in build_text
        and 'root_module.addImport("phase6_hexdump_vectors", fixtures_module);' in build_text
        and str(HELPER_SOURCE) in build_text
        and str(FIXTURE_SOURCE) in build_text
        and str(ZIG_RUNNER) in build_text
        and derive_root(Path("/tmp/phase6-checker.py")) == Path("/tmp")
        and derive_root(Path("/tmp/a/b/c/phase6-checker.py")) == Path("/tmp/a")
        and len(EXPECTED_SORTED_LINES) == 29
        and sorted_lines("hexToBin\tA\t10\ndump\tplain\t3\tabc\n") == ["dump\tplain\t3\tabc", "hexToBin\tA\t10"]
        and len(aggregate_failures) == 3
        and aggregate_failures[0].startswith("phase6-hexdump-c-parity:c:unexpected_output:")
        and aggregate_failures[1].startswith("phase6-hexdump-c-parity:zig:unexpected_output:")
        and aggregate_failures[2]
        == "phase6-hexdump-c-parity:c-vs-zig:c_output_mismatch:"
        "expected=['hexToBin\\tA\\t10', 'length\\tplain\\t33']:"
        "actual=['hexToBin\\tA\\t10', 'length\\tplain\\t34', 'unexpected-extra\\tbogus\\t0\\t']",
        True,
    )
    unexpected_lines = EXPECTED_SORTED_LINES + ["unexpected-extra\tbogus\t0\t"]
    expect_system_exit(
        "unexpected_case",
        lambda: validate_expected_surface(unexpected_lines, "self-test-unexpected-case"),
        "phase6-hexdump-c-parity:self-test-unexpected-case:unexpected_output:"
        f"expected={EXPECTED_SORTED_LINES!r}:actual={unexpected_lines!r}",
    )
    missing_plain_dump_case = [
        line
        for line in EXPECTED_SORTED_LINES
        if line != "dump\tplain rowsize-16 group-8\t33\tb293180a7bdb32be 9b34837d24c4ba70"
    ]
    expect_system_exit(
        "missing_case",
        lambda: validate_expected_surface(missing_plain_dump_case, "self-test-missing-case"),
        "phase6-hexdump-c-parity:self-test-missing-case:unexpected_output:"
        f"expected={EXPECTED_SORTED_LINES!r}:actual={missing_plain_dump_case!r}",
    )
    expect_system_exit(
        "mismatch_surface",
        lambda: validate_matching_surface(
            ["hexToBin\tA\t10", "length\tplain\t33"],
            ["hexToBin\tA\t10", "length\tplain\t34"],
            "self-test-mismatch",
        ),
        "phase6-hexdump-c-parity:self-test-mismatch:c_output_mismatch:"
        "expected=['hexToBin\\tA\\t10', 'length\\tplain\\t33']:"
        "actual=['hexToBin\\tA\\t10', 'length\\tplain\\t34']",
    )

    print("PHASE6_HEXDUMP_C_PARITY_SELF_TEST=pass")
    print("PHASE6_HEXDUMP_C_PARITY_SELF_TEST_CASE_COUNT=8")
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
    validate_required_path(HELPER_SOURCE, "helper source")
    validate_required_path(FIXTURE_SOURCE, "fixture source")
    validate_required_path(ZIG_RUNNER, "runner")

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
    failures = collect_failures(c_lines, zig_lines)

    if failures:
        print("PHASE6_HEXDUMP_C_PARITY=fail")
        for failure in failures:
            print(failure)
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
