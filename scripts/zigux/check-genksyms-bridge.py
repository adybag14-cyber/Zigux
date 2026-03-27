#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIFF = ROOT / 'scripts' / 'zigux' / 'artifact_diff.py'
C_HARNESS = ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'genksyms_bridge_c_harness.c'
ZIG_TOOL = ROOT / 'scripts' / 'zigux' / 'genksyms.zig'
FIXTURE_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge'


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def find_compiler(explicit: str | None) -> str:
    if explicit:
        return explicit
    compiler = shutil.which('cc') or shutil.which('gcc') or shutil.which('clang')
    if compiler:
        return compiler
    raise SystemExit('C compiler not found; pass --cc or install cc/gcc/clang')


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    env = os.environ.get('ZIG')
    if env:
        return env
    zig = shutil.which('zig')
    if zig:
        return zig
    fallback = ROOT.parent / 'toolchains' / 'zig-master' / 'current' / 'zig.exe'
    if fallback.exists():
        return str(fallback)
    raise SystemExit('zig not found; pass --zig or add zig to PATH')


def windows_to_wsl(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(':').lower()
    tail = resolved.as_posix().split(':', 1)[1]
    return f'/mnt/{drive}{tail}'


def compile_run_c_wsl(tmp_dir: Path, exe: Path, actual: Path, compiler: str, argv: list[str]) -> None:
    script_path = tmp_dir / 'run_genksyms_bridge_c.sh'
    command = [
        shlex.quote(compiler),
        '-std=c11',
        '-Wall',
        '-Wextra',
        '-o',
        shlex.quote(windows_to_wsl(exe)),
        shlex.quote(windows_to_wsl(C_HARNESS)),
    ]
    run_line = [shlex.quote(windows_to_wsl(exe)), *[shlex.quote(arg) for arg in argv], '>', shlex.quote(windows_to_wsl(actual))]
    lines = [
        '#!/usr/bin/env bash',
        'set -euo pipefail',
        ' '.join(command),
        ' '.join(run_line),
    ]
    script_path.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    run(['wsl', 'bash', windows_to_wsl(script_path)], cwd=str(ROOT))


def compile_run_c(tmp_dir: Path, actual: Path, compiler: str, argv: list[str]) -> None:
    exe = tmp_dir / ('genksyms-bridge-c.exe' if os.name == 'nt' else 'genksyms-bridge-c')
    if os.name == 'nt' and shutil.which('wsl'):
        compile_run_c_wsl(tmp_dir, exe, actual, compiler, argv)
        return
    run([compiler, '-std=c11', '-Wall', '-Wextra', '-o', str(exe), str(C_HARNESS)], cwd=str(ROOT))
    result = run([str(exe), *argv], cwd=str(ROOT), capture_output=True)
    actual.write_text(result.stdout, encoding='utf-8', newline='\n')


def run_zig(zig: str, tmp_dir: Path, actual: Path, argv: list[str]) -> None:
    exe = tmp_dir / ('genksyms-bridge-zig.exe' if os.name == 'nt' else 'genksyms-bridge-zig')
    run([zig, 'build-exe', str(ZIG_TOOL), '-femit-bin=' + str(exe)], cwd=str(ROOT))
    result = run([str(exe), *argv], cwd=str(ROOT), capture_output=True)
    actual.write_text(result.stdout, encoding='utf-8', newline='\n')


def main() -> int:
    parser = argparse.ArgumentParser(description='Check bounded genksyms bridge parity.')
    parser.add_argument('--cc', help='C compiler to use')
    parser.add_argument('--zig', help='Path to Zig executable')
    parser.add_argument('--refresh', action='store_true', help='Refresh the committed expected fixtures from the C harness')
    args = parser.parse_args()

    compiler = args.cc or os.environ.get('CC') or ('gcc' if os.name == 'nt' and shutil.which('wsl') else find_compiler(None))
    zig = find_zig(args.zig)
    cases = json.loads((FIXTURE_DIR / 'cases.json').read_text(encoding='utf-8'))

    with tempfile.TemporaryDirectory(prefix='zigux_genksyms_bridge_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        for case in cases['cases']:
            c_actual = tmp_dir / f"{case['name']}.c.actual.json"
            zig_actual = tmp_dir / f"{case['name']}.zig.actual.json"
            compile_run_c(tmp_dir, c_actual, compiler, case['argv'])
            run_zig(zig, tmp_dir, zig_actual, case['argv'])

            expected = FIXTURE_DIR / case['expected']
            if args.refresh:
                expected.write_text(c_actual.read_text(encoding='utf-8'), encoding='utf-8', newline='\n')
                continue

            diff_base = [sys.executable, str(ARTIFACT_DIFF), '--mode', 'json']
            run(diff_base + [str(expected), str(c_actual)], cwd=str(ROOT))
            run(diff_base + [str(expected), str(zig_actual)], cwd=str(ROOT))
            run(diff_base + [str(c_actual), str(zig_actual)], cwd=str(ROOT))

    if args.refresh:
        print('GENKSYMS_BRIDGE_REFRESH=pass')
    else:
        print('GENKSYMS_BRIDGE_DIFF=pass')
    print(f'FIXTURE_DIR={FIXTURE_DIR}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
