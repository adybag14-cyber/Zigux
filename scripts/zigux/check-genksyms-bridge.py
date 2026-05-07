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
SELF_TEST_CASE_COUNT = 6


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


def load_cases(fixture_dir: Path) -> dict[str, object]:
    return json.loads((fixture_dir / 'cases.json').read_text(encoding='utf-8'))


def load_manifest(fixture_dir: Path) -> dict[str, object]:
    payload = json.loads((fixture_dir / 'manifest.json').read_text(encoding='utf-8'))
    if not isinstance(payload, dict):
        raise ValueError('genksyms bridge manifest must be a JSON object')
    return payload


def dedup_append(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def collect_expected_packets(
    cases_payload: dict[str, object],
    *,
    fixture_dir: Path,
) -> tuple[list[str], list[str], list[str], list[str], list[str], list[tuple[str, str]]]:
    issues: list[tuple[str, str]] = []
    supported_modes = {'stdout_json', 'process_json'}
    seen_names: set[str] = set()
    case_names: list[str] = []
    stdout_packet: list[str] = []
    process_packet: list[str] = []
    normalized_stderr_packet: list[str] = []
    action_abbrev_cases: list[str] = []

    for case in cases_payload['cases']:
        name = case['name']
        if name in seen_names:
            issues.append(('DUPLICATE_GENKSYMS_BRIDGE_CASE_NAMES', name))
        else:
            seen_names.add(name)
            case_names.append(name)

        mode = case.get('mode', 'stdout_json')
        if mode not in supported_modes:
            issues.append(('UNSUPPORTED_GENKSYMS_BRIDGE_CASE_MODES', f'{name}:{mode}'))
            continue

        expected = case.get('expected')
        if expected and not (fixture_dir / expected).exists():
            issues.append(('MISSING_GENKSYMS_BRIDGE_EXPECTED_PATHS', f'{name}:{expected}'))
            continue
        if not expected:
            continue

        if mode == 'stdout_json':
            dedup_append(stdout_packet, expected)
        else:
            dedup_append(process_packet, expected)
            if case.get('normalize_stderr', False):
                dedup_append(normalized_stderr_packet, expected)
            if name.startswith('abbreviated_'):
                action_abbrev_cases.append(name)

    return (
        case_names,
        stdout_packet,
        process_packet,
        normalized_stderr_packet,
        action_abbrev_cases,
        issues,
    )


def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    fixture_dir = root / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge'
    cases_payload = load_cases(fixture_dir)
    (
        case_names,
        stdout_packet,
        process_packet,
        normalized_stderr_packet,
        action_abbrev_cases,
        issues,
    ) = collect_expected_packets(cases_payload, fixture_dir=fixture_dir)

    manifest_path = fixture_dir / 'manifest.json'
    if not manifest_path.exists():
        issues.append(('MISSING_GENKSYMS_BRIDGE_MANIFEST_PATHS', 'manifest.json'))
        return issues

    try:
        manifest = load_manifest(fixture_dir)
    except (json.JSONDecodeError, ValueError) as exc:
        issues.append(('INVALID_GENKSYMS_BRIDGE_MANIFEST', str(exc)))
        return issues

    expected_scalars = {
        'tool': 'scripts/zigux/genksyms.zig',
        'status': 'closed',
        'mode': 'wrapper-first bridge',
        'fixture_root': 'zigux/tests/fixtures/genksyms_bridge',
        'fixture_case_source': 'zigux/tests/fixtures/genksyms_bridge/cases.json',
        'harness': 'zigux/tests/fixtures/genksyms_bridge/genksyms_bridge_c_harness.c',
        'case_count': len(case_names),
    }
    for field, expected in expected_scalars.items():
        actual = manifest.get(field)
        if actual != expected:
            issues.append(
                (
                    'GENKSYMS_BRIDGE_MANIFEST_DRIFT',
                    f'{field}:expected={expected!r}:actual={actual!r}',
                )
            )

    expected_lists = {
        'cases': case_names,
        'stdout_packet': stdout_packet,
        'process_packet': process_packet,
        'normalized_stderr_packet': normalized_stderr_packet,
        'action_abbrev_cases': action_abbrev_cases,
    }
    for field, expected in expected_lists.items():
        actual = manifest.get(field)
        if actual != expected:
            issues.append(
                (
                    'GENKSYMS_BRIDGE_MANIFEST_DRIFT',
                    f'{field}:expected={expected!r}:actual={actual!r}',
                )
            )

    return issues


def emit_manifest_issues(issues: list[tuple[str, str]]) -> None:
    grouped: dict[str, list[str]] = {}
    for block, value in issues:
        grouped.setdefault(block, []).append(value)

    print('GENKSYMS_BRIDGE_DIFF=fail')
    for block, values in grouped.items():
        print(f'{block}_START')
        for value in values:
            print(value)
        print(f'{block}_END')
    raise SystemExit(1)


def success_lines(*, refresh: bool) -> list[str]:
    lines: list[str] = []
    if refresh:
        lines.append('GENKSYMS_BRIDGE_REFRESH=pass')
    else:
        lines.append('GENKSYMS_BRIDGE_DIFF=pass')
        lines.append('GENKSYMS_BRIDGE_DETERMINISM=pass')
    lines.append(f'FIXTURE_DIR={FIXTURE_DIR}')
    return lines


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
        re.compile(r"^.+: (option '--.+?' is ambiguous)(?:; possibilities: .+)?$"),
        re.compile(r"^.+: (unrecognized option '.+')$"),
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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def build_self_test_root(root: Path) -> None:
    write_text(
        root / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'cases.json',
        json.dumps(
            {
                'cases': [
                    {
                        'name': 'minimal',
                        'argv': [],
                        'expected': 'minimal_expected.json',
                    },
                    {
                        'name': 'invalid_short_opt',
                        'argv': ['-Z'],
                        'mode': 'process_json',
                        'normalize_stderr': True,
                        'expected': 'invalid_short_opt_expected.json',
                    },
                    {
                        'name': 'abbreviated_help',
                        'argv': ['--hel'],
                        'mode': 'process_json',
                        'expected': 'help_expected.json',
                    },
                ]
            },
            indent=2,
        )
        + '\n',
    )
    write_text(root / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'minimal_expected.json', '{}\n')
    write_text(root / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'invalid_short_opt_expected.json', '{}\n')
    write_text(root / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'help_expected.json', '{}\n')
    write_text(
        root / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'manifest.json',
        json.dumps(
            {
                'tool': 'scripts/zigux/genksyms.zig',
                'status': 'closed',
                'mode': 'wrapper-first bridge',
                'fixture_root': 'zigux/tests/fixtures/genksyms_bridge',
                'fixture_case_source': 'zigux/tests/fixtures/genksyms_bridge/cases.json',
                'harness': 'zigux/tests/fixtures/genksyms_bridge/genksyms_bridge_c_harness.c',
                'case_count': 3,
                'cases': ['minimal', 'invalid_short_opt', 'abbreviated_help'],
                'stdout_packet': ['minimal_expected.json'],
                'process_packet': ['invalid_short_opt_expected.json', 'help_expected.json'],
                'normalized_stderr_packet': ['invalid_short_opt_expected.json'],
                'action_abbrev_cases': ['abbreviated_help'],
            },
            indent=2,
        )
        + '\n',
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix='zigux_genksyms_bridge_selftest_') as tmp_dir_str:
        root = Path(tmp_dir_str)
        build_self_test_root(root)
        assert collect_manifest_issues(root) == []

        build_self_test_root(root)
        cases_path = root / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'cases.json'
        payload = json.loads(cases_path.read_text(encoding='utf-8'))
        payload['cases'][0]['mode'] = 'yaml'
        write_text(cases_path, json.dumps(payload, indent=2) + '\n')
        issues = collect_manifest_issues(root)
        assert ('UNSUPPORTED_GENKSYMS_BRIDGE_CASE_MODES', 'minimal:yaml') in issues

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding='utf-8'))
        payload['cases'][1]['name'] = 'minimal'
        write_text(cases_path, json.dumps(payload, indent=2) + '\n')
        issues = collect_manifest_issues(root)
        assert ('DUPLICATE_GENKSYMS_BRIDGE_CASE_NAMES', 'minimal') in issues
        assert any(block == 'GENKSYMS_BRIDGE_MANIFEST_DRIFT' and 'cases:' in value for block, value in issues)

        build_self_test_root(root)
        missing_path = root / 'zigux' / 'tests' / 'fixtures' / 'genksyms_bridge' / 'invalid_short_opt_expected.json'
        missing_path.unlink()
        issues = collect_manifest_issues(root)
        assert ('MISSING_GENKSYMS_BRIDGE_EXPECTED_PATHS', 'invalid_short_opt:invalid_short_opt_expected.json') in issues
        assert any(block == 'GENKSYMS_BRIDGE_MANIFEST_DRIFT' and 'process_packet:' in value for block, value in issues)

        # Keep the count aligned to grouped stderr-normalization contract coverage.
        assert normalize_cli_stderr("genksyms: option '--reference' requires an argument\n") == "option '--reference' requires an argument\n"
        assert normalize_cli_stderr("genksyms: option '--help' doesn't allow an argument\n") == "option '--help' doesn't allow an argument\n"
        assert normalize_cli_stderr("genksyms: option '--du' is ambiguous; possibilities: '--dump' '--dump-types'\n") == "option '--du' is ambiguous\n"

        # Keep the count aligned to grouped success-marker contract coverage.
        assert success_lines(refresh=False)[:2] == [
            'GENKSYMS_BRIDGE_DIFF=pass',
            'GENKSYMS_BRIDGE_DETERMINISM=pass',
        ]
        assert success_lines(refresh=True)[0] == 'GENKSYMS_BRIDGE_REFRESH=pass'
        assert 'GENKSYMS_BRIDGE_DETERMINISM=pass' not in success_lines(refresh=True)

    print('GENKSYMS_BRIDGE_SELF_TEST=pass')
    print(f'GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Check bounded genksyms bridge parity.')
    parser.add_argument('--cc', help='C compiler to use')
    parser.add_argument('--zig', help='Path to Zig executable')
    parser.add_argument('--refresh', action='store_true', help='Refresh the committed expected fixtures from the C harness')
    parser.add_argument(
        '--self-test',
        action='store_true',
        help='Run built-in manifest coverage without compiling the bridge tools.',
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_manifest_issues(ROOT)
    if issues:
        emit_manifest_issues(issues)

    compiler = args.cc or os.environ.get('CC') or ('gcc' if os.name == 'nt' and shutil.which('wsl') else find_compiler(None))
    zig = find_zig(args.zig)
    cases = load_cases(FIXTURE_DIR)

    with tempfile.TemporaryDirectory(prefix='zigux_genksyms_bridge_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        for case in cases['cases']:
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

    for line in success_lines(refresh=args.refresh):
        print(line)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())