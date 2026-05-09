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
- `python3 scripts/zigux/install-zig.py --self-test` stays reviewable as the bounded installer-viability replay for that in-repo download step

This is part of closure because a closed validation tranche that is about to stop executing is not actually closed.

## Shared Review Packet

The closed Phase 1 host-tools packet also stays reviewable through these shared product surfaces:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-phase1-installer-review-surfaces.py`
- `scripts/zigux/validate-phase1.py`
- `scripts/zigux/validate-phase1-closure.py`
- `scripts/zigux/check-phase1-parity.py`
- `scripts/zigux/artifact_diff.py`
- `scripts/zigux/check-phase1-bench.py`
- `zigux/tests/README.md`
- `zigux/tests/build.zig`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/phase1_bench.zig`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `zigux/tests/fixtures/phase1_bench_expectations.json`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/Makefile`
- `zig build test --build-file zigux/tests/build.zig`
- `zig build bench --build-file zigux/tests/build.zig`
- `make -C zigux phase1-validate`
- `make -C zigux phase1-test`
- `make -C zigux phase1-bench`
- `make -C zigux phase1`
- `python3 scripts/zigux/install-zig.py --self-test`
- `python3 scripts/zigux/check-phase1-installer-review-surfaces.py --self-test`
- `python3 scripts/zigux/validate-phase1-closure.py`

Reviewers should treat drift across those packet summaries, the artifact-diff-backed parity replay, the committed helper and benchmark fixtures, the shared tests-root entrypoints, the bootstrap workflow replay, and the validator-first plus Linux-style replay routes as a closure regression even when the helper code itself is unchanged.

## Lane Sequencing Rule

The closed Phase 1 packet also keeps one explicit anti-overlap rule from `zigux/tests/fixtures/phase1_helper_manifest.json`:

- shared-replay parked helpers stay limited to `tools/lib/argv_split.zig`, `tools/lib/cmdline.zig`, `tools/lib/ctype.zig`, `tools/lib/hweight.zig`, `tools/lib/list_sort.zig`, `tools/lib/slab.zig`, `tools/lib/str_error_r.zig`, `tools/lib/vsprintf.zig`, and `tools/lib/zalloc.zig`
- direct helper-local follow-up anchors stay limited to `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig`

Reviewers should keep that split explicit whenever Phase 1 follow-up work reopens. Shared-replay parked helpers only reopen for packet drift, while bitmap, find_bit, rbtree, and string reopen only for their current helper-local anchors or already-committed shared fixture keys. Batching work across those two sets in one follow-up lane is a closure regression because it hides which bounded proof actually owns the reopened behavior on current `master`.

- `PHASE1_LANE_SEQUENCING_RULE=shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string reopen only for their current helper-local anchors or already-committed shared fixture keys`

## Find Bit Review Rule

For `tools/lib/find_bit.zig`, reviewers must also keep the helper-local single-word next-scan proof explicit through:

- `tools/lib/find_bit.zig`

That means `test "single-word next scans honor start masks"` stays present and review-visible whenever `findNextBit()`, `findNextZeroBit()`, or `findNextAndBit()` changes. This helper-local test is the bounded proof that one-word scans still honor caller-selected start masks instead of re-reading earlier bits.

- `PHASE1_FIND_BIT_SINGLE_WORD_REVIEW=helper-local single-word next-scan proof stays explicit through the direct find_bit test anchor because the shared Phase 1 parity fixture does not isolate same-word start-mask behavior`

For `tools/lib/find_bit.zig`, reviewers must also keep the helper-local inclusive boundary proof explicit through:

- `tools/lib/find_bit.zig`

That means `test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"` stays present and review-visible whenever `findNextBit()`, `findNextZeroBit()`, or `findNextAndBit()` changes. This helper-local test is the bounded proof that same-word next scans still keep the last live head-word bit reachable when the caller starts exactly on that in-range boundary instead of skipping forward into the next word.

- `PHASE1_FIND_BIT_INCLUSIVE_BOUNDARY_REVIEW=helper-local inclusive boundary proof stays explicit through the direct find_bit test anchor so same-word next scans keep the last in-range head-word bit reachable from an inclusive start`

The committed `inclusive_boundary_next`, `inclusive_boundary_zero`, and `inclusive_boundary_and` fields in `zigux/tests/fixtures/phase1_helpers.json` are now part of the authoritative shared replay contract because `zigux/tests/phase1_helpers.zig` consumes those fields directly. Reviewers should keep that shared replay and the direct helper-local inclusive-boundary test anchor aligned: the shared packet now catches inclusive-boundary regressions, while the direct helper-local test keeps the same-word inclusive-start path review-visible at the helper surface.

- `PHASE1_FIND_BIT_INCLUSIVE_BOUNDARY_OWNER=the shared Phase 1 replay now consumes the committed inclusive_boundary_* fixture fields directly, while the direct helper-local inclusive-boundary test remains a review-visible same-word anchor for that path`

For `tools/lib/find_bit.zig`, reviewers must also keep the helper-local zero-bit-window proof explicit through:

- `tools/lib/find_bit.zig`

That means `test "zero-bit windows return without reading bitmap words"` stays present and review-visible whenever `findFirstBit()`, `findFirstZeroBit()`, or `findFirstAndBit()` changes. This helper-local test is the bounded proof that the first-scan entrypoints return the empty-window boundary immediately instead of reading bitmap words outside a caller-visible zero-bit window.

- `PHASE1_FIND_BIT_ZERO_WINDOW_REVIEW=helper-local zero-bit-window proof stays explicit through the direct find_bit test anchor so first-scan entrypoints return the empty-window boundary without reading bitmap words`

For `tools/lib/find_bit.zig`, reviewers must also keep the helper-local zero-sized short-circuit proof explicit through:

- `tools/lib/find_bit.zig`

That means `test "zero-sized scans ignore populated backing words"` stays present and review-visible whenever `findFirstBit()`, `findFirstZeroBit()`, `findFirstAndBit()`, `findNextBit()`, `findNextZeroBit()`, `findNextAndBit()`, or `findLastBit()` changes. This helper-local test is the bounded proof that zero-sized windows still return the caller-visible boundary even when backing words are populated, instead of dereferencing or reporting bits from storage outside the declared live range.

- `PHASE1_FIND_BIT_ZERO_SIZED_REVIEW=helper-local zero-sized short-circuit proof stays explicit through the direct find_bit test anchor so zero-sized windows ignore populated backing words and return the caller-visible boundary without dereferencing live data`

For `tools/lib/find_bit.zig`, reviewers must also keep the helper-local past-`nbits` short-circuit proof explicit through:

- `tools/lib/find_bit.zig`

That means `test "next scans past nbits return without reading bitmap words"` stays present and review-visible whenever `findNextBit()`, `findNextZeroBit()`, or `findNextAndBit()` changes. This helper-local test is the bounded proof that scans starting at or beyond the declared limit still short-circuit to `nbits` without reading bitmap words outside the caller-visible window.

- `PHASE1_FIND_BIT_PAST_NBITS_REVIEW=helper-local past-nbits short-circuit proof stays explicit through the direct find_bit test anchor so next scans starting at or beyond nbits return the boundary without reading bitmap words outside the caller-visible window`

For `tools/lib/find_bit.zig`, reviewers must also keep the helper-local tail-word next-set skip proof explicit through:

- `tools/lib/find_bit.zig`

That means `test "tail-word next set scans skip earlier in-range matches before clamping"` stays present and review-visible whenever `findNextBit()` changes. This helper-local test is the bounded proof that tail-word next set scans still skip earlier in-range matches from the same last word before clamping to `nbits`, instead of returning a stale earlier match when the caller starts later in that tail word.

- `PHASE1_FIND_BIT_TAIL_WORD_SET_SKIP_REVIEW=helper-local tail-word next-set skip proof stays explicit through the direct find_bit test anchor so tail-word next set scans skip earlier in-range matches before clamping to nbits`

For `tools/lib/find_bit.zig`, reviewers must also keep the helper-local tail-word skip proof explicit through:

- `tools/lib/find_bit.zig`
- `zigux/tests/fixtures/phase1_helper_manifest.json`

That means `test "tail-word next zero and shared scans skip earlier in-range matches before clamping"` stays present and review-visible whenever `findNextZeroBit()` or `findNextAndBit()` changes. This helper-local test is the bounded proof that tail-word next zero and shared scans still skip earlier in-range matches before clamping to `nbits` instead of returning stale earlier matches from the same last word. The Phase 1 helper manifest keeps that direct anchor explicit too, so the helper-local review inventory and the parked direct-anchor packet do not silently drift apart while the shared replay remains limited to the committed tail-clamped fixture keys.

- `PHASE1_FIND_BIT_TAIL_WORD_SKIP_REVIEW=helper-local tail-word skip proof stays explicit through the direct find_bit test anchor and the Phase 1 helper manifest so tail-word next zero and shared scans skip earlier in-range matches before clamping to nbits`

For `tools/lib/find_bit.zig`, reviewers must also keep the helper-local underscore alias proof explicit through:

- `tools/lib/find_bit.zig`

That means `test "low-level underscore aliases mirror the primary find helpers"` stays present and review-visible whenever `_find_first_bit()`, `_find_first_and_bit()`, `_find_first_zero_bit()`, `_find_next_bit()`, `_find_next_and_bit()`, `_find_next_zero_bit()`, or `_find_last_bit()` changes. This helper-local test is the bounded proof that the Linux-style underscore entry points stay behaviorally locked to the primary Zig helpers instead of drifting into a second semantics path.

- `PHASE1_FIND_BIT_UNDERSCORE_ALIAS_REVIEW=helper-local underscore alias proof stays explicit through the direct find_bit test anchor so the Linux-style underscore entry points remain behaviorally locked to the primary Zig helpers`

The shared Phase 1 parity replay for `tools/lib/find_bit.zig` must also keep the tail-clamped `nbits` results explicit through:

- `zigux/tests/fixtures/phase1_helpers.json`
- `zigux/tests/phase1_helpers.zig`

That means `tail_clamped_first`, `tail_clamped_next`, `tail_zero_clamped_first`, `tail_zero_clamped_next`, `tail_and_clamped_first`, `tail_and_clamped_next`, `tail_clamped_last`, and `tail_clamped_empty_last` stay present and review-visible whenever the helper or its shared replay changes. Those fixture fields are the bounded proof that first-, next-, zero-, shared-, and last-bit scans all stop at the declared `nbits` boundary instead of silently reporting set or clear bits from the masked tail beyond the live window.

- `PHASE1_FIND_BIT_TAIL_CLAMP_REVIEW=tail_clamped_first, tail_clamped_next, tail_zero_clamped_first, tail_zero_clamped_next, tail_and_clamped_first, and tail_and_clamped_next stay explicit through the shared Phase 1 parity fixture and replay so last-word scans cannot silently leak masked tail bits beyond nbits`

The shared Phase 1 replay in `zigux/tests/phase1_helpers.zig` already consumes `tail_clamped_last` and `tail_clamped_empty_last` directly when it checks `findLastBit()`. Reviewers should keep those two last-bit fields aligned with the six existing first-, next-, zero-, and shared-bit tail-clamp fields whenever the helper or replay changes.

## Bitmap Review Rule

For `tools/lib/bitmap.zig`, reviewers must also keep the committed partial-window XOR fixture contract explicit through:

- `zigux/tests/fixtures/phase1_helpers.json`
- `zigux/tests/phase1_helpers.zig`

That means `partial_xor_nbits` and `partial_xor_masked_values` stay present and review-visible whenever the helper or its paired replay changes. Those two fields are the bounded proof that caller-selected bit windows remain masked instead of silently leaking tail bits beyond `nbits`.

- `PHASE1_BITMAP_PARTIAL_XOR_REVIEW=partial_xor_nbits and partial_xor_masked_values stay explicit through the shared Phase 1 parity fixture and replay so caller-selected bit windows cannot silently leak tail bits beyond nbits`

The helper-local bitmap predicate tail-mask proof must also stay explicit through:

- `tools/lib/bitmap.zig`

That means `test "bitmap predicates ignore out-of-range tail bits"` stays present and review-visible whenever `equal()`, `intersects()`, or `subset()` changes. This helper-local test is the bounded proof that the bitmap predicates still mask last-word tail noise instead of treating out-of-range bits as live equality, overlap, or subset data.

- `PHASE1_BITMAP_PREDICATE_TAIL_MASK_REVIEW=helper-local bitmap predicate tail-mask proof stays explicit through the direct bitmap test anchor so equal, intersects, and subset ignore out-of-range tail bits instead of treating tail noise as live data`

The helper-local first-word boundary proof must also stay explicit through:

- `tools/lib/bitmap.zig`

That means `test "bitmap range helpers honor exact first-word boundaries"` stays present and review-visible whenever `setRange()` or `clearRange()` changes. This helper-local test is the bounded proof that first-word masks stay exact when a range starts near the end of one word and stops exactly on that first-word boundary instead of spilling into the next word or clearing too much.

- `PHASE1_BITMAP_FIRST_WORD_BOUNDARY_REVIEW=helper-local bitmap first-word boundary proof stays explicit through the direct bitmap test anchor so setRange and clearRange preserve exact first-word masks when a range ends on the first-word boundary`

The helper-local final partial-word proof must also stay explicit through:

- `tools/lib/bitmap.zig`

That means `test "bitmap range helpers clamp the final partial word"` stays present and review-visible whenever `setRange()` or `clearRange()` changes. This helper-local test is the bounded proof that trailing partial-word masks stay clamped to the requested range instead of spilling set or clear work beyond the caller-selected tail window.

- `PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=helper-local bitmap final partial-word proof stays explicit through the direct bitmap test anchor so setRange and clearRange clamp trailing partial-word masks to the requested tail window instead of spilling work beyond it`

The helper-local `bitmap.scnprintf()` cross-word range-collapse proof must also stay explicit through:

- `tools/lib/bitmap.zig`
- `zigux/tests/fixtures/phase1_helper_manifest.json`

That means `test "bitmap scnprintf collapses contiguous ranges across word boundaries"` stays present and review-visible whenever `bitmap.scnprintf()` changes. This helper-local test is the bounded proof that one contiguous run still renders as one collapsed range even when it crosses a machine-word boundary, and the Phase 1 helper manifest keeps that direct anchor explicit so the parked direct review packet does not silently drop that word-boundary rendering proof.

- `PHASE1_BITMAP_SCNPRINTF_CROSS_WORD_REVIEW=helper-local bitmap.scnprintf cross-word range-collapse proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so contiguous runs crossing a machine-word boundary still render as one collapsed range instead of splitting at the word edge`

The helper-local `bitmap.scnprintf()` truncation proof must also stay explicit through:

- `tools/lib/bitmap.zig`

That means `test "bitmap scnprintf reports full length while truncating the buffer"` stays present and review-visible whenever `bitmap.scnprintf()` changes. The shared Phase 1 parity fixture only locks the full rendered range string, so this helper-local test is the bounded proof that shorter caller buffers stay NUL-terminated while `bitmap.scnprintf()` still reports the full would-have-rendered length.

- `PHASE1_BITMAP_SCNPRINTF_TRUNCATION_REVIEW=helper-local bitmap.scnprintf truncation proof stays explicit through the direct bitmap test anchor because the shared Phase 1 parity fixture only locks the full rendered range string`

The helper-local `bitmap.scnprintf()` tiny-buffer proof must also stay explicit through:

- `tools/lib/bitmap.zig`
- `zigux/tests/fixtures/phase1_helpers.json`
- `zigux/tests/phase1_helpers.zig`

That means `test "bitmap scnprintf handles terminator-only and zero-length caller views"` stays present and review-visible whenever `bitmap.scnprintf()` changes, and the shared Phase 1 parity fixture plus replay keep `terminator_only_scnprintf_len`, `terminator_only_nul`, and `zero_length_scnprintf_len` explicit. This paired packet is the bounded proof that terminator-only caller buffers stay NUL-terminated and zero-length caller views return without writing hidden bytes.

- `PHASE1_BITMAP_SCNPRINTF_TINY_BUFFER_REVIEW=helper-local bitmap.scnprintf tiny-buffer proof stays explicit through the direct bitmap test anchor plus the shared Phase 1 parity fixture and replay so terminator-only caller buffers stay NUL-terminated and zero-length caller views return without writing hidden bytes`

The helper-local bitmap copy alias proof must also stay explicit through:

- `tools/lib/bitmap.zig`

That means `test "bitmap copy aliases preserve tail clearing and extension semantics"` stays present and review-visible whenever `bitmap_copy_clear_tail()` or `bitmap_copy_and_extend()` changes. This helper-local test is the bounded proof that the alias entrypoints preserve last-word tail masking and zero-filled extension instead of drifting away from `copyClearTail()` and `copyAndExtend()`.

- `PHASE1_BITMAP_COPY_ALIAS_REVIEW=helper-local bitmap copy alias proof stays explicit through the direct bitmap test anchor so bitmap_copy_clear_tail and bitmap_copy_and_extend preserve tail masking and zero-filled extension semantics`

The helper-local raw `bitmap_copy()` alias proof must also stay explicit through:

- `tools/lib/bitmap.zig`

That means `test "bitmap copy alias preserves raw source words without tail clearing"` stays present and review-visible whenever `copy()` or `bitmap_copy()` changes. This helper-local test is the bounded proof that the raw alias entrypoint preserves unmasked source words instead of silently adopting the tail-clearing semantics reserved for `copyClearTail()` and `bitmap_copy_clear_tail()`.

- `PHASE1_BITMAP_RAW_COPY_ALIAS_REVIEW=helper-local raw bitmap_copy alias proof stays explicit through the direct bitmap test anchor so copy and bitmap_copy preserve unmasked source words instead of silently adopting tail-clearing semantics`

The helper-local zero-count and aligned-count copy proof must also stay explicit through:

- `tools/lib/bitmap.zig`

That means `test "bitmap copy and extend handles zero and aligned counts"` stays present and review-visible whenever `copyAndExtend()`, `bitmap_copy_and_extend()`, `copyClearTail()`, or `bitmap_copy_clear_tail()` changes. This helper-local test is the bounded proof that zero-count copies still clear the destination extension and that aligned word counts preserve the copied word without silently picking up partial-tail masking that belongs only to non-aligned windows.

- `PHASE1_BITMAP_COPY_EXTEND_ZERO_ALIGNED_REVIEW=helper-local bitmap copy-and-extend zero-count and aligned-count proof stays explicit through the direct bitmap test anchor so zero-count copies clear the destination extension and aligned word counts preserve copied words without accidental tail masking`

The helper-local zero-sized destination-view proof must also stay explicit through:

- `tools/lib/bitmap.zig`
- `zigux/tests/fixtures/phase1_helper_manifest.json`

That means `test "bitmap copy helpers keep zero-sized destination views untouched"` stays present and review-visible whenever `copyClearTail()`, `bitmap_copy_clear_tail()`, `copyAndExtend()`, or `bitmap_copy_and_extend()` changes. This helper-local test is the bounded proof that zero-sized destination views remain untouched instead of clearing sentinel caller storage when the live bitmap window is empty. The Phase 1 helper manifest keeps that direct anchor explicit too, so the helper-local review inventory and the direct-anchor packet do not silently drift apart while zero-sized destination behavior stays helper-local.

- `PHASE1_BITMAP_ZERO_SIZED_DESTINATION_VIEW_REVIEW=helper-local zero-sized destination-view proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so copyClearTail, bitmap_copy_clear_tail, copyAndExtend, and bitmap_copy_and_extend leave zero-sized destination views untouched instead of clearing caller sentinel storage`

The helper-local zero-bit no-op proof must also stay explicit through:

- `tools/lib/bitmap.zig`

That means `test "bitmap zero-bit helpers stay explicit no-ops"` stays present and review-visible whenever `zero()`, `orBits()`, `xorBits()`, `copy()`, or `scnprintf()` changes. This helper-local test is the bounded proof that zero-bit windows keep the mutating helpers, boolean queries, and rendered empty-window path explicit without touching caller-visible storage or writing hidden bytes.

- `PHASE1_BITMAP_ZERO_BIT_NOOP_REVIEW=helper-local bitmap zero-bit no-op proof stays explicit through the direct bitmap test anchor so zero-bit windows keep mutating helpers, boolean queries, and the rendered empty-window path from touching caller-visible storage or writing hidden bytes`

The helper-local zero-bit binary identity proof must also stay explicit through:

- `tools/lib/bitmap.zig`
- `zigux/tests/fixtures/phase1_helper_manifest.json`

That means `test "bitmap zero-bit binary helpers stay explicit identity operations"` stays present and review-visible whenever `andBits()`, `andNotBits()`, `equal()`, `intersects()`, or `subset()` changes. This helper-local test is the bounded proof that zero-bit binary helpers keep caller storage untouched and report the empty-window identity results instead of treating a zero-bit window as live data. The Phase 1 helper manifest keeps that direct anchor explicit too, so the helper-local review inventory and the direct-anchor packet do not silently drift apart when zero-bit binary semantics reopen.

- `PHASE1_BITMAP_ZERO_BIT_BINARY_IDENTITY_REVIEW=helper-local bitmap zero-bit binary identity proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so andBits, andNotBits, equal, intersects, and subset keep empty-window identity semantics without treating zero-bit windows as live data`

The helper-local Linux-style alias proof must also stay explicit through:

- `tools/lib/bitmap.zig`
- `zigux/tests/fixtures/phase1_helper_manifest.json`

That means `test "bitmap Linux-style aliases mirror the primary helper surface"` stays present and review-visible whenever the alias entrypoints change. This helper-local test is the bounded proof that the Linux-style bitmap alloc/free, zero/fill, predicate, mutation, and render aliases stay behaviorally locked to the primary helper surface instead of drifting into a second semantics path, and the Phase 1 helper manifest keeps that alias anchor visible inside the direct review packet.

- `PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so the Linux-style bitmap alloc/free, zero/fill, predicate, mutation, and render aliases remain behaviorally locked to the primary helper surface`

## Rbtree Review Rule

For `tools/lib/rbtree.zig`, reviewers must keep the current bounded Phase 1 rbtree surface explicit through:

- `tools/lib/rbtree.zig`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `zigux/tests/fixtures/phase1_helpers.json`

That means `test "rbtree inserts and traverses in sorted order"`, `test "rbtree erase and replace keep traversal consistent"`, `test "rbtree eraseInit detaches erased node"`, `test "rbtree postorder and empty node helpers behave"`, `test "rbtree findAdd keeps the first duplicate and inserts new keys"`, `test "rbtree nextMatch walks the duplicate range in order"`, `test "rbtree matchIterator walks the duplicate range in order"`, `test "rbtree addCached returns the inserted node only when it becomes leftmost"`, `test "rbtree findAddCached keeps cached leftmost stable while inserting misses"`, `test "rbtree cached root keeps the leftmost pointer in sync"`, `test "rbtree cached-root Linux-style aliases mirror the primary helpers"`, `test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"`, `test "rbtree eraseCached returns null for a singleton cached tree"`, `test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"`, and `test "rbtree eraseInitCached clears singleton cached roots before reseed"` stay present and review-visible whenever the helper changes. The shared replay must also keep `empty_root`, `insert_order`, `reverse_order`, `replace_order`, `erase_init_order`, `postorder_count`, `erase_init_node_empty`, `cleared_node_empty`, `find_found_key`, `find_missing`, `find_first_serial`, and `next_match_serials` and `next_match_terminal_null` explicit so traversal, detached-node, and duplicate-search parity remain reviewable while match-iterator coverage plus cached-root insert-miss, leftmost-sync, singleton-erase, replacement, detach, and reseed paths stay owned by direct helper-local anchors instead of implying a broader shared iterator or cached-root fixture packet than current `master` actually ships.

- `PHASE1_RBTREE_REVIEW_PACKET=helper-local rbtree tests plus the shared traversal, detached-node, and duplicate-search replay stay explicit so duplicate-search parity keys remain shared-replay-owned while match-iterator coverage plus cached-root insert-miss, leftmost-sync, singleton-erase, replacement, detach, and reseed behavior keep direct review anchors without implying a broader shared iterator or cached-root fixture packet than current master ships`

The committed shared replay in `zigux/tests/phase1_helpers.zig` now consumes `find_found_key`, `find_missing`, `find_first_serial`, and `next_match_serials` and `next_match_terminal_null` directly, so duplicate-search parity is shared-replay-owned as well as helper-local. Reviewers should keep those shared fixture fields and the direct helper-local duplicate-search anchors `test "rbtree findAdd keeps the first duplicate and inserts new keys"`, `test "rbtree nextMatch walks the duplicate range in order"`, and `test "rbtree matchIterator walks the duplicate range in order"` aligned whenever `find()`, `findFirst()`, `findAdd()`, `nextMatch()`, or `matchIterator()` changes.

The direct helper-local cached-root follow-up anchors `test "rbtree addCached returns the inserted node only when it becomes leftmost"`, `test "rbtree findAddCached keeps cached leftmost stable while inserting misses"`, `test "rbtree cached root keeps the leftmost pointer in sync"`, `test "rbtree cached-root Linux-style aliases mirror the primary helpers"`, `test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"`, `test "rbtree eraseCached returns null for a singleton cached tree"`, `test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"`, and `test "rbtree eraseInitCached clears singleton cached roots before reseed"` are also owning proofs for now. The shared Phase 1 replay does not consume committed cached-root alias, insert, insert-miss, steady-state leftmost-sync, singleton-erase, replacement, detach, or reseed fixture fields directly yet, so reviewers must keep those eight helper-local anchors explicit whenever `addCached()`, `findAddCached()`, `firstCached()`, `insertColorCached()`, `rb_insert_color_cached()`, `rb_add_cached()`, `rb_first_cached()`, `rb_erase_cached()`, `rb_replace_node_cached()`, `eraseCached()`, `replaceNodeCached()`, or `eraseInitCached()` changes.

This stays intentionally helper-local: the committed Phase 1 fixture packet still only owns traversal, detached-node, and duplicate-search parity for `rbtree`. Until current `master` ships dedicated cached-root fixture keys, the manifest and this closure rule are the review-visible ownership packet for those cached-root follow-ups, including the steady-state leftmost-sync and singleton-erase-null cases.

## String Review Rule

For `tools/lib/string.zig`, reviewers must keep the current bounded host-side string surface explicit through:

- `tools/lib/string.zig`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `zigux/tests/fixtures/phase1_helpers.json`

That means `test "strtobool accepts common Linux forms"`, `test "strlcpy copies and returns the source length"`, `test "streq matches C-string equality semantics"`, `test "skip trim remove and replace spaces work in place"`, `test "strreplace mirrors replaceChar C-string semantics"`, `test "strHasPrefix honors C-string boundaries"`, `test "strstarts mirrors the header-level prefix helper"`, `test "strEndsWith honors C-string boundaries"`, `test "sysfsStreq treats trailing newline and NUL as equivalent"`, `test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"`, `test "memdup and memchrInv preserve byte content"`, `test "memchr_inv mirrors memchrInv byte-search semantics"`, `test "memchrInv keeps long-buffer first-dirty-byte results stable"`, `test "memchrInv follows the earliest dirty byte as long buffers change"`, `test "memchrInv dirty-word shortcut handles zero-value scans at word boundaries"`, `test "memchrInv zero-value scans keep the earliest dirty byte across every prefix alignment"`, `test "memchrInv short zero-value scans stay byte-accurate"`, `test "memparse handles decimal hexadecimal octal and suffixes"`, `test "memparse keeps original rest when sign is not followed by digits"`, `test "memparse saturates signed overflow instead of trapping"`, `test "memparse clamps explicit positive signed overflow"`, `test "memparse keeps signed values and their trailing rest aligned"`, `test "memparse consumes suffix after saturation"`, `test "memparse applies suffixes before signed clamping"`, and `test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"` stay present and review-visible whenever the helper changes. The helper-local memparse safety anchors must also stay explicit through the direct string tests so sign-prefixed invalid input preserves its original rest, explicit positive and negative signed overflow saturates instead of trapping, and recognized suffixes are still consumed after saturation. The broader string review inventory in `zigux/tests/fixtures/phase1_helper_manifest.json` should stay aligned with those direct anchors whenever `memparse()` moves. The current direct string packet also keeps `test "memparse clamps explicit positive signed overflow"`, `test "memparse keeps signed values and their trailing rest aligned"`, and `test "memparse applies suffixes before signed clamping"` review-visible whenever `memparse()` changes. Those helper-local anchors are the bounded proof that explicit `+`-prefixed overflow clamps at the signed maximum, signed inputs keep the same trailing-rest split as unsigned inputs instead of consuming or dropping bytes beyond the parsed magnitude, and recognized suffixes still scale signed magnitudes before signed clamping instead of saturating the pre-scaled value. The shared replay must also keep `test "phase 1 string replaceChar stops at embedded NUL"` plus the `strtobool_y`, `strtobool_on`, `strtobool_zero`, `strtobool_off`, `strtobool_invalid`, `strlcpy_len`, `strlcpy_buffer`, `skip_spaces`, `trim_spaces`, `remove_spaces`, `replace_char`, `replace_char_end`, `replace_char_cstr_end`, `replace_char_cstr_bytes`, `memchr_inv_index`, and `memchr_inv_none` fixture fields explicit so the packet still proves the shared boolean, copy, space-trimming, embedded-NUL stop, committed C-string replacement-byte, and byte-search parity surface, while `zigux/tests/fixtures/phase1_helper_manifest.json` keeps the broader direct string review anchors aligned with the live helper surface.

- `PHASE1_STRING_MEMPARSE_REVIEW=helper-local memparse safety anchors stay explicit through the direct string tests and the Phase 1 helper manifest so sign-prefixed invalid input preserves rest, explicit positive and signed overflow clamps remain review-visible, signed inputs keep trailing-rest splits aligned with unsigned parsing, and suffixes are still consumed after saturation`
- `PHASE1_STRING_REVIEW_PACKET=helper-local string tests and the shared embedded-NUL replay stay explicit so the bounded Phase 1 string surface keeps its direct review anchors, committed C-string replacement bytes, and parity fixture keys`

The direct helper-local follow-up `test "memchrInv follows the earliest dirty byte as long buffers change"` must also stay review-visible whenever `memchrInv()` changes. The shared Phase 1 fixture still pins one fixed first-dirty-byte position and the all-clean case, so this direct follow-up remains the owning proof that the earliest mismatch advances correctly as later dirty bytes become the next live divergence instead of drifting to a stale earlier offset. The Phase 1 helper manifest keeps that follow-up anchor explicit too, so the direct helper inventory and the moving-dirty-byte review rule do not silently drift apart while the shared replay stays limited to the fixed-position parity fields.

The direct helper-local follow-up `test "memchrInv dirty-word shortcut handles zero-value scans at word boundaries"`, `test "memchrInv zero-value scans keep the earliest dirty byte across every prefix alignment"`, and `test "memchrInv short zero-value scans stay byte-accurate"` must also stay review-visible whenever `memchrInv()` changes. The shared Phase 1 fixture still pins one non-zero first-dirty-byte position and the all-clean case, so these three direct anchors remain the owning proof that zero-value scans keep the aligned dirty-word shortcut, the cross-alignment prefix handoff, and the short-buffer byte fallback honest instead of drifting at the first mismatch boundary. Keeping all three zero-value anchors explicit in the direct string review packet preserves review visibility for that bounded `memchrInv()` surface while the shared replay stays focused on the fixed-position parity fields.

The direct helper-local follow-up `test "memchr_inv mirrors memchrInv byte-search semantics"` must also stay review-visible whenever `memchr_inv()` changes. The shared Phase 1 fixture still pins the primary `memchrInv()` parity outputs rather than the Linux-style alias entry point separately, so this alias-focused anchor remains the owning proof that `memchr_inv()` stays behaviorally locked to `memchrInv()` across fixed-position and all-clean scans instead of drifting into a second byte-search path.

The direct helper-local follow-up `test "sysfsStreq treats trailing newline and NUL as equivalent"` must also stay review-visible whenever `sysfsStreq()` changes. The shared Phase 1 string fixture does not currently pin sysfs-style newline trimming or first-terminator equivalence directly, so this direct follow-up remains the owning proof that newline-suffixed sysfs values compare the same as NUL-terminated values without reading bytes past the first terminator. Keeping that anchor explicit in the direct string review packet prevents this bounded sysfs comparison surface from slipping out of review visibility while the shared replay stays focused on replaceChar and memchrInv parity.

The direct helper-local follow-up `test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"` must also stay review-visible whenever `sysfs_streq()` changes. The shared Phase 1 string fixture still does not pin that alias entry point separately, so this alias-focused follow-up remains the owning proof that the Linux-style wrapper stays behaviorally locked to `sysfsStreq()` across newline trimming and first-terminator equivalence instead of drifting into a second sysfs comparison path. Keeping that anchor explicit in the direct string review packet preserves review visibility for the alias surface while the shared replay stays focused on replaceChar and memchrInv parity.

The direct helper-local follow-up test `test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"` must also stay review-visible whenever `trimSpaces()` or `strim()` changes. The shared Phase 1 string fixture still records the trimmed bytes but not the preserved tail bytes beyond the first terminator, so this direct follow-up remains the owning proof that trailing-whitespace trimming stops at the first embedded NUL instead of mutating bytes past the C-string boundary. The Phase 1 helper manifest keeps this trim follow-up anchor explicit as well, so helper-local C-string ownership stays aligned across the direct test packet and the broader string review inventory.

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
