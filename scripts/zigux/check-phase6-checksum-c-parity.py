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
C_HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase6_checksum_c_harness.c"
HELPER_SOURCE = ROOT / "lib" / "checksum.zig"
FIXTURE_SOURCE = ROOT / "zigux" / "tests" / "fixtures" / "phase6_checksum_vectors.zig"
ZIG_RUNNER = ROOT / "zigux" / "tests" / "phase6_checksum_c_parity.zig"
EXPECTED_SORTED_LINES = sorted(
    [
        "compute\tempty\t0xffff",
        "compute\ttwo-byte word\t0xfffe",
        "compute\todd payload\t0xd638",
        "compute\tcarry-heavy payload\t0x80ff",
        "ip-fast-csum\tipv4 header\t0x9c5d",
        "partial\todd payload with saturated seed\t0x000029c7",
        "partial\tcarry-heavy payload with unfolded seed\t0x00007f00",
        "partial\tipv4 fragment with arbitrary seed\t0x00004d50",
        "compose\teven split\t0x00000e7b",
        "compose\todd split\t0x00000e7b",
        "tcpudp-nofold\tudp pseudo header\t0x000085e4",
        "tcpudp-magic\tudp pseudo header\t0x7a1b",
        "tcpudp-v6-nofold\tudp pseudo header v6\t0x0000c388",
        "tcpudp-v6-magic\tudp pseudo header v6\t0x3c77",
        "negate\tzero stays zero\t0x00000000",
        "negate\tone negates to all ones\t0xffffffff",
        "negate\tall ones negates to one\t0x00000001",
        "negate\tmixed payload preserves ones complement carry\t0x21524110",
        "from32to16\tzero\t0x0000",
        "fold\tzero\t0xffff",
        "from32to16\tsingle carry into the low word\t0x0001",
        "fold\tsingle carry into the low word\t0xfffe",
        "from32to16\tdouble carry collapse\t0x0001",
        "fold\tdouble carry collapse\t0xfffe",
        "from32to16\tall ones saturates to sixteen bits\t0xffff",
        "fold\tall ones saturates to sixteen bits\t0x0000",
        "from32to16\tmixed words preserve the remaining payload\t0x68ac",
        "fold\tmixed words preserve the remaining payload\t0x9753",
        "unfold\tzero\t0x00000000",
        "unfold\tone\t0x00000001",
        "unfold\tipv4 header checksum word\t0x00009c5d",
        "unfold\tall ones\t0x0000ffff",
        "add16\tsaturated plus one wraps with carry\t0x0001",
        "add16\tsaturated plus zero stays saturated\t0xffff",
        "add16\tsaturated plus saturated preserves ones complement\t0xffff",
        "sub16\tzero minus one borrows across ones complement\t0xfffe",
        "sub16\tsubtracting a prior addend recovers the original word\t0x1234",
        "replace\tpayload-word\t0xffffd8dd",
        "replace-by-diff\tipv4-total-length\t0x9c59",
        "replace2\tipv4-total-length\t0x9c59",
        "replace4\tipv4-saddr\t0x9c58",
    ]
)
FIXTURE_COMPUTE_CASE_MARKER = "pub const compute_cases = [_]ComputeCase"
FIXTURE_COMPOSITION_CASE_MARKER = "pub const composition_cases = [_]CompositionCase"
FIXTURE_SEEDED_CASE_MARKER = "pub const seeded_cases = [_]SeededCase"
FIXTURE_PSEUDO_HEADER_CASE_MARKER = "pub const pseudo_header_cases = [_]PseudoHeaderCase"
FIXTURE_NEGATE_CASE_MARKER = "pub const negate_cases = [_]NegateCase"
FIXTURE_FOLD_CASE_MARKER = "pub const fold_cases = [_]FoldCase"
FIXTURE_ADD16_CASE_MARKER = "pub const add16_cases = [_]Add16Case"
FIXTURE_SUB16_CASE_MARKER = "pub const sub16_cases = [_]Sub16Case"
FIXTURE_CASE_NAME_MARKER = ".name = "
FIXED_IPV6_WRAPPER_CASE_COUNT = 2
FIXED_UNFOLD_CASE_COUNT = 4
FIXED_INCREMENTAL_REPLACEMENT_CASE_COUNT = 4


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


def read_fixture_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"failed to read fixture source: {path}: {exc}") from exc


def extract_initializer_block(fixture_text: str, marker: str, label: str) -> str:
    marker_index = fixture_text.find(marker)
    if marker_index == -1:
        raise SystemExit(f"phase6-checksum-c-parity:{label}:missing_fixture_marker:{marker!r}")

    open_brace_index = fixture_text.find("{", marker_index + len(marker))
    if open_brace_index == -1:
        raise SystemExit(f"phase6-checksum-c-parity:{label}:missing_initializer_brace:{marker!r}")

    depth = 0
    for index in range(open_brace_index, len(fixture_text)):
        char = fixture_text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return fixture_text[open_brace_index + 1 : index]

    raise SystemExit(f"phase6-checksum-c-parity:{label}:unterminated_initializer:{marker!r}")


def extract_named_case_count(fixture_text: str, marker: str, label: str) -> int:
    initializer = extract_initializer_block(fixture_text, marker, label)
    count = initializer.count(FIXTURE_CASE_NAME_MARKER)
    if count <= 0:
        raise SystemExit(f"phase6-checksum-c-parity:{label}:missing_case_names:{marker!r}")
    return count


def expected_fixture_case_count(fixture_text: str) -> int:
    compute_cases = extract_named_case_count(fixture_text, FIXTURE_COMPUTE_CASE_MARKER, "compute-cases")
    composition_cases = extract_named_case_count(fixture_text, FIXTURE_COMPOSITION_CASE_MARKER, "composition-cases")
    seeded_cases = extract_named_case_count(fixture_text, FIXTURE_SEEDED_CASE_MARKER, "seeded-cases")
    pseudo_header_cases = extract_named_case_count(fixture_text, FIXTURE_PSEUDO_HEADER_CASE_MARKER, "pseudo-header-cases")
    negate_cases = extract_named_case_count(fixture_text, FIXTURE_NEGATE_CASE_MARKER, "negate-cases")
    fold_cases = extract_named_case_count(fixture_text, FIXTURE_FOLD_CASE_MARKER, "fold-cases")
    add16_cases = extract_named_case_count(fixture_text, FIXTURE_ADD16_CASE_MARKER, "add16-cases")
    sub16_cases = extract_named_case_count(fixture_text, FIXTURE_SUB16_CASE_MARKER, "sub16-cases")

    if compute_cases < 1:
        raise SystemExit("phase6-checksum-c-parity:compute-cases:expected_at_least_one_case")

    return (
        (compute_cases - 1)
        + 1
        + seeded_cases
        + composition_cases
        + (pseudo_header_cases * 2)
        + FIXED_IPV6_WRAPPER_CASE_COUNT
        + negate_cases
        + (fold_cases * 2)
        + FIXED_UNFOLD_CASE_COUNT
        + add16_cases
        + sub16_cases
        + FIXED_INCREMENTAL_REPLACEMENT_CASE_COUNT
    )


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

            const checksum_module = b.createModule(.{{
                .root_source_file = .{{ .cwd_relative = "{HELPER_SOURCE}" }},
                .target = target,
                .optimize = optimize,
            }});
            const fixtures_module = b.createModule(.{{
                .root_source_file = .{{ .cwd_relative = "{FIXTURE_SOURCE}" }},
                .target = target,
                .optimize = optimize,
            }});
            const root_module = b.createModule(.{{
                .root_source_file = .{{ .cwd_relative = "{ZIG_RUNNER}" }},
                .target = target,
                .optimize = optimize,
            }});
            root_module.addImport("checksum", checksum_module);
            root_module.addImport("phase6_checksum_vectors", fixtures_module);

            const exe = b.addExecutable(.{{
                .name = "phase6-checksum-c-parity",
                .root_module = root_module,
            }});
            const run = b.addRunArtifact(exe);
            const step = b.step("run", "Run Phase 6 checksum C parity spot check");
            step.dependOn(&run.step);
        }}
        """
    )


def sorted_lines(stdout: str) -> list[str]:
    return sorted(stdout.strip().splitlines())


def assert_equal(label: str, actual, expected) -> None:
    if actual != expected:
        raise SystemExit(f"phase6-checksum-c-parity:self-test:{label}:expected={expected!r}:actual={actual!r}")


def expect_system_exit(label: str, callback, expected_message: str) -> None:
    try:
        callback()
    except SystemExit as exc:
        actual_message = str(exc)
        if actual_message != expected_message:
            raise SystemExit(
                f"phase6-checksum-c-parity:self-test:{label}:expected={expected_message!r}:actual={actual_message!r}"
            ) from exc
        return
    raise SystemExit(
        f"phase6-checksum-c-parity:self-test:{label}:missing_system_exit:{expected_message!r}"
    )


def validate_expected_surface(lines: list[str], label: str, expected_case_count: int) -> None:
    actual_case_count = len(EXPECTED_SORTED_LINES)
    if expected_case_count != actual_case_count:
        raise SystemExit(
            f"phase6-checksum-c-parity:{label}:fixture_case_count_mismatch:expected={expected_case_count!r}:actual={actual_case_count!r}"
        )
    if lines != EXPECTED_SORTED_LINES:
        raise SystemExit(
            f"phase6-checksum-c-parity:{label}:unexpected_output:expected={EXPECTED_SORTED_LINES!r}:actual={lines!r}"
        )


def validate_matching_surface(c_lines: list[str], zig_lines: list[str], label: str) -> None:
    if c_lines != zig_lines:
        raise SystemExit(
            f"phase6-checksum-c-parity:{label}:c_output_mismatch:expected={c_lines!r}:actual={zig_lines!r}"
        )


def run_self_test() -> int:
    assert_equal("require_tool_env", require_tool("zig", "PHASE6_SELFTEST_TOOL"), "/tmp/zig-self-test")
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
    assert_equal(
        "build_text_imports_and_paths",
        'root_module.addImport("checksum", checksum_module);' in build_text
        and 'root_module.addImport("phase6_checksum_vectors", fixtures_module);' in build_text
        and str(HELPER_SOURCE) in build_text
        and str(FIXTURE_SOURCE) in build_text
        and str(ZIG_RUNNER) in build_text,
        True,
    )
    fixture_text = textwrap.dedent(
        """
        pub const compute_cases = [_]ComputeCase{
            .{ .name = "empty" },
            .{ .name = "two-byte word" },
            .{ .name = "ipv4 header" },
            .{ .name = "odd payload" },
            .{ .name = "carry-heavy payload" },
        };
        pub const composition_cases = [_]CompositionCase{
            .{ .name = "even split" },
            .{ .name = "odd split" },
        };
        pub const seeded_cases = [_]SeededCase{
            .{ .name = "odd payload with saturated seed" },
            .{ .name = "carry-heavy payload with unfolded seed" },
            .{ .name = "ipv4 fragment with arbitrary seed" },
        };
        pub const pseudo_header_cases = [_]PseudoHeaderCase{
            .{ .name = "udp pseudo header" },
        };
        pub const negate_cases = [_]NegateCase{
            .{ .name = "zero stays zero" },
            .{ .name = "one negates to all ones" },
            .{ .name = "all ones negates to one" },
            .{ .name = "mixed payload preserves ones complement carry" },
        };
        pub const fold_cases = [_]FoldCase{
            .{ .name = "zero" },
            .{ .name = "single carry into the low word" },
            .{ .name = "double carry collapse" },
            .{ .name = "all ones saturates to sixteen bits" },
            .{ .name = "mixed words preserve the remaining payload" },
        };
        pub const add16_cases = [_]Add16Case{
            .{ .name = "saturated plus one wraps with carry" },
            .{ .name = "saturated plus zero stays saturated" },
            .{ .name = "saturated plus saturated preserves ones complement" },
        };
        pub const sub16_cases = [_]Sub16Case{
            .{ .name = "zero minus one borrows across ones complement" },
            .{ .name = "subtracting a prior addend recovers the original word" },
        };
        """
    )
    expected_case_count = expected_fixture_case_count(fixture_text)
    assert_equal("expected_surface_case_count", expected_case_count, 41)
    assert_equal(
        "sorted_lines",
        sorted_lines("partial\tseeded\t0x00000001\ncompute\tempty\t0xffff\n"),
        ["compute\tempty\t0xffff", "partial\tseeded\t0x00000001"],
    )
    validate_expected_surface(EXPECTED_SORTED_LINES, "self-test-positive", expected_case_count)
    unexpected_lines = EXPECTED_SORTED_LINES + ["unexpected-extra\tbogus\t0x00000000"]
    expect_system_exit(
        "unexpected_case",
        lambda: validate_expected_surface(unexpected_lines, "self-test-unexpected-case", expected_case_count),
        "phase6-checksum-c-parity:self-test-unexpected-case:unexpected_output:"
        f"expected={EXPECTED_SORTED_LINES!r}:actual={unexpected_lines!r}",
    )
    missing_replace4_case = [
        line for line in EXPECTED_SORTED_LINES if line != "replace4\tipv4-saddr\t0x9c58"
    ]
    expect_system_exit(
        "missing_case",
        lambda: validate_expected_surface(missing_replace4_case, "self-test-missing-case", expected_case_count),
        "phase6-checksum-c-parity:self-test-missing-case:unexpected_output:"
        f"expected={EXPECTED_SORTED_LINES!r}:actual={missing_replace4_case!r}",
    )
    expect_system_exit(
        "missing_compute_marker",
        lambda: expected_fixture_case_count(fixture_text.replace(FIXTURE_COMPUTE_CASE_MARKER, "pub const missing_compute_cases", 1)),
        f"phase6-checksum-c-parity:compute-cases:missing_fixture_marker:{FIXTURE_COMPUTE_CASE_MARKER!r}",
    )
    expect_system_exit(
        "mismatch_surface",
        lambda: validate_matching_surface(
            ["compute\tempty\t0xffff", "partial\tseeded\t0x00000001"],
            ["compute\tempty\t0xffff", "partial\tseeded\t0x00000002"],
            "self-test-mismatch",
        ),
        "phase6-checksum-c-parity:self-test-mismatch:c_output_mismatch:"
        "expected=['compute\\tempty\\t0xffff', 'partial\\tseeded\\t0x00000001']:"
        "actual=['compute\\tempty\\t0xffff', 'partial\\tseeded\\t0x00000002']",
    )

    print("PHASE6_CHECKSUM_C_PARITY_SELF_TEST=pass")
    print("PHASE6_CHECKSUM_C_PARITY_SELF_TEST_CASE_COUNT=12")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded Phase 6 checksum C parity spot check.")
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

    fixture_text = read_fixture_text(FIXTURE_SOURCE)
    expected_case_count = expected_fixture_case_count(fixture_text)

    out_dir = ROOT / ".zigux-cache" / "phase6-checksum-c-parity"
    out_dir.mkdir(parents=True, exist_ok=True)
    c_bin = out_dir / "phase6_checksum_c_harness"
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
    failures: list[str] = []
    for label, lines in (("c", c_lines), ("zig", zig_lines)):
        try:
            validate_expected_surface(lines, label, expected_case_count)
        except SystemExit as exc:
            failures.append(str(exc))
    try:
        validate_matching_surface(c_lines, zig_lines, "c-vs-zig")
    except SystemExit as exc:
        failures.append(str(exc))

    if failures:
        print("PHASE6_CHECKSUM_C_PARITY=fail")
        for failure in failures:
            print(failure)
        print("C_OUTPUT_START")
        print(c_run.stdout.rstrip())
        print("C_OUTPUT_END")
        print("ZIG_OUTPUT_START")
        print(zig_run.stdout.rstrip())
        print("ZIG_OUTPUT_END")
        return 1

    print("PHASE6_CHECKSUM_C_PARITY=pass")
    print(f"PHASE6_CHECKSUM_C_PARITY_CASES={len(c_lines)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
