# Phase 15 Parity Scorecard Verification Survey

This document records the bounded Phase 15 governance lane around verifying the current parity-scorecard metrics, evidence, and reporting surfaces on `master`.

## Status

- `PHASE15_LANE_KEY=P15-L11`
- `PHASE15_STATUS=parity_scorecard_verification_survey`
- `PHASE15_SLICE=parity-metrics-evidence-reporting-verify`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- scope: one survey-grade note that compares the live Phase 15 parity-scorecard note, the machine-readable scorecard JSON, and the surrounding reporting packet without widening into new deep-core implementation claims
- survey provenance refreshed against dated current-master readback marker `current-master-readback-2026-05-11` on 2026-05-11
- product boundary:
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `zigux/tests/phase15_parity_scorecard.json`
  - `Documentation/zigux/phase15-handoff-next-steps-survey.md`
  - `zigux/tests/phase15_handoff_next_steps_manifest.json`
  - `scripts/zigux/validate-phase15.py`
  - `scripts/zigux/check-phase15-scripts-readme-alignment.py`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/phase15-parity-scorecard-survey.md`

## Why this survey exists

The roadmap's Phase 15 packet requires a parity scorecard so the frozen deep-core anchors can be tracked with bounded ownership, blocker posture, and replay evidence.

Current `master` does carry that scorecard packet now, but the surrounding reminders do not all describe it truthfully. The honest same-lane question is no longer whether Zigux lacks a parity scorecard. It is whether the current scorecard note, the machine-readable JSON companion, and the broader reporting packet still agree on what has actually landed.

## Current master readback

The dated 2026-05-11 readback shows these parity-scorecard surfaces present on `master`:

- `Documentation/zigux/phase15-parity-scorecard.md`
- `zigux/tests/phase15_parity_scorecard.json`

The current note and JSON agree on the following machine-readable anchor facts:

- surveyed head marker: `current-master-readback-2026-05-11`
- active freeze-in-C anchor count: `4`
- blocked status-change anchor count: `4`
- anchor coverage: `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c`
- per-anchor ownership, rollback owner, decision-record path, benchmark-notes status, replay command, and blocker-disposition evidence are all present in the current JSON and mirrored in the note

The current note also carries two aggregate metrics that are not mirrored in the JSON payload yet:

- study-only anchors tracked outside this scorecard: `2`
- Architecture Council approvals recorded for status change: `0`

## Current reporting gap

The current same-packet gap is not a missing scorecard note.

The real gap is that several surrounding Phase 15 reporting surfaces still speak as if the machine-checked parity-scorecard companion is a dedicated Zig replay file:

- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/validate-phase15.py`
- `scripts/zigux/check-phase15-scripts-readme-alignment.py`

Those surfaces currently name `zigux/tests/phase15_parity_scorecard.zig`, while the live machine-readable parity-scorecard surface that is actually present on `master` is `zigux/tests/phase15_parity_scorecard.json`.

That means the current reporting packet still mixes two different stories:

- the landed scorecard note and JSON say the parity-accounting packet already exists
- several shared reminders still point at a missing Zig replay path instead of the shipped JSON evidence surface

## Honest current posture

The honest bounded Phase 15 statement on current `master` is:

- the parity-scorecard note is landed
- the machine-readable parity-scorecard JSON is landed
- two core aggregate counts are aligned between the note and the JSON
- two note-level aggregate metrics are not yet mirrored in the JSON payload
- the broader Phase 15 reporting packet still needs a truthfulness refresh so shared reminders stop naming `zigux/tests/phase15_parity_scorecard.zig` as if that file were the shipped scorecard companion
- no Architecture Council approval is recorded for any freeze-map status change
- every frozen anchor remains blocked from a direct Zigux port claim

## Recorded gaps

The current lane state is:

- landed `phase15-parity-scorecard-doc`
- landed `phase15-parity-scorecard-json`
- landed `phase15-parity-scorecard-anchor-evidence`
- landed `phase15-parity-scorecard-core-aggregate-counts`
- open `phase15-parity-scorecard-json-aggregate-metric-sync`
- open `phase15-parity-scorecard-reporting-surface-sync`
- open `phase15-parity-scorecard-validator-file-inventory-sync`
- open `phase15-parity-scorecard-optional-zig-replay-followup`

This keeps the lane narrow. The missing work is not a new deep-core implementation step. It is the truthfulness follow-through that makes the current parity packet and its shared reminders describe the same live repo surface.

## Non-goals

This survey does not claim:

- that the parity-scorecard packet is missing from current `master`
- that a dedicated `zigux/tests/phase15_parity_scorecard.zig` replay currently exists on `master`
- that the broader Phase 15 build packet is fully reconciled in this lane
- any status change for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`
- any new deep-core Zig bridge, wrapper, or direct port starter

## Next bounded step

Realign the shared Phase 15 validator, docs-root, scripts-root, tests-root, checklist, and handoff reminders so they point at `zigux/tests/phase15_parity_scorecard.json` as the shipped machine-readable scorecard companion, then decide in a separate bounded follow-up whether the two note-only aggregate metrics should also be promoted into the JSON payload or whether a dedicated Zig replay should actually be landed.
