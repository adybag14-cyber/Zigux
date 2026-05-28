#!/usr/bin/env python3
"""Compare bounded `genksyms` CRC outputs from the C and Zig helpers."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile


def repo_root_from(script_path: Path, explicit: str | None) -> Path:
    """Return the repository root derived from the script path or override."""
    if explicit:
        return Path(explicit).resolve()
    return script_path.resolve().parents[2]


def fixture_paths(root: Path) -> tuple[Path, Path, Path, Path]:
    """Return the helper, harness, input, and expected fixture paths."""
    fixture_dir = root / "zigux" / "tests" / "fixtures" / "genksyms_crc"
    return (
        root / "scripts" / "zigux" / "genksyms_crc.zig",
        fixture_dir / "genksyms_crc_c_harness.c",
        fixture_dir / "inputs.txt",
        fixture_dir / "expected.json",
    )


def required_paths(refresh: bool, zig_tool: Path, harness: Path, inputs: Path, expected: Path) -> tuple[Path, ...]:
    """Return the exact files required for the requested execution mode."""
    if refresh:
        return (zig_tool, harness, inputs)
    return (zig_tool, harness, inputs, expected)


def ensure_required_files_exist(paths: tuple[Path, ...]) -> None:
    """Fail fast when any required path is missing or is not a regular file."""
    for path in paths:
        if not path.is_file():
            raise SystemExit(f"missing required file: {path}")


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    """Run a subprocess and require it to exit successfully."""
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def run_checked(label: str, cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    """Run a subprocess and normalize launch and exit failures into SystemExit."""
    try:
        return run(cmd, **kwargs)
    except FileNotFoundError as exc:
        raise SystemExit(f"{label} failed: missing executable: {cmd[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"{label} failed with exit {exc.returncode}: {' '.join(cmd)}") from exc
    except OSError as exc:
        detail = exc.strerror or str(exc)
        raise SystemExit(f"{label} failed to launch {cmd[0]}: {detail}") from exc


def resolve_tool(candidate: str, missing_message: str) -> str:
    """Resolve an executable name or path and fail with a caller-provided message."""
    resolved = shutil.which(candidate)
    if resolved:
        return resolved
    raise SystemExit(missing_message)


def find_compiler(explicit: str | None) -> str:
    """Locate the C compiler from an override, environment, or common defaults."""
    if explicit:
        return resolve_tool(explicit, f"C compiler not found or not executable: {explicit}")
    compiler = os.environ.get("CC")
    if compiler:
        return resolve_tool(compiler, f"C compiler from CC not found or not executable: {compiler}")
    detected = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    if detected:
        return detected
    raise SystemExit("C compiler not found; pass --cc or install cc/gcc/clang")


def find_zig(explicit: str | None, root: Path) -> str:
    """Locate Zig from an override, environment, PATH, or the attached fallback."""
    if explicit:
        return resolve_tool(explicit, f"zig not found or not executable: {explicit}")
    env = os.environ.get("ZIG")
    if env:
        return resolve_tool(env, f"zig from ZIG not found or not executable: {env}")
    detected = shutil.which("zig")
    if detected:
        return detected
    fallback = root.parent / ".toolchains" / "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2" / "zig"
    if fallback.exists():
        return resolve_tool(str(fallback), f"zig fallback not executable: {fallback}")
    raise SystemExit("zig not found; pass --zig, set ZIG, or extract the attached toolchain")


def validate_case_packet_shape(data: object, label: str) -> None:
    """Reject JSON packets that drift from the exact `{\"cases\": [...]}` schema."""
    if not isinstance(data, dict):
        raise SystemExit(f"{label} invalid shape: top-level value must be an object")
    if "cases" not in data:
        raise SystemExit(f"{label} invalid shape: missing 'cases' array")
    if len(data) != 1:
        extra_keys = sorted(key for key in data.keys() if key != "cases")
        raise SystemExit(f"{label} invalid shape: unexpected top-level keys: {extra_keys}")
    cases = data["cases"]
    if not isinstance(cases, list):
        raise SystemExit(f"{label} invalid shape: 'cases' must be a list")
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise SystemExit(f"{label} invalid shape: cases[{index}] must be an object")
        if "input" not in case:
            raise SystemExit(f"{label} invalid shape: cases[{index}] missing 'input'")
        if "crc_hex" not in case:
            raise SystemExit(f"{label} invalid shape: cases[{index}] missing 'crc_hex'")
        if len(case) != 2:
            extra_keys = sorted(key for key in case.keys() if key not in {"input", "crc_hex"})
            raise SystemExit(f"{label} invalid shape: cases[{index}] unexpected keys: {extra_keys}")
        if not isinstance(case["input"], str):
            raise SystemExit(f"{label} invalid shape: cases[{index}].input must be a string")
        if not isinstance(case["crc_hex"], str):
            raise SystemExit(f"{label} invalid shape: cases[{index}].crc_hex must be a string")


def canonicalize_json(text: str, label: str = "json") -> str:
    """Parse, validate, and canonically serialize a case packet."""
    data = json.loads(text)
    validate_case_packet_shape(data, label)
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def canonicalize_json_file(path: Path, label: str) -> str:
    """Read, validate, and canonicalize a JSON case-packet file."""
    try:
        return canonicalize_json(path.read_text(encoding="utf-8"), label)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{label} invalid json: {path}: {exc.msg}") from exc


def summarize_mismatch(left: str, right: str) -> str:
    """Describe the earliest difference between two canonical JSON strings."""
    shared_prefix = 0
    for shared_prefix, (left_char, right_char) in enumerate(zip(left, right)):
        if left_char != right_char:
            return (
                f"first differing byte {shared_prefix}: "
                f"left={left_char!r} right={right_char!r}; "
                f"left_len={len(left)} right_len={len(right)}"
            )

    shared_prefix = min(len(left), len(right))
    if len(left) != len(right):
        return (
            f"shared prefix length {shared_prefix}; "
            f"left_len={len(left)} right_len={len(right)}"
        )
    return f"left_len={len(left)} right_len={len(right)}"


def compare_json(label: str, left: Path, right: Path) -> None:
    """Assert that two JSON packet files have identical canonical content."""
    left_canonical = canonicalize_json_file(left, label)
    right_canonical = canonicalize_json_file(right, label)
    if left_canonical != right_canonical:
        detail = summarize_mismatch(left_canonical, right_canonical)
        raise SystemExit(f"{label} mismatch: {left} != {right} ({detail})")


def compile_run_c(root: Path, tmp_dir: Path, harness: Path, inputs: Path, actual: Path, compiler: str) -> None:
    """Build the C harness, run it, and persist its JSON output."""
    exe = tmp_dir / "genksyms-crc-c"
    run_checked("compile C harness", [compiler, "-std=c11", "-Wall", "-Wextra", "-o", str(exe), str(harness)], cwd=str(root))
    result = run_checked("run C harness", [str(exe), str(inputs)], cwd=str(root), capture_output=True)
    actual.write_text(result.stdout, encoding="utf-8", newline="\n")


def compile_run_zig(root: Path, tmp_dir: Path, zig_tool: Path, inputs: Path, actual: Path, zig: str) -> None:
    """Build the Zig helper, run it, and persist its JSON output."""
    exe = tmp_dir / "genksyms-crc-zig"
    run_checked("build Zig CRC helper", [zig, "build-exe", str(zig_tool), "-femit-bin=" + str(exe)], cwd=str(root))
    result = run_checked("run Zig CRC helper", [str(exe), str(inputs)], cwd=str(root), capture_output=True)
    actual.write_text(result.stdout, encoding="utf-8", newline="\n")


def write_fake_executable(path: Path, body: str = "#!/bin/sh\nexit 0\n") -> Path:
    """Create a tiny executable file for tool-discovery self-tests."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8", newline="\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def expect_system_exit_contains(callback, needle: str) -> None:
    """Assert that a callback exits with a message containing the expected text."""
    try:
        callback()
    except SystemExit as exc:
        if needle not in str(exc):
            raise SystemExit(f"GENKSYMS_CRC_SELF_TEST=fail: expected {needle!r} in {exc!s}")
        return
    raise SystemExit(f"GENKSYMS_CRC_SELF_TEST=fail: expected SystemExit containing {needle!r}")


def run_self_test() -> int:
    """Exercise the checker's schema, tool, and comparison guards without building helpers."""
    sample_a = canonicalize_json('{"cases":[{"crc_hex":"0x1451dab1","input":"int"}]}')
    sample_b = canonicalize_json('{\n  "cases": [ { "input": "int", "crc_hex": "0x1451dab1" } ]\n}')
    if sample_a != sample_b:
        raise SystemExit("GENKSYMS_CRC_SELF_TEST=fail")

    derived_root = repo_root_from(Path("/tmp/zigux/scripts/zigux/check-genksyms-crc-diff.py"), None)
    if derived_root != Path("/tmp/zigux").resolve():
        raise SystemExit("GENKSYMS_CRC_SELF_TEST=fail")

    explicit_root = repo_root_from(Path("/tmp/ignored/scripts/zigux/check-genksyms-crc-diff.py"), "/tmp/explicit-root")
    if explicit_root != Path("/tmp/explicit-root").resolve():
        raise SystemExit("GENKSYMS_CRC_SELF_TEST=fail")

    expected_paths = (
        derived_root / "scripts" / "zigux" / "genksyms_crc.zig",
        derived_root / "zigux" / "tests" / "fixtures" / "genksyms_crc" / "genksyms_crc_c_harness.c",
        derived_root / "zigux" / "tests" / "fixtures" / "genksyms_crc" / "inputs.txt",
        derived_root / "zigux" / "tests" / "fixtures" / "genksyms_crc" / "expected.json",
    )
    if fixture_paths(derived_root) != expected_paths:
        raise SystemExit("GENKSYMS_CRC_SELF_TEST=fail")
    if required_paths(False, *expected_paths) != expected_paths:
        raise SystemExit("GENKSYMS_CRC_SELF_TEST=fail")
    if required_paths(True, *expected_paths) != expected_paths[:-1]:
        raise SystemExit("GENKSYMS_CRC_SELF_TEST=fail")

    expect_system_exit_contains(
        lambda: canonicalize_json("[]", "selftest-top-level-array"),
        "selftest-top-level-array invalid shape: top-level value must be an object",
    )
    expect_system_exit_contains(
        lambda: canonicalize_json("{}", "selftest-missing-cases"),
        "selftest-missing-cases invalid shape: missing 'cases' array",
    )
    expect_system_exit_contains(
        lambda: canonicalize_json('{"cases":{} }', "selftest-cases-not-list"),
        "selftest-cases-not-list invalid shape: 'cases' must be a list",
    )
    expect_system_exit_contains(
        lambda: canonicalize_json('{"cases":[{"input":"int"}]}', "selftest-missing-crc"),
        "selftest-missing-crc invalid shape: cases[0] missing 'crc_hex'",
    )
    expect_system_exit_contains(
        lambda: canonicalize_json('{"cases":[{"input":"int","crc_hex":"0x1451dab1","extra":true}]}', "selftest-extra-case-key"),
        "selftest-extra-case-key invalid shape: cases[0] unexpected keys: ['extra']",
    )
    expect_system_exit_contains(
        lambda: canonicalize_json('{"cases":[{"input":"int","crc_hex":123}]}', "selftest-non-string-crc"),
        "selftest-non-string-crc invalid shape: cases[0].crc_hex must be a string",
    )

    with tempfile.TemporaryDirectory(prefix="genksyms_crc_selftest_required_files_") as required_files_tmp_dir_str:
        required_files_root = Path(required_files_tmp_dir_str) / "repo"
        required_paths_tuple = fixture_paths(required_files_root)
        for path in required_paths_tuple[:-1]:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("", encoding="utf-8", newline="\n")
        ensure_required_files_exist(required_paths(True, *required_paths_tuple))
        expect_system_exit_contains(
            lambda: ensure_required_files_exist(required_paths(False, *required_paths_tuple)),
            f"missing required file: {required_paths_tuple[-1]}",
        )
        required_paths_tuple[-1].parent.mkdir(parents=True, exist_ok=True)
        required_paths_tuple[-1].write_text("{}\n", encoding="utf-8", newline="\n")
        ensure_required_files_exist(required_paths(False, *required_paths_tuple))

        directory_placeholders_root = Path(required_files_tmp_dir_str) / "directory-placeholders"
        directory_paths_tuple = fixture_paths(directory_placeholders_root)
        for path in directory_paths_tuple:
            path.mkdir(parents=True, exist_ok=True)
        expect_system_exit_contains(
            lambda: ensure_required_files_exist(required_paths(False, *directory_paths_tuple)),
            f"missing required file: {directory_paths_tuple[0]}",
        )

    with tempfile.TemporaryDirectory(prefix="genksyms_crc_selftest_tools_") as tool_tmp_dir_str:
        tool_tmp_dir = Path(tool_tmp_dir_str)
        tool_bin = tool_tmp_dir / "bin"
        tool_bin.mkdir()
        fake_cc = write_fake_executable(tool_bin / "cc")
        fake_zig = write_fake_executable(tool_bin / "zig")
        fake_fallback = write_fake_executable(
            tool_tmp_dir / ".toolchains" / "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2" / "zig"
        )
        fake_nonexec = tool_bin / "not-executable"
        fake_nonexec.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8", newline="\n")

        saved_path = os.environ.get("PATH")
        saved_cc = os.environ.get("CC")
        saved_zig = os.environ.get("ZIG")
        try:
            os.environ["PATH"] = str(tool_bin)
            os.environ.pop("CC", None)
            os.environ.pop("ZIG", None)
            if Path(find_compiler(None)).resolve() != fake_cc.resolve():
                raise SystemExit("GENKSYMS_CRC_SELF_TEST=fail")
            if Path(find_zig(None, tool_tmp_dir / "repo")).resolve() != fake_zig.resolve():
                raise SystemExit("GENKSYMS_CRC_SELF_TEST=fail")

            os.environ["CC"] = str(fake_cc)
            os.environ["ZIG"] = str(fake_zig)
            if Path(find_compiler(None)).resolve() != fake_cc.resolve():
                raise SystemExit("GENKSYMS_CRC_SELF_TEST=fail")
            if Path(find_zig(None, tool_tmp_dir / "repo")).resolve() != fake_zig.resolve():
                raise SystemExit("GENKSYMS_CRC_SELF_TEST=fail")

            expect_system_exit_contains(
                lambda: find_compiler(str(fake_nonexec)),
                f"C compiler not found or not executable: {fake_nonexec}",
            )
            expect_system_exit_contains(
                lambda: find_zig(str(fake_nonexec), tool_tmp_dir / "repo"),
                f"zig not found or not executable: {fake_nonexec}",
            )

            os.environ["CC"] = str(fake_nonexec)
            os.environ["ZIG"] = str(fake_nonexec)
            expect_system_exit_contains(
                lambda: find_compiler(None),
                f"C compiler from CC not found or not executable: {fake_nonexec}",
            )
            expect_system_exit_contains(
                lambda: find_zig(None, tool_tmp_dir / "repo"),
                f"zig from ZIG not found or not executable: {fake_nonexec}",
            )

            os.environ.pop("CC", None)
            os.environ.pop("ZIG", None)
            os.environ["PATH"] = ""
            if Path(find_compiler(str(fake_cc))).resolve() != fake_cc.resolve():
                raise SystemExit("GENKSYMS_CRC_SELF_TEST=fail")
            if Path(find_zig(str(fake_zig), tool_tmp_dir / "repo")).resolve() != fake_zig.resolve():
                raise SystemExit("GENKSYMS_CRC_SELF_TEST=fail")
            if Path(find_zig(None, tool_tmp_dir / "repo")).resolve() != fake_fallback.resolve():
                raise SystemExit("GENKSYMS_CRC_SELF_TEST=fail")
            fake_fallback.chmod(0o644)
            expect_system_exit_contains(
                lambda: find_zig(None, tool_tmp_dir / "repo"),
                f"zig fallback not executable: {fake_fallback}",
            )
        finally:
            if saved_path is None:
                os.environ.pop("PATH", None)
            else:
                os.environ["PATH"] = saved_path
            if saved_cc is None:
                os.environ.pop("CC", None)
            else:
                os.environ["CC"] = saved_cc
            if saved_zig is None:
                os.environ.pop("ZIG", None)
            else:
                os.environ["ZIG"] = saved_zig

    with tempfile.TemporaryDirectory(prefix="genksyms_crc_selftest_missing_tools_") as missing_tool_tmp_dir_str:
        missing_tool_tmp_dir = Path(missing_tool_tmp_dir_str)
        saved_path = os.environ.get("PATH")
        saved_cc = os.environ.get("CC")
        saved_zig = os.environ.get("ZIG")
        try:
            os.environ["PATH"] = ""
            os.environ.pop("CC", None)
            os.environ.pop("ZIG", None)
            expect_system_exit_contains(lambda: find_compiler(None), "C compiler not found")
            expect_system_exit_contains(lambda: find_zig(None, missing_tool_tmp_dir / "repo"), "zig not found")
        finally:
            if saved_path is None:
                os.environ.pop("PATH", None)
            else:
                os.environ["PATH"] = saved_path
            if saved_cc is None:
                os.environ.pop("CC", None)
            else:
                os.environ["CC"] = saved_cc
            if saved_zig is None:
                os.environ.pop("ZIG", None)
            else:
                os.environ["ZIG"] = saved_zig

    with tempfile.TemporaryDirectory(prefix="genksyms_crc_selftest_run_checked_") as run_checked_tmp_dir_str:
        run_checked_tmp_dir = Path(run_checked_tmp_dir_str)
        fake_missing = run_checked_tmp_dir / "missing-tool"
        fake_fail = write_fake_executable(run_checked_tmp_dir / "fail-tool", "#!/bin/sh\nexit 7\n")
        fake_nonexec = run_checked_tmp_dir / "not-executable"
        fake_nonexec.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8", newline="\n")
        fake_directory = run_checked_tmp_dir / "directory-tool"
        fake_directory.mkdir()
        expect_system_exit_contains(
            lambda: run_checked("selftest-missing-tool", [str(fake_missing)]),
            f"selftest-missing-tool failed: missing executable: {fake_missing}",
        )
        expect_system_exit_contains(
            lambda: run_checked("selftest-failing-tool", [str(fake_fail)]),
            f"selftest-failing-tool failed with exit 7: {fake_fail}",
        )
        expect_system_exit_contains(
            lambda: run_checked("selftest-nonexec-tool", [str(fake_nonexec)]),
            f"selftest-nonexec-tool failed to launch {fake_nonexec}: Permission denied",
        )
        expect_system_exit_contains(
            lambda: run_checked("selftest-directory-tool", [str(fake_directory)]),
            f"selftest-directory-tool failed to launch {fake_directory}: Permission denied",
        )

    with tempfile.TemporaryDirectory(prefix="genksyms_crc_selftest_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        left = tmp_dir / "left.json"
        equivalent = tmp_dir / "equivalent.json"
        mismatch = tmp_dir / "mismatch.json"
        reordered = tmp_dir / "reordered.json"
        prefix_mismatch = tmp_dir / "prefix_mismatch.json"
        left_invalid = tmp_dir / "left_invalid.json"
        invalid = tmp_dir / "invalid.json"
        left.write_text(
            '{"cases":[{"crc_hex":"0x1451dab1","input":"int"},{"crc_hex":"0x8cdc1683","input":"x"}]}\n',
            encoding="utf-8",
        )
        equivalent.write_text(
            '{\n  "cases": [ { "input": "int", "crc_hex": "0x1451dab1" }, { "input": "x", "crc_hex": "0x8cdc1683" } ]\n}\n',
            encoding="utf-8",
        )
        mismatch.write_text('{"cases":[{"crc_hex":"0x8cdc1683","input":"x"}]}\n', encoding="utf-8")
        reordered.write_text(
            '{"cases":[{"crc_hex":"0x8cdc1683","input":"x"},{"crc_hex":"0x1451dab1","input":"int"}]}\n',
            encoding="utf-8",
        )
        prefix_mismatch.write_text(
            '{"cases":[{"crc_hex":"0x1451dab1","input":"int"}]}\n',
            encoding="utf-8",
        )
        left_invalid.write_text('{"cases":[', encoding="utf-8")
        invalid.write_text('{"cases":[', encoding="utf-8")
        if summarize_mismatch("abc", "ab") != "shared prefix length 2; left_len=3 right_len=2":
            raise SystemExit("GENKSYMS_CRC_SELF_TEST=fail")
        compare_json("selftest-equal", left, equivalent)
        expect_system_exit_contains(
            lambda: compare_json("selftest-left-invalid-json", left_invalid, equivalent),
            "selftest-left-invalid-json invalid json",
        )
        expect_system_exit_contains(
            lambda: compare_json("selftest-mismatch", left, mismatch),
            "selftest-mismatch mismatch",
        )
        expect_system_exit_contains(
            lambda: compare_json("selftest-mismatch", left, mismatch),
            "first differing byte",
        )
        expect_system_exit_contains(
            lambda: compare_json("selftest-mismatch", left, mismatch),
            "left_len=",
        )
        expect_system_exit_contains(
            lambda: compare_json("selftest-order-sensitive", left, reordered),
            "selftest-order-sensitive mismatch",
        )
        expect_system_exit_contains(
            lambda: compare_json("selftest-prefix-sensitive", left, prefix_mismatch),
            "first differing byte",
        )
        expect_system_exit_contains(
            lambda: compare_json("selftest-invalid-json", left, invalid),
            "selftest-invalid-json invalid json",
        )

    print("GENKSYMS_CRC_SELF_TEST=pass")
    print("GENKSYMS_CRC_SELF_TEST_CASE_COUNT=39")
    return 0


def main() -> int:
    """Parse CLI flags and run refresh, self-test, or cross-implementation comparison."""
    parser = argparse.ArgumentParser(description="Compare bounded genksyms CRC C and Zig outputs.")
    parser.add_argument("--cc", help="C compiler to use")
    parser.add_argument("--zig", help="Path to Zig executable")
    parser.add_argument("--repo-root", help="Repository root containing scripts/zigux and zigux/tests")
    parser.add_argument("--refresh", action="store_true", help="Refresh expected.json from the current C harness output")
    parser.add_argument("--self-test", action="store_true", help="Run fast checker self-tests without compiling tools")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = repo_root_from(Path(__file__), args.repo_root)
    zig_tool, harness, inputs, expected = fixture_paths(root)
    ensure_required_files_exist(required_paths(args.refresh, zig_tool, harness, inputs, expected))

    compiler = find_compiler(args.cc)
    zig = find_zig(args.zig, root)

    with tempfile.TemporaryDirectory(prefix="zigux_genksyms_crc_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        c_actual = tmp_dir / "genksyms_crc.c.actual.json"
        c_repeat = tmp_dir / "genksyms_crc.c.repeat.json"
        zig_actual = tmp_dir / "genksyms_crc.zig.actual.json"
        zig_repeat = tmp_dir / "genksyms_crc.zig.repeat.json"

        compile_run_c(root, tmp_dir, harness, inputs, c_actual, compiler)
        compile_run_zig(root, tmp_dir, zig_tool, inputs, zig_actual, zig)

        if args.refresh:
            expected.write_text(c_actual.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
            print("GENKSYMS_CRC_REFRESH=pass")
            print(f"FIXTURE={expected}")
            return 0

        compare_json("expected-vs-c", expected, c_actual)
        compare_json("expected-vs-zig", expected, zig_actual)
        compare_json("c-vs-zig", c_actual, zig_actual)

        compile_run_c(root, tmp_dir, harness, inputs, c_repeat, compiler)
        compile_run_zig(root, tmp_dir, zig_tool, inputs, zig_repeat, zig)
        compare_json("c-determinism", c_actual, c_repeat)
        compare_json("zig-determinism", zig_actual, zig_repeat)

    print("GENKSYMS_CRC_DIFF=pass")
    print("GENKSYMS_CRC_DETERMINISM=pass")
    print(f"FIXTURE={expected}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())