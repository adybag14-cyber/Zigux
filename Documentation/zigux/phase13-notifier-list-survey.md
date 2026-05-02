# Phase 13 notifier and list interop survey

This lane stays inside Phase 13 shared-helper reviewability and still does not claim a live generic notifier subsystem.

Current repo state on `master`:

- last inspected current-master commit: `66b55d8a9a800345097f3c04b9f95130b1f8d0b8`
- lane key: `P13-L18`
- `zigux/bindings/abi.zig` still carries the preexisting `ListHeadRef` and `HListHeadRef` footholds that make list-shaped interop reusable
- `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` still summarize bounded `list_head` and `hlist_head` traversal without touching live mutation
- `zigux/bindings/notifier_abi.zig` now mirrors the generic read-only notifier shapes through `NotifierBlockRef`, `RawNotifierHeadRef`, `NotifierChainView`, and `NotifierChainSummary`
- `zigux/helpers/notifier_chain_view.zig` now provides the bounded raw-notifier traversal helper with empty, terminated, truncated, and self-loop coverage
- the list, hlist, and raw-notifier helpers now share the same small companion API shape: `viewFromHead`, `isEmpty`, `length`, and `summarize`
- `zigux/tests/phase13_build.zig` now compiles both the reviewability gate and the new notifier helper directly inside the shared Phase 13 replay
- notifier-shaped logic outside this packet is still present only in the chrdev-specific planner family such as `zigux/helpers/chrdev_notify_plan.zig`
- `include/linux/notifier.h`, `include/linux/acpi_amd_wbrf.h`, `include/net/dsa.h`, and `include/linux/watchdog.h` still provide the public upstream anchors that justify this mirror as a read-only reviewability step

Why this matters for Phase 13:

- the roadmap still names `libfs`, `devres`, and Landlock as the tranche anchors, so this packet remains roadmap-adjacent helper infrastructure rather than a new named Phase 13 pillar
- the old survey-only gap is now closed with a tiny reusable Zigux-side generic notifier foothold
- the shared companion API shape across the list, hlist, and notifier helpers makes the interop story more reviewable without widening it into mutation or execution behavior
- the list and hlist view surface remains the natural companion for this work, which keeps the interop story helper-first and read-only
- registration, callback execution, SRCU, and blocking notifier semantics remain out of scope
- the explicit helper and build-hook presence means later runs can tell the difference between this landed bounded foothold and any future wider notifier behavior
