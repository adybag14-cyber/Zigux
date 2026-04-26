#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[2]
EXPECTATIONS = ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_bench_expectations.json'


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    zig = shutil.which('zig')
    if zig:
        return zig
    raise SystemExit('zig not found; pass --zig or add zig to PATH')


def parse_output(stdout: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line or '=' not in line:
            continue
        key, value = line.split('=', 1)
        parsed[key] = value
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description='Run and validate the bounded Phase 1 benchmark smoke output.')
    parser.add_argument('--zig', help='Path to Zig executable')
    args = parser.parse_args()

    zig = find_zig(args.zig)
    expectations = json.loads(EXPECTATIONS.read_text(encoding='utf-8'))

    result = run(
        [zig, 'build', 'bench', '--build-file', 'zigux/tests/build.zig', '-Doptimize=ReleaseSafe'],
        cwd=str(ROOT),
        capture_output=True,
    )

    parsed = parse_output(result.stdout)

    if parsed.get('PHASE1_BENCH') != expectations['status']:
        print('PHASE1_BENCH_CHECK=fail')
        print(f"EXPECTED_STATUS={expectations['status']}")
        print(f"ACTUAL_STATUS={parsed.get('PHASE1_BENCH')}")
        return 1

    missing = []
    for key, value in expectations['iterations'].items():
        actual = parsed.get(key)
        if actual is None:
            missing.append(key)
            continue
        if int(actual) != int(value):
            print('PHASE1_BENCH_CHECK=fail')
            print(f'ITERATION_MISMATCH={key}')
            print(f'EXPECTED={value}')
            print(f'ACTUAL={actual}')
            return 1

    for key, value in expectations.get('exact_checksums', {}).items():
        actual = parsed.get(key)
        if actual is None:
            missing.append(key)
            continue
        if int(actual) != int(value):
            print('PHASE1_BENCH_CHECK=fail')
            print(f'CHECKSUM_MISMATCH={key}')
            print(f'EXPECTED={value}')
            print(f'ACTUAL={actual}')
            return 1

    for key in expectations['checksums']:
        actual = parsed.get(key)
        if actual is None:
            missing.append(key)
            continue
        if int(actual) <= 0:
            print('PHASE1_BENCH_CHECK=fail')
            print(f'NONPOSITIVE_CHECKSUM={key}')
            print(f'ACTUAL={actual}')
            return 1

    if missing:
        print('PHASE1_BENCH_CHECK=fail')
        print('MISSING_PHASE1_BENCH_KEYS_START')
        for key in missing:
            print(key)
        print('MISSING_PHASE1_BENCH_KEYS_END')
        return 1

    print('PHASE1_BENCH_CHECK=pass')
    print(f'PHASE1_BENCH_EXPECTATIONS={EXPECTATIONS}')
    print(f'PHASE1_BENCH_ZIG={zig}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())