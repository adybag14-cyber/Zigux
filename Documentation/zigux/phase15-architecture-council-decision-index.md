# Phase 15 Architecture Council Decision Index

This note records the bounded Phase 15 index for Architecture Council decision records that affect freeze-map anchors.

## Status

- `PHASE15_STATUS=architecture_council_decision_index_landed`
- `PHASE15_LANE_KEY=P15-L09`
- `PHASE15_SLICE=decision-record-inventory`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-27`
- `PHASE15_PACKET_VALIDATION_GATE=python3 scripts/zigux/check-phase15-architecture-council-decision-index.py`
- `PHASE15_PACKET_ROLLBACK_OWNER=Architecture Council`
- role: keep a single reviewable inventory of Architecture Council decisions, explicit zero-decision posture, future record-link rules, and the dedicated decision-index manifest/checker/replay trio beside the freeze-map governance packet, the review-process owner note, and the decision-record template without implying approval where none exists

## Why this slice exists

The Phase 15 governance packet already carries the freeze map, the review-process owner note, the decision-record template, the parity scorecard, and the indefinite-C policy companion.

What it did not have was one bounded owner note that answers the simple product question, "which Architecture Council decisions are actually recorded on current `master`?"

This index closes that gap without widening Phase 15 into implementation work. It keeps decision inventory, zero-decision posture, future record-link rules, and the dedicated decision-index manifest/checker/replay trio explicit so later reminder surfaces do not have to infer them indirectly from the freeze map, the review-process note, or the parity scorecard.

## Current decision inventory

- approved status-bucket changes recorded on current `master`: none
- stay-in-C closeout decision records recorded on current `master`: none
- no freeze-map anchor has an Architecture Council approval for a status change on current `master`
- the freeze map, parity scorecard, and review-process packet therefore remain blocker-accounting and governance truthfulness evidence rather than approval evidence

## Index rules

- every future Architecture Council decision record for a freeze-map anchor must be linked here with decision record ID, exact Linux anchor path, review outcome, evidence archive path, surveyed commit marker, and next bounded step
- every linked record must also route back through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, and `Documentation/zigux/phase15-parity-scorecard.md`
- if no reviewable Architecture Council decision record exists yet, keep this note at an explicit zero-decision inventory instead of implying approval by omission
- if a freeze-in-C anchor changes status bucket, update this note in the same bounded change as the linked decision record and the freeze-map governance packet
- `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay outside this index until the freeze map changes, because they remain study-only anchors rather than freeze-in-C status-review records

## Future record format

Use one flat entry per landed Architecture Council decision record:

- decision record ID:
- exact Linux anchor path:
- review outcome:
- evidence archive path:
- surveyed commit marker:
- next bounded step:

## Related owner notes

- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `zigux/tests/phase15_architecture_council_decision_index_manifest.json`
- `zigux/tests/phase15_architecture_council_decision_index.zig`
- `scripts/zigux/check-phase15-architecture-council-decision-index.py`

## Non-goals

This note does not claim:

- an Architecture Council approval for any freeze-map status change
- a stay-in-C closeout record that is not linked by path
- a status-review path for `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` while they remain study-only anchors
- a deep-core Zig bridge or port-readiness decision

## Next bounded step

Keep this note parked unless the first reviewable Architecture Council decision record lands, a freeze-map anchor changes status bucket, the dedicated decision-index manifest/checker/replay trio drifts away from this note, or the review-process owner note and decision-record template drift enough that the inventory or zero-decision wording needs a truthfulness refresh.
