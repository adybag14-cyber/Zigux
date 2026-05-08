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
C_HARNESS = ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_crc' / 'genksyms_crc_c_harness.c'
ZIG_TOOL = ROOT / 'scripts' / 'zigux' / 'genksyms_crc.zig'
FIXTURE_DIR = ROOT / 'zigux' / 'tests' / 'fixtures' / 'genksyms_crc'
INPUT = FIXTURE_DIR / 'inputs.txt'
EXPECTED = FIXTURE_DIR / 'expected.json'
SELF_TEST_CASE_COUNT = 6


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


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


def required_paths(root: Path) -> list[Path]:
    return [
        root / ARTIFACT_DIFF.relative_to(ROOT),
        root / C_HARNESS.relative_to(ROOT),
        root / ZIG_TOOL.relative_to(ROOT),
        root / INPUT.relative_to(ROOT),
        root / EXPECTED.relative_to(ROOT),
    ]


def missing_required_paths(root: Path) -> list[str]:
    return [str(path.relative_to(root)) for path in required_paths(root) if not path.exists()]


def success_lines(*, refresh: bool) -> list[str]:
    if refresh:
        return [
            'GENKSYMS_CRC_REFRESH=pass',
            f'FIXTURE={EXPECTED}',
        ]
    return [
        'GENKSYMS_CRC_DIFF=pass',
        f'FIXTURE={EXPECTED}',
    ]


def windows_to_wsl(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(':').lower()
    tail = resolved.as_posix().split(':', 1)[1]
    return f'/mnt/{drive}{tail}'


def compile_run_c_wsl(tmp_dir: Path, exe: Path, actual: Path, compiler: str) -> None:
    script_path = tmp_dir / 'run_genksyms_crc_c.sh'
    lines = [
        '#!/usr/bin/env bash',
        'set -euo pipefail',
        ' '.join([
            shlex.quote(compiler),
            '-std=c11',
            '-Wall',
            '-Wextra',
            '-o',
            shlex.quote(windows_to_wsl(exe)),
            shlex.quote(windows_to_wsl(C_HARNESS)),
        ]),
        ' '.join([
            shlex.quote(windows_to_wsl(exe)),
            shlex.quote(windows_to_wsl(INPUT)),
            '>',
            shlex.quote(windows_to_wsl(actual)),
        ]),
    ]
    script_path.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    run(['wsl', 'bash', windows_to_wsl(script_path)], cwd=str(ROOT))


def compile_run_c(tmp_dir: Path, actual: Path, compiler: str) -> None:
    exe = tmp_dir / ('genksyms-crc-c.exe' if os.name == 'nt' else 'genksyms-crc-c')
    if os.name == 'nt' and shutil.which('wsl'):
        compile_run_c_wsl(tmp_dir, exe, actual, compiler)
        return
    run([compiler, '-std=c11', '-Wall', '-Wextra', '-o', str(exe), str(C_HARNESS)], cwd=str(ROOT))
    result = run([str(exe), str(INPUT)], cwd=str(ROOT), capture_output=True)
    actual.write_text(result.stdout, encoding='utf-8', newline='\n')


def run_zig(zig: str, tmp_dir: Path, actual: Path) -> None:
    exe = tmp_dir / ('genksyms-crc-zig.exe' if os.name == 'nt' else 'genksyms-crc-zig')
    run([zig, 'build-exe', str(ZIG_TOOL), '-femit-bin=' + str(exe)], cwd=str(ROOT))
    result = run([str(exe), str(INPUT)], cwd=str(ROOT), capture_output=True)
    actual.write_text(result.stdout, encoding='utf-8', newline='\n')


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def build_self_test_root(root: Path) -> None:
    write_text(root / 'scripts' / 'zigux' / 'artifact_diff.py', '# artifact diff stub\n')
    write_text(root / 'scripts' / 'zigux' / 'genksyms_crc.zig', '// zig stub\n')
    write_text(
        root / 'zigux' / 'tests' / 'fixtures' / 'genksyms_crc' / 'genksyms_crc_c_harness.c',
        'int main(void) { return 0; }\n',
    )
    write_text(root / 'zigux' / 'tests' / 'fixtures' / 'genksyms_crc' / 'inputs.txt', 'crc crc32\n')
    write_text(root / 'zigux' / 'tests' / 'fixtures' / 'genksyms_crc' / 'expected.json', '{}\n')


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix='zigux_genksyms_crc_selftest_') as tmp_dir_str:
        root = Path(tmp_dir_str)

        build_self_test_root(root)
        assert missing_required_paths(root) == []
        checks_run += 1

        build_self_test_root(root)
        (root / 'zigux' / 'tests' / 'fixtures' / 'genksyms_crc' / 'inputs.txt').unlink()
        assert missing_required_paths(root) == ['zigux/tests/fixtures/genksyms_crc/inputs.txt']
        checks_run += 1

        build_self_test_root(root)
        (root / 'zigux' / 'tests' / 'fixtures' / 'genksyms_crc' / 'expected.json').unlink()
        assert missing_required_paths(root) == ['zigux/tests/fixtures/genksyms_crc/expected.json']
        checks_run += 1

        build_self_test_root(root)
        (root / 'zigux' / 'tests' / 'fixtures' / 'genksyms_crc' / 'genksyms_crc_c_harness.c').unlink()
        assert missing_required_paths(root) == ['zigux/tests/fixtures/genksyms_crc/genksyms_crc_c_harness.c']
        checks_run += 1

        assert success_lines(refresh=False) == [
            'GENKSYMS_CRC_DIFF=pass',
            f'FIXTURE={EXPECTED}',
        ]
        checks_run += 1

        assert success_lines(refresh=True) == [
            'GENKSYMS_CRC_REFRESH=pass',
            f'FIXTURE={EXPECTED}',
        ]
        checks_run += 1

    assert checks_run == SELF_TEST_CASE_COUNT
    print('GENKSYMS_CRC_SELF_TEST=pass')
    print(f'GENKSYMS_CRC_SELF_TEST_CASE_COUNT={checks_run}')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Compare bounded genksyms CRC C and Zig outputs.')
    parser.add_argument('--cc', help='C compiler to use')
    parser.add_argument('--zig', help='Path to Zig executable')
    parser.add_argument('--refresh', action='store_true', help='Refresh the committed expected fixture from current C output')
    parser.add_argument('--self-test', action='store_true', help='Run checkout-free guard coverage for genksyms_crc fixtures and success markers')
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = missing_required_paths(ROOT)
    if missing:
        print('GENKSYMS_CRC_DIFF=fail')
        print('MISSING_GENKSYMS_CRC_FILES_START')
        for item in missing:
            print(item)
        print('MISSING_GENKSYMS_CRC_FILES_END')
        return 1

    compiler = args.cc or os.environ.get('CC') or ('gcc' if os.name == 'nt' and shutil.which('wsl') else find_compiler(None))
    zig = find_zig(args.zig)

    with tempfile.TemporaryDirectory(prefix='zigux_genksyms_crc_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        c_actual = tmp_dir / 'genksyms_crc.c.actual.json'
        zig_actual = tmp_dir / 'genksyms_crc.zig.actual.json'

        compile_run_c(tmp_dir, c_actual, compiler)
        run_zig(zig, tmp_dir, zig_actual)

        if args.refresh:
            EXPECTED.write_text(c_actual.read_text(encoding='utf-8'), encoding='utf-8', newline='\n')
            for line in success_lines(refresh=True):
                print(line)
            return 0

        diff_base = [sys.executable, str(ARTIFACT_DIFF), '--mode', 'json']
        run(diff_base + [str(EXPECTED), str(c_actual)], cwd=str(ROOT))
        run(diff_base + [str(EXPECTED), str(zig_actual)], cwd=str(ROOT))
        run(diff_base + [str(c_actual), str(zig_actual)], cwd=str(ROOT))
        for line in success_lines(refresh=False):
            print(line)
        return 0


if __name__ == '__main__':
    raise SystemExit(main())