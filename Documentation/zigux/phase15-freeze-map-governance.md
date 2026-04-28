# Phase 15 Freeze-Map Governance

This document records the bounded Phase 15 governance lane around `Documentation/zigux/freeze-map.md`.

## Status

- `PHASE15_STATUS=governance_slice_landed`
- `PHASE15_SLICE=freeze-map-governance-enforcement-refresh`
- scope: the live freeze map, the existing dedicated Phase 15 manifest and test gate, and one bounded maintenance follow-up that keeps the root freeze-map note aligned with the already-landed parity-scorecard, review-process, indefinite-C policy, retained stay-in-C closeout, current blocker posture, and the real current enforcement state on `master`
- survey provenance refreshed against verified `master` head `177c4179368f23f670c6e68678fcde4869199700`
- product boundary:
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase15-freeze-map-governance.md`
  - `Documentation/zigux/phase15-parity-scorecard.md`
  - `Documentation/zigux/phase15-architecture-council-review-process.md`
  - `Documentation/zigux/phase15-indefinite-c-policy.md`
  - `zigux/tests/phase15_freeze_map_manifest.json`
  - `zigux/tests/phase15_freeze_map_governance.zig`
  - `zigux/tests/phase15_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The roadmap's Phase 15 work is about governance, not another burst of deep-core implementation. The live repo now carries much more than the original freeze-map starter: the parity scorecard, Architecture Council review-process note, retained stay-in-C closeout rule, reopen-trigger catalog, and indefinite-C policy note are all already landed.

That still leaves room for packet drift. This focused note and manifest were carrying an older maintenance snapshot, so the honest bounded step is to refresh the freeze-map-specific lane record to the current `master` head and keep the current blocker posture explicit without widening into neighboring Phase 15 packet ownership.

The real current state is steady rather than broken: the narrower freeze-map packet still replays locally, and the broader shared `phase15_build.zig` governance bundle now passes on current `master` while the same deep-core blocker posture remains in place.

## Roadmap versus repo reality

The roadmap and the live repo still agree on the Phase 15 deep-core freeze set.

- roadmap freeze-in-C anchors: `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, `net/core/skbuff.c`
- live `Documentation/zigux/freeze-map.md` freeze-in-C anchors: `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, `net/core/skbuff.c`
- roadmap study-only anchors: `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`
- live `Documentation/zigux/freeze-map.md` study-only anchors: `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`

Current repo reality also still supports the same blocker posture rather than a status-change-ready one:

- `kernel/sched/core.c`: the Phase 15 scorecard still records `blocked_no_bounded_scheduler_seam`, and the repo still has no narrower scheduler seam packet or Architecture Council decision record
- `mm/page_alloc.c`: the Phase 15 scorecard still records `blocked_no_bounded_allocator_seam`, and the repo still has no narrower allocator seam packet or Architecture Council decision record
- `kernel/rcu/tree.c`: the existing `Documentation/zigux/phase14-rcu-tree-survey.md` packet still keeps the follow-up wider than the allowed seam, and the Phase 15 scorecard still records `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`
- `net/core/skbuff.c`: the existing `Documentation/zigux/phase14-skbuff-bridge-survey.md` packet still keeps the follow-up wider than the allowed packet-lifetime boundary, and the Phase 15 scorecard still records `blocked_packet_lifetime_boundary_still_too_wide`

That means the honest current comparison is stable: no roadmap freeze-map delta needs to be opened, and no deep-core blocker has moved from governance-ready into status-change-ready.

## Landed governance rules

- changes to the freeze or study lists require an explicit Architecture Council decision with written rationale
- any lane that touches a listed anchor must declare owner, phase, status bucket, validation gate, and rollback owner in a reviewable record
- direct Zig bridge or port claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry and the Architecture Council records why the status can change
- the stay-in-C policy says the C implementation remains the product source of truth, and ambiguous validation must keep the code in C with an explicit blocker
- a freeze-in-C review that closes without a status change must retain the blocker, record `retired_from_active_discussion`, and keep the documented reopen triggers attached to the evidence archive
- there is no silent exception path around the stay-in-C policy; only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review

## Current blocker posture

- `kernel/sched/core.c` remains blocked because the repo still has no bounded scheduler seam
- `mm/page_alloc.c` remains blocked because the repo still has no bounded allocator seam
- `kernel/rcu/tree.c` remains blocked because the published Phase 14 follow-up is still wider than the allowed RCU seam
- `net/core/skbuff.c` remains blocked because the published Phase 14 follow-up is still wider than the allowed packet-lifetime boundary
- no Architecture Council decision record currently claims a freeze-map status change for any of those four anchors
- the freeze-map anchor set therefore stays unchanged on current `master`

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
- blocked `phase15-deep-core-status-change-blocker`

This keeps the lane tight: Zigux now has a reviewable governance rule for the freeze map that matches the current roadmap freeze list, the current repo evidence packet family, and the already-landed broader stay-in-C governance artifacts. What remains blocked is any deep-core status change, and the wider shared Phase 15 replay drift still belongs to neighboring maintenance packets rather than a freeze-map status change.

## Non-goals

This slice does not claim:

- an Architecture Council roster, schedule, or approval workflow implementation
- any status change for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`
- any new deep-core Zig bridge or wrapper for a freeze-in-C anchor

## Gates

1. run the dedicated Phase 15 build
- `zig build test --build-file zigux/tests/phase15_build.zig`

2. run the convenience target
- `make -C zigux phase15`

## Current enforcement evidence

- verified remote `master` head for this check: `177c4179368f23f670c6e68678fcde4869199700`
- the root policy is present and explicit in `Documentation/zigux/freeze-map.md`, including the freeze-in-C list, study-only list, Architecture Council requirement, parity-scorecard requirement, retained stay-in-C closeout state, reopen-trigger language, and the no-silent-exception rule
- the review hook is present in `Documentation/zigux/review-checklist.md`, which now asks whether freeze-map anchors carry parity-scorecard evidence or blocker state, decision-record links, retained-discussion state, reopen triggers, and an explicit current lane owner for blocked evidence packets
- the shared review checklist now carries a dedicated freeze-map governance-packet drift gate, so edits to `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, or `Documentation/zigux/phase15-parity-scorecard.md` must keep the automatic return-to-blocked trigger, retained discussion state, reopen triggers, and the current maintenance-mode handoff aligned
- the current roadmap-versus-repo comparison remains stable: the freeze and study-only lists in `Documentation/zigux/freeze-map.md` still match the roadmap, and the scorecard plus the existing Phase 14 RCU or skbuff survey packets still back the same four deep-core blockers
- the dedicated local replay surface is present in `zigux/tests/phase15_build.zig` and `zigux/Makefile`, so a focused maintainer run can still use `zig build test --build-file zigux/tests/phase15_build.zig` or `make -C zigux phase15`
- the shared bootstrap workflow now invokes the Phase 15 gate through `Run Phase 15 governance tests`, so the current freeze-map governance bundle is no longer maintainer-run only
- focused replay against current `master` shows both the narrower freeze-map governance packet and the broader shared Phase 15 bundle are runnable:
  - `zigux/tests/phase15_freeze_map_governance.zig` compiled and its `4/4` tests passed
  - `zig build test --build-file zigux/tests/phase15_build.zig --summary all` now passes on current `master` with `13/13` build steps succeeded and `16/16` tests passed
  - `make -C zigux phase15` remains the same bounded shared replay path exposed through `zigux/Makefile`
- current observed behavior on live `master`: the repo carries real freeze-map policy, manifests, scorecard, dedicated replay entrypoints, shared bootstrap workflow coverage for the current Phase 15 gate, one explicit checklist gate that keeps the governance packet aligned during maintenance edits, and the broader shared Phase 15 governance bundle is green while the deep-core blocker posture remains unchanged

## Exact blocker record

- `freeze-map-policy-present`: yes
- `freeze-map-review-hook-present`: yes
- `phase15-local-entrypoint-present`: yes
- `phase15-shared-ci-enforcement-present`: yes
- `phase15-build-clean-on-current-master`: yes
- `phase15-build-failure-cause`: `none`
- next repair step inside this lane family: leave the deep-core blocker posture parked here until one of the named reopen triggers fits again or the blocker posture changes

## Next bounded step

Keep the Phase 15 governance lane in maintenance mode. The next honest action is to wait for one of the named reopen triggers or the deep-core blocker posture to change before opening another freeze-map governance slice.
