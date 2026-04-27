# Phase 15 Freeze-Map Governance

This document records the bounded Phase 15 governance lane around `Documentation/zigux/freeze-map.md`.

## Status

- `PHASE15_STATUS=governance_slice_landed`
- `PHASE15_SLICE=freeze-map-governance-blocker-verification`
- scope: the live freeze map, the existing dedicated Phase 15 manifest and test gate, and one bounded maintenance follow-up that keeps the root freeze-map note aligned with the already-landed parity-scorecard, review-process, indefinite-C policy, retained stay-in-C closeout, and current blocker posture
- survey provenance refreshed against verified `master` head `0aedabd88664ce71bb1ccf5c8591db50b858950e`
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

That makes the original freeze-map governance slice slightly stale. Its focused note, manifest, and test still read like the parity scorecard is merely the next step, and they still understate the current blocker posture even after the root freeze map gained the retained stay-in-C closeout and no-silent-exception wording that the newer Phase 15 policy family already depends on.

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

- verified remote `master` head for this check: `0aedabd88664ce71bb1ccf5c8591db50b858950e`
- the root policy is present and explicit in `Documentation/zigux/freeze-map.md`, including the freeze-in-C list, study-only list, Architecture Council requirement, parity-scorecard requirement, retained stay-in-C closeout state, reopen-trigger language, and the no-silent-exception rule
- the review hook is present in `Documentation/zigux/review-checklist.md`, which now asks whether freeze-map anchors carry parity-scorecard evidence or blocker state, decision-record links, retained-discussion state, reopen triggers, and an explicit current lane owner for blocked evidence packets
- the dedicated local replay surface is present in `zigux/tests/phase15_build.zig` and `zigux/Makefile`, so a focused maintainer run can still use `zig build test --build-file zigux/tests/phase15_build.zig` or `make -C zigux phase15`
- the shared bootstrap workflow does not currently invoke the Phase 15 gate: `.github/workflows/zigux-bootstrap.yml` runs through Phase 14 and contains no `Validate Phase 15` or `Run Phase 15` step, so freeze-map governance is not enforced by the published shared CI path today
- focused replay against current `master` shows the local enforcement bundle is clean even though shared CI still does not invoke it:
  - `zigux/tests/phase15_freeze_map_governance.zig` compiled and its `4/4` tests passed
  - `zigux/tests/phase15_parity_scorecard.zig` compiled and its `3/3` tests passed
  - `zigux/tests/phase15_architecture_council_review_process.zig` compiled and its `2/2` tests passed
  - `zigux/tests/phase15_indefinite_c_policy.zig` compiled and its `2/2` tests passed
  - `zig build test --build-file zigux/tests/phase15_build.zig --summary all` passed cleanly with `9/9` steps succeeded and `11/11` tests passed
- current observed behavior on live `master`: the repo carries real freeze-map policy, manifests, scorecard, and dedicated replay entrypoints, and the local Phase 15 governance bundle is fully runnable, but the published shared CI path still does not enforce it

## Exact blocker record

- `freeze-map-policy-present`: yes
- `freeze-map-review-hook-present`: yes
- `phase15-local-entrypoint-present`: yes
- `phase15-shared-ci-enforcement-present`: no
- `phase15-build-clean-on-current-master`: yes
- `phase15-build-failure-cause`: none in the focused local replay; the remaining enforcement gap is that shared CI still does not invoke the Phase 15 gate
- next repair step inside this lane family: decide separately whether `.github/workflows/zigux-bootstrap.yml` should begin running the already-green Phase 15 governance bundle on qualifying changes

## Next bounded step

Keep the Phase 15 governance lane in maintenance mode. The next honest action is to wait for one of the named reopen triggers or the deep-core blocker posture to change before opening another freeze-map governance slice.
