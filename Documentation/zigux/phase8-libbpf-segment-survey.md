# Phase 8 Libbpf Segment Survey

This note records the current bounded Phase 8 libbpf segmentation reviewability gap against the roadmap's `tools/lib/bpf/libbpf.c` anchor.

## Status
- `PHASE8_STATUS=parked`
- `PHASE8_SURVEY=libbpf-segment-gap-readback`
- roadmap anchor: `tools/lib/bpf/libbpf.c`
- intended Zigux destination family: `tools/lib/bpf/zigux_segments/`
- scope: current-tree reviewability and lane-safe next-step selection only

## Why this survey exists
The Phase 8 roadmap still calls for a segmented libbpf rollout under `tools/lib/bpf/zigux_segments/` so Zigux can expand through helper-first, output-stable tooling slices instead of widening directly into heavier routing, object-model, or descriptor-lifecycle behavior.

That plan only stays reviewable if the repo's public survey surfaces truthfully describe what is actually present on `master`.

## Current public-tree readback
Public default-branch readback on 2026-05-11 showed:
- `Documentation/zigux/` currently exposes `phase8-tooling-lane-sequencing.md` and `phase8-userspace-kernel-bridge-boundary-survey.md`, but not the broader Phase 8 libbpf slice-note family previously advertised by some shared reminder surfaces.
- the same public tree readback did not expose the richer parked libbpf docs-and-tests packet that older shared Phase 8 reminders still describe.
- the shared Phase 8 owner-map note still keeps the roadmap posture clear: any same-family follow-up must stay smaller than deferred `perf-buffer-online-cpu-routing`, `perf_event_open()` setup, epoll registration, mmap-backed ring ownership, or broader timeout-sensitive routing behavior.

## Current bounded gap
The real current gap is reviewability truthfulness, not a helper-behavior claim.

Right now the roadmap-backed segmented libbpf posture is easier to infer from older shared reminder text than from the live docs tree itself. That makes it too easy for nearby scheduled runs to confuse missing public packet surfaces with landed reviewable segment coverage.

## Non-goals
This survey does not claim:
- restored `tools/lib/bpf/zigux_segments/*.zig` behavior coverage by itself
- restored Phase 8 tests-tree shard coverage by itself
- direct `perf_event_open()` setup, epoll wiring, mmap-backed ring ownership, or online-CPU routing parity
- any reopen of the shared command or symbol packets

## Next bounded step
Start with the smallest shared-surface truthfulness repair that matches the current public tree exactly.

Preferred order:
1. `Documentation/zigux/README.md`
2. `scripts/zigux/README.md`
3. only then consider any packet-local Phase 8 libbpf slice-note or tests-root follow-through that current-tree readback really justifies

Keep follow-up inside the libbpf segment survey family until the public docs packet truthfully matches the current tree again.