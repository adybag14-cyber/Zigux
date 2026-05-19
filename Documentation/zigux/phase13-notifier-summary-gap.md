# Phase 13 Notifier Summary Gap

## Scope

This note records the current Phase 13 notifier or `list_head` summary drift that still shows up in broader contributor-facing reminder material on `master`.

It stays inside the adjacent read-only notifier packet. It does not reopen callback execution, registration, SRCU, blocking-notifier semantics, or a broader shared-helper replay claim.

## Current Drift

Public current-`master` readback now materializes these adjacent notifier or list surfaces:

- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `include/zigux/abi.h`
- `drivers/tty/hvc/hvc_console.h`

That closes the older survey-local missing-checker gap.

Current reread also shows the broader contributor-facing reminder surfaces already keep the checker-backed adjacent packet explicit, keep `zigux/Makefile` distinct from the still-missing route names, and keep `zigux/helpers/notifier_chain_view.zig` plus `scripts/zigux/check-phase13-notifier-priority-signal.py` recorded as repo-reality gaps.

The remaining notifier-family gaps are therefore the still-missing direct companions themselves rather than stale summary wording inside the already-shipped reminder set.

## Still-Missing Surfaces

This note still does not claim a broader list bridge or a closed notifier packet. These direct companions should remain treated as gaps unless a future same-lane reread proves otherwise:

- `zigux/helpers/notifier_chain_view.zig`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `scripts/zigux/validate-phase13-release.py`
- `include/zigux/notifier_abi.h`
- `zigux/tests/phase13_build.zig`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

## Why It Matters

Phase 13 in the roadmap is still the shared-helper tranche around the `libfs`, `devres`, and Landlock anchors. The notifier or list packet remains adjacent evidence only, so the adjacent gap note should stay truthful about which checker-backed notifier or list-facing surfaces now exist, which shared build file is still missing, which direct notifier helper is still missing, and which route names are still missing.

## Next Bounded Step

Leave this note parked unless a future same-lane reread finds one of the broader reminder surfaces drifting away from the checker-backed adjacent packet.

If the same notifier or list family needs follow-through again, first compare `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, and `Documentation/zigux/phase13-notifier-list-survey.md` together, then land at most one reminder-surface refresh only if one of them stops treating `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, and `zigux/tests/phase13_notifier_list_reviewability.zig` as shipped adjacent evidence while `zigux/helpers/notifier_chain_view.zig` and the missing Phase 13 build-route names stay in the repo-reality-gap bucket.
