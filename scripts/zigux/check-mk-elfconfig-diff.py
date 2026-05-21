#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
ZIG_TOOL = ROOT / "scripts" / "zigux" / "mk_elfconfig.zig"
FD_TRAILING_ZIG_TOOL = ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_trailing_bytes_test.zig"
FD_EXACT_CURSOR_ZIG_TOOL = ROOT / "scripts" / "zigux" / "mk_elfconfig_fd_exact_cursor_test.zig"
FIXTURE_DIR = ROOT / "zigux" / "tests" / "fixtures" / "mk_elfconfig"
CASES_PATH = FIXTURE_DIR / "cases.json"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"

EXPECTED_CASES = {
    "elf32": {"input": "elf32.hex", "expected": "elf32_expected.json"},
    "elf32_trailing": {"input": "elf32_trailing.hex", "expected": "elf32_trailing_expected.json"},
    "elf64": {"input": "elf64.hex", "expected": "elf64_expected.json"},
    "elf64_trailing": {"input": "elf64_trailing.hex", "expected": "elf64_trailing_expected.json"},
    "empty": {"input": "empty.hex", "expected": "empty_expected.json"},
    "invalid_class": {"input": "invalid_class.hex", "expected": "invalid_class_expected.json"},
    "invalid_class_trailing": {
        "input": "invalid_class_trailing.hex",
        "expected": "invalid_class_trailing_expected.json",
    },
    "not_elf": {"input": "not_elf.hex", "expected": "not_elf_expected.json"},
    "not_elf_trailing": {"input": "not_elf_trailing.hex", "expected": "not_elf_trailing_expected.json"},
    "truncated": {"input": "truncated.hex", "expected": "truncated_expected.json"},
}
EXPECTED_CASE_ORDER = list(EXPECTED_CASES)
EXPECTED_FIXTURE_FILES = frozenset(
    {
        "cases.json",
        "elf32.hex",
        "elf32_expected.json",
        "elf32_trailing.hex",
        "elf32_trailing_expected.json",
        "elf64.hex",
        "elf64_expected.json",
        "elf64_trailing.hex",
        "elf64_trailing_expected.json",
        "empty.hex",
        "empty_expected.json",
        "invalid_class.hex",
        "invalid_class_expected.json",
        "invalid_class_trailing.hex",
        "invalid_class_trailing_expected.json",
        "not_elf.hex",
        "not_elf_expected.json",
        "not_elf_trailing.hex",
        "not_elf_trailing_expected.json",
        "truncated.hex",
        "truncated_expected.json",
    }
)
EXPECTED_RESULT_KEYS = frozenset({"stdout", "stderr", "exit_code"})
EXPECTED_ZIG_MARKERS = {
    "fd_entrypoint": "pub fn runMkElfconfigFromFd(",
    "fd_empty_eof": 'test "fd-backed empty input exits with stderr at EOF" {',
    "fd_exact_elf32": 'test "fd-backed exact 32-bit ELF header exits with stdout at EOF" {',
    "fd_exact_elf64": 'test "fd-backed exact 64-bit ELF header exits with stdout at EOF" {',
    "fd_exact_truncated": 'test "fd-backed exact truncated header exits with stderr at EOF" {',
    "fd_exact_invalid_class": 'test "fd-backed exact invalid-class header exits silently at EOF" {',
    "fd_exact_not_elf": 'test "fd-backed exact non-ELF header exits with stderr at EOF" {',
    "elf32_trailing_direct": 'test "classifies 32-bit ELF input even when trailing bytes are present" {',
    "elf64_trailing_direct": 'test "classifies valid ELF input even when trailing bytes are present" {',
    "elf32_trailing_helper_stdout": 'test "32-bit ELF input with trailing bytes exits with stdout" {',
    "elf64_trailing_helper_stdout": 'test "valid ELF input with trailing bytes exits with stdout" {',
    "invalid_class_trailing": 'test "classifies unsupported ELF class with trailing bytes silently" {',
    "invalid_class_trailing_helper": 'test "invalid class with trailing bytes exits without stderr" {',
    "not_elf_trailing_direct": 'test "classifies non-ELF input with trailing bytes" {',
    "not_elf_trailing_helper": 'test "non-ELF input with trailing bytes exits with stderr" {',
    "partial_read_failure": 'test "readHeader keeps partial bytes when a later read fails" {',
    "readheader_exact_elf32_failure": 'test "readHeader keeps exact 32-bit ELF bytes when the next read would fail" {',
    "readheader_exact_elf64_failure": 'test "readHeader keeps exact 64-bit ELF bytes when the next read would fail" {',
    "readheader_exact_invalid_class_failure": 'test "readHeader keeps exact invalid-class bytes when the next read would fail" {',
    "readheader_exact_not_elf_failure": 'test "readHeader keeps exact non-ELF bytes when the next read would fail" {',
    "readheader_near_full_failure": 'test "readHeader keeps fifteen bytes when a later read fails one byte before the full header" {',
    "readheader_near_full_eof": 'test "readHeader preserves fifteen-byte count at EOF one byte before the full header" {',
    "readheader_split_fill": 'test "readHeader stops after filling the first ELF header across split reads" {',
    "readheader_split_truncated_count": 'test "readHeader preserves truncated byte count across split reads" {',
    "readheader_immediate_error": 'test "readHeader treats an immediate read error like truncated input" {',
    "readheader_truncated_count": 'test "readHeader reports the exact truncated byte count" {',
    "readheader_zero_eof": 'test "readHeader returns zero bytes on immediate EOF" {',
    "render_truncated": 'test "renders truncated error" {',
    "render_not_elf": 'test "renders non-ELF error" {',
    "render_invalid_class": 'test "renders invalid class silently" {',
    "split_trailing_elf64": 'test "split-read ELF input exits with stdout and ignores trailing bytes" {',
    "split_trailing_elf32": 'test "split-read 32-bit ELF input exits with stdout and ignores trailing bytes" {',
    "split_exact_elf32_first_chunk": 'test "split-read exact 32-bit ELF header in first chunk exits after one read" {',
    "split_exact_elf64_first_chunk": 'test "split-read exact 64-bit ELF header in first chunk exits after one read" {',
    "split_exact_invalid_class_first_chunk": 'test "split-read exact invalid-class header in first chunk exits after one read" {',
    "split_exact_not_elf_first_chunk": 'test "split-read exact non-ELF header in first chunk exits after one read" {',
    "split_exact_elf32": 'test "split-read exact 32-bit ELF header exits with stdout at EOF" {',
    "split_exact_elf64": 'test "split-read exact 64-bit ELF header exits with stdout at EOF" {',
    "split_exact_elf32_failure": 'test "split-read exact 32-bit ELF header ignores later read failure and exits with stdout" {',
    "split_exact_elf64_failure": 'test "split-read exact 64-bit ELF header ignores later read failure and exits with stdout" {',
    "split_exact_invalid_class": 'test "split-read exact invalid-class header exits silently at EOF" {',
    "split_exact_invalid_class_failure": 'test "split-read exact invalid-class header ignores later read failure and exits silently" {',
    "split_empty_eof": 'test "split-read empty input exits with stderr after immediate EOF" {',
    "split_trailing_invalid_class": 'test "split-read invalid class exits silently and ignores trailing bytes" {',
    "split_trailing_not_elf": 'test "split-read non-ELF input exits with stderr and ignores trailing bytes" {',
    "split_exact_not_elf": 'test "split-read exact non-ELF header exits with stderr at EOF" {',
    "split_exact_not_elf_failure": 'test "split-read exact non-ELF header ignores later read failure and exits with stderr" {',
    "split_truncated_eof": 'test "split-read truncated input exits with stderr after final EOF read" {',
    "split_near_full_eof": 'test "split-read one byte short of a full header exits with truncated stderr at EOF" {',
    "split_truncated_failure": 'test "split-read truncated input keeps stderr when a later read fails" {',
}
EXPECTED_FD_TRAILING_ZIG_MARKERS = {
    "fd_trailing_elf32": 'test "fd-backed trailing 32-bit ELF input exits with stdout" {',
    "fd_trailing_elf64": 'test "fd-backed trailing 64-bit ELF input exits with stdout" {',
    "fd_trailing_invalid_class": 'test "fd-backed trailing invalid-class input exits silently" {',
    "fd_trailing_not_elf": 'test "fd-backed trailing non-ELF input exits with stderr" {',
}
EXPECTED_FD_EXACT_CURSOR_ZIG_MARKERS = {
    "fd_exact_cursor_empty": 'test "fd-backed exact empty input leaves the cursor at zero" {',
    "fd_exact_cursor_truncated": 'test "fd-backed exact truncated input leaves the cursor at the truncated byte count" {',
    "fd_exact_cursor_elf32": 'test "fd-backed exact 32-bit ELF input leaves the cursor at the full header" {',
    "fd_exact_cursor_elf64": 'test "fd-backed exact 64-bit ELF input leaves the cursor at the full header" {',
    "fd_exact_cursor_invalid_class": 'test "fd-backed exact invalid-class input leaves the cursor at the full header" {',
    "fd_exact_cursor_not_elf": 'test "fd-backed exact non-ELF input leaves the cursor at the full header" {',
}
EXPECTED_WORKFLOW_LINES = (
    "      - name: Self-test current Phase 2 mk_elfconfig checker",
    "        run: python3 scripts/zigux/check-mk-elfconfig-diff.py --self-test",
    "      - name: Check current Phase 2 mk_elfconfig packet",
    "        run: python3 scripts/zigux/check-mk-elfconfig-diff.py",
)

C_REFERENCE_SOURCE = """// SPDX-License-Identifier: GPL-2.0
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <elf.h>

int main(int argc, char **argv)
{
\tunsigned char ei[EI_NIDENT];

\tif (fread(ei, 1, EI_NIDENT, stdin) != EI_NIDENT) {
\t\tfprintf(stderr, \"Error: input truncated\\n\");
\t\treturn 1;
\t}
\tif (memcmp(ei, ELFMAG, SELFMAG) != 0) {
\t\tfprintf(stderr, \"Error: not ELF\\n\");
\t\treturn 1;
\t}
\tswitch (ei[EI_CLASS]) {
\tcase ELFCLASS32:
\t\tprintf(\"#define KERNEL_ELFCLASS ELFCLASS32\\n\");
\t\tbreak;
\tcase ELFCLASS64:
\t\tprintf(\"#define KERNEL_ELFCLASS ELFCLASS64\\n\");
\t\tbreak;
\tdefault:
\t\texit(1);
\t}

\treturn 0;
}
"""


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    env = os.environ.get("ZIG")
    if env:
        return env
    path = shutil.which("zig")
    if path:
        return path
    raise FileNotFoundError("no zig executable found; set --zig or ZIG")


def find_compiler(explicit: str | None) -> str:
    if explicit:
        return explicit
    for candidate in ("gcc", "cc", "clang"):
        path = shutil.which(candidate)
        if path:
            return path
    raise FileNotFoundError("no C compiler found on PATH")


def validate_fixture_inventory() -> None:
    actual_files = {path.name for path in FIXTURE_DIR.iterdir() if path.is_file()}
    missing = sorted(EXPECTED_FIXTURE_FILES - actual_files)
    unexpected = sorted(actual_files - EXPECTED_FIXTURE_FILES)
    if missing:
        raise FileNotFoundError(f"{FIXTURE_DIR}:missing_fixtures:{','.join(missing)}")
    if unexpected:
        raise ValueError(f"{FIXTURE_DIR}:unexpected_fixtures:{','.join(unexpected)}")


def validate_zig_source_markers(path: Path, markers: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8")
    for label, marker in markers.items():
        if marker not in text:
            raise ValueError(f"{path}:missing_marker:{label}")


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_workflow_step_packet(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    positions: list[int] = []
    for expected_line in EXPECTED_WORKFLOW_LINES:
        matches = [index for index, line in enumerate(lines) if line == expected_line]
        if not matches:
            raise ValueError(f"{path}:missing_workflow_line:{expected_line}")
        if len(matches) != 1:
            raise ValueError(f"{path}:duplicate_workflow_line:{expected_line}")
        positions.append(matches[0])
    if positions != sorted(positions):
        raise ValueError(f"{path}:workflow_line_order={positions!r}")


def validate_cases(cases: object) -> list[dict[str, str]]:
    if not isinstance(cases, list) or not cases:
        raise ValueError(f"{CASES_PATH}:expected_non_empty_json_list")

    validated: list[dict[str, str]] = []
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

        unexpected_fields = sorted(set(raw_case) - {"name", "input", "expected"})
        if unexpected_fields:
            raise ValueError(f"{CASES_PATH}:{name}:unexpected_field:{unexpected_fields[0]}")

        input_name = raw_case.get("input")
        expected_name = raw_case.get("expected")
        if input_name != expected_case["input"]:
            raise ValueError(f"{CASES_PATH}:{name}:input={input_name!r},expected={expected_case['input']!r}")
        if expected_name != expected_case["expected"]:
            raise ValueError(
                f"{CASES_PATH}:{name}:expected={expected_name!r},expected_value={expected_case['expected']!r}"
            )
        if not (FIXTURE_DIR / input_name).exists():
            raise FileNotFoundError(f"{CASES_PATH}:missing_input:{input_name}")
        if not (FIXTURE_DIR / expected_name).exists():
            raise FileNotFoundError(f"{CASES_PATH}:missing_expected:{expected_name}")

        validated.append({"name": name, "input": input_name, "expected": expected_name})

    if seen_names != EXPECTED_CASE_ORDER:
        raise ValueError(f"{CASES_PATH}:case_order={seen_names!r},expected={EXPECTED_CASE_ORDER!r}")
    return validated


def validate_expected_result(path: Path) -> dict[str, object]:
    result = load_json(path)
    if not isinstance(result, dict):
        raise ValueError(f"{path}:expected_json_object")
    if set(result) != EXPECTED_RESULT_KEYS:
        raise ValueError(f"{path}:keys={sorted(result)!r},expected={sorted(EXPECTED_RESULT_KEYS)!r}")
    stdout = result.get("stdout")
    stderr = result.get("stderr")
    exit_code = result.get("exit_code")
    if not isinstance(stdout, str):
        raise ValueError(f"{path}:stdout_not_string")
    if not isinstance(stderr, str):
        raise ValueError(f"{path}:stderr_not_string")
    if not isinstance(exit_code, int):
        raise ValueError(f"{path}:exit_code_not_int")
    return {"stdout": stdout, "stderr": stderr, "exit_code": exit_code}


def decode_hex_input(path: Path) -> bytes:
    tokens = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.split("#", 1)[0].strip()
        if stripped:
            tokens.append(stripped)
    return bytes.fromhex(" ".join(tokens))


def build_reference_c(compiler: str, output: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="mk-elfconfig-c-") as tmp_dir:
        source_path = Path(tmp_dir) / "mk_elfconfig.c"
        source_path.write_text(C_REFERENCE_SOURCE, encoding="utf-8")
        run([compiler, "-std=c99", "-Wall", "-Wextra", "-O2", "-o", str(output), str(source_path)])


def build_zig_tool(zig: str, output: Path) -> None:
    run([zig, "build-exe", str(ZIG_TOOL), "-O", "Debug", f"-femit-bin={output}"])


def run_zig_tests(zig: str, source: Path) -> None:
    run([zig, "test", str(source)])


def run_tool(binary: Path, input_bytes: bytes) -> dict[str, object]:
    result = subprocess.run(
        [str(binary)],
        check=False,
        input=input_bytes,
        capture_output=True,
    )
    return {
        "stdout": result.stdout.decode("utf-8"),
        "stderr": result.stderr.decode("utf-8"),
        "exit_code": result.returncode,
    }


def check_cases(*, zig: str, compiler: str) -> None:
    validate_fixture_inventory()
    validate_zig_source_markers(ZIG_TOOL, EXPECTED_ZIG_MARKERS)
    if not FD_TRAILING_ZIG_TOOL.exists():
        raise FileNotFoundError(FD_TRAILING_ZIG_TOOL)
    validate_zig_source_markers(FD_TRAILING_ZIG_TOOL, EXPECTED_FD_TRAILING_ZIG_MARKERS)
    if not FD_EXACT_CURSOR_ZIG_TOOL.exists():
        raise FileNotFoundError(FD_EXACT_CURSOR_ZIG_TOOL)
    validate_zig_source_markers(FD_EXACT_CURSOR_ZIG_TOOL, EXPECTED_FD_EXACT_CURSOR_ZIG_MARKERS)
    validate_workflow_step_packet(WORKFLOW_PATH)
    run_zig_tests(zig, ZIG_TOOL)
    run_zig_tests(zig, FD_TRAILING_ZIG_TOOL)
    run_zig_tests(zig, FD_EXACT_CURSOR_ZIG_TOOL)
    cases = validate_cases(load_json(CASES_PATH))
    for case in cases:
        validate_expected_result(FIXTURE_DIR / case["expected"])

    with tempfile.TemporaryDirectory(prefix="mk-elfconfig-diff-") as tmp_dir:
        tmp_path = Path(tmp_dir)
        c_binary = tmp_path / "mk_elfconfig_c"
        zig_binary = tmp_path / "mk_elfconfig_zig"
        build_reference_c(compiler, c_binary)
        build_zig_tool(zig, zig_binary)

        for case in cases:
            input_bytes = decode_hex_input(FIXTURE_DIR / case["input"])
            expected = validate_expected_result(FIXTURE_DIR / case["expected"])
            c_result = run_tool(c_binary, input_bytes)
            zig_result = run_tool(zig_binary, input_bytes)
            if c_result != expected:
                raise SystemExit(f"{case['name']}:c_result={c_result!r}:expected={expected!r}")
            if zig_result != expected:
                raise SystemExit(f"{case['name']}:zig_result={zig_result!r}:expected={expected!r}")
            if zig_result != c_result:
                raise SystemExit(f"{case['name']}:zig_and_c_mismatch")

    print("MK_ELFCONFIG_DIFF=pass")
    print(f"MK_ELFCONFIG_CASE_COUNT={len(cases)}")


def validate_self_test_case_count(cases: list[dict[str, str]]) -> int:
    expected_case_count = len(EXPECTED_CASES)
    actual_case_count = len(cases)
    if actual_case_count != expected_case_count:
        raise ValueError(
            f"{CASES_PATH}:case_count={actual_case_count},expected_case_count={expected_case_count}"
        )
    return actual_case_count + 1


def run_self_test() -> None:
    validate_fixture_inventory()
    cases = validate_cases(load_json(CASES_PATH))
    for case in cases:
        validate_expected_result(FIXTURE_DIR / case["expected"])
        decode_hex_input(FIXTURE_DIR / case["input"])
    if not ZIG_TOOL.exists():
        raise FileNotFoundError(ZIG_TOOL)
    validate_zig_source_markers(ZIG_TOOL, EXPECTED_ZIG_MARKERS)
    if not FD_TRAILING_ZIG_TOOL.exists():
        raise FileNotFoundError(FD_TRAILING_ZIG_TOOL)
    validate_zig_source_markers(FD_TRAILING_ZIG_TOOL, EXPECTED_FD_TRAILING_ZIG_MARKERS)
    if not FD_EXACT_CURSOR_ZIG_TOOL.exists():
        raise FileNotFoundError(FD_EXACT_CURSOR_ZIG_TOOL)
    validate_zig_source_markers(FD_EXACT_CURSOR_ZIG_TOOL, EXPECTED_FD_EXACT_CURSOR_ZIG_MARKERS)
    validate_workflow_step_packet(WORKFLOW_PATH)
    print("MK_ELFCONFIG_DIFF_SELF_TEST=pass")
    print(f"MK_ELFCONFIG_DIFF_SELF_TEST_CASE_COUNT={validate_self_test_case_count(cases)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare mk_elfconfig Zig behavior with the Linux C helper.")
    parser.add_argument("--zig", help="path to the Zig executable")
    parser.add_argument("--cc", help="path to the C compiler")
    parser.add_argument("--self-test", action="store_true", help="validate the checker inventory without compiling tools")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    check_cases(zig=find_zig(args.zig), compiler=find_compiler(args.cc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())