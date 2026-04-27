#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
GENKSYMS_BRIDGE_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge'
KCONFIG_BRIDGE_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'kconfig_bridge'
FIXDEP_CASES = ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'cases.json'


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


def case_files_from_list(case_manifest: Path, *field_names: str) -> list[Path]:
    cases = json.loads(case_manifest.read_text(encoding='utf-8'))
    discovered_files: list[Path] = []
    seen: set[Path] = set()
    for case in cases:
        for field_name in field_names:
            file_name = case.get(field_name)
            if not file_name:
                continue
            discovered_path = case_manifest.parent / file_name
            if discovered_path in seen:
                continue
            seen.add(discovered_path)
            discovered_files.append(discovered_path)
    return discovered_files


def fixdep_depfile_inputs(case_manifest: Path) -> list[Path]:
    cases = json.loads(case_manifest.read_text(encoding='utf-8'))
    discovered_files: list[Path] = []
    seen: set[Path] = set()

    for case in cases:
        if int(case.get('expected_exit_code', 0)) != 0:
            continue
        depfile_path = case_manifest.parent / case['depfile']
        text = depfile_path.read_text(encoding='utf-8')
        index = 0
        is_target = True

        while index < len(text):
            ch = text[index]
            if ch == '#':
                index += 1
                while index < len(text) and text[index] != '\n':
                    if text[index] == '\\' and index + 1 < len(text):
                        index += 1
                    index += 1
                continue
            if ch in ' \t':
                index += 1
                continue
            if ch == '\\' and index + 1 < len(text) and text[index + 1] == '\n':
                index += 2
                continue
            if ch == '\n':
                index += 1
                is_target = True
                continue
            if ch == ':':
                index += 1
                is_target = False
                continue

            token_chars: list[str] = []
            while index < len(text):
                ch = text[index]
                if ch in ' \t\n#:':
                    break
                if ch == '\\' and index + 1 < len(text):
                    escaped = text[index + 1]
                    if escaped == '\n':
                        break
                    if escaped in '#:':
                        token_chars.append(escaped)
                        index += 2
                        continue
                    if escaped in ' \t':
                        token_chars.append(ch)
                        token_chars.append(escaped)
                        index += 2
                        continue
                token_chars.append(ch)
                index += 1

            token = ''.join(token_chars)
            if not token or is_target:
                continue
            if token.endswith('include/generated/autoconf.h'):
                continue

            discovered_path = ROOT / token
            if discovered_path in seen:
                continue
            seen.add(discovered_path)
            discovered_files.append(discovered_path)

    return discovered_files


def validate_expected_fixdep_cases(case_manifest: Path) -> list[str]:
    cases = json.loads(case_manifest.read_text(encoding='utf-8'))
    expected_cases = {
        'sample': {
            'depfile': 'sample.d',
            'expected': 'sample_expected.txt',
            'expected_exit_code': 0,
        },
        'sample_multi_target': {
            'depfile': 'sample_multi_target.d',
            'expected': 'sample_multi_target_expected.txt',
            'expected_exit_code': 0,
        },
        'sample_escaped_space': {
            'depfile': 'sample_escaped_space.d',
            'expected': 'sample_escaped_space_expected.txt',
            'expected_exit_code': 0,
        },
        'sample_comment_only': {
            'depfile': 'sample_comment_only.d',
            'expected': 'sample_comment_only_expected.txt',
            'expected_stderr': 'sample_comment_only_expected.stderr.txt',
            'expected_exit_code': 1,
        },
        'sample_missing_dep': {
            'depfile': 'sample_missing_dep.d',
            'expected': 'sample_missing_dep_expected.txt',
            'expected_stderr': 'sample_missing_dep_expected.stderr.txt',
            'expected_exit_code': 2,
        },
    }

    issues: list[str] = []
    seen_names: set[str] = set()
    for case in cases:
        name = case.get('name')
        if not name:
            issues.append('fixdep_cases:missing_name')
            continue
        if name in seen_names:
            issues.append(f'fixdep_cases:duplicate_name:{name}')
            continue
        seen_names.add(name)

        expected_case = expected_cases.get(name)
        if expected_case is not None:
            for field_name, expected_value in expected_case.items():
                actual_value = case.get(field_name, 0 if field_name == 'expected_exit_code' else None)
                if actual_value != expected_value:
                    issues.append(
                        f'fixdep_cases:{name}:{field_name}={actual_value!r},expected={expected_value!r}'
                    )
            continue

        depfile = case.get('depfile')
        if not depfile:
            issues.append(f'fixdep_cases:{name}:missing_depfile')

        target = case.get('target')
        if not target:
            issues.append(f'fixdep_cases:{name}:missing_target')

        cmdline = case.get('cmdline')
        if not cmdline:
            issues.append(f'fixdep_cases:{name}:missing_cmdline')

        if not case.get('expected') and not case.get('expected_stdout'):
            issues.append(f'fixdep_cases:{name}:missing_expected_output')

        try:
            exit_code = int(case.get('expected_exit_code', 0))
        except (TypeError, ValueError):
            issues.append(f"fixdep_cases:{name}:invalid_expected_exit_code:{case.get('expected_exit_code')!r}")
            continue

        if exit_code != 0 and not case.get('expected_stderr'):
            issues.append(f'fixdep_cases:{name}:missing_expected_stderr')

    missing_names = sorted(set(expected_cases) - seen_names)
    for name in missing_names:
        issues.append(f'fixdep_cases:missing_name:{name}')
    if len(cases) < len(expected_cases):
        issues.append(f'fixdep_cases:count={len(cases)},minimum_expected={len(expected_cases)}')
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
    ROOT / 'scripts' / 'zigux' / 'mk_elfconfig.zig',
    ROOT / 'scripts' / 'zigux' / 'check-mk-elfconfig-diff.py',
    ROOT / 'scripts' / 'zigux' / 'kconfig' / 'conf_bridge.zig',
    ROOT / 'scripts' / 'zigux' / 'kconfig' / 'confdata_bridge.zig',
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
required_files.extend(case_files_from_list(
    FIXDEP_CASES,
    'depfile',
    'expected',
    'expected_stdout',
    'expected_stderr',
))
required_files.extend(fixdep_depfile_inputs(
    FIXDEP_CASES,
))
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

fixdep_case_issues = validate_expected_fixdep_cases(FIXDEP_CASES)
if fixdep_case_issues:
    print('PHASE2_VALIDATION=fail')
    print('MISSING_PHASE2_FIXDEP_CASES_START')
    for item in fixdep_case_issues:
        print(item)
    print('MISSING_PHASE2_FIXDEP_CASES_END')
    sys.exit(1)

ledger = (ROOT / 'zigux-alpha' / 'BOOTSTRAP_COMMIT_LEDGER.md').read_text(encoding='utf-8')
workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
artifact_doc = (ROOT / 'Documentation' / 'zigux' / 'artifact-diff.md').read_text(encoding='utf-8')
script_readme = (ROOT / 'scripts' / 'zigux' / 'README.md').read_text(encoding='utf-8')

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
    'sample_escaped_space_expected.txt',
    'genksyms',
    'zigux/tests/fixtures/genksyms_bridge/minimal_expected.json',
    'genksyms_crc',
    'zigux/tests/fixtures/genksyms_crc/expected.json',
    'kconfig_bridge',
    'mk_elfconfig',
    'elf32_expected.json',
]
required_script_markers = [
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

if missing_markers:
    print('PHASE2_VALIDATION=fail')
    print('MISSING_PHASE2_MARKERS_START')
    for marker in missing_markers:
        print(marker)
    print('MISSING_PHASE2_MARKERS_END')
    sys.exit(1)

print('PHASE2_VALIDATION=pass')
print(f'PHASE2_REQUIRED_FILE_COUNT={len(required_files)}')
print('PHASE2_FIXDEP_CASE_COUNT=5')
print(f'PHASE2_REQUIRED_MARKER_COUNT={len(required_ledger_markers) + len(required_workflow_markers) + len(required_doc_markers) + len(required_script_markers)}')