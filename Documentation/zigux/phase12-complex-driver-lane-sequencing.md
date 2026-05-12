# Phase 12 Complex-Driver Lane Sequencing

This note is the anti-overlap companion for the shared Phase 12 complex-driver packet.

It keeps the release-planning work segmented so the active shared packet stays truthful without collapsing back into direct DMA, queueing, throughput, rollback, or recovery delivery.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_LANE=complex-driver-shared-release-packet`
- scope: shared release-planning, review-surface truthfulness, smoke-first replay reminders, fallback wording, and anti-overlap guidance for the bounded `nvme_pci`, `virtio_net`, and `virtio_scsi` families while current Phase 12 evidence stays split between published shared reminders, a shipped `virtio_scsi` lab packet, a parked `virtio_net` survey packet, and still-unpublished `nvme_pci` lane-local work
- release-order companion: `Documentation/zigux/phase12-release-sequencing.md`
- closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
- readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
- shared fallback overview: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`
- shared libbpf anti-overlap companion: `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
- driver-local NVMe reopen companion: `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`

## Lane Scope
- Stay inside the shipped docs-root, checklist, scripts-root, tests-root, workflow, and Makefile reminder packet. Treat `zigux/tests/phase12_build.zig` as the live shared-route anchor for the current smoke-first Phase 12 packet on `master`, not as a hypothetical reland target.
- Keep the current driver-local evidence explicit through the published `Documentation/zigux/phase12-virtio-net-survey.md`, `zigux/tests/phase12_virtio_net_manifest.json`, `zigux/tests/phase12_virtio_net_survey.zig`, `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, and `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig` packet.
- Keep the published NVMe reminder surface explicit through `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, while treating `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, direct `zigux/tests/phase12_nvme_pci*.zig`, `drivers/nvme/host/pci_verify.zig`, and `zigux/tests/phase12_nvme_pci_manifest.json` paths as lane-local unpublished-or-absent evidence until fresh repo reality on current `master` proves otherwise. Do not borrow the published fallback map as proof that the shared complex-driver packet has already widened into a shipped direct NVMe replay.
- Treat absent `drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, and `zigux/tests/phase12_virtio_net_syntax_lab.zig` surfaces as explicit anti-overlap boundaries for the parked direct `virtio_net` replay family, while keeping `zigux/tests/phase12_build.zig` named only as the shipped `virtio_scsi` smoke-first route rather than proof that `virtio_net` already has a direct shared replay.
- Treat the active shared replay order as fixed unless new shipped routes land first:
  1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
  2. `make -C zigux phase12-smoke`
  3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
  4. `make -C zigux phase12`
- Because current `master` does ship `zigux/tests/phase12_build.zig`, keep those commands documented as the live shared smoke-first route for the shipped `virtio_scsi` packet only. Do not treat them as proof that any one driver-local family, especially the parked `virtio_net` survey packet or unpublished `nvme_pci` work, is already runnable through its own direct replay.
- If `zig` is unavailable on `PATH`, reuse that same smoke-first order only through the shipped Make routes with `ZIG=<attached-zig-path>` instead of inventing a validator-first, driver-only, or other unshipped fallback route.
- Keep the degraded-workflow checker pair explicit beside that same order too:
  - `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
  - `python3 scripts/zigux/check-build-only-phase12-surface.py`

## Anti-Overlap Rules
- Shared-packet follow-through here should prefer one-file truthfulness repairs in `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, or `scripts/zigux/check-build-only-phase12-surface.py` before reopening driver-local behavior.
- Driver-local replay evolution belongs in the specific survey or test packet that changes, not in this shared owner-map note.
- If a nearby lane is relanding `nvme_pci` scratch files or rebuilding a parked `virtio_net` starter, keep that work in the driver-local packet even when shared reminders mention the family by name. This shared note only owns the routing truth about which driver-local packet is published, parked, absent, or still unpublished.
- The separate `p12-complex-drivers-nvme-pci-history` lane remains the home for bounded nvme recovery replay history and should not be folded back into this shared note unless the repo explicitly broadens the release packet.
- `P12-Y02` now owns the explicit NVMe driver-local reopen map in `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`; this shared note should mention that lane but should not absorb its DMA-note, recovery-governance, or owner-split follow-through.
- `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` remains the sibling owner map for shared libbpf heavy-helper reviewability so the shared Phase 12 packet does not merge driver-facing and helper-facing follow-through into one lane.

## Boundaries
- This note must not imply direct delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
- Keep queueing, throughput, rollback, and recovery wording bounded to the already-shipped driver-local packet plus the shared PMO release companions.
- There is still no shipped shared `scripts/zigux/validate-phase12.py`, `check-phase12-*.py`, focused-libbpf-only replay, cross-build replay, or `make -C zigux phase12-validate` route on current `master`.

## Next Bounded Step
If this lane reopens soon, rerun `python3 scripts/zigux/check-build-only-phase12-surface.py`, then reread `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` against the same published-versus-parked-versus-unpublished split recorded here. Current `master` already keeps the shared PMO release companions aligned around the parked `nvme_pci`, `virtio_net`, and libbpf direct-replay boundaries, and the sibling libbpf owner map plus `zigux/tests/README.md` already keep the snapshot-only verify-shard boundary explicit, so the next honest same-lane follow-through is the one-file `scripts/zigux/README.md` reminder repair that surfaces `Documentation/zigux/phase12-libbpf-verify-shard-note.md` beside the shared Phase 12 release packet before reopening PMO closure wording or widening any driver-local, DMA, queueing, throughput, or recovery claim.
