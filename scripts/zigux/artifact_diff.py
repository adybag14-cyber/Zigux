#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def canonical_json(path: Path):
    return json.loads(read_text(path))


def sha256_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description='Compare two artifacts in a stable mode.')
    parser.add_argument('--mode', choices=['text', 'json', 'sha256'], required=True)
    parser.add_argument('expected')
    parser.add_argument('actual')
    args = parser.parse_args()

    expected = Path(args.expected)
    actual = Path(args.actual)

    if not expected.exists() or not actual.exists():
        print('ARTIFACT_DIFF=fail')
        print(f'EXPECTED_EXISTS={expected.exists()}')
        print(f'ACTUAL_EXISTS={actual.exists()}')
        return 1

    if args.mode == 'text':
        expected_value = read_text(expected)
        actual_value = read_text(actual)
    elif args.mode == 'json':
        expected_value = canonical_json(expected)
        actual_value = canonical_json(actual)
    else:
        expected_value = sha256_digest(expected)
        actual_value = sha256_digest(actual)

    if expected_value != actual_value:
        print('ARTIFACT_DIFF=fail')
        print(f'MODE={args.mode}')
        print(f'EXPECTED={expected}')
        print(f'ACTUAL={actual}')
        if args.mode == 'sha256':
            print(f'EXPECTED_SHA256={expected_value}')
            print(f'ACTUAL_SHA256={actual_value}')
        return 1

    print('ARTIFACT_DIFF=pass')
    print(f'MODE={args.mode}')
    print(f'EXPECTED={expected}')
    print(f'ACTUAL={actual}')
    if args.mode == 'sha256':
        print(f'SHA256={expected_value}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
