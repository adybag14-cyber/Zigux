# Phase 3 chrdev notify slice

PHASE3_STATUS=active
PHASE3_SLICE=chrdev-notify-plan-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-chrdev-notify.py
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

This slice adds a bounded notification-planning `chrdev_notify` seam on top of `chrdev_complete`.

Boundaries:
- no live kernel dispatch
- no `struct notifier_block` ownership or callback interop
- no notifier-chain registration or unregister flow
- no `list_head` or `hlist` traversal beyond the existing `list-hlist-view-interop` substrate
- no notification queue implementation
- no wakeup or irq delivery
- no scheduler or worker integration

It only proves deterministic notification matching, delivered-vs-deferred-vs-dropped disposition, and bounded notification-budget metadata over a fixed completion result.

## Current Interop Evidence

On current `master`, this slice stays scalar-only:

- `zigux/helpers/chrdev_notify_plan.zig` models notify masks, budgets, cookies, and completion-derived disposition without embedding or traversing intrusive list nodes.
- `Documentation/zigux/phase3-list-hlist-slice.md` remains the only committed Zigux slice that owns reusable `list_head` or `hlist` interop semantics.
- the current dump-and-fixture replay for this slice stays in `zigux/tests/phase3_chrdev_notify_dump.zig` plus `zigux/tests/fixtures/phase3_chrdev_notify/expected.json`, which means current notifier behavior is planner evidence, not live chain execution.

Any future notifier-chain or list-backed callback work should extend the Phase 3 list or hlist substrate first, then add a new bounded notifier-facing slice instead of widening this planning helper in place.
