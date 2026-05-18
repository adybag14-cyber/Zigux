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

That means the older survey-local list-helper drift is now closed: `Documentation/zigux/phase13-notifier-list-survey.md` already keeps `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` explicit as shipped adjacent evidence.

Authenticated GitHub contents readback in this run also resolves `zigux/Makefile`, so the remaining same-lane truthfulness gap is no longer whether a shared build file exists. The narrower drift is that broader Phase 13 reminder surfaces can still blur that returned file together with the still-missing Phase 13 route names.

The remaining same-lane truthfulness gap has therefore narrowed to the scripts-root route wording: `scripts/zigux/README.md` still groups `zigux/Makefile` together with the missing `make -C zigux phase13-validate` and blocked convenience route `make -C zigux phase13` even though authenticated readback now resolves the file itself.

Broad Phase 13 reminder work should therefore stop reopening the already-closed survey-local list-helper drift and instead target that scripts-root route wording while keeping the adjacent notifier evidence explicit.

## Still-Missing Surfaces

This note still does not claim a broader list bridge or a closed notifier packet. These direct companions should remain treated as gaps unless a future same-lane reread proves otherwise:

- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `scripts/zigux/validate-phase13-release.py`
- `include/zigux/notifier_abi.h`
- `zigux/tests/phase13_build.zig`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

## Why It Matters

Phase 13 in the roadmap is still the shared-helper tranche around the `libfs`, `devres`, and Landlock anchors. The notifier or list packet remains adjacent evidence only, so the adjacent gap note should stay truthful about which notifier or list-facing helper surfaces now exist, which shared build file has returned, and which direct companions and route names are still missing.

## Next Bounded Step

Leave the notifier survey itself parked unless a fresh same-lane reread finds new survey-local drift.

If the same notifier or list family needs follow-through again, refresh `scripts/zigux/README.md` and its shipped shared-summary guard so they keep `zigux/Makefile` explicit as a returned shared build file while leaving `make -C zigux phase13-validate` and `make -C zigux phase13` recorded as repo-reality gaps.
