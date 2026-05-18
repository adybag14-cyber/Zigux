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
  * intended shared raw-read anchors during degraded contents reads:
    * `scripts/zigux/check-build-only-phase12-surface.py`
    * `zigux/tests/phase12_build.zig`
  * rule: keep this one-catalog plus one-gap-note plus two-anchor split explicit in shared PMO wording, keep the intended shared raw-read anchors visible during degraded contents reads too, and do not promote the gap note, shared-tree anchors, or shared raw-read anchors into extra commit-pinned fallback artifacts unless dedicated files actually land
## Exact Coverage Evidence
- exact coverage evidence checked on `2026-05-18`: the commit-pinned direct replay catalog is still publicly raw-readable on current `master` as `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- exact coverage evidence checked on `2026-05-18`: the current-master NVMe gap-inventory companion is still publicly raw-readable on current `master` as `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
- exact coverage evidence checked on `2026-05-18`: the shared-tree-only anchors are currently present on `master` as `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md`
- exact coverage evidence checked on `2026-05-18`: the current GitHub contents bridge directly reads `scripts/zigux/check-build-only-phase12-surface.py` at blob `f63930f3b44c6654ecb48cc3a93a9d4fabd129f1`, `scripts/zigux/check-phase12-release-readiness-packet.py` at blob `13bf09d84b6946486cabcd7ad99b9733ea439be8`, `.github/workflows/zigux-bootstrap.yml` at blob `046f5ea160e61c260109a521de2b66786c46bc24`, `scripts/zigux/README.md` at blob `9d40d4157e5ff67bccb543969671a14ead437571`, and `zigux/Makefile` at blob `c2f5485e4391c3cb4471d8223210be5407b63147`, while a direct contents read for `zigux/tests/phase12_build.zig` still returns `404` through the same current `master` bridge
- exact runtime-reality evidence checked on `2026-05-18`: keep the publicly raw-readable direct replay catalog and driver-local gap companion explicit as dedicated fallback artifacts, and keep the directly readable build-only checker, release-readiness checker, workflow, scripts-root README, and current Makefile as bounded reminder evidence only, not authoritative degraded-read coverage proof, while a direct contents read for `zigux/tests/phase12_build.zig` still returns `404` through the live bridge
- exact runtime-reality evidence checked on `2026-05-18`: the raw-URL-backed fallback pair and the contents-bridge-backed shared support bundle are distinct evidence paths in this runtime, so future fallback wording should reread both paths before widening shared coverage claims
- exact runtime-reality evidence checked on `2026-05-18`: the directly readable `zigux/Makefile` blob `c2f5485e4391c3cb4471d8223210be5407b63147` now exposes shared `phase12-smoke`, `phase12-test`, and `phase12` again while still omitting `phase12-validate`, so treat the readable Makefile as bounded support evidence for the returned smoke-and-test wrappers rather than as proof that the whole shared packet is directly bridge-readable, and keep the validator-first plus smoke-first Phase 12 route vocabulary anchored to `Documentation/zigux/phase12-release-sequencing.md` and `Documentation/zigux/phase12-release-readiness-survey.md` while `make -C zigux phase12-validate` remains reminder-only text on current `master`
## Review Use
  * reread this note beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` whenever fallback wording changes
  * reread raw GitHub URL readback for `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` and `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` beside contents-bridge reads of `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/README.md`, and `zigux/Makefile`, then compare those results against a direct contents read of `zigux/tests/phase12_build.zig` before widening fallback claims; if that build-file direct read still fails, keep this note parked as a degraded-reality warning instead of as coverage proof for the larger shared packet
  * keep the current validator-first then smoke-first order explicit through the reminder-only `make -C zigux phase12-validate` vocabulary, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, the shipped wrapper evidence `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, the shipped wrapper evidence `make -C zigux phase12-test`, and the shipped wrapper evidence `make -C zigux phase12`
  * if `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order explicit and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`; if that local fallback is also absent, keep the same reminder-only validator route plus shipped wrapper reruns explicit as `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing a focused libbpf-only route, a cross-build route, or another unshipped fallback route
  * keep the intended shared raw-read anchor pair `zigux/tests/phase12_build.zig` plus `scripts/zigux/check-build-only-phase12-surface.py` explicit when GitHub contents reads degrade, but do not treat that pair as current-master proof while the direct contents read for `zigux/tests/phase12_build.zig` still fails through the live bridge
## Anti-Overlap Notes

  * `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` should be reread beside this shared fallback overview whenever shared Phase 12 libbpf ownership wording changes
  * `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` remains the separate driver-only anti-overlap companion
## Boundaries
  * This note must not imply a focused-libbpf-only replay, a cross-build replay, or another shared replay route that current `master` does not ship.
  * This note must keep `phase12-validate` explicit as the bounded degraded-workflow support bundle and distinct from the smoke-first direct replay packet.
  * This note must keep the repo-local `.zig-toolchain` fallback explicit as the first shipped degraded rerun path when `ZIG` is unset, and keep the attached-toolchain override framed as the last-resort rerun of the same shipped Make routes rather than a separate public fallback artifact or replay surface.
  * This note must not imply that the checker's transmit-recycle, queue-resume, repeated-replan, repeated-rollback, or packet-test expectations are already wired into the raw `zigux/tests/phase12_build.zig` anchor on current `master`.
  * This note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
  * Treat this file as a compact fallback reminder only; the concrete survey, slice, manifest, smoke-route, and reviewability details remain in the shipped Phase 12 packet itself.
## Next Bounded Step

If the shared Phase 12 support packet is restored or retargeted later, update this note together with `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, the release-order, closure, readiness, coordination, driver anti-overlap, libbpf survey, libbpf anti-overlap, verify-shard, scripts-root, and tests-root companions so the shared Phase 12 packet keeps one truthful public-read story.