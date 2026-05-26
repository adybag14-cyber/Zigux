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
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json` is present, marks the tool `closed`, records the same 16-case packet, keeps `randconfig_expected.json` in the override packet, limits `allconfig_sentinel_packet` to `allnoconfig_expected.json`, `allyesconfig_expected.json`, and `alldefconfig_expected.json`, keeps the fixture-backed `allconfig_override_packet` on `allmodconfig_expected.json`, `alldefconfig_expected.json`, and `randconfig_expected.json`, and currently inventories a five-mode `helper_local_allconfig_explicit_override_modes` reminder: `allmodconfig`, `allnoconfig`, `allyesconfig`, `alldefconfig`, and `randconfig`.
- `Documentation/zigux/phase2-closure.md` still lists `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, and `zigux/tests/fixtures/kconfig_bridge/cases.json` inside the current directly readable Phase 2 closure packet.

## Current Repo-Reality Gap
- The roadmap-backed conf bridge scaffold is still landed. This lane does not show a missing bridge, checker, or fixture family that needs to be recreated from scratch.
- The earlier bare-`randconfig` drift is no longer live on current `master`: `scripts/zigux/kconfig/conf_bridge.zig` now keeps the sentinel path narrowed to `allnoconfig`, `allyesconfig`, and `alldefconfig`, while `cases.json` and `conf_manifest.json` continue to model `randconfig` only through the explicit override packet.
- The older helper-anchor checker-parity follow-through is no longer live: current `master` still carries the live helper-anchor inventory in both `scripts/zigux/kconfig/conf_bridge.zig` and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, and `scripts/zigux/check-kconfig-bridge.py` still fails closed on manifest-side bridge-anchor parity by exact-checking `helper_local_anchors` against `REQUIRED_CONF_HELPER_ANCHORS`.
- The earlier helper-local explicit-override undercount is no longer live either: current `master` now keeps `alldefconfig` inside both `allconfig_override_packet` and `helper_local_allconfig_explicit_override_modes`, matching the already-landed helper coverage in `scripts/zigux/kconfig/conf_bridge.zig` and the checker expectations in `scripts/zigux/check-kconfig-bridge.py`.
- One shared reminder mismatch still remains adjacent to this bridge-local packet: `Documentation/zigux/phase2-conf-bridge-survey.md` is the dedicated current-master note for this conf-side packet, but `Documentation/zigux/phase2-closure.md` still undercounts that bridge-family reminder surface by listing the bridge source, checker, fixtures, and manifests without naming this survey note.
- Fixture-backed explicit override governance remains narrower than helper-local behavior on current `master`: the `conf_cases` packet still only materializes explicit override expected-output coverage through `allmodconfig`, `alldefconfig`, and `randconfig`, so `allnoconfig` and `allyesconfig` explicit overrides are still helper-local coverage only today.

## Survey Result
- `current master` does not have a remaining roadmap gap at the level of conf bridge scaffolding.
- The live Phase 2 packet still contains the bridge source, checker, fixture roster, manifest, dedicated survey note, and shared closure reminder surfaces expected for the bounded `conf.c` bridge.
- The honest survey-level result is back to a parked bridge-local story: bridge behavior and expected-output parity for the existing 16 fixture-backed cases are closed on current `master`, and the checker plus manifest now count the same explicit-override helper coverage that the shipped bridge code already exercises. The remaining follow-through is the adjacent shared closure-note reminder undercount, not a new bridge-local behavior or manifest mismatch.

## Next Bounded Step
- Keep the bridge-local survey packet parked unless a future current-master reread finds a fresh bridge-only truthfulness drift.
- If the adjacent shared reminder undercount is still live when this family reopens, update `Documentation/zigux/phase2-closure.md` so the shared Phase 2 closure packet explicitly names this dedicated survey note.
- After that shared reminder repair lands, reread `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/check-kconfig-bridge.py`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, and `zigux/tests/fixtures/kconfig_bridge/cases.json` together before deciding whether to materialize explicit `allconfig` expected-output fixtures for `allnoconfig` and `allyesconfig` or keep those paths intentionally helper-local only.
- Do not widen this note into broader Phase 2 closure maintenance, fixture-output replay beyond the conf bridge packet, or confdata work unless the bridge-only reminder surfaces drift again.
