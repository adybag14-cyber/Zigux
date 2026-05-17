# Phase 13 Notifier Summary Gap

## Scope

This note records the current Phase 13 notifier or `list_head` summary drift that still shows up in broad reminder surfaces on `master`.

It stays inside the adjacent read-only notifier packet. It does not reopen callback execution, registration, SRCU, blocking-notifier semantics, or a broader shared-helper replay claim.

## Current Drift

Fresh current-`master` reads still return missing for these notifier-facing packet files:

- `Documentation/zigux/phase13-notifier-list-survey.md`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/tests/phase13_build.zig`

The shipped broad reminder surfaces in:

- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

already keep those missing notifier companions framed as repo-reality gaps.

That means there is no remaining broad-summary undercount for the notifier survey note, manifest, reviewability, or shared-build footholds on current `master`. The stale claim was this note itself: it still named the missing `Documentation/zigux/phase13-notifier-list-survey.md` file as if it were one of the broad reminder surfaces already carrying the gap wording.

## Still-Missing Surfaces

This note does not claim a broader list bridge has landed. These direct companions should remain treated as gaps unless a future same-lane reread proves otherwise:

- `Documentation/zigux/phase13-notifier-list-survey.md`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/tests/phase13_build.zig`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`

## Why It Matters

Phase 13 in the roadmap is still the shared-helper tranche around bounded helper layers. The notifier packet remains adjacent evidence only, so broad reminder surfaces should stay honest about what is still absent instead of being pushed to count missing notifier files as landed evidence.

## Next Bounded Step

Leave the current broad reminder wording parked unless a fresh same-lane reread finds a different shared-surface drift or current `master` rematerializes one of the missing notifier companions above.
