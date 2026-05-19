# Zigux Review Checklist
  * if the change touches the shared Phase 2 toolchain packet, do `Documentation/zigux/README.md`
  * `scripts/zigux/install-zig.py`
  * `scripts/zigux/check-phase2-cross.py`
  * `zigux/tests/fixtures/phase2_cross_targets.json`
  * `scripts/zigux/check-kconfig-bridge.py`
  * `scripts/zigux/check-genksyms-bridge.py`
  * `scripts/zigux/genksyms.zig`
  * `zigux/tests/fixtures/genksyms_bridge/cases.json`
  * `zigux/tests/fixtures/genksyms_bridge/help_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`
  * current directly readable Phase 2 toolchain, installer, kbuild, kconfig bridge, direct cross-route, docs-shared-reminder, and required-make-route packet
  * `python3 scripts/zigux/install-zig.py --self-test`
  * `python3 scripts/zigux/check-phase2-cross.py --self-test`
  * `make -C zigux phase2-genksyms`
  * current rematerialized Phase 2 closure-side, closure-validator, validation, installer-selftest, direct-cross-selftest, artifact-support, toolchain self-check, and make-wrapper packet?
  * direct current-tree readback plus `zigux/tests/README.md` outrank the lagging repo-reality-gap wording still present in `Documentation/zigux/phase2-toolchain-bootstrap-notes.md` and `scripts/zigux/README.md` for the returned installer, direct cross-route, and cross-target fixture packet, while direct current-tree readback plus `zigux/tests/fixtures/phase2_tool_manifest.json` outrank the still-lagging reminder wording for the shipped `check-kconfig-bridge.py` surface and bounded `genksyms` helper/checker packet.
