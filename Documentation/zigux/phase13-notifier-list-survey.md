# Phase 13 notifier and list interop survey

This lane stays inside Phase 13 shared-helper reviewability and does not claim a new generic notifier helper.

The Phase 13 roadmap names `fs/libfs.c`, `lib/devres.c`, and the Landlock slices as the tranche's concrete anchors. This notifier/list packet is roadmap-adjacent reviewability evidence only: it explains how preexisting shared list surfaces relate to the still-missing generic notifier surface without promoting notifier/list interop to a new named anchor.

Current repo state on `master`:

- last inspected current-master commit: `66b55d8a9a800345097f3c04b9f95130b1f8d0b8`
- lane key: `P13-L17`
- `zigux/bindings/abi.zig` already exposes `ListHeadRef` and `HListHeadRef`, so list-shaped interop has a reusable ABI foothold
- `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` already summarize bounded `list_head` and `hlist_head` traversal without touching live mutation
- `zigux/tests/build.zig` already replays those list helpers under the Phase 3 helper bundle
- `zigux/tests/phase13_build.zig` still replays `zigux/tests/phase13_notifier_list_reviewability.zig`, so this packet remains machine-checkable inside the Phase 13 shared-helper bundle
- notifier-shaped logic is present only in the chrdev-specific planner family such as `zigux/helpers/chrdev_notify_plan.zig`
- a driver-local notifier/list anchor is also already visible in the landed Phase 11 `drivers/tty/hvc/hvc_console.h` plus `drivers/tty/hvc/hvc_console.zig` parity surface, where `struct hvc_struct` carries `struct list_head next` and `hv_ops` exposes notifier callbacks without turning that header into a shared helper API
- a generic notifier header anchor is already present in `include/linux/acpi_amd_wbrf.h`, which includes `include/linux/notifier.h` and publishes `amd_wbrf_register_notifier()` plus `amd_wbrf_unregister_notifier()` around `struct notifier_block *nb` without yet giving Zigux a shared ABI or helper surface for that contract
- `include/linux/notifier.h` also already fixes the field-level read-only shape that any future Zigux ABI would need to mirror: `struct notifier_block` carries `notifier_call`, `next`, and `priority`, and `struct raw_notifier_head` anchors the chain through `head`
- a public list-plus-notifier coexistence anchor is also already visible in `include/net/dsa.h`, where `struct dsa_switch_tree` carries `list`, `ports`, `nh`, and `rtable` while the same header's `struct dsa_switch` carries a notifier listener `nb`, which makes shared read-only notifier or list adjacency reviewable without claiming a Zigux helper yet
- a same-struct public notifier-plus-list anchor is also already visible in `include/linux/watchdog.h`, where `struct watchdog_device` carries `reboot_nb`, `restart_nb`, and `pm_nb` notifier blocks plus the deferred `list_head` in one exported read-only shape, which tightens the future Zigux mirroring target without widening into helper delivery
- there is still no generic notifier ABI surface in `zigux/bindings/abi.zig`, no shared notifier helper file or build replay hook, and no helper under `zigux/helpers/` that models notifier-chain linkage directly

Why this matters for Phase 13:

- the roadmap treats Phase 13 as the shared helper tranche, but its named anchors are still `libfs`, `devres`, and Landlock, so notifier/list evidence belongs here only as a bounded helper-first interop note
- the explicit `P13-L17` lane marker keeps this existing reviewability packet from silently drifting across adjacent notifier evidence lanes when later runs only refresh head pins or upstream anchor evidence
- the current list side is reusable enough to survey today, and there is now concrete driver-local evidence that notifier callbacks can coexist with `list_head` linkage without yet implying a shared helper contract
- the generic header anchor narrows the remaining gap: upstream C already exposes a reusable `notifier_block` contract, but Zigux still lacks the tiny read-only ABI and helper surfaces that would make that contract reviewable on the Zig side
- the field-level notifier layout anchor makes that remaining gap sharper: the missing Zigux ABI is no longer just about naming the contract, but about mirroring a specific read-only chain shape without over-claiming registration or execution semantics
- the public list-plus-notifier coexistence anchor sharpens the adjacency question further: shared public headers already keep `list_head`, `raw_notifier_head`, and `notifier_block` shapes near each other, and this survey packet now records that DSA header explicitly instead of leaving it prose-only, so the missing Zigux work is clearly about mirroring those read-only shapes rather than discovering whether the upstream surface exists
- the same-struct public notifier-plus-list anchor sharpens that claim one notch further: `watchdog_device` shows exported `notifier_block` fields and a `list_head` living in one concrete public layout, so a later Zigux ABI foothold can be judged against a stronger read-only shape than header-level coexistence alone
- the explicit Phase 13 replay hook matters too: because `zigux/tests/phase13_build.zig` still runs `phase13_notifier_list_reviewability.zig`, future generic-notifier work cannot silently widen the packet without first updating the evidence and keeping the same bounded posture explicit
- the reviewability gate now follows the manifest's explicit ABI or helper or build-surface posture instead of hard-coding permanent absence, so a later ABI-only foothold can land without being mistaken for helper delivery
- the explicit no-helper or no-build-hook proof keeps this lane from drifting into false positives once a later run starts a real notifier helper, because the current reviewability gate now fails as soon as a `zigux/helpers/notifier_chain_view.zig` style file or matching replay hook lands without the survey packet moving with it
- that mismatch means later helper work such as list-backed cursor or chain bookkeeping can accidentally overstate notifier readiness unless the gap is recorded explicitly

The next honest bounded step in this same lane is a tiny generic notifier ABI foothold, paired with one helper-first survey of notifier-chain linkage against the existing list and hlist view surface. That follow-up must stay out of live callback registration, chain execution, SRCU or blocking semantics, and any new chrdev delivery expansion.
