# Zigux Samples

This directory holds reviewable Zigux sample code.

## Phase 5 reference samples

These files are bounded, non-runtime reference readings for the roadmap's
approved Phase 5 sample anchors. They are meant to make Zigux idioms
reviewable and repeatable without claiming runtime substrate parity.

- `bytestream_fifo.zig`
- `kobject_example.zig`
- `kretprobe_example.zig`
- `trace_events_sample.zig`

For the landed `kfifo`-style sample in `bytestream_fifo.zig`, keep these cues
explicit:

- fixed embedded storage keeps the sample in memory and reviewable
- exact queue-order replay mirrors `samples/kfifo/bytestream-example.c`
- `init()`, replay, and `exit()` keep ownership and lifetime boundaries visible
- procfs, user-copy, locking, and module registration remain out of scope

## Phase 9 runtime starters

These files are separate runtime-oriented starters. They are not part of the
Phase 5 reference-sample contract and should not be read as proof that the
matching non-runtime sample has runtime parity.

- `runtime_atomic64.zig`
- `runtime_bitmap.zig`
- `runtime_kretprobe.zig`
- `runtime_trace_events.zig`
