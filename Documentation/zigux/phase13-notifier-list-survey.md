# Phase 13 Notifier List Survey

## Purpose

This note records the bounded Phase 13 notifier or list evidence that current `master` can still honestly treat as adjacent release-surface context for the shared subsystem-helper packet. The goal is contributor reviewability, not a new replay lane.

## Roadmap fit

Phase 13 in the Zigux roadmap is the shared-subsystem-helper tranche around bounded helper layers such as `fs/libfs.c`, `lib/devres.c`, and the Landlock helpers. The notifier or list packet stays adjacent to that tranche because the current release guidance still uses it as boundary evidence for notifier-oriented truthfulness work without promoting it into a separate shared replay count.

## Survey Snapshot

- owner posture: adjacent notifier evidence rather than helper-lane ownership
- lane key: `P13-L18`
- evidence refresh lane: `P13-L15`
- surveyed commit: `master-readback-2026-06-08`
- surveyed state: `current master` authenticated readback refreshed on `2026-06-08`
- owner-map reminder: `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` keeps adjacent notifier evidence outside the four roadmap-owned helper anchors, so this note stays adjacent release-surface evidence instead of claiming a fifth helper lane
- roadmap-adjacent reviewability evidence only
- shared Phase 13 build intentionally omits this packet, so the adjacent notifier surfaces stay reviewable without adding a counted helper replay to the shared Phase 13 bundle

## Current Repo Reality

As of `2026-06-08`, current `master` keeps this adjacent notifier-facing packet explicit through:

- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/notifier_chain_view.zig`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `include/zigux/abi.h`
- `include/zigux/notifier_abi.h`
- `zigux/Makefile`
- `drivers/tty/hvc/hvc_console.h`
- `scripts/zigux/validate-phase13-release.py`

Current authenticated readback fixes that shipped adjacent packet to these exact file states:

- `zigux/bindings/notifier_abi.zig` blob `37f8abdb8883476a916e9fdd8b8f35798e677d46` keeps the bounded read-only ABI foothold explicit through `NotifierResult`, `resultFromInt()`, `resultIsKnown()`, `resultStopsChainValue()`, `resultStopsChain()`, `NotifierBlock`, `NotifierChainPriorityIncrease`, `ListHead`, `HListHead`, `HListNode`, `chainHasNonincreasingPriority()`, `firstChainPriorityIncrease()`, `listIsEmpty()`, `firstBrokenBacklink()`, `listHasConsistentBacklinks()`, `firstPprevMatchesHead()`, `firstBrokenPrevLink()`, and `hlistHasConsistentPrevLinks()`, plus layout and witness tests for result-alignment, empty, single-node, descending, broken-link, and empty-sentinel list cases.
- `zigux/helpers/notifier_chain_view.zig` blob `ff94005922bd7ed6cc78949f8b13ea2e5ef60bff` keeps the notifier-chain helper read-only through `NotifierChainView.isEmpty()`, `first()`, `last()`, `len()`, `iterator()`, `hasNonincreasingPriority()`, and `firstPriorityIncrease()`, plus bounded witness tests for null-head, single-node, descending-priority, and first-priority-increase cases.
- `zigux/helpers/list_view.zig` blob `0d0400bb8f1239fdd0338e21dfc5323f5fda32c9` keeps the `list_head` helper read-only through `ListView.isEmpty()`, `first()`, `last()`, `len()`, `iterator()`, `hasConsistentBacklinks()`, and `firstBrokenBacklink()`.
- `zigux/helpers/hlist_view.zig` blob `425e7f8788d550ff845849979f84e6bb9242f0d9` keeps the `hlist` helper read-only through `HListView.isEmpty()`, `first()`, `len()`, `firstPprevMatchesHead()`, `hasConsistentPrevLinks()`, `firstBrokenPrevLink()`, and `tailNextIsNull()`.
- `include/zigux/abi.h` blob `8b7ee51e9d432f992dcc8ae885c12f0388c007e7` mirrors the same bounded C-side packet through `struct zigux_notifier_block`, `struct zigux_list_head`, `struct zigux_hlist_head`, `zigux_notifier_result_is_known()`, `zigux_notifier_result_stops_chain()`, `zigux_notifier_chain_has_nonincreasing_priority()`, `zigux_notifier_first_chain_priority_increase()`, `zigux_list_is_empty()`, `zigux_list_first_broken_backlink()`, `zigux_list_has_consistent_backlinks()`, `zigux_hlist_first_pprev_matches_head()`, `zigux_hlist_first_broken_prev_link()`, `zigux_hlist_has_consistent_prev_links()`, and `zigux_hlist_tail_next_is_null()`.
- `include/zigux/notifier_abi.h` blob `e69c2756f1b63167602fb9d2bf2337937f4aa6a8` is directly readable again as a dedicated C-side notifier/list ABI header through `ZIGUX_NOTIFIER_DONE`, `ZIGUX_NOTIFIER_OK`, `ZIGUX_NOTIFIER_STOP`, `struct zigux_notifier_block`, `zigux_notifier_chain_priority_increase`, `struct zigux_list_head`, `struct zigux_hlist_head`, `struct zigux_hlist_node`, `zigux_notifier_result_is_known()`, `zigux_notifier_result_stops_chain()`, `zigux_notifier_chain_has_nonincreasing_priority()`, `zigux_notifier_first_chain_priority_increase()`, `zigux_list_is_empty()`, and the list/hlist backlink witness helpers.
- `drivers/tty/hvc/hvc_console.h` blob `57f1542b3e6f1901f444bc2d94b5e438f14eb9b3` still keeps the adjacent HVC notifier declarations visible through `notifier_add_irq`, `notifier_del_irq`, and `notifier_hangup_irq` beside the `hv_ops` notifier callbacks.
- `zigux/tests/phase13_notifier_list_manifest.json` blob `f2c7ba99055597275c24a3601201f8b72583f36e`, `zigux/tests/phase13_notifier_list_reviewability.zig` blob `6d89c65a0582ed3d3dfe35d99093d97be46c13e0`, `scripts/zigux/check-phase13-notifier-packet.py` blob `be20b2bbd5c0b6bf73f0a5b1b03ea2d15bf06875`, and `scripts/zigux/validate-phase13-release.py` blob `ebde21e34e28766379bd7fcb5f6b96a5f6bb001e` still gate the adjacent packet and still frame the shared Phase 13 build shard, priority-signal companion, and Makefile route names as repo-reality gaps rather than shipped evidence.
- `zigux/Makefile` blob `47952e68dfa7f1579860db9b6bed6a6c7fd361d9` is present on current `master`, but its live body still does not expose `make -C zigux phase13-validate` or `make -C zigux phase13`, so keep the returned file distinct from those still-missing route names instead of treating it as a shared build handle for this adjacent packet.

The shipped adjacent `zigux/bindings/notifier_abi.zig` foothold keeps notifier priority ordering plus `list_head` and `hlist` layout witnesses explicit without claiming callback execution, registration, SRCU, or blocking-notifier semantics.

The shipped adjacent `zigux/helpers/notifier_chain_view.zig`, `zigux/helpers/list_view.zig`, and `zigux/helpers/hlist_view.zig` helpers walk notifier-chain, `list_head`, and `hlist` links in read-only form, report ordering, empty-sentinel, backlink, `pprev`, broken-prev, or tail-null witnesses, and stop short of mutation or notifier callback behavior.

The shipped adjacent `include/zigux/abi.h` foothold mirrors that same bounded posture for C-side callers that only need read-only notifier ordering or list-link truthfulness, including the exported tail-null witness `zigux_hlist_tail_next_is_null()`.

The dedicated adjacent `include/zigux/notifier_abi.h` header is current repo evidence again, so future Phase 13 notifier follow-through should treat it as shipped adjacent header evidence rather than as a missing direct companion.

The focused checker `scripts/zigux/check-phase13-notifier-packet.py` now keeps that adjacent packet fail-closed around the survey note, manifest, reviewability gate, ABI foothold, read-only notifier and list helpers, the exported list-empty, first-node `pprev`, broken-prev, consistent-prev, and tail-next hlist witnesses, and the Linux-side HVC notifier declarations. The focused Zig gate `zigux/tests/phase13_notifier_list_reviewability.zig` keeps the manifest, checker, exported list-empty, first-node `pprev`, broken-prev, consistent-prev, and tail-next witnesses, and returned-Makefile-versus-missing-route distinction visible without widening the shared Phase 13 build packet.

Current direct readback in this lane still does not rematerialize `scripts/zigux/check-phase13-notifier-priority-signal.py`, `zigux/tests/phase13_build.zig`, `make -C zigux phase13-validate`, or `make -C zigux phase13`, so keep those paths framed as repo-reality gaps instead of shipped adjacent notifier evidence until a fresh reread proves they returned on current `master`.

## Review Posture

Keep this packet framed as adjacent Phase 13 evidence:

- it supports the broader shared-helper release packet without becoming a fifth helper anchor
- it keeps the shipped `zigux/bindings/notifier_abi.zig` plus `include/zigux/abi.h` ABI footholds explicit as adjacent notifier and list/hlist interop evidence, including the returned `listIsEmpty()` plus `zigux_list_is_empty()` sentinel witness, the exported first-node `pprev` witness `zigux_hlist_first_pprev_matches_head()`, and the exported tail-null witness `zigux_hlist_tail_next_is_null()`
- it keeps the dedicated `include/zigux/notifier_abi.h` header explicit as returned adjacent notifier/list ABI evidence
- it keeps the shipped `zigux/helpers/notifier_chain_view.zig`, `zigux/helpers/list_view.zig`, and `zigux/helpers/hlist_view.zig` helper surfaces explicit as bounded notifier-chain, `list_head`, and `hlist` interop evidence
- it keeps `scripts/zigux/validate-phase13-release.py` explicit as the shipped shared release-discipline validator companion for this adjacent packet without treating it as a direct notifier-only checker
- it keeps the Linux-side `drivers/tty/hvc/hvc_console.h` notifier declarations explicit as adjacent evidence without claiming HVC runtime parity
- it keeps the focused checker and reviewability pair explicit through `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, and `zigux/tests/phase13_notifier_list_reviewability.zig`
- it keeps the missing priority-signal companion and still-missing `make -C zigux phase13-validate` plus `make -C zigux phase13` route names framed as repo-reality gaps while keeping the returned `zigux/Makefile` file itself distinct from those gaps
- it does not add extra shared replay steps beyond the current contributor-facing reminder packet
- it should not claim broader callback, registration, SRCU, blocking-notifier, or HVC runtime parity on top of these read-only adjacent surfaces

## Contributor Checks

When the adjacent Phase 13 contributor packet changes, re-read these surfaces together:

- `Documentation/zigux/phase13-notifier-list-survey.md`
- `Documentation/zigux/phase13-notifier-summary-gap.md`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/notifier_chain_view.zig`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `include/zigux/abi.h`
- `include/zigux/notifier_abi.h`
- `drivers/tty/hvc/hvc_console.h`
- `scripts/zigux/validate-phase13-release.py`

Keep `scripts/zigux/check-phase13-notifier-priority-signal.py`, `zigux/tests/phase13_build.zig`, `make -C zigux phase13-validate`, and `make -C zigux phase13` framed as repo-reality gaps until they rematerialize on current `master`.

## Non-goals

- This note does not claim a new shared-helper replay count.
- This note does not claim broader HVC runtime parity.
- This note does not reopen frozen or study-only roadmap areas.
