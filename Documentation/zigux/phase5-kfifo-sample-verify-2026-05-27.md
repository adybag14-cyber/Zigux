# Phase 5 Kfifo Sample Verification 2026-05-27

Lane: `P5-L03`
Phase: `Phase 5`
Anchor: `samples/kfifo/bytestream-example.c`
Sample under check: `samples/zigux/bytestream_fifo.zig`
Window companion under check: `samples/zigux/bytestream_fifo_window_contract.zig`
Focused replay packet checked: `zigux/tests/phase5_bytestream_fifo.zig`

## Why this note exists

This lane was scoped to verify the current kfifo-style sample behavior and record the exact checks that were exercised, without widening into unrelated Phase 5 sample work.

The roadmap and current repo state already expose a bounded bytestream FIFO sample packet, so the highest-value step for this run was verification evidence rather than another new helper or survey variant.

## Commands run on 2026-05-27

The checks were rerun locally with the bundled Zig toolchain archive `zig-x86_64-linux-0.17.0-dev.87+9b177a7d2`.

1. `zig test samples/zigux/bytestream_fifo.zig`
2. `zig test samples/zigux/bytestream_fifo_window_contract.zig`
3. `zig test --dep bytestream_fifo_sample -Mroot=zigux/tests/phase5_bytestream_fifo.zig -Mbytestream_fifo_sample=samples/zigux/bytestream_fifo.zig`

Observed result summary:

- sample-owned self-check route: `4/4` tests passed
- window-contract companion route: `2/2` tests passed
- focused replay route: `3/3` tests passed in the narrow replay mirror used for this verification run

## Exact behavior checks recorded

### Sample-owned self-check route

The sample-root self-check packet passed with these exact anchors visible in code and exercised by `zig test samples/zigux/bytestream_fifo.zig`:

- descriptor keeps `name = "bytestream_fifo"`, `anchor = "samples/kfifo/bytestream-example.c"`, `requires_runtime_substrate = false`, `provides_selfcheck = true`, and `StorageBacking.embedded_fixed_buffer`
- `runAnchorReplay()` keeps `len_after_initial_fill = 15`
- the first drain still yields `"hello"`
- the second drain still yields `{ 0, 1 }`
- the final drain length still lands at `32`
- the final drain sequence still matches `{ 3, 4, 5, 6, 7, 8, 9, 0, 1, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42 }`
- `runPreviewBoundaryReplay()` still keeps `snapshot_prefix = { 2, 3, 4, 5 }`, `preview_prefix = { 2, 3, 4, 5, 6, 7, 8, 9 }`, `preview_total_visible = 10`, `queue_len_after_preview = 10`, and `available_after_preview = 22`
- the preview boundary still keeps `head_index = 7`, `tail_index = 17`, `first_window_len = 10`, `second_window_len = 0`, and `wraps = false`
- `runWrappedPreviewReplay()` still keeps `drained_prefix = "hell"`, `refill_values = { 200, 201, 202, 203 }`, and the wrapped visible split `{ 28, 4 }`
- the wrapped-full preview boundary still keeps `head_index = 4`, `tail_index = 4`, `total_visible = 32`, `available_after_preview = 0`, and `wraps = true`
- `runReinitBoundaryReplay()` still keeps `init_runs_after_reinit = 2`, `exit_runs_after_first_exit = 1`, `exit_runs_after_second_exit = 2`, `available_after_reinit = 32`, and the second replay final sequence equal to the anchor result
- `runRemainingCapacityReplay()` still keeps `available_after_init = 32`, `available_after_hello = 27`, `available_when_full = 0`, `available_after_skip = 1`, `available_after_wrap_refill = 0`, and `available_after_partial_drain = 8`
- the partial-drain wrapped boundary still keeps `queue_len_after_partial_drain = 24`, `head_index = 9`, `tail_index = 1`, `first_window_len = 23`, `second_window_len = 1`, and `wraps = true`
- `runPartialEnqueueBoundaryReplay()` still keeps `queue_len_before_extra = 30`, `available_before_extra = 2`, `requested_extra_len = 4`, `copied_extra_len = 2`, `dropped_extra_len = 2`, `queue_len_after_extra = 32`, and `available_after_extra = 0`
- the helper boundary still keeps the short-drain split `"hel"` then `"lo"`
- post-exit replay rejection still stays in place through `error.InvalidLifecycleTransition`

### Window-contract companion route

The queue-window companion passed with these exact fixed shapes exercised by `zig test samples/zigux/bytestream_fifo_window_contract.zig`:

- visible window `preview_after_skip_and_requeue`: `head_index = 7`, `tail_index = 17`, `total_visible = 10`, `first_window_len = 10`, `second_window_len = 0`, `wraps = false`
- visible window `wrapped_full_after_refill`: `head_index = 4`, `tail_index = 4`, `total_visible = 32`, `first_window_len = 28`, `second_window_len = 4`, `wraps = true`
- visible window `partial_drain_after_wrap_refill`: `head_index = 9`, `tail_index = 1`, `total_visible = 24`, `first_window_len = 23`, `second_window_len = 1`, `wraps = true`
- writable window `preview_after_skip_and_requeue`: `tail_index = 17`, `writable_count = 22`, `first_window_len = 15`, `second_window_len = 7`, `wraps = true`
- writable window `wrapped_full_after_refill`: `tail_index = 4`, `writable_count = 0`, `first_window_len = 0`, `second_window_len = 0`, `wraps = false`
- writable window `partial_drain_after_wrap_refill`: `tail_index = 1`, `writable_count = 8`, `first_window_len = 8`, `second_window_len = 0`, `wraps = false`
- `preview_is_non_destructive`, `wrapped_preview_is_non_destructive`, `rollover_refill_required_for_wrap`, `visible_windows_never_exceed_two`, and `writable_windows_never_exceed_two` all remain true

### Focused replay route

The focused replay packet passed with these exact checks exercised by `zig test --dep bytestream_fifo_sample -Mroot=zigux/tests/phase5_bytestream_fifo.zig -Mbytestream_fifo_sample=samples/zigux/bytestream_fifo.zig`:

- lane contract still keeps the sample non-runtime and fixed-buffer-backed
- replay transfer counts still keep `initial_string_copy_count = 5`, `first_drain_count = 5`, `second_drain_count = 2`, and `requeue_count = 2`
- the replay boundary still keeps `skipped_byte = 2`, `peek_value = 3`, `preview_len = 8`, `preview_total_visible = 32`, and `preview_truncated = true`
- the replay boundary still keeps `fill_start = 20` and `fill_end = 42`
- the final replay sequence still matches the anchored 32-byte drain result
- reinit-after-exit reuse still leaves `module.stage() = exited`, `module.init_runs = 2`, `module.exit_runs = 2`, and `module.available() = 32`

## Scope note

This run did not widen into the broader Phase 5 survey-note lane. It only re-verified the current bytestream sample behavior and recorded exact checks for the present sample packet.

It also did not claim a standalone Phase 5 bitmap sample or any runtime-owned registration, procfs, user-copy, or locking semantics.

## Next bounded step

If this lane is revisited, the next bounded step is to refresh the existing Phase 5 kfifo survey note so its dated verification snapshot reflects the same exact check values that were rerun here on 2026-05-27, without reopening unrelated sample families.
