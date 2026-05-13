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
REQUIRED_PACKET_PATHS = (
    ("harness", C_HARNESS),
    ("helper source", HELPER_SOURCE),
    ("fixture source", FIXTURE_SOURCE),
    ("runner", ZIG_RUNNER),
)
EXPECTED_SORTED_LINES = sorted(
    [
        "add16\tsaturated plus one wraps with carry\t0x0001",
        "add16\tsaturated plus saturated preserves ones complement\t0xffff",
        "add16\tsaturated plus zero stays saturated\t0xffff",
        "carry-discipline\tall-ones even payload with zero seed\t0x0000",
        "carry-discipline\tall-ones odd payload with saturated seed\t0x00ff",
        "carry-discipline\tsingle-byte no-carry seed stays one step below overflow\t0x0004",
        "carry-discipline\ttwo-byte no-carry seed stays one step below overflow\t0x0404",
        "compose\teven split\t0x00000e7b",
        "compose\todd split\t0x00000e7b",
        "compute\tcarry-heavy payload\t0x80ff",
        "compute\tempty\t0xffff",
        "compute\tipv4 header\t0x9c5d",
        "compute\todd payload\t0xd638",
        "compute\ttwo-byte word\t0xfffe",
        "partial\tcarry-heavy payload with unfolded seed\t0x00007f00",
        "partial\tipv4 fragment with arbitrary seed\t0x00004d50",
        "partial\todd payload with saturated seed\t0x000029c7",
        "replace\tpayload-word\t0xffffd8dd",
        "replace-by-diff\tipv4-total-length\t0x9c59",
        "replace2\tipv4-total-length\t0x9c59",
        "replace4\tipv4-saddr\t0x9c58",
        "sub16\tsubtracting a prior addend recovers the original word\t0x1234",
        "sub16\tzero minus one borrows across ones complement\t0xfffe",
        "tcpudp-nofold\tudp pseudo header\t0x000085e4",
        "tcpudpv6-nofold\ticmpv6 preserves upper declared length bits\t0x00007e10",
        "tcpudpv6-nofold\ttcp carry payload even\t0x0000b842",
        "tcpudpv6-nofold\tudp doc payload odd\t0x0000f876",
    ]
)
FIXTURE_COMPUTE_CASE_MARKER = "pub const compute_cases = [_]ComputeCase"
FIXTURE_COMPOSITION_CASE_MARKER = "pub const composition_cases = [_]CompositionCase"
FIXTURE_SEEDED_CASE_MARKER = "pub const seeded_cases = [_]SeededCase"
FIXTURE_PSEUDO_HEADER_CASE_MARKER = "pub const pseudo_header_cases = [_]PseudoHeaderCase"
FIXTURE_IPV6_PSEUDO_HEADER_CASE_MARKER = "pub const ipv6_pseudo_header_cases = [_]Ipv6PseudoHeaderCase"
FIXTURE_CARRY_DISCIPLINE_CASE_MARKER = "pub const carry_discipline_cases = [_]CarryDisciplineCase"
FIXTURE_CASE_NAME_MARKER = ".name = "
FIXED_INCREMENTAL_REPLACEMENT_CASE_COUNT = 4
FIXED_DIRECT_16BIT_CARRY_CASE_COUNT = 5


def require_tool(name: str, env_name: str) -> str:
    preferred = os.environ.get(env_name)
    if preferred:
        return preferred

    tool = shutil.which(name)
    if tool is None:
        raise SystemExit(f"missing required tool: {name}")
    return tool


def collect_missing_required_paths(required_paths: tuple[tuple[str, Path], ...] = REQUIRED_PACKET_PATHS) -> list[str]:
    missing: list[str] = []
    for label, path in required_paths:
        if not path.exists():
            missing.append(f"missing {label}: {path}")
    return missing


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
    ipv6_pseudo_header_cases = extract_named_case_count(
        fixture_text, FIXTURE_IPV6_PSEUDO_HEADER_CASE_MARKER, "ipv6-pseudo-header-cases"
    )
    carry_discipline_cases = extract_named_case_count(
        fixture_text, FIXTURE_CARRY_DISCIPLINE_CASE_MARKER, "carry-discipline-cases"
    )

    if compute_cases < 1:
        raise SystemExit("phase6-checksum-c-parity:compute-cases:expected_at_least_one_case")

    return (
        compute_cases
        + seeded_cases
        + composition_cases
        + pseudo_header_cases
        + ipv6_pseudo_header_cases
        + carry_discipline_cases
        + FIXED_INCREMENTAL_REPLACEMENT_CASE_COUNT
        + FIXED_DIRECT_16BIT_CARRY_CASE_COUNT
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
        const std = @import(\"std\");

        pub fn build(b: *std.Build) void {{
            const target = b.standardTargetOptions(.{{}});
            const optimize = b.standardOptimizeOption(.{{}});

            const checksum_module = b.createModule(.{{
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
            root_module.addImport(\"checksum\", checksum_module);
            root_module.addImport(\"phase6_checksum_vectors\", fixtures_module);

            const exe = b.addExecutable(.{{
                .name = \"phase6-checksum-c-parity\",
                .root_module = root_module,
            }});
            const run = b.addRunArtifact(exe);
            const step = b.step(\"run\", \"Run Phase 6 checksum C parity spot check\");
            step.dependOn(&run.step);
        }}
        """
    )


def emit_missing_packet_report(missing_paths: list[str]) -> int:
    print("PHASE6_CHECKSUM_C_PARITY=blocked")
    print("PHASE6_CHECKSUM_C_PARITY_BLOCKERS_START")
    for item in missing_paths:
        print(item)
    print("PHASE6_CHECKSUM_C_PARITY_BLOCKERS_END")
    return 1


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
    assert_equal(
        "collect_missing_required_paths",
        collect_missing_required_paths(
            (
                ("helper source", Path("/tmp/phase6-missing-helper.zig")),
                ("fixture source", Path("/tmp/phase6-missing-fixture.zig")),
                ("runner", Path("/tmp/phase6-missing-runner.zig")),
            )
        ),
        [
            "missing helper source: /tmp/phase6-missing-helper.zig",
            "missing fixture source: /tmp/phase6-missing-fixture.zig",
            "missing runner: /tmp/phase6-missing-runner.zig",
        ],
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
        pub const ipv6_pseudo_header_cases = [_]Ipv6PseudoHeaderCase{
            .{ .name = "udp doc payload odd" },
            .{ .name = "tcp carry payload even" },
            .{ .name = "icmpv6 preserves upper declared length bits" },
        };
        pub const carry_discipline_cases = [_]CarryDisciplineCase{
            .{ .name = "all-ones odd payload with saturated seed" },
            .{ .name = "all-ones even payload with zero seed" },
            .{ .name = "single-byte no-carry seed stays one step below overflow" },
            .{ .name = "two-byte no-carry seed stays one step below overflow" },
        };
        """
    )
    expected_case_count = expected_fixture_case_count(fixture_text)
    assert_equal("expected_surface_case_count", expected_case_count, 27)
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
        "expected=['compute\\tempty\\t0xffff', 'partial\\tempty\\t0x00000001']:"
        "actual=['compute\\tempty\\t0xffff', 'partial\\tempty\\t0x00000002']",
    )

    print("PHASE6_CHECKSUM_C_PARITY_SELF_TEST=pass")
    print("PHASE6_CHECKSUM_C_PARITY_SELF_TEST_CASE_COUNT=13")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded Phase 6 checksum C parity spot check.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in parity-script checks")
    args = parser.parse_args()

    if args.self_test:
        os.environ["PHASE6_SELFTEST_TOOL"] = "/tmp/zig-self-test"
        return run_self_test()

    missing_paths = collect_missing_required_paths()
    if missing_paths:
        return emit_missing_packet_report(missing_paths)

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
