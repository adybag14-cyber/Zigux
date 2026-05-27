# Phase 8 Libbpf Segment Survey

This note records the current bounded Phase 8 libbpf segmentation reviewability gap against the roadmap's `tools/lib/bpf/libbpf.c` anchor.

## Status
- `PHASE8_STATUS=parked`
- `PHASE8_SURVEY=libbpf-segment-gap-readback`
- survey checkpoint: refreshed against inspected current `master` readback on 2026-05-27
- roadmap anchor: `tools/lib/bpf/libbpf.c`
- intended Zigux destination family: `tools/lib/bpf/zigux_segments/`
- scope: current-tree reviewability and lane-safe next-step selection only

## Why this survey exists
Phase 8 only makes roadmap-aligned progress here if libbpf grows as reviewable helper-first shards instead of as a single opaque port attempt.

That means the dedicated survey has to keep directly readable helper evidence, public current-tree readback, and shared reminder surfaces separated without losing the current roadmap-aligned packet.

## Current helper-plus-build packet
Exact authenticated contents readback on 2026-05-27 still keeps `Documentation/zigux/phase8-libbpf-segment-survey.md`, `tools/lib/bpf/zigux_segments/verify.zig`, `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/cpu_mask_verify.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/logging_verify.zig`, `tools/lib/bpf/zigux_segments/pin_path.zig`, `tools/lib/bpf/zigux_segments/pin_path_verify.zig`, `tools/lib/bpf/zigux_segments/type_names.zig`, `tools/lib/bpf/zigux_segments/type_names_verify.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge_verify.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig`, `tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`, `tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig`, `tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig`, `zigux/tests/phase8_libbpf_segments.zig`, and `zigux/tests/phase8_libbpf_segments_only_build.zig` directly readable.

The directly readable stable-output helper set therefore now keeps the aggregate verifier plus `cpu_mask.zig`, `cpu_mask_verify.zig`, `logging.zig`, `logging_verify.zig`, `pin_path.zig`, `pin_path_verify.zig`, `type_names.zig`, `type_names_verify.zig`, `perf_buffer_poll.zig`, `perf_buffer_wait_budget.zig`, `perf_buffer_poll_verify.zig`, `perf_buffer_ready_window.zig`, `online_cpu_routing.zig`, `online_cpu_routing_mask_bridge.zig`, `online_cpu_routing_mask_bridge_verify.zig`, `online_cpu_routing_verify.zig`, `ready_buffer_attempt_verify.zig`, `ready_buffer_fd_verify.zig`, and `ready_buffer_window_verify.zig` explicit. Shared reminder surfaces may still name older bridge helper and focused build-shard vocabulary, but this survey should keep those bridge-facing paths separate from the exact helper set until the same readback mode serves them directly again.

`tools/lib/bpf/zigux_segments/cpu_mask_verify.zig` now keeps direct parse, string-backed summary, reader-backed summary, auto-count, and fail-closed cpu-mask outputs explicit beside that same stable-output helper packet.

`tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig` now keeps wait classification, poll summary, execution summary, and impossible-summary fail-closed outputs explicit beside that same stable-output helper packet.

`zigux/tests/phase8_build.zig` still wires the current libbpf helper-first shard packet.

`zigux/tests/phase8_libbpf_segments.zig` plus `zigux/tests/phase8_libbpf_segments_only_build.zig` now keep the shared stable-output verifier, mixed-source bridge, focused verify-routing, and no-timer poll-boundary packet explicit from the tests root beside that same helper-first shard packet.

The readable helper packet now keeps stable cpu-mask parsing, logging/version/errno formatting, pin-path composition and sanitization, type-name formatter outputs, bounded wait-budget normalization, perf-buffer summary bookkeeping, ready-buffer window mapped-size and lookup-return outputs, helper-local online-CPU routing outputs, and cpu-mask-backed next-route CPU-index and buffer-FD wrappers explicit below the still-deferred setup-side routing boundary.

`tools/lib/bpf/zigux_segments/online_cpu_routing.zig` keeps `advanceOnlineCpuCursor()`, `summarizeNextOnlineCpuRoute()`, and `summarizeOnlineCpuRouting()` explicit as bounded helper-local review surfaces below the still-deferred setup-side routing boundary.

`tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge.zig` now keeps `summarizeNextOnlineCpuRouteFromString()`, `summarizeNextOnlineCpuRouteFromReader()`, `resolveNextOnlineCpuRouteCpuIndexFromString()`, `resolveNextOnlineCpuRouteCpuIndexFromReader()`, `resolveNextOnlineCpuRouteBufferFdFromString()`, and `resolveNextOnlineCpuRouteBufferFdFromReader()` explicit as cpu-mask-backed helper-local routing bridges below the still-deferred setup-side routing boundary.

The directly readable verifier packet now also keeps dedicated stable-output witnesses for cpu-mask parse, string-backed summary, reader-backed summary, auto-count, and fail-closed outputs, online-CPU mask-bridge next-route CPU-index and buffer-FD wrappers, logging env/version/error outputs, perf-buffer wait-classification, poll-summary, execution-summary, and impossible-summary fail-closed outputs, pin-path map/program output and validation wrappers, online-CPU route CPU-index and buffer-FD wrappers, ready-buffer attempt wrappers, ready-buffer FD wrappers, ready-buffer window mapped-size and lookup-return wrappers, and type-name lookup plus formatter wrappers explicit beside the aggregate `verify.zig` replay surface.

The new dedicated cpu-mask verifier shard stays bounded to parse, summary, auto-count, and reader/validation witnesses and does not widen into setup-side routing or bridge-heavy setup.

Current authenticated contents readback in this runtime now reaches the mixed-source bridge reminder packet more directly: the stable-output helper set above stays the exact authenticated helper anchor, while the same contents path now also serves `tools/lib/bpf/zigux_segments/manifest.json`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, and `zigux/tests/phase8_file_path_handle_bridge.zig` on current `master`. The focused bridge-only build and broader replay companions, including `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, remain reminder vocabulary outside the exact stable-output helper set. Keep those bridge-facing paths explicit without folding them back into the exact helper set or promoting the deferred resource boundary into helper-first proof.
That narrower split is now packet role rather than fetchability: the bridge-side helper and focused bridge witness stay on the boundary side of the Phase 8 packet, while the focused bridge-only build shard and shared replay routes remain reminder evidence instead of stable-output helper proof.

## Current bounded gap
The current helper-plus-build survey packet is now truthful about the directly readable stable-output helper set, the helper-local routing evidence, the dedicated cpu-mask, perf-buffer poll, logging, ready-buffer, type-name, and mask-bridge verifier shards, the shared `phase8_build` companion route, and the directly readable `phase8_libbpf_segments` compatibility witness pair.

The remaining repo-reality gap in this note is no longer a helper-local code omission. It is reminder-surface discipline: older bridge, manifest, and focused build names may still appear in shared Phase 8 vocabulary, but this survey should now treat the manifest, the two bridge reminder docs, the bridge helper, and the focused bridge witness as direct-readback companion evidence, while the focused bridge-only build shard stays outside the exact stable-output helper set.
The shared tests-root reminder also now needs to distinguish packet classes more carefully: `Documentation/zigux/phase8-libbpf-segment-survey.md`, `zigux/tests/phase8_libbpf_segments.zig`, and `zigux/tests/phase8_libbpf_segments_only_build.zig` are directly readable broader packet evidence on current `master`, while the help and kallsyms companions still stay in the separate public-tree-backed bucket outside the narrow direct-readback anchor set.
That older mixed-source wording now needs the same caution: the bridge-side reminder docs, the bridge helper, and the focused bridge witness stay reviewable on current `master`, but the focused bridge-only build shard still stays outside the exact stable-output helper set because it documents the deferred bridge boundary rather than extending helper semantics.

Current repo-facing reminder surfaces already keep the bridge helper, the focused bridge build shard, the focused libbpf-segment shard, and the shared Phase 8 build replay explicit on `master`, while that same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/logging_verify.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`, `tools/lib/bpf/zigux_segments/pin_path_verify.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge_verify.zig`, `tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`, and `tools/lib/bpf/zigux_segments/type_names_verify.zig` explicit.

Those same repo-facing reminder surfaces also keep the timing-adjacent perf-buffer poll boundary explicit through `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and `make -C zigux phase8-perf-buffer-poll-test`, so the shared packet stays truthful about no standalone timer or clockevent helper behavior and about no broader timeout-sensitive routing behavior.

That same reminder-side bridge test packet in `zigux/tests/phase8_file_path_handle_bridge.zig` now also keeps the Linux-style replay route, the manifest-backed split between the landed `fdinfo-path-and-reuse-name-footholds`, `fdinfo-map-info-helpers`, and `map-reuse-compatibility` helper slices plus the deferred `file-path-and-handle-bridge` resource boundary, and the source-level ban on `bpf_obj_get(`, `F_DUPFD_CLOEXEC`, and direct file-open bridge-heavy calls explicit on current `master`.

`tools/lib/bpf/zigux_segments/manifest.json` has since advanced both `fdinfo-map-info-helpers` and `map-reuse-compatibility` as landed helper-first slices with the newer shared bridge rationale, so the smallest same-family reminder drift is now whether sibling reminder surfaces continue to reflect those same landed `why_now` strings whenever they restate the focused bridge packet.
The shared bridge packet still keeps `fdinfo-path-and-reuse-name-footholds` explicit beside those landed helper slices while leaving `file-path-and-handle-bridge` deferred as the remaining resource boundary, so reminder wording should preserve that landed-helper-versus-deferred-bridge split rather than sliding back to the older partial-helper story.

That focused libbpf-segment shard is currently carried by `zigux/tests/phase8_verify_routing_gap.zig` plus `zigux/tests/phase8_verify_routing_gap_only_build.zig`, which keep the bounded online-CPU route CPU-index witness explicit without widening into setup-side routing, reopen-flow, or bridge-heavy claims.

The timing-adjacent poll boundary is already explicit through `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and `make -C zigux phase8-perf-buffer-poll-test`; those reminder surfaces keep the packet honest about no standalone timer or clockevent helper behavior and about no broader timeout-sensitive routing behavior.

This survey should therefore keep the helper-first packet and the shared wrapper-route vocabulary explicit together without promoting the still-deferred setup-side routing, reopen-flow, token-materialization, object-model, or bridge-heavy work into direct authenticated helper proof.

## Non-goals
This survey slice does not yet claim:
- any direct Zig port of `tools/lib/bpf/libbpf.c`
- direct readable proof for every bridge, routing, manifest, or focused build shard named by roadmap or older reminder surfaces
- direct `perf_event_open()` setup, epoll wiring, mmap-backed ring ownership, or online-CPU setup parity
- live bpffs reopen flow, token materialization, `bpf_obj_get()` reopen flow, or broader fd ownership parity
- standalone timer or clockevent helper behavior
- broader timeout-sensitive routing behavior
- any reopen of the shared command or symbol packets
- any reopen of deferred object-model, descriptor-lifecycle, or bridge-heavy libbpf work

## Next bounded step
Keep the libbpf survey packet parked after this helper-local cpumask-backed routing bridge update unless a fresh shared reminder-surface drift reappears against the current helper-plus-build evidence.

Preferred order:
1. reread `Documentation/zigux/phase8-libbpf-segment-survey.md`, `tools/lib/bpf/zigux_segments/verify.zig`, `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/cpu_mask_verify.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/logging_verify.zig`, `tools/lib/bpf/zigux_segments/pin_path.zig`, `tools/lib/bpf/zigux_segments/pin_path_verify.zig`, `tools/lib/bpf/zigux_segments/type_names.zig`, `tools/lib/bpf/zigux_segments/type_names_verify.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge_verify.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig`, `tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`, `tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig`, and `tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig`, `zigux/tests/phase8_verify_routing_gap.zig`, `zigux/tests/phase8_verify_routing_gap_only_build.zig`, `zigux/tests/phase8_libbpf_segments.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, `zigux/tests/phase8_build.zig`, and `zigux/Makefile` together before treating any helper-first shard or build route as removed
2. keep this survey aligned to the direct-helper packet plus the narrower direct-readback bridge reminder docs unless a fresh repo reread proves one of those reminder docs or build companions disappeared again
3. if sibling reminder surfaces drift again against the current helper-plus-build evidence, correct the smallest reminder sentence first and keep the focused bridge test plus manifest wording aligned to the current three landed helper slices plus the deferred `file-path-and-handle-bridge` resource boundary
4. otherwise keep bridge, routing, manifest, and focused build references framed according to the current direct-helper packet plus the mixed-source bridge reminder packet