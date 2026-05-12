# Phase 12 Libbpf Segment Survey

This document records the bounded Phase 12 survey lane around `tools/lib/bpf/libbpf.c` and the existing `tools/lib/bpf/zigux_segments/` rollout.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_SLICE=libbpf-segment-survey`
- scope: Phase 12 roadmap comparison, shared survey truthfulness, the publicly present libbpf reviewability companions, and the boundary between the landed helper-first segment footing and the still-unadopted shared replay packet
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

That matters because current `master` already has real helper-first progress under `tools/lib/bpf/zigux_segments/`: a segment catalog, dense type-name tables, a CPU-mask helper with the deferred chunk-reader path for sysfs-style buffered input, a bounded logging helper, bounded bpffs pin-path helpers, a bounded perf-buffer poll helper for wait-result normalization and ready-buffer bookkeeping, a shared file-path bridge packet that now carries helper-only fdinfo parsing, reused-map compatibility shaping, and token-path readiness planning, and a dedicated `verify.zig` shard that keeps those landed helper surfaces compile-reachable together.

Those are useful footholds, but the live Phase 12 survey has to explain how they fit the heavy-helper roadmap without overstating the current replay packet. The helper footing is real, while the shared Phase 12 smoke-and-test order is still narrower than the parked libbpf reviewability packet described beside it.

## Survey findings
- `tools/lib/bpf/libbpf.c` is present on `master` at 14,771 lines, which is large enough to cross helper, bridge, queue-routing, object-model, relocation, and verifier-facing concerns in one file.
- the live repo still carries the older Phase 8 rooted segment catalog at `tools/lib/bpf/zigux_segments/manifest.json`, and that file remains useful as legacy helper-first scaffolding beside the landed helper-first surfaces in `type_names.zig`, `cpu_mask.zig`, `logging.zig`, `pin_path.zig`, `perf_buffer_poll.zig`, `file_path_handle_bridge.zig`, and the earlier `verify.zig` compile-reachability shard described by the parked Phase 12 notes.
- the dedicated Phase 12 libbpf reviewability companions are still recorded by `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, but current repo-first reads in this runtime only re-confirm the shared notes and parked boundaries. The snapshot-recorded `zigux/tests/phase12_libbpf_manifest.json`, `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, and `tools/lib/bpf/zigux_segments/verify.zig` therefore need to stay described as parked note-owned evidence until they land again on current `master`, not as directly re-readable replay files on head.
- the shared shipped replay order is still narrower than that parked reviewability packet. Current `zigux/tests/phase12_build.zig` wires only the `virtio_net` and `virtio_scsi` Phase 12 shards, and current `zigux/Makefile` keeps `phase12-smoke`, `phase12-test`, and `phase12` tied to that same build file.
- `scripts/zigux/check-build-only-phase12-surface.py` is a shared release-packet checker for the active Phase 12 build-only contract. It exact-checks the current driver-facing release packet and adjacent PMO reminders, but it does not yet mean that the parked libbpf reviewability packet has been adopted into `zigux/tests/phase12_build.zig` or the shipped Make replay order.
- the landed helper footing is still the honest roadmap-aligned progress here: helper-first segmentation already proved useful for libbpf, while the heavier file-path-and-handle bridge, perf-buffer online-CPU routing, skeleton population, object loading, and verifier-facing relocation buckets still stay deferred or blocked as their own later risks.
- the current lane therefore needs survey truthfulness more than a new helper claim. The real boundary is no longer "libbpf is missing" versus "libbpf is landed"; it is "helper-first segment footing is real and the parked reviewability packet is still note-owned evidence" versus "the shared shipped replay order has not adopted that parked packet and current repo-first reads do not re-confirm those direct replay files on head."

## Recorded gap
The highest-value honest gap is the survey boundary itself.

Current `master` still has the helper-first segment footing, and it still has note-owned evidence for the parked Phase 12 reviewability packet through the tracked snapshot and the paired anti-overlap notes, but the shared shipped replay packet still stops at `zigux/tests/phase12_build.zig`, `zigux/Makefile`, and the active driver-facing release order described by the Phase 12 PMO notes.

That means this survey should keep three facts explicit at the same time:
- the helper-first libbpf footing is real and roadmap-relevant Phase 12 progress
- the parked reviewability packet is still recorded through the tracked snapshot plus the paired survey, verify-shard, and anti-overlap notes
- the shared Phase 12 smoke and test routes still do not exercise that parked packet directly

Keeping those three facts aligned is the bounded roadmap gap for this lane. It prevents Phase 12 libbpf wording from collapsing back into stale Phase 8 framing, and it also prevents the release-facing Phase 12 packet from quietly promoting the parked libbpf reviewability files into either directly present head-state evidence or shipped replay evidence before `zigux/tests/phase12_build.zig` or `zigux/Makefile` actually adopt them.

The same boundary applies to `tools/lib/bpf/zigux_segments/manifest.json`: current repo reality still treats that file as a legacy Phase 8 rooted helper catalog, so Phase 12 wording should keep naming it as scaffolding beside the parked reviewability packet instead of treating it like a current Phase 12 lane-keyed reviewability artifact.

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
Keep `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md` aligned around the same parked-versus-shipped boundary.

If this lane reopens, prefer the next one-file truthfulness repair that keeps the helper-first libbpf footing explicit without implying that `zigux/tests/phase12_libbpf_manifest.json`, `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, or `tools/lib/bpf/zigux_segments/verify.zig` are already both re-readable on current `master` and adopted into the shared `zigux/tests/phase12_build.zig` or `zigux/Makefile` replay packet.