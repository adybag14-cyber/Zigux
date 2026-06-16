# Phase 14 Validate-Route Reminder Gap

## Scope

- lane: `P14-L02`
- phase: `Phase 14`
- packet: shared Phase 14 smoke reminder truthfulness
- status: `current-master reminder-route drift`

## Why this note exists

The Phase 14 roadmap keeps Zigux in a bounded study-only and wrapper-first posture for core-adjacent internals. That makes reminder-surface truthfulness part of the product work: if the shared smoke route changes on current `master`, the shared reminder packet needs to say so plainly instead of replaying older route vocabulary as if it were still exact.

## Current repo readback

Fresh current-`master` readback on 2026-05-19 shows a narrow but real shared-smoke route split:

- `zigux/Makefile` now ships `phase14-validate`
- `scripts\zigux/check_phase14_shared_smoke_route.zig` already fail-closes on that dedicated `phase14-validate` route and still rejects `phase14-smoke` and `phase14-test` as active workflow proof
- `scripts\zigux/validate_phase14.zig` and `scripts\zigux/check_phase14_release_boundary_exact_counts.zig` are both directly readable current shared-smoke evidence

At the same time, several shared reminder surfaces still lag that live route split:

- `zigux/tests/README.md` still says the readable Makefile has no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets
- `scripts/zigux/README.md` still says there are no `phase14-validate`, `phase14-smoke`, `phase14-test`, or `phase14` targets
- `Documentation/zigux/review-checklist.md` still frames `phase14-validate`, `phase14-smoke`, `phase14-test`, and `phase14` together as packet-local or repo-reality-gap vocabulary

## Why this matters

This is a bounded productization gap rather than a new delivery claim:

- the roadmap says Phase 14 should stay disciplined, explicit, and reviewability-first
- the shared smoke route checker already records the live route truth
- reminder drift can send future runs back toward stale assumptions even when the route itself is already shipped

## Smallest honest same-lane conclusion

The live route gap is no longer about whether `phase14-validate` exists. It is about reminder surfaces that have not caught up to that shipped route yet.

The next honest same-lane follow-through is therefore either:

1. repair the smallest shared reminder surface that still denies `phase14-validate`, or
2. keep this note and its checker aligned until a wider same-lane reminder refresh lands.

## Non-goals

- do not treat `phase14-smoke`, `phase14-test`, or `phase14` as returned current-`master` routes
- do not reopen workqueue, ring-buffer, skbuff, or RCU anchor-local content
- do not claim executable-layer recovery for `zigux/tests/phase14_build.zig` or the broader unreadable packet members
