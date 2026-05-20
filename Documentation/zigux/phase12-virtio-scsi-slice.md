# Phase 12 virtio_scsi Slice
- `PHASE12_SLICE=virtio-scsi-queue-lab-support`
- reread against live `master` and the current `P12-L13` survey packet on `2026-05-19`
- lane: `complex-drivers-infra`
- anchor: `drivers/scsi/virtio_scsi.c`

## Shipped packet
- `drivers/scsi/virtio_scsi.zig` is the current complex-driver scaffold on `master`
- `zigux/tests/phase12_virtio_scsi.zig` keeps queue layout, request-queue selection, probe snapshot, host-limit, queue-depth, request-submit sequencing, completion-handback sequencing, command-buffer ownership, io-map, and transport-reset recovery summaries explicit
- `zigux/tests/phase12_virtio_scsi_syntax_lab.zig` keeps the current export surface reachable
- `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig` keeps the second-cycle recovery boundary explicit
- `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig` keeps the second-cycle rollback contract and post-restore readiness explicit
- `zigux/tests/phase12_virtio_scsi_manifest.json` keeps the lane key, surveyed commit, shipped paths, and direct validation commands machine-checkable for the current survey packet
- `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` keep the newer roadmap-gap survey machine-checkable beside the direct replay and rollback gates
- `zigux/tests/phase12_build.zig` now acts as a shared Phase 12 support-bundle surface only: current `master` wires the `virtio_net` queue-resume, transmit-recycle, post-reset replay, and throughput-parity tests through the shared `smoke` and `test` steps, while the `virtio_scsi` direct replay, syntax-lab, repeated-replan gate, repeated-rollback gate, and survey gate remain lane-local validation surfaces
- `scripts/zigux/check-phase12-virtio-scsi-packet.py` fails closed if the survey manifest, survey note, slice note, or support-bundle reminder drifts

## Repo-reality boundaries
- `drivers/nvme/host/pci.zig` now lives in the separate Phase 12 NVMe packet on current `master`, so this `virtio_scsi` support note should treat NVMe as neighboring packet evidence rather than a repo-reality gap
- `Documentation/zigux/phase12-closure.md` is still absent on the surveyed head

## Why this packet exists
- The roadmap's complex-driver lane wants infrastructure prep, not another helper family
- `master` already has a real `virtio_scsi` scaffold plus a newer bounded survey packet, so the highest-value same-lane move here is to keep this note aligned with the shipped direct replay, rollback gates, and survey surfaces instead of pretending a removed support replay still anchors the packet
- the direct replay, the newer survey gate and survey note, the repeated-rollback gate, and the shared Phase 12 support-bundle surfaces keep this slice reviewable without claiming broader Phase 12 closure, `scsi_host` registration, or live DMA-backed request flow
- This note intentionally stays scoped to the current `virtio_scsi` survey packet and does not claim broader Phase 12 closure
