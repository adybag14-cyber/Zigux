# Phase 8 Userspace-Kernel Bridge Boundary Survey

This note records the current bounded Phase 8 userspace-adjacent bridge boundary against the roadmap's `tools/lib/bpf/libbpf.c` anchor.

## Status
- `PHASE8_STATUS=parked`
- `PHASE8_SURVEY=userspace-kernel-bridge-boundary-readback`
- survey checkpoint: refreshed against inspected current `master` readback on 2026-05-25
- roadmap anchor: `tools/lib/bpf/libbpf.c`
- intended Zigux destination family: `tools/lib/bpf/zigux_segments/`
- scope: helper-local bridge reviewability and deferred interrupt-routing boundary truthfulness only

## Why this survey exists
Phase 8 only makes roadmap-aligned progress here if Zigux keeps the helper-first bridge packet explicit without pretending that the broader userspace-to-kernel bridge, object reopen flow, or interrupt-routing setup already landed.

That means the note has to keep the landed helper-local bridge packet, the helper-local online-CPU routing evidence, and the still-deferred setup-side routing boundary explicit at the same time.

The separate Phase 8 command-side anchors under `tools/lib/subcmd/` and `tools/lib/symbol/` keep their own parked packets. This survey stays limited to the libbpf-side syscall, descriptor, and routing boundary from `tools/lib/bpf/libbpf.c`.

## Current mixed-source bridge packet
Current `master` still keeps the mixed-source bridge packet reviewable, but the readable sources stay split in this runtime.

Exact authenticated contents readback now serves this survey note, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, and `tools/lib/bpf/zigux_segments/manifest.json` directly, while the broader bridge helper and replay companions remain mixed-source reminder evidence through `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_file_path_handle_boundary_guard.zig`, `zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`, `zigux/tests/phase8_build.zig`, `scripts/zigux/validate-phase8.py`, `zigux/Makefile`, `make -C zigux phase8-file-path-handle-bridge-test`, and `make -C zigux phase8`.

That packet stays smaller than live procfs reads, live bpffs opens, token materialization, `bpf_obj_get()` reopen flow, descriptor replacement, or broader fd ownership behavior.

Within that bounded packet, the already-landed planning helpers still keep `resolveReusePinnedMapAttempt()` and `planTokenPreparation()` explicit as side-effect-free bridge intent summaries: they describe pinned-map reuse and token-readiness decisions without claiming direct procfs reads, bpffs opens, token materialization, or descriptor ownership behavior.

The landed `fdinfo-map-info-helpers` slice therefore still mirrors the manifest rationale exactly: The shared file-path bridge destination already carries the bounded procfs path construction and fdinfo text parsing helpers, so this landed slice should stay explicitly smaller than direct file reads, descriptor ownership, or pinned-object reopen flow.

The sibling `map-reuse-compatibility` slice likewise still mirrors the manifest rationale exactly: The shared bridge surface now already carries the reused-map-name chooser and compatibility comparison as landed helper-only behavior, and it should stay reviewable without widening into FD duplication, close-on-replacement, or pinned-map reopen side effects.

## Helper-local online-CPU routing evidence
Current `master` also keeps bounded helper-local online-CPU routing evidence explicit through `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig`, `zigux/tests/phase8_verify_routing_gap.zig`, and `zigux/tests/phase8_verify_routing_gap_only_build.zig`.

That helper-local routing packet keeps `advanceOnlineCpuCursor()`, `summarizeNextOnlineCpuRoute()`, and `summarizeOnlineCpuRouting()` explicit as reviewable route-summary helpers below the riskier setup-side bridge.

It records route selection, missing buffer-slot detection, missing buffer-fd detection, requested-subset summaries, and no-online-CPU summaries without claiming that the surrounding perf-event setup path is already ported.

The dedicated verifier shard and focused verify-routing witness now also keep typed CPU-index wrappers, errno-shaped CPU-index wrappers, typed buffer-fd wrappers, errno-shaped buffer-fd wrappers, and the hand-built CPU-index overflow fail-closed output explicit without promoting the surrounding perf-event setup path into landed routing delivery.

## Deferred interrupt-routing boundary
It also does not claim the deferred `perf-buffer-online-cpu-routing` packet.

That broader deferred packet still includes `/sys/devices/system/cpu/online` reads, `libbpf_num_possible_cpus()`, online CPU filtering, per-CPU perf-event-array map updates, per-CPU `perf_event_open()` setup, `mmap()` setup, `PERF_EVENT_IOC_ENABLE` enablement, epoll-backed perf FD registration, and poll waits.

Those setup-side routing and ring-ownership steps remain intentionally deferred even though the helper-local routing summaries are already reviewable on current `master`.

The timing-adjacent poll reminder also stays explicit through `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `make -C zigux phase8-perf-buffer-poll-test`, and the shared `phase8` routes; that dedicated packet keeps no standalone timer helper behavior, no standalone clockevent helper behavior, and no broader timeout-sensitive routing behavior explicit while the surrounding setup-side bridge remains deferred.

## Non-goals
This survey does not yet claim:
- direct `perf_event_open()` parity beyond helper-local summaries
- direct epoll wiring, `mmap()`-backed ring ownership, or broader timeout-sensitive routing behavior
- token materialization or live `bpf_obj_get()` reopen flow
- live procfs reads, live bpffs opens, or descriptor-ownership side effects
- standalone timer helper behavior
- standalone clockevent helper behavior
- any direct Zig port of the full `tools/lib/bpf/libbpf.c` bridge-heavy setup path

## Next bounded step
Keep this bridge-boundary survey parked unless a future reread finds drift between this note, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_verify_routing_gap.zig`, or `zigux/tests/phase8_verify_routing_gap_only_build.zig` around the mixed-source bridge packet, the helper-local routing markers, or the deferred setup-side routing boundary.

If it reopens, reread those eight surfaces together first and keep the next repair note-local or checker-local rather than widening into helper semantics, validator ownership, or setup-side routing delivery.
