# zigux/tests

This directory is the home of reusable Zigux parity and differential validation harnesses.

Purpose

  * hold shared harness logic before subsystem-specific tests spread through the tree
  * keep product-facing validation code separate from ad hoc experiments
  * provide the checks for helper parity, ABI assertions, and rollback readiness

Key entrypoints
  * `zigux/tests/build.zig`
  * current direct-readback Phase 2 kconfig bridge packet:
    `Documentation/zigux/review-checklist.md`
    `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
    `scripts/zigux/kconfig/conf_bridge.zig`
    `scripts/zigux/kconfig/confdata_bridge.zig`
    `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
    `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
  * current shared Phase 2 kconfig route: `make -C zigux phase2-kconfig`
  * Phase 2 review packet:
    `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
    `Documentation/zigux/phase2-closure.md`
    `Documentation/zigux/review-checklist.md`
    `scripts/zigux/README.md`
    `scripts/zigux/validate-phase2.py`
    `scripts/zigux/validate-phase2-closure.py`
    `scripts/zigux/check-zig-toolchain.py`
    `scripts/zigux/check-phase2-kbuild-routes.py`
    `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
    `scripts/zigux/check-phase2-tests-readme-alignment.py`
    `scripts/zigux/check-phase2-cross-selftest-alignment.py`
    `scripts/zigux/check-phase2-toolchain-pinning.py`
    `scripts/zigux/check-phase2-toolchain-pin-scope.py`
    `scripts/zigux/check-phase2-docs-shared-reminder.py`
    `scripts/zigux/check-phase2-required-make-routes.py`
    `python3 scripts/zigux/check-zig-toolchain.py --self-test`
    `python3 scripts/zigux/check-zig-toolchain.py --policy-only`
    `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`
    `scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
    `scripts/zigux/kconfig/conf_bridge.zig`
    `scripts/zigux/kconfig/confdata_bridge.zig`
    `scripts/zigux/zig-toolchain-policy.json`
    `zigux/Makefile`
    `zigux/tests/fixtures/phase2_tool_manifest.json`
    `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
    `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
    `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
    `make -C zigux phase2-toolchain`
    `make -C zigux phase2-tools`
    `make -C zigux phase2-kconfig`
    `make -C zigux phase2-cross`
    `make -C zigux phase2-validate`
    `make -C zigux phase2`
    `zigux/tests/fixtures/kconfig_bridge/cases.json`
  * the current directly readable Phase 2 packet is the scripts-root kbuild, cross-selftest, docs-shared-reminder, required-make-route, toolchain reminder set, the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, and closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster
  * keep `scripts/zigux/zig-toolchain-policy.json`, the pinned `x86_64-linux` bootstrap archive note, the live `python3 scripts/zigux/check-zig-toolchain.py --policy-only` plus `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replays, and the repo-local `.zig-toolchain` fallback reused by the surviving `scripts/zigux/check-zig-toolchain.py` and pin-scope guards explicit in this tests-root packet
  * current `master` still does not directly materialize `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep those installer, direct cross-route, and cross-target fixture names framed as historical packet members instead of shipped tests-root evidence
  * keep the fixture-backed tool-manifest, artifact-tools, and kconfig bridge packet visible in the tests root without reviving missing installer, direct cross-route, validator-first, or make-wrapper proof text
