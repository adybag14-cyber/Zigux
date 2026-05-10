# Phase 13 Notifier List Survey

This note keeps the shipped adjacent notifier evidence in the Phase 13 contributor workflow explicit on current `master`.

It is an adjacent release-surface survey, not a fifth shared-helper anchor and not an extra shared replay step inside the current Phase 13 validator-first packet.

## Why This Survey Exists

Broad contributor-facing surfaces already point at a notifier-adjacent evidence packet, but that packet needs its own compact owner note so the docs root, tests root, scripts root, and checklist do not have to inline the full rationale every time Phase 13 wording shifts.

Use this survey when a change touches the adjacent notifier evidence named beside the shared helper packet in `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/README.md`, or `Documentation/zigux/review-checklist.md`.

## Current Adjacent Evidence

The current adjacent notifier packet on `master` is:

- `scripts/zigux/check-phase13-notifier-packet.py`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/abi.h`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `zigux/helpers/notifier_chain_view.zig`
- `drivers/tty/hvc/hvc_console.h`

Treat that packet as shipped adjacent release-surface evidence that sits beside the four manifest-backed Phase 13 helper anchors rather than inside them.

## Boundaries That Must Stay Honest

Keep the following boundaries explicit whenever contributor workflow wording changes:

- `scripts/zigux/check-phase13-notifier-packet.py` is the dedicated adjacent evidence guard for this packet; do not borrow it as shorthand for the `libfs`, `devres`, or Landlock helper lanes.
- `zigux/tests/phase13_notifier_list_manifest.json` and `zigux/tests/phase13_notifier_list_reviewability.zig` are direct notifier reviewability evidence, not a ninth shared replay step in `zigux/tests/phase13_build.zig`.
- `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, and `include/zigux/notifier_abi.h` keep the adjacent ABI edge explicit without recasting that ABI surface as a fifth shared-helper anchor.
- `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `zigux/helpers/notifier_chain_view.zig` are shipped helper-adjacent evidence for contributor reviewability, but they do not widen the shared Phase 13 replay route.
- `drivers/tty/hvc/hvc_console.h` remains the concrete notifier-adjacent HVC header reminder for contributor guidance, but it does not reopen Phase 11 HVC replay ownership.

## Review Order

When this adjacent evidence changes, keep the narrow review route explicit:

1. `python3 scripts/zigux/check-phase13-notifier-packet.py`
2. `python3 scripts/zigux/validate-phase13-release.py`
3. `make -C zigux phase13-validate`
4. `make -C zigux phase13`

## Surfaces To Keep In Sync

When this note changes, keep these broad contributor-facing surfaces aligned in the same follow-through:

- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Those broader reminders should continue to treat the notifier packet as adjacent evidence rather than as a new shared replay step.

## Non-Goals

This survey does not:

- add a fifth Phase 13 manifest-backed helper anchor
- add a ninth shared replay step to `zigux/tests/phase13_build.zig`
- reopen the dedicated Phase 11 HVC survey lane
- imply broader runtime closure outside the current Phase 13 helper-first packet

## Next Safe Follow-up

After this survey lands, the next same-lane documentation step is to refresh the broad Phase 13 summary lines in `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md` so they cite the full adjacent notifier evidence packet as completely as the tests-root and scripts-root reminders already do.
