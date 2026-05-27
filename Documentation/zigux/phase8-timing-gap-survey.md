# Phase 8 Timing Gap Survey

This note records the current bounded Phase 8 timing and clockevent-substrate gap against the roadmap's `tools/lib/bpf/libbpf.c` anchor.

## Status
- `PHASE8_STATUS=parked_gap_survey`
- `PHASE8_SURVEY=timing-gap-readback`
- survey checkpoint: refreshed against inspected current `master` readback on 2026-05-27
- roadmap anchor: `tools/lib/bpf/libbpf.c`
- intended Zigux destination family: `tools/lib/bpf/zigux_segments/`
- scope: helper-local timing-boundary truthfulness and next-step selection only

## Current bounded evidence
Current `master` already keeps helper-local wait budgeting explicit through `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig`, `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, `zigux/tests/phase8_build.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/validate-phase8.py`, `zigux/Makefile`, and `make -C zigux phase8-perf-buffer-poll-test`.

That evidence is real product progress because it keeps wait-class normalization, bounded millisecond budgets, derived nanosecond budgets, and invalid negative timeout rejection reviewable inside the existing libbpf helper-first packet.

## Current bounded gap
Current `master` does materialize helper-local wait-budget normalization, but it still does not materialize standalone timer helper behavior or standalone clockevent helper behavior.

The current timing packet is therefore narrower than a true timer or clockevent substrate: it only explains the timeout budget already consumed by the perf-buffer poll helper family, and it stays below broader timeout-sensitive routing behavior.

That means the roadmap-aligned gap is no longer "any timing evidence at all." The remaining gap is the absence of a dedicated standalone timing helper family that would own timer or clockevent behavior outside the bounded perf-buffer poll packet.

## Explicit non-goals
This survey does not claim:
- standalone timer helper behavior
- standalone clockevent helper behavior
- direct `perf_event_open()` setup parity
- epoll wiring, `mmap()`-backed ring ownership, or online-CPU setup parity
- broader timeout-sensitive routing behavior
- any direct Zig port of the full `tools/lib/bpf/libbpf.c` setup path

## Recommended lane-safe next step
Keep the Phase 8 timing packet parked unless one of these changes lands on current `master`:
1. a new standalone timing helper beside the current perf-buffer packet
2. a new standalone clockevent-oriented helper slice
3. broader timeout-sensitive routing behavior that stops being helper-local

If one of those lands, reread `Documentation/zigux/phase8-timing-gap-survey.md`, `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, `zigux/tests/phase8_build.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig`, and `zigux/Makefile` together before widening the lane.
