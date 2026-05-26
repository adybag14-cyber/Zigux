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
CONFDATA_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "confdata_manifest.json"
CONFDATA_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"
KCONFIG_BRIDGE_CHECKER = ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py"
KCONFIG_CASES = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json"
PHASE2_VALIDATE = ROOT / "scripts" / "zigux" / "validate-phase2.py"
PHASE2_TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

REQUIRED_HELPER_ANCHORS = [
    "confdata bridge parses bounded config states",
    "confdata bridge keeps only the last assignment for duplicate symbols",
    "confdata bridge keeps explicit empty assignments distinct from quoted empty strings",
    "confdata bridge preserves duplicate unset ownership on allocation failure",
]

REQUIRED_WORKFLOW_LINES = [
    "run: python3 scripts/zigux/check-phase2-kconfig-confdata-helper-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-confdata-helper-packet.py",
]

REQUIRED_MAKEFILE_LINES = [
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-confdata-helper-packet.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-confdata-helper-packet.py",
]

REQUIRED_PHASE2_VALIDATE_MARKERS = [
    '"scripts/zigux/check-phase2-kconfig-confdata-helper-packet.py",',
    '"run: python3 scripts/zigux/check-phase2-kconfig-confdata-helper-packet.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-kconfig-confdata-helper-packet.py",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-confdata-helper-packet.py --self-test",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-confdata-helper-packet.py",',
]

REQUIRED_TOOL_MANIFEST_CHECKERS = [
    "scripts/zigux/check-phase2-kconfig-confdata-helper-packet.py",
]

BRIDGE_CHECKER_CONFDATA_CASES_CONST = "SAMPLE_CONFDATA_CASES"
BRIDGE_CHECKER_CONFDATA_HELPER_ANCHORS_CONST = "REQUIRED_CONFDATA_HELPER_ANCHORS"
SELF_TEST_CASE_COUNT = 10


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
    raise SystemExit(f"failed to parse {const_name} from {KCONFIG_BRIDGE_CHECKER}")


def load_bridge_checker_contract(path: Path) -> tuple[list[dict[str, object]], list[str]]:
    module_text = read_text(path)
    confdata_cases = extract_literal(module_text, BRIDGE_CHECKER_CONFDATA_CASES_CONST)
    helper_anchors = extract_literal(module_text, BRIDGE_CHECKER_CONFDATA_HELPER_ANCHORS_CONST)
    if not isinstance(confdata_cases, list) or not all(isinstance(case, dict) for case in confdata_cases):
        raise SystemExit("failed to parse confdata cases from check-kconfig-bridge.py")
    if not isinstance(helper_anchors, list) or not all(isinstance(anchor, str) for anchor in helper_anchors):
        raise SystemExit("failed to parse confdata helper anchors from check-kconfig-bridge.py")
    return list(confdata_cases), list(helper_anchors)


def load_tool_manifest_checkers(path: Path) -> list[str]:
    payload = read_json(path)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid tool manifest payload in {path}")
    present_surfaces = payload.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        raise SystemExit(f"invalid tool manifest present_surfaces in {path}")
    checkers = present_surfaces.get("checkers")
    if not isinstance(checkers, list) or not all(isinstance(entry, str) for entry in checkers):
        raise SystemExit(f"invalid tool manifest checker list in {path}")
    return list(checkers)


def build_expected_manifest(confdata_cases: list[dict[str, object]], helper_anchors: list[str]) -> dict[str, object]:
    return {
        "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
        "status": "closed",
        "mode": "bounded config bridge",
        "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
        "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
        "case_count": len(confdata_cases),
        "cases": [str(case["name"]) for case in confdata_cases],
        "input_packet": [str(case["input"]) for case in confdata_cases],
        "expected_packet": [str(case["expected"]) for case in confdata_cases],
        "helper_local_anchors": helper_anchors,
    }


def collect_exact_line_issues(path: Path, markers: list[str], missing_code: str, duplicate_code: str) -> list[tuple[str, str]]:
    text = read_text(path)
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

    manifest_path = root / CONFDATA_MANIFEST.relative_to(ROOT)
    bridge_path = root / CONFDATA_BRIDGE.relative_to(ROOT)
    checker_path = root / KCONFIG_BRIDGE_CHECKER.relative_to(ROOT)
    cases_path = root / KCONFIG_CASES.relative_to(ROOT)
    phase2_validate_path = root / PHASE2_VALIDATE.relative_to(ROOT)
    workflow_path = root / WORKFLOW.relative_to(ROOT)
    makefile_path = root / MAKEFILE.relative_to(ROOT)
    tool_manifest_path = root / PHASE2_TOOL_MANIFEST.relative_to(ROOT)

    bridge_cases, bridge_helper_anchors = load_bridge_checker_contract(checker_path)

    for anchor in REQUIRED_HELPER_ANCHORS:
        if anchor not in bridge_helper_anchors:
            issues.append(("CONFDATA_BRIDGE_CHECKER_MISSING_HELPER_ANCHOR", anchor))

    bridge_text = read_text(bridge_path)
    for anchor in REQUIRED_HELPER_ANCHORS:
        if anchor not in bridge_text:
            issues.append(("MISSING_CONFDATA_BRIDGE_HELPER_ANCHOR", anchor))

    cases_payload = read_json(cases_path)
    if not isinstance(cases_payload, dict):
        return [("INVALID_KCONFIG_CASES_PAYLOAD", type(cases_payload).__name__)]

    confdata_cases = cases_payload.get("confdata_cases")
    if confdata_cases != bridge_cases:
        issues.append(("CONFDATA_CASE_PACKET_MISMATCH", f"actual={confdata_cases!r}:expected={bridge_cases!r}"))

    manifest_payload = read_json(manifest_path)
    expected_manifest = build_expected_manifest(bridge_cases, bridge_helper_anchors)
    if manifest_payload != expected_manifest:
        issues.append(("CONFDATA_MANIFEST_MISMATCH", "root"))

    issues.extend(
        collect_exact_line_issues(
            workflow_path,
            REQUIRED_WORKFLOW_LINES,
            "MISSING_WORKFLOW_LINE",
            "DUPLICATE_WORKFLOW_LINE",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            makefile_path,
            REQUIRED_MAKEFILE_LINES,
            "MISSING_MAKEFILE_LINE",
            "DUPLICATE_MAKEFILE_LINE",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            phase2_validate_path,
            REQUIRED_PHASE2_VALIDATE_MARKERS,
            "MISSING_PHASE2_VALIDATE_MARKER",
            "DUPLICATE_PHASE2_VALIDATE_MARKER",
        )
    )

    manifest_checkers = load_tool_manifest_checkers(tool_manifest_path)
    for checker in REQUIRED_TOOL_MANIFEST_CHECKERS:
        if checker not in manifest_checkers:
            issues.append(("MISSING_TOOL_MANIFEST_CHECKER", checker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_KCONFIG_CONFDATA_HELPER_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def render_bridge_checker_stub(
    *,
    helper_anchors: list[str] | None = None,
    confdata_cases: list[dict[str, object]] | None = None,
) -> str:
    if helper_anchors is None:
        helper_anchors = list(REQUIRED_HELPER_ANCHORS)
    if confdata_cases is None:
        confdata_cases = [
            {"name": "sample", "input": "sample.config", "expected": "sample_expected.json"},
            {"name": "duplicate_assignments", "input": "duplicate_assignments.config", "expected": "duplicate_assignments_expected.json"},
        ]
    return (
        f"{BRIDGE_CHECKER_CONFDATA_HELPER_ANCHORS_CONST} = {helper_anchors!r}\n"
        f"{BRIDGE_CHECKER_CONFDATA_CASES_CONST} = {confdata_cases!r}\n"
    )


def build_self_test_root(root: Path) -> None:
    confdata_cases = [
        {"name": "sample", "input": "sample.config", "expected": "sample_expected.json"},
        {"name": "duplicate_assignments", "input": "duplicate_assignments.config", "expected": "duplicate_assignments_expected.json"},
    ]
    helper_anchors = list(REQUIRED_HELPER_ANCHORS)
    write_text(root / CONFDATA_BRIDGE.relative_to(ROOT), "\n".join(f'test "{anchor}" {{}}' for anchor in helper_anchors) + "\n")
    write_text(root / KCONFIG_BRIDGE_CHECKER.relative_to(ROOT), render_bridge_checker_stub(helper_anchors=helper_anchors, confdata_cases=confdata_cases))
    write_text(root / KCONFIG_CASES.relative_to(ROOT), json.dumps({"confdata_cases": confdata_cases}, indent=2) + "\n")
    write_text(root / CONFDATA_MANIFEST.relative_to(ROOT), json.dumps(build_expected_manifest(confdata_cases, helper_anchors), indent=2) + "\n")
    write_text(root / WORKFLOW.relative_to(ROOT), "\n".join(REQUIRED_WORKFLOW_LINES) + "\n")
    write_text(root / MAKEFILE.relative_to(ROOT), "\n".join(REQUIRED_MAKEFILE_LINES) + "\n")
    write_text(root / PHASE2_VALIDATE.relative_to(ROOT), "\n".join(REQUIRED_PHASE2_VALIDATE_MARKERS) + "\n")
    write_text(
        root / PHASE2_TOOL_MANIFEST.relative_to(ROOT),
        json.dumps({"present_surfaces": {"checkers": REQUIRED_TOOL_MANIFEST_CHECKERS}}, indent=2) + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_kconfig_confdata_helper_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        manifest_path = root / CONFDATA_MANIFEST.relative_to(ROOT)
        payload = read_json(manifest_path)
        assert isinstance(payload, dict)
        payload["helper_local_anchors"] = ["drifted anchor"]
        write_text(manifest_path, json.dumps(payload, indent=2) + "\n")
        assert ("CONFDATA_MANIFEST_MISMATCH", "root") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        checker_path = root / KCONFIG_BRIDGE_CHECKER.relative_to(ROOT)
        write_text(checker_path, render_bridge_checker_stub(helper_anchors=REQUIRED_HELPER_ANCHORS[:-1]))
        assert ("CONFDATA_BRIDGE_CHECKER_MISSING_HELPER_ANCHOR", REQUIRED_HELPER_ANCHORS[-1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        bridge_path = root / CONFDATA_BRIDGE.relative_to(ROOT)
        write_text(bridge_path, read_text(bridge_path).replace(REQUIRED_HELPER_ANCHORS[-1], "drifted anchor", 1))
        assert ("MISSING_CONFDATA_BRIDGE_HELPER_ANCHOR", REQUIRED_HELPER_ANCHORS[-1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        cases_path = root / KCONFIG_CASES.relative_to(ROOT)
        payload = read_json(cases_path)
        assert isinstance(payload, dict)
        payload["confdata_cases"][0]["expected"] = "drifted.json"
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        assert any(code == "CONFDATA_CASE_PACKET_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        workflow_path = root / WORKFLOW.relative_to(ROOT)
        write_text(workflow_path, REQUIRED_WORKFLOW_LINES[1] + "\n")
        assert ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = root / WORKFLOW.relative_to(ROOT)
        write_text(workflow_path, "\n".join((REQUIRED_WORKFLOW_LINES[0], REQUIRED_WORKFLOW_LINES[0], REQUIRED_WORKFLOW_LINES[1])) + "\n")
        assert ("DUPLICATE_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[0] + ":count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path = root / MAKEFILE.relative_to(ROOT)
        write_text(makefile_path, REQUIRED_MAKEFILE_LINES[1] + "\n")
        assert ("MISSING_MAKEFILE_LINE", REQUIRED_MAKEFILE_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        phase2_validate_path = root / PHASE2_VALIDATE.relative_to(ROOT)
        write_text(phase2_validate_path, REQUIRED_PHASE2_VALIDATE_MARKERS[1] + "\n")
        assert ("MISSING_PHASE2_VALIDATE_MARKER", REQUIRED_PHASE2_VALIDATE_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        tool_manifest_path = root / PHASE2_TOOL_MANIFEST.relative_to(ROOT)
        write_text(tool_manifest_path, json.dumps({"present_surfaces": {"checkers": []}}, indent=2) + "\n")
        assert ("MISSING_TOOL_MANIFEST_CHECKER", REQUIRED_TOOL_MANIFEST_CHECKERS[0]) in collect_issues(root)
        checks_run += 1

    if checks_run != SELF_TEST_CASE_COUNT:
        print("PHASE2_KCONFIG_CONFDATA_HELPER_PACKET_SELF_TEST=fail")
        print(f"PHASE2_KCONFIG_CONFDATA_HELPER_PACKET_SELF_TEST_CASE_COUNT_ACTUAL={checks_run}")
        print(f"PHASE2_KCONFIG_CONFDATA_HELPER_PACKET_SELF_TEST_CASE_COUNT_EXPECTED={SELF_TEST_CASE_COUNT}")
        return 1

    print("PHASE2_KCONFIG_CONFDATA_HELPER_PACKET_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_CONFDATA_HELPER_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the helper-local confdata bridge packet against the Phase 2 kconfig scaffolding.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    bridge_cases, _ = load_bridge_checker_contract(args.root.resolve() / KCONFIG_BRIDGE_CHECKER.relative_to(ROOT))
    print("PHASE2_KCONFIG_CONFDATA_HELPER_PACKET=pass")
    print(f"PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT={len(REQUIRED_HELPER_ANCHORS)}")
    print(f"PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT={len(bridge_cases)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
