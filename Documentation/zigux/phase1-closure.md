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
- reviewer surface: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-tests-root-review-companion.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` keep the same closed helper inventory, validator-first replay path, and fail-closed checker stack explicit for this bounded Phase 1 packet.

No additional helper should be called Phase 1 work unless this document and the bootstrap validators are deliberately reopened.

## Helper Review Notes

- `tools/lib/bitmap.zig` closure includes committed C-backed parity coverage for allocator-backed bitmap sizing, zero-allocation state, contiguous-range rendering, the empty-bitmap buffer-preservation contract, and the truncation path that must preserve a trailing terminator slot.
- `tools/lib/bitmap.zig` direct Zig unit coverage keeps `bitmapAlloc()`, `bitmapZalloc()`, and `bitmapFree()` honest by proving optional bitmap handles size through `bitsToWords()`, zero-filled allocation stays intact, and released optionals reset to `null`.
- `tools/lib/bitmap.zig` direct Zig unit coverage also keeps `bitmap_zero()`, `bitmap_fill()`, `bitmap_copy()`, `bitmap_empty()`, and `bitmap_full()` aligned with `zero()`, `fill()`, `copy()`, `empty()`, and `full()` for active-word clearing, partial-tail fill masking, copied-tail preservation, and predicate results across the same declared bit window.
- `tools/lib/bitmap.zig` direct Zig unit coverage also keeps `bitmap_alloc()`, `bitmap_zalloc()`, and `bitmap_free()` aligned with `bitmapAlloc()`, `bitmapZalloc()`, and `bitmapFree()` for partial-word sizing, zero-filled allocation, and optional-handle reset semantics.
- `tools/lib/bitmap.zig` direct Zig unit coverage also keeps tail-masked reduction helpers aligned so `andBits()`, `andNotBits()`, `equal()`, `intersects()`, and `subset()` ignore out-of-range tail differences while preserving the in-range window.
- `tools/lib/bitmap.zig` direct Zig unit coverage also keeps `xorBits()` aligned across a multiword tail by proving callers can clamp the last word back to the in-range bits without leaking the out-of-range tail.
- `tools/lib/bitmap.zig` direct Zig unit coverage also keeps zero-length helper calls explicit and side-effect free so `zero()`, `fill()`, `copy()`, `copyClearTail()`, `orBits()`, `xorBits()`, scans, and formatting all leave caller-owned buffers untouched when `nbits` is zero.
- `tools/lib/bitmap.zig` direct Zig unit coverage also keeps the underscore alias entry points aligned so `bitmap_weight()`, `bitmap_and()`, `bitmap_andnot()`, `bitmap_or()`, `bitmap_xor()`, `bitmap_equal()`, `bitmap_intersects()`, `bitmap_subset()`, `bitmap_set()`, `bitmap_clear()`, and `bitmap_scnprintf()` preserve the same caller-selected window semantics as the camelCase helpers.
- `tools/lib/bitmap.zig` direct Zig unit coverage also keeps the double-underscore alias entry points aligned so `__bitmap_weight()`, `__bitmap_or()`, `__bitmap_and()`, `__bitmap_andnot()`, `__bitmap_xor()`, `__bitmap_equal()`, `__bitmap_intersects()`, `__bitmap_subset()`, `__bitmap_set()`, and `__bitmap_clear()` preserve the same caller-selected window semantics as the core helpers.
- `tools/lib/bitmap.zig` direct Zig unit coverage also keeps `bitmapSize()` and `bitmap_size()` aligned by rounding zero-length, partial-word, and multiword bit counts up to the same full-word byte footprint.
- bitmap range unit-test anchor: `tools/lib/bitmap.zig:test "bitmap range helpers preserve edges across whole-word spans"`
- bitmap copy unit-test anchor: `tools/lib/bitmap.zig:test "bitmap copyClearTail clears out-of-range bits in the last copied word"`
- bitmap bitwise unit-test anchor: `tools/lib/bitmap.zig:test "bitmap and andnot equal intersects subset"`
- bitmap fixture authority: `zigux/tests/fixtures/phase1_helpers.json`
- bitmap manifest review anchor: `zigux/tests/fixtures/phase1_helper_manifest.json`
- bitmap direct unit-test anchor: `tools/lib/bitmap.zig:test "bitmap allocation helpers size zero fill and reset optionals"`
- bitmap header alias unit-test anchor: `tools/lib/bitmap.zig:test "bitmap header-style aliases preserve zero fill copy and predicate semantics"`
- bitmap alias unit-test anchor: `tools/lib/bitmap.zig:test "bitmap underscore aliases preserve bitmap helper semantics"`
- bitmap allocator alias unit-test anchor: `tools/lib/bitmap.zig:test "bitmap underscore allocator aliases preserve allocation and ownership semantics"`
- bitmap double-underscore alias unit-test anchor: `tools/lib/bitmap.zig:test "bitmap double-underscore aliases preserve core helper semantics"`
- bitmap size unit-test anchor: `tools/lib/bitmap.zig:test "bitmap size helpers round up to full words in bytes"`
- bitmap xor unit-test anchor: `tools/lib/bitmap.zig:test "bitmap xor across a multiword tail still lets callers clamp the last word"`
- bitmap tail-mask unit-test anchor: `tools/lib/bitmap.zig:test "bitmap tail-masked helpers ignore out-of-range differences"`
- bitmap zero-bit unit-test anchor: `tools/lib/bitmap.zig:test "bitmap zero-bit helpers stay explicit no-ops"`
- bitmap empty unit-test anchor: `tools/lib/bitmap.zig:test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"`
- bitmap empty-bitmap review note: `bitmap_scnprintf` must leave a non-empty caller buffer untouched when no bits are set, matching the C helper contract
- bitmap allocator review note: `bitmap_alloc()` and `bitmap_zalloc()` must size partial-word bitmaps through `BITS_TO_LONGS(nbits)`, while `bitmapFree()` optional-reset behavior remains direct Zig-only coverage because the C helper frees raw pointers in place

- `PHASE1_BITMAP_FIXTURE=zigux/tests/fixtures/phase1_helpers.json`
- `PHASE1_BITMAP_REVIEW=bitmap parity covers allocator-backed sizing, zero-allocation state, contiguous-range rendering, empty-bitmap buffer preservation, and truncation that preserves the terminator slot`
- `PHASE1_BITMAP_UNIT_REVIEW=bitmap allocation helpers keep bitmapFree optional handles null after release while shared parity covers allocator-backed sizing and zero-allocation state`
- `PHASE1_BITMAP_HEADER_ALIAS_UNIT_REVIEW=bitmap bitmap_zero bitmap_fill bitmap_copy bitmap_empty and bitmap_full stay aligned with zero fill copy empty and full for active-word clearing partial-tail fill masking copied-tail preservation and predicate results across the same declared bit window`
- `PHASE1_BITMAP_ALIAS_UNIT_REVIEW=bitmap underscore alias entry points preserve the same caller-selected window semantics as the camelCase helpers for weight bitwise range and formatting operations`
- `PHASE1_BITMAP_ALLOCATOR_ALIAS_UNIT_REVIEW=bitmap bitmap_alloc bitmap_zalloc and bitmap_free stay aligned with bitmapAlloc bitmapZalloc and bitmapFree for partial-word sizing zero-filled allocation and optional-handle reset semantics`
- `PHASE1_BITMAP_XOR_UNIT_REVIEW=bitmap xorBits multiword-tail coverage proves callers can clamp the last word back to the in-range bits without leaking the out-of-range tail`
- `PHASE1_BITMAP_TAIL_MASK_UNIT_REVIEW=bitmap tail-masked reduction helpers ignore out-of-range differences while preserving the in-range window for andBits, andNotBits, equal, intersects, and subset`
- `PHASE1_BITMAP_ZERO_BIT_UNIT_REVIEW=bitmap zero-length helper calls stay side-effect free so zero fill copy copyClearTail orBits xorBits scans and formatting leave caller-owned buffers untouched when nbits is zero`
- `PHASE1_BITMAP_EMPTY_UNIT_REVIEW=bitmap bitmap_scnprintf keeps a non-empty caller buffer untouched when no bits are set, matching the committed empty-bitmap parity fixture contract`

- `tools/lib/find_bit.zig` closure includes committed C-backed parity coverage for baseline set, zero, and shared-bit scans plus tail-clamped set, zero, and AND searches, including the mixed-tail case where one shared bit remains in range while another lives past `nbits`.
- `tools/lib/find_bit.zig` direct Zig unit coverage now keeps same-word zero-scan start masking aligned so inclusive starts can return the current zero, later starts skip earlier same-word zeros, and tail scans still clamp to `nbits`.
- `tools/lib/find_bit.zig` direct Zig unit coverage also keeps same-word set-scan start masking aligned so inclusive starts can return the current set bit, later starts skip earlier same-word matches, and tail scans still clamp to `nbits`.
- `tools/lib/find_bit.zig` direct Zig unit coverage also keeps same-word shared-bit start masking aligned so inclusive starts can return the current shared bit, later starts skip earlier same-word overlaps, and tail-clamped AND scans still stop at `nbits`.
- `tools/lib/find_bit.zig` direct Zig unit coverage also keeps exported mask and sizing helpers aligned with Linux-style boundaries so whole-word, partial-word, and wrapped-start calls stay reviewable without relying only on indirect scan behavior.
- `tools/lib/find_bit.zig` direct Zig unit coverage also keeps empty and out-of-range scan boundaries aligned by returning `nbits` for zero-length bitmaps, start-at-`nbits` searches, and fully set zero-bit windows that must not report past the declared range.
- `tools/lib/find_bit.zig` direct Zig unit coverage also keeps the underscore alias entry points aligned so `find_first_bit()`, `find_first_and_bit()`, `find_first_zero_bit()`, `find_next_bit()`, `find_next_and_bit()`, and `find_next_zero_bit()` preserve the same scan semantics as the camelCase helpers across the same caller-selected bit windows and tail clamps.
- `tools/lib/find_bit.zig` direct Zig unit coverage also keeps the low-level underscore entry points aligned so `_find_first_bit()`, `_find_first_and_bit()`, `_find_first_zero_bit()`, `_find_next_bit()`, `_find_next_and_bit()`, and `_find_next_zero_bit()` preserve same-word inclusive starts and tail-clamped scan behavior across the same caller-selected bit windows as the public helpers.
- `tools/lib/find_bit.zig` direct Zig unit coverage also keeps single-word set, zero, and shared-bit scans aligned with Linux small-bitmap semantics by masking out-of-range tail bits while preserving inclusive in-range matches inside one word.
- `tools/lib/find_bit.zig` direct Zig unit coverage also keeps tail-clamped set, zero, and shared-bit scans aligned when the inclusive start lands on the last in-range bit, while later starts still return `nbits` instead of leaking the out-of-range tail.
- `tools/lib/find_bit.zig` direct Zig unit coverage also keeps tail-clamped set, zero, and shared-bit scans aligned when the search starts exactly at the first tail-word bit index, so the first in-range tail match remains reachable without rereading an earlier full-word result.
- `tools/lib/find_bit.zig` direct Zig unit coverage also keeps zero-length set, zero, and shared-bit scans aligned by returning `0` even when backing words are populated, so declared `nbits` stays authoritative over caller storage.
- find_bit fixture authority: `zigux/tests/fixtures/phase1_helpers.json`
- find_bit manifest review anchor: `zigux/tests/fixtures/phase1_helper_manifest.json`
- find_bit direct unit-test anchor: `tools/lib/find_bit.zig:test "find next zero bit skips earlier matches in the same word"`
- find_bit set unit-test anchor: `tools/lib/find_bit.zig:test "find next bit skips earlier matches in the same word"`
- find_bit and unit-test anchor: `tools/lib/find_bit.zig:test "find next and bit skips earlier shared matches in the same word"`
- find_bit mask unit-test anchor: `tools/lib/find_bit.zig:test "word helpers keep linux-style mask and sizing boundaries"`
- find_bit boundary unit-test anchor: `tools/lib/find_bit.zig:test "empty and boundary scans return nbits"`
- find_bit alias unit-test anchor: `tools/lib/find_bit.zig:test "find underscore aliases preserve scan semantics"`
- find_bit low-level unit-test anchor: `tools/lib/find_bit.zig:test "find low-level underscore entry points preserve same-word and tail-clamped scan semantics"`
- find_bit small-bitmap unit-test anchor: `tools/lib/find_bit.zig:test "single-word scans keep linux small-bitmap semantics"`
- find_bit tail-start unit-test anchor: `tools/lib/find_bit.zig:test "tail scans keep the last in-range bit reachable from an inclusive start"`
- find_bit tail-word-boundary unit-test anchor: `tools/lib/find_bit.zig:test "tail scans honor an exact tail-word boundary start"`
- find_bit zero-sized unit-test anchor: `tools/lib/find_bit.zig:test "zero-sized scans ignore populated backing words"`

- `PHASE1_FIND_BIT_FIXTURE=zigux/tests/fixtures/phase1_helpers.json`
- `PHASE1_FIND_BIT_REVIEW=find_bit baseline set, zero, shared-bit, and tail-clamped scans ignore bits beyond nbits while preserving the in-range mixed-tail match`
- `PHASE1_FIND_BIT_UNIT_REVIEW=find_bit same-word zero-scan start masking keeps inclusive starts honest, skips earlier zero matches after the search advances, and still clamps tail results to nbits`
- `PHASE1_FIND_BIT_SET_UNIT_REVIEW=find_bit same-word set-scan start masking keeps inclusive starts honest, skips earlier same-word set matches after the search advances, and still clamps tail results to nbits`
- `PHASE1_FIND_BIT_AND_UNIT_REVIEW=find_bit same-word shared-bit start masking keeps inclusive starts honest, skips earlier same-word overlaps after the search advances, and still clamps tail AND results to nbits`
- `PHASE1_FIND_BIT_MASK_UNIT_REVIEW=find_bit mask and sizing helpers keep Linux-style whole-word, partial-word, and wrapped-start boundaries reviewable without relying only on indirect scan coverage`
- `PHASE1_FIND_BIT_BOUNDARY_UNIT_REVIEW=find_bit empty and out-of-range scans return nbits for zero-length bitmaps, start-at-nbits searches, and fully set zero-bit windows that must not report past the declared range`
- `PHASE1_FIND_BIT_ALIAS_UNIT_REVIEW=find_bit underscore alias entry points preserve the same set, shared-bit, and zero-bit scan semantics as the camelCase helpers across the same caller-selected bit windows and tail clamps`
- `PHASE1_FIND_BIT_LOW_LEVEL_UNIT_REVIEW=find_bit low-level underscore entry points preserve same-word inclusive starts and tail-clamped set, shared-bit, and zero-bit scan behavior across the same caller-selected bit windows as the public helpers`
- `PHASE1_FIND_BIT_SMALL_BITMAP_UNIT_REVIEW=find_bit single-word set zero and shared-bit scans keep Linux small-bitmap semantics aligned by masking out-of-range tail bits while preserving inclusive in-range matches inside one word`
- `PHASE1_FIND_BIT_TAIL_START_UNIT_REVIEW=find_bit tail-clamped set zero and shared-bit scans keep the last in-range bit reachable from an inclusive start while later starts still return nbits instead of leaking the out-of-range tail`
- `PHASE1_FIND_BIT_TAIL_WORD_BOUNDARY_UNIT_REVIEW=find_bit tail-clamped set zero and shared-bit scans keep the first in-range tail-word match reachable when the search starts exactly at the tail-word boundary instead of rereading an earlier full-word result`
- `PHASE1_FIND_BIT_ZERO_SIZED_UNIT_REVIEW=find_bit zero-length set zero and shared-bit scans return 0 even when backing words are populated so declared nbits stays authoritative over caller storage`

- `tools/lib/rbtree.zig` closure includes committed C-backed parity coverage for ordered forward and reverse traversal plus `replaceNode`, `eraseInit`, postorder traversal, and detached-node state checks, while Linux-style `rb_*` alias parity remains explicitly out of scope for this closed Phase 1 tranche.
- `tools/lib/rbtree.zig` direct Zig unit coverage keeps `findAdd` duplicate handling aligned so the first equal key stays resident while new distinct keys still link into the tree.
- `tools/lib/rbtree.zig` direct Zig unit coverage also keeps `find()`, `findFirst()`, and `nextMatch()` aligned so duplicate-key lookups start at the leftmost match and walk through the final equal node without drifting into a later key.
- `tools/lib/rbtree.zig` direct Zig unit coverage also keeps duplicate-key search aligned after `erase()` and same-key `replaceNode()` so `findFirst()`, `findLast()`, and duplicate-range iterators continue to report the surviving equal-key window in both directions.
- `tools/lib/rbtree.zig` direct Zig unit coverage also keeps `RootCached` leftmost tracking aligned so cached insert, erase, and replace helpers continue to expose the same first node as the underlying tree root.
- `tools/lib/rbtree.zig` direct Zig unit coverage also keeps `RootCached` duplicate minima aligned so erasing the first equal key promotes the next duplicate minimum while non-leftmost replacement leaves the cached first node unchanged.
- `tools/lib/rbtree.zig` direct Zig unit coverage also keeps `findAddCached()` aligned so equal-key probes return the original resident node, distinct inserts still link into the cached tree, and `RootCached` continues to expose the same leftmost node as the underlying tree root.
- `tools/lib/rbtree.zig` direct Zig review notes keep the remaining `rb_*` alias gap explicit so the closed Phase 1 tranche cannot be misread as already covering the header-level alias surface.
- `tools/lib/rbtree.zig` direct Zig closure validation also fails closed if `tools/lib/rbtree.zig` grows Linux-style `rb_*` aliases before this closed Phase 1 tranche is deliberately reopened.
- `tools/lib/rbtree.zig` direct Zig unit coverage also keeps `iterateMatches()` aligned so duplicate-key iteration yields only the equal-key range and cleanly reports no match for missing keys.
- `tools/lib/rbtree.zig` direct Zig unit coverage also keeps `findLast()`, `prevMatch()`, and `iterateMatchesReverse()` aligned so reverse duplicate-key lookups start at the rightmost match, walk back through the equal-key range, and cleanly report no match for missing keys.
- `tools/lib/rbtree.zig` direct Zig unit coverage also keeps `iteratePostorder()` aligned so the explicit iterator visits each node exactly once in left-right-root order and reports exhaustion cleanly after the full walk.
- `tools/lib/rbtree.zig` direct Zig unit coverage also keeps `iteratePostorderSafe()` aligned by caching exactly one step ahead so callers can invalidate the current node without truncating the remaining postorder walk.
- `tools/lib/rbtree.zig` direct Zig unit coverage also keeps `iteratePostorderSafe()` aligned across erase-driven rebalancing so the walk still reaches each remaining node exactly once after the current node is removed.
- rbtree fixture authority: `zigux/tests/fixtures/phase1_helpers.json`
- rbtree manifest review anchor: `zigux/tests/fixtures/phase1_helper_manifest.json`
- rbtree direct unit-test anchor: `tools/lib/rbtree.zig:test "rbtree findAdd keeps the first duplicate and inserts new keys"`
- rbtree search unit-test anchor: `tools/lib/rbtree.zig:test "rbtree nextMatch walks the duplicate range in order"`
- rbtree duplicate-search unit-test anchor: `tools/lib/rbtree.zig:test "rbtree duplicate search stays aligned after erase and same-key replace"`
- rbtree cached-root unit-test anchor: `tools/lib/rbtree.zig:test "rbtree cached root keeps leftmost in sync across add erase and replace"`
- rbtree cached duplicate-minima unit-test anchor: `tools/lib/rbtree.zig:test "rbtree cached root tracks duplicate minima through erase and non-leftmost replace"`
- rbtree cached findAdd unit-test anchor: `tools/lib/rbtree.zig:test "rbtree findAddCached preserves duplicate ownership and leftmost cache"`
- rbtree iterator unit-test anchor: `tools/lib/rbtree.zig:test "rbtree iterateMatches streams only the duplicate range"`
- rbtree reverse unit-test anchor: `tools/lib/rbtree.zig:test "rbtree iterateMatchesReverse streams only the duplicate range in reverse"`
- rbtree postorder iterator unit-test anchor: `tools/lib/rbtree.zig:test "rbtree iteratePostorder streams the full postorder walk once"`
- rbtree postorder safe unit-test anchor: `tools/lib/rbtree.zig:test "rbtree iteratePostorderSafe survives erase-driven rebalancing"`
- rbtree postorder safe rebalance unit-test anchor: `tools/lib/rbtree.zig:test "rbtree iteratePostorderSafe survives erase-driven rebalancing"`

- `PHASE1_RBTREE_FIXTURE=zigux/tests/fixtures/phase1_helpers.json`
- `PHASE1_RBTREE_REVIEW=rbtree parity covers ordered traversal, replaceNode, eraseInit, postorder traversal, and detached-node state while Linux-style rb_* alias parity remains explicitly out of scope for this closed tranche`
- `PHASE1_RBTREE_UNIT_REVIEW=rbtree findAdd keeps the first equal key resident while new distinct keys still link into the tree`
- `PHASE1_RBTREE_SEARCH_UNIT_REVIEW=rbtree find, findFirst, and nextMatch keep duplicate-key lookup walks aligned from the leftmost match through the final equal node`
- `PHASE1_RBTREE_DUPLICATE_SEARCH_UNIT_REVIEW=rbtree duplicate-key search stays aligned after erase and same-key replace so findFirst, findLast, and duplicate-range iterators report the surviving equal-key window in both directions`
- `PHASE1_RBTREE_CACHED_UNIT_REVIEW=rbtree RootCached leftmost tracking stays aligned across addCached, eraseCached, and replaceNodeCached so the cached first node matches the underlying tree root`
- `PHASE1_RBTREE_CACHED_DUPLICATE_UNIT_REVIEW=rbtree RootCached duplicate minima stay aligned when eraseCached promotes the next equal-key minimum and replaceNodeCached leaves the cached first node unchanged for non-leftmost replacement`
- `PHASE1_RBTREE_CACHED_FINDADD_UNIT_REVIEW=rbtree findAddCached returns the original equal-key resident node, still links new distinct keys into the cached tree, and keeps the cached first node aligned with the underlying tree root`
- `PHASE1_RBTREE_ITERATE_UNIT_REVIEW=rbtree iterateMatches yields only the equal-key duplicate range and cleanly reports no match for missing keys`
- `PHASE1_RBTREE_REVERSE_UNIT_REVIEW=rbtree findLast, prevMatch, and iterateMatchesReverse keep reverse duplicate-key lookup walks aligned from the rightmost match back through the equal-key range while still reporting no match for missing keys`
- `PHASE1_RBTREE_POSTORDER_ITERATOR_UNIT_REVIEW=rbtree iteratePostorder visits each node exactly once in left-right-root order and reports exhaustion cleanly after the full walk`
- `PHASE1_RBTREE_POSTORDER_SAFE_UNIT_REVIEW=rbtree iteratePostorderSafe caches exactly one step ahead so callers can invalidate the current node without truncating the remaining postorder walk`
- `PHASE1_RBTREE_POSTORDER_SAFE_REBALANCE_UNIT_REVIEW=rbtree iteratePostorderSafe stays aligned across erase-driven rebalancing so the walk still reaches each remaining node exactly once after the current node is removed`
- `PHASE1_RBTREE_ALIAS_GAP_NOTE=the closed Phase 1 rbtree tranche still excludes Linux-style rb_* alias parity for the already-ported entry points, and that remaining surface stays explicitly out of scope until a later bounded repair lands`
- `PHASE1_RBTREE_ALIAS_GAP_GATE=phase1 closure validation fails closed if tools/lib/rbtree.zig grows Linux-style rb_* aliases before the closed helper tranche is deliberately reopened`

- `tools/lib/string.zig` closure includes committed C-backed parity coverage for Linux-style bool parsing, C-string-aware `strlcpy` length and truncation behavior, in-place whitespace and replacement helpers including embedded-NUL `remove_spaces` handling, and first-mismatch `memchrInv` detection.
- `tools/lib/string.zig` direct Zig unit coverage also keeps `strlcpy` aligned with C-string semantics by stopping at the first embedded NUL, preserving truncation behavior, and leaving zero-sized destinations untouched.
- `tools/lib/string.zig` direct Zig unit coverage also keeps `strscpy` aligned with bounded kernel copy semantics for exact-fit, truncation, embedded-NUL, and zero-sized destination cases.
- `tools/lib/string.zig` direct Zig unit coverage also keeps `strEq()` and `streq()` aligned with C-string equality semantics for exact, empty, length-mismatched, case-sensitive, and embedded-NUL comparisons.
- `tools/lib/string.zig` direct Zig unit coverage also keeps `sysfsStreq()` and `sysfs_streq()` aligned by treating a single trailing newline as equivalent to C-string termination while still rejecting non-terminal newline and content mismatches.
- `tools/lib/string.zig` direct Zig unit coverage keeps `memchrInv` honest for both aligned and misaligned long buffers beyond the short C-backed fixture cases.
- `tools/lib/string.zig` direct Zig unit coverage also keeps `trimSpaces` and `strim` aligned with C-string semantics by trimming trailing whitespace that appears before the first embedded NUL while preserving bytes beyond that terminator.
- `tools/lib/string.zig` direct Zig unit coverage also keeps `strStarts` and `strstarts` aligned with kernel-style prefix semantics for exact, empty-prefix, shorter-input, and case-sensitive comparisons.
- `tools/lib/string.zig` direct Zig unit coverage also keeps `strHasPrefix` and `str_has_prefix` aligned by returning the matched C-string prefix length for exact and embedded-NUL prefixes while rejecting mismatches and longer prefixes.
- `tools/lib/string.zig` direct Zig unit coverage also keeps `strEndsWith`, `str_ends_with`, and `strends` aligned with kernel-style suffix semantics for exact, empty-suffix, shorter-input, and case-sensitive comparisons.
- `tools/lib/string.zig` direct Zig unit coverage also keeps the local `memparse()` parser contract aligned by preserving decimal, hexadecimal, suffix-bearing, invalid, and binary-unit-tail inputs including optional trailing B forms without changing the parsed value or rest pointer contract.
- `tools/lib/string.zig` direct Zig unit coverage also keeps `memparse()` binary-unit-tail replays aligned so `KiB` and optional trailing `B` forms preserve the same parsed value and rest pointer contract as the base suffix cases already recorded in the closure validator.
- string fixture authority: `zigux/tests/fixtures/phase1_helpers.json`
- string manifest review anchor: `zigux/tests/fixtures/phase1_helper_manifest.json`
- string c-string unit-test anchor: `tools/lib/string.zig:test "strlcpy stops at the first embedded NUL in the source"`
- string strscpy unit-test anchor: `tools/lib/string.zig:test "strscpy mirrors bounded kernel copy semantics"`
- string equality unit-test anchor: `tools/lib/string.zig:test "streq matches C-string equality semantics"`
- string sysfs unit-test anchor: `tools/lib/string.zig:test "sysfsStreq treats a trailing newline as equivalent to C-string termination"`
- string direct unit-test anchor: `tools/lib/string.zig:test "memchrInv scans aligned and misaligned long buffers"`
- string alias unit-test anchor: `tools/lib/string.zig:test "trimSpaces and strim trim trailing whitespace before an embedded NUL"`
- string prefix unit-test anchor: `tools/lib/string.zig:test "strstarts matches kernel prefix semantics"`
- string prefix-length unit-test anchor: `tools/lib/string.zig:test "strHasPrefix returns the matched prefix length with C-string semantics"`
- string suffix unit-test anchor: `tools/lib/string.zig:test "str_ends_with matches kernel suffix semantics"`
- string memparse unit-test anchor: `tools/lib/string.zig:test "memparse preserves the header-level string helper contract"`

- `PHASE1_STRING_FIXTURE=zigux/tests/fixtures/phase1_helpers.json`
- `PHASE1_STRING_REVIEW=string parity covers Linux-style bool parsing for true, false, and invalid forms, C-string-aware strlcpy length and truncation behavior, whitespace cleanup including embedded-NUL remove_spaces handling, replacement, and memchrInv mismatch detection`
- `PHASE1_STRING_CSTRING_UNIT_REVIEW=string strlcpy stops at the first embedded NUL, preserves truncation behavior, and leaves zero-sized destinations untouched`
- `PHASE1_STRING_STRSCPY_UNIT_REVIEW=string strscpy keeps bounded kernel copy semantics aligned for exact-fit, truncation, embedded-NUL, and zero-sized destination cases`
- `PHASE1_STRING_EQUALITY_UNIT_REVIEW=string strEq and streq keep C-string equality aligned for exact, empty, length-mismatched, case-sensitive, and embedded-NUL comparisons`
- `PHASE1_STRING_SYSFS_UNIT_REVIEW=string sysfsStreq and sysfs_streq treat a single trailing newline as equivalent to C-string termination while still rejecting non-terminal newline and content mismatches`
- `PHASE1_STRING_UNIT_REVIEW=string memchrInv aligned and misaligned long-buffer scans stay consistent beyond the short C-backed fixture cases`
- `PHASE1_STRING_ALIAS_UNIT_REVIEW=string trimSpaces and strim trim trailing whitespace before the first embedded NUL while preserving bytes beyond that terminator`
- `PHASE1_STRING_PREFIX_UNIT_REVIEW=string strStarts and strstarts keep kernel-style prefix checks aligned for exact, empty-prefix, shorter-input, and case-sensitive comparisons`
- `PHASE1_STRING_PREFIX_LENGTH_UNIT_REVIEW=string strHasPrefix and str_has_prefix return the matched C-string prefix length for exact and embedded-NUL prefixes while rejecting mismatches and longer prefixes`
- `PHASE1_STRING_SUFFIX_UNIT_REVIEW=string strEndsWith, str_ends_with, and strends keep kernel-style suffix semantics aligned for exact, empty-suffix, shorter-input, and case-sensitive comparisons`
- `PHASE1_STRING_MEMPARSE_UNIT_REVIEW=string memparse preserves decimal, hexadecimal, suffix-bearing, invalid, and binary-unit-tail inputs including optional trailing B forms without changing the parsed value or rest pointer contract`

## Closure Gates

Phase 1 is only considered closed when all of the following are green:

1. parity gate
- `python3 scripts/zigux/check-phase1-parity.py`

2. parity checker self-test
- `python3 scripts/zigux/check-phase1-parity.py --self-test`

3. helper unit gate
- `zig build test --build-file zigux/tests/build.zig`

4. helper benchmark smoke
- `zig build bench --build-file zigux/tests/build.zig`

5. benchmark validation
- `python3 scripts/zigux/check-phase1-bench.py`

6. benchmark checker self-test
- `python3 scripts/zigux/check-phase1-bench.py --self-test`

7. closure validation
- `python3 scripts/zigux/validate-phase1-closure.py`

8. closure validator self-test
- `python3 scripts/zigux/validate-phase1-closure.py --self-test`

9. workflow viability
- the bootstrap workflow must not rely on deprecated Node 20 action execution
- the bootstrap workflow must pin current action releases where available

- `PHASE1_PARITY_GATE=python3 scripts/zigux/check-phase1-parity.py`
- `PHASE1_PARITY_SELF_TEST_GATE=python3 scripts/zigux/check-phase1-parity.py --self-test`
- `PHASE1_UNIT_GATE=zig build test --build-file zigux/tests/build.zig`
- `PHASE1_BENCH_GATE=zig build bench --build-file zigux/tests/build.zig`
- `PHASE1_BENCH_CHECK_GATE=python3 scripts/zigux/check-phase1-bench.py`
- `PHASE1_BENCH_SELF_TEST_GATE=python3 scripts/zigux/check-phase1-bench.py --self-test`
- `PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py`
- `PHASE1_CLOSURE_SELF_TEST_GATE=python3 scripts/zigux/validate-phase1-closure.py --self-test`

## Performance Policy

Phase 1 does not enforce hard CI timing thresholds yet.

That is intentional.

Host-side helper timing is too sensitive to hosted runner drift to make nanosecond thresholds trustworthy at this stage.

Instead, Phase 1 uses:

- a benchmark smoke executable for representative helper paths
- representative bitmap smoke for weight, tail-window bitwise ops, tail-sensitive copy and `copyClearTail` replay, plus empty-bitmap buffer-preservation and truncation-aware range rendering checks
- stable checksum and iteration outputs so the benchmark cannot silently optimize away the hot loops
- machine-readable benchmark expectations in `zigux/tests/fixtures/phase1_bench_expectations.json`
- manual review of timing deltas before expanding helper scope

- `PHASE1_BITMAP_BENCH_REVIEW=bitmap benchmark smoke pins deterministic weight, tail-window bitwise, tail-sensitive copy, and range-rendering checksums so helper-local regressions cannot hide behind a broad positive bench result`
- `PHASE1_BITMAP_BENCH_KEYS=PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM,PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM,PHASE1_BENCH_BITMAP_COPY_CHECKSUM,PHASE1_BENCH_BITMAP_SCNPRINTF_CHECKSUM`
- `PHASE1_BITMAP_BENCH_ITERATIONS=PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS,PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS,PHASE1_BENCH_BITMAP_COPY_ITERATIONS,PHASE1_BENCH_BITMAP_SCNPRINTF_ITERATIONS`
- `PHASE1_FIND_BIT_BENCH_REVIEW=find_bit benchmark smoke pins deterministic next-bit, whole-family, tail-window, same-word, zero-bit, and shared-bit scan checksums plus the live loop counts so helper-local scan regressions cannot hide behind a generic positive checksum or a silently shrunk workload`
- `PHASE1_FIND_BIT_BENCH_KEYS=PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM,PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM,PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM,PHASE1_BENCH_FIND_SAME_WORD_CHECKSUM,PHASE1_BENCH_FIND_NEXT_ZERO_BIT_CHECKSUM,PHASE1_BENCH_FIND_NEXT_AND_BIT_CHECKSUM`
- `PHASE1_FIND_BIT_BENCH_ITERATIONS=PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS,PHASE1_BENCH_FIND_SAME_WORD_ITERATIONS,PHASE1_BENCH_FIND_NEXT_ZERO_BIT_ITERATIONS,PHASE1_BENCH_FIND_NEXT_AND_BIT_ITERATIONS`
- `PHASE1_STRING_BENCH_REVIEW=string benchmark smoke pins deterministic bool-trim, cstring/sysfs, memchr, compare, and memparse checksum surfaces plus the live loop count so string regressions cannot hide behind the broader string checksum alone`
- `PHASE1_STRING_BENCH_KEYS=PHASE1_BENCH_STRING_CHECKSUM,PHASE1_BENCH_STRING_BOOL_TRIM_CHECKSUM,PHASE1_BENCH_STRING_CSTRING_CHECKSUM,PHASE1_BENCH_STRING_MEMCHR_CHECKSUM,PHASE1_BENCH_STRING_COMPARE_CHECKSUM,PHASE1_BENCH_STRING_MEMPARSE_CHECKSUM`
- `PHASE1_STRING_BENCH_ITERATIONS=PHASE1_BENCH_STRING_ITERATIONS`
- `PHASE1_RBTREE_BENCH_REVIEW=rbtree benchmark smoke pins ordered traversal, duplicate-range, cached-leftmost, findAdd, and postorder-safe checksum surfaces so duplicate-owner and erase-while-walking regressions cannot hide behind the broader tree checksum alone`
- `PHASE1_RBTREE_BENCH_KEYS=PHASE1_BENCH_RBTREE_CHECKSUM,PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM,PHASE1_BENCH_RBTREE_CACHED_CHECKSUM,PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM,PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM`

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