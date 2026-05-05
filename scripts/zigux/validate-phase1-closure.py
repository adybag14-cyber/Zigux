#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_HELPERS = [
    'tools/lib/argv_split.zig',
    'tools/lib/bitmap.zig',
    'tools/lib/cmdline.zig',
    'tools/lib/ctype.zig',
    'tools/lib/find_bit.zig',
    'tools/lib/hweight.zig',
    'tools/lib/list_sort.zig',
    'tools/lib/rbtree.zig',
    'tools/lib/slab.zig',
    'tools/lib/str_error_r.zig',
    'tools/lib/string.zig',
    'tools/lib/vsprintf.zig',
    'tools/lib/zalloc.zig',
]

required_files = [
    ROOT / 'Documentation' / 'zigux' / 'phase1-closure.md',
    ROOT / 'scripts' / 'zigux' / 'check-phase1-bench.py',
    ROOT / 'scripts' / 'zigux' / 'install-zig.py',
    ROOT / 'scripts' / 'zigux' / 'validate-phase1-closure.py',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_bench_expectations.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helper_manifest.json',
    ROOT / 'zigux' / 'tests' / 'phase1_bench.zig',
]

required_closure_markers = [
    'PHASE1_STATUS=closed',
    'PHASE1_HELPER_COUNT=13',
    'manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`',
    'PHASE1_PARITY_GATE=python3 scripts/zigux/check-phase1-parity.py',
    'PHASE1_UNIT_GATE=zig build test --build-file zigux/tests/build.zig',
    'PHASE1_BENCH_GATE=zig build bench --build-file zigux/tests/build.zig',
    'PHASE1_BENCH_CHECK_GATE=python3 scripts/zigux/check-phase1-bench.py',
    'PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py',
    'PHASE1_ROLLBACK=keep C authoritative and remove failing Zig helper from test/build wiring',
]
required_workflow_markers = [
    'FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true',
    'uses: actions/checkout@v6.0.2',
    'uses: actions/setup-python@v6.2.0',
    'python3 scripts/zigux/install-zig.py --channel master --dest .zig-toolchain',
    'run: zig version',
    'python3 scripts/zigux/validate-phase1-closure.py',
    'python3 scripts/zigux/check-phase1-bench.py',
    'zig build bench --build-file zigux/tests/build.zig',
]
required_build_markers = [
    'phase1_bench.zig',
    'const bench_step = b.step("bench", "Run Phase 1 helper benchmark smoke");',
]
required_ledger_markers = [
    'docs(zigux): close bounded phase-1 helper tranche',
]


def collect_manifest_markers(manifest: object, root: Path) -> list[str]:
    missing_markers: list[str] = []
    if not isinstance(manifest, dict):
        return ['manifest:json_object']

    manifest_helpers = manifest.get('helpers')
    if not isinstance(manifest_helpers, list):
        return ['manifest:helpers=list']

    manifest_count = manifest.get('helper_count')
    if manifest.get('phase') != 'Phase 1':
        missing_markers.append('manifest:phase=Phase 1')
    if manifest.get('status') != 'closed':
        missing_markers.append('manifest:status=closed')
    if manifest_count != len(EXPECTED_HELPERS):
        missing_markers.append(f'manifest:helper_count={len(EXPECTED_HELPERS)}')
    if len(manifest_helpers) != len(EXPECTED_HELPERS):
        missing_markers.append(f'manifest:helpers_len={len(manifest_helpers)}')

    seen: set[str] = set()
    duplicates: list[str] = []
    string_helpers: list[str] = []
    for rel in manifest_helpers:
        if not isinstance(rel, str):
            missing_markers.append('manifest:helper_path_type=str')
            continue
        string_helpers.append(rel)
        if rel in seen and rel not in duplicates:
            duplicates.append(rel)
        seen.add(rel)
        if not (root / rel).exists():
            missing_markers.append(f'manifest_file:{rel}')

    expected = set(EXPECTED_HELPERS)
    actual = set(string_helpers)
    for rel in sorted(expected - actual):
        missing_markers.append(f'manifest:missing_helper={rel}')
    for rel in sorted(actual - expected):
        missing_markers.append(f'manifest:unexpected_helper={rel}')
    for rel in duplicates:
        missing_markers.append(f'manifest:duplicate_helper={rel}')

    return missing_markers


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix='zigux_phase1_closure_') as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        for rel in EXPECTED_HELPERS:
            path = tmp_root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('// fixture\n', encoding='utf-8')

        valid_manifest = {
            'phase': 'Phase 1',
            'status': 'closed',
            'helper_count': len(EXPECTED_HELPERS),
            'helpers': EXPECTED_HELPERS,
        }
        duplicate_manifest = {
            'phase': 'Phase 1',
            'status': 'closed',
            'helper_count': len(EXPECTED_HELPERS),
            'helpers': EXPECTED_HELPERS[:-1] + [EXPECTED_HELPERS[0]],
        }

        assert collect_manifest_markers(valid_manifest, tmp_root) == []
        duplicate_markers = collect_manifest_markers(duplicate_manifest, tmp_root)
        assert f'manifest:duplicate_helper={EXPECTED_HELPERS[0]}' in duplicate_markers
        assert f'manifest:missing_helper={EXPECTED_HELPERS[-1]}' in duplicate_markers

    print('PHASE1_CLOSURE_VALIDATOR_SELF_TEST=pass')
    print('PHASE1_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT=2')


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate the bounded Phase 1 closure packet.')
    parser.add_argument('--self-test', action='store_true', help='Run validator self-test cases without reading repo files.')
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
    if missing:
        print('PHASE1_CLOSURE_VALIDATION=fail')
        print('MISSING_PHASE1_CLOSURE_FILES_START')
        for item in missing:
            print(item)
        print('MISSING_PHASE1_CLOSURE_FILES_END')
        return 1

    closure = (ROOT / 'Documentation' / 'zigux' / 'phase1-closure.md').read_text(encoding='utf-8')
    workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
    tests_build = (ROOT / 'zigux' / 'tests' / 'build.zig').read_text(encoding='utf-8')
    ledger = (ROOT / 'zigux-alpha' / 'BOOTSTRAP_COMMIT_LEDGER.md').read_text(encoding='utf-8')
    manifest = json.loads((ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helper_manifest.json').read_text(encoding='utf-8'))

    missing_markers = []
    for marker in required_closure_markers:
        if marker not in closure:
            missing_markers.append(f'closure:{marker}')
    for marker in required_workflow_markers:
        if marker not in workflow:
            missing_markers.append(f'workflow:{marker}')
    for marker in required_build_markers:
        if marker not in tests_build:
            missing_markers.append(f'build:{marker}')
    for marker in required_ledger_markers:
        if marker not in ledger:
            missing_markers.append(f'ledger:{marker}')

    if 'mlugg/setup-zig@' in workflow:
        missing_markers.append('workflow:remove mlugg/setup-zig@')

    missing_markers.extend(collect_manifest_markers(manifest, ROOT))

    if missing_markers:
        print('PHASE1_CLOSURE_VALIDATION=fail')
        print('MISSING_PHASE1_CLOSURE_MARKERS_START')
        for marker in missing_markers:
            print(marker)
        print('MISSING_PHASE1_CLOSURE_MARKERS_END')
        return 1

    print('PHASE1_CLOSURE_VALIDATION=pass')
    print(f'PHASE1_CLOSURE_REQUIRED_FILE_COUNT={len(required_files)}')
    print(f'PHASE1_CLOSURE_REQUIRED_MARKER_COUNT={len(required_closure_markers) + len(required_workflow_markers) + len(required_build_markers) + len(required_ledger_markers)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
