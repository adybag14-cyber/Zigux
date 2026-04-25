# Phase 15 Architecture Council Review Process Survey

This document records the bounded Phase 15 governance lane around the Architecture Council review-process gap named in the roadmap.

## Status

- `PHASE15_STATUS=review_process_slice_landed`
- `PHASE15_SLICE=architecture-council-review-process`
- scope: one review-process note, one dedicated manifest and Zig test, the shared Phase 15 build wiring, and a small review-checklist update
- survey provenance refreshed against verified `master` head `40aa574db33204bfbb0c972f1de37ad4cb396a77`
- product boundary:
  - `Documentation/zigux/phase15-architecture-council-review-process.md`
  - `Documentation/zigux/review-checklist.md`
  - `zigux/tests/phase15_architecture_council_review_process_manifest.json`
  - `zigux/tests/phase15_architecture_council_review_process.zig`
  - `zigux/tests/phase15_build.zig`

## Why this slice exists

The roadmap's Phase 15 requirements include an Architecture Council review process, a parity scorecard, and the policy for code that remains in C indefinitely. Current `master` already carries the freeze map plus stay-in-C governance language, but it still lacks a reviewable record that says when the Architecture Council must be engaged, what evidence a request must carry, and what bounded outcomes are allowed.

That missing process leaves a governance gap between the roadmap and the live repo. Without it, a future patch can mention the Architecture Council in principle while still leaving reviewers to guess what packet a status-change request needs and which decisions are legitimate inside the current mixed-language product plan.

The honest bounded step is to land a survey-grade review-process note that turns the roadmap requirement into a concrete review artifact without pretending the council already has a full roster, cadence, or automation surface.

## Trigger Conditions

The Architecture Council review process must be invoked when a lane proposes any of the following:

- a change to the freeze-in-C list or the study-only list in `Documentation/zigux/freeze-map.md`
- a status-bucket change for a freeze-map anchor, including any request to move from `freeze in C initially` toward a direct Zigux port claim
- a claim that a deep-core boundary study is now ready for bounded dual implementation
- contradictory validation results that need a written decision about whether the code stays in C with a blocker or advances to another bounded status

## Required Review Packet

Every Architecture Council request in this lane family must carry:

- the exact Linux anchor path and current roadmap phase
- the requested decision bucket
- the named owner for the lane and the rollback owner
- the validation gate summary with links to the live evidence
- a parity scorecard link, or an explicit blocker record saying why the scorecard is not ready yet
- explicit non-goals so the request does not quietly widen into deep-core delivery
- the written rationale for why the current product state needs council attention now

## Decision Buckets

The bounded outcomes for this review process are:

- `keep_in_c`: the existing C implementation remains the product source of truth and the blocker stays recorded
- `study_only_followup`: a boundary-study lane may continue, but no direct Zigux ownership claim is approved
- `bounded_dual_implementation`: a tightly scoped wrapper-first or dual-implementation follow-up is allowed with named validation and rollback gates
- `defer_or_reject`: the request is not approved and the lane must narrow or stop

## Recordkeeping Rules

- every decision must leave a written rationale in a reviewable artifact
- the lane note must record the chosen decision bucket, the owner, the validation gate, and the rollback owner
- if the council keeps the code in C, the blocker must remain explicit rather than disappearing into prose
- if the parity scorecard is missing, the record must say that clearly instead of implying silent approval

## Recorded Gaps

The current lane state is:

- landed `phase15-architecture-council-review-process-doc`
- landed `phase15-architecture-council-review-process-manifest`
- landed `phase15-architecture-council-review-process-test`
- landed `phase15-review-checklist-hook`
- landed `phase15-build-gate-review-process`
- ready-next `phase15-parity-scorecard-template`

This keeps the slice narrow. Zigux gains a reviewable Architecture Council process description and a runnable governance gate, but it still does not claim a parity scorecard template, a real council roster, or any change to a freeze-map anchor status.

## Non-goals

This slice does not claim:

- a full Architecture Council charter, roster, calendar, or voting system
- a finished parity scorecard document
- any status change for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`
- any new deep-core Zig bridge, wrapper, or direct port starter

## Gates

1. run the dedicated Phase 15 build
- `zig build test --build-file zigux/tests/phase15_build.zig`

2. run the convenience target
- `make -C zigux phase15`

## Next bounded step

Stay in the Phase 15 governance lane and add the bounded parity-scorecard template next so future Architecture Council requests can attach a concrete comparison artifact instead of only a process note.
