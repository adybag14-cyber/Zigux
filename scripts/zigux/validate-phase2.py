#!/usr/bin/env python3
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
GENKSYMS_BRIDGE_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge'
KCONFIG_BRIDGE_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'kconfig_bridge'
FIXDEP_CASES = ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'cases.json'
CONF_BRIDGE = ROOT / 'scripts' / 'zigux' / 'kconfig' / 'conf_bridge.zig'
CHECK_KCONFIG_BRIDGE = ROOT / 'scripts' / 'zigux' / 'check-kconfig-bridge.py'
GENKSYMS_BRIDGE_CASES = GENKSYMS_BRIDGE_DIR / 'cases.json'


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
        'sample_concatenated': {
            'depfile': 'sample_concatenated.d',
            'expected': 'sample_concatenated_expected.txt',
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
        'sample_output_write': {
            'depfile': 'sample.d',
            'expected': 'sample_output_write_expected.txt',
            'expected_stderr': 'sample_output_write_expected.stderr.txt',
            'expected_exit_code': 1,
            'stdout_mode': 'dev_full',
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


def validate_expected_genksyms_bridge_cases(case_manifest: Path) -> list[str]:
    data = json.loads(case_manifest.read_text(encoding='utf-8'))
    issues: list[str] = []

    if not isinstance(data, dict):
        return ['genksyms_bridge:manifest:expected_object']

    expected_top_level = {'cases'}
    unexpected_top_level = sorted(set(data) - expected_top_level)
    for name in unexpected_top_level:
        issues.append(f'genksyms_bridge:manifest:unexpected_top_level:{name}')

    cases = data.get('cases')
    if not isinstance(cases, list):
        issues.append('genksyms_bridge:manifest:cases:expected_list')
        return issues
    if not cases:
        issues.append('genksyms_bridge:manifest:cases:empty')
        return issues

    expected_cases = {
        'minimal': 'minimal_expected.json',
        'debug_reference_types': 'debug_reference_types_expected.json',
        'short_inline_reference_dump_types': 'short_inline_reference_dump_types_expected.json',
        'long_options': 'long_options_expected.json',
        'abbreviated_long_options': 'abbreviated_long_options_expected.json',
        'quiet_overrides_warning': 'quiet_overrides_warning_expected.json',
        'explicit_option_terminator': 'explicit_option_terminator_expected.json',
        'positional_passthrough': 'positional_passthrough_expected.json',
        'lone_dash_passthrough': 'lone_dash_passthrough_expected.json',
        'explicit_terminator_positional_passthrough': 'explicit_terminator_positional_passthrough_expected.json',
        'help': 'help_expected.json',
        'version': 'version_expected.json',
        'invalid_option': 'invalid_option_expected.json',
        'missing_reference_argument': 'missing_reference_argument_expected.json',
        'unsupported_long_option': 'unsupported_long_option_expected.json',
        'ambiguous_abbreviated_long_option': 'ambiguous_abbreviated_long_option_expected.json',
        'unexpected_long_option_argument': 'unexpected_long_option_argument_expected.json',
        'abbreviated_unexpected_long_option_argument': 'abbreviated_unexpected_long_option_argument_expected.json',
        'missing_long_reference_argument': 'missing_long_reference_argument_expected.json',
        'abbreviated_missing_long_reference_argument': 'abbreviated_missing_long_reference_argument_expected.json',
        'missing_long_dump_types_argument': 'missing_long_dump_types_argument_expected.json',
    }
    process_json_cases = {
        'help',
        'version',
        'invalid_option',
        'missing_reference_argument',
        'unsupported_long_option',
        'ambiguous_abbreviated_long_option',
        'unexpected_long_option_argument',
        'abbreviated_unexpected_long_option_argument',
        'missing_long_reference_argument',
        'abbreviated_missing_long_reference_argument',
        'missing_long_dump_types_argument',
    }
    normalize_stderr_cases = {
        'invalid_option',
        'missing_reference_argument',
        'unsupported_long_option',
        'ambiguous_abbreviated_long_option',
        'unexpected_long_option_argument',
        'abbreviated_unexpected_long_option_argument',
        'missing_long_reference_argument',
        'abbreviated_missing_long_reference_argument',
        'missing_long_dump_types_argument',
    }

    seen_names: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            issues.append('genksyms_bridge:manifest:case:expected_object')
            continue

        name = case.get('name')
        if not name:
            issues.append('genksyms_bridge:missing_name')
            continue
        if name in seen_names:
            issues.append(f'genksyms_bridge:duplicate_name:{name}')
            continue
        seen_names.add(name)

        argv = case.get('argv')
        if not isinstance(argv, list):
            issues.append(f'genksyms_bridge:{name}:argv:expected_list')

        expected = case.get('expected')
        expected_file = expected_cases.get(name)
        if expected_file is None:
            issues.append(f'genksyms_bridge:unexpected_name:{name}')
        elif expected != expected_file:
            issues.append(f'genksyms_bridge:{name}:expected={expected!r},expected_file={expected_file!r}')

        expected_mode = 'process_json' if name in process_json_cases else 'stdout_json'
        actual_mode = case.get('mode', 'stdout_json')
        if actual_mode != expected_mode:
            issues.append(f'genksyms_bridge:{name}:mode={actual_mode!r},expected_mode={expected_mode!r}')

        expected_normalize = name in normalize_stderr_cases
        actual_normalize = case.get('normalize_stderr', False)
        if actual_normalize != expected_normalize:
            issues.append(
                f'genksyms_bridge:{name}:normalize_stderr={actual_normalize!r},expected_normalize_stderr={expected_normalize!r}'
            )

    missing_names = sorted(set(expected_cases) - seen_names)
    for name in missing_names:
        issues.append(f'genksyms_bridge:missing_name:{name}')
    if len(cases) != len(expected_cases):
        issues.append(f'genksyms_bridge:count={len(cases)},expected={len(expected_cases)}')
    return issues


def supported_conf_modes(conf_bridge: Path) -> set[str]:
    source = conf_bridge.read_text(encoding='utf-8')
    match = re.search(r'pub const Mode = enum \{(.*?)\n\s*pub fn parse', source, re.S)
    if not match:
        return set()

    modes: set[str] = set()
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith('pub ') or line.startswith('//'):
            continue
        if line.endswith(','):
            candidate = line[:-1].strip()
            if candidate and candidate.isidentifier():
                modes.add(candidate)
    return modes


def validate_kconfig_bridge_manifest(case_manifest: Path, conf_bridge: Path) -> list[str]:
    cases = json.loads(case_manifest.read_text(encoding='utf-8'))
    manifest_modes = {case.get('mode') for case in cases.get('conf_cases', []) if case.get('mode')}
    bridge_modes = supported_conf_modes(conf_bridge)
    issues: list[str] = []

    if not bridge_modes:
        issues.append('kconfig_bridge:failed_to_parse_conf_bridge_modes')
        return issues

    missing = sorted(bridge_modes - manifest_modes)
    for mode in missing:
        issues.append(f'kconfig_bridge:missing_conf_case_mode:{mode}')

    unsupported = sorted(manifest_modes - bridge_modes)
    for mode in unsupported:
        issues.append(f'kconfig_bridge:unsupported_conf_case_mode:{mode}')

    return issues


def validate_kconfig_checker_confdata_gate(checker_script: Path) -> list[str]:
    source = checker_script.read_text(encoding='utf-8')
    required_markers = {
        'confdata_bridge_constant': "CONFDATA_BRIDGE = ROOT / 'scripts' / 'zigux' / 'kconfig' / 'confdata_bridge.zig'",
        'confdata_bridge_compile': 'compile_tool(zig, CONFDATA_BRIDGE, confdata_exe)',
        'confdata_cases_loop': "for case in CASES['confdata_cases']:",
        'confdata_case_order_gate': 'UNSORTED_CONFDATA_CASE_ORDER',
        'confdata_bridge_replay': "result = run([str(confdata_exe), str(FIXTURE_DIR / case['input'])], cwd=str(ROOT), capture_output=True)",
    }

    issues: list[str] = []
    for issue_name, marker in required_markers.items():
        if marker not in source:
            issues.append(f'kconfig_checker:{issue_name}')
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

genksyms_bridge_case_issues = validate_expected_genksyms_bridge_cases(GENKSYMS_BRIDGE_CASES)
if genksyms_bridge_case_issues:
    print('PHASE2_VALIDATION=fail')
    print('MISSING_PHASE2_GENKSYMS_BRIDGE_CASES_START')
    for item in genksyms_bridge_case_issues:
        print(item)
    print('MISSING_PHASE2_GENKSYMS_BRIDGE_CASES_END')
    sys.exit(1)

kconfig_bridge_issues = validate_kconfig_bridge_manifest(KCONFIG_BRIDGE_DIR / 'cases.json', CONF_BRIDGE)
if kconfig_bridge_issues:
    print('PHASE2_VALIDATION=fail')
    print('MISSING_PHASE2_KCONFIG_BRIDGE_CASES_START')
    for item in kconfig_bridge_issues:
        print(item)
    print('MISSING_PHASE2_KCONFIG_BRIDGE_CASES_END')
    sys.exit(1)

kconfig_checker_issues = validate_kconfig_checker_confdata_gate(CHECK_KCONFIG_BRIDGE)
if kconfig_checker_issues:
    print('PHASE2_VALIDATION=fail')
    print('MISSING_PHASE2_KCONFIG_CHECKER_GATES_START')
    for item in kconfig_checker_issues:
        print(item)
    print('MISSING_PHASE2_KCONFIG_CHECKER_GATES_END')
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
    'sample_concatenated_expected.txt',
    'sample_output_write_expected.stderr.txt',
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
print(f'PHASE2_FIXDEP_CASE_COUNT={len(json.loads(FIXDEP_CASES.read_text(encoding="utf-8")))}')
print(f'PHASE2_REQUIRED_MARKER_COUNT={len(required_ledger_markers) + len(required_workflow_markers) + len(required_doc_markers) + len(required_script_markers)}')
