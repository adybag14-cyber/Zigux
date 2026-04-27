#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
EXPECTED_CASE_KEYS = {'name', 'argv', 'expected', 'mode', 'normalize_stderr'}
EXPECTED_JSON_SUFFIX = '_expected.json'


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
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8', newline='\n')


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


def validate_cases_manifest(payload: object) -> list[dict[str, object]]:
    if not isinstance(payload, dict):
        raise SystemExit('genksyms bridge cases.json must contain a top-level object')

    raw_cases = payload.get('cases')
    if not isinstance(raw_cases, list):
        raise SystemExit('genksyms bridge cases.json must expose a list in the "cases" field')

    fixture_names = {
        path.name
        for path in FIXTURE_DIR.glob(f'*{EXPECTED_JSON_SUFFIX}')
        if path.is_file()
    }
    referenced_expected: set[str] = set()
    seen_names: set[str] = set()
    seen_expected: set[str] = set()
    validated_cases: list[dict[str, object]] = []

    for index, case in enumerate(raw_cases):
        case_label = f'cases[{index}]'
        if not isinstance(case, dict):
            raise SystemExit(f'{case_label} must be an object')

        unknown_keys = sorted(set(case) - EXPECTED_CASE_KEYS)
        if unknown_keys:
            raise SystemExit(f'{case_label} uses unsupported keys: {", ".join(unknown_keys)}')

        name = case.get('name')
        if not isinstance(name, str) or not name:
            raise SystemExit(f'{case_label}.name must be a non-empty string')
        if name in seen_names:
            raise SystemExit(f'duplicate genksyms bridge case name: {name}')
        seen_names.add(name)

        argv = case.get('argv')
        if not isinstance(argv, list) or any(not isinstance(arg, str) for arg in argv):
            raise SystemExit(f'{case_label}.argv must be a list of strings')

        expected_name = case.get('expected')
        if not isinstance(expected_name, str) or not expected_name:
            raise SystemExit(f'{case_label}.expected must be a non-empty string')
        if expected_name in seen_expected:
            raise SystemExit(f'duplicate genksyms bridge expected fixture reference: {expected_name}')
        if expected_name not in fixture_names:
            raise SystemExit(f'{case_label}.expected points to a missing fixture: {expected_name}')
        seen_expected.add(expected_name)
        referenced_expected.add(expected_name)

        mode = case.get('mode', 'stdout_json')
        if mode not in {'stdout_json', 'process_json'}:
            raise SystemExit(f'{case_label}.mode must be "stdout_json" or "process_json"')

        normalize_stderr = case.get('normalize_stderr', False)
        if not isinstance(normalize_stderr, bool):
            raise SystemExit(f'{case_label}.normalize_stderr must be a boolean when present')
        if normalize_stderr and mode != 'process_json':
            raise SystemExit(f'{case_label}.normalize_stderr is only valid for process_json cases')

        validated_cases.append(case)

    orphan_fixtures = sorted(fixture_names - referenced_expected)
    if orphan_fixtures:
        raise SystemExit(
            'unreferenced genksyms bridge expected fixtures: ' + ', '.join(orphan_fixtures)
        )

    return validated_cases


def main() -> int:
    parser = argparse.ArgumentParser(description='Check bounded genksyms bridge parity.')
    parser.add_argument('--cc', help='C compiler to use')
    parser.add_argument('--zig', help='Path to Zig executable')
    parser.add_argument('--refresh', action='store_true', help='Refresh the committed expected fixtures from the C harness')
    args = parser.parse_args()

    compiler = args.cc or os.environ.get('CC') or ('gcc' if os.name == 'nt' and shutil.which('wsl') else find_compiler(None))
    zig = find_zig(args.zig)
    cases = validate_cases_manifest(
        json.loads((FIXTURE_DIR / 'cases.json').read_text(encoding='utf-8'))
    )

    with tempfile.TemporaryDirectory(prefix='zigux_genksyms_bridge_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        for case in cases:
            mode = case.get('mode', 'stdout_json')
            c_actual = tmp_dir / f"{case['name']}.c.actual.json"
            zig_actual = tmp_dir / f"{case['name']}.zig.actual.json"
            if mode == 'process_json':
                normalize_stderr = bool(case.get('normalize_stderr', False))
                capture_run_c(tmp_dir, c_actual, compiler, case['argv'], normalize_stderr=normalize_stderr)
                capture_run_zig(zig, tmp_dir, zig_actual, case['argv'], normalize_stderr=normalize_stderr)
            elif mode == 'stdout_json':
                compile_run_c(tmp_dir, c_actual, compiler, case['argv'])
                run_zig(zig, tmp_dir, zig_actual, case['argv'])
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

    if args.refresh:
        print('GENKSYMS_BRIDGE_REFRESH=pass')
    else:
        print('GENKSYMS_BRIDGE_DIFF=pass')
    print(f'FIXTURE_DIR={FIXTURE_DIR}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
