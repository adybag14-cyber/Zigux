# Phase 12 Complex-Driver Lane Sequencing

This note is the anti-overlap companion for the shared Phase 12 complex-driver packet.

It keeps the starter-present network and storage packet reviewable without turning the shared release reminders into claims of deeper queueing, throughput, or transport parity.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_LANE=complex-driver-shared-release-packet`
- scope: shared release-planning truthfulness, build-only contract reminders, and anti-overlap guidance for the starter-present `virtio_net` packet, the bounded `virtio_scsi` rollback-lab packet, and the published-but-still-unwired NVMe foothold
- release-order companion: `Documentation/zigux/phase12-release-sequencing.md`
- closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
- readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
- shared fallback overview: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- shared libbpf anti-overlap companion: `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
- driver-local NVMe reopen companion: `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`
- build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`

## Lane Scope

- Treat the current `virtio_net` family as a starter-present direct-replay packet
- `drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, and `zigux/tests/phase12_virtio_net_syntax_lab.zig` are now present on `master`
- Keep the shared validator-first then smoke-first order fixed unless a new shipped route lands first:
  1. `make -C zigux phase12-validate`
  2. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
  3. `make -C zigux phase12-smoke`
  4. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
  5. `make -C zigux phase12`
- Keep the degraded-workflow support bundle explicit beside that same order too:
  - `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
  - `python3 scripts/zigux/check-phase12-cross.py --self-test`
  - `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`
  - `make -C zigux phase12-validate`

## Anti-Overlap Rules

- starter-present `virtio_net` syntax-lab and direct contract packet
- `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig` packet.
- the driver-local `virtio_scsi` rollback-lab companions
- Keep the bounded NVMe packet explicit through `drivers/nvme/host/pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_nvme_pci.zig`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `zigux/tests/phase12_nvme_pci_survey.zig`, and `zigux/tests/phase12_nvme_pci_manifest.json` while leaving it outside the shared smoke-first route.
- Leave the parked libbpf packet, its survey, and its verify-shard boundary to `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` and `Documentation/zigux/phase12-libbpf-verify-shard-note.md` rather than reopening helper-local or loader-facing claims here.
- Keep the shared fallback split explicit: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` remains the one commit-pinned direct replay artifact, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` remains the current-master gap-inventory companion, and `Documentation/zigux/phase12-virtio-net-survey.md` plus `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors.

## Boundaries

- stops undercounting the newly landed `virtio_net` starter
- This note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
- This note must keep the shared release wording bounded to the starter-present `virtio_net` packet, the driver-local `virtio_scsi` rollback-lab packet, the published-but-still-unwired NVMe foothold, and the shipped validator-first support bundle.
- This note must not recast the parked libbpf packet as direct shared replay or as a second active complex-driver lane.

## Next Bounded Step

If the shared Phase 12 packet moves again, reread this note beside `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `scripts/zigux/check-build-only-phase12-surface.py`, and `zigux/tests/README.md` before widening any driver-local claims.
