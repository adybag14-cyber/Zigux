#!/usr/bin/env python3
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
GENKSYMS_BRIDGE_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge'
KCONFIG_BRIDGE_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'kconfig_bridge'
TESTS_README_ALIGNMENT_CHECKER = ROOT / 'scripts' / 'zigux' / 'check-phase2-tests-readme-alignment.py'
CHECK_PHASE2_CROSS_SELFTEST_ALIGNMENT = ROOT / 'scripts' / 'zigux' / 'check-phase2-cross-selftest-alignment.py'
TOOLCHAIN_PIN_SCOPE_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"


def case_files_from_groups(case_manifest: Path, *group_specs: tuple[str, str]) -> list[Path]:
    cases = json.loads(case_manifest.read_text(encoding='utf-8'))
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


def run_guard(command: list[str], required_markers: list[str]) -> list[str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    issues: list[str] = []
    label = " ".join(command[1:]) if len(command) > 1 else command[0]
    if result.returncode != 0:
        issues.append(f'guard_exit:{label}:returncode={result.returncode}')
    combined_output = "\n".join(
        part for part in (result.stdout.strip(), result.stderr.strip()) if part
    )
    for marker in required_markers:
        if marker not in combined_output:
            issues.append(f'guard_marker:{label}:{marker}')
    return issues


required_files = [
    ROOT / 'scripts' / 'zigux' / 'fixdep.zig',
    ROOT / 'scripts' / 'zigux' / 'check-fixdep-diff.py',
    ROOT / 'scripts' / 'zigux' / 'genksyms.zig',
    ROOT / 'scripts' / 'zigux' / 'check-genksyms-bridge.py',
    ROOT / 'scripts' / 'zigux' / 'genksyms_crc.zig',
    ROOT / 'scripts' / 'zigux' / 'check-genksyms-crc-diff.py',
    ROOT / 'scripts' / 'zigux' / 'check-kconfig-bridge.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase2-cross.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase2-cross-selftest-alignment.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase2-tests-readme-alignment.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase2-toolchain-pin-scope.py',
    ROOT / 'scripts' / 'zigux' / 'mk_elfconfig.zig',
    ROOT / 'scripts' / 'zigux' / 'check-mk-elfconfig-diff.py',
    ROOT / 'scripts' / 'zigux' / 'kconfig' / 'conf_bridge.zig',
    ROOT / 'scripts' / 'zigux' / 'kconfig' / 'confdata_bridge.zig',
    ROOT / 'Documentation' / 'zigux' / 'README.md',
    ROOT / 'Documentation' / 'zigux' / 'review-checklist.md',
    ROOT / 'Documentation' / 'zigux' / 'phase2-toolchain-bootstrap-notes.md',
    ROOT / 'zigux' / 'tests' / 'README.md',
    ROOT / 'scripts' / 'zigux' / 'zig-toolchain-policy.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_cross_targets.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'cases.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample.d',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample.h',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample-config.h',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample.rmeta',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample_expected.txt',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample_multi_target.d',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample2.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample2-config.h',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample2.so',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'shared#config.h',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample_multi_target_expected.txt',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample_missing_dep.d',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample_missing_dep_source.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample_missing_dep_expected.txt',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'sample_missing_dep_expected.stderr.txt',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_crc' / 'genksyms_crc_c_harness.c',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_crc' / 'inputs.txt',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_crc' / 'expected.json',
    GENKSYMS_BRIDGE_DIR / 'genksyms_bridge_c_harness.c',
    GENKSYMS_BRIDGE_DIR / 'cases.json',
    KCONFIG_BRIDGE_DIR / 'cases.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'cases.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'elf32.hex',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'elf64.hex',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'invalid_class.hex',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'not_elf.hex',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'truncated.hex',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'elf32_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'elf64_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'invalid_class_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'not_elf_expected.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig' / 'truncated_expected.json',
]
required_files.extend(case_files_from_groups(GENKSYMS_BRIDGE_DIR / 'cases.json', ('cases', 'expected')))
required_files.extend(case_files_from_groups(
    KCONFIG_BRIDGE_DIR / 'cases.json',
    ('conf_cases', 'expected'),
    ('confdata_cases', 'input'),
    ('confdata_cases', 'expected'),
))

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print('PHASE2_VALIDATION=fail')
    print('MISSING_PHASE2_FILES_START')
    for item in missing:
        print(item)
    print('MISSING_PHASE2_FILES_END')
    sys.exit(1)

ledger = (ROOT / 'zigux-alpha' / 'BOOTSTRAP_COMMIT_LEDGER.md').read_text(encoding='utf-8')
workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
artifact_doc = (ROOT / 'Documentation' / 'zigux' / 'artifact-diff.md').read_text(encoding='utf-8')
script_readme = (ROOT / 'scripts' / 'zigux' / 'README.md').read_text(encoding='utf-8')
docs_root = (ROOT / 'Documentation' / 'zigux' / 'README.md').read_text(encoding='utf-8')
review_checklist = (ROOT / 'Documentation' / 'zigux' / 'review-checklist.md').read_text(encoding='utf-8')

required_ledger_markers = [
    'feat(tools/lib): add phase-1 memory and formatting helper ports',
    'feat(scripts/zigux): add bounded Phase 2 fixdep dual-implementation lane',
    'test(zigux): widen bounded fixdep parity fixtures',
    'feat(scripts/zigux): start bounded Phase 2 genksyms lane',
    'feat(scripts/zigux): add bounded Phase 2 genksyms wrapper lane',
    'feat(scripts/zigux): add bounded Phase 2 kconfig bridge scaffolding',
    'feat(scripts/zigux): add bounded Phase 2 mk_elfconfig lane',
]
required_workflow_markers = [
    'python3 scripts/zigux/validate-phase2.py',
    'python3 scripts/zigux/validate-phase2-closure.py',
    'python3 scripts/zigux/check-fixdep-diff.py',
    'python3 scripts/zigux/check-genksyms-bridge.py',
    'python3 scripts/zigux/check-genksyms-crc-diff.py',
    'python3 scripts/zigux/check-kconfig-bridge.py',
    'python3 scripts/zigux/check-phase2-cross.py --target',
    'python3 scripts/zigux/check-mk-elfconfig-diff.py',
    'zig test scripts/zigux/fixdep.zig',
    'zig test scripts/zigux/genksyms.zig',
    'zig test scripts/zigux/genksyms_crc.zig',
    'zig test scripts/zigux/kconfig/conf_bridge.zig',
    'zig test scripts/zigux/kconfig/confdata_bridge.zig',
    'zig test scripts/zigux/mk_elfconfig.zig',
]
required_doc_markers = [
    'fixdep',
    'sample_multi_target_expected.txt',
    'genksyms',
    'zigux/tests/fixtures/genksyms_bridge/minimal_expected.json',
    'genksyms_crc',
    'zigux/tests/fixtures/genksyms_crc/expected.json',
    'kconfig_bridge',
    'mk_elfconfig',
    'elf32_expected.json',
]
required_script_markers = [
    'check-phase2-tests-readme-alignment.py',
    'check-phase2-cross-selftest-alignment.py',
    'check-phase2-toolchain-pin-scope.py',
    'validate-phase2.py',
    'validate-phase2-closure.py',
    'check-fixdep-diff.py',
    'check-genksyms-bridge.py',
    'check-genksyms-crc-diff.py',
    'check-kconfig-bridge.py',
    'check-phase2-cross.py',
    'genksyms.zig',
    'genksyms_crc.zig',
    'kconfig/conf_bridge.zig',
    'kconfig/confdata_bridge.zig',
    'check-mk-elfconfig-diff.py',
    'mk_elfconfig.zig',
]
required_docs_root_markers = [
    'scripts/zigux/check-phase2-tests-readme-alignment.py',
    'scripts/zigux/check-phase2-cross-selftest-alignment.py',
    'scripts/zigux/check-phase2-toolchain-pin-scope.py',
    'make -C zigux phase2-validate',
    'make -C zigux phase2',
]
required_review_markers = [
    'scripts/zigux/check-phase2-tests-readme-alignment.py',
    'scripts/zigux/check-phase2-cross-selftest-alignment.py',
    'scripts/zigux/check-phase2-toolchain-pin-scope.py',
]

missing_markers = []
for marker in required_ledger_markers:
    if marker not in ledger:
        missing_markers.append(f'ledger:{marker}')
for marker in required_workflow_markers:
    if marker not in workflow:
        missing_markers.append(f'workflow:{marker}')
for marker in required_doc_markers:
    if marker not in artifact_doc:
        missing_markers.append(f'doc:{marker}')
for marker in required_script_markers:
    if marker not in script_readme:
        missing_markers.append(f'scripts:{marker}')
for marker in required_docs_root_markers:
    if marker not in docs_root:
        missing_markers.append(f'docs_root:{marker}')
for marker in required_review_markers:
    if marker not in review_checklist:
        missing_markers.append(f'review:{marker}')

if missing_markers:
    print('PHASE2_VALIDATION=fail')
    print('MISSING_PHASE2_MARKERS_START')
    for marker in missing_markers:
        print(marker)
    print('MISSING_PHASE2_MARKERS_END')
    sys.exit(1)

guard_issues: list[str] = []
guard_issues.extend(run_guard(
    [sys.executable, str(TESTS_README_ALIGNMENT_CHECKER)],
    ['PHASE2_TESTS_README_ALIGNMENT=pass'],
))
guard_issues.extend(run_guard(
    [sys.executable, str(CHECK_PHASE2_CROSS_SELFTEST_ALIGNMENT), '--self-test'],
    ['PHASE2_CROSS_SELFTEST_ALIGNMENT_SELF_TEST=pass'],
))
guard_issues.extend(run_guard(
    [sys.executable, str(CHECK_PHASE2_CROSS_SELFTEST_ALIGNMENT)],
    ['PHASE2_CROSS_SELFTEST_ALIGNMENT=pass'],
))
guard_issues.extend(run_guard(
    [sys.executable, str(TOOLCHAIN_PIN_SCOPE_CHECKER), '--self-test'],
    ["PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass"],
))
guard_issues.extend(run_guard(
    [sys.executable, str(TOOLCHAIN_PIN_SCOPE_CHECKER)],
    ["PHASE2_TOOLCHAIN_PIN_SCOPE=pass"],
))
if guard_issues:
    print('PHASE2_VALIDATION=fail')
    print('PHASE2_GUARD_ISSUES_START')
    for issue in guard_issues:
        print(issue)
    print('PHASE2_GUARD_ISSUES_END')
    sys.exit(1)

print('PHASE2_VALIDATION=pass')
print(f'PHASE2_REQUIRED_FILE_COUNT={len(required_files)}')
print(
    'PHASE2_REQUIRED_MARKER_COUNT='
    f"{len(required_ledger_markers) + len(required_workflow_markers) + len(required_doc_markers) + len(required_script_markers) + len(required_docs_root_markers) + len(required_review_markers)}"
)
