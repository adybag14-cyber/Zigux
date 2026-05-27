# Developer Enablement Contributor Workflow

This guide is the shared workflow note for reminder-surface maintenance in Zigux.

It is for docs-only and checklist-only follow-through. It does not authorize helper, driver, ABI, or runtime implementation work by itself.

Use it with `Documentation/zigux/contributor-entrypoints.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.

Matching guard: `python3 scripts/zigux/check-developer-enablement-workflow.py`

## Use This Guide When

- the change is limited to `Documentation/zigux/`
- the change updates `Documentation/zigux/review-checklist.md`
- the change updates shared reminder surfaces such as `Documentation/zigux/README.md`, `scripts/zigux/README.md`, or `zigux/tests/README.md`
- the change adds or refreshes contributor-facing workflow guidance, closure checklists, or lane-sequencing notes

## Source-Of-Truth Order

Refresh reminder wording in this order:

1. the owner packet for the phase or lane
2. any dedicated closure note, checklist, sequencing note, or survey that owns the exact claim
3. the smallest shared reminder surface that repeats that claim
4. checker or validator wording only if the owner packet and shared reminder text now disagree

Do not start from the broad README files and work inward. Shared reminder surfaces summarize landed owner packets; they do not invent new repo state.

## Shared Reminder Surfaces

The usual shared reminder surfaces are:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Treat those files as contributor-facing summaries. Keep them aligned with current owner packets, but do not widen them into proof that a missing replay route, wrapper, workflow step, or deeper implementation slice is already landed.

## Bounded Update Loop

For a docs-and-checklist lane change, use this loop:

1. reread the owner packet and the nearest shared reminder surface together
2. identify the smallest stale or missing contributor-facing statement
3. update only the surface that is currently understated or missing
4. verify that the new wording does not claim more than current `master` proves
5. rerun the nearest checker or validator if one already exists for that packet
6. if the change touches this guide or its contributor-entrypoint handoff, rerun `python3 scripts/zigux/check-developer-enablement-workflow.py`

If no checker exists, keep the change docs-only unless adding a new checker is clearly the smallest honest way to keep the workflow trustworthy.

## Validation Order

Prefer existing packet-local checks before inventing new ones:

1. packet-local `python3 scripts/zigux/check-*.py --self-test` routes
2. packet-local validator entrypoints such as `python3 scripts/zigux/validate-phase*.py`
3. existing `make -C zigux ...` wrapper routes when current `master` already exposes them
4. attached Zig toolchain replay only when a current route expects Zig and the local pinned path is unavailable

If the environment cannot materialize a trustworthy live checkout, keep validation scoped to exact readback evidence and the smallest honest self-check you can perform.

## Non-Goals

This guide does not:

- reopen deeper implementation lanes
- promote public-tree hints into authenticated current-head proof
- treat missing wrappers or missing CI routes as landed
- convert a docs-only reminder refresh into a broad multi-phase rewrite

## Next-Step Rule

When a reminder surface drifts, fix the nearest owner packet first. Only then update the broader shared surface that understated it.

When several reminder surfaces look stale at once, choose one bounded contributor-facing step per run and leave the remaining follow-through explicitly for the next lane pass.
