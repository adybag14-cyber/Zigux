# Phase 8 Perf-Buffer Poll Slice

This note records the bounded Phase 8 helper-first slice around the pure wait-result and ready-buffer bookkeeping surface inside `perf_buffer__poll(timeout_ms)`.

## Status

- `PHASE8_STATUS=active`
- `PHASE8_SLICE=perf-buffer-poll-helper`
- scope: pure wait-result classification plus ready-buffer bookkeeping only
- product boundary:
  - `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
  - `zigux/tests/phase8_perf_buffer_poll.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The remaining `perf-buffer-online-cpu-routing` packet is still too large to land honestly in one step because it crosses `/sys` reads, online CPU filtering, perf-event-array updates, epoll-backed registration, and interrupt-routing-sensitive delivery behavior.

The narrower `perf_buffer__poll(timeout_ms)` bookkeeping surface is smaller and safer. Zigux can model wait-result classification, ready-buffer counting, first-ready indexing, and first-error surfacing without claiming direct `epoll_wait()` parity or broader timer ownership.

## Current helper contract

The helper now keeps these bounded rules explicit:

- timeout requests stay classified as nonblocking, bounded, or indefinite based only on the already-observed `timeout_ms` input
- ready-buffer bookkeeping counts ready buffers, remembers the first ready index, and surfaces the first buffer-local error without claiming record decoding
- observed wait outcomes stay compact through explicit `timed_out`, `interrupted`, `ready_events`, and `failed(errno)` variants instead of hidden syscall behavior
- inconsistent states such as more ready buffers than observed ready events still fail fast

## Non-goals

This helper does not yet claim:

- direct `epoll_wait()` parity
- epoll-backed perf FD registration
- `/sys/devices/system/cpu/online` reads
- cached `libbpf_num_possible_cpus()` behavior
- online CPU filtering
- per-CPU perf-event-array map updates
- direct `perf_buffer__poll(timeout_ms)` timeout parity for the broader routing loop
- no standalone timer helper
- no standalone clockevent helper
- interrupt-routing-sensitive perf-buffer delivery behavior

## Gates

1. `zig test tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
2. `zig test zigux/tests/phase8_perf_buffer_poll.zig`
3. `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

## Next bounded step

Keep the helper parked unless the live `perf_buffer__poll()` loop changes shape. The remaining same-family follow-on is still the shared `perf-buffer-online-cpu-routing` boundary, not a wider timer or clockevent claim.
