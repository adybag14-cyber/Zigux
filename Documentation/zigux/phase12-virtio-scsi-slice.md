# Phase 12 virtio_scsi Slice
- `PHASE12_SLICE=virtio-scsi-queue-lab-support`
- reread against live `master` and the current `P12-L13` survey packet on `2026-05-17`
- lane: `complex-drivers-infra`
- anchor: `drivers/scsi/virtio_scsi.c`

## Shipped packet
- `drivers/scsi/virtio_scsi.zig` is the current complex-driver scaffold on `master`
- `zigux/tests/phase12_virtio_scsi.zig` keeps queue layout, request-queue selection, probe snapshot, host-limit, queue-depth, request-submit sequencing, completion-handback sequencing, command-buffer ownership, io-map, and transport-reset recovery summaries explicit
- `zigux/tests/phase12_virtio_scsi_syntax_lab.zig` keeps the current export surface reachable
- `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig` keeps the second-cycle recovery boundary explicit
- `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig` keeps the second-cycle rollback contract and post-restore readiness explicit
- `zigux/tests/phase12_virtio_scsi_packet.zig` remains the manifest-backed support replay for this bounded infra-prep slice
- `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json` pins the lane key, surveyed commit, shipped paths, and direct validation commands for the current support packet
- `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` now keep the newer roadmap-gap survey machine-checkable beside the earlier support packet
- `zigux/tests/phase12_build.zig` keeps the direct replay, syntax-lab smoke, repeated-replan gate, repeated-rollback gate, survey gate, and support packet wired into the shared `phase12` smoke and test routes
- `scripts/zigux/check-phase12-virtio-scsi-packet.py` fails closed if the manifest, slice note, or build route drifts

## Repo-reality boundaries
- `drivers/nvme/host/pci.zig` now lives in the separate Phase 12 NVMe packet on current `master`, so this `virtio_scsi` support note should treat NVMe as neighboring packet evidence rather than a repo-reality gap
- `Documentation/zigux/phase12-closure.md` is still absent on the surveyed head

## Why this packet exists
- The roadmap's complex-driver lane wants infrastructure prep, not another helper family
- `master` already has a real `virtio_scsi` scaffold plus a newer bounded survey packet, so the highest-value same-lane move here is to keep the older support note aligned with that shipped review surface instead of pretending the packet stopped at queue-layout-only evidence
- the manifest-backed support replay, the newer survey gate and survey note, the repeated-rollback gate, and the shared Phase 12 build wiring keep this slice reviewable without claiming broader Phase 12 closure, `scsi_host` registration, or live DMA-backed request flow
- This note intentionally stays scoped to the current `virtio_scsi` support packet and does not claim broader Phase 12 closure