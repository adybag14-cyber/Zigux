# Phase 5 Kfifo Next Safe Step

This note records one bounded same-packet follow-through for the roadmap's `samples/kfifo/bytestream-example.c` anchor.

## Status

- `PHASE5_STATUS=next-safe-step-recorded`
- `PHASE5_LANE_KEY=P5-Y02`
- `PHASE5_SLICE=kfifo-focused-test-contract-sync`
- scope: keep the bytestream packet truthful and narrowly routed through one focused test repair only

## Current repo evidence on `master`

Current readback for the non-runtime bytestream packet shows:

- `samples/zigux/bytestream_fifo.zig` still exposes a ten-item `BytestreamFifoSample.reviewContract().focus` order: `bounded_fifo_order`, `wraparound_requeue`, `peek_and_skip`, `non_destructive_snapshot`, `preview_truncation`, `remaining_capacity`, `queue_shape_boundaries`, `helper_boundaries`, `reset_and_replay`, and `ownership_and_lifetime`
- `Documentation/zigux/phase5-kfifo-sample-survey.md` still repeats that same ten-cue order and the current reviewed packet posture
- `zigux/tests/phase5_bytestream_fifo_manifest.json` still points at the same bytestream packet and already describes the queue-shape and helper-boundary evidence surfaces
- `zigux/tests/phase5_bytestream_fifo.zig` still asserts the older eight-item contract by keeping `contract.focus.len == 8` and jumping from `remaining_capacity` straight to `reset_and_replay` and `ownership_and_lifetime`
- `zigux/tests/phase5_build.zig` still wires the sample, focused test, and survey replay into one Phase 5 build route

## Next safe step

The smallest safe follow-through is one focused packet repair:

1. update only `zigux/tests/phase5_bytestream_fifo.zig`
2. change the expected review-contract length from `8` to `10`
3. add `queue_shape_boundaries` and `helper_boundaries` at indexes `6` and `7`
4. shift `reset_and_replay` and `ownership_and_lifetime` to indexes `8` and `9`
5. rerun `zig build test --build-file zigux/tests/phase5_build.zig --summary all`

## Why this stays bounded

This follow-through does not need:

- sample-behavior changes in `samples/zigux/bytestream_fifo.zig`
- manifest rewrites in `zigux/tests/phase5_bytestream_fifo_manifest.json`
- shared Phase 5 guide, README, runtime, or other sample-family edits

## Non-goals

This note does not reopen:

- procfs parity
- `kfifo_from_user()` or `kfifo_to_user()` parity
- loadable module registration
- locking or blocking semantics
