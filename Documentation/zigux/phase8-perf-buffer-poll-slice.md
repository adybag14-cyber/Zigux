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

The narrower `perf_buffer__poll(timeout_ms)` bookkeeping surface is smaller and safer. Zigux can model normalized negative errno-or-ready-count wait results, ready-buffer counting, first-ready indexing, first-error surfacing, fail-fast ready-buffer processing order, and the cumulative processed-record count returned before the first failing ready buffer without claiming direct `epoll_wait()` parity or broader timer ownership.

## Current helper contract

The helper now keeps these bounded rules explicit:

- timeout requests stay classified as nonblocking, bounded, or indefinite based only on the already-observed `timeout_ms` input
- normalized negative errno-or-ready-count wait results stay compact through explicit `timed_out`, `interrupted`, `ready_events`, and `failed(errno)` variants before buffer bookkeeping starts
- ready-buffer bookkeeping counts ready buffers, remembers the first ready index, and surfaces the first buffer-local error without claiming record decoding
- the ordered `perf_buffer__process_records()` pass can now be summarized separately as successful ready-buffer processing until the first failing ready buffer, plus the cumulative processed-record count returned before that failure, keeping libbpf's fail-fast loop explicit without claiming callback delivery or record decoding parity
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

The shared review path now fail-closes through the shared Phase 8 validator, the dedicated tests-readme alignment checker, and their built-in self-tests before the focused helper and shared build replays run, so this slice stays tied to the same validator-first Phase 8 tooling packet as the docs root, tests root, Makefile, workflow, and broader segmented libbpf notes.

1. `python3 scripts/zigux/validate-phase8.py --self-test`
2. `python3 scripts/zigux/check-phase8-tests-readme-alignment.py --self-test`
3. `python3 scripts/zigux/validate-phase8.py`
4. `python3 scripts/zigux/check-phase8-tests-readme-alignment.py`
5. `make -C zigux phase8-validate`
6. `zig test tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
7. `zig test zigux/tests/phase8_perf_buffer_poll.zig`
8. `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

## Next bounded step

Keep the helper parked unless the live `perf_buffer__poll()` loop changes shape. The remaining same-family follow-on is still the shared `perf-buffer-online-cpu-routing` boundary, not a wider timer or clockevent claim.
