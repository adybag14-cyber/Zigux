# Phase 5 Kfifo Current Verification

This note records the latest current-`master` verification status I could confirm for the shipped Phase 5 `samples/zigux/bytestream_fifo.zig` packet.

## Scope

- sample under test: `samples/zigux/bytestream_fifo.zig`
- roadmap anchor: `samples/kfifo/bytestream-example.c`
- packet-level survey note still owned separately by `Documentation/zigux/phase5-kfifo-sample-survey.md`
- sample blob inspected on current `master`: `91dd0b38844712d73c272eda5b0f084c2c588a2c`
- verification date: `2026-05-09`
- toolchain for the last sample-only scratch replay route: `0.17.0-dev.87+9b177a7d2`

## Exact commands tracked for the sample-only scratch route

- `zig fmt --check samples/zigux/bytestream_fifo.zig`
- `zig test samples/zigux/bytestream_fifo.zig`

## Result

Live current-`master` readback now shows that the shipped sample exposes `6/6` direct self-checks, including the wrapped-preview replay that was not listed in the older five-test snapshot:

1. `bytestream fifo sample replays the Linux anchor result sequence`
2. `bytestream fifo sample keeps bounded helper behavior without runtime claims`
3. `bytestream fifo sample keeps preview truncation explicit`
4. `bytestream fifo sample keeps wrapped preview truncation non-destructive`
5. `bytestream fifo sample exposes empty full and wrapped state boundaries explicitly`
6. `bytestream fifo sample makes ownership and lifetime boundaries explicit`

I could not honestly rerun the repo-local scratch route in this workspace today because there is still no writable Zigux checkout here, so this note is a current-`master` truthfulness refresh based on exact file readback rather than a fresh local replay claim.

## Exact checks observed

- the descriptor still names `samples/kfifo/bytestream-example.c`, keeps `requires_runtime_substrate = false`, keeps `provides_selfcheck = true`, and keeps `StorageBacking.embedded_fixed_buffer` explicit
- the anchor replay still reaches `len_after_initial_fill = 15`
- the first drain still yields `"hello"`
- the second drain still yields `{ 0, 1 }`, and those same bytes are still re-enqueued at the tail
- skipping the next byte still removes `2`, and peeking afterward still observes `3`
- the preview boundary still reports `snapshot_prefix = { 2, 3, 4, 5 }`, `preview_prefix = { 2, 3, 4, 5, 6, 7, 8, 9 }`, `preview_total_visible = 10`, and `queue_len_after_preview = 10`
- the wrapped preview boundary still drains `"hell"`, refills `{ 200, 201, 202, 203 }`, keeps `snapshot_prefix = { 'o', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 }`, keeps `preview_prefix = { 'o', 0, 1, 2, 3, 4, 5, 6 }`, still reports `preview_total_visible = 32`, and preserves the wrapped split after the refill rollover without mutating queue state
- the non-destructive snapshot and final drain still match `[3,4,5,6,7,8,9,0,1,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42]`
- the bounded helper replay still keeps empty peek and skip at `null`, rejects overflow at the 32-byte capacity, and restores an empty queue after reset
- the short-drain helper replay still yields `"hel"`, preserves the queued `"lo"` remainder, and returns `0` on the empty follow-up drain
- the queue-shape replay still keeps the bounded empty/full and rollover cues explicit, including the wrapped refill state after skip-at-capacity plus refill
- the lifetime path still stays `cold -> initialized -> replay_complete -> exited`

## Current limit

This was a current-`master` file-readback refresh, not a new repo-local scratch replay. I could not honestly rerun `zig build test --build-file zigux/tests/phase5_build.zig --summary all`, `make -C zigux phase5-test`, `make -C zigux phase5`, or even the sample-only `zig test samples/zigux/bytestream_fifo.zig` route in this workspace because there is still no writable Zigux checkout here.

Treat this note as confirmation that the current shipped sample file now exposes six direct bounded self-checks and still documents the same exact reviewable behavior surface on current `master`.

It complements `Documentation/zigux/phase5-kfifo-sample-survey.md` rather than replacing it: keep the broader packet truth source in that survey note, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig` until those three surfaces are rerun together on a writable checkout.
