#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TOOLCHAIN_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
ARTIFACT_DIFF_DOC = ROOT / "Documentation" / "zigux" / "artifact-diff.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
MAKEFILE = ROOT / "zigux" / "Makefile"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
LEDGER = ROOT / "zigux-alpha" / "BOOTSTRAP_COMMIT_LEDGER.md"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
ARTIFACT_TOOLS_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_artifact_tools_manifest.json"
CROSS_TARGETS = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
GENKSYMS_CASES = ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "cases.json"
KCONFIG_CASES = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json"
KCONFIG_CONF_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json"

PHASE2_CROSS_ALIGNMENT_REQUIRED_SOURCE_MARKERS = [
    "PHASE2_CROSS_ALIGNMENT_SELF_TEST=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "PHASE2_CROSS_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
]

PHASE2_KCONFIG_ALIGNMENT_REQUIRED_SOURCE_MARKERS = [
    "PHASE2_KCONFIG_ALIGNMENT_SELF_TEST=python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "PHASE2_KCONFIG_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
]

PHASE2_TOOLCHAIN_PIN_SCOPE_REQUIRED_SOURCE_MARKERS = [
    "PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "PHASE2_TOOLCHAIN_PIN_SCOPE_GATE=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
]

PHASE2_TESTS_README_ALIGNMENT_REQUIRED_SOURCE_MARKERS = [
    "PHASE2_TESTS_README_ALIGNMENT_SELF_TEST=python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "PHASE2_TESTS_README_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
]

PHASE2_MAKEFILE_RUN_COUNTS = {
    "scripts/zigux/check-phase2-fixdep-gate.py --self-test": 1,
    "scripts/zigux/check-phase2-fixdep-gate.py": 1,
    "scripts/zigux/check-fixdep-diff.py --self-test": 1,
    "scripts/zigux/check-fixdep-diff.py": 1,
    "scripts/zigux/check-zig-toolchain.py": 1,
    "scripts/zigux/validate-phase2.py": 1,
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test": 1,
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py": 1,
    "scripts/zigux/validate-phase2-closure.py": 1,
    "scripts/zigux/check-phase2-tests-readme-alignment.py --self-test": 1,
    "scripts/zigux/check-phase2-tests-readme-alignment.py": 1,
    "scripts/zigux/check-phase2-tool-manifest-packets.py --self-test": 1,
    "scripts/zigux/check-phase2-tool-manifest-packets.py": 1,
    "scripts/zigux/check-phase2-cross.py --self-test": 1,
    "scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test": 1,
    "scripts/zigux/check-phase2-cross-selftest-alignment.py": 1,
    "scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test": 1,
    "scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test": 1,
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py": 1,
    "scripts/zigux/check-kconfig-bridge.py --self-test": 1,
    "scripts/zigux/check-kconfig-bridge.py": 1,
    "scripts/zigux/check-mk-elfconfig-diff.py --self-test": 1,
    "scripts/zigux/check-mk-elfconfig-diff.py": 1,
    "scripts/zigux/check-genksyms-bridge.py --self-test": 1,
    "scripts/zigux/check-genksyms-bridge.py": 1,
    "scripts/zigux/check-genksyms-crc-diff.py": 1,
    "scripts/zigux/check-phase2-cross.py": 1,
}

PHASE2_MAKEFILE_EXACT_LINES = {
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig": 1,
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig": 1,
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms_crc.zig": 1,
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig": 1,
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig": 1,
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/mk_elfconfig.zig": 1,
}

PHASE2_WORKFLOW_RUN_COUNTS = {
    "python3 scripts/zigux/install-zig.py --self-test": 1,
    "python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain": 2,
    "python3 scripts/zigux/check-zig-toolchain.py --self-test": 1,
    "python3 scripts/zigux/check-zig-toolchain.py": 1,
    "python3 scripts/zigux/validate-phase2.py": 1,
    "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-fixdep-gate.py": 1,
    "python3 scripts/zigux/check-fixdep-diff.py --self-test": 1,
    "python3 scripts/zigux/check-fixdep-diff.py": 1,
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py": 1,
    "python3 scripts/zigux/validate-phase2-closure.py": 1,
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py": 1,
    "python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-tool-manifest-packets.py": 1,
    "python3 scripts/zigux/check-phase2-cross.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}": 1,
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py": 1,
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py": 1,
    "python3 scripts/zigux/check-kconfig-bridge.py --self-test": 1,
    "python3 scripts/zigux/check-kconfig-bridge.py": 1,
    "python3 scripts/zigux/check-mk-elfconfig-diff.py --self-test": 1,
    "python3 scripts/zigux/check-mk-elfconfig-diff.py": 1,
    "python3 scripts/zigux/check-genksyms-bridge.py --self-test": 1,
    "python3 scripts/zigux/check-genksyms-bridge.py": 1,
    "python3 scripts/zigux/check-genksyms-crc-diff.py": 1,
}

PHASE2_WORKFLOW_EXACT_LINES = {
    "run: zig test scripts/zigux/fixdep.zig": 1,
    "run: zig test scripts/zigux/genksyms.zig": 1,
    "run: zig test scripts/zigux/genksyms_crc.zig": 1,
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig": 1,
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig": 1,
    "run: zig test scripts/zigux/mk_elfconfig.zig": 1,
}

PHASE2_TOOLCHAIN_NOTES_REQUIRED_MARKERS = [
    "scripts/zigux/zig-toolchain-policy.json",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
    "python3 scripts/zigux/check-zig-toolchain.py",
    "current pinned Zig channel: `0.17.0-dev.87+9b177a7d2`",
    "current minimum Zig version: `0.17.0-dev.87+9b177a7d2`",
    "x86_64-linux",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
]


def load_json_object(path: Path, *, label: str) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"{label}:expected_object")
    return payload


def required_files_for(root: Path) -> list[Path]:
    return [
        root / PHASE2_CLOSURE.relative_to(ROOT),
        root / DOCS_ROOT_README.relative_to(ROOT),
        root / REVIEW_CHECKLIST.relative_to(ROOT),
        root / TOOLCHAIN_NOTES.relative_to(ROOT),
        root / ARTIFACT_DIFF_DOC.relative_to(ROOT),
        root / SCRIPTS_README.relative_to(ROOT),
        root / MAKEFILE.relative_to(ROOT),
        root / WORKFLOW.relative_to(ROOT),
        root / LEDGER.relative_to(ROOT),
        root / TOOLCHAIN_POLICY.relative_to(ROOT),
        root / TOOL_MANIFEST.relative_to(ROOT),
        root / ARTIFACT_TOOLS_MANIFEST.relative_to(ROOT),
        root / CROSS_TARGETS.relative_to(ROOT),
        root / GENKSYMS_CASES.relative_to(ROOT),
        root / KCONFIG_CASES.relative_to(ROOT),
        root / KCONFIG_CONF_MANIFEST.relative_to(ROOT),
        root / "scripts/zigux/check-phase2-fixdep-gate.py",
        root / "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
        root / "scripts/zigux/check-genksyms-bridge.py",
        root / "scripts/zigux/check-genksyms-crc-diff.py",
        root / "scripts/zigux/check-kconfig-bridge.py",
        root / "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        root / "scripts/zigux/check-phase2-cross.py",
        root / "scripts/zigux/check-phase2-cross-selftest-alignment.py",
        root / "scripts/zigux/check-phase2-toolchain-pin-scope.py",
        root / "scripts/zigux/check-phase2-tests-readme-alignment.py",
        root / "scripts/zigux/check-phase2-tool-manifest-packets.py",
        root / "scripts/zigux/validate-phase2-closure.py",
        root / "scripts/zigux/fixdep.zig",
        root / "scripts/zigux/genksyms.zig",
        root / "scripts/zigux/genksyms_crc.zig",
        root / "scripts/zigux/mk_elfconfig.zig",
        root / "scripts/zigux/kconfig/conf_bridge.zig",
        root / "scripts/zigux/kconfig/confdata_bridge.zig",
    ]


def collect_genksyms_metadata(
    cases_payload: dict[str, object],
) -> tuple[list[Path], list[str], list[str], list[str], list[str], list[str]]:
    cases = cases_payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise SystemExit("genksyms_cases:cases:expected_nonempty_list")

    expected_files: list[Path] = []
    case_names: list[str] = []
    stdout_packet: list[str] = []
    process_packet: list[str] = []
    normalized_stderr_packet: list[str] = []
    seen_expected: set[str] = set()

    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise SystemExit(f"genksyms_cases:cases[{index}]:expected_object")
        name = case.get("name")
        expected = case.get("expected")
        if not isinstance(name, str) or not name:
            raise SystemExit(f"genksyms_cases:cases[{index}]:name:expected_nonempty_string")
        if not isinstance(expected, str) or not expected:
            raise SystemExit(f"genksyms_cases:{name}:expected:expected_nonempty_string")
        if expected in seen_expected:
            raise SystemExit(f"genksyms_cases:{name}:expected:duplicate_reference:{expected}")
        seen_expected.add(expected)
        case_names.append(name)
        expected_files.append(GENKSYMS_CASES.parent / expected)
        if case.get("mode") == "process_json":
            process_packet.append(expected)
            if case.get("normalize_stderr") is True:
                normalized_stderr_packet.append(expected)
        else:
            stdout_packet.append(expected)

    return (
        expected_files,
        case_names,
        stdout_packet,
        process_packet,
        normalized_stderr_packet,
        ["abbreviated_help", "abbreviated_version"],
    )


def collect_confdata_metadata(
    cases_payload: dict[str, object],
) -> tuple[list[Path], list[str], list[str]]:
    cases = cases_payload.get("confdata_cases")
    if not isinstance(cases, list) or not cases:
        raise SystemExit("kconfig_bridge_cases:confdata_cases:expected_nonempty_list")

    discovered_files: list[Path] = []
    case_names: list[str] = []
    expected_packet: list[str] = []
    seen_paths: set[Path] = set()

    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise SystemExit(f"kconfig_bridge_cases:confdata_cases[{index}]:expected_object")
        name = case.get("name")
        if not isinstance(name, str) or not name:
            raise SystemExit(
                f"kconfig_bridge_cases:confdata_cases[{index}]:name:expected_nonempty_string"
            )
        case_names.append(name)
        for field_name in ("input", "expected"):
            rel_path = case.get(field_name)
            if not isinstance(rel_path, str) or not rel_path:
                raise SystemExit(
                    f"kconfig_bridge_cases:{name}:{field_name}:expected_nonempty_string"
                )
            discovered_path = KCONFIG_CASES.parent / rel_path
            if discovered_path not in seen_paths:
                seen_paths.add(discovered_path)
                discovered_files.append(discovered_path)
            if field_name == "expected":
                expected_packet.append(rel_path)

    return discovered_files, case_names, expected_packet


def require_markers(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def validate_exact_runs(
    text: str,
    *,
    prefix: str,
    counted_runs: dict[str, int],
    exact_lines: dict[str, int],
    line_prefix: str = "",
) -> list[str]:
    issues: list[str] = []
    lines = [line.strip() for line in text.splitlines()]

    for command, expected_count in counted_runs.items():
        expected_line = f"{line_prefix}{command}"
        count = sum(1 for line in lines if line == expected_line)
        if count != expected_count:
            issues.append(f"{prefix}_exact_run:{command}:count={count}:expected={expected_count}")

    for expected_line, expected_count in exact_lines.items():
        count = sum(1 for line in lines if line == expected_line)
        if count != expected_count:
            issues.append(f"{prefix}_exact_line:{expected_line}:count={count}:expected={expected_count}")

    return issues


def build_required_closure_markers(
    *,
    genksyms_case_names: list[str],
    genksyms_stdout_packet: list[str],
    genksyms_process_packet: list[str],
    genksyms_normalized_stderr_packet: list[str],
    genksyms_action_abbrev_cases: list[str],
    conf_case_names: list[str],
    conf_stdout_packet: list[str],
    confdata_case_names: list[str],
    confdata_expected_packet: list[str],
) -> list[str]:
    markers = [
        "PHASE2_STATUS=closed",
        "PHASE2_TOOL_COUNT=6",
        "PHASE2_CROSS_TARGET_COUNT=3",
        "PHASE2_FIXDEP_SELF_TEST=python3 scripts/zigux/check-fixdep-diff.py --self-test",
        "PHASE2_FIXDEP_GATE_SELF_TEST=python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
        "PHASE2_FIXDEP_GATE=python3 scripts/zigux/check-phase2-fixdep-gate.py",
        "PHASE2_GENKSYMS_BRIDGE_GATE=python3 scripts/zigux/check-genksyms-bridge.py",
        "PHASE2_KCONFIG_BRIDGE_GATE=python3 scripts/zigux/check-kconfig-bridge.py",
        "PHASE2_CROSS_SELF_TEST=python3 scripts/zigux/check-phase2-cross.py --self-test",
        "PHASE2_CROSS_GATE=python3 scripts/zigux/check-phase2-cross.py",
        "PHASE2_CROSS_MANIFEST_POLICY=check-phase2-cross.py rejects duplicate tool entries, duplicate requested targets, unexpected explicit targets, duplicate manifest targets, and manifest-count drift before live compile replay",
        "PHASE2_TOOLCHAIN_PIN_SCOPE_POLICY=scripts/zigux/zig-toolchain-policy.json",
        "scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
        "scripts/zigux/check-phase2-toolchain-pin-scope.py",
        "x86_64-linux",
        "PHASE2_CLOSURE_GATE=python3 scripts/zigux/validate-phase2-closure.py",
        "PHASE2_FIXDEP_EMBEDDED_NUL_GUARD=fixdep.zig truncates depfile parsing at the first embedded NUL and keeps dep parsing skips bytes after the first embedded NUL as the bounded parser guard",
        "PHASE2_TOOL_MANIFEST_PACKET_SELF_TEST=python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test",
        "PHASE2_TOOL_MANIFEST_PACKET_GATE=python3 scripts/zigux/check-phase2-tool-manifest-packets.py",
        "PHASE2_ARTIFACT_TOOLS_PACKET=zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
        f"PHASE2_GENKSYMS_BRIDGE_CASE_COUNT={len(genksyms_case_names)}",
        "PHASE2_GENKSYMS_BRIDGE_CASES=" + ",".join(genksyms_case_names),
        "PHASE2_GENKSYMS_BRIDGE_STDOUT_PACKET=" + ",".join(genksyms_stdout_packet),
        "PHASE2_GENKSYMS_BRIDGE_PROCESS_PACKET=" + ",".join(genksyms_process_packet),
        "PHASE2_GENKSYMS_BRIDGE_NORMALIZED_STDERR_PACKET="
        + ",".join(genksyms_normalized_stderr_packet),
        "PHASE2_GENKSYMS_BRIDGE_ACTION_ABBREV_CASES="
        + ",".join(genksyms_action_abbrev_cases),
        f"PHASE2_KCONFIG_BRIDGE_CONF_CASE_COUNT={len(conf_case_names)}",
        "PHASE2_KCONFIG_BRIDGE_CONF_CASES=" + ",".join(conf_case_names),
        "PHASE2_KCONFIG_BRIDGE_CONF_STDOUT_PACKET=" + ",".join(conf_stdout_packet),
        "PHASE2_KCONFIG_BRIDGE_ALLCONFIG_SENTINEL_PACKET=allnoconfig_expected.json,allyesconfig_expected.json,alldefconfig_expected.json",
        "request-plan coverage stays anchored by the oldaskconfig baseline, syncconfig auto-output env injection, oldconfig refresh path, allnoconfig and allyesconfig mode selection, alldefconfig mode selection, allmodconfig explicit empty allconfig override forwarding, randconfig seed and probability forwarding, yes2modconfig/mod2yesconfig/mod2noconfig mode selection, defconfig/savedefconfig mode-argument ordering, and listnewconfig/helpnewconfig request-plan fixtures in `zigux/tests/fixtures/kconfig_bridge/`",
        "allconfig coverage stays anchored by `allnoconfig_expected.json`, `allyesconfig_expected.json`, `alldefconfig_expected.json`, `allmodconfig_expected.json`, and `randconfig_expected.json`, which keep the bounded sentinel packet plus the explicit empty and named allconfig override packets reviewable",
        "conf bridge emits syncconfig auto files",
        "conf bridge emits alldefconfig argv and env",
        "conf bridge emits explicit empty allconfig override for allmodconfig",
        "conf bridge emits randconfig tunables when present",
        "conf bridge emits yes2modconfig argv and env",
        "conf bridge emits defconfig mode argument before kconfig",
        "conf bridge emits savedefconfig mode argument before kconfig",
        "conf bridge escapes low control bytes in JSON strings",
        "PHASE2_ROLLBACK=keep C kbuild tools authoritative and remove failing Zigux bridge/tool from workflow wiring",
        f"PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT={len(confdata_case_names)}",
        "PHASE2_KCONFIG_BRIDGE_CONFDATA_CASES=" + ",".join(confdata_case_names),
        "PHASE2_KCONFIG_BRIDGE_CONFDATA_EXPECTED_PACKET="
        + ",".join(confdata_expected_packet),
        "confdata bridge decodes escaped quoted strings",
        "confdata bridge strips backslashes from escaped control sequences like upstream confdata",
        "confdata bridge keeps trailing escaped backslashes in quoted strings",
        "confdata bridge accepts CRLF config lines",
        "confdata bridge preserves trailing carriage return on final unterminated value line",
        "confdata bridge ignores unterminated unset comment with trailing carriage return",
        "confdata bridge keeps explicit n assignments as tristate values",
        "confdata bridge recognizes uppercase tristate assignments",
        "confdata bridge ignores non-CONFIG lines like upstream confdata",
        "PHASE2_FIXDEP_CASE_COUNT=7",
        "PHASE2_FIXDEP_CASES=sample,sample_escaped_space,sample_escaped_colon,sample_multi_target,sample_comment_only,sample_missing_dep,sample_escaped_hash_comment_chain",
        "PHASE2_FIXDEP_STDOUT_PACKET=sample_expected.txt,sample_escaped_space_expected.txt,sample_escaped_colon_expected.txt,sample_multi_target_expected.txt,sample_comment_only_expected.txt,sample_missing_dep_expected.txt,sample_escaped_hash_comment_chain_expected.txt",
    ]
    markers.extend(PHASE2_CROSS_ALIGNMENT_REQUIRED_SOURCE_MARKERS)
    markers.extend(PHASE2_KCONFIG_ALIGNMENT_REQUIRED_SOURCE_MARKERS)
    markers.extend(PHASE2_TOOLCHAIN_PIN_SCOPE_REQUIRED_SOURCE_MARKERS)
    markers.extend(PHASE2_TESTS_README_ALIGNMENT_REQUIRED_SOURCE_MARKERS)
    return markers


def main_validation(root: Path) -> list[str]:
    missing = [str(path.relative_to(root)) for path in required_files_for(root) if not path.exists()]
    if missing:
        return [f"missing_file:{item}" for item in missing]

    genksyms_cases_payload = load_json_object(root / GENKSYMS_CASES.relative_to(ROOT), label="genksyms_cases")
    (
        genksyms_expected_files,
        genksyms_case_names,
        genksyms_stdout_packet,
        genksyms_process_packet,
        genksyms_normalized_stderr_packet,
        genksyms_action_abbrev_cases,
    ) = collect_genksyms_metadata(genksyms_cases_payload)

    kconfig_cases_payload = load_json_object(root / KCONFIG_CASES.relative_to(ROOT), label="kconfig_cases")
    confdata_case_files, confdata_case_names, confdata_expected_packet = collect_confdata_metadata(kconfig_cases_payload)
    conf_manifest = load_json_object(root / KCONFIG_CONF_MANIFEST.relative_to(ROOT), label="kconfig_conf_manifest")
    conf_case_names = conf_manifest.get("cases", [])
    conf_stdout_packet = conf_manifest.get("stdout_packet", [])
    if not isinstance(conf_case_names, list) or not all(isinstance(item, str) for item in conf_case_names):
        return ["kconfig_conf_manifest:cases:expected_string_list"]
    if not isinstance(conf_stdout_packet, list) or not all(isinstance(item, str) for item in conf_stdout_packet):
        return ["kconfig_conf_manifest:stdout_packet:expected_string_list"]

    dynamic_files = genksyms_expected_files + confdata_case_files
    dynamic_missing = [str(path.relative_to(root)) for path in dynamic_files if not path.exists()]
    if dynamic_missing:
        return [f"missing_file:{item}" for item in dynamic_missing]

    closure = (root / PHASE2_CLOSURE.relative_to(ROOT)).read_text(encoding="utf-8")
    workflow = (root / WORKFLOW.relative_to(ROOT)).read_text(encoding="utf-8")
    ledger = (root / LEDGER.relative_to(ROOT)).read_text(encoding="utf-8")
    script_readme = (root / SCRIPTS_README.relative_to(ROOT)).read_text(encoding="utf-8")
    artifact_doc = (root / ARTIFACT_DIFF_DOC.relative_to(ROOT)).read_text(encoding="utf-8")
    toolchain_notes = (root / TOOLCHAIN_NOTES.relative_to(ROOT)).read_text(encoding="utf-8")
    makefile = (root / MAKEFILE.relative_to(ROOT)).read_text(encoding="utf-8")
    tool_manifest = load_json_object(root / TOOL_MANIFEST.relative_to(ROOT), label="phase2_tool_manifest")
    artifact_tools_manifest = load_json_object(
        root / ARTIFACT_TOOLS_MANIFEST.relative_to(ROOT), label="phase2_artifact_tools_manifest"
    )
    targets_manifest = load_json_object(root / CROSS_TARGETS.relative_to(ROOT), label="phase2_cross_targets")

    required_closure_markers = build_required_closure_markers(
        genksyms_case_names=genksyms_case_names,
        genksyms_stdout_packet=genksyms_stdout_packet,
        genksyms_process_packet=genksyms_process_packet,
        genksyms_normalized_stderr_packet=genksyms_normalized_stderr_packet,
        genksyms_action_abbrev_cases=genksyms_action_abbrev_cases,
        conf_case_names=conf_case_names,
        conf_stdout_packet=conf_stdout_packet,
        confdata_case_names=confdata_case_names,
        confdata_expected_packet=confdata_expected_packet,
    )

    required_workflow_markers = [
        "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
        "python3 scripts/zigux/check-phase2-fixdep-gate.py",
        "python3 scripts/zigux/check-fixdep-diff.py --self-test",
        "python3 scripts/zigux/check-fixdep-diff.py",
        "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
        "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
        "python3 scripts/zigux/check-genksyms-bridge.py --self-test",
        "python3 scripts/zigux/check-genksyms-bridge.py",
        "python3 scripts/zigux/check-genksyms-crc-diff.py",
        "python3 scripts/zigux/check-kconfig-bridge.py --self-test",
        "python3 scripts/zigux/check-kconfig-bridge.py",
        "python3 scripts/zigux/check-mk-elfconfig-diff.py --self-test",
        "python3 scripts/zigux/check-mk-elfconfig-diff.py",
        "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
        "python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
        "python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test",
        "python3 scripts/zigux/check-phase2-tool-manifest-packets.py",
        "python3 scripts/zigux/check-phase2-cross.py --self-test",
        "python3 scripts/zigux/check-phase2-cross.py --target",
        "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
        "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "python3 scripts/zigux/check-zig-toolchain.py --self-test",
        "python3 scripts/zigux/check-zig-toolchain.py",
        "python3 scripts/zigux/install-zig.py --self-test",
        "python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain",
        "python3 scripts/zigux/validate-phase2-closure.py",
        "zig test scripts/zigux/fixdep.zig",
        "zig test scripts/zigux/genksyms.zig",
        "zig test scripts/zigux/genksyms_crc.zig",
        "zig test scripts/zigux/kconfig/conf_bridge.zig",
        "zig test scripts/zigux/kconfig/confdata_bridge.zig",
        "zig test scripts/zigux/mk_elfconfig.zig",
    ]

    required_ledger_markers = [
        "feat(scripts/zigux): add bounded Phase 2 genksyms wrapper lane",
        "ci(zigux): widen Phase 2 closure matrix",
        "docs(zigux): reopen and close broadened Phase 2 tranche",
        "feat(scripts/zigux): add bounded Phase 2 kconfig bridge scaffolding",
        "ci(zigux): add Phase 2 cross-arch build matrix",
        "docs(zigux): close bounded Phase 2 toolchain tranche",
    ]

    required_readme_markers = [
        "check-genksyms-bridge.py",
        "check-kconfig-bridge.py",
        "check-phase2-cross.py",
        "genksyms.zig",
        "kconfig/conf_bridge.zig",
        "kconfig/confdata_bridge.zig",
    ]

    required_doc_markers = ["genksyms_bridge", "kconfig_bridge", "phase2_cross_targets.json"]

    required_makefile_markers = [
        "phase2-toolchain:",
        "phase2-validate: phase2-toolchain",
        "phase2-kconfig:",
        "phase2-cross:",
        "check-zig-toolchain.py",
        "check-phase2-tests-readme-alignment.py --self-test",
        "check-phase2-tests-readme-alignment.py",
        "check-phase2-tool-manifest-packets.py",
        "check-phase2-cross-selftest-alignment.py --self-test",
        "check-phase2-cross-selftest-alignment.py",
        "check-phase2-toolchain-pin-scope.py --self-test",
        "check-phase2-toolchain-pin-scope.py",
        "check-phase2-kconfig-selftest-alignment.py --self-test",
        "check-phase2-kconfig-selftest-alignment.py",
        "check-kconfig-bridge.py --self-test",
        "check-kconfig-bridge.py",
        "check-mk-elfconfig-diff.py --self-test",
        "check-mk-elfconfig-diff.py",
        "check-genksyms-bridge.py --self-test",
        "check-genksyms-bridge.py",
        "check-genksyms-crc-diff.py",
    ]

    issues: list[str] = []
    issues.extend(require_markers(closure, required_closure_markers, "closure"))
    issues.extend(require_markers(workflow, required_workflow_markers, "workflow"))
    issues.extend(require_markers(ledger, required_ledger_markers, "ledger"))
    issues.extend(require_markers(script_readme, required_readme_markers, "scripts"))
    issues.extend(require_markers(artifact_doc, required_doc_markers, "doc"))
    issues.extend(require_markers(toolchain_notes, PHASE2_TOOLCHAIN_NOTES_REQUIRED_MARKERS, "toolchain_notes"))
    issues.extend(require_markers(makefile, required_makefile_markers, "make"))

    issues.extend(
        validate_exact_runs(
            makefile,
            prefix="make",
            counted_runs=PHASE2_MAKEFILE_RUN_COUNTS,
            exact_lines=PHASE2_MAKEFILE_EXACT_LINES,
            line_prefix="cd $(ZIGUX_ROOT) && $(PYTHON) ",
        )
    )
    issues.extend(
        validate_exact_runs(
            workflow,
            prefix="workflow",
            counted_runs=PHASE2_WORKFLOW_RUN_COUNTS,
            exact_lines=PHASE2_WORKFLOW_EXACT_LINES,
            line_prefix="run: ",
        )
    )

    if tool_manifest.get("phase") != "Phase 2":
        issues.append("manifest:phase=Phase 2")
    if tool_manifest.get("status") != "closed":
        issues.append("manifest:status=closed")
    if tool_manifest.get("tool_count") != 6:
        issues.append("manifest:tool_count=6")
    if len(tool_manifest.get("tools", [])) != 6:
        issues.append(f"manifest:tools_len={len(tool_manifest.get('tools', []))}")

    if artifact_tools_manifest.get("phase") != "Phase 2":
        issues.append("artifact_tools_manifest:phase=Phase 2")
    if artifact_tools_manifest.get("status") != "closed":
        issues.append("artifact_tools_manifest:status=closed")
    if artifact_tools_manifest.get("tool_count") != 2:
        issues.append("artifact_tools_manifest:tool_count=2")

    if targets_manifest.get("phase") != "Phase 2":
        issues.append("targets:phase=Phase 2")
    if targets_manifest.get("status") != "closed":
        issues.append("targets:status=closed")
    if targets_manifest.get("target_count") != 3:
        issues.append("targets:target_count=3")
    if len(targets_manifest.get("targets", [])) != 3:
        issues.append(f"targets:len={len(targets_manifest.get('targets', []))}")

    return issues


def run_self_test() -> int:
    cases_run = 0

    sample_cases = {
        "cases": [
            {"name": "minimal", "expected": "minimal_expected.json"},
            {"name": "process", "mode": "process_json", "expected": "process_expected.json"},
            {
                "name": "normalized",
                "mode": "process_json",
                "normalize_stderr": True,
                "expected": "normalized_expected.json",
            },
        ]
    }
    (
        expected_files,
        case_names,
        stdout_packet,
        process_packet,
        normalized_packet,
        action_abbrev_cases,
    ) = collect_genksyms_metadata(sample_cases)
    assert len(expected_files) == 3
    assert case_names == ["minimal", "process", "normalized"]
    assert stdout_packet == ["minimal_expected.json"]
    assert process_packet == ["process_expected.json", "normalized_expected.json"]
    assert normalized_packet == ["normalized_expected.json"]
    assert action_abbrev_cases == ["abbreviated_help", "abbreviated_version"]
    cases_run += 1

    sample_confdata_cases = {
        "confdata_cases": [
            {"name": "sample", "input": "sample.config", "expected": "sample_expected.json"},
            {"name": "tail", "input": "tail.config", "expected": "tail_expected.json"},
        ]
    }
    conf_files, conf_names, conf_expected = collect_confdata_metadata(sample_confdata_cases)
    assert len(conf_files) == 4
    assert conf_names == ["sample", "tail"]
    assert conf_expected == ["sample_expected.json", "tail_expected.json"]
    cases_run += 1

    duplicate_make = "\n".join(
        [
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-crc-diff.py",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-crc-diff.py",
            "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/mk_elfconfig.zig",
        ]
    )
    issues = validate_exact_runs(
        duplicate_make,
        prefix="make",
        counted_runs={"scripts/zigux/check-genksyms-crc-diff.py": 1},
        exact_lines={"cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/mk_elfconfig.zig": 1},
        line_prefix="cd $(ZIGUX_ROOT) && $(PYTHON) ",
    )
    assert "make_exact_run:scripts/zigux/check-genksyms-crc-diff.py:count=2:expected=1" in issues
    cases_run += 1

    with tempfile.TemporaryDirectory(prefix="phase2_toolchain_notes_") as tmp_dir:
        notes = Path(tmp_dir) / "notes.md"
        notes.write_text(
            "\n".join(
                [
                    "- policy file: `scripts/zigux/zig-toolchain-policy.json`",
                    "- guard self-test: `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
                    "- guard: `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`",
                    "- shared tests README alignment self-test: `python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test`",
                    "- shared tests README alignment gate: `python3 scripts/zigux/check-phase2-tests-readme-alignment.py`",
                    "- workflow install path: `python3 scripts/zigux/install-zig.py --dest .zig-toolchain`",
                    "- workflow verification path: `python3 scripts/zigux/check-zig-toolchain.py`",
                    "- current pinned Zig channel: `0.17.0-dev.87+9b177a7d2`",
                    "- current minimum Zig version: `0.17.0-dev.87+9b177a7d2`",
                    "- current pinned bootstrap archive target: `x86_64-linux`",
                    "- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keeps the committed `genksyms_crc` plus `mk_elfconfig` fixture packet explicit beside `zigux/tests/fixtures/phase2_tool_manifest.json`, so the artifact-backed half of the bounded Phase 2 tool-manifest surface stays reviewable from this bootstrap note instead of being folded into the aggregate packet name alone",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        assert require_markers(notes.read_text(encoding="utf-8"), PHASE2_TOOLCHAIN_NOTES_REQUIRED_MARKERS, "toolchain_notes") == []
    cases_run += 1

    with tempfile.TemporaryDirectory(prefix="phase2_toolchain_notes_missing_artifact_") as tmp_dir:
        notes = Path(tmp_dir) / "notes.md"
        notes.write_text(
            "\n".join(
                [
                    "- policy file: `scripts/zigux/zig-toolchain-policy.json`",
                    "- guard self-test: `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
                    "- guard: `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`",
                    "- shared tests README alignment self-test: `python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test`",
                    "- shared tests README alignment gate: `python3 scripts/zigux/check-phase2-tests-readme-alignment.py`",
                    "- workflow install path: `python3 scripts/zigux/install-zig.py --dest .zig-toolchain`",
                    "- workflow verification path: `python3 scripts/zigux/check-zig-toolchain.py`",
                    "- current pinned Zig channel: `0.17.0-dev.87+9b177a7d2`",
                    "- current minimum Zig version: `0.17.0-dev.87+9b177a7d2`",
                    "- current pinned bootstrap archive target: `x86_64-linux`",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        issues = require_markers(
            notes.read_text(encoding="utf-8"),
            PHASE2_TOOLCHAIN_NOTES_REQUIRED_MARKERS,
            "toolchain_notes",
        )
        assert (
            "toolchain_notes:zigux/tests/fixtures/phase2_artifact_tools_manifest.json"
            in issues
        )
    cases_run += 1

    print("PHASE2_CLOSURE_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_SELF_TEST_CASE_COUNT={cases_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 2 closure packet.")
    parser.add_argument("--self-test", action="store_true", help="Run checkout-free validator self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = [str(path.relative_to(ROOT)) for path in required_files_for(ROOT) if not path.exists()]
    if missing:
        print("PHASE2_CLOSURE_VALIDATION=fail")
        print("MISSING_PHASE2_CLOSURE_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE2_CLOSURE_FILES_END")
        return 1

    issues = main_validation(ROOT)
    if issues:
        print("PHASE2_CLOSURE_VALIDATION=fail")
        print("MISSING_PHASE2_CLOSURE_MARKERS_START")
        for issue in issues:
            print(issue)
        print("MISSING_PHASE2_CLOSURE_MARKERS_END")
        return 1

    genksyms_cases_payload = load_json_object(GENKSYMS_CASES, label="genksyms_cases")
    genksyms_expected_files, *_ = collect_genksyms_metadata(genksyms_cases_payload)
    kconfig_cases_payload = load_json_object(KCONFIG_CASES, label="kconfig_cases")
    confdata_case_files, _, _ = collect_confdata_metadata(kconfig_cases_payload)

    print("PHASE2_CLOSURE_VALIDATION=pass")
    print(
        "PHASE2_CLOSURE_REQUIRED_FILE_COUNT="
        f"{len(required_files_for(ROOT)) + len(genksyms_expected_files) + len(confdata_case_files)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
