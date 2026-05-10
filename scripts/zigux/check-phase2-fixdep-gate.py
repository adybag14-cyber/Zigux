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
FIXDEP_PACKET_RUNS = REQUIRED_WORKFLOW_RUNS[:-1]
REQUIRED_CASE_PACKET = (
    ("sample", "sample_expected.txt"),
    ("sample_escaped_space", "sample_escaped_space_expected.txt"),
    ("sample_escaped_colon", "sample_escaped_colon_expected.txt"),
    ("sample_multi_target", "sample_multi_target_expected.txt"),
    ("sample_comment_only", "sample_comment_only_expected.txt"),
    ("sample_missing_dep", "sample_missing_dep_expected.txt"),
    ("sample_escaped_hash_comment_chain", "sample_escaped_hash_comment_chain_expected.txt"),
)
REQUIRED_STDERR_BY_CASE = {
    "sample_comment_only": "sample_comment_only_expected.stderr.txt",
    "sample_missing_dep": "sample_missing_dep_expected.stderr.txt",
}
REQUIRED_HELPER_ANCHORS = (
    "dep parsing returns NoTargets for comment-only depfiles",
    "dep parsing keeps escaped spaces inside tokens",
    "dep parsing unescapes escaped colons inside tokens",
    "dep parsing continues dependency tokens across escaped newlines",
    "dep parsing skips bytes after the first embedded NUL",
    "dependency file reads beyond the legacy one mebibyte ceiling",
    "output write failure uses C-style wording",
    "escaped hash dependency survives concatenated target comment path",
    "escaped space dependency survives concatenated target comment path",
)
REQUIRED_CASE_NAMES = tuple(name for name, _ in REQUIRED_CASE_PACKET)
REQUIRED_STDOUT_PACKET = tuple(expected for _, expected in REQUIRED_CASE_PACKET)
REQUIRED_STDERR_PACKET = tuple(REQUIRED_STDERR_BY_CASE[name] for name in REQUIRED_STDERR_BY_CASE)


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
        start = commands.index(FIXDEP_PACKET_RUNS[0])
    except ValueError:
        return False
    return commands[start : start + len(FIXDEP_PACKET_RUNS)] == FIXDEP_PACKET_RUNS


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

    actual_case_names = [
        case.get("name")
        for case in cases
        if isinstance(case, dict) and isinstance(case.get("name"), str)
    ]
    if actual_case_names != list(REQUIRED_CASE_NAMES):
        issues.append(
            f"fixdep_cases:order_or_count:actual={actual_case_names}:expected={list(REQUIRED_CASE_NAMES)}"
        )

    case_map: dict[str, list[dict[str, object]]] = {}
    for case in cases:
        if isinstance(case, dict) and isinstance(case.get("name"), str):
            case_map.setdefault(case["name"], []).append(case)

    for name, expected_stdout in REQUIRED_CASE_PACKET:
        matching = case_map.get(name, [])
        if len(matching) != 1:
            issues.append(f"fixdep_cases:{name}:count={len(matching)}:expected=1")
            continue

        actual_stdout = matching[0].get("expected_stdout", matching[0].get("expected"))
        if actual_stdout != expected_stdout:
            issues.append(
                f"fixdep_cases:{name}:expected_stdout:{actual_stdout}:expected={expected_stdout}"
            )

        expected_stderr = REQUIRED_STDERR_BY_CASE.get(name)
        actual_stderr = matching[0].get("expected_stderr")
        if expected_stderr is None:
            if actual_stderr is not None:
                issues.append(f"fixdep_cases:{name}:unexpected_stderr:{actual_stderr}")
        elif actual_stderr != expected_stderr:
            issues.append(
                f"fixdep_cases:{name}:expected_stderr:{actual_stderr}:expected={expected_stderr}"
            )

    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError:
        issues.append("fixdep_manifest:json_decode")
        manifest = {}
    if not isinstance(manifest, dict):
        issues.append("fixdep_manifest:type")
        manifest = {}

    if manifest.get("case_count") != len(REQUIRED_CASE_PACKET):
        issues.append(
            f"fixdep_manifest:case_count:{manifest.get('case_count')}:expected={len(REQUIRED_CASE_PACKET)}"
        )

    manifest_cases = manifest.get("cases")
    if not isinstance(manifest_cases, list):
        issues.append("fixdep_manifest:cases:type")
        manifest_cases = []
    if manifest_cases != list(REQUIRED_CASE_NAMES):
        issues.append(
            f"fixdep_manifest:cases:actual={manifest_cases}:expected={list(REQUIRED_CASE_NAMES)}"
        )
    for name in REQUIRED_CASE_NAMES:
        count = count_exact(manifest_cases, name)
        if count != 1:
            issues.append(f"fixdep_manifest:cases:{name}:count={count}:expected=1")

    stdout_packet = manifest.get("stdout_packet")
    if not isinstance(stdout_packet, list):
        issues.append("fixdep_manifest:stdout_packet:type")
        stdout_packet = []
    if stdout_packet != list(REQUIRED_STDOUT_PACKET):
        issues.append(
            f"fixdep_manifest:stdout_packet:actual={stdout_packet}:expected={list(REQUIRED_STDOUT_PACKET)}"
        )
    for packet in REQUIRED_STDOUT_PACKET:
        count = count_exact(stdout_packet, packet)
        if count != 1:
            issues.append(
                f"fixdep_manifest:stdout_packet:{packet}:count={count}:expected=1"
            )

    stderr_packet = manifest.get("stderr_packet")
    if not isinstance(stderr_packet, list):
        issues.append("fixdep_manifest:stderr_packet:type")
        stderr_packet = []
    if stderr_packet != list(REQUIRED_STDERR_PACKET):
        issues.append(
            f"fixdep_manifest:stderr_packet:actual={stderr_packet}:expected={list(REQUIRED_STDERR_PACKET)}"
        )
    for packet in REQUIRED_STDERR_PACKET:
        count = count_exact(stderr_packet, packet)
        if count != 1:
            issues.append(
                f"fixdep_manifest:stderr_packet:{packet}:count={count}:expected=1"
            )

    helper_local_anchors = manifest.get("helper_local_anchors")
    if not isinstance(helper_local_anchors, list):
        issues.append("fixdep_manifest:helper_local_anchors:type")
        helper_local_anchors = []
    if helper_local_anchors != list(REQUIRED_HELPER_ANCHORS):
        issues.append(
            "fixdep_manifest:helper_local_anchors:"
            f"actual={helper_local_anchors}:expected={list(REQUIRED_HELPER_ANCHORS)}"
        )
    for anchor in REQUIRED_HELPER_ANCHORS:
        count = count_exact(helper_local_anchors, anchor)
        if count != 1:
            issues.append(
                f"fixdep_manifest:helper_local_anchors:{anchor}:count={count}:expected=1"
            )
        source_count = fixdep_text.count(anchor)
        if source_count != 1:
            issues.append(
                f"fixdep_source_anchor:{anchor}:count={source_count}:expected=1"
            )

    return issues


def run_self_test() -> int:
    workflow_text = "\n".join(f"run: {marker}" for marker in REQUIRED_WORKFLOW_RUNS) + "\n"
    good_cases = [
        {
            "name": name,
            "expected": expected,
            **(
                {"expected_stderr": REQUIRED_STDERR_BY_CASE[name]}
                if name in REQUIRED_STDERR_BY_CASE
                else {}
            ),
        }
        for name, expected in REQUIRED_CASE_PACKET
    ]
    manifest_text = json.dumps(
        {
            "case_count": len(REQUIRED_CASE_PACKET),
            "cases": list(REQUIRED_CASE_NAMES),
            "stdout_packet": list(REQUIRED_STDOUT_PACKET),
            "stderr_packet": list(REQUIRED_STDERR_PACKET),
            "helper_local_anchors": list(REQUIRED_HELPER_ANCHORS),
        }
    )
    fixdep_text = "\n".join(
        f'test "{anchor}" {{}}' for anchor in REQUIRED_HELPER_ANCHORS
    ) + "\n"

    assert validate_texts(workflow_text, json.dumps(good_cases), manifest_text, fixdep_text) == []

    issues = validate_texts(
        workflow_text.replace(
            "run: python3 scripts/zigux/check-phase2-fixdep-gate.py\n",
            "",
            1,
        ),
        json.dumps(good_cases),
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
        json.dumps(good_cases),
        manifest_text,
        fixdep_text,
    )
    assert "workflow_exact_marker:python3 scripts/zigux/check-fixdep-diff.py:count=2:expected=1" in issues

    reduced_cases = [
        case for case in good_cases if case["name"] != "sample_escaped_hash_comment_chain"
    ]
    issues = validate_texts(
        workflow_text,
        json.dumps(reduced_cases),
        manifest_text,
        fixdep_text,
    )
    assert "fixdep_cases:sample_escaped_hash_comment_chain:count=0:expected=1" in issues

    bad_manifest = json.loads(manifest_text)
    bad_manifest["stdout_packet"] = list(REQUIRED_STDOUT_PACKET[:-1])
    issues = validate_texts(
        workflow_text,
        json.dumps(good_cases),
        json.dumps(bad_manifest),
        fixdep_text,
    )
    assert (
        "fixdep_manifest:stdout_packet:sample_escaped_hash_comment_chain_expected.txt:count=0:expected=1"
        in issues
    )

    bad_manifest = json.loads(manifest_text)
    bad_manifest["helper_local_anchors"] = list(REQUIRED_HELPER_ANCHORS[:-1])
    issues = validate_texts(
        workflow_text,
        json.dumps(good_cases),
        json.dumps(bad_manifest),
        fixdep_text,
    )
    assert (
        "fixdep_manifest:helper_local_anchors:escaped space dependency survives concatenated target comment path:count=0:expected=1"
        in issues
    )

    issues = validate_texts(
        workflow_text,
        json.dumps(good_cases),
        manifest_text,
        'test "other anchor" {}\n',
    )
    assert (
        "fixdep_source_anchor:dep parsing returns NoTargets for comment-only depfiles:count=0:expected=1"
        in issues
    )

    missing_tail_anchor_text = "\n".join(
        f'test "{anchor}" {{}}' for anchor in REQUIRED_HELPER_ANCHORS[:-1]
    ) + "\n"
    issues = validate_texts(
        workflow_text,
        json.dumps(good_cases),
        manifest_text,
        missing_tail_anchor_text,
    )
    assert (
        "fixdep_source_anchor:escaped space dependency survives concatenated target comment path:count=0:expected=1"
        in issues
    )

    bad_cases = [dict(case) for case in good_cases]
    for case in bad_cases:
        if case["name"] == "sample_escaped_colon":
            case["expected"] = "wrong_expected.txt"
    issues = validate_texts(
        workflow_text,
        json.dumps(bad_cases),
        manifest_text,
        fixdep_text,
    )
    assert (
        "fixdep_cases:sample_escaped_colon:expected_stdout:wrong_expected.txt:expected=sample_escaped_colon_expected.txt"
        in issues
    )

    bad_manifest = json.loads(manifest_text)
    bad_manifest["case_count"] = 6
    issues = validate_texts(
        workflow_text,
        json.dumps(good_cases),
        json.dumps(bad_manifest),
        fixdep_text,
    )
    assert "fixdep_manifest:case_count:6:expected=7" in issues

    print("PHASE2_FIXDEP_GATE_SELF_TEST=pass")
    print("PHASE2_FIXDEP_GATE_SELF_TEST_CASE_COUNT=10")
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
    print(f"PHASE2_FIXDEP_GATE_PACKET_CASE_COUNT={len(REQUIRED_CASE_PACKET)}")
    print(f"PHASE2_FIXDEP_GATE_PACKET_ANCHOR_COUNT={len(REQUIRED_HELPER_ANCHORS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
