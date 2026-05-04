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
C_HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase6_checksum_c_harness.c"
FIXTURE_SOURCE = ROOT / "zigux" / "tests" / "fixtures" / "phase6_checksum_vectors.zig"
ZIG_RUNNER = ROOT / "zigux" / "tests" / "phase6_checksum_c_parity.zig"
EXPECTED_SORTED_LINES = sorted(
    [
        "compute\tempty\t0xffff",
        "compute\ttwo-byte word\t0xfffe",
        "compute\tipv4 header\t0x9c5d",
        "compute\todd payload\t0xd638",
        "compute\tcarry-heavy payload\t0x80ff",
        "partial\todd payload with saturated seed\t0x000029c7",
        "partial\tcarry-heavy payload with unfolded seed\t0x00007f00",
        "partial\tipv4 fragment with arbitrary seed\t0x00004d50",
        "compose\teven split\t0x00000e7b",
        "compose\todd split\t0x00000e7b",
        "tcpudp-nofold\tudp pseudo header\t0x000085e4",
        "tcpudpv6-nofold\tudp doc payload odd\t0x0000f876",
        "tcpudpv6-nofold\ttcp carry payload even\t0x0000b842",
        "tcpudpv6-nofold\ticmpv6 preserves upper declared length bits\t0x00007e10",
        "carry-discipline\tall-ones odd payload with saturated seed\t0x00ff",
        "carry-discipline\tall-ones even payload with zero seed\t0x0000",
        "carry-discipline\tsingle-byte no-carry seed stays one step below overflow\t0x0004",
        "carry-discipline\ttwo-byte no-carry seed stays one step below overflow\t0x0404",
        "add16\twrap-plus-one\t0x0001",
        "add16\tzero-addend-preserves-saturated-sum\t0xffff",
        "add16\tdouble-saturated-addends-fold-carry\t0xffff",
        "sub16\tzero-minus-one-wraps\t0xfffe",
        "sub16\tinverse-of-add16-round-trip\t0x1234",
        "replace\tpayload-word\t0xffffd8dd",
        "replace-by-diff\tipv4-total-length\t0x9c59",
        "replace2\tipv4-total-length\t0x9c59",
        "replace4\tipv4-saddr\t0x9c58",
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

            const checksum_module = b.createModule(.{{
                .root_source_file = .{{ .cwd_relative = \"{ROOT / 'lib' / 'checksum.zig'}\" }},
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


def validate_expected_surface(lines: list[str], label: str) -> None:
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
    assert_equal("build_text_checksum_import", 'root_module.addImport("checksum", checksum_module);' in build_text, True)
    assert_equal(
        "build_text_fixture_import_and_paths",
        'root_module.addImport("phase6_checksum_vectors", fixtures_module);' in build_text
        and str(FIXTURE_SOURCE) in build_text
        and str(ZIG_RUNNER) in build_text,
        True,
    )
    assert_equal("expected_surface_case_count", len(EXPECTED_SORTED_LINES), 27)
    assert_equal(
        "sorted_lines",
        sorted_lines("partial\tseeded\t0x00000001\ncompute\tempty\t0xffff\n"),
        ["compute\tempty\t0xffff", "partial\tseeded\t0x00000001"],
    )
    validate_expected_surface(EXPECTED_SORTED_LINES, "self-test-positive")
    unexpected_lines = EXPECTED_SORTED_LINES + ["unexpected-extra\tbogus\t0x00000000"]
    expect_system_exit(
        "unexpected_case",
        lambda: validate_expected_surface(unexpected_lines, "self-test-unexpected-case"),
        "phase6-checksum-c-parity:self-test-unexpected-case:unexpected_output:"
        f"expected={EXPECTED_SORTED_LINES!r}:actual={unexpected_lines!r}",
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
    print("PHASE6_CHECKSUM_C_PARITY_SELF_TEST_CASE_COUNT=11")
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
    validate_required_path(FIXTURE_SOURCE, "fixture source")
    validate_required_path(ZIG_RUNNER, "runner")

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
            validate_expected_surface(lines, label)
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
