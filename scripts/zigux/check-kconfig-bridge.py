#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import argparse
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
CASES = json.loads((FIXTURE_DIR / 'cases.json').read_text(encoding='utf-8'))


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


def supported_conf_modes_in_order() -> list[str]:
    source = CONF_BRIDGE.read_text(encoding='utf-8')
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


def ensure_manifest_matches_bridge_modes() -> None:
    bridge_modes = supported_conf_modes_in_order()
    manifest_modes = [case['mode'] for case in CASES['conf_cases']]

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


def ensure_confdata_case_order_is_sorted() -> None:
    manifest_names = [case['name'] for case in CASES['confdata_cases']]
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


def ensure_manifest_shape() -> None:
    if not isinstance(CASES, dict):
        raise SystemExit('kconfig bridge cases manifest must be a JSON object')

    issues: list[str] = []
    expected_top_level = {'conf_cases', 'confdata_cases'}
    actual_top_level = set(CASES)
    unexpected_top_level = sorted(actual_top_level - expected_top_level)
    if unexpected_top_level:
        issues.extend(f'top_level:unexpected_key:{name}' for name in unexpected_top_level)

    for group_name in ('conf_cases', 'confdata_cases'):
        group = CASES.get(group_name)
        if not isinstance(group, list):
            issues.append(f'{group_name}:expected_list')
        elif not group:
            issues.append(f'{group_name}:empty')

    if issues:
        fail_check('INVALID_KCONFIG_MANIFEST', sorted(issues))


def ensure_manifest_is_deterministic() -> None:
    issues: list[str] = []
    seen_names: dict[str, str] = {}
    duplicate_names: list[str] = []
    seen_expected_paths: dict[str, str] = {}
    seen_config_inputs: dict[str, str] = {}
    referenced_files: set[str] = {'cases.json'}

    for group_name in ('conf_cases', 'confdata_cases'):
        for case in CASES[group_name]:
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
                allowed_keys = {'name', 'mode', 'kconfig', 'config', 'arch', 'mode_arg', 'expected'}
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
    for case in CASES['conf_cases']:
        rel_path = case['expected']
        if not (FIXTURE_DIR / rel_path).exists():
            missing_paths.append(f"{case['name']}:expected:{rel_path}")
    for case in CASES['confdata_cases']:
        for field_name in ('input', 'expected'):
            rel_path = case[field_name]
            if not (FIXTURE_DIR / rel_path).exists():
                missing_paths.append(f"{case['name']}:{field_name}:{rel_path}")
    if missing_paths:
        issues.extend(f'missing_path:{value}' for value in sorted(missing_paths))

    orphaned_files = sorted(
        path.name
        for path in FIXTURE_DIR.iterdir()
        if path.is_file() and path.name not in referenced_files
    )
    if orphaned_files:
        issues.extend(f'orphaned_fixture:{name}' for name in orphaned_files)

    if issues:
        fail_check('INVALID_KCONFIG_MANIFEST', sorted(issues))


def main() -> int:
    parser = argparse.ArgumentParser(description='Check bounded kconfig bridge fixture parity.')
    parser.add_argument('--zig', help='Explicit zig executable path')
    args = parser.parse_args()

    ensure_manifest_shape()
    ensure_manifest_matches_bridge_modes()
    ensure_confdata_case_order_is_sorted()
    ensure_manifest_is_deterministic()
    zig = find_zig(args.zig)

    with tempfile.TemporaryDirectory(prefix='zigux_kconfig_bridge_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        conf_exe = tmp_dir / ('conf-bridge.exe' if sys.platform == 'win32' else 'conf-bridge')
        confdata_exe = tmp_dir / ('confdata-bridge.exe' if sys.platform == 'win32' else 'confdata-bridge')
        compile_tool(zig, CONF_BRIDGE, conf_exe)
        compile_tool(zig, CONFDATA_BRIDGE, confdata_exe)

        for case in CASES['conf_cases']:
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
            result = run(cmd, cwd=str(ROOT), capture_output=True)
            actual.write_text(result.stdout, encoding='utf-8', newline='\n')
            run([sys.executable, str(ARTIFACT_DIFF), '--mode', 'json', str(FIXTURE_DIR / case['expected']), str(actual)], cwd=str(ROOT))
            repeat_result = run(cmd, cwd=str(ROOT), capture_output=True)
            repeat.write_text(repeat_result.stdout, encoding='utf-8', newline='\n')
            run([sys.executable, str(ARTIFACT_DIFF), '--mode', 'json', str(actual), str(repeat)], cwd=str(ROOT))

        for case in CASES['confdata_cases']:
            actual = tmp_dir / f"{case['name']}.actual.json"
            repeat = tmp_dir / f"{case['name']}.repeat.json"
            result = run([str(confdata_exe), str(FIXTURE_DIR / case['input'])], cwd=str(ROOT), capture_output=True)
            actual.write_text(result.stdout, encoding='utf-8', newline='\n')
            run([sys.executable, str(ARTIFACT_DIFF), '--mode', 'json', str(FIXTURE_DIR / case['expected']), str(actual)], cwd=str(ROOT))
            repeat_result = run([str(confdata_exe), str(FIXTURE_DIR / case['input'])], cwd=str(ROOT), capture_output=True)
            repeat.write_text(repeat_result.stdout, encoding='utf-8', newline='\n')
            run([sys.executable, str(ARTIFACT_DIFF), '--mode', 'json', str(actual), str(repeat)], cwd=str(ROOT))

    print('KCONFIG_BRIDGE_DIFF=pass')
    print('KCONFIG_BRIDGE_DETERMINISM=pass')
    print(f'FIXTURE_DIR={FIXTURE_DIR}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
