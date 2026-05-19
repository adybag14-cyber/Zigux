#!/usr/bin/env python3
"""Guard the Lane 16 bench checker's clean success packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
BENCH_CHECKER_REL = 'scripts/zigux/check-phase1-bench.py'

REQUIRED_MARKERS = (
    'def emit_success_packet(expectations: dict[str, object]) -> int:',
    'def capture_success_packet_output(expectations: dict[str, object]) -> list[str]:',
    'print("PHASE1_BENCH_CHECK=pass")',
    "print(f\"PHASE1_BENCH_EXPECTATION_COUNT={len(expectations['checksums'])}\")",
    'success_output = capture_success_packet_output(expectations)',
    'assert success_output == [',
    '"PHASE1_BENCH_CHECK=pass",',
    'f"PHASE1_BENCH_EXPECTATION_COUNT={len(expectations[\'checksums\'])}",',
    'return emit_success_packet(expectations)',
)

SUCCESS_ASSERT_BLOCK = (
    'assert success_output == [',
    '"PHASE1_BENCH_CHECK=pass",',
    'f"PHASE1_BENCH_EXPECTATION_COUNT={len(expectations[\'checksums\'])}",',
    ']',
)

FORBIDDEN_FRAGMENTS = (
    "print(f'PHASE1_BENCH_SOURCE={PHASE1_BENCH}')",
    "print(f'PHASE1_BENCH_ZIG={zig}')",
)

FORBIDDEN_SUCCESS_BLOCK_FRAGMENTS = (
    'PHASE1_BENCH_CHECK_REASON=',
    'PHASE1_BENCH_EXPECTATIONS=',
    'BENCH_COMMAND_EXIT=',
    'BENCH_COMMAND_MISSING=',
    'EXPECTATIONS_JSON_ERROR=',
    'EXPECTATIONS_JSON_LINE=',
    'EXPECTATIONS_JSON_COLUMN=',
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def checker_path(root: Path) -> Path:
    return root / BENCH_CHECKER_REL


def collect_issues(root: Path) -> list[str]:
    path = checker_path(root)
    if not path.exists():
        return [f'missing_file:{BENCH_CHECKER_REL}']

    text = path.read_text(encoding='utf-8')
    issues: list[str] = []

    for marker in REQUIRED_MARKERS:
        count = text.count(marker)
        if count != 1:
            issues.append(f'marker_count:{marker}:expected=1:actual={count}')

    for fragment in FORBIDDEN_FRAGMENTS:
        count = text.count(fragment)
        if count != 0:
            issues.append(f'forbidden:{fragment}:actual={count}')

    if all(text.count(marker) == 1 for marker in SUCCESS_ASSERT_BLOCK[:-1]):
        success_block = extract_success_assert_block(text)
        joined_block = '\n'.join(success_block)
        block_forbidden = []
        for fragment in FORBIDDEN_SUCCESS_BLOCK_FRAGMENTS:
            count = joined_block.count(fragment)
            if count != 0:
                block_forbidden.append(f'success_block_forbidden:{fragment}:actual={count}')
        if block_forbidden:
            issues.extend(block_forbidden)
        elif success_block != list(SUCCESS_ASSERT_BLOCK):
            issues.append(f'success_assert_block:{success_block!r}')

    return issues


def write_checker(root: Path, content: str) -> None:
    path = checker_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def build_sample_checker() -> str:
    lines = [
        'def emit_success_packet(expectations: dict[str, object]) -> int:',
        'def capture_success_packet_output(expectations: dict[str, object]) -> list[str]:',
        'print("PHASE1_BENCH_CHECK=pass")',
        "print(f\"PHASE1_BENCH_EXPECTATION_COUNT={len(expectations['checksums'])}\")",
        'success_output = capture_success_packet_output(expectations)',
        'assert success_output == [',
        '"PHASE1_BENCH_CHECK=pass",',
        'f"PHASE1_BENCH_EXPECTATION_COUNT={len(expectations[\'checksums\'])}",',
        ']',
        'return emit_success_packet(expectations)',
        '',
    ]
    return '\n'.join(lines) + '\n'


def extract_success_assert_block(text: str) -> list[str]:
    block: list[str] = []
    capturing = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not capturing:
            if line == SUCCESS_ASSERT_BLOCK[0]:
                capturing = True
                block.append(line)
            continue
        block.append(line)
        if line == SUCCESS_ASSERT_BLOCK[-1]:
            return block
    return block


def expected_issue(needle: str | None, operation: str) -> str:
    if operation == 'unlink':
        return f'missing_file:{BENCH_CHECKER_REL}'
    if operation == 'remove':
        assert needle is not None
        return f'marker_count:{needle}:expected=1:actual=0'
    if operation == 'duplicate':
        assert needle is not None
        return f'marker_count:{needle}:expected=1:actual=2'
    assert operation == 'append'
    assert needle is not None
    if needle in FORBIDDEN_SUCCESS_BLOCK_FRAGMENTS:
        return f'success_block_forbidden:{needle}:actual=1'
    return f'forbidden:{needle}:actual=1'


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix='phase1-bench-success-packet-ok-') as tmpdir:
        root = Path(tmpdir)
        write_checker(root, build_sample_checker())
        issues = collect_issues(root)
        if issues:
            print('PHASE1_BENCH_SUCCESS_PACKET_SELF_TEST=fail')
            for issue in issues:
                print(issue)
            return 1

    cases: list[tuple[str | None, str | None, str]] = [(None, None, 'unlink')]
    for marker in REQUIRED_MARKERS:
        cases.append((f'remove:{marker}', marker, 'remove'))
        cases.append((f'duplicate:{marker}', marker, 'duplicate'))
    for fragment in FORBIDDEN_FRAGMENTS:
        cases.append((f'forbidden:{fragment}', fragment, 'append'))
    for fragment in FORBIDDEN_SUCCESS_BLOCK_FRAGMENTS:
        cases.append((f'success-block-forbidden:{fragment}', fragment, 'append'))

    for label, needle, operation in cases:
        with tempfile.TemporaryDirectory(prefix='phase1-bench-success-packet-case-') as tmpdir:
            root = Path(tmpdir)
            write_checker(root, build_sample_checker())
            path = checker_path(root)

            if operation == 'unlink':
                path.unlink()
            elif operation == 'remove':
                assert needle is not None
                path.write_text(
                    path.read_text(encoding='utf-8').replace(needle + '\n', '', 1),
                    encoding='utf-8',
                )
            elif operation == 'duplicate':
                assert needle is not None
                path.write_text(
                    path.read_text(encoding='utf-8').replace(needle, needle + '\n' + needle, 1),
                    encoding='utf-8',
                )
            else:
                assert needle is not None
                text = path.read_text(encoding='utf-8')
                if needle in FORBIDDEN_SUCCESS_BLOCK_FRAGMENTS:
                    text = text.replace(']\n', f'"{needle}",\n]\n', 1)
                else:
                    text = text + needle + '\n'
                path.write_text(text, encoding='utf-8')

            issues = collect_issues(root)
            if issues != [expected_issue(needle, operation)]:
                print('PHASE1_BENCH_SUCCESS_PACKET_SELF_TEST=fail')
                print(f'case={label}')
                print(f'expected={expected_issue(needle, operation)}')
                print(f'actual={issues!r}')
                return 1

    print('PHASE1_BENCH_SUCCESS_PACKET_SELF_TEST=pass')
    print(f'PHASE1_BENCH_SUCCESS_PACKET_SELF_TEST_CASE_COUNT={len(cases) + 1}')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', help='override repository root')
    parser.add_argument('--self-test', action='store_true', help='run the built-in self-test')
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(repo_root(args.root))
    if issues:
        print('PHASE1_BENCH_SUCCESS_PACKET=fail')
        for issue in issues:
            print(issue)
        return 1

    print('PHASE1_BENCH_SUCCESS_PACKET=pass')
    print(f'PHASE1_BENCH_SUCCESS_PACKET_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())