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


def load_cases(cases_path: Path) -> object:
    return json.loads(cases_path.read_text(encoding='utf-8'))


def validate_cases(cases_path: Path, fixture_dir: Path, cases: object) -> list[dict[str, str]]:
    if not isinstance(cases, list) or not cases:
        raise ValueError(f'{cases_path} must contain a non-empty JSON list')

    validated: list[dict[str, str]] = []
    seen_names: set[str] = set()
    seen_inputs: set[str] = set()
    seen_expected: set[str] = set()
    required_fields = ('name', 'input_hex', 'expected')

    for index, raw_case in enumerate(cases):
        if not isinstance(raw_case, dict):
            raise ValueError(f'{cases_path} entry {index} must be a JSON object')

        case: dict[str, str] = {}
        for field_name in required_fields:
            field_value = raw_case.get(field_name)
            if not isinstance(field_value, str) or not field_value:
                raise ValueError(f'{cases_path} entry {index} is missing non-empty {field_name!r}')
            case[field_name] = field_value

        if case['name'] in seen_names:
            raise ValueError(f'{cases_path} reuses case name {case["name"]!r}')
        if case['input_hex'] in seen_inputs:
            raise ValueError(f'{cases_path} reuses input_hex {case["input_hex"]!r}')
        if case['expected'] in seen_expected:
            raise ValueError(f'{cases_path} reuses expected artifact {case["expected"]!r}')

        for field_name in ('input_hex', 'expected'):
            case_path = fixture_dir / case[field_name]
            if not case_path.exists():
                raise FileNotFoundError(f'{cases_path} references missing {field_name} file {case[field_name]!r}')

        seen_names.add(case['name'])
        seen_inputs.add(case['input_hex'])
        seen_expected.add(case['expected'])
        validated.append(case)

    return validated


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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def build_self_test_root(root: Path) -> tuple[Path, Path]:
    fixture_dir = root / 'zigux' / 'tests' / 'fixtures' / 'mk_elfconfig'
    cases_path = fixture_dir / 'cases.json'
    write_text(fixture_dir / 'elf32.hex', '7f454c46\n')
    write_text(fixture_dir / 'elf64.hex', '7f454c4602010100\n')
    write_text(fixture_dir / 'elf32_expected.json', '{}\n')
    write_text(fixture_dir / 'elf64_expected.json', '{}\n')
    write_text(
        cases_path,
        json.dumps(
            [
                {'name': 'elf32', 'input_hex': 'elf32.hex', 'expected': 'elf32_expected.json'},
                {'name': 'elf64', 'input_hex': 'elf64.hex', 'expected': 'elf64_expected.json'},
            ],
            indent=2,
        )
        + '\n',
    )
    return fixture_dir, cases_path


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix='zigux_mkelfconfig_selftest_') as tmp_dir_str:
        root = Path(tmp_dir_str)
        fixture_dir, cases_path = build_self_test_root(root)
        assert validate_cases(cases_path, fixture_dir, load_cases(cases_path)) == [
            {'name': 'elf32', 'input_hex': 'elf32.hex', 'expected': 'elf32_expected.json'},
            {'name': 'elf64', 'input_hex': 'elf64.hex', 'expected': 'elf64_expected.json'},
        ]

        fixture_dir, cases_path = build_self_test_root(root)
        duplicate_name_cases = load_cases(cases_path)
        duplicate_name_cases[1]['name'] = 'elf32'
        try:
            validate_cases(cases_path, fixture_dir, duplicate_name_cases)
        except ValueError as exc:
            assert "reuses case name 'elf32'" in str(exc)
        else:
            raise AssertionError('expected duplicate-name validation failure')

        fixture_dir, cases_path = build_self_test_root(root)
        duplicate_expected_cases = load_cases(cases_path)
        duplicate_expected_cases[1]['expected'] = 'elf32_expected.json'
        try:
            validate_cases(cases_path, fixture_dir, duplicate_expected_cases)
        except ValueError as exc:
            assert "reuses expected artifact 'elf32_expected.json'" in str(exc)
        else:
            raise AssertionError('expected duplicate-expected validation failure')

        fixture_dir, cases_path = build_self_test_root(root)
        missing_expected_cases = load_cases(cases_path)
        (fixture_dir / 'elf64_expected.json').unlink()
        try:
            validate_cases(cases_path, fixture_dir, missing_expected_cases)
        except FileNotFoundError as exc:
            assert "references missing expected file 'elf64_expected.json'" in str(exc)
        else:
            raise AssertionError('expected missing-expected validation failure')

    print('MK_ELFCONFIG_SELF_TEST=pass')
    print('MK_ELFCONFIG_SELF_TEST_CASE_COUNT=4')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Check bounded mk_elfconfig C/Zig artifact parity.')
    parser.add_argument('--refresh', action='store_true', help='Refresh committed expected outputs from current C behavior.')
    parser.add_argument('--cc', help='Explicit C compiler path to use.')
    parser.add_argument('--zig', help='Explicit zig executable path to use.')
    parser.add_argument('--self-test', action='store_true', help='Run checkout-free validator coverage for mk_elfconfig fixture rules.')
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    compiler = args.cc or os.environ.get('CC') or ('gcc' if os.name == 'nt' and shutil.which('wsl') else find_compiler(None))
    zig = find_zig(args.zig)
    cases = validate_cases(CASES_PATH, FIXTURE_DIR, load_cases(CASES_PATH))

    with tempfile.TemporaryDirectory(prefix='zigux_mkelfconfig_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        c_exe = compile_c(tmp_dir, compiler)
        zig_exe = compile_zig(tmp_dir, zig)

        for case in cases:
            input_path = FIXTURE_DIR / case['input_hex']
            expected_path = FIXTURE_DIR / case['expected']
            c_actual = tmp_dir / f"{case['name']}.c.actual.json"
            zig_actual = tmp_dir / f"{case['name']}.zig.actual.json"
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

    if args.refresh:
        print('MK_ELFCONFIG_REFRESH=pass')
        print(f'FIXTURE_DIR={FIXTURE_DIR}')
    else:
        print('MK_ELFCONFIG_DIFF=pass')
        print(f'FIXTURE_DIR={FIXTURE_DIR}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
