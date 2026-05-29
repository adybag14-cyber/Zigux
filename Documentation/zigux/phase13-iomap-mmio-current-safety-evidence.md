# Phase 13 iomap/MMIO Current Safety Evidence

This `P13-L03` evidence note records the current `master` behavior for the Phase 13 devres iomap/MMIO safety surface. It is evidence-only: it does not claim a new live MMIO implementation, a non-posted remap wrapper, live device-tree traversal, or arch memtype mutation.

## Grounding

- roadmap phase: Phase 13, shared subsystem helpers, with `lib/devres.c` as the Linux anchor and `lib/devres.zig` as the Zigux destination
- repo readback: `master-readback-2026-05-29`
- current helper blob: `lib/devres.zig` blob `3b77c4efd24092009e18f2986dd212e1af77b00e`
- current survey blob: `Documentation/zigux/phase13-devres-survey.md` blob `c3668b155fd67885463fc7895211021aea6b8c6c`
- current slice blob: `Documentation/zigux/phase13-devres-slice.md` blob `e64767929cd689dc47fbb6f1a267bc2327e26a5d`

## Exact Current Packet Evidence

- `Documentation/zigux/phase13-devres-iounmap-planner.md` blob `231cd9d019e00369b943598cfcc92b84b3bbd749`
- `zigux/tests/phase13_devres_iounmap_planner_manifest.json` blob `2c4873b0169dd8571e482ae3ea8fe208f4093fbe`
- `zigux/tests/phase13_devres_iounmap_planner.zig` blob `4f84ce08a9df314730e242b22302267cf57133b2`
- `Documentation/zigux/phase13-devres-iomap-planner.md` blob `e39973b8b47d2b4d8e432fd080509e21d7d6a4f8`
- `zigux/tests/phase13_devres_iomap_planner_manifest.json` blob `ecdb25acee029bfac70f47bb2de2704ea211120f`
- `zigux/tests/phase13_devres_iomap_planner.zig` blob `9915878b36ea85825b863c0da4c421874d76ef0d`
- `scripts/zigux/check-phase13-devres-iomap-planner.py` blob `5e51e36b858c865ff04936a790647f06ac7b1c7a`
- `scripts/zigux/check-phase13-devres-mmio-packet.py` blob `81bca7a47f83347c9931d6508e43bee65034025e`
- `scripts/zigux/check-phase13-devres-current-packet.py` blob `4f2d8ad430088676e26b6b28bf1153b7f5e768ea`

## Current Safety Behavior

The live helper descriptor records the bounded helper-first posture:

- `.provides_of_iomap_planning = true`
- `.provides_of_iomap_cleanup_handoff_planning = true`
- `.provides_iounmap_cleanup_planning = true`
- `.provides_ioport_unmap_call_planning = true`
- `.provides_arch_phys_wc_add_planning = true`
- `.touches_live_mmio = false`

The current iomap replay proves these safety decisions:

- translation-miss input stops before the managed ioremap-resource planning stage
- request-region denial preserves the translated size, marks the region denied, and keeps remap readiness false
- remap failure after a successful requested-region reservation records that the requested region must be released again
- non-posted requests remain attached to the planning surface through `requires_nonposted_ioremap` and `keeps_nonposted_mapping_type`, without claiming the blocked `devm_ioremap_np()` wrapper
- successful helper-first remap planning hands off to `planDeviceTreeIomapCleanupHandoff(...)`
- cleanup handoff consumes a matching release record when present
- cleanup handoff still unmaps the planned mapping and reports `warns_on_release_miss` when the release record is absent
- cleanup handoff stays inert before remap readiness

The current iounmap replay proves these safety decisions:

- a tracked mapping owner generates helper-first cleanup work
- a matching release record is consumed from devres during cleanup
- a missing release record still keeps the unmap action planned while surfacing a warn-on-release-miss outcome
- absence of a tracked mapping owner keeps cleanup inert

## Current Blocked Boundaries

The current packet still keeps these live MMIO and arch-memtype boundaries blocked:

- `phase13-devres-missing-devm-ioremap-np-surface`
- `phase13-devres-missing-devm-arch-phys-wc-add-surface`
- `phase13-devres-missing-devm-arch-io-reserve-memtype-wc-surface`
- `phase13-devres-live-mmio-mapping-state`
- `phase13-devres-live-device-tree-walks`
- `phase13-devres-live-arch-memtype-mutation`

The helper source was also read for the live-call markers that would break the evidence-only posture. Current `master` keeps these direct call markers absent from `lib/devres.zig`:

- `devm_ioremap_np(`
- `devm_of_iomap(`
- `devm_arch_phys_wc_add(`
- `devm_arch_io_reserve_memtype_wc(`

## Next Bounded Step

Before widening this lane into any helper-first non-posted, live ioport-unmap, or arch-memtype planner, rerun the packet-local guards and compare this evidence note against the current helper, manifests, replays, survey, and checker blobs. If the blobs or marker behavior drift, refresh the evidence first instead of claiming new helper progress.
