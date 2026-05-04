#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]
GENKSYMS_BRIDGE_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge'
KCONFIG_BRIDGE_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'kconfig_bridge'
FIXDEP_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep'
FIXDEP_CASES = FIXDEP_DIR / 'cases.json'
CHECK_KCONFIG_BRIDGE = ROOT / 'scripts' / 'zigux' / 'check-kconfig-bridge.py'
CHECK_FIXDEP = ROOT / 'scripts' / 'zigux' / 'check-fixdep-diff.py'
CHECK_ARTIFACT_DIFF_CONTRACT = ROOT / 'scripts' / 'zigux' / 'check-artifact-diff-contract.py'
CHECK_PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT = ROOT / 'scripts' / 'zigux' / 'check-phase2-genksyms-bridge-selftest-alignment.py'
CHECK_PHASE2_KCONFIG_SELFTEST_ALIGNMENT = ROOT / 'scripts' / 'zigux' / 'check-phase2-kconfig-selftest-alignment.py'
CHECK_PHASE2_CROSS_SELFTEST_ALIGNMENT = ROOT / 'scripts' / 'zigux' / 'check-phase2-cross-selftest-alignment.py'
CHECK_PHASE2_TOOLCHAIN_PIN_SCOPE = ROOT / 'scripts' / 'zigux' / 'check-phase2-toolchain-pin-scope.py'
TOOLCHAIN_POLICY = ROOT / 'scripts' / 'zigux' / 'zig-toolchain-policy.json'
TOOLCHAIN_NOTES = ROOT / 'Documentation' / 'zigux' / 'phase2-toolchain-bootstrap-notes.md'
EXPECTED_TOOL_MANIFEST_TOOLS = [
    'scripts/zigux/fixdep.zig',
    'scripts/zigux/genksyms.zig',
    'scripts/zigux/genksyms_crc.zig',
    'scripts/zigux/mk_elfconfig.zig',
    'scripts/zigux/kconfig/conf_bridge.zig',
    'scripts/zigux/kconfig/confdata_bridge.zig',
]
EXPECTED_CROSS_TARGETS = [
    'x86_64-linux-musl',
    'aarch64-linux-musl',
    'riscv64-linux-musl',
]
EXACT_WORKFLOW_RUN_COUNTS = {
    'python3 scripts/zigux/install-zig.py --self-test': 1,
    'python3 scripts/zigux/check-zig-toolchain.py --self-test': 1,
    'python3 scripts/zigux/artifact_diff.py --self-test': 1,
    'python3 scripts/zigux/check-artifact-diff-contract.py': 1,
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
    'python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test': 1,
    'python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py': 1,
    'python3 scripts/zigux/check-phase2-cross.py --self-test': 2,
    'python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}': 1,
    'python3 scripts/zigux/check-zig-toolchain.py': 2,
    'python3 scripts/zigux/install-zig.py --dest .zig-toolchain': 2,
    'python3 scripts/zigux/check-mk-elfconfig-diff.py --self-test': 1,
    'python3 scripts/zigux/check-mk-elfconfig-diff.py': 1,
    'python3 scripts/zigux/validate-phase2.py': 1,
    'python3 scripts/zigux/validate-phase2-closure.py': 1,
}
EXACT_MAKEFILE_RUN_COUNTS = {
    'scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test': 1,
    'scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py': 1,
    'scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test': 1,
    'scripts/zigux/check-phase2-kconfig-selftest-alignment.py': 1,
    'scripts/zigux/validate-phase2.py': 1,
    'scripts/zigux/validate-phase2-closure.py': 1,
}
EXACT_TOOLCHAIN_PIN_SCOPE_MAKEFILE_RUN_COUNTS = {
    'scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test': 1,
    'scripts/zigux/check-phase2-toolchain-pin-scope.py': 1,
    'scripts/zigux/check-zig-toolchain.py': 1,
}


def case_files_from_groups(cases_path: Path, *group_specs: tuple[str, str]) -> list[Path]:
    data = json.loads(cases_path.read_text(encoding='utf-8'))
    discovered: list[Path] = []
    for group_name, field_name in group_specs:
        for case in data.get(group_name, []):
            rel = case.get(field_name)
            if rel:
                discovered.append(cases_path.parent / rel)
    return discovered


def load_fixdep_cases(cases_path: Path) -> list[dict[str, object]]:
    data = json.loads(cases_path.read_text(encoding='utf-8'))
    if not isinstance(data, list):
        raise SystemExit('fixdep cases manifest must be a JSON list')
    return data


def validate_expected_fixdep_cases(cases_path: Path) -> list[str]:
    cases = load_fixdep_cases(cases_path)
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
        if expected_case is None:
            issues.append(f'fixdep_cases:unexpected_name:{name}')
            continue

        for field_name, expected_value in expected_case.items():
            actual_value = case.get(field_name, 0 if field_name == 'expected_exit_code' else None)
            if actual_value != expected_value:
                issues.append(
                    f'fixdep_cases:{name}:{field_name}={actual_value!r},expected={expected_value!r}'
                )

    missing_names = sorted(set(expected_cases) - seen_names)
    for name in missing_names:
        issues.append(f'fixdep_cases:missing_name:{name}')
    if len(cases) != len(expected_cases):
        issues.append(f'fixdep_cases:count={len(cases)},expected={len(expected_cases)}')
    return issues


def validate_kconfig_bridge_manifest(cases_path: Path) -> list[str]:
    data = json.loads(cases_path.read_text(encoding='utf-8'))
    issues: list[str] = []

    if not isinstance(data, dict):
        return ['kconfig_bridge:manifest:expected_object']

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
            'autoconfig': 'generated/phase2/auto-sync.conf',
            'autoheader': 'generated/phase2/autoconf-sync.h',
            'nosilentupdate': '1',
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
            'allconfig_env': 'arch/riscv/configs/allyes-seed.config',
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
            'allconfig': 'seed/allrandom.config',
            'seed': '0xC0FFEE',
            'probability': '10:20:30',
            'expected': 'randconfig_expected.json',
        },
        {
            'name': 'listnewconfig',
            'mode': 'listnewconfig',
            'kconfig': 'Kconfig',
            'config': 'pending/.config',
            'arch': 's390',
            'expected': 'listnewconfig_expected.json',
        },
        {
            'name': 'helpnewconfig',
            'mode': 'helpnewconfig',
            'kconfig': 'Kconfig',
            'config': 'help/.config',
            'arch': 'powerpc64le',
            'expected': 'helpnewconfig_expected.json',
        },
        {
            'name': 'olddefconfig',
            'mode': 'olddefconfig',
            'kconfig': 'Kconfig',
            'config': '.config',
            'arch': 'x86_64',
            'expected': 'olddefconfig_expected.json',
        },
        {
            'name': 'yes2modconfig',
            'mode': 'yes2modconfig',
            'kconfig': 'Kconfig',
            'config': 'rewrite/.config',
            'arch': 'x86',
            'expected': 'yes2modconfig_expected.json',
        },
        {
            'name': 'mod2yesconfig',
            'mode': 'mod2yesconfig',
            'kconfig': 'Kconfig',
            'config': 'promote/.config',
            'arch': 'loongarch',
            'expected': 'mod2yesconfig_expected.json',
        },
        {
            'name': 'mod2noconfig',
            'mode': 'mod2noconfig',
            'kconfig': 'Kconfig',
            'config': 'demote/.config',
            'arch': 'mips',
            'expected': 'mod2noconfig_expected.json',
        },
    ]
    expected_confdata_cases = [
        {'name': 'duplicate_assignments', 'input': 'duplicate_assignments.config', 'expected': 'duplicate_assignments_expected.json'},
        {'name': 'empty_string', 'input': 'empty_string.config', 'expected': 'empty_string_expected.json'},
        {'name': 'empty_symbol_names', 'input': 'empty_symbol_names.config', 'expected': 'empty_symbol_names_expected.json'},
        {'name': 'escaped_control_sequences', 'input': 'escaped_control_sequences.config', 'expected': 'escaped_control_sequences_expected.json'},
        {'name': 'escaped_low_control_bytes', 'input': 'escaped_low_control_bytes.config', 'expected': 'escaped_low_control_bytes_expected.json'},
        {'name': 'escaped_strings', 'input': 'escaped_strings.config', 'expected': 'escaped_strings_expected.json'},
        {'name': 'explicit_n_tristate', 'input': 'explicit_n_tristate.config', 'expected': 'explicit_n_tristate_expected.json'},
        {'name': 'final_trailing_carriage_return', 'input': 'final_trailing_carriage_return.config', 'expected': 'final_trailing_carriage_return_expected.json'},
        {'name': 'final_unterminated_unset_comment', 'input': 'final_unterminated_unset_comment.config', 'expected': 'final_unterminated_unset_comment_expected.json'},
        {'name': 'ignore_non_config_lines', 'input': 'ignore_non_config_lines.config', 'expected': 'ignore_non_config_lines_expected.json'},
        {'name': 'malformed_quoted_string', 'input': 'malformed_quoted_string.config', 'expected': 'malformed_quoted_string_expected.json'},
        {'name': 'negative_signed_numeric_kinds', 'input': 'negative_signed_numeric_kinds.config', 'expected': 'negative_signed_numeric_kinds_expected.json'},
        {'name': 'numeric_kinds', 'input': 'numeric_kinds.config', 'expected': 'numeric_kinds_expected.json'},
        {'name': 'quoted_suffix_bytes', 'input': 'quoted_suffix_bytes.config', 'expected': 'quoted_suffix_bytes_expected.json'},
        {'name': 'sample', 'input': 'sample.config', 'expected': 'sample_expected.json'},
        {'name': 'sample_crlf', 'input': 'sample_crlf.config', 'expected': 'sample_crlf_expected.json'},
        {'name': 'signed_numeric_kinds', 'input': 'signed_numeric_kinds.config', 'expected': 'signed_numeric_kinds_expected.json'},
        {'name': 'trailing_escaped_backslash', 'input': 'trailing_escaped_backslash.config', 'expected': 'trailing_escaped_backslash_expected.json'},
    ]

    expected_mode_order = [case['mode'] for case in expected_conf_cases]
    manifest_mode_order = [case.get('mode') for case in conf_cases if isinstance(case, dict) and case.get('mode')]
    if manifest_mode_order != expected_mode_order:
        issues.append(
            'kconfig_bridge:conf_case_order=' + ','.join(manifest_mode_order) +
            ',expected=' + ','.join(expected_mode_order)
        )

    if conf_cases != expected_conf_cases:
        issues.append('kconfig_bridge:conf_cases:expected_exact_manifest')
    if confdata_cases != expected_confdata_cases:
        issues.append('kconfig_bridge:confdata_cases:expected_exact_manifest')

    return issues


def validate_kconfig_checker_gate(checker_script: Path) -> list[str]:
    source = checker_script.read_text(encoding='utf-8')
    required_markers = {
        'self_test_arg': "parser.add_argument('--self-test'",
        'self_test_pass_marker': "print('KCONFIG_BRIDGE_SELF_TEST=pass')",
        'self_test_case_count_marker': "print(f'KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT={total_self_test_cases}')",
        'unexpected_conf_mode_guard': 'UNEXPECTED_CONF_BRIDGE_MODES_START',
        'unsorted_conf_case_guard': 'UNSORTED_CONF_CASE_ORDER_START',
        'unsorted_confdata_case_guard': 'UNSORTED_CONFDATA_CASE_ORDER_START',
        'invalid_manifest_guard': 'INVALID_KCONFIG_MANIFEST_START',
        'orphaned_fixture_guard': 'orphaned_fixture:',
        'exact_confdata_compare': 'compare_text_artifacts(actual, repeat)',
        'rebuilt_confdata_compare': 'compare_text_artifacts(actual, rebuild)',
        'randconfig_seed_env': "env['KCONFIG_SEED'] = case['seed']",
        'randconfig_probability_env': "env['KCONFIG_PROBABILITY'] = case['probability']",
        'determinism_marker': "print('KCONFIG_BRIDGE_DETERMINISM=pass')",
    }

    issues: list[str] = []
    for issue_name, markers in required_markers.items():
        if not any(marker in source for marker in (markers if isinstance(markers, tuple) else (markers,))):
            issues.append(f'kconfig_checker:{issue_name}')
    return issues


def validate_phase2_cross_checker_gate(checker_script: Path) -> list[str]:
    source = checker_script.read_text(encoding='utf-8')
    required_markers = {
        'self_test_arg': "parser.add_argument('--self-test'",
        'self_test_pass_marker': "print('PHASE2_CROSS_SELF_TEST=pass')",
        'self_test_case_count_marker': "print('PHASE2_CROSS_SELF_TEST_CASE_COUNT=9')",
        'duplicate_tool_guard': 'phase2-cross:duplicate_tool:',
        'tool_count_mismatch_guard': 'phase2-cross:tool_count_mismatch',
        'target_count_mismatch_guard': 'phase2-cross:target_count_mismatch',
        'duplicate_target_guard': 'phase2-cross:duplicate_target:',
        'unexpected_target_guard': 'phase2-cross:unexpected_target:',
        'duplicate_manifest_target_guard': 'phase2-cross:duplicate_manifest_target:',
    }

    issues: list[str] = []
    for issue_name, marker in required_markers.items():
        if marker not in source:
            issues.append(f'phase2_cross_checker:{issue_name}')
    return issues


def validate_phase2_cross_alignment_checker_gate(checker_script: Path) -> list[str]:
    source = checker_script.read_text(encoding='utf-8')
    required_markers = {
        'self_test_arg': 'parser.add_argument("--self-test"',
        'self_test_pass_marker': 'print("PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass")',
        'self_test_case_count_marker': 'print("PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT=16")',
        'validator_anchor': 'PHASE2_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2.py"',
        'closure_doc_anchor': 'CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"',
        'targets_manifest_anchor': 'TARGETS_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"',
        'pass_marker': 'print("PHASE2_CROSS_ALIGNMENT=pass")',
    }

    issues: list[str] = []
    for issue_name, marker in required_markers.items():
        if marker not in source:
            issues.append(f'phase2_cross_alignment_checker:{issue_name}')
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
        'self_test_case_count_marker': "print('GENKSYMS_CRC_SELF_TEST_CASE_COUNT=11')",
        'missing_fixture_guard': 'genksyms-crc:self-test:missing_expected_fixture',
        'missing_input_guard': 'genksyms-crc:self-test:missing_input_fixture',
        'orphaned_expected_guard': 'orphaned_expected:',
        'orphaned_input_guard': 'orphaned_input:',
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


def validate_fixdep_checker_gate(checker_script: Path) -> list[str]:
    source = checker_script.read_text(encoding='utf-8')
    required_markers = {
        'repeat_c_stdout': 'diff_text(c_actual, c_repeat)',
        'repeat_zig_stdout': 'diff_text(zig_actual, zig_repeat)',
        'repeat_c_stderr': 'diff_text(c_actual_stderr, c_repeat_stderr)',
        'repeat_zig_stderr': 'diff_text(zig_actual_stderr, zig_repeat_stderr)',
        'expected_stderr_fallback': "expected_stderr_path = expected_stderr or implicit_expected_stderr",
        'quiet_success_stderr_gate': "implicit_expected_stderr.write_text('', encoding='utf-8')",
        'determinism_marker': "print('FIXDEP_DETERMINISM=pass')",
    }

    issues: list[str] = []
    for issue_name, marker in required_markers.items():
        if marker not in source:
            issues.append(f'fixdep_checker:{issue_name}')
    return issues


def validate_artifact_diff_contract_gate(checker_script: Path) -> list[str]:
    source = checker_script.read_text(encoding='utf-8')
    required_markers = {
        'text_pass_case': "['--mode', 'text', str(expected), str(actual)]",
        'missing_expected_case': 'EXPECTED_EXISTS=False',
        'missing_actual_case': 'ACTUAL_EXISTS=False',
        'expected_json_error_case': 'EXPECTED_JSON_ERROR=',
        'actual_json_error_case': 'ACTUAL_JSON_ERROR=',
        'sha256_pass_case': 'SHA256=0051a1ffdd63accde60d9c9893094b287388cecb4fcc734a204ea5a36a5c3576',
        'sha256_fail_case': 'EXPECTED_SHA256=',
        'sha256_fail_actual_case': 'ACTUAL_SHA256=',
        'contract_pass_marker': 'expected_contract_summary_lines()',
    }

    issues: list[str] = []
    for issue_name, marker in required_markers.items():
        if marker not in source:
            issues.append(f'artifact_diff_contract:{issue_name}')
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
    ROOT / 'Documentation' / 'zigux' / 'phase2-closure.md',
    TOOLCHAIN_NOTES,
    ROOT / 'scripts' / 'zigux' / 'artifact_diff.py',
    ROOT / 'scripts' / 'zigux' / 'check-artifact-diff-contract.py',
    ROOT / 'scripts' / 'zigux' / 'check-fixdep-diff.py',
    ROOT / 'scripts' / 'zigux' / 'check-genksyms-bridge.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase2-genksyms-bridge-selftest-alignment.py',
    CHECK_PHASE2_KCONFIG_SELFTEST_ALIGNMENT,
    CHECK_PHASE2_CROSS_SELFTEST_ALIGNMENT,
    CHECK_PHASE2_TOOLCHAIN_PIN_SCOPE,
    TOOLCHAIN_POLICY,
    ROOT / 'scripts' / 'zigux' / 'check-genksyms-crc-diff.py',
    ROOT / 'scripts' / 'zigux' / 'check-kconfig-bridge.py',
    ROOT / 'scripts' / 'zigux' / 'check-mk-elfconfig-diff.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase2-cross.py',
    ROOT / 'scripts' / 'zigux' / 'validate-phase2.py',
    ROOT / 'scripts' / 'zigux' / 'validate-phase2-closure.py',
    ROOT / 'scripts' / 'zigux' / 'fixdep.zig',
    ROOT / 'scripts' / 'zigux' / 'genksyms.zig',
    ROOT / 'scripts' / 'zigux' / 'genksyms_crc.zig',
    ROOT / 'scripts' / 'zigux' / 'mk_elfconfig.zig',
    ROOT / 'scripts' / 'zigux' / 'README.md',
    ROOT / 'scripts' / 'zigux' / 'kconfig' / 'conf_bridge.zig',
    ROOT / 'scripts' / 'zigux' / 'kconfig' / 'confdata_bridge.zig',
    ROOT / 'zigux-alpha' / 'BOOTSTRAP_COMMIT_LEDGER.md',
    ROOT / 'zigux' / 'Makefile',
    FIXDEP_CASES,
    FIXDEP_DIR / 'sample_escaped_colon_expected.txt',
    FIXDEP_DIR / 'sample_concatenated_expected.txt',
    FIXDEP_DIR / 'sample_output_write_expected.txt',
    FIXDEP_DIR / 'sample_output_write_expected.stderr.txt',
    GENKSYMS_BRIDGE_DIR / 'genksyms_bridge_c_harness.c',
    GENKSYMS_BRIDGE_DIR / 'cases.json',
    KCONFIG_BRIDGE_DIR / 'cases.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_tool_manifest.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_cross_targets.json',
]
required_files.extend(case_files_from_groups(
    GENKSYMS_BRIDGE_DIR / 'cases.json',
    ('cases', 'expected'),
))
required_files.extend(case_files_from_groups(
    KCONFIG_BRIDGE_DIR / 'cases.json',
    ('conf_cases', 'expected'),
    ('confdata_cases', 'input'),
    ('confdata_cases', 'expected'),
))

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print('PHASE2_CLOSURE_VALIDATION=fail')
    print('MISSING_PHASE2_CLOSURE_FILES_START')
    for item in missing:
        print(item)
    print('MISSING_PHASE2_CLOSURE_FILES_END')
    sys.exit(1)

closure = (ROOT / 'Documentation' / 'zigux' / 'phase2-closure.md').read_text(encoding='utf-8')
workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
ledger = (ROOT / 'zigux-alpha' / 'BOOTSTRAP_COMMIT_LEDGER.md').read_text(encoding='utf-8')
script_readme = (ROOT / 'scripts' / 'zigux' / 'README.md').read_text(encoding='utf-8')
artifact_doc = (ROOT / 'Documentation' / 'zigux' / 'artifact-diff.md').read_text(encoding='utf-8')
toolchain_notes = TOOLCHAIN_NOTES.read_text(encoding='utf-8')
makefile = (ROOT / 'zigux' / 'Makefile').read_text(encoding='utf-8')
tool_manifest = json.loads((ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_tool_manifest.json').read_text(encoding='utf-8'))
targets_manifest = json.loads((ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_cross_targets.json').read_text(encoding='utf-8'))
fixdep_cases = load_fixdep_cases(FIXDEP_CASES)
fixdep_case_count = len(fixdep_cases)
fixdep_case_issues = validate_expected_fixdep_cases(FIXDEP_CASES)

required_closure_markers = [
    'PHASE2_STATUS=closed',
    'PHASE2_TOOL_COUNT=6',
    'PHASE2_CROSS_TARGET_COUNT=3',
    'x86_64-linux',
    'scripts/zigux/zig-toolchain-policy.json',
    'scripts/zigux/check-phase2-toolchain-pin-scope.py',
    'PHASE2_FIXDEP_GATE=python3 scripts/zigux/check-fixdep-diff.py',
    'PHASE2_FIXDEP_DETERMINISM=check-fixdep-diff.py replays C and Zig outputs twice before comparing artifacts',
    'PHASE2_FIXDEP_FULL_READ_POLICY=fixdep.zig reads dependency files at full C-helper size and maps short writes to fixdep output errors',
    f'PHASE2_FIXDEP_CASE_COUNT={fixdep_case_count}',
    'PHASE2_FIXDEP_OUTPUT_WRITE_CASE=zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt',
    'PHASE2_GENKSYMS_BRIDGE_GATE=python3 scripts/zigux/check-genksyms-bridge.py',
    'PHASE2_GENKSYMS_BRIDGE_DETERMINISM=check-genksyms-bridge.py replays C and Zig bridge outputs twice before comparing artifacts',
    'PHASE2_GENKSYMS_BRIDGE_CASE_COUNT=26',
    'PHASE2_GENKSYMS_BRIDGE_INLINE_SHORT_CASE=zigux/tests/fixtures/genksyms_bridge/short_inline_reference_dump_types_expected.json',
    'PHASE2_GENKSYMS_BRIDGE_CLUSTERED_SHORT_INLINE_CASE=zigux/tests/fixtures/genksyms_bridge/clustered_short_inline_reference_expected.json',
    'PHASE2_GENKSYMS_BRIDGE_MISSING_SHORT_DUMP_TYPES_CASE=zigux/tests/fixtures/genksyms_bridge/missing_dump_types_argument_expected.json',
    'PHASE2_GENKSYMS_BRIDGE_POSITIONAL_CASES=zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json,zigux/tests/fixtures/genksyms_bridge/explicit_terminator_positional_passthrough_expected.json',
    'PHASE2_GENKSYMS_BRIDGE_STDERR_POLICY=success-path stderr silence plus repeat-run stderr determinism are required for closure',
    'PHASE2_GENKSYMS_BRIDGE_EVIDENCE=artifact fixtures plus abbreviated-long, inline-short, clustered-short-inline, missing-short-dump-types, lone-dash, explicit-terminator, empty-long-name, abbreviated-dump-types, and reference-limit coverage are required for closure',
    'PHASE2_GENKSYMS_CRC_DETERMINISM=check-genksyms-crc-diff.py replays C and Zig outputs twice before comparing artifacts',
    'PHASE2_MK_ELFCONFIG_SELF_TEST=python3 scripts/zigux/check-mk-elfconfig-diff.py --self-test',
    'genksyms bridge parses clustered short flags before inline reference argument',
    'genksyms bridge accepts abbreviated unique long options',
    'genksyms bridge treats lone dash as positional passthrough',
    'genksyms bridge permutes prior positionals behind explicit terminator',
    'genksyms bridge reports missing short dump-types argument in getopt style',
    'genksyms bridge canonicalizes abbreviated dump-types missing-argument errors',
    'genksyms bridge rejects reference lists beyond the bounded C harness limit',
    'PHASE2_KCONFIG_BRIDGE_SELF_TEST=python3 scripts/zigux/check-kconfig-bridge.py --self-test',
    'PHASE2_KCONFIG_BRIDGE_GATE=python3 scripts/zigux/check-kconfig-bridge.py',
    'PHASE2_KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT=6',
    'PHASE2_KCONFIG_BRIDGE_DETERMINISM=check-kconfig-bridge.py replays conf and confdata outputs twice and compares a rebuilt confdata binary against the same JSON artifacts',
    'conf bridge emits allconfig env for allconfig family modes',
    'conf bridge requires mode arg for defconfig modes',
    'conf bridge emits savedefconfig mode argument before kconfig',
    'conf bridge escapes low control bytes in argv and env values',
    'confdata bridge decodes escaped control sequences in quoted strings',
    'confdata bridge keeps empty quoted strings as string values',
    'confdata bridge keeps explicit n assignments as tristate values',
    'confdata bridge skips entries with empty symbol names',
    'confdata bridge skips malformed quoted strings',
    'confdata bridge distinguishes integer, hex, and fallback scalar values',
    'confdata bridge keeps quoted payloads before trailing suffix bytes',
    'confdata bridge accepts CRLF config lines',
    'confdata bridge rejects empty config path arguments',
    'confdata bridge escapes low control bytes in emitted json',
    'PHASE2_KCONFIG_BRIDGE_CONF_CASE_COUNT=16',
    'PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=18',
    'PHASE2_KCONFIG_BRIDGE_ALLCONFIG_CASES=zigux/tests/fixtures/kconfig_bridge/allnoconfig_expected.json,zigux/tests/fixtures/kconfig_bridge/randconfig_expected.json',
    'PHASE2_KCONFIG_BRIDGE_ARGUMENT_CASES=zigux/tests/fixtures/kconfig_bridge/defconfig_expected.json,zigux/tests/fixtures/kconfig_bridge/savedefconfig_expected.json',
    'PHASE2_KCONFIG_BRIDGE_LOW_CONTROL_CASE=zigux/tests/fixtures/kconfig_bridge/escaped_low_control_bytes_expected.json',
    'PHASE2_KCONFIG_BRIDGE_MANIFEST_POLICY=check-kconfig-bridge.py rejects uncovered modes, malformed manifests, duplicate fixture references, orphaned fixture files, and non-canonical confdata names before replay',
    'PHASE2_KCONFIG_BRIDGE_EVIDENCE=artifact fixtures plus conf bridge mode coverage, allconfig env, mode-arg, manifest-determinism, confdata escaped-control decode, empty-string, empty-symbol, explicit-n, malformed-quote, signed-numeric, trailing-unset-comment, quoted-suffix, CRLF, trailing-escaped-backslash, empty-path rejection, and low-control JSON emission anchors are required for closure',
    'PHASE2_MK_ELFCONFIG_GATE=python3 scripts/zigux/check-mk-elfconfig-diff.py',
    'PHASE2_MK_ELFCONFIG_DETERMINISM=check-mk-elfconfig-diff.py replays C and Zig outputs twice before comparing artifacts',
    'PHASE2_CROSS_SELF_TEST=python3 scripts/zigux/check-phase2-cross.py --self-test',
    'PHASE2_CROSS_GATE=python3 scripts/zigux/check-phase2-cross.py',
    'PHASE2_CROSS_ALIGNMENT_SELF_TEST=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test',
    'PHASE2_CROSS_ALIGNMENT_GATE=python3 scripts/zigux/check-phase2-cross-selftest-alignment.py',
    'PHASE2_CROSS_MANIFEST_POLICY=check-phase2-cross.py rejects duplicate tool entries, duplicate requested targets, unexpected explicit targets, duplicate manifest targets, and manifest-count drift before live compile replay',
    'PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test',
    'PHASE2_TOOLCHAIN_PIN_SCOPE_GATE=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py',
    'PHASE2_TOOLCHAIN_PIN_SCOPE_POLICY=scripts/zigux/zig-toolchain-policy.json keeps the bootstrap archive pin limited to x86_64-linux until a new runner target gains first-class workflow evidence',
    'PHASE2_SHARED_VALIDATOR=python3 scripts/zigux/validate-phase2.py',
    'PHASE2_CLOSURE_GATE=python3 scripts/zigux/validate-phase2-closure.py',
    'PHASE2_ARTIFACT_DIFF_SELF_TEST=python3 scripts/zigux/artifact_diff.py --self-test',
    'PHASE2_ARTIFACT_DIFF_CONTRACT=python3 scripts/zigux/check-artifact-diff-contract.py',
    'dep parsing skips escaped-newline comments before the first target',
    'dep parsing continues dependency tokens across escaped newlines',
    'dep parsing keeps the first source across concatenated target entries',
    'dep parsing unescapes escaped hash and colon tokens once',
    'dependency file error messages keep C helper wording',
    'missing dependency path is preserved for later error reporting',
    'output writer maps print and flush failures to fixdep output-write errors',
    'preserving a primary error ignores late output flush failures',
    'PHASE2_FIXDEP_EVIDENCE=artifact fixtures plus direct escaped-newline-comment, dep-continuation, concatenated-target, escaped-token, dependency-file-error, missing-path-preservation, output-write, and primary-error-preservation unit anchors are required for closure',
    'PHASE2_ROLLBACK=keep C kbuild tools authoritative and remove failing Zigux bridge/tool from workflow wiring',
]
required_workflow_markers = [
    'python3 scripts/zigux/artifact_diff.py --self-test',
    'python3 scripts/zigux/check-artifact-diff-contract.py',
    'python3 scripts/zigux/check-fixdep-diff.py',
    'python3 scripts/zigux/check-genksyms-bridge.py',
    'python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test',
    'python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py',
    'python3 scripts/zigux/check-genksyms-crc-diff.py',
    'python3 scripts/zigux/check-kconfig-bridge.py --self-test',
    'python3 scripts/zigux/check-kconfig-bridge.py',
    'python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test',
    'python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py',
    'python3 scripts/zigux/check-phase2-cross.py --self-test',
    'python3 scripts/zigux/check-phase2-cross.py --target',
    'python3 scripts/zigux/check-mk-elfconfig-diff.py',
    'python3 scripts/zigux/validate-phase2-closure.py',
    'zig test scripts/zigux/fixdep.zig',
    'zig test scripts/zigux/genksyms.zig',
    'zig test scripts/zigux/genksyms_crc.zig',
    'zig test scripts/zigux/kconfig/conf_bridge.zig',
    'zig test scripts/zigux/kconfig/confdata_bridge.zig',
    'zig test scripts/zigux/mk_elfconfig.zig',
]
required_ledger_markers = [
    'feat(scripts/zigux): add bounded Phase 2 genksyms wrapper lane',
    'ci(zigux): widen Phase 2 closure matrix',
    'docs(zigux): reopen and close broadened Phase 2 tranche',
    'feat(scripts/zigux): add bounded Phase 2 kconfig bridge scaffolding',
    'ci(zigux): add Phase 2 cross-arch build matrix',
    'docs(zigux): close bounded Phase 2 toolchain tranche',
]
required_readme_markers = [
    'artifact_diff.py --self-test',
    'check-artifact-diff-contract.py',
    'check-genksyms-bridge.py',
    'check-genksyms-crc-diff.py',
    'check-kconfig-bridge.py --self-test',
    'check-kconfig-bridge.py',
    'check-phase2-cross.py --self-test',
    'duplicate tool entries',
    'check-phase2-toolchain-pin-scope.py --self-test',
    'check-phase2-toolchain-pin-scope.py',
    'zig-toolchain-policy.json',
    'x86_64-linux',
    'Documentation/zigux/phase2-toolchain-bootstrap-notes.md',
    'Documentation/zigux/review-checklist.md',
    'make -C zigux phase2-validate',
    'make -C zigux phase2',
    'kbuild-facing review path',
    'check-mk-elfconfig-diff.py',
    'check-phase2-cross.py',
    'genksyms.zig',
    'genksyms_crc.zig',
    'mk_elfconfig.zig',
    'kconfig/conf_bridge.zig',
    'kconfig/confdata_bridge.zig',
]
required_doc_markers = [
    'python3 scripts/zigux/artifact_diff.py --self-test',
    'python3 scripts/zigux/check-artifact-diff-contract.py',
    'genksyms_bridge',
    'genksyms_crc',
    'kconfig_bridge',
    'mk_elfconfig',
    'phase2_cross_targets.json',
]
required_makefile_markers = [
    'phase2-validate:',
    'artifact_diff.py --self-test',
    'check-artifact-diff-contract.py',
    'phase2-tools:',
    'phase2-kconfig:',
    'check-kconfig-bridge.py --self-test',
    'phase2-cross:',
    'check-phase2-cross.py --self-test',
    'check-fixdep-diff.py',
    'check-genksyms-bridge.py',
    'check-phase2-genksyms-bridge-selftest-alignment.py --self-test',
    'check-phase2-genksyms-bridge-selftest-alignment.py',
    'check-phase2-kconfig-selftest-alignment.py --self-test',
    'check-phase2-kconfig-selftest-alignment.py',
    'check-genksyms-crc-diff.py',
    'check-kconfig-bridge.py',
    'check-mk-elfconfig-diff.py',
    '$(ZIG) test scripts/zigux/fixdep.zig',
    '$(ZIG) test scripts/zigux/genksyms.zig',
    '$(ZIG) test scripts/zigux/genksyms_crc.zig',
    '$(ZIG) test scripts/zigux/kconfig/conf_bridge.zig',
    '$(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig',
    '$(ZIG) test scripts/zigux/mk_elfconfig.zig',
]
required_toolchain_notes_markers = [
    'scripts/zigux/zig-toolchain-policy.json',
    'python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test',
    'python3 scripts/zigux/check-phase2-toolchain-pin-scope.py',
    'python3 scripts/zigux/validate-phase2.py',
    'python3 scripts/zigux/validate-phase2-closure.py',
    'Documentation/zigux/phase2-closure.md',
    'Documentation/zigux/review-checklist.md',
    'make -C zigux phase2-validate',
    'make -C zigux phase2',
    'x86_64-linux',
]

missing_markers = []
for marker in required_closure_markers:
    if marker not in closure:
        missing_markers.append(f'closure:{marker}')
for marker in required_workflow_markers:
    if marker not in workflow:
        missing_markers.append(f'workflow:{marker}')
for marker in required_ledger_markers:
    if marker not in ledger:
        missing_markers.append(f'ledger:{marker}')
for marker in required_readme_markers:
    if marker not in script_readme:
        missing_markers.append(f'scripts:{marker}')
for marker in required_doc_markers:
    if marker not in artifact_doc:
        missing_markers.append(f'doc:{marker}')
for marker in required_makefile_markers:
    if marker not in makefile:
        missing_markers.append(f'make:{marker}')
for marker in required_toolchain_notes_markers:
    if marker not in toolchain_notes:
        missing_markers.append(f'toolchain_notes:{marker}')

if tool_manifest.get('phase') != 'Phase 2':
    missing_markers.append('manifest:phase=Phase 2')
if tool_manifest.get('status') != 'closed':
    missing_markers.append('manifest:status=closed')
if tool_manifest.get('tool_count') != 6:
    missing_markers.append('manifest:tool_count=6')
tool_manifest_tools = tool_manifest.get('tools', [])
if len(tool_manifest_tools) != 6:
    missing_markers.append(f'manifest:tools_len={len(tool_manifest_tools)}')
if tool_manifest_tools != EXPECTED_TOOL_MANIFEST_TOOLS:
    missing_markers.append('manifest:tools=exact_phase2_tool_list')
for rel in tool_manifest_tools:
    if not (ROOT / rel).exists():
        missing_markers.append(f'manifest_file:{rel}')

if targets_manifest.get('phase') != 'Phase 2':
    missing_markers.append('targets:phase=Phase 2')
if targets_manifest.get('status') != 'closed':
    missing_markers.append('targets:status=closed')
if targets_manifest.get('target_count') != 3:
    missing_markers.append('targets:target_count=3')
target_manifest_targets = targets_manifest.get('targets', [])
if len(target_manifest_targets) != 3:
    missing_markers.append(f'targets:len={len(target_manifest_targets)}')
if target_manifest_targets != EXPECTED_CROSS_TARGETS:
    missing_markers.append('targets:list=x86_64-linux-musl,aarch64-linux-musl,riscv64-linux-musl')

missing_markers.extend(validate_kconfig_bridge_manifest(KCONFIG_BRIDGE_DIR / 'cases.json'))
missing_markers.extend(validate_kconfig_checker_gate(CHECK_KCONFIG_BRIDGE))
missing_markers.extend(validate_phase2_cross_checker_gate(ROOT / 'scripts' / 'zigux' / 'check-phase2-cross.py'))
missing_markers.extend(validate_phase2_cross_alignment_checker_gate(CHECK_PHASE2_CROSS_SELFTEST_ALIGNMENT))
missing_markers.extend(validate_genksyms_bridge_checker_gate(ROOT / 'scripts' / 'zigux' / 'check-genksyms-bridge.py'))
missing_markers.extend(validate_genksyms_crc_checker_gate(ROOT / 'scripts' / 'zigux' / 'check-genksyms-crc-diff.py'))
missing_markers.extend(validate_fixdep_checker_gate(CHECK_FIXDEP))
missing_markers.extend(validate_artifact_diff_contract_gate(CHECK_ARTIFACT_DIFF_CONTRACT))
missing_markers.extend(validate_mk_elfconfig_checker_gate(ROOT / 'scripts' / 'zigux' / 'check-mk-elfconfig-diff.py'))
missing_markers.extend(fixdep_case_issues)
missing_markers.extend(validate_exact_workflow_runs(workflow, EXACT_WORKFLOW_RUN_COUNTS))
missing_markers.extend(validate_exact_makefile_runs(makefile, EXACT_MAKEFILE_RUN_COUNTS))
missing_markers.extend(validate_exact_makefile_runs(makefile, EXACT_TOOLCHAIN_PIN_SCOPE_MAKEFILE_RUN_COUNTS))

if missing_markers:
    print('PHASE2_CLOSURE_VALIDATION=fail')
    print('MISSING_PHASE2_CLOSURE_MARKERS_START')
    for marker in missing_markers:
        print(marker)
    print('MISSING_PHASE2_CLOSURE_MARKERS_END')
    sys.exit(1)

print('PHASE2_CLOSURE_VALIDATION=pass')
print(f'PHASE2_CLOSURE_REQUIRED_FILE_COUNT={len(required_files)}')
print(f'PHASE2_CLOSURE_REQUIRED_MARKER_COUNT={len(required_closure_markers) + len(required_workflow_markers) + len(required_ledger_markers) + len(required_readme_markers) + len(required_doc_markers) + len(required_makefile_markers) + len(required_toolchain_notes_markers)}')
