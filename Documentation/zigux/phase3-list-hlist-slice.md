# Phase 3 list/hlist Slice

This note records one bounded shared-helper starter packet for the existing Phase 3 `list_head` and `hlist` helpers on current `master`.

## Current Slice

- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `zigux/tests/phase3_list_hlist_starter_packet.zig`
- `zigux/tests/phase3_list_hlist_starter_packet_build.zig`

## Bounded Contract

- `list_view.zig` keeps sentinel emptiness, first and last node discovery, bounded forward iteration, length counting, and backlink break detection explicit for circular `list_head` chains.
- `hlist_view.zig` keeps empty-head detection, first-node discovery, bounded forward iteration, length counting, head-to-first `pprev` validation, tail-null validation, and first broken prev-link detection explicit for singly linked `hlist` chains.
- `phase3_list_hlist_starter_packet.zig` proves that both helpers keep the empty sentinels, ordered chains, and first broken backlink witnesses explicit without widening into container-of traversal, mutation helpers, or broader subsystem ownership semantics.

## Replay Route

- `zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig`

## Scope

This slice is intentionally starter-packet sized. It does not yet claim C parity fixtures, exported ABI structs, intrusive container recovery helpers, list mutation semantics, or wider subsystem-specific list ownership behavior.
