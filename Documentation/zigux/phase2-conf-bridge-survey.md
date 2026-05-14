# Phase 2 Conf Bridge Survey

This note records the current `master` readback for the roadmap-backed `scripts/zigux/kconfig/conf_bridge.zig` bridge so Phase 2 review stays grounded in the live packet instead of reviving the older missing-scaffold story.

## Roadmap Target

- Phase 2 keeps `scripts/kconfig/conf.c` inside the bounded parser-heavy tooling tranche.
- The roadmap's recommended Zigux destination is `scripts/zigux/kconfig/conf_bridge.zig` beside `scripts/zigux/kconfig/confdata_bridge.zig`.
- The bootstrap ledger's bounded Phase 2 kconfig bridge scaffolding commit already names `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `scripts/zigux/check-kconfig-bridge.py`, and the `zigux/tests/fixtures/kconfig_bridge/` packet as the intended scaffold surfaces.

## Current Master Readback

- `scripts/zigux/kconfig/conf_bridge.zig` is present on `master` and already ships a bounded `runConfBridge()` entrypoint plus a CLI `main()` wrapper for the conf request packet.
- The live bridge mode surface already covers the current bounded conf packet: `oldaskconfig`, `syncconfig`, `oldconfig`, `allnoconfig`, `allyesconfig`, `allmodconfig`, `alldefconfig`, `randconfig`, `defconfig`, `savedefconfig`, `listnewconfig`, `helpnewconfig`, `olddefconfig`, `yes2modconfig`, `mod2yesconfig`, and `mod2noconfig`.
- `zigux/tests/fixtures/kconfig_bridge/cases.json` currently carries a `conf_cases` packet with 16 external fixture cases matching that live mode set, including the `helpnewconfig` silent request row and the bounded mode-argument, allconfig, randconfig, and syncconfig variants.
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json` is present, marks the tool `closed`, records the same 16-case packet, and keeps the bounded request-plan bridge packet explicit in the committed fixture inventory.
- `scripts/zigux/check-kconfig-bridge.py`, `Documentation/zigux/phase2-closure.md`, and the shared Phase 2 reminder surfaces already treat the conf bridge as an existing packet on current `master` instead of a missing scaffold.

## Survey Result

- `current master` does not have a remaining roadmap gap at the level of conf bridge scaffolding. The bridge, checker, fixture packet, manifest, and shared Phase 2 reminder surfaces are already present.
- The honest remaining work for this file family is smaller than scaffolding: keep the bridge-local truthfulness surfaces aligned when the bridge grows.
- The live bridge helper surface has moved beyond the current checker-backed subset. `scripts/zigux/check-kconfig-bridge.py` and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json` now agree on a 14-anchor helper packet, but `scripts/zigux/kconfig/conf_bridge.zig` currently carries 31 bridge-local test anchors spanning the mode-surface check, the `silentoldconfig` alias, empty `nosilentupdate` omission, `--silent` ordering, sentinel and override env handling, mode-argument validation, and duplicate-option rejection.
- That smaller helper-anchor parity follow-through belongs in the separate conf bridge maintenance lane rather than reopening this survey lane as if scaffolding were still missing.

## Next Bounded Step

- Leave this survey lane parked unless current `master` later loses one of the scaffold surfaces above or the roadmap expectation for the conf bridge changes.
- If the conf bridge family reopens first, start with a fresh current-master reread of `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/check-kconfig-bridge.py`, and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, then keep the follow-through to the smaller checker-and-manifest helper-anchor parity repair instead of recreating a missing-scaffold narrative.
