#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import argparse
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


def main() -> int:
    parser = argparse.ArgumentParser(description='Check bounded kconfig bridge fixture parity.')
    parser.add_argument('--zig', help='Explicit zig executable path')
    args = parser.parse_args()

    zig = find_zig(args.zig)

    with tempfile.TemporaryDirectory(prefix='zigux_kconfig_bridge_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        conf_exe = tmp_dir / ('conf-bridge.exe' if sys.platform == 'win32' else 'conf-bridge')
        confdata_exe = tmp_dir / ('confdata-bridge.exe' if sys.platform == 'win32' else 'confdata-bridge')
        compile_tool(zig, CONF_BRIDGE, conf_exe)
        compile_tool(zig, CONFDATA_BRIDGE, confdata_exe)

        for case in CASES['conf_cases']:
            actual = tmp_dir / f"{case['name']}.actual.json"
            result = run([
                str(conf_exe),
                case['mode'],
                case['kconfig'],
                case['config'],
                case['arch'],
            ], cwd=str(ROOT), capture_output=True)
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
