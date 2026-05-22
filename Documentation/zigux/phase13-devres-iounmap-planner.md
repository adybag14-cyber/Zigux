# Phase 13 devres iounmap Planner

This bounded `P13-L09` helper-first packet lands one pure `devm_iounmap()` cleanup planning surface in `lib/devres.zig` while keeping live MMIO mapping state, device-tree walks, arch memtype mutation, and broader devres-group behavior blocked.

The planner stays intentionally narrow:
- exposes `planManagedIounmapCleanup(...)` as a helper-first cleanup decision instead of a live MMIO helper implementation
- records whether a tracked mapping owner generates cleanup work
- records whether helper-first cleanup unmaps the tracked mapping
- records whether a matching release record is consumed from devres during cleanup
- records whether a missing release record still unmaps the tracked mapping while surfacing a warn-on-release-miss outcome
- records whether the absence of a tracked mapping owner keeps cleanup inert
- keeps `devm_ioremap_np()`, `devm_of_iomap()`, `devm_arch_phys_wc_add()`, and `devm_arch_io_reserve_memtype_wc()` out of scope
- does not claim live MMIO mapping state, device-tree walks, arch memtype mutation, DMA attributes, or wider devres group teardown behavior

The helper packet now consists of:
- `lib/devres.zig`
- `zigux/tests/phase13_devres_iounmap_planner.zig`
- `Documentation/zigux/phase13-devres-iounmap-planner.md`
- `zigux/tests/phase13_devres_iounmap_planner_manifest.json`
- `scripts/zigux/check-phase13-devres-iounmap-planner.py`

Fixture governance stays helper-local:
- `zigux/tests/phase13_devres_iounmap_planner.zig` owns the tracked-mapping, missing-release-record, and no-mapping fixture coverage for `planManagedIounmapCleanup(...)`
- `zigux/tests/phase13_devres_iounmap_planner_manifest.json` is the packet-local owner map for that fixture and should stay aligned with the helper, note, and replay
- `scripts/zigux/check-phase13-devres-iounmap-planner.py` is the packet-local fail-closed checker and should stay aligned with the helper, planner note, manifest, and replay
- `Documentation/zigux/phase13-devres-survey.md` remains adjacent boundary evidence only and does not own the helper-local MMIO fixture packet

Adjacent boundary evidence stays unchanged:
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `scripts/zigux/check-phase13-devres-mmio-packet.py`

Standalone replay handles:
- `zig test --dep devres -Mroot=zigux/tests/phase13_devres_iounmap_planner.zig -Mdevres=lib/devres.zig`
- `python3 scripts/zigux/check-phase13-devres-iounmap-planner.py`
- `python3 scripts/zigux/check-phase13-devres-mmio-packet.py --self-test`
