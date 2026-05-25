# Phase 15 Architecture Council Approver Matrix

This note records the bounded Phase 15 approver matrix for freeze-in-C anchors that can only move through an explicit Architecture Council reviewable record.

## Status

- `PHASE15_STATUS=architecture_council_approver_matrix_landed`
- `PHASE15_LANE_KEY=P15-L17`
- `PHASE15_SLICE=required-approver-and-rollback-owner-matrix`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-24`
- role: keep the required approver set, rollback owner, blocker posture, and evidence archive path explicit in one reviewable owner note so adjacent Phase 15 summaries do not have to restate those Architecture Council fields from memory

## Why this note exists

The current Phase 15 packet already keeps required approver sets inside the freeze-map governance note, the parity scorecard, and the review-process template. That is enough to preserve truthfulness, but it is not yet a compact Architecture Council lookup surface.

This note closes that narrow governance gap. It keeps the per-anchor approver and rollback inventory explicit in one place without implying a status change, a deep-core Zig bridge, or any Architecture Council approval for a freeze-map status change.

Use this note together with `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, and `Documentation/zigux/phase15-parity-scorecard.md`.

## Matrix Rules

- this is a governance lookup note, not an approval record
- every row stays in `freeze_in_c` until an Architecture Council decision record says otherwise
- the required approver set and rollback owner here must match the active freeze-map governance packet
- study-only anchors stay outside this matrix until the freeze map changes their status bucket

## Freeze-In-C Approver Matrix

### `kernel/sched/core.c`

- lane owner: `Architecture Council`
- phase: `Phase 15`
- current status bucket: `freeze_in_c`
- required approver set: `Architecture Council + PMO / Release Management`
- rollback owner: `Architecture Council + PMO / Release Management`
- current blocker: `blocked_no_bounded_scheduler_seam`
- evidence archive path: `Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md`
- replay command: `zig test zigux/tests/phase15_freeze_map_governance.zig`

### `mm/page_alloc.c`

- lane owner: `Architecture Council`
- phase: `Phase 15`
- current status bucket: `freeze_in_c`
- required approver set: `Architecture Council + Validation and Perf Team`
- rollback owner: `Architecture Council + Validation and Perf Team`
- current blocker: `blocked_no_bounded_allocator_seam`
- evidence archive path: `Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md`
- replay command: `zig test zigux/tests/phase15_freeze_map_governance.zig`

### `kernel/rcu/tree.c`

- lane owner: `ABI and Runtime Team`
- phase: `Phase 15`
- current status bucket: `freeze_in_c`
- required approver set: `Architecture Council + ABI and Runtime Team`
- rollback owner: `Architecture Council + ABI and Runtime Team`
- current blocker: `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`
- evidence archive path: `Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md`
- replay command: `zig test zigux/tests/phase15_freeze_map_governance.zig`

### `net/core/skbuff.c`

- lane owner: `Shared Subsystems Pod`
- phase: `Phase 15`
- current status bucket: `freeze_in_c`
- required approver set: `Architecture Council + Shared Subsystems Pod`
- rollback owner: `Architecture Council + Shared Subsystems Pod`
- current blocker: `blocked_packet_lifetime_boundary_still_too_wide`
- evidence archive path: `Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md`
- replay command: `zig test zigux/tests/phase15_freeze_map_governance.zig`

## Study-Only Boundary

`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay outside this matrix because the current roadmap still treats them as study-only anchors rather than freeze-in-C status-review rows. Route those anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` unless the freeze map changes first.

## Non-goals

This note does not claim:

- an Architecture Council approval for any deep-core status change
- a direct Zig bridge or delivery-ready seam for any freeze-in-C anchor
- that study-only anchors have entered a freeze-in-C status-review packet

## Next bounded step

Keep this note parked unless one anchor's required approver set, rollback owner, blocker posture, or evidence archive path changes in the live freeze-map governance packet, or a shared reminder surface starts undercounting the Architecture Council approver inventory.
