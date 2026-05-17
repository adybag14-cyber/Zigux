#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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
    'test "genksyms bridge accepts unambiguous abbreviated long options"',
    'test "genksyms bridge renders normalized invocation plan"',
    'test "genksyms bridge ignores positional args while still parsing later options"',
]

EXPECTED_HARNESS_MARKERS = [
    'getenv("ZIGUX_GENKSYMS_TOOL")',
    'execv(tool_path, child_argv);',
]

EXPECTED_SELF_TEST_CASE_COUNT = 7


def load_json(path: Path, label: str) -> tuple[object | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return None, [f"missing_file:{label}"]
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json:{label}:{exc.msg}"]


def validate_expected_object(
    payload: dict[str, object], expected: dict[str, object], label: str
) -> list[str]:
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
            issues.append(
                "genksyms_cases:case_count:"
                f"expected={len(EXPECTED_CASES)!r}:actual={len(payload)!r}"
            )
        actual_names = [item.get("name") for item in payload if isinstance(item, dict)]
        expected_names = [case["name"] for case in EXPECTED_CASES]
        if actual_names != expected_names:
            issues.append(
                f"genksyms_cases:names:expected={expected_names!r}:actual={actual_names!r}"
            )
        for index, expected_case in enumerate(EXPECTED_CASES):
            if index >= len(payload):
                break
            actual_case = payload[index]
            if not isinstance(actual_case, dict):
                issues.append(
                    "genksyms_cases:entry:"
                    f"{index}:expected_object:actual={type(actual_case).__name__}"
                )
                continue
            for key, expected_value in expected_case.items():
                if actual_case.get(key) != expected_value:
                    issues.append(
                        "genksyms_cases:"
                        f"{expected_case['name']}:{key}:expected={expected_value!r}:"
                        f"actual={actual_case.get(key)!r}"
                    )
            for key in sorted(set(actual_case) - set(expected_case)):
                issues.append(f"genksyms_cases:{expected_case['name']}:unexpected_key:{key}")
    return issues


def validate_checker_text(text: str) -> list[str]:
    issues: list[str] = []
    required_markers = [
        'EXPECTED_SELF_TEST_CASE_COUNT = 7',
        'GENKSYMS_HARNESS_REL = f"{FIXTURE_ROOT_REL}/genksyms_bridge_c_harness.c"',
        'print("PHASE2_GENKSYMS_BRIDGE_SELF_TEST=pass")',
        'print("PHASE2_GENKSYMS_BRIDGE=pass")',
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


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []
    required = [
        GENKSYMS_TOOL_REL,
        GENKSYMS_CHECKER_REL,
        GENKSYMS_CASES_REL,
        GENKSYMS_HARNESS_REL,
    ]
    required.extend(f"{FIXTURE_ROOT_REL}/{name}" for name in EXPECTED_OUTPUTS)
    for rel_path in required:
        if not (root / rel_path).is_file():
            issues.append(f"missing_file:{rel_path}")
    if issues:
        return issues

    payload, load_issues = load_json(root / GENKSYMS_CASES_REL, "genksyms_cases")
    issues.extend(load_issues)
    if payload is not None:
        issues.extend(validate_cases(payload))

    for name, expected in EXPECTED_OUTPUTS.items():
        payload, load_issues = load_json(root / FIXTURE_ROOT_REL / name, name)
        issues.extend(load_issues)
        if isinstance(payload, dict):
            issues.extend(validate_expected_object(payload, expected, name))
        elif payload is not None:
            issues.append(f"invalid_shape:{name}:expected_object")

    tool_text = (root / GENKSYMS_TOOL_REL).read_text(encoding="utf-8")
    issues.extend(validate_marker_counts(tool_text, EXPECTED_TOOL_TESTS, GENKSYMS_TOOL_REL))

    harness_text = (root / GENKSYMS_HARNESS_REL).read_text(encoding="utf-8")
    issues.extend(
        validate_marker_counts(harness_text, EXPECTED_HARNESS_MARKERS, GENKSYMS_HARNESS_REL)
    )

    checker_text = (root / GENKSYMS_CHECKER_REL).read_text(encoding="utf-8")
    issues.extend(validate_checker_text(checker_text))
    return issues


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_fixture_root(root: Path, checker_text: str) -> None:
    for rel_path in [GENKSYMS_TOOL_REL, GENKSYMS_HARNESS_REL]:
        source = ROOT / rel_path
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    write_json(root / GENKSYMS_CASES_REL, EXPECTED_CASES)
    for name, payload in EXPECTED_OUTPUTS.items():
        write_json(root / FIXTURE_ROOT_REL / name, payload)
    checker_path = root / GENKSYMS_CHECKER_REL
    checker_path.parent.mkdir(parents=True, exist_ok=True)
    checker_path.write_text(checker_text, encoding="utf-8")


def run_self_test() -> list[str]:
    checker_text = SELF_PATH.read_text(encoding="utf-8")
    issues: list[str] = []
    with tempfile.TemporaryDirectory(prefix="lane23_genksyms_bridge_") as tmpdir:
        tmp_root = Path(tmpdir)
        write_fixture_root(tmp_root, checker_text)
        if validate_root(tmp_root):
            issues.append("self_test:positive_root_failed")

        broken_cases = tmp_root / GENKSYMS_CASES_REL
        write_json(broken_cases, EXPECTED_CASES[:-1])
        case_issues = validate_root(tmp_root)
        if not any("genksyms_cases:case_count" in issue for issue in case_issues):
            issues.append("self_test:missing_case_count_failure")

        write_fixture_root(tmp_root, checker_text)
        wrong_output = dict(EXPECTED_OUTPUTS["minimal_expected.json"])
        wrong_output["stdout"] = "wrong"
        write_json(tmp_root / FIXTURE_ROOT_REL / "minimal_expected.json", wrong_output)
        output_issues = validate_root(tmp_root)
        if not any(issue.startswith("minimal_expected.json:stdout:") for issue in output_issues):
            issues.append("self_test:missing_expected_output_failure")

        write_fixture_root(tmp_root, checker_text)
        tool_path = tmp_root / GENKSYMS_TOOL_REL
        tool_path.write_text(
            tool_path.read_text(encoding="utf-8").replace(EXPECTED_TOOL_TESTS[0], "", 1),
            encoding="utf-8",
        )
        tool_issues = validate_root(tmp_root)
        if not any(issue.startswith("marker_count:scripts/zigux/genksyms.zig:") for issue in tool_issues):
            issues.append("self_test:missing_tool_anchor_failure")

        write_fixture_root(tmp_root, checker_text)
        harness_path = tmp_root / GENKSYMS_HARNESS_REL
        harness_path.write_text(
            harness_path.read_text(encoding="utf-8").replace(EXPECTED_HARNESS_MARKERS[0], "", 1),
            encoding="utf-8",
        )
        harness_issues = validate_root(tmp_root)
        if not any(
            issue.startswith(
                "marker_count:zigux/tests/fixtures/genksyms_bridge/genksyms_bridge_c_harness.c:"
            )
            for issue in harness_issues
        ):
            issues.append("self_test:missing_harness_marker_failure")

        write_fixture_root(tmp_root, checker_text)
        checker_path = tmp_root / GENKSYMS_CHECKER_REL
        checker_path.write_text(
            checker_text.replace(
                'GENKSYMS_HARNESS_REL = f"{FIXTURE_ROOT_REL}/genksyms_bridge_c_harness.c"',
                'GENKSYMS_HARNESS_REL = "broken"',
            ),
            encoding="utf-8",
        )
        checker_issues = validate_root(tmp_root)
        if not any(
            issue.startswith(
                "missing_marker:scripts/zigux/check-genksyms-bridge.py:"
                'GENKSYMS_HARNESS_REL = f"{FIXTURE_ROOT_REL}/genksyms_bridge_c_harness.c"'
            )
            for issue in checker_issues
        ):
            issues.append("self_test:missing_checker_marker_failure")

        write_fixture_root(tmp_root, checker_text)
        broken_json = tmp_root / FIXTURE_ROOT_REL / "long_options_expected.json"
        broken_json.write_text("{\n", encoding="utf-8")
        json_issues = validate_root(tmp_root)
        if not any(issue.startswith("invalid_json:long_options_expected.json:") for issue in json_issues):
            issues.append("self_test:missing_invalid_json_failure")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        issues = run_self_test()
        if issues:
            for issue in issues:
                print(issue)
            return 1
        print("PHASE2_GENKSYMS_BRIDGE_SELF_TEST=pass")
        print(f"PHASE2_GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT={EXPECTED_SELF_TEST_CASE_COUNT}")
        return 0

    issues = validate_root(args.root.resolve())
    if issues:
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_GENKSYMS_BRIDGE=pass")
    print(f"PHASE2_GENKSYMS_BRIDGE_CASE_COUNT={len(EXPECTED_CASES)}")
    print(f"PHASE2_GENKSYMS_BRIDGE_EXPECTED_COUNT={len(EXPECTED_OUTPUTS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
