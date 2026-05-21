# Phase 8 Libbpf Segment Survey

This note records the current bounded Phase 8 libbpf segmentation reviewability gap against the roadmap's `tools/lib/bpf/libbpf.c` anchor.

## Status
- `PHASE8_STATUS=parked`
- `PHASE8_SURVEY=libbpf-segment-gap-readback`
- survey checkpoint: refreshed against inspected current `master` readback on 2026-05-20
- roadmap anchor: `tools/lib/bpf/libbpf.c`
- intended Zigux destination family: `tools/lib/bpf/zigux_segments/`
- scope: current-tree reviewability and lane-safe next-step selection only

## Why this survey exists
Phase 8 only makes roadmap-aligned progress here if libbpf grows as reviewable helper-first shards instead of as a single opaque port attempt.

That means the dedicated survey has to keep directly readable helper evidence, public current-tree readback, and shared reminder surfaces separated without losing the current roadmap-aligned packet.

## Current helper-plus-build packet
Exact authenticated contents readback on 2026-05-20 still keeps `Documentation/zigux/phase8-libbpf-segment-survey.md`, `tools/lib/bpf/zigux_segments/verify.zig`, `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/cpu_mask_verify.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/logging_verify.zig`, `tools/lib/bpf/zigux_segments/pin_path.zig`, `tools/lib/bpf/zigux_segments/pin_path_verify.zig`, `tools/lib/bpf/zigux_segments/type_names.zig`, `tools/lib/bpf/zigux_segments/type_names_verify.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig`, `tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`, `tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig`, and `tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig` directly readable.

The directly readable stable-output helper set therefore now keeps the aggregate verifier plus `cpu_mask.zig`, `cpu_mask_verify.zig`, `logging.zig`, `logging_verify.zig`, `pin_path.zig`, `pin_path_verify.zig`, `type_names.zig`, `type_names_verify.zig`, `perf_buffer_poll.zig`, `perf_buffer_ready_window.zig`, `online_cpu_routing.zig`, `online_cpu_routing_verify.zig`, `ready_buffer_attempt_verify.zig`, `ready_buffer_fd_verify.zig`, and `ready_buffer_window_verify.zig` explicit. Shared reminder surfaces may still name older bridge helper and focused build-shard vocabulary, but this survey should keep those bridge-facing paths separate from the exact authenticated helper set until the same readback mode serves them directly again.

`tools/lib/bpf/zigux_segments/cpu_mask_verify.zig` now keeps direct parse, string-backed summary, reader-backed summary, auto-count, and fail-closed cpu-mask outputs explicit beside that same stable-output helper packet.

`zigux/tests/phase8_build.zig` still wires the current libbpf helper-first shard packet.

The readable helper packet now keeps stable cpu-mask parsing, logging/version/errno formatting, pin-path composition and sanitization, type-name formatter outputs, perf-buffer summary bookkeeping, ready-buffer window mapped-size and lookup-return outputs, and helper-local online-CPU routing outputs explicit below the still-deferred setup-side routing boundary.

`tools/lib/bpf/zigux_segments/online_cpu_routing.zig` keeps `advanceOnlineCpuCursor()`, `summarizeNextOnlineCpuRoute()`, and `summarizeOnlineCpuRouting()` explicit as bounded helper-local review surfaces below the still-deferred setup-side routing boundary.

The directly readable verifier packet now also keeps dedicated stable-output witnesses for cpu-mask parse, string-backed summary, reader-backed summary, auto-count, and fail-closed outputs, logging env/version/error outputs, pin-path map/program output and validation wrappers, online-CPU route CPU-index and buffer-FD wrappers, ready-buffer attempt wrappers, ready-buffer FD wrappers, ready-buffer window mapped-size and lookup-return wrappers, and type-name lookup plus formatter wrappers explicit beside the aggregate `verify.zig` replay surface.

The new dedicated cpu-mask verifier shard stays bounded to parse, summary, auto-count, and reader/validation witnesses and does not widen into setup-side routing or bridge-heavy setup.

Current authenticated tree readback in this runtime is narrower than some older Phase 8 reminder surfaces: the helper packet above is directly readable, but `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, and the focused libbpf bridge-side build companions are not currently materialized through the same direct-read path. Keep those older names framed as reminder-only or wrapper-route vocabulary rather than as direct helper-set proof until the same current-master readback path serves them again.

## Current bounded gap
The current helper-plus-build survey packet is now truthful about the directly readable stable-output helper set, the helper-local routing evidence, the dedicated cpu-mask, logging, ready-buffer, and type-name verifier shards, and the shared `phase8_build` companion route.

The remaining repo-reality gap in this note is no longer a helper-local code omission. It is reminder-surface discipline: older bridge, manifest, and focused build names may still appear in shared Phase 8 vocabulary, but this survey should not describe those paths as mere authenticated-read flakiness or fold them back into the direct helper packet while they remain outside the same exact current-tree readback mode.

Current repo-facing reminder surfaces already keep the bridge helper, the focused bridge build shard, the focused libbpf-segment shard, and the shared Phase 8 build replay explicit on `master`, while that same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/logging_verify.zig`, `tools/lib/bpf/zigux_segments/pin_path_verify.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence, `tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`, and `tools/lib/bpf/zigux_segments/type_names_verify.zig` explicit.

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
Keep the libbpf survey packet parked after this readback truthfulness repair unless a fresh shared reminder-surface drift reappears against the current helper-plus-build evidence.

Preferred order:
1. reread `Documentation/zigux/phase8-libbpf-segment-survey.md`, `tools/lib/bpf/zigux_segments/verify.zig`, `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/cpu_mask_verify.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/logging_verify.zig`, `tools/lib/bpf/zigux_segments/pin_path.zig`, `tools/lib/bpf/zigux_segments/pin_path_verify.zig`, `tools/lib/bpf/zigux_segments/type_names.zig`, `tools/lib/bpf/zigux_segments/type_names_verify.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig`, `tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`, `tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig`, and `tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig`, `zigux/tests/phase8_verify_routing_gap.zig`, `zigux/tests/phase8_verify_routing_gap_only_build.zig`, `zigux/tests/phase8_build.zig`, and `zigux/Makefile` together before treating any helper-first shard or build route as removed
2. if current-master authenticated reads later rematerialize `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, or focused build companions, retell this survey to that larger directly inspectable packet without widening into new helper claims
3. if sibling reminder surfaces drift again against the current helper-plus-build evidence, correct the smallest reminder sentence before reopening any bridge, routing, checker, or validator follow-through
4. otherwise keep bridge, routing, manifest, and focused build references framed according to the current mixed direct-helper-plus-wrapper-route packet
