# Phase 8 Userspace-Kernel Bridge Boundary Survey

This document records the bounded Phase 8 userspace-adjacent tooling boundary around the current libbpf bridge helpers parked under `tools/lib/bpf/zigux_segments/`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=userspace-kernel-bridge-boundary-survey`
- scope: helper-first review of the current fdinfo bridge packet plus the landed adjacent perf-buffer poll helper packet and the still-queued adjacent bridge steps only
- product boundary:
  - `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
  - `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
  - `zigux/tests/phase8_file_path_handle_bridge.zig`
  - `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`
  - `zigux/tests/phase8_perf_buffer_poll.zig`
  - `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
  - `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`
  - `Documentation/zigux/phase8-perf-buffer-poll-slice.md`
  - `Documentation/zigux/phase8-libbpf-segment-survey.md`

## Why this survey exists

The live Phase 8 packet already carries a bounded fdinfo helper slice, but the adjacent bridge boundary was still only implicit across the file-path helper note and the broader libbpf segment survey. This survey keeps that boundary explicit so the validator-first Phase 8 packet can describe the shipped helpers and the queued follow-through without implying procfs, bpffs, object-model, or deferred interrupt-routing closure.

## Current landed packet

The currently landed bridge-side helper remains intentionally small:

- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` keeps exact `"/proc/%d/fdinfo/%d"` assembly, bounded fdinfo map-info parsing, explicit decimal or octal or hex numeric handling, and compact completion summaries reviewable
- `zigux/tests/phase8_file_path_handle_bridge.zig` keeps the helper packet wired to stable path, ignored-line, repeated-field, numeric-base, and summary expectations
- the adjacent `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig` packet keeps bounded `perf_buffer__poll(timeout_ms)` wait-result classification, poll waits, ready-buffer bookkeeping, and ordered record-processing summaries reviewable without claiming live epoll wiring, per-CPU setup, mmap-backed ring ownership, or standalone timer or clockevent helper behavior
- the helper family stays smaller than direct procfs reads, pinned-object reopen flow, token creation, descriptor lifecycle behavior, and the still-deferred `perf_buffer__new()` online-CPU routing packet

## Boundary findings

The current packet is productively landed, but the remaining bridge-facing work still needs a sharp fence:

- `planTokenPreparation()` remains outside the shipped helper packet because token construction would widen the slice from stable text parsing into capability and ownership setup
- `resolveReusePinnedMapAttempt()` remains queued because map reuse needs explicit path-open, reopen, and compatibility decisions that go beyond the current fdinfo-only helper
- direct procfs reads, bpffs opens, `bpf_obj_get()` reopen flow, and fd close or ownership semantics remain intentionally outside the current packet
- the deferred `perf-buffer-online-cpu-routing` packet still remains outside the current helper-first bridge surface because it combines `/sys/devices/system/cpu/online` reads, cached `/sys/devices/system/cpu/possible` counts via `libbpf_num_possible_cpus()`, online CPU filtering, per-CPU perf-event-array map updates, per-CPU `perf_event_open()` setup, perf-buffer ring `mmap()` setup, `PERF_EVENT_IOC_ENABLE` enablement, epoll-backed perf FD registration, and poll-loop ownership beyond the already-landed bounded `perf_buffer__poll(timeout_ms)` helper packet
- the current helper-first bridge note should stay adjacent to the libbpf segment survey until the queued bridge packet can be reviewed as one tighter step

## Review gates

1. run the shared Phase 8 validator route first
- `make -C zigux phase8-validate`

2. run the shared Phase 8 validator self-test
- `python3 scripts/zigux/validate-phase8.py --self-test`

3. run the shared Phase 8 validator
- `python3 scripts/zigux/validate-phase8.py`

4. run the focused file-path bridge wrapper
- `make -C zigux phase8-file-path-handle-bridge-test`
- `zig build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all`

5. run the focused perf-buffer poll wrapper
- `make -C zigux phase8-perf-buffer-poll-test`
- `zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all`

6. run the shared Phase 8 replay
- `make -C zigux phase8-test`
- `zig build test --build-file zigux/tests/phase8_build.zig --summary all`
- `make -C zigux phase8`

## Non-goals

This survey does not claim:

- direct procfs file reads
- token materialization or capability handoff
- map reopen or bpffs compatibility closure
- object-model or loader parity
- descriptor duplication, transfer, or close ownership rules
- `/sys/devices/system/cpu/online` reads or cached `/sys/devices/system/cpu/possible` counts via `libbpf_num_possible_cpus()`
- online CPU filtering, per-CPU perf-event-array map updates, per-CPU `perf_event_open()` setup, perf-buffer ring `mmap()` setup, `PERF_EVENT_IOC_ENABLE` enablement, or epoll-backed perf FD registration
- poll-loop ownership beyond the bounded `perf_buffer__poll(timeout_ms)` helper packet
- standalone timer or clockevent helper behavior

## Next bounded step

Keep this survey parked beside the landed fdinfo helper packet and the adjacent bounded poll helper until one adjacent bridge step is ready to move as a single bounded review surface. Keep the shared `make -C zigux phase8-validate` route explicit in that parked boundary so validator-first review stays ahead of the bridge-side replay, and keep the deferred `perf-buffer-online-cpu-routing` packet explicitly parked beside the current helper family so the file-path bridge note does not accidentally over-claim libbpf parity. The next honest reopen remains the smallest helper-first packet that can connect the current fdinfo note to queued reuse planning without widening into direct procfs reads, bpffs opens, token creation, loader-facing libbpf work, or live interrupt-routing behavior.
