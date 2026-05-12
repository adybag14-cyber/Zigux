# Phase 15 Indefinite-C Policy Survey

This document records the bounded Phase 15 governance lane for comparing the current indefinite-C policy packet on `master` against the roadmap requirement for a policy covering code that remains in C indefinitely.

## Status

- `PHASE15_LANE_KEY=P15-L13`
- `PHASE15_STATUS=indefinite_c_policy_survey`
- `PHASE15_SLICE=indefinite-c-policy-gap-vs-roadmap`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- survey provenance refreshed against dated current-master readback marker `current-master-readback-2026-05-12` on 2026-05-12
- scope: one survey-grade note that compares the live indefinite-C policy note, its machine-readable JSON companion, the dedicated Zig replay, the narrower blocker-evidence pair, and the surrounding Phase 15 governance reminders without widening into any deep-core status-change claim
- product boundary:
  - `Documentation/zigux/phase15-indefinite-c-policy.md`
  - `zigux/tests/phase15_indefinite_c_policy.json`
  - `zigux/tests/phase15_indefinite_c_policy.zig`
  - `zigux/tests/phase15_indefinite_c_blocker_evidence.zig`
  - `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase15-governance-lane-sequencing.md`
  - `Documentation/zigux/phase15-handoff-next-steps-survey.md`
  - `Documentation/zigux/phase15-readiness-gate-survey.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
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

The dated 2026-05-12 readback shows that the indefinite-C policy requirement itself is already satisfied on `master` through:

- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `zigux/tests/phase15_indefinite_c_policy.json`
- `zigux/tests/phase15_indefinite_c_policy.zig`

The current policy packet also keeps the two narrower same-family replays explicit:

- `zigux/tests/phase15_indefinite_c_blocker_evidence.zig`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`

The dedicated policy packet itself now records packet-local lane key `P15-L16` and its own exact surveyed-commit field, so this survey lane stays distinct from the landed policy packet instead of reusing packet-local ownership.

## Current packet agreement

The landed indefinite-C note, JSON companion, and Zig replay agree on these core facts:

- the roadmap requirement is `policy for code that remains in C indefinitely`
- the governed freeze-in-C anchors are `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c`
- the dedicated policy packet keeps packet-local lane key `P15-L16` while this note stays the survey lane `P15-L13`
- the existing C implementation remains the product source of truth for the current plan horizon
- there is no silent exception path around the stay-in-C posture
- the only allowed reopen path is an Architecture Council request with fresh linked evidence
- the named reopen-trigger catalog remains `narrower_followup_answers_blocker`, `evidence_packet_stale_or_contradictory`, and `ownership_or_validation_changed`
- the remaining blocker is still `phase15-deep-core-status-change-blocker`

The broader governance reminders also keep that same maintenance-mode posture explicit:

- `Documentation/zigux/freeze-map.md` keeps the freeze-in-C rule and the no-silent-exception language explicit
- `Documentation/zigux/phase15-governance-lane-sequencing.md` keeps the anti-overlap split explicit so shared-summary follow-up does not consume this policy lane
- `Documentation/zigux/phase15-handoff-next-steps-survey.md` treats the indefinite-C note as a landed member of the parked governance family
- `Documentation/zigux/phase15-readiness-gate-survey.md` keeps the no-approval-yet posture explicit for the whole Phase 15 packet
- `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md` already keep the landed indefinite-C packet visible from the shared summaries instead of understating it as missing policy work
- `scripts/zigux/validate-phase15.py` requires the indefinite-C note, the JSON companion, and the shared replay routes before Phase 15 validation can pass
- `scripts/zigux/README.md` and `zigux/tests/README.md` both name the indefinite-C packet as part of the shipped Phase 15 maintenance surface

## Current gap

The current same-lane gap is not a missing indefinite-C policy packet.

The real gap was narrower: this survey note had drifted behind current packet state by still carrying the older dated readback marker from 2026-05-11 and a gap list that no longer matched the live policy manifest after the packet-local field-sync follow-up landed.

Without that refresh, neighboring Phase 15 work could too easily collapse back into two unhelpful stories:

- incorrectly implying that the roadmap-required indefinite-C policy is still absent from `master`
- incorrectly treating the landed policy packet as if it had already moved beyond the current no-approval-yet blocker posture while also naming stale or non-manifest gap labels

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
- landed `phase15-indefinite-c-policy-manifest`
- landed `phase15-indefinite-c-policy-test`
- landed `phase15-build-gate-indefinite-c-policy`
- landed `phase15-indefinite-c-field-sync-followup`
- blocked `phase15-deep-core-status-change-blocker`

The blocker-evidence and lane-owner-alignment Zig replays remain the companion review surfaces beside that landed packet rather than separate additional gap IDs inside the policy manifest.

This keeps the lane narrow. The missing work is not a new deep-core bridge, wrapper, or direct port. It is the continued maintenance of truthful stay-in-C evidence until the blocker posture changes.

## Non-goals

This survey does not claim:

- that the indefinite-C policy packet is missing from current `master`
- that any freeze-in-C anchor is ready for a direct Zigux port claim
- that an Architecture Council status-change approval has landed
- that the parity-scorecard lane, readiness-gate lane, handoff lane, or shared-summary lane should be reopened here
- any new deep-core Zig bridge, wrapper, or direct port starter

## Next bounded step

Keep this packet parked unless one of the named reopen triggers fires or the deep-core blocker posture changes. If this survey reopens first, reread `Documentation/zigux/phase15-indefinite-c-policy.md`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, and `Documentation/zigux/phase15-handoff-next-steps-survey.md` together before touching any shared-summary, parity-scorecard, or freeze-map lane.
