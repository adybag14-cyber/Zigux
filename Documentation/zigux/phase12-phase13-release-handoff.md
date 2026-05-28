# Phase 12 to Phase 13 Release Handoff

This note records the PMO handoff boundary between the active Phase 12 release packet and the active Phase 13 shared-helper packet on current `master`.

It is a release-planning artifact only. It does not close either tranche, widen either packet, or create a new replay route.

## Status

- `PHASE12_STATUS=active`
- `PHASE13_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- `PHASE13_RELEASE_CLOSED=no`
- `PHASE12_TO_PHASE13_HANDOFF_STATE=sequenced_not_promoted`
- lane owner: `pmo-release`
- Phase 12 source companions: `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`
- Phase 13 destination companions: `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-packet-index.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`
- shared validator-side companions: `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, `scripts/zigux/check-phase13-tests-readme-alignment.py`, `scripts/zigux/validate-phase13-release.py`

## Handoff Reading

- Phase 12 stays the active-not-closed release packet for the returned shared wrapper set `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`, plus the six-file shared `virtio_net` smoke-and-test sextet in `zigux/tests/phase12_build.zig`.
- Phase 12 remains narrower than its adjacent driver-local packets: the rollback-lab `virtio_scsi` survey-build packet, the bounded `nvme_pci` foothold, and the parked libbpf packet stay explicit as release-planning context but do not become shared Phase 12 closure proof through this handoff note.
- Phase 13 stays the next release-facing packet only as a contributor-facing and reminder-surface transition. Its shared handle remains the workflow guide, scripts-root reminder, tests-root reminder, release-packet index, release-coordination matrix, release-notes survey, roadmap-traceability note, shared-summary gap note, notifier-gap note, and the shipped Phase 13 reminder validators.
- Phase 13 still does not own a returned shared Makefile route. `zigux/Makefile` is present on current `master`, but `make -C zigux phase13-validate` and `make -C zigux phase13` stay repo-reality gaps and must remain explicit as gaps whenever this handoff note summarizes the downstream packet.
- The practical PMO handoff is therefore sequencing-only: keep Phase 12 reviewable as the active release packet, keep Phase 13 reviewable as the next contributor-facing release packet, and do not promote either packet into closure language or cross-phase build-handle language that current `master` does not support.

## Review Order

1. Reread the Phase 12 source packet first through `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `scripts/zigux/validate-phase12.py`, and `zigux/Makefile`.
2. Reread the Phase 13 destination packet next through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-packet-index.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, and `scripts/zigux/check-phase13-tests-readme-alignment.py`.
3. Refresh this note only when one of those two packets changes the cross-phase release boundary. Leave fallback-only evidence refreshes to the neighboring fallback lane and leave helper-local Phase 13 expansion to the shared-helper lane.

## Boundaries

- This note does not close Phase 12.
- This note does not close Phase 13.
- This note does not promote driver-local `virtio_scsi`, `nvme_pci`, or parked libbpf evidence into shared Phase 12 replay proof.
- This note does not promote the missing Phase 13 Makefile routes into shipped evidence.
- This note does not reopen Phase 14 study-only or freeze-map ownership.

## Next Bounded Step

If the active Phase 12 packet changes its shared wrapper set, its six-file `virtio_net` sextet, or its release-planning boundaries, reread this note beside the updated Phase 12 packet first and land only the smallest handoff-side truthfulness repair.

If the active Phase 13 packet changes its stable contributor-facing handle, its four roadmap anchors, or its repo-reality-gap list, reread this note beside the updated Phase 13 packet first and keep the handoff downstream of the still-missing shared Phase 13 build handle.

If only fallback-read evidence drifts, keep this handoff note parked and let the neighboring fallback-specific lane absorb that narrower update.
