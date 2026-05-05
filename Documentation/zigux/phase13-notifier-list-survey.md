# Phase 13 Notifier/List Survey

lane key: `P13-L13`
phase: `Phase 13`
surveyed commit: `master-reviewability`
scope: roadmap-adjacent reviewability evidence only

## Why this packet exists

Phase 13 is still scheduled around `fs/libfs.c`, `lib/devres.c`, and the two Landlock anchors. The live tree nevertheless carries a small notifier-plus-list foothold through `zigux/bindings/notifier_abi.zig`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and the exported list or hlist structs in `include/zigux/abi.h`. This note keeps that adjacent surface reviewable without recasting notifier work as a new shared-helper delivery anchor.

## Current live evidence

- `zigux/bindings/notifier_abi.zig` already defines the bounded read-only notifier flag set plus `NotifierBlockRef`, `RawNotifierHeadRef`, `NotifierChainView`, and `NotifierChainSummary`.
- `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` already provide read-only list traversal summaries with explicit bounded scan limits.
- `include/zigux/abi.h` already exports the list and hlist ABI carrier structs that those helpers depend on.
- the shared Phase 13 build intentionally omits this packet from the six-test release replay, so this survey stays adjacent release-surface evidence rather than another shared replay step.

## Remaining bounded gaps

- no read-only notifier chain helper on current `master`; `zigux/helpers/notifier_chain_view.zig` remains the next helper-local follow-up if this lane reopens
- no dedicated exported notifier C header yet; `include/zigux/notifier_abi.h` remains a separate interop follow-up rather than a hidden current capability

## Non-goals

- no notifier callback execution
- no registration or chain mutation helpers
- no SRCU or blocking-notifier semantics
- no expansion into a new roadmap anchor beyond reviewability evidence

## Validation intent

`zigux/tests/phase13_notifier_list_reviewability.zig` should keep the current binding-only notifier surface, the list or hlist helper footholds, the adjacent-only build posture, and the two explicit missing follow-ups aligned with this note and the manifest.
