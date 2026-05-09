#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
CASES_PATH = ROOT / "zigux" / "tests" / "fixtures" / "fixdep" / "cases.json"
MANIFEST_PATH = ROOT / "zigux" / "tests" / "fixtures" / "fixdep" / "manifest.json"
FIXDEP_PATH = ROOT / "scripts" / "zigux" / "fixdep.zig"

REQUIRED_WORKFLOW_RUNS = [
    "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "python3 scripts/zigux/check-fixdep-diff.py",
    "zig test scripts/zigux/fixdep.zig",
]
REQUIRED_CASE_NAME = "sample_escaped_colon"
REQUIRED_STDOUT_PACKET = "sample_escaped_colon_expected.txt"
REQUIRED_HELPER_ANCHOR = "dep parsing unescapes escaped colons inside tokens"


def workflow_run_lines(workflow_text: str) -> list[str]:
    return [line.strip() for line in workflow_text.splitlines()]


def workflow_run_commands(lines: list[str]) -> list[str]:
    commands: list[str] = []
    for line in lines:
        if line.startswith("run: "):
            commands.append(line.removeprefix("run: "))
    return commands


def count_workflow_marker(commands: list[str], marker: str) -> int:
    return sum(1 for command in commands if command == marker)


def count_exact(items: list[str], value: str) -> int:
    return sum(1 for item in items if item == value)


def has_exact_fixdep_packet(commands: list[str]) -> bool:
    try:
        start = commands.index(REQUIRED_WORKFLOW_RUNS[0])
    except ValueError:
        return False
    return commands[start : start + len(REQUIRED_WORKFLOW_RUNS)] == REQUIRED_WORKFLOW_RUNS


def validate_texts(
    workflow_text: str,
    cases_text: str,
    manifest_text: str,
    fixdep_text: str,
) -> list[str]:
    issues: list[str] = []

    workflow_lines = workflow_run_lines(workflow_text)
    workflow_commands = workflow_run_commands(workflow_lines)
    for marker in REQUIRED_WORKFLOW_RUNS:
        count = count_workflow_marker(workflow_commands, marker)
        if count != 1:
            issues.append(f"workflow_exact_marker:{marker}:count={count}:expected=1")

    if not issues and not has_exact_fixdep_packet(workflow_commands):
        issues.append("workflow_packet:fixdep_gate_packet")

    try:
        cases = json.loads(cases_text)
    except json.JSONDecodeError:
        issues.append("fixdep_cases:json_decode")
        cases = []
    if not isinstance(cases, list):
        issues.append("fixdep_cases:type")
        cases = []

    escaped_cases = [case for case in cases if isinstance(case, dict) and case.get("name") == REQUIRED_CASE_NAME]
    if len(escaped_cases) != 1:
        issues.append(f"fixdep_cases:{REQUIRED_CASE_NAME}:count={len(escaped_cases)}:expected=1")
    else:
        expected_stdout = escaped_cases[0].get("expected_stdout", escaped_cases[0].get("expected"))
        if expected_stdout != REQUIRED_STDOUT_PACKET:
            issues.append(
                f"fixdep_cases:{REQUIRED_CASE_NAME}:expected_stdout:{expected_stdout}:expected={REQUIRED_STDOUT_PACKET}"
            )

    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError:
        issues.append("fixdep_manifest:json_decode")
        manifest = {}
    if not isinstance(manifest, dict):
        issues.append("fixdep_manifest:type")
        manifest = {}

    manifest_cases = manifest.get("cases")
    if not isinstance(manifest_cases, list):
        issues.append("fixdep_manifest:cases:type")
        manifest_cases = []
    count = count_exact(manifest_cases, REQUIRED_CASE_NAME)
    if count != 1:
        issues.append(f"fixdep_manifest:cases:{REQUIRED_CASE_NAME}:count={count}:expected=1")

    stdout_packet = manifest.get("stdout_packet")
    if not isinstance(stdout_packet, list):
        issues.append("fixdep_manifest:stdout_packet:type")
        stdout_packet = []
    count = count_exact(stdout_packet, REQUIRED_STDOUT_PACKET)
    if count != 1:
        issues.append(
            f"fixdep_manifest:stdout_packet:{REQUIRED_STDOUT_PACKET}:count={count}:expected=1"
        )

    helper_local_anchors = manifest.get("helper_local_anchors")
    if not isinstance(helper_local_anchors, list):
        issues.append("fixdep_manifest:helper_local_anchors:type")
        helper_local_anchors = []
    count = count_exact(helper_local_anchors, REQUIRED_HELPER_ANCHOR)
    if count != 1:
        issues.append(
            f"fixdep_manifest:helper_local_anchors:{REQUIRED_HELPER_ANCHOR}:count={count}:expected=1"
        )

    if REQUIRED_HELPER_ANCHOR not in fixdep_text:
        issues.append(f"fixdep_source_anchor:{REQUIRED_HELPER_ANCHOR}")

    return issues


def run_self_test() -> int:
    workflow_text = "\n".join(f"run: {marker}" for marker in REQUIRED_WORKFLOW_RUNS) + "\n"
    cases_text = json.dumps(
        [
            {"name": "sample", "expected": "sample_expected.txt"},
            {"name": REQUIRED_CASE_NAME, "expected": REQUIRED_STDOUT_PACKET},
        ]
    )
    manifest_text = json.dumps(
        {
            "cases": ["sample", REQUIRED_CASE_NAME],
            "stdout_packet": ["sample_expected.txt", REQUIRED_STDOUT_PACKET],
            "helper_local_anchors": [REQUIRED_HELPER_ANCHOR],
        }
    )
    fixdep_text = f'test "{REQUIRED_HELPER_ANCHOR}" {{}}\n'

    assert validate_texts(workflow_text, cases_text, manifest_text, fixdep_text) == []

    issues = validate_texts(
        workflow_text.replace(
            "run: python3 scripts/zigux/check-phase2-fixdep-gate.py\n",
            "",
            1,
        ),
        cases_text,
        manifest_text,
        fixdep_text,
    )
    assert (
        "workflow_exact_marker:python3 scripts/zigux/check-phase2-fixdep-gate.py:count=0:expected=1"
        in issues
    )

    issues = validate_texts(
        workflow_text.replace(
            "run: python3 scripts/zigux/check-fixdep-diff.py\n",
            "run: python3 scripts/zigux/check-fixdep-diff.py\nrun: python3 scripts/zigux/check-fixdep-diff.py\n",
            1,
        ),
        cases_text,
        manifest_text,
        fixdep_text,
    )
    assert "workflow_exact_marker:python3 scripts/zigux/check-fixdep-diff.py:count=2:expected=1" in issues

    issues = validate_texts(
        workflow_text.replace(
            "run: python3 scripts/zigux/check-phase2-fixdep-gate.py\n",
            "run: python3 scripts/zigux/check-phase1-parity.py\nrun: python3 scripts/zigux/check-phase2-fixdep-gate.py\n",
            1,
        ),
        cases_text,
        manifest_text,
        fixdep_text,
    )
    assert "workflow_packet:fixdep_gate_packet" in issues

    issues = validate_texts(
        workflow_text,
        json.dumps([{"name": "sample", "expected": "sample_expected.txt"}]),
        manifest_text,
        fixdep_text,
    )
    assert f"fixdep_cases:{REQUIRED_CASE_NAME}:count=0:expected=1" in issues

    issues = validate_texts(
        workflow_text,
        cases_text,
        json.dumps(
            {
                "cases": ["sample", REQUIRED_CASE_NAME],
                "stdout_packet": ["sample_expected.txt"],
                "helper_local_anchors": [REQUIRED_HELPER_ANCHOR],
            }
        ),
        fixdep_text,
    )
    assert (
        f"fixdep_manifest:stdout_packet:{REQUIRED_STDOUT_PACKET}:count=0:expected=1"
        in issues
    )

    issues = validate_texts(
        workflow_text,
        cases_text,
        json.dumps(
            {
                "cases": ["sample", REQUIRED_CASE_NAME],
                "stdout_packet": ["sample_expected.txt", REQUIRED_STDOUT_PACKET],
                "helper_local_anchors": [],
            }
        ),
        fixdep_text,
    )
    assert (
        f"fixdep_manifest:helper_local_anchors:{REQUIRED_HELPER_ANCHOR}:count=0:expected=1"
        in issues
    )

    issues = validate_texts(
        workflow_text,
        cases_text,
        manifest_text,
        'test "other anchor" {}\n',
    )
    assert f"fixdep_source_anchor:{REQUIRED_HELPER_ANCHOR}" in issues

    issues = validate_texts(
        workflow_text,
        json.dumps(
            [
                {"name": "sample", "expected": "sample_expected.txt"},
                {"name": REQUIRED_CASE_NAME, "expected": "wrong_expected.txt"},
            ]
        ),
        manifest_text,
        fixdep_text,
    )
    assert (
        f"fixdep_cases:{REQUIRED_CASE_NAME}:expected_stdout:wrong_expected.txt:expected={REQUIRED_STDOUT_PACKET}"
        in issues
    )

    print("PHASE2_FIXDEP_GATE_SELF_TEST=pass")
    print("PHASE2_FIXDEP_GATE_SELF_TEST_CASE_COUNT=8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the bounded Phase 2 fixdep workflow gating packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run checkout-free checker self-tests.")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()

    issues = validate_texts(
        WORKFLOW_PATH.read_text(encoding="utf-8"),
        CASES_PATH.read_text(encoding="utf-8"),
        MANIFEST_PATH.read_text(encoding="utf-8"),
        FIXDEP_PATH.read_text(encoding="utf-8"),
    )
    if issues:
        print("PHASE2_FIXDEP_GATE=fail")
        print("PHASE2_FIXDEP_GATE_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_FIXDEP_GATE_ISSUES_END")
        return 1

    print("PHASE2_FIXDEP_GATE=pass")
    print(f"PHASE2_FIXDEP_GATE_WORKFLOW_MARKER_COUNT={len(REQUIRED_WORKFLOW_RUNS)}")
    print("PHASE2_FIXDEP_GATE_PACKET_MARKER_COUNT=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
