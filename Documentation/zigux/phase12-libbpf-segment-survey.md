# Phase 12 Libbpf Segment Survey

This document records the bounded Phase 12 survey lane around `tools/lib/bpf/libbpf.c` and the existing `tools/lib/bpf/zigux_segments/` rollout.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_SLICE=libbpf-segment-survey`
- scope: the shared Phase 12 libbpf survey note, the shared release-planning packet, the shipped build-only Phase 12 surface checker, the smoke-first shared replay contract, the PMO closure companion, the compact release-coordination matrix, and the anti-overlap note that compares the current `zigux_segments/` footing against the roadmap's heavy-helper consumer plan
- product boundary:
- `Documentation/zigux/phase12-libbpf-segment-survey.md`
- `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
- `Documentation/zigux/phase12-libbpf-verify-shard-note.md`
- `Documentation/zigux/phase12-release-sequencing.md`
- `Documentation/zigux/phase12-release-closure-checklist.md`
- `Documentation/zigux/phase12-release-coordination-matrix.md`
- `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- `scripts/zigux/check-build-only-phase12-surface.py`
- `zigux/tests/phase12_build.zig`
- `zigux/Makefile`
- public fallback posture: shared-tree-only anchor; unlike `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, this libbpf note is not a commit-pinned raw GitHub fallback artifact.
- rollback owner and reversible-delivery drill: this shared survey packet rolls back by restoring the last truthful libbpf-survey wording in this note and then rerunning `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-build-only-phase12-surface.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` so the shared build-only Phase 12 contract stays reversible without inventing a dedicated libbpf-only replay route that current `master` does not ship.

## Why this slice exists

The roadmap places `tools/lib/bpf/libbpf.c` in Phase 12 alongside the other high-risk production-facing consumers because the file is both large and semantically dense even though it lives under `tools/`.

That matters because the live repo already has real helper-first progress under `tools/lib/bpf/zigux_segments/`: a segment catalog, dense type-name tables, a CPU-mask helper with the deferred chunk-reader path for sysfs-style buffered input, a bounded logging helper, bounded bpffs pin-path helpers, a bounded perf-buffer poll helper for wait-result normalization and ready-buffer bookkeeping, and a shared file-path bridge packet whose landed surface now includes helper-only fdinfo parsing, reused-map compatibility shaping, and token-path readiness planning without crossing into live token opens or reopen side effects.

Those are useful footholds, but they still need a current Phase 12 survey checkpoint that explains how the earlier helper work fits the modern roadmap instead of leaving libbpf stranded in older Phase 8 wording or stale Phase 12 reviewability assumptions.

The honest same-lane step is therefore a survey checkpoint that records the existing segmented footing, keeps the shared smoke-first Phase 12 packet aware of it, keeps the shared-tree fallback split explicit, and preserves the anti-overlap boundary between the landed helper-only bridge work and the heavier deferred bridge, queue-routing, object-loading, relocation, and syscall-backed behavior.

## Survey findings
- `tools/lib/bpf/libbpf.c` is present on `master` at 14,771 lines, which is large enough to cross helper, loader, object-model, relocation, and verifier-facing concerns in one file.
- the live repo already ships the earlier `tools/lib/bpf/zigux_segments/manifest.json` survey plus helper-sized libbpf footholds around `type_names`, `cpu_mask`, `logging`, `pin_path`, `perf_buffer_poll`, and the helper-only file-path bridge packet.
- the earlier Phase 8 tooling lane proved that helper-first segmentation works for libbpf, but the current roadmap places the broader heavy-consumer rollout in Phase 12 because the remaining work depends on object-model discipline, loader boundaries, queue-routing boundaries, and high-risk validation gates.
- the current shared Phase 12 release packet keeps the libbpf footing reviewable through this survey note, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, the shared `scripts/zigux/check-build-only-phase12-surface.py` checker pair, the smoke-first `zigux/tests/phase12_build.zig` plus `make -C zigux phase12` route, and the shared-tree fallback split. That is the shipped replay contract this note is allowed to name on current `master`.
- the dedicated libbpf verify-shard packet still stays parked behind `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, but public-tree readback now shows `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, `zigux/tests/phase12_libbpf_manifest.json`, `tools/lib/bpf/zigux_segments/manifest.json`, and `tools/lib/bpf/zigux_segments/verify.zig` present again on current `master`. This survey still must not present that parked reviewability packet as part of the shipped replay order until the shared checker, `zigux/tests/phase12_build.zig`, and `zigux/Makefile` adopt it explicitly.
- the older segment catalog still leaves three bounded shared-bridge helpers explicitly nearer than the object-model wall: the helper-only fdinfo map-info packet, the map-reuse compatibility packet, and token-path readiness planning inside the shared `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` destination, while direct procfs reads, token opens, bpffs reopens, and fd-ownership semantics remain deferred.
- the repo still has no `skeleton.zig`, no object-loader parity surface, and no relocation-facing Zig slice, and it still intentionally avoids direct ELF collection, `bpf_object` parity, BTF relocation, and load-time verifier interactions.
- the current risk split is therefore explicit again: the landed helper-only bridge foundations stay smaller than the missing object-model wall, the heavier shared file-path-and-handle bridge and perf-buffer online-CPU routing stay deferred as their own bridge and queue-routing buckets, `skeleton.zig` remains the nearest post-helper cluster once those smaller bridge decisions are exhausted, loader and program-load work stay blocked behind that boundary, and the verifier-facing relocation cluster stays deferred as its own later risk bucket.
- with the bounded helper-first utility slices now landed, the next honest libbpf-facing step is to keep review wording aligned with the shared smoke-first packet, preserve the landed helper-only bridge packet plus the deferred bridge and queue-routing buckets, and avoid collapsing those smaller boundaries into later skeleton, loader, or relocation risks unless fresh repo reality changes the actual segment boundaries.

## Recorded gaps

This survey now records:
- the landed shared `phase12-build-gate` and `phase12-make-target` posture through `zigux/tests/phase12_build.zig`, `zigux/Makefile`, and `scripts/zigux/check-build-only-phase12-surface.py`
- the landed `phase12-libbpf-survey-note` and the shared-tree fallback posture for the libbpf packet
- the landed helper-first libbpf foundations around type-name lookup, CPU-mask parsing, logging helpers, pin-path validation, perf-buffer poll bookkeeping, and the helper-only file-path bridge packet
- the still-deferred `phase12-libbpf-file-path-and-handle-bridge-boundary`
- the still-deferred `phase12-libbpf-perf-buffer-online-cpu-routing-boundary`
- the still-blocked `phase12-libbpf-skeleton-population`
- the still-blocked `phase12-libbpf-object-and-elf-loader`
- the still-deferred `phase12-libbpf-btf-relocation-and-program-load`
- the parked verify-shard and reviewability packet described in `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, which is publicly visible again on current `master` but remains outside the shipped replay order until the shared checker and smoke-first replay packet adopt it explicitly

This keeps the lane explicit without overstating progress: Zigux already has real libbpf helper footholds, including the deferred CPU-mask reader path plus bounded logging, pin-path validation, perf-buffer poll bookkeeping, and helper-only token-path readiness planning, and it now keeps the landed helper-only bridge foundations explicit before the heavier file-path bridge, queue-routing, skeleton, loader, and verifier-facing relocation buckets instead of pretending the object-model wall is the only remaining split that matters.

## Non-goals

This survey slice does not claim:
- direct Zig parity for `tools/lib/bpf/libbpf.c`
- object-model parity for `bpf_object`, `bpf_map`, or `bpf_program`
- a live dedicated libbpf verify-shard replay on current `master`
- ELF collection or object loading
- BTF relocation recording
- load-time verifier interactions
- syscall-backed libbpf runtime behavior

## Gates
1. run the shared build-only Phase 12 surface checker self-test
- `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
2. run the shared build-only Phase 12 surface checker
- `python3 scripts/zigux/check-build-only-phase12-surface.py`
3. run the focused smoke preflight direct build route
- `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
4. run the focused smoke preflight Makefile route
- `make -C zigux phase12-smoke`
5. run the shared Phase 12 build replay
- `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
6. run the Linux-style entrypoint last
- `make -C zigux phase12`
7. If `zig` is unavailable on `PATH`, keep the same smoke-first order and rerun the shipped Make routes with `ZIG=<attached-zig-path>` instead of inventing a new libbpf-specific or Phase 12 entrypoint.
- `make -C zigux phase12-smoke ZIG=<attached-zig-path>`
- `make -C zigux phase12 ZIG=<attached-zig-path>`
- This is an environment override for the existing replay packet, not a validator-first, libbpf-only, or `phase12-validate` route.

Use `Documentation/zigux/phase12-release-closure-checklist.md` as the PMO companion when judging whether this shared-tree libbpf survey packet is close enough to describe the active Phase 12 tranche as release-closed.
Keep `Documentation/zigux/phase12-release-coordination-matrix.md` visible beside that same PMO closure companion when judging whether the compact lane-owner split, fallback split, smoke-first replay order, and parked verify-shard boundary still match this shared-tree libbpf packet.

## Next bounded step
Keep the Phase 12 libbpf survey, the verify-shard companion, the PMO closure companion, the compact release-coordination matrix, the shared build-only replay contract, and the reviewability wording aligned with the live helper set, the smoke-first shared replay order, the landed helper-only bridge packet plus the deferred bridge and queue-routing buckets, and the later skeleton-loader-relocation split, and only reopen `tools/lib/bpf/zigux_segments/` for another bounded utility slice if fresh repo reality shows something materially smaller than those already-recorded boundaries.