#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml'
CLOSURE = ROOT / 'Documentation' / 'zigux' / 'phase2-closure.md'
MAKEFILE = ROOT / 'zigux' / 'Makefile'
BRIDGE_CHECKER = ROOT / 'scripts' / 'zigux' / 'check-genksyms-bridge.py'

WORKFLOW_MARKERS = (
    'run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test',
    'run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py',
    'run: python3 scripts/zigux/check-genksyms-bridge.py --self-test',
    'run: python3 scripts/zigux/check-genksyms-bridge.py',
)

CLOSURE_MARKERS = (
    'shared genksyms bridge selftest-alignment self-test: `python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test`',
    'shared genksyms bridge selftest-alignment gate: `python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py`',
    'direct genksyms bridge self-test: `python3 scripts/zigux/check-genksyms-bridge.py --self-test`',
    'direct genksyms bridge gate: `python3 scripts/zigux/check-genksyms-bridge.py`',
)

MAKEFILE_MARKERS = (
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test',
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py',
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test',
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py',
)

BRIDGE_CHECKER_MARKERS = (
    "print('PHASE2_GENKSYMS_BRIDGE_SELF_TEST=pass')",
    "print('GENKSYMS_BRIDGE_DETERMINISM=pass')",
)

EXACT_COUNT_CHECKS = {
    '.github/workflows/zigux-bootstrap.yml': {
        WORKFLOW_MARKERS[0]: 1,
        WORKFLOW_MARKERS[1]: 1,
        WORKFLOW_MARKERS[2]: 1,
        WORKFLOW_MARKERS[3]: 1,
    },
    'zigux/Makefile': {
        MAKEFILE_MARKERS[0]: 1,
        MAKEFILE_MARKERS[1]: 1,
        MAKEFILE_MARKERS[2]: 1,
        MAKEFILE_MARKERS[3]: 1,
    },
}

FILE_MARKERS = {
    '.github/workflows/zigux-bootstrap.yml': WORKFLOW_MARKERS,
    'Documentation/zigux/phase2-closure.md': CLOSURE_MARKERS,
    'zigux/Makefile': MAKEFILE_MARKERS,
    'scripts/zigux/check-genksyms-bridge.py': BRIDGE_CHECKER_MARKERS,
}

REQUIRED_FILES = tuple(FILE_MARKERS)


def count_occurrences(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in REQUIRED_FILES:
        path = root / rel_path
        if not path.exists():
            issues.append(f'missing_file:{rel_path}')
            continue
        text = path.read_text(encoding='utf-8')
        for marker in FILE_MARKERS[rel_path]:
            if marker not in text:
                issues.append(f'missing_marker:{rel_path}:{marker}')
        for marker, expected_count in EXACT_COUNT_CHECKS.get(rel_path, {}).items():
            count = count_occurrences(text, marker)
            if count != expected_count:
                issues.append(
                    f'exact_count:{rel_path}:{marker}:count={count}:expected={expected_count}'
                )
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def build_valid_root(root: Path) -> None:
    for rel_path, markers in FILE_MARKERS.items():
        write_text(root / rel_path, '\n'.join(markers) + '\n')


def remove_marker_once(text: str, marker: str) -> str:
    line = marker + '\n'
    if line in text:
        return text.replace(line, '', 1)
    return text.replace(marker, '', 1)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix='phase2_genksyms_alignment_') as tmp_dir:
        root = Path(tmp_dir)

        build_valid_root(root)
        assert collect_issues(root) == []
        case_count += 1

        workflow_path = root / '.github/workflows/zigux-bootstrap.yml'
        workflow_text = workflow_path.read_text(encoding='utf-8')
        workflow_path.write_text(remove_marker_once(workflow_text, WORKFLOW_MARKERS[0]), encoding='utf-8')
        issues = collect_issues(root)
        assert any(issue.startswith('missing_marker:.github/workflows/zigux-bootstrap.yml:') for issue in issues)
        case_count += 1

        build_valid_root(root)
        workflow_path = root / '.github/workflows/zigux-bootstrap.yml'
        workflow_path.write_text(
            workflow_path.read_text(encoding='utf-8') + WORKFLOW_MARKERS[2] + '\n',
            encoding='utf-8',
        )
        issues = collect_issues(root)
        assert any(
            issue == f'exact_count:.github/workflows/zigux-bootstrap.yml:{WORKFLOW_MARKERS[2]}:count=2:expected=1'
            for issue in issues
        )
        case_count += 1

        build_valid_root(root)
        makefile_path = root / 'zigux/Makefile'
        makefile_text = makefile_path.read_text(encoding='utf-8')
        makefile_path.write_text(remove_marker_once(makefile_text, MAKEFILE_MARKERS[1]), encoding='utf-8')
        issues = collect_issues(root)
        assert any(issue.startswith('exact_count:zigux/Makefile:') for issue in issues)
        case_count += 1

        build_valid_root(root)
        closure_path = root / 'Documentation/zigux/phase2-closure.md'
        closure_text = closure_path.read_text(encoding='utf-8')
        closure_path.write_text(remove_marker_once(closure_text, CLOSURE_MARKERS[2]), encoding='utf-8')
        issues = collect_issues(root)
        assert any(issue.startswith('missing_marker:Documentation/zigux/phase2-closure.md:') for issue in issues)
        case_count += 1

        build_valid_root(root)
        bridge_path = root / 'scripts/zigux/check-genksyms-bridge.py'
        bridge_text = bridge_path.read_text(encoding='utf-8')
        bridge_path.write_text(remove_marker_once(bridge_text, BRIDGE_CHECKER_MARKERS[1]), encoding='utf-8')
        issues = collect_issues(root)
        assert any(issue.startswith('missing_marker:scripts/zigux/check-genksyms-bridge.py:') for issue in issues)
        case_count += 1

        build_valid_root(root)
        (root / 'scripts/zigux/check-genksyms-bridge.py').unlink()
        issues = collect_issues(root)
        assert 'missing_file:scripts/zigux/check-genksyms-bridge.py' in issues
        case_count += 1

    expected_case_count = 7
    if case_count != expected_case_count:
        print('PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST=fail')
        print(f'PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT_ACTUAL={case_count}')
        print(f'PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT_EXPECTED={expected_case_count}')
        return 1

    print('PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST=pass')
    print(f'PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Check that the Phase 2 genksyms bridge self-test reminders stay aligned with workflow, closure, and Makefile wiring.'
    )
    parser.add_argument('--self-test', action='store_true', help='Run built-in coverage without a repo checkout.')
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(ROOT)
    if issues:
        print('PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT=fail')
        print('PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_ISSUES_START')
        for issue in issues:
            print(issue)
        print('PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_ISSUES_END')
        return 1

    marker_count = sum(len(markers) for markers in FILE_MARKERS.values())
    print('PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT=pass')
    print(f'PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_MARKER_COUNT={marker_count}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
