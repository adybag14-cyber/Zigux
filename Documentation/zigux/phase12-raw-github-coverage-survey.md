# Phase 12 Raw GitHub Coverage Survey

This note records the public-read fallback split for the active Phase 12 release packet.

It is a compact fallback overview, not a new replay surface and not a commit-pinned artifact itself.
## Status
  * `PHASE12_STATUS=active`
  * scope: keep the mixed public fallback story explicit across the shipped Phase 12 driver and libbpf packet without promoting shared-tree anchors into dedicated fallback artifacts
  * release-order companion: `Documentation/zigux/phase12-release-sequencing.md`
  * closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
  * readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
  * coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
  * libbpf survey companion: `Documentation/zigux/phase12-libbpf-segment-survey.md`
  * verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`
## Fallback Split
  * commit-pinned direct replay catalog:
    * `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
  * driver-local current-master gap-inventory companion:
    * `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
  * shared-tree-only anchors:
    * `Documentation/zigux/phase12-virtio-net-survey.md`
    * `Documentation/zigux/phase12-libbpf-segment-survey.md`
  * shared raw-read anchors during degraded contents reads:
    * `scripts/zigux/check-build-only-phase12-surface.py`
    * `zigux/tests/phase12_build.zig`
  * rule: keep this one-catalog plus one-gap-note plus two-anchor split explicit in shared PMO wording, keep the shared raw-read anchors visible during degraded contents reads too, and do not promote the gap note, shared-tree anchors, or shared raw-read anchors into extra commit-pinned fallback artifacts unless dedicated files actually land
## Exact Coverage Evidence
  * exact coverage evidence checked on `2026-05-16`: the commit-pinned direct replay catalog is currently present on `master` as `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
  * exact coverage evidence checked on `2026-05-16`: the current-master NVMe gap-inventory companion is currently present on `master` as `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
  * exact coverage evidence checked on `2026-05-16`: the shared-tree-only anchors are currently present on `master` as `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md`
  * exact coverage evidence checked on `2026-05-16`: the shared raw-read anchors remain `python3 scripts/zigux/check-build-only-phase12-surface.py` plus `zigux/tests/phase12_build.zig`, whose raw GitHub fallback read still exposes the shipped `smoke` and `test` steps even when a degraded contents read for that path no longer gives the normal file body
  * exact runtime-reality evidence checked on `2026-05-16`: current `master` ships `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `zigux/Makefile`; the bounded degraded-workflow support route is now shipped as `make -C zigux phase12-validate`, and the shared Make routing should first rely on the repo-local `.zig-toolchain` fallback when `ZIG` is unset before escalating to the attached `ZIG=<attached-zig-path>` override
## Review Use
  * reread this note beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` whenever fallback wording changes
  * rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening fallback claims or release wording
  * keep the current validator-first then smoke-first order explicit through `make -C zigux phase12-validate`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12`
  * if `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order explicit and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`; if that local fallback is also absent, rerun only the shipped Make routes with `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing a focused libbpf-only route, a cross-build route, or another unshipped fallback route
  * keep `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py` explicit as shared-tree raw-read anchors when GitHub contents reads degrade; they stay part of the shipped validator-first support bundle plus smoke-first packet and are not extra commit-pinned fallback artifacts
## Anti-Overlap Notes

  * `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` should be reread beside this shared fallback overview whenever shared Phase 12 libbpf ownership wording changes
  * `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` remains the separate driver-only anti-overlap companion
## Boundaries
  * This note must not imply a focused-libbpf-only replay, a cross-build replay, or another shared replay route that current `master` does not ship.
  * This note must keep `phase12-validate` explicit as the bounded degraded-workflow support bundle and distinct from the smoke-first direct replay packet.
  * This note must keep the repo-local `.zig-toolchain` fallback explicit as the first shipped degraded rerun path when `ZIG` is unset, and keep the attached-toolchain override framed as the last-resort rerun of the same shipped Make routes rather than a separate public fallback artifact or replay surface.
  * This note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
  * Treat this file as a compact fallback reminder only; the concrete survey, slice, manifest, smoke-route, and reviewability details remain in the shipped Phase 12 packet itself.
## Next Bounded Step

If the fallback split changes later, update this note together with `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, the release-order, closure, readiness, coordination, driver anti-overlap, libbpf survey, libbpf anti-overlap, verify-shard, scripts-root, and tests-root companions so the shared Phase 12 packet keeps one truthful public-read story.
