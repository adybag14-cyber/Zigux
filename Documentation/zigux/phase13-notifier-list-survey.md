# Phase 13 notifier and list interop survey

This lane stays inside Phase 13 shared-helper reviewability and does not claim a new generic notifier helper.

Current repo state on `master`:

- reviewed against live `master` `3d734fefe5c64e29bed0dc38d69f64cae45be7ba`
- `zigux/bindings/abi.zig` already exposes `ListHeadRef` and `HListHeadRef`, so list-shaped interop has a reusable ABI foothold
- `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` already summarize bounded `list_head` and `hlist_head` traversal without touching live mutation
- `zigux/tests/build.zig` already replays those list helpers under the Phase 3 helper bundle
- notifier-shaped logic is present only in the chrdev-specific planner family such as `zigux/helpers/chrdev_notify_plan.zig`
- a driver-local notifier/list anchor is also already visible in the landed Phase 11 `drivers/tty/hvc/hvc_console.h` plus `drivers/tty/hvc/hvc_console.zig` parity surface, where `struct hvc_struct` carries `struct list_head next` and `hv_ops` exposes notifier callbacks without turning that header into a shared helper API
- a generic notifier header anchor is already present in `include/linux/acpi_amd_wbrf.h`, which includes `include/linux/notifier.h` and publishes `amd_wbrf_register_notifier()` plus `amd_wbrf_unregister_notifier()` around `struct notifier_block *nb` without yet giving Zigux a shared ABI or helper surface for that contract
- there is still no generic notifier ABI surface in `zigux/bindings/abi.zig` and no shared helper under `zigux/helpers/` that models notifier-chain linkage directly

Why this matters for Phase 13:

- the roadmap treats Phase 13 as the shared helper tranche, so list and notifier surfaces belong here only if they stay bounded and helper-first
- the current list side is reusable enough to survey today, and there is now concrete driver-local evidence that notifier callbacks can coexist with `list_head` linkage without yet implying a shared helper contract
- the generic header anchor narrows the remaining gap: upstream C already exposes a reusable `notifier_block` contract, but Zigux still lacks the tiny read-only ABI and helper surfaces that would make that contract reviewable on the Zig side
- that mismatch means later helper work such as list-backed cursor or chain bookkeeping can accidentally overstate notifier readiness unless the gap is recorded explicitly

The next honest bounded step in this same lane is a tiny generic notifier ABI foothold, paired with one helper-first survey of notifier-chain linkage against the existing list and hlist view surface. That follow-up must stay out of live callback registration, chain execution, SRCU or blocking semantics, and any new chrdev delivery expansion.
