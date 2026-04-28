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
    'PHASE1_BITMAP_REVIEW=bitmap scnprintf parity covers contiguous-range rendering, empty-bitmap buffer preservation, and truncation that preserves the terminator slot',
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
    'PHASE1_STRING_REVIEW=string parity covers bool parsing, bounded strlcpy, whitespace cleanup, replacement, and memchrInv mismatch detection',
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
find_bit_review = manifest.get('helper_review_notes', {}).get('tools/lib/find_bit.zig', {})
rbtree_review = manifest.get('helper_review_notes', {}).get('tools/lib/rbtree.zig', {})
string_review = manifest.get('helper_review_notes', {}).get('tools/lib/string.zig', {})
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
    'bitmap.scnprintf_empty_len',
    'bitmap.scnprintf_empty_bytes',
    'bitmap.scnprintf_trunc_len',
    'bitmap.scnprintf_trunc',
]:
    missing_markers.append('manifest:bitmap.evidence_keys')
if bitmap_review.get('summary') != 'Committed C-backed parity coverage includes contiguous-range rendering, the empty-bitmap buffer-preservation contract, and truncation behavior that preserves the trailing terminator slot.':
    missing_markers.append('manifest:bitmap.summary')
if bitmap_review.get('unit_test_anchor') != 'tools/lib/bitmap.zig:test "bitmap xor across a multiword tail still lets callers clamp the last word"':
    missing_markers.append('manifest:bitmap.unit_test_anchor')
if bitmap_review.get('unit_test_contract') != 'Direct Zig unit coverage keeps multiword-tail xor behavior aligned so callers can clamp the last word after xorBits without leaking out-of-range bits into the asserted view.':
    missing_markers.append('manifest:bitmap.unit_test_contract')
if find_bit_review.get('fixture') != 'zigux/tests/fixtures/phase1_helpers.json':
    missing_markers.append('manifest:find_bit.fixture=zigux/tests/fixtures/phase1_helpers.json')
if find_bit_review.get('evidence_keys') != [
    'find_bit.first',
    'find_bit.next_after_6',
    'find_bit.next_after_word',
    'find_bit.first_zero',
    'find_bit.next_zero',
    'find_bit.first_and',
    'find_bit.next_and',
    'find_bit.tail_clamped_first',
    'find_bit.tail_clamped_next',
    'find_bit.tail_zero_clamped_first',
    'find_bit.tail_zero_clamped_next',
    'find_bit.tail_and_clamped_first',
    'find_bit.tail_and_clamped_next',
    'find_bit.tail_and_mixed_first',
    'find_bit.tail_and_mixed_next',
]:
    missing_markers.append('manifest:find_bit.evidence_keys')
if find_bit_review.get('summary') != 'Committed C-backed parity coverage includes baseline set, zero, and shared-bit scans plus tail-clamped set, zero, and AND searches, including the mixed-tail case where one shared bit remains in range while another lives past nbits.':
    missing_markers.append('manifest:find_bit.summary')
if find_bit_review.get('unit_test_anchor') != 'tools/lib/find_bit.zig:test "find next zero bit skips earlier matches in the same word"':
    missing_markers.append('manifest:find_bit.unit_test_anchor')
if find_bit_review.get('unit_test_contract') != 'Direct Zig unit coverage keeps same-word zero-scan start masking aligned so inclusive starts can return the current zero, later starts skip earlier same-word zeros, and tail scans still clamp to nbits.':
    missing_markers.append('manifest:find_bit.unit_test_contract')
if rbtree_review.get('fixture') != 'zigux/tests/fixtures/phase1_helpers.json':
    missing_markers.append('manifest:rbtree.fixture=zigux/tests/fixtures/phase1_helpers.json')
if rbtree_review.get('evidence_keys') != [
    'rbtree.empty_root',
    'rbtree.insert_order',
    'rbtree.reverse_order',
    'rbtree.replace_order',
    'rbtree.erase_init_order',
    'rbtree.postorder_count',
    'rbtree.erase_init_node_empty',
    'rbtree.cleared_node_empty',
]:
    missing_markers.append('manifest:rbtree.evidence_keys')
if rbtree_review.get('summary') != 'Committed C-backed parity coverage includes ordered forward and reverse traversal plus replaceNode, eraseInit, postorder traversal, and detached-node state checks.':
    missing_markers.append('manifest:rbtree.summary')
if rbtree_review.get('unit_test_anchor') != 'tools/lib/rbtree.zig:test "rbtree findAdd keeps the first duplicate and inserts new keys"':
    missing_markers.append('manifest:rbtree.unit_test_anchor')
if rbtree_review.get('unit_test_contract') != 'Direct Zig unit coverage keeps findAdd duplicate handling aligned so the first equal key stays resident while new distinct keys still link into the tree.':
    missing_markers.append('manifest:rbtree.unit_test_contract')
if rbtree_review.get('search_unit_test_anchor') != 'tools/lib/rbtree.zig:test "rbtree nextMatch walks the duplicate range in order"':
    missing_markers.append('manifest:rbtree.search_unit_test_anchor')
if rbtree_review.get('search_unit_test_contract') != 'Direct Zig unit coverage keeps find(), findFirst(), and nextMatch() aligned so duplicate-key lookups start at the leftmost match and walk through the final equal node without drifting into a later key.':
    missing_markers.append('manifest:rbtree.search_unit_test_contract')
if rbtree_review.get('cached_unit_test_anchor') != 'tools/lib/rbtree.zig:test "rbtree cached root keeps leftmost in sync across add erase and replace"':
    missing_markers.append('manifest:rbtree.cached_unit_test_anchor')
if rbtree_review.get('cached_unit_test_contract') != 'Direct Zig unit coverage keeps RootCached leftmost tracking aligned so addCached(), eraseCached(), and replaceNodeCached() continue to expose the same first node as the underlying tree root.':
    missing_markers.append('manifest:rbtree.cached_unit_test_contract')
if rbtree_review.get('iterator_unit_test_anchor') != 'tools/lib/rbtree.zig:test "rbtree iterateMatches streams only the duplicate range"':
    missing_markers.append('manifest:rbtree.iterator_unit_test_anchor')
if rbtree_review.get('iterator_unit_test_contract') != 'Direct Zig unit coverage keeps iterateMatches() aligned so duplicate-key iteration yields only the equal-key range and cleanly reports no match for missing keys.':
    missing_markers.append('manifest:rbtree.iterator_unit_test_contract')
if string_review.get('fixture') != 'zigux/tests/fixtures/phase1_helpers.json':
    missing_markers.append('manifest:string.fixture=zigux/tests/fixtures/phase1_helpers.json')
if string_review.get('evidence_keys') != [
    'string.strtobool_y',
    'string.strtobool_on',
    'string.strtobool_zero',
    'string.strtobool_off',
    'string.strtobool_invalid',
    'string.strlcpy_len',
    'string.strlcpy_buffer',
    'string.skip_spaces',
    'string.trim_spaces',
    'string.remove_spaces',
    'string.replace_char',
    'string.replace_char_end',
    'string.memchr_inv_index',
    'string.memchr_inv_none',
]:
    missing_markers.append('manifest:string.evidence_keys')
if string_review.get('summary') != 'Committed C-backed parity coverage includes Linux-style bool parsing for true, false, and invalid forms, bounded strlcpy truncation, in-place whitespace and replacement helpers, and first-mismatch memchrInv detection.':
    missing_markers.append('manifest:string.summary')
if string_review.get('unit_test_anchor') != 'tools/lib/string.zig:test "memchrInv scans aligned and misaligned long buffers"':
    missing_markers.append('manifest:string.unit_test_anchor')
if string_review.get('unit_test_contract') != 'Direct Zig unit coverage keeps memchrInv honest for both aligned and misaligned long buffers beyond the short C-backed fixture cases.':
    missing_markers.append('manifest:string.unit_test_contract')
if string_review.get('alias_unit_test_anchor') != 'tools/lib/string.zig:test "trimSpaces and strim trim trailing whitespace before an embedded NUL"':
    missing_markers.append('manifest:string.alias_unit_test_anchor')
if string_review.get('alias_unit_test_contract') != 'Direct Zig unit coverage keeps trimSpaces and strim aligned with C-string semantics by trimming trailing whitespace that appears before the first embedded NUL while preserving bytes beyond that terminator.':
    missing_markers.append('manifest:string.alias_unit_test_contract')

exact_checksums = bench_expectations.get('exact_checksums', {})
loose_checksums = bench_expectations.get('checksums', [])
if exact_checksums.get('PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM') != 15621472:
    missing_markers.append('bench:exact_checksums.PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM=15621472')
if exact_checksums.get('PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM') != 17862764:
    missing_markers.append('bench:exact_checksums.PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM=17862764')
if exact_checksums.get('PHASE1_BENCH_STRING_CHECKSUM') != 100000:
    missing_markers.append('bench:exact_checksums.PHASE1_BENCH_STRING_CHECKSUM=100000')
if exact_checksums.get('PHASE1_BENCH_RBTREE_CHECKSUM') != 1308000:
    missing_markers.append('bench:exact_checksums.PHASE1_BENCH_RBTREE_CHECKSUM=1308000')
if 'PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM' in loose_checksums:
    missing_markers.append('bench:remove_loose_find_bit_checksum')
if 'PHASE1_BENCH_STRING_CHECKSUM' in loose_checksums:
    missing_markers.append('bench:remove_loose_string_checksum')
if 'PHASE1_BENCH_RBTREE_CHECKSUM' in loose_checksums:
    missing_markers.append('bench:remove_loose_rbtree_checksum')

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
