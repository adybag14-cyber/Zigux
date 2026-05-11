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
Public default-branch exact readback on 2026-05-11 showed:
- `Documentation/zigux/` still exposes the shared sequencing and bridge-boundary notes at `phase8-tooling-lane-sequencing.md` and `phase8-userspace-kernel-bridge-boundary-survey.md`.
- the same public readback also exposes the bounded bridge slice note at `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, so the Phase 8 docs packet is no longer limited to only the two shared reminder surfaces.
- the manifest-backed bridge packet keeps the roadmap boundary explicit: `fdinfo-map-info-helpers` and `map-reuse-compatibility` are already landed inside `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, while the broader `file-path-and-handle-bridge` resource boundary still stays deferred.
- the shared Phase 8 owner-map note still keeps the roadmap posture clear: any same-family follow-up must stay smaller than direct procfs reads, bpffs opens, token creation, `bpf_obj_get()` reopen flow, fd ownership semantics, or the separate deferred `perf-buffer-online-cpu-routing` packet.

## Current bounded gap
The real current gap is still reviewability truthfulness, not a helper-behavior claim.

Older shared reminder surfaces can still make the public docs packet look thinner than it really is, while the live bridge packet has already split into two landed helper-first bridge segments plus one still-deferred resource-boundary segment. This survey should keep that landed-versus-deferred boundary explicit so nearby scheduled runs do not collapse the helper packet into the heavier resource bridge.

## Non-goals
This survey does not claim:
- restored `tools/lib/bpf/zigux_segments/*.zig` behavior coverage by itself
- restored Phase 8 tests-tree shard coverage by itself
- direct `perf_event_open()` setup, epoll wiring, mmap-backed ring ownership, or online-CPU routing parity
- direct procfs reads, live bpffs opens, token creation, `bpf_obj_get()` reopen flow, or fd ownership parity for the deferred resource-boundary packet
- any reopen of the shared command or symbol packets

## Next bounded step
Start with the smallest shared-surface truthfulness repair that matches the current public packet exactly.

Preferred order:
1. `Documentation/zigux/README.md`
2. `scripts/zigux/README.md`
3. only then consider any packet-local Phase 8 libbpf slice-note or tests-root follow-through that current-tree readback really justifies

Keep follow-up inside the libbpf segment survey family until the public reminder packet explicitly matches the live bridge split: the helper-first bridge packet is landed, but the broader file-path-and-handle resource boundary remains parked.