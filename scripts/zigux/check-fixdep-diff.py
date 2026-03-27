#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIFF = ROOT / 'scripts' / 'zigux' / 'artifact_diff.py'
C_FIXDEP = ROOT / 'scripts' / 'basic' / 'fixdep.c'
ZIG_FIXDEP = ROOT / 'scripts' / 'zigux' / 'fixdep.zig'
FIXTURE_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep'
DEPFILE = FIXTURE_DIR / 'sample.d'
EXPECTED = FIXTURE_DIR / 'sample_expected.txt'
TARGET = 'sample.o'
CMDLINE = 'clang -Iinclude -DZIGUX_SAMPLE -c zigux/tests/fixtures/fixdep/sample.c -o sample.o'


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def find_compiler(explicit: str | None) -> str:
    if explicit:
        return explicit
    for candidate in ('gcc', 'cc', 'clang'):
        path = shutil.which(candidate)
        if path:
            return path
    raise FileNotFoundError('no C compiler found on PATH')


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    env = os.environ.get('ZIG')
    if env:
        return env
    path = shutil.which('zig')
    if path:
        return path
    fallback = ROOT.parent / 'toolchains' / 'zig-master' / 'current' / 'zig.exe'
    if fallback.exists():
        return str(fallback)
    raise FileNotFoundError('no zig executable found; set --zig or ZIG')


def windows_to_wsl(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(':').lower()
    tail = resolved.as_posix().split(':', 1)[1]
    return f'/mnt/{drive}{tail}'


def compile_run_c_wsl(tmp_dir: Path, exe: Path, actual: Path, compiler: str) -> None:
    script_path = tmp_dir / 'run_fixdep_c.sh'
    lines = [
        '#!/usr/bin/env bash',
        'set -euo pipefail',
        ' '.join([
            shlex.quote(compiler),
            '-std=gnu11',
            '-Wall',
            '-Wextra',
            '-I', shlex.quote(windows_to_wsl(ROOT / 'scripts' / 'include')),
            '-o', shlex.quote(windows_to_wsl(exe)),
            shlex.quote(windows_to_wsl(C_FIXDEP)),
        ]),
        ' '.join([
            shlex.quote(windows_to_wsl(exe)),
            shlex.quote(windows_to_wsl(DEPFILE)),
            shlex.quote(TARGET),
            shlex.quote(CMDLINE),
            '>',
            shlex.quote(windows_to_wsl(actual)),
        ]),
    ]
    script_path.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    run(['wsl', 'bash', windows_to_wsl(script_path)], cwd=str(ROOT))


def compile_run_c(tmp_dir: Path, actual: Path, compiler: str) -> None:
    exe = tmp_dir / ('fixdep-c.exe' if os.name == 'nt' else 'fixdep-c')
    if os.name == 'nt' and shutil.which('wsl'):
        compile_run_c_wsl(tmp_dir, exe, actual, compiler)
        return

    compile_cmd = [
        compiler,
        '-std=gnu11',
        '-Wall',
        '-Wextra',
        '-I', str(ROOT / 'scripts' / 'include'),
        '-o', str(exe),
        str(C_FIXDEP),
    ]
    run(compile_cmd, cwd=str(ROOT))
    result = run([str(exe), str(DEPFILE), TARGET, CMDLINE], cwd=str(ROOT), capture_output=True)
    actual.write_text(result.stdout, encoding='utf-8')


def run_zig(zig: str, tmp_dir: Path, actual: Path) -> None:
    exe = tmp_dir / ('fixdep-zig.exe' if os.name == 'nt' else 'fixdep-zig')
    build_cmd = [zig, 'build-exe', str(ZIG_FIXDEP), '-femit-bin=' + str(exe)]
    run(build_cmd, cwd=str(ROOT))
    result = run([str(exe), str(DEPFILE), TARGET, CMDLINE], cwd=str(ROOT), capture_output=True)
    actual.write_text(result.stdout, encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Check bounded fixdep C/Zig artifact parity.')
    parser.add_argument('--refresh', action='store_true', help='Refresh the committed expected output from current C fixdep.')
    parser.add_argument('--cc', help='Explicit C compiler path to use.')
    parser.add_argument('--zig', help='Explicit zig executable path to use.')
    args = parser.parse_args()

    compiler = args.cc or os.environ.get('CC') or ('gcc' if os.name == 'nt' and shutil.which('wsl') else find_compiler(None))
    zig = find_zig(args.zig)

    with tempfile.TemporaryDirectory(prefix='zigux_fixdep_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        c_actual = tmp_dir / 'fixdep.c.actual.txt'
        zig_actual = tmp_dir / 'fixdep.zig.actual.txt'

        compile_run_c(tmp_dir, c_actual, compiler)
        run_zig(zig, tmp_dir, zig_actual)

        if args.refresh:
            EXPECTED.write_text(c_actual.read_text(encoding='utf-8'), encoding='utf-8')
            print('FIXDEP_REFRESH=pass')
            print(f'FIXTURE={EXPECTED}')
            return 0

        diff_base = [sys.executable, str(ARTIFACT_DIFF), '--mode', 'text']
        run(diff_base + [str(EXPECTED), str(c_actual)], cwd=str(ROOT))
        run(diff_base + [str(EXPECTED), str(zig_actual)], cwd=str(ROOT))
        run(diff_base + [str(c_actual), str(zig_actual)], cwd=str(ROOT))
        print('FIXDEP_DIFF=pass')
        print(f'FIXTURE={EXPECTED}')
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
