# Phase 13 devres Slice

This bounded Phase 13 slice starts `lib/devres.zig` with a pure helper-first foothold anchored to `lib/devres.c`.

The current helper stays intentionally narrow:

- preserves the already-landed managed `__devm_ioremap()` lifetime bookkeeping so the lane can distinguish retained release records from free-on-failure cleanup and keep the `devm_iounmap()` pointer match exact
- extends that starter into the reviewable `__devm_ioremap_resource()` planning step by checking that a resource is memory-backed, computing the inclusive resource size, and switching plain managed ioremap requests to the non-posted variant when the resource flags demand it
- adds the adjacent `devm_ioremap_uc()` wrapper step as a pure helper that always drives the existing managed lifetime planner through the uncached path without claiming any live MMIO side effects
- adds the adjacent `devm_ioport_map()` / `devm_ioport_unmap()` lifetime planner so the lane now models release-record retention on successful ioport mapping, free-on-failure cleanup when the map call returns `NULL`, and exact detach-time pointer matching without claiming any live port-space side effects
- adds the adjacent `devm_ioremap_resource_wc()` wrapper step as a pure helper that always drives the existing managed-resource planner through the write-combined path without claiming any live MMIO side effects
- keeps the landed `devm_of_iomap()` bridge as a pure planner that selects one translated resource by index, records the optional reported size as soon as translation succeeds, and then delegates to the existing managed-resource planner without pretending to read a live device tree
- adds one adjacent token-style helper for `devm_arch_phys_wc_add()` that models release-record allocation, the success path that retains the returned WC token for detach-time cleanup, and the failure path that frees the release record without claiming any live MTRR or arch write-combining side effects
- adds one adjacent resource-lifetime helper for `devm_arch_io_reserve_memtype_wc()` that models release-record allocation, the success path that retains the `(start, size)` range for detach-time cleanup, and the failure path that frees the release record without claiming any live arch memtype side effects
- records the managed request-region, remap, UC wrapper, ioport-map, WC wrapper, WC token, and WC memtype reservation failure branches so the lane stays explicit about when the helper would surface `-EINVAL`, `-EBUSY`, or `-ENOMEM`, and when a failed remap, wrapper call, ioport map, token add, or memtype reservation would avoid keeping a detach-time release record

This slice does not claim live `devres_alloc_node()` ownership, actual MMIO mappings, resource-region side effects, live `ioport_map()` or `ioport_unmap()` side effects, device-tree walking, live `arch_phys_wc_add()` or arch memtype reservation side effects, devres groups, or the broader managed resource-family teardown behavior from `lib/devres.c`.

The next honest bounded step in this same lane is to keep the work helper-first and give `lib/devres.c` the same manifest-backed survey packet already used by the other active Phase 13 anchors, without widening into new helper behavior, live mappings, generic devres groups, or cross-subsystem device-resource state.
