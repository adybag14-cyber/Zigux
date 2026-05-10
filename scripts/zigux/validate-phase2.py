#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

_parents = Path(__file__).resolve().parents
ROOT = _parents[2] if len(_parents) > 2 else _parents[-1]
GENKSYMS_BRIDGE_DIR = ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge"
KCONFIG_BRIDGE_DIR = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge"


def case_files_from_groups(case_manifest: Path, *group_specs: tuple[str, str]) -> list[Path]:
    cases = json.loads(case_manifest.read_text(encoding="utf-8"))
    discovered_files: list[Path] = []
    seen: set[Path] = set()
    for group_name, field_name in group_specs:
        for case in cases.get(group_name, []):
            file_name = case.get(field_name)
            if not file_name:
                continue
            discovered_path = case_manifest.parent / file_name
            if discovered_path in seen:
                continue
            seen.add(discovered_path)
            discovered_files.append(discovered_path)
    return discovered_files


def run_guard(root: Path, command: list[str], required_markers: list[str]) -> list[str]:
    result = subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    issues: list[str] = []
    label = " ".join(command[1:]) if len(command) > 1 else command[0]
    if result.returncode != 0:
        issues.append(f"guard_exit:{label}:returncode={result.returncode}")
    combined_output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
    for marker in required_markers:
        if marker not in combined_output:
            issues.append(f"guard_marker:{label}:{marker}")
    return issues


def required_files(root: Path) -> list[Path]:
    genksyms_bridge_dir = root / "zigux" / "tests" / "fixtures" / "genksyms_bridge"
    kconfig_bridge_dir = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge"
    files = [
        root / "scripts" / "zigux" / "fixdep.zig",
        root / "scripts" / "zigux" / "check-fixdep-diff.py",
        root / "scripts" / "zigux" / "genksyms.zig",
        root / "scripts" / "zigux" / "check-genksyms-bridge.py",
        root / "scripts" / "zigux" / "check-phase2-fixdep-gate.py",
        root / "scripts" / "zigux" / "check-phase2-genksyms-bridge-selftest-alignment.py",
        root / "scripts" / "zigux" / "genksyms_crc.zig",
        root / "scripts" / "zigux" / "check-genksyms-crc-diff.py",
        root / "scripts" / "zigux" / "check-kconfig-bridge.py",
        root / "scripts" / "zigux" / "check-phase2-cross.py",
        root / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py",
        root / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py",
        root / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py",
        root / "scripts" / "zigux" / "check-phase2-tool-manifest-packets.py",
        root / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py",
        root / "scripts" / "zigux" / "check-zig-toolchain.py",
        root / "scripts" / "zigux" / "install-zig.py",
        root / "scripts" / "zigux" / "mk_elfconfig.zig",
        root / "scripts" / "zigux" / "check-mk-elfconfig-diff.py",
        root / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig",
        root / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig",
        root / "Documentation" / "zigux" / "README.md",
        root / "Documentation" / "zigux" / "phase2-closure.md",
        root / "Documentation" / "zigux" / "review-checklist.md",
        root / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md",
        root / "Documentation" / "zigux" / "artifact-diff.md",
        root / "zigux" / "tests" / "README.md",
        root / "scripts" / "zigux" / "README.md",
        root / "scripts" / "zigux" / "validate-phase2.py",
        root / "scripts" / "zigux" / "validate-phase2-closure.py",
        root / "scripts" / "zigux" / "zig-toolchain-policy.json",
        root / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json",
        root / "zigux" / "tests" / "fixtures" / "phase2_artifact_tools_manifest.json",
        genksyms_bridge_dir / "manifest.json",
        kconfig_bridge_dir / "conf_manifest.json",
        kconfig_bridge_dir / "confdata_manifest.json",
        root / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "cases.json",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "manifest.json",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample.d",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample.c",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample.h",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample-config.h",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample.rmeta",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_expected.txt",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_escaped_space.d",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_escaped_space_expected.txt",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_escaped_colon.d",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_escaped_colon_source.c",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "shared:config.h",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_escaped_colon_expected.txt",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_multi_target.d",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample2.c",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample2-config.h",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample2.so",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "shared#config.h",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_multi_target_expected.txt",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_comment_only.d",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_comment_only_expected.txt",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_comment_only_expected.stderr.txt",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_missing_dep.d",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_missing_dep_source.c",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_missing_dep_expected.txt",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_missing_dep_expected.stderr.txt",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_escaped_hash_comment_chain.d",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_escaped_hash_comment_chain_expected.txt",
        root / "zigux" / "tests" / "fixtures" / "genksyms_crc" / "genksyms_crc_c_harness.c",
        root / "zigux" / "tests" / "fixtures" / "genksyms_crc" / "inputs.txt",
        root / "zigux" / "tests" / "fixtures" / "genksyms_crc" / "expected.json",
        genksyms_bridge_dir / "genksyms_bridge_c_harness.c",
        genksyms_bridge_dir / "cases.json",
        kconfig_bridge_dir / "cases.json",
        root / "zigux" / "tests" / "fixtures" / "mk_elfconfig" / "cases.json",
        root / "zigux" / "tests" / "fixtures" / "mk_elfconfig" / "elf32.hex",
        root / "zigux" / "tests" / "fixtures" / "mk_elfconfig" / "elf64.hex",
        root / "zigux" / "tests" / "fixtures" / "mk_elfconfig" / "invalid_class.hex",
        root / "zigux" / "tests" / "fixtures" / "mk_elfconfig" / "not_elf.hex",
        root / "zigux" / "tests" / "fixtures" / "mk_elfconfig" / "truncated.hex",
        root / "zigux" / "tests" / "fixtures" / "mk_elfconfig" / "elf32_expected.json",
        root / "zigux" / "tests" / "fixtures" / "mk_elfconfig" / "elf64_expected.json",
        root / "zigux" / "tests" / "fixtures" / "mk_elfconfig" / "invalid_class_expected.json",
        root / "zigux" / "tests" / "fixtures" / "mk_elfconfig" / "not_elf_expected.json",
        root / "zigux" / "tests" / "fixtures" / "mk_elfconfig" / "truncated_expected.json",
        root / "zigux-alpha" / "BOOTSTRAP_COMMIT_LEDGER.md",
        root / ".github" / "workflows" / "zigux-bootstrap.yml",
        root / "zigux" / "Makefile",
    ]
    files.extend(case_files_from_groups(genksyms_bridge_dir / "cases.json", ("cases", "expected")))
    files.extend(
        case_files_from_groups(
            kconfig_bridge_dir / "cases.json",
            ("conf_cases", "expected"),
            ("confdata_cases", "input"),
            ("confdata_cases", "expected"),
        )
    )
    return files


REQUIRED_LEDGER_MARKERS = [
    "feat(tools/lib): add phase-1 memory and formatting helper ports",
    "feat(scripts/zigux): add bounded Phase 2 fixdep dual-implementation lane",
    "test(zigux): widen bounded fixdep parity fixtures",
    "feat(scripts/zigux): start bounded Phase 2 genksyms lane",
    "feat(scripts/zigux): add bounded Phase 2 genksyms wrapper lane",
    "feat(scripts/zigux): add bounded Phase 2 kconfig bridge scaffolding",
    "feat(scripts/zigux): add bounded Phase 2 mk_elfconfig lane",
]

REQUIRED_WORKFLOW_MARKERS = [
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py",
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test",
    "python3 scripts/zigux/check-phase2-tool-manifest-packets.py",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "python3 scripts/zigux/check-fixdep-diff.py",
    "python3 scripts/zigux/check-genksyms-bridge.py",
    "python3 scripts/zigux/check-genksyms-crc-diff.py",
    "python3 scripts/zigux/check-kconfig-bridge.py",
    "python3 scripts/zigux/check-phase2-cross.py --target",
    "python3 scripts/zigux/check-mk-elfconfig-diff.py --self-test",
    "python3 scripts/zigux/check-mk-elfconfig-diff.py",
    "zig test scripts/zigux/fixdep.zig",
    "zig test scripts/zigux/genksyms.zig",
    "zig test scripts/zigux/genksyms_crc.zig",
    "zig test scripts/zigux/kconfig/conf_bridge.zig",
    "zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "zig test scripts/zigux/mk_elfconfig.zig",
]

REQUIRED_EXACT_WORKFLOW_RUN_COUNTS = {
    "python3 scripts/zigux/check-zig-toolchain.py --self-test": 1,
    "python3 scripts/zigux/check-zig-toolchain.py": 1,
    "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-fixdep-gate.py": 1,
    "python3 scripts/zigux/check-fixdep-diff.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py": 1,
    "python3 scripts/zigux/check-genksyms-bridge.py --self-test": 1,
    "python3 scripts/zigux/check-genksyms-bridge.py": 1,
    "python3 scripts/zigux/check-genksyms-crc-diff.py": 1,
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py": 1,
    "python3 scripts/zigux/validate-phase2.py": 1,
    "python3 scripts/zigux/validate-phase2-closure.py": 1,
    "python3 scripts/zigux/check-phase2-cross.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py": 1,
    "python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-tool-manifest-packets.py": 1,
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py": 1,
    "python3 scripts/zigux/check-kconfig-bridge.py --self-test": 1,
    "python3 scripts/zigux/check-mk-elfconfig-diff.py --self-test": 1,
    "python3 scripts/zigux/check-mk-elfconfig-diff.py": 1,
}

REQUIRED_DOC_MARKERS = [
    "fixdep",
    "sample_multi_target_expected.txt",
    "genksyms",
    "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
    "genksyms_crc",
    "zigux/tests/fixtures/genksyms_crc/expected.json",
    "kconfig_bridge",
    "mk_elfconfig",
    "elf32_expected.json",
]

REQUIRED_SCRIPT_MARKERS = [
    "check-zig-toolchain.py",
    "install-zig.py",
    "check-phase2-fixdep-gate.py",
    "check-phase2-tests-readme-alignment.py",
    "check-phase2-cross-selftest-alignment.py",
    "check-phase2-kconfig-selftest-alignment.py",
    "check-phase2-tool-manifest-packets.py",
    "check-phase2-toolchain-pin-scope.py",
    "validate-phase2.py",
    "validate-phase2-closure.py",
    "check-fixdep-diff.py",
    "check-genksyms-bridge.py",
    "check-genksyms-crc-diff.py",
    "check-kconfig-bridge.py",
    "check-phase2-cross.py",
    "genksyms.zig",
    "genksyms_crc.zig",
    "kconfig/conf_bridge.zig",
    "kconfig/confdata_bridge.zig",
    "check-mk-elfconfig-diff.py",
    "mk_elfconfig.zig",
]

REQUIRED_SCRIPT_HELPER_INDEX_MARKERS = [
    "- `check-kconfig-bridge.py`\n- `check-phase2-kconfig-selftest-alignment.py`\n- `check-phase2-tests-readme-alignment.py`\n- `check-phase2-cross-selftest-alignment.py`\n- `check-phase2-toolchain-pin-scope.py`\n- `check-phase2-cross.py`\n- `check-mk-elfconfig-diff.py`",
]

REQUIRED_DOCS_ROOT_MARKERS = [
    "Documentation/zigux/phase2-closure.md",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "python3 scripts/zigux/check-phase2-cross.py",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
]

REQUIRED_TOOLCHAIN_NOTES_MARKERS = [
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "python3 scripts/zigux/check-zig-toolchain.py",
    "make -C zigux phase2-toolchain",
]

REQUIRED_REVIEW_MARKERS = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-genksyms-crc-diff.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-mk-elfconfig-diff.py",
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/mk_elfconfig.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "make -C zigux phase2-validate",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2",
]

PHASE2_REVIEW_PACKET_LEAD = "if the change touches the shared Phase 2 toolchain packet"


def workflow_has_run_marker(workflow_run_lines: list[str], marker: str) -> bool:
    expected = f"run: {marker}"
    if marker.endswith("--target"):
        return any(line == expected or line.startswith(expected + " ") for line in workflow_run_lines)
    return expected in workflow_run_lines


def count_workflow_run_marker(workflow_run_lines: list[str], marker: str) -> int:
    expected = f"run: {marker}"
    if marker.endswith("--target"):
        return sum(1 for line in workflow_run_lines if line == expected or line.startswith(expected + " "))
    return sum(1 for line in workflow_run_lines if line == expected)


def count_marker_occurrences(text: str, marker: str) -> int:
    pattern = rf"(?<![A-Za-z0-9_./-]){re.escape(marker)}(?![A-Za-z0-9_./-])"
    return len(re.findall(pattern, text))


def extract_phase2_review_packet_line(review_checklist: str) -> str | None:
    for line in review_checklist.splitlines():
        if PHASE2_REVIEW_PACKET_LEAD in line:
            return line
    return None


def validate_exact_review_markers(text: str) -> list[str]:
    issues: list[str] = []
    for marker in REQUIRED_REVIEW_MARKERS:
        count = count_marker_occurrences(text, marker)
        if count != 1:
            issues.append(f"review_exact_marker:{marker}:count={count}:expected=1")
    return issues


def validate_exact_workflow_runs(workflow_run_lines: list[str]) -> list[str]:
    issues: list[str] = []
    for marker, expected in REQUIRED_EXACT_WORKFLOW_RUN_COUNTS.items():
        count = count_workflow_run_marker(workflow_run_lines, marker)
        if count != expected:
            issues.append(f"workflow_exact_marker:{marker}:count={count}:expected={expected}")
    return issues


def validate_root(root: Path) -> list[str]:
    missing = [str(path.relative_to(root)) for path in required_files(root) if not path.exists()]
    if missing:
        return [f"missing_file:{item}" for item in missing]

    ledger = (root / "zigux-alpha" / "BOOTSTRAP_COMMIT_LEDGER.md").read_text(encoding="utf-8")
    workflow = (root / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
    artifact_doc = (root / "Documentation" / "zigux" / "artifact-diff.md").read_text(encoding="utf-8")
    script_readme = (root / "scripts" / "zigux" / "README.md").read_text(encoding="utf-8")
    docs_root = (root / "Documentation" / "zigux" / "README.md").read_text(encoding="utf-8")
    toolchain_notes = (root / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md").read_text(encoding="utf-8")
    review_checklist = (root / "Documentation" / "zigux" / "review-checklist.md").read_text(encoding="utf-8")
    review_phase2_line = extract_phase2_review_packet_line(review_checklist)

    issues: list[str] = []
    for marker in REQUIRED_LEDGER_MARKERS:
        if marker not in ledger:
            issues.append(f"ledger:{marker}")

    workflow_run_lines = [line.strip() for line in workflow.splitlines()]
    for marker in REQUIRED_WORKFLOW_MARKERS:
        if not workflow_has_run_marker(workflow_run_lines, marker):
            issues.append(f"workflow:{marker}")
    issues.extend(validate_exact_workflow_runs(workflow_run_lines))

    for marker in REQUIRED_DOC_MARKERS:
        if marker not in artifact_doc:
            issues.append(f"doc:{marker}")
    for marker in REQUIRED_SCRIPT_MARKERS:
        if marker not in script_readme:
            issues.append(f"scripts:{marker}")
    for marker in REQUIRED_SCRIPT_HELPER_INDEX_MARKERS:
        if marker not in script_readme:
            issues.append("scripts_helper_index:phase2_helper_block")
    for marker in REQUIRED_DOCS_ROOT_MARKERS:
        if marker not in docs_root:
            issues.append(f"docs_root:{marker}")
    for marker in REQUIRED_TOOLCHAIN_NOTES_MARKERS:
        if marker not in toolchain_notes:
            issues.append(f"toolchain_notes:{marker}")
    if review_phase2_line is None:
        issues.append(f"review_packet:{PHASE2_REVIEW_PACKET_LEAD}")
    for marker in REQUIRED_REVIEW_MARKERS:
        if review_phase2_line is None or marker not in review_phase2_line:
            issues.append(f"review:{marker}")
    if review_phase2_line is not None:
        issues.extend(validate_exact_review_markers(review_phase2_line))
    if issues:
        return issues

    guard_issues: list[str] = []
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-fixdep-gate.py"), "--self-test"],
            ["PHASE2_FIXDEP_GATE_SELF_TEST=pass", "PHASE2_FIXDEP_GATE_SELF_TEST_CASE_COUNT=8"],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-fixdep-gate.py" )],
            ["PHASE2_FIXDEP_GATE=pass", "PHASE2_FIXDEP_GATE_WORKFLOW_MARKER_COUNT=5"],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-fixdep-diff.py"), "--self-test"],
            ["FIXDEP_DIFF_SELF_TEST=pass", "FIXDEP_DIFF_SELF_TEST_CASE_COUNT=2"],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-fixdep-diff.py")],
            ["FIXDEP_DIFF=pass", "FIXDEP_DETERMINISM=pass"],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-genksyms-bridge.py"), "--self-test"],
            ["GENKSYMS_BRIDGE_SELF_TEST=pass", "GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=8"],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-genksyms-bridge.py")],
            ["GENKSYMS_BRIDGE_DIFF=pass", "GENKSYMS_BRIDGE_DETERMINISM=pass", "FIXTURE_DIR="],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-genksyms-crc-diff.py")],
            ["GENKSYMS_CRC_DIFF=pass", "FIXTURE="],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-genksyms-bridge-selftest-alignment.py"), "--self-test"],
            [
                "PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST=pass",
                "PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT=25",
            ],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-genksyms-bridge-selftest-alignment.py")],
            ["PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT=pass"],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"), "--self-test"],
            ["PHASE2_TESTS_README_ALIGNMENT_SELF_TEST=pass", "PHASE2_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT=136"],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py")],
            ["PHASE2_TESTS_README_ALIGNMENT=pass", "PHASE2_TESTS_README_ALIGNMENT_MARKER_COUNT="],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"), "--self-test"],
            ["PHASE2_CROSS_SELFTEST_ALIGNMENT_SELF_TEST=pass"],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py")],
            ["PHASE2_CROSS_SELFTEST_ALIGNMENT=pass"],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-cross.py"), "--self-test"],
            ["PHASE2_CROSS_SELF_TEST=pass", "PHASE2_CROSS_SELF_TEST_CASE_COUNT=9"],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-cross.py")],
            ["PHASE2_CROSS=pass", "PHASE2_CROSS_TARGET_COUNT=", "PHASE2_CROSS_TOOL_COUNT="],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-tool-manifest-packets.py"), "--self-test"],
            ["PHASE2_TOOL_MANIFEST_PACKETS_SELF_TEST=pass", "PHASE2_TOOL_MANIFEST_PACKETS_SELF_TEST_CASE_COUNT=37"],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-tool-manifest-packets.py")],
            ["PHASE2_TOOL_MANIFEST_PACKETS=pass"],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"), "--self-test"],
            ["PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass", "PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST_CASE_COUNT=37"],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py")],
            ["PHASE2_TOOLCHAIN_PIN_SCOPE=pass"],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py"), "--self-test"],
            ["PHASE2_KCONFIG_ALIGNMENT_SELF_TEST=pass", "PHASE2_KCONFIG_ALIGNMENT_SELF_TEST_CASE_COUNT=64"],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py")],
            ["PHASE2_KCONFIG_ALIGNMENT=pass"],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-kconfig-bridge.py"), "--self-test"],
            ["KCONFIG_BRIDGE_SELF_TEST=pass", "KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT=21"],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-kconfig-bridge.py")],
            ["KCONFIG_BRIDGE_DIFF=pass", "FIXTURE_DIR="],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-mk-elfconfig-diff.py"), "--self-test"],
            ["MK_ELFCONFIG_SELF_TEST=pass", "MK_ELFCONFIG_SELF_TEST_CASE_COUNT=4"],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-mk-elfconfig-diff.py")],
            ["MK_ELFCONFIG_DIFF=pass", "FIXTURE_DIR="],
        )
    )
    return guard_issues


def run_self_test() -> int:
    helper_block = REQUIRED_SCRIPT_HELPER_INDEX_MARKERS[0]
    assert "`check-phase2-kconfig-selftest-alignment.py`" in helper_block
    assert helper_block.index("check-phase2-kconfig-selftest-alignment.py") < helper_block.index("check-phase2-tests-readme-alignment.py")
    assert "python3 scripts/zigux/check-fixdep-diff.py --self-test" in REQUIRED_WORKFLOW_MARKERS
    assert REQUIRED_EXACT_WORKFLOW_RUN_COUNTS["python3 scripts/zigux/check-fixdep-diff.py --self-test"] == 1
    assert "python3 scripts/zigux/check-genksyms-bridge.py" in REQUIRED_WORKFLOW_MARKERS
    assert REQUIRED_EXACT_WORKFLOW_RUN_COUNTS["python3 scripts/zigux/check-genksyms-bridge.py"] == 1
    assert "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test" in REQUIRED_WORKFLOW_MARKERS
    assert REQUIRED_EXACT_WORKFLOW_RUN_COUNTS["python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test"] == 1
    assert "python3 scripts/zigux/check-phase2-cross.py --self-test" in REQUIRED_WORKFLOW_MARKERS
    assert REQUIRED_EXACT_WORKFLOW_RUN_COUNTS["python3 scripts/zigux/check-phase2-cross.py --self-test"] == 1
    assert "python3 scripts/zigux/check-mk-elfconfig-diff.py --self-test" in REQUIRED_WORKFLOW_MARKERS
    assert REQUIRED_EXACT_WORKFLOW_RUN_COUNTS["python3 scripts/zigux/check-mk-elfconfig-diff.py --self-test"] == 1
    assert "python3 scripts/zigux/check-zig-toolchain.py" in REQUIRED_WORKFLOW_MARKERS
    assert REQUIRED_EXACT_WORKFLOW_RUN_COUNTS["python3 scripts/zigux/check-zig-toolchain.py"] == 1
    assert "python3 scripts/zigux/check-kconfig-bridge.py --self-test" in REQUIRED_WORKFLOW_MARKERS
    assert REQUIRED_EXACT_WORKFLOW_RUN_COUNTS["python3 scripts/zigux/check-kconfig-bridge.py --self-test"] == 1
    assert REQUIRED_TOOLCHAIN_NOTES_MARKERS == [
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
        "python3 scripts/zigux/check-zig-toolchain.py",
        "make -C zigux phase2-toolchain",
    ]
    assert "python3 scripts/zigux/check-zig-toolchain.py --self-test" in REQUIRED_REVIEW_MARKERS
    assert "scripts/zigux/check-genksyms-bridge.py" in REQUIRED_REVIEW_MARKERS
    assert "scripts/zigux/check-genksyms-crc-diff.py" in REQUIRED_REVIEW_MARKERS
    assert "scripts/zigux/check-kconfig-bridge.py" in REQUIRED_REVIEW_MARKERS
    assert "scripts/zigux/check-mk-elfconfig-diff.py" in REQUIRED_REVIEW_MARKERS
    assert "scripts/zigux/fixdep.zig" in REQUIRED_REVIEW_MARKERS
    assert "scripts/zigux/kconfig/confdata_bridge.zig" in REQUIRED_REVIEW_MARKERS
    assert "zigux/tests/fixtures/phase2_artifact_tools_manifest.json" in REQUIRED_REVIEW_MARKERS
    with tempfile.TemporaryDirectory(prefix="phase2_required_files_root_") as tmp_dir:
        temp_root = Path(tmp_dir)
        (temp_root / "zigux" / "tests" / "fixtures" / "genksyms_bridge").mkdir(parents=True)
        (temp_root / "zigux" / "tests" / "fixtures" / "kconfig_bridge").mkdir(parents=True)
        (temp_root / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "cases.json").write_text(
            '{"cases":[]}',
            encoding="utf-8",
        )
        (temp_root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json").write_text(
            '{"conf_cases":[],"confdata_cases":[]}',
            encoding="utf-8",
        )
        rooted_required_files = required_files(temp_root)
    assert rooted_required_files
    assert all(path.is_relative_to(temp_root) for path in rooted_required_files)
    review_line = (
        "  * if the change touches the shared Phase 2 toolchain packet, do "
        "`Documentation/zigux/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, "
        "`Documentation/zigux/phase2-closure.md`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase2_cross_targets.json`, "
        "`zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/README.md`, "
        "`scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/check-phase2-tool-manifest-packets.py`, "
        "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py`, "
        "`scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, "
        "`scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, "
        "`scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-fixdep-diff.py`, "
        "`scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-genksyms-crc-diff.py`, "
        "`scripts/zigux/check-kconfig-bridge.py`, `scripts/zigux/check-mk-elfconfig-diff.py`, "
        "`scripts/zigux/fixdep.zig`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_crc.zig`, "
        "`scripts/zigux/mk_elfconfig.zig`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, "
        "`python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`, "
        "`make -C zigux phase2-validate`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, "
        "`make -C zigux phase2-cross`, and `make -C zigux phase2` still agree "
        "on the same pinned toolchain and bounded kbuild-facing replay surface?"
    )
    issues = validate_exact_review_markers(review_line)
    assert issues == []
    with tempfile.TemporaryDirectory(prefix="phase2_validate_root_") as tmp_dir:
        temp_root = Path(tmp_dir)
        (temp_root / "zigux" / "tests" / "fixtures" / "genksyms_bridge").mkdir(parents=True)
        (temp_root / "zigux" / "tests" / "fixtures" / "kconfig_bridge").mkdir(parents=True)
        (temp_root / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "cases.json").write_text(
            '{"cases":[]}',
            encoding="utf-8",
        )
        (temp_root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json").write_text(
            '{"conf_cases":[],"confdata_cases":[]}',
            encoding="utf-8",
        )
        missing = validate_root(temp_root)
    assert missing
    assert missing[0] == "missing_file:scripts/zigux/fixdep.zig"
    print("PHASE2_VALIDATION_SELF_TEST=pass")
    print("PHASE2_VALIDATION_SELF_TEST_CASE_COUNT=11")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 2 toolchain packet.")
    parser.add_argument("--self-test", action="store_true", help="Run checkout-free validator self-tests.")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    missing = [str(path.relative_to(ROOT)) for path in required_files(ROOT) if not path.exists()]
    if missing:
        print("PHASE2_VALIDATION=fail")
        print("MISSING_PHASE2_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE2_FILES_END")
        return 1
    issues = validate_root(ROOT)
    if issues:
        prefix = "PHASE2_GUARD_ISSUES_START" if any(issue.startswith("guard_") for issue in issues) else "MISSING_PHASE2_MARKERS_START"
        suffix = "PHASE2_GUARD_ISSUES_END" if prefix == "PHASE2_GUARD_ISSUES_START" else "MISSING_PHASE2_MARKERS_END"
        print("PHASE2_VALIDATION=fail")
        print(prefix)
        for issue in issues:
            print(issue)
        print(suffix)
        return 1
    print("PHASE2_VALIDATION=pass")
    print(f"PHASE2_REQUIRED_FILE_COUNT={len(required_files(ROOT))}")
    print(
        "PHASE2_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_LEDGER_MARKERS) + len(REQUIRED_WORKFLOW_MARKERS) + len(REQUIRED_DOC_MARKERS) + len(REQUIRED_SCRIPT_MARKERS) + len(REQUIRED_SCRIPT_HELPER_INDEX_MARKERS) + len(REQUIRED_DOCS_ROOT_MARKERS) + len(REQUIRED_TOOLCHAIN_NOTES_MARKERS) + len(REQUIRED_REVIEW_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
