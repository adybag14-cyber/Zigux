# Phase 15 Freeze-Map Governance

This document records the bounded Phase 15 governance lane around `Documentation/zigux/freeze-map.md`.

## Status

- `PHASE15_LANE_KEY=P15-L04`
- `PHASE15_STATUS=governance_slice_landed`
- `PHASE15_SLICE=freeze-map-governance-blocker-ownership-sync`
- scope: the live freeze map, the existing dedicated Phase 15 manifest and test gate, and one bounded maintenance follow-up that keeps the root freeze-map note aligned with the already-landed parity-scorecard, review-process, indefinite-C policy, retained stay-in-C closeout, current blocker posture, explicit per-anchor blocker ownership, and the real current enforcement state on `master`
- survey provenance last refreshed against reviewed `master` head `d918be7ded6383c13cbd5eea4ca4aa4f3cdafee4`; later repo movement touching this freeze-map governance surface now requires a fresh bounded provenance refresh before this note should make a new current-`master` claim
- product boundary:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase15-freeze-map-governance.md`
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `Documentation/zigux/phase15-architecture-council-review-process.md`
  - `Documentation/zigux/phase15-indefinite-c-policy.md`
  - `Documentation/zigux/phase15-evidence-archives/`
  - `scripts/zigux/validate-phase15.py`
  - `zigux/tests/phase15_freeze_map_manifest.json`
  - `zigux/tests/phase15_freeze_map_governance.zig`
  - `zigux/tests/phase15_evidence_archive_templates.zig`
  - `zigux/tests/phase15_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The roadmap's Phase 15 work is about governance, not another burst of deep-core implementation. The live repo now carries much more than the original freeze-map starter: the parity scorecard, Architecture Council review-process note, retained stay-in-C closeout rule, reopen-trigger catalog, and indefinite-C policy note are all already landed.

That still leaves room for packet drift. The root freeze map already says that any lane touching a freeze anchor must keep owner, validation gate, and rollback owner explicit, and the parity scorecard already names those records per anchor. The freeze-map-specific packet, though, was still stopping at blocker names and status without restating the ownership inventory that reviewers need when this packet is read on its own.

The honest bounded step is to sync the freeze-map packet to that already-landed ownership truth while keeping the current blocker posture explicit and without widening into parity-scorecard maintenance or a neighboring Phase 15 packet.

The last reviewed state for this packet was steady rather than status-change-ready: the narrower freeze-map packet replayed locally at the reviewed governance head, the same deep-core blocker posture remained in place there, and the earlier docs-root summary alignment drift is now already closed by the dedicated readiness and handoff packets rather than remaining a freeze-map change.

## Roadmap versus repo reality

The roadmap and the reviewed repo state still agree on the Phase 15 deep-core freeze set.

- roadmap freeze-in-C anchors: `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, `net/core/skbuff.c`
- live `Documentation/zigux/freeze-map.md` freeze-in-C anchors: `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, `net/core/skbuff.c`
- roadmap study-only anchors: `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`
- live `Documentation/zigux/freeze-map.md` study-only anchors: `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`

At the last reviewed governance head, repo reality also still supported the same blocker posture rather than a status-change-ready one:

- `kernel/sched/core.c`: the Phase 15 scorecard still recorded `blocked_no_bounded_scheduler_seam`, and the repo still had no narrower scheduler seam packet or Architecture Council decision record
- `mm/page_alloc.c`: the Phase 15 scorecard still recorded `blocked_no_bounded_allocator_seam`, and the repo still had no narrower allocator seam packet or Architecture Council decision record
- `kernel/rcu/tree.c`: the existing `Documentation/zigux/phase14-rcu-tree-survey.md` packet still kept the follow-up wider than the allowed seam, and the Phase 15 scorecard still recorded `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`
- `net/core/skbuff.c`: the existing `Documentation/zigux/phase14-skbuff-bridge-survey.md` packet still kept the follow-up wider than the allowed packet-lifetime boundary, and the Phase 15 scorecard still recorded `blocked_packet_lifetime_boundary_still_too_wide`

That means the last reviewed comparison was stable: no roadmap freeze-map delta needed to be opened at that reviewed head, and no deep-core blocker had moved from governance-ready into status-change-ready there.

## Landed governance rules

- changes to the freeze or study lists require an explicit Architecture Council decision with written rationale
- any lane that touches a listed anchor must declare owner, phase, status bucket, validation gate, and rollback owner in a reviewable record
- direct Zig bridge or port claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry and the Architecture Council records why the status can change
- any reopen packet for a freeze-in-C anchor must state the rollback threshold that forces the anchor back to its blocked freeze posture if the decision record, parity scorecard evidence, benchmark notes, replay command, blocker disposition, or rollback owner stops being explicit
- any reopen packet for a freeze-in-C anchor must restate that the existing C implementation remains the product source of truth unless the Architecture Council approves a status change
- the stay-in-C policy says the C implementation remains the product source of truth, and ambiguous validation must keep the code in C with an explicit blocker
- a freeze-in-C review that closes without a status change must retain the blocker, record `retired_from_active_discussion`, and keep the documented reopen triggers attached to the evidence archive
- there is no silent exception path around the stay-in-C policy; only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review

## Current blocker posture

- `kernel/sched/core.c` was still blocked at the reviewed governance head because the repo had no bounded scheduler seam
- `mm/page_alloc.c` was still blocked at the reviewed governance head because the repo had no bounded allocator seam
- `kernel/rcu/tree.c` was still blocked at the reviewed governance head because the published Phase 14 follow-up was still wider than the allowed RCU seam
- `net/core/skbuff.c` was still blocked at the reviewed governance head because the published Phase 14 follow-up was still wider than the allowed packet-lifetime boundary
- no Architecture Council decision record currently claimed a freeze-map status change for any of those four anchors at the reviewed governance head
- the freeze-map anchor set was therefore unchanged at that reviewed `master` head

## Current blocker ownership

- `kernel/sched/core.c`: current lane owner `Architecture Council`; current validation gate `dedicated Phase 15 scorecard test and manifest replay, plus a future lane-local parity harness before any status change`; rollback owner `Architecture Council + PMO / Release Management`
- `mm/page_alloc.c`: current lane owner `Architecture Council`; current validation gate `dedicated Phase 15 scorecard test and manifest replay, plus a future lane-local parity harness before any status change`; rollback owner `Architecture Council + Validation and Perf Team`
- `kernel/rcu/tree.c`: current lane owner `ABI and Runtime Team`; current validation gate `dedicated Phase 15 scorecard test and manifest replay, existing Phase 14 survey evidence must stay green, and a future lane-local parity harness before any status change`; rollback owner `Architecture Council + ABI and Runtime Team`
- `net/core/skbuff.c`: current lane owner `Shared Subsystems Pod`; current validation gate `dedicated Phase 15 scorecard test and manifest replay, existing Phase 14 survey evidence must stay green, and a future lane-local parity harness before any status change`; rollback owner `Architecture Council + Shared Subsystems Pod`

These ownership records are not a new approval path. They restate the already-landed scorecard evidence inside the freeze-map packet so a blocker review cannot quietly lose its owner or rollback path while still appearing governance-complete.

## Recorded gaps

The current lane state is:

- landed `phase15-freeze-map-governance-doc`
- landed `phase15-freeze-map-governance-note`
- landed `phase15-build-gate`
- landed `phase15-make-target`
- landed `phase15-stay-in-c-closeout-sync`
- landed `phase15-governance-family-alignment`
- landed `phase15-governance-packet-drift-gate`
- landed `phase15-roadmap-vs-repo-reality-survey`
- landed `phase15-rollback-threshold-sync`
- landed `phase15-blocker-ownership-sync`
- blocked `phase15-deep-core-status-change-blocker`

This keeps the lane tight: Zigux now has a reviewable governance rule for the freeze map that matches the current roadmap freeze list, the current repo evidence packet family, the explicit rollback-threshold requirement already present at the root policy layer, the already-landed broader stay-in-C governance artifacts, and the current per-anchor owner plus rollback-owner inventory. What remains blocked is any deep-core status change, while the earlier docs-root summary drift is already closed in the dedicated readiness and handoff packets rather than remaining open inside this freeze-map slice.

## Non-goals

This slice does not claim:

- an Architecture Council roster, schedule, or approval workflow implementation
- any status change for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`
- any new deep-core Zig bridge or wrapper for a freeze-in-C anchor

## Gates

1. run the shared validator-first gate
- `python3 scripts/zigux/validate-phase15.py`
- `make -C zigux phase15-validate`

2. run the dedicated Phase 15 build
- `zig build test --build-file zigux/tests/phase15_build.zig`

3. run the convenience target
- `make -C zigux phase15`

## Current enforcement evidence

- last reviewed remote `master` head for this packet: `d918be7ded6383c13cbd5eea4ca4aa4f3cdafee4`; later repo movement now requires a fresh bounded provenance refresh before any new current-`master` enforcement claim
- the root policy was present and explicit at that reviewed head in `Documentation/zigux/freeze-map.md`, including the freeze-in-C list, study-only list, Architecture Council requirement, parity-scorecard requirement, explicit rollback-threshold language, retained stay-in-C closeout state, reopen-trigger language, the explicit source-of-truth reminder for reopened packets, and the no-silent-exception rule
- the review hook was present there in `Documentation/zigux/review-checklist.md`, which now asks whether freeze-map anchors carry parity-scorecard evidence or blocker state, decision-record links, retained-discussion state, reopen triggers, rollback-threshold language, and an explicit current lane owner for blocked evidence packets
- the shared review checklist now carried a dedicated freeze-map governance-packet drift gate, so edits to `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, or `Documentation/zigux/phase15-parity-scorecard.md` had to keep the rollback threshold, automatic return-to-blocked trigger, retained discussion state, reopen triggers, and the current maintenance-mode handoff aligned
- the shared validator-first governance gate was present there in `scripts/zigux/validate-phase15.py` and `zigux/Makefile`, so freeze-map maintenance edits kept one explicit pre-replay review boundary through `python3 scripts/zigux/validate-phase15.py` or `make -C zigux phase15-validate` before the wider `make -C zigux phase15` replay path
- the reserved evidence archive packet remained explicit through `Documentation/zigux/phase15-evidence-archives/` and `zigux/tests/phase15_evidence_archive_templates.zig`, so the per-anchor no-approval posture, retained discussion state, reopen-trigger catalog, and indefinite-C policy links stayed reviewable as concrete records instead of only shared prose
- the parity scorecard already carried the current per-anchor lane owner, validation gate, rollback owner, blocker disposition, and rollback threshold records, and this freeze-map packet now restated that owner inventory so the anchor-local blocker posture remained reviewable without a separate scorecard lookup
- the reviewed roadmap-versus-repo comparison remained stable: the freeze and study-only lists in `Documentation/zigux/freeze-map.md` still matched the roadmap, and the scorecard plus the existing Phase 14 RCU or skbuff survey packets still backed the same four deep-core blockers
- the dedicated local replay surface was present in `zigux/tests/phase15_build.zig` and `zigux/Makefile`, so a focused maintainer run could still use `zig build test --build-file zigux/tests/phase15_build.zig` or `make -C zigux phase15`
- the shared bootstrap workflow now invoked the Phase 15 gate through `Run Phase 15 governance tests`, so the current freeze-map governance bundle was no longer maintainer-run only at that reviewed head
- focused replay at reviewed `master` head `d918be7ded6383c13cbd5eea4ca4aa4f3cdafee4` showed the narrower freeze-map governance packet was runnable:
  - `zigux/tests/phase15_freeze_map_governance.zig` compiled and its `4/4` tests passed
  - `make -C zigux phase15` remained the same bounded shared replay path exposed through `zigux/Makefile`
- observed behavior at reviewed `master` head `d918be7ded6383c13cbd5eea4ca4aa4f3cdafee4`: the repo carried real freeze-map policy, manifests, scorecard, dedicated replay entrypoints, shared bootstrap workflow coverage for the current Phase 15 gate, one explicit checklist gate that kept the governance packet aligned during maintenance edits, and one explicit owner inventory that kept the blocker posture reviewable while the deep-core blocker posture remained unchanged

## Exact blocker record

- `freeze-map-policy-present`: yes
- `freeze-map-review-hook-present`: yes
- `phase15-validator-first-gate-present`: yes
- `phase15-local-entrypoint-present`: yes
- `phase15-shared-ci-enforcement-present`: yes
- `phase15-rollback-threshold-rule-present`: yes
- `phase15-blocker-ownership-present`: yes
- `phase15-neighboring-maintenance-drift`: `closed_docs_root_summary_alignment_landed_in_readiness_and_handoff_packets`
- `phase15-shared-bundle-green-claim`: `out_of_scope_for_this_freeze_map_packet`
- next repair step inside this lane family: leave the deep-core blocker posture parked here and wait for a later blocker-posture change or a new replay drift instead of reopening docs-root alignment work that is already landed in the readiness and handoff packets

## Next bounded step

Keep the Phase 15 governance lane in maintenance mode. The next honest action is to wait for one of the named reopen triggers, the current blocker ownership inventory to drift, or the deep-core blocker posture to change before opening another freeze-map governance slice.
