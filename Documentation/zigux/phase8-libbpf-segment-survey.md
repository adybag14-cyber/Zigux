# Phase 8 Libbpf Segment Survey

This note records the current bounded Phase 8 libbpf segmentation reviewability gap against the roadmap's `tools/lib/bpf/libbpf.c` anchor.

## Status
- `PHASE8_STATUS=parked`
- `PHASE8_SURVEY=libbpf-segment-gap-readback`
- roadmap anchor: `tools/lib/bpf/libbpf.c`
- intended Zigux destination family: `tools/lib/bpf/zigux_segments/`
- scope: current-tree reviewability and lane-safe next-step selection only

## Why this survey exists
The Phase 8 roadmap still calls for a segmented libbpf rollout under `tools/lib/bpf/zigux_segments/` so Zigux can expand through helper-first, output-stable tooling slices instead of widening directly into heavier routing, object-model, or descriptor-lifecycle behavior.

That plan only stays reviewable if the repo's public survey surfaces truthfully describe what is actually present on `master`.

## Current public-tree readback
Public default-branch exact readback on 2026-05-12 still showed:
- `Documentation/zigux/README.md` and `scripts/zigux/README.md` still expose the broader Phase 8 libbpf helper packet instead of only the shared sequencing, bridge-boundary, and bridge-slice notes.
- `zigux/tests/phase8_build.zig` still wires the current libbpf helper-first shard packet through `phase8_cpu_mask.zig`, `phase8_logging.zig`, `phase8_pin_path.zig`, `phase8_bpf_type_names.zig`, `phase8_file_path_handle_bridge.zig`, `phase8_perf_buffer_poll.zig`, `phase8_libbpf_segments.zig`, and `tools/lib/bpf/zigux_segments/verify.zig`.
- same-day mixed authenticated readback still shows targeted readable helper blobs include `tools/lib/bpf/zigux_segments/cpu_mask.zig` and `tools/lib/bpf/zigux_segments/logging.zig`, while `zigux/tests/phase8_pin_path.zig` remains readable even though authenticated contents reads from this environment still return `404` for `Documentation/zigux/phase8-pin-path-slice.md` and `tools/lib/bpf/zigux_segments/pin_path.zig`, so the pin-path shard should stay framed as a mixed review-surface split rather than a removed helper packet.
- the manifest-backed bridge packet still keeps the roadmap boundary explicit: `fdinfo-map-info-helpers` and `map-reuse-compatibility` are already landed inside `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, while the broader `file-path-and-handle-bridge` resource boundary stays deferred.
- authenticated contents reads remain inconsistent for some paired Phase 8 docs and helper paths from this environment, so exact readable blob content and public tree evidence should outweigh older absent-file assumptions when choosing the next bounded step.

## Current bounded gap
The real current gap is still reviewability truthfulness, not a helper-behavior claim.

Same-day 2026-05-12 readback kept the pin-path evidence narrower and mixed: the shared build plus tests-root shard still show the helper-first pin-path packet is present on `master`, but the paired docs-plus-source note and helper blob remain unreadable through the authenticated contents route used here. This survey should keep that split explicit without collapsing back into the heavier deferred bridge or routing work.

## Non-goals
This survey does not claim:
- restored direct behavior verification for every paired Phase 8 libbpf test shard by itself
- direct `perf_event_open()` setup, epoll wiring, mmap-backed ring ownership, or online-CPU routing parity
- direct procfs reads, live bpffs opens, token creation, `bpf_obj_get()` reopen flow, or fd ownership parity for the deferred resource-boundary packet
- any reopen of the shared command or symbol packets
- any reopen of deferred object-model, descriptor-lifecycle, or bridge-heavy libbpf work

## Next bounded step
Start with the smallest directly coupled libbpf survey follow-through that matches the current readable tree exactly, and keep `scripts/zigux/check-phase8-libbpf-shard-routes.py` aligned with this survey note so the broader helper-plus-build packet fails closed when these live markers drift again.

Preferred order:
1. re-read the dedicated Phase 8 libbpf shard files named by `zigux/tests/phase8_build.zig` before calling any helper packet removed
2. after this survey sync, only then trim or widen any shared reminder surface that still disagrees with the live helper-plus-build packet
3. keep follow-up smaller than deferred `perf-buffer-online-cpu-routing`, `perf_event_open()` setup, epoll registration, mmap-backed ring ownership, or broader timeout-sensitive routing behavior

Keep follow-up inside the libbpf segment survey family until the public survey packet and the current readable helper-plus-build evidence agree again.
