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
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json` is present, marks the tool `closed`, records the same 16-case packet, keeps `randconfig_expected.json` in the override packet, and currently limits `allconfig_sentinel_packet` to `allnoconfig_expected.json`, `allyesconfig_expected.json`, and `alldefconfig_expected.json`.
- `Documentation/zigux/phase2-closure.md` still lists `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, and `zigux/tests/fixtures/kconfig_bridge/cases.json` inside the current directly readable Phase 2 closure packet.

## Current Repo-Reality Gap
- The roadmap-backed conf bridge scaffold is still landed. This lane does not show a missing bridge, checker, or fixture family that needs to be recreated from scratch.
- The dedicated survey note itself had dropped out of the docs tree on current `master`; this file restores that missing reviewer-facing survey surface.
- A narrower same-family drift is now visible inside the live conf bridge packet: `scripts/zigux/kconfig/conf_bridge.zig` currently still treats bare `randconfig` as an `allconfig` sentinel mode through `modeUsesAllConfigSentinel()` and a helper-local test titled `conf bridge emits randconfig allconfig sentinel without explicit override`, while the current fixture and manifest packet still models `randconfig` only through the explicit override case in `cases.json` and `randconfig_expected.json`, and the current manifest keeps `randconfig_expected.json` out of `allconfig_sentinel_packet`.
- Because of that split, the real current-master follow-through is no longer a missing scaffold. It is a narrower live behavior-versus-reminder mismatch inside the already-landed bridge family.

## Survey Result
- `current master` does not have a remaining roadmap gap at the level of conf bridge scaffolding.
- The live Phase 2 packet still contains the bridge source, checker, fixture roster, manifest, and shared closure reminder surfaces expected for the bounded `conf.c` bridge.
- The honest survey-level reopen is the restored note plus the newly visible bare-`randconfig` drift above, not a fresh scaffold buildout.

## Next Bounded Step
- If the family reopens on the behavior side, keep the follow-through on the dedicated conf bridge verification lane and reconcile the live bare-`randconfig` sentinel behavior against the committed fixture and manifest packet before widening into any broader Phase 2 reminder edits.
- If the family reopens only on helper-anchor accounting, keep that follow-through on the separate checker-and-manifest parity lane rather than in this survey file.
- Leave this survey parked unless a later reread shows another same-family scaffold surface disappearing or the roadmap expectation changing.
