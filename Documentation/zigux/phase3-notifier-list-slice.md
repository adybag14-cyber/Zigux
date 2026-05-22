# Phase 3 notifier/list Slice

This note records one bounded shared-helper replay for the current notifier-chain and `list_head` interop surfaces on `master`.

## Current Slice

- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/list_view.zig`
- `zigux/tests/phase3_notifier_list_starter_packet.zig`
- `zigux/tests/phase3_notifier_list_starter_packet_build.zig`

## Bounded Contract

- `notifier_abi.zig` keeps notifier priority ordering and first-increase witnesses explicit for published notifier-chain metadata.
- `list_view.zig` keeps sentinel emptiness, bounded forward traversal, and first broken backlink witnesses explicit for circular `list_head` chains.
- `phase3_notifier_list_starter_packet.zig` proves that the notifier-side `ListHead` and `ListBackLinkBreak` layouts stay aligned with the shared `list_view` helper and that both surfaces report the same first broken backlink witness.

## Replay Route

- `zig build phase3-notifier-list-starter-packet --build-file zigux/tests/phase3_notifier_list_starter_packet_build.zig`

## Scope

This slice stays validation-first. It does not add notifier mutation helpers, callback invocation, container recovery, or broader subsystem ownership behavior.
