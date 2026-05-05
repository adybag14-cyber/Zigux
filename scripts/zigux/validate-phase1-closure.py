#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
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
    ROOT / 'Documentation' / 'zigux' / 'README.md',
    ROOT / 'Documentation' / 'zigux' / 'phase1-closure.md',
    ROOT / 'scripts' / 'zigux' / 'README.md',
    ROOT / 'scripts' / 'zigux' / 'check-phase1-bench.py',
    ROOT / 'scripts' / 'zigux' / 'install-zig.py',
    ROOT / 'scripts' / 'zigux' / 'validate-phase1-closure.py',
    ROOT / 'zigux' / 'Makefile',
    ROOT / 'zigux' / 'tests' / 'README.md',
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
required_makefile_markers = [
    (
        'makefile_phase1_validate_target',
        'phase1-validate:',
        1,
    ),
    (
        'makefile_phase1_validate_inventory',
        'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1.py',
        1,
    ),
    (
        'makefile_phase1_validate_closure',
        'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py',
        1,
    ),
    (
        'makefile_phase1_test_target',
        'phase1-test:',
        1,
    ),
    (
        'makefile_phase1_test_parity',
        'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-parity.py',
        1,
    ),
    (
        'makefile_phase1_test_replay',
        'cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/build.zig',
        1,
    ),
    (
        'makefile_phase1_bench_target',
        'phase1-bench:',
        1,
    ),
    (
        'makefile_phase1_bench_check',
        'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bench.py',
        1,
    ),
    (
        'makefile_phase1_bench_replay',
        'cd $(ZIGUX_ROOT) && $(ZIG) build bench --build-file zigux/tests/build.zig',
        1,
    ),
    (
        'makefile_phase1_target',
        'phase1: phase1-validate phase1-test phase1-bench',
        1,
    ),
]
required_docs_root_markers = [
    (
        'docs_root_phase1_packet',
        '- `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` keep the closed host-side helper packet reviewable through the shared helper build entrypoint and the Linux-style replay route, while `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, and `zigux/Makefile` keep the closure and validator-first contract explicit from the docs root instead of leaving the Phase 1 packet split across later review surfaces.',
        1,
    ),
]
required_scripts_readme_markers = [
    (
        'scripts_readme_phase1_packet',
        '- `Documentation/zigux/phase1-closure.md`, `zigux/Makefile`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` keep that same closed host-side helper packet reviewable through the docs-root closure record and the Linux-style replay routes instead of leaving the Phase 1 closure stack visible only through direct script and Zig commands.',
        1,
    ),
]
required_tests_readme_markers = [
    (
        'tests_readme_phase1_packet',
        '- keep the closed Phase 1 host-tools packet explicit in the tests root too: `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` should continue to keep the closed helper tranche reviewable from the tests root instead of leaving the host-tools closure stack split across the docs root and scripts root',
        1,
    ),
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


def collect_exact_count_markers(text: str, markers: list[tuple[str, str, int]]) -> list[str]:
    missing_markers: list[str] = []
    for label, marker, expected_count in markers:
        actual_count = text.count(marker)
        if actual_count != expected_count:
            missing_markers.append(f'{label}:expected={expected_count}:actual={actual_count}')
    return missing_markers


def render_marker_fixture(markers: list[tuple[str, str, int]]) -> str:
    return '\n'.join(marker for _, marker, _ in markers) + '\n'


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
        unexpected_helper = 'tools/lib/not_phase1.zig'
        unexpected_path = tmp_root / unexpected_helper
        unexpected_path.parent.mkdir(parents=True, exist_ok=True)
        unexpected_path.write_text('// out of scope fixture\n', encoding='utf-8')
        unexpected_manifest = {
            'phase': 'Phase 1',
            'status': 'closed',
            'helper_count': len(EXPECTED_HELPERS) + 1,
            'helpers': EXPECTED_HELPERS[:-1] + [unexpected_helper],
        }

        assert collect_manifest_markers(valid_manifest, tmp_root) == []
        duplicate_markers = collect_manifest_markers(duplicate_manifest, tmp_root)
        assert f'manifest:duplicate_helper={EXPECTED_HELPERS[0]}' in duplicate_markers
        assert f'manifest:missing_helper={EXPECTED_HELPERS[-1]}' in duplicate_markers
        unexpected_markers = collect_manifest_markers(unexpected_manifest, tmp_root)
        assert f'manifest:helper_count={len(EXPECTED_HELPERS)}' in unexpected_markers
        assert f'manifest:missing_helper={EXPECTED_HELPERS[-1]}' in unexpected_markers
        assert f'manifest:unexpected_helper={unexpected_helper}' in unexpected_markers

        valid_makefile = render_marker_fixture(required_makefile_markers)
        assert collect_exact_count_markers(valid_makefile, required_makefile_markers) == []

        missing_validate_target = valid_makefile.replace('phase1-validate:\n', '', 1)
        missing_validate_markers = collect_exact_count_markers(missing_validate_target, required_makefile_markers)
        assert 'makefile_phase1_validate_target:expected=1:actual=0' in missing_validate_markers

        duplicate_phase1_target = valid_makefile + 'phase1: phase1-validate phase1-test phase1-bench\n'
        duplicate_phase1_markers = collect_exact_count_markers(duplicate_phase1_target, required_makefile_markers)
        assert 'makefile_phase1_target:expected=1:actual=2' in duplicate_phase1_markers

        missing_bench_check = valid_makefile.replace(
            'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bench.py\n',
            '',
            1,
        )
        missing_bench_markers = collect_exact_count_markers(missing_bench_check, required_makefile_markers)
        assert 'makefile_phase1_bench_check:expected=1:actual=0' in missing_bench_markers

        valid_docs_root = render_marker_fixture(required_docs_root_markers)
        assert collect_exact_count_markers(valid_docs_root, required_docs_root_markers) == []
        missing_docs_root = collect_exact_count_markers('', required_docs_root_markers)
        assert 'docs_root_phase1_packet:expected=1:actual=0' in missing_docs_root

        valid_scripts_readme = render_marker_fixture(required_scripts_readme_markers)
        assert collect_exact_count_markers(valid_scripts_readme, required_scripts_readme_markers) == []
        duplicate_scripts_readme = valid_scripts_readme + valid_scripts_readme
        duplicate_scripts_markers = collect_exact_count_markers(
            duplicate_scripts_readme,
            required_scripts_readme_markers,
        )
        assert 'scripts_readme_phase1_packet:expected=1:actual=2' in duplicate_scripts_markers

        valid_tests_readme = render_marker_fixture(required_tests_readme_markers)
        assert collect_exact_count_markers(valid_tests_readme, required_tests_readme_markers) == []
        missing_tests_markers = collect_exact_count_markers('', required_tests_readme_markers)
        assert 'tests_readme_phase1_packet:expected=1:actual=0' in missing_tests_markers

    print('PHASE1_CLOSURE_VALIDATOR_SELF_TEST=pass')
    print('PHASE1_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT=9')


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

    docs_root = (ROOT / 'Documentation' / 'zigux' / 'README.md').read_text(encoding='utf-8')
    closure = (ROOT / 'Documentation' / 'zigux' / 'phase1-closure.md').read_text(encoding='utf-8')
    scripts_readme = (ROOT / 'scripts' / 'zigux' / 'README.md').read_text(encoding='utf-8')
    workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
    tests_build = (ROOT / 'zigux' / 'tests' / 'build.zig').read_text(encoding='utf-8')
    tests_readme = (ROOT / 'zigux' / 'tests' / 'README.md').read_text(encoding='utf-8')
    ledger = (ROOT / 'zigux-alpha' / 'BOOTSTRAP_COMMIT_LEDGER.md').read_text(encoding='utf-8')
    makefile = (ROOT / 'zigux' / 'Makefile').read_text(encoding='utf-8')
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
    missing_markers.extend(collect_exact_count_markers(makefile, required_makefile_markers))
    missing_markers.extend(collect_exact_count_markers(docs_root, required_docs_root_markers))
    missing_markers.extend(collect_exact_count_markers(scripts_readme, required_scripts_readme_markers))
    missing_markers.extend(collect_exact_count_markers(tests_readme, required_tests_readme_markers))

    if missing_markers:
        print('PHASE1_CLOSURE_VALIDATION=fail')
        print('MISSING_PHASE1_CLOSURE_MARKERS_START')
        for marker in missing_markers:
            print(marker)
        print('MISSING_PHASE1_CLOSURE_MARKERS_END')
        return 1

    print('PHASE1_CLOSURE_VALIDATION=pass')
    print(f'PHASE1_CLOSURE_REQUIRED_FILE_COUNT={len(required_files)}')
    print(
        'PHASE1_CLOSURE_REQUIRED_MARKER_COUNT='
        f'{len(required_closure_markers) + len(required_workflow_markers) + len(required_build_markers) + len(required_ledger_markers) + len(required_makefile_markers) + len(required_docs_root_markers) + len(required_scripts_readme_markers) + len(required_tests_readme_markers)}'
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
