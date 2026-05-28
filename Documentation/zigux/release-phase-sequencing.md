# Release Phase Sequencing

This note is the compact PMO release-order map for the active release-facing Zigux packet on current `master`.

It is a release-planning artifact only. It does not close any tranche, create a new replay route, or widen helper-local or study-only delivery claims.

## Status

- `RELEASE_PACKET_STATUS=active_not_closed`
- `RELEASE_PACKET_LANE=pmo-release`
- `RELEASE_PHASE_SEQUENCE_MODE=current_master_truthfulness`
- source packet companions:
  - `Documentation/zigux/phase12-release-sequencing.md`
  - `Documentation/zigux/phase12-release-coordination-matrix.md`
  - `Documentation/zigux/phase12-phase13-release-handoff.md`
  - `Documentation/zigux/phase13-release-coordination-matrix.md`
  - `Documentation/zigux/phase13-release-notes-survey.md`
  - `Documentation/zigux/phase14-release-boundary-survey.md`
  - `Documentation/zigux/phase15-readiness-gate-survey.md`
  - `Documentation/zigux/freeze-map.md`
- rule: keep release wording tied to directly readable current-`master` surfaces, and keep missing shared routes explicit instead of smoothing them over with summary prose

## Release Order

1. **Phase 12 active release packet**
   - status: active, not closed
   - shipped shared wrapper evidence: `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`
   - shared packet scope: the six-file `virtio_net` smoke-and-test sextet in `zigux/tests/phase12_build.zig`
   - boundary: keep driver-local `virtio_scsi`, `nvme_pci`, and parked libbpf evidence outside the shared release proof
2. **Phase 13 downstream contributor-facing release packet**
   - status: active, not closed
   - shipped shared release handle: docs-root, scripts-root, tests-root, packet-index, release-notes, roadmap-traceability, and validator surfaces only
   - current blocker: `zigux/Makefile` is present on current `master`, but `make -C zigux phase13-validate` and `make -C zigux phase13` remain repo-reality gaps
   - boundary: keep the four roadmap anchors explicit and do not promote adjacent notifier evidence into a fifth helper lane
3. **Phase 14 study-only release boundary packet**
   - status: reviewable study-only packet, not active delivery
   - shipped shared gate: `make -C zigux phase14-validate`
   - current blocker: `phase14-smoke`, `phase14-test`, and `phase14` remain absent from the readable Makefile surface
   - boundary: keep workqueue and ring-buffer follow-through study-only, and keep `net/core/skbuff.c` plus `kernel/rcu/tree.c` under freeze-map ownership
4. **Phase 15 governance readiness packet**
   - status: landed governance packet with validator-first maintenance replay, not broader route closure
   - shipped readiness evidence: `python3 scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_build.zig`, and `zigux/tests/phase15_readiness_gap_matrix.json`
   - current blocker: no dedicated `phase15-validate`, `phase15-test`, `phase15`, or shared workflow route is directly readable on current `master`
   - boundary: do not turn governance readiness into a freeze-map status change or deep-core delivery approval claim

## Coordination Rules

- Treat Phase 12 as the only returned shared wrapper-backed release packet in this sequence.
- Treat Phase 13 as the next release-facing packet only through reminder surfaces, validator surfaces, and roadmap-owned helper anchors until its shared Makefile routes return.
- Treat Phase 14 as a release-boundary and study-only packet with one returned validation gate, not as an active replay tranche.
- Treat Phase 15 as governance readiness with direct maintenance evidence, not as a returned one-command or shared-CI route family.
- Escalate only the smallest reminder-side truthfulness repair when one phase note drifts against this sequence.

## Review Order

1. Reread the active Phase 12 packet first through `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, and `Documentation/zigux/phase12-phase13-release-handoff.md`.
2. Reread the downstream Phase 13 packet next through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-release-notes-survey.md`, and `Documentation/zigux/phase13-roadmap-traceability.md`.
3. Reread the study-only boundary packet next through `Documentation/zigux/phase14-release-boundary-survey.md` and `Documentation/zigux/freeze-map.md`.
4. Reread the governance readiness packet last through `Documentation/zigux/phase15-readiness-gate-survey.md` and `zigux/tests/phase15_readiness_gap_matrix.json`.

## Non-goals

- This note does not close Phase 12, Phase 13, Phase 14, or Phase 15.
- This note does not create a new build or validation route.
- This note does not promote missing Phase 13 or Phase 15 Makefile routes into shipped evidence.
- This note does not weaken freeze-map ownership for deep-core anchors.

## Next Bounded Step

Keep this sequencing note parked unless one of the phase-local PMO notes changes the current release ladder.

If Phase 12 changes its shared wrapper set or its six-file shared packet, refresh the Phase 12 entry only.

If Phase 13 returns shared Makefile routes or changes its roadmap-owned helper split, refresh the Phase 13 entry only.

If Phase 14 returns broader shared routes or Phase 15 returns dedicated wrappers or workflow coverage, refresh only the smallest affected entry and leave the rest of the release ladder untouched.
