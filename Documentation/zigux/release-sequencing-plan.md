# Zigux Release Sequencing Plan

This document records the bounded PMO release-planning packet for phase sequencing, tranche closure, and release coordination across the current Zigux roadmap state.

## Status

- `RELEASE_PLAN_STATUS=active`
- `RELEASE_PLAN_SCOPE=phase_sequencing_tranche_closure_release_coordination`
- `RELEASE_PLAN_VALIDATOR=python3 scripts/zigux/validate-release-sequencing.py`
- `RELEASE_PLAN_FOUNDATION_PHASES=phase1_closed,phase2_closed`
- `RELEASE_PLAN_ACTIVE_RELEASE_PACKET=phase13_release_discipline`
- `RELEASE_PLAN_ACTIVE_SMOKE_PACKET=phase14_stay_in_c_smoke`
- `RELEASE_PLAN_PARKED_GOVERNANCE_PACKET=phase15_maintenance_mode`
- `RELEASE_PLAN_NEXT_REOPEN_TRIGGER=phase_state_change_or_shared_replay_drift`
- product boundary:
  - `Documentation/zigux/release-sequencing-plan.md`
  - `scripts/zigux/validate-release-sequencing.py`
  - `Documentation/zigux/phase1-closure.md`
  - `Documentation/zigux/phase2-closure.md`
  - `Documentation/zigux/phase13-release-notes-survey.md`
  - `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
  - `Documentation/zigux/phase15-readiness-gate-survey.md`
  - `Documentation/zigux/phase15-handoff-next-steps-survey.md`

## Why this packet exists

The roadmap and bootstrap ledger already give Zigux a lot of phase-local evidence:

- closed Phase 1 and Phase 2 tranche records
- active Phase 13 release-discipline evidence
- active Phase 14 stay-in-C smoke evidence
- parked Phase 15 governance and handoff evidence

What the repo did not yet carry in one place was the PMO view that answers the release-sequencing question directly:

- which phases are already closed
- which phases are still active and should not be announced as closed
- which governance packet is parked rather than unfinished
- what the next honest coordination trigger is for refreshing the release story

This note exists to keep that reading explicit without inventing a new product phase or reopening any deeper implementation lane.

## Current release sequence

### Release train A: foundations already closed

- Phase 1 is closed through `Documentation/zigux/phase1-closure.md`
- Phase 2 is closed through `Documentation/zigux/phase2-closure.md`
- those two phases are the only current roadmap tranches with explicit closure records on `master`

### Release train B: substrate and validation packets still active

- Phases 3 through 6 remain validator-backed and reviewable, but they are not globally closed release tranches
- their current repo value is ongoing substrate, helper, and validation coverage rather than a new tranche-close announcement

### Release train C: runtime-safe helpers and tooling still active

- Phases 7 and 8 are active helper and tooling packets with dedicated replay paths
- those packets are release-relevant, but they still read as active bounded lanes rather than closure artifacts

### Release train D: runtime and driver pilots still active

- Phases 9 through 12 remain active runtime, transport, and driver packets
- they should stay release-facing only through their bounded surveys, manifests, and validator-first replay paths

### Release train E: release discipline and governance packet

- Phase 13 is the current active release-discipline packet through `Documentation/zigux/phase13-release-notes-survey.md`
- Phase 14 is the current active stay-in-C smoke packet through `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
- Phase 15 is governance-landed and parked in maintenance mode through `Documentation/zigux/phase15-readiness-gate-survey.md` and `Documentation/zigux/phase15-handoff-next-steps-survey.md`

## Current tranche-closure reading

The current honest tranche-closure reading is:

- closed: Phase 1, Phase 2
- active and release-facing: Phase 13, Phase 14
- parked after green shared replay: Phase 15
- not to be announced as globally closed from this packet alone: Phases 3 through 14 beyond the two explicit closure records already present

That keeps the release story narrow. The repo already has real validation and survey coverage for many later phases, but this PMO packet should not confuse active evidence with a tranche-close claim.

## Coordination rule

Refresh this release-sequencing packet only when one of these changes happens:

1. a new phase-level closure record lands
2. an active release-facing packet changes its status or replay posture
3. the parked Phase 15 governance packet reopens or drifts out of alignment

If none of those three changes is true, the release-planning lane should stay parked instead of generating another adjacent planning artifact.

## Next bounded step

Keep this packet aligned with the existing Phase 13, Phase 14, and Phase 15 evidence families, and refresh it only when the next real phase-status change lands on `master`.
