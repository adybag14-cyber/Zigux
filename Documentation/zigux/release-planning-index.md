# Zigux Release Planning Index

This note is the compact docs-root index for the active Zigux release-planning packet.

It keeps the currently relevant release-planning surfaces for Phases 12 through 15 in one place so PMO and release-management follow-up can stay scoped to the real roadmap packet instead of drifting across unrelated helper or driver lanes.

## Status

- `RELEASE_PLANNING_PACKET=active`
- `RELEASE_PLANNING_PHASE_WINDOW=12-15`
- `RELEASE_PLANNING_SCOPE=phase sequencing, tranche closure posture, release coordination artifacts, and governance handoff surfaces`
- `RELEASE_PLANNING_CLOSURE_CLAIM=no_global_release_closure`
- docs-root companion: `Documentation/zigux/README.md`
- review companion: `Documentation/zigux/review-checklist.md`

## Phase Map

### Phase 12

- posture: active, not closed
- packet focus: starter-present complex-driver release sequencing and readiness
- primary coordination surfaces:
  - `Documentation/zigux/phase12-release-sequencing.md`
  - `Documentation/zigux/phase12-release-coordination-matrix.md`
  - `Documentation/zigux/phase12-release-readiness-survey.md`
  - `Documentation/zigux/phase12-release-closure-checklist.md`
- validation and replay handle:
  - `scripts/zigux/check-build-only-phase12-surface.py`
  - `scripts/zigux/check-phase12-release-readiness-packet.py`
  - `make -C zigux phase12-validate`
  - `make -C zigux phase12-smoke`
  - `make -C zigux phase12`
- next honest PMO step:
  - keep shared reminder surfaces aligned with the validator-first then smoke-first packet without promoting the parked libbpf or driver-local NVMe notes into the shipped shared release route

### Phase 13

- posture: active, not closed
- packet focus: contributor-facing shared-helper release coordination
- primary coordination surfaces:
  - `Documentation/zigux/phase13-release-coordination-matrix.md`
  - `Documentation/zigux/phase13-release-notes-survey.md`
  - `Documentation/zigux/phase13-roadmap-traceability.md`
  - `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- validation and replay handle:
  - `scripts/zigux/validate-phase13-release.py`
  - `make -C zigux phase13-validate`
  - `make -C zigux phase13`
- next honest PMO step:
  - keep the docs-root, scripts-root, tests-root, and contributor-facing reminder packet aligned around the same four helper anchors and adjacent notifier support without reopening a missing shared build route

### Phase 14

- posture: active release-boundary packet, not closed
- packet focus: study-only end-to-end smoke and release-boundary review
- primary coordination surfaces:
  - `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
  - `Documentation/zigux/phase14-release-boundary-survey.md`
  - `Documentation/zigux/phase14-core-boundary-traceability.md`
- validation and replay handle:
  - `scripts/zigux/validate-phase14.py`
  - `scripts/zigux/check-phase14-docs-root-smoke-summary.py`
  - `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`
  - `make -C zigux phase14-validate`
  - `make -C zigux phase14-smoke`
  - `make -C zigux phase14-test`
  - `make -C zigux phase14`
- next honest PMO step:
  - keep the shared smoke packet parked unless the manifest-backed anchor bundle or the release-boundary wording drifts, and keep any follow-up inside review-only boundary maintenance rather than status-change claims

### Phase 15

- posture: parked governance packet in maintenance mode
- packet focus: freeze-map governance, review-process truthfulness, and release-governance handoff
- primary coordination surfaces:
  - `Documentation/zigux/phase15-freeze-map-governance.md`
  - `Documentation/zigux/phase15-architecture-council-review-process.md`
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `Documentation/zigux/phase15-indefinite-c-policy.md`
- validation and replay handle:
  - `scripts/zigux/validate-phase15.py`
  - `scripts/zigux/check-phase15-scripts-readme-alignment.py`
  - `scripts/zigux/check-phase15-review-process-handoff.py`
  - `make -C zigux phase15-validate`
  - `make -C zigux phase15-test`
  - `make -C zigux phase15`
- next honest PMO step:
  - leave the governance packet parked unless a named reopen trigger, deep-core blocker change, or shared-summary drift makes one of the Phase 15 maintenance notes untruthful

## Release Order By Posture

1. Treat Phase 12 as the live release-planning tranche for shipped shared replay sequencing.
2. Treat Phase 13 as the active contributor-facing release packet that keeps shared-helper delivery reviewable but not closed.
3. Treat Phase 14 as a release-boundary smoke packet that verifies study-only evidence without implying promotion.
4. Treat Phase 15 as governance and handoff maintenance, not as an implementation-release tranche.

## PMO Use

- reread this index beside `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md` when any Phase 12-15 release note changes
- narrow follow-up to the smallest phase-local coordination, sequencing, closure, or governance artifact that drifted
- do not treat this index as a substitute for the phase-local notes or the validator-backed replay handles
- do not use this index to justify new delivery claims outside the current roadmap-backed packet

## Next Bounded Step

If future repo drift makes the docs root harder to navigate again, the next same-lane PMO step is to align `Documentation/zigux/README.md` with this index and the existing Phase 12-15 release notes. Until that drift appears, keep follow-up phase-local and avoid widening the release-planning packet.
