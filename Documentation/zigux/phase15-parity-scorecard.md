# Phase 15 Parity Scorecard

This note records the bounded Phase 15 parity-accounting surface for the freeze-in-C anchors that remain blocked from a direct Zigux status change.

## Status

- `PHASE15_STATUS=parity_scorecard_slice_landed`
- `PHASE15_LANE_KEY=P15-L03`
- `PHASE15_SLICE=parity-scorecard-baseline`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- `PHASE15_SCORECARD_ROLE=blocked_posture_accounting_not_port_readiness`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-19`
- no Architecture Council approval is currently recorded for a freeze-map status change
- the scorecard remains an honest blocker-accounting packet, not a port-readiness claim

## Purpose

The roadmap requires a parity scorecard so the mixed-language end state stays explicit about what is still blocked, who owns the blocker posture, and what evidence would have to move before a freeze-map anchor could leave the current stay-in-C bucket.

This scorecard does not claim that a deep-core anchor is ready for a direct Zigux port. It exists to keep the freeze map, the review-process note, and the indefinite-C policy aligned around the same blocked posture.

The scorecard now also carries the same phase, status-bucket, required-approver-set, and validation-gate summary fields that the freeze-map governance packet expects from reviewable Phase 15 records, so the human-readable scorecard no longer underreports those core Architecture Council handoff fields.

For `net/core/skbuff.c`, that evidence bundle now keeps both the packet-local Phase 14 survey note and the shared Phase 14 traceability note explicit, because the live freeze-map governance packet uses both surfaces to keep the blocked ownership posture reviewable.

That means the current parity-tracking gap is maintenance-only: keep the scorecard's lane identity, surveyed-master provenance, current reminder-route wording, and replay-backed evidence packet current so the roadmap requirement stays explicitly satisfied instead of drifting into stale metadata.

## Aggregate Metrics

- active freeze-in-C anchor count: `4`
- blocked status-change anchor count: `4`
- anchors blocked entirely within Phase 15 governance evidence: `2`
- Phase 14 coupled blocker anchor count: `2`
- anchors still blocked on prior-phase bridge evidence: `2`
- study-only anchors tracked outside this scorecard: `2`
- Architecture Council approvals recorded for status change: `0`

## Current reminder route

- the current directly materialized reminder route exists through `python3 scripts/zigux/check-phase15-docs-readme-alignment.py`, `python3 scripts/zigux/check-phase15-scripts-readme-alignment.py`, `python3 scripts/zigux/check-phase15-review-process-handoff.py`, `python3 scripts/zigux/check-phase15-shared-summary-gap.py`, and `zig test zigux/tests/phase15_parity_scorecard.zig`
- anchor-level blocker evidence stays reviewable through `zig test zigux/tests/phase15_freeze_map_governance.zig`
- the broader validator-first and shared-build route wording through `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_build.zig`, `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` remains repo-reality gap vocabulary on current `master`, not shipped evidence

## Anchor Scorecard

### `kernel/sched/core.c`
- lane owner: `Architecture Council`
- phase: `Phase 15`
- current status bucket: `freeze_in_c`
- required approver set: `Architecture Council + PMO / Release Management`
- validation gate summary: `Phase 15 parity scorecard plus Architecture Council reopen record`
- rollback owner: `Architecture Council + PMO / Release Management`
- current blocker: `blocked_no_bounded_scheduler_seam`
- decision record path: `Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md`
- linked evidence: `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`
- benchmark-notes status: `pending_until_bounded_scheduler_seam_exists`
- replay command: `zig test zigux/tests/phase15_freeze_map_governance.zig`
- next honest posture: keep the anchor frozen until a bounded scheduler seam exists and a reopen trigger is recorded

### `mm/page_alloc.c`
- lane owner: `Architecture Council`
- phase: `Phase 15`
- current status bucket: `freeze_in_c`
- required approver set: `Architecture Council + Validation and Perf Team`
- validation gate summary: `Phase 15 parity scorecard plus Architecture Council reopen record`
- rollback owner: `Architecture Council + Validation and Perf Team`
- current blocker: `blocked_no_bounded_allocator_seam`
- decision record path: `Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md`
- linked evidence: `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`
- benchmark-notes status: `pending_until_bounded_allocator_seam_exists`
- replay command: `zig test zigux/tests/phase15_freeze_map_governance.zig`
- next honest posture: keep the anchor frozen until a bounded allocator seam exists and a reopen trigger is recorded

### `kernel/rcu/tree.c`
- lane owner: `ABI and Runtime Team`
- phase: `Phase 15`
- current status bucket: `freeze_in_c`
- required approver set: `Architecture Council + ABI and Runtime Team`
- validation gate summary: `Phase 15 parity scorecard plus Architecture Council reopen record`
- rollback owner: `Architecture Council + ABI and Runtime Team`
- current blocker: `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`
- decision record path: `Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md`
- linked evidence: `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase14-rcu-tree-survey.md`
- benchmark-notes status: `pending_until_rcu_followup_is_narrower_than_freeze_boundary`
- replay command: `zig test zigux/tests/phase15_freeze_map_governance.zig`
- next honest posture: keep the anchor frozen until a narrower-than-freeze RCU follow-up exists and a reopen trigger is recorded

### `net/core/skbuff.c`
- lane owner: `Shared Subsystems Pod`
- phase: `Phase 15`
- current status bucket: `freeze_in_c`
- required approver set: `Architecture Council + Shared Subsystems Pod`
- validation gate summary: `Phase 15 parity scorecard plus Architecture Council reopen record`
- rollback owner: `Architecture Council + Shared Subsystems Pod`
- current blocker: `blocked_packet_lifetime_boundary_still_too_wide`
- decision record path: `Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md`
- linked evidence: `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase14-skbuff-bridge-survey.md`, `Documentation/zigux/phase14-core-boundary-traceability.md`
- benchmark-notes status: `pending_until_skbuff_followup_is_narrower_than_lifetime_boundary`
- replay command: `zig test zigux/tests/phase15_freeze_map_governance.zig`
- next honest posture: keep the anchor frozen until a narrower-than-lifetime skbuff follow-up exists and a reopen trigger is recorded

## Accounting Rules

- every scorecard row must keep the lane owner, phase, current status bucket, required approver set, validation gate summary, rollback owner, current blocker, evidence archive path, benchmark-notes status, and replay command explicit
- if the evidence becomes stale or contradictory, the scorecard must keep the anchor blocked until the review-process packet records a fresh dated readback or reopen trigger
- if a future lane wants a status change, it must update this scorecard together with `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, and `Documentation/zigux/phase15-architecture-council-review-process.md`
- study-only anchors remain outside this scorecard until a lane asks for a status-bucket review

## Non-goals

This scorecard does not claim:

- Architecture Council approval for any direct Zigux deep-core port
- parity closure for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`
- a broader implementation roadmap beyond the current blocker-accounting packet

## Gates

1. run the current directly materialized reminder route
   - `python3 scripts/zigux/check-phase15-docs-readme-alignment.py`
   - `python3 scripts/zigux/check-phase15-scripts-readme-alignment.py`
   - `python3 scripts/zigux/check-phase15-review-process-handoff.py`
   - `python3 scripts/zigux/check-phase15-shared-summary-gap.py`
2. run the dedicated parity scorecard replay
   - `zig test zigux/tests/phase15_parity_scorecard.zig`
3. keep the broader validator-first and shared-build wording gap-tracked until direct reads recover it
   - `scripts/zigux/validate-phase15.py`
   - `zigux/tests/phase15_build.zig`
   - `make -C zigux phase15-validate`
   - `make -C zigux phase15-test`
   - `make -C zigux phase15`

## Next bounded step

Keep the scorecard parked until one of the named reopen triggers fits the evidence, the blocker posture changes, or the direct reminder-route wording drifts enough that the aggregate metrics or anchor records need another truthfulness refresh.
