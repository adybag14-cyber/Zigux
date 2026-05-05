#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import re
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


def run_capture(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=False, text=True, capture_output=True, **kwargs)


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


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding='utf-8', newline='\n')


def write_stdout_stderr(
    stdout_path: Path,
    stderr_path: Path | None,
    result: subprocess.CompletedProcess[str],
    *,
    normalize_stderr: bool = False,
) -> None:
    write_text(stdout_path, result.stdout)
    if stderr_path is not None:
        stderr = normalize_cli_stderr(result.stderr) if normalize_stderr else result.stderr
        write_text(stderr_path, stderr)


def compile_run_c_wsl(tmp_dir: Path, exe: Path, actual: Path, actual_stderr: Path | None, compiler: str, argv: list[str]) -> None:
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
    if actual_stderr is not None:
        run_line.extend(['2>', shlex.quote(windows_to_wsl(actual_stderr))])
    lines = [
        '#!/usr/bin/env bash',
        'set -euo pipefail',
        ' '.join(command),
        ' '.join(run_line),
    ]
    script_path.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    run(['wsl', 'bash', windows_to_wsl(script_path)], cwd=str(ROOT))


def compile_run_c(tmp_dir: Path, actual: Path, actual_stderr: Path | None, compiler: str, argv: list[str]) -> None:
    exe = tmp_dir / ('genksyms-bridge-c.exe' if os.name == 'nt' else 'genksyms-bridge-c')
    if os.name == 'nt' and shutil.which('wsl'):
        compile_run_c_wsl(tmp_dir, exe, actual, actual_stderr, compiler, argv)
        return
    run([compiler, '-std=c11', '-Wall', '-Wextra', '-o', str(exe), str(C_HARNESS)], cwd=str(ROOT))
    result = run_capture([str(exe), *argv], cwd=str(ROOT))
    result.check_returncode()
    write_stdout_stderr(actual, actual_stderr, result)


def run_zig(zig: str, tmp_dir: Path, actual: Path, actual_stderr: Path | None, argv: list[str]) -> None:
    exe = tmp_dir / ('genksyms-bridge-zig.exe' if os.name == 'nt' else 'genksyms-bridge-zig')
    run([zig, 'build-exe', str(ZIG_TOOL), '-femit-bin=' + str(exe)], cwd=str(ROOT))
    result = run_capture([str(exe), *argv], cwd=str(ROOT))
    result.check_returncode()
    write_stdout_stderr(actual, actual_stderr, result)


def normalize_cli_stderr(text: str) -> str:
    patterns = (
        re.compile(r"^.+: (invalid option -- '.+')$"),
        re.compile(r"^.+: (option requires an argument -- '.+')$"),
        re.compile(r"^.+: (option '--.+?' requires an argument)$"),
        re.compile(r"^.+: (option '--.+?' doesn't allow an argument)$"),
        re.compile(r"^.+: (unrecognized option '.+')$"),
        re.compile(r"^.+: (option '--.+?' is ambiguous; possibilities: .+)$"),
    )
    normalized_lines: list[str] = []
    for line in text.splitlines():
        normalized = line
        for pattern in patterns:
            match = pattern.match(line)
            if match:
                normalized = match.group(1)
                break
        normalized_lines.append(normalized)
    if not normalized_lines:
        return ''
    return '\n'.join(normalized_lines) + '\n'


def write_process_json(path: Path, result: subprocess.CompletedProcess[str], *, normalize_stderr: bool) -> None:
    payload = {
        'stdout': result.stdout,
        'stderr': normalize_cli_stderr(result.stderr) if normalize_stderr else result.stderr,
        'exit_code': result.returncode,
    }
    write_text(path, json.dumps(payload, indent=2) + '\n')


def capture_run_c(tmp_dir: Path, actual: Path, compiler: str, argv: list[str], *, normalize_stderr: bool) -> None:
    exe = tmp_dir / ('genksyms-bridge-c.exe' if os.name == 'nt' else 'genksyms-bridge-c')
    if os.name == 'nt' and shutil.which('wsl'):
        raise SystemExit('CLI parity capture is not implemented for Windows WSL mode')
    run([compiler, '-std=c11', '-Wall', '-Wextra', '-o', str(exe), str(C_HARNESS)], cwd=str(ROOT))
    result = run_capture([str(exe), *argv], cwd=str(ROOT))
    write_process_json(actual, result, normalize_stderr=normalize_stderr)


def capture_run_zig(zig: str, tmp_dir: Path, actual: Path, argv: list[str], *, normalize_stderr: bool) -> None:
    exe = tmp_dir / ('genksyms-bridge-zig.exe' if os.name == 'nt' else 'genksyms-bridge-zig')
    run([zig, 'build-exe', str(ZIG_TOOL), '-femit-bin=' + str(exe)], cwd=str(ROOT))
    result = run_capture([str(exe), *argv], cwd=str(ROOT))
    write_process_json(actual, result, normalize_stderr=normalize_stderr)


def fail_manifest(issues: list[str]) -> None:
    print('GENKSYMS_BRIDGE_MANIFEST=fail')
    print('GENKSYMS_BRIDGE_MANIFEST_ISSUES_START')
    for issue in issues:
        print(issue)
    print('GENKSYMS_BRIDGE_MANIFEST_ISSUES_END')
    raise SystemExit(1)


def load_cases_manifest(cases_path: Path = FIXTURE_DIR / 'cases.json') -> list[dict[str, object]]:
    try:
        payload = json.loads(cases_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        fail_manifest([f'cases.json:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}'])

    issues: list[str] = []
    if not isinstance(payload, dict):
        fail_manifest(['cases.json:expected_top_level_object'])

    cases = payload.get('cases')
    if not isinstance(cases, list):
        fail_manifest(['cases.json:cases:expected_list'])
    if not cases:
        issues.append('cases.json:cases:empty')

    expected_files = {path.name for path in FIXTURE_DIR.glob('*_expected.json')}
    referenced_expected: set[str] = set()
    seen_names: set[str] = set()
    seen_expected: set[str] = set()
    valid_modes = {'stdout_json', 'process_json'}

    for index, case in enumerate(cases):
        prefix = f'cases.json:cases[{index}]'
        if not isinstance(case, dict):
            issues.append(f'{prefix}:expected_object')
            continue

        name = case.get('name')
        if not isinstance(name, str) or not name:
            issues.append(f'{prefix}:name:expected_nonempty_string')
        elif name in seen_names:
            issues.append(f'{prefix}:name:duplicate:{name}')
        else:
            seen_names.add(name)

        argv = case.get('argv')
        if not isinstance(argv, list) or any(not isinstance(item, str) for item in argv):
            issues.append(f'{prefix}:argv:expected_string_list')

        expected = case.get('expected')
        if not isinstance(expected, str) or not expected:
            issues.append(f'{prefix}:expected:expected_nonempty_string')
        else:
            if Path(expected).name != expected:
                issues.append(f'{prefix}:expected:must_be_flat_filename:{expected}')
            elif expected in seen_expected:
                issues.append(f'{prefix}:expected:duplicate_reference:{expected}')
            else:
                seen_expected.add(expected)
            referenced_expected.add(expected)
            if expected not in expected_files:
                issues.append(f'{prefix}:expected:missing_fixture:{expected}')

        mode = case.get('mode', 'stdout_json')
        if not isinstance(mode, str) or mode not in valid_modes:
            issues.append(f'{prefix}:mode:unsupported:{mode}')

        normalize_stderr = case.get('normalize_stderr')
        if normalize_stderr is not None and not isinstance(normalize_stderr, bool):
            issues.append(f'{prefix}:normalize_stderr:expected_bool')
        if mode != 'process_json' and normalize_stderr:
            issues.append(f'{prefix}:normalize_stderr:requires_process_json_mode')

    orphaned_expected = sorted(expected_files - referenced_expected)
    for name in orphaned_expected:
        issues.append(f'cases.json:orphaned_expected:{name}')

    if issues:
        fail_manifest(issues)

    return cases


def expect_self_test_failure(label: str, expected_fragment: str, func, *args) -> None:
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        try:
            func(*args)
        except SystemExit as exc:
            if exc.code != 1:
                raise SystemExit(
                    f"genksyms-bridge:self-test:{label}:expected_exit=1:actual_exit={exc.code!r}"
                ) from exc
        else:
            raise SystemExit(
                f"genksyms-bridge:self-test:{label}:missing_system_exit:{expected_fragment!r}"
            )

    actual = capture.getvalue()
    if expected_fragment not in actual:
        raise SystemExit(
            f"genksyms-bridge:self-test:{label}:expected={expected_fragment!r}:actual={actual!r}"
        )


def expect_process_json(
    label: str,
    *,
    stdout: str,
    stderr: str,
    exit_code: int,
    normalize_stderr: bool,
    expected_stderr: str,
) -> None:
    with tempfile.TemporaryDirectory(prefix='zigux_genksyms_bridge_process_json_') as tmp_dir_str:
        actual_path = Path(tmp_dir_str) / 'actual.json'
        result = subprocess.CompletedProcess(
            args=['genksyms-bridge-self-test'],
            returncode=exit_code,
            stdout=stdout,
            stderr=stderr,
        )
        write_process_json(actual_path, result, normalize_stderr=normalize_stderr)
        payload = json.loads(actual_path.read_text(encoding='utf-8'))

    expected = {
        'stdout': stdout,
        'stderr': expected_stderr,
        'exit_code': exit_code,
    }
    if payload != expected:
        raise SystemExit(
            f'genksyms-bridge:self-test:{label}:expected={expected!r}:actual={payload!r}'
        )


def run_self_test() -> None:
    if find_compiler('/tmp/zigux-self-test-cc') != '/tmp/zigux-self-test-cc':
        raise SystemExit('genksyms-bridge:self-test:explicit_cc_passthrough')
    if find_zig('/tmp/zigux-self-test-zig') != '/tmp/zigux-self-test-zig':
        raise SystemExit('genksyms-bridge:self-test:explicit_zig_passthrough')

    normalized = normalize_cli_stderr(
        "zigux-genksyms: invalid option -- 'x'\n"
        "zigux-genksyms: option '--debug' doesn't allow an argument\n"
        "zigux-genksyms: option '--dum' is ambiguous; possibilities: --dump-types --dummy\n"
    )
    expected_normalized = (
        "invalid option -- 'x'\n"
        "option '--debug' doesn't allow an argument\n"
        "option '--dum' is ambiguous; possibilities: --dump-types --dummy\n"
    )
    if normalized != expected_normalized:
        raise SystemExit(
            f'genksyms-bridge:self-test:stderr_normalization:expected={expected_normalized!r}:actual={normalized!r}'
        )

    expect_process_json(
        'process_json_normalized_stderr',
        stdout='{"tool":"scripts/genksyms/genksyms"}\n',
        stderr="zigux-genksyms: invalid option -- 'x'\n",
        exit_code=1,
        normalize_stderr=True,
        expected_stderr="invalid option -- 'x'\n",
    )
    expect_process_json(
        'process_json_raw_stderr',
        stdout='',
        stderr='verbatim stderr\nsecond line\n',
        exit_code=7,
        normalize_stderr=False,
        expected_stderr='verbatim stderr\nsecond line\n',
    )

    cases = load_cases_manifest()
    if len(cases) != 26:
        raise SystemExit(f'genksyms-bridge:self-test:case_count={len(cases)},expected=26')
    if cases[0].get('name') != 'minimal':
        raise SystemExit(
            f"genksyms-bridge:self-test:first_case={cases[0].get('name')!r},expected='minimal'"
        )

    with tempfile.TemporaryDirectory(prefix='zigux_genksyms_bridge_selftest_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        expected_fixture = tmp_dir / 'minimal_expected.json'
        expected_fixture.write_text('{}\n', encoding='utf-8', newline='\n')
        cases_path = tmp_dir / 'cases.json'

        cases_path.writeText(
            json.dumps(
                {
                    'cases': [
                        {
                            'name': 'minimal',
                            'argv': [],
                            'expected': expected_fixture.name,
                            'normalize_stderr': True,
                        }
                    ]
                },
                indent=2,
            )
            + '\n',
            encoding='utf-8',
            newline='\n',
        )
        expect_self_test_failure(
            'normalize_stderr_requires_process_json',
            'cases.json:cases[0]:normalize_stderr:requires_process_json_mode',
            load_cases_manifest,
            cases_path,
        )

        cases_path.write_text(
            json.dumps({'cases': [{'name': 'minimal', 'argv': [], 'expected': 'missing.json'}]}, indent=2) + '\n',
            encoding='utf-8',
            newline='\n',
        )
        expect_self_test_failure(
            'missing_expected_fixture',
            'cases.json:cases[0]:expected:missing_fixture:missing.json',
            load_cases_manifest,
            cases_path,
        )

    print('PHASE2_GENKSYMS_BRIDGE_SELF_TEST=pass')
    print('PHASE2_GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=26')


def main() -> int:
    parser = argparse.ArgumentParser(description='Check bounded genksyms bridge parity.')
    parser.add_argument('--cc', help='C compiler to use')
    parser.add_argument('--zig', help='Path to Zig executable')
    parser.add_argument('--refresh', action='store_true', help='Refresh the committed expected fixtures from the C harness')
    parser.add_argument('--self-test', action='store_true', help='Run built-in manifest and stderr-normalization checks.')
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    cases = load_cases_manifest()
    compiler = args.cc or os.environ.get('CC') or ('gcc' if os.name == 'nt' and shutil.which('wsl') else find_compiler(None))
    zig = find_zig(args.zig)

    with tempfile.TemporaryDirectory(prefix='zigux_genksyms_bridge_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        for case in cases:
            mode = case.get('mode', 'stdout_json')
            c_actual = tmp_dir / f"{case['name']}.c.actual.json"
            c_repeat = tmp_dir / f"{case['name']}.c.repeat.json"
            zig_actual = tmp_dir / f"{case['name']}.zig.actual.json"
            zig_repeat = tmp_dir / f"{case['name']}.zig.repeat.json"
            c_actual_stderr = tmp_dir / f"{case['name']}.c.actual.stderr.txt"
            c_repeat_stderr = tmp_dir / f"{case['name']}.c.repeat.stderr.txt"
            zig_actual_stderr = tmp_dir / f"{case['name']}.zig.actual.stderr.txt"
            zig_repeat_stderr = tmp_dir / f"{case['name']}.zig.repeat.stderr.txt"
            empty_stderr = tmp_dir / 'expected-empty.stderr.txt'
            write_text(empty_stderr, '')
            if mode == 'process_json':
                normalize_stderr = bool(case.get('normalize_stderr', False))
                capture_run_c(tmp_dir, c_actual, compiler, case['argv'], normalize_stderr=normalize_stderr)
                capture_run_zig(zig, tmp_dir, zig_actual, case['argv'], normalize_stderr=normalize_stderr)
            elif mode == 'stdout_json':
                compile_run_c(tmp_dir, c_actual, c_actual_stderr, compiler, case['argv'])
                run_zig(zig, tmp_dir, zig_actual, zig_actual_stderr, case['argv'])
            else:
                raise SystemExit(f"Unsupported genksyms bridge case mode: {mode}")

            expected = FIXTURE_DIR / case['expected']
            if args.refresh:
                expected.write_text(c_actual.read_text(encoding='utf-8'), encoding='utf-8', newline='\n')
                continue

            diff_base = [sys.executable, str(ARTIFACT_DIFF), '--mode', 'json']
            run(diff_base + [str(expected), str(c_actual)], cwd=str(ROOT))
            run(diff_base + [str(expected), str(zig_actual)], cwd=str(ROOT))
            run(diff_base + [str(c_actual), str(zig_actual)], cwd=str(ROOT))
            if mode == 'stdout_json':
                text_diff_base = [sys.executable, str(ARTIFACT_DIFF), '--mode', 'text']
                run(text_diff_base + [str(empty_stderr), str(c_actual_stderr)], cwd=str(ROOT))
                run(text_diff_base + [str(empty_stderr), str(zig_actual_stderr)], cwd=str(ROOT))
                run(text_diff_base + [str(c_actual_stderr), str(zig_actual_stderr)], cwd=str(ROOT))

            if mode == 'process_json':
                normalize_stderr = bool(case.get('normalize_stderr', False))
                capture_run_c(tmp_dir, c_repeat, compiler, case['argv'], normalize_stderr=normalize_stderr)
                capture_run_zig(zig, tmp_dir, zig_repeat, case['argv'], normalize_stderr=normalize_stderr)
            else:
                compile_run_c(tmp_dir, c_repeat, c_repeat_stderr, compiler, case['argv'])
                run_zig(zig, tmp_dir, zig_repeat, zig_repeat_stderr, case['argv'])

            run(diff_base + [str(c_actual), str(c_repeat)], cwd=str(ROOT))
            run(diff_base + [str(zig_actual), str(zig_repeat)], cwd=str(ROOT))
            if mode == 'stdout_json':
                text_diff_base = [sys.executable, str(ARTIFACT_DIFF), '--mode', 'text']
                run(text_diff_base + [str(c_actual_stderr), str(c_repeat_stderr)], cwd=str(ROOT))
                run(text_diff_base + [str(zig_actual_stderr), str(zig_repeat_stderr)], cwd=str(ROOT))

    if args.refresh:
        print('GENKSYMS_BRIDGE_REFRESH=pass')
    else:
        print('GENKSYMS_BRIDGE_DIFF=pass')
        print('GENKSYMS_BRIDGE_DETERMINISM=pass')
    print(f'FIXTURE_DIR={FIXTURE_DIR}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
