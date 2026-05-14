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
Public default-branch exact tree readback on 2026-05-14 shows the current packet is narrower than this note previously claimed:
- current shared reminder surfaces still include `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase8.py`, `zigux/Makefile`, and `zigux/tests/README.md`.
- current `tools/lib/bpf/zigux_segments/` tree evidence includes `cpu_mask.zig`, `manifest.json`, `online_cpu_routing.zig`, `perf_buffer_poll.zig`, and `type_names.zig`.
- current `zigux/tests/phase8_*` tree evidence includes `phase8_cpu_mask.zig`, `phase8_help.zig`, `phase8_help_only_build.zig`, `phase8_kallsyms.zig`, `phase8_libbpf_segments.zig`, `phase8_perf_buffer_poll.zig`, `phase8_perf_buffer_poll_only_build.zig`, and `phase8_pin_path.zig`.
- current exact tree readback does not expose `zigux/tests/phase8_build.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, or `tools/lib/bpf/zigux_segments/verify.zig`.
- current exact tree readback also does not expose the older wider helper packet paths `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/pin_path.zig`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `zigux/tests/phase8_bpf_type_names.zig`, or `zigux/tests/phase8_file_path_handle_bridge.zig`.
- exact readable blob content still confirms the shared helper catalog in `tools/lib/bpf/zigux_segments/manifest.json`, the helper-local routing evidence in `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, and the dedicated survey gate in `zigux/tests/phase8_libbpf_segments.zig`.
- that narrower readback means this lane should stay grounded in exact readable blob content and current tree evidence rather than older broader build-surface wording.
- the live helper packet still keeps `fdinfo-map-info-helpers`, `map-reuse-compatibility`, `file-path-and-handle-bridge`, `perf-buffer-online-cpu-routing`, and `perf-buffer-poll-bookkeeping` explicit in the broader segmented catalog.
- current `master` also carries helper-local routing evidence in `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, where `advanceOnlineCpuCursor()` and `summarizeOnlineCpuRouting()` keep the online-CPU cursor and routing-summary helper packet explicit below the broader setup-side routing boundary.

The manifest currently records twelve bounded segments: seven landed helper or helper-adjacent slices and five deferred or blocked follow-ons.

The seven landed bounded slices are `logging-version-and-errno`, `pin-path-helpers`, `cpu-mask-parsing`, `type-name-helpers`, `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and `perf-buffer-poll-bookkeeping`.

An older shared-wording pass still carried the sentence "The two ready-next helper-first catalog entries are `fdinfo-map-info-helpers` and `map-reuse-compatibility`, and they stay queued helper-first catalog entries until the next bridge-local helper follow-through lands." Current `master` no longer matches that wording: the manifest and the shared file-path bridge packet now treat those two bridge-adjacent helpers as landed helper-first slices while keeping the heavier `file-path-and-handle-bridge` destination deferred.

The deferred or blocked follow-ons are `file-path-and-handle-bridge`, `perf-buffer-online-cpu-routing`, `skeleton-population`, `object-and-elf-loader`, and `btf-relocation-and-program-load`.

Those segments still keep the bounded fdinfo helper packet explicit while the resource-boundary packet still stays deferred.

The deferred `perf-buffer-online-cpu-routing` segment also stays explicitly larger than the helper-local `online_cpu_routing.zig` evidence: the setup-side packet still covers sysfs reads, `perf_event_open()` setup, `mmap()`-backed ring state, per-CPU perf-event-array updates, epoll registration, and timeout-sensitive waits, while the landed helper-local cursor and routing-summary code remains smaller than that broader setup boundary.

## Current bounded gap
The real current gap is now survey truthfulness about the already-landed checker packet and helper-local routing evidence, not a missing checker rule or docs-root summary.

Exact 2026-05-14 tree readback keeps the earlier docs-root reopen cue closed: the shared docs-root, scripts-root, tests-root, and validator reminder files are still present, but this note had kept repeating an older broader helper-plus-build inventory as if the current tree still exposed it directly.

Current exact tree readback no longer supports calling `zigux/tests/phase8_build.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, or `tools/lib/bpf/zigux_segments/verify.zig` part of the current visible build surface for this lane, so this packet should stay grounded in the narrower readable manifest, routing-helper, and survey-gate evidence until fresh exact readback shows those broader replay files again.

That same checker packet should also keep the landed `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence explicit so the deferred routing segment stays framed as broader setup-side parity rather than as if no routing-side helper evidence exists yet.

Current mixed 2026-05-14 readback also closes the older scripts-root omission cue outside this lane: `scripts/zigux/README.md` now explicitly carries `scripts/zigux/check-phase8-exec-cmd-packet.py` alongside the broader Phase 8 checker inventory that `Documentation/zigux/phase8-tooling-lane-sequencing.md`, `zigux/Makefile`, and the shipped exec-cmd packet already keep visible on `master`.

That scripts-root alignment keeps this survey focused on libbpf helper-local truthfulness rather than reopening shared wording from a stale non-libbpf cue.

That leaves the narrower same-lane task as keeping this survey parked and truthful about the currently readable manifest, test, and helper-local routing evidence instead of reopening the same checker-local step.

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
Keep the libbpf survey packet parked after this current-tree refresh unless a fresh shared reminder-surface drift reappears against the narrower readable manifest-plus-routing evidence.

Preferred order:
1. re-read the exact current-tree packet before calling any broader build surface live again, starting with `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, `zigux/tests/phase8_libbpf_segments.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, and `zigux/tests/phase8_pin_path.zig`
2. confirm the dedicated survey, `scripts/zigux/check-phase8-libbpf-shard-routes.py`, and the shared reminder packet no longer imply that `zigux/tests/phase8_build.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, or `tools/lib/bpf/zigux_segments/verify.zig` are still visible current-tree replay surfaces
3. treat the older `scripts/zigux/README.md` exec-cmd-checker omission cue as closed on current `master`; only reopen shared wording from this libbpf survey lane if a fresh scripts-root drift appears that the dedicated sequencing note and current scripts packet both confirm
4. keep the helper-local `online_cpu_routing.zig` evidence explicit while staying smaller than deferred `perf-buffer-online-cpu-routing`, `perf_event_open()` setup, epoll registration, mmap-backed ring ownership, standalone timer or clockevent helper behavior, or broader timeout-sensitive routing behavior

especially the explicit `standalone timer or clockevent helper behavior` and broader timeout-sensitive routing behavior boundaries that keep this packet smaller than the deferred interrupt-routing work.
