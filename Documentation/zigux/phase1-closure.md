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

This is part of closure because a closed validation tranche that is about to stop executing is not actually closed.

## Shared Review Packet

The closed Phase 1 host-tools packet also stays reviewable through these shared product surfaces:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/Makefile`
- `python3 scripts/zigux/validate-phase1-closure.py`

Reviewers should treat drift across those packet summaries, the bootstrap workflow replay, and the validator-first replay route as a closure regression even when the helper code itself is unchanged.

## Find Bit Review Rule

For `tools/lib/find_bit.zig`, reviewers must also keep the helper-local single-word next-scan proof explicit through:

- `tools/lib/find_bit.zig`

That means `test "single-word next scans honor start masks"` stays present and review-visible whenever `findNextBit()`, `findNextZeroBit()`, or `findNextAndBit()` changes. The shared Phase 1 parity fixture already locks the cross-word and tail-clamped `find_bit` results, but it does not isolate the same-word `start` masking path, so this helper-local test is the bounded proof that one-word scans still honor caller-selected start masks instead of re-reading earlier bits.

- `PHASE1_FIND_BIT_SINGLE_WORD_REVIEW=helper-local single-word next-scan proof stays explicit through the direct find_bit test anchor because the shared Phase 1 parity fixture does not isolate same-word start-mask behavior`

For `tools/lib/find_bit.zig`, reviewers must also keep the helper-local inclusive boundary proof explicit through:

- `tools/lib/find_bit.zig`

That means `test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"` stays present and review-visible whenever `findNextBit()`, `findNextZeroBit()`, or `findNextAndBit()` changes. This helper-local test is the bounded proof that same-word next scans still keep the last live head-word bit reachable when the caller starts exactly on that in-range boundary instead of skipping forward into the next word.

- `PHASE1_FIND_BIT_INCLUSIVE_BOUNDARY_REVIEW=helper-local inclusive boundary proof stays explicit through the direct find_bit test anchor so same-word next scans keep the last in-range head-word bit reachable from an inclusive start`

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

The helper-local `bitmap.scnprintf()` truncation proof must also stay explicit through:

- `tools/lib/bitmap.zig`

That means `test "bitmap scnprintf reports full length while truncating the buffer"` stays present and review-visible whenever `bitmap.scnprintf()` changes. The shared Phase 1 parity fixture only locks the full rendered range string, so this helper-local test is the bounded proof that shorter caller buffers still receive the full logical length while preserving NUL-terminated truncation.

- `PHASE1_BITMAP_SCNPRINTF_TRUNCATION_REVIEW=helper-local bitmap.scnprintf truncation proof stays explicit through the direct bitmap test anchor because the shared Phase 1 parity fixture only locks the full rendered range string`

The helper-local bitmap copy alias proof must also stay explicit through:

- `tools/lib/bitmap.zig`

That means `test "bitmap copy aliases preserve tail clearing and extension semantics"` stays present and review-visible whenever `bitmap_copy_clear_tail()` or `bitmap_copy_and_extend()` changes. This helper-local test is the bounded proof that the alias entrypoints preserve last-word tail masking and zero-filled extension instead of drifting away from `copyClearTail()` and `copyAndExtend()`.

- `PHASE1_BITMAP_COPY_ALIAS_REVIEW=helper-local bitmap copy alias proof stays explicit through the direct bitmap test anchor so bitmap_copy_clear_tail and bitmap_copy_and_extend preserve tail masking and zero-filled extension semantics`

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
