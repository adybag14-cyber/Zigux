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


def supported_conf_modes() -> set[str]:
    source = CONF_BRIDGE.read_text(encoding='utf-8')
    match = re.search(r'pub const Mode = enum \{(.*?)\n\s*pub fn parse', source, re.S)
    if not match:
        raise SystemExit('failed to parse conf bridge Mode enum')

    modes: set[str] = set()
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith('pub ') or line.startswith('//'):
            continue
        if line.endswith(','):
            candidate = line[:-1].strip()
            if candidate and candidate.isidentifier():
                modes.add(candidate)
    if not modes:
        raise SystemExit('failed to discover conf bridge modes')
    return modes


def ensure_manifest_matches_bridge_modes() -> None:
    manifest_modes = {case['mode'] for case in CASES['conf_cases']}
    bridge_modes = supported_conf_modes()
    unsupported = sorted(manifest_modes - bridge_modes)
    if unsupported:
        fail_check('UNSUPPORTED_CONF_CASE_MODES', unsupported)

    missing = sorted(bridge_modes - manifest_modes)
    if missing:
        fail_check('MISSING_CONF_CASE_MODES', missing)


def ensure_manifest_is_deterministic() -> None:
    seen_names: dict[str, str] = {}
    duplicate_names: list[str] = []
    for group_name in ('conf_cases', 'confdata_cases'):
        for case in CASES[group_name]:
            name = case['name']
            previous_group = seen_names.get(name)
            if previous_group is not None:
                duplicate_names.append(f'{name}:{previous_group},{group_name}')
                continue
            seen_names[name] = group_name
    if duplicate_names:
        fail_check('DUPLICATE_KCONFIG_CASE_NAMES', sorted(duplicate_names))

    missing_paths: list[str] = []
    for case in CASES['conf_cases']:
        for field_name in ('expected',):
            rel_path = case[field_name]
            if not (FIXTURE_DIR / rel_path).exists():
                missing_paths.append(f"{case['name']}:{field_name}:{rel_path}")
    for case in CASES['confdata_cases']:
        for field_name in ('input', 'expected'):
            rel_path = case[field_name]
            if not (FIXTURE_DIR / rel_path).exists():
                missing_paths.append(f"{case['name']}:{field_name}:{rel_path}")
    if missing_paths:
        fail_check('MISSING_CONFDATA_CASE_PATHS', sorted(missing_paths))


def main() -> int:
    parser = argparse.ArgumentParser(description='Check bounded kconfig bridge fixture parity.')
    parser.add_argument('--zig', help='Explicit zig executable path')
    args = parser.parse_args()

    ensure_manifest_matches_bridge_modes()
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

        for case in CASES['confdata_cases']:
            actual = tmp_dir / f"{case['name']}.actual.json"
            result = run([str(confdata_exe), str(FIXTURE_DIR / case['input'])], cwd=str(ROOT), capture_output=True)
            actual.write_text(result.stdout, encoding='utf-8', newline='\n')
            run([sys.executable, str(ARTIFACT_DIFF), '--mode', 'json', str(FIXTURE_DIR / case['expected']), str(actual)], cwd=str(ROOT))

    print('KCONFIG_BRIDGE_DIFF=pass')
    print(f'FIXTURE_DIR={FIXTURE_DIR}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
