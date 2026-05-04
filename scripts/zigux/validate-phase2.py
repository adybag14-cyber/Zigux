#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
CLOSURE_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2-closure.py"
CHECK_GENKSYMS_BRIDGE = ROOT / "scripts" / "zigux" / "check-genksyms-bridge.py"
GENKSYMS_BRIDGE_ALIGNMENT_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-genksyms-bridge-selftest-alignment.py"
)
KCONFIG_ALIGNMENT_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py"
)
PHASE2_CROSS_ALIGNMENT_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"
)
PHASE2_CROSS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
PHASE2_TESTS_README_ALIGNMENT_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"
)
TOOLCHAIN_PIN_SCOPE_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"
TOOLCHAIN_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
CHECK_FIXDEP = ROOT / "scripts" / "zigux" / "check-fixdep-diff.py"
CHECK_KCONFIG_BRIDGE = ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py"
WORKFLOW_FILE = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE_FILE = ROOT / "zigux" / "Makefile"
README_FILE = ROOT / "scripts" / "zigux" / "README.md"
PHASE2_TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
PHASE2_CROSS_TARGETS = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
FIXDEP_CASES = ROOT / "zigux" / "tests" / "fixtures" / "fixdep" / "cases.json"
EXPECTED_TOOL_MANIFEST_TOOLS = [
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/mk_elfconfig.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
]
EXPECTED_CROSS_TARGETS = [
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
]
REQUIRED_PHASE2_FILES = [
    CLOSURE_VALIDATOR,
    ROOT / "scripts" / "zigux" / "artifact_diff.py",
    ROOT / "scripts" / "zigux" / "check-artifact-diff-contract.py",
    CHECK_FIXDEP,
    CHECK_GENKSYMS_BRIDGE,
    GENKSYMS_BRIDGE_ALIGNMENT_CHECKER,
    ROOT / "scripts" / "zigux" / "check-genksyms-crc-diff.py",
    CHECK_KCONFIG_BRIDGE,
    KCONFIG_ALIGNMENT_CHECKER,
    PHASE2_CROSS_ALIGNMENT_CHECKER,
    PHASE2_CROSS_CHECKER,
    PHASE2_TESTS_README_ALIGNMENT_CHECKER,
    TOOLCHAIN_PIN_SCOPE_CHECKER,
    ROOT / "scripts" / "zigux" / "check-mk-elfconfig-diff.py",
    ROOT / "scripts" / "zigux" / "fixdep.zig",
    ROOT / "scripts" / "zigux" / "genksyms.zig",
    ROOT / "scripts" / "zigux" / "genksyms_crc.zig",
    ROOT / "scripts" / "zigux" / "mk_elfconfig.zig",
    ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig",
    ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig",
    WORKFLOW_FILE,
    README_FILE,
    TOOLCHAIN_NOTES,
    REVIEW_CHECKLIST,
    TESTS_README,
    ROOT / "Documentation" / "zigux" / "phase2-closure.md",
    MAKEFILE_FILE,
    PHASE2_TOOL_MANIFEST,
    PHASE2_CROSS_TARGETS,
    FIXDEP_CASES,
]
PHASE2_GENKSYMS_BRIDGE_REQUIRED_SOURCE_MARKERS = [
    "PHASE2_GENKSYMS_BRIDGE_SELF_TEST=pass",
    "PHASE2_GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=26",
    "normalize_stderr:requires_process_json_mode",
    "expected:missing_fixture:",
    "cases.json:orphaned_expected:",
    "expected:duplicate_reference:",
    "run(diff_base + [str(c_actual), str(c_repeat)], cwd=str(ROOT))",
    "run(diff_base + [str(zig_actual), str(zig_repeat)], cwd=str(ROOT))",
    "run(text_diff_base + [str(c_actual_stderr), str(c_repeat_stderr)], cwd=str(ROOT))",
    "run(text_diff_base + [str(zig_actual_stderr), str(zig_repeat_stderr)], cwd=str(ROOT))",
    "print('GENKSYMS_BRIDGE_DETERMINISM=pass')",
]
PHASE2_GENKSYMS_BRIDGE_ALIGNMENT_REQUIRED_SOURCE_MARKERS = [
    "PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT=20",
    "print('GENKSYMS_BRIDGE_DETERMINISM=pass')",
    '"python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test": 1',
    '"python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py": 1',
]
PHASE2_GENKSYMS_REQUIRED_README_MARKERS = [
    "check-genksyms-bridge.py --self-test",
    "check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
    "check-phase2-genksyms-bridge-selftest-alignment.py",
    "check-genksyms-crc-diff.py --self-test",
]
PHASE2_KCONFIG_ALIGNMENT_REQUIRED_SOURCE_MARKERS = [
    "PHASE2_KCONFIG_ALIGNMENT_SELF_TEST=pass",
    "PHASE2_KCONFIG_ALIGNMENT_SELF_TEST_CASE_COUNT=13",
    '"python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test": 1',
    '"python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py": 1',
]
PHASE2_CROSS_ALIGNMENT_REQUIRED_SOURCE_MARKERS = [
    "PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass",
    "PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT=18",
]
PHASE2_CROSS_ALIGNMENT_REQUIRED_WORKFLOW_COUNTS = {
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py": 1,
}
PHASE2_CROSS_REQUIRED_SOURCE_MARKERS = [
    "phase2-cross:tool_manifest_path_missing:",
    "phase2-cross:self-test:explicit_target_failure:",
    "print('PHASE2_CROSS_SELF_TEST_CASE_COUNT=9')",
]
PHASE2_TOOLCHAIN_PIN_SCOPE_REQUIRED_SOURCE_MARKERS = [
    "PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass",
    "PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST_CASE_COUNT=48",
    "PHASE2_TOOLCHAIN_PIN_SCOPE=pass",
    '"python3 scripts/zigux/install-zig.py --self-test": 1',
    '"python3 scripts/zigux/check-zig-toolchain.py --self-test": 1',
    '"python3 scripts/zigux/install-zig.py --dest .zig-toolchain": 2',
    '"python3 scripts/zigux/check-zig-toolchain.py": 2',
    'EXPECTED_PIN_TARGETS = [',
]
PHASE2_TOOLCHAIN_NOTES_REQUIRED_SOURCE_MARKERS = [
    "scripts/zigux/zig-toolchain-policy.json",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
    "same three-target compile matrix, validator pair, and Linux-style `make -C zigux phase2-validate` plus `make -C zigux phase2` replay surface",
    "kbuild-facing replay surface",
    "same kbuild-facing replay surface named by the shared validators, the closure note, and the shared review checklist",
    "x86_64-linux",
]
PHASE2_TOOLCHAIN_README_REQUIRED_SOURCE_MARKERS = [
    "check-phase2-toolchain-pin-scope.py --self-test",
    "check-phase2-toolchain-pin-scope.py",
    "check-phase2-tests-readme-alignment.py --self-test",
    "check-phase2-tests-readme-alignment.py",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "phase2_cross_targets.json",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
    "kbuild-facing review path",
    "x86_64-linux",
]
PHASE2_TOOLCHAIN_REVIEW_CHECKLIST_REQUIRED_SOURCE_MARKERS = [
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/zig-toolchain-policy.json",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "bounded archive pin",
    "dedicated tests-root alignment guard",
    "workflow bootstrap install and verification route",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
]
PHASE2_TESTS_README_REQUIRED_SOURCE_MARKERS = [
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
    "same three-target compile matrix, direct cross gate, alignment guard, and kbuild-facing replay surface as the docs root, scripts root, closure note, review checklist, workflow, and Makefile",
]
PHASE2_FIXDEP_REQUIRED_SOURCE_MARKERS = [
    "FIXDEP_SELF_TEST=pass",
    "print(f'FIXDEP_SELF_TEST_CASE_COUNT={checks_run}')",
    "validate_tool_sources(C_FIXDEP, ZIG_FIXDEP)",
    "expected_stderr_path = expected_stderr or implicit_expected_stderr",
    "diff_text(c_actual, c_repeat)",
    "diff_text(zig_actual, zig_repeat)",
    "diff_text(c_actual_stderr, zig_actual_stderr)",
    "diff_text(c_actual_stderr, c_repeat_stderr)",
    "diff_text(zig_actual_stderr, zig_repeat_stderr)",
    "print('FIXDEP_DETERMINISM=pass')",
]
PHASE2_FIXDEP_REQUIRED_WORKFLOW_COUNTS = {
    "python3 scripts/zigux/check-fixdep-diff.py --self-test": 1,
    "python3 scripts/zigux/check-fixdep-diff.py": 1,
    "zig test scripts/zigux/fixdep.zig": 1,
}
PHASE2_FIXDEP_REQUIRED_MAKEFILE_COUNTS = {
    "scripts/zigux/check-fixdep-diff.py --self-test": 1,
    "scripts/zigux/check-fixdep-diff.py": 1,
    "$(ZIG) test scripts/zigux/fixdep.zig": 1,
}
PHASE2_GENKSYMS_BRIDGE_REQUIRED_WORKFLOW_COUNTS = {
    "python3 scripts/zigux/check-genksyms-bridge.py --self-test": 1,
    "python3 scripts/zigux/check-genksyms-bridge.py": 1,
    "zig test scripts/zigux/genksyms.zig": 1,
}
PHASE2_GENKSYMS_BRIDGE_REQUIRED_MAKEFILE_COUNTS = {
    "scripts/zigux/check-genksyms-bridge.py --self-test": 1,
    "scripts/zigux/check-genksyms-bridge.py": 1,
    "$(ZIG) test scripts/zigux/genksyms.zig": 1,
}
PHASE2_KCONFIG_REQUIRED_SOURCE_MARKERS = [
    "assert total_self_test_cases == 6",
    "print(f'KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT={total_self_test_cases}')",
    "compare_text_artifacts(actual, repeat)",
    "compare_text_artifacts(actual, rebuild)",
    "compare_text_artifacts(default_actual, default_repeat)",
    "compare_text_artifacts(default_actual, default_rebuild)",
    "input_path=trailing_cr_input",
    "input_path=final_unset_input",
    "confdata bridge normalizes a trailing carriage return on the final unterminated line",
    "print('KCONFIG_BRIDGE_DETERMINISM=pass')",
]
PHASE2_KCONFIG_REQUIRED_WORKFLOW_COUNTS = {
    "python3 scripts/zigux/check-kconfig-bridge.py --self-test": 1,
    "python3 scripts/zigux/check-kconfig-bridge.py": 1,
    "zig test scripts/zigux/kconfig/conf_bridge.zig": 1,
    "zig test scripts/zigux/kconfig/confdata_bridge.zig": 1,
}
PHASE2_KCONFIG_REQUIRED_MAKEFILE_COUNTS = {
    "scripts/zigux/check-kconfig-bridge.py --self-test": 1,
    "scripts/zigux/check-kconfig-bridge.py": 1,
    "$(ZIG) test scripts/zigux/kconfig/conf_bridge.zig": 1,
    "$(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig": 1,
}
PHASE2_KCONFIG_ALIGNMENT_REQUIRED_WORKFLOW_COUNTS = {
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py": 1,
}
PHASE2_KCONFIG_ALIGNMENT_REQUIRED_MAKEFILE_COUNTS = {
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test": 1,
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py": 1,
}
PHASE2_CROSS_ALIGNMENT_REQUIRED_MAKEFILE_COUNTS = {
    "scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test": 1,
    "scripts/zigux/check-phase2-cross-selftest-alignment.py": 1,
}


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_list_manifest(
    path: Path,
    *,
    label: str,
    count_key: str,
    expected_count: int,
    list_key: str,
    expected_items: list[str],
) -> list[str]:
    payload = load_json(path)
    issues: list[str] = []
    if not isinstance(payload, dict):
        return [f"{label}:expected_object"]

    if payload.get("phase") != "Phase 2":
        issues.append(f"{label}:phase={payload.get('phase')!r}:expected='Phase 2'")
    if payload.get("status") != "closed":
        issues.append(f"{label}:status={payload.get('status')!r}:expected='closed'")
    if payload.get(count_key) != expected_count:
        issues.append(f"{label}:{count_key}={payload.get(count_key)!r}:expected={expected_count}")

    items = payload.get(list_key)
    if not isinstance(items, list):
        issues.append(f"{label}:{list_key}:expected_list")
        return issues
    if len(items) != expected_count:
        issues.append(f"{label}:{list_key}_len={len(items)}:expected={expected_count}")
    if items != expected_items:
        issues.append(f"{label}:{list_key}=expected_exact_list")
    for rel in items:
        if not isinstance(rel, str):
            issues.append(f"{label}:{list_key}:non_string_item")
            continue
        if list_key == "tools" and not (ROOT / rel).exists():
            issues.append(f"{label}:missing_tool:{rel}")
    return issues


def validate_source_markers(path: Path, *, label: str, required_markers: list[str]) -> list[str]:
    source = path.read_text(encoding="utf-8")
    issues: list[str] = []
    for marker in required_markers:
        if marker not in source:
            issues.append(f"{label}:missing_marker:{marker}")
    return issues


def validate_exact_command_counts(
    path: Path,
    *,
    label: str,
    expected_counts: dict[str, int],
    workflow_mode: bool = False,
) -> list[str]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    issues: list[str] = []
    for command, expected_count in expected_counts.items():
        if workflow_mode:
            expected_line = f"run: {command}"
            count = sum(1 for line in lines if line == expected_line)
        else:
            count = sum(1 for line in lines if line.endswith(command))
        if count != expected_count:
            issues.append(f"{label}:{command}:count={count}:expected={expected_count}")
    return issues


def load_fixdep_cases(cases_path: Path) -> list[dict[str, object]]:
    data = load_json(cases_path)
    if not isinstance(data, list):
        raise ValueError("fixdep cases manifest must be a JSON list")
    return data


def validate_expected_fixdep_cases(cases_path: Path) -> list[str]:
    cases = load_fixdep_cases(cases_path)
    fixture_dir = cases_path.parent
    expected_cases = {
        "sample": {
            "depfile": "sample.d",
            "target": "sample.o",
            "cmdline": "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample.o",
            "expected": "sample_expected.txt",
            "expected_exit_code": 0,
        },
        "sample_multi_target": {
            "depfile": "sample_multi_target.d",
            "target": "module/sample2.o",
            "cmdline": "clang -Iinclude -DZIGUX_MULTI -c zigux/tests/fixtures/fixdep/sample2.c -o module/sample2.o",
            "expected": "sample_multi_target_expected.txt",
            "expected_exit_code": 0,
        },
        "sample_escaped_space": {
            "depfile": "sample_escaped_space.d",
            "target": "sample_escaped_space.o",
            "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_escaped_space_source.c -o sample_escaped_space.o",
            "expected": "sample_escaped_space_expected.txt",
            "expected_exit_code": 0,
        },
        "sample_escaped_colon": {
            "depfile": "sample_escaped_colon.d",
            "target": "sample_escaped_colon.o",
            "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c -o sample_escaped_colon.o",
            "expected": "sample_escaped_colon_expected.txt",
            "expected_exit_code": 0,
        },
        "sample_concatenated": {
            "depfile": "sample_concatenated.d",
            "target": "sample_concatenated.o",
            "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_concatenated_source.c -o sample_concatenated.o",
            "expected": "sample_concatenated_expected.txt",
            "expected_exit_code": 0,
        },
        "sample_comment_continued": {
            "depfile": "sample_comment_continued.d",
            "target": "sample_comment_continued.o",
            "cmdline": "rustc --emit dep-info=sample_comment_continued.d -o sample_comment_continued.o zigux/tests/fixtures/fixdep/sample_comment_continued.rs",
            "expected": "sample_comment_continued_expected.txt",
            "expected_exit_code": 0,
        },
        "sample_comment_only": {
            "depfile": "sample_comment_only.d",
            "target": "sample_comment_only.o",
            "cmdline": "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only.o",
            "expected": "sample_comment_only_expected.txt",
            "expected_stderr": "sample_comment_only_expected.stderr.txt",
            "expected_exit_code": 1,
        },
        "sample_comment_only_stdout_full": {
            "depfile": "sample_comment_only.d",
            "target": "sample_comment_only_stdout_full.o",
            "cmdline": "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only_stdout_full.o",
            "expected": "sample_output_write_expected.txt",
            "expected_stderr": "sample_comment_only_expected.stderr.txt",
            "expected_exit_code": 1,
            "stdout_mode": "dev_full",
        },
        "sample_missing_dep": {
            "depfile": "sample_missing_dep.d",
            "target": "sample_missing_dep.o",
            "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep.o",
            "expected": "sample_missing_dep_expected.txt",
            "expected_stderr": "sample_missing_dep_expected.stderr.txt",
            "expected_exit_code": 2,
        },
        "sample_missing_dep_stdout_full": {
            "depfile": "sample_missing_dep.d",
            "target": "sample_missing_dep_stdout_full.o",
            "cmdline": "clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep_stdout_full.o",
            "expected": "sample_output_write_expected.txt",
            "expected_stderr": "sample_missing_dep_expected.stderr.txt",
            "expected_exit_code": 2,
            "stdout_mode": "dev_full",
        },
        "sample_output_write": {
            "depfile": "sample.d",
            "target": "sample_output_write.o",
            "cmdline": "clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_output_write.o",
            "expected": "sample_output_write_expected.txt",
            "expected_stderr": "sample_output_write_expected.stderr.txt",
            "expected_exit_code": 1,
            "stdout_mode": "dev_full",
        },
    }

    issues: list[str] = []
    seen_names: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            issues.append(f"fixdep_cases:entry[{index}]:expected_object")
            continue

        name = case.get("name")
        if not isinstance(name, str) or not name:
            issues.append("fixdep_cases:missing_name")
            continue
        if name in seen_names:
            issues.append(f"fixdep_cases:duplicate_name:{name}")
            continue
        seen_names.add(name)

        expected_case = expected_cases.get(name)
        if expected_case is None:
            issues.append(f"fixdep_cases:unexpected_name:{name}")
            continue

        for field_name, expected_value in expected_case.items():
            actual_value = case.get(field_name, 0 if field_name == "expected_exit_code" else None)
            if actual_value != expected_value:
                issues.append(
                    f"fixdep_cases:{name}:{field_name}={actual_value!r},expected={expected_value!r}"
                )

        depfile = case.get("depfile")
        if not isinstance(depfile, str) or not depfile:
            issues.append(f"fixdep_cases:{name}:missing_non_empty_depfile")
        elif not (fixture_dir / depfile).exists():
            issues.append(f"fixdep_cases:missing_depfile:{depfile}")

        expected_stdout_name = case.get("expected_stdout", case.get("expected"))
        if not isinstance(expected_stdout_name, str) or not expected_stdout_name:
            issues.append(f"fixdep_cases:{name}:missing_expected_output")
        elif not (fixture_dir / expected_stdout_name).exists():
            issues.append(f"fixdep_cases:missing_expected_output:{expected_stdout_name}")

        expected_exit_code = int(case.get("expected_exit_code", 0))
        if expected_exit_code != 0:
            expected_stderr_name = case.get("expected_stderr")
            if not isinstance(expected_stderr_name, str) or not expected_stderr_name:
                issues.append(f"fixdep_cases:{name}:missing_expected_stderr")
            elif not (fixture_dir / expected_stderr_name).exists():
                issues.append(f"fixdep_cases:missing_expected_stderr:{expected_stderr_name}")

        stdout_mode = case.get("stdout_mode")
        if stdout_mode not in (None, "dev_full"):
            issues.append(f"fixdep_cases:{name}:unsupported_stdout_mode:{stdout_mode!r}")

    missing_names = sorted(set(expected_cases) - seen_names)
    for name in missing_names:
        issues.append(f"fixdep_cases:missing_name:{name}")
    if len(cases) != len(expected_cases):
        issues.append(f"fixdep_cases:count={len(cases)},expected={len(expected_cases)}")
    return issues


def main() -> int:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_PHASE2_FILES if not path.exists()]
    if missing:
        print("PHASE2_VALIDATION=fail")
        print("MISSING_PHASE2_SHARED_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE2_SHARED_FILES_END")
        return 1

    issues: list[str] = []
    issues.extend(
        validate_list_manifest(
            PHASE2_TOOL_MANIFEST,
            label="phase2_tool_manifest",
            count_key="tool_count",
            expected_count=6,
            list_key="tools",
            expected_items=EXPECTED_TOOL_MANIFEST_TOOLS,
        )
    )
    issues.extend(
        validate_list_manifest(
            PHASE2_CROSS_TARGETS,
            label="phase2_cross_targets",
            count_key="target_count",
            expected_count=3,
            list_key="targets",
            expected_items=EXPECTED_CROSS_TARGETS,
        )
    )
    issues.extend(validate_expected_fixdep_cases(FIXDEP_CASES))
    issues.extend(
        validate_source_markers(
            CHECK_GENKSYMS_BRIDGE,
            label="phase2_genksyms_bridge_checker",
            required_markers=PHASE2_GENKSYMS_BRIDGE_REQUIRED_SOURCE_MARKERS,
        )
    )
    issues.extend(
        validate_source_markers(
            GENKSYMS_BRIDGE_ALIGNMENT_CHECKER,
            label="phase2_genksyms_bridge_alignment_checker",
            required_markers=PHASE2_GENKSYMS_BRIDGE_ALIGNMENT_REQUIRED_SOURCE_MARKERS,
        )
    )
    issues.extend(
        validate_source_markers(
            README_FILE,
            label="phase2_genksyms_readme",
            required_markers=PHASE2_GENKSYMS_REQUIRED_README_MARKERS,
        )
    )
    issues.extend(
        validate_source_markers(
            KCONFIG_ALIGNMENT_CHECKER,
            label="phase2_kconfig_alignment_checker",
            required_markers=PHASE2_KCONFIG_ALIGNMENT_REQUIRED_SOURCE_MARKERS,
        )
    )
    issues.extend(
        validate_source_markers(
            PHASE2_CROSS_ALIGNMENT_CHECKER,
            label="phase2_cross_alignment_checker",
            required_markers=PHASE2_CROSS_ALIGNMENT_REQUIRED_SOURCE_MARKERS,
        )
    )
    issues.extend(
        validate_source_markers(
            PHASE2_CROSS_CHECKER,
            label="phase2_cross_checker",
            required_markers=PHASE2_CROSS_REQUIRED_SOURCE_MARKERS,
        )
    )
    issues.extend(
        validate_source_markers(
            TOOLCHAIN_PIN_SCOPE_CHECKER,
            label="toolchain_pin_scope_checker",
            required_markers=PHASE2_TOOLCHAIN_PIN_SCOPE_REQUIRED_SOURCE_MARKERS,
        )
    )
    issues.extend(
        validate_source_markers(
            TOOLCHAIN_NOTES,
            label="phase2_toolchain_notes",
            required_markers=PHASE2_TOOLCHAIN_NOTES_REQUIRED_SOURCE_MARKERS,
        )
    )
    issues.extend(
        validate_source_markers(
            README_FILE,
            label="phase2_toolchain_readme",
            required_markers=PHASE2_TOOLCHAIN_README_REQUIRED_SOURCE_MARKERS,
        )
    )
    issues.extend(
        validate_source_markers(
            REVIEW_CHECKLIST,
            label="phase2_toolchain_review_checklist",
            required_markers=PHASE2_TOOLCHAIN_REVIEW_CHECKLIST_REQUIRED_SOURCE_MARKERS,
        )
    )
    issues.extend(
        validate_source_markers(
            TESTS_README,
            label="phase2_tests_readme",
            required_markers=PHASE2_TESTS_README_REQUIRED_SOURCE_MARKERS,
        )
    )
    issues.extend(
        validate_source_markers(
            CHECK_FIXDEP,
            label="phase2_fixdep_checker",
            required_markers=PHASE2_FIXDEP_REQUIRED_SOURCE_MARKERS,
        )
    )
    issues.extend(
        validate_source_markers(
            CHECK_KCONFIG_BRIDGE,
            label="phase2_kconfig_bridge_checker",
            required_markers=PHASE2_KCONFIG_REQUIRED_SOURCE_MARKERS,
        )
    )
    issues.extend(
        validate_exact_command_counts(
            WORKFLOW_FILE,
            label="phase2_fixdep_workflow",
            expected_counts=PHASE2_FIXDEP_REQUIRED_WORKFLOW_COUNTS,
            workflow_mode=True,
        )
    )
    issues.extend(
        validate_exact_command_counts(
            MAKEFILE_FILE,
            label="phase2_fixdep_makefile",
            expected_counts=PHASE2_FIXDEP_REQUIRED_MAKEFILE_COUNTS,
        )
    )
    issues.extend(
        validate_exact_command_counts(
            WORKFLOW_FILE,
            label="phase2_genksyms_bridge_workflow",
            expected_counts=PHASE2_GENKSYMS_BRIDGE_REQUIRED_WORKFLOW_COUNTS,
            workflow_mode=True,
        )
    )
    issues.extend(
        validate_exact_command_counts(
            MAKEFILE_FILE,
            label="phase2_genksyms_bridge_makefile",
            expected_counts=PHASE2_GENKSYMS_BRIDGE_REQUIRED_MAKEFILE_COUNTS,
        )
    )
    issues.extend(
        validate_exact_command_counts(
            WORKFLOW_FILE,
            label="phase2_kconfig_workflow",
            expected_counts=PHASE2_KCONFIG_REQUIRED_WORKFLOW_COUNTS,
            workflow_mode=True,
        )
    )
    issues.extend(
        validate_exact_command_counts(
            MAKEFILE_FILE,
            label="phase2_kconfig_makefile",
            expected_counts=PHASE2_KCONFIG_REQUIRED_MAKEFILE_COUNTS,
        )
    )
    issues.extend(
        validate_exact_command_counts(
            WORKFLOW_FILE,
            label="phase2_kconfig_alignment_workflow",
            expected_counts=PHASE2_KCONFIG_ALIGNMENT_REQUIRED_WORKFLOW_COUNTS,
            workflow_mode=True,
        )
    )
    issues.extend(
        validate_exact_command_counts(
            MAKEFILE_FILE,
            label="phase2_kconfig_alignment_makefile",
            expected_counts=PHASE2_KCONFIG_ALIGNMENT_REQUIRED_MAKEFILE_COUNTS,
        )
    )
    issues.extend(
        validate_exact_command_counts(
            WORKFLOW_FILE,
            label="phase2_cross_alignment_workflow",
            expected_counts=PHASE2_CROSS_ALIGNMENT_REQUIRED_WORKFLOW_COUNTS,
            workflow_mode=True,
        )
    )
    issues.extend(
        validate_exact_command_counts(
            MAKEFILE_FILE,
            label="phase2_cross_alignment_makefile",
            expected_counts=PHASE2_CROSS_ALIGNMENT_REQUIRED_MAKEFILE_COUNTS,
        )
    )

    if issues:
        print("PHASE2_VALIDATION=fail")
        print("INVALID_PHASE2_SHARED_METADATA_START")
        for item in issues:
            print(item)
        print("INVALID_PHASE2_SHARED_METADATA_END")
        return 1

    result = subprocess.run(
        [sys.executable, str(GENKSYMS_BRIDGE_ALIGNMENT_CHECKER)],
        cwd=ROOT,
    )
    if result.returncode != 0:
        print("PHASE2_VALIDATION=fail")
        return result.returncode

    result = subprocess.run(
        [sys.executable, str(KCONFIG_ALIGNMENT_CHECKER)],
        cwd=ROOT,
    )
    if result.returncode != 0:
        print("PHASE2_VALIDATION=fail")
        return result.returncode

    result = subprocess.run(
        [sys.executable, str(PHASE2_CROSS_ALIGNMENT_CHECKER)],
        cwd=ROOT,
    )
    if result.returncode != 0:
        print("PHASE2_VALIDATION=fail")
        return result.returncode

    result = subprocess.run(
        [sys.executable, str(PHASE2_TESTS_README_ALIGNMENT_CHECKER)],
        cwd=ROOT,
    )
    if result.returncode != 0:
        print("PHASE2_VALIDATION=fail")
        return result.returncode

    result = subprocess.run(
        [sys.executable, str(TOOLCHAIN_PIN_SCOPE_CHECKER)],
        cwd=ROOT,
    )
    if result.returncode != 0:
        print("PHASE2_VALIDATION=fail")
        return result.returncode

    result = subprocess.run([sys.executable, str(CLOSURE_VALIDATOR)], cwd=ROOT)
    if result.returncode == 0:
        print("PHASE2_VALIDATION=pass")
    else:
        print("PHASE2_VALIDATION=fail")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
