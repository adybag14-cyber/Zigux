# Phase 2 Conf Bridge Survey

This note records the current `master` readback for the roadmap-backed `scripts/zigux/kconfig/conf_bridge.zig` bridge so Phase 2 review stays grounded in the live scaffold packet instead of replaying older already-landed or now-drifted claims.

## Roadmap Target
- Phase 2 keeps `scripts/kconfig/conf.c` inside the bounded toolchain and Kbuild enablement tranche.
- The roadmap's recommended Zigux destination is `scripts/zigux/kconfig/conf_bridge.zig` beside `scripts/zigux/kconfig/confdata_bridge.zig`.
- The bootstrap ledger's bounded kconfig bridge scaffolding packet centers on `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/check-kconfig-bridge.py`, and `zigux/tests/fixtures/kconfig_bridge/`.

## Current Master Readback
- `scripts/zigux/kconfig/conf_bridge.zig` is present on `master` and still ships the bounded request-plan bridge shape: a `Mode` enum with the live sixteen-mode surface, a `runConfBridge()` JSON emitter, a CLI `main()` wrapper, and helper-local tests covering mode text and flag mapping, mode-argument validation, silent handling, syncconfig environment wiring, allconfig handling, randconfig tunables, and option-parser duplicate rejection.
- `scripts/zigux/check-kconfig-bridge.py` is present on `master` and still treats the conf-side packet as a bounded bridge-plus-fixture surface, with the current required mode inventory, manifest packet checks, and helper-anchor inventory review.
- `zigux/tests/fixtures/kconfig_bridge/cases.json` currently keeps a `conf_cases` packet with 16 cases: `oldaskconfig`, `syncconfig`, `oldconfig`, `allnoconfig`, `allyesconfig`, `allmodconfig`, `alldefconfig`, `randconfig`, `defconfig`, `savedefconfig`, `listnewconfig`, `helpnewconfig`, `olddefconfig`, `yes2modconfig`, `mod2yesconfig`, and `mod2noconfig`.
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json` is present, marks the tool `closed`, records the same 16-case packet, keeps `randconfig_expected.json` in the override packet, limits `allconfig_sentinel_packet` to `allnoconfig_expected.json`, `allyesconfig_expected.json`, and `alldefconfig_expected.json`, and now inventories the live 28-entry `helper_local_anchors` packet.
- `Documentation/zigux/phase2-closure.md` still lists `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, and `zigux/tests/fixtures/kconfig_bridge/cases.json` inside the current directly readable Phase 2 closure packet.

## Current Repo-Reality Gap
- The roadmap-backed conf bridge scaffold is still landed. This lane does not show a missing bridge, checker, or fixture family that needs to be recreated from scratch.
- The earlier bare-`randconfig` drift is no longer live on current `master`: `scripts/zigux/kconfig/conf_bridge.zig` now keeps the sentinel path narrowed to `allnoconfig`, `allyesconfig`, and `alldefconfig`, while `cases.json` and `conf_manifest.json` continue to model `randconfig` only through the explicit override packet.
- The remaining same-family follow-through is narrower and bridge-only: current `master` now carries the live helper-anchor inventory in both `scripts/zigux/kconfig/conf_bridge.zig` and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, but `scripts/zigux/check-kconfig-bridge.py` still does not fail closed on manifest-side bridge-anchor parity.
- The next safe bridge-local move is to keep behavior and expected-output surfaces parked, then land only the separate checker-and-manifest helper-anchor parity repair instead of reopening the bridge as if it still had a current behavior-versus-fixture mismatch.

## Survey Result
- `current master` does not have a remaining roadmap gap at the level of conf bridge scaffolding.
- The live Phase 2 packet still contains the bridge source, checker, fixture roster, manifest, and shared closure reminder surfaces expected for the bounded `conf.c` bridge.
- The honest survey-level result is that the earlier `randconfig` drift has already been closed, the manifest-side helper-anchor inventory is already present, and the remaining same-family follow-through is the separate checker parity packet rather than a fresh scaffold or expected-output repair.

## Next Bounded Step
- Leave this survey parked after recording the current bridge-only truthfulness gap.
- If the family reopens, keep the next bridge-local step to `scripts/zigux/check-kconfig-bridge.py` plus `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json` so the checker exact-checks the manifest-carried `conf_bridge.zig` helper-anchor packet.
- Do not widen this note into broader Phase 2 closure maintenance, fixture-output replay, or confdata work unless the bridge-only reminder surfaces drift again.
