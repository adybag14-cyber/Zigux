#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
GENKSYMS_BRIDGE_DIR = ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge"
KCONFIG_BRIDGE_DIR = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge"
TESTS_README_ALIGNMENT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"
CHECK_PHASE2_CROSS_SELFTEST_ALIGNMENT = ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"
TOOLCHAIN_PIN_SCOPE_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"
GENKSYMS_BRIDGE_ALIGNMENT_CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-genksyms-bridge-selftest-alignment.py"
)


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
        root / "scripts" / "zigux" / "check-phase2-genksyms-bridge-selftest-alignment.py",
        root / "scripts" / "zigux" / "genksyms_crc.zig",
        root / "scripts" / "zigux" / "check-genksyms-crc-diff.py",
        root / "scripts" / "zigux" / "check-kconfig-bridge.py",
        root / "scripts" / "zigux" / "check-phase2-cross.py",
        root / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py",
        root / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py",
        root / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py",
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
        root / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "cases.json",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample.d",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample.c",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample.h",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample-config.h",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample.rmeta",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_expected.txt",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_multi_target.d",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample2.c",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample2-config.h",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample2.so",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "shared#config.h",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_multi_target_expected.txt",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_missing_dep.d",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_missing_dep_source.c",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_missing_dep_expected.txt",
        root / "zigux" / "tests" / "fixtures" / "fixdep" / "sample_missing_dep_expected.stderr.txt",
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
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "python3 scripts/zigux/check-fixdep-diff.py",
    "python3 scripts/zigux/check-genksyms-bridge.py",
    "python3 scripts/zigux/check-genksyms-crc-diff.py",
    "python3 scripts/zigux/check-kconfig-bridge.py",
    "python3 scripts/zigux/check-phase2-cross.py --target",
    "python3 scripts/zigux/check-mk-elfconfig-diff.py",
    "zig test scripts/zigux/fixdep.zig",
    "zig test scripts/zigux/genksyms.zig",
    "zig test scripts/zigux/genksyms_crc.zig",
    "zig test scripts/zigux/kconfig/conf_bridge.zig",
    "zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "zig test scripts/zigux/mk_elfconfig.zig",
]
REQUIRED_EXACT_WORKFLOW_RUN_COUNTS = {
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py": 1,
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py": 1,
    "python3 scripts/zigux/check-phase2-cross.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py": 1,
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py": 1,
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
    "check-phase2-tests-readme-alignment.py",
    "check-phase2-cross-selftest-alignment.py",
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
    "- `check-kconfig-bridge.py`\n- `check-phase2-tests-readme-alignment.py`\n- `check-phase2-cross-selftest-alignment.py`\n- `check-phase2-toolchain-pin-scope.py`\n- `check-phase2-cross.py`\n- `check-mk-elfconfig-diff.py`",
]
REQUIRED_DOCS_ROOT_MARKERS = [
    "Documentation/zigux/phase2-closure.md",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "python3 scripts/zigux/check-phase2-cross.py",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
]
REQUIRED_REVIEW_MARKERS = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "make -C zigux phase2-validate",
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


def build_phase2_review_checklist_line(markers: list[str]) -> str:
    quoted_markers = ", ".join(f"`{marker}`" for marker in markers[:-2])
    return (
        f"  * {PHASE2_REVIEW_PACKET_LEAD}, do {quoted_markers}, "
        f"and `{markers[-2]}` plus `{markers[-1]}` still agree on the same pinned toolchain "
        "and bounded kbuild-facing replay surface?\n"
    )


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
    review_checklist = (root / "Documentation" / "zigux" / "review-checklist.md").read_text(encoding="utf-8")
    review_phase2_line = extract_phase2_review_packet_line(review_checklist)

    missing_markers = []
    for marker in REQUIRED_LEDGER_MARKERS:
        if marker not in ledger:
            missing_markers.append(f"ledger:{marker}")
    workflow_run_lines = [line.strip() for line in workflow.splitlines()]
    for marker in REQUIRED_WORKFLOW_MARKERS:
        if not workflow_has_run_marker(workflow_run_lines, marker):
            missing_markers.append(f"workflow:{marker}")
    missing_markers.extend(validate_exact_workflow_runs(workflow_run_lines))
    for marker in REQUIRED_DOC_MARKERS:
        if marker not in artifact_doc:
            missing_markers.append(f"doc:{marker}")
    for marker in REQUIRED_SCRIPT_MARKERS:
        if marker not in script_readme:
            missing_markers.append(f"scripts:{marker}")
    for marker in REQUIRED_SCRIPT_HELPER_INDEX_MARKERS:
        if marker not in script_readme:
            missing_markers.append("scripts_helper_index:phase2_helper_block")
    for marker in REQUIRED_DOCS_ROOT_MARKERS:
        if marker not in docs_root:
            missing_markers.append(f"docs_root:{marker}")
    if review_phase2_line is None:
        missing_markers.append(f"review_packet:{PHASE2_REVIEW_PACKET_LEAD}")
    for marker in REQUIRED_REVIEW_MARKERS:
        if review_phase2_line is None or marker not in review_phase2_line:
            missing_markers.append(f"review:{marker}")
    if review_phase2_line is not None:
        missing_markers.extend(validate_exact_review_markers(review_phase2_line))
    if missing_markers:
        return missing_markers

    guard_issues: list[str] = []
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-fixdep-diff.py"), "--self-test"],
            [
                "FIXDEP_DIFF_SELF_TEST=pass",
                "FIXDEP_DIFF_SELF_TEST_CASE_COUNT=4",
            ],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-fixdep-diff.py")],
            [
                "FIXDEP_DIFF=pass",
                "FIXDEP_DETERMINISM=pass",
            ],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-genksyms-bridge.py"), "--self-test"],
            [
                "GENKSYMS_BRIDGE_SELF_TEST=pass",
                "GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=6",
            ],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-genksyms-bridge-selftest-alignment.py"), "--self-test"],
            [
                "PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST=pass",
                "PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT=4",
            ],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-genksyms-bridge-selftest-alignment.py")],
            [
                "PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT=pass",
            ],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"), "--self-test"],
            [
                "PHASE2_TESTS_README_ALIGNMENT_SELF_TEST=pass",
                "PHASE2_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT=25",
            ],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py")],
            [
                "PHASE2_TESTS_README_ALIGNMENT=pass",
                "PHASE2_TESTS_README_ALIGNMENT_MARKER_COUNT=",
            ],
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
            [sys.executable, str(root / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"), "--self-test"],
            [
                "PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass",
                "PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST_CASE_COUNT=31",
            ],
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
            [
                "PHASE2_KCONFIG_ALIGNMENT_SELF_TEST=pass",
                "PHASE2_KCONFIG_ALIGNMENT_SELF_TEST_CASE_COUNT=8",
            ],
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
            [
                "KCONFIG_BRIDGE_SELF_TEST=pass",
                "KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT=5",
            ],
        )
    )
    guard_issues.extend(
        run_guard(
            root,
            [sys.executable, str(root / "scripts" / "zigux" / "check-mk-elfconfig-diff.py"), "--self-test"],
            [
                "MK_ELFCONFIG_SELF_TEST=pass",
                "MK_ELFCONFIG_SELF_TEST_CASE_COUNT=4",
            ],
        )
    )
    return guard_issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_stub_guard(path: Path, *, self_test_marker: str, live_markers: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "#!/usr/bin/env python3",
        "import sys",
        "if '--self-test' in sys.argv:",
    ]
    for line in self_test_marker.split("\n"):
        lines.append(f"    print({line!r})")
    lines.extend(
        [
            "else:",
        ]
    )
    for marker in live_markers:
        lines.append(f"    print({marker!r})")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_script_readme_text() -> str:
    return "\n".join(REQUIRED_SCRIPT_MARKERS) + "\n\n" + REQUIRED_SCRIPT_HELPER_INDEX_MARKERS[0] + "\n"


def build_self_test_root(root: Path) -> None:
    base_files = [
        "scripts/zigux/fixdep.zig",
        "scripts/zigux/genksyms.zig",
        "scripts/zigux/genksyms_crc.zig",
        "scripts/zigux/mk_elfconfig.zig",
        "scripts/zigux/kconfig/conf_bridge.zig",
        "scripts/zigux/kconfig/confdata_bridge.zig",
        "Documentation/zigux/README.md",
        "Documentation/zigux/phase2-closure.md",
        "Documentation/zigux/review-checklist.md",
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        "Documentation/zigux/artifact-diff.md",
        "zigux/tests/README.md",
        "scripts/zigux/README.md",
        "scripts/zigux/validate-phase2.py",
        "scripts/zigux/validate-phase2-closure.py",
        "scripts/zigux/zig-toolchain-policy.json",
        "zigux/tests/fixtures/phase2_cross_targets.json",
        "zigux/tests/fixtures/fixdep/cases.json",
        "zigux/tests/fixtures/fixdep/sample.d",
        "zigux/tests/fixtures/fixdep/sample.c",
        "zigux/tests/fixtures/fixdep/sample.h",
        "zigux/tests/fixtures/fixdep/sample-config.h",
        "zigux/tests/fixtures/fixdep/sample.rmeta",
        "zigux/tests/fixtures/fixdep/sample_expected.txt",
        "zigux/tests/fixtures/fixdep/sample_multi_target.d",
        "zigux/tests/fixtures/fixdep/sample2.c",
        "zigux/tests/fixtures/fixdep/sample2-config.h",
        "zigux/tests/fixtures/fixdep/sample2.so",
        "zigux/tests/fixtures/fixdep/shared#config.h",
        "zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt",
        "zigux/tests/fixtures/fixdep/sample_missing_dep.d",
        "zigux/tests/fixtures/fixdep/sample_missing_dep_source.c",
        "zigux/tests/fixtures/fixdep/sample_missing_dep_expected.txt",
        "zigux/tests/fixtures/fixdep/sample_missing_dep_expected.stderr.txt",
        "zigux/tests/fixtures/genksyms_crc/genksyms_crc_c_harness.c",
        "zigux/tests/fixtures/genksyms_crc/inputs.txt",
        "zigux/tests/fixtures/genksyms_crc/expected.json",
        "zigux/tests/fixtures/genksyms_bridge/genksyms_bridge_c_harness.c",
        "zigux/tests/fixtures/genksyms_bridge/cases.json",
        "zigux/tests/fixtures/kconfig_bridge/cases.json",
        "zigux/tests/fixtures/mk_elfconfig/cases.json",
        "zigux/tests/fixtures/mk_elfconfig/elf32.hex",
        "zigux/tests/fixtures/mk_elfconfig/elf64.hex",
        "zigux/tests/fixtures/mk_elfconfig/invalid_class.hex",
        "zigux/tests/fixtures/mk_elfconfig/not_elf.hex",
        "zigux/tests/fixtures/mk_elfconfig/truncated.hex",
        "zigux/tests/fixtures/mk_elfconfig/elf32_expected.json",
        "zigux/tests/fixtures/mk_elfconfig/elf64_expected.json",
        "zigux/tests/fixtures/mk_elfconfig/invalid_class_expected.json",
        "zigux/tests/fixtures/mk_elfconfig/not_elf_expected.json",
        "zigux/tests/fixtures/mk_elfconfig/truncated_expected.json",
        "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
        ".github/workflows/zigux-bootstrap.yml",
        "zigux/Makefile",
    ]
    for rel in base_files:
        write_text(root / rel, "\n")
    write_text(root / "zigux/tests/fixtures/phase2_tool_manifest.json", json.dumps({"phase": "Phase 2", "status": "closed", "tool_count": 6, "tools": ["scripts/zigux/fixdep.zig", "scripts/zigux/genksyms.zig", "scripts/zigux/genksyms_crc.zig", "scripts/zigux/mk_elfconfig.zig", "scripts/zigux/kconfig/conf_bridge.zig", "scripts/zigux/kconfig/confdata_bridge.zig"]}, indent=2) + "\n")
    write_text(root / "zigux/tests/fixtures/genksyms_bridge/cases.json", json.dumps({"cases": [{"expected": "minimal_expected.json"}]}, indent=2) + "\n")
    write_text(root / "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json", "{}\n")
    write_text(root / "zigux/tests/fixtures/kconfig_bridge/cases.json", json.dumps({"conf_cases": [{"expected": "olddefconfig_expected.json"}], "confdata_cases": [{"input": "sample.config", "expected": "sample_expected.json"}]}, indent=2) + "\n")
    write_text(root / "zigux/tests/fixtures/kconfig_bridge/olddefconfig_expected.json", "{}\n")
    write_text(root / "zigux/tests/fixtures/kconfig_bridge/sample.config", "\n")
    write_text(root / "zigux/tests/fixtures/kconfig_bridge/sample_expected.json", "{}\n")
    write_text(root / "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", "\n".join(REQUIRED_LEDGER_MARKERS) + "\n")
    write_text(root / ".github/workflows/zigux-bootstrap.yml", "\n".join(f"run: {marker}" for marker in REQUIRED_WORKFLOW_MARKERS) + "\n")
    write_text(root / "Documentation/zigux/artifact-diff.md", "\n".join(REQUIRED_DOC_MARKERS) + "\n")
    write_text(root / "scripts/zigux/README.md", build_script_readme_text())
    write_text(root / "Documentation/zigux/README.md", "\n".join(REQUIRED_DOCS_ROOT_MARKERS) + "\n")
    write_text(root / "Documentation/zigux/review-checklist.md", build_phase2_review_checklist_line(REQUIRED_REVIEW_MARKERS))
    write_stub_guard(root / "scripts/zigux/check-fixdep-diff.py", self_test_marker="FIXDEP_DIFF_SELF_TEST=pass\nFIXDEP_DIFF_SELF_TEST_CASE_COUNT=4", live_markers=["FIXDEP_DIFF=pass", "FIXDEP_DETERMINISM=pass"])
    write_stub_guard(root / "scripts/zigux/check-genksyms-bridge.py", self_test_marker="GENKSYMS_BRIDGE_SELF_TEST=pass\nGENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=6", live_markers=["GENKSYMS_BRIDGE_DIFF=pass"])
    write_stub_guard(root / "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py", self_test_marker="PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST=pass\nPHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT=4", live_markers=["PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT=pass"])
    write_stub_guard(root / "scripts/zigux/check-phase2-tests-readme-alignment.py", self_test_marker="PHASE2_TESTS_README_ALIGNMENT_SELF_TEST=pass\nPHASE2_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT=25", live_markers=["PHASE2_TESTS_README_ALIGNMENT=pass", "PHASE2_TESTS_README_ALIGNMENT_MARKER_COUNT=1"])
    write_stub_guard(root / "scripts/zigux/check-phase2-cross-selftest-alignment.py", self_test_marker="PHASE2_CROSS_SELFTEST_ALIGNMENT_SELF_TEST=pass", live_markers=["PHASE2_CROSS_SELFTEST_ALIGNMENT=pass"])
    write_stub_guard(root / "scripts/zigux/check-phase2-toolchain-pin-scope.py", self_test_marker="PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass\nPHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST_CASE_COUNT=31", live_markers=["PHASE2_TOOLCHAIN_PIN_SCOPE=pass"])
    write_stub_guard(root / "scripts/zigux/check-phase2-kconfig-selftest-alignment.py", self_test_marker="PHASE2_KCONFIG_ALIGNMENT_SELF_TEST=pass\nPHASE2_KCONFIG_ALIGNMENT_SELF_TEST_CASE_COUNT=8", live_markers=["PHASE2_KCONFIG_ALIGNMENT=pass"])
    write_stub_guard(root / "scripts/zigux/check-kconfig-bridge.py", self_test_marker="KCONFIG_BRIDGE_SELF_TEST=pass\nKCONFIG_BRIDGE_SELF_TEST_CASE_COUNT=5", live_markers=["KCONFIG_BRIDGE_DIFF=pass"])
    write_stub_guard(root / "scripts/zigux/check-mk-elfconfig-diff.py", self_test_marker="MK_ELFCONFIG_SELF_TEST=pass\nMK_ELFCONFIG_SELF_TEST_CASE_COUNT=4", live_markers=["MK_ELFCONFIG_DIFF=pass"])


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase2_validate_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert validate_root(root) == []
        build_self_test_root(root)
        workflow_path = root / ".github" / "workflows" / "zigux-bootstrap.yml"
        workflow_text = workflow_path.read_text(encoding="utf-8").replace("run: python3 scripts/zigux/check-phase2-cross.py --target\n", "run: python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}\n")
        write_text(workflow_path, workflow_text)
        assert validate_root(root) == []
        build_self_test_root(root)
        workflow_text = workflow_path.read_text(encoding="utf-8").replace("run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test\n", "", 1)
        write_text(workflow_path, workflow_text)
        issues = validate_root(root)
        assert "workflow:python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test" in issues
        build_self_test_root(root)
        workflow_text = workflow_path.read_text(encoding="utf-8").replace("run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test\n", "run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test\nrun: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test\n", 1)
        write_text(workflow_path, workflow_text)
        issues = validate_root(root)
        assert "workflow_exact_marker:python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test:count=2:expected=1" in issues
        build_self_test_root(root)
        workflow_text = workflow_path.read_text(encoding="utf-8").replace("run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py\n", "run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py\nrun: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py\n", 1)
        write_text(workflow_path, workflow_text)
        issues = validate_root(root)
        assert "workflow_exact_marker:python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py:count=2:expected=1" in issues
        build_self_test_root(root)
        workflow_text = workflow_path.read_text(encoding="utf-8").replace("run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py\n", "", 1)
        write_text(workflow_path, workflow_text)
        issues = validate_root(root)
        assert "workflow:python3 scripts/zigux/check-phase2-tests-readme-alignment.py" in issues
        build_self_test_root(root)
        workflow_text = workflow_path.read_text(encoding="utf-8").replace("run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py\n", "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py\nrun: python3 scripts/zigux/check-phase2-tests-readme-alignment.py\n", 1)
        write_text(workflow_path, workflow_text)
        issues = validate_root(root)
        assert "workflow_exact_marker:python3 scripts/zigux/check-phase2-tests-readme-alignment.py:count=2:expected=1" in issues
        build_self_test_root(root)
        workflow_text = workflow_path.read_text(encoding="utf-8").replace("run: python3 scripts/zigux/check-phase2-cross.py --self-test\n", "run: python3 scripts/zigux/check-phase2-cross.py --self-test\nrun: python3 scripts/zigux/check-phase2-cross.py --self-test\n", 1)
        write_text(workflow_path, workflow_text)
        issues = validate_root(root)
        assert "workflow_exact_marker:python3 scripts/zigux/check-phase2-cross.py --self-test:count=2:expected=1" in issues
        build_self_test_root(root)
        workflow_text = workflow_path.read_text(encoding="utf-8").replace("run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test\n", "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test\nrun: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test\n", 1)
        write_text(workflow_path, workflow_text)
        issues = validate_root(root)
        assert "workflow_exact_marker:python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test:count=2:expected=1" in issues
        build_self_test_root(root)
        workflow_text = workflow_path.read_text(encoding="utf-8").replace("run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py\n", "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py\nrun: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py\n", 1)
        write_text(workflow_path, workflow_text)
        issues = validate_root(root)
        assert "workflow_exact_marker:python3 scripts/zigux/check-phase2-cross-selftest-alignment.py:count=2:expected=1" in issues
        build_self_test_root(root)
        workflow_text = workflow_path.read_text(encoding="utf-8").replace("run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test\n", "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test\nrun: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test\n", 1)
        write_text(workflow_path, workflow_text)
        issues = validate_root(root)
        assert "workflow_exact_marker:python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test:count=2:expected=1" in issues
        build_self_test_root(root)
        workflow_text = workflow_path.read_text(encoding="utf-8").replace("run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py\n", "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py\nrun: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py\n", 1)
        write_text(workflow_path, workflow_text)
        issues = validate_root(root)
        assert "workflow_exact_marker:python3 scripts/zigux/check-phase2-toolchain-pin-scope.py:count=2:expected=1" in issues
        build_self_test_root(root)
        workflow_text = workflow_path.read_text(encoding="utf-8").replace("run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test\n", "", 1)
        write_text(workflow_path, workflow_text)
        issues = validate_root(root)
        assert "workflow:python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test" in issues
        build_self_test_root(root)
        workflow_text = workflow_path.read_text(encoding="utf-8").replace("run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test\n", "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test\nrun: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test\n", 1)
        write_text(workflow_path, workflow_text)
        issues = validate_root(root)
        assert "workflow_exact_marker:python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test:count=2:expected=1" in issues
        build_self_test_root(root)
        workflow_text = workflow_path.read_text(encoding="utf-8").replace("run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py\n", "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py\nrun: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py\n", 1)
        write_text(workflow_path, workflow_text)
        issues = validate_root(root)
        assert "workflow_exact_marker:python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py:count=2:expected=1" in issues
        build_self_test_root(root)
        workflow_text = workflow_path.read_text(encoding="utf-8").replace("run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test\n", "", 1)
        write_text(workflow_path, workflow_text)
        issues = validate_root(root)
        assert "workflow:python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test" in issues
        build_self_test_root(root)
        workflow_text = workflow_path.read_text(encoding="utf-8").replace("run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py\n", "", 1)
        write_text(workflow_path, workflow_text)
        issues = validate_root(root)
        assert "workflow:python3 scripts/zigux/check-phase2-toolchain-pin-scope.py" in issues
        build_self_test_root(root)
        workflow_text = workflow_path.read_text(encoding="utf-8").replace("run: python3 scripts/zigux/check-phase2-cross.py --self-test\n", "", 1)
        write_text(workflow_path, workflow_text)
        issues = validate_root(root)
        assert "workflow:python3 scripts/zigux/check-phase2-cross.py --self-test" in issues
        build_self_test_root(root)
        (root / "zigux/tests/fixtures/phase2_tool_manifest.json").unlink()
        issues = validate_root(root)
        assert "missing_file:zigux/tests/fixtures/phase2_tool_manifest.json" in issues
        build_self_test_root(root)
        (root / "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py").unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py" in issues
        build_self_test_root(root)
        (root / "scripts/zigux/check-phase2-kconfig-selftest-alignment.py").unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/check-phase2-kconfig-selftest-alignment.py" in issues
        build_self_test_root(root)
        write_text(root / "Documentation/zigux/review-checklist.md", build_phase2_review_checklist_line(REQUIRED_REVIEW_MARKERS[1:]))
        issues = validate_root(root)
        assert "review:Documentation/zigux/README.md" in issues
        build_self_test_root(root)
        write_text(root / "Documentation/zigux/review-checklist.md", build_phase2_review_checklist_line([REQUIRED_REVIEW_MARKERS[0], *REQUIRED_REVIEW_MARKERS[2:]]))
        issues = validate_root(root)
        assert "review:Documentation/zigux/phase2-toolchain-bootstrap-notes.md" in issues
        build_self_test_root(root)
        write_text(root / "Documentation/zigux/review-checklist.md", build_phase2_review_checklist_line([*REQUIRED_REVIEW_MARKERS[:2], *REQUIRED_REVIEW_MARKERS[3:]]))
        issues = validate_root(root)
        assert "review:Documentation/zigux/phase2-closure.md" in issues
        build_self_test_root(root)
        write_text(root / "Documentation/zigux/review-checklist.md", build_phase2_review_checklist_line(REQUIRED_REVIEW_MARKERS[:7] + REQUIRED_REVIEW_MARKERS[8:]))
        issues = validate_root(root)
        assert "review:scripts/zigux/validate-phase2-closure.py" in issues
        build_self_test_root(root)
        write_text(root / "Documentation/zigux/review-checklist.md", build_phase2_review_checklist_line(REQUIRED_REVIEW_MARKERS[:-2]))
        issues = validate_root(root)
        assert "review:make -C zigux phase2-validate" in issues
        assert "review:make -C zigux phase2" in issues
        build_self_test_root(root)
        write_text(root / "Documentation/zigux/review-checklist.md", build_phase2_review_checklist_line(REQUIRED_REVIEW_MARKERS[:8] + REQUIRED_REVIEW_MARKERS[9:]))
        issues = validate_root(root)
        assert "review:scripts/zigux/check-phase2-tests-readme-alignment.py" in issues
        build_self_test_root(root)
        write_text(root / "Documentation/zigux/review-checklist.md", build_phase2_review_checklist_line(REQUIRED_REVIEW_MARKERS + [REQUIRED_REVIEW_MARKERS[4]]))
        issues = validate_root(root)
        assert "review_exact_marker:zigux/tests/fixtures/phase2_cross_targets.json:count=2:expected=1" in issues
        build_self_test_root(root)
        write_text(root / "Documentation/zigux/review-checklist.md", build_phase2_review_checklist_line(REQUIRED_REVIEW_MARKERS + [REQUIRED_REVIEW_MARKERS[-1]]))
        issues = validate_root(root)
        assert "review_exact_marker:make -C zigux phase2:count=2:expected=1" in issues
        build_self_test_root(root)
        write_text(root / "Documentation/zigux/README.md", "\n".join(marker for marker in REQUIRED_DOCS_ROOT_MARKERS if marker != "scripts/zigux/check-phase2-toolchain-pin-scope.py") + "\n")
        issues = validate_root(root)
        assert "docs_root:scripts/zigux/check-phase2-toolchain-pin-scope.py" in issues
        build_self_test_root(root)
        checker_path = root / "scripts" / "zigux" / "check-fixdep-diff.py"
        write_stub_guard(checker_path, self_test_marker="FIXDEP_DIFF_SELF_TEST=pass", live_markers=["FIXDEP_DIFF=pass", "FIXDEP_DETERMINISM=pass"])
        issues = validate_root(root)
        assert any(issue.startswith("guard_marker:") and "check-fixdep-diff.py --self-test:FIXDEP_DIFF_SELF_TEST_CASE_COUNT=4" in issue for issue in issues)
        build_self_test_root(root)
        checker_path = root / "scripts" / "zigux" / "check-genksyms-bridge.py"
        write_stub_guard(checker_path, self_test_marker="GENKSYMS_BRIDGE_SELF_TEST=pass", live_markers=["GENKSYMS_BRIDGE_DIFF=pass"])
        issues = validate_root(root)
        assert any(issue.startswith("guard_marker:") and "check-genksyms-bridge.py --self-test:GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=6" in issue for issue in issues)
        build_self_test_root(root)
        checker_path = root / "scripts" / "zigux" / "check-phase2-genksyms-bridge-selftest-alignment.py"
        write_stub_guard(checker_path, self_test_marker="PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST=pass", live_markers=["PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT=pass"])
        issues = validate_root(root)
        assert any(issue.startswith("guard_marker:") and "check-phase2-genksyms-bridge-selftest-alignment.py --self-test:PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT=4" in issue for issue in issues)
        build_self_test_root(root)
        checker_path = root / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"
        write_stub_guard(checker_path, self_test_marker="PHASE2_TESTS_README_ALIGNMENT_SELF_TEST=pass", live_markers=["PHASE2_TESTS_README_ALIGNMENT=pass"])
        issues = validate_root(root)
        assert any(issue.startswith("guard_marker:") for issue in issues)
        build_self_test_root(root)
        checker_path = root / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py"
        write_stub_guard(checker_path, self_test_marker="PHASE2_KCONFIG_ALIGNMENT_SELF_TEST=pass", live_markers=["PHASE2_KCONFIG_ALIGNMENT=pass"])
        issues = validate_root(root)
        assert any(issue.startswith("guard_marker:") and "check-phase2-kconfig-selftest-alignment.py --self-test:PHASE2_KCONFIG_ALIGNMENT_SELF_TEST_CASE_COUNT=8" in issue for issue in issues)
        build_self_test_root(root)
        write_text(root / "scripts/zigux/README.md", build_script_readme_text().replace("- `check-phase2-cross-selftest-alignment.py`\n", ""))
        issues = validate_root(root)
        assert "scripts_helper_index:phase2_helper_block" in issues
        build_self_test_root(root)
        checker_path = root / "scripts" / "zigux" / "check-kconfig-bridge.py"
        write_stub_guard(checker_path, self_test_marker="KCONFIG_BRIDGE_SELF_TEST=pass", live_markers=["KCONFIG_BRIDGE_DIFF=pass"])
        issues = validate_root(root)
        assert any(issue.startswith("guard_marker:") and "check-kconfig-bridge.py --self-test:KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT=5" in issue for issue in issues)
        build_self_test_root(root)
        checker_path = root / "scripts" / "zigux" / "check-mk-elfconfig-diff.py"
        write_stub_guard(checker_path, self_test_marker="MK_ELFCONFIG_SELF_TEST=pass", live_markers=["MK_ELFCONFIG_DIFF=pass"])
        issues = validate_root(root)
        assert any(issue.startswith("guard_marker:") and "check-mk-elfconfig-diff.py --self-test:MK_ELFCONFIG_SELF_TEST_CASE_COUNT=4" in issue for issue in issues)
    print("PHASE2_VALIDATION_SELF_TEST=pass")
    print("PHASE2_VALIDATION_SELF_TEST_CASE_COUNT=38")
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
    print("PHASE2_REQUIRED_MARKER_COUNT=" f"{len(REQUIRED_LEDGER_MARKERS) + len(REQUIRED_WORKFLOW_MARKERS) + len(REQUIRED_DOC_MARKERS) + len(REQUIRED_SCRIPT_MARKERS) + len(REQUIRED_SCRIPT_HELPER_INDEX_MARKERS) + len(REQUIRED_DOCS_ROOT_MARKERS) + len(REQUIRED_REVIEW_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
