# Phase 8 Perf-Buffer Poll Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around the poll-result bookkeeping helpers adjacent to `perf_buffer__poll()` in `tools/lib/bpf/libbpf.c`.

## Status
- `PHASE8_STATUS=active_helper_step`
- `PHASE8_SLICE=libbpf-perf-buffer-poll`
- scope: observed wait-result normalization, ready-buffer bookkeeping, bounded buffer-fd lookup and errno shaping, bounded buffer-window lookup and mapped-size passthrough, and ordered record-processing summaries only
- product boundary:
  - `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
  - `zigux/tests/phase8_perf_buffer_poll.zig`
  - `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
  - `zigux/tests/phase8_build.zig`
  - `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`

## Why this slice exists
The Phase 8 roadmap still calls for a segmented libbpf rollout under `tools/lib/bpf/zigux_segments/` instead of widening into object loading or broader perf-buffer routing too early.

The `perf_buffer__poll(timeout_ms)` path is a reasonable bounded adjunct because it lets Zigux prove output-stable wait-result classification and ready-buffer accounting without claiming live epoll wiring, per-CPU setup, or mmap-backed ring ownership.

The same bounded packet can also carry the tiny adjacent return-shaping surfaces around `perf_buffer__buffer_fd(buf_idx)` and `perf_buffer__buffer(buf_idx, &buf, &buf_size)` as slot-validation helpers, so long as it stops short of ring creation, lifetime ownership, or mmap setup parity.

## Gates
1. run the shared Phase 8 validator route first
   - `make -C zigux phase8-validate`
2. run the shared Phase 8 validator self-test
   - `python3 scripts/zigux/validate-phase8.py --self-test`
3. run the shared Phase 8 validator
   - `python3 scripts/zigux/validate-phase8.py`
4. run the dedicated Phase 8 perf-buffer poll gate
   - `python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py`
5. run the focused Phase 8 perf-buffer poll shard
   - `make -C zigux phase8-perf-buffer-poll-test`
   - `zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all`
6. run the shared Phase 8 tooling replay
   - `make -C zigux phase8-test`
   - `zig build test --build-file zigux/tests/phase8_build.zig --summary all`
7. run the convenience target
   - `make -C zigux phase8`

## Current parity surface
The current bounded helper covers:
- `perf_buffer__poll(timeout_ms)` wait-result classification
- normalized negative errno-or-ready-count wait results
- ready-buffer bookkeeping after the observed wait result
- ordered `perf_buffer__process_records()` pass summaries
- cumulative processed-record count across attempted ready buffers
- first failing ready buffer and its error code
- final return-path choice between a successful ready count and the first processing failure
- explicit `perf_buffer__buffer_fd(buf_idx)` slot lookup classification
- return shaping for valid buffer fds, invalid indices, and missing buffer fds
- explicit `perf_buffer__buffer(buf_idx, &buf, &buf_size)` slot lookup classification
- mapped-size passthrough for present buffer windows
- return shaping for valid buffer windows, invalid indices, and missing buffer windows
- ready-buffer processing attempts cannot exceed observed ready events
- non-ready wait observations cannot claim record processing
- reject impossible post-wait buffer state combinations

The current tests check:
- bounded, nonblocking, and indefinite timeout classification
- direct and raw wait-result normalization into compact wait observations
- stable ready-buffer counting with the first error preserved for reviewability
- fail-fast processing summaries that stop on the first failing ready buffer
- helper-local execution summaries that keep processed-record totals compact
- return-path helpers that preserve the successful ready count until the first processing failure wins instead
- buffer-fd slot lookups and errno-shaped invalid-index or missing-fd returns
- buffer-window slot lookups and mapped-size passthrough plus errno-shaped invalid-index or missing-window returns
- impossible processing paths that overrun the observed ready-event budget
- impossible post-wait buffer state combinations that must stay rejected

## Non-goals
This slice does not yet claim:
- no standalone timer helper behavior
- no standalone clockevent helper behavior
- direct `perf_event_open()` setup or enablement
- epoll registration or wakeup-loop ownership
- mmap-backed ring creation or teardown
- descriptor ownership, duplication, or close semantics beyond bounded buffer-fd lookup results
- direct user-visible buffer pointer materialization beyond bounded slot classification and mapped-size passthrough
- broader perf-buffer-online-cpu-routing parity

## Next bounded step
If this helper family moves again, keep follow-up smaller than full routing, epoll, timer, clockevent, object-model, or ring-lifecycle work. The next honest reopen inside `P8-L02` is another tiny helper-local guard or replay update inside the same wait-result, buffer-fd, or buffer-window packet.
