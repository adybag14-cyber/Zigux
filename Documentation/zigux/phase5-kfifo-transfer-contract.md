# Phase 5 Kfifo Transfer Contract

This note records the bounded Phase 5 transfer-contract companion for the roadmap's `samples/kfifo/bytestream-example.c` anchor.

## Scope

- lane family: `Phase 5` sample packet for the non-runtime bytestream FIFO anchor
- sample-root companion: `samples/zigux/bytestream_fifo_transfer_contract.zig`
- focused replay route: `zig test --dep bytestream_fifo_transfer_contract -Mroot=zigux/tests/phase5_bytestream_fifo_transfer_contract.zig -Mbytestream_fifo_transfer_contract=samples/zigux/bytestream_fifo_transfer_contract.zig`

## Why this companion exists

The main bytestream sample already carries the queue lifecycle, preview, window-shape, remaining-capacity, and reinit boundaries. This companion keeps the Linux-style transfer packet explicit in one smaller place so reviewers can recheck the anchor's exact copy and drain cues without rereading the broader sample file.

Keep this companion framed as reviewability help for the existing Phase 5 sample family, not as a fifth sample:

- `initial_string_copy_count = 5` and `len_after_initial_fill = 15`
- first drain is `"hello"` with `first_drain_count = 5`
- second drain is `{ 0, 1 }` with `second_drain_count = 2` and `requeue_count = 2`
- `skipped_byte = 2` and `peek_value = 3`
- preview prefix remains `{ 3, 4, 5, 6, 7, 8, 9, 0 }` with `preview_len = 8` and `preview_total_visible = 32`
- short-drain behavior stays `"hel"` followed by queued `"lo"`
- partial `enqueueSlice()` truncation stays bounded at `requested = 4`, `copied = 2`, and `dropped = 2`
- the companion continues to state that the sample remains non-runtime, self-checking, and fixed-buffer-backed

## Boundaries

- keep procfs, user-copy, locking, and runtime registration out of scope
- keep queue-window shape proof in `samples/zigux/bytestream_fifo_window_contract.zig`
- keep full replay and lifecycle proof in `samples/zigux/bytestream_fifo.zig` and `zigux/tests/phase5_bytestream_fifo.zig`
