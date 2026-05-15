# Phase 8 Libbpf Segment Survey

This note records the current bounded Phase 8 libbpf segmentation reviewability gap against the roadmap's `tools/lib/bpf/libbpf.c` anchor.

## Status
- `PHASE8_STATUS=parked`
- `PHASE8_SURVEY=libbpf-segment-gap-readback`
- survey checkpoint: refreshed against inspected `master` head `37d0ccdc93587eab8eed84de29ad9d659c623aea`
- roadmap anchor: `tools/lib/bpf/libbpf.c`
- intended Zigux destination family: `tools/lib/bpf/zigux_segments/`
- scope: current-tree reviewability and lane-safe next-step selection only

## Why this survey exists
The Phase 8 roadmap still calls for a segmented rollout instead of a single-file port attempt under `tools/lib/bpf/zigux_segments/`.

That plan only stays reviewable if the repo's public survey surfaces truthfully describe what is actually present on `master`, and if the first realistic Zigux entry points are helper-first clusters with stable text or path behavior rather than a premature heavy bridge or loader claim.

## Current public-tree readback
Public mixed default-branch tree and raw readback on 2026-05-14 keeps the current packet broader than this note previously claimed:
- current shared reminder surfaces still include `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase8.py`, `zigux/Makefile`, and `zigux/tests/README.md`.
- current `tools/lib/bpf/zigux_segments/` tree evidence includes `cpu_mask.zig`, `logging.zig`, `manifest.json`, `online_cpu_routing.zig`, `perf_buffer_poll.zig`, `pin_path.zig`, `type_names.zig`, and `verify.zig`.
- current `zigux/tests/phase8_*` tree and raw evidence includes `phase8_build.zig`, `phase8_cpu_mask.zig`, `phase8_cpu_mask_only_build.zig`, `phase8_help.zig`, `phase8_help_only_build.zig`, `phase8_kallsyms.zig`, `phase8_libbpf_segments.zig`, `phase8_libbpf_segments_only_build.zig`, `phase8_perf_buffer_poll.zig`, `phase8_perf_buffer_poll_only_build.zig`, `phase8_pin_path.zig`, `phase8_bpf_type_names.zig`, `phase8_file_path_handle_bridge.zig`, and `phase8_file_path_handle_bridge_only_build.zig`.
- `Documentation/zigux/README.md` now names the live `Documentation/zigux/phase8-file-path-handle-bridge-slice.md` note in the broad Phase 8 docs summary, public Phase 8 readback still serves `Documentation/zigux/phase8-bpf-type-names-slice.md`, and `scripts/zigux/README.md` keeps the broader Phase 8 libbpf helper packet visible through the shared sequencing, bridge-boundary, bridge-slice, checker, and build-surface reminders.
- `zigux/tests/phase8_build.zig` still wires the current libbpf helper-first shard packet through `phase8_cpu_mask.zig`, `phase8_logging.zig`, `phase8_pin_path.zig`, `phase8_bpf_type_names.zig`, `phase8_file_path_handle_bridge.zig`, `phase8_perf_buffer_poll.zig`, and `phase8_libbpf_segments.zig`, and it still keeps `tools/lib/bpf/zigux_segments/verify.zig` visible as part of the same broad helper packet.
- current make-surface readback still keeps `make -C zigux phase8-libbpf-segments-test`, `zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all`, `make -C zigux phase8-perf-buffer-poll-test`, `zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all`, `make -C zigux phase8-test`, and `zig build test --build-file zigux/tests/phase8_build.zig --summary all` reviewable on current `master`.
- exact readable blob content still confirms the shared helper catalog in `tools/lib/bpf/zigux_segments/manifest.json`, the helper-local routing evidence in `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, and the dedicated survey gate in `zigux/tests/phase8_libbpf_segments.zig`.
- targeted readable helper blobs still include `tools/lib/bpf/zigux_segments/cpu_mask.zig` and `tools/lib/bpf/zigux_segments/logging.zig`, while `zigux/tests/phase8_pin_path.zig` remains readable even though authenticated contents reads from this environment still return `404` for `Documentation/zigux/phase8-pin-path-slice.md` and `tools/lib/bpf/zigux_segments/pin_path.zig`.
- current 2026-05-15 authenticated contents readback from this environment also returned `404` for `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, and `zigux/tests/phase8_build.zig`, so the landed bridge-helper and shared-build packet should still be treated as mixed-source review evidence rather than as uniformly stable contents-route proof.
- current `master` also carries helper-local routing evidence in `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, where `advanceOnlineCpuCursor()` and `summarizeOnlineCpuRouting()` keep the online-CPU cursor and routing-summary helper packet explicit below the broader setup-side routing boundary.
- the live helper packet still keeps `fdinfo-map-info-helpers`, `map-reuse-compatibility`, `file-path-and-handle-bridge`, `perf-buffer-online-cpu-routing`, and `perf-buffer-poll-bookkeeping` explicit in the broader segmented catalog.

The manifest currently records twelve bounded segments: seven landed helper or helper-adjacent slices and five deferred or blocked follow-ons.

The seven landed bounded slices are `logging-version-and-errno`, `pin-path-helpers`, `cpu-mask-parsing`, `type-name-helpers`, `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and `perf-buffer-poll-bookkeeping`.

The deferred or blocked follow-ons are `file-path-and-handle-bridge`, `perf-buffer-online-cpu-routing`, `skeleton-population`, `object-and-elf-loader`, and `btf-relocation-and-program-load`.

Those segments still keep the bounded fdinfo helper packet explicit while the resource-boundary packet still stays deferred.

The deferred `perf-buffer-online-cpu-routing` segment also stays explicitly larger than the helper-local `online_cpu_routing.zig` evidence: the setup-side packet still covers sysfs reads, `perf_event_open()` setup, `mmap()`-backed ring state, per-CPU perf-event-array updates, epoll registration, and timeout-sensitive waits, while the landed helper-local cursor and routing-summary code remains smaller than that broader setup boundary.

## Current bounded gap
The real current gap is now survey truthfulness about the already-landed checker packet, helper-local routing evidence, and the still-mixed contents-route stability for the landed bridge-plus-build packet, not a missing checker rule or docs-root summary.

The older narrower readback cue is now closed. Public mixed readback keeps the broader helper-plus-build packet visible on current `master`, so this survey should stay grounded in the readable manifest, helper roots, and build surfaces instead of repeating the older claim that `zigux/tests/phase8_build.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, or `tools/lib/bpf/zigux_segments/verify.zig` are absent from current reviewable evidence.

That same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence explicit so the deferred routing segment stays framed as broader setup-side parity rather than as if no routing-side helper evidence exists yet.

Current mixed 2026-05-14 readback also closes the older scripts-root omission cue outside this lane: `scripts/zigux/README.md` now explicitly carries the broader Phase 8 checker inventory alongside the shared sequencing, the bridge-boundary note, the bridge-slice note, and the live build-surface reminders that current `master` still exposes.

That leaves the narrower same-lane task as keeping this survey parked and truthful about the current readable helper-plus-build evidence instead of reopening the same checker-local step.

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
Keep the libbpf survey packet parked after this survey-and-checker sync unless a fresh shared reminder-surface drift reappears against the current readable helper-plus-build evidence.

Preferred order:
1. re-read the exact current-tree packet before calling any broader build surface missing again, starting with `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, `zigux/tests/phase8_build.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, `zigux/tests/phase8_libbpf_segments.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, and `zigux/tests/phase8_pin_path.zig`
2. confirm the dedicated survey, `scripts/zigux/check-phase8-libbpf-shard-routes.py`, and the shared reminder packet no longer undercount the visible build surfaces or helper-local routing evidence
3. treat the older scripts-root omission cue as closed on current `master`; only reopen shared wording from this libbpf survey lane if a fresh scripts-root drift appears that the dedicated sequencing note and current scripts packet both confirm
4. keep the helper-local `online_cpu_routing.zig` evidence explicit while staying smaller than deferred `perf-buffer-online-cpu-routing`, `perf_event_open()` setup, epoll registration, mmap-backed ring ownership, standalone timer or clockevent helper behavior, or broader timeout-sensitive routing behavior