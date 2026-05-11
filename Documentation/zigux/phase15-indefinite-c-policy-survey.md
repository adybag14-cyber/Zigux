# Phase 15 Indefinite-C Policy Survey

This document records the bounded Phase 15 governance lane for comparing the current indefinite-C policy packet on `master` against the roadmap requirement for a policy covering code that remains in C indefinitely.

## Status

- `PHASE15_LANE_KEY=P15-L13`
- `PHASE15_STATUS=indefinite_c_policy_survey`
- `PHASE15_SLICE=indefinite-c-policy-gap-vs-roadmap`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- survey provenance refreshed against dated current-master readback marker `current-master-readback-2026-05-11` on 2026-05-11
- scope: one survey-grade note that compares the live indefinite-C policy note, its machine-readable JSON companion, the dedicated Zig replay, and the surrounding Phase 15 governance reminders without widening into any deep-core status-change claim
- product boundary:
  - `Documentation/zigux/phase15-indefinite-c-policy.md`
  - `zigux/tests/phase15_indefinite_c_policy.json`
  - `zigux/tests/phase15_indefinite_c_policy.zig`
  - `zigux/tests/phase15_indefinite_c_blocker_evidence.zig`
  - `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase15-handoff-next-steps-survey.md`
  - `Documentation/zigux/phase15-readiness-gate-survey.md`
  - `scripts/zigux/validate-phase15.py`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`

## Why this survey exists

The roadmap says Phase 15 must include a policy for code that remains in C indefinitely.

Current `master` now carries that policy packet. The same-lane question is no longer whether Zigux lacks an indefinite-C policy. The honest survey question is whether the landed note, the machine-readable companion, the Zig replay, and the surrounding governance reminders all describe the same maintenance-mode stay-in-C posture.

## Roadmap requirement versus current master

The roadmap-required Phase 15 governance features are:

- freeze map
- Architecture Council review process
- parity scorecard
- policy for code that remains in C indefinitely

The dated 2026-05-11 readback shows that the indefinite-C policy requirement itself is already satisfied on `master` through:

- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `zigux/tests/phase15_indefinite_c_policy.json`
- `zigux/tests/phase15_indefinite_c_policy.zig`

The current policy packet also keeps the two narrower same-family replays explicit:

- `zigux/tests/phase15_indefinite_c_blocker_evidence.zig`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`

## Current packet agreement

The landed indefinite-C note, JSON companion, and Zig replay agree on these core facts:

- the roadmap requirement is `policy for code that remains in C indefinitely`
- the governed freeze-in-C anchors are `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c`
- the existing C implementation remains the product source of truth for the current plan horizon
- there is no silent exception path around the stay-in-C posture
- the only allowed reopen path is an Architecture Council request with fresh linked evidence
- the named reopen-trigger catalog remains `narrower_followup_answers_blocker`, `evidence_packet_stale_or_contradictory`, and `ownership_or_validation_changed`
- the remaining blocker is still `phase15-deep-core-status-change-blocker`

The broader governance reminders also keep that same maintenance-mode posture explicit:

- `Documentation/zigux/freeze-map.md` keeps the freeze-in-C rule and the no-silent-exception language explicit
- `Documentation/zigux/phase15-handoff-next-steps-survey.md` treats the indefinite-C note as a landed member of the parked governance family
- `Documentation/zigux/phase15-readiness-gate-survey.md` keeps the no-approval-yet posture explicit for the whole Phase 15 packet
- `scripts/zigux/validate-phase15.py` requires the indefinite-C note, the JSON companion, and the shared replay routes before Phase 15 validation can pass
- `scripts/zigux/README.md` and `zigux/tests/README.md` both name the indefinite-C packet as part of the shipped Phase 15 maintenance surface

## Current gap

The current same-lane gap is not a missing indefinite-C policy packet.

The real gap was narrower: Phase 15 already carried the indefinite-C note, its machine-readable companion, its Zig replay, and its blocker-evidence pair, but it did not yet carry a dedicated survey note that compared those landed surfaces against the roadmap and recorded that the remaining work is maintenance-mode blocker posture rather than another missing policy artifact.

Without that survey note, neighboring Phase 15 work could too easily collapse back into two unhelpful stories:

- incorrectly implying that the roadmap-required indefinite-C policy is still absent from `master`
- incorrectly treating the landed policy packet as if it had already moved beyond the current no-approval-yet blocker posture

## Honest current posture

The honest bounded Phase 15 statement on current `master` is:

- the roadmap-required indefinite-C policy packet is landed
- its dedicated note, machine-readable JSON companion, and Zig replay are all present on `master`
- the narrower blocker-evidence and lane-owner-alignment replays are also present
- the shared validator-first and replay routes still point at the landed packet
- no Architecture Council approval is recorded for a freeze-map status change
- every freeze-in-C anchor remains blocked from a direct Zigux port claim
- the remaining same-lane work is maintenance-only truthfulness and blocker upkeep until one of the named reopen triggers fires

## Recorded gaps

The current lane state is:

- landed `phase15-indefinite-c-policy-note`
- landed `phase15-indefinite-c-policy-json-companion`
- landed `phase15-indefinite-c-policy-zig-replay`
- landed `phase15-indefinite-c-blocker-evidence-replay`
- landed `phase15-indefinite-c-lane-owner-alignment-replay`
- landed `phase15-indefinite-c-policy-roadmap-survey`
- blocked `phase15-deep-core-status-change-blocker`

This keeps the lane narrow. The missing work is not a new deep-core bridge, wrapper, or direct port. It is the continued maintenance of truthful stay-in-C evidence until the blocker posture changes.

## Non-goals

This survey does not claim:

- that the indefinite-C policy packet is missing from current `master`
- that any freeze-in-C anchor is ready for a direct Zigux port claim
- that an Architecture Council status-change approval has landed
- that the parity-scorecard lane, readiness-gate lane, or handoff lane should be reopened here
- any new deep-core Zig bridge, wrapper, or direct port starter

## Next bounded step

Keep this packet parked unless one of the named reopen triggers fires or the deep-core blocker posture changes, and if shared Phase 15 reminder surfaces drift again, refresh them so they continue to describe the landed indefinite-C packet as a maintenance-mode stay-in-C policy rather than a missing or reopened implementation lane.
