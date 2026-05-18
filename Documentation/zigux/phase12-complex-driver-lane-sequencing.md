# Phase 12 Complex-Driver Lane Sequencing

This note is the anti-overlap companion for the shared Phase 12 complex-driver packet.

It keeps the starter-present network packet and the storage-facing reminder surfaces reviewable without turning the shared release reminders into claims of deeper queueing, throughput, or transport parity.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_LANE=complex-driver-shared-release-packet`
- scope: shared release-planning truthfulness, build-only contract reminders, and anti-overlap guidance for the starter-present `virtio_net` packet, its bounded `virtio_net_transmit_recycle` and `virtio_net_queue_resume` reviewability follow-ups, the directly readable but still lane-split `virtio_scsi` rollback-lab survey packet, and the published-but-still-unwired NVMe foothold
- release-order companion: `Documentation/zigux/phase12-release-sequencing.md`
- closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
- readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
- shared fallback overview: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- shared libbpf anti-overlap companion: `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
- driver-local NVMe reopen companion: `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`
- build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`
- readiness-note support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`

## Lane Scope

- Treat the current `virtio_net` family as a starter-present direct-replay packet
- `drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, and `zigux/tests/phase12_virtio_net_syntax_lab.zig` are now present on `master`
- `drivers/net/virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `drivers/net/virtio_net_queue_resume.zig`, and `zigux/tests/phase12_virtio_net_queue_resume.zig` are now present on `master` as bounded transmit-disposition and queue-resume reviewability follow-ups inside that same shared packet
- Keep the shared validator-first then smoke-first packet wording explicit, but current `zigux/Makefile` no longer ships `phase12-validate`, `phase12-smoke`, or `phase12`, so those route names are stale reminder vocabulary rather than current wrapper proof until same-lane work rematerializes them.
- The directly readable rerun and support surfaces in this lane are `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `scripts/zigux/validate-phase12.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, while the older `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, and `make -C zigux phase12` names stay documented only as shared reminder text until the wrapper layer returns on current `master`.
- Keep the current partial direct-read bridge explicit too: `Documentation/zigux/phase12-raw-github-coverage-survey.md` now records that `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/README.md`, and `zigux/Makefile` are directly readable on current `master`, while `zigux/tests/phase12_build.zig` still fails through the same bridge, and the readable Makefile still stops short of the `phase12-*` wrappers, so that checker-plus-workflow-plus-scripts-plus-Makefile set stays reminder evidence only rather than proof for the larger shared packet.

## Anti-Overlap Rules

- starter-present `virtio_net` syntax-lab and direct contract packet, plus the bounded `virtio_net_transmit_recycle` and `virtio_net_queue_resume` reviewability follow-ups
- keep those two `virtio_net` follow-ups framed as bounded transmit-disposition and queue-resume reviewability inside the shared packet rather than as live DMA-safe receive ownership, queue restart parity, transport-backed queue flow, or completion-path parity
- current `master` now directly rematerializes the bounded `virtio_scsi` rollback-lab packet through `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig`
- keep those `virtio_scsi` files framed as one directly readable bounded driver-local packet, but leave exact survey-packet lane-key and verified-on realignment to the packet-local survey follow-through in `P12-L09` rather than reopening broader shared PMO wording or driver-local code from this anti-overlap note alone
- shared PMO companions such as `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md` may therefore keep the `virtio_scsi` survey companions explicit as current driver-local packet members, while this anti-overlap note stays responsible only for keeping the family distinct from the starter-present `virtio_net` packet, its bounded transmit-disposition and queue-resume follow-ups, the published-but-unwired NVMe foothold, and the parked libbpf packet
- the driver-local `virtio_scsi` rollback-lab companions still stay bounded review evidence only; do not reopen storage-driver, queueing, rollback execution, or completion-path claims from this shared note alone
- Keep the bounded NVMe packet explicit through `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `drivers/nvme/host/pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, and `zigux/tests/phase12_nvme_pci_manifest.json` while leaving it outside the shared smoke-first route.
- Leave the parked libbpf packet, its survey, and its verify-shard boundary to `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` and `Documentation/zigux/phase12-libbpf-verify-shard-note.md` rather than reopening helper-local or loader-facing claims here.
- Keep the shared fallback split explicit: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` remains the one commit-pinned direct replay artifact, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` remains the current-master gap-inventory companion, and `Documentation/zigux/phase12-virtio-net-survey.md` plus `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors.

## Boundaries

- stops undercounting the newly landed `virtio_net` starter
- This note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
- This note must keep the shared release wording bounded to the starter-present `virtio_net` packet, its bounded `virtio_net_transmit_recycle` and `virtio_net_queue_resume` reviewability follow-ups, the directly readable but still survey-lane-split `virtio_scsi` rollback-lab packet, the published-but-still-unwired NVMe foothold, and the directly readable validator-side support bundle while the `phase12-*` Make-wrapper names remain stale reminder vocabulary on current `master`.
- This note must not recast the parked libbpf packet as direct shared replay or as a second active complex-driver lane.

## Next Bounded Step

If the shared Phase 12 packet moves again, reread this note beside `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `scripts/zigux/check-build-only-phase12-surface.py`, and `zigux/tests/README.md` before widening any driver-local claims. If the `virtio_scsi` packet drifts again, keep future same-lane follow-through parked inside one shared anti-overlap or checker truthfulness repair at a time, and leave exact survey-packet lane-key or verified-on realignment to the packet-local `P12-L09` surfaces rather than re-blurring the shared and driver-local Phase 12 lanes.
