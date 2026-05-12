# Phase 12 virtio_scsi Slice

- `PHASE12_SLICE=virtio-scsi-queue-lab-support`
- reviewed against live `master` `4b5b0667d4651364ccd4b388d84c3107b64fdd6a`
- lane: `complex-drivers-infra`
- anchor: `drivers/scsi/virtio_scsi.c`

## Shipped packet

- `drivers/scsi/virtio_scsi.zig` is the current complex-driver scaffold on `master`
- `zigux/tests/phase12_virtio_scsi.zig` keeps the queue planner, host-limit, queue-depth, and recovery summaries explicit
- `zigux/tests/phase12_virtio_scsi_syntax_lab.zig` keeps the current export surface reachable
- `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig` keeps the second-cycle recovery boundary explicit
- `zigux/tests/phase12_virtio_scsi_packet.zig` is the manifest-backed packet replay for this bounded infra-prep slice
- `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json` pins the lane key, surveyed commit, shipped paths, and direct validation commands for the current support packet
- `zigux/tests/phase12_build.zig` keeps the packet replay wired into the shared `phase12` smoke and test routes beside the syntax-lab and repeated-replan gates
- `scripts/zigux/check-phase12-virtio-scsi-packet.py` fails closed if the manifest, slice note, or build route drifts

## Repo-reality gaps

- `drivers/net/virtio_net.zig` is still absent on the surveyed head
- `drivers/nvme/host/pci.zig` is still absent on the surveyed head
- `Documentation/zigux/phase12-closure.md` is still absent on the surveyed head

## Why this packet exists

- The roadmap's complex-driver lane wants infrastructure prep, not another helper family
- `master` already has a real `virtio_scsi` scaffold and direct tests, so the highest-value bounded step here is to make that packet easier to audit and keep aligned
- the manifest-backed replay, shared Phase 12 build wiring, and packet checker keep this support slice reviewable without claiming broader Phase 12 closure or live DMA-backed request flow
- This note intentionally stays scoped to the current `virtio_scsi` support packet and does not claim broader Phase 12 closure
