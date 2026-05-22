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
  * driver-local current-master gap-note companion:
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
  * rule: keep this one-catalog plus one current-master NVMe gap-note companion plus two shared-tree-only anchors split explicit, keep both the directly readable build-only anchor pair and the broader shared support bundle visible during degraded contents reads too, and do not promote the direct NVMe gap-note companion, the shared-tree anchors, the build-only anchor pair, or the broader shared support bundle into extra commit-pinned fallback artifacts unless dedicated files actually land
## Exact Coverage Evidence
- exact coverage evidence checked on `2026-05-21`: authenticated contents-bridge reads still return the commit-pinned direct replay catalog on current `master` as `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`; browser-side raw GitHub readback for that same `master` path also returns the note, while direct container-side raw-URL fetches in this runtime still fail through the proxy tunnel with HTTP `403`
- exact coverage evidence checked on `2026-05-21`: authenticated contents-bridge reads still return `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` on current `master`; browser-side raw GitHub readback for that same `master` path also returns the note, while direct container-side raw-URL fetches in this runtime still fail through the proxy tunnel with HTTP `403`
- exact coverage evidence checked on `2026-05-21`: the shared-tree-only anchors are currently present on `master` as `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md`, and browser-side raw GitHub readback for both paths also returned their current `master` bodies during this reread
- exact coverage evidence checked on `2026-05-21`: the current GitHub contents bridge directly reads `scripts/zigux/check-build-only-phase12-surface.py` at blob `b34900db85b8872b5981b63839ab35583d340f0a`, `scripts/zigux/validate-phase12.py` at blob `de1e248f6688adf89b9f9edb3abd824ece6ddae5`, `scripts/zigux/check-phase12-release-readiness-packet.py` at blob `9c1c9e99ac368690a5ee9683364f5a21eaead6aa`, `.github/workflows/zigux-bootstrap.yml` at blob `d33dbde416395f8d7cd0e79da73d90b6e5dea3bb`, `scripts/zigux/README.md` at blob `929ebe22494d052da408cf3a5be1de903f18ff24`, `zigux/Makefile` at blob `73e62472ae62a7d3b1e5ec773af5c7b5d35ec0d8`, and `zigux/tests/phase12_build.zig` at blob `c338d24f4d12317c6a58d25708bbc14a5006852c`
- exact runtime-reality evidence checked on `2026-05-21`: keep the directly readable validator, build-only checker, release-readiness checker, workflow, scripts-root README, current Makefile, and current `zigux/tests/phase12_build.zig` as bounded reminder evidence only, and keep the driver-local NVMe gap-note companion bounded to its own packet rather than as authoritative degraded-read coverage proof for the larger shared packet
- exact runtime-reality evidence checked on `2026-05-21`: the commit-pinned `virtio_scsi` fallback catalog, the current-master NVMe gap-note companion, and the two shared-tree anchors still exist on current `master`, and browser-side raw GitHub readback returned all four notes during this reread; in this runtime, however, direct container-side `curl`, `wget`, and `urllib` raw-URL fetches still tunnel-fail with HTTP `403`, so shell-side fallback verification remains split between browser-visible raw-read proof and GitHub contents-bridge reads
- exact runtime-reality evidence checked on `2026-05-21`: the directly readable `zigux/Makefile` blob `73e62472ae62a7d3b1e5ec773af5c7b5d35ec0d8` now exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` again, so treat the readable Makefile as bounded support evidence for the returned validator-first plus smoke-and-test wrappers rather than as proof that the whole shared packet is directly bridge-readable, and keep the validator-first plus smoke-first Phase 12 route vocabulary anchored to `Documentation/zigux/phase12-release-sequencing.md` and `Documentation/zigux/phase12-release-readiness-survey.md` while the shared support bundle remains reminder evidence only on current `master`
- exact runtime-reality evidence checked on `2026-05-21`: `.github/workflows/zigux-bootstrap.yml` now rebuilds the repo-local `.zig-toolchain` fallback by trying the pinned `third_party` archive first, then the Zig community-mirror list, and finally `ziglang.org`, so treat the Makefile fallback as a restorable local-first degraded-workflow path before falling back to attached `ZIG=<attached-zig-path>` reruns
## Review Use
  * reread this note beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` whenever fallback wording changes
  * reread GitHub contents-bridge readback for `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` and `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, and only add same-runtime raw GitHub URL proof if the runtime can actually reach `raw.githubusercontent.com`; then compare those results beside contents-bridge reads of `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/README.md`, `zigux/Makefile`, and `zigux/tests/phase12_build.zig` before widening fallback claims; if the direct NVMe gap-note companion disappears again or raw-URL access stays tunnel-blocked here, keep this note parked as a degraded-reality warning instead of re-promoting the older missing-handle wording
  * keep the current validator-first then smoke-first order explicit through the shipped wrapper evidence `make -C zigux phase12-validate`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, the shipped wrapper evidence `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, the shipped wrapper evidence `make -C zigux phase12-test`, and the shipped wrapper evidence `make -C zigux phase12`
  * if `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order explicit and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`; if that local fallback is also absent, keep the same shipped route explicit as `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing a focused libbpf-only route, a cross-build route, or another unshipped fallback route
  * keep the current shared raw-read anchor pair `zigux/tests/phase12_build.zig` plus `scripts/zigux/check-build-only-phase12-surface.py` explicit when GitHub contents reads degrade, but do not treat that directly readable pair as current-master proof for the larger shared packet and do not treat the direct NVMe gap-note companion as if it had become a second commit-pinned fallback artifact
## Anti-Overlap Notes

  * `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` should be reread beside this shared fallback overview whenever shared Phase 12 libbpf ownership wording changes
  * `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` remains the separate driver-only anti-overlap companion
## Boundaries
  * This note must not imply a focused-libbpf-only replay, a cross-build replay, or another shared replay route that current `master` does not ship.
  * This note must keep the returned `make -C zigux phase12-validate` wrapper evidence explicit beside the bounded degraded-workflow support bundle and distinct from the smoke-first direct replay packet.
  * This note must keep the repo-local `.zig-toolchain` fallback explicit as the first shipped degraded rerun path when `ZIG` is unset, and keep the attached-toolchain override framed as the last-resort rerun of the same shipped Make routes rather than a separate public fallback artifact or replay surface.
  * This note must not imply that the checker's transmit-recycle, queue-resume, repeated-replan, repeated-rollback, or packet-test expectations are already wired into the raw `zigux/tests/phase12_build.zig` anchor on current `master`.
  * This note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
  * Treat this file as a compact fallback reminder only; the concrete survey, slice, manifest, smoke-route, and reviewability details remain in the shipped Phase 12 packet itself.
## Next Bounded Step

If the shared Phase 12 support packet is restored, the direct NVMe gap-note companion regresses out of current `master`, or the packet is retargeted later, update this note together with `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, the release-order, closure, readiness, coordination, driver anti-overlap, libbpf survey, libbpf anti-overlap, verify-shard, scripts-root, and tests-root companions so the shared Phase 12 packet keeps one truthful public-read story.