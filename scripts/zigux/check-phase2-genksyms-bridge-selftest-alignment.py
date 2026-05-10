#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()
BRIDGE_CHECKER = Path("scripts/zigux/check-genksyms-bridge.py")
GENKSYMS_ZIG = Path("scripts/zigux/genksyms.zig")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
BRIDGE_CASES = Path("zigux/tests/fixtures/genksyms_bridge/cases.json")
BRIDGE_MANIFEST = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")
PHASE2_TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
BRIDGE_MANIFEST_PATH = "zigux/tests/fixtures/genksyms_bridge/manifest.json"
EXPECTED_HELPER_LOCAL_ANCHORS_NAME = "EXPECTED_HELPER_LOCAL_ANCHORS"
GENKSYMS_TEST_DECL_PATTERN = re.compile(r'^test "([^"]+)" \{$', re.MULTILINE)
BRIDGE_CONTRACT = {
    "tool": "scripts/genksyms/genksyms",
    "stdin": "cpp-stream",
    "stdout": "symversions",
    "argv_lead": "scripts/genksyms/genksyms",
    "options_fields": [
        "debug_level",
        "warnings",
        "dump_defs",
        "preserve",
        "reference_files",
        "dump_types_file",
    ],
}
EXPECTED_VERSION_STDERR_CASES = [
    "version",
    "abbreviated_version",
    "version_then_short_help",
    "version_then_long_help",
    "version_then_invalid_option",
]

REQUIRED_BRIDGE_MARKERS = (
    "print('GENKSYMS_BRIDGE_SELF_TEST=pass')",
    "print(f'GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}')",
)
REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
    "run: zig test scripts/zigux/genksyms.zig",
)
REQUIRED_MAKEFILE_LINES = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
    "phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def load_json(path: Path) -> object:
    return json.loads(read_text(path))


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def case_emits_version_stderr(argv: object) -> bool:
    if not isinstance(argv, list):
        return False
    for arg in argv:
        if not isinstance(arg, str):
            continue
        if arg.startswith("--ver"):
            return True
        if arg.startswith("-") and not arg.startswith("--") and "V" in arg[1:]:
            return True
    return False


def load_bridge_checker_helper_local_anchors(
    root: Path,
) -> tuple[list[str] | None, list[tuple[str, str]]]:
    bridge_checker_path = root / BRIDGE_CHECKER
    try:
        module = ast.parse(read_text(bridge_checker_path), filename=str(bridge_checker_path))
    except SyntaxError as exc:
        return None, [("BRIDGE_HELPER_LOCAL_ANCHOR_ISSUES", f"syntax:{exc.lineno}:{exc.msg}")]

    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == EXPECTED_HELPER_LOCAL_ANCHORS_NAME
            for target in node.targets
        ):
            continue
        try:
            value = ast.literal_eval(node.value)
        except (SyntaxError, ValueError) as exc:
            return None, [("BRIDGE_HELPER_LOCAL_ANCHOR_ISSUES", f"invalid_literal:{exc}")]
        if not isinstance(value, (list, tuple)):
            return None, [
                (
                    "BRIDGE_HELPER_LOCAL_ANCHOR_ISSUES",
                    f"{EXPECTED_HELPER_LOCAL_ANCHORS_NAME}:expected_list_or_tuple",
                )
            ]
        anchors = list(value)
        if any(not isinstance(item, str) or not item for item in anchors):
            return None, [
                (
                    "BRIDGE_HELPER_LOCAL_ANCHOR_ISSUES",
                    f"{EXPECTED_HELPER_LOCAL_ANCHORS_NAME}:expected_nonempty_string_entries",
                )
            ]
        return anchors, []

    return None, [("BRIDGE_HELPER_LOCAL_ANCHOR_ISSUES", f"missing:{EXPECTED_HELPER_LOCAL_ANCHORS_NAME}")]


def load_genksyms_test_names(
    root: Path,
) -> tuple[list[str] | None, list[tuple[str, str]]]:
    genksyms_path = root / GENKSYMS_ZIG
    try:
        text = genksyms_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None, [("BRIDGE_HELPER_LOCAL_ANCHOR_ISSUES", f"missing:{GENKSYMS_ZIG}")]

    names = GENKSYMS_TEST_DECL_PATTERN.findall(text)
    if not names:
        return None, [("BRIDGE_HELPER_LOCAL_ANCHOR_ISSUES", "missing:test_declarations")]

    issues: list[tuple[str, str]] = []
    seen_names: set[str] = set()
    for name in names:
        if name in seen_names:
            issues.append(("BRIDGE_HELPER_LOCAL_ANCHOR_ISSUES", f"duplicate_genksyms_zig_test:{name}"))
            continue
        seen_names.add(name)
    if issues:
        return None, issues
    return names, []


def collect_expected_manifest_payload(root: Path) -> tuple[dict[str, object] | None, list[tuple[str, str]]]:
    issues: list[tuple[str, str]] = []
    cases_path = root / BRIDGE_CASES
    manifest = load_json(cases_path)
    if not isinstance(manifest, dict):
        return None, [("CASE_PAYLOAD_ISSUES", "cases.json:expected_object")]

    helper_local_anchors, helper_local_anchor_issues = load_bridge_checker_helper_local_anchors(root)
    issues.extend(helper_local_anchor_issues)
    genksyms_test_names, genksyms_test_issues = load_genksyms_test_names(root)
    issues.extend(genksyms_test_issues)

    cases = manifest.get("cases")
    if not isinstance(cases, list):
        return None, [("CASE_PAYLOAD_ISSUES", "cases.json:cases:expected_list")]

    case_names: list[str] = []
    stdout_packet: list[str] = []
    process_packet: list[str] = []
    normalized_stderr_packet: list[str] = []
    normalized_stderr_cases: list[str] = []
    action_abbrev_cases: list[str] = []
    discovered_version_stderr_cases: list[str] = []
    seen_names: set[str] = set()

    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            issues.append(("CASE_PAYLOAD_ISSUES", f"cases[{index}]:expected_object"))
            continue

        name = case.get("name")
        if not isinstance(name, str) or not name:
            issues.append(("CASE_PAYLOAD_ISSUES", f"cases[{index}]:name:expected_nonempty_string"))
            continue
        if name in seen_names:
            issues.append(("CASE_PAYLOAD_ISSUES", f"duplicate_case_name:{name}"))
            continue
        seen_names.add(name)

        expected = case.get("expected")
        if not isinstance(expected, str) or not expected:
            issues.append(("CASE_PAYLOAD_ISSUES", f"{name}:expected:expected_nonempty_string"))
            continue

        mode = case.get("mode", "stdout_json")
        if mode not in {"stdout_json", "process_json"}:
            issues.append(("CASE_PAYLOAD_ISSUES", f"{name}:unsupported_mode:{mode}"))
            continue

        case_names.append(name)
        if mode == "stdout_json":
            stdout_packet.append(expected)
        else:
            process_packet.append(expected)
            if bool(case.get("normalize_stderr", False)):
                normalized_stderr_packet.append(expected)
                normalized_stderr_cases.append(name)
            if name.startswith("abbreviated_"):
                action_abbrev_cases.append(name)
            if case_emits_version_stderr(case.get("argv")):
                discovered_version_stderr_cases.append(name)

    if helper_local_anchors is not None and genksyms_test_names is not None:
        genksyms_test_name_set = set(genksyms_test_names)
        for anchor in helper_local_anchors:
            if anchor not in genksyms_test_name_set:
                issues.append(("BRIDGE_HELPER_LOCAL_ANCHOR_ISSUES", f"missing_genksyms_zig_test:{anchor}"))

    if issues or helper_local_anchors is None:
        return None, issues

    payload = {
        "tool": "scripts/zigux/genksyms.zig",
        "status": "closed",
        "mode": "wrapper-first bridge",
        "fixture_root": "zigux/tests/fixtures/genksyms_bridge",
        "fixture_case_source": "zigux/tests/fixtures/genksyms_bridge/cases.json",
        "harness": "zigux/tests/fixtures/genksyms_bridge/genksyms_bridge_c_harness.c",
        "bridge_contract": BRIDGE_CONTRACT,
        "case_count": len(case_names),
        "cases": case_names,
        "stdout_packet": ordered_unique(stdout_packet),
        "process_packet": ordered_unique(process_packet),
        "normalized_stderr_packet": ordered_unique(normalized_stderr_packet),
        "expected_output_governance": {
            "stdout_json_fields": ["tool", "stdin", "stdout", "argv", "options"],
            "process_json_fields": ["stdout", "stderr", "exit_code"],
            "normalized_stderr_cases": ordered_unique(normalized_stderr_cases),
            "version_stderr_cases": [
                name
                for name in EXPECTED_VERSION_STDERR_CASES
                if name in discovered_version_stderr_cases
            ],
        },
        "action_abbrev_cases": ordered_unique(action_abbrev_cases),
        "helper_local_anchors": helper_local_anchors,
    }
    return payload, []


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    bridge_text = read_text(root / BRIDGE_CHECKER)
    workflow_text = read_text(root / WORKFLOW)
    makefile_text = read_text(root / MAKEFILE)

    for marker in REQUIRED_BRIDGE_MARKERS:
        if marker not in bridge_text:
            issues.append(("MISSING_BRIDGE_MARKERS", marker))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_HOOKS", f"{marker}:count={count}"))

    manifest_path = root / BRIDGE_MANIFEST
    cases_path = root / BRIDGE_CASES
    phase2_tool_manifest_path = root / PHASE2_TOOL_MANIFEST
    for path in (manifest_path, cases_path, phase2_tool_manifest_path):
        if not path.exists():
            issues.append(("MISSING_MANIFEST_FILES", str(path.relative_to(root))))
    if any(block == "MISSING_MANIFEST_FILES" for block, _ in issues):
        return issues

    expected_manifest, manifest_issues = collect_expected_manifest_payload(root)
    issues.extend(manifest_issues)
    if expected_manifest is None:
        return issues

    manifest_payload = load_json(manifest_path)
    if not isinstance(manifest_payload, dict):
        issues.append(("MANIFEST_FIELD_MISMATCHES", "manifest.json:expected_object"))
        return issues

    phase2_tool_manifest = load_json(phase2_tool_manifest_path)
    if not isinstance(phase2_tool_manifest, dict):
        issues.append(("MANIFEST_POINTER_MISMATCH", "phase2_tool_manifest.json:expected_object"))
        return issues

    if phase2_tool_manifest.get("genksyms_bridge_packet") != BRIDGE_MANIFEST_PATH:
        issues.append(
            (
                "MANIFEST_POINTER_MISMATCH",
                f"genksyms_bridge_packet:{phase2_tool_manifest.get('genksyms_bridge_packet')}",
            )
        )

    for key, expected in expected_manifest.items():
        if manifest_payload.get(key) != expected:
            issues.append(
                (
                    "MANIFEST_FIELD_MISMATCHES",
                    f"{key}:expected={json.dumps(expected, sort_keys=True)}:actual={json.dumps(manifest_payload.get(key), sort_keys=True)}",
                )
            )

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for block, value in issues:
        grouped.setdefault(block, []).append(value)

    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT=fail")
    for block, values in grouped.items():
        print(f'{block}_START')
        for value in values:
            print(value)
        print(f'{block}_END')
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f'marker line not found: {marker}')


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f'marker line not found: {marker}')


def build_self_test_root(root: Path) -> None:
    write_text(
        root / BRIDGE_CHECKER,
        "\n".join(
            (
                "EXPECTED_HELPER_LOCAL_ANCHORS = [",
                "    'genksyms bridge parses repeated short flags and arguments',",
                "    'genksyms bridge reports invalid short option in getopt style',",
                "]",
                "",
                "SELF_TEST_CASE_COUNT = 7",
                "print('GENKSYMS_BRIDGE_SELF_TEST=pass')",
                "print(f'GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}')",
                "",
            )
        ),
    )
    write_text(
        root / GENKSYMS_ZIG,
        "\n".join(
            (
                'test "genksyms bridge parses repeated short flags and arguments" {',
                '}',
                'test "genksyms bridge reports invalid short option in getopt style" {',
                '}',
                '',
            )
        ),
    )
    write_text(
        root / WORKFLOW,
        "\n".join(
            (
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test Phase 2 genksyms bridge alignment",
                "        run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
                "      - name: Check Phase 2 genksyms bridge alignment",
                "        run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
                "      - name: Self-test bounded genksyms bridge parity checker",
                "        run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
                "      - name: Check bounded genksyms bridge parity",
                "        run: python3 scripts/zigux/check-genksyms-bridge.py",
                "      - name: Run bounded genksyms bridge unit tests",
                "        run: zig test scripts/zigux/genksyms.zig",
                "",
            )
        ),
    )
    write_text(
        root / MAKEFILE,
        "\n".join(
            (
                "phase2-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
                "phase2-tools:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
                "phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross",
                "",
            )
        ),
    )
    write_text(
        root / BRIDGE_CASES,
        json.dumps(
            {
                "cases": [
                    {"name": "minimal", "argv": [], "expected": "minimal_expected.json"},
                    {
                        "name": "abbreviated_help",
                        "argv": ["--hel"],
                        "mode": "process_json",
                        "expected": "help_expected.json",
                    },
                    {
                        "name": "invalid_option",
                        "argv": ["-x"],
                        "mode": "process_json",
                        "normalize_stderr": True,
                        "expected": "invalid_option_expected.json",
                    },
                ]
            },
            indent=2,
        )
        + "\n",
    )
    expected_manifest, issues = collect_expected_manifest_payload(root)
    assert expected_manifest is not None and issues == []
    write_text(root / BRIDGE_MANIFEST, json.dumps(expected_manifest, indent=2) + "\n")
    write_text(
        root / PHASE2_TOOL_MANIFEST,
        json.dumps({"genksyms_bridge_packet": BRIDGE_MANIFEST_PATH}, indent=2) + "\n",
    )


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_genksyms_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []

        build_self_test_root(root)
        path = root / BRIDGE_CHECKER
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_BRIDGE_MARKERS[0], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_BRIDGE_MARKERS", REQUIRED_BRIDGE_MARKERS[0]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(
            replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[0], "        run: python3 other.py"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_WORKFLOW_HOOKS", REQUIRED_WORKFLOW_LINES[0]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[1]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_WORKFLOW_HOOKS", f"{REQUIRED_WORKFLOW_LINES[1]}:count=2") in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(
            replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[2], "        run: python3 other.py --self-test"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_WORKFLOW_HOOKS", REQUIRED_WORKFLOW_LINES[2]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[3]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_WORKFLOW_HOOKS", f"{REQUIRED_WORKFLOW_LINES[3]}:count=2") in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(
            replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[4], "        run: zig test scripts/zigux/other.zig"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_WORKFLOW_HOOKS", REQUIRED_WORKFLOW_LINES[4]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / MAKEFILE
        path.write_text(
            replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[0], "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/other.py --self-test"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_MAKEFILE_HOOKS", REQUIRED_MAKEFILE_LINES[0]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / MAKEFILE
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[1]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_MAKEFILE_HOOKS", f"{REQUIRED_MAKEFILE_LINES[1]}:count=2") in issues
        cases += 1

        build_self_test_root(root)
        path = root / MAKEFILE
        path.write_text(
            replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[4], "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/other.zig"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_MAKEFILE_HOOKS", REQUIRED_MAKEFILE_LINES[4]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / MAKEFILE
        path.write_text(
            replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[5], "phase2: phase2-validate phase2-kconfig phase2-cross"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_MAKEFILE_HOOKS", REQUIRED_MAKEFILE_LINES[5]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / MAKEFILE
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[5]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_MAKEFILE_HOOKS", f"{REQUIRED_MAKEFILE_LINES[5]}:count=2") in issues
        cases += 1

        build_self_test_root(root)
        path = root / PHASE2_TOOL_MANIFEST
        path.write_text(json.dumps({"genksyms_bridge_packet": "zigux/tests/fixtures/other.json"}, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("MANIFEST_POINTER_MISMATCH", "genksyms_bridge_packet:zigux/tests/fixtures/other.json") in issues
        cases += 1

        build_self_test_root(root)
        path = root / BRIDGE_MANIFEST
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["case_count"] = 99
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(block == "MANIFEST_FIELD_MISMATCHES" and value.startswith("case_count:") for block, value in issues)
        cases += 1

        build_self_test_root(root)
        path = root / BRIDGE_MANIFEST
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["process_packet"] = ["wrong.json"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(block == "MANIFEST_FIELD_MISMATCHES" and value.startswith("process_packet:") for block, value in issues)
        cases += 1

        build_self_test_root(root)
        path = root / BRIDGE_MANIFEST
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["normalized_stderr_packet"] = []
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(block == "MANIFEST_FIELD_MISMATCHES" and value.startswith("normalized_stderr_packet:") for block, value in issues)
        cases += 1

        build_self_test_root(root)
        path = root / BRIDGE_MANIFEST
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["helper_local_anchors"] = ["wrong anchor"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(block == "MANIFEST_FIELD_MISMATCHES" and value.startswith("helper_local_anchors:") for block, value in issues)
        cases += 1

        build_self_test_root(root)
        path = root / BRIDGE_MANIFEST
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["bridge_contract"] = {"tool": "scripts/genksyms/genksyms", "stdin": "stdin", "stdout": "stdout"}
        payload["expected_output_governance"] = {"stdout_json_fields": ["tool"]}
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(block == "MANIFEST_FIELD_MISMATCHES" and value.startswith("bridge_contract:") for block, value in issues)
        assert any(block == "MANIFEST_FIELD_MISMATCHES" and value.startswith("expected_output_governance:") for block, value in issues)
        cases += 1

        build_self_test_root(root)
        path = root / BRIDGE_CASES
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cases"][0]["mode"] = "yaml"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("CASE_PAYLOAD_ISSUES", "minimal:unsupported_mode:yaml") in issues
        cases += 1

        build_self_test_root(root)
        path = root / BRIDGE_CASES
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cases"][1]["name"] = "minimal"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("CASE_PAYLOAD_ISSUES", "duplicate_case_name:minimal") in issues
        cases += 1

        build_self_test_root(root)
        path = root / GENKSYMS_ZIG
        path.write_text(
            "\n".join(
                (
                    'test "genksyms bridge parses repeated short flags and arguments" {',
                    '}',
                    '',
                )
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (
            "BRIDGE_HELPER_LOCAL_ANCHOR_ISSUES",
            "missing_genksyms_zig_test:genksyms bridge reports invalid short option in getopt style",
        ) in issues
        cases += 1

    assert cases == 20
    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 genksyms bridge self-test surface stays wired into CI and make routes."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT=pass")
    print(f"PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_BRIDGE_MARKER_COUNT={len(REQUIRED_BRIDGE_MARKERS)}")
    print(f"PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_WORKFLOW_HOOK_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_MAKEFILE_HOOK_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_MANIFEST_PATH=" + BRIDGE_MANIFEST_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
