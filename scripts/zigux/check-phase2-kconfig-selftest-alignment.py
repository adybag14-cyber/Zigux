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
KCONFIG_FIXTURE_ROOT = KCONFIG_BRIDGE_CASES.parent
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
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
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

EXPECTED_SILENT_CONF_CASE_NAMES = ("listnewconfig", "helpnewconfig")
EXPECTED_MODE_ARG_CASE_NAMES = ("defconfig", "savedefconfig")
EXPECTED_ALLCONFIG_OVERRIDE_CASE_NAMES = ("allnoconfig", "allmodconfig", "alldefconfig", "randconfig")
EXPECTED_SYNCCONFIG_ENV_CASE_NAMES = ("syncconfig",)
EXPECTED_RANDCONFIG_ENV_CASE_NAMES = ("randconfig",)

CONF_MANIFEST_STATIC_FIELDS = {
    "tool": "scripts/zigux/kconfig/conf_bridge.zig",
    "status": "closed",
    "mode": "bounded request-plan bridge",
    "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
    "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
}

CONFDATA_MANIFEST_STATIC_FIELDS = {
    "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
    "status": "closed",
    "mode": "bounded config bridge",
    "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
    "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
}

CONF_HELPER_ANCHOR_CONST = "REQUIRED_CONF_HELPER_ANCHORS"
CONFDATA_HELPER_ANCHOR_CONST = "REQUIRED_CONFDATA_HELPER_ANCHORS"
CONF_HELPER_IMPLICIT_OMISSION_MODES_CONST = "REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES"
CONF_HELPER_EXPLICIT_OVERRIDE_MODES_CONST = "REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES"
CONFDATA_CASE_PACKET_CONST = "SAMPLE_CONFDATA_CASES"

VALID_CONF_HELPER_ANCHORS = (
    "conf bridge mode surface stays aligned with conf.c long options",
    "conf bridge emits olddefconfig argv and env",
    "conf bridge emits syncconfig auto files",
    "conf bridge emits syncconfig nosilentupdate when present",
    "conf bridge omits empty syncconfig nosilentupdate",
    "conf bridge emits silent flag before mode flag",
    "conf bridge emits alldefconfig argv and env",
    "conf bridge emits explicit empty allconfig override for allmodconfig",
    "conf bridge emits randconfig tunables when present",
    "conf bridge emits explicit randconfig allconfig override when present",
    "conf bridge omits randconfig allconfig sentinel without explicit override",
    "conf bridge emits yes2modconfig argv and env",
    "conf bridge emits defconfig mode argument before kconfig",
    "conf bridge emits savedefconfig mode argument before kconfig",
    "conf bridge escapes low control bytes in JSON strings",
    "mode argument validation rejects bridge option shaped defconfig payload",
    "mode argument validation accepts defconfig path that only starts with silent",
    "mode argument validation still accepts ordinary path text with equals",
    "bridge options parser accepts explicit allconfig override for allmodconfig",
    "bridge options parser accepts syncconfig nosilentupdate",
    "bridge options parser keeps empty syncconfig nosilentupdate unset",
    "bridge options parser accepts generic silent flag",
    "bridge options parser accepts silent alongside randconfig options",
    "bridge options parser rejects duplicate silent flag",
    "bridge options parser rejects duplicate randconfig probability",
    "bridge options parser rejects unexpected options for mode",
    "bridge options parser keeps empty randconfig tunables unset",
    "bridge options parser rejects duplicate mode specific options",
)

VALID_CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES = (
    "allmodconfig",
    "randconfig",
)

VALID_CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES = (
    "allmodconfig",
    "allnoconfig",
    "allyesconfig",
    "alldefconfig",
    "randconfig",
)

VALID_CONFDATA_HELPER_ANCHORS = (
    "confdata bridge parses bounded config states",
    "confdata bridge emits bounded json output",
    "confdata bridge decodes escaped quoted strings",
    "confdata bridge strips backslashes from escaped control sequences like upstream confdata",
    "confdata bridge escapes low control bytes in json output",
    "confdata bridge accepts CRLF config lines",
    "confdata bridge preserves trailing carriage return on final unterminated value line",
    "confdata bridge ignores unterminated unset comment with trailing carriage return",
    "confdata bridge ignores suffix bytes after an embedded NUL",
    "confdata bridge preserves carriage return before an embedded NUL on newline-terminated lines",
    "confdata bridge keeps explicit n assignments as tristate values",
    "confdata bridge recognizes uppercase tristate assignments",
    "confdata bridge ignores non-CONFIG lines like upstream confdata",
    "confdata bridge ignores empty CONFIG symbol names",
    "confdata bridge ignores malformed unset comments with extra tokens",
    "confdata bridge keeps trailing escaped backslashes in quoted strings",
    "confdata bridge ignores trailing suffix bytes after a closing quote like upstream confdata",
    "confdata bridge ignores malformed quoted values like upstream confdata",
    "confdata bridge emits no entries for empty CONFIG symbol names",
    "confdata bridge keeps only the last assignment for duplicate symbols",
    "confdata bridge keeps the prior duplicate value when a later quoted assignment is malformed",
    "confdata bridge emits the preserved duplicate state after later malformed quoted assignments",
    "confdata bridge keeps only the last state across unset and set transitions",
    "confdata bridge keeps explicit empty assignments distinct from quoted empty strings",
    "confdata bridge emits explicit empty assignments distinctly in json output",
    "confdata bridge escapes parsed string bytes in json output",
    "confdata bridge releases appended entry ownership on index-allocation failure",
    "confdata bridge preserves duplicate unset ownership on allocation failure",
)

VALID_CASES_PAYLOAD = {
    "conf_cases": [
        {"name": "oldaskconfig", "mode": "oldaskconfig", "kconfig": "Kconfig", "config": "ask/.config", "arch": "x86_64", "expected": "oldaskconfig_expected.json"},
        {"name": "syncconfig", "mode": "syncconfig", "kconfig": "Kconfig", "config": "out/.config", "arch": "riscv64", "nosilentupdate": "1", "expected": "syncconfig_expected.json"},
        {"name": "oldconfig", "mode": "oldconfig", "kconfig": "Kconfig", "config": "refresh/.config", "arch": "x86", "expected": "oldconfig_expected.json"},
        {"name": "allnoconfig", "mode": "allnoconfig", "kconfig": "Kconfig", "config": "none/.config", "arch": "arm64", "allconfig": "mini-all.config", "expected": "allnoconfig_expected.json"},
        {"name": "allyesconfig", "mode": "allyesconfig", "kconfig": "Kconfig", "config": "yes/.config", "arch": "arm64", "expected": "allyesconfig_expected.json"},
        {"name": "allmodconfig", "mode": "allmodconfig", "kconfig": "Kconfig", "config": "mod/.config", "arch": "arm", "allconfig": "", "expected": "allmodconfig_expected.json"},
        {"name": "alldefconfig", "mode": "alldefconfig", "kconfig": "Kconfig", "config": "build/.config", "arch": "arm64", "allconfig": "mini-all.config", "expected": "alldefconfig_expected.json"},
        {"name": "randconfig", "mode": "randconfig", "kconfig": "Kconfig", "config": "rand/.config", "arch": "x86_64", "allconfig": "", "seed": "0xC0FFEE", "probability": "15:25", "expected": "randconfig_expected.json"},
        {"name": "defconfig", "mode": "defconfig", "kconfig": "Kconfig", "config": "out/.config", "arch": "arm64", "mode_arg": "arch/arm64/configs/defconfig", "expected": "defconfig_expected.json"},
        {"name": "savedefconfig", "mode": "savedefconfig", "kconfig": "Kconfig", "config": ".config", "arch": "x86_64", "mode_arg": "silent=debug_defconfig", "expected": "savedefconfig_expected.json"},
        {"name": "listnewconfig", "mode": "listnewconfig", "kconfig": "Kconfig", "config": "out/list.config", "arch": "x86_64", "silent": true, "expected": "listnewconfig_expected.json"},
        {"name": "helpnewconfig", "mode": "helpnewconfig", "kconfig": "Kconfig", "config": "out/help.config", "arch": "riscv64", "silent": true, "expected": "helpnewconfig_expected.json"},
        {"name": "olddefconfig", "mode": "olddefconfig", "kconfig": "Kconfig", "config": ".config", "arch": "x86_64", "expected": "olddefconfig_expected.json"},
        {"name": "yes2modconfig", "mode": "yes2modconfig", "kconfig": "Kconfig", "config": "rewrite/.config", "arch": "x86", "expected": "yes2modconfig_expected.json"},
        {"name": "mod2yesconfig", "mode": "mod2yesconfig", "kconfig": "Kconfig", "config": "promote/.config", "arch": "x86", "expected": "mod2yesconfig_expected.json"},
        {"name": "mod2noconfig", "mode": "mod2noconfig", "kconfig": "Kconfig", "config": "demote/.config", "arch": "x86", "expected": "mod2noconfig_expected.json"}
    ],
    "confdata_cases": [
        {"name": "sample", "input": "sample.config", "expected": "sample_expected.json"},
        {"name": "escaped_strings", "input": "escaped_strings.config", "expected": "escaped_strings_expected.json"},
        {"name": "escaped_control_sequences", "input": "escaped_control_sequences.config", "expected": "escaped_control_sequences_expected.json"},
        {"name": "trailing_escaped_backslash", "input": "trailing_escaped_backslash.config", "expected": "trailing_escaped_backslash_expected.json"},
        {"name": "sample_crlf", "input": "sample_crlf.config", "expected": "sample_crlf_expected.json"},
        {"name": "explicit_n_tristate", "input": "explicit_n_tristate.config", "expected": "explicit_n_tristate_expected.json"},
        {"name": "final_trailing_carriage_return", "input": "final_trailing_carriage_return.config", "expected": "final_trailing_carriage_return_expected.json"},
        {"name": "final_unterminated_unset_comment", "input": "final_unterminated_unset_comment.config", "expected": "final_unterminated_unset_comment_expected.json"},
        {"name": "uppercase_tristate", "input": "uppercase_tristate.config", "expected": "uppercase_tristate_expected.json"},
        {"name": "non_config_lines", "input": "non_config_lines.config", "expected": "non_config_lines_expected.json"},
        {"name": "empty_config_symbol_names", "input": "empty_config_symbol_names.config", "expected": "empty_config_symbol_names_expected.json"},
        {"name": "malformed_unset_comment_tokens", "input": "malformed_unset_comment_tokens.config", "expected": "malformed_unset_comment_tokens_expected.json"},
        {"name": "last_state_transitions", "input": "last_state_transitions.config", "expected": "last_state_transitions_expected.json"},
        {"name": "duplicate_assignments", "input": "duplicate_assignments.config", "expected": "duplicate_assignments_expected.json"},
        {"name": "duplicate_malformed_quoted_assignment", "input": "duplicate_malformed_quoted_assignment.config", "expected": "duplicate_malformed_quoted_assignment_expected.json"},
        {"name": "explicit_empty_assignments", "input": "explicit_empty_assignments.config", "expected": "explicit_empty_assignments_expected.json"}
    ]
}

EXPECTED_SELF_TEST_CASE_COUNT = 24


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    return json.loads(read_text(path))


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def extract_literal(module_text: str, const_name: str) -> object:
    module = ast.parse(module_text)
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == const_name:
                return ast.literal_eval(node.value)
    raise ValueError(f"missing constant {const_name}")


def extract_string_sequence(module_text: str, const_name: str) -> tuple[str, ...]:
    value = extract_literal(module_text, const_name)
    if not isinstance(value, (list, tuple)) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{const_name} must be a string sequence")
    return tuple(value)


def extract_case_mapping_sequence(module_text: str, const_name: str) -> tuple[dict[str, object], ...]:
    value = extract_literal(module_text, const_name)
    if not isinstance(value, list):
        raise ValueError(f"{const_name} must be a list")
    cases: list[dict[str, object]] = []
    for index, case in enumerate(value):
        if not isinstance(case, dict):
            raise ValueError(f"{const_name} entry {index} must be a dict")
        cases.append(case)
    return tuple(cases)


def load_bridge_checker_anchor_packets(
    bridge_checker_text: str,
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[dict[str, object], ...]]:
    return (
        extract_string_sequence(bridge_checker_text, CONF_HELPER_ANCHOR_CONST),
        extract_string_sequence(bridge_checker_text, CONFDATA_HELPER_ANCHOR_CONST),
        extract_string_sequence(bridge_checker_text, CONF_HELPER_IMPLICIT_OMISSION_MODES_CONST),
        extract_string_sequence(bridge_checker_text, CONF_HELPER_EXPLICIT_OVERRIDE_MODES_CONST),
        extract_case_mapping_sequence(bridge_checker_text, CONFDATA_CASE_PACKET_CONST),
    )


def extract_dict_case_list(raw_cases: list[object], *, entry_code: str) -> tuple[list[dict[str, object]], list[tuple[str, str]]]:
    cases: list[dict[str, object]] = []
    issues: list[tuple[str, str]] = []
    for index, case in enumerate(raw_cases):
        if not isinstance(case, dict):
            issues.append((entry_code, f"{index}:{type(case).__name__}"))
            continue
        cases.append(case)
    return cases, issues


def build_conf_manifest_payload(
    conf_cases: list[dict[str, object]],
    conf_helper_anchors: tuple[str, ...],
    implicit_omission_modes: tuple[str, ...],
    explicit_override_modes: tuple[str, ...],
) -> dict[str, object]:
    return {
        **CONF_MANIFEST_STATIC_FIELDS,
        "case_count": len(conf_cases),
        "cases": [case["name"] for case in conf_cases],
        "stdout_packet": [case["expected"] for case in conf_cases],
        "mode_arg_cases": [case["name"] for case in conf_cases if "mode_arg" in case],
        "silent_request_packet": [case["expected"] for case in conf_cases if case.get("silent") is True],
        "syncconfig_env_packet": [case["expected"] for case in conf_cases if "nosilentupdate" in case],
        "allconfig_sentinel_packet": [case["expected"] for case in conf_cases if case["mode"] in ("allnoconfig", "allyesconfig", "alldefconfig")],
        "allconfig_override_packet": [case["expected"] for case in conf_cases if "allconfig" in case],
        "helper_local_allconfig_implicit_omission_modes": list(implicit_omission_modes),
        "helper_local_allconfig_explicit_override_modes": list(explicit_override_modes),
        "randconfig_env_packet": [case["expected"] for case in conf_cases if "seed" in case or "probability" in case],
        "helper_local_anchors": list(conf_helper_anchors),
    }


def build_confdata_manifest_payload(
    confdata_cases: list[dict[str, object]],
    confdata_helper_anchors: tuple[str, ...],
) -> dict[str, object]:
    return {
        **CONFDATA_MANIFEST_STATIC_FIELDS,
        "case_count": len(confdata_cases),
        "cases": [case["name"] for case in confdata_cases],
        "input_packet": [case["input"] for case in confdata_cases],
        "expected_packet": [case["expected"] for case in confdata_cases],
        "helper_local_anchors": list(confdata_helper_anchors),
    }


def collect_manifest_field_issues(
    manifest: object,
    *,
    expected_fields: dict[str, object],
    invalid_payload_code: str,
    field_mismatch_code: str,
) -> list[tuple[str, str]]:
    if not isinstance(manifest, dict):
        return [(invalid_payload_code, type(manifest).__name__)]
    issues: list[tuple[str, str]] = []
    for field_name, expected_value in expected_fields.items():
        actual_value = manifest.get(field_name)
        if actual_value != expected_value:
            issues.append((field_mismatch_code, f"{field_name}:actual={actual_value!r}:expected={expected_value!r}"))
    return issues


def collect_missing_case_paths(
    root: Path,
    fixture_root: Path,
    cases: list[dict[str, object]],
    field_names: tuple[str, ...],
    code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for case in cases:
        case_name = str(case.get("name", "<unknown>"))
        for field_name in field_names:
            rel_path = case.get(field_name)
            if not isinstance(rel_path, str):
                continue
            if not resolve_path(root, fixture_root / rel_path).exists():
                issues.append((code, f"{case_name}:{field_name}:{rel_path}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    scripts_readme_text = read_text(resolve_path(root, SCRIPTS_README))
    tests_readme_text = read_text(resolve_path(root, TESTS_README))
    review_checklist_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    bridge_checker_text = read_text(resolve_path(root, KCONFIG_BRIDGE_CHECKER))

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    for marker in WORKFLOW_PATH_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_PATH_FILTERS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_PATH_FILTERS", f"{marker}:count={count}"))

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_HOOKS", f"{marker}:count={count}"))

    issues.extend(collect_missing_markers(scripts_readme_text, SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKERS"))
    issues.extend(collect_missing_markers(tests_readme_text, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"))
    issues.extend(collect_missing_markers(review_checklist_text, REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKERS"))

    for marker in BRIDGE_CHECKER_LINE_MARKERS:
        count = count_exact_lines(bridge_checker_text, marker)
        if count == 0:
            issues.append(("MISSING_BRIDGE_CHECKER_MARKERS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_BRIDGE_CHECKER_MARKERS", f"{marker}:count={count}"))

    conf_helper_anchors, confdata_helper_anchors, implicit_omission_modes, explicit_override_modes, bridge_checker_confdata_cases = load_bridge_checker_anchor_packets(bridge_checker_text)

    conf_cases: list[dict[str, object]] = []
    confdata_cases: list[dict[str, object]] = []
    try:
        cases_payload = read_json(resolve_path(root, KCONFIG_BRIDGE_CASES))
    except json.JSONDecodeError as exc:
        issues.append(("INVALID_CASES_JSON", str(exc)))
    else:
        if not isinstance(cases_payload, dict):
            issues.append(("INVALID_CASES_PAYLOAD", type(cases_payload).__name__))
        else:
            raw_conf_cases = cases_payload.get("conf_cases")
            if not isinstance(raw_conf_cases, list):
                issues.append(("INVALID_CONF_CASES_PAYLOAD", type(raw_conf_cases).__name__))
            else:
                conf_cases, conf_case_issues = extract_dict_case_list(raw_conf_cases, entry_code="INVALID_CONF_CASE_ENTRY")
                issues.extend(conf_case_issues)
                silent_case_names = [case.get("name") for case in conf_cases if case.get("silent") is True]
                if silent_case_names != list(EXPECTED_SILENT_CONF_CASE_NAMES):
                    issues.append(("CONF_CASE_SILENT_PACKET_MISMATCH", f"actual={silent_case_names!r}:expected={list(EXPECTED_SILENT_CONF_CASE_NAMES)!r}"))
                mode_arg_case_names = [case.get("name") for case in conf_cases if "mode_arg" in case]
                if mode_arg_case_names != list(EXPECTED_MODE_ARG_CASE_NAMES):
                    issues.append(("CONF_CASE_MODE_ARG_PACKET_MISMATCH", f"actual={mode_arg_case_names!r}:expected={list(EXPECTED_MODE_ARG_CASE_NAMES)!r}"))
                allconfig_override_case_names = [case.get("name") for case in conf_cases if "allconfig" in case]
                if allconfig_override_case_names != list(EXPECTED_ALLCONFIG_OVERRIDE_CASE_NAMES):
                    issues.append(("CONF_CASE_ALLCONFIG_OVERRIDE_PACKET_MISMATCH", f"actual={allconfig_override_case_names!r}:expected={list(EXPECTED_ALLCONFIG_OVERRIDE_CASE_NAMES)!r}"))
                syncconfig_env_case_names = [case.get("name") for case in conf_cases if "nosilentupdate" in case]
                if syncconfig_env_case_names != list(EXPECTED_SYNCCONFIG_ENV_CASE_NAMES):
                    issues.append(("CONF_CASE_SYNCCONFIG_ENV_PACKET_MISMATCH", f"actual={syncconfig_env_case_names!r}:expected={list(EXPECTED_SYNCCONFIG_ENV_CASE_NAMES)!r}"))
                randconfig_env_case_names = [case.get("name") for case in conf_cases if "seed" in case or "probability" in case]
                if randconfig_env_case_names != list(EXPECTED_RANDCONFIG_ENV_CASE_NAMES):
                    issues.append(("CONF_CASE_RANDCONFIG_ENV_PACKET_MISMATCH", f"actual={randconfig_env_case_names!r}:expected={list(EXPECTED_RANDCONFIG_ENV_CASE_NAMES)!r}"))
                issues.extend(collect_missing_case_paths(root, KCONFIG_FIXTURE_ROOT, conf_cases, ("expected",), "MISSING_CONF_CASE_PATHS"))

            raw_confdata_cases = cases_payload.get("confdata_cases")
            if not isinstance(raw_confdata_cases, list):
                issues.append(("INVALID_CONFDATA_CASES_PAYLOAD", type(raw_confdata_cases).__name__))
            else:
                confdata_cases, confdata_case_issues = extract_dict_case_list(raw_confdata_cases, entry_code="INVALID_CONFDATA_CASE_ENTRY")
                issues.extend(confdata_case_issues)
                expected_confdata_case_names = [case.get("name") for case in bridge_checker_confdata_cases]
                confdata_case_names = [case.get("name") for case in confdata_cases]
                if confdata_case_names != expected_confdata_case_names:
                    issues.append(("CONFDATA_CASE_PACKET_MISMATCH", f"actual={confdata_case_names!r}:expected={expected_confdata_case_names!r}"))
                expected_confdata_input_packet = [case.get("input") for case in bridge_checker_confdata_cases]
                confdata_input_packet = [case.get("input") for case in confdata_cases if "input" in case]
                if confdata_input_packet != expected_confdata_input_packet:
                    issues.append(("CONFDATA_INPUT_PACKET_MISMATCH", f"actual={confdata_input_packet!r}:expected={expected_confdata_input_packet!r}"))
                expected_confdata_output_packet = [case.get("expected") for case in bridge_checker_confdata_cases]
                confdata_expected_packet = [case.get("expected") for case in confdata_cases if "expected" in case]
                if confdata_expected_packet != expected_confdata_output_packet:
                    issues.append(("CONFDATA_EXPECTED_PACKET_MISMATCH", f"actual={confdata_expected_packet!r}:expected={expected_confdata_output_packet!r}"))
                issues.extend(collect_missing_case_paths(root, KCONFIG_FIXTURE_ROOT, confdata_cases, ("input", "expected"), "MISSING_CONFDATA_CASE_PATHS"))

    if conf_cases:
        try:
            conf_manifest = read_json(resolve_path(root, CONF_MANIFEST))
        except json.JSONDecodeError as exc:
            issues.append(("INVALID_CONF_MANIFEST_JSON", str(exc)))
        else:
            issues.extend(
                collect_manifest_field_issues(
                    conf_manifest,
                    expected_fields=build_conf_manifest_payload(conf_cases, conf_helper_anchors, implicit_omission_modes, explicit_override_modes),
                    invalid_payload_code="INVALID_CONF_MANIFEST_PAYLOAD",
                    field_mismatch_code="CONF_MANIFEST_FIELD_MISMATCH",
                )
            )

    if confdata_cases:
        try:
            confdata_manifest = read_json(resolve_path(root, CONFDATA_MANIFEST))
        except json.JSONDecodeError as exc:
            issues.append(("INVALID_CONFDATA_MANIFEST_JSON", str(exc)))
        else:
            issues.extend(
                collect_manifest_field_issues(
                    confdata_manifest,
                    expected_fields=build_confdata_manifest_payload(confdata_cases, confdata_helper_anchors),
                    invalid_payload_code="INVALID_CONFDATA_MANIFEST_PAYLOAD",
                    field_mismatch_code="CONFDATA_MANIFEST_FIELD_MISMATCH",
                )
            )

    for bridge_path in KCONFIG_BRIDGE_SURFACE_PATHS:
        if not resolve_path(root, bridge_path).exists():
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


def render_bridge_checker_stub() -> str:
    return f'''REQUIRED_CONF_HELPER_ANCHORS = {list(VALID_CONF_HELPER_ANCHORS)!r}
REQUIRED_CONFDATA_HELPER_ANCHORS = {list(VALID_CONFDATA_HELPER_ANCHORS)!r}
REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES = {list(VALID_CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES)!r}
REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES = {list(VALID_CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES)!r}
SAMPLE_CONFDATA_CASES = {VALID_CASES_PAYLOAD["confdata_cases"]!r}

def validate_case_mapping(raw_cases, *, group_name):
    for case in raw_cases:
        if group_name == "conf_cases" and "silent" in case and not isinstance(case["silent"], bool):
            return False
        if "silent" in case and case["silent"] is not True:
            return False
    return True

def build_conf_command(case):
    cmd = []
    if case.get("silent"):
        cmd.append("silent")
    if "mode_arg" in case:
        cmd.append(str(case["mode_arg"]))
    if "allconfig" in case:
        cmd.append(f"allconfig={{case['allconfig']}}")
    if "seed" in case:
        cmd.append(f"seed={{case['seed']}}")
    if "probability" in case:
        cmd.append(f"probability={{case['probability']}}")
    if "nosilentupdate" in case:
        cmd.append(f"nosilentupdate={{case['nosilentupdate']}}")
    return cmd
'''


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, WORKFLOW), "\n".join(("name: zigux-bootstrap", *WORKFLOW_PATH_LINES, *WORKFLOW_LINES)) + "\n")
    write_text(
        resolve_path(root, MAKEFILE),
        "\n".join(
            (
                "PYTHON ?= python3",
                "ZIG ?= zig",
                "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
                "ZIGUX_ROOT := ..",
                "",
                *MAKEFILE_LINES,
            )
        )
        + "\n",
    )
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(resolve_path(root, KCONFIG_BRIDGE_CHECKER), render_bridge_checker_stub())
    write_text(resolve_path(root, ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"), 'test "placeholder" {}\n')
    write_text(resolve_path(root, ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"), 'test "placeholder" {}\n')
    write_text(resolve_path(root, KCONFIG_BRIDGE_CASES), json.dumps(VALID_CASES_PAYLOAD, indent=2) + "\n")
    write_text(
        resolve_path(root, CONF_MANIFEST),
        json.dumps(
            build_conf_manifest_payload(
                VALID_CASES_PAYLOAD["conf_cases"],
                VALID_CONF_HELPER_ANCHORS,
                VALID_CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES,
                VALID_CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES,
            ),
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve_path(root, CONFDATA_MANIFEST),
        json.dumps(build_confdata_manifest_payload(VALID_CASES_PAYLOAD["confdata_cases"], VALID_CONFDATA_HELPER_ANCHORS), indent=2) + "\n",
    )

    for case in VALID_CASES_PAYLOAD["conf_cases"]:
        write_text(resolve_path(root, KCONFIG_FIXTURE_ROOT / str(case["expected"])), "{}\n")
    for case in VALID_CASES_PAYLOAD["confdata_cases"]:
        write_text(resolve_path(root, KCONFIG_FIXTURE_ROOT / str(case["input"])), "# fixture\n")
        write_text(resolve_path(root, KCONFIG_FIXTURE_ROOT / str(case["expected"])), "{}\n")


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_kconfig_alignment_") as tmp_dir_str:
        root = Path(tmp_dir_str)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        write_text(workflow_path, replace_exact_line(read_text(workflow_path), WORKFLOW_LINES[0], "run: python3 scripts/zigux/other.py"))
        assert ("MISSING_WORKFLOW_HOOKS", WORKFLOW_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        write_text(workflow_path, read_text(workflow_path) + WORKFLOW_LINES[0] + "\n")
        assert ("DUPLICATE_WORKFLOW_HOOKS", f"{WORKFLOW_LINES[0]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        write_text(workflow_path, replace_exact_line(read_text(workflow_path), WORKFLOW_PATH_LINES[0], "- 'scripts/other.c'"))
        assert ("MISSING_WORKFLOW_PATH_FILTERS", WORKFLOW_PATH_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        write_text(workflow_path, read_text(workflow_path) + WORKFLOW_PATH_LINES[0] + "\n")
        assert ("DUPLICATE_WORKFLOW_PATH_FILTERS", f"{WORKFLOW_PATH_LINES[0]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        write_text(makefile_path, replace_exact_line(read_text(makefile_path), MAKEFILE_LINES[0], "# removed"))
        assert ("MISSING_MAKEFILE_HOOKS", MAKEFILE_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        write_text(makefile_path, read_text(makefile_path) + MAKEFILE_LINES[0] + "\n")
        assert ("DUPLICATE_MAKEFILE_HOOKS", f"{MAKEFILE_LINES[0]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        scripts_readme_path = resolve_path(root, SCRIPTS_README)
        write_text(scripts_readme_path, read_text(scripts_readme_path).replace(SCRIPTS_README_MARKERS[0], "scripts/zigux/other.py", 1))
        assert ("MISSING_SCRIPTS_README_MARKERS", SCRIPTS_README_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        tests_readme_path = resolve_path(root, TESTS_README)
        write_text(tests_readme_path, read_text(tests_readme_path).replace(TESTS_README_MARKERS[0], "scripts/zigux/other.py", 1))
        assert ("MISSING_TESTS_README_MARKERS", TESTS_README_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        review_path = resolve_path(root, REVIEW_CHECKLIST)
        write_text(review_path, read_text(review_path).replace(REVIEW_CHECKLIST_MARKERS[0], "scripts/zigux/other.py", 1))
        assert ("MISSING_REVIEW_CHECKLIST_MARKERS", REVIEW_CHECKLIST_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        bridge_checker_path = resolve_path(root, KCONFIG_BRIDGE_CHECKER)
        write_text(bridge_checker_path, read_text(bridge_checker_path).replace(BRIDGE_CHECKER_LINE_MARKERS[-1], 'cmd.append("oops")', 1))
        assert ("MISSING_BRIDGE_CHECKER_MARKERS", BRIDGE_CHECKER_LINE_MARKERS[-1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        cases_path = resolve_path(root, KCONFIG_BRIDGE_CASES)
        write_text(cases_path, "{broken\n")
        assert any(code == "INVALID_CASES_JSON" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        cases_path = resolve_path(root, KCONFIG_BRIDGE_CASES)
        write_text(cases_path, json.dumps([], indent=2) + "\n")
        assert ("INVALID_CASES_PAYLOAD", "list") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        cases_path = resolve_path(root, KCONFIG_BRIDGE_CASES)
        payload = read_json(cases_path)
        assert isinstance(payload, dict)
        payload["conf_cases"][10].pop("silent")
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        assert any(code == "CONF_CASE_SILENT_PACKET_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        cases_path = resolve_path(root, KCONFIG_BRIDGE_CASES)
        payload = read_json(cases_path)
        assert isinstance(payload, dict)
        payload["conf_cases"][8].pop("mode_arg")
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        assert any(code == "CONF_CASE_MODE_ARG_PACKET_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        cases_path = resolve_path(root, KCONFIG_BRIDGE_CASES)
        payload = read_json(cases_path)
        assert isinstance(payload, dict)
        payload["conf_cases"][6].pop("allconfig")
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        assert any(code == "CONF_CASE_ALLCONFIG_OVERRIDE_PACKET_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        cases_path = resolve_path(root, KCONFIG_BRIDGE_CASES)
        payload = read_json(cases_path)
        assert isinstance(payload, dict)
        payload["conf_cases"][1].pop("nosilentupdate")
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        assert any(code == "CONF_CASE_SYNCCONFIG_ENV_PACKET_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        conf_manifest_path = resolve_path(root, CONF_MANIFEST)
        payload = read_json(conf_manifest_path)
        assert isinstance(payload, dict)
        payload["case_count"] = 99
        write_text(conf_manifest_path, json.dumps(payload, indent=2) + "\n")
        assert any(code == "CONF_MANIFEST_FIELD_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        confdata_manifest_path = resolve_path(root, CONFDATA_MANIFEST)
        payload = read_json(confdata_manifest_path)
        assert isinstance(payload, dict)
        payload["expected_packet"] = []
        write_text(confdata_manifest_path, json.dumps(payload, indent=2) + "\n")
        assert any(code == "CONFDATA_MANIFEST_FIELD_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        conf_case_output = resolve_path(root, KCONFIG_FIXTURE_ROOT / "oldaskconfig_expected.json")
        conf_case_output.unlink()
        assert any(code == "MISSING_CONF_CASE_PATHS" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        confdata_case_input = resolve_path(root, KCONFIG_FIXTURE_ROOT / "sample.config")
        confdata_case_input.unlink()
        assert any(code == "MISSING_CONFDATA_CASE_PATHS" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        conf_bridge_path = resolve_path(root, ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig")
        conf_bridge_path.unlink()
        assert ("MISSING_BRIDGE_SURFACE_PATHS", "scripts/zigux/kconfig/conf_bridge.zig") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        conf_manifest_path = resolve_path(root, CONF_MANIFEST)
        write_text(conf_manifest_path, json.dumps([], indent=2) + "\n")
        assert ("INVALID_CONF_MANIFEST_PAYLOAD", "list") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        confdata_manifest_path = resolve_path(root, CONFDATA_MANIFEST)
        write_text(confdata_manifest_path, json.dumps([], indent=2) + "\n")
        assert ("INVALID_CONFDATA_MANIFEST_PAYLOAD", "list") in collect_issues(root)
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
