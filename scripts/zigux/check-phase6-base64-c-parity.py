#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
C_HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase6_base64_c_harness.c"
HELPER_SOURCE = ROOT / "lib" / "base64.zig"
CASE_GENERATOR = ROOT / "zigux" / "tests" / "phase6_base64_c_casegen.zig"
FIXTURE_SOURCE = ROOT / "zigux" / "tests" / "fixtures" / "phase6_base64_c_parity_vectors.zig"
GENERATED_INCLUDE = ROOT / "zigux" / "tests" / "fixtures" / "phase6_base64_c_generated_cases.inc"
ZIG_RUNNER = ROOT / "zigux" / "tests" / "phase6_base64_c_parity.zig"
BYTE_CONST_RE = re.compile(r"(?:pub\s+)?const\s+(\w+)\s*=\s*\[_\]u8\{([^}]*)\};")
ENTRY_RE = re.compile(r"\.\{([^}]*)\}", re.S)
FIELD_RE = re.compile(r'\.(\w+)\s*=\s*("(?:\\.|[^"])*"|&?\w+(?:\[0\.\.\])?|true|false)')


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

            const base64_module = b.createModule(.{{
                .root_source_file = .{{ .cwd_relative = \"{HELPER_SOURCE}\" }},
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


def validate_expected_surface(lines: list[str], expected_lines: list[str], label: str) -> None:
    if lines != expected_lines:
        raise SystemExit(
            f"phase6-base64-c-parity:{label}:unexpected_output:expected={expected_lines!r}:actual={lines!r}"
        )


def validate_matching_surface(c_lines: list[str], zig_lines: list[str], label: str) -> None:
    if c_lines != zig_lines:
        raise SystemExit(
            f"phase6-base64-c-parity:{label}:c_output_mismatch:expected={c_lines!r}:actual={zig_lines!r}"
        )


def parse_zig_string_literal(expr: str) -> bytes:
    try:
        value = ast.literal_eval("b" + expr)
    except (SyntaxError, ValueError) as exc:
        raise SystemExit(f"phase6-base64-c-parity:unsupported_string_literal:{expr}") from exc
    if not isinstance(value, bytes):
        raise SystemExit(f"phase6-base64-c-parity:unsupported_string_literal:{expr}")
    return value


def parse_zig_byte_token(token: str) -> int:
    token = token.strip()
    if not token:
        raise SystemExit("phase6-base64-c-parity:empty_byte_token")
    if token.startswith("'") and token.endswith("'"):
        try:
            value = ast.literal_eval(token)
        except (SyntaxError, ValueError) as exc:
            raise SystemExit(f"phase6-base64-c-parity:unsupported_byte_token:{token}") from exc
        if not isinstance(value, str) or len(value) != 1:
            raise SystemExit(f"phase6-base64-c-parity:unsupported_byte_token:{token}")
        return ord(value)
    try:
        return int(token, 0)
    except ValueError as exc:
        raise SystemExit(f"phase6-base64-c-parity:unsupported_byte_token:{token}") from exc


def parse_byte_constants(text: str) -> dict[str, bytes]:
    constants: dict[str, bytes] = {}
    for name, body in BYTE_CONST_RE.findall(text):
        tokens = [token.strip() for token in body.split(",") if token.strip()]
        constants[name] = bytes(parse_zig_byte_token(token) for token in tokens)
    return constants


def extract_array_block(text: str, name: str) -> str:
    marker = f"pub const {name} ="
    start = text.find(marker)
    if start == -1:
        raise SystemExit(f"phase6-base64-c-parity:missing_fixture_array:{name}")

    brace_start = text.find("{", start)
    if brace_start == -1:
        raise SystemExit(f"phase6-base64-c-parity:missing_fixture_block:{name}")

    depth = 0
    for index in range(brace_start, len(text)):
        ch = text[index]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[brace_start + 1 : index]

    raise SystemExit(f"phase6-base64-c-parity:unterminated_fixture_block:{name}")


def parse_case_entries(block: str, label: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for match in ENTRY_RE.finditer(block):
        fields = {name: value.strip() for name, value in FIELD_RE.findall(match.group(1))}
        if fields:
            entries.append(fields)
    if not entries:
        raise SystemExit(f"phase6-base64-c-parity:empty_fixture_array:{label}")
    return entries


def parse_bool(expr: str) -> bool:
    if expr == "true":
        return True
    if expr == "false":
        return False
    raise SystemExit(f"phase6-base64-c-parity:unsupported_bool:{expr}")


def parse_bytes_expr(expr: str, byte_constants: dict[str, bytes]) -> bytes:
    expr = expr.strip()
    if expr.startswith("&"):
        expr = expr[1:].strip()
    if expr.endswith("[0..]"):
        expr = expr[:-5].strip()
    if expr.startswith('"'):
        return parse_zig_string_literal(expr)
    if expr in byte_constants:
        return byte_constants[expr]
    raise SystemExit(f"phase6-base64-c-parity:unsupported_bytes_expr:{expr}")


def parse_variant_name(expr: str) -> str:
    return parse_zig_string_literal(expr).decode("ascii")


def expected_surface_from_fixture_text(text: str) -> list[str]:
    byte_constants = parse_byte_constants(text)
    rows: list[str] = []

    for case in parse_case_entries(extract_array_block(text, "standard_cases"), "standard_cases"):
        rows.append(
            "enc\tstd\t{padding}\t{input_hex}\t{output_hex}".format(
                padding=int(parse_bool(case["padding"])),
                input_hex=parse_bytes_expr(case["input"], byte_constants).hex(),
                output_hex=parse_bytes_expr(case["expected"], byte_constants).hex(),
            )
        )

    for case in parse_case_entries(extract_array_block(text, "variant_cases"), "variant_cases"):
        rows.append(
            "enc\t{variant}\t{padding}\t{input_hex}\t{output_hex}".format(
                variant=parse_variant_name(case["variant_name"]),
                padding=int(parse_bool(case["padding"])),
                input_hex=parse_bytes_expr(case["input"], byte_constants).hex(),
                output_hex=parse_bytes_expr(case["expected"], byte_constants).hex(),
            )
        )

    for case in parse_case_entries(extract_array_block(text, "standard_decode_cases"), "standard_decode_cases"):
        expected = parse_bytes_expr(case["expected"], byte_constants)
        rows.append(
            "dec\tstd\t{padding}\t{output_len}\t{input_hex}\t{output_hex}".format(
                padding=int(parse_bool(case["padding"])),
                output_len=len(expected),
                input_hex=parse_bytes_expr(case["input"], byte_constants).hex(),
                output_hex=expected.hex(),
            )
        )

    for case in parse_case_entries(extract_array_block(text, "variant_decode_cases"), "variant_decode_cases"):
        expected = parse_bytes_expr(case["expected"], byte_constants)
        rows.append(
            "dec\t{variant}\t{padding}\t{output_len}\t{input_hex}\t{output_hex}".format(
                variant=parse_variant_name(case["variant_name"]),
                padding=int(parse_bool(case["padding"])),
                output_len=len(expected),
                input_hex=parse_bytes_expr(case["input"], byte_constants).hex(),
                output_hex=expected.hex(),
            )
        )

    for case in parse_case_entries(extract_array_block(text, "invalid_decode_cases"), "invalid_decode_cases"):
        rows.append(
            "inv\t{variant}\t{padding}\t{input_hex}\tInvalidInput\tInvalidInput".format(
                variant=parse_variant_name(case["variant_name"]),
                padding=int(parse_bool(case["padding"])),
                input_hex=parse_bytes_expr(case["input"], byte_constants).hex(),
            )
        )

    return sorted(rows)


def expected_surface_from_fixture_file(path: Path) -> list[str]:
    return expected_surface_from_fixture_text(path.read_text(encoding="utf-8"))


def cleanup_generated_include(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def cleanup_generated_include_self_test() -> bool:
    temp_dir = Path(tempfile.mkdtemp(prefix="phase6-base64-selftest-"))
    try:
        generated_include = temp_dir / GENERATED_INCLUDE.name
        generated_include.write_text("transient fixture data", encoding="utf-8")
        cleanup_generated_include(generated_include)
        cleanup_generated_include(generated_include)
        return not generated_include.exists()
    finally:
        temp_dir.rmdir()


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
        "missing_case_generator",
        lambda: validate_required_path(Path("/tmp/phase6-missing-casegen.zig"), "case generator"),
        "missing case generator: /tmp/phase6-missing-casegen.zig",
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
    sample_fixture = """
const variant_sample = [_]u8{ 0xfb };
const invalid_with_nul = [_]u8{ 'Z', 'g', 0, '=' };
pub const standard_cases = [_]EncodeCase{
    .{ .input = "Man", .expected = "TWFu", .padding = true },
};
pub const variant_cases = [_]VariantCase{
    .{ .input = &variant_sample, .expected = "-w", .padding = false, .variant_name = "urlsafe" },
};
pub const standard_decode_cases = [_]DecodeCase{
    .{ .input = "TWFu", .expected = "Man", .padding = true, .variant_name = "std" },
};
pub const variant_decode_cases = [_]DecodeCase{
    .{ .input = "-w", .expected = &variant_sample, .padding = false, .variant_name = "urlsafe" },
};
pub const invalid_decode_cases = [_]InvalidDecodeCase{
    .{ .input = invalid_with_nul[0..], .padding = true, .variant_name = "std" },
};
"""
    sample_expected = sorted(
        [
            "dec\tstd\t1\t3\t54574675\t4d616e",
            "dec\turlsafe\t0\t1\t2d77\tfb",
            "enc\tstd\t1\t4d616e\t54574675",
            "enc\turlsafe\t0\tfb\t2d77",
            "inv\tstd\t1\t5a67003d\tInvalidInput\tInvalidInput",
        ]
    )
    assert_equal(
        "build_text_and_surface",
        require_tool("zig", "PHASE6_SELFTEST_TOOL") == "/tmp/zig-self-test"
        and 'root_module.addImport("base64", base64_module);' in build_text
        and str(HELPER_SOURCE) in build_text
        and str(ZIG_RUNNER) in build_text
        and expected_surface_from_fixture_text(sample_fixture) == sample_expected
        and cleanup_generated_include_self_test(),
        True,
    )
    expect_system_exit(
        "unsupported_byte_token",
        lambda: parse_byte_constants("const bad = [_]u8{ bogus };"),
        "phase6-base64-c-parity:unsupported_byte_token:bogus",
    )
    unexpected_lines = sample_expected + ["unexpected-extra\tstd\t1\tbogus\tok"]
    expect_system_exit(
        "unexpected_case",
        lambda: validate_expected_surface(unexpected_lines, sample_expected, "self-test-unexpected-case"),
        "phase6-base64-c-parity:self-test-unexpected-case:unexpected_output:"
        f"expected={sample_expected!r}:actual={unexpected_lines!r}",
    )
    missing_std_encode_case = [
        line for line in sample_expected if line != "enc\tstd\t1\t4d616e\t54574675"
    ]
    expect_system_exit(
        "missing_case",
        lambda: validate_expected_surface(missing_std_encode_case, sample_expected, "self-test-missing-case"),
        "phase6-base64-c-parity:self-test-missing-case:unexpected_output:"
        f"expected={sample_expected!r}:actual={missing_std_encode_case!r}",
    )
    mismatched_zig_lines = [
        line if line != "inv\tstd\t1\t5a67003d\tInvalidInput\tInvalidInput" else "inv\tstd\t1\t5a67003d\tInvalidInput\tok"
        for line in sample_expected
    ]
    expect_system_exit(
        "mismatch_case",
        lambda: validate_matching_surface(sample_expected, mismatched_zig_lines, "self-test-mismatch"),
        "phase6-base64-c-parity:self-test-mismatch:c_output_mismatch:"
        f"expected={sample_expected!r}:actual={mismatched_zig_lines!r}",
    )

    print("PHASE6_BASE64_C_PARITY_SELF_TEST=pass")
    print("PHASE6_BASE64_C_PARITY_SELF_TEST_CASE_COUNT=10")
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
    validate_required_path(HELPER_SOURCE, "helper source")
    validate_required_path(CASE_GENERATOR, "case generator")
    validate_required_path(FIXTURE_SOURCE, "fixture source")
    validate_required_path(ZIG_RUNNER, "runner")

    expected_lines = expected_surface_from_fixture_file(FIXTURE_SOURCE)

    out_dir = ROOT / ".zigux-cache" / "phase6-base64-c-parity"
    out_dir.mkdir(parents=True, exist_ok=True)
    c_bin = out_dir / "phase6_base64_c_harness"
    zig_build = out_dir / "build.zig"

    try:
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
    finally:
        cleanup_generated_include(GENERATED_INCLUDE)

    c_lines = sorted_lines(c_run.stdout)
    zig_lines = sorted_lines(zig_run.stdout)
    validate_expected_surface(c_lines, expected_lines, "c")
    validate_expected_surface(zig_lines, expected_lines, "zig")

    try:
        validate_matching_surface(c_lines, zig_lines, "c-vs-zig")
    except SystemExit as exc:
        print("PHASE6_BASE64_C_PARITY=fail")
        print(str(exc))
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
