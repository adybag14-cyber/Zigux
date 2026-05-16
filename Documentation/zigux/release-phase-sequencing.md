# Zigux Release Phase Sequencing

This note is the docs-root PMO index for the current release-facing Zigux phases.

It exists to keep the active release packet ordered across Phase 12, Phase 13, Phase 14, and Phase 15 without reopening already-bounded driver, helper, smoke, or governance slices.

## Status

- `ZIGUX_RELEASE_SEQUENCE_VERSION=1`
- scope: cross-phase release planning only
- authority: current `master` reminder surfaces and shared validator or replay handles
- release-planning packet:
  - `Documentation/zigux/phase12-release-sequencing.md`
  - `Documentation/zigux/phase12-release-coordination-matrix.md`
  - `Documentation/zigux/phase13-release-coordination-matrix.md`
  - `Documentation/zigux/phase14-release-boundary-survey.md`
  - `Documentation/zigux/phase15-readiness-gate-survey.md`
  - `Documentation/zigux/phase15-handoff-next-steps-survey.md`

## Roadmap Reading

The roadmap keeps release-facing work staged rather than collapsed into one broad closure claim.

That means the PMO release order on current `master` is:

1. Phase 12 shared release packet
2. Phase 13 contributor-facing shared-helper packet
3. Phase 14 study-only smoke boundary packet
4. Phase 15 parked governance and handoff packet

This is a sequencing rule, not a statement that every earlier phase is fully closed.

## Phase Order

### Phase 12: active shared release packet

- posture: active and not closed
- owner packet: `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md`
- stable support handle: `make -C zigux phase12-validate`
- stable replay handles: `make -C zigux phase12-smoke` and `make -C zigux phase12`
- current PMO reading: this is the first release-facing phase because it is the earliest live packet that already carries validator-first then smoke-first release wording for active complex-driver work on current `master`
- boundary: keep `virtio_net` starter-present, `virtio_scsi` smoke-first plus rollback-lab companions, and the published-but-still-unwired NVMe foothold explicit without promoting parked libbpf notes or deeper transport work into shipped release evidence

### Phase 13: active contributor-facing shared-helper packet

- posture: active and not closed
- owner packet: `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, and `Documentation/zigux/phase13-release-coordination-matrix.md`
- stable support handle: `python3 scripts/zigux/validate-phase13-release.py`
- stable replay handle: `make -C zigux phase13-validate`
- blocked convenience route: `make -C zigux phase13`
- current PMO reading: this phase follows Phase 12 because it packages contributor-facing helper release wording and traceability around shipped `libfs`, `devres`, and Landlock packets, but it still depends on a validator-first handle instead of a landed shared build replay
- boundary: keep repo-reality gaps explicit, especially the missing shared `zigux/tests/phase13_build.zig` companion, and do not describe adjacent notifier evidence as a fifth shipped helper lane

### Phase 14: study-only smoke boundary packet

- posture: present, reviewable, and not closed
- owner packet: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-core-boundary-traceability.md`, and `Documentation/zigux/phase14-release-boundary-survey.md`
- stable support handle: `make -C zigux phase14-validate`
- stable smoke handle: `make -C zigux phase14-smoke`
- stable full-bundle handle: `make -C zigux phase14-test`
- stable convenience route: `make -C zigux phase14`
- current PMO reading: this phase follows Phase 13 because it is release-facing only as a study-only smoke and boundary packet for deep-core-adjacent anchors, not as a new delivery tranche
- boundary: keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` in bounded study-only follow-through, keep `net/core/skbuff.c` and `kernel/rcu/tree.c` frozen in C, and route any status-change discussion to Phase 15 governance instead

### Phase 15: parked governance and handoff packet

- posture: maintenance-mode governance only
- owner packet: `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-parity-scorecard-survey.md`, and `Documentation/zigux/phase15-indefinite-c-policy.md`
- stable support handle: `make -C zigux phase15-validate`
- stable replay handles: `make -C zigux phase15-test` and `make -C zigux phase15`
- current PMO reading: this phase is last in the release sequence because it does not unlock new implementation scope by itself; it records the blocked readiness and handoff posture that must stay truthful until stronger evidence exists for any freeze-map status change
- boundary: keep `phase15-deep-core-status-change-blocker` explicit and do not treat governance maintenance as a release-closure event

## Hand-off Rules

Use this cross-phase order when deciding which release artifact to refresh:

1. Refresh Phase 12 first when a shared validator-first, smoke-first, complex-driver release packet changes.
2. Refresh Phase 13 next when contributor-facing helper release wording, repo-reality gaps, or stable validator-first handles change.
3. Refresh Phase 14 next when the study-only smoke boundary packet, full-bundle inventory, or attached-toolchain replay wording changes.
4. Refresh Phase 15 last when governance, readiness, or handoff posture changes.

If a later phase changes but an earlier phase still has shared-summary drift in the same release family, repair the earlier shared-summary drift first.

## Non-goals

- This note does not close any phase.
- This note does not create a new validator or replay route.
- This note does not replace the phase-local matrices, surveys, or checklists.
- This note does not authorize deep-core status changes.

## Next Bounded Step

If release-planning wording drifts again, reread this note beside:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase12-release-sequencing.md`
- `Documentation/zigux/phase12-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase14-release-boundary-survey.md`
- `Documentation/zigux/phase15-readiness-gate-survey.md`
- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Keep the next PMO follow-through bounded to the smallest shared-summary or coordination artifact that current `master` actually shows as stale.
