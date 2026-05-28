#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
KCONFIG_BRIDGE_CHECKER = ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py"
KCONFIG_BRIDGE_CASES = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json"
CONF_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json"
CONFDATA_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "confdata_manifest.json"
KCONFIG_BRIDGE_SURFACE_PATHS = (
    ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig",
    ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig",
    KCONFIG_BRIDGE_CHECKER,
    KCONFIG_BRIDGE_CASES,
    CONF_MANIFEST,
    CONFDATA_MANIFEST,
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "run: python3 scripts/zigux/check-kconfig-bridge.py",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "run: make -C zigux phase2-kconfig",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
)

WORKFLOW_PATH_LINES = (
    "- 'scripts/kconfig/conf.c'",
    "- 'scripts/kconfig/confdata.c'",
)

MAKEFILE_LINES = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py",
)

SCRIPTS_README_MARKERS = (
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "the manifest-backed kconfig fixture roster",
)

TESTS_README_MARKERS = (
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "make -C zigux phase2-kconfig",
)

REVIEW_CHECKLIST_MARKERS = (
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "make -C zigux phase2-kconfig",
)

BRIDGE_CHECKER_LINE_MARKERS = (
    'if group_name == "conf_cases" and "silent" in case and not isinstance(case["silent"], bool):',
    'if "silent" in case and case["silent"] is not True:',
    'if case.get("silent"):',
    'if "mode_arg" in case:',
    'if "allconfig" in case:',
    'if "seed" in case:',
    'if "probability" in case:',
    'if "nosilentupdate" in case:',
    'cmd.append("silent")',
    'cmd.append(str(case["mode_arg"]))',
    'cmd.append(f"allconfig={case[\'allconfig\']}")',
    'cmd.append(f"seed={case[\'seed\']}")',
    'cmd.append(f"probability={case[\'probability\']}")',
    'cmd.append(f"nosilentupdate={case[\'nosilentupdate\']}")',
)

CONF_HELPER_ANCHOR_CONST = "REQUIRED_CONF_HELPER_ANCHORS"
CONFDATA_HELPER_ANCHOR_CONST = "REQUIRED_CONFDATA_HELPER_ANCHORS"
CONF_HELPER_IMPLICIT_OMISSION_MODES_CONST = "REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES"
CONF_HELPER_EXPLICIT_OVERRIDE_MODES_CONST = "REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES"
CONFDATA_CASE_PACKET_CONST = "SAMPLE_CONFDATA_CASES"
EXPECTED_SELF_TEST_CASE_COUNT = 8


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    return json.loads(read_text(path))


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def extract_literal(module_text: str, const_name: str) -> object:
    module = ast.parse(module_text)
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == const_name:
                return ast.literal_eval(node.value)
    raise SystemExit(f"missing constant {const_name} in {KCONFIG_BRIDGE_CHECKER}")


def load_bridge_checker_contract(path: Path) -> tuple[list[str], list[str], list[str], list[str], list[dict[str, object]]]:
    module_text = read_text(path)
    conf_anchors = extract_literal(module_text, CONF_HELPER_ANCHOR_CONST)
    confdata_anchors = extract_literal(module_text, CONFDATA_HELPER_ANCHOR_CONST)
    implicit_modes = extract_literal(module_text, CONF_HELPER_IMPLICIT_OMISSION_MODES_CONST)
    explicit_modes = extract_literal(module_text, CONF_HELPER_EXPLICIT_OVERRIDE_MODES_CONST)
    confdata_cases = extract_literal(module_text, CONFDATA_CASE_PACKET_CONST)
    return list(conf_anchors), list(confdata_anchors), list(implicit_modes), list(explicit_modes), list(confdata_cases)


def build_conf_manifest_payload(conf_cases: list[dict[str, object]], conf_anchors: list[str], implicit_modes: list[str], explicit_modes: list[str]) -> dict[str, object]:
    return {
        "tool": "scripts/zigux/kconfig/conf_bridge.zig",
        "status": "closed",
        "mode": "bounded request-plan bridge",
        "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
        "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
        "case_count": len(conf_cases),
        "cases": [case["name"] for case in conf_cases],
        "stdout_packet": [case["expected"] for case in conf_cases],
        "mode_arg_cases": [case["name"] for case in conf_cases if "mode_arg" in case],
        "silent_request_packet": [case["expected"] for case in conf_cases if case.get("silent") is True],
        "syncconfig_env_packet": [case["expected"] for case in conf_cases if "nosilentupdate" in case],
        "allconfig_sentinel_packet": [case["expected"] for case in conf_cases if case["mode"] in ("allnoconfig", "allyesconfig", "alldefconfig")],
        "allconfig_override_packet": [case["expected"] for case in conf_cases if "allconfig" in case],
        "helper_local_allconfig_implicit_omission_modes": implicit_modes,
        "helper_local_allconfig_explicit_override_modes": explicit_modes,
        "randconfig_env_packet": [case["expected"] for case in conf_cases if "seed" in case or "probability" in case],
        "helper_local_anchors": conf_anchors,
    }


def build_confdata_manifest_payload(confdata_cases: list[dict[str, object]], confdata_anchors: list[str]) -> dict[str, object]:
    return {
        "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
        "status": "closed",
        "mode": "bounded config bridge",
        "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
        "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
        "case_count": len(confdata_cases),
        "cases": [case["name"] for case in confdata_cases],
        "input_packet": [case["input"] for case in confdata_cases],
        "expected_packet": [case["expected"] for case in confdata_cases],
        "helper_local_anchors": confdata_anchors,
    }


def collect_marker_issues(text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(root / WORKFLOW.relative_to(ROOT))
    makefile_text = read_text(root / MAKEFILE.relative_to(ROOT))
    scripts_readme_text = read_text(root / SCRIPTS_README.relative_to(ROOT))
    tests_readme_text = read_text(root / TESTS_README.relative_to(ROOT))
    checklist_text = read_text(root / REVIEW_CHECKLIST.relative_to(ROOT))
    checker_path = root / KCONFIG_BRIDGE_CHECKER.relative_to(ROOT)
    checker_text = read_text(checker_path)
    cases_payload = read_json(root / KCONFIG_BRIDGE_CASES.relative_to(ROOT))
    conf_manifest = read_json(root / CONF_MANIFEST.relative_to(ROOT))
    confdata_manifest = read_json(root / CONFDATA_MANIFEST.relative_to(ROOT))

    issues.extend(collect_marker_issues(workflow_text, WORKFLOW_LINES, "MISSING_WORKFLOW_HOOKS", "DUPLICATE_WORKFLOW_HOOKS"))
    issues.extend(collect_marker_issues(workflow_text, WORKFLOW_PATH_LINES, "MISSING_WORKFLOW_PATH_FILTERS", "DUPLICATE_WORKFLOW_PATH_FILTERS"))
    issues.extend(collect_marker_issues(makefile_text, MAKEFILE_LINES, "MISSING_MAKEFILE_HOOKS", "DUPLICATE_MAKEFILE_HOOKS"))
    issues.extend(collect_marker_issues(checker_text, BRIDGE_CHECKER_LINE_MARKERS, "MISSING_BRIDGE_CHECKER_MARKERS", "DUPLICATE_BRIDGE_CHECKER_MARKERS"))

    for marker in SCRIPTS_README_MARKERS:
        if marker not in scripts_readme_text:
            issues.append(("MISSING_SCRIPTS_README_MARKERS", marker))
    for marker in TESTS_README_MARKERS:
        if marker not in tests_readme_text:
            issues.append(("MISSING_TESTS_README_MARKERS", marker))
    for marker in REVIEW_CHECKLIST_MARKERS:
        if marker not in checklist_text:
            issues.append(("MISSING_REVIEW_CHECKLIST_MARKERS", marker))

    conf_anchors, confdata_anchors, implicit_modes, explicit_modes, checker_confdata_cases = load_bridge_checker_contract(checker_path)
    if not isinstance(cases_payload, dict):
        return [("INVALID_CASES_PAYLOAD", type(cases_payload).__name__)]
    conf_cases = cases_payload.get("conf_cases")
    confdata_cases = cases_payload.get("confdata_cases")
    if not isinstance(conf_cases, list) or not isinstance(confdata_cases, list):
        return [("INVALID_CASES_FIELDS", "conf_cases/confdata_cases")]

    if [case.get("name") for case in confdata_cases] != [case.get("name") for case in checker_confdata_cases]:
        issues.append(("CONFDATA_CASE_PACKET_MISMATCH", "name packet"))
    if conf_manifest != build_conf_manifest_payload(conf_cases, conf_anchors, implicit_modes, explicit_modes):
        issues.append(("CONF_MANIFEST_FIELD_MISMATCH", "conf manifest drift"))
    if confdata_manifest != build_confdata_manifest_payload(confdata_cases, confdata_anchors):
        issues.append(("CONFDATA_MANIFEST_FIELD_MISMATCH", "confdata manifest drift"))

    for bridge_path in KCONFIG_BRIDGE_SURFACE_PATHS:
        if not (root / bridge_path.relative_to(ROOT)).exists():
            issues.append(("MISSING_BRIDGE_SURFACE_PATHS", bridge_path.relative_to(ROOT).as_posix()))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_KCONFIG_ALIGNMENT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def render_checker_stub() -> str:
    return '''
REQUIRED_CONF_HELPER_ANCHORS = []
REQUIRED_CONFDATA_HELPER_ANCHORS = []
REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES = []
REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES = []
SAMPLE_CONFDATA_CASES = []

def build_conf_command(case):
    cmd = []
    group_name = "conf_cases"
    if group_name == "conf_cases" and "silent" in case and not isinstance(case["silent"], bool):
        return cmd
    if "silent" in case and case["silent"] is not True:
        return cmd
    if case.get("silent"):
        cmd.append("silent")
    if "mode_arg" in case:
        cmd.append(str(case["mode_arg"]))
    if "allconfig" in case:
        cmd.append(f"allconfig={case['allconfig']}")
    if "seed" in case:
        cmd.append(f"seed={case['seed']}")
    if "probability" in case:
        cmd.append(f"probability={case['probability']}")
    if "nosilentupdate" in case:
        cmd.append(f"nosilentupdate={case['nosilentupdate']}")
    return cmd
'''


def build_self_test_root(root: Path) -> None:
    write_text(root / WORKFLOW.relative_to(ROOT), "\n".join(("name: zigux-bootstrap", *WORKFLOW_PATH_LINES, *WORKFLOW_LINES)) + "\n")
    write_text(root / MAKEFILE.relative_to(ROOT), "\n".join(("PYTHON ?= python3", "ZIG ?= zig", "PHASE2_SCRIPT_ROOT := ../scripts/zigux", "ZIGUX_ROOT := ..", *MAKEFILE_LINES)) + "\n")
    write_text(root / SCRIPTS_README.relative_to(ROOT), "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(root / TESTS_README.relative_to(ROOT), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(root / REVIEW_CHECKLIST.relative_to(ROOT), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(root / KCONFIG_BRIDGE_CHECKER.relative_to(ROOT), render_checker_stub())
    write_text(root / KCONFIG_BRIDGE_CASES.relative_to(ROOT), json.dumps({"conf_cases": [], "confdata_cases": []}, indent=2) + "\n")
    write_text(root / CONF_MANIFEST.relative_to(ROOT), json.dumps(build_conf_manifest_payload([], [], [], []), indent=2) + "\n")
    write_text(root / CONFDATA_MANIFEST.relative_to(ROOT), json.dumps(build_confdata_manifest_payload([], []), indent=2) + "\n")
    write_text(root / (ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig").relative_to(ROOT), "test \"placeholder\" {}\n")
    write_text(root / (ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig").relative_to(ROOT), "test \"placeholder\" {}\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_kconfig_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1
        build_self_test_root(root)
        (root / KCONFIG_BRIDGE_CASES.relative_to(ROOT)).write_text("[]\n", encoding="utf-8")
        assert collect_issues(root) == [("INVALID_CASES_PAYLOAD", "list")]
        checks_run += 1
        build_self_test_root(root)
        (root / WORKFLOW.relative_to(ROOT)).write_text("name: zigux-bootstrap\n", encoding="utf-8")
        assert any(code == "MISSING_WORKFLOW_HOOKS" for code, _ in collect_issues(root))
        checks_run += 1
        build_self_test_root(root)
        (root / MAKEFILE.relative_to(ROOT)).write_text("PYTHON ?= python3\n", encoding="utf-8")
        assert any(code == "MISSING_MAKEFILE_HOOKS" for code, _ in collect_issues(root))
        checks_run += 1
        build_self_test_root(root)
        (root / SCRIPTS_README.relative_to(ROOT)).write_text("\n", encoding="utf-8")
        assert any(code == "MISSING_SCRIPTS_README_MARKERS" for code, _ in collect_issues(root))
        checks_run += 1
        build_self_test_root(root)
        (root / CONF_MANIFEST.relative_to(ROOT)).write_text("{}\n", encoding="utf-8")
        assert any(code == "CONF_MANIFEST_FIELD_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1
        build_self_test_root(root)
        (root / CONFDATA_MANIFEST.relative_to(ROOT)).write_text("{}\n", encoding="utf-8")
        assert any(code == "CONFDATA_MANIFEST_FIELD_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1
        build_self_test_root(root)
        (root / (ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig").relative_to(ROOT)).unlink()
        assert any(code == "MISSING_BRIDGE_SURFACE_PATHS" for code, _ in collect_issues(root))
        checks_run += 1
    if checks_run != EXPECTED_SELF_TEST_CASE_COUNT:
        print("PHASE2_KCONFIG_ALIGNMENT_SELF_TEST=fail")
        print(f"PHASE2_KCONFIG_ALIGNMENT_SELF_TEST_CASE_COUNT_ACTUAL={checks_run}")
        print(f"PHASE2_KCONFIG_ALIGNMENT_SELF_TEST_CASE_COUNT_EXPECTED={EXPECTED_SELF_TEST_CASE_COUNT}")
        return 1
    print("PHASE2_KCONFIG_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check current Phase 2 kconfig reminder surfaces against the live bridge packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)
    print("PHASE2_KCONFIG_ALIGNMENT=pass")
    print(f"PHASE2_KCONFIG_ALIGNMENT_WORKFLOW_HOOK_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_MAKEFILE_HOOK_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_BRIDGE_SURFACE_COUNT={len(KCONFIG_BRIDGE_SURFACE_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
