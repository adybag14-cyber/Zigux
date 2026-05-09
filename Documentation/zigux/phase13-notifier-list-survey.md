# Phase 13 Notifier/List Survey

lane key: `P13-L18`
phase: `Phase 13`
surveyed commit: `23d15e44622d2cedd7691c88f78709db6bf1eb7e`
scope: roadmap-adjacent reviewability evidence only

## Why this packet exists

Phase 13 is still scheduled around `fs/libfs.c`, `lib/devres.c`, and the two Landlock anchors. The live tree nevertheless carries a small notifier-plus-list foothold through `zigux/bindings/notifier_abi.zig`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/helpers/notifier_chain_view.zig`, the exported list or hlist structs in `include/zigux/abi.h`, and the concrete mixed interop anchor in `drivers/tty/hvc/hvc_console.h`. This note keeps that adjacent surface reviewable without recasting notifier work as a new shared-helper delivery anchor.

## Current live evidence

- `zigux/bindings/notifier_abi.zig` already defines the bounded read-only notifier flag set plus `NotifierBlockRef`, `RawNotifierHeadRef`, `NotifierChainView`, and `NotifierChainSummary`.
- `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` already provide read-only list traversal summaries with explicit bounded scan limits.
- `zigux/helpers/notifier_chain_view.zig` now provides the matching read-only notifier-chain summary helpers, including the nonincreasing-priority signal.
- `include/zigux/abi.h` already exports the list and hlist ABI carrier structs that those helpers depend on.
- `include/zigux/notifier_abi.h` is now shipped as adjacent notifier interop evidence beside `zigux/bindings/notifier_abi.zig` and `zigux/helpers/notifier_chain_view.zig`.
- `drivers/tty/hvc/hvc_console.h` still shows the concrete interop anchor: `struct hvc_struct` carries `struct list_head next`, while `struct hv_ops` plus the exported `notifier_*_irq` helpers keep the notifier-side callback shape visible without claiming callback execution parity.
- `scripts/zigux/check-phase13-notifier-packet.py` now fails closed on the adjacent notifier packet so the survey note, manifest, helper, header, and adjacent-only build posture stay aligned.
- the shared `scripts/zigux/validate-phase13-release.py` route now keeps this survey and its adjacent notifier helper footholds visible inside the broader Phase 13 release packet without recasting them as a ninth shared replay step.
- `zigux/tests/phase13_notifier_list_manifest.json` and `zigux/tests/phase13_notifier_list_reviewability.zig` now keep that notifier-plus-list foothold pinned to roadmap-adjacent reviewability evidence instead of silently reading like a ninth shared replay step.
- the shared Phase 13 build intentionally omits this packet from the eight-test release replay, so this survey stays adjacent release-surface evidence rather than another shared replay step.

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

`zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, and the shared `scripts/zigux/validate-phase13-release.py` route should keep this note, the manifest, the adjacent notifier header plus helper footholds, the `hvc_console.h` interop anchor, and the adjacent-only release posture aligned without turning the notifier packet into a ninth shared replay step.
