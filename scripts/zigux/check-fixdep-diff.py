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
C_FIXDEP = ROOT / 'scripts' / 'basic' / 'fixdep.c'
ZIG_FIXDEP = ROOT / 'scripts' / 'zigux' / 'fixdep.zig'
FIXTURE_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'fixdep'
CASES = json.loads((FIXTURE_DIR / 'cases.json').read_text(encoding='utf-8'))


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def run_capture(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=False, text=True, capture_output=True, **kwargs)


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


def compile_run_c_wsl(tmp_dir: Path, exe: Path, compiler: str, depfile: Path, target: str, cmdline: str) -> subprocess.CompletedProcess[str]:
    script_path = tmp_dir / 'run_fixdep_c.sh'
    stdout_path = tmp_dir / 'fixdep.c.actual.txt'
    stderr_path = tmp_dir / 'fixdep.c.actual.stderr.txt'
    rc_path = tmp_dir / 'fixdep.c.actual.rc'
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
            shlex.quote(windows_to_wsl(depfile)),
            shlex.quote(target),
            shlex.quote(cmdline),
        ]),
        'rc=$?',
        f"printf '%s' \"$rc\" > {shlex.quote(windows_to_wsl(rc_path))}",
    ]
    lines[3] += f" > {shlex.quote(windows_to_wsl(stdout_path))} 2> {shlex.quote(windows_to_wsl(stderr_path))} || true"
    script_path.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    run(['wsl', 'bash', windows_to_wsl(script_path)], cwd=str(ROOT))
    return subprocess.CompletedProcess(
        args=[str(exe), str(depfile), target, cmdline],
        returncode=int(rc_path.read_text(encoding='utf-8') or '0'),
        stdout=stdout_path.read_text(encoding='utf-8'),
        stderr=stderr_path.read_text(encoding='utf-8'),
    )


def compile_run_c(tmp_dir: Path, compiler: str, depfile: Path, target: str, cmdline: str) -> subprocess.CompletedProcess[str]:
    exe = tmp_dir / ('fixdep-c.exe' if os.name == 'nt' else 'fixdep-c')
    if os.name == 'nt' and shutil.which('wsl'):
        return compile_run_c_wsl(tmp_dir, exe, compiler, depfile, target, cmdline)

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
    return run_capture([str(exe), str(depfile), target, cmdline], cwd=str(ROOT))


def run_zig(zig: str, tmp_dir: Path, depfile: Path, target: str, cmdline: str) -> subprocess.CompletedProcess[str]:
    exe = tmp_dir / ('fixdep-zig.exe' if os.name == 'nt' else 'fixdep-zig')
    build_cmd = [zig, 'build-exe', str(ZIG_FIXDEP), '-femit-bin=' + str(exe)]
    run(build_cmd, cwd=str(ROOT))
    return run_capture([str(exe), str(depfile), target, cmdline], cwd=str(ROOT))


def compare_returncode(label: str, expected: int, actual: int) -> None:
    if expected != actual:
        raise RuntimeError(f'{label} return code mismatch: expected {expected}, got {actual}')


def main() -> int:
    parser = argparse.ArgumentParser(description='Check bounded fixdep C/Zig artifact parity.')
    parser.add_argument('--refresh', action='store_true', help='Refresh the committed expected output from current C fixdep.')
    parser.add_argument('--cc', help='Explicit C compiler path to use.')
    parser.add_argument('--zig', help='Explicit zig executable path to use.')
    args = parser.parse_args()

    compiler = args.cc or os.environ.get('CC') or ('gcc' if os.name == 'nt' and shutil.which('wsl') else find_compiler(None))
    zig = find_zig(args.zig)

    for case in CASES:
        depfile = FIXTURE_DIR / case['depfile']
        expected_stdout = FIXTURE_DIR / case.get('expected_stdout', case['expected'])
        expected_stderr_name = case.get('expected_stderr')
        expected_stderr = FIXTURE_DIR / expected_stderr_name if expected_stderr_name else None
        expected_exit_code = int(case.get('expected_exit_code', 0))
        target = case['target']
        cmdline = case['cmdline']

        with tempfile.TemporaryDirectory(prefix=f"zigux_fixdep_{case['name']}_") as tmp_dir_str:
            tmp_dir = Path(tmp_dir_str)
            c_actual = tmp_dir / 'fixdep.c.actual.txt'
            c_actual_stderr = tmp_dir / 'fixdep.c.actual.stderr.txt'
            zig_actual = tmp_dir / 'fixdep.zig.actual.txt'
            zig_actual_stderr = tmp_dir / 'fixdep.zig.actual.stderr.txt'

            c_result = compile_run_c(tmp_dir, compiler, depfile, target, cmdline)
            zig_result = run_zig(zig, tmp_dir, depfile, target, cmdline)
            c_actual.write_text(c_result.stdout, encoding='utf-8')
            c_actual_stderr.write_text(c_result.stderr, encoding='utf-8')
            zig_actual.write_text(zig_result.stdout, encoding='utf-8')
            zig_actual_stderr.write_text(zig_result.stderr, encoding='utf-8')

            if args.refresh:
                expected_stdout.write_text(c_result.stdout, encoding='utf-8')
                if expected_stderr is not None:
                    expected_stderr.write_text(c_result.stderr, encoding='utf-8')
                continue

            diff_base = [sys.executable, str(ARTIFACT_DIFF), '--mode', 'text']
            compare_returncode(f"{case['name']} C", expected_exit_code, c_result.returncode)
            compare_returncode(f"{case['name']} Zig", expected_exit_code, zig_result.returncode)
            compare_returncode(f"{case['name']} C-vs-Zig", c_result.returncode, zig_result.returncode)
            run(diff_base + [str(expected_stdout), str(c_actual)], cwd=str(ROOT))
            run(diff_base + [str(expected_stdout), str(zig_actual)], cwd=str(ROOT))
            run(diff_base + [str(c_actual), str(zig_actual)], cwd=str(ROOT))
            if expected_stderr is not None:
                run(diff_base + [str(expected_stderr), str(c_actual_stderr)], cwd=str(ROOT))
                run(diff_base + [str(expected_stderr), str(zig_actual_stderr)], cwd=str(ROOT))
                run(diff_base + [str(c_actual_stderr), str(zig_actual_stderr)], cwd=str(ROOT))

    if args.refresh:
        print('FIXDEP_REFRESH=pass')
        print(f'FIXTURE_DIR={FIXTURE_DIR}')
    else:
        print('FIXDEP_DIFF=pass')
        print(f'FIXTURE_DIR={FIXTURE_DIR}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
