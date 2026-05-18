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

That closes the older survey-local missing-checker gap. The narrower remaining drift is broader Phase 13 reminder wording that can still blur the returned adjacent packet together with the still-missing `zigux/helpers/notifier_chain_view.zig` helper, the still-missing priority-signal companion, and the still-missing Phase 13 build-route names.

Broad Phase 13 reminder work should therefore keep the checker-backed adjacent packet explicit, keep `zigux/Makefile` distinct from the still-missing route names, and keep `zigux/helpers/notifier_chain_view.zig` plus `scripts/zigux/check-phase13-notifier-priority-signal.py` recorded as repo-reality gaps until a future reread proves they returned.

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

Phase 13 in the roadmap is still the shared-helper tranche around the `libfs`, `devres`, and Landlock anchors. The notifier or list packet remains adjacent evidence only, so the adjacent gap note should stay truthful about which checker-backed notifier or list-facing surfaces now exist, which shared build file has returned, which direct notifier helper is still missing, and which route names are still missing.

## Next Bounded Step

Leave the notifier survey itself parked unless a fresh same-lane reread finds new survey-local drift.

If the same notifier or list family needs follow-through again, refresh `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, and `scripts/zigux/check-phase13-shared-summary-surfaces.py` so they treat `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, and `zigux/tests/phase13_notifier_list_reviewability.zig` as shipped adjacent evidence while still keeping `zigux/helpers/notifier_chain_view.zig` and the missing Phase 13 build-route names in the repo-reality-gap bucket.
