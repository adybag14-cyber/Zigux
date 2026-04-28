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


def run_redirected(
    cmd: list[str],
    *,
    cwd: str,
    stdout_mode: str | None = None,
) -> subprocess.CompletedProcess[str]:
    if stdout_mode is None:
        return run_capture(cmd, cwd=cwd)
    if stdout_mode != 'dev_full':
        raise ValueError(f'unsupported stdout mode: {stdout_mode}')

    with open('/dev/full', 'w', encoding='utf-8') as stdout_handle:
        result = subprocess.run(
            cmd,
            check=False,
            text=True,
            stdout=stdout_handle,
            stderr=subprocess.PIPE,
            cwd=cwd,
        )
    return subprocess.CompletedProcess(
        args=result.args,
        returncode=result.returncode,
        stdout='',
        stderr=result.stderr or '',
    )


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


def compile_run_c_wsl(
    tmp_dir: Path,
    exe: Path,
    compiler: str,
    depfile: Path,
    target: str,
    cmdline: str,
    stdout_mode: str | None = None,
) -> subprocess.CompletedProcess[str]:
    script_path = tmp_dir / 'run_fixdep_c.sh'
    stdout_path = tmp_dir / 'fixdep.c.actual.txt'
    stderr_path = tmp_dir / 'fixdep.c.actual.stderr.txt'
    rc_path = tmp_dir / 'fixdep.c.actual.rc'
    stdout_redirect = windows_to_wsl(stdout_path) if stdout_mode is None else '/dev/full'
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
    lines[3] += f" > {shlex.quote(stdout_redirect)} 2> {shlex.quote(windows_to_wsl(stderr_path))} || true"
    script_path.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    run(['wsl', 'bash', windows_to_wsl(script_path)], cwd=str(ROOT))
    if stdout_mode is None:
        stdout_text = stdout_path.read_text(encoding='utf-8')
    else:
        stdout_text = ''
    return subprocess.CompletedProcess(
        args=[str(exe), str(depfile), target, cmdline],
        returncode=int(rc_path.read_text(encoding='utf-8') or '0'),
        stdout=stdout_text,
        stderr=stderr_path.read_text(encoding='utf-8'),
    )


def compile_run_c(
    tmp_dir: Path,
    compiler: str,
    depfile: Path,
    target: str,
    cmdline: str,
    stdout_mode: str | None = None,
) -> subprocess.CompletedProcess[str]:
    exe = tmp_dir / ('fixdep-c.exe' if os.name == 'nt' else 'fixdep-c')
    if os.name == 'nt' and shutil.which('wsl'):
        return compile_run_c_wsl(tmp_dir, exe, compiler, depfile, target, cmdline, stdout_mode)

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
    return run_redirected([str(exe), str(depfile), target, cmdline], cwd=str(ROOT), stdout_mode=stdout_mode)


def run_zig(
    zig: str,
    tmp_dir: Path,
    depfile: Path,
    target: str,
    cmdline: str,
    stdout_mode: str | None = None,
) -> subprocess.CompletedProcess[str]:
    exe = tmp_dir / ('fixdep-zig.exe' if os.name == 'nt' else 'fixdep-zig')
    build_cmd = [zig, 'build-exe', str(ZIG_FIXDEP), '-femit-bin=' + str(exe)]
    run(build_cmd, cwd=str(ROOT))
    return run_redirected([str(exe), str(depfile), target, cmdline], cwd=str(ROOT), stdout_mode=stdout_mode)


def compare_returncode(label: str, expected: int, actual: int) -> None:
    if expected != actual:
        raise RuntimeError(f'{label} return code mismatch: expected {expected}, got {actual}')


def write_result(stdout_path: Path, stderr_path: Path, result: subprocess.CompletedProcess[str]) -> None:
    stdout_path.write_text(result.stdout, encoding='utf-8')
    stderr_path.write_text(result.stderr, encoding='utf-8')


def diff_text(expected: Path, actual: Path) -> None:
    run([sys.executable, str(ARTIFACT_DIFF), '--mode', 'text', str(expected), str(actual)], cwd=str(ROOT))


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
        stdout_mode = case.get('stdout_mode')
        target = case['target']
        cmdline = case['cmdline']

        with tempfile.TemporaryDirectory(prefix=f"zigux_fixdep_{case['name']}_") as tmp_dir_str:
            tmp_dir = Path(tmp_dir_str)
            c_actual = tmp_dir / 'fixdep.c.actual.txt'
            c_actual_stderr = tmp_dir / 'fixdep.c.actual.stderr.txt'
            c_repeat = tmp_dir / 'fixdep.c.repeat.txt'
            c_repeat_stderr = tmp_dir / 'fixdep.c.repeat.stderr.txt'
            zig_actual = tmp_dir / 'fixdep.zig.actual.txt'
            zig_actual_stderr = tmp_dir / 'fixdep.zig.actual.stderr.txt'
            zig_repeat = tmp_dir / 'fixdep.zig.repeat.txt'
            zig_repeat_stderr = tmp_dir / 'fixdep.zig.repeat.stderr.txt'
            implicit_expected_stderr = tmp_dir / 'fixdep.expected.stderr.txt'
            implicit_expected_stderr.write_text('', encoding='utf-8')
            expected_stderr_path = expected_stderr or implicit_expected_stderr

            c_result = compile_run_c(tmp_dir, compiler, depfile, target, cmdline, stdout_mode)
            zig_result = run_zig(zig, tmp_dir, depfile, target, cmdline, stdout_mode)
            write_result(c_actual, c_actual_stderr, c_result)
            write_result(zig_actual, zig_actual_stderr, zig_result)

            if args.refresh:
                expected_stdout.write_text(c_result.stdout, encoding='utf-8')
                if expected_stderr is not None:
                    expected_stderr.write_text(c_result.stderr, encoding='utf-8')
                continue

            c_repeat_result = compile_run_c(tmp_dir, compiler, depfile, target, cmdline, stdout_mode)
            zig_repeat_result = run_zig(zig, tmp_dir, depfile, target, cmdline, stdout_mode)
            write_result(c_repeat, c_repeat_stderr, c_repeat_result)
            write_result(zig_repeat, zig_repeat_stderr, zig_repeat_result)

            compare_returncode(f"{case['name']} C", expected_exit_code, c_result.returncode)
            compare_returncode(f"{case['name']} Zig", expected_exit_code, zig_result.returncode)
            compare_returncode(f"{case['name']} C-vs-Zig", c_result.returncode, zig_result.returncode)
            compare_returncode(f"{case['name']} C repeat", c_result.returncode, c_repeat_result.returncode)
            compare_returncode(f"{case['name']} Zig repeat", zig_result.returncode, zig_repeat_result.returncode)

            diff_text(expected_stdout, c_actual)
            diff_text(expected_stdout, zig_actual)
            diff_text(c_actual, zig_actual)
            diff_text(c_actual, c_repeat)
            diff_text(zig_actual, zig_repeat)
            diff_text(c_actual_stderr, zig_actual_stderr)
            diff_text(c_actual_stderr, c_repeat_stderr)
            diff_text(zig_actual_stderr, zig_repeat_stderr)
            diff_text(expected_stderr_path, c_actual_stderr)
            diff_text(expected_stderr_path, zig_actual_stderr)

    if args.refresh:
        print('FIXDEP_REFRESH=pass')
        print(f'FIXTURE_DIR={FIXTURE_DIR}')
    else:
        print('FIXDEP_DIFF=pass')
        print('FIXDEP_DETERMINISM=pass')
        print(f'FIXTURE_DIR={FIXTURE_DIR}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
