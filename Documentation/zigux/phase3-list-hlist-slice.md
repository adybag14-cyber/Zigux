# Phase 3 list/hlist Slice

This note records one bounded shared-helper starter-plus-dump packet for the existing Phase 3 `list_head` and `hlist` helpers on current `master`.

## Current Slice

- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `zigux/bindings/notifier_list_shape.zig`
- `zigux/tests/phase3_list_hlist_starter_packet.zig`
- `zigux/tests/phase3_list_hlist_starter_packet_build.zig`
- `scripts/zigux/check-phase3-list-hlist-starter-packet.py`
- `zigux/tests/phase3_list_hlist_dump.zig`
- `zigux/tests/phase3_list_hlist_dump_build.zig`
- `zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c`
- `zigux/tests/fixtures/phase3_list_hlist/expected.json`
- `zigux/tests/fixtures/phase3_list_hlist_manifest.json`
- `scripts/zigux/check-phase3-list-hlist.py`
- `zigux/Makefile`

## Bounded Contract

- `list_view.zig` keeps sentinel emptiness, first and last node discovery, bounded forward iteration, length counting, and backlink break detection explicit for circular `list_head` chains.
- `hlist_view.zig` keeps empty-head detection, first-node discovery, bounded forward iteration, length counting, head-to-first `pprev` validation, tail-null validation, and first broken prev-link detection explicit for singly linked `hlist` chains.
- `zigux/bindings/notifier_list_shape.zig` keeps the notifier-priority witness plus the list and hlist shape helpers directly reusable through one bounded shared relay companion, including emptiness, length, backlink, `pprev`, and tail-null checks, without widening into mutation helpers or container-of recovery.
- `phase3_list_hlist_starter_packet.zig` proves that both helpers keep the empty sentinels, ordered chains, and first broken backlink witnesses explicit without widening into container-of traversal, mutation helpers, or broader subsystem ownership semantics.
- `phase3_list_hlist_dump.zig` and `phase3_list_hlist_c_harness.c` replay the same bounded list and hlist witnesses through Zig and C so the helper-local answers stay parity-checked without widening into exported ABI structs or intrusive mutation coverage.
- `expected.json` keeps the tiny parity packet directly readable through stable node-index and backlink-label summaries instead of address-specific dumps.
- `zigux/tests/fixtures/phase3_list_hlist_manifest.json` keeps the bounded starter-plus-dump packet machine-readable through its packet files, replay routes, and explicit next safe step.
- `zigux/Makefile` exposes bounded `phase3-list-hlist-starter-packet` and `phase3-list-hlist-dump` wrappers so the helper-local packet stays reachable through the shared Zigux rerun surface without widening into the aggregate Phase 3 lane.
- `scripts/zigux/check-phase3-list-hlist.py` fail-closes the helper-local packet so the slice note, helper files, starter replay, dump replay, C harness, expected fixture, manifest, and wrapper surface stay aligned.

## Replay Route

- `zig test zigux/bindings/notifier_list_shape.zig`
- `python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py`
- `zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig`
- `make -C zigux phase3-list-hlist-starter-packet`
- `python3 scripts/zigux/check-phase3-list-hlist.py --self-test`
- `python3 scripts/zigux/check-phase3-list-hlist.py --repo-root . --zig zig --cc gcc`
- `zig build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig`
- `make -C zigux phase3-list-hlist-dump`

## Scope

This slice stays intentionally helper-local even after parity expansion. It does not claim exported ABI structs, intrusive container recovery helpers, list mutation semantics, or wider subsystem-specific list ownership behavior. The new shared relay companion keeps the same lane honest by reusing the existing notifier/list/hlist witness surface instead of opening a broader ABI rewrite. Any future same-lane follow-through should stay narrowed to shared validator-entrypoint alignment, the existing wrapper surface, another explicitly bounded shared relay helper, or another explicitly bounded helper-local replay route after rereading current `master`.
