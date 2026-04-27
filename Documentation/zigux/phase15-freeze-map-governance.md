# Phase 15 Freeze-Map Governance

This document records the bounded Phase 15 governance lane around `Documentation/zigux/freeze-map.md`.

## Status

- `PHASE15_STATUS=governance_slice_landed`
- `PHASE15_SLICE=freeze-map-governance-enforcement-refresh`
- scope: the live freeze map, the existing dedicated Phase 15 manifest and test gate, and one bounded maintenance follow-up that keeps the root freeze-map note aligned with the already-landed parity-scorecard, review-process, indefinite-C policy, retained stay-in-C closeout, current blocker posture, and the real current enforcement state on `master`
- survey provenance refreshed against verified `master` head `783e573845f21769925870e53a591e48878bb7f0`
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

That makes the freeze-map governance slice slightly stale again. Its focused note and manifest still describe an older maintenance snapshot where the dedicated Phase 15 build was blocked by truncated governance tests, even though current `master` now ships a working local Phase 15 governance bundle and the shared bootstrap workflow now replays that bundle too.

The honest bounded step is therefore maintenance, not expansion: refresh the freeze-map-specific lane record so it matches current repo reality, and keep the current blocker posture explicit while the central policy note carries the same retained stay-in-C closeout and reopen posture as the later governance artifacts.

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
- the freeze-map anchor set therefore stays unchanged on current `master`

## Recorded gaps

The current lane state is:

- landed `phase15-freeze-map-governance-doc`
- landed `phase15-freeze-map-governance-note`
- landed `phase15-build-gate`
- landed `phase15-make-target`
- landed `phase15-stay-in-c-closeout-sync`
- landed `phase15-governance-family-alignment`
- blocked `phase15-deep-core-status-change-blocker`

This keeps the lane tight: Zigux now has a reviewable and runnable governance rule for the freeze map that matches the current stay-in-C policy family and the already-landed broader governance artifacts. What remains blocked is any deep-core status change, not the governance scaffolding itself.

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

- verified remote `master` head for this check: `2521496aeecede51ed8d7d81820b9cf70a527ceb`
- the root policy is present and explicit in `Documentation/zigux/freeze-map.md`, including the freeze-in-C list, study-only list, Architecture Council requirement, parity-scorecard requirement, retained stay-in-C closeout state, reopen-trigger language, and the no-silent-exception rule
- the review hook is present in `Documentation/zigux/review-checklist.md`, which now asks whether freeze-map anchors carry parity-scorecard evidence or blocker state, decision-record links, retained-discussion state, reopen triggers, and an explicit current lane owner for blocked evidence packets
- the dedicated local replay surface is present in `zigux/tests/phase15_build.zig` and `zigux/Makefile`, so a focused maintainer run can still use `zig build test --build-file zigux/tests/phase15_build.zig` or `make -C zigux phase15`
- the shared bootstrap workflow now invokes the Phase 15 gate through `Run Phase 15 governance tests`, so the current freeze-map governance bundle is no longer maintainer-run only
- focused replay against current `master` shows the local governance bundle is runnable:
  - `zigux/tests/phase15_freeze_map_governance.zig` compiled and its `4/4` tests passed
  - `zig build test --build-file zigux/tests/phase15_build.zig --summary all` succeeded with `9/9` steps and `11/11` tests passed
  - `make -C zigux phase15` succeeded with the attached Zig toolchain
- current observed behavior on live `master`: the repo carries real freeze-map policy, manifests, scorecard, dedicated replay entrypoints, a clean local Phase 15 governance build, and shared bootstrap workflow coverage for the current Phase 15 gate

## Exact blocker record

- `freeze-map-policy-present`: yes
- `freeze-map-review-hook-present`: yes
- `phase15-local-entrypoint-present`: yes
- `phase15-shared-ci-enforcement-present`: yes
- `phase15-build-clean-on-current-master`: yes
- `phase15-build-failure-cause`: none observed in the local replay against current `master`
- next repair step inside this lane family: wait for new deep-core evidence or a named reopen trigger, because the remaining freeze-map governance work is blocker posture maintenance rather than missing replay coverage

## Next bounded step

Keep the Phase 15 governance lane in maintenance mode. The next honest action is to wait for one of the named reopen triggers or the deep-core blocker posture to change before opening another freeze-map governance slice.
