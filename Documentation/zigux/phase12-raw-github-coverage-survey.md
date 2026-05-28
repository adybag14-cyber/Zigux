# Phase 12 Raw GitHub Coverage Survey

This note records the public-read fallback split for the active Phase 12 release packet.

It is a compact fallback overview, not a new replay surface and not a commit-pinned artifact itself.

## Status

- `PHASE12_STATUS=active`
- roadmap scope: keep the public-read story aligned with the roadmap-backed Phase 12 targets `drivers/net/virtio_net.c`, `drivers/scsi/virtio_scsi.c`, `drivers/nvme/host/pci.c`, and `tools/lib/bpf/libbpf.c`
- release-order companion: `Documentation/zigux/phase12-release-sequencing.md`
- closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
- readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
- complex-driver anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- shared libbpf anti-overlap companion: `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
- libbpf survey companion: `Documentation/zigux/phase12-libbpf-segment-survey.md`
- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`

## Fallback Split

- commit-pinned direct replay catalog:
  - `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- driver-local current-master gap inventory companion:
  - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
- shared-tree-only anchors:
  - `Documentation/zigux/phase12-virtio-net-survey.md`
  - `Documentation/zigux/phase12-libbpf-segment-survey.md`
- shared anti-overlap companions:
  - `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
  - `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
- current contents-bridge build-only anchor pair during degraded contents reads:
  - `scripts/zigux/check-build-only-phase12-surface.py`
  - `zigux/tests/phase12_build.zig`
- current contents-bridge shared support bundle during degraded contents reads:
    * `scripts/zigux/check-phase12-complex-driver-lane-packet.py`
    * `scripts/zigux/check-phase12-cross-compile-smoke.py`
    * `scripts/zigux/check-phase12-libbpf-snapshot.py`
    * `scripts/zigux/check-phase12-libbpf-lane-marker.py`
    * `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`
    * `scripts/zigux/check-phase12-release-readiness-packet.py`
    * `scripts/zigux/validate-phase12.py`
    * `.github/workflows/zigux-bootstrap.yml`
    * `scripts/zigux/README.md`
    * `zigux/Makefile`
- rule: keep this one-catalog plus one-gap-note plus two-anchor split explicit in PMO release wording. Only the `virtio_scsi` catalog is commit-pinned direct replay evidence, and neither the NVMe gap note, the shared-tree anchors, nor the current contents-bridge shared support bundle should be promoted into extra commit-pinned fallback artifacts unless new dedicated files actually land.

## Exact Coverage Evidence

- exact coverage evidence checked on `2026-05-28`: the current GitHub contents bridge directly reads `Documentation/zigux/phase12-virtio-net-survey.md` `4897c1eaf95abe08bcfccc7d7e5231ef974f7dc9`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` `769b69b910c031c9d4037e61642b8185faad6e59`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` `e24ff02b887278a38992da1bf63a5d9b4983fbef`, and `Documentation/zigux/phase12-libbpf-segment-survey.md` on current `master`.
- exact coverage evidence checked on `2026-05-28`: the current GitHub contents bridge directly reads `scripts/zigux/check-build-only-phase12-surface.py` `5d4a081067b5abf4f9a313ddc7bbcc18c1505f67`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py` `7befbdae2cf416715a502ca41c90db304354e251`, `scripts/zigux/check-phase12-cross-compile-smoke.py` `2278a40d4afaa7c155b6da4ece1b9892a9a8d771`, `scripts/zigux/check-phase12-libbpf-lane-marker.py` `7be88fe75bda8cc9d71eba627cb3309d8d6a0ccf`, `scripts/zigux/check-phase12-release-readiness-packet.py` `bc3d72db9e449f84478ebb027a2281e2dfea9576`, `scripts/zigux/validate-phase12.py` `c342f3db6da8bd9a5d2113f6c456121f8687dcab`, `scripts/zigux/README.md` `449f24c2477c2174b4e13a33b4af4f90595423fb`, `.github/workflows/zigux-bootstrap.yml` `5bdb136b8b6710c08c19566879d5a9da42b63445`, `zigux/Makefile` `09f92bc2f9903fc4fd58d6335e93da13e7f0793b`, and `zigux/tests/phase12_build.zig` `eacfc63df9670ba22fd1f88e4ee33212d1818e29` on current `master`.
- exact coverage evidence checked on `2026-05-28`: the current GitHub contents bridge also directly reads `drivers/net/virtio_net_queue_resume.zig` `b5848b0f7a8d00e0856ea2b846e3085137c5b2fb` and `zigux/tests/phase12_virtio_net_survey.zig` `af1625180cb63fac5df719e4eb89f610b1965a25` on current `master`, which keeps the shared `virtio_net` packet inspectable through the shared-tree anchor without requiring a separate driver-local fallback map.
- exact coverage evidence checked on `2026-05-28`: the raw-URL-backed direct replay catalog, the current-master NVMe gap-note companion, the contents-bridge-backed build-only anchor pair, and the contents-bridge-backed shared support bundle are distinct evidence states in this runtime.
- exact runtime-reality evidence checked on `2026-05-28`: direct container-side `curl`, `wget`, and `git clone https://github.com/adybag14-cyber/Zigux.git` still fail in this runtime through the proxy tunnel with HTTP `403`, so same-runtime exact verification still depends on GitHub contents readback rather than a trustworthy current-head local checkout.
- exact runtime-reality evidence checked on `2026-05-28`: `zigux/Makefile` now exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` again, so treat the readable Makefile as bounded support evidence for the returned validator-first plus smoke-and-test wrappers rather than as proof that the whole shared packet is directly bridge-readable.
- exact runtime-reality evidence checked on `2026-05-28`: `.github/workflows/zigux-bootstrap.yml` now rebuilds the repo-local `.zig-toolchain` fallback by trying the pinned `third_party` archive first, then the Zig community-mirror list, and finally `ziglang.org`, so treat the Makefile fallback as a restorable local-first degraded-workflow path before falling back to attached `ZIG=<attached-zig-path>` reruns.

## Review Use

- reread this note beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` whenever fallback wording changes.
- reread GitHub contents-bridge readback for `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` and `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, and only add same-runtime raw GitHub URL proof if the runtime can actually reach `raw.githubusercontent.com`.
- compare those doc-side results beside contents-bridge reads of `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, `scripts/zigux/check-phase12-cross-compile-smoke.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-lane-marker.py`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/README.md`, `zigux/Makefile`, and `zigux/tests/phase12_build.zig` before widening fallback claims.
- keep the current validator-first then smoke-first order explicit through the shipped wrapper evidence `make -C zigux phase12-validate`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-test`, and `make -C zigux phase12`.
- if `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order explicit and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`; if that local fallback is also absent, keep the same shipped route explicit as `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing a focused libbpf-only route, a cross-build route, or another unshipped fallback route.
- keep the current shared raw-read anchor pair `zigux/tests/phase12_build.zig` plus `scripts/zigux/check-build-only-phase12-surface.py` explicit when GitHub contents reads degrade, but do not treat that directly readable pair as current-master proof for the larger shared packet.

## Anti-Overlap Notes

- `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` should be reread beside this shared fallback overview whenever shared Phase 12 libbpf ownership wording changes.
- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` remains the separate driver-only anti-overlap companion.

## Boundaries

- This note must not imply a focused-libbpf-only replay, a cross-build replay, or another shared replay route that current `master` does not ship.
- This note must keep the returned `make -C zigux phase12-validate` wrapper evidence explicit beside the bounded degraded-workflow support bundle and distinct from the smoke-first direct replay packet.
- This note must keep the repo-local `.zig-toolchain` fallback explicit as the first shipped degraded rerun path when `ZIG` is unset, and keep the attached-toolchain override framed as the last-resort rerun of the same shipped Make routes rather than a separate public fallback artifact or replay surface.
- This note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
- Treat this file as a compact fallback reminder only; the concrete survey, slice, manifest, smoke-route, and reviewability details remain in the shipped Phase 12 packet itself.

## Next Bounded Step

If the shared Phase 12 support packet is retargeted later, the `nvme_pci` current-master packet companion regresses out of current `master`, or raw-URL access becomes directly reachable from the container, update this note together with `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, the release-order, closure, readiness, coordination, driver anti-overlap, libbpf survey, libbpf anti-overlap, verify-shard, scripts-root, and tests-root companions so the shared Phase 12 packet keeps one truthful public-read story.