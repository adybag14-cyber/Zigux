# Zigux Freeze Map

This file records code that should not move into active Zigux delivery without an explicit Architecture Council decision.

## Freeze In C Initially
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

## Study / Boundary Only
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

## Governance For Freeze-Map Changes
- changes to either list require an explicit Architecture Council decision with written rationale
- any lane that touches a listed anchor must declare owner, phase, status bucket, validation gate summary, and rollback owner in the reviewable record for that lane
- freeze-map status-change requests must route through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, and `Documentation/zigux/phase15-indefinite-c-policy.md`, and keep the exact Linux anchor path, current roadmap phase, lane owner, rollback owner, current status bucket, requested decision bucket, decision record ID, required approver set, validation gate summary, evidence archive path, latest blocker disposition, automatic return-to-blocked trigger, benchmark notes, replay command, rollback threshold, retained discussion state, reopen triggers, trigger-specific evidence refresh, parity scorecard link or blocker record, indefinite-C policy link or non-applicability note, explicit non-goals, and written rationale explicit beside those minimum lane fields
- direct Zig port or bridge claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry and the Architecture Council records why the status can change

## Stay-In-C Policy
- the existing C implementation remains the product source of truth for every freeze-in-C anchor
- allowed near-term Zigux work on those anchors is limited to survey notes, boundary manifests, validation gates, blocker-accounting upkeep, and explicit non-goal records
- wrapper-first or helper-first experiments may continue only for study-only anchors, and they still must keep scheduler, MM, RCU, skbuff, and other deep-core ownership explicit
- study-only follow-up may gather narrower evidence, but it must not present `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as active delivery targets before an Architecture Council reviewable record changes their status bucket
- freeze-in-C follow-up may improve parity scorecard evidence, review-process records, and blocker-accounting posture, but it must not imply a status change for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c` without the required approver set and linked evidence archive path
- if validation is incomplete, contradictory, or too weak to justify a status change, keep the code in C and record the blocker
- closing a freeze-in-C review without a status change must retain the blocker, keep the required approver set and automatic return-to-blocked trigger explicit for the recorded closeout, record the closeout as `retired_from_active_discussion`, and keep the evidence archive path, reopen triggers, and trigger-specific evidence refresh attached to the evidence archive
- any reopen request for code that remains in C indefinitely must keep the automatic return-to-blocked trigger and trigger-specific evidence refresh explicit so stale summaries, contradictory evidence, or route drift return the anchor to blocked posture instead of implying continued approval
- there is no silent exception path around the stay-in-C policy; only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review

## Policy
- deep-core files do not become sprint targets by enthusiasm alone
- research is allowed
- product commitments require explicit gates, validation, and ownership
- if evidence is not overwhelming, keep the code in C and document why
