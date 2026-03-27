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
CASES = json.loads((FIXTURE_DIR / 'cases.json').read_text(encoding='utf-8'))


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
    parser.add_argument('--zig', help='Explicit zig executable path to use.')
    args = parser.parse_args()

    compiler = args.cc or os.environ.get('CC') or ('gcc' if os.name == 'nt' and shutil.which('wsl') else find_compiler(None))
    zig = find_zig(args.zig)

    with tempfile.TemporaryDirectory(prefix='zigux_mkelfconfig_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        c_exe = compile_c(tmp_dir, compiler)
        zig_exe = compile_zig(tmp_dir, zig)

        for case in CASES:
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
