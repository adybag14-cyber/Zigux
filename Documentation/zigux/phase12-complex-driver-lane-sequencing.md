# Phase 12 Complex-Driver Lane Sequencing

This note is the anti-overlap companion for the shared Phase 12 complex-driver packet.

It keeps the release-planning work segmented so the active shared packet stays truthful without collapsing back into direct DMA, queueing, throughput, rollback, or recovery delivery.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_LANE=complex-driver-shared-release-packet`
- scope: shared release-planning, review-surface truthfulness, smoke-first replay reminders, fallback wording, and anti-overlap guidance for the bounded `nvme_pci`, `virtio_net`, and `virtio_scsi` packet already shipped on current `master`
- release-order companion: `Documentation/zigux/phase12-release-sequencing.md`
- closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
- readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
- shared fallback overview: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- shared libbpf anti-overlap companion: `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`

## Lane Scope
- Stay inside the shipped docs-root, checklist, scripts-root, tests-root, workflow, Makefile, and `zigux/tests/phase12_build.zig` packet.
- Keep the current driver-local evidence explicit through `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_nvme_pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi.zig`, and `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`.
- Treat the active shared replay order as fixed unless new shipped routes land first:
  1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
  2. `make -C zigux phase12-smoke`
  3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
  4. `make -C zigux phase12`

## Anti-Overlap Rules
- Shared-packet follow-through here should prefer one-file truthfulness repairs in `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, or `scripts/zigux/check-build-only-phase12-surface.py` before reopening driver-local behavior.
- Driver-local replay evolution belongs in the specific survey or test packet that changes, not in this shared owner-map note.
- The separate `p12-complex-drivers-nvme-pci-history` lane remains the home for bounded nvme recovery replay history and should not be folded back into this shared note unless the repo explicitly broadens the release packet.
- `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` remains the sibling owner map for shared libbpf heavy-helper reviewability so the shared Phase 12 packet does not merge driver-facing and helper-facing follow-through into one lane.

## Boundaries
- This note must not imply direct delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
- Keep queueing, throughput, rollback, and recovery wording bounded to the already-shipped driver-local packet plus the shared PMO release companions.
- There is still no shipped shared `scripts/zigux/validate-phase12.py`, `check-phase12-*.py`, focused-libbpf-only replay, cross-build replay, or `make -C zigux phase12-validate` route on current `master`.

## Next Bounded Step
If this lane reopens soon, start with the one-file scripts-root wording sync that keeps `scripts/zigux/README.md` explicit about the already-landed `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, then recheck `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, and `zigux/tests/README.md` against the same smoke-first Phase 12 packet before widening any driver-local, DMA, queueing, throughput, or recovery claim.
