# Phase 8 Perf-Buffer Poll Slice

This note records the bounded Phase 8 helper-first slice around the pure wait-result and ready-buffer bookkeeping surface inside `perf_buffer__poll(timeout_ms)`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=perf-buffer-poll-helper`
- scope: pure wait-result classification plus ready-buffer bookkeeping only
- product boundary:
  - `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
  - `zigux/tests/phase8_perf_buffer_poll.zig`
  - `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The remaining `perf-buffer-online-cpu-routing` packet is still too large to land honestly in one step because it crosses `/sys` reads, online CPU filtering, perf-event-array updates, epoll-backed registration, and interrupt-routing-sensitive delivery behavior.

The narrower `perf_buffer__poll(timeout_ms)` bookkeeping surface is smaller and safer.

Zigux can model normalized negative errno-or-ready-count wait results, ready-buffer counting, first-ready indexing, first-error surfacing, fail-fast ready-buffer processing order, the cumulative processed-record count returned before the first failing ready buffer, and the final return-path choice between a successful ready count and the first processing failure without claiming direct `epoll_wait()` parity or broader timer or clockevent ownership.

## Current helper contract

The helper now keeps these bounded rules explicit:

- timeout requests stay classified as nonblocking, bounded, or indefinite based only on the already-observed `timeout_ms` input
- normalized negative errno-or-ready-count wait results stay compact through explicit `timed_out`, `interrupted`, `ready_events`, and `failed(errno)` variants before buffer bookkeeping starts
- ready-buffer bookkeeping counts ready buffers, remembers the first ready index, and surfaces the first buffer-local error without claiming record decoding
- the ordered `perf_buffer__process_records()` pass can now be summarized separately as successful ready-buffer processing until the first failing ready buffer, plus the cumulative processed-record count returned before that failure, keeping libbpf's fail-fast loop explicit without claiming callback delivery or record decoding parity
- final poll return keeps successful ready counts and first processing failures explicit, so the helper can preserve the observed ready-event count on success or surface the first process-record failure without widening into the broader routing loop
- ready-buffer processing attempts cannot exceed observed ready events, so the helper keeps `epoll_wait()`'s bounded ready-event budget visible before any wider routing work
- non-ready wait observations cannot claim record processing, matching the live loop's timeout, interrupted, and already-failed early returns without widening into broader poll parity claims
- observed wait outcomes stay compact instead of hiding error or ready-state intent inside broader loop behavior
- inconsistent states such as more ready buffers than observed ready events still fail fast
- timed-out, interrupted, and already-failed wait observations now reject impossible post-wait buffer state combinations because the live loop never processes records on those paths

## Non-goals

This helper does not yet claim:

- direct `epoll_wait()` parity
- epoll-backed perf FD registration
- `/sys/devices/system/cpu/online` reads
- cached `libbpf_num_possible_cpus()` behavior
- online CPU filtering
- per-CPU perf-event-array map updates
- direct `perf_buffer__poll(timeout_ms)` timeout parity for the broader routing loop
- callback delivery or record decoding parity inside `perf_buffer__process_records()`
- no standalone timer helper
- no standalone clockevent helper
- interrupt-routing-sensitive perf-buffer delivery behavior

## Gates

The current review path on `master` is smaller than the older validator-heavy snapshot that this note used to describe. The live helper stays reviewable through its focused Zig test shard, the shared Phase 8 build replay, and the shipped `make` wrappers that expose those same build routes without claiming a dedicated Phase 8 validator stack that is not currently present on the repo path.

1. `zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all`
2. `zig build test --build-file zigux/tests/phase8_build.zig --summary all`
3. `make -C zigux phase8-test`
4. `make -C zigux phase8`

## Latest committed gate snapshot

- provenance and anchor alignment rechecked against inspected `master` head `ea628a896debcda7d57a87aa8e5d9f8e47d17cdc`
- `zigux/tests/phase8_perf_buffer_poll_only_build.zig` currently publishes the dedicated `phase8-perf-buffer-poll-tests` shard and the `Run focused Phase 8 perf-buffer poll tests` entrypoint for this helper packet
- `zigux/tests/phase8_build.zig` currently keeps `../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig` and `phase8_perf_buffer_poll.zig` wired into the shared `phase8-perf-buffer-poll-tests` bundle beside the other landed Phase 8 tooling slices
- `zigux/Makefile` currently ships `phase8-test` and `phase8`, but it does not currently ship `phase8-validate` or `phase8-perf-buffer-poll-test`
- the current repo path also does not currently expose `scripts/zigux/check-phase8-validator-flow.py` or `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, so future validator-route claims for this slice should wait until those files actually land again on `master`

## Next bounded step

Keep the helper parked unless the live `perf_buffer__poll()` loop changes shape. The remaining same-family follow-on is still the shared `perf-buffer-online-cpu-routing` boundary, not a wider timer or clockevent claim.
