# Phase 13 devres Slice

This bounded Phase 13 slice starts `lib/devres.zig` with a pure helper-first foothold anchored to `lib/devres.c`.

The current helper stays intentionally narrow:
  * preserves the already-landed managed `__devm_ioremap()` lifetime bookkeeping so the lane can distinguish retained release records from free-on-failure cleanup and keep the `devm_iounmap()` pointer match exact
  * extends that starter into the reviewable `__devm_ioremap_resource()` planning step by checking that a resource is memory-backed, computing the inclusive resource size, and switching plain managed ioremap requests to the non-posted variant when the resource flags demand it
  * keeps the landed `devm_of_iomap()` bridge as a pure planner that selects one translated resource by index, records the optional reported size as soon as translation succeeds, and then delegates to the existing managed-resource planner without pretending to read a live device tree
  * adds one adjacent resource-lifetime helper for `devm_arch_io_reserve_memtype_wc()` that models release-record allocation, the success path that retains the `(start, size)` range for detach-time cleanup, and the failure path that frees the release record without claiming any live arch memtype side effects
  * adds the landed token-style `devm_arch_phys_wc_add()` planner that retains the returned release token for detach-time `arch_phys_wc_del()` intent, frees the release record on negative token returns, and keeps live arch memtype side effects out of scope
  * records the managed request-region, remap, WC memtype reservation, and phys-WC token failure branches so the lane stays explicit about when the helper would surface `-EINVAL`, `-EBUSY`, `-ENOMEM`, or a negative token result, and when a failed remap, memtype reservation, or phys-WC token add would avoid keeping detach-time cleanup ownership

This slice does not claim live `devres_alloc_node()` ownership, actual MMIO mappings, resource-region side effects, ioport helpers, device-tree walking, live arch memtype reservation, devres groups, or the broader managed resource-family teardown behavior from `lib/devres.c`.

The next honest bounded step in this same lane is to keep the packet truthfulness reviewable by rereading `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` together before widening into live mappings, generic devres groups, or cross-subsystem device-resource state.
