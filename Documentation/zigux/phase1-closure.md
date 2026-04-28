# Phase 1 Closure

This document closes the bounded Phase 1 helper tranche for Zigux.

## Status

- `PHASE1_STATUS=closed`
- scope: bounded host-side helper ports only
- product boundary: `tools/lib/*.zig`
- authority: current Linux C behavior remains the parity source

## Closed Helper Set

The bounded Phase 1 helper set is:

- `tools/lib/argv_split.zig`
- `tools/lib/bitmap.zig`
- `tools/lib/cmdline.zig`
- `tools/lib/ctype.zig`
- `tools/lib/find_bit.zig`
- `tools/lib/hweight.zig`
- `tools/lib/list_sort.zig`
- `tools/lib/rbtree.zig`
- `tools/lib/slab.zig`
- `tools/lib/str_error_r.zig`
- `tools/lib/string.zig`
- `tools/lib/vsprintf.zig`
- `tools/lib/zalloc.zig`

- `PHASE1_HELPER_COUNT=13`
- manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`

No additional helper should be called Phase 1 work unless this document and the bootstrap validators are deliberately reopened.

## Helper Review Notes

- `tools/lib/bitmap.zig` closure includes committed C-backed parity coverage for allocator-backed bitmap sizing, zero-allocation state, contiguous-range rendering, the empty-bitmap buffer-preservation contract, and the truncation path that must preserve a trailing terminator slot.
- `tools/lib/bitmap.zig` direct Zig unit coverage now keeps `bitmapFree()` aligned by proving optional bitmap handles reset to null after release while the shared C-backed fixture covers allocator-backed sizing and zero-allocation state.
- bitmap fixture authority: `zigux/tests/fixtures/phase1_helpers.json`
- bitmap manifest review anchor: `zigux/tests/fixtures/phase1_helper_manifest.json`
- bitmap direct unit-test anchor: `tools/lib/bitmap.zig:test "bitmap allocation helpers size zero fill and reset optionals"`
- bitmap empty-bitmap review note: `bitmap_scnprintf` must leave a non-empty caller buffer untouched when no bits are set, matching the C helper contract
- bitmap allocator review note: `bitmap_alloc()` and `bitmap_zalloc()` must size partial-word bitmaps through `BITS_TO_LONGS(nbits)`, while `bitmapFree()` optional-reset behavior remains direct Zig-only coverage because the C helper frees raw pointers in place

- `PHASE1_BITMAP_FIXTURE=zigux/tests/fixtures/phase1_helpers.json`
- `PHASE1_BITMAP_REVIEW=bitmap parity covers allocator-backed sizing, zero-allocation state, contiguous-range rendering, empty-bitmap buffer preservation, and truncation that preserves the terminator slot`
- `PHASE1_BITMAP_UNIT_REVIEW=bitmap allocation helpers keep bitmapFree optional handles null after release while shared parity covers allocator-backed sizing and zero-allocation state`

- `tools/lib/find_bit.zig` closure includes committed C-backed parity coverage for baseline set, zero, and shared-bit scans plus tail-clamped set, zero, and AND searches, including the mixed-tail case where one shared bit remains in range while another lives past `nbits`.
- `tools/lib/find_bit.zig` direct Zig unit coverage now keeps same-word zero-scan start masking aligned so inclusive starts can return the current zero, later starts skip earlier same-word zeros, and tail scans still clamp to `nbits`.
- find_bit fixture authority: `zigux/tests/fixtures/phase1_helpers.json`
- find_bit manifest review anchor: `zigux/tests/fixtures/phase1_helper_manifest.json`
- find_bit direct unit-test anchor: `tools/lib/find_bit.zig:test "find next zero bit skips earlier matches in the same word"`

- `PHASE1_FIND_BIT_FIXTURE=zigux/tests/fixtures/phase1_helpers.json`
- `PHASE1_FIND_BIT_REVIEW=find_bit baseline set, zero, shared-bit, and tail-clamped scans ignore bits beyond nbits while preserving the in-range mixed-tail match`
- `PHASE1_FIND_BIT_UNIT_REVIEW=find_bit same-word zero-scan start masking keeps inclusive starts honest, skips earlier zero matches after the search advances, and still clamps tail results to nbits`

- `tools/lib/rbtree.zig` closure includes committed C-backed parity coverage for ordered forward and reverse traversal plus `replaceNode`, `eraseInit`, postorder traversal, and detached-node state checks.
- `tools/lib/rbtree.zig` direct Zig unit coverage keeps `findAdd` duplicate handling aligned so the first equal key stays resident while new distinct keys still link into the tree.
- `tools/lib/rbtree.zig` direct Zig unit coverage also keeps `find()`, `findFirst()`, and `nextMatch()` aligned so duplicate-key lookups start at the leftmost match and walk through the final equal node without drifting into a later key.
- `tools/lib/rbtree.zig` direct Zig unit coverage also keeps `RootCached` leftmost tracking aligned so cached insert, erase, and replace helpers continue to expose the same first node as the underlying tree root.
- `tools/lib/rbtree.zig` direct Zig unit coverage also keeps `iterateMatches()` aligned so duplicate-key iteration yields only the equal-key range and cleanly reports no match for missing keys.
- rbtree fixture authority: `zigux/tests/fixtures/phase1_helpers.json`
- rbtree manifest review anchor: `zigux/tests/fixtures/phase1_helper_manifest.json`
- rbtree direct unit-test anchor: `tools/lib/rbtree.zig:test "rbtree findAdd keeps the first duplicate and inserts new keys"`
- rbtree search unit-test anchor: `tools/lib/rbtree.zig:test "rbtree nextMatch walks the duplicate range in order"`
- rbtree cached-root unit-test anchor: `tools/lib/rbtree.zig:test "rbtree cached root keeps leftmost in sync across add erase and replace"`
- rbtree iterator unit-test anchor: `tools/lib/rbtree.zig:test "rbtree iterateMatches streams only the duplicate range"`

- `PHASE1_RBTREE_FIXTURE=zigux/tests/fixtures/phase1_helpers.json`
- `PHASE1_RBTREE_REVIEW=rbtree parity covers ordered traversal, replaceNode, eraseInit, postorder traversal, and detached-node state`
- `PHASE1_RBTREE_UNIT_REVIEW=rbtree findAdd keeps the first equal key resident while new distinct keys still link into the tree`
- `PHASE1_RBTREE_SEARCH_UNIT_REVIEW=rbtree find, findFirst, and nextMatch keep duplicate-key lookup walks aligned from the leftmost match through the final equal node`
- `PHASE1_RBTREE_CACHED_UNIT_REVIEW=rbtree RootCached leftmost tracking stays aligned across addCached, eraseCached, and replaceNodeCached so the cached first node matches the underlying tree root`
- `PHASE1_RBTREE_ITERATE_UNIT_REVIEW=rbtree iterateMatches yields only the equal-key duplicate range and cleanly reports no match for missing keys`

- `tools/lib/string.zig` closure includes committed C-backed parity coverage for Linux-style bool parsing, bounded `strlcpy` truncation, in-place whitespace and replacement helpers, and first-mismatch `memchrInv` detection.
- `tools/lib/string.zig` direct Zig unit coverage keeps `memchrInv` honest for both aligned and misaligned long buffers beyond the short C-backed fixture cases.
- `tools/lib/string.zig` direct Zig unit coverage also keeps `trimSpaces` and `strim` aligned with C-string semantics by trimming trailing whitespace that appears before the first embedded NUL while preserving bytes beyond that terminator.
- string fixture authority: `zigux/tests/fixtures/phase1_helpers.json`
- string manifest review anchor: `zigux/tests/fixtures/phase1_helper_manifest.json`
- string direct unit-test anchor: `tools/lib/string.zig:test "memchrInv scans aligned and misaligned long buffers"`
- string alias unit-test anchor: `tools/lib/string.zig:test "trimSpaces and strim trim trailing whitespace before an embedded NUL"`

- `PHASE1_STRING_FIXTURE=zigux/tests/fixtures/phase1_helpers.json`
- `PHASE1_STRING_REVIEW=string parity covers bool parsing, bounded strlcpy, whitespace cleanup, replacement, and memchrInv mismatch detection`
- `PHASE1_STRING_UNIT_REVIEW=string memchrInv aligned and misaligned long-buffer scans stay consistent beyond the short C-backed fixture cases`
- `PHASE1_STRING_ALIAS_UNIT_REVIEW=string trimSpaces and strim trim trailing whitespace before the first embedded NUL while preserving bytes beyond that terminator`

## Closure Gates

Phase 1 is only considered closed when all of the following are green:

1. parity gate
- `python3 scripts/zigux/check-phase1-parity.py`

2. helper unit gate
- `zig build test --build-file zigux/tests/build.zig`

3. helper benchmark smoke
- `zig build bench --build-file zigux/tests/build.zig`

4. benchmark validation
- `python3 scripts/zigux/check-phase1-bench.py`

5. closure validation
- `python3 scripts/zigux/validate-phase1-closure.py`

6. workflow viability
- the bootstrap workflow must not rely on deprecated Node 20 action execution
- the bootstrap workflow must pin current action releases where available

- `PHASE1_PARITY_GATE=python3 scripts/zigux/check-phase1-parity.py`
- `PHASE1_UNIT_GATE=zig build test --build-file zigux/tests/build.zig`
- `PHASE1_BENCH_GATE=zig build bench --build-file zigux/tests/build.zig`
- `PHASE1_BENCH_CHECK_GATE=python3 scripts/zigux/check-phase1-bench.py`
- `PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py`

## Performance Policy

Phase 1 does not enforce hard CI timing thresholds yet.

That is intentional.

Host-side helper timing is too sensitive to hosted runner drift to make nanosecond thresholds trustworthy at this stage.

Instead, Phase 1 uses:

- a benchmark smoke executable for representative helper paths
- representative bitmap smoke for weight, tail-window bitwise ops, tail-sensitive copy and `copyClearTail` replay, and range rendering
- stable checksum and iteration outputs so the benchmark cannot silently optimize away the hot loops
- machine-readable benchmark expectations in `zigux/tests/fixtures/phase1_bench_expectations.json`
- manual review of timing deltas before expanding helper scope

This is a smoke-grade performance gate, not a release-grade perf contract.

## CI Viability Policy

Phase 1 closure also requires the bootstrap workflow itself to remain viable.

That means:

- current supported GitHub Action major versions where available
- explicit opt-in to Node 24 action execution on GitHub-hosted runners
- no known dependency on the deprecated Node 20 runtime
- Zig installation through an in-repo official-download step instead of a Node 20-bound action

This is part of closure because a closed validation tranche that is about to stop executing is not actually closed.

## Rollback

Rollback owner:
- Zigux product maintainers working in `tools/lib` and `scripts/zigux`

Fallback rule:
- if a helper regresses, the Zig port is disabled from the Zigux validation/build path and current C remains authoritative

Disable path:
- remove the failing helper from `zigux/tests/build.zig`
- remove the helper from `zigux/tests/phase1_helpers.zig`
- refresh the committed parity fixture if Phase 1 scope is intentionally reduced

- `PHASE1_ROLLBACK=keep C authoritative and remove failing Zig helper from test/build wiring`

## Boundary

Phase 1 closure does not imply:

- runtime kernel helper closure
- ABI closure
- atomic or barrier substrate closure
- driver readiness
- Phase 2 toolchain closure

Phase 1 is only the bounded proof that Zig helper code can live in-tree beside Linux-owned host helper code with parity fixtures and repeatable validation.
