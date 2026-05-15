# Phase 8 Libbpf Segment Survey

This note records the current bounded Phase 8 libbpf segmentation reviewability gap against the roadmap's `tools/lib/bpf/libbpf.c` anchor.

## Status
- `PHASE8_STATUS=parked`
- `PHASE8_SURVEY=libbpf-segment-gap-readback`
- survey checkpoint: refreshed against inspected `master` head `089188c96b86c0da16088e916094a7c977d0cfc6`
- roadmap anchor: `tools/lib/bpf/libbpf.c`
- intended Zigux destination family: `tools/lib/bpf/zigux_segments/`
- scope: current-tree reviewability and lane-safe next-step selection only

## Why this survey exists
The Phase 8 roadmap still calls for a segmented rollout instead of a single-file port attempt under `tools/lib/bpf/zigux_segments/`.

That plan only stays reviewable if the repo's public survey surfaces truthfully describe what is actually present on `master`, and if the first realistic Zigux entry points are helper-first clusters with stable text or path behavior rather than a premature heavy bridge or loader claim.

## Current public-tree readback
Exact GitHub file readback on 2026-05-15 keeps the directly readable packet narrower than some broader shared reminder wording still implies:
- current shared reminder surfaces still include `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase8.py`, `zigux/Makefile`, and `zigux/tests/README.md`.
- exact readable helper-side files currently include `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, and `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`.
- exact readable dedicated survey evidence currently includes `zigux/tests/phase8_libbpf_segments.zig`.
- current authenticated contents readback from this environment returns `404` for `tools/lib/bpf/zigux_segments/verify.zig`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, and `zigux/tests/phase8_build.zig`.
- `Documentation/zigux/README.md` still names `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, and the broader shared reminder packet still keeps the Phase 8 libbpf tranche visible through `scripts/zigux/README.md`, `Documentation/zigux/phase8-tooling-lane-sequencing.md`, and `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, but this dedicated survey should stay grounded in the narrower directly readable helper packet plus the manifest-backed segment catalog.
- exact readable blob content still confirms the shared segment catalog in `tools/lib/bpf/zigux_segments/manifest.json`, the helper-local routing evidence in `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, and the dedicated survey gate in `zigux/tests/phase8_libbpf_segments.zig`.
- current `master` also carries helper-local routing evidence in `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, where `advanceOnlineCpuCursor()`, `summarizeNextOnlineCpuRoute()`, and `summarizeOnlineCpuRouting()` keep the online-CPU cursor, single-attempt route summary, and broader routing-summary helper packet explicit below the broader setup-side routing boundary.
- the manifest still keeps `fdinfo-map-info-helpers`, `map-reuse-compatibility`, `file-path-and-handle-bridge`, `perf-buffer-online-cpu-routing`, and `perf-buffer-poll-bookkeeping` explicit in the broader segmented catalog even though the directly readable current-tree packet is narrower for the bridge and build follow-through.

The manifest currently records twelve bounded segments: seven landed helper or helper-adjacent slices and five deferred or blocked follow-ons.

The seven landed bounded slices are `logging-version-and-errno`, `pin-path-helpers`, `cpu-mask-parsing`, `type-name-helpers`, `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and `perf-buffer-poll-bookkeeping`.

The deferred or blocked follow-ons are `file-path-and-handle-bridge`, `perf-buffer-online-cpu-routing`, `skeleton-population`, `object-and-elf-loader`, and `btf-relocation-and-program-load`.

Those segments still keep the bounded fdinfo helper packet explicit while the resource-boundary packet still stays deferred.

The deferred `perf-buffer-online-cpu-routing` segment also stays explicitly larger than the helper-local `online_cpu_routing.zig` evidence: the setup-side packet still covers sysfs reads, `perf_event_open()` setup, `mmap()`-backed ring state, per-CPU perf-event-array updates, epoll registration, and timeout-sensitive waits, while the landed helper-local cursor and routing-summary code remains smaller than that broader setup boundary.

## Current bounded gap
The real current gap is now survey truthfulness about which parts of the helper-first libbpf packet stay directly readable on current `master` and which parts remain manifest-backed or shared-reminder claims.

Exact 2026-05-15 GitHub file reads still confirm the manifest, the bounded cpu-mask, logging, perf-buffer poll, and helper-local routing files, plus the dedicated survey gate in `zigux/tests/phase8_libbpf_segments.zig`, but they do not currently confirm the bridge helper, the focused bridge build shard, the focused libbpf-segment build shard, or the broader Phase 8 build replay.

That keeps the file-path helper packet and the focused build routes smaller than live helper delivery: the manifest still records the fdinfo and map-reuse helper segmentation, while direct readable current-tree evidence stays parked on the narrower helper-local routing and poll-side packet until those bridge and build files are readable again.

Current shared reminder surfaces still carry broader wording outside this lane, but that shared-packet follow-through belongs to the shared wording lane, not to this dedicated survey file.

## Non-goals
This survey slice does not yet claim:
- any direct Zig port of `tools/lib/bpf/libbpf.c`
- restored direct behavior verification for every paired Phase 8 libbpf test shard by itself
- direct `perf_event_open()` setup, epoll wiring, mmap-backed ring ownership, or online-CPU routing parity
- direct procfs reads, live bpffs opens, token creation, `bpf_obj_get()` reopen flow, or fd ownership parity for the deferred resource-boundary packet
- standalone timer or clockevent helper behavior
- any reopen of the shared command or symbol packets
- any reopen of deferred object-model, descriptor-lifecycle, or bridge-heavy libbpf work

## Next bounded step
Keep the libbpf survey packet parked after this truthfulness refresh unless fresh direct readable evidence returns for the bridge or build files.

Preferred order:
1. re-read `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`, and `zigux/tests/phase8_libbpf_segments.zig` together before broadening the directly readable helper packet again
2. only reopen the bridge or build claims in this dedicated survey if exact readable current-tree evidence returns for `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `tools/lib/bpf/zigux_segments/verify.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, or `zigux/tests/phase8_build.zig`
3. keep the manifest-backed `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and deferred `file-path-and-handle-bridge` segmentation explicit without widening into procfs reads, token materialization, bpffs reopen flow, or fd ownership claims
4. keep the helper-local `online_cpu_routing.zig` evidence explicit while staying smaller than deferred `perf-buffer-online-cpu-routing`, `perf_event_open()` setup, epoll registration, mmap-backed ring ownership, standalone timer or clockevent helper behavior, or broader timeout-sensitive routing behavior
