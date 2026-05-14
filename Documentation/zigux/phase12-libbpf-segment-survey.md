# Phase 12 Libbpf Segment Survey

This document records the bounded Phase 12 survey lane around `tools/lib/bpf/libbpf.c` and the earlier `tools/lib/bpf/zigux_segments/` rollout.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_SLICE=libbpf-segment-survey`
- scope: Phase 12 roadmap comparison, shared survey truthfulness, the parked libbpf reviewability companions, and the boundary between the still-present direct helper-first segment footing and the still-unadopted shared replay packet
- product boundary:
  - `Documentation/zigux/phase12-libbpf-segment-survey.md`
  - `Documentation/zigux/phase12-libbpf-verify-shard-note.md`
  - `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
  - `Documentation/zigux/phase12-release-coordination-matrix.md`
  - `scripts/zigux/check-build-only-phase12-surface.py`
  - `zigux/tests/phase12_build.zig`
  - `zigux/Makefile`
- public fallback posture: shared-tree-only anchor; unlike `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, this libbpf note is not a commit-pinned raw GitHub fallback artifact
- rollback owner and reversible-delivery drill: restore the last truthful survey wording in this note, then rerun `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-build-only-phase12-surface.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` so the shared Phase 12 release packet stays reviewable without pretending those shared routes already exercise the parked libbpf reviewability files directly

## Why this slice exists
The roadmap places `tools/lib/bpf/libbpf.c` in Phase 12 alongside the other high-risk production-facing consumers because the file is both large and semantically dense even though it lives under `tools/`.

That matters because current `master` still exposes a bounded direct `zigux_segments` footing through `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `online_cpu_routing.zig`, `perf_buffer_poll.zig`, and the legacy `manifest.json` catalog, while `tools/lib/bpf/zigux_segments/verify.zig`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, and the direct `phase12_libbpf_*` replay files remain parked note-owned boundaries. That mixed state preserves real segmented progress while also keeping the broader reviewability packet smaller than the shipped replay order.

Those are still useful footholds, but the live Phase 12 survey has to explain how that earlier helper work fits the heavy-helper roadmap without overstating the current replay packet. The direct helper-first footing remains roadmap-relevant, while the broader parked libbpf reviewability packet has to stay described through the survey, verify-shard, anti-overlap notes, and snapshot anchor until the shared replay order actually adopts it.

## Survey findings
- `tools/lib/bpf/libbpf.c` is present on `master` at 14,771 lines, which is large enough to cross helper, bridge, queue-routing, object-model, relocation, and verifier-facing concerns in one file.
- current `master` still exposes a bounded direct libbpf segment footing under `tools/lib/bpf/zigux_segments/` through `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `online_cpu_routing.zig`, `perf_buffer_poll.zig`, and the legacy `manifest.json` catalog.
- the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/verify.zig` and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` still stay recorded only through the survey, verify-shard, and anti-overlap notes until they land again on current `master`; the still-present `zigux/tests/fixtures/phase12_libbpf_snapshot.json` anchor keeps that broader parked reviewability packet visible without promoting it into the shared shipped replay order.
- the shared shipped replay order is still narrower than that mixed direct-plus-parked libbpf packet. Current `zigux/tests/phase12_build.zig` wires only the `virtio_net` and `virtio_scsi` Phase 12 shards, and current `zigux/Makefile` keeps `phase12-smoke`, `phase12-test`, and `phase12` tied to that same build file.
- `scripts/zigux/check-build-only-phase12-surface.py` is a shared release-packet checker for the active Phase 12 build-only contract. It exact-checks the current driver-facing release packet and adjacent PMO reminders, but it does not yet mean that the parked libbpf reviewability packet has been adopted into `zigux/tests/phase12_build.zig` or the shipped Make replay order.
- the direct helper-first segmentation is still roadmap-relevant, while the shared Phase 12 smoke-and-test order is still narrower than the combined direct-helper and parked reviewability packet described only through the survey, verify-shard, anti-overlap notes, and snapshot anchor.
- the current lane therefore needs survey truthfulness more than a new helper claim. The real boundary is no longer "libbpf is missing" versus "libbpf is landed"; it is "a bounded direct helper-first segment packet is present on current `master`" versus "the shared shipped replay order has not adopted the absent verify-shard, file-path bridge, and direct `phase12_libbpf_*` replay packet into the active smoke-first route."

## Recorded gap
The highest-value honest gap is the survey boundary itself.

Current `master` still exposes the bounded direct helper subset plus the legacy manifest catalog, and it still has the snapshot anchor plus the paired survey, verify-shard, and anti-overlap notes, but it does not expose `tools/lib/bpf/zigux_segments/verify.zig`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, or the direct `phase12_libbpf_*` replay files, and the shared shipped replay packet still stops at `zigux/tests/phase12_build.zig`, `zigux/Makefile`, and the active driver-facing release order described by the Phase 12 PMO notes.

That means this survey should keep three facts explicit at the same time:
- the bounded direct helper-first libbpf footing remains visible on current `master` and still counts as roadmap-relevant Phase 12 progress
- the broader parked libbpf reviewability packet is still carried through `zigux/tests/fixtures/phase12_libbpf_snapshot.json` plus the survey, verify-shard, and anti-overlap notes because `tools/lib/bpf/zigux_segments/verify.zig`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, and the direct `phase12_libbpf_*` replay files are still absent from current `master`
- the shared Phase 12 smoke and test routes still do not exercise that broader parked packet directly

Keeping those three facts aligned is the bounded roadmap gap for this lane. It prevents Phase 12 libbpf wording from erasing the still-present direct helper segmentation, and it also prevents the release-facing Phase 12 packet from quietly promoting the absent verify-shard and replay set into shipped replay evidence before `zigux/tests/phase12_build.zig` or `zigux/Makefile` actually adopt them.

The same boundary applies to the older `tools/lib/bpf/zigux_segments/manifest.json` story: current Phase 12 wording should keep treating it as a directly checked-out legacy helper catalog and reviewability aid on current `master`, not as proof that the absent verify-shard or file-path bridge surfaces have joined the shared replay order.

## Non-goals
This survey slice does not claim:
- direct Zig parity for `tools/lib/bpf/libbpf.c`
- object-model parity for `bpf_object`, `bpf_map`, or `bpf_program`
- direct procfs reads, bpffs opens, token creation, pinned-object reopen flow, or descriptor ownership side effects
- direct `perf_event_open()` setup, epoll registration, mmap-backed ring ownership, online-CPU routing, or callback delivery
- skeleton population
- ELF collection or object loading
- BTF relocation or load-time verifier interaction
- that the shared Phase 12 smoke-and-test packet already compiles or runs the parked libbpf reviewability files

## Gates
1. rerun the shared build-only Phase 12 surface checker self-test
   - `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
2. rerun the shared build-only Phase 12 surface checker
   - `python3 scripts/zigux/check-build-only-phase12-surface.py`
3. rerun the current shipped smoke-first Phase 12 replay order as shared packet evidence, not as a focused libbpf replay
   - `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
   - `make -C zigux phase12-smoke`
   - `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
   - `make -C zigux phase12`
4. if `zig` is unavailable on `PATH`, keep the same smoke-first order and reuse only the shipped Make routes with `ZIG=<attached-zig-path>`
   - `make -C zigux phase12-smoke ZIG=<attached-zig-path>`
   - `make -C zigux phase12 ZIG=<attached-zig-path>`

## Next bounded step
Keep `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md` aligned around the same direct-helper-versus-parked-reviewability-versus-shipped-replay boundary.

If this lane reopens, prefer the next one-file truthfulness repair that keeps clear that the bounded direct helper-first libbpf footing and the legacy `tools/lib/bpf/zigux_segments/manifest.json` catalog are still present on current `master`, while the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/verify.zig` and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` stay recorded only through the parked reviewability packet until the direct replay set lands again on current `master`.