# Release Planning Index

This note is the compact PMO index for the active Zigux release-planning packet on current `master`.

It exists to keep the later-phase release surfaces easy to find without implying that those phases are already closed, share one replay route, or collapse helper-local and governance-only packets into one generic release claim.

## Status

- `RELEASE_PACKET_STATUS=active_not_closed`
- lane owner: `PMO / Release Management`
- scope: active release sequencing, tranche-closure companions, release-boundary reminders, and governance-closeout inputs across the later roadmap phases
- docs-root release index guard: `python3 scripts/zigux/check-release-planning-index.py`

## Active Packet

Keep the active release packet anchored to these current-owner notes:

- `Documentation/zigux/phase12-release-sequencing.md`
- `Documentation/zigux/phase12-release-readiness-survey.md`
- `Documentation/zigux/phase12-release-closure-checklist.md`
- `Documentation/zigux/phase12-release-coordination-matrix.md`
- `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase14-release-boundary-survey.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`

## Phase Split

- Phase 12 remains the active shared release packet for validator-first ordering, smoke-first replay order, fallback coverage, and driver-local release coordination. Keep it tied to the bounded `virtio_net` shared route plus the adjacent `virtio_scsi`, NVMe, and libbpf reminders instead of widening it into deeper transport delivery claims.
- Phase 13 remains the active helper-release packet for contributor-facing sequencing, release notes, roadmap traceability, and helper-family coordination across `libfs`, `devres`, and Landlock. Keep notifier evidence adjacent and do not promote it into a fifth shared-helper anchor.
- Phase 14 remains the release-boundary and productization reminder packet. Keep it framed as a study-only and release-boundary surface with the returned `phase14-validate` split, not as a closed smoke tranche.
- Phase 15 remains Architecture Council governance for stay-in-C review, closeout posture, and reopen-evidence rules. Keep it explicit as governance support for release decisions rather than as direct feature-delivery proof.

## Review Loop

When PMO release wording changes, reread this note beside:

- `Documentation/zigux/phase12-release-sequencing.md`
- `Documentation/zigux/phase12-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase14-release-boundary-survey.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `python3 scripts/zigux/check-release-planning-index.py`

## Boundaries

- This index does not close any tranche by itself.
- This index does not create a new shared build or replay route.
- This index must keep Phase 12 shared replay, Phase 13 helper-local release wording, Phase 14 release-boundary posture, and Phase 15 governance posture distinct.

## Next Bounded Step

Leave this note parked unless one of the indexed owner notes moves or a later-phase PMO surface becomes hard to discover from current release-planning rereads. If that happens, land only the smallest index-side truthfulness repair and rerun `python3 scripts/zigux/check-release-planning-index.py`.
