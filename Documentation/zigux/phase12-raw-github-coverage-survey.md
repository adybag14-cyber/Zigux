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
  * driver-local current-master missing gap-note handle in this runtime:
    * `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
  * shared-tree-only anchors:
    * `Documentation/zigux/phase12-virtio-net-survey.md`
    * `Documentation/zigux/phase12-libbpf-segment-survey.md`
  * current contents-bridge build-only anchor pair during degraded contents reads:
    * `scripts/zigux/check-build-only-phase12-surface.py`
    * `zigux/tests/phase12_build.zig`
  * current contents-bridge shared support bundle during degraded contents reads:
    * `scripts/zigux/validate-phase12.py`
    * `scripts/zigux/check-phase12-release-readiness-packet.py`
    * `.github/workflows/zigux-bootstrap.yml`
    * `scripts/zigux/README.md`
    * `zigux/Makefile`
    * `zigux/tests/phase12_build.zig`
  * rule: keep this one-catalog plus one currently missing NVMe gap-note handle plus two shared-tree-only anchors split explicit, keep both the directly readable build-only anchor pair and the broader shared support bundle visible during degraded contents reads too, and do not promote the missing gap-note handle, the shared-tree anchors, the build-only anchor pair, or the broader shared support bundle into extra commit-pinned fallback artifacts unless dedicated files actually land
## Exact Coverage Evidence
- exact coverage evidence checked on `2026-05-19`: the commit-pinned direct replay catalog is still publicly raw-readable on current `master` as `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- exact coverage evidence checked on `2026-05-19`: direct raw-URL and contents-bridge reads for `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` currently return `404` on current `master` in this runtime
- exact coverage evidence checked on `2026-05-19`: the shared-tree-only anchors are currently present on `master` as `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md`
- exact coverage evidence checked on `2026-05-19`: the current GitHub contents bridge directly reads `scripts/zigux/check-build-only-phase12-surface.py` at blob `59848d1e892f3883c47e0e92ab8f5a4c145b9435`, `scripts/zigux/validate-phase12.py` at blob `c06560034f1b5378a6025daea31cdd08369c8892`, `scripts/zigux/check-phase12-release-readiness-packet.py` at blob `d08925161f02adaeaaa85b7fc2511d653fff52a3`, `.github/workflows/zigux-bootstrap.yml` at blob `8f373d8734694964dd63d754c4889fe82bd558b9`, `scripts/zigux/README.md` at blob `07d955918ed24c81be3c1cb45ad99f1b54e48a54`, `zigux/Makefile` at blob `875044b9debc4bee2831b3d981c99b41b564e0bb`, and `zigux/tests/phase12_build.zig` at blob `db74940c2581c6953948a7b6277af58f10498f72`
- exact runtime-reality evidence checked on `2026-05-19`: keep the directly readable validator, build-only checker, release-readiness checker, workflow, scripts-root README, current Makefile, and current `zigux/tests/phase12_build.zig` as bounded reminder evidence only, not authoritative degraded-read coverage proof for the larger shared packet, while the NVMe gap-note handle is currently missing through both direct read paths in this runtime
- exact runtime-reality evidence checked on `2026-05-19`: the raw-URL-backed direct replay catalog, the currently missing raw NVMe gap-note handle, the contents-bridge-backed build-only anchor pair, and the contents-bridge-backed shared support bundle are distinct evidence states in this runtime, so future fallback wording should reread all four states before widening shared coverage claims
- exact runtime-reality evidence checked on `2026-05-19`: the directly readable `zigux/Makefile` blob `875044b9debc4bee2831b3d981c99b41b564e0bb` now exposes shared `phase12-smoke`, `phase12-test`, and `phase12` again while still omitting `phase12-validate`, so treat the readable Makefile as bounded support evidence for the returned smoke-and-test wrappers rather than as proof that the whole shared packet is directly bridge-readable, and keep the validator-first plus smoke-first Phase 12 route vocabulary anchored to `Documentation/zigux/phase12-release-sequencing.md` and `Documentation/zigux/phase12-release-readiness-survey.md` while `make -C zigux phase12-validate` remains reminder-only text on current `master`
## Review Use
  * reread this note beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` whenever fallback wording changes
  * reread raw GitHub URL readback for `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, confirm whether `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` still returns `404` through both direct contents and raw-URL reads, then compare those results beside contents-bridge reads of `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/README.md`, `zigux/Makefile`, and `zigux/tests/phase12_build.zig` before widening fallback claims; if the NVMe gap-note handle stays missing, keep this note parked as a degraded-reality warning instead of re-promoting the older one-catalog-plus-one-gap-note split
  * keep the current validator-first then smoke-first order explicit through the reminder-only `make -C zigux phase12-validate` vocabulary, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, the shipped wrapper evidence `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, the shipped wrapper evidence `make -C zigux phase12-test`, and the shipped wrapper evidence `make -C zigux phase12`
  * if `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order explicit and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`; if that local fallback is also absent, keep the same reminder-only validator route plus shipped wrapper reruns explicit as `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing a focused libbpf-only route, a cross-build route, or another unshipped fallback route
  * keep the current shared raw-read anchor pair `zigux/tests/phase12_build.zig` plus `scripts/zigux/check-build-only-phase12-surface.py` explicit when GitHub contents reads degrade, but do not treat that directly readable pair as current-master proof for the larger shared packet and do not treat the missing NVMe gap-note handle as if it had already returned through the same read path
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

If the shared Phase 12 support packet is restored, the missing NVMe gap-note handle rematerializes, or the packet is retargeted later, update this note together with `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, the release-order, closure, readiness, coordination, driver anti-overlap, libbpf survey, libbpf anti-overlap, verify-shard, scripts-root, and tests-root companions so the shared Phase 12 packet keeps one truthful public-read story.