#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

VALIDATE_PHASE2 = ROOT / "scripts" / "zigux" / "validate-phase2.py"
CHECK_PHASE2_TOOLCHAIN_PIN_SCOPE = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"
CHECK_PHASE2_TESTS_README_ALIGNMENT = ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"
CHECK_PHASE2_KCONFIG_README_ALIGNMENT = ROOT / "scripts" / "zigux" / "check-phase2-kconfig-readme-alignment.py"
CHECK_PHASE2_TOOL_MANIFEST_PACKETS = ROOT / "scripts" / "zigux" / "check-phase2-tool-manifest-packets.py"
PHASE2_TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
PHASE2_ARTIFACT_TOOLS_MANIFEST = (
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_artifact_tools_manifest.json"
)
PHASE2_CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
PHASE2_FIXDEP_NEXT_STEP_NOTE = (
    ROOT / "Documentation" / "zigux" / "phase2-fixdep-next-step-note.md"
)
PHASE2_CONFDATA_BRIDGE_SURVEY = (
    ROOT / "Documentation" / "zigux" / "phase2-confdata-bridge-survey.md"
)
PHASE2_MAKEFILE = ROOT / "zigux" / "Makefile"
PHASE2_WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
FIXDEP_CASES = ROOT / "zigux" / "tests" / "fixtures" / "fixdep" / "cases.json"
KCONFIG_BRIDGE_CASES = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json"
KCONFIG_BRIDGE_CONF_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json"
KCONFIG_BRIDGE_CONFDATA_MANIFEST = (
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "confdata_manifest.json"
)

FIXDEP_CLOSURE_MARKER = (
    "the current `fixdep` closure packet now stays explicit as the eleven-case artifact replay under "
    "`zigux/tests/fixtures/fixdep/cases.json`, including the escaped-newline rustc-style pre-target "
    "comment case, the concatenated same-target dep tail, and the bounded `/dev/full` stdout-write "
    "cases that preserve the original parse-error or missing-dependency stderr contract"
)

PHASE2_COMPANION_NOTES_MARKER = (
    "`Documentation/zigux/phase2-fixdep-next-step-note.md` and "
    "`Documentation/zigux/phase2-confdata-bridge-survey.md` are active Phase 2 companion notes "
    "on current `master`: the fixdep note records that `scripts/zigux/check-phase2-fixdep-gate.py`, "
    "`Documentation/zigux/artifact-diff.md`, `Documentation/zigux/phase2-closure.md`, and "
    "`zigux/tests/fixtures/fixdep/cases.json` already agree on the same live eleven-case packet "
    "and keeps the parked validation rerun explicit, and the confdata survey keeps the roadmap-backed "
    "scaffold marked closed so future reopening stays bridge-local instead of recreating "
    "missing-scaffold claims."
)

PHASE2_REQUIRED_SOURCE_MARKERS = [
    "PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "PHASE2_TOOLCHAIN_PIN_SCOPE_GATE=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "shared tool-manifest packet self-test: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test`",
    "shared tool-manifest packet gate: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "PHASE2_FIXDEP_EMBEDDED_NUL_GUARD=fixdep.zig truncates depfile parsing at the first embedded NUL and keeps dep parsing skips bytes after the first embedded NUL as the bounded parser guard",
    FIXDEP_CLOSURE_MARKER,
    PHASE2_COMPANION_NOTES_MARKER,
    "shared cross compile self-test: `python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "shared cross compile gate: `python3 scripts/zigux/check-phase2-cross.py`",
    "shared cross-selftest alignment self-test: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`",
    "shared cross-selftest alignment gate: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "shared fixdep gate self-test: `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`",
    "shared fixdep gate: `python3 scripts/zigux/check-phase2-fixdep-gate.py`",
    "shared fixdep diff self-test: `python3 scripts/zigux/check-fixdep-diff.py --self-test`",
    "shared fixdep diff gate: `python3 scripts/zigux/check-fixdep-diff.py`",
    "committed genksyms bridge fixture packet: `zigux/tests/fixtures/genksyms_bridge/`",
    "committed genksyms CRC and mk_elfconfig artifact fixture packets: `zigux/tests/fixtures/genksyms_crc/` and `zigux/tests/fixtures/mk_elfconfig/`",
    "shared kconfig selftest-alignment self-test: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`",
    "shared kconfig selftest-alignment gate: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "the dedicated `Phase 2 genksyms` bridge packet remains the live `23-case` bridge surface under `zigux/tests/fixtures/genksyms_bridge/`, and the shared reminder surfaces should keep that fixture-backed bridge evidence explicit without drifting back to older undercounts or claiming standalone checker scripts that are not present on current `master`",
    "the current `kconfig` closure packet now stays explicit as the `16-case` conf bridge plus `12-case` confdata fixture replay under `zigux/tests/fixtures/kconfig_bridge/cases.json`, with `syncconfig` `nosilentupdate`, explicit `allconfig` overrides, and the current confdata packet all carried through the shared checker and committed expected outputs instead of leaving those later bridge expansions implicit",
]

PHASE2_MAKEFILE_RUN_COUNTS = {
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py": 1,
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test": 1,
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py": 1,
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py --self-test": 1,
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py": 1,
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test": 1,
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-readme-alignment.py": 1,
}

PHASE2_WORKFLOW_RUN_COUNTS = {
    "run: python3 scripts/zigux/validate-phase2.py": 1,
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py": 1,
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test": 1,
    "run: python3 scripts/zigux/check-genksyms-bridge.py": 1,
    "run: python3 scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test": 1,
    "run: python3 scripts/zigux/check-phase2-kconfig-readme-alignment.py": 1,
}

PHASE2_VALIDATION_COMMAND_SPECS = (
    (VALIDATE_PHASE2,),
    (CHECK_PHASE2_TESTS_README_ALIGNMENT,),
    (CHECK_PHASE2_KCONFIG_README_ALIGNMENT,),
    (CHECK_PHASE2_TOOL_MANIFEST_PACKETS,),
    (CHECK_PHASE2_TOOLCHAIN_PIN_SCOPE,),
)

PHASE2_VALIDATOR_MARKERS = [
    'PHASE2_TOOL_MANIFEST_PACKET_CHECKER = (',
    '    (PHASE2_TOOL_MANIFEST_PACKET_CHECKER, "--self-test"),',
    '    (PHASE2_TOOL_MANIFEST_PACKET_CHECKER,),',
    '    "scripts/zigux/check-phase2-tool-manifest-packets.py",',
    '    "zigux/tests/fixtures/phase2_tool_manifest.json",',
    '    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",',
    "PHASE2_VALIDATION_EXPECTED_COMMAND_COUNT = 21",
    "PHASE2_VALIDATION_EXPECTED_REQUIRED_FILE_COUNT = 32",
]

EXPECTED_FIXDEP_CASES = (
    {"name": "sample"},
    {"name": "sample_multi_target"},
    {"name": "sample_escaped_space"},
    {"name": "sample_escaped_colon"},
    {"name": "sample_concatenated"},
    {"name": "sample_comment_continuation"},
    {"name": "sample_comment_only"},
    {"name": "sample_comment_only_stdout_full", "stdout_mode": "dev_full"},
    {"name": "sample_missing_dep"},
    {"name": "sample_missing_dep_stdout_full", "stdout_mode": "dev_full"},
    {"name": "sample_output_write", "stdout_mode": "dev_full"},
)

EXPECTED_CONF_CASES = (
    {
        "name": "oldaskconfig",
        "mode": "oldaskconfig",
        "kconfig": "Kconfig",
        "config": "ask/.config",
        "arch": "x86_64",
        "expected": "oldaskconfig_expected.json",
    },
    {
        "name": "syncconfig",
        "mode": "syncconfig",
        "kconfig": "Kconfig",
        "config": "out/.config",
        "arch": "riscv64",
        "nosilentupdate": "1",
        "expected": "syncconfig_expected.json",
    },
    {
        "name": "oldconfig",
        "mode": "oldconfig",
        "kconfig": "Kconfig",
        "config": "refresh/.config",
        "arch": "x86",
        "expected": "oldconfig_expected.json",
    },
    {
        "name": "allnoconfig",
        "mode": "allnoconfig",
        "kconfig": "Kconfig",
        "config": "none/.config",
        "arch": "arm64",
        "expected": "allnoconfig_expected.json",
    },
    {
        "name": "allyesconfig",
        "mode": "allyesconfig",
        "kconfig": "Kconfig",
        "config": "yes/.config",
        "arch": "arm64",
        "expected": "allyesconfig_expected.json",
    },
    {
        "name": "allmodconfig",
        "mode": "allmodconfig",
        "kconfig": "Kconfig",
        "config": "mod/.config",
        "arch": "arm",
        "allconfig": "",
        "expected": "allmodconfig_expected.json",
    },
    {
        "name": "alldefconfig",
        "mode": "alldefconfig",
        "kconfig": "Kconfig",
        "config": "build/.config",
        "arch": "arm64",
        "expected": "alldefconfig_expected.json",
    },
    {
        "name": "randconfig",
        "mode": "randconfig",
        "kconfig": "Kconfig",
        "config": "rand/.config",
        "arch": "x86_64",
        "allconfig": "allrandom.config",
        "seed": "0xC0FFEE",
        "probability": "15:25",
        "expected": "randconfig_expected.json",
    },
    {
        "name": "defconfig",
        "mode": "defconfig",
        "kconfig": "Kconfig",
        "config": "out/.config",
        "arch": "arm64",
        "mode_arg": "arch/arm64/configs/defconfig",
        "expected": "defconfig_expected.json",
    },
    {
        "name": "savedefconfig",
        "mode": "savedefconfig",
        "kconfig": "Kconfig",
        "config": ".config",
        "arch": "x86_64",
        "mode_arg": "defconfig.out",
        "expected": "savedefconfig_expected.json",
    },
    {
        "name": "listnewconfig",
        "mode": "listnewconfig",
        "kconfig": "Kconfig",
        "config": "out/list.config",
        "arch": "x86_64",
        "expected": "listnewconfig_expected.json",
    },
    {
        "name": "helpnewconfig",
        "mode": "helpnewconfig",
        "kconfig": "Kconfig",
        "config": "out/help.config",
        "arch": "riscv64",
        "silent": True,
        "expected": "helpnewconfig_expected.json",
    },
    {
        "name": "olddefconfig",
        "mode": "olddefconfig",
        "kconfig": "Kconfig",
        "config": ".config",
        "arch": "x86_64",
        "expected": "olddefconfig_expected.json",
    },
    {
        "name": "yes2modconfig",
        "mode": "yes2modconfig",
        "kconfig": "Kconfig",
        "config": "rewrite/.config",
        "arch": "x86",
        "expected": "yes2modconfig_expected.json",
    },
    {
        "name": "mod2yesconfig",
        "mode": "mod2yesconfig",
        "kconfig": "Kconfig",
        "config": "promote/.config",
        "arch": "x86",
        "expected": "mod2yesconfig_expected.json",
    },
    {
        "name": "mod2noconfig",
        "mode": "mod2noconfig",
        "kconfig": "Kconfig",
        "config": "demote/.config",
        "arch": "x86",
        "expected": "mod2noconfig_expected.json",
    },
)

EXPECTED_CONF_MANIFEST = {
    "tool": "scripts/zigux/kconfig/conf_bridge.zig",
    "status": "closed",
    "mode": "bounded request-plan bridge",
    "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
    "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "case_count": 16,
    "cases": [case["name"] for case in EXPECTED_CONF_CASES],
    "stdout_packet": [case["expected"] for case in EXPECTED_CONF_CASES],
    "mode_arg_cases": ["defconfig", "savedefconfig"],
    "silent_request_packet": ["helpnewconfig_expected.json"],
    "syncconfig_env_packet": ["syncconfig_expected.json"],
    "allconfig_sentinel_packet": [
        "allnoconfig_expected.json",
        "allyesconfig_expected.json",
        "alldefconfig_expected.json",
    ],
    "allconfig_override_packet": [
        "allmodconfig_expected.json",
        "randconfig_expected.json",
    ],
}

EXPECTED_CONFDATA_CASES = (
    {"name": "sample", "input": "sample.config", "expected": "sample_expected.json"},
    {
        "name": "escaped_strings",
        "input": "escaped_strings.config",
        "expected": "escaped_strings_expected.json",
    },
    {
        "name": "escaped_control_sequences",
        "input": "escaped_control_sequences.config",
        "expected": "escaped_control_sequences_expected.json",
    },
    {
        "name": "trailing_escaped_backslash",
        "input": "trailing_escaped_backslash.config",
        "expected": "trailing_escaped_backslash_expected.json",
    },
    {"name": "sample_crlf", "input": "sample_crlf.config", "expected": "sample_crlf_expected.json"},
    {
        "name": "explicit_n_tristate",
        "input": "explicit_n_tristate.config",
        "expected": "explicit_n_tristate_expected.json",
    },
    {
        "name": "final_trailing_carriage_return",
        "input": "final_trailing_carriage_return.config",
        "expected": "final_trailing_carriage_return_expected.json",
    },
    {
        "name": "final_unterminated_unset_comment",
        "input": "final_unterminated_unset_comment.config",
        "expected": "final_unterminated_unset_comment_expected.json",
    },
    {
        "name": "uppercase_tristate",
        "input": "uppercase_tristate.config",
        "expected": "uppercase_tristate_expected.json",
    },
    {
        "name": "non_config_lines",
        "input": "non_config_lines.config",
        "expected": "non_config_lines_expected.json",
    },
    {
        "name": "empty_config_symbol_names",
        "input": "empty_config_symbol_names.config",
        "expected": "empty_config_symbol_names_expected.json",
    },
    {
        "name": "last_state_transitions",
        "input": "last_state_transitions.config",
        "expected": "last_state_transitions_expected.json",
    },
)

EXPECTED_CONFDATA_MANIFEST = {
    "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
    "status": "closed",
    "mode": "bounded config bridge",
    "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
    "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "case_count": 12,
    "cases": [case["name"] for case in EXPECTED_CONFDATA_CASES],
    "input_packet": [case["input"] for case in EXPECTED_CONFDATA_CASES],
    "expected_packet": [case["expected"] for case in EXPECTED_CONFDATA_CASES],
    "helper_local_anchors": [
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
        "confdata bridge keeps trailing escaped backslashes in quoted strings",
        "confdata bridge emits escaped quoted payloads before trailing suffix bytes",
        "confdata bridge leaves malformed quoted values as raw scalar values",
        "confdata bridge emits no entries for empty CONFIG symbol names",
        "confdata bridge keeps only the last assignment for duplicate symbols",
        "confdata bridge keeps only the last state across unset and set transitions",
    ],
}

def require_files(paths: list[Path]) -> list[str]:
    missing: list[str] = []
    for path in paths:
        if not path.exists():
            missing.append(str(path.relative_to(ROOT)))
    return missing


def validate_required_markers(text: str, markers: list[str], label: str) -> list[str]:
    return [f"{label}:missing:{marker}" for marker in markers if marker not in text]


def validate_exact_lines(text: str, counts: dict[str, int], label: str) -> list[str]:
    issues: list[str] = []
    lines = [line.strip() for line in text.splitlines()]
    for marker, expected in counts.items():
        count = sum(1 for line in lines if line == marker)
        if count != expected:
            issues.append(f"{label}:exact_count:{marker}:count={count}:expected={expected}")
    return issues


def command_tail(command: list[str]) -> str:
    tail_parts: list[str] = []
    for part in command[1:]:
        path = Path(part)
        if path.is_absolute():
            try:
                tail_parts.append(str(path.relative_to(ROOT)))
                continue
            except ValueError:
                pass
        tail_parts.append(str(part))
    return " ".join(tail_parts)


def build_validation_commands() -> list[list[str]]:
    return [[sys.executable, str(spec[0]), *[str(part) for part in spec[1:]]] for spec in PHASE2_VALIDATION_COMMAND_SPECS]


def load_json_object(path: Path, label: str) -> tuple[dict[str, object] | None, list[str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, [f"{label}:read_error:{exc}"]
    except json.JSONDecodeError as exc:
        return None, [f"{label}:invalid_json:{exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"{label}:expected_object"]
    return payload, []


def load_json_list(path: Path, label: str) -> tuple[list[object] | None, list[str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, [f"{label}:read_error:{exc}"]
    except json.JSONDecodeError as exc:
        return None, [f"{label}:invalid_json:{exc.msg}"]
    if not isinstance(payload, list):
        return None, [f"{label}:expected_list"]
    return payload, []


def validate_fixdep_cases(payload: list[object]) -> list[str]:
    issues: list[str] = []
    expected_count = len(EXPECTED_FIXDEP_CASES)
    if len(payload) != expected_count:
        issues.append(f"fixdep_cases:count={len(payload)}:expected={expected_count}")
    for index, expected_case in enumerate(EXPECTED_FIXDEP_CASES):
        if index >= len(payload):
            break
        case = payload[index]
        if not isinstance(case, dict):
            issues.append(f"fixdep_cases[{index}]:expected_object")
            continue
        name = expected_case["name"]
        for field_name, expected_value in expected_case.items():
            actual_value = case.get(field_name)
            if actual_value != expected_value:
                issues.append(
                    f"fixdep_cases:{name}:{field_name}:expected={expected_value}:actual={actual_value}"
                )
    if len(payload) > expected_count:
        for case in payload[expected_count:]:
            extra_name = case.get("name", "<missing>") if isinstance(case, dict) else "<non_object>"
            issues.append(f"fixdep_cases:unexpected_extra:{extra_name}")
    return issues


def validate_case_list(
    payload: dict[str, object],
    *,
    key: str,
    expected_cases: tuple[dict[str, object], ...],
) -> tuple[list[Path], list[str]]:
    issues: list[str] = []
    raw_cases = payload.get(key)
    if not isinstance(raw_cases, list):
        return [], [f"kconfig_bridge_cases:{key}:expected_list"]
    if not raw_cases:
        return [], [f"kconfig_bridge_cases:{key}:empty"]

    expected_count = len(expected_cases)
    if len(raw_cases) != expected_count:
        issues.append(f"kconfig_bridge_cases:{key}:count={len(raw_cases)}:expected={expected_count}")

    required_files: list[Path] = []
    seen_paths: set[str] = set()
    for index, expected_case in enumerate(expected_cases):
        if index >= len(raw_cases):
            break
        case = raw_cases[index]
        if not isinstance(case, dict):
            issues.append(f"kconfig_bridge_cases:{key}[{index}]:expected_object")
            continue
        name = expected_case["name"]
        for field_name, expected_value in expected_case.items():
            actual_value = case.get(field_name)
            if actual_value != expected_value:
                issues.append(
                    f"kconfig_bridge_cases:{name}:{field_name}:expected={expected_value}:actual={actual_value}"
                )
        unexpected_fields = sorted(set(case.keys()) - set(expected_case.keys()))
        for field_name in unexpected_fields:
            issues.append(f"kconfig_bridge_cases:{name}:{field_name}:unexpected={case.get(field_name)}")
        for field_name in ("input", "expected"):
            value = case.get(field_name)
            if isinstance(value, str) and value:
                if value in seen_paths:
                    issues.append(f"kconfig_bridge_cases:{name}:{field_name}:duplicate_reference:{value}")
                else:
                    seen_paths.add(value)
                    required_files.append(KCONFIG_BRIDGE_CASES.parent / value)
    if len(raw_cases) > expected_count:
        for case in raw_cases[expected_count:]:
            extra_name = case.get("name", "<missing>") if isinstance(case, dict) else "<non_object>"
            issues.append(f"kconfig_bridge_cases:{key}:unexpected_extra:{extra_name}")
    return required_files, issues


def validate_manifest(payload: dict[str, object], *, expected: dict[str, object], label: str) -> list[str]:
    issues: list[str] = []
    for field_name, expected_value in expected.items():
        actual_value = payload.get(field_name)
        if actual_value != expected_value:
            issues.append(f"{label}:{field_name}:expected={expected_value}:actual={actual_value}")
    return issues


def run_self_test_checks() -> list[str]:
    checks = [
        (
            "validation_commands_include_shared_validator",
            validate_required_markers(
                "\n".join(command_tail(command) for command in build_validation_commands()),
                ["scripts/zigux/validate-phase2.py"],
                "phase2_validation_commands",
            ),
            [],
        ),
        (
            "validation_commands_missing_shared_validator",
            validate_required_markers(
                "\n".join(
                    [
                        "scripts/zigux/check-phase2-tests-readme-alignment.py",
                        "scripts/zigux/check-phase2-kconfig-readme-alignment.py",
                        "scripts/zigux/check-phase2-tool-manifest-packets.py",
                        "scripts/zigux/check-phase2-toolchain-pin-scope.py",
                    ]
                ),
                ["scripts/zigux/validate-phase2.py"],
                "phase2_validation_commands",
            ),
            ["phase2_validation_commands:missing:scripts/zigux/validate-phase2.py"],
        ),
        (
            "fixdep_cases_ok",
            validate_fixdep_cases([dict(case) for case in EXPECTED_FIXDEP_CASES]),
            [],
        ),
        (
            "fixdep_cases_missing_dev_full",
            validate_fixdep_cases(
                [
                    *[dict(case) for case in EXPECTED_FIXDEP_CASES[:7]],
                    {"name": "sample_comment_only_stdout_full"},
                    *[dict(case) for case in EXPECTED_FIXDEP_CASES[8:]],
                ]
            ),
            ["fixdep_cases:sample_comment_only_stdout_full:stdout_mode:expected=dev_full:actual=None"],
        ),
        (
            "fixdep_cases_missing_closure_marker",
            validate_required_markers(
                "\n".join(marker for marker in PHASE2_REQUIRED_SOURCE_MARKERS if marker != FIXDEP_CLOSURE_MARKER),
                PHASE2_REQUIRED_SOURCE_MARKERS,
                "phase2_closure",
            ),
            [f"phase2_closure:missing:{FIXDEP_CLOSURE_MARKER}"],
        ),
        (
            "companion_notes_marker_missing",
            validate_required_markers(
                "\n".join(
                    marker for marker in PHASE2_REQUIRED_SOURCE_MARKERS if marker != PHASE2_COMPANION_NOTES_MARKER
                ),
                PHASE2_REQUIRED_SOURCE_MARKERS,
                "phase2_closure",
            ),
            [f"phase2_closure:missing:{PHASE2_COMPANION_NOTES_MARKER}"],
        ),
        (
            "conf_cases_ok",
            validate_case_list(
                {"conf_cases": [dict(case) for case in EXPECTED_CONF_CASES]},
                key="conf_cases",
                expected_cases=EXPECTED_CONF_CASES,
            )[1],
            [],
        ),
        (
            "conf_cases_missing_mode_arg",
            validate_case_list(
                {
                    "conf_cases": [
                        *[dict(case) for case in EXPECTED_CONF_CASES[:8]],
                        {
                            "name": "defconfig",
                            "mode": "defconfig",
                            "kconfig": "Kconfig",
                            "config": "out/.config",
                            "arch": "arm64",
                            "expected": "defconfig_expected.json",
                        },
                        *[dict(case) for case in EXPECTED_CONF_CASES[9:]],
                    ]
                },
                key="conf_cases",
                expected_cases=EXPECTED_CONF_CASES,
            )[1],
            ["kconfig_bridge_cases:defconfig:mode_arg:expected=arch/arm64/configs/defconfig:actual=None"],
        ),
        (
            "conf_manifest_case_count_mismatch",
            validate_manifest(
                dict(EXPECTED_CONF_MANIFEST, case_count=15),
                expected=EXPECTED_CONF_MANIFEST,
                label="kconfig_bridge_conf_manifest",
            ),
            ["kconfig_bridge_conf_manifest:case_count:expected=16:actual=15"],
        ),
        (
            "confdata_cases_ok",
            validate_case_list(
                {"confdata_cases": [dict(case) for case in EXPECTED_CONFDATA_CASES]},
                key="confdata_cases",
                expected_cases=EXPECTED_CONFDATA_CASES,
            )[1],
            [],
        ),
        (
            "confdata_cases_missing_input",
            validate_case_list(
                {
                    "confdata_cases": [
                        {"name": "sample", "expected": "sample_expected.json"},
                        *[dict(case) for case in EXPECTED_CONFDATA_CASES[1:]],
                    ]
                },
                key="confdata_cases",
                expected_cases=EXPECTED_CONFDATA_CASES,
            )[1],
            ["kconfig_bridge_cases:sample:input:expected=sample.config:actual=None"],
        ),
        (
            "confdata_manifest_case_count_mismatch",
            validate_manifest(
                dict(EXPECTED_CONFDATA_MANIFEST, case_count=11),
                expected=EXPECTED_CONFDATA_MANIFEST,
                label="kconfig_bridge_confdata_manifest",
            ),
            ["kconfig_bridge_confdata_manifest:case_count:expected=12:actual=11"],
        ),
        (
            "workflow_tests_readme_selftest_missing",
            validate_exact_lines(
                "run: python3 scripts/zigux/validate-phase2.py\n"
                "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py\n"
                "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test\n"
                "run: python3 scripts/zigux/check-genksyms-bridge.py\n"
                "run: python3 scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test\n"
                "run: python3 scripts/zigux/check-phase2-kconfig-readme-alignment.py\n",
                PHASE2_WORKFLOW_RUN_COUNTS,
                "workflow",
            ),
            [
                "workflow:exact_count:run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test:count=0:expected=1"
            ],
        ),
        (
            "workflow_genksyms_bridge_selftest_missing",
            validate_exact_lines(
                "run: python3 scripts/zigux/validate-phase2.py\n"
                "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test\n"
                "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py\n"
                "run: python3 scripts/zigux/check-genksyms-bridge.py\n"
                "run: python3 scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test\n"
                "run: python3 scripts/zigux/check-phase2-kconfig-readme-alignment.py\n",
                PHASE2_WORKFLOW_RUN_COUNTS,
                "workflow",
            ),
            [
                "workflow:exact_count:run: python3 scripts/zigux/check-genksyms-bridge.py --self-test:count=0:expected=1"
            ],
        ),
        (
            "makefile_phase2_validation_missing",
            validate_exact_lines(
                "\n".join(
                    [
                        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py",
                        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
                        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py",
                        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
                        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py",
                        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test",
                        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-readme-alignment.py",
                    ]
                ),
                PHASE2_MAKEFILE_RUN_COUNTS,
                "makefile",
            ),
            ["makefile:exact_count:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py:count=0:expected=1"],
        ),
        (
            "phase2_validator_missing_tool_manifest_command",
            validate_required_markers(
                "\n".join(marker for marker in PHASE2_VALIDATOR_MARKERS if marker != '    (PHASE2_TOOL_MANIFEST_PACKET_CHECKER, "--self-test"),'),
                PHASE2_VALIDATOR_MARKERS,
                "phase2_validator",
            ),
            ['phase2_validator:missing:    (PHASE2_TOOL_MANIFEST_PACKET_CHECKER, "--self-test"),'],
        ),
        (
            "phase2_validator_missing_command_count_marker",
            validate_required_markers(
                "\n".join(marker for marker in PHASE2_VALIDATOR_MARKERS if marker != "PHASE2_VALIDATION_EXPECTED_COMMAND_COUNT = 21"),
                PHASE2_VALIDATOR_MARKERS,
                "phase2_validator",
            ),
            ["phase2_validator:missing:PHASE2_VALIDATION_EXPECTED_COMMAND_COUNT = 21"],
        ),
        (
            "phase2_validator_missing_required_file_count_marker",
            validate_required_markers(
                "\n".join(marker for marker in PHASE2_VALIDATOR_MARKERS if marker != "PHASE2_VALIDATION_EXPECTED_REQUIRED_FILE_COUNT = 32"),
                PHASE2_VALIDATOR_MARKERS,
                "phase2_validator",
            ),
            ["phase2_validator:missing:PHASE2_VALIDATION_EXPECTED_REQUIRED_FILE_COUNT = 32"],
        ),
    ]

    issues: list[str] = []
    for name, actual, expected in checks:
        if actual != expected:
            issues.append(f"self_test:{name}:actual={actual}:expected={expected}")
    return issues


def run(command: list[str]) -> int:
    return subprocess.run(command, cwd=ROOT, check=False).returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current live Phase 2 closure packet on current master."
    )
    parser.add_argument("--self-test", action="store_true", help="Run closure-validator self coverage.")
    args = parser.parse_args()

    required = [
        VALIDATE_PHASE2,
        CHECK_PHASE2_TOOLCHAIN_PIN_SCOPE,
        CHECK_PHASE2_TESTS_README_ALIGNMENT,
        CHECK_PHASE2_KCONFIG_README_ALIGNMENT,
        CHECK_PHASE2_TOOL_MANIFEST_PACKETS,
        PHASE2_TOOL_MANIFEST,
        PHASE2_ARTIFACT_TOOLS_MANIFEST,
        PHASE2_CLOSURE_DOC,
        PHASE2_FIXDEP_NEXT_STEP_NOTE,
        PHASE2_CONFDATA_BRIDGE_SURVEY,
        PHASE2_MAKEFILE,
        PHASE2_WORKFLOW,
        FIXDEP_CASES,
        KCONFIG_BRIDGE_CASES,
        KCONFIG_BRIDGE_CONF_MANIFEST,
        KCONFIG_BRIDGE_CONFDATA_MANIFEST,
    ]
    missing = require_files(required)
    if missing:
        label = "PHASE2_CLOSURE_VALIDATION_SELF_TEST" if args.self_test else "PHASE2_CLOSURE_VALIDATION"
        print(f"{label}=fail")
        print("PHASE2_CLOSURE_VALIDATION_MISSING_FILES_START")
        for item in missing:
            print(item)
        print("PHASE2_CLOSURE_VALIDATION_MISSING_FILES_END")
        return 1

    issues: list[str] = []
    closure_text = PHASE2_CLOSURE_DOC.read_text(encoding="utf-8")
    issues.extend(validate_required_markers(closure_text, PHASE2_REQUIRED_SOURCE_MARKERS, "phase2_closure"))
    issues.extend(validate_exact_lines(PHASE2_MAKEFILE.read_text(encoding="utf-8"), PHASE2_MAKEFILE_RUN_COUNTS, "makefile"))
    issues.extend(validate_exact_lines(PHASE2_WORKFLOW.read_text(encoding="utf-8"), PHASE2_WORKFLOW_RUN_COUNTS, "workflow"))
    issues.extend(
        validate_required_markers(
            VALIDATE_PHASE2.read_text(encoding="utf-8"),
            PHASE2_VALIDATOR_MARKERS,
            "phase2_validator",
        )
    )

    fixdep_cases_payload, fixdep_issues = load_json_list(FIXDEP_CASES, "fixdep_cases")
    issues.extend(fixdep_issues)
    if fixdep_cases_payload is not None:
        issues.extend(validate_fixdep_cases(fixdep_cases_payload))

    cases_payload, cases_issues = load_json_object(KCONFIG_BRIDGE_CASES, "kconfig_bridge_cases")
    issues.extend(cases_issues)
    if cases_payload is not None:
        conf_required, conf_list_issues = validate_case_list(
            cases_payload,
            key="conf_cases",
            expected_cases=EXPECTED_CONF_CASES,
        )
        issues.extend(conf_list_issues)
        confdata_required, confdata_list_issues = validate_case_list(
            cases_payload,
            key="confdata_cases",
            expected_cases=EXPECTED_CONFDATA_CASES,
        )
        issues.extend(confdata_list_issues)
        for path in require_files(conf_required + confdata_required):
            issues.append(f"kconfig_bridge_cases:missing_expected:{path}")

    conf_manifest_payload, conf_manifest_issues = load_json_object(
        KCONFIG_BRIDGE_CONF_MANIFEST,
        "kconfig_bridge_conf_manifest",
    )
    issues.extend(conf_manifest_issues)
    if conf_manifest_payload is not None:
        issues.extend(
            validate_manifest(
                conf_manifest_payload,
                expected=EXPECTED_CONF_MANIFEST,
                label="kconfig_bridge_conf_manifest",
            )
        )

    confdata_manifest_payload, confdata_manifest_issues = load_json_object(
        KCONFIG_BRIDGE_CONFDATA_MANIFEST,
        "kconfig_bridge_confdata_manifest",
    )
    issues.extend(confdata_manifest_issues)
    if confdata_manifest_payload is not None:
        issues.extend(
            validate_manifest(
                confdata_manifest_payload,
                expected=EXPECTED_CONFDATA_MANIFEST,
                label="kconfig_bridge_confdata_manifest",
            )
        )

    if args.self_test:
        issues.extend(run_self_test_checks())
        if issues:
            print("PHASE2_CLOSURE_VALIDATION_SELF_TEST=fail")
            for issue in issues:
                print(issue)
            return 1
        print("PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass")
        print("PHASE2_CLOSURE_VALIDATION_SELF_TEST_CHECK_COUNT=18")
        return 0

    if issues:
        print("PHASE2_CLOSURE_VALIDATION=fail")
        for issue in issues:
            print(issue)
        return 1

    commands = build_validation_commands()
    for command in commands:
        if run(command) != 0:
            print("PHASE2_CLOSURE_VALIDATION=fail")
            print(f"PHASE2_CLOSURE_VALIDATION_FAILED_COMMAND={' '.join(command[1:])}")
            return 1

    print("PHASE2_CLOSURE_VALIDATION=pass")
    print(f"PHASE2_CLOSURE_VALIDATION_COMMAND_COUNT={len(commands)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
