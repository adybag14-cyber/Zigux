#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent
CHECK_PHASE2_CROSS_SELFTEST_ALIGNMENT = ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"
CHECK_PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT = (
    ROOT / "scripts" / "zigux" / "check-phase2-genksyms-bridge-selftest-alignment.py"
)
CHECK_PHASE2_KCONFIG_SELFTEST_ALIGNMENT = (
    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py"
)
CHECK_PHASE2_TOOLCHAIN_PIN_SCOPE = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"
CHECK_PHASE2_TESTS_README_ALIGNMENT = ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TOOLCHAIN_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
GENKSYMS_CASES = ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "cases.json"
KCONFIG_BRIDGE_CASES = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json"

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
    "PHASE2_TESTS_README_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
]

PHASE2_MAKEFILE_RUN_COUNTS = {
    "scripts/zigux/check-fixdep-diff.py --self-test": 1,
    "scripts/zigux/check-fixdep-diff.py": 1,
    "scripts/zigux/check-zig-toolchain.py": 1,
    "scripts/zigux/validate-phase2.py": 1,
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test": 1,
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py": 1,
    "scripts/zigux/validate-phase2-closure.py": 1,
    "scripts/zigux/check-phase2-tests-readme-alignment.py": 1,
    "scripts/zigux/check-phase2-cross.py --self-test": 1,
    "scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test": 1,
    "scripts/zigux/check-phase2-cross-selftest-alignment.py": 1,
    "scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test": 1,
    "scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test": 1,
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py": 1,
    "scripts/zigux/check-kconfig-bridge.py --self-test": 1,
    "scripts/zigux/check-kconfig-bridge.py": 1,
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
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py": 1,
    "python3 scripts/zigux/validate-phase2-closure.py": 1,
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py": 1,
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


def required_files_for(root: Path) -> list[Path]:
    return [
        root / "Documentation" / "zigux" / "phase2-closure.md",
        root / "Documentation" / "zigux" / "README.md",
        root / "Documentation" / "zigux" / "review-checklist.md",
        root / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md",
        root / "scripts" / "zigux" / "check-phase2-genksyms-bridge-selftest-alignment.py",
        root / "scripts" / "zigux" / "check-genksyms-bridge.py",
        root / "scripts" / "zigux" / "check-genksyms-crc-diff.py",
        root / "scripts" / "zigux" / "check-kconfig-bridge.py",
        root / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py",
        root / "scripts" / "zigux" / "check-phase2-cross.py",
        root / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py",
        root / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py",
        root / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py",
        root / "scripts" / "zigux" / "validate-phase2-closure.py",
        root / "scripts" / "zigux" / "fixdep.zig",
        root / "scripts" / "zigux" / "genksyms.zig",
        root / "scripts" / "zigux" / "genksyms_crc.zig",
        root / "scripts" / "zigux" / "mk_elfconfig.zig",
        root / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig",
        root / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig",
        root / "zigux" / "Makefile",
        root / "scripts" / "zigux" / "zig-toolchain-policy.json",
        root / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "cases.json",
        root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json",
        root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "alldefconfig_expected.json",
        root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "olddefconfig_expected.json",
        root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "syncconfig_expected.json",
        root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "allmodconfig_expected.json",
        root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "yes2modconfig_expected.json",
        root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "defconfig_expected.json",
        root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "savedefconfig_expected.json",
        root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "listnewconfig_expected.json",
        root / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json",
        root / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json",
    ]


def load_json_object(path: Path, *, label: str) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"{label}:expected_object")
    return payload


def collect_genksyms_expected_files(cases_payload: dict[str, object]) -> tuple[list[Path], list[str]]:
    issues: list[str] = []
    cases = cases_payload.get("cases")
    if not isinstance(cases, list):
        return [], ["genksyms_cases:cases:expected_list"]
    if not cases:
        return [], ["genksyms_cases:cases:empty"]

    expected_files: list[Path] = []
    seen_expected: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            issues.append(f"genksyms_cases:cases[{index}]:expected_object")
            continue
        name = case.get("name")
        if not isinstance(name, str) or not name:
            issues.append(f"genksyms_cases:cases[{index}]:name:expected_nonempty_string")
            continue
        expected = case.get("expected")
        if not isinstance(expected, str) or not expected:
            issues.append(f"genksyms_cases:{name}:expected:expected_nonempty_string")
            continue
        if expected in seen_expected:
            issues.append(f"genksyms_cases:{name}:expected:duplicate_reference:{expected}")
            continue
        seen_expected.add(expected)
        expected_files.append(GENKSYMS_CASES.parent / expected)
    return expected_files, issues


def collect_confdata_case_metadata(
    cases_payload: dict[str, object],
) -> tuple[list[Path], list[str], list[str], list[str]]:
    issues: list[str] = []
    cases = cases_payload.get("confdata_cases")
    if not isinstance(cases, list):
        return [], [], [], ["kconfig_bridge_cases:confdata_cases:expected_list"]
    if not cases:
        return [], [], [], ["kconfig_bridge_cases:confdata_cases:empty"]

    discovered_files: list[Path] = []
    case_names: list[str] = []
    expected_packet: list[str] = []
    seen_paths: set[Path] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            issues.append(f"kconfig_bridge_cases:confdata_cases[{index}]:expected_object")
            continue
        name = case.get("name")
        if not isinstance(name, str) or not name:
            issues.append(
                f"kconfig_bridge_cases:confdata_cases[{index}]:name:expected_nonempty_string"
            )
            continue
        case_names.append(name)
        expected_rel_path: str | None = None
        for field_name in ("input", "expected"):
            rel_path = case.get(field_name)
            if not isinstance(rel_path, str) or not rel_path:
                issues.append(
                    f"kconfig_bridge_cases:{name}:{field_name}:expected_nonempty_string"
                )
                continue
            if field_name == "expected":
                expected_rel_path = rel_path
            discovered_path = KCONFIG_BRIDGE_CASES.parent / rel_path
            if discovered_path in seen_paths:
                continue
            seen_paths.add(discovered_path)
            discovered_files.append(discovered_path)
        if expected_rel_path is not None:
            expected_packet.append(expected_rel_path)
    return discovered_files, case_names, expected_packet, issues


def validate_exact_makefile_runs(text: str) -> list[str]:
    issues: list[str] = []
    lines = [line.strip() for line in text.splitlines()]
    for command, expected_count in PHASE2_MAKEFILE_RUN_COUNTS.items():
        expected_line = f"cd $(ZIGUX_ROOT) && $(PYTHON) {command}"
        count = sum(1 for line in lines if line == expected_line)
        if count != expected_count:
            issues.append(f"make_exact_run:{command}:count={count}:expected={expected_count}")
    for expected_line, expected_count in PHASE2_MAKEFILE_EXACT_LINES.items():
        count = sum(1 for line in lines if line == expected_line)
        if count != expected_count:
            issues.append(f"make_exact_line:{expected_line}:count={count}:expected={expected_count}")
    return issues


def validate_exact_workflow_runs(text: str) -> list[str]:
    issues: list[str] = []
    lines = [line.strip() for line in text.splitlines()]
    for command, expected_count in PHASE2_WORKFLOW_RUN_COUNTS.items():
        expected_line = f"run: {command}"
        count = sum(1 for line in lines if line == expected_line)
        if count != expected_count:
            issues.append(
                f"workflow_exact_run:{command}:count={count}:expected={expected_count}"
            )
    for expected_line, expected_count in PHASE2_WORKFLOW_EXACT_LINES.items():
        count = sum(1 for line in lines if line == expected_line)
        if count != expected_count:
            issues.append(
                f"workflow_exact_line:{expected_line}:count={count}:expected={expected_count}"
            )
    return issues


def make_ok_text() -> str:
    return "\n".join(
        [
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-mk-elfconfig-diff.py",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-crc-diff.py",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
            "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
            "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
            "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms_crc.zig",
            "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
            "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
            "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/mk_elfconfig.zig",
        ]
    )


def workflow_ok_text() -> str:
    return (
        "\n".join(
            [
                "run: python3 scripts/zigux/install-zig.py --self-test",
                "run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain",
                "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
                "run: python3 scripts/zigux/check-zig-toolchain.py",
                "run: python3 scripts/zigux/validate-phase2.py",
                "run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
                "run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
                "run: python3 scripts/zigux/validate-phase2-closure.py",
                "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
                "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
                "run: python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}",
                "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
                "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
                "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
                "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
                "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
                "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
                "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
                "run: python3 scripts/zigux/check-kconfig-bridge.py",
                "run: python3 scripts/zigux/check-mk-elfconfig-diff.py",
                "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
                "run: python3 scripts/zigux/check-genksyms-bridge.py",
                "run: python3 scripts/zigux/check-genksyms-crc-diff.py",
                "run: zig test scripts/zigux/fixdep.zig",
                "run: zig test scripts/zigux/genksyms.zig",
                "run: zig test scripts/zigux/genksyms_crc.zig",
                "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
                "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
                "run: zig test scripts/zigux/mk_elfconfig.zig",
                "run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain",
            ]
        )
        + "\n"
    )


def require_marker(text: str, marker: str, bucket: list[str], prefix: str) -> None:
    if marker not in text:
        bucket.append(f"{prefix}:{marker}")


def main_validation(root: Path) -> list[str]:
    required_files = required_files_for(root)
    missing = [str(path.relative_to(root)) for path in required_files if not path.exists()]
    if missing:
        return [f"missing_file:{item}" for item in missing]

    genksyms_cases_payload = load_json_object(
        root / GENKSYMS_CASES.relative_to(ROOT), label="genksyms_cases"
    )
    genksyms_expected_files, genksyms_case_issues = collect_genksyms_expected_files(
        genksyms_cases_payload
    )
    kconfig_cases_payload = load_json_object(
        root / KCONFIG_BRIDGE_CASES.relative_to(ROOT), label="kconfig_bridge_cases"
    )
    (
        confdata_case_files,
        confdata_case_names,
        confdata_expected_packet,
        confdata_case_issues,
    ) = collect_confdata_case_metadata(kconfig_cases_payload)
    if genksyms_case_issues:
        return genksyms_case_issues
    if confdata_case_issues:
        return confdata_case_issues
    for rel_path in genksyms_expected_files + confdata_case_files:
        abs_path = root / rel_path.relative_to(ROOT)
        if not abs_path.exists():
            return [f"missing_file:{abs_path.relative_to(root)}"]

    closure = (root / "Documentation/zigux/phase2-closure.md").read_text(encoding="utf-8")
    workflow = (root / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
    ledger = (root / "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md").read_text(encoding="utf-8")
    script_readme = (root / "scripts/zigux/README.md").read_text(encoding="utf-8")
    artifact_doc = (root / "Documentation" / "zigux" / "artifact-diff.md").read_text(encoding="utf-8")
    makefile = (root / "zigux/Makefile").read_text(encoding="utf-8")
    tool_manifest = json.loads(
        (root / "zigux/tests/fixtures/phase2_tool_manifest.json").read_text(encoding="utf-8")
    )
    targets_manifest = json.loads(
        (root / "zigux/tests/fixtures/phase2_cross_targets.json").read_text(encoding="utf-8")
    )

    required_closure_markers = [
        "PHASE2_STATUS=closed",
        "PHASE2_TOOL_COUNT=6",
        "PHASE2_CROSS_TARGET_COUNT=3",
        "PHASE2_FIXDEP_SELF_TEST=python3 scripts/zigux/check-fixdep-diff.py --self-test",
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
        "PHASE2_GENKSYMS_BRIDGE_CASE_COUNT=16",
        "PHASE2_GENKSYMS_BRIDGE_CASES=minimal,debug_reference_types,long_options,abbreviated_long_options,quiet_overrides_warning,explicit_option_terminator,positional_passthrough,help,abbreviated_help,version,abbreviated_version,invalid_option,missing_reference_argument,unsupported_long_option,missing_long_reference_argument,missing_long_dump_types_argument",
        "PHASE2_GENKSYMS_BRIDGE_STDOUT_PACKET=minimal_expected.json,debug_reference_types_expected.json,long_options_expected.json,abbreviated_long_options_expected.json,quiet_overrides_warning_expected.json,explicit_option_terminator_expected.json,positional_passthrough_expected.json",
        "PHASE2_GENKSYMS_BRIDGE_PROCESS_PACKET=help_expected.json,version_expected.json,abbreviated_version_expected.json,invalid_option_expected.json,missing_reference_argument_expected.json,unsupported_long_option_expected.json,missing_long_reference_argument_expected.json,missing_long_dump_types_argument_expected.json",
        "PHASE2_GENKSYMS_BRIDGE_NORMALIZED_STDERR_PACKET=invalid_option_expected.json,missing_reference_argument_expected.json,unsupported_long_option_expected.json,missing_long_reference_argument_expected.json,missing_long_dump_types_argument_expected.json",
        "PHASE2_GENKSYMS_BRIDGE_ACTION_ABBREV_CASES=abbreviated_help,abbreviated_version",
        "PHASE2_KCONFIG_BRIDGE_CONF_CASE_COUNT=11",
        "PHASE2_KCONFIG_BRIDGE_CONF_CASES=olddefconfig,syncconfig,alldefconfig,allmodconfig,randconfig,yes2modconfig,mod2yesconfig,mod2noconfig,defconfig,savedefconfig,listnewconfig",
        "PHASE2_KCONFIG_BRIDGE_CONF_STDOUT_PACKET=olddefconfig_expected.json,syncconfig_expected.json,alldefconfig_expected.json,allmodconfig_expected.json,randconfig_expected.json,yes2modconfig_expected.json,mod2yesconfig_expected.json,mod2noconfig_expected.json,defconfig_expected.json,savedefconfig_expected.json,listnewconfig_expected.json",
        "conf bridge emits syncconfig auto files",
        "conf bridge emits alldefconfig argv and env",
        "conf bridge emits allmodconfig argv and env",
        "conf bridge emits randconfig tunables when present",
        "conf bridge emits yes2modconfig argv and env",
        "conf bridge emits defconfig mode argument before kconfig",
        "conf bridge emits savedefconfig mode argument before kconfig",
        "conf bridge escapes low control bytes in JSON strings",
        "PHASE2_ROLLBACK=keep C kbuild tools authoritative and remove failing Zigux bridge/tool from workflow wiring",
        f"PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT={len(confdata_case_names)}",
        "PHASE2_KCONFIG_BRIDGE_CONFDATA_CASES=" + ",".join(confdata_case_names),
        "PHASE2_KCONFIG_BRIDGE_CONFDATA_EXPECTED_PACKET=" + ",".join(confdata_expected_packet),
        "confdata bridge decodes escaped quoted strings",
        "confdata bridge decodes escaped control sequences in quoted strings",
        "confdata bridge keeps trailing escaped backslashes in quoted strings",
        "confdata bridge accepts CRLF config lines",
        "confdata bridge preserves trailing carriage return on final unterminated value line",
        "confdata bridge ignores unterminated unset comment with trailing carriage return",
        "confdata bridge keeps explicit n assignments as tristate values",
        "confdata bridge recognizes uppercase tristate assignments",
        "confdata bridge ignores non-CONFIG lines like upstream confdata",
        "PHASE2_FIXDEP_CASE_COUNT=5",
        "PHASE2_FIXDEP_CASES=sample,sample_escaped_space,sample_multi_target,sample_comment_only,sample_missing_dep",
        "PHASE2_FIXDEP_STDOUT_PACKET=sample_expected.txt,sample_escaped_space_expected.txt,sample_multi_target_expected.txt,sample_comment_only_expected.txt,sample_missing_dep_expected.txt",
    ]
    required_closure_markers.extend(PHASE2_CROSS_ALIGNMENT_REQUIRED_SOURCE_MARKERS)
    required_closure_markers.extend(PHASE2_KCONFIG_ALIGNMENT_REQUIRED_SOURCE_MARKERS)
    required_closure_markers.extend(PHASE2_TOOLCHAIN_PIN_SCOPE_REQUIRED_SOURCE_MARKERS)
    required_closure_markers.extend(PHASE2_TESTS_README_ALIGNMENT_REQUIRED_SOURCE_MARKERS)

    required_workflow_markers = [
        "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
        "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
        "python3 scripts/zigux/check-genksyms-bridge.py --self-test",
        "python3 scripts/zigux/check-genksyms-bridge.py",
        "python3 scripts/zigux/check-genksyms-crc-diff.py",
        "python3 scripts/zigux/check-kconfig-bridge.py --self-test",
        "python3 scripts/zigux/check-kconfig-bridge.py",
        "python3 scripts/zigux/check-mk-elfconfig-diff.py",
        "python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
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
        "phase2-validate:",
        "check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
        "check-phase2-genksyms-bridge-selftest-alignment.py",
        "phase2-kconfig:",
        "phase2-cross:",
        "check-zig-toolchain.py",
        "check-phase2-tests-readme-alignment.py",
        "check-phase2-cross-selftest-alignment.py --self-test",
        "check-phase2-cross-selftest-alignment.py",
        "check-phase2-toolchain-pin-scope.py --self-test",
        "check-phase2-toolchain-pin-scope.py",
        "check-phase2-kconfig-selftest-alignment.py --self-test",
        "check-phase2-kconfig-selftest-alignment.py",
        "check-kconfig-bridge.py --self-test",
        "check-kconfig-bridge.py",
        "check-mk-elfconfig-diff.py",
        "check-genksyms-bridge.py --self-test",
        "check-genksyms-bridge.py",
        "check-genksyms-crc-diff.py",
        "$(ZIG) test scripts/zigux/fixdep.zig",
        "$(ZIG) test scripts/zigux/genksyms.zig",
        "$(ZIG) test scripts/zigux/genksyms_crc.zig",
        "$(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
        "$(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
        "$(ZIG) test scripts/zigux/mk_elfconfig.zig",
    ]

    issues: list[str] = []
    for marker in required_closure_markers:
        require_marker(closure, marker, issues, "closure")
    for marker in required_workflow_markers:
        require_marker(workflow, marker, issues, "workflow")
    for marker in required_ledger_markers:
        require_marker(ledger, marker, issues, "ledger")
    for marker in required_readme_markers:
        require_marker(script_readme, marker, issues, "scripts")
    for marker in required_doc_markers:
        require_marker(artifact_doc, marker, issues, "doc")
    for marker in required_makefile_markers:
        require_marker(makefile, marker, issues, "make")
    issues.extend(validate_exact_makefile_runs(makefile))
    issues.extend(validate_exact_workflow_runs(workflow))

    if tool_manifest.get("phase") != "Phase 2":
        issues.append("manifest:phase=Phase 2")
    if tool_manifest.get("status") != "closed":
        issues.append("manifest:status=closed")
    if tool_manifest.get("tool_count") != 6:
        issues.append("manifest:tool_count=6")
    if len(tool_manifest.get("tools", [])) != 6:
        issues.append(f"manifest:tools_len={len(tool_manifest.get('tools', []))}")
    for rel in tool_manifest.get("tools", []):
        if not (root / rel).exists():
            issues.append(f"manifest_file:{rel}")
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
    cases: list[tuple[str, list[str], list[str]]] = []
    make_ok = make_ok_text()
    workflow_ok = workflow_ok_text()
    cases.append(("make_ok", validate_exact_makefile_runs(make_ok), []))
    cases.append(("workflow_ok", validate_exact_workflow_runs(workflow_ok), []))

    make_duplicate_cases = [
        "scripts/zigux/check-kconfig-bridge.py --self-test",
        "scripts/zigux/check-kconfig-bridge.py",
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "scripts/zigux/check-genksyms-crc-diff.py",
    ]
    for command in make_duplicate_cases:
        mutated = make_ok + f"\ncd $(ZIGUX_ROOT) && $(PYTHON) {command}"
        cases.append(
            (
                f"make_duplicate_{command}",
                validate_exact_makefile_runs(mutated),
                [f"make_exact_run:{command}:count=2:expected=1"],
            )
        )

    make_duplicate_exact_lines = [
        "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms_crc.zig",
        "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
        "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
    ]
    for line in make_duplicate_exact_lines:
        cases.append(
            (
                f"make_duplicate_{line}",
                validate_exact_makefile_runs(make_ok + f"\n{line}"),
                [f"make_exact_line:{line}:count=2:expected=1"],
            )
        )

    workflow_duplicate_cases = [
        "python3 scripts/zigux/check-kconfig-bridge.py --self-test",
        "python3 scripts/zigux/check-kconfig-bridge.py",
        "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
        "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "python3 scripts/zigux/check-genksyms-crc-diff.py",
    ]
    for command in workflow_duplicate_cases:
        mutated = workflow_ok + f"run: {command}\n"
        cases.append(
            (
                f"workflow_duplicate_{command}",
                validate_exact_workflow_runs(mutated),
                [f"workflow_exact_run:{command}:count=2:expected=1"],
            )
        )

    workflow_duplicate_exact_lines = [
        "run: zig test scripts/zigux/genksyms_crc.zig",
        "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
        "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
    ]
    for line in workflow_duplicate_exact_lines:
        cases.append(
            (
                f"workflow_duplicate_{line}",
                validate_exact_workflow_runs(workflow_ok + f"{line}\n"),
                [f"workflow_exact_line:{line}:count=2:expected=1"],
            )
        )

    failures = [
        f"{name}:expected={expected}:actual={actual}"
        for name, actual, expected in cases
        if actual != expected
    ]
    if failures:
        print("PHASE2_CLOSURE_SELF_TEST=fail")
        print("PHASE2_CLOSURE_SELF_TEST_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE2_CLOSURE_SELF_TEST_FAILURES_END")
        return 1
    print("PHASE2_CLOSURE_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    required_files = required_files_for(ROOT)
    missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
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
    genksyms_expected_files, _ = collect_genksyms_expected_files(genksyms_cases_payload)
    kconfig_cases_payload = load_json_object(KCONFIG_BRIDGE_CASES, label="kconfig_bridge_cases")
    confdata_case_files, confdata_case_names, confdata_expected_packet, _ = collect_confdata_case_metadata(
        kconfig_cases_payload
    )
    _ = confdata_case_names, confdata_expected_packet
    print("PHASE2_CLOSURE_VALIDATION=pass")
    print(
        "PHASE2_CLOSURE_REQUIRED_FILE_COUNT="
        f"{len(required_files) + len(genksyms_expected_files) + len(confdata_case_files)}"
    )
    print(
        "PHASE2_CLOSURE_REQUIRED_MARKER_COUNT="
        f"{49 + len(PHASE2_CROSS_ALIGNMENT_REQUIRED_SOURCE_MARKERS) + len(PHASE2_KCONFIG_ALIGNMENT_REQUIRED_SOURCE_MARKERS) + len(PHASE2_TOOLCHAIN_PIN_SCOPE_REQUIRED_SOURCE_MARKERS) + len(PHASE2_TESTS_README_ALIGNMENT_REQUIRED_SOURCE_MARKERS) + 23 + 6 + 3 + 27}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
