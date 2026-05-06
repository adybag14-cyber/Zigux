#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SCRIPT_PATH.parents[1] if len(SCRIPT_PATH.parents) > 1 else SCRIPT_PATH.parent

REQUIRED_FILES = {
    "bridge_checker": "scripts/zigux/check-genksyms-bridge.py",
    "workflow": ".github/workflows/zigux-bootstrap.yml",
    "cases": "zigux/tests/fixtures/genksyms_bridge/cases.json",
}

EXPECTED_CASE_NAMES = [
    "minimal",
    "debug_reference_types",
    "long_options",
    "abbreviated_long_options",
    "quiet_overrides_warning",
    "explicit_option_terminator",
    "positional_passthrough",
    "help",
    "abbreviated_help",
    "version",
    "abbreviated_version",
    "invalid_option",
    "missing_reference_argument",
    "unsupported_long_option",
    "missing_long_reference_argument",
    "missing_long_dump_types_argument",
]

EXPECTED_CASE_SPECS = {
    "minimal": {"expected": "minimal_expected.json", "mode": "stdout_json", "normalize_stderr": False},
    "debug_reference_types": {"expected": "debug_reference_types_expected.json", "mode": "stdout_json", "normalize_stderr": False},
    "long_options": {"expected": "long_options_expected.json", "mode": "stdout_json", "normalize_stderr": False},
    "abbreviated_long_options": {"expected": "abbreviated_long_options_expected.json", "mode": "stdout_json", "normalize_stderr": False},
    "quiet_overrides_warning": {"expected": "quiet_overrides_warning_expected.json", "mode": "stdout_json", "normalize_stderr": False},
    "explicit_option_terminator": {"expected": "explicit_option_terminator_expected.json", "mode": "stdout_json", "normalize_stderr": False},
    "positional_passthrough": {"expected": "positional_passthrough_expected.json", "mode": "stdout_json", "normalize_stderr": False},
    "help": {"expected": "help_expected.json", "mode": "process_json", "normalize_stderr": False},
    "abbreviated_help": {"expected": "help_expected.json", "mode": "process_json", "normalize_stderr": False},
    "version": {"expected": "version_expected.json", "mode": "process_json", "normalize_stderr": False},
    "abbreviated_version": {"expected": "abbreviated_version_expected.json", "mode": "process_json", "normalize_stderr": False},
    "invalid_option": {"expected": "invalid_option_expected.json", "mode": "process_json", "normalize_stderr": True},
    "missing_reference_argument": {"expected": "missing_reference_argument_expected.json", "mode": "process_json", "normalize_stderr": True},
    "unsupported_long_option": {"expected": "unsupported_long_option_expected.json", "mode": "process_json", "normalize_stderr": True},
    "missing_long_reference_argument": {"expected": "missing_long_reference_argument_expected.json", "mode": "process_json", "normalize_stderr": True},
    "missing_long_dump_types_argument": {"expected": "missing_long_dump_types_argument_expected.json", "mode": "process_json", "normalize_stderr": True},
}

BRIDGE_CHECKER_MARKERS = [
    "print('GENKSYMS_BRIDGE_SELF_TEST=pass')",
    "print('GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=6')",
]

WORKFLOW_RUN_COUNTS = {
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py": 1,
    "python3 scripts/zigux/check-genksyms-bridge.py --self-test": 1,
    "python3 scripts/zigux/check-genksyms-bridge.py": 1,
    "zig test scripts/zigux/genksyms.zig": 1,
}

WORKFLOW_ORDERED_COMMANDS = [
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
]


def resolve_root() -> Path:
    args = sys.argv[1:]
    if "--root" in args:
        index = args.index("--root")
        try:
            return Path(args[index + 1]).resolve()
        except IndexError as exc:
            raise SystemExit("--root requires a path") from exc
    if "ZIGUX_PHASE2_ROOT" in os.environ:
        return Path(os.environ["ZIGUX_PHASE2_ROOT"]).resolve()
    return DEFAULT_ROOT


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate_cases(root: Path) -> list[str]:
    issues: list[str] = []
    payload = json.loads(read_text(root, REQUIRED_FILES["cases"]))
    if not isinstance(payload, dict):
        return ["cases:expected_top_level_object"]
    cases = payload.get("cases")
    if not isinstance(cases, list):
        return ["cases:expected_list"]

    actual_names: list[str] = []
    seen_names: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            issues.append("cases:entry:expected_object")
            continue
        name = case.get("name")
        if not isinstance(name, str) or not name:
            issues.append("cases:missing_name")
            continue
        if name in seen_names:
            issues.append(f"cases:duplicate_name:{name}")
            continue
        seen_names.add(name)
        actual_names.append(name)
        spec = EXPECTED_CASE_SPECS.get(name)
        if spec is None:
            issues.append(f"cases:unexpected_name:{name}")
            continue
        if case.get("expected") != spec["expected"]:
            issues.append(f"cases:{name}:expected={case.get('expected')!r}:expected_file={spec['expected']!r}")
        if case.get("mode", "stdout_json") != spec["mode"]:
            issues.append(f"cases:{name}:mode={case.get('mode', 'stdout_json')!r}:expected_mode={spec['mode']!r}")
        if case.get("normalize_stderr", False) != spec["normalize_stderr"]:
            issues.append(
                f"cases:{name}:normalize_stderr={case.get('normalize_stderr', False)!r}:"
                f"expected_normalize_stderr={spec['normalize_stderr']!r}"
            )

    if len(cases) != len(EXPECTED_CASE_NAMES):
        issues.append(f"cases:count={len(cases)}:expected={len(EXPECTED_CASE_NAMES)}")
    if actual_names != EXPECTED_CASE_NAMES:
        issues.append("cases:names=expected_exact_phase2_genksyms_bridge_case_list")
    for name in sorted(set(EXPECTED_CASE_NAMES) - seen_names):
        issues.append(f"cases:missing_name:{name}")
    return issues


def validate_ordered_commands(stripped_lines: list[str], ordered_commands: list[str], prefix: str, matcher) -> list[str]:
    issues: list[str] = []
    positions: dict[str, int] = {}
    for command in ordered_commands:
        position = next((index for index, line in enumerate(stripped_lines) if matcher(line, command)), None)
        if position is not None:
            positions[command] = position
    for before, after in zip(ordered_commands, ordered_commands[1:]):
        if before in positions and after in positions and positions[before] >= positions[after]:
            issues.append(f"{prefix}_order:{before}:before:{after}")
    return issues


def validate_workflow(text: str) -> list[str]:
    issues: list[str] = []
    stripped_lines = [line.strip() for line in text.splitlines()]
    for command, expected_count in WORKFLOW_RUN_COUNTS.items():
        expected_line = f"run: {command}"
        count = sum(1 for line in stripped_lines if line == expected_line)
        if count != expected_count:
            issues.append(f"workflow_run:{command}:count={count}:expected={expected_count}")
    issues.extend(
        validate_ordered_commands(
            stripped_lines,
            WORKFLOW_ORDERED_COMMANDS,
            "workflow",
            matcher=lambda line, command: line == f"run: {command}",
        )
    )
    return issues


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for label, rel_path in REQUIRED_FILES.items():
        if not (root / rel_path).exists():
            issues.append(f"missing:{label}:{rel_path}")
    if issues:
        return issues

    bridge_checker = read_text(root, REQUIRED_FILES["bridge_checker"])
    workflow = read_text(root, REQUIRED_FILES["workflow"])
    for marker in BRIDGE_CHECKER_MARKERS:
        if marker not in bridge_checker:
            issues.append(f"bridge_checker:{marker}")
    issues.extend(validate_workflow(workflow))
    issues.extend(validate_cases(root))
    return issues


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py"), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


def clone_fixture_root(destination_root: Path) -> None:
    script_target = destination_root / "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py"
    script_target.parent.mkdir(parents=True, exist_ok=True)
    script_target.write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")

    for key in REQUIRED_FILES.values():
        (destination_root / key).parent.mkdir(parents=True, exist_ok=True)

    (destination_root / REQUIRED_FILES["bridge_checker"]).write_text(
        "print('GENKSYMS_BRIDGE_SELF_TEST=pass')\nprint('GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=6')\n",
        encoding="utf-8",
    )
    workflow_lines = [
        "run: python3 scripts/zigux/validate-phase2.py",
        "run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
        "run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
        "run: python3 scripts/zigux/validate-phase2-closure.py",
        "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
        "run: python3 scripts/zigux/check-genksyms-bridge.py",
        "run: zig test scripts/zigux/genksyms.zig",
    ]
    (destination_root / REQUIRED_FILES["workflow"]).write_text("\n".join(workflow_lines) + "\n", encoding="utf-8")
    (destination_root / REQUIRED_FILES["cases"]).write_text(
        json.dumps(
            {
                "cases": [
                    {
                        "name": name,
                        "expected": EXPECTED_CASE_SPECS[name]["expected"],
                        **({"mode": EXPECTED_CASE_SPECS[name]["mode"]} if EXPECTED_CASE_SPECS[name]["mode"] != "stdout_json" else {}),
                        **({"normalize_stderr": True} if EXPECTED_CASE_SPECS[name]["normalize_stderr"] else {}),
                    }
                    for name in EXPECTED_CASE_NAMES
                ]
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def expect_issue(label: str, root: Path, needle: str) -> None:
    result = run_checker(root)
    if result.returncode == 0:
        raise SystemExit(f"phase2-genksyms-selftest-alignment:{label}:unexpected_pass")
    if needle not in result.stdout:
        actual = result.stdout.strip() or "none"
        raise SystemExit(f"phase2-genksyms-selftest-alignment:{label}:expected:{needle}:actual:{actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_genksyms_selftest_alignment_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        baseline = run_checker(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase2-genksyms-selftest-alignment:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        cases_path = tmp_root / REQUIRED_FILES["cases"]
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["cases"].pop()
        cases_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        expect_issue("case_count", tmp_root, f"cases:count={len(EXPECTED_CASE_NAMES)-1}:expected={len(EXPECTED_CASE_NAMES)}")
        clone_fixture_root(tmp_root)

        workflow_path = tmp_root / REQUIRED_FILES["workflow"]
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(original_workflow.replace("run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test\n", "", 1), encoding="utf-8")
        expect_issue("workflow_checker_self_test", tmp_root, "workflow_run:python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test:count=0:expected=1")
        clone_fixture_root(tmp_root)

        workflow_path = tmp_root / REQUIRED_FILES["workflow"]
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(original_workflow.replace("run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py\n", "", 1), encoding="utf-8")
        expect_issue("workflow_checker_live_run", tmp_root, "workflow_run:python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py:count=0:expected=1")
        clone_fixture_root(tmp_root)

        bridge_checker_path = tmp_root / REQUIRED_FILES["bridge_checker"]
        bridge_checker_path.write_text("print('GENKSYMS_BRIDGE_SELF_TEST=pass')\n", encoding="utf-8")
        expect_issue("bridge_checker_case_count_marker", tmp_root, "bridge_checker:print('GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=6')")
        clone_fixture_root(tmp_root)

    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT=6")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())

ROOT = resolve_root()
problems = validate(ROOT)
if problems:
    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT=fail")
    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_ISSUES_START")
    for problem in problems:
        print(problem)
    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_ISSUES_END")
    raise SystemExit(1)

print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT=pass")
print(f"PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_ROOT={ROOT}")