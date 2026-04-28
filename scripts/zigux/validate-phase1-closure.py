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
bench_expectations = json.loads((ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_bench_expectations.json').read_text(encoding='utf-8'))

required_closure_markers = [
    'PHASE1_STATUS=closed',
    'PHASE1_HELPER_COUNT=13',
    'manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`',
    'PHASE1_BITMAP_FIXTURE=zigux/tests/fixtures/phase1_helpers.json',
    'bitmap empty-bitmap review note: `bitmap_scnprintf` must leave a non-empty caller buffer untouched when no bits are set, matching the C helper contract',
    'PHASE1_BITMAP_REVIEW=bitmap parity covers contiguous-range rendering, partial-word copy without clearing words beyond nbits, empty-bitmap buffer preservation, and truncation that preserves the terminator slot',
    'bitmap direct unit-test anchor: `tools/lib/bitmap.zig:test "bitmap xor across a multiword tail still lets callers clamp the last word"`',
    'PHASE1_BITMAP_UNIT_REVIEW=bitmap multiword-tail xorBits behavior still lets callers clamp the last word without leaking out-of-range bits into the asserted view',
    'PHASE1_FIND_BIT_FIXTURE=zigux/tests/fixtures/phase1_helpers.json',
    'PHASE1_FIND_BIT_REVIEW=find_bit baseline set, zero, shared-bit, and tail-clamped scans ignore bits beyond nbits while preserving the in-range mixed-tail match',
    'find_bit direct unit-test anchor: `tools/lib/find_bit.zig:test "find next zero bit skips earlier matches in the same word"`',
    'PHASE1_FIND_BIT_UNIT_REVIEW=find_bit same-word zero-scan start masking keeps inclusive starts honest, skips earlier zero matches after the search advances, and still clamps tail results to nbits',
    'PHASE1_RBTREE_FIXTURE=zigux/tests/fixtures/phase1_helpers.json',
    'PHASE1_RBTREE_REVIEW=rbtree parity covers ordered traversal, replaceNode, eraseInit, postorder traversal, and detached-node state',
    'rbtree direct unit-test anchor: `tools/lib/rbtree.zig:test "rbtree findAdd keeps the first duplicate and inserts new keys"`',
    'PHASE1_RBTREE_UNIT_REVIEW=rbtree findAdd keeps the first equal key resident while new distinct keys still link into the tree',
    'rbtree search unit-test anchor: `tools/lib/rbtree.zig:test "rbtree nextMatch walks the duplicate range in order"`',
    'PHASE1_RBTREE_SEARCH_UNIT_REVIEW=rbtree find, findFirst, and nextMatch keep duplicate-key lookup walks aligned from the leftmost match through the final equal node',
    'rbtree cached-root unit-test anchor: `tools/lib/rbtree.zig:test "rbtree cached root keeps leftmost in sync across add erase and replace"`',
    'PHASE1_RBTREE_CACHED_UNIT_REVIEW=rbtree RootCached leftmost tracking stays aligned across addCached, eraseCached, and replaceNodeCached so the cached first node matches the underlying tree root',
    'rbtree iterator unit-test anchor: `tools/lib/rbtree.zig:test "rbtree iterateMatches streams only the duplicate range"`',
    'PHASE1_RBTREE_ITERATE_UNIT_REVIEW=rbtree iterateMatches yields only the equal-key duplicate range and cleanly reports no match for missing keys',
    'PHASE1_STRING_FIXTURE=zigux/tests/fixtures/phase1_helpers.json',
    'PHASE1_STRING_REVIEW=string parity covers true, false, and invalid bool parsing, bounded strlcpy, whitespace cleanup, replacement, and memchrInv mismatch detection',
    'string direct unit-test anchor: `tools/lib/string.zig:test "memchrInv scans aligned and misaligned long buffers"`',
    'PHASE1_STRING_UNIT_REVIEW=string memchrInv aligned and misaligned long-buffer scans stay consistent beyond the short C-backed fixture cases',
    'string alias unit-test anchor: `tools/lib/string.zig:test "trimSpaces and strim trim trailing whitespace before an embedded NUL"`',
    'PHASE1_STRING_ALIAS_UNIT_REVIEW=string trimSpaces and strim trim trailing whitespace before the first embedded NUL while preserving bytes beyond that terminator',
    'PHASE1_PARITY_GATE=python3 scripts/zigux/check-phase1-parity.py',
    'PHASE1_UNIT_GATE=zig build test --build-file zigux/tests/build.zig',
    'PHASE1_BENCH_GATE=zig build bench --build-file zigux/tests/build.zig',
    'PHASE1_BENCH_CHECK_GATE=python3 scripts/zigux/check-phase1-bench.py',
    'PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py',
    'PHASE1_ROLLBACK=keep C authoritative and remove failing Zig helper from test/build wiring',
]