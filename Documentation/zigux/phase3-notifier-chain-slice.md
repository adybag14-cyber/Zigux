# Phase 3 notifier-chain Slice

This note records one bounded Phase 3 helper-side notifier-chain packet on current `master`.

## Current Slice

- `zigux/helpers/notifier_chain_view.zig`
- `zigux/tests/phase3_notifier_chain_starter_packet.zig`
- `zigux/tests/phase3_notifier_chain_starter_packet_build.zig`

## Bounded Contract

- `zigux/helpers/notifier_chain_view.zig` keeps null-head detection, bounded forward iteration, chain length, tail discovery, and first priority-increase witnesses explicit for existing `struct notifier_block` chains.
- `zigux/tests/phase3_notifier_chain_starter_packet.zig` keeps the empty chain, ordered descending-or-equal chains, and first increasing-priority witness directly reviewable without widening into callbacks, notifier return codes, or broader subsystem ownership semantics.
- `zigux/tests/phase3_notifier_chain_starter_packet_build.zig` exposes the packet as a standalone replay route so this helper-local slice can be rerun without reopening the shared tests root.

## Replay Route

- `zig build phase3-notifier-chain-starter-packet --build-file zigux/tests/phase3_notifier_chain_starter_packet_build.zig`

## Scope

This slice stays intentionally helper-local. It does not claim notifier return-code policy, callback invocation behavior, container recovery, list mutation helpers, or broader notifier-chain ownership semantics.
