# Phase 13 devres Slice

This bounded Phase 13 slice starts `lib/devres.zig` with a pure helper-first foothold anchored to `lib/devres.c`.

The current helper stays intentionally narrow:

- preserves the already-landed managed `__devm_ioremap()` lifetime bookkeeping so the lane can distinguish retained release records from free-on-failure cleanup and keep the `devm_iounmap()` pointer match exact
- extends that starter into the reviewable `__devm_ioremap_resource()` planning step by checking that a resource is memory-backed, computing the inclusive resource size, and switching plain managed ioremap requests to the non-posted variant when the resource flags demand it
- keeps the landed `devm_of_iomap()` bridge as a pure planner that selects one translated resource by index, records the optional reported size as soon as translation succeeds, and then delegates to the existing managed-resource planner without pretending to read a live device tree; this keeps the devm_of_iomap() bridge as a pure planner
- adds one adjacent resource-lifetime helper for `devm_arch_io_reserve_memtype_wc()` that models release-record allocation, the success path that retains the `(start, size)` range for detach-time cleanup, and the failure path that frees the release record without claiming any live arch memtype side effects
- adds one matching token-style planner for `devm_arch_phys_wc_add()` that records the retained release token on success, frees the release record on negative token returns, and keeps the detach-time remove path reviewable without touching live arch memtype state
- records the managed request-region, remap, and WC memtype reservation failure branches so the lane stays explicit about when the helper would surface `-EINVAL`, `-EBUSY`, or `-ENOMEM`, and when a failed remap or memtype reservation would avoid keeping a detach-time release record
  or when a failed phys WC token add would avoid keeping a detach-time removal record

This slice does not claim live `devres_alloc_node()` ownership, actual MMIO mappings, resource-region side effects, ioport helpers, device-tree walking, live arch memtype reservation or removal side effects, devres groups, or the broader managed resource-family teardown behavior from `lib/devres.c`.

The next honest bounded step in this same lane is to keep the work steady unless current repo evidence reveals another equally small exported-helper gap. Do not widen into live mappings, generic devres groups, or cross-subsystem device-resource state just to keep the file moving.
