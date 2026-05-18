# Zigux Program Charter

This document is the docs-root charter for Zigux as a product program.

It exists to keep roadmap discipline, review boundaries, freeze-map compliance, and Architecture Council decision ownership explicit in one place.

## Purpose

Zigux is a Linux product program, not a language-rewrite experiment.

The project should grow by shipping bounded helpers, ABI slices, validation harnesses, closure records, and other reviewable infrastructure that the roadmap actually calls for.

The project should not treat wrapper proliferation, broad mirror-tree growth, or speculative deep-core rewrites as progress.

## Program posture

- the roadmap in `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md` is the main scheduler for what kind of work belongs in Zigux
- the docs root keeps product commitments reviewable on current `master`
- each lane should finish one bounded step instead of widening into unrelated phases or file families
- deep-core ambition does not outrank reviewability, validation, rollback ownership, or evidence quality
- if repo reality and older notes disagree, current repo evidence wins and reminder surfaces must be refreshed

## Architecture Council boundary

The Architecture Council owns the review boundary for deep-core status changes and other architecture decisions that would materially change Zigux scope.

That includes:

- changes to the freeze-in-C or study-only anchor sets recorded in `Documentation/zigux/freeze-map.md`
- requests to move a freeze-map anchor into a different status bucket
- requests that would turn a study-only anchor into an active delivery target
- architecture decisions that would widen the product boundary beyond the current roadmap phase without a fresh reviewable record

These decisions must stay explicit, reviewable, and reversible.

## Required decision inputs

Any Architecture Council status-review request must keep the following explicit before the repo treats it as an active product decision:

- exact Linux anchor path
- roadmap phase and lane key
- current status bucket and requested decision bucket
- lane owner, required approver set, and rollback owner
- validation gate summary, replay command, and rollback threshold
- evidence archive path and latest blocker disposition
- automatic return-to-blocked trigger, reopen triggers, and trigger-specific evidence refresh
- parity scorecard link or blocker record
- indefinite-C policy link or explicit non-applicability note
- explicit non-goals and written rationale

If those fields cannot be stated honestly, the request stays blocked and the current source of truth stays in C.

## Freeze-map compliance

The freeze map is not a suggestion.

Until an Architecture Council record changes the status bucket with fresh evidence, Zigux must treat:

- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

as freeze-in-C anchors, and it must treat:

- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

as study-only anchors.

Work around those anchors may improve surveys, manifests, gates, parity accounting, blocker tracking, or review-process truthfulness, but it must not imply a status change by momentum alone.

## Current governing surfaces

Keep this charter aligned with the existing docs-root governance packet:

- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`

If one of those files changes the Architecture Council field inventory, freeze posture, or stay-in-C policy vocabulary, this charter should be updated to match instead of carrying a competing policy summary.

## What counts as progress

Real Zigux progress should look like one or more of the following:

- a new or improved helper, ABI slice, harness, or validation surface inside the roadmap lane being worked
- a tranche-closing note, manifest, checker, or closure record that makes an existing slice more trustworthy
- a reminder-surface repair that keeps current repo reality truthful and reviewable
- a bounded governance update that reduces the chance of false architecture claims or freeze-map drift

The following do not count as product progress by themselves:

- naming churn without new capability
- wrapper chains that do not close a real roadmap gap
- broad speculative ports for deep-core anchors
- stale summary text that implies more current evidence than the repo actually carries

## Non-goals

This charter does not approve:

- any freeze-map status change
- a direct Zig bridge for a freeze-in-C anchor
- an exception path around review, validation, or rollback ownership
- roadmap phase skipping by enthusiasm alone

## Next bounded step

Keep this charter aligned with `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `Documentation/zigux/freeze-map.md` whenever Architecture Council boundaries, freeze-map vocabulary, or docs-root governance entry points change.
