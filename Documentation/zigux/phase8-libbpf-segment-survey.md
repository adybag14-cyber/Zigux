# Phase 8 Libbpf Segment Survey

This note records the current bounded Phase 8 libbpf segmentation reviewability gap against the roadmap's `tools/lib/bpf/libbpf.c` anchor.

## Status
- `PHASE8_STATUS=parked`
- `PHASE8_SURVEY=libbpf-segment-readback-drift`
- survey checkpoint: authenticated contents readback on 2026-05-12
- roadmap anchor: `tools/lib/bpf/libbpf.c`
- intended Zigux destination family: `tools/lib/bpf/zigux_segments/`
- scope: survey-only truthfulness and lane-safe next-step selection

## Why this survey exists
The Phase 8 roadmap still calls for a segmented rollout instead of a single-file port attempt under `tools/lib/bpf/zigux_segments/`.

That plan only stays reviewable if the repo's public survey surfaces truthfully describe what is directly readable on current `master`, and if the next bounded step stays smaller than a premature bridge, loader, or descriptor-ownership claim.

## Current current-tree readback
Same-day 2026-05-12 readback from this environment still showed the shared Phase 8 libbpf reminder packet around this survey note:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase8-tooling-lane-sequencing.md`
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase8.py`
- `scripts/zigux/check-phase8-libbpf-segment-gate.py`
- `scripts/zigux/check-phase8-libbpf-shard-routes.py`
- `zigux/tests/README.md`
- `zigux/Makefile`

Those shared reminder surfaces still describe a helper-first libbpf packet built around `tools/lib/bpf/zigux_segments/manifest.json`, `zigux/tests/phase8_libbpf_segments.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, the shared `zigux/tests/phase8_build.zig` replay, and the `make -C zigux phase8-libbpf-segments-test` route.

But the same authenticated contents readback currently returns `404` for directly coupled workstream files that the older survey wording treated as freshly re-verified current-tree evidence:
- `tools/lib/bpf/zigux_segments/manifest.json`
- `zigux/tests/phase8_libbpf_segments.zig`
- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`

That means this lane currently has a readable survey note plus shared reminder surfaces, but not a directly re-readable manifest-backed segment catalog or focused bridge-helper packet from the same contents route.

## Current bounded gap
The real current gap is survey truthfulness, not a new helper-behavior claim.

This note should not keep restating counted landed-slice totals, ready-next ordering, or helper-local catalog details as if they were freshly rechecked on current `master` when the directly coupled manifest and focused test or helper files are not currently readable from the same environment.

The honest current state is narrower: shared reminder surfaces still carry the older libbpf helper packet, while direct authenticated contents readback for the packet's manifest-backed proof files is presently missing or unstable.

## Non-goals
This survey slice does not currently claim:
- a direct Zig port of `tools/lib/bpf/libbpf.c`
- a freshly re-verified counted manifest inventory for landed, ready-next, or deferred libbpf segments
- direct `perf_event_open()` setup, epoll wiring, `mmap()`-backed ring ownership, or online-CPU routing parity
- direct procfs reads, live bpffs opens, `bpf_obj_get()` reopen flow, fd ownership transfer, or token materialization
- any reopen of the separate Phase 8 command or symbol packets

## Next bounded step
Keep follow-up inside the `tools/lib/bpf/zigux_segments` workstream only.

Preferred order:
1. re-read `tools/lib/bpf/zigux_segments/manifest.json`, `zigux/tests/phase8_libbpf_segments.zig`, and the directly coupled helper packet from the same authenticated contents route before restating any counted segment inventory
2. if those files are meant to remain live, rebuild this survey's segmentation summary from the readable packet and only then refresh shared reminder surfaces
3. if those files are intentionally absent, retell the shared docs-root, checklist, scripts-root, tests-root, and Makefile reminder packet to an explicit survey-only blocked posture before any Phase 8 surface calls the libbpf shard landed again

Until one of those bounded follow-through paths happens, treat the older counted segment summary as historical wording rather than current directly re-verified `master` evidence.
