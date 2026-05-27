# Phase 2 Scripts-Root Tooling Inventory

This note keeps the current Phase 2 repo-tooling packet explicit from the scripts root.

## Review Surfaces

- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

## Tooling Surfaces

- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-lane05-local-first-archive-workflow.py`
- `scripts/zigux/check-lane05-local-archive-readme.py`
- `scripts/zigux/check-lane05-install-zig-archive-verification.py`
- `scripts/zigux/check-lane05-stage-helper-contract.py`
- `scripts/zigux/check-lane05-stage-helper-selftest.py`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/stage-pinned-zig-archive.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-docs-shared-reminder.py`
- `scripts/zigux/check-phase2-required-make-routes.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-kconfig-bridge.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`
- `scripts/zigux/check-genksyms-bridge.py`
- `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`
- `scripts/zigux/check-phase2-fixdep-gate.py`
- `scripts/zigux/check-fixdep-diff.py`
- `scripts/zigux/check-phase2-tool-manifest.py`
- `scripts/zigux/check-phase2-artifact-tools-manifest.py`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`
- `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`
- `scripts/zigux/fixdep.zig`
- `scripts/zigux/zig-toolchain-policy.json`
- `scripts/zigux/artifact_diff.py`

## Fixtures And Manifests

- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `zigux/tests/fixtures/genksyms_bridge/cases.json`
- `zigux/tests/fixtures/genksyms_bridge/manifest.json`
- `zigux/tests/fixtures/fixdep/cases.json`
- `third_party/README.md`
- `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`
- `zigux/Makefile`

## Replay Commands

- `python3 scripts/zigux/check-phase2-scripts-root-tooling-inventory.py --self-test`
- `python3 scripts/zigux/check-phase2-scripts-root-tooling-inventory.py`
- `make -C zigux phase2-toolchain`
- `make -C zigux phase2-tools`
- `make -C zigux phase2-kconfig`
- `make -C zigux phase2-cross`
- `make -C zigux phase2-genksyms`
- `make -C zigux phase2-fixdep`
- `make -C zigux phase2-validate`
- `make -C zigux phase2`

## Boundary

`scripts/zigux/README.md` remains the broader scripts-root reminder surface. This inventory is the bounded Phase 2 checklist for toolchain pinning, local-first archive bootstrap, kbuild, kconfig, genksyms, fixdep, cross-route, manifest, and make-wrapper follow-through.
