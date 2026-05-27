# Phase 8 Userspace-Kernel Bridge Boundary Survey

This note records the current bounded Phase 8 userspace-adjacent bridge boundary against the roadmap's `tools/lib/bpf/libbpf.c` anchor.

## Status
- `PHASE8_STATUS=parked`
- `PHASE8_SURVEY=userspace-kernel-bridge-boundary-readback`
- survey checkpoint: refreshed against inspected current `master` readback on 2026-05-26
- roadmap anchor: `tools/lib/bpf/libbpf.c`
- intended Zigux destination family: `tools/lib/bpf/zigux_segments/`
- scope: helper-local bridge reviewability and deferred interrupt-routing boundary truthfulness only

## Why this survey exists
Phase 8 only makes roadmap-aligned progress here if Zigux keeps the helper-first bridge packet explicit without pretending that the broader userspace-to-kernel bridge, object reopen flow, or interrupt-routing setup already landed.

That means the note has to keep the landed helper-local bridge packet, the helper-local online-CPU routing evidence, and the still-deferred setup-side routing boundary explicit at the same time.

The separate Phase 8 command-side anchors under `tools/lib/subcmd/` and `tools/lib/symbol/` keep their own parked packets. This survey stays limited to the libbpf-side syscall, descriptor, and routing boundary from `tools/lib/bpf/libbpf.c`.

## Current mixed-source bridge packet
Current `master` still keeps the mixed-source bridge packet reviewable, and authenticated contents readback now reaches the bridge-side helper and witness files directly again in this runtime.

Exact authenticated contents readback now serves this survey note, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, and `zigux/tests/phase8_file_path_handle_bridge.zig` directly, while the focused bridge build and broader replay companions remain reminder evidence through `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_file_path_handle_boundary_guard.zig`, `zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`, `zigux/tests/phase8_build.zig`, `scripts/zigux/check-phase8-libbpf-shard-routes.py`, `scripts/zigux/validate-phase8.py`, `zigux/Makefile`, `make -C zigux phase8-file-path-handle-bridge-test`, and `make -C zigux phase8`.

That narrower split is therefore packet role rather than fetchability: the bridge helper and witness stay on the boundary side of the Phase 8 packet so this survey does not overclaim delivered procfs, bpffs, token, or fd-ownership behavior.

That packet stays smaller than live procfs reads, live bpffs opens, token materialization, `bpf_obj_get()` reopen flow, descriptor replacement, or broader fd ownership behavior.

Within that bounded packet, current `master` keeps `validateProcFdinfoRoot()`, `buildProcFdinfoPath()`, `buildCurrentProcessFdinfoPath()`, `parseFdinfoLine()`, `applyFdinfoMapInfoLine()`, `parseFdinfoMapInfo()`, `summarizeFdinfoMapInfo()`, `mapReuseObservationFromFdinfo()`, `summarizeMapReuseCompatibility()`, `isMapReuseCompatible()`, `summarizeReusedMapName()`, `resolveReusedMapName()`, `resolveReusePinnedMapAttempt()`, and `planTokenPreparation()` explicit as side-effect-free bridge-adjacent helpers. They keep pathname shaping, fdinfo map-info parsing, helper-only reuse observation, compatibility summaries, retained-name summaries, planning-only reopen-attempt gating, and planning-only token-preparation gating reviewable without claiming direct procfs reads, bpffs opens, token materialization, or descriptor ownership behavior.

The planning-only bridge surface now also keeps the bounded reopen-intent and token-open-intent packet explicit: `resolveReusePinnedMapAttempt()` records when the helper-only packet is ready for a reopen attempt without performing one, and `planTokenPreparation()` records when the same bounded packet is ready for a token-open attempt without materializing a token.

The landed `fdinfo-path-and-reuse-name-footholds` slice therefore now mirrors the manifest rationale exactly: This materializes the shared bridge destination with side-effect-free pathname shaping and bounded reused-map name retention while keeping procfs reads, full fdinfo map-info parsing, and reuse comparison logic deferred.

The neighboring `fdinfo-map-info-helpers` slice now stays explicit as landed helper-only bridge proof rather than queued groundwork: current helper source already keeps proc-fdinfo pathname shaping, fdinfo line splitting, numeric map-info decoding, and compact completion summaries reviewable without crossing into direct procfs reads, descriptor ownership, or pinned-object reopen flow.

The sibling `map-reuse-compatibility` slice likewise now stays explicit as landed helper-only bridge proof rather than queued groundwork: current helper source already keeps reuse observations, compatibility summaries, and helper-only comparison behavior reviewable without widening into FD duplication, close-on-replacement, or pinned-map reopen side effects.

## Helper-local online-CPU routing evidence
Current `master` also keeps bounded helper-local online-CPU routing evidence explicit through `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge_verify.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig`, `zigux/tests/phase8_verify_routing_gap.zig`, and `zigux/tests/phase8_verify_routing_gap_only_build.zig`.

That helper-local routing packet keeps `advanceOnlineCpuCursor()`, `summarizeNextOnlineCpuRoute()`, and `summarizeOnlineCpuRouting()` explicit as reviewable route-summary helpers below the riskier setup-side bridge, and the shared `scripts/zigux/check-phase8-libbpf-shard-routes.py` guard keeps that route-side reminder packet tied back to the broader stable-output libbpf survey.

The paired mask-bridge helper now keeps `summarizeOnlineCpuRoutingFromString()` and `summarizeOnlineCpuRoutingFromReader()` explicit as cpumask-backed routing summaries, so the bridge packet records both direct mask-to-routing summaries and the narrower per-attempt route wrappers without claiming that the surrounding perf-event setup path is already ported.

It records route selection, missing buffer-slot detection, missing buffer-fd detection, requested-subset summaries, and no-online-CPU summaries without claiming that the surrounding perf-event setup path is already ported.

The dedicated verifier shards and focused verify-routing witness now also keep string-backed and reader-backed mask-to-routing summaries, typed CPU-index wrappers, errno-shaped CPU-index wrappers, typed buffer-fd wrappers, errno-shaped buffer-fd wrappers, and the hand-built CPU-index overflow fail-closed output explicit without promoting the surrounding perf-event setup path into landed routing delivery.

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
Keep this bridge-boundary survey parked unless a future reread finds drift between this note, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `tools/lib/bpf/zigux_segments/manifest.json`, `scripts/zigux/check-phase8-libbpf-shard-routes.py`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_verify_routing_gap.zig`, or `zigux/tests/phase8_verify_routing_gap_only_build.zig` around the mixed-source bridge packet, the three landed helper-only bridge slices, or the deferred setup-side routing boundary.

If it reopens, reread those nine surfaces together first and keep the next repair note-local or checker-local rather than widening into helper semantics, validator ownership, or setup-side routing delivery.
