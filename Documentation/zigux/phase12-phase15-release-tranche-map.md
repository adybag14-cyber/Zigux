# Phase 12-15 Release Tranche Map

This note is the compact PMO handoff map for the active late-phase Zigux release packet on current `master`.

It does not reopen any closed tranche, and it does not invent a new replay route.

## Status

- `RELEASE_PACKET_PROVENANCE=current-master-readback-2026-05-13`
- `RELEASE_PACKET_PHASE_COUNT=4`
- `RELEASE_PACKET_ACTIVE_PHASES=phase12,phase13,phase14,phase15`
- `RELEASE_PACKET_RELEASE_CLOSED_PHASE_COUNT=0`

## Sequencing Rules

1. Treat `Phase 12` as the active release packet that still owns smoke-first replay truthfulness.
2. Treat `Phase 13` as the contributor-facing release surface that keeps helper-family release wording honest.
3. Treat `Phase 14` as the study-only release-boundary packet for bounded deep-core evidence, not as an active delivery tranche.
4. Treat `Phase 15` as parked governance maintenance until an Architecture Council status-change approval actually lands.

## Phase 12

- status: `active`
- release posture: starter-present `virtio_net` plus smoke-first `virtio_scsi`; not release-closed
- authoritative notes:
  - `Documentation/zigux/phase12-release-sequencing.md`
  - `Documentation/zigux/phase12-release-closure-checklist.md`
  - `Documentation/zigux/phase12-release-readiness-survey.md`
  - `Documentation/zigux/phase12-release-coordination-matrix.md`
- shipped routes:
  - `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
  - `make -C zigux phase12-smoke`
  - `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
  - `make -C zigux phase12`
- boundary:
  - keep `Documentation/zigux/phase12-libbpf-verify-shard-note.md` parked as reviewability-only
  - do not describe `phase12-validate`, focused libbpf replay, cross-build replay, or direct `nvme_pci` replays as shipped release evidence
- next bounded PMO step:
  - reread the four release notes above plus `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` only after the shared Phase 12 packet moves again

## Phase 13

- status: `active`
- release posture: contributor-facing shared-helper release surface; not release-closed
- authoritative notes:
  - `Documentation/zigux/phase13-release-notes-survey.md`
  - `Documentation/zigux/phase13-roadmap-traceability.md`
  - `Documentation/zigux/phase13-contributor-workflow-guide.md`
  - `Documentation/zigux/phase13-notifier-list-survey.md`
- shipped routes:
  - `make -C zigux phase13-validate`
  - `make -C zigux phase13`
- boundary:
  - keep missing shared-build or notifier companion files framed as repo-reality gaps
  - keep notifier evidence adjacent to the release surface rather than turning it into a fifth helper lane
- next bounded PMO step:
  - refresh broad contributor-facing release wording only if helper-family release notes drift away from the shipped helper-local and validator-first packet

## Phase 14

- status: `active`
- release posture: shared smoke packet for study-only or freeze-in-C anchors; not release-closed
- authoritative notes:
  - `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
  - `Documentation/zigux/phase14-release-boundary-survey.md`
  - `Documentation/zigux/phase14-core-boundary-traceability.md`
- shipped routes:
  - `make -C zigux phase14-validate`
  - `make -C zigux phase14-smoke`
  - `make -C zigux phase14-test`
  - `make -C zigux phase14`
- boundary:
  - `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain boundary-study-only anchors
  - `net/core/skbuff.c` and `kernel/rcu/tree.c` remain freeze-in-C-governed anchors
  - no active deep-core port claim is allowed from this release packet
- next bounded PMO step:
  - keep the packet parked unless a shared smoke artifact, manifest, checker, or route inventory drifts

## Phase 15

- status: `parked`
- release posture: governance maintenance only; no freeze-map status change approved
- authoritative notes:
  - `Documentation/zigux/phase15-readiness-gate-survey.md`
  - `Documentation/zigux/phase15-governance-lane-sequencing.md`
  - `Documentation/zigux/phase15-freeze-map-governance.md`
  - `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- shipped routes:
  - `make -C zigux phase15-validate`
  - `make -C zigux phase15-test`
  - `make -C zigux phase15`
- boundary:
  - keep the packet in maintenance mode until the blocker posture changes
  - do not treat parity-scorecard or indefinite-C maintenance as shared-summary backlog
- next bounded PMO step:
  - wait for a named reopen trigger or a real blocker-posture change; otherwise keep summary work limited to truthfulness repairs

## Handoff Use

- Start with `Phase 12` when the question is about release closure, sequencing, or shipped replay truthfulness.
- Start with `Phase 13` when the question is about contributor-facing release wording for the shared-helper tranche.
- Start with `Phase 14` when the question is about smoke-packet boundaries for study-only deep-core anchors.
- Start with `Phase 15` when the question is about governance readiness or freeze-map review posture.

## Non-Goals

- This map does not claim any late phase is release-closed.
- This map does not create a new validator, workflow, or make target.
- This map does not change the freeze map, blocker state, or release evidence for any phase.
