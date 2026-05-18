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
- `Documentation/zigux/README.md` now names the live `Documentation/zigux/phase8-file-path-handle-bridge-slice.md` note in the broad Phase 8 docs summary, public Phase 8 readback still serves `Documentation/zigux/phase8-bpf-type-names-slice.md`, and `scripts/zigux/README.md` keeps the broader Phase 8 libbpf helper packet visible through the shared sequencing, bridge-boundary, bridge-slice, checker, and build-surface reminders.
- `zigux/tests/phase8_build.zig` still wires the current libbpf helper-first shard packet through `phase8_cpu_mask.zig`, `phase8_logging.zig`, `phase8_pin_path.zig`, `phase8_bpf_type_names.zig`, `phase8_file_path_handle_bridge.zig`, `phase8_perf_buffer_poll.zig`, `phase8_libbpf_segments.zig`, and `tools/lib/bpf/zigux_segments/verify.zig`.
- the shared helper catalog still comes from `tools/lib/bpf/zigux_segments/manifest.json`.
- the shared landed helper packet still names `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/pin_path.zig`, `tools/lib/bpf/zigux_segments/type_names.zig`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, and `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`.
- the shared landed helper packet still names `zigux/tests/phase8_bpf_type_names.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, `zigux/tests/phase8_libbpf_segments.zig`, and `zigux/tests/phase8_libbpf_segments_only_build.zig`.
- the focused replay routes remain `make -C zigux phase8-libbpf-segments-test`, `zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all`, `make -C zigux phase8-perf-buffer-poll-test`, `zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all`, `make -C zigux phase8-test`, and `zig build test --build-file zigux/tests/phase8_build.zig --summary all`.
- same-day mixed authenticated readback still shows targeted readable helper blobs include `tools/lib/bpf/zigux_segments/cpu_mask.zig` and `tools/lib/bpf/zigux_segments/logging.zig`, while `zigux/tests/phase8_pin_path.zig` remains readable even though authenticated contents reads from this environment still return `404` for `Documentation/zigux/phase8-pin-path-slice.md` and `tools/lib/bpf/zigux_segments/pin_path.zig`.
- retained marker for the existing shared checker: "targeted readable helper blobs still include `tools/lib/bpf/zigux_segments/cpu_mask.zig` and `tools/lib/bpf/zigux_segments/logging.zig`, while `zigux/tests/phase8_pin_path.zig` remains readable even though authenticated contents reads from this environment still return `404` for `Documentation/zigux/phase8-pin-path-slice.md` and `tools/lib/bpf/zigux_segments/pin_path.zig`"
- that mixed readback means the pin-path shard should stay framed as a review-surface split rather than a removed helper packet.
- the live helper packet still keeps `fdinfo-map-info-helpers`, `map-reuse-compatibility`, `file-path-and-handle-bridge`, `perf-buffer-online-cpu-routing`, and `perf-buffer-poll-bookkeeping` explicit in the broader segmented catalog.
- current `master` also carries helper-local routing evidence in `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, where `advanceOnlineCpuCursor()` and `summarizeOnlineCpuRouting()` keep the online-CPU cursor and routing-summary helper packet explicit below the broader setup-side routing boundary.
- authenticated contents reads remain inconsistent for some paired Phase 8 docs and helper paths from this environment, so exact readable blob content and public tree evidence should outweigh older absent-file assumptions when choosing the next bounded step.

The manifest currently records twelve bounded segments: seven landed helper or helper-adjacent slices and five deferred or blocked follow-ons.

The seven landed bounded slices are `logging-version-and-errno`, `pin-path-helpers`, `cpu-mask-parsing`, `type-name-helpers`, `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and `perf-buffer-poll-bookkeeping`.

An older shared-wording pass still carried the sentence "The two ready-next helper-first catalog entries are `fdinfo-map-info-helpers` and `map-reuse-compatibility`, and they stay queued helper-first catalog entries until the next bridge-local helper follow-through lands." Current `master` no longer matches that wording: the manifest and the shared file-path bridge packet now treat those two bridge-adjacent helpers as landed helper-first slices while keeping the heavier `file-path-and-handle-bridge` destination deferred.

The deferred or blocked follow-ons are `file-path-and-handle-bridge`, `perf-buffer-online-cpu-routing`, `skeleton-population`, `object-and-elf-loader`, and `btf-relocation-and-program-load`.

Those segments still keep the bounded fdinfo helper packet explicit while the resource-boundary packet still stays deferred.

The deferred `perf-buffer-online-cpu-routing` segment also stays explicitly larger than the helper-local `online_cpu_routing.zig` evidence: the setup-side packet still covers sysfs reads, `perf_event_open()` setup, `mmap()`-backed ring state, per-CPU perf-event-array updates, epoll registration, and timeout-sensitive waits, while the landed helper-local cursor and routing-summary code remains smaller than that broader setup boundary.

## Current bounded gap
The real current gap is now survey truthfulness about the already-landed checker packet and helper-local routing evidence, not a missing checker rule or docs-root summary.

Exact 2026-05-13 readback closes the earlier docs-root reopen cue: public Phase 8 readback still serves both `Documentation/zigux/phase8-bpf-type-names-slice.md` and `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, and `Documentation/zigux/README.md` now names the live file-path bridge note in the broad Phase 8 docs summary.

Exact 2026-05-13 readback also shows `scripts/zigux/check-phase8-libbpf-shard-routes.py` aligned with the closed docs-root cue and the shared bridge-boundary note: the checker now requires `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md` together with the focused `make -C zigux phase8-file-path-handle-bridge-test`, `zig build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all`, `make -C zigux phase8-perf-buffer-poll-test`, and `zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all` markers while this packet still keeps `standalone timer or clockevent helper behavior` and broader timeout-sensitive routing behavior out of scope.

That same checker packet should also keep the landed `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence explicit so the deferred routing segment stays framed as broader setup-side parity rather than as if no routing-side helper evidence exists yet.

That same current packet should also keep the timing-adjacent poll slice explicit: `Documentation/zigux/phase8-perf-buffer-poll-slice.md` and `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig` now keep `perf_buffer__poll(timeout_ms)` reviewable not only for wait-result shaping and upper-bound ready-buffer checks, but also for the fail-closed rule that a successful ready wait cannot stop before every helper-counted ready buffer is processed.

That leaves the narrower same-lane task as keeping this survey parked and truthful about that already-landed checker coverage instead of reopening the same checker-local step.

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
1. re-read the dedicated Phase 8 libbpf shard files named by `zigux/tests/phase8_build.zig` before calling any helper packet removed
2. confirm the shared bridge-boundary note and `scripts/zigux/check-phase8-libbpf-shard-routes.py` still agree on the focused bridge and perf-buffer replay markers while the dedicated survey stays aligned with that already-landed checker state
3. keep the helper-local `online_cpu_routing.zig` evidence explicit, keep the timing-adjacent poll slice explicit for the landed full ready-buffer completion guard, and stay smaller than deferred `perf-buffer-online-cpu-routing`, `perf_event_open()` setup, epoll registration, mmap-backed ring ownership, standalone timer or clockevent helper behavior, or broader timeout-sensitive routing behavior

especially the explicit `standalone timer or clockevent helper behavior` and broader timeout-sensitive routing behavior boundaries that keep this packet smaller than the deferred interrupt-routing work.
