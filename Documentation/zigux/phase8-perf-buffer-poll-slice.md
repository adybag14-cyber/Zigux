# Phase 8 Perf-Buffer Poll Slice

This note records the current bounded Phase 8 perf-buffer poll helper packet against the roadmap's `tools/lib/bpf/libbpf.c` anchor.

## Status
- `PHASE8_STATUS=parked_helper_slice`
- `PHASE8_SLICE=libbpf-perf-buffer-poll`
- survey checkpoint: refreshed against inspected current `master` readback on 2026-05-27
- roadmap anchor: `tools/lib/bpf/libbpf.c`
- intended Zigux destination family: `tools/lib/bpf/zigux_segments/`
- scope: helper-local perf-buffer poll reviewability and timing-boundary truthfulness only

## Current helper packet
Current `master` keeps the dedicated helper packet reviewable through `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig`, `tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`, `tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig`, `tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, `zigux/tests/phase8_build.zig`, `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `make -C zigux phase8-validate`, `python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `make -C zigux phase8-perf-buffer-poll-test`, and `make -C zigux phase8-test`.

The focused `zigux/tests/phase8_perf_buffer_poll_only_build.zig` replay now compiles `zigux/tests/phase8_perf_buffer_poll.zig` together with `tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig`, `tools/lib/bpf/zigux_segments/ready_buffer_fd_lookup.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig`, `tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig`, and `tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`, while the broader aggregate Phase 8 replay continues to carry the wider helper packet and verifier companions through `zigux/tests/phase8_build.zig` and `make -C zigux phase8-test`.

That packet stays bounded to helper-local wait classification, bounded wait-budget normalization, poll summary bookkeeping, ready-buffer attempt routing, ready-buffer fd lookup, and ready-buffer mapped-window lookup behavior. It does not promote broader setup-side perf-event ownership, shared routing setup, or bridge-heavy reopen flow into shipped proof.

The landed verifier companion keeps wait classification, poll summary, execution summary, and impossible-summary fail-closed outputs explicit beside that same bounded helper packet.

The dedicated wait-budget helper keeps bounded millisecond budgets, derived nanosecond budgets, and invalid negative timeout rejection explicit beside that same bounded helper packet.

The dedicated ready-buffer attempt verifier keeps ready-buffer ordinal lookup summaries, typed attempt resolution, and errno-shaped attempt returns explicit beside that same bounded helper packet.

The dedicated ready-buffer fd verifier keeps typed ready-buffer fd lookups, compact errno-shaped fd returns, and missing-ready-buffer precedence explicit beside that same bounded helper packet.

The dedicated ready-buffer window companion keeps helper-local ready-buffer window summaries, typed mapped-size resolution, compact errno-shaped mapped-size returns, and lookup-return wrappers explicit beside that same bounded helper packet.

## Timing boundary
Current `master` now keeps helper-local wait-budget normalization explicit through `tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig`, including bounded millisecond-to-nanosecond conversion for existing poll waits.

The dedicated reminder still stays explicit about no standalone timer helper behavior and no standalone clockevent helper behavior.

The same packet also keeps broader perf-buffer-online-cpu-routing parity deferred while the helper-local summaries remain reviewable on current `master`.

## Non-goals
This slice does not yet claim:
- direct `perf_event_open()` setup parity
- epoll wiring or `mmap()`-backed ring ownership
- broader perf-buffer-online-cpu-routing parity
- no standalone timer helper behavior beyond the bounded reminder packet
- no standalone clockevent helper behavior beyond the bounded reminder packet
- any direct Zig port of the full `tools/lib/bpf/libbpf.c` setup path

## Next bounded step
Keep this helper slice parked unless the dedicated wait-budget helper, the dedicated poll gate, the focused poll replay, the dedicated ready-buffer fd verifier, the dedicated ready-buffer window companion, or the shared timing-boundary reminder surfaces drift again around the bounded timeout budget, the no-timer and no-clockevent boundary, or the broader timeout-sensitive routing boundary.
