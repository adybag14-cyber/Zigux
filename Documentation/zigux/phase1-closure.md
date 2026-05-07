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
- `python3 scripts/zigux/validate-phase1-closure.py`

Reviewers should treat drift across those packet summaries, the committed helper and benchmark fixtures, the shared tests-root entrypoints, the bootstrap workflow replay, and the validator-first plus Linux-style replay routes as a closure regression even when the helper code itself is unchanged.

## Find Bit Review Rule

For `tools/lib/find_bit.zig`, reviewers must also keep the helper-local single-word next-scan proof explicit through:

- `tools/lib/find_bit.zig`

That means `test "single-word next scans honor start masks"` stays present and review-visible whenever `findNextBit()`, `findNextZeroBit()`, or `findNextAndBit()` changes. The shared Phase 1 parity fixture already locks the cross-word and tail-clamped `find_bit` results, but it does not isolate the same-word `start` masking path, so this helper-local test is the bounded proof that one-word scans still honor caller-selected start masks instead of re-reading earlier bits.

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

For `tools/lib/find_bit.zig`, reviewers must also keep the helper-local past-`nbits` short-circuit proof explicit through:

- `tools/lib/find_bit.zig`

That means `test "next scans past nbits return without reading bitmap words"` stays present and review-visible whenever `findNextBit()`, `findNextZeroBit()`, or `findNextAndBit()` changes. This helper-local test is the bounded proof that scans starting at or beyond the declared limit still short-circuit to `nbits` without reading bitmap words outside the caller-visible window.

- `PHASE1_FIND_BIT_PAST_NBITS_REVIEW=helper-local past-nbits short-circuit proof stays explicit through the direct find_bit test anchor so next scans starting at or beyond nbits return the boundary without reading bitmap words outside the caller-visible window`

For `tools/lib/find_bit.zig`, reviewers must also keep the helper-local underscore alias proof explicit through:

- `tools/lib/find_bit.zig`

That means `test "low-level underscore aliases mirror the primary find helpers"` stays present and review-visible whenever `_find_first_bit()`, `_find_first_and_bit()`, `_find_first_zero_bit()`, `_find_next_bit()`, `_find_next_and_bit()`, or `_find_next_zero_bit()` changes. This helper-local test is the bounded proof that the Linux-style underscore entry points stay behaviorally locked to the primary Zig helpers instead of drifting into a second semantics path.

- `PHASE1_FIND_BIT_UNDERSCORE_ALIAS_REVIEW=helper-local underscore alias proof stays explicit through the direct find_bit test anchor so the Linux-style underscore entry points remain behaviorally locked to the primary Zig helpers`

The shared Phase 1 parity replay for `tools/lib/find_bit.zig` must also keep the tail-clamped `nbits` results explicit through:

- `zigux/tests/fixtures/phase1_helpers.json`
- `zigux/tests/phase1_helpers.zig`

That means `tail_clamped_first`, `tail_clamped_next`, `tail_zero_clamped_first`, `tail_zero_clamped_next`, `tail_and_clamped_first`, and `tail_and_clamped_next` stay present and review-visible whenever the helper or its shared replay changes. Those fixture fields are the bounded proof that last-word scans stop at the declared `nbits` boundary instead of silently reporting set or clear bits from the masked tail beyond the live window.

- `PHASE1_FIND_BIT_TAIL_CLAMP_REVIEW=tail_clamped_first, tail_clamped_next, tail_zero_clamped_first, tail_zero_clamped_next, tail_and_clamped_first, and tail_and_clamped_next stay explicit through the shared Phase 1 parity fixture and replay so last-word scans cannot silently leak masked tail bits beyond nbits`

## Bitmap Review Rule

For `tools/lib/bitmap.zig`, reviewers must also keep the committed partial-window XOR fixture contract explicit through:

- `zigux/tests/fixtures/phase1_helpers.json`
- `zigux/tests/phase1_helpers.zig`

That means `partial_xor_nbits` and `partial_xor_masked_values` stay present and review-visible whenever the helper or its paired replay changes. Those two fields are the bounded proof that caller-selected bit windows remain masked instead of silently leaking tail bits beyond `nbits`.

- `PHASE1_BITMAP_PARTIAL_XOR_REVIEW=partial_xor_nbits and partial_xor_masked_values stay explicit through the shared Phase 1 parity fixture and replay so caller-selected bit windows cannot silently leak tail bits beyond nbits`

The helper-local first-word boundary proof must also stay explicit through:

- `tools/lib/bitmap.zig`

That means `test "bitmap range helpers honor exact first-word boundaries"` stays present and review-visible whenever `setRange()` or `clearRange()` changes. This helper-local test is the bounded proof that first-word masks stay exact when a range starts near the end of one word and stops exactly on that first-word boundary instead of spilling into the next word or clearing too much.

- `PHASE1_BITMAP_FIRST_WORD_BOUNDARY_REVIEW=helper-local bitmap first-word boundary proof stays explicit through the direct bitmap test anchor so setRange and clearRange preserve exact first-word masks when a range ends on the first-word boundary`

The helper-local `bitmap.scnprintf()` truncation proof must also stay explicit through:

- `tools/lib/bitmap.zig`

That means `test "bitmap scnprintf reports full length while truncating the buffer"` stays present and review-visible whenever `bitmap.scnprintf()` changes. The shared Phase 1 parity fixture only locks the full rendered range string, so this helper-local test is the bounded proof that shorter caller buffers stay NUL-terminated and report only the bytes actually stored.

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

The helper-local zero-bit no-op proof must also stay explicit through:

- `tools/lib/bitmap.zig`

That means `test "bitmap zero-bit helpers stay explicit no-ops"` stays present and review-visible whenever `zero()`, `orBits()`, `xorBits()`, `copy()`, or `scnprintf()` changes. This helper-local test is the bounded proof that zero-bit windows keep the mutating helpers, boolean queries, and rendered empty-window path explicit without touching caller-visible storage or writing hidden bytes.

- `PHASE1_BITMAP_ZERO_BIT_NOOP_REVIEW=helper-local bitmap zero-bit no-op proof stays explicit through the direct bitmap test anchor so zero-bit windows keep mutating helpers, boolean queries, and the rendered empty-window path from touching caller-visible storage or writing hidden bytes`

## Rbtree Review Rule

For `tools/lib/rbtree.zig`, reviewers must keep the current bounded Phase 1 rbtree surface explicit through:

- `tools/lib/rbtree.zig`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `zigux/tests/fixtures/phase1_helpers.json`

That means `test "rbtree inserts and traverses in sorted order"`, `test "rbtree erase and replace keep traversal consistent"`, `test "rbtree eraseInit detaches erased node"`, `test "rbtree postorder and empty node helpers behave"`, `test "rbtree findAdd keeps the first duplicate and inserts new keys"`, `test "rbtree nextMatch walks the duplicate range in order"`, `test "rbtree addCached returns the inserted node only when it becomes leftmost"`, `test "rbtree cached root keeps the leftmost pointer in sync"`, `test "rbtree eraseCached returns null for a singleton cached tree"`, `test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"`, and `test "rbtree eraseInitCached clears singleton cached roots before reseed"` stay present and review-visible whenever the helper changes. The shared replay must also keep `empty_root`, `insert_order`, `reverse_order`, `replace_order`, `erase_init_order`, `postorder_count`, `erase_init_node_empty`, `cleared_node_empty`, `find_found_key`, `find_missing`, `find_first_serial`, `next_match_serials`, and `next_match_terminal_null` explicit so traversal, detached-node, and duplicate-search parity remain reviewable while the cached-root detach and reseed paths stay owned by direct helper-local anchors instead of implying a broader shared cached-root fixture packet than current `master` actually ships.

- `PHASE1_RBTREE_REVIEW_PACKET=helper-local rbtree tests plus the shared traversal, detached-node, and duplicate-search replay stay explicit so duplicate-search parity keys remain shared-replay-owned while cached-root behavior keeps direct review anchors without implying a broader cached-root fixture packet than current master ships`

The committed shared replay in `zigux/tests/phase1_helpers.zig` now consumes `find_found_key`, `find_missing`, `find_first_serial`, `next_match_serials`, and `next_match_terminal_null` directly, so duplicate-search parity is shared-replay-owned as well as helper-local. Reviewers should keep those shared fixture fields and the direct helper-local duplicate-search anchors `test "rbtree findAdd keeps the first duplicate and inserts new keys"` and `test "rbtree nextMatch walks the duplicate range in order"` aligned whenever `find()`, `findFirst()`, `findAdd()`, or `nextMatch()` changes.

The direct helper-local cached-root reset follow-up anchors `test "rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned"` and `test "rbtree eraseInitCached clears singleton cached roots before reseed"` are also owning proofs for now. The shared Phase 1 replay does not consume committed cached-root detach or reseed fixture fields directly yet, so reviewers must keep those two helper-local anchors explicit whenever `eraseInitCached()` changes.

## String Review Rule

For `tools/lib/string.zig`, reviewers must keep the current bounded host-side string surface explicit through:

- `tools/lib/string.zig`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `zigux/tests/fixtures/phase1_helpers.json`

That means `test "strtobool accepts common Linux forms"`, `test "strlcpy copies and returns the source length"`, `test "streq matches C-string equality semantics"`, `test "skip trim remove and replace spaces work in place"`, `test "strreplace mirrors replaceChar C-string semantics"`, `test "strHasPrefix honors C-string boundaries"`, `test "strstarts mirrors the header-level prefix helper"`, `test "strEndsWith honors C-string boundaries"`, `test "memdup and memchrInv preserve byte content"`, `test "memchrInv keeps long-buffer first-dirty-byte results stable"`, `test "memparse handles decimal hexadecimal octal and suffixes"`, `test "memparse keeps original rest when sign is not followed by digits"`, `test "memparse saturates signed overflow instead of trapping"`, and `test "memparse consumes suffix after saturation"` stay present and review-visible whenever the helper changes. The helper-local memparse safety anchors must also stay explicit through the direct string tests and `zigux/tests/fixtures/phase1_helper_manifest.json` so sign-prefixed invalid input preserves its original rest, signed overflow saturates instead of trapping, and recognized suffixes are still consumed after saturation. The current direct string packet also keeps `test "memparse keeps signed values and their trailing rest aligned"` review-visible whenever `memparse()` changes. That helper-local anchor is the bounded proof that signed inputs keep the same trailing-rest split as unsigned inputs instead of consuming or dropping bytes beyond the parsed magnitude. The shared replay must also keep `test "phase 1 string replaceChar stops at embedded NUL"` plus the `replace_char`, `replace_char_end`, `replace_char_cstr_end`, `replace_char_cstr_bytes`, `memchr_inv_index`, and `memchr_inv_none` fixture fields explicit so the packet still proves the embedded-NUL stop rule, the committed shared C-string replacement bytes, and the shared byte-search parity, while `zigux/tests/fixtures/phase1_helper_manifest.json` keeps the broader direct string review anchors aligned with the live helper surface.

- `PHASE1_STRING_MEMPARSE_REVIEW=helper-local memparse safety anchors stay explicit through the direct string tests and the Phase 1 helper manifest so sign-prefixed invalid input preserves rest, signed overflow saturates instead of trapping, and suffixes are still consumed after saturation`
- `PHASE1_STRING_REVIEW_PACKET=helper-local string tests and the shared embedded-NUL replay stay explicit so the bounded Phase 1 string surface keeps its direct review anchors, committed C-string replacement bytes, and parity fixture keys`

The direct helper-local follow-up test `test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"` must also stay review-visible whenever `trimSpaces()` or `strim()` changes. The shared Phase 1 string fixture still records the trimmed bytes but not the preserved tail bytes beyond the first terminator, so this direct follow-up remains the owning proof that trailing-whitespace trimming stops at the first embedded NUL instead of mutating bytes past the C-string boundary.

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
