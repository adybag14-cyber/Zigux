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
C_TOOL = ROOT / 'scripts' / 'mod' / 'mk_elfconfig.c'
ZIG_TOOL = ROOT / 'scripts' / 'zigux' / 'mk_elfconfig.zig'
FIXTURE_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig'
CASES_PATH = FIXTURE_DIR / 'cases.json'
CASES = json.loads(CASES_PATH.read_text(encoding='utf-8'))
EXPECTED_C_TOOL = ROOT / 'scripts' / 'mod' / 'mk_elfconfig.c'
EXPECTED_ZIG_TOOL = ROOT / 'scripts' / 'zigux' / 'mk_elfconfig.zig'


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


def read_hex_fixture(path: Path) -> bytes:
    text = path.read_text(encoding='utf-8').strip()
    return bytes.fromhex(text)


def validate_cases(cases: object) -> list[dict[str, str]]:
    if not isinstance(cases, list) or not cases:
        raise ValueError(f'{CASES_PATH}:expected_non_empty_json_list')

    validated: list[dict[str, str]] = []
    seen_names: set[str] = set()
    seen_inputs: set[str] = set()
    seen_expected: set[str] = set()
    required_fields = ('name', 'input_hex', 'expected')

    for index, raw_case in enumerate(cases):
        if not isinstance(raw_case, dict):
            raise ValueError(f'{CASES_PATH} entry {index} must be a JSON object')

        case: dict[str, str] = {}
        for field_name in required_fields:
            field_value = raw_case.get(field_name)
            if not isinstance(field_value, str) or not field_value:
                raise ValueError(f'{CASES_PATH}:entry[{index}]:missing_non_empty_{field_name}')
            case[field_name] = field_value

        if case['name'] in seen_names:
            raise ValueError(f'{CASES_PATH}:duplicate_name:{case["name"]}')
        if case['input_hex'] in seen_inputs:
            raise ValueError(f'{CASES_PATH}:duplicate_input_hex:{case["input_hex"]}')
        if case['expected'] in seen_expected:
            raise ValueError(f'{CASES_PATH}:duplicate_expected:{case["expected"]}')

        for field_name in ('input_hex', 'expected'):
            case_path = FIXTURE_DIR / case[field_name]
            if not case_path.exists():
                raise FileNotFoundError(f'{CASES_PATH}:missing_{field_name}:{case[field_name]}')

        seen_names.add(case['name'])
        seen_inputs.add(case['input_hex'])
        seen_expected.add(case['expected'])
        validated.append(case)

    return validated


def validate_tool_sources(c_tool: Path, zig_tool: Path) -> None:
    if c_tool != EXPECTED_C_TOOL:
        raise ValueError(f'mk_elfconfig:c_tool={c_tool},expected={EXPECTED_C_TOOL}')
    if zig_tool != EXPECTED_ZIG_TOOL:
        raise ValueError(f'mk_elfconfig:zig_tool={zig_tool},expected={EXPECTED_ZIG_TOOL}')


def expect_failure(label: str, callback, expected_message: str) -> None:
    try:
        callback()
    except (ValueError, FileNotFoundError) as exc:
        actual_message = str(exc)
        if actual_message != expected_message:
            raise SystemExit(
                f'mk_elfconfig:self-test:{label}:expected={expected_message!r}:actual={actual_message!r}'
            ) from exc
        return
    raise SystemExit(f'mk_elfconfig:self-test:{label}:missing_failure:{expected_message!r}')


def run_self_test() -> int:
    valid_cases = validate_cases(CASES)
    if len(valid_cases) != 5:
        raise SystemExit(f'mk_elfconfig:self-test:case_count={len(valid_cases)},expected=5')

    validate_tool_sources(C_TOOL, ZIG_TOOL)

    expect_failure(
        'non_list_cases',
        lambda: validate_cases({'cases': valid_cases}),
        f'{CASES_PATH}:expected_non_empty_json_list',
    )
    expect_failure(
        'empty_cases',
        lambda: validate_cases([]),
        f'{CASES_PATH}:expected_non_empty_json_list',
    )
    expect_failure(
        'duplicate_name',
        lambda: validate_cases([valid_cases[0], dict(valid_cases[0])]),
        f'{CASES_PATH}:duplicate_name:{valid_cases[0]["name"]}',
    )
    expect_failure(
        'duplicate_input_hex',
        lambda: validate_cases([valid_cases[0], {**valid_cases[1], 'input_hex': valid_cases[0]['input_hex']}]),
        f'{CASES_PATH}:duplicate_input_hex:{valid_cases[0]["input_hex"]}',
    )
    expect_failure(
        'duplicate_expected',
        lambda: validate_cases([valid_cases[0], {**valid_cases[1], 'expected': valid_cases[0]['expected']}]),
        f'{CASES_PATH}:duplicate_expected:{valid_cases[0]["expected"]}',
    )
    expect_failure(
        'missing_field',
        lambda: validate_cases([{'name': 'elf32', 'input_hex': 'elf32.hex'}]),
        f'{CASES_PATH}:entry[0]:missing_non_empty_expected',
    )
    expect_failure(
        'missing_fixture',
        lambda: validate_cases([{'name': 'missing', 'input_hex': 'missing.hex', 'expected': 'missing_expected.json'}]),
        f'{CASES_PATH}:missing_input_hex:missing.hex',
    )
    expect_failure(
        'explicit_tool_drift',
        lambda: validate_tool_sources(C_TOOL.with_name('mk_elfconfig-mismatch.c'), ZIG_TOOL),
        f'mk_elfconfig:c_tool={C_TOOL.with_name("mk_elfconfig-mismatch.c")},expected={EXPECTED_C_TOOL}',
    )

    print('MK_ELFCONFIG_SELF_TEST=pass')
    print('MK_ELFCONFIG_SELF_TEST_CASE_COUNT=8')
    return 0


def compile_c(tmp_dir: Path, compiler: str) -> Path:
    exe = tmp_dir / ('mk_elfconfig-c.exe' if os.name == 'nt' else 'mk_elfconfig-c')
    if os.name == 'nt' and shutil.which('wsl'):
        script_path = tmp_dir / 'compile_mk_elfconfig_c.sh'
        script_path.write_text(
            '\n'.join([
                '#!/usr/bin/env bash',
                'set -euo pipefail',
                ' '.join([
                    shlex.quote(compiler),
                    '-std=gnu11',
                    '-Wall',
                    '-Wextra',
                    '-o', shlex.quote(windows_to_wsl(exe)),
                    shlex.quote(windows_to_wsl(C_TOOL)),
                ]),
            ]) + '\n',
            encoding='utf-8',
            newline='\n',
        )
        run(['wsl', 'bash', windows_to_wsl(script_path)], cwd=str(ROOT))
        return exe

    run([compiler, '-std=gnu11', '-Wall', '-Wextra', '-o', str(exe), str(C_TOOL)], cwd=str(ROOT))
    return exe


def compile_zig(tmp_dir: Path, zig: str) -> Path:
    exe = tmp_dir / ('mk_elfconfig-zig.exe' if os.name == 'nt' else 'mk_elfconfig-zig')
    run([zig, 'build-exe', str(ZIG_TOOL), '-femit-bin=' + str(exe)], cwd=str(ROOT))
    return exe


def run_binary(exe: Path, data: bytes) -> dict[str, object]:
    proc = subprocess.run([str(exe)], input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return {
        'exit_code': proc.returncode,
        'stdout': proc.stdout.decode('utf-8'),
        'stderr': proc.stderr.decode('utf-8'),
    }


def run_c_binary_wsl(exe: Path, data: bytes, out_path: Path) -> dict[str, object]:
    input_hex = data.hex()
    script_path = out_path.with_suffix('.sh')
    script_path.write_text(
        '\n'.join([
            '#!/usr/bin/env bash',
            'set -euo pipefail',
            'python3 - <<\'PY\'',
            'import json, pathlib, subprocess',
            f'hex_data = {input_hex!r}',
            f'exe_path = {windows_to_wsl(exe)!r}',
            f'out_path = {windows_to_wsl(out_path)!r}',
            'data = bytes.fromhex(hex_data)',
            'proc = subprocess.run([exe_path], input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)',
            'pathlib.Path(out_path).write_text(json.dumps({"exit_code": proc.returncode, "stdout": proc.stdout.decode("utf-8"), "stderr": proc.stderr.decode("utf-8")}, indent=2) + "\\n", encoding="utf-8")',
            'PY',
        ]) + '\n',
        encoding='utf-8',
        newline='\n',
    )
    run(['wsl', 'bash', windows_to_wsl(script_path)], cwd=str(ROOT))
    return json.loads(out_path.read_text(encoding='utf-8'))


def run_c_binary(exe: Path, data: bytes, out_path: Path) -> dict[str, object]:
    if os.name == 'nt' and shutil.which('wsl'):
        return run_c_binary_wsl(exe, data, out_path)
    result = run_binary(exe, data)
    out_path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description='Check bounded mk_elfconfig C/Zig artifact parity.')
    parser.add_argument('--refresh', action='store_true', help='Refresh committed expected outputs from current C behavior.')
    parser.add_argument('--cc', help='Explicit C compiler path to use.')
    parser.add_argument('--self-test', action='store_true', help='Run built-in manifest and explicit-tool failure checks.')
    parser.add_argument('--zig', help='Explicit zig executable path to use.')
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    compiler = args.cc or os.environ.get('CC') or ('gcc' if os.name == 'nt' and shutil.which('wsl') else find_compiler(None))
    zig = find_zig(args.zig)
    cases = validate_cases(CASES)
    validate_tool_sources(C_TOOL, ZIG_TOOL)

    with tempfile.TemporaryDirectory(prefix='zigux_mkelfconfig_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        c_exe = compile_c(tmp_dir, compiler)
        zig_exe = compile_zig(tmp_dir, zig)

        for case in cases:
            input_path = FIXTURE_DIR / case['input_hex']
            expected_path = FIXTURE_DIR / case['expected']
            c_actual = tmp_dir / f"{case['name']}.c.actual.json"
            c_repeat = tmp_dir / f"{case['name']}.c.repeat.json"
            zig_actual = tmp_dir / f"{case['name']}.zig.actual.json"
            zig_repeat = tmp_dir / f"{case['name']}.zig.repeat.json"
            data = read_hex_fixture(input_path)

            c_result = run_c_binary(c_exe, data, c_actual)
            zig_result = run_binary(zig_exe, data)
            zig_actual.write_text(json.dumps(zig_result, indent=2) + '\n', encoding='utf-8')

            if args.refresh:
                expected_path.write_text(json.dumps(c_result, indent=2) + '\n', encoding='utf-8')
                continue

            diff = [sys.executable, str(ARTIFACT_DIFF), '--mode', 'json']
            run(diff + [str(expected_path), str(c_actual)], cwd=str(ROOT))
            run(diff + [str(expected_path), str(zig_actual)], cwd=str(ROOT))
            run(diff + [str(c_actual), str(zig_actual)], cwd=str(ROOT))

            c_repeat_result = run_c_binary(c_exe, data, c_repeat)
            zig_repeat_result = run_binary(zig_exe, data)
            zig_repeat.write_text(json.dumps(zig_repeat_result, indent=2) + '\n', encoding='utf-8')

            run(diff + [str(c_actual), str(c_repeat)], cwd=str(ROOT))
            run(diff + [str(zig_actual), str(zig_repeat)], cwd=str(ROOT))

    if args.refresh:
        print('MK_ELFCONFIG_REFRESH=pass')
        print(f'FIXTURE_DIR={FIXTURE_DIR}')
    else:
        print('MK_ELFCONFIG_DIFF=pass')
        print('MK_ELFCONFIG_DETERMINISM=pass')
        print(f'FIXTURE_DIR={FIXTURE_DIR}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
