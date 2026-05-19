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
FIXTURE_DIR = ROOT / "zigux" / "tests" / "fixtures" / "mk_elfconfig"
CASES_PATH = FIXTURE_DIR / "cases.json"

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

C_REFERENCE_SOURCE = """// SPDX-License-Identifier: GPL-2.0
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <elf.h>

int main(int argc, char **argv)
{
\tunsigned char ei[EI_NIDENT];

\tif (fread(ei, 1, EI_NIDENT, stdin) != EI_NIDENT) {
\t\tfprintf(stderr, "Error: input truncated\\n");
\t\treturn 1;
\t}
\tif (memcmp(ei, ELFMAG, SELFMAG) != 0) {
\t\tfprintf(stderr, "Error: not ELF\\n");
\t\treturn 1;
\t}
\tswitch (ei[EI_CLASS]) {
\tcase ELFCLASS32:
\t\tprintf("#define KERNEL_ELFCLASS ELFCLASS32\\n");
\t\tbreak;
\tcase ELFCLASS64:
\t\tprintf("#define KERNEL_ELFCLASS ELFCLASS64\\n");
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


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


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
    return actual_case_count


def run_self_test() -> None:
    validate_fixture_inventory()
    cases = validate_cases(load_json(CASES_PATH))
    for case in cases:
        validate_expected_result(FIXTURE_DIR / case["expected"])
        decode_hex_input(FIXTURE_DIR / case["input"])
    if not ZIG_TOOL.exists():
        raise FileNotFoundError(ZIG_TOOL)
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
