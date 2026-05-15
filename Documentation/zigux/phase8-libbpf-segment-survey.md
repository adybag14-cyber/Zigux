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
Exact GitHub file readback on 2026-05-15, using the documented public default-branch raw fallback where authenticated contents reads stay flaky, now keeps the dedicated libbpf survey packet aligned with the broader shared reminder surfaces:
- current shared reminder surfaces still include `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase8.py`, `zigux/Makefile`, and `zigux/tests/README.md`.
- exact readable helper-side files currently include `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/verify.zig`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, and `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`.
- exact readable dedicated survey evidence currently includes `zigux/tests/phase8_build.zig`, `zigux/tests/phase8_cpu_mask.zig`, `zigux/tests/phase8_logging.zig`, `zigux/tests/phase8_pin_path.zig`, `zigux/tests/phase8_bpf_type_names.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, `zigux/tests/phase8_libbpf_segments.zig`, and `zigux/tests/phase8_libbpf_segments_only_build.zig`.
- the directly readable focused replay packet therefore keeps `phase8_cpu_mask.zig`, `phase8_logging.zig`, `phase8_pin_path.zig`, `phase8_bpf_type_names.zig`, `phase8_file_path_handle_bridge.zig`, `phase8_perf_buffer_poll.zig`, `phase8_perf_buffer_poll_only_build.zig`, `phase8_libbpf_segments.zig`, and `phase8_libbpf_segments_only_build.zig` explicit inside the parked helper-first libbpf tranche.
- `Documentation/zigux/README.md` now names the live `Documentation/zigux/phase8-file-path-handle-bridge-slice.md` note in the broad Phase 8 docs summary, public Phase 8 readback still serves `Documentation/zigux/phase8-bpf-type-names-slice.md`, and `scripts/zigux/README.md` keeps the broader Phase 8 libbpf helper packet visible through the shared sequencing, bridge-boundary, bridge-slice, checker, and build-surface reminders.
- exact readable blob content still confirms the shared segment catalog in `tools/lib/bpf/zigux_segments/manifest.json`, the helper-local routing evidence in `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, the combined helper compile gate in `tools/lib/bpf/zigux_segments/verify.zig`, the shared build replay in `zigux/tests/phase8_build.zig`, and the dedicated survey gate in `zigux/tests/phase8_libbpf_segments.zig`.
- current `master` also carries helper-local routing evidence in `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, where `advanceOnlineCpuCursor()`, `summarizeNextOnlineCpuRoute()`, and `summarizeOnlineCpuRouting()` keep the online-CPU cursor, single-attempt route summary, and broader routing-summary helper packet explicit below the broader setup-side routing boundary.
- `zigux/tests/phase8_build.zig` still wires the current libbpf helper-first shard packet, `make -C zigux phase8-libbpf-segments-test` still routes through `zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all`, `make -C zigux phase8-perf-buffer-poll-test` still routes through `zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all`, and `make -C zigux phase8-test` still routes through `zig build test --build-file zigux/tests/phase8_build.zig --summary all`.
- targeted readable helper blobs still include `tools/lib/bpf/zigux_segments/cpu_mask.zig` and `tools/lib/bpf/zigux_segments/logging.zig`, while `zigux/tests/phase8_pin_path.zig` remains readable even though authenticated contents reads from this environment still return `404` for `Documentation/zigux/phase8-pin-path-slice.md` and `tools/lib/bpf/zigux_segments/pin_path.zig`.
- current shared reminder surfaces already keep the landed bridge-plus-build packet explicit through `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, `zigux/tests/phase8_build.zig`, `zigux/Makefile`, and `scripts/zigux/validate-phase8.py`.
- the manifest still keeps `fdinfo-map-info-helpers`, `map-reuse-compatibility`, `file-path-and-handle-bridge`, `perf-buffer-online-cpu-routing`, and `perf-buffer-poll-bookkeeping` explicit in the broader segmented catalog even while the dedicated survey now stays aligned with the landed helper-plus-build packet.

The manifest currently records twelve bounded segments: seven landed helper or helper-adjacent slices and five deferred or blocked follow-ons.

The seven landed bounded slices are `logging-version-and-errno`, `pin-path-helpers`, `cpu-mask-parsing`, `type-name-helpers`, `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and `perf-buffer-poll-bookkeeping`.

The deferred or blocked follow-ons are `file-path-and-handle-bridge`, `perf-buffer-online-cpu-routing`, `skeleton-population`, `object-and-elf-loader`, and `btf-relocation-and-program-load`.

Those segments still keep the bounded fdinfo helper packet explicit while the resource-boundary packet still stays deferred.

The deferred `perf-buffer-online-cpu-routing` segment also stays explicitly larger than the helper-local `online_cpu_routing.zig` evidence: the setup-side packet still covers sysfs reads, `perf_event_open()` setup, `mmap()`-backed ring state, per-CPU perf-event-array updates, epoll registration, and timeout-sensitive waits, while the landed helper-local cursor and routing-summary code remains smaller than that broader setup boundary.

## Current bounded gap
The real current gap is now survey truthfulness about the already-landed checker packet, helper-local routing evidence, and the landed bridge-plus-build packet itself, not environment-specific contents-route flakiness or a missing checker rule.

The older mixed-source caveat is now too weak for this packet.

Current repo-facing reminder surfaces already keep the bridge helper, the focused bridge build shard, the focused libbpf-segment shard, and the shared Phase 8 build replay explicit on `master`, while that same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence explicit.

That same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence explicit.

## Non-goals
This survey slice does not yet claim:
- any direct Zig port of `tools/lib/bpf/libbpf.c`
- direct `perf_event_open()` setup, epoll wiring, mmap-backed ring ownership, or online-CPU routing parity
- direct procfs reads, live bpffs opens, token creation, `bpf_obj_get()` reopen flow, or fd ownership parity for the deferred resource-boundary packet
- standalone timer or clockevent helper behavior
- broader timeout-sensitive routing behavior
- any reopen of the shared command or symbol packets
- any reopen of deferred object-model, descriptor-lifecycle, or bridge-heavy libbpf work

## Next bounded step
Keep the libbpf survey packet parked after this survey-and-route sync unless a fresh shared reminder-surface drift reappears against the current helper-plus-build evidence.

Preferred order:
1. re-read `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/verify.zig`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`, `zigux/tests/phase8_build.zig`, `zigux/tests/phase8_libbpf_segments.zig`, and `zigux/tests/phase8_libbpf_segments_only_build.zig` together before narrowing the directly readable helper packet again
2. keep the manifest-backed `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and deferred `file-path-and-handle-bridge` segmentation explicit without widening into procfs reads, token materialization, bpffs reopen flow, or fd ownership claims
3. keep the helper-local `online_cpu_routing.zig` evidence explicit while staying smaller than deferred `perf-buffer-online-cpu-routing`, `perf_event_open()` setup, epoll registration, mmap-backed ring ownership, standalone timer or clockevent helper behavior, or broader timeout-sensitive routing behavior
