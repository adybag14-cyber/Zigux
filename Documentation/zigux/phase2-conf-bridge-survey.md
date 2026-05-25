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
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json` is present, marks the tool `closed`, records the same 16-case packet, keeps `randconfig_expected.json` in the override packet, limits `allconfig_sentinel_packet` to `allnoconfig_expected.json`, `allyesconfig_expected.json`, and `alldefconfig_expected.json`, keeps the fixture-backed `allconfig_override_packet` narrowed to `allmodconfig_expected.json` plus `randconfig_expected.json`, and currently inventories a four-mode `helper_local_allconfig_explicit_override_modes` reminder: `allmodconfig`, `allnoconfig`, `allyesconfig`, and `randconfig`.
- `Documentation/zigux/phase2-closure.md` still lists `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, and `zigux/tests/fixtures/kconfig_bridge/cases.json` inside the current directly readable Phase 2 closure packet.

## Current Repo-Reality Gap
- The roadmap-backed conf bridge scaffold is still landed. This lane does not show a missing bridge, checker, or fixture family that needs to be recreated from scratch.
- The earlier bare-`randconfig` drift is no longer live on current `master`: `scripts/zigux/kconfig/conf_bridge.zig` now keeps the sentinel path narrowed to `allnoconfig`, `allyesconfig`, and `alldefconfig`, while `cases.json` and `conf_manifest.json` continue to model `randconfig` only through the explicit override packet.
- The older helper-anchor checker-parity follow-through is no longer live: current `master` still carries the live helper-anchor inventory in both `scripts/zigux/kconfig/conf_bridge.zig` and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, and `scripts/zigux/check-kconfig-bridge.py` still fails closed on manifest-side bridge-anchor parity by exact-checking `helper_local_anchors` against `REQUIRED_CONF_HELPER_ANCHORS`.
- One fresh bridge-local reminder mismatch is now visible on current `master`: `scripts/zigux/kconfig/conf_bridge.zig` helper coverage and `modeAcceptsAllConfigOverride()` both include explicit `allconfig` override support for `alldefconfig`, but `scripts/zigux/check-kconfig-bridge.py` and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json` still undercount `helper_local_allconfig_explicit_override_modes` to four modes and omit `alldefconfig`.
- The remaining shared reminder drift is still present too: `Documentation/zigux/phase2-conf-bridge-survey.md` is the dedicated current-master note for this conf-side packet, but `Documentation/zigux/phase2-closure.md` still undercounts that bridge-family reminder surface by listing the bridge source, checker, fixtures, and manifests without naming this survey note.
- Fixture-backed explicit override governance remains narrower than helper-local behavior on current `master`: the `conf_cases` packet and `allconfig_override_packet` still only govern that explicit override path through `allmodconfig` and `randconfig`, so `allnoconfig`, `allyesconfig`, and `alldefconfig` explicit overrides are still helper-local coverage only today.

## Survey Result
- `current master` does not have a remaining roadmap gap at the level of conf bridge scaffolding.
- The live Phase 2 packet still contains the bridge source, checker, fixture roster, manifest, dedicated survey note, and shared closure reminder surfaces expected for the bounded `conf.c` bridge.
- The honest survey-level result is no longer a fully parked story: bridge behavior and expected-output parity for the existing 16 fixture-backed cases are still closed on current `master`, but one reminder mismatch remains inside the same packet because the checker plus manifest undercount the already-landed `alldefconfig` explicit override helper coverage. Shared closure-note undercount for this survey note is still the adjacent reminder-only follow-through.

## Next Bounded Step
- Reopen only one bridge-local governance correction at a time.
- The highest-value same-family follow-through is to update `scripts/zigux/check-kconfig-bridge.py` and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json` together so `helper_local_allconfig_explicit_override_modes` includes `alldefconfig` everywhere the existing helper-local override reminder is enforced.
- After that parity repair lands, reread `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/check-kconfig-bridge.py`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, and `zigux/tests/fixtures/kconfig_bridge/cases.json` together before deciding whether to materialize explicit `allconfig` expected-output fixtures for `allnoconfig`, `allyesconfig`, and `alldefconfig` or keep those paths intentionally helper-local only.
- Keep the shared `Documentation/zigux/phase2-closure.md` follow-through separate unless this packet-local undercount is already closed and the survey note is still the only stale surface.
- Do not widen this note into broader Phase 2 closure maintenance, fixture-output replay beyond the conf bridge packet, or confdata work unless the bridge-only reminder surfaces drift again.
