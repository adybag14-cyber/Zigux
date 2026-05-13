# Phase 8 Libbpf Segment Survey

This note records the current bounded Phase 8 libbpf segmentation reviewability gap against the roadmap's `tools/lib/bpf/libbpf.c` anchor.

## Status
- `PHASE8_STATUS=parked`
- `PHASE8_SURVEY=libbpf-segment-gap-readback`
- survey checkpoint: refreshed against inspected `master` head `17fd5f8e2b234738428770e192346d040aff13ce`
- roadmap anchor: `tools/lib/bpf/libbpf.c`
- intended Zigux destination family: `tools/lib/bpf/zigux_segments/`
- scope: current-tree reviewability and lane-safe next-step selection only

## Why this survey exists
The Phase 8 roadmap still calls for a segmented rollout instead of a single-file port attempt under `tools/lib/bpf/zigux_segments/`.

That plan only stays reviewable if the repo's public survey surfaces truthfully describe what is actually present on `master`, and if the first realistic Zigux entry points are helper-first clusters with stable text or path behavior rather than a premature heavy bridge or loader claim.

## Current public-tree readback
Public default-branch exact readback on 2026-05-12 still showed:
- `Documentation/zigux/README.md` still exposes the broader Phase 8 libbpf helper packet through a stale `Documentation/zigux/phase8-bpf-type-names-slice.md` note path that current readable contents no longer expose, while omitting the live `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`; `scripts/zigux/README.md` still exposes the broader Phase 8 libbpf helper packet instead of only the shared sequencing, bridge-boundary, and bridge-slice notes.
- `zigux/tests/phase8_build.zig` still wires the current libbpf helper-first shard packet through `phase8_cpu_mask.zig`, `phase8_logging.zig`, `phase8_pin_path.zig`, `phase8_bpf_type_names.zig`, `phase8_file_path_handle_bridge.zig`, `phase8_perf_buffer_poll.zig`, `phase8_libbpf_segments.zig`, and `tools/lib/bpf/zigux_segments/verify.zig`.
- the shared helper catalog still comes from `tools/lib/bpf/zigux_segments/manifest.json`.
- the shared landed helper packet still names `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/pin_path.zig`, `tools/lib/bpf/zigux_segments/type_names.zig`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, and `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`.
- the shared landed helper packet still names `zigux/tests/phase8_bpf_type_names.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, `zigux/tests/phase8_libbpf_segments.zig`, and `zigux/tests/phase8_libbpf_segments_only_build.zig`.
- the focused replay routes remain `make -C zigux phase8-libbpf-segments-test`, `zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all`, `make -C zigux phase8-perf-buffer-poll-test`, `zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all`, `make -C zigux phase8-test`, and `zig build test --build-file zigux/tests/phase8_build.zig --summary all`.
- same-day mixed authenticated readback still shows targeted readable helper blobs include `tools/lib/bpf/zigux_segments/cpu_mask.zig` and `tools/lib/bpf/zigux_segments/logging.zig`, while `zigux/tests/phase8_pin_path.zig` remains readable even though authenticated contents reads from this environment still return `404` for `Documentation/zigux/phase8-pin-path-slice.md` and `tools/lib/bpf/zigux_segments/pin_path.zig`.
- retained marker for the existing shared checker: "targeted readable helper blobs still include `tools/lib/bpf/zigux_segments/cpu_mask.zig` and `tools/lib/bpf/zigux_segments/logging.zig`, while `zigux/tests/phase8_pin_path.zig` remains readable even though authenticated contents reads from this environment still return `404` for `Documentation/zigux/phase8-pin-path-slice.md` and `tools/lib/bpf/zigux_segments/pin_path.zig`"
- that mixed readback means the pin-path shard should stay framed as a review-surface split rather than a removed helper packet.
- the live helper packet still keeps `fdinfo-map-info-helpers`, `map-reuse-compatibility`, `file-path-and-handle-bridge`, `perf-buffer-online-cpu-routing`, and `perf-buffer-poll-bookkeeping` explicit in the broader segmented catalog.
- authenticated contents reads remain inconsistent for some paired Phase 8 docs and helper paths from this environment, so exact readable blob content and public tree evidence should outweigh older absent-file assumptions when choosing the next bounded step.

The manifest currently records twelve bounded segments: seven landed helper or helper-adjacent slices and five deferred or blocked follow-ons.

The seven landed bounded slices are `logging-version-and-errno`, `pin-path-helpers`, `cpu-mask-parsing`, `type-name-helpers`, `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and `perf-buffer-poll-bookkeeping`.

An older shared-wording pass still carried the sentence "The two ready-next helper-first catalog entries are `fdinfo-map-info-helpers` and `map-reuse-compatibility`, and they stay queued helper-first catalog entries until the next bridge-local helper follow-through lands." Current `master` no longer matches that wording: the manifest and the shared file-path bridge packet now treat those two bridge-adjacent helpers as landed helper-first slices while keeping the heavier `file-path-and-handle-bridge` destination deferred.

The deferred or blocked follow-ons are `file-path-and-handle-bridge`, `perf-buffer-online-cpu-routing`, `skeleton-population`, `object-and-elf-loader`, and `btf-relocation-and-program-load`.

Those segments still keep the bounded fdinfo helper packet explicit while the resource-boundary packet still stays deferred.

## Current bounded gap
The real current gap is still reviewability truthfulness, not a helper-behavior claim.

Same-day 2026-05-12 readback kept the pin-path evidence narrower and mixed, and the broader libbpf survey still needs to keep that split explicit while also matching the live bridge-adjacent landed-helper packet and the docs-root README drift: current `master` omits the live `phase8-file-path-handle-bridge-slice.md` note from the broad Phase 8 docs summary while still naming the missing `phase8-bpf-type-names-slice.md` path.

That means the bounded fdinfo helper packet, the landed reused-map compatibility packet, the file-path bridge slice reminder, and the perf-buffer poll reminder surface should stay explicit inside this survey, while the heavier resource-boundary packet still stays deferred and the interrupt-routing follow-on remains outside the current bounded packet.

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
Start with the smallest directly coupled libbpf survey follow-through that matches the current readable tree exactly, and keep `scripts/zigux/check-phase8-libbpf-shard-routes.py` aligned with this survey note so the broader helper-plus-build packet fails closed when these live markers drift again.

Preferred order:
1. re-read the dedicated Phase 8 libbpf shard files named by `zigux/tests/phase8_build.zig` before calling any helper packet removed
2. after this survey sync, start with the docs-root Phase 8 summary before trimming or widening any other shared reminder surface that still disagrees with the live helper-plus-build packet
3. keep follow-up smaller than deferred `perf-buffer-online-cpu-routing`, `perf_event_open()` setup, epoll registration, mmap-backed ring ownership, standalone timer or clockevent helper behavior, or broader timeout-sensitive routing behavior

Keep follow-up inside the libbpf segment survey family until the public survey packet and the current readable helper-plus-build evidence agree again.
