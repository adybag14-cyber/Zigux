#!/usr/bin/env python3
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
    if explicit:
        return Path(explicit).resolve()
    return script_path.resolve().parents[2]


def fixture_paths(root: Path) -> tuple[Path, Path, Path, Path]:
    fixture_dir = root / "zigux" / "tests" / "fixtures" / "genksyms_crc"
    return (
        root / "scripts" / "zigux" / "genksyms_crc.zig",
        fixture_dir / "genksyms_crc_c_harness.c",
        fixture_dir / "inputs.txt",
        fixture_dir / "expected.json",
    )


def required_paths(refresh: bool, zig_tool: Path, harness: Path, inputs: Path, expected: Path) -> tuple[Path, ...]:
    if refresh:
        return (zig_tool, harness, inputs)
    return (zig_tool, harness, inputs, expected)


def ensure_required_files_exist(paths: tuple[Path, ...]) -> None:
    for path in paths:
        if not path.exists():
            raise SystemExit(f"missing required file: {path}")


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def resolve_tool(candidate: str, missing_message: str) -> str:
    resolved = shutil.which(candidate)
    if resolved:
        return candidate
    raise SystemExit(missing_message)


def find_compiler(explicit: str | None) -> str:
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


def canonicalize_json(text: str) -> str:
    data = json.loads(text)
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def compare_json(label: str, left: Path, right: Path) -> None:
    left_text = left.read_text(encoding="utf-8")
    right_text = right.read_text(encoding="utf-8")
    if canonicalize_json(left_text) != canonicalize_json(right_text):
        raise SystemExit(f"{label} mismatch: {left} != {right}")


def compile_run_c(root: Path, tmp_dir: Path, harness: Path, inputs: Path, actual: Path, compiler: str) -> None:
    exe = tmp_dir / "genksyms-crc-c"
    run([compiler, "-std=c11", "-Wall", "-Wextra", "-o", str(exe), str(harness)], cwd=str(root))
    result = run([str(exe), str(inputs)], cwd=str(root), capture_output=True)
    actual.write_text(result.stdout, encoding="utf-8", newline="\n")


def compile_run_zig(root: Path, tmp_dir: Path, zig_tool: Path, inputs: Path, actual: Path, zig: str) -> None:
    exe = tmp_dir / "genksyms-crc-zig"
    run([zig, "build-exe", str(zig_tool), "-femit-bin=" + str(exe)], cwd=str(root))
    result = run([str(exe), str(inputs)], cwd=str(root), capture_output=True)
    actual.write_text(result.stdout, encoding="utf-8", newline="\n")


def write_fake_executable(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8", newline="\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def expect_system_exit_contains(callback, needle: str) -> None:
    try:
        callback()
    except SystemExit as exc:
        if needle not in str(exc):
            raise SystemExit(f"GENKSYMS_CRC_SELF_TEST=fail: expected {needle!r} in {exc!s}")
        return
    raise SystemExit(f"GENKSYMS_CRC_SELF_TEST=fail: expected SystemExit containing {needle!r}")


def run_self_test() -> int:
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
            if find_compiler(None) != str(fake_cc):
                raise SystemExit("GENKSYMS_CRC_SELF_TEST=fail")
            if find_zig(None, tool_tmp_dir / "repo") != str(fake_zig):
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
            if find_compiler(str(fake_cc)) != str(fake_cc):
                raise SystemExit("GENKSYMS_CRC_SELF_TEST=fail")
            if find_zig(str(fake_zig), tool_tmp_dir / "repo") != str(fake_zig):
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

    with tempfile.TemporaryDirectory(prefix="genksyms_crc_selftest_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        left = tmp_dir / "left.json"
        equivalent = tmp_dir / "equivalent.json"
        mismatch = tmp_dir / "mismatch.json"
        reordered = tmp_dir / "reordered.json"
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
        compare_json("selftest-equal", left, equivalent)
        expect_system_exit_contains(lambda: compare_json("selftest-mismatch", left, mismatch), "selftest-mismatch mismatch")
        expect_system_exit_contains(
            lambda: compare_json("selftest-order-sensitive", left, reordered),
            "selftest-order-sensitive mismatch",
        )

    print("GENKSYMS_CRC_SELF_TEST=pass")
    print("GENKSYMS_CRC_SELF_TEST_CASE_COUNT=21")
    return 0


def main() -> int:
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
