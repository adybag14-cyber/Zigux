# Phase 13 devres iomap Planner

This bounded `P13-L02` helper-first packet lands one pure `devm_of_iomap()` planning surface in `lib/devres.zig` while keeping live MMIO mapping state, device-tree walks, non-posted wrapper ownership, and arch memtype mutation blocked.

The planner stays intentionally narrow:
- exposes `planDeviceTreeIomap(...)` as a helper-first iomap decision instead of a live device-tree or MMIO helper implementation
- records whether address translation reaches the managed ioremap-resource stage
- records whether translated size is preserved when a requested region is denied as busy
- records whether a denied region request blocks remap progress without claiming live mapping state
- records whether a requested region is released again when remap later fails
- records whether the requested non-posted mapping type stays attached to the planning surface
- records whether a translated helper-first remap would require the still-blocked `devm_ioremap_np()` wrapper before any live MMIO mapping state is claimed
- records whether a successful helper-first remap hands off to `devm_iounmap()` cleanup planning
- records whether the cleanup handoff consumes the matching release record or still warns when the release record is missing
- keeps `devm_ioremap_np()`, `devm_iounmap()`, `devm_arch_phys_wc_add()`, and `devm_arch_io_reserve_memtype_wc()` out of scope
- does not claim live MMIO mapping state, device-tree walks, arch memtype mutation, DMA attributes, or broader devres group teardown behavior

The helper packet now consists of:
- `lib/devres.zig`
- `zigux/tests/phase13_devres_iomap_planner.zig`
- `Documentation/zigux/phase13-devres-iomap-planner.md`
- `zigux/tests/phase13_devres_iomap_planner_manifest.json`
- `scripts/zigux/check-phase13-devres-iomap-planner.py`

Fixture governance stays helper-local:
- `zigux/tests/phase13_devres_iomap_planner.zig` owns the translation-miss, request-region-denial, non-posted-wrapper, remap-failure, cleanup-handoff, and cleanup-release-miss fixture coverage for `planDeviceTreeIomap(...)` and `planDeviceTreeIomapCleanupHandoff(...)`
- `zigux/tests/phase13_devres_iomap_planner_manifest.json` is the packet-local owner map for that fixture and should stay aligned with the helper, note, and replay
- `scripts/zigux/check-phase13-devres-iomap-planner.py` is the packet-local fail-closed checker and should stay aligned with the helper, planner note, manifest, and replay
- `Documentation/zigux/phase13-devres-survey.md` remains adjacent boundary evidence only and does not own the helper-local iomap fixture packet

Adjacent boundary evidence stays unchanged:
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `scripts/zigux/check-phase13-devres-mmio-packet.py`

Standalone replay handles:
- `zig test --dep devres -Mroot=zigux/tests/phase13_devres_iomap_planner.zig -Mdevres=lib/devres.zig`
- `python3 scripts/zigux/check-phase13-devres-iomap-planner.py`
- `python3 scripts/zigux/check-phase13-devres-mmio-packet.py --self-test`
