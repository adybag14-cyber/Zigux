#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path


def derive_repo_root(script_path: Path) -> Path:
    return script_path.parents[2] if len(script_path.parents) >= 3 else script_path.parent


SELF_PATH = Path(__file__).resolve()
ROOT = derive_repo_root(SELF_PATH)

GENKSYMS_TOOL_REL = "scripts/zigux/genksyms.zig"
GENKSYMS_CHECKER_REL = "scripts/zigux/check-genksyms-bridge.py"
FIXTURE_ROOT_REL = "zigux/tests/fixtures/genksyms_bridge"
GENKSYMS_CASES_REL = f"{FIXTURE_ROOT_REL}/cases.json"
GENKSYMS_HARNESS_REL = f"{FIXTURE_ROOT_REL}/genksyms_bridge_c_harness.c"

EXPECTED_CASES = [
    {
        "name": "minimal",
        "argv": [],
        "mode": "stdout_json",
        "expected": "minimal_expected.json",
    },
    {
        "name": "debug_reference_types",
        "argv": [
            "-d",
            "-d",
            "-D",
            "-w",
            "-p",
            "-r",
            "foo.symref",
            "-r",
            "bar.symref",
            "-T",
            "out.symtypes",
        ],
        "mode": "stdout_json",
        "expected": "debug_reference_types_expected.json",
    },
    {
        "name": "long_options",
        "argv": [
            "--debug",
            "--warnings",
            "--quiet",
            "--reference=foo.symref",
            "--dump-types",
            "types.symtypes",
            "--preserve",
        ],
        "mode": "stdout_json",
        "expected": "long_options_expected.json",
    },
    {
        "name": "abbreviated_long_options",
        "argv": [
            "--deb",
            "--warn",
            "--qui",
            "--ref=foo.symref",
            "--dump-t",
            "types.symtypes",
            "--pres",
        ],
        "mode": "stdout_json",
        "expected": "abbreviated_long_options_expected.json",
    },
    {
        "name": "ambiguous_long_option",
        "argv": ["--d"],
        "mode": "process_json",
        "expected": "ambiguous_long_option_expected.json",
        "normalize_stderr": True,
    },
    {
        "name": "missing_long_reference_argument",
        "argv": ["--reference"],
        "mode": "process_json",
        "expected": "missing_long_reference_argument_expected.json",
    },
    {
        "name": "empty_inline_long_reference_argument",
        "argv": ["--reference="],
        "mode": "process_json",
        "expected": "missing_long_reference_argument_expected.json",
    },
    {
        "name": "missing_long_dump_types_argument",
        "argv": ["--dump-types"],
        "mode": "process_json",
        "expected": "missing_long_dump_types_argument_expected.json",
    },
    {
        "name": "empty_inline_abbreviated_long_dump_types_argument",
        "argv": ["--dump-t="],
        "mode": "process_json",
        "expected": "missing_long_dump_types_argument_expected.json",
    },
    {
        "name": "missing_short_dump_types_argument",
        "argv": ["-T"],
        "mode": "process_json",
        "expected": "missing_short_dump_types_argument_expected.json",
    },
    {
        "name": "unexpected_long_option_argument",
        "argv": ["--help=extra"],
        "mode": "process_json",
        "expected": "unexpected_long_option_argument_expected.json",
    },
    {
        "name": "version_before_invalid_short_option",
        "argv": ["-Vx"],
        "mode": "process_json",
        "expected": "version_before_invalid_short_option_expected.json",
    },
    {
        "name": "long_version_before_invalid_short_option",
        "argv": ["--version", "-x"],
        "mode": "process_json",
        "expected": "version_before_invalid_short_option_expected.json",
    },
    {
        "name": "version_before_missing_short_option_argument",
        "argv": ["-Vr"],
        "mode": "process_json",
        "expected": "version_before_missing_short_option_argument_expected.json",
    },
    {
        "name": "version_before_short_help",
        "argv": ["-Vh"],
        "mode": "process_json",
        "expected": "version_before_short_help_expected.json",
    },
    {
        "name": "long_version_before_short_help",
        "argv": ["--version", "-h"],
        "mode": "process_json",
        "expected": "version_before_short_help_expected.json",
    },
    {
        "name": "version_before_long_help",
        "argv": ["-V", "--help"],
        "mode": "process_json",
        "expected": "version_before_long_help_expected.json",
    },
    {
        "name": "long_version_before_long_help",
        "argv": ["--version", "--help"],
        "mode": "process_json",
        "expected": "version_before_long_help_expected.json",
    },
    {
        "name": "abbreviated_long_version_before_long_help",
        "argv": ["--ver", "--help"],
        "mode": "process_json",
        "expected": "version_before_long_help_expected.json",
    },
    {
        "name": "abbreviated_long_version_before_short_help",
        "argv": ["--ver", "-h"],
        "mode": "process_json",
        "expected": "version_before_short_help_expected.json",
    },
    {
        "name": "repeated_version",
        "argv": ["-VV"],
        "mode": "process_json",
        "expected": "repeated_version_expected.json",
    },
    {
        "name": "repeated_long_version",
        "argv": ["--version", "--ver"],
        "mode": "process_json",
        "expected": "repeated_version_expected.json",
    },
    {
        "name": "unsupported_long_option",
        "argv": ["--unknown"],
        "mode": "process_json",
        "expected": "unsupported_long_option_expected.json",
        "normalize_stderr": True,
    },
    {
        "name": "too_many_reference_files",
        "argv": [
            "-r",
            "01.symref",
            "-r",
            "02.symref",
            "-r",
            "03.symref",
            "-r",
            "04.symref",
            "-r",
            "05.symref",
            "-r",
            "06.symref",
            "-r",
            "07.symref",
            "-r",
            "08.symref",
            "-r",
            "09.symref",
            "-r",
            "10.symref",
            "-r",
            "11.symref",
            "-r",
            "12.symref",
            "-r",
            "13.symref",
            "-r",
            "14.symref",
            "-r",
            "15.symref",
            "-r",
            "16.symref",
            "-r",
            "17.symref",
        ],
        "mode": "process_json",
        "expected": "too_many_reference_files_expected.json",
        "normalize_stderr": True,
    },
    {
        "name": "quiet_overrides_warning",
        "argv": ["-w", "-q"],
        "mode": "stdout_json",
        "expected": "quiet_overrides_warning_expected.json",
    },
]

EXPECTED_OUTPUTS = {
    "minimal_expected.json": {
        "tool": "scripts/genksyms/genksyms",
        "stdin": "cpp-stream",
        "stdout": "symversions",
        "argv": ["scripts/genksyms/genksyms"],
        "options": {
            "debug_level": 0,
            "warnings": False,
            "dump_defs": False,
            "preserve": False,
            "reference_files": [],
            "dump_types_file": None,
        },
    },
    "debug_reference_types_expected.json": {
        "tool": "scripts/genksyms/genksyms",
        "stdin": "cpp-stream",
        "stdout": "symversions",
        "argv": [
            "scripts/genksyms/genksyms",
            "-d",
            "-d",
            "-D",
            "-w",
            "-p",
            "-r",
            "foo.symref",
            "-r",
            "bar.symref",
            "-T",
            "out.symtypes",
        ],
        "options": {
            "debug_level": 2,
            "warnings": True,
            "dump_defs": True,
            "preserve": True,
            "reference_files": ["foo.symref", "bar.symref"],
            "dump_types_file": "out.symtypes",
        },
    },
    "long_options_expected.json": {
        "tool": "scripts/genksyms/genksyms",
        "stdin": "cpp-stream",
        "stdout": "symversions",
        "argv": [
            "scripts/genksyms/genksyms",
            "--debug",
            "--warnings",
            "--quiet",
            "--reference=foo.symref",
            "--dump-types",
            "types.symtypes",
            "--preserve",
        ],
        "options": {
            "debug_level": 1,
            "warnings": False,
            "dump_defs": False,
            "preserve": True,
            "reference_files": ["foo.symref"],
            "dump_types_file": "types.symtypes",
        },
    },
    "abbreviated_long_options_expected.json": {
        "tool": "scripts/genksyms/genksyms",
        "stdin": "cpp-stream",
        "stdout": "symversions",
        "argv": [
            "scripts/genksyms/genksyms",
            "--deb",
            "--warn",
            "--qui",
            "--ref=foo.symref",
            "--dump-t",
            "types.symtypes",
            "--pres",
        ],
        "options": {
            "debug_level": 1,
            "warnings": False,
            "dump_defs": False,
            "preserve": True,
            "reference_files": ["foo.symref"],
            "dump_types_file": "types.symtypes",
        },
    },
    "ambiguous_long_option_expected.json": {
        "stdout": "",
        "stderr": "option '--d' is ambiguous\n",
        "exit_code": 1,
    },
    "missing_long_reference_argument_expected.json": {
        "stdout": "",
        "stderr": "option '--reference' requires an argument\n",
        "exit_code": 1,
    },
    "missing_long_dump_types_argument_expected.json": {
        "stdout": "",
        "stderr": "option '--dump-types' requires an argument\n",
        "exit_code": 1,
    },
    "missing_short_dump_types_argument_expected.json": {
        "stdout": "",
        "stderr": "option requires an argument -- 'T'\n",
        "exit_code": 1,
    },
    "unexpected_long_option_argument_expected.json": {
        "stdout": "",
        "stderr": "option '--help' doesn't allow an argument\n",
        "exit_code": 1,
    },
    "version_before_invalid_short_option_expected.json": {
        "stdout": "",
        "stderr": "genksyms version 2.5.60\ninvalid option -- 'x'\n",
        "exit_code": 1,
    },
    "version_before_missing_short_option_argument_expected.json": {
        "stdout": "",
        "stderr": "genksyms version 2.5.60\noption requires an argument -- 'r'\n",
        "exit_code": 1,
    },
    "version_before_short_help_expected.json": {
        "stdout": "",
        "stderr": "genksyms version 2.5.60\nUsage:\ngenksyms [-adDTwqhVR] > /path/to/.tmp_obj.ver\n\n -d, --debug Increment the debug level (repeatable)\n -D, --dump Dump expanded symbol defs (for debugging only)\n -r, --reference file Read reference symbols from a file\n -T, --dump-types file Dump expanded types into file\n -p, --preserve Preserve reference modversions or fail\n -w, --warnings Enable warnings\n -q, --quiet Disable warnings (default)\n -h, --help Print this message\n -V, --version Print the release version\n",
        "exit_code": 0,
    },
    "version_before_long_help_expected.json": {
        "stdout": "",
        "stderr": "genksyms version 2.5.60\nUsage:\ngenksyms [-adDTwqhVR] > /path/to/.tmp_obj.ver\n\n -d, --debug Increment the debug level (repeatable)\n -D, --dump Dump expanded symbol defs (for debugging only)\n -r, --reference file Read reference symbols from a file\n -T, --dump-types file Dump expanded types into file\n -p, --preserve Preserve reference modversions or fail\n -w, --warnings Enable warnings\n -q, --quiet Disable warnings (default)\n -h, --help Print this message\n -V, --version Print the release version\n",
        "exit_code": 0,
    },
    "repeated_version_expected.json": {
        "stdout": "",
        "stderr": "genksyms version 2.5.60\ngenksyms version 2.5.60\n",
        "exit_code": 0,
    },
    "unsupported_long_option_expected.json": {
        "stdout": "",
        "stderr": "unrecognized option '--unknown'\n",
        "exit_code": 1,
    },
    "too_many_reference_files_expected.json": {
        "stdout": "",
        "stderr": "too many reference files\n",
        "exit_code": 1,
    },
    "quiet_overrides_warning_expected.json": {
        "tool": "scripts/genksyms/genksyms",
        "stdin": "cpp-stream",
        "stdout": "symversions",
        "argv": ["scripts/genksyms/genksyms", "-w", "-q"],
        "options": {
            "debug_level": 0,
            "warnings": False,
            "dump_defs": False,
            "preserve": False,
            "reference_files": [],
            "dump_types_file": None,
        },
    },
}

EXPECTED_TOOL_TESTS = [
    'test "genksyms bridge parses repeated short flags and arguments"',
    'test "genksyms bridge parses long options and quiet override"',
    'test "genksyms bridge keeps version as a side effect while parsing later options"',
    'test "genksyms bridge preserves repeated pure version invocations"',
    'test "genksyms bridge accepts unambiguous abbreviated long options"',
    'test "parseArgs reports ambiguous abbreviated long options"',
    'test "genksyms bridge canonicalizes unexpected long option argument failures"',
    'test "genksyms bridge preserves version side effects before later parse failures"',
    'test "genksyms bridge preserves long version side effects before later short parse failures"',
    'test "genksyms bridge renders unexpected long option argument like the fixture"',
    'test "genksyms bridge keeps version side effect before long help"',
    'test "genksyms bridge keeps long version side effect before short help"',
    'test "genksyms bridge keeps long version side effect before long help"',
    'test "genksyms bridge keeps abbreviated long version side effect before long help"',
    'test "genksyms bridge keeps abbreviated long version side effect before short help"',
    'test "genksyms bridge rejects empty inline long reference argument"',
    'test "genksyms bridge canonicalizes abbreviated dump-types empty inline argument"',
    'test "genksyms bridge rejects more than sixteen reference files like the C harness"',
    'test "genksyms bridge renders normalized invocation plan"',
    'test "genksyms bridge ignores positional args while still parsing later options"',
]

EXPECTED_HARNESS_MARKERS = [
    'getenv("ZIGUX_GENKSYMS_TOOL")',
    'execv(tool_path, child_argv);',
]

EXPECTED_SELF_TEST_CASE_COUNT = 10


def load_json(path: Path, label: str) -> tuple[object | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return None, [f"missing_file:{label}"]
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json:{label}:{exc.msg}"]


def validate_expected_object(payload: dict[str, object], expected: dict[str, object], label: str) -> list[str]:
    issues: list[str] = []
    if payload != expected:
        for key, expected_value in expected.items():
            actual_value = payload.get(key)
            if actual_value != expected_value:
                issues.append(f"{label}:{key}:expected={expected_value!r}:actual={actual_value!r}")
        for key in sorted(set(payload) - set(expected)):
            issues.append(f"{label}:unexpected_key:{key}")
    return issues


def validate_cases(payload: object) -> list[str]:
    if not isinstance(payload, list):
        return ["invalid_shape:genksyms_cases:expected_list"]
    issues: list[str] = []
    if payload != EXPECTED_CASES:
        if len(payload) != len(EXPECTED_CASES):
            issues.append("genksyms_cases:case_count:" f"expected={len(EXPECTED_CASES)!r}:actual={len(payload)!r}")
        actual_names = [item.get("name") for item in payload if isinstance(item, dict)]
        expected_names = [case["name"] for case in EXPECTED_CASES]
        if actual_names != expected_names:
            issues.append(f"genksyms_cases:names:expected={expected_names!r}:actual={actual_names!r}")
        for index, expected_case in enumerate(EXPECTED_CASES):
            if index >= len(payload):
                break
            actual_case = payload[index]
            if not isinstance(actual_case, dict):
                issues.append("genksyms_cases:" f"entry:{index}:expected_object:actual={type(actual_case).__name__}")
                continue
            for key, expected_value in expected_case.items():
                if actual_case.get(key) != expected_value:
                    issues.append("genksyms_cases:" f"{expected_case['name']}:{key}:expected={expected_value!r}:" f"actual={actual_case.get(key)!r}")
            for key in sorted(set(actual_case) - set(expected_case)):
                issues.append(f"genksyms_cases:{expected_case['name']}:unexpected_key:{key}")
    return issues


def validate_checker_text(text: str) -> list[str]:
    issues: list[str] = []
    required_markers = [
        'EXPECTED_SELF_TEST_CASE_COUNT = 10',
        'GENKSYMS_HARNESS_REL = f"{FIXTURE_ROOT_REL}/genksyms_bridge_c_harness.c"',
        'print("PHASE2_GENKSYMS_BRIDGE_SELF_TEST=pass")',
        'print("PHASE2_GENKSYMS_BRIDGE=pass")',
        'PHASE2_GENKSYMS_BRIDGE_RUNTIME_CASE_COUNT',
        'runtime_compile_failed',
    ]
    for marker in required_markers:
        if marker not in text:
            issues.append(f"missing_marker:{GENKSYMS_CHECKER_REL}:{marker}")
    return issues


def validate_marker_counts(text: str, markers: list[str], label: str) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append(f"marker_count:{label}:{marker}:count={count}:expected=1")
    return issues


def build_runtime_stdout_observation(expected_name: str) -> dict[str, object]:
    return {"stdout": json.dumps(EXPECTED_OUTPUTS[expected_name]) + "\n", "stderr": "", "exit_code": 0}


def validate_runtime_observation(case: dict[str, object], observation: dict[str, object], label: str) -> list[str]:
    issues: list[str] = []
    expected = EXPECTED_OUTPUTS[case["expected"]]
    if case["mode"] == "stdout_json":
        if observation.get("exit_code") != 0:
            issues.append(f"{label}:exit_code:expected=0:actual={observation.get('exit_code')!r}")
        if observation.get("stderr") != "":
            issues.append(f"{label}:stderr:expected='':actual={observation.get('stderr')!r}")
        try:
            payload = json.loads(str(observation.get("stdout", "")))
        except json.JSONDecodeError as exc:
            issues.append(f"{label}:stdout:invalid_json:{exc.msg}")
            return issues
        if not isinstance(payload, dict):
            issues.append(f"{label}:stdout:expected_object:actual={type(payload).__name__}")
            return issues
        issues.extend(validate_expected_object(payload, expected, f"{label}:stdout_json"))
        return issues
    expected_process = {"stdout": expected["stdout"], "stderr": expected["stderr"], "exit_code": expected["exit_code"]}
    issues.extend(validate_expected_object(observation, expected_process, f"{label}:process_json"))
    return issues


def validate_runtime_repeat(case: dict[str, object], first: dict[str, object], second: dict[str, object], label: str) -> list[str]:
    if first == second:
        return []
    return [f"{label}:determinism:expected_identical_replay:{case['name']}"]


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="genksyms_bridge_selftest_") as tmp:
        root = Path(tmp)

        def build_root() -> None:
            (root / "scripts/zigux").mkdir(parents=True, exist_ok=True)
            (root / FIXTURE_ROOT_REL).mkdir(parents=True, exist_ok=True)
            (root / GENKSYMS_CHECKER_REL).write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")
            (root / GENKSYMS_TOOL_REL).write_text("\n".join(EXPECTED_TOOL_TESTS + [""]), encoding="utf-8")
            (root / GENKSYMS_HARNESS_REL).write_text("\n".join(EXPECTED_HARNESS_MARKERS + [""]), encoding="utf-8")
            (root / GENKSYMS_CASES_REL).write_text(json.dumps(EXPECTED_CASES, indent=2) + "\n", encoding="utf-8")
            for name, payload in EXPECTED_OUTPUTS.items():
                (root / FIXTURE_ROOT_REL / name).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

        checks_run = 0
        build_root()
        if validate_checker_text((root / GENKSYMS_CHECKER_REL).read_text(encoding="utf-8")):
            return 1
        checks_run += 1
        if validate_runtime_observation(EXPECTED_CASES[0], build_runtime_stdout_observation("minimal_expected.json"), "runtime:minimal"):
            return 1
        checks_run += 1
        if validate_runtime_observation(EXPECTED_CASES[4], {"stdout": "", "stderr": "option '--d' is ambiguous\n", "exit_code": 1}, "runtime:ambiguous"):
            return 1
        checks_run += 1
        if validate_runtime_observation(EXPECTED_CASES[21], {"stdout": "", "stderr": "genksyms version 2.5.60\ngenksyms version 2.5.60\n", "exit_code": 0}, "runtime:repeated-long-version"):
            return 1
        checks_run += 1
        if not validate_runtime_observation(EXPECTED_CASES[0], {"stdout": "[]\n", "stderr": "", "exit_code": 0}, "runtime:minimal-bad"):
            return 1
        checks_run += 1
        if not validate_runtime_observation(EXPECTED_CASES[4], {"stdout": "", "stderr": "", "exit_code": 1}, "runtime:ambiguous-bad"):
            return 1
        checks_run += 1
        if validate_runtime_repeat(EXPECTED_CASES[0], build_runtime_stdout_observation("minimal_expected.json"), build_runtime_stdout_observation("minimal_expected.json"), "runtime:minimal-repeat"):
            return 1
        checks_run += 1
        if not validate_runtime_repeat(EXPECTED_CASES[0], build_runtime_stdout_observation("minimal_expected.json"), {"stdout": "{}\n", "stderr": "", "exit_code": 0}, "runtime:minimal-repeat-bad"):
            return 1
        checks_run += 1
        build_root()
        tool_text = (root / GENKSYMS_TOOL_REL).read_text(encoding="utf-8")
        (root / GENKSYMS_TOOL_REL).write_text(tool_text.replace(EXPECTED_TOOL_TESTS[0], "", 1), encoding="utf-8")
        if not any(issue.startswith(f"marker_count:{GENKSYMS_TOOL_REL}:") for issue in validate_marker_counts((root / GENKSYMS_TOOL_REL).read_text(encoding="utf-8"), EXPECTED_TOOL_TESTS, GENKSYMS_TOOL_REL)):
            return 1
        checks_run += 1
        build_root()
        cases_payload = json.loads((root / GENKSYMS_CASES_REL).read_text(encoding="utf-8"))
        cases_payload.pop()
        (root / GENKSYMS_CASES_REL).write_text(json.dumps(cases_payload, indent=2) + "\n", encoding="utf-8")
        if not any(issue.startswith("genksyms_cases:case_count:") for issue in validate_cases(json.loads((root / GENKSYMS_CASES_REL).read_text(encoding="utf-8")))):
            return 1
        checks_run += 1
    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_GENKSYMS_BRIDGE_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 2 genksyms wrapper packet.")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    print("PHASE2_GENKSYMS_BRIDGE=pass")
    print(f"PHASE2_GENKSYMS_BRIDGE_RUNTIME_CASE_COUNT={len(EXPECTED_CASES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())