#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
BRIDGE_CHECKER = ROOT / "scripts" / "zigux" / "check-genksyms-bridge.py"
VERSION_SIDE_EFFECT_TEST = ROOT / "scripts" / "zigux" / "genksyms_version_before_invalid_long_option_test.zig"
CASES_FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "cases.json"
MANIFEST_FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "manifest.json"
HELP_FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "help_expected.json"

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: make -C zigux phase2-genksyms",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
)

MAKEFILE_LINES = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py",
)

EXPECTED_SELF_TEST_CASE_COUNT = 15


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path, issue_code: str) -> tuple[object | None, tuple[str, str] | None]:
    try:
        return json.loads(read_text(path)), None
    except json.JSONDecodeError:
        return None, (issue_code, path.name)


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def extract_literal(module_text: str, const_name: str) -> object:
    module = ast.parse(module_text)
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == const_name:
                    return ast.literal_eval(node.value)
    raise ValueError(f"missing constant {const_name}")


def extract_bridge_packets(bridge_checker_text: str) -> tuple[list[dict[str, object]], tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    return (
        list(extract_literal(bridge_checker_text, "CASE_FIXTURES")),
        tuple(extract_literal(bridge_checker_text, "EXPECTED_PROCESS_OUTPUT_PACKET")),
        tuple(extract_literal(bridge_checker_text, "EXPECTED_HELPER_LOCAL_ANCHORS")),
        tuple(extract_literal(bridge_checker_text, "REQUIRED_VERSION_SIDE_EFFECT_TEST_LINES")),
    )


def build_expected_manifest(
    case_fixtures: list[dict[str, object]],
    process_output_packet: tuple[str, ...],
    helper_local_anchors: tuple[str, ...],
) -> dict[str, object]:
    return {
        "tool": "scripts/zigux/genksyms.zig",
        "status": "closed",
        "mode": "bounded wrapper-first dual-implementation bridge",
        "fixture_root": "zigux/tests/fixtures/genksyms_bridge",
        "fixture_case_source": "zigux/tests/fixtures/genksyms_bridge/cases.json",
        "case_count": len(case_fixtures),
        "cases": [str(case["name"]) for case in case_fixtures],
        "bridge_expected_packet": [str(case["expected_file"]) for case in case_fixtures],
        "help_packet": ["help_expected.json"],
        "standalone_proof_packet": [VERSION_SIDE_EFFECT_TEST.relative_to(ROOT).as_posix()],
        "process_output_packet": list(process_output_packet),
        "helper_local_anchors": list(helper_local_anchors),
    }


def collect_manifest_field_issues(manifest: object, expected: dict[str, object]) -> list[tuple[str, str]]:
    if not isinstance(manifest, dict):
        return [("INVALID_MANIFEST_PAYLOAD", type(manifest).__name__)]
    issues: list[tuple[str, str]] = []
    for key, expected_value in expected.items():
        actual_value = manifest.get(key)
        if actual_value != expected_value:
            issues.append(("MANIFEST_FIELD_MISMATCH", f"{key}:actual={actual_value!r}:expected={expected_value!r}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(root / WORKFLOW.relative_to(ROOT))
    makefile_text = read_text(root / MAKEFILE.relative_to(ROOT))
    bridge_checker_text = read_text(root / BRIDGE_CHECKER.relative_to(ROOT))
    version_side_effect_text = read_text(root / VERSION_SIDE_EFFECT_TEST.relative_to(ROOT))

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_HOOKS", f"{marker}:count={count}"))

    case_fixtures, process_output_packet, helper_local_anchors, version_side_effect_lines = extract_bridge_packets(bridge_checker_text)

    required_paths = [
        root / CASES_FIXTURE.relative_to(ROOT),
        root / MANIFEST_FIXTURE.relative_to(ROOT),
        root / HELP_FIXTURE.relative_to(ROOT),
    ]
    required_paths.extend(root / f"zigux/tests/fixtures/genksyms_bridge/{case['expected_file']}" for case in case_fixtures)
    required_paths.extend(root / f"zigux/tests/fixtures/genksyms_bridge/{name}" for name in process_output_packet)
    for path in required_paths:
        if not path.exists():
            issues.append(("MISSING_REQUIRED_PATHS", path.relative_to(root).as_posix()))
    if issues:
        return issues

    for marker in version_side_effect_lines:
        count = count_exact_lines(version_side_effect_text, marker)
        if count == 0:
            issues.append(("MISSING_VERSION_SIDE_EFFECT_TEST_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VERSION_SIDE_EFFECT_TEST_LINE", f"{marker}:count={count}"))

    cases_payload, cases_issue = read_json(root / CASES_FIXTURE.relative_to(ROOT), "INVALID_CASES_JSON")
    if cases_issue is not None:
        issues.append(cases_issue)
        return issues
    expected_cases = [
        {
            "name": case["name"],
            "args": case["args"],
            "expected_file": case["expected_file"],
        }
        for case in case_fixtures
    ]
    if cases_payload != expected_cases:
        issues.append(("CASE_PACKET_MISMATCH", CASES_FIXTURE.name))

    manifest_payload, manifest_issue = read_json(root / MANIFEST_FIXTURE.relative_to(ROOT), "INVALID_MANIFEST_JSON")
    if manifest_issue is not None:
        issues.append(manifest_issue)
        return issues
    issues.extend(
        collect_manifest_field_issues(
            manifest_payload,
            build_expected_manifest(case_fixtures, process_output_packet, helper_local_anchors),
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_GENKSYMS_ALIGNMENT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def render_bridge_checker_stub() -> str:
    case_fixtures = [
        {"name": "minimal", "args": [], "expected_file": "minimal_expected.json"},
        {"name": "debug_reference_types", "args": ["-d", "-r", "ref.symvers"], "expected_file": "debug_reference_types_expected.json"},
    ]
    process_output_packet = ("invalid_option_expected.json", "unexpected_long_help_argument_expected.json")
    helper_local_anchors = (
        "genksyms bridge treats pure version requests as version command",
        "genksyms bridge preserves repeated pure version invocations",
    )
    version_lines = (
        'test "genksyms bridge preserves version side effect before invalid long option" {',
        'test "genksyms bridge preserves abbreviated version side effect before invalid long option" {',
    )
    return (
        f"CASE_FIXTURES = {case_fixtures!r}\n"
        f"EXPECTED_PROCESS_OUTPUT_PACKET = {process_output_packet!r}\n"
        f"EXPECTED_HELPER_LOCAL_ANCHORS = {helper_local_anchors!r}\n"
        f"REQUIRED_VERSION_SIDE_EFFECT_TEST_LINES = {version_lines!r}\n"
    )


def build_self_test_root(root: Path) -> None:
    write_text(root / WORKFLOW.relative_to(ROOT), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(root / MAKEFILE.relative_to(ROOT), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(root / BRIDGE_CHECKER.relative_to(ROOT), render_bridge_checker_stub())
    write_text(
        root / VERSION_SIDE_EFFECT_TEST.relative_to(ROOT),
        'test "genksyms bridge preserves version side effect before invalid long option" {\n'
        '}\n'
        'test "genksyms bridge preserves abbreviated version side effect before invalid long option" {\n'
        '}\n',
    )
    bridge_checker_text = read_text(root / BRIDGE_CHECKER.relative_to(ROOT))
    case_fixtures, process_output_packet, helper_local_anchors, _ = extract_bridge_packets(bridge_checker_text)
    write_text(root / CASES_FIXTURE.relative_to(ROOT), json.dumps([
        {"name": case["name"], "args": case["args"], "expected_file": case["expected_file"]}
        for case in case_fixtures
    ], indent=2) + "\n")
    write_text(
        root / MANIFEST_FIXTURE.relative_to(ROOT),
        json.dumps(build_expected_manifest(case_fixtures, process_output_packet, helper_local_anchors), indent=2) + "\n",
    )
    write_text(root / HELP_FIXTURE.relative_to(ROOT), "{}\n")
    for case in case_fixtures:
        write_text(root / f"zigux/tests/fixtures/genksyms_bridge/{case['expected_file']}", "{}\n")
    for rel in process_output_packet:
        write_text(root / f"zigux/tests/fixtures/genksyms_bridge/{rel}", "{}\n")


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_genksyms_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        workflow_path = root / WORKFLOW.relative_to(ROOT)
        workflow_path.write_text(replace_exact_line(workflow_path.read_text(encoding="utf-8"), WORKFLOW_LINES[0], "run: python3 broken.py"), encoding="utf-8")
        assert ("MISSING_WORKFLOW_HOOKS", WORKFLOW_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = root / WORKFLOW.relative_to(ROOT)
        workflow_path.write_text(duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), WORKFLOW_LINES[4]), encoding="utf-8")
        assert ("DUPLICATE_WORKFLOW_HOOKS", f"{WORKFLOW_LINES[4]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path = root / MAKEFILE.relative_to(ROOT)
        makefile_path.write_text(replace_exact_line(makefile_path.read_text(encoding="utf-8"), MAKEFILE_LINES[3], "$(PYTHON) broken.py"), encoding="utf-8")
        assert ("MISSING_MAKEFILE_HOOKS", MAKEFILE_LINES[3]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path = root / MAKEFILE.relative_to(ROOT)
        makefile_path.write_text(
            duplicate_exact_line(makefile_path.read_text(encoding="utf-8"), MAKEFILE_LINES[4]),
            encoding="utf-8",
        )
        assert ("DUPLICATE_MAKEFILE_HOOKS", f"{MAKEFILE_LINES[4]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        cases_path = root / CASES_FIXTURE.relative_to(ROOT)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload[0]["expected_file"] = "drifted.json"
        cases_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("CASE_PACKET_MISMATCH", CASES_FIXTURE.name) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        cases_path = root / CASES_FIXTURE.relative_to(ROOT)
        cases_path.write_text("{broken\n", encoding="utf-8")
        assert ("INVALID_CASES_JSON", CASES_FIXTURE.name) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = root / MANIFEST_FIXTURE.relative_to(ROOT)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["cases"] = ["broken"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert any(code == "MANIFEST_FIELD_MISMATCH" and value.startswith("cases:") for code, value in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        manifest_path = root / MANIFEST_FIXTURE.relative_to(ROOT)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["helper_local_anchors"] = ["drifted anchor"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert any(code == "MANIFEST_FIELD_MISMATCH" and value.startswith("helper_local_anchors:") for code, value in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        manifest_path = root / MANIFEST_FIXTURE.relative_to(ROOT)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["standalone_proof_packet"] = []
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert any(code == "MANIFEST_FIELD_MISMATCH" and value.startswith("standalone_proof_packet:") for code, value in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        version_path = root / VERSION_SIDE_EFFECT_TEST.relative_to(ROOT)
        version_path.write_text(version_path.read_text(encoding="utf-8").replace('test "genksyms bridge preserves version side effect before invalid long option" {\n', '', 1), encoding="utf-8")
        assert any(code == "MISSING_VERSION_SIDE_EFFECT_TEST_LINE" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        version_path = root / VERSION_SIDE_EFFECT_TEST.relative_to(ROOT)
        version_path.write_text(duplicate_exact_line(version_path.read_text(encoding="utf-8"), 'test "genksyms bridge preserves abbreviated version side effect before invalid long option" {'), encoding="utf-8")
        assert any(code == "DUPLICATE_VERSION_SIDE_EFFECT_TEST_LINE" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        (root / HELP_FIXTURE.relative_to(ROOT)).unlink()
        assert ("MISSING_REQUIRED_PATHS", HELP_FIXTURE.relative_to(ROOT).as_posix()) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = root / MANIFEST_FIXTURE.relative_to(ROOT)
        manifest_path.write_text("{broken\n", encoding="utf-8")
        assert ("INVALID_MANIFEST_JSON", MANIFEST_FIXTURE.name) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        bridge_path = root / BRIDGE_CHECKER.relative_to(ROOT)
        bridge_path.write_text(bridge_path.read_text(encoding="utf-8").replace("EXPECTED_PROCESS_OUTPUT_PACKET = ('invalid_option_expected.json', 'unexpected_long_help_argument_expected.json')", "EXPECTED_PROCESS_OUTPUT_PACKET = ('invalid_option_expected.json',)", 1), encoding="utf-8")
        assert any(code == "MANIFEST_FIELD_MISMATCH" and value.startswith("process_output_packet:") for code, value in collect_issues(root))
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_GENKSYMS_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the current Phase 2 genksyms bridge packet stays aligned with its shared reminder and replay surfaces.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)
    print("PHASE2_GENKSYMS_ALIGNMENT=pass")
    print(f"PHASE2_GENKSYMS_ALIGNMENT_WORKFLOW_HOOK_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_GENKSYMS_ALIGNMENT_MAKEFILE_HOOK_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_GENKSYMS_ALIGNMENT_CASE_COUNT=derived")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())