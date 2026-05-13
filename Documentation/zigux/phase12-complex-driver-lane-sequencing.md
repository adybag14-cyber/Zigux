# Phase 12 Complex-Driver Lane Sequencing

This note is the anti-overlap companion for the shared Phase 12 complex-driver packet.

It keeps the release-planning work segmented so the active shared packet stays truthful without collapsing back into direct DMA, queueing, throughput, rollback, or recovery delivery.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_LANE=complex-driver-shared-release-packet`
- scope: shared release-planning, review-surface truthfulness, smoke-first replay reminders, fallback wording, and anti-overlap guidance for the bounded `nvme_pci`, `virtio_net`, and `virtio_scsi` families while current Phase 12 evidence stays split between published shared reminders, a shipped `virtio_scsi` lab packet, a starter-present `virtio_net` packet, and a bounded NVMe starter-plus-verifier-plus-direct-test-plus-survey-note packet whose slice and survey-gate surfaces still remain outside the wired shared release route
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
- Keep the current driver-local evidence explicit through the published `Documentation/zigux/phase12-virtio-net-survey.md`, `zigux/tests/phase12_virtio_net_manifest.json`, `zigux/tests/phase12_virtio_net_survey.zig`, `drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig` packet.
- Keep the published NVMe reminder surfaces explicit through `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` together with `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`, the bounded starter `drivers/nvme/host/pci.zig`, the bounded verifier shard `drivers/nvme/host/pci_verify.zig`, the direct replay `zigux/tests/phase12_nvme_pci.zig`, the survey note `Documentation/zigux/phase12-nvme-pci-survey.md`, and the manifest anchor `zigux/tests/phase12_nvme_pci_manifest.json`, while still treating `Documentation/zigux/phase12-nvme-pci-slice.md` and `zigux/tests/phase12_nvme_pci_survey.zig` as repo-reality gaps rather than part of the shipped shared release packet until fresh repo reality on current `master` proves otherwise. Do not borrow the published fallback map, the reopen-governance note, or the starter-plus-verifier-plus-direct-test-plus-survey-note packet as proof that the shared complex-driver packet has already widened into a fully wired direct NVMe replay.
- Treat the current `virtio_net` family as a starter-present direct-replay packet, not as a release-closed or runtime-data-path claim: `drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, and `zigux/tests/phase12_virtio_net_syntax_lab.zig` are now present on `master`, while `Documentation/zigux/phase12-virtio-net-survey.md`, `zigux/tests/phase12_virtio_net_manifest.json`, and `zigux/tests/phase12_virtio_net_survey.zig` keep that starter explicitly below live DMA-safe receive ownership, refill execution, transport-backed queue flow, NAPI, XDP, XSK, RSS table programming, control-virtqueue runtime traffic, or full `net_device` lifecycle claims.
- Keep that same starter-present split explicit in future rereads so the shared owner map stops undercounting the newly landed `virtio_net` starter while the broader DMA-safe receive, refill, transport-backed queue flow, NAPI, XDP, XSK, RSS, control-virtqueue runtime traffic, and lifecycle work remains blocked.
- Treat the active shared replay order as fixed unless new shipped routes land first:
  1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
  2. `make -C zigux phase12-smoke`
  3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
  4. `make -C zigux phase12`
- Because current `master` does ship `zigux/tests/phase12_build.zig`, keep those commands documented as the live shared smoke-first route for the shipped `virtio_scsi` packet plus the starter-present `virtio_net` syntax-lab and direct contract packet. Do not treat them as proof that the still-missing `nvme_pci` slice, survey, or survey-gate packet, or the parked libbpf reviewability packet, already has its own direct shared replay.
- If `zig` is unavailable on `PATH`, reuse that same smoke-first order only through the shipped Make routes with `ZIG=<attached-zig-path>` instead of inventing a validator-first, driver-only, or other unshipped fallback route.
- Keep the degraded-workflow checker pair explicit beside that same order too:
  - `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
  - `python3 scripts/zigux/check-build-only-phase12-surface.py`

## Anti-Overlap Rules
- Shared-packet follow-through here should prefer one-file truthfulness repairs in `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, or `scripts/zigux/check-build-only-phase12-surface.py` before reopening driver-local behavior.
- Driver-local replay evolution belongs in the specific survey or test packet that changes, not in this shared owner-map note.
- If a nearby lane is relanding `nvme_pci` scratch files or rebuilding a parked `virtio_net` starter, keep that work in the driver-local packet even when shared reminders mention the family by name. This shared note only owns the routing truth about which driver-local packet is published, starter-present, verifier-only, parked, unwired, absent, or still unpublished.
- The separate `p12-complex-drivers-nvme-pci-history` lane remains the home for bounded nvme recovery replay history and should not be folded back into this shared note unless the repo explicitly broadens the release packet.
- `P12-L08` now owns the active starter-plus-verifier-plus-direct-test NVMe lane while `P12-Y02` stays the later reopen alias captured in `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`; this shared note should mention that lane family but should not absorb its DMA-note, recovery-governance, or owner-split follow-through.
- `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` remains the sibling owner map for shared libbpf heavy-helper reviewability so the shared Phase 12 packet does not merge driver-facing and helper-facing follow-through into one lane.

## Boundaries
- This note must not imply direct delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.
- Keep queueing, throughput, rollback, and recovery wording bounded to the already-shipped driver-local packet plus the shared PMO release companions.
- Current `master` does ship `scripts/zigux/validate-phase12.py` as an unwired helper, but there is still no shipped shared `check-phase12-*.py`, focused-libbpf-only replay, cross-build replay, or `make -C zigux phase12-validate` route.

## Next Bounded Step
If this lane reopens soon, rerun `python3 scripts/zigux/check-build-only-phase12-surface.py`, then reread `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` against the same published-versus-starter-present-versus-starter-plus-verifier-plus-direct-test-plus-survey-note-versus-published-fallback-only split recorded here. Current `master` already keeps the shared PMO release companions, the shared review checklist, the scripts-root packet, the tests-root packet, the driver-local `virtio_scsi` rollback-lab companions, the starter-present `virtio_net` packet, the parked libbpf direct-replay boundary, the parked `zigux/tests/fixtures/phase12_libbpf_snapshot.json` anchor, and the shipped-but-unwired `scripts/zigux/validate-phase12.py` helper aligned around that same bounded release packet. The next honest same-lane follow-through is therefore to leave this owner map parked unless that same shared release packet or the parked verify-shard boundary moves first instead of reopening already-landed review-checklist, scripts-root, or tests-root churn.
