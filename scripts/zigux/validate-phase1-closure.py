#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml',
    ROOT / 'Documentation' / 'zigux' / 'phase1-closure.md',
    ROOT / 'scripts' / 'zigux' / 'artifact_diff.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase1-parity.py',
    ROOT / 'scripts' / 'zigux' / 'check-phase1-bench.py',
    ROOT / 'scripts' / 'zigux' / 'install-zig.py',
    ROOT / 'scripts' / 'zigux' / 'validate-phase1-closure.py',
    ROOT / 'zigux-alpha' / 'BOOTSTRAP_COMMIT_LEDGER.md',
    ROOT / 'zigux' / 'tests' / 'build.zig',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_bench_expectations.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helper_manifest.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helpers.json',
    ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helpers_c_harness.c',
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
    'PHASE1_BITMAP_REVIEW=bitmap parity covers allocator-backed sizing, zero-allocation state, contiguous-range rendering, empty-bitmap buffer preservation, and truncation that preserves the terminator slot',
    'bitmap direct unit-test anchor: `tools/lib/bitmap.zig:test "bitmap allocation helpers size zero fill and reset optionals"`',
    'PHASE1_BITMAP_UNIT_REVIEW=bitmap allocation helpers keep bitmapFree optional handles null after release while shared parity covers allocator-backed sizing and zero-allocation state',
    'bitmap tail-mask unit-test anchor: `tools/lib/bitmap.zig:test "bitmap tail-masked helpers ignore out-of-range differences"`',
    'PHASE1_BITMAP_TAIL_MASK_UNIT_REVIEW=bitmap tail-masked reduction helpers ignore out-of-range differences while preserving the in-range window for andBits, andNotBits, equal, intersects, and subset',
    'PHASE1_FIND_BIT_FIXTURE=zigux/tests/fixtures/phase1_helpers.json',
    'PHASE1_FIND_BIT_REVIEW=find_bit baseline set, zero, shared-bit, and tail-clamped scans ignore bits beyond nbits while preserving the in-range mixed-tail match',
    'find_bit direct unit-test anchor: `tools/lib/find_bit.zig:test "find next zero bit skips earlier matches in the same word"`',
    'PHASE1_FIND_BIT_UNIT_REVIEW=find_bit same-word zero-scan start masking keeps inclusive starts honest, skips earlier zero matches after the search advances, and still clamps tail results to nbits',
    'find_bit set unit-test anchor: `tools/lib/find_bit.zig:test "find next bit skips earlier matches in the same word"`',
    'PHASE1_FIND_BIT_SET_UNIT_REVIEW=find_bit same-word set-scan start masking keeps inclusive starts honest, skips earlier same-word set matches after the search advances, and still clamps tail results to nbits',
    'find_bit and unit-test anchor: `tools/lib/find_bit.zig:test "find next and bit skips earlier shared matches in the same word"`',
    'PHASE1_FIND_BIT_AND_UNIT_REVIEW=find_bit same-word shared-bit start masking keeps inclusive starts honest, skips earlier same-word overlaps after the search advances, and still clamps tail AND results to nbits',
    'find_bit mask unit-test anchor: `tools/lib/find_bit.zig:test "word helpers keep linux-style mask and sizing boundaries"`',
    'PHASE1_FIND_BIT_MASK_UNIT_REVIEW=find_bit mask and sizing helpers keep Linux-style whole-word, partial-word, and wrapped-start boundaries reviewable without relying only on indirect scan coverage',
    'find_bit boundary unit-test anchor: `tools/lib/find_bit.zig:test "empty and boundary scans return nbits"`',
    'PHASE1_FIND_BIT_BOUNDARY_UNIT_REVIEW=find_bit empty and out-of-range scans return nbits for zero-length bitmaps, start-at-nbits searches, and fully set zero-bit windows that must not report past the declared range',
    'PHASE1_RBTREE_FIXTURE=zigux/tests/fixtures/phase1_helpers.json',
    'PHASE1_RBTREE_REVIEW=rbtree parity covers ordered traversal, replaceNode, eraseInit, postorder traversal, and detached-node state',
    'rbtree direct unit-test anchor: `tools/lib/rbtree.zig:test "rbtree findAdd keeps the first duplicate and inserts new keys"`',
    'PHASE1_RBTREE_UNIT_REVIEW=rbtree findAdd keeps the first equal key resident while new distinct keys still link into the tree',
    'rbtree search unit-test anchor: `tools/lib/rbtree.zig:test "rbtree nextMatch walks the duplicate range in order"`',
    'PHASE1_RBTREE_SEARCH_UNIT_REVIEW=rbtree find, findFirst, and nextMatch keep duplicate-key lookup walks aligned from the leftmost match through the final equal node',
    'rbtree duplicate-search unit-test anchor: `tools/lib/rbtree.zig:test "rbtree duplicate search stays aligned after erase and same-key replace"`',
    'PHASE1_RBTREE_DUPLICATE_SEARCH_UNIT_REVIEW=rbtree duplicate-key search stays aligned after erase and same-key replace so findFirst, findLast, and duplicate-range iterators report the surviving equal-key window in both directions',
    'rbtree cached-root unit-test anchor: `tools/lib/rbtree.zig:test "rbtree cached root keeps leftmost in sync across add erase and replace"`',
    'PHASE1_RBTREE_CACHED_UNIT_REVIEW=rbtree RootCached leftmost tracking stays aligned across addCached, eraseCached, and replaceNodeCached so the cached first node matches the underlying tree root',
    'rbtree cached duplicate-minima unit-test anchor: `tools/lib/rbtree.zig:test "rbtree cached root tracks duplicate minima through erase and non-leftmost replace"`',
    'PHASE1_RBTREE_CACHED_DUPLICATE_UNIT_REVIEW=rbtree RootCached duplicate minima stay aligned when eraseCached promotes the next equal-key minimum and replaceNodeCached leaves the cached first node unchanged for non-leftmost replacement',
    'rbtree iterator unit-test anchor: `tools/lib/rbtree.zig:test "rbtree iterateMatches streams only the duplicate range"`',
    'PHASE1_RBTREE_ITERATE_UNIT_REVIEW=rbtree iterateMatches yields only the equal-key duplicate range and cleanly reports no match for missing keys',
    'rbtree reverse unit-test anchor: `tools/lib/rbtree.zig:test "rbtree iterateMatchesReverse streams only the duplicate range in reverse"`',
    'PHASE1_RBTREE_REVERSE_UNIT_REVIEW=rbtree findLast, prevMatch, and iterateMatchesReverse keep reverse duplicate-key lookup walks aligned from the rightmost match back through the equal-key range while still reporting no match for missing keys',
    'PHASE1_STRING_FIXTURE=zigux/tests/fixtures/phase1_helpers.json',
    'PHASE1_STRING_REVIEW=string parity covers Linux-style bool parsing for true, false, and invalid forms, C-string-aware strlcpy length and truncation behavior, whitespace cleanup including embedded-NUL remove_spaces handling, replacement, and memchrInv mismatch detection',
    'string c-string unit-test anchor: `tools/lib/string.zig:test "strlcpy stops at the first embedded NUL in the source"`',
    'PHASE1_STRING_CSTRING_UNIT_REVIEW=string strlcpy stops at the first embedded NUL, preserves truncation behavior, and leaves zero-sized destinations untouched',
    'string equality unit-test anchor: `tools/lib/string.zig:test "streq matches C-string equality semantics"`',
    'PHASE1_STRING_EQUALITY_UNIT_REVIEW=string strEq and streq keep C-string equality aligned for exact, empty, length-mismatched, case-sensitive, and embedded-NUL comparisons',
    'string direct unit-test anchor: `tools/lib/string.zig:test "memchrInv scans aligned and misaligned long buffers"`',
    'PHASE1_STRING_UNIT_REVIEW=string memchrInv aligned and misaligned long-buffer scans stay consistent beyond the short C-backed fixture cases',
    'string alias unit-test anchor: `tools/lib/string.zig:test "trimSpaces and strim trim trailing whitespace before an embedded NUL"`',
    'PHASE1_STRING_ALIAS_UNIT_REVIEW=string trimSpaces and strim trim trailing whitespace before the first embedded NUL while preserving bytes beyond that terminator',
    'string prefix unit-test anchor: `tools/lib/string.zig:test "strstarts matches kernel prefix semantics"`',
    'PHASE1_STRING_PREFIX_UNIT_REVIEW=string strStarts and strstarts keep kernel-style prefix checks aligned for exact, empty-prefix, shorter-input, and case-sensitive comparisons',
    'string prefix-length unit-test anchor: `tools/lib/string.zig:test "strHasPrefix returns the matched prefix length with C-string semantics"`',
    'PHASE1_STRING_PREFIX_LENGTH_UNIT_REVIEW=string strHasPrefix and str_has_prefix return the matched C-string prefix length for exact and embedded-NUL prefixes while rejecting mismatches and longer prefixes',
    'string suffix unit-test anchor: `tools/lib/string.zig:test "str_ends_with matches kernel suffix semantics"`',
    'PHASE1_STRING_SUFFIX_UNIT_REVIEW=string strEndsWith, str_ends_with, and strends keep kernel-style suffix checks aligned for exact, empty-suffix, shorter-input, and case-sensitive comparisons',
    'string memparse unit-test anchor: `tools/lib/string.zig:test "memparse forwards the header-level string helper surface"`',
    'PHASE1_STRING_MEMPARSE_UNIT_REVIEW=string memparse forwards decimal, hexadecimal, suffix-bearing, and invalid inputs through the shared command-line parser without changing the parsed value or rest pointer contract',
    'PHASE1_PARITY_GATE=python3 scripts/zigux/check-phase1-parity.py',
    'PHASE1_UNIT_GATE=zig build test --build-file zigux/tests/build.zig',
    'PHASE1_BENCH_GATE=zig build bench --build-file zigux/tests/build.zig',
    'PHASE1_BENCH_CHECK_GATE=python3 scripts/zigux/check-phase1-bench.py',
    'PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py',
    'PHASE1_FIND_BIT_BENCH_REVIEW=find_bit benchmark smoke pins deterministic next-bit, whole-family, tail-window, and same-word start-mask checksums so helper-local scan regressions cannot hide behind a generic positive checksum',
    'PHASE1_FIND_BIT_BENCH_KEYS=PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM,PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM,PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM,PHASE1_BENCH_FIND_SAME_WORD_CHECKSUM',
    'PHASE1_FIND_BIT_BENCH_ITERATIONS=PHASE1_BENCH_FIND_SAME_WORD_ITERATIONS',
    'PHASE1_ROLLBACK=keep C authoritative and remove failing Zig helper from test/build wiring',
]
required_workflow_markers = [
    'FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true',
    'uses: actions/checkout@v6.0.2',
    'uses: actions/setup-python@v6.2.0',
    'python3 scripts/zigux/install-zig.py --dest .zig-toolchain',
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
    'bitmap.weight',
    'bitmap.scnprintf',
    'bitmap.scnprintf_empty_len',
    'bitmap.scnprintf_empty_bytes',
    'bitmap.scnprintf_trunc_len',
    'bitmap.scnprintf_trunc',
    'bitmap.alloc_nbits',
    'bitmap.alloc_values',
    'bitmap.zalloc_nbits',
    'bitmap.zalloc_values',
    'bitmap.and_result',
    'bitmap.and_values',
    'bitmap.andnot_result',
    'bitmap.andnot_values',
    'bitmap.or_values',
    'bitmap.xor_values',
    'bitmap.copy_nbits',
    'bitmap.copy_values',
    'bitmap.partial_xor_nbits',
    'bitmap.partial_xor_masked_values',
    'bitmap.equal',
    'bitmap.intersects',
    'bitmap.subset',
    'bitmap.range_after_set',
    'bitmap.range_after_clear',
    'bitmap.full_after_fill',
    'bitmap.empty_after_zero',
]:
    missing_markers.append('manifest:bitmap.evidence_keys')
if bitmap_review.get('summary') != 'Committed C-backed parity coverage includes allocator-backed bitmap sizing, zero-allocation state, tail-sensitive bitwise and copy replay, range set and clear behavior, contiguous-range rendering, the empty-bitmap buffer-preservation contract, and truncation behavior that preserves the trailing terminator slot.':
    missing_markers.append('manifest:bitmap.summary')
if bitmap_review.get('unit_test_anchor') != 'tools/lib/bitmap.zig:test "bitmap allocation helpers size zero fill and reset optionals"':
    missing_markers.append('manifest:bitmap.unit_test_anchor')
if bitmap_review.get('unit_test_contract') != 'Direct Zig unit coverage keeps bitmapAlloc(), bitmapZalloc(), and bitmapFree() honest by proving optional bitmap handles size through bitsToWords(), zero-filled allocation stays intact, and released optionals reset to null.':
    missing_markers.append('manifest:bitmap.unit_test_contract')
if bitmap_review.get('range_unit_test_anchor') != 'tools/lib/bitmap.zig:test "bitmap range helpers preserve edges across whole-word spans"':
    missing_markers.append('manifest:bitmap.range_unit_test_anchor')
if bitmap_review.get('range_unit_test_contract') != 'Direct Zig unit coverage keeps cross-word setRange() and clearRange() aligned by preserving the first-word start mask, fully covering interior words, clamping the last word, and restoring the whole window to zero on clear.':
    missing_markers.append('manifest:bitmap.range_unit_test_contract')
if bitmap_review.get('copy_unit_test_anchor') != 'tools/lib/bitmap.zig:test "bitmap copyClearTail clears out-of-range bits in the last copied word"':
    missing_markers.append('manifest:bitmap.copy_unit_test_anchor')
if bitmap_review.get('copy_unit_test_contract') != 'Direct Zig unit coverage keeps copy() and copyClearTail() aligned by preserving copied source words while forcing tail bits above nbits back to zero in the final copied word.':
    missing_markers.append('manifest:bitmap.copy_unit_test_contract')
if bitmap_review.get('bitwise_unit_test_anchor') != 'tools/lib/bitmap.zig:test "bitmap and andnot equal intersects subset"':
    missing_markers.append('manifest:bitmap.bitwise_unit_test_anchor')
if bitmap_review.get('bitwise_unit_test_contract') != 'Direct Zig unit coverage keeps andBits(), andNotBits(), xorBits(), equal(), intersects(), and subset() aligned on the shared caller-selected bit window instead of leaking unrelated tail bits.':
    missing_markers.append('manifest:bitmap.bitwise_unit_test_contract')
if bitmap_review.get('tail_mask_unit_test_anchor') != 'tools/lib/bitmap.zig:test "bitmap tail-masked helpers ignore out-of-range differences"':
    missing_markers.append('manifest:bitmap.tail_mask_unit_test_anchor')
if bitmap_review.get('tail_mask_unit_test_contract') != 'Direct Zig unit coverage keeps andBits(), andNotBits(), equal(), intersects(), and subset() aligned by masking out-of-range tail differences while preserving the declared in-range window.':
    missing_markers.append('manifest:bitmap.tail_mask_unit_test_contract')
if bitmap_review.get('zero_bit_unit_test_anchor') != 'tools/lib/bitmap.zig:test "bitmap zero-bit helpers stay explicit no-ops"':
    missing_markers.append('manifest:bitmap.zero_bit_unit_test_anchor')
if bitmap_review.get('zero_bit_unit_test_contract') != 'Direct Zig unit coverage keeps zero-length helper calls explicit and side-effect free so zero(), fill(), copy(), copyClearTail(), orBits(), xorBits(), scans, and formatting all leave caller-owned buffers untouched when nbits is zero.':
    missing_markers.append('manifest:bitmap.zero_bit_unit_test_contract')
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
if find_bit_review.get('set_unit_test_anchor') != 'tools/lib/find_bit.zig:test "find next bit skips earlier matches in the same word"':
    missing_markers.append('manifest:find_bit.set_unit_test_anchor')
if find_bit_review.get('set_unit_test_contract') != 'Direct Zig unit coverage keeps same-word set-scan start masking aligned so inclusive starts can return the current set bit, later starts skip earlier same-word matches, and tail scans still clamp to nbits.':
    missing_markers.append('manifest:find_bit.set_unit_test_contract')
if find_bit_review.get('and_unit_test_anchor') != 'tools/lib/find_bit.zig:test "find next and bit skips earlier shared matches in the same word"':
    missing_markers.append('manifest:find_bit.and_unit_test_anchor')
if find_bit_review.get('and_unit_test_contract') != 'Direct Zig unit coverage keeps same-word shared-bit start masking aligned so inclusive starts can return the current shared bit, later starts skip earlier same-word overlaps, and tail-clamped AND scans still stop at nbits.':
    missing_markers.append('manifest:find_bit.and_unit_test_contract')
if find_bit_review.get('boundary_unit_test_anchor') != 'tools/lib/find_bit.zig:test "empty and boundary scans return nbits"':
    missing_markers.append('manifest:find_bit.boundary_unit_test_anchor')
if find_bit_review.get('boundary_unit_test_contract') != 'Direct Zig unit coverage keeps empty and out-of-range scan boundaries aligned by returning nbits for zero-length bitmaps, start-at-nbits searches, and fully set zero-bit windows that must not report past the declared range.':
    missing_markers.append('manifest:find_bit.boundary_unit_test_contract')
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
if rbtree_review.get('duplicate_search_unit_test_anchor') != 'tools/lib/rbtree.zig:test "rbtree duplicate search stays aligned after erase and same-key replace"':
    missing_markers.append('manifest:rbtree.duplicate_search_unit_test_anchor')
if rbtree_review.get('duplicate_search_unit_test_contract') != 'Direct Zig unit coverage keeps duplicate-key search aligned after erase() and same-key replaceNode() so findFirst(), findLast(), and duplicate-range iterators continue to report the surviving equal-key window in both directions.':
    missing_markers.append('manifest:rbtree.duplicate_search_unit_test_contract')
if rbtree_review.get('cached_unit_test_anchor') != 'tools/lib/rbtree.zig:test "rbtree cached root keeps leftmost in sync across add erase and replace"':
    missing_markers.append('manifest:rbtree.cached_unit_test_anchor')
if rbtree_review.get('cached_unit_test_contract') != 'Direct Zig unit coverage keeps RootCached leftmost tracking aligned so addCached(), eraseCached(), and replaceNodeCached() continue to expose the same first node as the underlying tree root.':
    missing_markers.append('manifest:rbtree.cached_unit_test_contract')
if rbtree_review.get('cached_duplicate_unit_test_anchor') != 'tools/lib/rbtree.zig:test "rbtree cached root tracks duplicate minima through erase and non-leftmost replace"':
    missing_markers.append('manifest:rbtree.cached_duplicate_unit_test_anchor')
if rbtree_review.get('cached_duplicate_unit_test_contract') != 'Direct Zig unit coverage keeps RootCached duplicate minima aligned so eraseCached() promotes the next equal-key minimum and replaceNodeCached() leaves the cached first node unchanged when a non-leftmost node is replaced.':
    missing_markers.append('manifest:rbtree.cached_duplicate_unit_test_contract')
if rbtree_review.get('iterator_unit_test_anchor') != 'tools/lib/rbtree.zig:test "rbtree iterateMatches streams only the duplicate range"':
    missing_markers.append('manifest:rbtree.iterator_unit_test_anchor')
if rbtree_review.get('iterator_unit_test_contract') != 'Direct Zig unit coverage keeps iterateMatches() aligned so duplicate-key iteration yields only the equal-key range and cleanly reports no match for missing keys.':
    missing_markers.append('manifest:rbtree.iterator_unit_test_contract')
if rbtree_review.get('reverse_unit_test_anchor') != 'tools/lib/rbtree.zig:test "rbtree iterateMatchesReverse streams only the duplicate range in reverse"':
    missing_markers.append('manifest:rbtree.reverse_unit_test_anchor')
if rbtree_review.get('reverse_unit_test_contract') != 'Direct Zig unit coverage keeps findLast(), prevMatch(), and iterateMatchesReverse() aligned so reverse duplicate-key lookups start at the rightmost match, walk back through the equal-key range, and cleanly report no match for missing keys.':
    missing_markers.append('manifest:rbtree.reverse_unit_test_contract')
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
    'string.remove_spaces_nul',
    'string.remove_spaces_nul_bytes',
    'string.replace_char',
    'string.replace_char_end',
    'string.memchr_inv_index',
    'string.memchr_inv_none',
]:
    missing_markers.append('manifest:string.evidence_keys')
if string_review.get('summary') != 'Committed C-backed parity coverage includes Linux-style bool parsing for true, false, and invalid forms, C-string-aware strlcpy length and truncation behavior, in-place whitespace and replacement helpers including embedded-NUL remove_spaces handling, and first-mismatch memchrInv detection.':
    missing_markers.append('manifest:string.summary')
if string_review.get('unit_test_anchor') != 'tools/lib/string.zig:test "memchrInv scans aligned and misaligned long buffers"':
    missing_markers.append('manifest:string.unit_test_anchor')
if string_review.get('unit_test_contract') != 'Direct Zig unit coverage keeps memchrInv honest for both aligned and misaligned long buffers beyond the short C-backed fixture cases.':
    missing_markers.append('manifest:string.unit_test_contract')
if string_review.get('cstring_unit_test_anchor') != 'tools/lib/string.zig:test "strlcpy stops at the first embedded NUL in the source"':
    missing_markers.append('manifest:string.cstring_unit_test_anchor')
if string_review.get('cstring_unit_test_contract') != 'Direct Zig unit coverage keeps strlcpy aligned with C-string semantics by stopping at the first embedded NUL, preserving truncation behavior, and leaving zero-sized destinations untouched.':
    missing_markers.append('manifest:string.cstring_unit_test_contract')
if string_review.get('equality_unit_test_anchor') != 'tools/lib/string.zig:test "streq matches C-string equality semantics"':
    missing_markers.append('manifest:string.equality_unit_test_anchor')
if string_review.get('equality_unit_test_contract') != 'Direct Zig unit coverage keeps strEq() and streq() aligned with C-string equality semantics for exact, empty, length-mismatched, case-sensitive, and embedded-NUL comparisons.':
    missing_markers.append('manifest:string.equality_unit_test_contract')
if string_review.get('alias_unit_test_anchor') != 'tools/lib/string.zig:test "trimSpaces and strim trim trailing whitespace before an embedded NUL"':
    missing_markers.append('manifest:string.alias_unit_test_anchor')
if string_review.get('alias_unit_test_contract') != 'Direct Zig unit coverage keeps trimSpaces and strim aligned with C-string semantics by trimming trailing whitespace that appears before the first embedded NUL while preserving bytes beyond that terminator.':
    missing_markers.append('manifest:string.alias_unit_test_contract')
if string_review.get('prefix_unit_test_anchor') != 'tools/lib/string.zig:test "strstarts matches kernel prefix semantics"':
    missing_markers.append('manifest:string.prefix_unit_test_anchor')
if string_review.get('prefix_unit_test_contract') != 'Direct Zig unit coverage keeps strStarts and strstarts aligned with kernel-style prefix semantics for exact, empty-prefix, shorter-input, and case-sensitive comparisons.':
    missing_markers.append('manifest:string.prefix_unit_test_contract')
if string_review.get('prefix_length_unit_test_anchor') != 'tools/lib/string.zig:test "strHasPrefix returns the matched prefix length with C-string semantics"':
    missing_markers.append('manifest:string.prefix_length_unit_test_anchor')
if string_review.get('prefix_length_unit_test_contract') != 'Direct Zig unit coverage keeps strHasPrefix and str_has_prefix aligned by returning the matched C-string prefix length for exact and embedded-NUL prefixes while rejecting mismatches and longer prefixes.':
    missing_markers.append('manifest:string.prefix_length_unit_test_contract')
if string_review.get('suffix_unit_test_anchor') != 'tools/lib/string.zig:test "str_ends_with matches kernel suffix semantics"':
    missing_markers.append('manifest:string.suffix_unit_test_anchor')
if string_review.get('suffix_unit_test_contract') != 'Direct Zig unit coverage keeps strEndsWith, str_ends_with, and strends aligned with kernel-style suffix semantics for exact, empty-suffix, shorter-input, and case-sensitive comparisons.':
    missing_markers.append('manifest:string.suffix_unit_test_contract')
if string_review.get('memparse_unit_test_anchor') != 'tools/lib/string.zig:test "memparse forwards the header-level string helper surface"':
    missing_markers.append('manifest:string.memparse_unit_test_anchor')
if string_review.get('memparse_unit_test_contract') != 'Direct Zig unit coverage keeps memparse aligned by forwarding decimal, hexadecimal, suffix-bearing, and invalid inputs through the shared command-line parser without changing the parsed value or rest pointer contract.':
    missing_markers.append('manifest:string.memparse_unit_test_contract')

exact_checksums = bench_expectations.get('exact_checksums', {})
loose_checksums = bench_expectations.get('checksums', [])
required_exact_checksums = {
    'PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM': 2260000,
    'PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM': 620000,
    'PHASE1_BENCH_BITMAP_COPY_CHECKSUM': 22040000,
    'PHASE1_BENCH_BITMAP_SCNPRINTF_CHECKSUM': 11760000,
    'PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM': 15621472,
    'PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM': 17862764,
    'PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM': 8124000,
    'PHASE1_BENCH_FIND_SAME_WORD_CHECKSUM': 2200000,
    'PHASE1_BENCH_FIND_NEXT_ZERO_BIT_CHECKSUM': 1929133,
    'PHASE1_BENCH_FIND_NEXT_AND_BIT_CHECKSUM': 1925492,
    'PHASE1_BENCH_STRING_CHECKSUM': 2500000,
    'PHASE1_BENCH_RBTREE_CHECKSUM': 1308000,
    'PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM': 1188000,
    'PHASE1_BENCH_RBTREE_CACHED_CHECKSUM': 196000,
}
required_iterations = {
    'PHASE1_BENCH_FIND_SAME_WORD_ITERATIONS': 20000,
}
for key, expected in required_iterations.items():
    if bench_expectations.get('iterations', {}).get(key) != expected:
        missing_markers.append(f'bench:iterations.{key}={expected}')
for key, expected in required_exact_checksums.items():
    if exact_checksums.get(key) != expected:
        missing_markers.append(f'bench:exact_checksums.{key}={expected}')
    if key in loose_checksums:
        missing_markers.append(f'bench:remove_loose_exact_checksum:{key}')

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
