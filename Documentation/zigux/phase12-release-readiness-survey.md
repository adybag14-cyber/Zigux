# Phase 12 Release Readiness Survey

This document records the current release-discipline reading for the active bounded Phase 12 complex-driver tranche without claiming that the roadmap phase is globally closed.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_TRANCHE=driver-and-libbpf-survey-bundle`
- direct smoke preflight entrypoint: `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
- focused smoke preflight entrypoint: `make -C zigux phase12-smoke`
- shared build replay entrypoint: `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
- Linux-style replay entrypoint: `make -C zigux phase12`
- freeze-boundary authority: `Documentation/zigux/freeze-map.md`
- product boundary: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/README.md`, `zigux/tests/phase12_build.zig`, the committed Phase 12 manifests under `zigux/tests/`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`, `zigux/tests/phase12_libbpf_snapshot_determinism.zig`, `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/verify.zig`, `zigux/Makefile`, and the bounded `Documentation/zigux/phase12-virtio-scsi-slice.md` rollback-drill wording

## Current release reading
The current shared Phase 12 packet on `master` is smoke-first plus shared build replay.

If the local runtime does not provide `zig` on `PATH`, keep that same smoke-first release packet and rerun only the shipped Make routes as `make -C zigux phase12-smoke ZIG=<attached-zig-path>` and `make -C zigux phase12 ZIG=<attached-zig-path>`.

Keep the same degraded-workflow validation pair explicit too: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test` and `python3 scripts/zigux/check-build-only-phase12-surface.py` should run before or beside those attached-toolchain Make reruns so build-only contract drift still fails closed when the local runtime needs the fallback path.

This is an environment override for the existing replay packet, not a validator-first or `phase12-validate` route.

It stays explicit through the PMO closure companion `Documentation/zigux/phase12-release-closure-checklist.md`, the compact release-coordination matrix `Documentation/zigux/phase12-release-coordination-matrix.md`, the driver-only anti-overlap companion `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, the shared libbpf anti-overlap companion `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, the mixed raw-fallback overview note `Documentation/zigux/phase12-raw-github-coverage-survey.md`, the workflow-backed build-only contract `scripts/zigux/check-build-only-phase12-surface.py` plus `.github/workflows/zigux-bootstrap.yml`, the dedicated libbpf verify shard `tools/lib/bpf/zigux_segments/verify.zig`, the deterministic tracked-helper snapshot fixture `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, the deterministic snapshot-digest evidence fixture `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`, the dedicated snapshot-determinism replay `zigux/tests/phase12_libbpf_snapshot_determinism.zig`, and the bounded `virtio_net`, `nvme_pci`, `virtio_scsi`, and libbpf survey packet.

The canonical replay path for that deterministic snapshot check is `zigux/tests/phase12_libbpf_snapshot_determinism.zig`; shared PMO release surfaces must not drift it into `zigux/tests/fixtures/`, because only the JSON snapshot and JSON digest evidence live under the fixtures tree.

There is no shipped shared `scripts/zigux/validate-phase12.py`, no dedicated `check-phase12-*.py` release packet, and no `make -C zigux phase12-validate` target on `master`, so this release-facing note should not imply validator-first, dedicated PMO checker, focused libbpf-only replay, raw-coverage checker, or cross-build routes as part of the active shared release path.

The public fallback split must stay explicit: `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are the only commit-pinned fallback artifacts, while `virtio_net` and `libbpf` remain shared-tree-only anchors.

The bounded `virtio_scsi` rollback drill remains storage-lane-local release evidence, not a tranche-wide recovery claim.

That bounded storage packet now covers repeated transport-reset generation plus restore queue rebind, request-queue restart, event rearm, event-buffer ownership, and rollback summaries as lab-only reversible-delivery scaffolding, not as closure-ready runtime recovery.

The landed `virtio_net` segmented-rollout boundary remains lane-local review evidence, not DMA-safe transport readiness, runtime recovery proof, or live runtime-data-path progress.

Queueing, throughput, rollback, and recovery wording in this release-facing note must stay below active delivery claims against frozen `net/core/skbuff.c` and below boundary-study-only `kernel/workqueue.c` plus `kernel/trace/ring_buffer.c` until a broader Phase 12 packet actually lands.

## Next bounded step
Leave this note parked unless the shared Phase 12 packet drifts again.

The older docs-root and deterministic-replay follow-through is already closed on current `master`: `Documentation/zigux/README.md` now keeps `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, and the canonical `zigux/tests/phase12_libbpf_snapshot_determinism.zig` replay path explicit beside the same shared Phase 12 packet.

The scripts-root undercount is now closed too: `scripts/zigux/README.md` now keeps `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` explicit beside the same shared packet, and `scripts/zigux/check-build-only-phase12-surface.py` now fails closed on that exact scripts-root marker so the shared release packet cannot silently drift back to a one-artifact reminder.

The next bounded same-lane follow-through is shared-surface drift control only: reread `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` together for the next smallest PMO-only wording gap before widening into any driver, DMA, queueing, throughput, recovery, object-model, loader, or relocation work.

That reread should keep the smoke-first order, the same canonical `zigux/tests/phase12_libbpf_snapshot_determinism.zig` replay path plus its fixtures-only JSON split, the two-artifact-plus-two-anchor fallback posture, the compact release-coordination matrix, the driver-only anti-overlap boundary, the shared libbpf anti-overlap boundary, and the freeze-boundary reminder aligned across `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, and `scripts/zigux/check-build-only-phase12-surface.py`.
