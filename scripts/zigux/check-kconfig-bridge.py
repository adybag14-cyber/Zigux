#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIFF = ROOT / "scripts" / "zigux" / "artifact_diff.py"
CONF_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"
CONFDATA_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"
FIXTURE_DIR = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge"

REQUIRED_CONF_HELPER_ANCHORS = [
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
]

REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES = [
    "allmodconfig",
    "randconfig",
]

REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES = [
    "allmodconfig",
    "allnoconfig",
    "allyesconfig",
    "alldefconfig",
    "randconfig",
]

REQUIRED_CONFDATA_CASES = [
    "sample",
    "escaped_strings",
    "escaped_control_sequences",
    "trailing_escaped_backslash",
    "sample_crlf",
    "explicit_n_tristate",
    "final_trailing_carriage_return",
    "final_unterminated_unset_comment",
    "uppercase_tristate",
    "non_config_lines",
    "empty_config_symbol_names",
    "malformed_unset_comment_tokens",
    "last_state_transitions",
    "duplicate_assignments",
    "duplicate_malformed_quoted_assignment",
    "explicit_empty_assignments",
]

REQUIRED_CONFDATA_INPUT_PACKET = [
    "sample.config",
    "escaped_strings.config",
    "escaped_control_sequences.config",
    "trailing_escaped_backslash.config",
    "sample_crlf.config",
    "explicit_n_tristate.config",
    "final_trailing_carriage_return.config",
    "final_unterminated_unset_comment.config",
    "uppercase_tristate.config",
    "non_config_lines.config",
    "empty_config_symbol_names.config",
    "malformed_unset_comment_tokens.config",
    "last_state_transitions.config",
    "duplicate_assignments.config",
    "duplicate_malformed_quoted_assignment.config",
    "explicit_empty_assignments.config",
]

REQUIRED_CONFDATA_EXPECTED_PACKET = [
    "sample_expected.json",
    "escaped_strings_expected.json",
    "escaped_control_sequences_expected.json",
    "trailing_escaped_backslash_expected.json",
    "sample_crlf_expected.json",
    "explicit_n_tristate_expected.json",
    "final_trailing_carriage_return_expected.json",
    "final_unterminated_unset_comment_expected.json",
    "uppercase_tristate_expected.json",
    "non_config_lines_expected.json",
    "empty_config_symbol_names_expected.json",
    "malformed_unset_comment_tokens_expected.json",
    "last_state_transitions_expected.json",
    "duplicate_assignments_expected.json",
    "duplicate_malformed_quoted_assignment_expected.json",
    "explicit_empty_assignments_expected.json",
]

REQUIRED_CONFDATA_HELPER_ANCHORS = [
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
    "confdata bridge releases appended entry ownership on index-allocation failure",
    "confdata bridge preserves duplicate unset ownership on allocation failure",
]

REQUIRED_CONF_CASE_MODES = [
    "oldaskconfig",
    "syncconfig",
    "oldconfig",
    "allnoconfig",
    "allyesconfig",
    "allmodconfig",
    "alldefconfig",
    "randconfig",
    "defconfig",
    "savedefconfig",
    "listnewconfig",
    "helpnewconfig",
    "olddefconfig",
    "yes2modconfig",
    "mod2yesconfig",
    "mod2noconfig",
]

ALLCONFIG_OVERRIDE_MODES = {"allnoconfig", "allyesconfig", "allmodconfig", "alldefconfig", "randconfig"}
ALLCONFIG_SENTINEL_MODES = {"allnoconfig", "allyesconfig", "alldefconfig"}

SAMPLE_CONF_CASES = [
    {"name": "oldaskconfig", "mode": "oldaskconfig", "kconfig": "Kconfig", "config": "ask/.config", "arch": "x86_64", "expected": "oldaskconfig_expected.json"},
    {"name": "syncconfig", "mode": "syncconfig", "kconfig": "Kconfig", "config": "out/.config", "arch": "riscv64", "nosilentupdate": "1", "expected": "syncconfig_expected.json"},
    {"name": "oldconfig", "mode": "oldconfig", "kconfig": "Kconfig", "config": "refresh/.config", "arch": "x86", "expected": "oldconfig_expected.json"},
    {"name": "allnoconfig", "mode": "allnoconfig", "kconfig": "Kconfig", "config": "none/.config", "arch": "arm64", "allconfig": "mini-all.config", "expected": "allnoconfig_expected.json"},
    {"name": "allyesconfig", "mode": "allyesconfig", "kconfig": "Kconfig", "config": "yes/.config", "arch": "arm64", "allconfig": "", "expected": "allyesconfig_expected.json"},
    {"name": "allmodconfig", "mode": "allmodconfig", "kconfig": "Kconfig", "config": "mod/.config", "arch": "arm", "allconfig": "", "expected": "allmodconfig_expected.json"},
    {"name": "alldefconfig", "mode": "alldefconfig", "kconfig": "Kconfig", "config": "build/.config", "arch": "arm64", "allconfig": "mini-all.config", "expected": "alldefconfig_expected.json"},
    {"name": "randconfig", "mode": "randconfig", "kconfig": "Kconfig", "config": "rand/.config", "arch": "x86_64", "allconfig": "", "seed": "0xC0FFEE", "probability": "15:25", "expected": "randconfig_expected.json"},
    {"name": "defconfig", "mode": "defconfig", "kconfig": "Kconfig", "config": "out/.config", "arch": "arm64", "mode_arg": "arch/arm64/configs/defconfig", "expected": "defconfig_expected.json"},
    {"name": "savedefconfig", "mode": "savedefconfig", "kconfig": "Kconfig", "config": ".config", "arch": "x86_64", "mode_arg": "silent=debug_defconfig", "expected": "savedefconfig_expected.json"},
    {"name": "listnewconfig", "mode": "listnewconfig", "kconfig": "Kconfig", "config": "out/list.config", "arch": "x86_64", "silent": True, "expected": "listnewconfig_expected.json"},
    {"name": "helpnewconfig", "mode": "helpnewconfig", "kconfig": "Kconfig", "config": "out/help.config", "arch": "riscv64", "silent": True, "expected": "helpnewconfig_expected.json"},
    {"name": "olddefconfig", "mode": "olddefconfig", "kconfig": "Kconfig", "config": ".config", "arch": "x86_64", "expected": "olddefconfig_expected.json"},
    {"name": "yes2modconfig", "mode": "yes2modconfig", "kconfig": "Kconfig", "config": "rewrite/.config", "arch": "x86", "expected": "yes2modconfig_expected.json"},
    {"name": "mod2yesconfig", "mode": "mod2yesconfig", "kconfig": "Kconfig", "config": "promote/.config", "arch": "x86", "expected": "mod2yesconfig_expected.json"},
    {"name": "mod2noconfig", "mode": "mod2noconfig", "kconfig": "Kconfig", "config": "demote/.config", "arch": "x86", "expected": "mod2noconfig_expected.json"},
]

SAMPLE_CONFDATA_CASES = [
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
    {"name": "explicit_empty_assignments", "input": "explicit_empty_assignments.config", "expected": "explicit_empty_assignments_expected.json"},
]

EXPECTED_SELF_TEST_CASE_COUNT = 13

def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)

def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    found = shutil.which("zig")
    if found:
        return found
    fallback = ROOT.parent / "toolchains" / "zig-master" / "current" / "zig.exe"
    if fallback.exists():
        return str(fallback)
    raise SystemExit("zig not found; pass --zig or add zig to PATH")

def compile_tool(zig: str, source: Path, output: Path) -> None:
    run([zig, "build-exe", str(source), "-femit-bin=" + str(output)], cwd=str(ROOT))

def read_json(path: Path, issue_code: str):
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError:
        return None, (issue_code, path.name)

def ordered_test_anchors(path: Path, error: str) -> list[str]:
    anchors = re.findall(r'^test "([^"]+)" \{$', path.read_text(encoding="utf-8"), re.M)
    if not anchors:
        raise SystemExit(error)
    return anchors

def ordered_conf_modes(conf_bridge_path: Path) -> list[str]:
    source = conf_bridge_path.read_text(encoding="utf-8")
    match = re.search(r"pub const Mode = enum \{(.*?)\n\s*pub fn parse", source, re.S)
    if not match:
        raise SystemExit("failed to parse conf bridge Mode enum")
    modes: list[str] = []
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if line.endswith(","):
            candidate = line[:-1].strip()
            if candidate and candidate.isidentifier():
                modes.append(candidate)
    if not modes:
        raise SystemExit("failed to discover conf bridge modes")
    return modes

def expected_conf_case_order(conf_cases: list[dict[str, object]]) -> list[str]:
    present_modes = {str(case["mode"]) for case in conf_cases}
    return [mode for mode in REQUIRED_CONF_CASE_MODES if mode in present_modes]

def build_conf_manifest(conf_cases: list[dict[str, object]]) -> dict[str, object]:
    return {
        "tool": "scripts/zigux/kconfig/conf_bridge.zig",
        "status": "closed",
        "mode": "bounded request-plan bridge",
        "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
        "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
        "case_count": len(conf_cases),
        "cases": [str(case["name"]) for case in conf_cases],
        "stdout_packet": [str(case["expected"]) for case in conf_cases],
        "mode_arg_cases": [str(case["name"]) for case in conf_cases if "mode_arg" in case],
        "silent_request_packet": [str(case["expected"]) for case in conf_cases if case.get("silent")],
        "syncconfig_env_packet": [str(case["expected"]) for case in conf_cases if "nosilentupdate" in case],
        "allconfig_sentinel_packet": [str(case["expected"]) for case in conf_cases if str(case["mode"]) in ALLCONFIG_SENTINEL_MODES and "allconfig" not in case],
        "allconfig_override_packet": [str(case["expected"]) for case in conf_cases if "allconfig" in case],
        "helper_local_allconfig_implicit_omission_modes": ["allmodconfig", "randconfig"],
        "helper_local_allconfig_explicit_override_modes": ["allmodconfig", "allnoconfig", "allyesconfig", "alldefconfig", "randconfig"],
        "randconfig_env_packet": [str(case["expected"]) for case in conf_cases if "seed" in case or "probability" in case],
        "helper_local_anchors": REQUIRED_CONF_HELPER_ANCHORS,
    }

def build_confdata_manifest(confdata_cases: list[dict[str, object]]) -> dict[str, object]:
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
        "helper_local_anchors": REQUIRED_CONFDATA_HELPER_ANCHORS,
    }

def load_case_groups(fixture_dir: Path) -> tuple[list[dict[str, object]] | None, list[dict[str, object]] | None, list[tuple[str, str]]]:
    cases_payload, read_issue = read_json(fixture_dir / "cases.json", "INVALID_CASES_JSON")
    if read_issue is not None:
        return None, None, [read_issue]
    if not isinstance(cases_payload, dict):
        return None, None, [("INVALID_CASES_PAYLOAD", type(cases_payload).__name__)]
    conf_cases = cases_payload.get("conf_cases")
    confdata_cases = cases_payload.get("confdata_cases")
    if not isinstance(conf_cases, list) or not isinstance(confdata_cases, list):
        return None, None, [("INVALID_CASES_FIELDS", "conf_cases/confdata_cases")]
    return conf_cases, confdata_cases, []

def collect_duplicate_values(issue_code: str, values: list[str]) -> list[tuple[str, str]]:
    duplicates: list[tuple[str, str]] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.append((issue_code, value))
            continue
        seen.add(value)
    return duplicates

def expected_conf_expected_path(case_name: str) -> str:
    return f"{case_name}_expected.json"

def expected_confdata_input_path(case_name: str) -> str:
    return f"{case_name}.config"

def expected_confdata_expected_path(case_name: str) -> str:
    return f"{case_name}_expected.json"

def collect_conf_manifest_issues(fixture_dir: Path, conf_bridge_path: Path, conf_cases: list[dict[str, object]]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    actual_anchors = ordered_test_anchors(conf_bridge_path, "failed to discover conf bridge test anchors")
    if actual_anchors != REQUIRED_CONF_HELPER_ANCHORS:
        issues.append(("CONF_SOURCE_HELPER_LOCAL_ANCHORS_ACTUAL", ",".join(actual_anchors)))
        issues.append(("CONF_SOURCE_HELPER_LOCAL_ANCHORS_EXPECTED", ",".join(REQUIRED_CONF_HELPER_ANCHORS)))
    manifest, read_issue = read_json(fixture_dir / "conf_manifest.json", "INVALID_CONF_MANIFEST_JSON")
    if read_issue is not None:
        return issues + [read_issue]
    if not isinstance(manifest, dict):
        return issues + [("INVALID_CONF_MANIFEST_PAYLOAD", type(manifest).__name__)]
    expected = build_conf_manifest(conf_cases)
    for field_name, expected_value in expected.items():
        actual_value = manifest.get(field_name)
        if actual_value != expected_value:
            issues.append((f"CONF_MANIFEST_{field_name.upper()}_MISMATCH", f"actual={actual_value!r}:expected={expected_value!r}"))
    for rel_path in expected["stdout_packet"]:
        if not (fixture_dir / rel_path).exists():
            issues.append(("CONF_MANIFEST_REFERENCES_MISSING_FIXTURE", str(rel_path)))
    return issues

def collect_confdata_manifest_issues(fixture_dir: Path, confdata_bridge_path: Path, confdata_cases: list[dict[str, object]]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    actual_anchors = ordered_test_anchors(confdata_bridge_path, "failed to discover confdata bridge test anchors")
    if actual_anchors != REQUIRED_CONFDATA_HELPER_ANCHORS:
        issues.append(("CONFDATA_SOURCE_HELPER_LOCAL_ANCHORS_ACTUAL", ",".join(actual_anchors)))
        issues.append(("CONFDATA_SOURCE_HELPER_LOCAL_ANCHORS_EXPECTED", ",".join(REQUIRED_CONFDATA_HELPER_ANCHORS)))
    manifest, read_issue = read_json(fixture_dir / "confdata_manifest.json", "INVALID_CONFDATA_MANIFEST_JSON")
    if read_issue is not None:
        return issues + [read_issue]
    if not isinstance(manifest, dict):
        return issues + [("INVALID_CONFDATA_MANIFEST_PAYLOAD", type(manifest).__name__)]
    expected = build_confdata_manifest(confdata_cases)
    for field_name, expected_value in expected.items():
        actual_value = manifest.get(field_name)
        if actual_value != expected_value:
            issues.append((f"CONFDATA_MANIFEST_{field_name.upper()}_MISMATCH", f"actual={actual_value!r}:expected={expected_value!r}"))
    for rel_path in [*expected["input_packet"], *expected["expected_packet"]]:
        if not (fixture_dir / rel_path).exists():
            issues.append(("MISSING_CONFDATA_CASE_PATHS", str(rel_path)))
    return issues

def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    fixture_dir = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge"
    conf_bridge = root / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"
    confdata_bridge = root / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"
    conf_cases, confdata_cases, load_issues = load_case_groups(fixture_dir)
    if load_issues:
        return load_issues
    issues: list[tuple[str, str]] = []
    bridge_modes = set(ordered_conf_modes(conf_bridge))
    manifest_modes = [str(case["mode"]) for case in conf_cases]
    for mode in REQUIRED_CONF_CASE_MODES:
        if mode not in manifest_modes:
            issues.append(("MISSING_REQUIRED_CONF_CASE_MODES", mode))
    for mode in manifest_modes:
        if mode not in bridge_modes:
            issues.append(("UNSUPPORTED_CONF_CASE_MODES", mode))
    expected_mode_order = expected_conf_case_order(conf_cases)
    if manifest_modes != expected_mode_order:
        issues.append(("CONF_CASE_MODE_ORDER_ACTUAL", ",".join(manifest_modes)))
        issues.append(("CONF_CASE_MODE_ORDER_EXPECTED", ",".join(expected_mode_order)))
    confdata_case_names = [str(case["name"]) for case in confdata_cases]
    if confdata_case_names != REQUIRED_CONFDATA_CASES:
        issues.append(("CONFDATA_CASE_ORDER_ACTUAL", ",".join(confdata_case_names)))
        issues.append(("CONFDATA_CASE_ORDER_EXPECTED", ",".join(REQUIRED_CONFDATA_CASES)))
    confdata_input_packet = [str(case["input"]) for case in confdata_cases]
    if confdata_input_packet != REQUIRED_CONFDATA_INPUT_PACKET:
        issues.append(("CONFDATA_INPUT_PACKET_ACTUAL", ",".join(confdata_input_packet)))
        issues.append(("CONFDATA_INPUT_PACKET_EXPECTED", ",".join(REQUIRED_CONFDATA_INPUT_PACKET)))
    confdata_expected_packet = [str(case["expected"]) for case in confdata_cases]
    if confdata_expected_packet != REQUIRED_CONFDATA_EXPECTED_PACKET:
        issues.append(("CONFDATA_EXPECTED_PACKET_ACTUAL", ",".join(confdata_expected_packet)))
        issues.append(("CONFDATA_EXPECTED_PACKET_EXPECTED", ",".join(REQUIRED_CONFDATA_EXPECTED_PACKET)))
    seen_names: set[str] = set()
    for case in [*conf_cases, *confdata_cases]:
        name = str(case["name"])
        if name in seen_names:
            issues.append(("DUPLICATE_KCONFIG_CASE_NAMES", name))
        seen_names.add(name)
    for case in conf_cases:
        mode = str(case["mode"])
        name = str(case["name"])
        expected_path = str(case["expected"])
        if expected_path != expected_conf_expected_path(name):
            issues.append(("CONF_EXPECTED_PATH_NAME_MISMATCH", f"{name}:{expected_path}"))
        if mode in ("defconfig", "savedefconfig") and not case.get("mode_arg"):
            issues.append(("MISSING_CONF_MODE_ARG_FIELDS", f"{name}:{mode}"))
        elif mode not in ("defconfig", "savedefconfig") and "mode_arg" in case:
            issues.append(("UNEXPECTED_CONF_MODE_ARG_FIELDS", f"{name}:{mode}"))
        if mode != "randconfig":
            for field_name in ("seed", "probability"):
                if field_name in case:
                    issues.append(("INVALID_CONF_CASE_RANDCONFIG_FIELDS", f"{name}:{field_name}"))
        if mode != "syncconfig" and "nosilentupdate" in case:
            issues.append(("INVALID_CONF_CASE_SYNCCONFIG_FIELDS", f"{name}:nosilentupdate"))
        if mode not in ALLCONFIG_OVERRIDE_MODES and "allconfig" in case:
            issues.append(("INVALID_CONF_CASE_ALLCONFIG_FIELDS", f"{name}:allconfig"))
        if "silent" in case and case["silent"] is not True:
            issues.append(("INVALID_CONF_CASE_SILENT_FIELDS", f"{name}:silent"))
        if not (fixture_dir / expected_path).exists():
            issues.append(("MISSING_CONF_CASE_EXPECTED_PATHS", f"{name}:expected:{expected_path}"))
    issues.extend(collect_duplicate_values("DUPLICATE_CONF_CASE_EXPECTED_PATHS", [str(case["expected"]) for case in conf_cases]))
    for case in confdata_cases:
        name = str(case["name"])
        input_path = str(case["input"])
        expected_path = str(case["expected"])
        if input_path != expected_confdata_input_path(name):
            issues.append(("CONFDATA_INPUT_PATH_NAME_MISMATCH", f"{name}:{input_path}"))
        if expected_path != expected_confdata_expected_path(name):
            issues.append(("CONFDATA_EXPECTED_PATH_NAME_MISMATCH", f"{name}:{expected_path}"))
    issues.extend(collect_duplicate_values("DUPLICATE_CONFDATA_INPUT_PATHS", [str(case["input"]) for case in confdata_cases]))
    issues.extend(collect_duplicate_values("DUPLICATE_CONFDATA_EXPECTED_PATHS", [str(case["expected"]) for case in confdata_cases]))
    issues.extend(collect_conf_manifest_issues(fixture_dir, conf_bridge, conf_cases))
    issues.extend(collect_confdata_manifest_issues(fixture_dir, confdata_bridge, confdata_cases))
    return issues

def emit_manifest_issues(issues: list[tuple[str, str]]) -> None:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("KCONFIG_BRIDGE_DIFF=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    raise SystemExit(1)

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def build_conf_command(conf_exe: Path, case: dict[str, object]) -> list[str]:
    cmd = [str(conf_exe), str(case["mode"]), str(case["kconfig"]), str(case["config"]), str(case["arch"])]
    if "mode_arg" in case:
        cmd.append(str(case["mode_arg"]))
    if case.get("silent"):
        cmd.append("silent")
    if "allconfig" in case:
        cmd.append(f"allconfig={case['allconfig']}")
    if "seed" in case:
        cmd.append(f"seed={case['seed']}")
    if "probability" in case:
        cmd.append(f"probability={case['probability']}")
    if "nosilentupdate" in case:
        cmd.append(f"nosilentupdate={case['nosilentupdate']}")
    return cmd

def check_repeatable_json_output(expected: Path, actual: Path, repeat: Path) -> None:
    run([sys.executable, str(ARTIFACT_DIFF), "--mode", "json", str(expected), str(actual)], cwd=str(ROOT))
    run([sys.executable, str(ARTIFACT_DIFF), "--mode", "json", str(actual), str(repeat)], cwd=str(ROOT))

def render_conf_bridge_self_test_source() -> str:
    blocks = [f'test "{anchor}" {{\n    try std.testing.expect(true);\n}}\n' for anchor in REQUIRED_CONF_HELPER_ANCHORS]
    return (
        'const std = @import("std");\n\n'
        "pub const Mode = enum {\n"
        "    oldaskconfig,\n    syncconfig,\n    oldconfig,\n    allnoconfig,\n    allyesconfig,\n    allmodconfig,\n    alldefconfig,\n    randconfig,\n    defconfig,\n    savedefconfig,\n    listnewconfig,\n    helpnewconfig,\n    olddefconfig,\n    yes2modconfig,\n    mod2yesconfig,\n    mod2noconfig,\n\n"
        "    pub fn parse(input_text: []const u8) ?Mode {\n        _ = input_text;\n        return null;\n    }\n};\n\n"
        + "\n".join(blocks)
    )

def render_confdata_bridge_self_test_source() -> str:
    blocks = [f'test "{anchor}" {{\n    try std.testing.expect(true);\n}}\n' for anchor in REQUIRED_CONFDATA_HELPER_ANCHORS]
    return 'const std = @import("std");\n\n' + "\n".join(blocks)

def build_self_test_root(root: Path) -> None:
    fixture_root = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge"
    write_text(root / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig", render_conf_bridge_self_test_source())
    write_text(root / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig", render_confdata_bridge_self_test_source())
    write_text(fixture_root / "cases.json", json.dumps({"conf_cases": SAMPLE_CONF_CASES, "confdata_cases": SAMPLE_CONFDATA_CASES}, indent=2) + "\n")
    write_text(fixture_root / "conf_manifest.json", json.dumps(build_conf_manifest(SAMPLE_CONF_CASES), indent=2) + "\n")
    write_text(fixture_root / "confdata_manifest.json", json.dumps(build_confdata_manifest(SAMPLE_CONFDATA_CASES), indent=2) + "\n")
    for rel_path in {*(str(case["expected"]) for case in SAMPLE_CONF_CASES), *(str(case["input"]) for case in SAMPLE_CONFDATA_CASES), *(str(case["expected"]) for case in SAMPLE_CONFDATA_CASES)}:
        write_text(fixture_root / rel_path, "{}\n")

def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_kconfig_bridge_selftest_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        fixture_root = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge"
        cases_path = fixture_root / "cases.json"
        conf_manifest_path = fixture_root / "conf_manifest.json"
        confdata_manifest_path = fixture_root / "confdata_manifest.json"
        conf_bridge_path = root / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"
        confdata_bridge_path = root / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"

        build_self_test_root(root)
        assert collect_manifest_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        write_text(cases_path, "{broken\n")
        assert ("INVALID_CASES_JSON", "cases.json") in collect_manifest_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = json.loads(conf_manifest_path.read_text(encoding="utf-8"))
        manifest["allconfig_sentinel_packet"].append("alldefconfig_expected.json")
        write_text(conf_manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert any(code == "CONF_MANIFEST_ALLCONFIG_SENTINEL_PACKET_MISMATCH" for code, _ in collect_manifest_issues(root))
        checks_run += 1

        build_self_test_root(root)
        manifest = json.loads(conf_manifest_path.read_text(encoding="utf-8"))
        manifest["helper_local_allconfig_implicit_omission_modes"] = ["allmodconfig"]
        write_text(conf_manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert any(code == "CONF_MANIFEST_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES_MISMATCH" for code, _ in collect_manifest_issues(root))
        checks_run += 1

        build_self_test_root(root)
        manifest = json.loads(conf_manifest_path.read_text(encoding="utf-8"))
        manifest["helper_local_allconfig_explicit_override_modes"] = ["allmodconfig", "allnoconfig"]
        write_text(conf_manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert any(code == "CONF_MANIFEST_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES_MISMATCH" for code, _ in collect_manifest_issues(root))
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["conf_cases"][0]["mode"] = "unsupported_mode"
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        assert ("UNSUPPORTED_CONF_CASE_MODES", "unsupported_mode") in collect_manifest_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["confdata_cases"][0]["name"] = "drifted"
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        assert any(code == "CONFDATA_CASE_ORDER_ACTUAL" for code, _ in collect_manifest_issues(root))
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["conf_cases"][10].pop("silent")
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        assert any(code == "CONF_MANIFEST_SILENT_REQUEST_PACKET_MISMATCH" for code, _ in collect_manifest_issues(root))
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["conf_cases"][8].pop("mode_arg")
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        assert any(code == "CONF_MANIFEST_MODE_ARG_CASES_MISMATCH" for code, _ in collect_manifest_issues(root))
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["conf_cases"][7].pop("seed")
        payload["conf_cases"][7].pop("probability")
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        assert any(code == "CONF_MANIFEST_RANDCONFIG_ENV_PACKET_MISMATCH" for code, _ in collect_manifest_issues(root))
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["conf_cases"][1]["expected"] = payload["conf_cases"][0]["expected"]
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("DUPLICATE_CONF_CASE_EXPECTED_PATHS", "oldaskconfig_expected.json") in issues
        assert ("CONF_EXPECTED_PATH_NAME_MISMATCH", "syncconfig:oldaskconfig_expected.json") in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["confdata_cases"][0]["input"] = "wrong-name.config"
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        assert ("CONFDATA_INPUT_PATH_NAME_MISMATCH", "sample:wrong-name.config") in collect_manifest_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["confdata_cases"][1]["expected"] = payload["confdata_cases"][0]["expected"]
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("DUPLICATE_CONFDATA_EXPECTED_PATHS", "sample_expected.json") in issues
        assert ("CONFDATA_EXPECTED_PATH_NAME_MISMATCH", "escaped_strings:sample_expected.json") in issues
        checks_run += 1

    if checks_run != EXPECTED_SELF_TEST_CASE_COUNT:
        print("KCONFIG_BRIDGE_SELF_TEST=fail")
        print(f"KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT_ACTUAL={checks_run}")
        print(f"KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT_EXPECTED={EXPECTED_SELF_TEST_CASE_COUNT}")
        return 1
    print("KCONFIG_BRIDGE_SELF_TEST=pass")
    print(f"KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description="Check bounded kconfig bridge fixture parity.")
    parser.add_argument("--zig", help="Explicit zig executable path")
    parser.add_argument("--self-test", action="store_true", help="Run built-in manifest coverage without compiling the bridge tools.")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()

    issues = collect_manifest_issues(ROOT)
    if issues:
        emit_manifest_issues(issues)

    zig = find_zig(args.zig)
    conf_cases, confdata_cases, load_issues = load_case_groups(FIXTURE_DIR)
    if load_issues:
        emit_manifest_issues(load_issues)
    with tempfile.TemporaryDirectory(prefix="zigux_kconfig_bridge_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        conf_exe = tmp_dir / ("conf-bridge.exe" if sys.platform == "win32" else "conf-bridge")
        confdata_exe = tmp_dir / ("confdata-bridge.exe" if sys.platform == "win32" else "confdata-bridge")
        compile_tool(zig, CONF_BRIDGE, conf_exe)
        compile_tool(zig, CONFDATA_BRIDGE, confdata_exe)
        for case in conf_cases:
            actual = tmp_dir / f"{case['name']}.actual.json"
            repeat = tmp_dir / f"{case['name']}.repeat.json"
            cmd = build_conf_command(conf_exe, case)
            actual.write_text(run(cmd, cwd=str(ROOT), capture_output=True).stdout, encoding="utf-8", newline="\n")
            repeat.write_text(run(cmd, cwd=str(ROOT), capture_output=True).stdout, encoding="utf-8", newline="\n")
            check_repeatable_json_output(FIXTURE_DIR / str(case["expected"]), actual, repeat)
        for case in confdata_cases:
            actual = tmp_dir / f"{case['name']}.actual.json"
            repeat = tmp_dir / f"{case['name']}.repeat.json"
            cmd = [str(confdata_exe), str(FIXTURE_DIR / str(case["input"]))]
            actual.write_text(run(cmd, cwd=str(ROOT), capture_output=True).stdout, encoding="utf-8", newline="\n")
            repeat.write_text(run(cmd, cwd=str(ROOT), capture_output=True).stdout, encoding="utf-8", newline="\n")
            check_repeatable_json_output(FIXTURE_DIR / str(case["expected"]), actual, repeat)

    print("KCONFIG_BRIDGE_DETERMINISM=pass")
    print("KCONFIG_BRIDGE_DIFF=pass")
    print(f"FIXTURE_DIR={FIXTURE_DIR}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
