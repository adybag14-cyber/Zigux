# Phase 13 notifier and list interop survey

This lane stays inside Phase 13 shared-helper reviewability and still does not claim a live generic notifier subsystem.

Current repo state on `master`:

- last inspected current-master commit: `66b55d8a9a800345097f3c04b9f95130b1f8d0b8`
- lane key: `P13-L19`
- `zigux/bindings/abi.zig` still carries the preexisting `ListHeadRef` and `HListHeadRef` footholds that make list-shaped interop reusable
- `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` still summarize bounded `list_head` and `hlist_head` traversal without touching live mutation
- `zigux/bindings/notifier_abi.zig` now mirrors the generic read-only notifier shapes through `NotifierBlockRef`, `RawNotifierHeadRef`, `NotifierChainView`, and `NotifierChainSummary`
- `zigux/helpers/notifier_chain_view.zig` now provides the bounded raw-notifier traversal helper with empty, terminated, truncated, self-loop, and priority-order coverage
- `include/zigux/notifier_abi.h` now mirrors that same read-only packet on the exported C side, keeps `zigux_notifier_chain_view_valid()` explicit for reserved or zero-bounded views, and keeps the dedicated exported C header small instead of widening `include/linux/zigux.h`
- the list and hlist helpers still share the same small companion API shape: `viewFromHead`, `isEmpty`, `length`, and `summarize`
- the notifier helper keeps that same bounded shape while also exposing direct priority-order convenience through `hasNonincreasingPriorityOrder` and `zigux_notifier_chain_has_nonincreasing_priority_order()`
- `zigux/tests/phase13_notifier_list_manifest.json` now records the notifier binding, helper, dedicated exported C header, and shared Phase 13 build hook as landed packet-local evidence instead of as inherited preexisting groundwork
- `zigux/tests/phase13_build.zig` still compiles both the reviewability gate and the new notifier helper directly inside the shared Phase 13 replay
- notifier-shaped logic outside this packet is still present only in the chrdev-specific planner family such as `zigux/helpers/chrdev_notify_plan.zig`
- `include/linux/notifier.h`, `include/linux/acpi_amd_wbrf.h`, `include/net/dsa.h`, and `include/linux/watchdog.h` still provide the public upstream anchors that justify this mirror as a read-only reviewability step

Why this matters for Phase 13:

- the roadmap still names `libfs`, `devres`, and Landlock as the tranche anchors, so this packet remains roadmap-adjacent helper infrastructure rather than a new named Phase 13 pillar
- the earlier survey-only gap is now closed on both sides of the Zigux boundary through the Zig binding, the Zig helper, and the dedicated exported C header
- the shared companion API shape across the list and hlist helpers keeps the interop story more reviewable without widening it into mutation or execution behavior
- the direct priority-order convenience keeps the already-landed summary flag reviewable without forcing downstream readers to decode flags by hand
- the dedicated exported C header makes the shared notifier packet reusable for C-facing review surfaces without forcing broader kernel helper churn
- the exported C-side validity guard keeps reserved or zero-bounded view rejection reviewable before callers rely on empty, length, summarize, or priority-order results across the boundary
- the packet-local note now keeps the direct priority-order convenience reviewable on both the Zig and C sides while still keeping the dedicated exported C header small
- the list and hlist view surface remains the natural companion for this work, which keeps the interop story helper-first and read-only
- registration, callback execution, SRCU, and blocking notifier semantics remain out of scope
