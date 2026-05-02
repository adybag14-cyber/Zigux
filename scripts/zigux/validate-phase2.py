#!/usr/bin/env python3
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
GENKSYMS_BRIDGE_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge'
KCONFIG_BRIDGE_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'kconfig_bridge'
FIXDEP_CASES = ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep' / 'cases.json'
PHASE2_TOOL_MANIFEST = ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_tool_manifest.json'
PHASE2_CROSS_TARGETS = ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_cross_targets.json'
CONF_BRIDGE = ROOT / 'scripts' / 'zigux' / 'kconfig' / 'conf_bridge.zig'
CHECK_KCONFIG_BRIDGE = ROOT / 'scripts' / 'zigux' / 'check-kconfig-bridge.py'
CHECK_PHASE2_CROSS = ROOT / 'scripts' / 'zigux' / 'check-phase2-cross.py'
CHECK_GENKSYMS_BRIDGE = ROOT / 'scripts' / 'zigux' / 'check-genksyms-bridge.py'
CHECK_GENKSYMS_CRC = ROOT / 'scripts' / 'zigux' / 'check-genksyms-crc-diff.py'
CHECK_MK_ELFCONFIG = ROOT / 'scripts' / 'zigux' / 'check-mk-elfconfig-diff.py'
CHECK_PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT = ROOT / 'scripts' / 'zigux' / 'check-phase2-genksyms-bridge-selftest-alignment.py'
GENKSYMS_BRIDGE_CASES = GENKSYMS_BRIDGE_DIR / 'cases.json'
EXPECTED_PHASE2_TOOL_MANIFEST_TOOLS = [
    'scripts/zigux/fixdep.zig',
    'scripts/zigux/genksyms.zig',
    'scripts/zigux/genksyms_crc.zig',
    'scripts/zigux/mk_elfconfig.zig',
    'scripts/zigux/kconfig/conf_bridge.zig',
    'scripts/zigux/kconfig/confdata_bridge.zig',
]
EXPECTED_PHASE2_CROSS_TARGETS = [
    'x86_64-linux-musl',
    'aarch64-linux-musl',
    'riscv64-linux-musl',
]
EXACT_WORKFLOW_RUN_COUNTS = {
    'python3 scripts/zigux/check-fixdep-diff.py --self-test': 1,
    'python3 scripts/zigux/check-fixdep-diff.py': 1,
    'python3 scripts/zigux/check-genksyms-bridge.py --self-test': 1,
    'python3 scripts/zigux/check-genksyms-bridge.py': 1,
    'python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test': 1,
    'python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py': 1,
    'python3 scripts/zigux/check-genksyms-crc-diff.py --self-test': 1,
    'python3 scripts/zigux/check-genksyms-crc-diff.py': 1,
    'python3 scripts/zigux/check-kconfig-bridge.py --self-test': 1,
    'python3 scripts/zigux/check-kconfig-bridge.py': 1,
    'python3 scripts/zigux/check-phase2-cross.py --self-test': 2,
    'python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}': 1,
    'python3 scripts/zigux/check-mk-elfconfig-diff.py --self-test': 1,
    'python3 scripts/zigux/check-mk-elfconfig-diff.py': 1,
}
EXACT_MAKEFILE_RUN_COUNTS = {
    'scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test': 1,
    'scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py': 1,
    'scripts/zigux/validate-phase2.py': 1,
    'scripts/zigux/validate-phase2-closure.py': 1,
}


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
            'target': 'sample.o',
            'cmdline': 'clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample.o',
            'expected': 'sample_expected.txt',
            'expected_exit_code': 0,
        },
        'sample_multi_target': {
            'depfile': 'sample_multi_target.d',
            'target': 'module/sample2.o',
            'cmdline': 'clang -Iinclude -DZIGUX_MULTI -c zigux/tests/fixtures/fixdep/sample2.c -o module/sample2.o',
            'expected': 'sample_multi_target_expected.txt',
            'expected_exit_code': 0,
        },
        'sample_escaped_space': {
            'depfile': 'sample_escaped_space.d',
            'target': 'sample_escaped_space.o',
            'cmdline': 'clang -c zigux/tests/fixtures/fixdep/sample_escaped_space_source.c -o sample_escaped_space.o',
            'expected': 'sample_escaped_space_expected.txt',
            'expected_exit_code': 0,
        },
        'sample_escaped_colon': {
            'depfile': 'sample_escaped_colon.d',
            'target': 'sample_escaped_colon.o',
            'cmdline': 'clang -c zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c -o sample_escaped_colon.o',
            'expected': 'sample_escaped_colon_expected.txt',
            'expected_exit_code': 0,
        },
        'sample_concatenated': {
            'depfile': 'sample_concatenated.d',
            'target': 'sample_concatenated.o',
            'cmdline': 'clang -c zigux/tests/fixtures/fixdep/sample_concatenated_source.c -o sample_concatenated.o',
            'expected': 'sample_concatenated_expected.txt',
            'expected_exit_code': 0,
        },
        'sample_comment_only': {
            'depfile': 'sample_comment_only.d',
            'target': 'sample_comment_only.o',
            'cmdline': 'clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only.o',
            'expected': 'sample_comment_only_expected.txt',
            'expected_stderr': 'sample_comment_only_expected.stderr.txt',
            'expected_exit_code': 1,
        },
        'sample_comment_only_stdout_full': {
            'depfile': 'sample_comment_only.d',
            'target': 'sample_comment_only_stdout_full.o',
            'cmdline': 'clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_comment_only_stdout_full.o',
            'expected': 'sample_output_write_expected.txt',
            'expected_stderr': 'sample_comment_only_expected.stderr.txt',
            'expected_exit_code': 1,
            'stdout_mode': 'dev_full',
        },
        'sample_missing_dep': {
            'depfile': 'sample_missing_dep.d',
            'target': 'sample_missing_dep.o',
            'cmdline': 'clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep.o',
            'expected': 'sample_missing_dep_expected.txt',
            'expected_stderr': 'sample_missing_dep_expected.stderr.txt',
            'expected_exit_code': 2,
        },
        'sample_missing_dep_stdout_full': {
            'depfile': 'sample_missing_dep.d',
            'target': 'sample_missing_dep_stdout_full.o',
            'cmdline': 'clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep_stdout_full.o',
            'expected': 'sample_output_write_expected.txt',
            'expected_stderr': 'sample_missing_dep_expected.stderr.txt',
            'expected_exit_code': 2,
            'stdout_mode': 'dev_full',
        },
        'sample_output_write': {
            'depfile': 'sample.d',
            'target': 'sample_output_write.o',
            'cmdline': 'clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample_output_write.o',
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

        issues.append(f'fixdep_cases:unexpected_name:{name}')

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
    if len(cases) != len(expected_cases):
        issues.append(f'fixdep_cases:count={len(cases)},expected={len(expected_cases)}')
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
        'clustered_short_inline_reference': 'clustered_short_inline_reference_expected.json',
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
        'missing_dump_types_argument': 'missing_dump_types_argument_expected.json',
        'unsupported_long_option': 'unsupported_long_option_expected.json',
        'ambiguous_abbreviated_long_option': 'ambiguous_abbreviated_long_option_expected.json',
        'empty_long_option_name': 'empty_long_option_name_expected.json',
        'unexpected_long_option_argument': 'unexpected_long_option_argument_expected.json',
        'abbreviated_unexpected_long_option_argument': 'abbreviated_unexpected_long_option_argument_expected.json',
        'missing_long_reference_argument': 'missing_long_reference_argument_expected.json',
        'abbreviated_missing_long_reference_argument': 'abbreviated_missing_long_reference_argument_expected.json',
        'missing_long_dump_types_argument': 'missing_long_dump_types_argument_expected.json',
        'abbreviated_missing_long_dump_types_argument': 'abbreviated_missing_long_dump_types_argument_expected.json',
        'too_many_reference_files': 'too_many_reference_files_expected.json',
    }
    process_json_cases = {
        'help',
        'version',
        'invalid_option',
        'missing_reference_argument',
        'missing_dump_types_argument',
        'unsupported_long_option',
        'ambiguous_abbreviated_long_option',
        'empty_long_option_name',
        'unexpected_long_option_argument',
        'abbreviated_unexpected_long_option_argument',
        'missing_long_reference_argument',
        'abbreviated_missing_long_reference_argument',
        'missing_long_dump_types_argument',
        'abbreviated_missing_long_dump_types_argument',
        'too_many_reference_files',
    }
    normalize_stderr_cases = {
        'invalid_option',
        'missing_reference_argument',
        'missing_dump_types_argument',
        'unsupported_long_option',
        'ambiguous_abbreviated_long_option',
        'empty_long_option_name',
        'unexpected_long_option_argument',
        'abbreviated_unexpected_long_option_argument',
        'missing_long_reference_argument',
        'abbreviated_missing_long_reference_argument',
        'missing_long_dump_types_argument',
        'abbreviated_missing_long_dump_types_argument',
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


def supported_conf_modes_in_order(conf_bridge: Path) -> list[str]:
    source = conf_bridge.read_text(encoding='utf-8')
    match = re.search(r'pub const Mode = enum \{(.*?)\n\s*pub fn parse', source, re.S)
    if not match:
        return []

    modes: list[str] = []
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith('pub ') or line.startswith('//'):
            continue
        if line.endswith(','):
            candidate = line[:-1].strip()
            if candidate and candidate.isidentifier():
                modes.append(candidate)
    return modes


def validate_kconfig_bridge_manifest(case_manifest: Path, conf_bridge: Path) -> list[str]:
    data = json.loads(case_manifest.read_text(encoding='utf-8'))
    issues: list[str] = []
    bridge_modes = supported_conf_modes_in_order(conf_bridge)

    if not isinstance(data, dict):
        issues.append('kconfig_bridge:manifest:expected_object')
        return issues

    expected_top_level = {'conf_cases', 'confdata_cases'}
    unexpected_top_level = sorted(set(data) - expected_top_level)
    for name in unexpected_top_level:
        issues.append(f'kconfig_bridge:manifest:unexpected_top_level:{name}')

    conf_cases = data.get('conf_cases')
    if not isinstance(conf_cases, list):
        issues.append('kconfig_bridge:manifest:conf_cases:expected_list')
        conf_cases = []
    elif not conf_cases:
        issues.append('kconfig_bridge:manifest:conf_cases:empty')

    confdata_cases = data.get('confdata_cases')
    if not isinstance(confdata_cases, list):
        issues.append('kconfig_bridge:manifest:confdata_cases:expected_list')
        confdata_cases = []
    elif not confdata_cases:
        issues.append('kconfig_bridge:manifest:confdata_cases:empty')

    if not bridge_modes:
        issues.append('kconfig_bridge:failed_to_parse_conf_bridge_modes')
        return issues

    expected_conf_cases = [
        {
            'name': 'oldaskconfig',
            'mode': 'oldaskconfig',
            'kconfig': 'Kconfig',
            'config': '.config',
            'arch': 'x86_64',
            'expected': 'oldaskconfig_expected.json',
        },
        {
            'name': 'oldconfig',
            'mode': 'oldconfig',
            'kconfig': 'Kconfig',
            'config': 'old/.config',
            'arch': 'x86_64',
            'expected': 'oldconfig_expected.json',
        },
        {
            'name': 'syncconfig',
            'mode': 'syncconfig',
            'kconfig': 'Kconfig',
            'config': 'out/.config',
            'arch': 'riscv64',
            'expected': 'syncconfig_expected.json',
        },
        {
            'name': 'defconfig',
            'mode': 'defconfig',
            'kconfig': 'Kconfig',
            'config': 'out/.config',
            'arch': 'arm64',
            'mode_arg': 'arch/arm64/configs/defconfig',
            'expected': 'defconfig_expected.json',
        },
        {
            'name': 'savedefconfig',
            'mode': 'savedefconfig',
            'kconfig': 'Kconfig',
            'config': 'out/.config',
            'arch': 'arm64',
            'mode_arg': 'arch/arm64/configs/minimal_defconfig',
            'expected': 'savedefconfig_expected.json',
        },
        {
            'name': 'allnoconfig',
            'mode': 'allnoconfig',
            'kconfig': 'Kconfig',
            'config': 'none/.config',
            'arch': 'arm64',
            'allconfig': 'arch/arm64/configs/tiny.config',
            'expected': 'allnoconfig_expected.json',
        },
        {
            'name': 'allyesconfig',
            'mode': 'allyesconfig',
            'kconfig': 'Kconfig',
            'config': 'yes/.config',
            'arch': 'riscv64',
            'expected': 'allyesconfig_expected.json',
        },
        {
            'name': 'allmodconfig',
            'mode': 'allmodconfig',
            'kconfig': 'Kconfig',
            'config': 'mod/.config',
            'arch': 'arm',
            'expected': 'allmodconfig_expected.json',
        },
        {
            'name': 'alldefconfig',
            'mode': 'alldefconfig',
            'kconfig': 'Kconfig',
            'config': 'build/.config',
            'arch': 'arm64',
            'expected': 'alldefconfig_expected.json',
        },
        {
            'name': 'randconfig',
            'mode': 'randconfig',
            'kconfig': 'Kconfig',
            'config': 'rand/.config',
            'arch': 'x86',
            'expected': 'randconfig_expected.json',
        },
        {
            'name': 'listnewconfig',
            'mode': 'listnewconfig',
            'kconfig': 'Kconfig',
            'config': 'list/.config',
            'arch': 'x86_64',
            'expected': 'listnewconfig_expected.json',
        },
        {
            'name': 'helpnewconfig',
            'mode': 'helpnewconfig',
            'kconfig': 'Kconfig',
            'config': 'help/.config',
            'arch': 'x86_64',
            'expected': 'helpnewconfig_expected.json',
        },
        {
            'name': 'olddefconfig',
            'mode': 'olddefconfig',
            'kconfig': 'Kconfig',
            'config': 'olddef/.config',
            'arch': 'arm64',
            'expected': 'olddefconfig_expected.json',
        },
        {
            'name': 'yes2modconfig',
            'mode': 'yes2modconfig',
            'kconfig': 'Kconfig',
            'config': 'yes2mod/.config',
            'arch': 'arm64',
            'expected': 'yes2modconfig_expected.json',
        },
        {
            'name': 'mod2yesconfig',
            'mode': 'mod2yesconfig',
            'kconfig': 'Kconfig',
            'config': 'mod2yes/.config',
            'arch': 'arm64',
            'expected': 'mod2yesconfig_expected.json',
        },
        {
            'name': 'mod2noconfig',
            'mode': 'mod2noconfig',
            'kconfig': 'Kconfig',
            'config': 'mod2no/.config',
            'arch': 'arm64',
            'expected': 'mod2noconfig_expected.json',
        },
    ]

    conf_case_names: set[str] = set()
    if len(conf_cases) != len(expected_conf_cases):
        issues.append(f'kconfig_bridge:manifest:conf_cases:count={len(conf_cases)},expected={len(expected_conf_cases)}')
    expected_mode_names = [case['mode'] for case in expected_conf_cases]
    if bridge_modes != expected_mode_names:
        issues.append(f'kconfig_bridge:bridge_modes={bridge_modes!r},expected={expected_mode_names!r}')
    for index, expected_case in enumerate(expected_conf_cases):
        try:
            case = conf_cases[index]
        except IndexError:
            break
        if not isinstance(case, dict):
            issues.append(f'kconfig_bridge:conf_case:{index}:expected_object')
            continue
        name = case.get('name')
        if not name:
            issues.append(f'kconfig_bridge:conf_case:{index}:missing_name')
            continue
        if name in conf_case_names:
            issues.append(f'kconfig_bridge:conf_case:duplicate_name:{name}')
            continue
        conf_case_names.add(name)
        if name != expected_case['name']:
            issues.append(f"kconfig_bridge:conf_case:{index}:name={name!r},expected={expected_case['name']!r}")
        for field_name, expected_value in expected_case.items():
            if field_name == 'name':
                continue
            actual_value = case.get(field_name)
            if actual_value != expected_value:
                issues.append(
                    f"kconfig_bridge:conf_case:{name}:{field_name}={actual_value!r},expected={expected_value!r}"
                )
        extra_fields = sorted(set(case) - set(expected_case))
        for field_name in extra_fields:
            issues.append(f'kconfig_bridge:conf_case:{name}:unexpected_field:{field_name}')

    expected_conf_names = {case['name'] for case in expected_conf_cases}
    for name in sorted(expected_conf_names - conf_case_names):
        issues.append(f'kconfig_bridge:conf_case:missing_name:{name}')

    expected_confdata_cases = [
        {
            'name': 'sample',
            'input': 'sample.config',
            'expected': 'sample_expected.json',
        },
        {
            'name': 'empty_string',
            'input': 'empty_string.config',
            'expected': 'empty_string_expected.json',
        },
        {
            'name': 'explicit_n_tristate',
            'input': 'explicit_n_tristate.config',
            'expected': 'explicit_n_tristate_expected.json',
        },
        {
            'name': 'numeric_kinds',
            'input': 'numeric_kinds.config',
            'expected': 'numeric_kinds_expected.json',
        },
        {
            'name': 'signed_numeric_kinds',
            'input': 'signed_numeric_kinds.config',
            'expected': 'signed_numeric_kinds_expected.json',
        },
        {
            'name': 'negative_signed_numeric_kinds',
            'input': 'negative_signed_numeric_kinds.config',
            'expected': 'negative_signed_numeric_kinds_expected.json',
        },
        {
            'name': 'duplicate_assignments',
            'input': 'duplicate_assignments.config',
            'expected': 'duplicate_assignments_expected.json',
        },
        {
            'name': 'ignore_non_config_lines',
            'input': 'ignore_non_config_lines.config',
            'expected': 'ignore_non_config_lines_expected.json',
        },
        {
            'name': 'escaped_strings',
            'input': 'escaped_strings.config',
            'expected': 'escaped_strings_expected.json',
        },
        {
            'name': 'escaped_control_sequences',
            'input': 'escaped_control_sequences.config',
            'expected': 'escaped_control_sequences_expected.json',
        },
        {
            'name': 'malformed_quoted_string',
            'input': 'malformed_quoted_string.config',
            'expected': 'malformed_quoted_string_expected.json',
        },
        {
            'name': 'quoted_suffix_bytes',
            'input': 'quoted_suffix_bytes.config',
            'expected': 'quoted_suffix_bytes_expected.json',
        },
        {
            'name': 'empty_symbol_names',
            'input': 'empty_symbol_names.config',
            'expected': 'empty_symbol_names_expected.json',
        },
        {
            'name': 'sample_crlf',
            'input': 'sample_crlf.config',
            'expected': 'sample_crlf_expected.json',
        },
        {
            'name': 'escaped_low_control_bytes',
            'input': 'escaped_low_control_bytes.config',
            'expected': 'escaped_low_control_bytes_expected.json',
        },
    ]

    confdata_case_names: set[str] = set()
    if len(confdata_cases) != len(expected_confdata_cases):
        issues.append(
            f'kconfig_bridge:manifest:confdata_cases:count={len(confdata_cases)},expected={len(expected_confdata_cases)}'
        )
    for index, expected_case in enumerate(expected_confdata_cases):
        try:
            case = confdata_cases[index]
        except IndexError:
            break
        if not isinstance(case, dict):
            issues.append(f'kconfig_bridge:confdata_case:{index}:expected_object')
            continue
        name = case.get('name')
        if not name:
            issues.append(f'kconfig_bridge:confdata_case:{index}:missing_name')
            continue
        if name in confdata_case_names:
            issues.append(f'kconfig_bridge:confdata_case:duplicate_name:{name}')
            continue
        confdata_case_names.add(name)
        if name != expected_case['name']:
            issues.append(
                f"kconfig_bridge:confdata_case:{index}:name={name!r},expected={expected_case['name']!r}"
            )
        for field_name, expected_value in expected_case.items():
            if field_name == 'name':
                continue
            actual_value = case.get(field_name)
            if actual_value != expected_value:
                issues.append(
                    f"kconfig_bridge:confdata_case:{name}:{field_name}={actual_value!r},expected={expected_value!r}"
                )
        extra_fields = sorted(set(case) - set(expected_case))
        for field_name in extra_fields:
            issues.append(f'kconfig_bridge:confdata_case:{name}:unexpected_field:{field_name}')

    expected_confdata_names = {case['name'] for case in expected_confdata_cases}
    for name in sorted(expected_confdata_names - confdata_case_names):
        issues.append(f'kconfig_bridge:confdata_case:missing_name:{name}')

    return issues


def validate_fixdep_checker_gate(checker_script: Path) -> list[str]:
    source = checker_script.read_text(encoding='utf-8')
    required_markers = {
        'self_test_arg': "parser.add_argument('--self-test'",
        'self_test_pass_marker': "print('FIXDEP_DIFF_SELF_TEST=pass')",
        'self_test_case_count_marker': "print('FIXDEP_DIFF_SELF_TEST_CASE_COUNT=17')",
        'unsupported_stdout_mode_guard': 'unsupported_stdout_mode',
        'dev_full_missing_expected_stdout_guard': 'stdout_mode=dev_full:requires_expected_stdout',
        'success_stderr_guard': 'success_path_stderr_mismatch',
        'missing_expected_stderr_guard': 'missing expected stderr fixture',
        'repeat_c_compare': "run(diff + [str(c_out), str(c_repeat)], cwd=str(ROOT))",
        'repeat_zig_compare': "run(diff + [str(zig_out), str(zig_repeat)], cwd=str(ROOT))",
        'determinism_marker': "print('FIXDEP_DETERMINISM=pass')",
    }

    issues: list[str] = []
    for issue_name, marker in required_markers.items():
        if marker not in source:
            issues.append(f'fixdep_checker:{issue_name}')
    return issues


def validate_artifact_diff_contract_gate(contract_script: Path) -> list[str]:
    source = contract_script.read_text(encoding='utf-8')
    required_markers = {
        'self_test_arg': "parser.add_argument('--self-test'",
        'self_test_pass_marker': "print('ARTIFACT_DIFF_CONTRACT_SELF_TEST=pass')",
        'self_test_case_count_marker': "print('ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT=5')",
        'missing_actual_guard': 'ARTIFACT_DIFF_MISSING_FILE=',
        'json_actual_guard': 'ACTUAL_JSON_ERROR=',
        'json_expected_guard': 'EXPECTED_JSON_ERROR=',
        'sha_mode_guard': 'ARTIFACT_DIFF_SHA256=',
        'text_mode_guard': 'ARTIFACT_DIFF_TEXT_DIFF_START',
        'stable_path_guard': '--actual-label',
    }

    issues: list[str] = []
    for issue_name, marker in required_markers.items():
        if marker not in source:
            issues.append(f'artifact_diff_contract:{issue_name}')
    return issues


def validate_kconfig_checker_gate(checker_script: Path) -> list[str]:
    source = checker_script.read_text(encoding='utf-8')
    required_markers = {
        'self_test_arg': "parser.add_argument('--self-test'",
        'self_test_pass_marker': "print('KCONFIG_BRIDGE_SELF_TEST=pass')",
        'self_test_case_count_marker': "print('KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT=6')",
        'duplicate_expected_guard': ':duplicate_expected:',
        'orphaned_expected_guard': ':orphaned_expected:',
        'conf_mode_coverage_guard': 'conf_cases:missing_mode:',
        'conf_mode_order_guard': 'conf_cases:mode_order=',
        'confdata_naming_guard': 'confdata_cases:noncanonical_name:',
        'repeat_conf_compare': "run(diff + [str(conf_actual), str(conf_repeat)], cwd=str(ROOT))",
        'repeat_confdata_compare': "run(diff + [str(confdata_actual), str(confdata_repeat)], cwd=str(ROOT))",
        'rebuild_confdata_compare': "run(diff + [str(confdata_actual), str(confdata_rebuilt)], cwd=str(ROOT))",
        'determinism_marker': "print('KCONFIG_BRIDGE_DETERMINISM=pass')",
    }

    issues: list[str] = []
    for issue_name, marker in required_markers.items():
        if marker not in source:
            issues.append(f'kconfig_checker:{issue_name}')
    return issues


def validate_phase2_cross_checker_gate(checker_script: Path) -> list[str]:
    source = checker_script.read_text(encoding='utf-8')
    required_markers = {
        'self_test_arg': "parser.add_argument('--self-test'",
        'self_test_pass_marker': "print('PHASE2_CROSS_SELF_TEST=pass')",
        'self_test_case_count_marker': "print('PHASE2_CROSS_SELF_TEST_CASE_COUNT=11')",
        'target_flag_guard': "parser.add_argument('--target'",
        'manifest_count_guard': 'phase2-cross:manifest_count_mismatch',
        'compile_fail_guard': 'phase2-cross:compile_failed',
        'duplicate_tool_guard': 'phase2-cross:duplicate_tool:',
        'duplicate_target_guard': 'phase2-cross:duplicate_target:',
        'unexpected_target_guard': 'phase2-cross:unexpected_target:',
        'duplicate_manifest_target_guard': 'phase2-cross:duplicate_manifest_target:',
    }

    issues: list[str] = []
    for issue_name, marker in required_markers.items():
        if marker not in source:
            issues.append(f'phase2_cross_checker:{issue_name}')
    return issues


def validate_genksyms_bridge_checker_gate(checker_script: Path) -> list[str]:
    source = checker_script.read_text(encoding='utf-8')
    required_markers = {
        'self_test_arg': "parser.add_argument('--self-test'",
        'self_test_pass_marker': "print('PHASE2_GENKSYMS_BRIDGE_SELF_TEST=pass')",
        'self_test_case_count_marker': "print('PHASE2_GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=26')",
        'normalize_stderr_mode_guard': 'normalize_stderr:requires_process_json_mode',
        'missing_expected_fixture_guard': 'expected:missing_fixture:',
        'orphaned_expected_guard': 'cases.json:orphaned_expected:',
        'duplicate_expected_guard': 'expected:duplicate_reference:',
        'repeat_c_compare': "run(diff_base + [str(c_actual), str(c_repeat)], cwd=str(ROOT))",
        'repeat_zig_compare': "run(diff_base + [str(zig_actual), str(zig_repeat)], cwd=str(ROOT))",
        'determinism_marker': "print('GENKSYMS_BRIDGE_DETERMINISM=pass')",
    }

    issues: list[str] = []
    for issue_name, marker in required_markers.items():
        if marker not in source:
            issues.append(f'genksyms_bridge_checker:{issue_name}')
    return issues


def validate_genksyms_crc_checker_gate(checker_script: Path) -> list[str]:
    source = checker_script.read_text(encoding='utf-8')
    required_markers = {
        'self_test_arg': "parser.add_argument('--self-test'",
        'self_test_pass_marker': "print('GENKSYMS_CRC_SELF_TEST=pass')",
        'self_test_case_count_marker': "print('GENKSYMS_CRC_SELF_TEST_CASE_COUNT=4')",
        'explicit_zig_guard': 'genksyms-crc:self-test:explicit_zig_passthrough',
        'explicit_cc_guard': 'genksyms-crc:self-test:explicit_cc_passthrough',
        'mismatch_contract_guard': 'genksyms-crc:self-test:mismatch_contract',
        'repeat_c_compare': "run(diff_base + [str(c_actual), str(c_repeat)], cwd=str(ROOT))",
        'repeat_zig_compare': "run(diff_base + [str(zig_actual), str(zig_repeat)], cwd=str(ROOT))",
        'determinism_marker': "print('GENKSYMS_CRC_DETERMINISM=pass')",
    }

    issues: list[str] = []
    for issue_name, marker in required_markers.items():
        if marker not in source:
            issues.append(f'genksyms_crc_checker:{issue_name}')
    return issues


def validate_mk_elfconfig_checker_gate(checker_script: Path) -> list[str]:
    source = checker_script.read_text(encoding='utf-8')
    required_markers = {
        'self_test_arg': "parser.add_argument('--self-test'",
        'self_test_pass_marker': "print('MK_ELFCONFIG_SELF_TEST=pass')",
        'self_test_case_count_marker': "print('MK_ELFCONFIG_SELF_TEST_CASE_COUNT=8')",
        'duplicate_name_guard': ':duplicate_name:',
        'duplicate_input_guard': ':duplicate_input_hex:',
        'duplicate_expected_guard': ':duplicate_expected:',
        'explicit_tool_guard': 'validate_tool_sources(C_TOOL, ZIG_TOOL)',
        'explicit_tool_drift_guard': 'explicit_tool_drift',
        'repeat_c_compare': "run(diff + [str(c_actual), str(c_repeat)], cwd=str(ROOT))",
        'repeat_zig_compare': "run(diff + [str(zig_actual), str(zig_repeat)], cwd=str(ROOT))",
        'determinism_marker': "print('MK_ELFCONFIG_DETERMINISM=pass')",
    }

    issues: list[str] = []
    for issue_name, marker in required_markers.items():
        if marker not in source:
            issues.append(f'mk_elfconfig_checker:{issue_name}')
    return issues


def validate_phase2_tooling_manifests(tool_manifest_path: Path, cross_targets_path: Path) -> list[str]:
    issues: list[str] = []

    tool_manifest = json.loads(tool_manifest_path.read_text(encoding='utf-8'))
    if not isinstance(tool_manifest, dict):
        issues.append('phase2_tool_manifest:expected_object')
    else:
        if tool_manifest.get('phase') != 'Phase 2':
            issues.append(f"phase2_tool_manifest:phase={tool_manifest.get('phase')!r},expected='Phase 2'")
        if tool_manifest.get('status') != 'closed':
            issues.append(f"phase2_tool_manifest:status={tool_manifest.get('status')!r},expected='closed'")
        tools = tool_manifest.get('tools')
        if not isinstance(tools, list):
            issues.append('phase2_tool_manifest:tools:expected_list')
        else:
            if tool_manifest.get('tool_count') != len(EXPECTED_PHASE2_TOOL_MANIFEST_TOOLS):
                issues.append(
                    'phase2_tool_manifest:tool_count='
                    f"{tool_manifest.get('tool_count')!r},expected={len(EXPECTED_PHASE2_TOOL_MANIFEST_TOOLS)}"
                )
            if tools != EXPECTED_PHASE2_TOOL_MANIFEST_TOOLS:
                issues.append('phase2_tool_manifest:tools=expected_exact_phase2_tool_list')

    cross_targets = json.loads(cross_targets_path.read_text(encoding='utf-8'))
    if not isinstance(cross_targets, dict):
        issues.append('phase2_cross_targets:expected_object')
    else:
        if cross_targets.get('phase') != 'Phase 2':
            issues.append(f"phase2_cross_targets:phase={cross_targets.get('phase')!r},expected='Phase 2'")
        if cross_targets.get('status') != 'closed':
            issues.append(f"phase2_cross_targets:status={cross_targets.get('status')!r},expected='closed'")
        targets = cross_targets.get('targets')
        if not isinstance(targets, list):
            issues.append('phase2_cross_targets:targets:expected_list')
        else:
            if cross_targets.get('target_count') != len(EXPECTED_PHASE2_CROSS_TARGETS):
                issues.append(
                    'phase2_cross_targets:target_count='
                    f"{cross_targets.get('target_count')!r},expected={len(EXPECTED_PHASE2_CROSS_TARGETS)}"
                )
            if targets != EXPECTED_PHASE2_CROSS_TARGETS:
                issues.append('phase2_cross_targets:targets=expected_exact_phase2_cross_target_list')

    return issues


def validate_exact_workflow_runs(workflow_text: str, expected_commands: dict[str, int]) -> list[str]:
    issues: list[str] = []
    for command, expected_count in expected_commands.items():
        expected_line = f'run: {command}'
        count = sum(1 for line in workflow_text.splitlines() if line.strip() == expected_line)
        if count != expected_count:
            issues.append(f'workflow_exact_run:{command}:count={count}:expected={expected_count}')
    return issues


def validate_exact_makefile_runs(makefile_text: str, expected_commands: dict[str, int]) -> list[str]:
    issues: list[str] = []
    stripped_lines = [line.strip() for line in makefile_text.splitlines()]
    for command, expected_count in expected_commands.items():
        count = sum(1 for line in stripped_lines if line.endswith(command))
        if count != expected_count:
            issues.append(f'makefile_exact_run:{command}:count={count}:expected={expected_count}')
    return issues


required_files = [
    ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml',
    ROOT / 'Documentation' / 'zigux' / 'artifact-diff.md',
    ROOT / 'scripts' / 'zigux' / 'artifact_diff.py',
    ROOT / 'scripts' / 'zigux' / 'check-artifact-diff-contract.py',
    ROOT / 'scripts' / 'zigux' / 'fixdep.zig',
    ROOT / 'scripts' / 'zigux' / 'check-fixdep-diff.py',
    ROOT / 'scripts' / 'zigux' / 'genksyms.zig',
    ROOT / 'scripts' / 'zigux' / 'check-genksyms-bridge.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase2-genksyms-bridge-selftest-alignment.py',
    ROOT / 'scripts' / 'zigux' / 'genksyms_crc.zig',
    ROOT / 'scripts' / 'zigux' / 'check-genksyms-crc-diff.py',
    ROOT / 'scripts' / 'zigux' / 'check-kconfig-bridge.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase2-cross.py',
    ROOT / 'scripts' / 'zigux' / 'mk_elfconfig.zig',
    ROOT / 'scripts' / 'zigux' / 'check-mk-elfconfig-diff.py',
    ROOT / 'scripts' / 'zigux' / 'README.md',
    ROOT / 'scripts' / 'zigux' / 'kconfig' / 'conf_bridge.zig',
    ROOT / 'scripts' / 'zigux' / 'kconfig' / 'confdata_bridge.zig',
    ROOT / 'zigux-alpha' / 'BOOTSTRAP_COMMIT_LEDGER.md',
    PHASE2_TOOL_MANIFEST,
    PHASE2_CROSS_TARGETS,
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

kconfig_checker_issues = validate_kconfig_checker_gate(CHECK_KCONFIG_BRIDGE)
if kconfig_checker_issues:
    print('PHASE2_VALIDATION=fail')
    print('MISSING_PHASE2_KCONFIG_CHECKER_GATES_START')
    for item in kconfig_checker_issues:
        print(item)
    print('MISSING_PHASE2_KCONFIG_CHECKER_GATES_END')
    sys.exit(1)

phase2_cross_checker_issues = validate_phase2_cross_checker_gate(CHECK_PHASE2_CROSS)
if phase2_cross_checker_issues:
    print('PHASE2_VALIDATION=fail')
    print('MISSING_PHASE2_CROSS_CHECKER_GATES_START')
    for item in phase2_cross_checker_issues:
        print(item)
    print('MISSING_PHASE2_CROSS_CHECKER_GATES_END')
    sys.exit(1)

genksyms_bridge_checker_issues = validate_genksyms_bridge_checker_gate(CHECK_GENKSYMS_BRIDGE)
if genksyms_bridge_checker_issues:
    print('PHASE2_VALIDATION=fail')
    print('MISSING_PHASE2_GENKSYMS_BRIDGE_CHECKER_GATES_START')
    for item in genksyms_bridge_checker_issues:
        print(item)
    print('MISSING_PHASE2_GENKSYMS_BRIDGE_CHECKER_GATES_END')
    sys.exit(1)

genksyms_crc_checker_issues = validate_genksyms_crc_checker_gate(CHECK_GENKSYMS_CRC)
if genksyms_crc_checker_issues:
    print('PHASE2_VALIDATION=fail')
    print('MISSING_PHASE2_GENKSYMS_CRC_CHECKER_GATES_START')
    for item in genksyms_crc_checker_issues:
        print(item)
    print('MISSING_PHASE2_GENKSYMS_CRC_CHECKER_GATES_END')
    sys.exit(1)

fixdep_checker_issues = validate_fixdep_checker_gate(ROOT / 'scripts' / 'zigux' / 'check-fixdep-diff.py')
if fixdep_checker_issues:
    print('PHASE2_VALIDATION=fail')
    print('MISSING_PHASE2_FIXDEP_CHECKER_GATES_START')
    for item in fixdep_checker_issues:
        print(item)
    print('MISSING_PHASE2_FIXDEP_CHECKER_GATES_END')
    sys.exit(1)

artifact_diff_contract_issues = validate_artifact_diff_contract_gate(
    ROOT / 'scripts' / 'zigux' / 'check-artifact-diff-contract.py'
)
if artifact_diff_contract_issues:
    print('PHASE2_VALIDATION=fail')
    print('MISSING_PHASE2_ARTIFACT_DIFF_GATES_START')
    for item in artifact_diff_contract_issues:
        print(item)
    print('MISSING_PHASE2_ARTIFACT_DIFF_GATES_END')
    sys.exit(1)

mk_elfconfig_checker_issues = validate_mk_elfconfig_checker_gate(CHECK_MK_ELFCONFIG)
if mk_elfconfig_checker_issues:
    print('PHASE2_VALIDATION=fail')
    print('MISSING_PHASE2_MK_ELFCONFIG_CHECKER_GATES_START')
    for item in mk_elfconfig_checker_issues:
        print(item)
    print('MISSING_PHASE2_MK_ELFCONFIG_CHECKER_GATES_END')
    sys.exit(1)

phase2_tooling_manifest_issues = validate_phase2_tooling_manifests(
    PHASE2_TOOL_MANIFEST,
    PHASE2_CROSS_TARGETS,
)
if phase2_tooling_manifest_issues:
    print('PHASE2_VALIDATION=fail')
    print('MISSING_PHASE2_TOOLING_MANIFEST_GATES_START')
    for item in phase2_tooling_manifest_issues:
        print(item)
    print('MISSING_PHASE2_TOOLING_MANIFEST_GATES_END')
    sys.exit(1)

ledger = (ROOT / 'zigux-alpha' / 'BOOTSTRAP_COMMIT_LEDGER.md').read_text(encoding='utf-8')
workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
artifact_doc = (ROOT / 'Documentation' / 'zigux' / 'artifact-diff.md').read_text(encoding='utf-8')
script_readme = (ROOT / 'scripts' / 'zigux' / 'README.md').read_text(encoding='utf-8')
makefile = (ROOT / 'zigux' / 'Makefile').read_text(encoding='utf-8')

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
    'scripts/basic/fixdep.c',
    'python3 scripts/zigux/validate-phase2.py',
    'python3 scripts/zigux/check-artifact-diff-contract.py',
    'python3 scripts/zigux/check-fixdep-diff.py --self-test',
    'python3 scripts/zigux/check-fixdep-diff.py',
    'python3 scripts/zigux/check-genksyms-bridge.py --self-test',
    'python3 scripts/zigux/check-genksyms-bridge.py',
    'python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test',
    'python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py',
    'python3 scripts/zigux/check-genksyms-crc-diff.py',
    'python3 scripts/zigux/check-kconfig-bridge.py --self-test',
    'python3 scripts/zigux/check-kconfig-bridge.py',
    'python3 scripts/zigux/check-phase2-cross.py --self-test',
    'python3 scripts/zigux/check-phase2-cross.py --target',
    'python3 scripts/zigux/check-mk-elfconfig-diff.py',
    'python3 scripts/zigux/artifact_diff.py --self-test',
    'zig test scripts/zigux/fixdep.zig',
    'zig test scripts/zigux/genksyms.zig',
    'zig test scripts/zigux/genksyms_crc.zig',
    'zig test scripts/zigux/kconfig/conf_bridge.zig',
    'zig test scripts/zigux/kconfig/confdata_bridge.zig',
    'zig test scripts/zigux/mk_elfconfig.zig',
]
required_doc_markers = [
    'python3 scripts/zigux/artifact_diff.py --self-test',
    'python3 scripts/zigux/check-artifact-diff-contract.py',
    'fixdep',
    'check-fixdep-diff.py --self-test',
    'repeat-run artifact determinism',
    'sample_multi_target_expected.txt',
    'sample_escaped_space_expected.txt',
    'sample_concatenated_expected.txt',
    'sample_output_write_expected.stderr.txt',
    'genksyms',
    'zigux/tests/fixtures/genksyms_bridge/minimal_expected.json',
    'genksyms_crc',
    'zigux/tests/fixtures/genksyms_crc/expected.json',
    'kconfig_bridge',
    'conf and confdata repeat-run JSON determinism',
    'mk_elfconfig',
    'check-mk-elfconfig-diff.py',
    'repeat-run JSON determinism',
    'elf32_expected.json',
]
required_script_markers = [
    'artifact_diff.py --self-test',
    'check-artifact-diff-contract.py',
    'check-fixdep-diff.py --self-test',
    'check-fixdep-diff.py',
    'repeat-run artifact determinism',
    'check-genksyms-bridge.py --self-test',
    'check-genksyms-bridge.py',
    'check-genksyms-crc-diff.py',
    'check-kconfig-bridge.py --self-test',
    'check-kconfig-bridge.py',
    'check-phase2-cross.py --self-test',
    'check-phase2-cross.py',
    'genksyms.zig',
    'genksyms_crc.zig',
    'kconfig/conf_bridge.zig',
    'kconfig/confdata_bridge.zig',
    'check-mk-elfconfig-diff.py',
    'mk_elfconfig.zig',
]

required_makefile_markers = [
    'phase2-validate:',
    'scripts/zigux/artifact_diff.py --self-test',
    'scripts/zigux/check-artifact-diff-contract.py',
    'scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test',
    'scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py',
    'scripts/zigux/validate-phase2.py',
    'scripts/zigux/validate-phase2-closure.py',
    'scripts/zigux/check-fixdep-diff.py --self-test',
    'scripts/zigux/check-fixdep-diff.py',
    'phase2-kconfig:',
    'scripts/zigux/check-kconfig-bridge.py --self-test',
    'scripts/zigux/check-kconfig-bridge.py',
    'phase2-cross:',
    'scripts/zigux/check-phase2-cross.py --self-test',
    'scripts/zigux/check-phase2-cross.py',
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
for marker in required_makefile_markers:
    if marker not in makefile:
        missing_markers.append(f'make:{marker}')
missing_markers.extend(validate_exact_workflow_runs(workflow, EXACT_WORKFLOW_RUN_COUNTS))
missing_markers.extend(validate_exact_makefile_runs(makefile, EXACT_MAKEFILE_RUN_COUNTS))

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
print(f'PHASE2_REQUIRED_MARKER_COUNT={len(required_ledger_markers) + len(required_workflow_markers) + len(required_doc_markers) + len(required_script_markers) + len(required_makefile_markers)}')
