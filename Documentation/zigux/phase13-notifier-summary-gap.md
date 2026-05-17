# Phase 13 Notifier Summary Gap

## Scope

This note records the current Phase 13 notifier or `list_head` summary drift that still shows up in adjacent notifier-facing survey material on `master`.

It stays inside the adjacent read-only notifier packet. It does not reopen callback execution, registration, SRCU, blocking-notifier semantics, or a broader shared-helper replay claim.

## Current Drift

Public current-`master` readback now materializes these adjacent notifier or list surfaces:

- `Documentation/zigux/phase13-notifier-list-survey.md`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/notifier_chain_view.zig`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `include/zigux/abi.h`
- `drivers/tty/hvc/hvc_console.h`

That means the stale drift is no longer the broad reminder packet. The remaining same-lane truthfulness gap is narrower: `Documentation/zigux/phase13-notifier-list-survey.md` still treats `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` as repo-reality gaps even though current `master` now materializes both helper-local list surfaces.

Broad Phase 13 reminder work should keep those list-facing helpers framed as adjacent notifier or list evidence instead of repeating the older missing-helper wording.

## Still-Missing Surfaces

This note still does not claim a broader list bridge or a closed notifier packet. These direct companions should remain treated as gaps unless a future same-lane reread proves otherwise:

- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `include/zigux/notifier_abi.h`
- `zigux/tests/phase13_build.zig`

## Why It Matters

Phase 13 in the roadmap is still the shared-helper tranche around the `libfs`, `devres`, and Landlock anchors. The notifier or list packet remains adjacent evidence only, so the adjacent gap note should stay truthful about which list-facing helper surfaces now exist and which direct companions are still missing.

## Next Bounded Step

Leave the broader shared reminder packet parked unless a fresh same-lane reread finds another notifier-facing drift.

If the same notifier or list family needs follow-through again, refresh `Documentation/zigux/phase13-notifier-list-survey.md` so it stops treating `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` as repo-reality gaps, then let the broader shared-summary lanes decide whether any contributor-facing reminder wording needs to move with it.
