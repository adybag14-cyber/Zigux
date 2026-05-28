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
    "confdata bridge emits auto.conf symbol export lines",
    "confdata bridge emits autoconf header symbol export lines",
    "confdata bridge keeps explicit n out of autoconf header exports",
    "confdata bridge parses explicit output modes",
    "confdata bridge rejects unknown output modes",
    "confdata bridge emits auto.conf output through the explicit mode surface",
    "confdata bridge emits autoconf header output through the explicit mode surface",
    "confdata bridge file reader accepts config inputs beyond one mebibyte",
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
}
