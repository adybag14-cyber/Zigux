# Phase 13 devres Slice

This bounded Phase 13 slice starts `lib/devres.zig` with a pure helper-first foothold anchored to `lib/devres.c`.

The current helper stays intentionally narrow:

- preserves the already-landed managed `__devm_ioremap()` lifetime bookkeeping so the lane can distinguish retained release records from free-on-failure cleanup and keep the `devm_iounmap()` pointer match exact
- extends that starter into the next bounded `__devm_ioremap_resource()` planning step by checking that a resource is memory-backed, computing the inclusive resource size, and switching plain managed ioremap requests to the non-posted variant when the resource flags demand it
- adds the adjacent `devm_of_iomap()` bridge as a pure planner that selects one translated resource by index, records the optional reported size as soon as translation succeeds, and then delegates to the existing managed-resource planner without pretending to read a live device tree
- models the pretty-name helper policy that prefers `"<device> <resource>"` when a resource name is present and falls back to the bare device name otherwise
- records the managed request-region and remap failure branches so the lane stays explicit about when the helper would surface `-EINVAL`, `-EBUSY`, or `-ENOMEM`, and when a failed remap would need the requested region released

This slice does not claim live `devres_alloc_node()` ownership, actual MMIO mappings, resource-region side effects, ioport helpers, device-tree walking, devres groups, or the broader managed resource-family teardown behavior from `lib/devres.c`.

The next honest bounded step in this same lane is to keep the work helper-first and add one small adjacent planner around another `ioremap` family wrapper such as `devm_ioremap_resource_wc()` without widening into live mappings, generic devres groups, or cross-subsystem device-resource state.
