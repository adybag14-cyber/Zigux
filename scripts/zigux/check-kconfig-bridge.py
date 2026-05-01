#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIFF = ROOT / 'scripts' / 'zigux' / 'artifact_diff.py'
CONF_BRIDGE = ROOT / 'scripts' / 'zigux' / 'kconfig' / 'conf_bridge.zig'
CONFDATA_BRIDGE = ROOT / 'scripts' / 'zigux' / 'kconfig' / 'confdata_bridge.zig'
FIXTURE_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'kconfig_bridge'
CONF_ALLCONFIG_MODES = {'allnoconfig', 'allyesconfig', 'allmodconfig', 'alldefconfig', 'randconfig'}


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    env = shutil.which('zig')
    if env:
        return env
    fallback = ROOT.parent / 'toolchains' / 'zig-master' / 'current' / 'zig.exe'
    if fallback.exists():
        return str(fallback)
    raise SystemExit('zig not found; pass --zig or add zig to PATH')


def compile_tool(zig: str, source: Path, output: Path) -> None:
    run([zig, 'build-exe', str(source), '-femit-bin=' + str(output)], cwd=str(ROOT))


def fail_check(block: str, values: list[str]) -> None:
    print('KCONFIG_BRIDGE_DIFF=fail')
    print(f'{block}_START')
    for value in values:
        print(value)
    print(f'{block}_END')
    raise SystemExit(1)


def compare_json_artifacts(expected: Path, actual: Path) -> None:
    run([sys.executable, str(ARTIFACT_DIFF), '--mode', 'json', str(expected), str(actual)], cwd=str(ROOT))


def compare_text_artifacts(expected: Path, actual: Path) -> None:
    run([sys.executable, str(ARTIFACT_DIFF), '--mode', 'text', str(expected), str(actual)], cwd=str(ROOT))


def load_cases(fixture_dir: Path = FIXTURE_DIR) -> object:
    return json.loads((fixture_dir / 'cases.json').read_text(encoding='utf-8'))


def supported_conf_modes_in_order(conf_bridge_path: Path = CONF_BRIDGE) -> list[str]:
    source = conf_bridge_path.read_text(encoding='utf-8')
    match = re.search(r'pub const Mode = enum \{(.*?)\n\s*pub fn parse', source, re.S)
    if not match:
        raise SystemExit('failed to parse conf bridge Mode enum')

    modes: list[str] = []
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith('pub ') or line.startswith('//'):
            continue
        if line.endswith(','):
            candidate = line[:-1].strip()
            if candidate and candidate.isidentifier():
                modes.append(candidate)
    if not modes:
        raise SystemExit('failed to discover conf bridge modes')
    return modes


def supported_conf_modes_from_conf_c_in_order(conf_c_path: Path = ROOT / 'scripts' / 'kconfig' / 'conf.c') -> list[str]:
    source = conf_c_path.read_text(encoding='utf-8')
    match = re.search(r'static const struct option long_opts\[\] = \{(.*?)\n\};', source, re.S)
    if not match:
        raise SystemExit('failed to parse scripts/kconfig/conf.c long option surface')

    modes = re.findall(
        r'\{"([a-z0-9]+config)\",\s+(?:no_argument|required_argument),\s+&input_mode_opt,\s+([a-z0-9]+config)\}',
        match.group(1),
    )
    if not modes:
        raise SystemExit('failed to discover scripts/kconfig/conf.c modes')
    return [enum_name for _option_name, enum_name in modes]


def ensure_conf_bridge_matches_conf_c(
    conf_bridge_path: Path = CONF_BRIDGE,
    conf_c_path: Path = ROOT / 'scripts' / 'kconfig' / 'conf.c',
) -> None:
    bridge_modes = supported_conf_modes_in_order(conf_bridge_path)
    conf_c_modes = supported_conf_modes_from_conf_c_in_order(conf_c_path)

    missing = sorted(set(conf_c_modes) - set(bridge_modes))
    if missing:
        fail_check('MISSING_CONF_C_MODES', missing)

    unexpected = sorted(set(bridge_modes) - set(conf_c_modes))
    if unexpected:
        fail_check('UNEXPECTED_CONF_BRIDGE_MODES', unexpected)

    if bridge_modes != conf_c_modes:
        fail_check(
            'UNSORTED_CONF_BRIDGE_MODE_ORDER',
            [
                'bridge=' + ','.join(bridge_modes),
                'conf_c=' + ','.join(conf_c_modes),
            ],
        )


def ensure_manifest_matches_bridge_modes(cases: object, conf_bridge_path: Path = CONF_BRIDGE) -> None:
    bridge_modes = supported_conf_modes_in_order(conf_bridge_path)
    manifest = cases
    manifest_modes = [case['mode'] for case in manifest['conf_cases']]

    missing = sorted(set(manifest_modes) - set(bridge_modes))
    if missing:
        fail_check('UNSUPPORTED_CONF_CASE_MODES', missing)

    uncovered = sorted(set(bridge_modes) - set(manifest_modes))
    if uncovered:
        fail_check('UNCOVERED_CONF_BRIDGE_MODES', uncovered)

    if manifest_modes != bridge_modes:
        fail_check(
            'UNSORTED_CONF_CASE_ORDER',
            [
                'manifest=' + ','.join(manifest_modes),
                'expected=' + ','.join(bridge_modes),
            ],
        )


def ensure_confdata_case_order_is_sorted(cases: object) -> None:
    manifest = cases
    manifest_names = [case['name'] for case in manifest['confdata_cases']]
    expected_names = sorted(manifest_names)

    if manifest_names != expected_names:
        fail_check(
            'UNSORTED_CONFDATA_CASE_ORDER',
            [
                'manifest=' + ','.join(manifest_names),
                'expected=' + ','.join(expected_names),
            ],
        )


def read_nonempty_string(case: dict[str, object], field_name: str, issues: list[str], *, prefix: str) -> str | None:
    value = case.get(field_name)
    if not isinstance(value, str):
        issues.append(f'{prefix}:{field_name}:expected_nonempty_string')
        return None
    if not value:
        issues.append(f'{prefix}:{field_name}:expected_nonempty_string')
        return None
    return value


def ensure_manifest_shape(cases: object) -> None:
    manifest = cases
    if not isinstance(manifest, dict):
        raise SystemExit('kconfig bridge cases manifest must be a JSON object')

    issues: list[str] = []
    expected_top_level = {'conf_cases', 'confdata_cases'}
    actual_top_level = set(manifest)
    unexpected_top_level = sorted(actual_top_level - expected_top_level)
    if unexpected_top_level:
        issues.extend(f'top_level:unexpected_key:{name}' for name in unexpected_top_level)

    for group_name in ('conf_cases', 'confdata_cases'):
        group = manifest.get(group_name)
        if not isinstance(group, list):
            issues.append(f'{group_name}:expected_list')
        elif not group:
            issues.append(f'{group_name}:empty')

    if issues:
        fail_check('INVALID_KCONFIG_MANIFEST', sorted(issues))


def ensure_manifest_is_deterministic(cases: object, fixture_dir: Path = FIXTURE_DIR) -> None:
    manifest = cases
    issues: list[str] = []
    seen_names: dict[str, str] = {}
    duplicate_names: list[str] = []
    seen_expected_paths: dict[str, str] = {}
    seen_config_inputs: dict[str, str] = {}
    referenced_files: set[str] = {'cases.json'}

    for group_name in ('conf_cases', 'confdata_cases'):
        for case in manifest[group_name]:
            if not isinstance(case, dict):
                issues.append(f'{group_name}:non_object_case')
                continue

            name = read_nonempty_string(case, 'name', issues, prefix=group_name)
            if name is None:
                continue

            previous_group = seen_names.get(name)
            if previous_group is not None:
                duplicate_names.append(f'{name}:{previous_group},{group_name}')
                continue
            seen_names[name] = group_name
            case_prefix = f'{group_name}:{name}'

            expected_path = read_nonempty_string(case, 'expected', issues, prefix=case_prefix)
            if expected_path is not None:
                if not expected_path.endswith('_expected.json'):
                    issues.append(f'{case_prefix}:expected:expected_suffix')
                previous_case = seen_expected_paths.get(expected_path)
                if previous_case is not None:
                    issues.append(f'{case_prefix}:expected:duplicate_with:{previous_case}')
                else:
                    seen_expected_paths[expected_path] = f'{group_name}:{name}'
                referenced_files.add(expected_path)

            if group_name == 'conf_cases':
                allowed_keys = {'name', 'mode', 'kconfig', 'config', 'arch', 'mode_arg', 'allconfig', 'nosilentupdate', 'seed', 'probability', 'expected'}
                mode = read_nonempty_string(case, 'mode', issues, prefix=case_prefix)
                read_nonempty_string(case, 'kconfig', issues, prefix=case_prefix)
                read_nonempty_string(case, 'config', issues, prefix=case_prefix)
                read_nonempty_string(case, 'arch', issues, prefix=case_prefix)

                mode_arg = case.get('mode_arg')
                if mode in {'defconfig', 'savedefconfig'}:
                    if not isinstance(mode_arg, str) or not mode_arg:
                        issues.append(f'{case_prefix}:mode_arg:required_for_argument_mode')
                elif mode_arg is not None:
                    issues.append(f'{case_prefix}:mode_arg:unexpected_for_mode:{mode}')

                allconfig = case.get('allconfig')
                if mode in CONF_ALLCONFIG_MODES:
                    if allconfig is not None and (not isinstance(allconfig, str) or not allconfig):
                        issues.append(f'{case_prefix}:allconfig:expected_nonempty_string')
                elif allconfig is not None:
                    issues.append(f'{case_prefix}:allconfig:unexpected_for_mode:{mode}')

                nosilentupdate = case.get('nosilentupdate')
                if mode == 'syncconfig':
                    if nosilentupdate is not None and (not isinstance(nosilentupdate, str) or not nosilentupdate):
                        issues.append(f'{case_prefix}:nosilentupdate:expected_nonempty_string')
                elif nosilentupdate is not None:
                    issues.append(f'{case_prefix}:nosilentupdate:unexpected_for_mode:{mode}')

                seed = case.get('seed')
                probability = case.get('probability')
                if mode == 'randconfig':
                    if seed is not None and (not isinstance(seed, str) or not seed):
                        issues.append(f'{case_prefix}:seed:expected_nonempty_string')
                    if probability is not None and (not isinstance(probability, str) or not probability):
                        issues.append(f'{case_prefix}:probability:expected_nonempty_string')
                else:
                    if seed is not None:
                        issues.append(f'{case_prefix}:seed:unexpected_for_mode:{mode}')
                    if probability is not None:
                        issues.append(f'{case_prefix}:probability:unexpected_for_mode:{mode}')
            else:
                allowed_keys = {'name', 'input', 'expected'}
                input_path = read_nonempty_string(case, 'input', issues, prefix=case_prefix)
                if input_path is not None:
                    if not input_path.endswith('.config'):
                        issues.append(f'{case_prefix}:input:expected_config_suffix')
                    canonical_input = f'{name}.config'
                    if input_path != canonical_input:
                        issues.append(f'{case_prefix}:input:expected_canonical_name:{canonical_input}')
                    previous_case = seen_config_inputs.get(input_path)
                    if previous_case is not None:
                        issues.append(f'{case_prefix}:input:duplicate_with:{previous_case}')
                    else:
                        seen_config_inputs[input_path] = f'{group_name}:{name}'
                    referenced_files.add(input_path)
                if expected_path is not None:
                    canonical_expected = f'{name}_expected.json'
                    if expected_path != canonical_expected:
                        issues.append(f'{case_prefix}:expected:expected_canonical_name:{canonical_expected}')

            unexpected_case_keys = sorted(set(case) - allowed_keys)
            if unexpected_case_keys:
                issues.extend(f'{case_prefix}:unexpected_key:{field}' for field in unexpected_case_keys)

    if duplicate_names:
        issues.extend(f'duplicate_case_name:{value}' for value in sorted(duplicate_names))

    missing_paths: list[str] = []
    for case in manifest['conf_cases']:
        rel_path = case['expected']
        if not (fixture_dir / rel_path).exists():
            missing_paths.append(f"{case['name']}:expected:{rel_path}")
    for case in manifest['confdata_cases']:
        for field_name in ('input', 'expected'):
            rel_path = case[field_name]
            if not (fixture_dir / rel_path).exists():
                missing_paths.append(f"{case['name']}:{field_name}:{rel_path}")
    if missing_paths:
        issues.extend(f'missing_path:{value}' for value in sorted(missing_paths))

    orphaned_files = sorted(
        path.name
        for path in fixture_dir.iterdir()
        if path.is_file() and path.name not in referenced_files
    )
    if orphaned_files:
        issues.extend(f'orphaned_fixture:{name}' for name in orphaned_files)

    if issues:
        fail_check('INVALID_KCONFIG_MANIFEST', sorted(issues))


def capture_failure(callback, *args) -> list[str]:
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        try:
            callback(*args)
        except SystemExit as exc:
            if exc.code != 1:
                raise AssertionError(f'expected exit code 1, got {exc.code}') from exc
        else:
            raise AssertionError('expected the checker to fail')
    return stream.getvalue().splitlines()


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix='zigux_kconfig_bridge_selftest_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        fixture_dir = tmp_dir / 'fixtures'
        fixture_dir.mkdir()
        conf_bridge_path = tmp_dir / 'conf_bridge.zig'
        conf_c_path = tmp_dir / 'conf.c'
        conf_bridge_path.write_text(
            (
                'pub const Mode = enum {\n'
                '    oldaskconfig,\n'
                '    oldconfig,\n'
                '    syncconfig,\n'
                '    defconfig,\n'
                '\n'
                '    pub fn parse(input_text: []const u8) ?Mode {\n'
                '        _ = input_text;\n'
                '        return null;\n'
                '    }\n'
                '};\n'
            ),
            encoding='utf-8',
            newline='\n',
        )
        conf_c_path.write_text(
            (
                'static const struct option long_opts[] = {\n'
                '    {"oldaskconfig",  no_argument,       &input_mode_opt, oldaskconfig},\n'
                '    {"oldconfig",     no_argument,       &input_mode_opt, oldconfig},\n'
                '    {"syncconfig",    no_argument,       &input_mode_opt, syncconfig},\n'
                '    {"defconfig",     required_argument, &input_mode_opt, defconfig},\n'
                '    {NULL, 0, NULL, 0}\n'
                '};\n'
            ),
            encoding='utf-8',
            newline='\n',
        )

        valid_cases = {
            'conf_cases': [
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
            ],
            'confdata_cases': [
                {
                    'name': 'alpha',
                    'input': 'alpha.config',
                    'expected': 'alpha_expected.json',
                },
                {
                    'name': 'beta',
                    'input': 'beta.config',
                    'expected': 'beta_expected.json',
                },
            ],
        }

        for name in (
            'oldaskconfig_expected.json',
            'oldconfig_expected.json',
            'syncconfig_expected.json',
            'defconfig_expected.json',
            'alpha_expected.json',
            'beta_expected.json',
        ):
            (fixture_dir / name).write_text('{}\n', encoding='utf-8', newline='\n')
        for name in ('alpha.config', 'beta.config'):
            (fixture_dir / name).write_text('# test fixture\n', encoding='utf-8', newline='\n')
        (fixture_dir / 'cases.json').write_text(json.dumps(valid_cases, indent=2) + '\n', encoding='utf-8', newline='\n')

        cases = load_cases(fixture_dir)
        ensure_manifest_shape(cases)
        ensure_conf_bridge_matches_conf_c(conf_bridge_path, conf_c_path)
        ensure_manifest_matches_bridge_modes(cases, conf_bridge_path)
        ensure_confdata_case_order_is_sorted(cases)
        ensure_manifest_is_deterministic(cases, fixture_dir)

        mismatched_conf_c = conf_c_path.with_name('conf_mismatched.c')
        mismatched_conf_c.write_text(
            conf_c_path.read_text(encoding='utf-8').replace(
                '    {"syncconfig",    no_argument,       &input_mode_opt, syncconfig},\n',
                '',
            ),
            encoding='utf-8',
            newline='\n',
        )
        assert capture_failure(ensure_conf_bridge_matches_conf_c, conf_bridge_path, mismatched_conf_c) == [
            'KCONFIG_BRIDGE_DIFF=fail',
            'UNEXPECTED_CONF_BRIDGE_MODES_START',
            'syncconfig',
            'UNEXPECTED_CONF_BRIDGE_MODES_END',
        ]

        unsorted_conf_cases = json.loads(json.dumps(valid_cases))
        unsorted_conf_cases['conf_cases'][0], unsorted_conf_cases['conf_cases'][1] = (
            unsorted_conf_cases['conf_cases'][1],
            unsorted_conf_cases['conf_cases'][0],
        )
        assert capture_failure(ensure_manifest_matches_bridge_modes, unsorted_conf_cases, conf_bridge_path) == [
            'KCONFIG_BRIDGE_DIFF=fail',
            'UNSORTED_CONF_CASE_ORDER_START',
            'manifest=oldconfig,oldaskconfig,syncconfig,defconfig',
            'expected=oldaskconfig,oldconfig,syncconfig,defconfig',
            'UNSORTED_CONF_CASE_ORDER_END',
        ]

        unsorted_confdata_cases = json.loads(json.dumps(valid_cases))
        unsorted_confdata_cases['confdata_cases'][0], unsorted_confdata_cases['confdata_cases'][1] = (
            unsorted_confdata_cases['confdata_cases'][1],
            unsorted_confdata_cases['confdata_cases'][0],
        )
        assert capture_failure(ensure_confdata_case_order_is_sorted, unsorted_confdata_cases) == [
            'KCONFIG_BRIDGE_DIFF=fail',
            'UNSORTED_CONFDATA_CASE_ORDER_START',
            'manifest=beta,alpha',
            'expected=alpha,beta',
            'UNSORTED_CONFDATA_CASE_ORDER_END',
        ]

        (fixture_dir / 'orphaned_expected.json').write_text('{}\n', encoding='utf-8', newline='\n')
        failure_lines = capture_failure(ensure_manifest_is_deterministic, cases, fixture_dir)
        assert failure_lines[0] == 'KCONFIG_BRIDGE_DIFF=fail'
        assert failure_lines[1] == 'INVALID_KCONFIG_MANIFEST_START'
        assert 'orphaned_fixture:orphaned_expected.json' in failure_lines
        assert failure_lines[-1] == 'INVALID_KCONFIG_MANIFEST_END'

        exact_a = tmp_dir / 'exact-a.json'
        exact_b = tmp_dir / 'exact-b.json'
        exact_a.write_text('{"counts":{"set":1,"unset":0},"entries":[]}\n', encoding='utf-8', newline='\n')
        exact_b.write_text('{"entries":[],"counts":{"unset":0,"set":1}}\n', encoding='utf-8', newline='\n')
        compare_json_artifacts(exact_a, exact_b)
        text_result = subprocess.run(
            [sys.executable, str(ARTIFACT_DIFF), '--mode', 'text', str(exact_a), str(exact_b)],
            check=False,
            text=True,
            capture_output=True,
            cwd=str(ROOT),
        )
        if text_result.returncode != 1:
            raise AssertionError('expected compare_text_artifacts to catch byte drift for JSON-equivalent confdata output')
        assert 'ARTIFACT_DIFF=fail' in text_result.stdout
        assert 'MODE=text' in text_result.stdout

    print('KCONFIG_BRIDGE_SELF_TEST=pass')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Check bounded kconfig bridge fixture parity.')
    parser.add_argument('--zig', help='Explicit zig executable path')
    parser.add_argument('--self-test', action='store_true', help='Run built-in manifest and determinism checks.')
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    cases = load_cases()
    ensure_manifest_shape(cases)
    ensure_conf_bridge_matches_conf_c()
    ensure_manifest_matches_bridge_modes(cases)
    ensure_confdata_case_order_is_sorted(cases)
    ensure_manifest_is_deterministic(cases)
    zig = find_zig(args.zig)

    with tempfile.TemporaryDirectory(prefix='zigux_kconfig_bridge_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        conf_exe = tmp_dir / ('conf-bridge.exe' if sys.platform == 'win32' else 'conf-bridge')
        confdata_exe = tmp_dir / ('confdata-bridge.exe' if sys.platform == 'win32' else 'confdata-bridge')
        confdata_rebuild_exe = tmp_dir / ('confdata-bridge-rebuild.exe' if sys.platform == 'win32' else 'confdata-bridge-rebuild')
        compile_tool(zig, CONF_BRIDGE, conf_exe)
        compile_tool(zig, CONFDATA_BRIDGE, confdata_exe)
        compile_tool(zig, CONFDATA_BRIDGE, confdata_rebuild_exe)

        for case in cases['conf_cases']:
            actual = tmp_dir / f"{case['name']}.actual.json"
            repeat = tmp_dir / f"{case['name']}.repeat.json"
            cmd = [
                str(conf_exe),
                case['mode'],
                case['kconfig'],
                case['config'],
                case['arch'],
            ]
            if 'mode_arg' in case:
                cmd.append(case['mode_arg'])
            if 'allconfig' in case:
                cmd.append(case['allconfig'])
            env = os.environ.copy()
            if 'nosilentupdate' in case:
                env['KCONFIG_NOSILENTUPDATE'] = case['nosilentupdate']
            if 'seed' in case:
                env['KCONFIG_SEED'] = case['seed']
            if 'probability' in case:
                env['KCONFIG_PROBABILITY'] = case['probability']
            result = run(cmd, cwd=str(ROOT), capture_output=True, env=env)
            actual.write_text(result.stdout, encoding='utf-8', newline='\n')
            compare_json_artifacts(FIXTURE_DIR / case['expected'], actual)
            repeat_result = run(cmd, cwd=str(ROOT), capture_output=True, env=env)
            repeat.write_text(repeat_result.stdout, encoding='utf-8', newline='\n')
            compare_json_artifacts(actual, repeat)

        default_actual = tmp_dir / 'default-oldaskconfig.actual.json'
        default_repeat = tmp_dir / 'default-oldaskconfig.repeat.json'
        default_cmd = [
            str(conf_exe),
            'Kconfig',
            '.config',
            'x86_64',
        ]
        result = run(default_cmd, cwd=str(ROOT), capture_output=True)
        default_actual.write_text(result.stdout, encoding='utf-8', newline='\n')
        compare_json_artifacts(FIXTURE_DIR / 'oldaskconfig_expected.json', default_actual)
        repeat_result = run(default_cmd, cwd=str(ROOT), capture_output=True)
        default_repeat.write_text(repeat_result.stdout, encoding='utf-8', newline='\n')
        compare_json_artifacts(default_actual, default_repeat)

        for case in cases['confdata_cases']:
            actual = tmp_dir / f"{case['name']}.actual.json"
            repeat = tmp_dir / f"{case['name']}.repeat.json"
            rebuild = tmp_dir / f"{case['name']}.rebuild.json"
            result = run([str(confdata_exe), str(FIXTURE_DIR / case['input'])], cwd=str(ROOT), capture_output=True)
            actual.write_text(result.stdout, encoding='utf-8', newline='\n')
            compare_json_artifacts(FIXTURE_DIR / case['expected'], actual)
            repeat_result = run([str(confdata_exe), str(FIXTURE_DIR / case['input'])], cwd=str(ROOT), capture_output=True)
            repeat.write_text(repeat_result.stdout, encoding='utf-8', newline='\n')
            compare_json_artifacts(actual, repeat)
            compare_text_artifacts(actual, repeat)
            rebuild_result = run([str(confdata_rebuild_exe), str(FIXTURE_DIR / case['input'])], cwd=str(ROOT), capture_output=True)
            rebuild.write_text(rebuild_result.stdout, encoding='utf-8', newline='\n')
            compare_json_artifacts(actual, rebuild)
            compare_text_artifacts(actual, rebuild)

    print('KCONFIG_BRIDGE_DIFF=pass')
    print('KCONFIG_BRIDGE_DETERMINISM=pass')
    print(f'FIXTURE_DIR={FIXTURE_DIR}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
