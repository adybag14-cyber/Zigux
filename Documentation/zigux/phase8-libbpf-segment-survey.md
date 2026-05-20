# Phase 8 Libbpf Segment Survey

This note records the current bounded Phase 8 libbpf segmentation reviewability gap against the roadmap's `tools/lib/bpf/libbpf.c` anchor.

## Status
- `PHASE8_STATUS=parked`
- `PHASE8_SURVEY=libbpf-segment-gap-readback`
- survey checkpoint: refreshed against inspected `master` head `089188c96b86c0da16088e916094a7c977d0cfc6` on 2026-05-19
- roadmap anchor: `tools/lib/bpf/libbpf.c`
- intended Zigux destination family: `tools/lib/bpf/zigux_segments/`
- scope: current-tree reviewability and lane-safe next-step selection only

## Why this survey exists
Phase 8 only makes roadmap-aligned progress here if libbpf grows as reviewable helper-first shards instead of as a single opaque port attempt.

That means the dedicated survey has to keep directly readable helper evidence, public current-tree readback, and shared reminder surfaces separated without losing the current roadmap-aligned packet.

## Current helper-plus-build packet
Exact authenticated contents readback on 2026-05-19 still keeps `Documentation/zigux/phase8-libbpf-segment-survey.md`, `tools/lib/bpf/zigux_segments/verify.zig`, `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/pin_path.zig`, `tools/lib/bpf/zigux_segments/type_names.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`, and `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` directly readable.

The directly readable stable-output helper set therefore remains the verifier plus `cpu_mask.zig`, `logging.zig`, `pin_path.zig`, `type_names.zig`, `perf_buffer_poll.zig`, and `online_cpu_routing.zig`. Shared reminder surfaces may still name the bridge helper and focused build shards, but this survey should keep those bridge-facing paths separate from the exact authenticated helper set until the same readback mode serves them directly again.

`Documentation/zigux/README.md` now names the live `Documentation/zigux/phase8-file-path-handle-bridge-slice.md` note in the broad Phase 8 docs summary, and `scripts/zigux/README.md` keeps the broader Phase 8 libbpf helper packet visible through the shared sequencing, bridge-boundary, bridge-slice, checker, and build-surface reminders without treating older missing slice names as direct current-readback proof.

`zigux/tests/phase8_build.zig` still wires the current libbpf helper-first shard packet.

The readable helper packet now keeps stable cpu-mask parsing, logging/version/errno formatting, pin-path composition and sanitization, type-name formatter outputs, perf-buffer summary bookkeeping, and helper-local online-CPU routing outputs explicit below the still-deferred setup-side routing boundary.

`tools/lib/bpf/zigux_segments/online_cpu_routing.zig` keeps `advanceOnlineCpuCursor()`, `summarizeNextOnlineCpuRoute()`, and `summarizeOnlineCpuRouting()` explicit as bounded helper-local review surfaces below the still-deferred setup-side routing boundary.

The manifest currently records twelve bounded segments: seven landed helper or helper-adjacent slices and five deferred or blocked follow-ons.

The seven landed bounded slices are `logging-version-and-errno`, `pin-path-helpers`, `cpu-mask-parsing`, `type-name-helpers`, `fdinfo-map-info-helpers`, `map-reuse-compatibility`, and `perf-buffer-poll-bookkeeping`.

Authenticated contents reads from this environment still flap for `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, and some focused build or test companions, but the public current-tree reread plus the checker-backed reminder packet now describe a larger truthful Phase 8 libbpf surface than the older gap-only wording did.

## Current bounded gap
The current helper-plus-build survey packet is now truthful about the directly readable stable-output helper set, the helper-local routing evidence, the timing-adjacent poll note, and the landed bridge-plus-build reminder packet.

The remaining repo-reality gap in this note is still authenticated exact-read flakiness around `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, and some focused build companions. The already-readable helper packet is now stable-output backed through `tools/lib/bpf/zigux_segments/verify.zig`, so this survey should describe the bridge-facing paths as shared reminder or public-tree-backed evidence rather than as part of the direct authenticated helper set.

Current repo-facing reminder surfaces already keep the bridge helper vocabulary, the focused bridge build shard, the focused libbpf-segment shard, and the shared Phase 8 build replay explicit on `master`, while that same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence explicit.

The timing-adjacent poll boundary is already explicit through `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and `make -C zigux phase8-perf-buffer-poll-test`; those reminder surfaces keep the packet honest about no standalone timer or clockevent helper behavior and about no broader timeout-sensitive routing behavior.

This survey should therefore keep the helper-first packet, the bridge-plus-build reminder packet, and the routing-helper evidence explicit together without promoting the still-deferred setup-side routing, reopen-flow, token-materialization, or object-model work.

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
Keep the libbpf survey packet parked after this survey-and-route sync unless a fresh shared reminder-surface drift reappears against the current helper-plus-build evidence.

Preferred order:
1. reread `Documentation/zigux/phase8-libbpf-segment-survey.md`, `tools/lib/bpf/zigux_segments/verify.zig`, `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/pin_path.zig`, `tools/lib/bpf/zigux_segments/type_names.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, `zigux/tests/phase8_build.zig`, and `zigux/Makefile` together before treating any helper-first shard or build route as removed
2. if authenticated exact reads stabilize for `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, or focused build companions, retell this survey to that larger directly inspectable packet without widening into new helper claims
3. if sibling reminder surfaces drift again against the current helper-plus-build evidence, correct the smallest reminder sentence before reopening any bridge, routing, checker, or validator follow-through
4. otherwise keep bridge, routing, manifest, and focused build references framed according to the current mixed authenticated-plus-public reread surface