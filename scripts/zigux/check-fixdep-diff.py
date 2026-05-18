#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIFF = ROOT / "scripts" / "zigux" / "artifact_diff.py"
C_FIXDEP = ROOT / "scripts" / "basic" / "fixdep.c"
ZIG_FIXDEP = ROOT / "scripts" / "zigux" / "fixdep.zig"
FIXTURE_DIR = ROOT / "zigux" / "tests" / "fixtures" / "fixdep"
CASES_PATH = FIXTURE_DIR / "cases.json"
EXPECTED_C_FIXDEP = ROOT / "scripts" / "basic" / "fixdep.c"
EXPECTED_ZIG_FIXDEP = ROOT / "scripts" / "zigux" / "fixdep.zig"
EXPECTED_CASES = {
    "sample": {
        "depfile": "sample.d",
        "target": "sample.o",
        "cmdline": "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample.o",
        "expected": "sample_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_multi_target": {
        "depfile": "sample_multi_target.d",
        "target": "module/sample2.o",
        "cmdline": "clang -Iinclude -DZIGUX_MULTI -c zigux/tests/fixtures/fixdep/sample2.c -o module/sample2.o",
        "expected": "sample_multi_target_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_escaped_space": {
        "depfile": "sample_escaped_space.d",
        "target": "sample_escaped_space.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_escaped_space_source.c -o sample_escaped_space.o",
        "expected": "sample_escaped_space_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_escaped_colon": {
        "depfile": "sample_escaped_colon.d",
        "target": "sample_escaped_colon.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c -o sample_escaped_colon.o",
        "expected": "sample_escaped_colon_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_concatenated": {
        "depfile": "sample_concatenated.d",
        "target": "sample_concatenated.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_concatenated_source.c -o sample_concatenated.o",
        "expected": "sample_concatenated_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_dependency_continuation": {
        "depfile": "sample_dependency_continuation.d",
        "target": "sample_dependency_continuation.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_dependency_continuation_source.c -o sample_dependency_continuation.o",
        "expected": "sample_dependency_continuation_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_comment_continuation": {
        "depfile": "sample_comment_continuation.d",
        "target": "sample_comment_continuation.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_comment_continuation_source.c -o sample_comment_continuation.o",
        "expected": "sample_comment_continuation_expected.txt",
        "expected_exit_code": 0,
    },
    "sample_comment_only": {
        "depfile": "sample_comment_only.d",
        "target": "sample_comment_only.o",
        "cmdline": "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only.o",
        "expected": "sample_comment_only_expected.txt",
        "expected_stderr": "sample_comment_only_expected.stderr.txt",
        "expected_exit_code": 1,
    },
    "sample_comment_only_stdout_full": {
        "depfile": "sample_comment_only.d",
        "target": "sample_comment_only_stdout_full.o",
        "cmdline": "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only_stdout_full.o",
        "expected": "sample_output_write_expected.txt",
        "expected_stderr": "sample_comment_only_expected.stderr.txt",
        "expected_exit_code": 1,
        "stdout_mode": "dev_full",
    },
    "sample_missing_dep": {
        "depfile": "sample_missing_dep.d",
        "target": "sample_missing_dep.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep.o",
        "expected": "sample_missing_dep_expected.txt",
        "expected_stderr": "sample_missing_dep_expected.stderr.txt",
        "expected_exit_code": 2,
    },
    "sample_missing_dep_stdout_full": {
        "depfile": "sample_missing_dep.d",
        "target": "sample_missing_dep_stdout_full.o",
        "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep_stdout_full.o",
        "expected": "sample_output_write_expected.txt",
        "expected_stderr": "sample_missing_dep_expected.stderr.txt",
        "expected_exit_code": 2,
        "stdout_mode": "dev_full",
    },
    "sample_output_write": {
        "depfile": "sample.d",
        "target": "sample_output_write.o",
        "cmdline": "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_output_write.o",
        "expected": "sample_output_write_expected.txt",
        "expected_stderr": "sample_output_write_expected.stderr.txt",
        "expected_exit_code": 1,
        "stdout_mode": "dev_full",
    },
}
EXPECTED_CASE_ORDER = list(EXPECTED_CASES)
EXPECTED_FIXTURE_FILES = frozenset(
    {
        "cases.json",
        r"escaped\ space-config.h",
        "sample-config.h",
        "sample.c",
        "sample.d",
        "sample.h",
        "sample.rmeta",
        "sample2-config.h",
        "sample2.c",
        "sample2.so",
        "sample_comment_continuation.d",
        "sample_comment_continuation_dep.so",
        "sample_comment_continuation_expected.txt",
        "sample_comment_continuation_source.rmeta",
        "sample_comment_only.d",
        "sample_comment_only_expected.stderr.txt",
        "sample_comment_only_expected.txt",
        "sample_concatenated.d",
        "sample_concatenated_dep.h",
        "sample_concatenated_expected.txt",
        "sample_concatenated_source.c",
        "sample_concatenated_temp.c",
        "sample_concatenated_temp_dep.h",
        "sample_dependency_continuation.d",
        "sample_dependency_continuation_expected.txt",
        "sample_escaped_colon.d",
        "sample_escaped_colon_expected.txt",
        "sample_escaped_colon_source.c",
        "sample_escaped_space.d",
        "sample_escaped_space_expected.txt",
        "sample_escaped_space_source.c",
        "sample_expected.txt",
        "sample_missing_dep.d",
        "sample_missing_dep_expected.stderr.txt",
        "sample_missing_dep_expected.txt",
        "sample_missing_dep_source.c",
        "sample_multi_target.d",
        "sample_multi_target_expected.txt",
        "sample_output_write_expected.stderr.txt",
        "sample_output_write_expected.txt",
        "shared#config.h",
        "shared:config.h",
    }
)


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def run_capture(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=False, text=True, capture_output=True, **kwargs)


def run_redirected(
    cmd: list[str],
    *,
    cwd: str,
    stdout_mode: str | None = None,
) -> subprocess.CompletedProcess[str]:
    if stdout_mode is None:
        return run_capture(cmd, cwd=cwd)
    if stdout_mode != "dev_full":
        raise ValueError(f"unsupported stdout mode: {stdout_mode}")

    with open("/dev/full", "w", encoding="utf-8") as stdout_handle:
        result = subprocess.run(
            cmd,
            check=False,
            text=True,
            stdout=stdout_handle,
            stderr=subprocess.PIPE,
            cwd=cwd,
        )
    return subprocess.CompletedProcess(
        args=result.args,
        returncode=result.returncode,
        stdout="",
        stderr=result.stderr or "",
    )


def find_compiler(explicit: str | None) -> str:
    if explicit:
        return explicit
    for candidate in ("gcc", "cc", "clang"):
        path = shutil.which(candidate)
        if path:
            return path
    raise FileNotFoundError("no C compiler found on PATH")


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    env = os.environ.get("ZIG")
    if env:
        return env
    path = shutil.which("zig")
    if path:
        return path
    fallback = ROOT.parent / "toolchains" / "zig-master" / "current" / "zig.exe"
    if fallback.exists():
        return str(fallback)
    raise FileNotFoundError("no zig executable found; set --zig or ZIG")


def load_cases(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_tool_sources(c_fixdep: Path, zig_fixdep: Path) -> None:
    if c_fixdep != EXPECTED_C_FIXDEP:
        raise ValueError(f"fixdep:c_tool={c_fixdep},expected={EXPECTED_C_FIXDEP}")
    if zig_fixdep != EXPECTED_ZIG_FIXDEP:
        raise ValueError(f"fixdep:zig_tool={zig_fixdep},expected={EXPECTED_ZIG_FIXDEP}")


def validate_fixture_inventory(
    fixture_dir: Path = FIXTURE_DIR,
    expected_fixtures: frozenset[str] = EXPECTED_FIXTURE_FILES,
) -> None:
    actual_files = {path.name for path in fixture_dir.iterdir() if path.is_file()}
    missing = sorted(expected_fixtures - actual_files)
    unexpected = sorted(actual_files - expected_fixtures)
    if missing:
        raise FileNotFoundError(f"{fixture_dir}:missing_fixtures:{','.join(missing)}")
    if unexpected:
        raise ValueError(f"{fixture_dir}:unexpected_fixtures:{','.join(unexpected)}")


def validate_cases(cases: object) -> list[dict[str, object]]:
    if not isinstance(cases, list) or not cases:
        raise ValueError(f"{CASES_PATH}:expected_non_empty_json_list")

    validated: list[dict[str, object]] = []
    seen_names: list[str] = []
    seen_name_set: set[str] = set()
    for index, raw_case in enumerate(cases):
        if not isinstance(raw_case, dict):
            raise ValueError(f"{CASES_PATH}:entry[{index}]:expected_json_object")

        name = raw_case.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError(f"{CASES_PATH}:entry[{index}]:missing_non_empty_name")
        if name in seen_name_set:
            raise ValueError(f"{CASES_PATH}:duplicate_name:{name}")
        seen_name_set.add(name)
        seen_names.append(name)

        expected_case = EXPECTED_CASES.get(name)
        if expected_case is None:
            raise ValueError(f"{CASES_PATH}:unexpected_name:{name}")

        expected_fields = {"name", *expected_case.keys()}
        unexpected_fields = sorted(set(raw_case) - expected_fields)
        if unexpected_fields:
            raise ValueError(f"{CASES_PATH}:{name}:unexpected_field:{unexpected_fields[0]}")

        validated_case = dict(raw_case)
        depfile = validated_case.get("depfile")
        if not isinstance(depfile, str) or not depfile:
            raise ValueError(f"{CASES_PATH}:{name}:missing_non_empty_depfile")

        expected_stdout_name = validated_case.get("expected_stdout", validated_case.get("expected"))
        if not isinstance(expected_stdout_name, str) or not expected_stdout_name:
            raise ValueError(f"{CASES_PATH}:{name}:missing_expected_output")

        expected_exit_code = int(validated_case.get("expected_exit_code", 0))
        if expected_exit_code != 0:
            expected_stderr_name = validated_case.get("expected_stderr")
            if not isinstance(expected_stderr_name, str) or not expected_stderr_name:
                raise ValueError(f"{CASES_PATH}:{name}:missing_expected_stderr")

        stdout_mode = validated_case.get("stdout_mode")
        if stdout_mode not in (None, "dev_full"):
            raise ValueError(f"{CASES_PATH}:{name}:unsupported_stdout_mode:{stdout_mode!r}")

        for field_name, expected_value in expected_case.items():
            actual_value = validated_case.get(field_name, 0 if field_name == "expected_exit_code" else None)
            if actual_value != expected_value:
                raise ValueError(
                    f"{CASES_PATH}:{name}:{field_name}={actual_value!r},expected={expected_value!r}"
                )

        if not (FIXTURE_DIR / depfile).exists():
            raise FileNotFoundError(f"{CASES_PATH}:missing_depfile:{depfile}")
        if not (FIXTURE_DIR / expected_stdout_name).exists():
            raise FileNotFoundError(f"{CASES_PATH}:missing_expected_output:{expected_stdout_name}")
        if expected_exit_code != 0 and not (FIXTURE_DIR / expected_stderr_name).exists():
            raise FileNotFoundError(f"{CASES_PATH}:missing_expected_stderr:{expected_stderr_name}")

        validated.append(validated_case)

    if seen_names != EXPECTED_CASE_ORDER:
        raise ValueError(f"{CASES_PATH}:case_order={seen_names!r},expected={EXPECTED_CASE_ORDER!r}")

    if len(validated) != len(EXPECTED_CASES):
        raise ValueError(f"{CASES_PATH}:count={len(validated)},expected={len(EXPECTED_CASES)}")

    missing_names = sorted(set(EXPECTED_CASES) - seen_name_set)
    if missing_names:
        raise ValueError(f"{CASES_PATH}:missing_name:{missing_names[0]}")

    return validated


def expect_failure(label: str, callback, expected_message: str) -> None:
    try:
        callback()
    except (ValueError, FileNotFoundError) as exc:
        actual_message = str(exc)
        if actual_message != expected_message:
            raise SystemExit(
                f"fixdep:self-test:{label}:expected={expected_message!r}:actual={actual_message!r}"
            ) from exc
        return
    raise SystemExit(f"fixdep:self-test:{label}:missing_failure:{expected_message!r}")


def copy_valid_cases(valid_cases: list[dict[str, object]]) -> list[dict[str, object]]:
    return [dict(case) for case in valid_cases]


def find_case(valid_cases: list[dict[str, object]], name: str) -> dict[str, object]:
    for case in valid_cases:
        case_name = case.get("name")
        if case_name == name:
            return case
    raise KeyError(name)


def run_self_test() -> int:
    global FIXTURE_DIR

    validate_fixture_inventory()
    valid_cases = validate_cases(load_cases(CASES_PATH))
    validate_tool_sources(C_FIXDEP, ZIG_FIXDEP)

    expect_failure(
        "non_list_cases",
        lambda: validate_cases({"cases": valid_cases}),
        f"{CASES_PATH}:expected_non_empty_json_list",
    )
    expect_failure(
        "empty_cases",
        lambda: validate_cases([]),
        f"{CASES_PATH}:expected_non_empty_json_list",
    )

    non_object_cases = copy_valid_cases(valid_cases)
    non_object_cases[0] = "sample"
    expect_failure(
        "non_object_case_entry",
        lambda: validate_cases(non_object_cases),
        f"{CASES_PATH}:entry[0]:expected_json_object",
    )

    missing_name_cases = copy_valid_cases(valid_cases)
    missing_name_cases[0].pop("name", None)
    expect_failure(
        "missing_case_name",
        lambda: validate_cases(missing_name_cases),
        f"{CASES_PATH}:entry[0]:missing_non_empty_name",
    )

    duplicate_name_cases = copy_valid_cases(valid_cases)
    duplicate_name_cases[1]["name"] = duplicate_name_cases[0]["name"]
    expect_failure(
        "duplicate_name",
        lambda: validate_cases(duplicate_name_cases),
        f"{CASES_PATH}:duplicate_name:{valid_cases[0]['name']}",
    )

    unexpected_name_cases = copy_valid_cases(valid_cases)
    unexpected_name_cases[0]["name"] = "unexpected_fixdep_case"
    expect_failure(
        "unexpected_name",
        lambda: validate_cases(unexpected_name_cases),
        f"{CASES_PATH}:unexpected_name:unexpected_fixdep_case",
    )

    unexpected_field_cases = copy_valid_cases(valid_cases)
    find_case(unexpected_field_cases, "sample")["unexpected_field"] = "unexpected"
    expect_failure(
        "unexpected_field",
        lambda: validate_cases(unexpected_field_cases),
        f"{CASES_PATH}:sample:unexpected_field:unexpected_field",
    )

    reordered_cases = copy_valid_cases(valid_cases)
    reordered_cases[0], reordered_cases[1] = reordered_cases[1], reordered_cases[0]
    expect_failure(
        "reordered_case_packet",
        lambda: validate_cases(reordered_cases),
        f"{CASES_PATH}:case_order="
        f"{[case['name'] for case in reordered_cases]!r},expected={EXPECTED_CASE_ORDER!r}",
    )

    missing_stderr_cases = copy_valid_cases(valid_cases)
    find_case(missing_stderr_cases, "sample_comment_only").pop("expected_stderr", None)
    expect_failure(
        "missing_expected_stderr",
        lambda: validate_cases(missing_stderr_cases),
        f"{CASES_PATH}:sample_comment_only:missing_expected_stderr",
    )

    missing_expected_output_cases = copy_valid_cases(valid_cases)
    find_case(missing_expected_output_cases, "sample").pop("expected", None)
    expect_failure(
        "missing_expected_output_field",
        lambda: validate_cases(missing_expected_output_cases),
        f"{CASES_PATH}:sample:missing_expected_output",
    )

    mismatched_target_cases = copy_valid_cases(valid_cases)
    find_case(mismatched_target_cases, "sample")["target"] = "sample-wrong.o"
    expect_failure(
        "mismatched_target_field",
        lambda: validate_cases(mismatched_target_cases),
        f"{CASES_PATH}:sample:target='sample-wrong.o',expected='sample.o'",
    )

    with tempfile.TemporaryDirectory(prefix="zigux_fixdep_missing_output_fixture_") as tmp_dir:
        fixture_dir = Path(tmp_dir)
        for fixture_path in FIXTURE_DIR.iterdir():
            if fixture_path.name == "sample_expected.txt":
                continue
            shutil.copy2(fixture_path, fixture_dir / fixture_path.name)

        original_fixture_dir = FIXTURE_DIR
        FIXTURE_DIR = fixture_dir
        try:
            expect_failure(
                "missing_expected_output_fixture",
                lambda: validate_cases(valid_cases),
                f"{CASES_PATH}:missing_expected_output:sample_expected.txt",
            )
        finally:
            FIXTURE_DIR = original_fixture_dir
    with tempfile.TemporaryDirectory(prefix="zigux_fixdep_missing_stderr_fixture_") as tmp_dir:
        fixture_dir = Path(tmp_dir)
        for fixture_path in FIXTURE_DIR.iterdir():
            if fixture_path.name == "sample_comment_only_expected.stderr.txt":
                continue
            shutil.copy2(fixture_path, fixture_dir / fixture_path.name)

        original_fixture_dir = FIXTURE_DIR
        FIXTURE_DIR = fixture_dir
        try:
            expect_failure(
                "missing_expected_stderr_fixture",
                lambda: validate_cases(valid_cases),
                f"{CASES_PATH}:missing_expected_stderr:sample_comment_only_expected.stderr.txt",
            )
        finally:
            FIXTURE_DIR = original_fixture_dir

    missing_depfile_field_cases = copy_valid_cases(valid_cases)
    find_case(missing_depfile_field_cases, "sample").pop("depfile", None)
    expect_failure(
        "missing_non_empty_depfile",
        lambda: validate_cases(missing_depfile_field_cases),
        f"{CASES_PATH}:sample:missing_non_empty_depfile",
    )

    unsupported_stdout_mode_cases = copy_valid_cases(valid_cases)
    find_case(unsupported_stdout_mode_cases, "sample_comment_only_stdout_full")["stdout_mode"] = "pipe_full"
    expect_failure(
        "unsupported_stdout_mode",
        lambda: validate_cases(unsupported_stdout_mode_cases),
        f"{CASES_PATH}:sample_comment_only_stdout_full:unsupported_stdout_mode:'pipe_full'",
    )

    with tempfile.TemporaryDirectory(prefix="zigux_fixdep_missing_depfile_fixture_") as tmp_dir:
        fixture_dir = Path(tmp_dir)
        for fixture_path in FIXTURE_DIR.iterdir():
            if fixture_path.name == "sample.d":
                continue
            shutil.copy2(fixture_path, fixture_dir / fixture_path.name)

        original_fixture_dir = FIXTURE_DIR
        FIXTURE_DIR = fixture_dir
        try:
            expect_failure(
                "missing_depfile",
                lambda: validate_cases(valid_cases),
                f"{CASES_PATH}:missing_depfile:sample.d",
            )
        finally:
            FIXTURE_DIR = original_fixture_dir

    with tempfile.TemporaryDirectory(prefix="zigux_fixdep_fixture_inventory_ok_") as tmp_dir:
        fixture_dir = Path(tmp_dir)
        (fixture_dir / "fixture_a.txt").write_text("fixture\n", encoding="utf-8")
        (fixture_dir / r"escaped\ space-config.h").write_text("fixture\n", encoding="utf-8")
        validate_fixture_inventory(
            fixture_dir,
            frozenset({"fixture_a.txt", r"escaped\ space-config.h"}),
        )

    with tempfile.TemporaryDirectory(prefix="zigux_fixdep_fixture_inventory_missing_") as tmp_dir:
        fixture_dir = Path(tmp_dir)
        (fixture_dir / "fixture_a.txt").write_text("fixture\n", encoding="utf-8")
        expect_failure(
            "missing_escaped_space_fixture",
            lambda: validate_fixture_inventory(
                fixture_dir,
                frozenset({"fixture_a.txt", r"escaped\ space-config.h"}),
            ),
            f"{fixture_dir}:missing_fixtures:escaped\\ space-config.h",
        )

    with tempfile.TemporaryDirectory(prefix="zigux_fixdep_fixture_inventory_unexpected_") as tmp_dir:
        fixture_dir = Path(tmp_dir)
        (fixture_dir / "fixture_a.txt").write_text("fixture\n", encoding="utf-8")
        (fixture_dir / r"escaped\ space-config.h").write_text("fixture\n", encoding="utf-8")
        (fixture_dir / "unexpected.txt").write_text("fixture\n", encoding="utf-8")
        expect_failure(
            "unexpected_fixture_inventory",
            lambda: validate_fixture_inventory(
                fixture_dir,
                frozenset({"fixture_a.txt", r"escaped\ space-config.h"}),
            ),
            f"{fixture_dir}:unexpected_fixtures:unexpected.txt",
        )

    expect_failure(
        "explicit_c_tool_drift",
        lambda: validate_tool_sources(C_FIXDEP.with_name("fixdep-mismatch.c"), ZIG_FIXDEP),
        f"fixdep:c_tool={C_FIXDEP.with_name('fixdep-mismatch.c')},expected={EXPECTED_C_FIXDEP}",
    )
    expect_failure(
        "explicit_zig_tool_drift",
        lambda: validate_tool_sources(C_FIXDEP, ZIG_FIXDEP.with_name("fixdep-mismatch.zig")),
        f"fixdep:zig_tool={ZIG_FIXDEP.with_name('fixdep-mismatch.zig')},expected={EXPECTED_ZIG_FIXDEP}",
    )

    print("FIXDEP_SELF_TEST=pass")
    print(f"FIXDEP_SELF_TEST_CASE_COUNT={len(valid_cases) + 19}")
    return 0


def windows_to_wsl(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(":").lower()
    tail = resolved.as_posix().split(":", 1)[1]
    return f"/mnt/{drive}{tail}"


def compile_run_c_wsl(
    tmp_dir: Path,
    exe: Path,
    compiler: str,
    depfile: Path,
    target: str,
    cmdline: str,
    stdout_mode: str | None = None,
) -> subprocess.CompletedProcess[str]:
    script_path = tmp_dir / "run_fixdep_c.sh"
    stdout_path = tmp_dir / "fixdep.c.actual.txt"
    stderr_path = tmp_dir / "fixdep.c.actual.stderr.txt"
    rc_path = tmp_dir / "fixdep.c.actual.rc"
    stdout_redirect = windows_to_wsl(stdout_path) if stdout_mode is None else "/dev/full"
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        " ".join(
            [
                shlex.quote(compiler),
                "-std=gnu11",
                "-Wall",
                "-Wextra",
                "-I",
                shlex.quote(windows_to_wsl(ROOT / "scripts" / "include")),
                "-o",
                shlex.quote(windows_to_wsl(exe)),
                shlex.quote(windows_to_wsl(C_FIXDEP)),
            ]
        ),
        " ".join(
            [
                shlex.quote(windows_to_wsl(exe)),
                shlex.quote(windows_to_wsl(depfile)),
                shlex.quote(target),
                shlex.quote(cmdline),
            ]
        ),
        "rc=$?",
        f"printf '%s' \"$rc\" > {shlex.quote(windows_to_wsl(rc_path))}",
    ]
    lines[3] += f" > {stdout_redirect} 2> {shlex.quote(windows_to_wsl(stderr_path))} || true"
    script_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    run(["wsl", "bash", windows_to_wsl(script_path)], cwd=str(ROOT))
    if stdout_mode is None:
        stdout_text = stdout_path.read_text(encoding="utf-8")
    else:
        stdout_text = ""
    return subprocess.CompletedProcess(
        args=[str(exe), str(depfile), target, cmdline],
        returncode=int(rc_path.read_text(encoding="utf-8") or "0"),
        stdout=stdout_text,
        stderr=stderr_path.read_text(encoding="utf-8"),
    )


def compile_run_c(
    tmp_dir: Path,
    compiler: str,
    depfile: Path,
    target: str,
    cmdline: str,
    stdout_mode: str | None = None,
) -> subprocess.CompletedProcess[str]:
    exe = tmp_dir / ("fixdep-c.exe" if os.name == "nt" else "fixdep-c")
    if os.name == "nt" and shutil.which("wsl"):
        return compile_run_c_wsl(tmp_dir, exe, compiler, depfile, target, cmdline, stdout_mode)

    compile_cmd = [
        compiler,
        "-std=gnu11",
        "-Wall",
        "-Wextra",
        "-I",
        str(ROOT / "scripts" / "include"),
        "-o",
        str(exe),
        str(C_FIXDEP),
    ]
    run(compile_cmd, cwd=str(ROOT))
    return run_redirected([str(exe), str(depfile), target, cmdline], cwd=str(ROOT), stdout_mode=stdout_mode)


def run_zig(
    zig: str,
    tmp_dir: Path,
    depfile: Path,
    target: str,
    cmdline: str,
    stdout_mode: str | None = None,
) -> subprocess.CompletedProcess[str]:
    exe = tmp_dir / ("fixdep-zig.exe" if os.name == "nt" else "fixdep-zig")
    build_cmd = [zig, "build-exe", str(ZIG_FIXDEP), "-femit-bin=" + str(exe)]
    run(build_cmd, cwd=str(ROOT))
    return run_redirected([str(exe), str(depfile), target, cmdline], cwd=str(ROOT), stdout_mode=stdout_mode)


def compare_returncode(label: str, expected: int, actual: int) -> None:
    if expected != actual:
        raise RuntimeError(f"{label} return code mismatch: expected {expected}, got {actual}")


def write_result(stdout_path: Path, stderr_path: Path, result: subprocess.CompletedProcess[str]) -> None:
    stdout_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")


def diff_text(expected: Path, actual: Path) -> None:
    run([sys.executable, str(ARTIFACT_DIFF), "--mode", "text", str(expected), str(actual)], cwd=str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="Check bounded fixdep C/Zig artifact parity.")
    parser.add_argument("--refresh", action="store_true", help="Refresh the committed expected output from current C fixdep.")
    parser.add_argument("--cc", help="Explicit C compiler path to use.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in fixdep manifest, fixture-inventory, and explicit-tool checks.")
    parser.add_argument("--zig", help="Explicit zig executable path to use.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    compiler = args.cc or os.environ.get("CC") or ("gcc" if os.name == "nt" and shutil.which("wsl") else find_compiler(None))
    zig = find_zig(args.zig)
    validate_fixture_inventory()
    cases = validate_cases(load_cases(CASES_PATH))
    validate_tool_sources(C_FIXDEP, ZIG_FIXDEP)

    for case in cases:
        depfile = FIXTURE_DIR / case["depfile"]
        expected_stdout = FIXTURE_DIR / case.get("expected_stdout", case["expected"])
        expected_stderr_name = case.get("expected_stderr")
        expected_stderr = FIXTURE_DIR / expected_stderr_name if expected_stderr_name else None
        expected_exit_code = int(case.get("expected_exit_code", 0))
        stdout_mode = case.get("stdout_mode")
        target = case["target"]
        cmdline = case["cmdline"]

        with tempfile.TemporaryDirectory(prefix=f"zigux_fixdep_{case['name']}_") as tmp_dir_str:
            tmp_dir = Path(tmp_dir_str)
            c_actual = tmp_dir / "fixdep.c.actual.txt"
            c_actual_stderr = tmp_dir / "fixdep.c.actual.stderr.txt"
            c_repeat = tmp_dir / "fixdep.c.repeat.txt"
            c_repeat_stderr = tmp_dir / "fixdep.c.repeat.stderr.txt"
            zig_actual = tmp_dir / "fixdep.zig.actual.txt"
            zig_actual_stderr = tmp_dir / "fixdep.zig.actual.stderr.txt"
            zig_repeat = tmp_dir / "fixdep.zig.repeat.txt"
            zig_repeat_stderr = tmp_dir / "fixdep.zig.repeat.stderr.txt"
            implicit_expected_stderr = tmp_dir / "fixdep.expected.stderr.txt"
            implicit_expected_stderr.write_text("", encoding="utf-8")
            expected_stderr_path = expected_stderr or implicit_expected_stderr

            c_result = compile_run_c(tmp_dir, compiler, depfile, target, cmdline, stdout_mode)
            zig_result = run_zig(zig, tmp_dir, depfile, target, cmdline, stdout_mode)
            write_result(c_actual, c_actual_stderr, c_result)
            write_result(zig_actual, zig_actual_stderr, zig_result)

            if args.refresh:
                expected_stdout.write_text(c_result.stdout, encoding="utf-8")
                if expected_stderr is not None:
                    expected_stderr.write_text(c_result.stderr, encoding="utf-8")
                continue

            c_repeat_result = compile_run_c(tmp_dir, compiler, depfile, target, cmdline, stdout_mode)
            zig_repeat_result = run_zig(zig, tmp_dir, depfile, target, cmdline, stdout_mode)
            write_result(c_repeat, c_repeat_stderr, c_repeat_result)
            write_result(zig_repeat, zig_repeat_stderr, zig_repeat_result)

            compare_returncode(f"{case['name']} C", expected_exit_code, c_result.returncode)
            compare_returncode(f"{case['name']} Zig", expected_exit_code, zig_result.returncode)
            compare_returncode(f"{case['name']} C-vs-Zig", c_result.returncode, zig_result.returncode)
            compare_returncode(f"{case['name']} C repeat", c_result.returncode, c_repeat_result.returncode)
            compare_returncode(f"{case['name']} Zig repeat", zig_result.returncode, zig_repeat_result.returncode)

            diff_text(expected_stdout, c_actual)
            diff_text(expected_stdout, zig_actual)
            diff_text(c_actual, zig_actual)
            diff_text(c_actual, c_repeat)
            diff_text(zig_actual, zig_repeat)
            diff_text(c_actual_stderr, zig_actual_stderr)
            diff_text(c_actual_stderr, c_repeat_stderr)
            diff_text(zig_actual_stderr, zig_repeat_stderr)
            diff_text(expected_stderr_path, c_actual_stderr)
            diff_text(expected_stderr_path, zig_actual_stderr)

    if args.refresh:
        print("FIXDEP_REFRESH=pass")
        print(f"FIXTURE_DIR={FIXTURE_DIR}")
    else:
        print("FIXDEP_DIFF=pass")
        print("FIXDEP_DETERMINISM=pass")
        print(f"FIXTURE_DIR={FIXTURE_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
