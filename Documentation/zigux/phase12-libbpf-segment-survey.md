# Phase 12 Libbpf Segment Survey

This document records the bounded Phase 12 survey lane around `tools/lib/bpf/libbpf.c` and the earlier `tools/lib/bpf/zigux_segments/` rollout.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_SLICE=libbpf-segment-survey`
- scope: Phase 12 roadmap comparison, shared survey truthfulness, the parked libbpf reviewability companions, and the boundary between the earlier helper-first segment footing and the still-unadopted shared replay packet
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

That matters because current `master` no longer exposes the earlier helper-first `zigux_segments` footing as direct checked-out helper files, but it still keeps that footing reviewable through the survey, verify-shard, and anti-overlap notes together with the parked `zigux/tests/fixtures/phase12_libbpf_snapshot.json` anchor. That snapshot-backed packet preserves the earlier segmented story around dense type-name tables, CPU-mask parsing, bounded logging, bounded bpffs pin-path helpers, perf-buffer poll bookkeeping, and the later helper-only bridge direction without promoting those files into the shipped replay order.

Those are still useful footholds, but the live Phase 12 survey has to explain how that earlier helper work fits the heavy-helper roadmap without overstating the current replay packet. The helper footing remains roadmap-relevant, while the parked libbpf reviewability packet has to stay described through the survey, verify-shard, anti-overlap notes, and snapshot anchor until the shared replay order actually adopts it.

## Survey findings
- `tools/lib/bpf/libbpf.c` is present on `master` at 14,771 lines, which is large enough to cross helper, bridge, queue-routing, object-model, relocation, and verifier-facing concerns in one file.
- current `master` keeps the earlier helper-first libbpf footing only as a parked snapshot-backed reviewability packet around `tools/lib/bpf/zigux_segments/`, not as direct checked-out helper files or direct `phase12_libbpf_*` replay surfaces.
- the direct `phase12_libbpf_*` replay files and `tools/lib/bpf/zigux_segments/verify.zig` stay recorded only through the survey, verify-shard, and anti-overlap notes until they land again on current `master`; the still-present `zigux/tests/fixtures/phase12_libbpf_snapshot.json` anchor keeps that parked reviewability packet visible without promoting it into the shared shipped replay order.
- the shared shipped replay order is still narrower than that parked reviewability packet. Current `zigux/tests/phase12_build.zig` wires only the `virtio_net` and `virtio_scsi` Phase 12 shards, and current `zigux/Makefile` keeps `phase12-smoke`, `phase12-test`, and `phase12` tied to that same build file.
- `scripts/zigux/check-build-only-phase12-surface.py` is a shared release-packet checker for the active Phase 12 build-only contract. It exact-checks the current driver-facing release packet and adjacent PMO reminders, but it does not yet mean that the parked libbpf reviewability packet has been adopted into `zigux/tests/phase12_build.zig` or the shipped Make replay order.
- the earlier helper segmentation is still roadmap-relevant, while the shared Phase 12 smoke-and-test order is still narrower than the parked libbpf reviewability packet described only through the survey, verify-shard, anti-overlap notes, and snapshot anchor.
- the current lane therefore needs survey truthfulness more than a new helper claim. The real boundary is no longer "libbpf is missing" versus "libbpf is landed"; it is "earlier helper-first segmentation remains reviewable through the parked snapshot-backed packet" versus "the shared shipped replay order has not adopted that parked libbpf reviewability packet into the active smoke-first route."

## Recorded gap
The highest-value honest gap is the survey boundary itself.

Current `master` still has the snapshot anchor plus the paired survey, verify-shard, and anti-overlap notes, but it no longer exposes the earlier helper-first segment footing as direct checked-out `zigux_segments` helper files, and the shared shipped replay packet still stops at `zigux/tests/phase12_build.zig`, `zigux/Makefile`, and the active driver-facing release order described by the Phase 12 PMO notes.

That means this survey should keep three facts explicit at the same time:
- the earlier helper-first libbpf footing remains roadmap-relevant Phase 12 progress, but it is currently reviewable only through the parked snapshot-backed packet rather than through direct current-`master` helper files
- the parked libbpf reviewability packet is still carried through `zigux/tests/fixtures/phase12_libbpf_snapshot.json` plus the survey, verify-shard, and anti-overlap notes instead of through the shipped `phase12_build.zig` replay order
- the shared Phase 12 smoke and test routes still do not exercise that parked packet directly

Keeping those three facts aligned is the bounded roadmap gap for this lane. It prevents Phase 12 libbpf wording from collapsing back into stale Phase 8 framing, and it also prevents the release-facing Phase 12 packet from quietly promoting the parked libbpf reviewability story into shipped replay evidence before `zigux/tests/phase12_build.zig` or `zigux/Makefile` actually adopt it.

The same boundary applies to the older `tools/lib/bpf/zigux_segments/manifest.json` story: current Phase 12 wording should keep treating it as a parked snapshot-backed legacy helper scaffold inside the reviewability packet instead of as a current shared replay artifact or direct shipped helper path.

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
Keep `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md` aligned around the same parked snapshot-backed versus shipped replay boundary.

If this lane reopens, prefer the next one-file truthfulness repair that keeps clear that the earlier helper-first libbpf footing is now carried through the survey, verify-shard, anti-overlap notes, and snapshot anchor, while the direct `phase12_libbpf_*` replay files, `tools/lib/bpf/zigux_segments/verify.zig`, and the older `tools/lib/bpf/zigux_segments/manifest.json` story stay recorded only through that parked packet until the direct replay set lands again on current `master`.