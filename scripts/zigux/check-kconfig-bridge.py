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
    "conf bridge parses silentoldconfig alias as syncconfig",
    "conf bridge emits olddefconfig argv and env",
    "conf bridge emits syncconfig auto files",
    "conf bridge emits syncconfig nosilentupdate when present",
    "conf bridge omits empty syncconfig nosilentupdate",
    "conf bridge emits silent flag before mode flag",
    "conf bridge emits alldefconfig argv and env",
    "conf bridge emits explicit empty allconfig override for allmodconfig",
    "conf bridge emits allnoconfig sentinel env",
    "conf bridge emits allyesconfig sentinel env",
    "conf bridge emits randconfig tunables when present",
    "conf bridge emits explicit randconfig allconfig override when present",
    "conf bridge emits randconfig allconfig sentinel without explicit override",
    "conf bridge emits yes2modconfig argv and env",
    "conf bridge emits defconfig mode argument before kconfig",
    "conf bridge emits savedefconfig mode argument before kconfig",
    "conf bridge escapes low control bytes in JSON strings",
    "mode argument validation rejects bridge option shaped defconfig payload",
    "mode argument validation still accepts ordinary path text with equals",
    "mode argument validation accepts path text that only starts with silent",
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
    "last_state_transitions",
    "duplicate_malformed_quoted_assignment",
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
    "confdata bridge keeps explicit n assignments as tristate values",
    "confdata bridge recognizes uppercase tristate assignments",
    "confdata bridge ignores non-CONFIG lines like upstream confdata",
    "confdata bridge ignores empty CONFIG symbol names",
    "confdata bridge ignores malformed unset comments with extra tokens",
    "confdata bridge keeps trailing escaped backslashes in quoted strings",
    "confdata bridge emits escaped quoted payloads before trailing suffix bytes",
    "confdata bridge leaves malformed quoted values as raw scalar values",
    "confdata bridge emits no entries for empty CONFIG symbol names",
    "confdata bridge keeps only the last assignment for duplicate symbols",
    "confdata bridge keeps the prior duplicate value when a later quoted assignment is malformed",
    "confdata bridge keeps only the last state across unset and set transitions",
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

ALLCONFIG_OVERRIDE_MODES = {
    "allnoconfig",
    "allyesconfig",
    "allmodconfig",
    "alldefconfig",
    "randconfig",
}

ALLCONFIG_SENTINEL_MODES = {
    "allnoconfig",
    "allyesconfig",
    "alldefconfig",
}

EXPECTED_SELF_TEST_CASE_COUNT = 22


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


def load_cases(fixture_dir: Path) -> dict[str, object]:
    return json.loads((fixture_dir / "cases.json").read_text(encoding="utf-8"))


def ordered_conf_modes(conf_bridge_path: Path) -> list[str]:
    source = conf_bridge_path.read_text(encoding="utf-8")
    match = re.search(r"pub const Mode = enum \{(.*?)\n\s*pub fn parse", source, re.S)
    if not match:
        raise SystemExit("failed to parse conf bridge Mode enum")

    modes: list[str] = []
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("pub ") or line.startswith("//"):
            continue
        if line.endswith(","):
            candidate = line[:-1].strip()
            if candidate and candidate.isidentifier():
                modes.append(candidate)
    if not modes:
        raise SystemExit("failed to discover conf bridge modes")
    return modes


def ordered_conf_helper_anchors(conf_bridge_path: Path) -> list[str]:
    source = conf_bridge_path.read_text(encoding="utf-8")
    anchors = re.findall(r'^test "([^"]+)" \{$', source, re.M)
    if not anchors:
        raise SystemExit("failed to discover conf bridge test anchors")
    return anchors


def ordered_confdata_helper_anchors(confdata_bridge_path: Path) -> list[str]:
    source = confdata_bridge_path.read_text(encoding="utf-8")
    anchors = re.findall(r'^test "([^"]+)" \{$', source, re.M)
    if not anchors:
        raise SystemExit("failed to discover confdata bridge test anchors")
    return anchors


def expected_conf_case_order(conf_cases: list[dict[str, object]]) -> list[str]:
    manifest_mode_set = {str(case["mode"]) for case in conf_cases}
    return [mode for mode in REQUIRED_CONF_CASE_MODES if mode in manifest_mode_set]


def collect_conf_manifest_issues(
    fixture_dir: Path,
    conf_bridge_path: Path,
    conf_cases: list[dict[str, object]],
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    conf_manifest = fixture_dir / "conf_manifest.json"
    if not conf_manifest.exists():
        return [("MISSING_CONF_MANIFEST", conf_manifest.name)]

    source_helper_anchors = ordered_conf_helper_anchors(conf_bridge_path)
    if source_helper_anchors != REQUIRED_CONF_HELPER_ANCHORS:
        issues.append(("CONF_SOURCE_HELPER_LOCAL_ANCHORS_ACTUAL", ",".join(source_helper_anchors)))
        issues.append(("CONF_SOURCE_HELPER_LOCAL_ANCHORS_EXPECTED", ",".join(REQUIRED_CONF_HELPER_ANCHORS)))

    manifest = json.loads(conf_manifest.read_text(encoding="utf-8"))
    expected_case_names = [str(case["name"]) for case in conf_cases]
    expected_stdout_packet = [str(case["expected"]) for case in conf_cases]
    expected_mode_arg_cases = [str(case["name"]) for case in conf_cases if "mode_arg" in case]
    expected_silent_request_packet = [str(case["expected"]) for case in conf_cases if case.get("silent")]
    expected_syncconfig_env_packet = [str(case["expected"]) for case in conf_cases if "nosilentupdate" in case]
    expected_allconfig_sentinel_packet = [
        str(case["expected"]) for case in conf_cases if str(case["mode"]) in ALLCONFIG_SENTINEL_MODES
    ]
    expected_allconfig_override_packet = [str(case["expected"]) for case in conf_cases if "allconfig" in case]

    exact_fields = {
        "tool": "scripts/zigux/kconfig/conf_bridge.zig",
        "status": "closed",
        "mode": "bounded request-plan bridge",
        "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
        "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
    }
    for field_name, expected_value in exact_fields.items():
        actual_value = manifest.get(field_name)
        if actual_value != expected_value:
            issues.append(("CONF_MANIFEST_FIELD_MISMATCH", f"{field_name}:actual={actual_value!r}:expected={expected_value!r}"))

    if manifest.get("case_count") != len(conf_cases):
        issues.append(("CONF_MANIFEST_CASE_COUNT_MISMATCH", f"actual={manifest.get('case_count')!r}:expected={len(conf_cases)}"))

    sequence_fields = {
        "cases": expected_case_names,
        "stdout_packet": expected_stdout_packet,
        "mode_arg_cases": expected_mode_arg_cases,
        "silent_request_packet": expected_silent_request_packet,
        "syncconfig_env_packet": expected_syncconfig_env_packet,
        "allconfig_sentinel_packet": expected_allconfig_sentinel_packet,
        "allconfig_override_packet": expected_allconfig_override_packet,
        "helper_local_anchors": REQUIRED_CONF_HELPER_ANCHORS,
    }
    for field_name, expected_values in sequence_fields.items():
        actual_values = manifest.get(field_name)
        if actual_values != expected_values:
            issues.append((f"CONF_MANIFEST_{field_name.upper()}_MISMATCH", f"actual={actual_values!r}:expected={expected_values!r}"))

    for rel_path in expected_stdout_packet:
        if not (fixture_dir / rel_path).exists():
            issues.append(("CONF_MANIFEST_REFERENCES_MISSING_FIXTURE", rel_path))

    return issues


def collect_confdata_manifest_issues(
    fixture_dir: Path,
    confdata_bridge_path: Path,
    confdata_cases: list[dict[str, object]],
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    confdata_manifest = fixture_dir / "confdata_manifest.json"
    if not confdata_manifest.exists():
        return [("MISSING_CONFDATA_MANIFEST", confdata_manifest.name)]

    source_helper_anchors = ordered_confdata_helper_anchors(confdata_bridge_path)
    if source_helper_anchors != REQUIRED_CONFDATA_HELPER_ANCHORS:
        issues.append(("CONFDATA_SOURCE_HELPER_LOCAL_ANCHORS_ACTUAL", ",".join(source_helper_anchors)))
        issues.append(("CONFDATA_SOURCE_HELPER_LOCAL_ANCHORS_EXPECTED", ",".join(REQUIRED_CONFDATA_HELPER_ANCHORS)))

    manifest = json.loads(confdata_manifest.read_text(encoding="utf-8"))
    expected_case_names = [str(case["name"]) for case in confdata_cases]
    expected_input_packet = [str(case["input"]) for case in confdata_cases]
    expected_output_packet = [str(case["expected"]) for case in confdata_cases]

    exact_fields = {
        "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
        "status": "closed",
        "mode": "bounded config bridge",
        "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
        "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
    }
    for field_name, expected_value in exact_fields.items():
        actual_value = manifest.get(field_name)
        if actual_value != expected_value:
            issues.append(("CONFDATA_MANIFEST_FIELD_MISMATCH", f"{field_name}:actual={actual_value!r}:expected={expected_value!r}"))

    if manifest.get("case_count") != len(confdata_cases):
        issues.append(("CONFDATA_MANIFEST_CASE_COUNT_MISMATCH", f"actual={manifest.get('case_count')!r}:expected={len(confdata_cases)}"))

    sequence_fields = {
        "cases": expected_case_names,
        "input_packet": expected_input_packet,
        "expected_packet": expected_output_packet,
        "helper_local_anchors": REQUIRED_CONFDATA_HELPER_ANCHORS,
    }
    for field_name, expected_values in sequence_fields.items():
        actual_values = manifest.get(field_name)
        if actual_values != expected_values:
            issues.append((f"CONFDATA_MANIFEST_{field_name.upper()}_MISMATCH", f"actual={actual_values!r}:expected={expected_values!r}"))

    for rel_path in expected_input_packet + expected_output_packet:
        if not (fixture_dir / rel_path).exists():
            issues.append(("CONFDATA_MANIFEST_REFERENCES_MISSING_FIXTURE", rel_path))

    return issues


def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    fixture_dir = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge"
    conf_bridge = root / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"
    confdata_bridge = root / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"
    cases = load_cases(fixture_dir)
    issues: list[tuple[str, str]] = []

    conf_cases = cases["conf_cases"]
    bridge_modes = ordered_conf_modes(conf_bridge)
    bridge_mode_set = set(bridge_modes)
    manifest_modes = {str(case["mode"]) for case in conf_cases}

    for mode in REQUIRED_CONF_CASE_MODES:
        if mode not in manifest_modes:
            issues.append(("MISSING_REQUIRED_CONF_CASE_MODES", mode))
    for mode in sorted(manifest_modes - bridge_mode_set):
        issues.append(("UNSUPPORTED_CONF_CASE_MODES", mode))

    manifest_mode_order = [str(case["mode"]) for case in conf_cases]
    expected_mode_order = expected_conf_case_order(conf_cases)
    if manifest_mode_order != expected_mode_order:
        issues.append(("CONF_CASE_MODE_ORDER_ACTUAL", ",".join(manifest_mode_order)))
        issues.append(("CONF_CASE_MODE_ORDER_EXPECTED", ",".join(expected_mode_order)))

    confdata_cases = cases["confdata_cases"]
    manifest_confdata_case_order = [str(case["name"]) for case in confdata_cases]
    if manifest_confdata_case_order != REQUIRED_CONFDATA_CASES:
        issues.append(("CONFDATA_CASE_ORDER_ACTUAL", ",".join(manifest_confdata_case_order)))
        issues.append(("CONFDATA_CASE_ORDER_EXPECTED", ",".join(REQUIRED_CONFDATA_CASES)))

    seen_names: dict[str, str] = {}
    for group_name in ("conf_cases", "confdata_cases"):
        for case in cases[group_name]:
            name = str(case["name"])
            previous_group = seen_names.get(name)
            if previous_group is not None:
                issues.append(("DUPLICATE_KCONFIG_CASE_NAMES", f"{name}:{previous_group},{group_name}"))
                continue
            seen_names[name] = group_name

    for case in conf_cases:
        mode = str(case["mode"])
        name = str(case["name"])
        mode_arg = case.get("mode_arg")
        if mode in ("defconfig", "savedefconfig"):
            if not isinstance(mode_arg, str) or not mode_arg:
                issues.append(("MISSING_CONF_MODE_ARG_FIELDS", f"{name}:{mode}"))
        elif "mode_arg" in case:
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

        rel_path = case["expected"]
        if not (fixture_dir / rel_path).exists():
            issues.append(("MISSING_CONF_CASE_EXPECTED_PATHS", f"{name}:expected:{rel_path}"))

    for case in confdata_cases:
        for field_name in ("input", "expected"):
            rel_path = case[field_name]
            if not (fixture_dir / rel_path).exists():
                issues.append(("MISSING_CONFDATA_CASE_PATHS", f"{case['name']}:{field_name}:{rel_path}"))

    issues.extend(collect_conf_manifest_issues(fixture_dir, conf_bridge, conf_cases))
    issues.extend(collect_confdata_manifest_issues(fixture_dir, confdata_bridge, confdata_cases))
    return issues


def emit_manifest_issues(issues: list[tuple[str, str]]) -> None:
    grouped: dict[str, list[str]] = {}
    for block, value in issues:
        grouped.setdefault(block, []).append(value)

    print("KCONFIG_BRIDGE_DIFF=fail")
    for block, values in grouped.items():
        print(f"{block}_START")
        for value in values:
            print(value)
        print(f"{block}_END")
    raise SystemExit(1)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_conf_bridge_self_test_source() -> str:
    blocks = []
    for anchor in REQUIRED_CONF_HELPER_ANCHORS:
        blocks.append(
            f'test "{anchor}" {{\n'
            "    try std.testing.expect(true);\n"
            "}\n"
        )
    return (
        'const std = @import("std");\n\n'
        "pub const Mode = enum {\n"
        "    oldaskconfig,\n"
        "    syncconfig,\n"
        "    oldconfig,\n"
        "    allnoconfig,\n"
        "    allyesconfig,\n"
        "    allmodconfig,\n"
        "    alldefconfig,\n"
        "    randconfig,\n"
        "    defconfig,\n"
        "    savedefconfig,\n"
        "    listnewconfig,\n"
        "    helpnewconfig,\n"
        "    olddefconfig,\n"
        "    yes2modconfig,\n"
        "    mod2yesconfig,\n"
        "    mod2noconfig,\n\n"
        "    pub fn parse(input_text: []const u8) ?Mode {\n"
        "        _ = input_text;\n"
        "        return null;\n"
        "    }\n"
        "};\n\n"
        + "\n".join(blocks)
    )


def render_confdata_bridge_self_test_source() -> str:
    blocks = []
    for anchor in REQUIRED_CONFDATA_HELPER_ANCHORS:
        blocks.append(
            f'test "{anchor}" {{\n'
            "    try std.testing.expect(true);\n"
            "}\n"
        )
    return 'const std = @import("std");\n\n' + "\n".join(blocks)


def build_self_test_root(root: Path) -> None:
    write_text(root / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig", render_conf_bridge_self_test_source())
    write_text(
        root / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig",
        render_confdata_bridge_self_test_source(),
    )
    write_text(
        root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json",
        json.dumps(
            {
                "conf_cases": [
                    {"name": "oldaskconfig", "mode": "oldaskconfig", "kconfig": "Kconfig", "config": "ask/.config", "arch": "x86_64", "expected": "oldaskconfig_expected.json"},
                    {"name": "syncconfig", "mode": "syncconfig", "kconfig": "Kconfig", "config": "out/.config", "arch": "riscv64", "nosilentupdate": "1", "expected": "syncconfig_expected.json"},
                    {"name": "oldconfig", "mode": "oldconfig", "kconfig": "Kconfig", "config": "refresh/.config", "arch": "x86", "expected": "oldconfig_expected.json"},
                    {"name": "allnoconfig", "mode": "allnoconfig", "kconfig": "Kconfig", "config": "none/.config", "arch": "arm64", "expected": "allnoconfig_expected.json"},
                    {"name": "allyesconfig", "mode": "allyesconfig", "kconfig": "Kconfig", "config": "yes/.config", "arch": "arm64", "expected": "allyesconfig_expected.json"},
                    {"name": "allmodconfig", "mode": "allmodconfig", "kconfig": "Kconfig", "config": "mod/.config", "arch": "arm", "allconfig": "", "expected": "allmodconfig_expected.json"},
                    {"name": "alldefconfig", "mode": "alldefconfig", "kconfig": "Kconfig", "config": "build/.config", "arch": "arm64", "expected": "alldefconfig_expected.json"},
                    {"name": "randconfig", "mode": "randconfig", "kconfig": "Kconfig", "config": "rand/.config", "arch": "x86_64", "allconfig": "allrandom.config", "seed": "0xC0FFEE", "probability": "15:25", "expected": "randconfig_expected.json"},
                    {"name": "defconfig", "mode": "defconfig", "kconfig": "Kconfig", "config": "out/.config", "arch": "arm64", "mode_arg": "arch/arm64/configs/defconfig", "expected": "defconfig_expected.json"},
                    {"name": "savedefconfig", "mode": "savedefconfig", "kconfig": "Kconfig", "config": ".config", "arch": "x86_64", "mode_arg": "defconfig.out", "expected": "savedefconfig_expected.json"},
                    {"name": "listnewconfig", "mode": "listnewconfig", "kconfig": "Kconfig", "config": "out/list.config", "arch": "x86_64", "expected": "listnewconfig_expected.json"},
                    {"name": "helpnewconfig", "mode": "helpnewconfig", "kconfig": "Kconfig", "config": "out/help.config", "arch": "riscv64", "silent": true, "expected": "helpnewconfig_expected.json"},
                    {"name": "olddefconfig", "mode": "olddefconfig", "kconfig": "Kconfig", "config": ".config", "arch": "x86_64", "expected": "olddefconfig_expected.json"},
                    {"name": "yes2modconfig", "mode": "yes2modconfig", "kconfig": "Kconfig", "config": "rewrite/.config", "arch": "x86", "expected": "yes2modconfig_expected.json"},
                    {"name": "mod2yesconfig", "mode": "mod2yesconfig", "kconfig": "Kconfig", "config": "promote/.config", "arch": "x86", "expected": "mod2yesconfig_expected.json"},
                    {"name": "mod2noconfig", "mode": "mod2noconfig", "kconfig": "Kconfig", "config": "demote/.config", "arch": "x86", "expected": "mod2noconfig_expected.json"},
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
                    {"name": "last_state_transitions", "input": "last_state_transitions.config", "expected": "last_state_transitions_expected.json"},
                    {"name": "duplicate_malformed_quoted_assignment", "input": "duplicate_malformed_quoted_assignment.config", "expected": "duplicate_malformed_quoted_assignment_expected.json"},
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json",
        json.dumps(
            {
                "tool": "scripts/zigux/kconfig/conf_bridge.zig",
                "status": "closed",
                "mode": "bounded request-plan bridge",
                "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
                "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
                "case_count": len(REQUIRED_CONF_CASE_MODES),
                "cases": REQUIRED_CONF_CASE_MODES,
                "stdout_packet": [
                    "oldaskconfig_expected.json",
                    "syncconfig_expected.json",
                    "oldconfig_expected.json",
                    "allnoconfig_expected.json",
                    "allyesconfig_expected.json",
                    "allmodconfig_expected.json",
                    "alldefconfig_expected.json",
                    "randconfig_expected.json",
                    "defconfig_expected.json",
                    "savedefconfig_expected.json",
                    "listnewconfig_expected.json",
                    "helpnewconfig_expected.json",
                    "olddefconfig_expected.json",
                    "yes2modconfig_expected.json",
                    "mod2yesconfig_expected.json",
                    "mod2noconfig_expected.json",
                ],
                "mode_arg_cases": [
                    "defconfig",
                    "savedefconfig",
                ],
                "silent_request_packet": [
                    "helpnewconfig_expected.json",
                ],
                "syncconfig_env_packet": [
                    "syncconfig_expected.json",
                ],
                "allconfig_sentinel_packet": [
                    "allnoconfig_expected.json",
                    "allyesconfig_expected.json",
                    "alldefconfig_expected.json",
                ],
                "allconfig_override_packet": [
                    "allmodconfig_expected.json",
                    "randconfig_expected.json",
                ],
                "helper_local_anchors": REQUIRED_CONF_HELPER_ANCHORS,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "confdata_manifest.json",
        json.dumps(
            {
                "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
                "status": "closed",
                "mode": "bounded config bridge",
                "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
                "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
                "case_count": len(REQUIRED_CONFDATA_CASES),
                "cases": REQUIRED_CONFDATA_CASES,
                "input_packet": [
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
                    "last_state_transitions.config",
                    "duplicate_malformed_quoted_assignment.config",
                ],
                "expected_packet": [
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
                    "last_state_transitions_expected.json",
                    "duplicate_malformed_quoted_assignment_expected.json",
                ],
                "helper_local_anchors": REQUIRED_CONFDATA_HELPER_ANCHORS,
            },
            indent=2,
        )
        + "\n",
    )
    for rel_path in (
        "oldaskconfig_expected.json",
        "syncconfig_expected.json",
        "oldconfig_expected.json",
        "allnoconfig_expected.json",
        "allyesconfig_expected.json",
        "allmodconfig_expected.json",
        "alldefconfig_expected.json",
        "randconfig_expected.json",
        "defconfig_expected.json",
        "savedefconfig_expected.json",
        "listnewconfig_expected.json",
        "helpnewconfig_expected.json",
        "olddefconfig_expected.json",
        "yes2modconfig_expected.json",
        "mod2yesconfig_expected.json",
        "mod2noconfig_expected.json",
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
        "last_state_transitions_expected.json",
        "duplicate_malformed_quoted_assignment_expected.json",
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
        "last_state_transitions.config",
        "duplicate_malformed_quoted_assignment.config",
    ):
        write_text(root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / rel_path, "{}\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_kconfig_bridge_selftest_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        cases_path = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json"
        conf_manifest_path = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json"
        manifest_path = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "confdata_manifest.json"
        conf_bridge_path = root / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"
        confdata_bridge_path = root / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"

        build_self_test_root(root)
        assert collect_manifest_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["conf_cases"][0]["mode"] = "unsupported_mode"
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("UNSUPPORTED_CONF_CASE_MODES", "unsupported_mode") in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["conf_cases"] = [case for case in payload["conf_cases"] if case["mode"] != "helpnewconfig"]
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("MISSING_REQUIRED_CONF_CASE_MODES", "helpnewconfig") in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["conf_cases"][1], payload["conf_cases"][5] = payload["conf_cases"][5], payload["conf_cases"][1]
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert any(issue[0] == "CONF_CASE_MODE_ORDER_ACTUAL" for issue in issues)
        assert any(issue[0] == "CONF_CASE_MODE_ORDER_EXPECTED" for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["conf_cases"][1]["mode_arg"] = "unexpected"
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("UNEXPECTED_CONF_MODE_ARG_FIELDS", "syncconfig:syncconfig") in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        del payload["conf_cases"][8]["mode_arg"]
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("MISSING_CONF_MODE_ARG_FIELDS", "defconfig:defconfig") in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["conf_cases"][0]["seed"] = "0xBAD"
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("INVALID_CONF_CASE_RANDCONFIG_FIELDS", "oldaskconfig:seed") in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["conf_cases"][0]["allconfig"] = "mini.config"
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("INVALID_CONF_CASE_ALLCONFIG_FIELDS", "oldaskconfig:allconfig") in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["conf_cases"][0]["nosilentupdate"] = "1"
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("INVALID_CONF_CASE_SYNCCONFIG_FIELDS", "oldaskconfig:nosilentupdate") in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["confdata_cases"][0]["name"] = "syncconfig"
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("DUPLICATE_KCONFIG_CASE_NAMES", "syncconfig:conf_cases,confdata_cases") in issues
        checks_run += 1

        build_self_test_root(root)
        missing_path = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "helpnewconfig_expected.json"
        missing_path.unlink()
        issues = collect_manifest_issues(root)
        assert ("MISSING_CONF_CASE_EXPECTED_PATHS", "helpnewconfig:expected:helpnewconfig_expected.json") in issues
        assert ("CONF_MANIFEST_REFERENCES_MISSING_FIXTURE", "helpnewconfig_expected.json") in issues
        checks_run += 1

        build_self_test_root(root)
        missing_path = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "sample_crlf_expected.json"
        missing_path.unlink()
        issues = collect_manifest_issues(root)
        assert ("MISSING_CONFDATA_CASE_PATHS", "sample_crlf:expected:sample_crlf_expected.json") in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["confdata_cases"].pop()
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("CONFDATA_CASE_ORDER_ACTUAL", ",".join(REQUIRED_CONFDATA_CASES[:-1])) in issues
        assert ("CONFDATA_CASE_ORDER_EXPECTED", ",".join(REQUIRED_CONFDATA_CASES)) in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["confdata_cases"][1], payload["confdata_cases"][2] = payload["confdata_cases"][2], payload["confdata_cases"][1]
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("CONFDATA_CASE_ORDER_ACTUAL", "sample,escaped_control_sequences,escaped_strings,trailing_escaped_backslash,sample_crlf,explicit_n_tristate,final_trailing_carriage_return,final_unterminated_unset_comment,uppercase_tristate,non_config_lines,empty_config_symbol_names,last_state_transitions,duplicate_malformed_quoted_assignment") in issues
        assert ("CONFDATA_CASE_ORDER_EXPECTED", ",".join(REQUIRED_CONFDATA_CASES)) in issues
        checks_run += 1

        build_self_test_root(root)
        source = conf_bridge_path.read_text(encoding="utf-8")
        source = source.replace('test "conf bridge emits randconfig tunables when present" {\n', 'test "conf bridge emits renamed randconfig tunables" {\n', 1)
        write_text(conf_bridge_path, source)
        issues = collect_manifest_issues(root)
        assert any(issue[0] == "CONF_SOURCE_HELPER_LOCAL_ANCHORS_ACTUAL" for issue in issues)
        assert any(issue[0] == "CONF_SOURCE_HELPER_LOCAL_ANCHORS_EXPECTED" for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        source = conf_bridge_path.read_text(encoding="utf-8")
        source += '\ntest "conf bridge future helper surface stays visible to the checker" {\n    try std.testing.expect(true);\n}\n'
        write_text(conf_bridge_path, source)
        issues = collect_manifest_issues(root)
        assert any(issue[0] == "CONF_SOURCE_HELPER_LOCAL_ANCHORS_ACTUAL" for issue in issues)
        assert any(issue[0] == "CONF_SOURCE_HELPER_LOCAL_ANCHORS_EXPECTED" for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        conf_manifest_path.unlink()
        issues = collect_manifest_issues(root)
        assert ("MISSING_CONF_MANIFEST", "conf_manifest.json") in issues
        checks_run += 1

        build_self_test_root(root)
        manifest = json.loads(conf_manifest_path.read_text(encoding="utf-8"))
        manifest["mode_arg_cases"] = ["savedefconfig"]
        write_text(conf_manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert any(issue[0] == "CONF_MANIFEST_MODE_ARG_CASES_MISMATCH" for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        manifest = json.loads(conf_manifest_path.read_text(encoding="utf-8"))
        manifest["helper_local_anchors"] = REQUIRED_CONF_HELPER_ANCHORS[:-1]
        write_text(conf_manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert any(issue[0] == "CONF_MANIFEST_HELPER_LOCAL_ANCHORS_MISMATCH" for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        source = confdata_bridge_path.read_text(encoding="utf-8")
        source = source.replace('test "confdata bridge emits bounded json output" {\n', 'test "confdata bridge emits reordered json output" {\n', 1)
        write_text(confdata_bridge_path, source)
        issues = collect_manifest_issues(root)
        assert any(issue[0] == "CONFDATA_SOURCE_HELPER_LOCAL_ANCHORS_ACTUAL" for issue in issues)
        assert any(issue[0] == "CONFDATA_SOURCE_HELPER_LOCAL_ANCHORS_EXPECTED" for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        manifest_path.unlink()
        issues = collect_manifest_issues(root)
        assert ("MISSING_CONFDATA_MANIFEST", "confdata_manifest.json") in issues
        checks_run += 1

        build_self_test_root(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["helper_local_anchors"] = REQUIRED_CONFDATA_HELPER_ANCHORS[:-1]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert any(issue[0] == "CONFDATA_MANIFEST_HELPER_LOCAL_ANCHORS_MISMATCH" for issue in issues)
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
    cases = load_cases(FIXTURE_DIR)

    with tempfile.TemporaryDirectory(prefix="zigux_kconfig_bridge_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        conf_exe = tmp_dir / ("conf-bridge.exe" if sys.platform == "win32" else "conf-bridge")
        confdata_exe = tmp_dir / ("confdata-bridge.exe" if sys.platform == "win32" else "confdata-bridge")
        compile_tool(zig, CONF_BRIDGE, conf_exe)
        compile_tool(zig, CONFDATA_BRIDGE, confdata_exe)

        for case in cases["conf_cases"]:
            actual = tmp_dir / f"{case['name']}.actual.json"
            cmd = [str(conf_exe), case["mode"], case["kconfig"], case["config"], case["arch"]]
            if "mode_arg" in case:
                cmd.append(case["mode_arg"])
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
            result = run(cmd, cwd=str(ROOT), capture_output=True)
            actual.write_text(result.stdout, encoding="utf-8", newline="\n")
            run([sys.executable, str(ARTIFACT_DIFF), "--mode", "json", str(FIXTURE_DIR / case["expected"]), str(actual)], cwd=str(ROOT))

        for case in cases["confdata_cases"]:
            actual = tmp_dir / f"{case['name']}.actual.json"
            result = run([str(confdata_exe), str(FIXTURE_DIR / case["input"] )], cwd=str(ROOT), capture_output=True)
            actual.write_text(result.stdout, encoding="utf-8", newline="\n")
            run([sys.executable, str(ARTIFACT_DIFF), "--mode", "json", str(FIXTURE_DIR / case["expected"]), str(actual)], cwd=str(ROOT))

    print("KCONFIG_BRIDGE_DIFF=pass")
    print(f"FIXTURE_DIR={FIXTURE_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
