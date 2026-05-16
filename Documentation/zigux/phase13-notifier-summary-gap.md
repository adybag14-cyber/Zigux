# Phase 13 Notifier Summary Gap

## Scope

This note records the current Phase 13 notifier or `list_head` summary drift that still shows up in broad reminder surfaces on `master`.

It stays inside the adjacent read-only notifier packet. It does not reopen callback execution, registration, SRCU, blocking-notifier semantics, or a broader shared-helper replay claim.

## Current Drift

Current `master` still materializes these notifier-facing packet files:

- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/tests/phase13_build.zig`

But the current shared summaries in these broad reminder surfaces still describe those materialized files as repo-reality gaps:

- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/README.md`

That leaves the adjacent notifier packet internally truthful at the helper and tests-root layer, while the broader reminder packet still understates the materialized manifest, reviewability, and shared build footholds.

## Still-Missing Surfaces

This drift note does not claim a broader list bridge has landed. These direct companions should remain treated as gaps unless a future same-lane reread proves otherwise:

- `scripts/zigux/check-phase13-notifier-packet.py`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`

## Why It Matters

Phase 13 in the roadmap is still the shared-helper tranche around bounded helper layers. The notifier packet remains adjacent evidence only, so broad reminder surfaces should not erase materialized packet files or blur the remaining direct `list_head` and `hlist` gaps.

## Next Bounded Step

When a direct existing-file edit path is available, reconcile `Documentation/zigux/phase13-notifier-list-survey.md` and `scripts/zigux/README.md` so they keep the true missing direct companions explicit while no longer listing the materialized notifier manifest, reviewability, and `phase13_build.zig` files as absent.
