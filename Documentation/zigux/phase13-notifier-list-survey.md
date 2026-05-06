# Phase 13 Notifier/List Survey

lane key: `P13-L18`
phase: `Phase 13`
surveyed commit: `master-read-only-helper`
scope: roadmap-adjacent reviewability evidence only

## Why this packet exists

Phase 13 is still scheduled around `fs/libfs.c`, `lib/devres.c`, and the two Landlock anchors. The live tree nevertheless carries a small notifier-plus-list foothold through `zigux/bindings/notifier_abi.zig`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/helpers/notifier_chain_view.zig`, and the exported list or hlist structs in `include/zigux/abi.h`. This note keeps that adjacent surface reviewable without recasting notifier work as a new shared-helper delivery anchor.

## Current live evidence

- `zigux/bindings/notifier_abi.zig` already defines the bounded read-only notifier flag set plus `NotifierBlockRef`, `RawNotifierHeadRef`, `NotifierChainView`, and `NotifierChainSummary`.
- `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` already provide read-only list traversal summaries with explicit bounded scan limits.
- `zigux/helpers/notifier_chain_view.zig` now provides the matching read-only notifier-chain summary helpers, including the nonincreasing-priority signal.
- `include/zigux/abi.h` already exports the list and hlist ABI carrier structs that those helpers depend on.
- `include/zigux/notifier_abi.h` is now shipped as adjacent notifier interop evidence beside `zigux/bindings/notifier_abi.zig` and `zigux/helpers/notifier_chain_view.zig`.
- the shared Phase 13 build intentionally omits this packet from the seven-test release replay, so this survey stays adjacent release-surface evidence rather than another shared replay step.

## Remaining bounded gaps

- no dedicated notifier callback replay ships on `master`
- no registration or chain mutation helpers ship on `master`
- no SRCU or blocking-notifier semantics ship on `master`

## Non-goals

- no notifier callback execution
- no registration or chain mutation helpers
- no SRCU or blocking-notifier semantics
- no expansion into a new roadmap anchor beyond reviewability evidence

## Validation intent

`zigux/tests/phase13_notifier_list_reviewability.zig` should keep the current binding-side notifier surface, the shipped adjacent notifier header plus helper footholds, the adjacent-only build posture, and the remaining no-callback or no-registration boundaries aligned with this note and the manifest.
