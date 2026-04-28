# Phase 13 devres MMIO safety survey

This lane stays inside the Phase 13 shared-helper tranche and records the current `lib/devres.c` MMIO safety surface without claiming live device-resource teardown, live MMIO mappings, or generic devres-group ownership.

Current repo state on `master`:

- reviewed against live `master` `0d796d2d0bfe4d85c0b15fe27a6f4dfc626e0288`
- `lib/devres.zig` already anchors a helper-first `DevresHelperLab` on `lib/devres.c`
- `zigux/tests/phase13_devres.zig` already exercises managed `__devm_ioremap()` lifetime planning, `__devm_ioremap_resource()` planning, `devm_of_iomap()` translation handoff, `devm_ioport_map()` lifetime bookkeeping, `devm_arch_phys_wc_add()` token retention, and `devm_arch_io_reserve_memtype_wc()` range retention
- `Documentation/zigux/phase13-devres-slice.md` already marks the helper boundary clearly, but until this packet landed the MMIO safety posture was not recorded in the same manifest-backed survey shape as the other active Phase 13 anchors
- `zigux/Makefile` and `zigux/tests/phase13_build.zig` already expose the shared Phase 13 replay entrypoints that this survey now joins

Why this matters for Phase 13:

- the roadmap treats Phase 13 as the shared helper tranche, so `lib/devres.c` belongs here only as long as it stays helper-first and reviewable
- MMIO- and iomap-adjacent helpers are exactly the kind of risky surface that the roadmap says should remain wrapper-first before any wider runtime claims
- recording the current helper surface in a manifest-backed survey stops later runs from mistaking these planners for live mapping parity or from reopening the already-landed helper-only work as if it were still missing

What is landed today:

- managed `__devm_ioremap()` lifetime planning, including retained release records on success and free-on-failure cleanup when mapping returns `NULL`
- the `devm_ioremap_uc()` wrapper path and exact `devm_iounmap()` pointer-match release behavior
- managed `__devm_ioremap_resource()` planning around memory-resource validation, inclusive size calculation, pretty-name construction, request-region gating, remap cleanup, and non-posted fallback when the resource flags demand it
- the adjacent `devm_ioremap_resource_wc()` wrapper path without widening into live write-combined mappings
- `devm_of_iomap()` planning around translated resource selection, optional size reporting, and delegation into the managed-resource planner without walking a live device tree
- `devm_ioport_map()` and `devm_ioport_unmap()` lifetime bookkeeping without claiming live port-space side effects
- token-style `devm_arch_phys_wc_add()` release planning and range-style `devm_arch_io_reserve_memtype_wc()` release planning without claiming live memtype mutation

What remains explicitly blocked:

- live MMIO side effects such as `devres_alloc_node()` ownership, `devres_add()` installation, `devm_request_mem_region()` side effects, and direct `ioremap()` or `iounmap()` execution against real hardware state
- live device-tree walking, overlapping resource arbitration, or broader `struct device_node` ownership beyond the pure `devm_of_iomap()` planner boundary
- live MTRR or arch memtype state mutation beyond the token-style and range-style detach bookkeeping planners

The next honest bounded step for this lane is to keep the survey packet aligned with the helper lab and shared Phase 13 replay. New product work should move in the dedicated helper lanes rather than reopening this now-recorded MMIO safety survey gap.
