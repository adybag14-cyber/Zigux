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
CASES_PATH = FIXTURE_DIR / 'cases.json'


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


def load_cases(cases_path: Path, fixture_dir: Path) -> list[dict[str, object]]:
    cases = json.loads(cases_path.read_text(encoding='utf-8'))
    if not isinstance(cases, list):
        raise RuntimeError(f'{cases_path} must contain a JSON list of fixdep cases')

    validated: list[dict[str, object]] = []
    seen_names: set[str] = set()
    for index, raw_case in enumerate(cases):
        label = f'cases[{index}]'
        if not isinstance(raw_case, dict):
            raise RuntimeError(f'{label} must be a JSON object')

        case = dict(raw_case)
        for field in ('name', 'depfile', 'target', 'cmdline', 'expected'):
            value = case.get(field)
            if not isinstance(value, str) or not value:
                raise RuntimeError(f'{label}.{field} must be a non-empty string')

        name = case['name']
        if name in seen_names:
            raise RuntimeError(f'duplicate fixdep case name: {name}')
        seen_names.add(name)

        expected_stdout_name = case.get('expected_stdout', case['expected'])
        if not isinstance(expected_stdout_name, str) or not expected_stdout_name:
            raise RuntimeError(f'{label}.expected_stdout must be a non-empty string when provided')

        for field, file_name in (
            ('depfile', case['depfile']),
            ('expected', case['expected']),
            ('expected_stdout', expected_stdout_name),
        ):
            path = fixture_dir / file_name
            if not path.is_file():
                raise RuntimeError(f'{label}.{field} missing fixture file: {path}')

        expected_stderr_name = case.get('expected_stderr')
        if expected_stderr_name is not None:
            if not isinstance(expected_stderr_name, str) or not expected_stderr_name:
                raise RuntimeError(f'{label}.expected_stderr must be a non-empty string when provided')
            stderr_path = fixture_dir / expected_stderr_name
            if not stderr_path.is_file():
                raise RuntimeError(f'{label}.expected_stderr missing fixture file: {stderr_path}')

        expected_exit_code = case.get('expected_exit_code', 0)
        if not isinstance(expected_exit_code, int) or expected_exit_code < 0:
            raise RuntimeError(f'{label}.expected_exit_code must be a non-negative integer')

        validated.append(case)

    return validated


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


def write_result(stdout_path: Path, stderr_path: Path, result: subprocess.CompletedProcess[str]) -> None:
    stdout_path.write_text(result.stdout, encoding='utf-8')
    stderr_path.write_text(result.stderr, encoding='utf-8')


def diff_text(expected: Path, actual: Path) -> None:
    run([sys.executable, str(ARTIFACT_DIFF), '--mode', 'text', str(expected), str(actual)], cwd=str(ROOT))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix='fixdep_checker_selftest_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        fixture_dir = tmp_dir / 'fixdep'
        fixture_dir.mkdir(parents=True, exist_ok=True)

        for file_name in ('sample.d', 'sample_expected.txt', 'sample.stderr.txt'):
            (fixture_dir / file_name).write_text('fixture\n', encoding='utf-8')

        good_cases = [
            {
                'name': 'sample',
                'depfile': 'sample.d',
                'target': 'sample.o',
                'cmdline': 'clang -c sample.c -o sample.o',
                'expected': 'sample_expected.txt',
            },
            {
                'name': 'sample_error',
                'depfile': 'sample.d',
                'target': 'sample_error.o',
                'cmdline': 'clang -c sample_error.c -o sample_error.o',
                'expected': 'sample_expected.txt',
                'expected_stderr': 'sample.stderr.txt',
                'expected_exit_code': 2,
            },
        ]

        cases_path = tmp_dir / 'cases.json'
        cases_path.write_text(json.dumps(good_cases), encoding='utf-8')
        loaded_cases = load_cases(cases_path, fixture_dir)
        if len(loaded_cases) != 2:
            raise RuntimeError('self-test expected two validated cases')

        duplicate_cases = good_cases + [dict(good_cases[0])]
        duplicate_cases[-1]['target'] = 'dup.o'
        cases_path.write_text(json.dumps(duplicate_cases), encoding='utf-8')
        try:
            load_cases(cases_path, fixture_dir)
        except RuntimeError as exc:
            if 'duplicate fixdep case name' not in str(exc):
                raise
        else:
            raise RuntimeError('self-test expected duplicate case name failure')

        missing_fixture_cases = [dict(good_cases[0])]
        missing_fixture_cases[0]['expected'] = 'missing_expected.txt'
        cases_path.write_text(json.dumps(missing_fixture_cases), encoding='utf-8')
        try:
            load_cases(cases_path, fixture_dir)
        except RuntimeError as exc:
            if 'missing fixture file' not in str(exc):
                raise
        else:
            raise RuntimeError('self-test expected missing fixture failure')

        bad_exit_code_cases = [dict(good_cases[0])]
        bad_exit_code_cases[0]['expected_exit_code'] = -1
        cases_path.write_text(json.dumps(bad_exit_code_cases), encoding='utf-8')
        try:
            load_cases(cases_path, fixture_dir)
        except RuntimeError as exc:
            if 'expected_exit_code must be a non-negative integer' not in str(exc):
                raise
        else:
            raise RuntimeError('self-test expected bad exit code failure')

    print('FIXDEP_DIFF_SELF_TEST=pass')
    print('FIXDEP_DIFF_SELF_TEST_CASE_COUNT=4')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Check bounded fixdep C/Zig artifact parity.')
    parser.add_argument('--refresh', action='store_true', help='Refresh the committed expected output from current C fixdep.')
    parser.add_argument('--cc', help='Explicit C compiler path to use.')
    parser.add_argument('--zig', help='Explicit zig executable path to use.')
    parser.add_argument('--self-test', action='store_true', help='Run built-in checker self-tests.')
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    cases = load_cases(CASES_PATH, FIXTURE_DIR)

    compiler = args.cc or os.environ.get('CC') or ('gcc' if os.name == 'nt' and shutil.which('wsl') else find_compiler(None))
    zig = find_zig(args.zig)

    for case in cases:
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
            c_repeat = tmp_dir / 'fixdep.c.repeat.txt'
            c_repeat_stderr = tmp_dir / 'fixdep.c.repeat.stderr.txt'
            zig_actual = tmp_dir / 'fixdep.zig.actual.txt'
            zig_actual_stderr = tmp_dir / 'fixdep.zig.actual.stderr.txt'
            zig_repeat = tmp_dir / 'fixdep.zig.repeat.txt'
            zig_repeat_stderr = tmp_dir / 'fixdep.zig.repeat.stderr.txt'

            c_result = compile_run_c(tmp_dir, compiler, depfile, target, cmdline)
            zig_result = run_zig(zig, tmp_dir, depfile, target, cmdline)
            write_result(c_actual, c_actual_stderr, c_result)
            write_result(zig_actual, zig_actual_stderr, zig_result)

            if args.refresh:
                expected_stdout.write_text(c_result.stdout, encoding='utf-8')
                if expected_stderr is not None:
                    expected_stderr.write_text(c_result.stderr, encoding='utf-8')
                continue

            c_repeat_result = compile_run_c(tmp_dir, compiler, depfile, target, cmdline)
            zig_repeat_result = run_zig(zig, tmp_dir, depfile, target, cmdline)
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
            if expected_stderr is not None:
                diff_text(expected_stderr, c_actual_stderr)
                diff_text(expected_stderr, zig_actual_stderr)

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
