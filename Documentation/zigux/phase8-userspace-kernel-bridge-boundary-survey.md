# Phase 8 Userspace-Kernel Bridge Boundary Survey

This note records the current bounded Phase 8 userspace-adjacent bridge boundary against the roadmap's `tools/lib/bpf/libbpf.c` anchor.

## Status
- `PHASE8_STATUS=parked`
- `PHASE8_SURVEY=userspace-kernel-bridge-boundary-readback`
- survey checkpoint: refreshed against inspected current `master` readback on 2026-05-23
- roadmap anchor: `tools/lib/bpf/libbpf.c`
- intended Zigux destination family: `tools/lib/bpf/zigux_segments/`
- scope: helper-local bridge reviewability and deferred interrupt-routing boundary truthfulness only

## Why this survey exists
Phase 8 only makes roadmap-aligned progress here if Zigux keeps the helper-first bridge packet explicit without pretending that the broader userspace-to-kernel bridge, object reopen flow, or interrupt-routing setup already landed.

That means the note has to keep the landed helper-local bridge packet, the helper-local online-CPU routing evidence, and the still-deferred setup-side routing boundary explicit at the same time.

## Current mixed-source bridge packet
Current `master` still keeps the mixed-source bridge packet reviewable through `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_file_path_handle_boundary_guard.zig`, `zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`, `zigux/tests/phase8_build.zig`, `scripts/zigux/validate-phase8.py`, `zigux/Makefile`, `make -C zigux phase8-file-path-handle-bridge-test`, and `make -C zigux phase8`.

That packet stays smaller than live procfs reads, live bpffs opens, token materialization, `bpf_obj_get()` reopen flow, descriptor replacement, or broader fd ownership behavior.

## Helper-local online-CPU routing evidence
Current `master` also keeps bounded helper-local online-CPU routing evidence explicit through `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` and the focused review witnesses that read it.

That helper-local routing packet keeps `advanceOnlineCpuCursor()`, `summarizeNextOnlineCpuRoute()`, and `summarizeOnlineCpuRouting()` explicit as reviewable route-summary helpers below the riskier setup-side bridge.

It records route selection, missing buffer-slot detection, missing buffer-fd detection, requested-subset summaries, and no-online-CPU summaries without claiming that the surrounding perf-event setup path is already ported.

## Deferred interrupt-routing boundary
It also does not claim the deferred `perf-buffer-online-cpu-routing` packet.

That broader deferred packet still includes `/sys/devices/system/cpu/online` reads, `libbpf_num_possible_cpus()`, online CPU filtering, per-CPU perf-event-array map updates, per-CPU `perf_event_open()` setup, `mmap()` setup, `PERF_EVENT_IOC_ENABLE` enablement, epoll-backed perf FD registration, and poll waits.

Those setup-side routing and ring-ownership steps remain intentionally deferred even though the helper-local routing summaries are already reviewable on current `master`.

## Non-goals
This survey does not yet claim:
- direct `perf_event_open()` parity beyond helper-local summaries
- direct epoll wiring, `mmap()`-backed ring ownership, or broader timeout-sensitive routing behavior
- token materialization or live `bpf_obj_get()` reopen flow
- live procfs reads, live bpffs opens, or descriptor-ownership side effects
- any direct Zig port of the full `tools/lib/bpf/libbpf.c` bridge-heavy setup path

## Next bounded step
Keep this bridge-boundary survey parked unless a future reread finds drift between this note, `Documentation/zigux/phase8-libbpf-segment-survey.md`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, or `zigux/tests/phase8_verify_routing_gap.zig` around the helper-local routing markers or the deferred setup-side routing boundary.

If it reopens, reread those five surfaces together first and keep the next repair note-local or checker-local rather than widening into helper semantics, validator ownership, or setup-side routing delivery.
