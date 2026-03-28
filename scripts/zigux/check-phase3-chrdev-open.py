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
FIXTURE_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase3_chrdev_open'
EXPECTED = FIXTURE_DIR / 'expected.json'
HARNESS = FIXTURE_DIR / 'phase3_chrdev_open_c_harness.c'


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def find_compiler(explicit: str | None) -> str:
    if explicit:
        return explicit
    for candidate in ('gcc', 'cc', 'clang'):
        path = shutil.which(candidate)
        if path:
            return path
    raise SystemExit('no C compiler found; pass --cc or add gcc/cc/clang to PATH')


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    path = shutil.which('zig')
    if path:
        return path
    fallback = ROOT.parent / 'toolchains' / 'zig-master' / 'current' / 'zig.exe'
    if fallback.exists():
        return str(fallback)
    raise SystemExit('zig not found; pass --zig or add zig to PATH')


def windows_to_wsl(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(':').lower()
    tail = resolved.as_posix().split(':', 1)[1]
    return f'/mnt/{drive}{tail}'


def compile_and_run_c(tmp_dir: Path, compiler: str, actual: Path) -> None:
    exe = tmp_dir / ('phase3_chrdev_open_c_harness.exe' if os.name == 'nt' else 'phase3_chrdev_open_c_harness')
    flags = ['-I', str(ROOT / 'include')]

    if os.name == 'nt' and shutil.which('wsl'):
        script_path = tmp_dir / 'run_phase3_chrdev_open_c.sh'
        quoted = [shlex.quote(compiler), '-std=gnu11', '-Wall', '-Wextra', '-o', shlex.quote(windows_to_wsl(exe))]
        index = 0
        while index < len(flags):
            item = flags[index]
            quoted.append(shlex.quote(item))
            if item == '-I':
                index += 1
                quoted.append(shlex.quote(windows_to_wsl(Path(flags[index]))))
            index += 1
        quoted.append(shlex.quote(windows_to_wsl(HARNESS)))
        script = '\n'.join([
            '#!/usr/bin/env bash',
            'set -euo pipefail',
            ' '.join(quoted),
            f'{shlex.quote(windows_to_wsl(exe))} > {shlex.quote(windows_to_wsl(actual))}',
            '',
        ])
        script_path.write_text(script, encoding='utf-8', newline='\n')
        run(['wsl', 'bash', windows_to_wsl(script_path)], cwd=str(ROOT))
        return

    compile_cmd = [compiler, '-std=gnu11', '-Wall', '-Wextra', '-o', str(exe)]
    compile_cmd.extend(flags)
    compile_cmd.append(str(HARNESS))
    run(compile_cmd, cwd=str(ROOT))
    result = run([str(exe)], cwd=str(ROOT), capture_output=True)
    actual.write_text(result.stdout, encoding='utf-8', newline='\n')


def compile_and_run_zig(zig: str, actual: Path) -> None:
    env = os.environ.copy()
    env['ZIG'] = zig
    result = run([zig, 'build', 'phase3-chrdev-open-dump', '--build-file', str(ROOT / 'zigux' / 'tests' / 'build.zig')], cwd=str(ROOT), capture_output=True, env=env)
    actual.write_text(result.stdout, encoding='utf-8', newline='\n')


def main() -> int:
    parser = argparse.ArgumentParser(description='Check bounded Phase 3 chrdev open interop parity.')
    parser.add_argument('--cc', help='Explicit C compiler path')
    parser.add_argument('--zig', help='Explicit zig executable path')
    args = parser.parse_args()

    if args.cc:
        compiler = args.cc
    elif os.name == 'nt' and shutil.which('wsl'):
        compiler = 'gcc'
    else:
        compiler = find_compiler(None)
    zig = find_zig(args.zig)

    with tempfile.TemporaryDirectory(prefix='zigux_phase3_chrdev_open_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        c_actual = tmp_dir / 'phase3_chrdev_open_c.actual.json'
        zig_actual = tmp_dir / 'phase3_chrdev_open_zig.actual.json'

        compile_and_run_c(tmp_dir, compiler, c_actual)
        compile_and_run_zig(zig, zig_actual)

        run([sys.executable, str(ARTIFACT_DIFF), '--mode', 'json', str(EXPECTED), str(c_actual)], cwd=str(ROOT))
        run([sys.executable, str(ARTIFACT_DIFF), '--mode', 'json', str(EXPECTED), str(zig_actual)], cwd=str(ROOT))

    print('PHASE3_CHRDEV_OPEN_DIFF=pass')
    print(f'FIXTURE={EXPECTED}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
