# Phase 12 Libbpf Segment Survey

This document records the bounded Phase 12 survey lane around `tools/lib/bpf/libbpf.c` and the existing `tools/lib/bpf/zigux_segments/` rollout.

## Status
- `PHASE12_STATUS=parked`
- `PHASE12_SLICE=libbpf-segment-survey`
- scope: Phase 12 survey manifest, dedicated survey gate, shared build wiring, the shipped build-only Phase 12 surface checker, the PMO closure companion that now travels with the active release-order packet, and a lane note that compares the current `zigux_segments/` footing against the roadmap's heavy-helper consumer plan
- product boundary:
  - `scripts/zigux/check-build-only-phase12-surface.py`
  - `zigux/tests/phase12_libbpf_manifest.json`
  - `zigux/tests/phase12_libbpf_segments.zig`
  - `zigux/tests/phase12_libbpf_reviewability.zig`
  - `zigux/tests/phase12_build.zig`
  - `zigux/Makefile`
  - `Documentation/zigux/phase12-libbpf-segment-survey.md`
- public fallback posture: shared-tree-only anchor; unlike `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, this libbpf note is not a commit-pinned raw GitHub fallback artifact.
- rollback owner and reversible-delivery drill: this shared survey packet rolls back by restoring the last truthful libbpf-survey wording in this note and then rerunning `python3 scripts/zigux/check-build-only-phase12-surface.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` so the shared build-only Phase 12 contract stays reversible without inventing a dedicated libbpf-only replay route that current `master` does not ship.

## Why this slice exists
The roadmap now places `tools/lib/bpf/libbpf.c` in Phase 12, alongside the other high-risk production-facing consumers, because the file is both large and semantically dense even though it lives under `tools/`.

That matters because the live repo already has real helper-first progress under `tools/lib/bpf/zigux_segments/`: a segment catalog, dense type-name tables, a CPU-mask helper with the deferred chunk-reader path for sysfs-style buffered input, a bounded logging helper, bounded bpffs pin-path helpers, and a bounded perf-buffer poll helper for wait-result normalization and ready-buffer bookkeeping.

Those are useful footholds, but they still need a current Phase 12 survey checkpoint that explains how the earlier helper work fits the modern roadmap instead of leaving libbpf stranded in older Phase 8 wording or stale Phase 12 reviewability assumptions.

The highest-value honest step in this lane is therefore a survey checkpoint that records the existing segmented footing, keeps the shared Phase 12 build-and-make packet aware of it, verifies that the landed helper files still match the segment plan, and keeps the next helper-sized shared-bridge work separate from the heavier deferred bridge, queue-routing, object-loading, relocation, and syscall-backed behavior.

## Survey findings
- `tools/lib/bpf/libbpf.c` is present on `master` at 14,771 lines, which is large enough to cross helper, loader, object-model, relocation, and verifier-facing concerns in one file.
- the live repo already ships the earlier `tools/lib/bpf/zigux_segments/manifest.json` survey plus five landed helper slices:
  - `type_names.zig` for exported attach, link, map, and program type string tables
  - `cpu_mask.zig` for bounded CPU-mask parsing, set-bit counting, and a deferred reader interface that still stops short of direct file I/O
  - `logging.zig` for bounded print-level parsing, version reporting, and libbpf-specific error text formatting
  - `pin_path.zig` for bounded bpffs path joining, pin-name and root-path validation, and dot-sanitization without directory or syscall parity
  - `perf_buffer_poll.zig` for bounded wait-result normalization, ready-buffer bookkeeping, and per-buffer slot access that still stops short of epoll wiring, mmap-backed ring ownership, online-CPU routing, or callback delivery
- the earlier Phase 8 tooling lane proved that helper-first segmentation works for libbpf, but the current roadmap places the broader heavy-consumer rollout in Phase 12 because the remaining work depends on object-model discipline, loader boundaries, and high-risk validation gates.
- the current Phase 12 build-only packet now re-checks the landed helper-first foundations directly through `zigux/tests/phase12_libbpf_reviewability.zig`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, the shared `zigux/tests/phase12_build.zig` route, `make -C zigux phase12`, and `scripts/zigux/check-build-only-phase12-surface.py`, which together keep the manifest-backed helper set reviewable, cross-check the older `tools/lib/bpf/zigux_segments/manifest.json` catalog so the modern survey lane does not drift away from the original helper segmentation, and avoid implying a dedicated libbpf-only replay, packet checker, or shared validator route that current `master` does not ship.
- the reversible-delivery posture for this note is now the same as the rest of the shared Phase 12 packet: keep the shared-tree fallback explicit, rerun the build-only checker, the smoke-first preflight pair, and the shared build and make route after note edits, and only widen beyond survey truthfulness if live repo evidence lands a new shipped replay surface first.
- use `Documentation/zigux/phase12-release-closure-checklist.md` as the PMO companion when judging whether this shared-tree libbpf survey packet is close enough to describe the active Phase 12 tranche as release-closed, so the heavy-helper consumer note stays aligned with the same release-order packet that already governs the active driver-facing surveys and fallback notes.
- the older segment catalog still leaves two bounded shared-bridge helpers explicitly nearer than the object-model wall: fdinfo map-info parsing and map-reuse compatibility stay `ready_next` once Zigux chooses to materialize the existing `file_path_handle_bridge.zig` surface, while the heavier shared file-path-and-handle bridge remains its own deferred bucket.
- the repo still has no `skeleton.zig`, `object_loader.zig`, or relocation-facing Zig slice, and it still intentionally avoids direct ELF collection, `bpf_object` parity, BTF relocation, and load-time verifier interactions.
- the current risk split is now explicit again: the ready-next shared-bridge helpers stay smaller than the missing object-model wall, the heavier shared file-path-and-handle bridge and perf-buffer online-CPU routing stay deferred as their own bridge and queue-routing buckets, `skeleton.zig` remains the nearest post-helper cluster once those smaller bridge decisions are exhausted, loader and program-load work stay blocked behind that boundary, and the verifier-facing relocation cluster stays deferred as its own later risk bucket.
- with the bounded helper-first utility slices now landed, the next honest libbpf-facing step is to keep reviewability aligned, preserve the ready-next shared-bridge pair plus the deferred bridge and queue-routing buckets, and avoid collapsing those smaller boundaries into the later skeleton, loader, or relocation risks unless fresh repo reality changes the actual segment boundaries.

## Recorded gaps
The survey manifest now records:
- the landed `phase12-build-gate`
- the landed `phase12-make-target`
- the landed `phase12-libbpf-segment-manifest-foundation`
- the landed `phase12-libbpf-type-name-helper-foundation`
- the landed `phase12-libbpf-cpu-mask-helper-foundation`
- the landed `phase12-libbpf-perf-buffer-poll-helper-foundation`
- the landed `phase12-libbpf-logging-helper-foundation`
- the landed `phase12-libbpf-pin-path-helper-foundation`
- the ready-next `phase12-libbpf-fdinfo-map-info-helper-ready-next`
- the ready-next `phase12-libbpf-map-reuse-compatibility-ready-next`
- the landed `phase12-libbpf-survey-gate`
- the landed `phase12-libbpf-reviewability-gate`
- the landed `phase12-libbpf-survey-note`
- the still-deferred `phase12-libbpf-file-path-and-handle-bridge`
- the still-deferred `phase12-libbpf-perf-buffer-online-cpu-routing`
- the still-blocked `phase12-libbpf-skeleton-population`
- the still-blocked `phase12-libbpf-object-loader-and-program-load`
- the still-deferred `phase12-libbpf-btf-relocation-and-program-load`

This keeps the lane explicit without overstating progress: Zigux already has real libbpf helper footholds, including the deferred CPU-mask reader path plus bounded logging, pin-path validation, and perf-buffer poll bookkeeping helpers, and it now keeps the two smaller shared-bridge follow-ups visible before the heavier file-path bridge, queue-routing, skeleton, loader, and verifier-facing relocation buckets instead of pretending the object-model wall is the only remaining split that matters.

## Non-goals
This survey slice does not claim:
- direct Zig parity for `tools/lib/bpf/libbpf.c`
- object-model parity for `bpf_object`, `bpf_map`, or `bpf_program`
- ELF collection or object loading
- BTF relocation recording
- load-time verifier interactions
- syscall-backed libbpf runtime behavior

## Gates
1. run the shared build-only Phase 12 surface checker
- `python3 scripts/zigux/check-build-only-phase12-surface.py`
2. run the focused smoke preflight direct build route
- `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
3. run the focused smoke preflight Makefile route
- `make -C zigux phase12-smoke`
4. run the shared Phase 12 build replay
- `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
5. run the Linux-style entrypoint last
- `make -C zigux phase12`

Use `Documentation/zigux/phase12-release-closure-checklist.md` as the PMO companion when judging whether this shared-tree libbpf survey packet is close enough to describe the active Phase 12 tranche as release-closed.

## Next bounded step
Keep the Phase 12 libbpf survey, the PMO closure companion, the shared build-only replay contract, and the reviewability lane aligned with the live helper set, the smoke-first shared replay order, the ready-next shared-bridge pair, the deferred bridge and queue-routing buckets, and the later skeleton-loader-relocation split, and only reopen `tools/lib/bpf/zigux_segments/` for another bounded utility slice if fresh repo reality shows something materially smaller than those already-recorded boundaries.
