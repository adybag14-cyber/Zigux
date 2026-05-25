# Phase 8 Timer And Clockevent Substrate Survey

This note records the bounded Phase 8 timing-substrate gap against the roadmap and the current Phase 8 tooling packet on `master`.

## Status
- `PHASE8_STATUS=parked_timing_boundary_survey`
- `PHASE8_SURVEY=timer-clockevent-substrate-gap`
- survey checkpoint: refreshed against inspected current `master` readback on 2026-05-25
- roadmap anchors: `tools/lib/subcmd/exec-cmd.c`, `tools/lib/subcmd/help.c`, `tools/lib/symbol/kallsyms.c`, and `tools/lib/bpf/libbpf.c`
- intended Zigux destination family for this lane: Phase 8 reminder and survey surfaces only
- scope: current-tree timing-boundary truthfulness only

## Roadmap comparison
The roadmap still defines Phase 8 as userspace-adjacent tooling expansion, not as a runtime timer, clocksource, or clockevent delivery tranche.

Current `master` reflects that posture:
- the active Phase 8 packet is centered on `exec-cmd`, `help`, `kallsyms`, and helper-first `libbpf` segmentation
- the timing-adjacent Phase 8 surface is limited to bounded `perf_buffer_poll` helper bookkeeping inside `tools/lib/bpf/zigux_segments/`
- no standalone timer or clockevent helper family is present in the visible Phase 8 tree

That means the timing gap is not a hidden missing helper tranche inside the current roadmap packet. It is an intentionally deferred boundary.

## Current Phase 8 evidence
Current Phase 8 reminder and validation surfaces already keep the timing boundary explicit through:
- `Documentation/zigux/phase8-perf-buffer-poll-slice.md`
- `Documentation/zigux/phase8-libbpf-segment-survey.md`
- `Documentation/zigux/phase8-tooling-lane-sequencing.md`
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase8.py`
- `zigux/tests/README.md`
- `zigux/tests/phase8_perf_buffer_poll.zig`
- `zigux/tests/phase8_libbpf_segments.zig`
- `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
- `tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`
- `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`

Those surfaces are timing-adjacent only in the limited Phase 8 sense of helper-local wait classification, poll-summary bookkeeping, ready-buffer lookup summaries, and bounded online-CPU routing summaries.

They do not establish a reusable runtime timing substrate.

## Current bounded gap
Current `master` does not show a dedicated Phase 8 packet for:
- standalone timer helper behavior
- standalone clockevent helper behavior
- broader timeout-sensitive routing behavior
- `perf_event_open()` setup parity
- epoll registration parity
- `mmap()`-backed ring ownership parity
- broader online-CPU setup or routing lifecycle parity

That absence is currently roadmap-aligned because Phase 8 is still scoped as tooling-first reviewability work.

The nearest truthful interpretation is:
- Phase 8 may describe timing-adjacent helper bookkeeping inside the libbpf shard packet
- Phase 8 must not overclaim a timer or clockevent substrate
- broader timing delivery belongs to a later runtime or driver-facing tranche, not to the current tooling packet

## Lane rule
When this lane reopens, keep follow-up limited to reminder-surface truthfulness around the bounded Phase 8 timing language.

Allowed same-lane work:
- correcting a shared reminder surface that accidentally claims standalone timer behavior
- correcting a shared reminder surface that accidentally claims standalone clockevent behavior
- keeping the `perf_buffer_poll` helper packet explicit about helper-local wait and poll summaries only

Disallowed same-lane widening:
- inventing a new Phase 8 timer API
- inventing a new Phase 8 clockevent API
- claiming broader timeout-sensitive routing parity
- treating Phase 9 runtime-pilot timing needs as if they were already Phase 8 tooling work

## Next bounded step
Keep the survey parked unless one of the current Phase 8 reminder surfaces drifts away from the existing no-timer and no-clockevent boundary.

If follow-up is needed, reread this note together with:
- `Documentation/zigux/phase8-perf-buffer-poll-slice.md`
- `Documentation/zigux/phase8-libbpf-segment-survey.md`
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase8.py`
- `zigux/tests/README.md`

Then repair the smallest wording surface that overstates Phase 8 timing scope.
