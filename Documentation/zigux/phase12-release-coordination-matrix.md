# Phase 12 Release Coordination Matrix

This matrix is the compact PMO coordination companion for the active Phase 12 packet.

It is a release-planning artifact, not a closure claim and not a new replay route.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- shared-summary lane owner: `pmo-release`
- scope: keep the active shared Phase 12 packet reviewable without implying a broader validator-first or deep-core delivery claim
- readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- sequencing companion: `Documentation/zigux/phase12-release-sequencing.md`
- closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
- phase13 handoff companion: `Documentation/zigux/phase12-phase13-release-handoff.md`
- freeze-map companion: `Documentation/zigux/freeze-map.md`
- coverage companion: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- libbpf survey companion: `Documentation/zigux/phase12-libbpf-segment-survey.md`
- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`
- compile-smoke companion: `Documentation/zigux/phase12-cross-compile-smoke.md`
- driver-local NVMe reopen companion: `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`
- build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`
- support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`
- anti-overlap checker: `scripts/zigux/check-phase12-complex-driver-lane-packet.py`
- compile-smoke checker: `scripts/zigux/check-phase12-cross-compile-smoke.py`
- validator-first support bundle: `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, `scripts/zigux/check-phase12-cross-compile-smoke.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-lane-marker.py`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, and the shipped wrapper name `make -C zigux phase12-validate`
- shared replay wiring: `zigux/tests/phase12_build.zig` and `.github/workflows/zigux-bootstrap.yml`; `zigux/Makefile` remains directly readable repo evidence and now exposes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` on `master`

## Owner Split
- PMO / Release Management: keep `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, this matrix, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-phase13-release-handoff.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, and `scripts/zigux/README.md` aligned around the same active-not-closed release posture, the same repo-local `.zig-toolchain` then attached-Zig degraded rerun order, the same returned shared wrapper set, and the same downstream-only handoff into the active Phase 13 shared-helper reminder packet. Current `master` now directly serves the shared validator-side support packet through `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, `scripts/zigux/check-phase12-cross-compile-smoke.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-lane-marker.py`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/README.md`, `zigux/Makefile`, and `zigux/tests/phase12_build.zig`, while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped current-`master` wrapper evidence again. Keep the build-only checker, the release-readiness checker, the complex-driver anti-overlap checker, the compile-smoke checker, the libbpf snapshot checker, the libbpf lane-marker checker, the libbpf heavy-consumer packet checker, and the directly readable validator body explicit as the current PMO truthfulness surfaces.
- Complex-driver packet: keep the current split explicit. The shared `zigux/tests/phase12_build.zig` route is the six-file `virtio_net` packet only: `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig`, backed by `drivers/net/virtio_net_queue_resume.zig`, `drivers/net/virtio_net_receive_refill_replay.zig`, `drivers/net/virtio_net_transmit_recycle.zig`, `drivers/net/virtio_net_post_reset_replay.zig`, and `drivers/net/virtio_net_throughput_parity.zig` for the five driver-side helper surfaces. Keep those shared-route proofs framed as bounded queue-resume, receive-refill replay, transmit-disposition, post-reset replay, throughput-parity, and survey-gate reviewability rather than live DMA-safe receive ownership, queue-restart parity, transport-backed queue flow, interrupt-backed completion handling, or full `net_device` lifecycle parity. Keep the rollback-evidence-only `virtio_scsi` packet explicit through `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/phase12_virtio_scsi_survey_build.zig`, and `scripts/zigux/check-phase12-virtio-scsi-packet.py` while keeping that storage-facing rollback-evidence packet and its dedicated survey-build rerun outside the shared `smoke` and `test` build route. Keep the bounded NVMe foothold explicit through `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `drivers/nvme/host/pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, and `zigux/tests/phase12_nvme_pci_manifest.json` while leaving it outside the shared smoke-and-test route.
- Shared libbpf heavy-consumer packet: keep `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, and `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` aligned around the parked reviewability packet. `tools/lib/bpf/zigux_segments/verify.zig` stays the directly readable helper footing, while the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` remain note-owned boundaries until they land again on current `master`; do not imply a focused libbpf-only shared replay route from this matrix.
- Shared fallback and anti-overlap packet: keep `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-cross-compile-smoke.md`, and `Documentation/zigux/phase12-phase13-release-handoff.md` aligned with the same active smoke-first packet, the same one-catalog plus one-current-master-gap-note companion plus shared-support-bundle fallback split, and the same release-planning-only boundary.

## Fallback Split
- commit-pinned direct replay catalog:
  - `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- driver-local current-master gap inventory companion:
  - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
- shared-tree-only anchors:
  - `Documentation/zigux/phase12-virtio-net-survey.md`
  - `Documentation/zigux/phase12-libbpf-segment-survey.md`
- shared-tree raw-read anchors during degraded contents reads:
  - `zigux/tests/phase12_build.zig`
  - `scripts/zigux/check-build-only-phase12-surface.py`
- current contents-bridge shared support bundle during degraded contents reads:
  - `scripts/zigux/check-build-only-phase12-surface.py`
  - `scripts/zigux/check-phase12-complex-driver-lane-packet.py`
  - `scripts/zigux/check-phase12-cross-compile-smoke.py`
  - `scripts/zigux/check-phase12-libbpf-snapshot.py`
  - `scripts/zigux/check-phase12-libbpf-lane-marker.py`
  - `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`
  - `scripts/zigux/check-phase12-release-readiness-packet.py`
  - `scripts/zigux/validate-phase12.py`
  - `.github/workflows/zigux-bootstrap.yml`
  - `scripts/zigux/README.md`
  - `zigux/Makefile`
- rule: keep this one-catalog plus one-gap-note plus two-anchor split explicit in PMO release wording. Only the `virtio_scsi` catalog is commit-pinned direct replay evidence, and neither the NVMe gap note, the shared-tree anchors, nor the current contents-bridge shared support bundle should be promoted into extra commit-pinned fallback artifacts unless new dedicated files actually land.

## Smoke Set
Current repo-reality override: `zigux/Makefile` now exposes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` on current `master`. The directly readable rerun surfaces in the shared packet are `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py --self-test`, `python3 scripts/zigux/check-phase12-cross-compile-smoke.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-lane-marker.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test`, `scripts/zigux/validate-phase12.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`. Keep the compact PMO order aligned with the rest of the shared Phase 12 packet: `make -C zigux phase12-validate` is shipped wrapper evidence again and remains the validator-first entry in the sequencing contract before the shipped smoke-and-test wrapper reruns.

`.github/workflows/zigux-bootstrap.yml` still runs `zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all` after the shared `phase12-smoke` and `phase12-test` reruns, but that workflow-only throughput-parity anchor remains adjacent bounded `virtio_net` evidence rather than shared PMO route proof.

1. shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`
2. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
3. shipped wrapper evidence on current `master`: `make -C zigux phase12-smoke`
4. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
5. shipped wrapper evidence on current `master`: `make -C zigux phase12-test`
6. shipped wrapper evidence on current `master`: `make -C zigux phase12`

The active shared build packet is the returned six-file `virtio_net` sextet only:
- `zigux/tests/phase12_virtio_net_queue_resume.zig`
- `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`
- `zigux/tests/phase12_virtio_net_transmit_recycle.zig`
- `zigux/tests/phase12_virtio_net_post_reset_replay.zig`
- `zigux/tests/phase12_virtio_net_throughput_parity.zig`
- `zigux/tests/phase12_virtio_net_survey.zig`

That sextet is the current shared `smoke` and `test` route. Keep the directly readable `virtio_scsi` rollback-lab packet and the bounded NVMe foothold explicit as adjacent driver-local evidence rather than shared build outputs.

If `zig` is unavailable on `PATH`, keep the shipped degraded-workflow bundle plus that same validator-first then smoke-first order explicit, first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`, and only if that local fallback is also absent keep `make -C zigux phase12-validate` explicit as shipped current-route proof ahead of the attached-Zig rerun trio `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing a focused libbpf-only replay, a cross-build replay, or another unshipped PMO surface.

## Boundaries
- This matrix tracks only the shipped build-only contract and the active survey-backed packet on `master`.
- `Documentation/zigux/freeze-map.md` remains the boundary owner for deeper queueing and transport anchors, so this matrix must keep that governance note explicit whenever it summarizes the shared Phase 12 release packet.
- Queueing, throughput, rollback, and recovery wording must stay bounded to the driver-local packets and the lab-only reversible-delivery evidence already recorded in the shared Phase 12 docs; this PMO companion must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
- Segmented rollout is the governing rule for the active tranche: only the six-file `virtio_net` sextet may move through the shared wrapper set, while the rollback-lab `virtio_scsi` survey-build packet, the published-but-unwired `nvme_pci` foothold, and the parked libbpf packet stay outside that shared route until new checker-backed promotions land on `master`.
- The shared build-only contract checker `scripts/zigux/check-build-only-phase12-surface.py`, the complex-driver anti-overlap checker `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, and the compile-smoke checker `scripts/zigux/check-phase12-cross-compile-smoke.py` remain explicit beside the validator-first support packet, but current `master` still does not expose a standalone Phase 12 cross-build checker, a standalone Phase 12 cross-build replay, a focused-libbpf-only replay, or another shared cross-target route, so release-planning notes should keep that validator-first support packet distinct from the smoke-first direct replay packet.

## Review Use
- reread this matrix beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-phase13-release-handoff.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-cross-compile-smoke.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/phase12_virtio_scsi_survey_build.zig`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`, `scripts/zigux/README.md`, and `zigux/tests/README.md` whenever the shared Phase 12 packet changes.
- rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening PMO wording.
- treat this file as a compact owner-and-fallback summary, not as a substitute for the driver-local survey notes or the shared build packet.

## Next Bounded Step
If the shared Phase 12 packet moves again, reread this matrix beside the shared release companions, the bounded driver-local notes, the current support checker packet, and `Documentation/zigux/phase12-phase13-release-handoff.md` before widening PMO wording.

If a shared Phase 13 reminder change affects the downstream release boundary without changing fallback-only evidence, reread the same handoff note first and land only the smallest sequencing-side truthfulness repair instead of reopening driver-local or fallback-specific PMO notes.

If only `Documentation/zigux/phase12-raw-github-coverage-survey.md` needs another exact-readback refresh, leave this matrix parked and let the neighboring fallback-overview lane absorb that evidence update first.
