#!/usr/bin/env python3
#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / 'Documentation' / 'zigux' / 'phase1-closure.md',
    ROOT / 'scripts' / 'zigux' / 'check-phase1-bench.py',
    ROOT / 'scripts' / 'zigux' / 'install-zig.py',
    ROOT / 'scripts' / 'zigux' / 'validate-phase1-closure.py',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_bench_expectations.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helper_manifest.json',
    ROOT / 'zigux' / 'tests' / 'phase1_bench.zig',
]

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print('PHASE1_CLOSURE_VALIDATION=fail')
    print('MISSING_PHASE1_CLOSURE_FILES_START')
    for item in missing:
        print(item)
    print('MISSING_PHASE1_CLOSURE_FILES_END')
    sys.exit(1)

closure = (ROOT / 'Documentation' / 'zigux' / 'phase1-closure.md').read_text(encoding='utf-8')
workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
tests_build = (ROOT / 'zigux' / 'tests' / 'build.zig').read_text(encoding='utf-8')
ledger = (ROOT / 'zigux-alpha' / 'BOOTSTRAP_COMMIT_LEDGER.md').read_text(encoding='utf-8')
manifest = json.loads((ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helper_manifest.json').read_text(encoding='utf-8'))

required_closure_markers = [
    'PHASE1_STATUS=closed',
    'PHASE1_HELPER_COUNT=13',
    'manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`',
    'PHASE1_BITMAP_FIXTURE=zigux/tests/fixtures/phase1_helpers.json',
    'PHASE1_BITMAP_REVIEW=bitmap scnprintf truncation preserves the terminator slot',
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

manifest_helpers = manifest.get('helpers', [])
manifest_count = manifest.get('helper_count')
bitmap_review = manifest.get('helper_review_notes', {}).get('tools/lib/bitmap.zig', {})
if manifest.get('phase') != 'Phase 1':
    missing_markers.append('manifest:phase=Phase 1')
if manifest.get('status') != 'closed':
    missing_markers.append('manifest:status=closed')
if manifest_count != 13:
    missing_markers.append('manifest:helper_count=13')
if len(manifest_helpers) != 13:
    missing_markers.append(f'manifest:helpers_len={len(manifest_helpers)}')
for rel in manifest_helpers:
    if not (ROOT / rel).exists():
        missing_markers.append(f'manifest_file:{rel}')
if bitmap_review.get('fixture') != 'zigux/tests/fixtures/phase1_helpers.json':
    missing_markers.append('manifest:bitmap.fixture=zigux/tests/fixtures/phase1_helpers.json')
if bitmap_review.get('evidence_keys') != [
    'bitmap.scnprintf',
    'bitmap.scnprintf_trunc_len',
    'bitmap.scnprintf_trunc',
]:
    missing_markers.append('manifest:bitmap.evidence_keys')
if bitmap_review.get('summary') != 'Committed C-backed parity coverage includes contiguous-range rendering plus truncation behavior that preserves the trailing terminator slot.':
    missing_markers.append('manifest:bitmap.summary')

if missing_markers:
    print('PHASE1_CLOSURE_VALIDATION=fail')
    print('MISSING_PHASE1_CLOSURE_MARKERS_START')
    for marker in missing_markers:
        print(marker)
    print('MISSING_PHASE1_CLOSURE_MARKERS_END')
    sys.exit(1)

print('PHASE1_CLOSURE_VALIDATION=pass')
print(f'PHASE1_CLOSURE_REQUIRED_FILE_COUNT={len(required_files)}')
print(f'PHASE1_CLOSURE_REQUIRED_MARKER_COUNT={len(required_closure_markers) + len(required_workflow_markers) + len(required_build_markers) + len(required_ledger_markers)}')
