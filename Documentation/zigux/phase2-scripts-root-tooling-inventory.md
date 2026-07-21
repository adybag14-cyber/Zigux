# Phase 2 Scripts-Root Tooling Inventory

This note keeps the current Phase 2 repo-tooling packet explicit from the scripts root.

## Review Surfaces

- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

## Tooling Surfaces

- `scripts\zigux/check_zig_toolchain.zig`
- `scripts\zigux/check_lane05_local_first_archive_workflow.zig`
- `scripts\zigux/check_lane05_local_archive_readme.zig`
- `scripts\zigux/check_lane05_install_zig_archive_verification.zig`
- `scripts\zigux/check_lane05_stage_helper_contract.zig`
- `scripts\zigux/check_lane05_stage_helper_selftest.zig`
- `scripts/zigux/install_zig.zig`
- `scripts/zigux/stage_pinned_zig_archive.zig`
- `scripts\zigux/check_phase2_kbuild_routes.zig`
- `scripts\zigux/check_phase2_docs_shared_reminder.zig`
- `scripts\zigux/check_phase2_required_make_routes.zig`
- `scripts\zigux/check_phase2_toolchain_pinning.zig`
- `scripts\zigux/check_phase2_toolchain_pin_scope.zig`
- `scripts\zigux/check_phase2_cross.zig`
- `scripts\zigux/check_phase2_cross_selftest_alignment.zig`
- `scripts\zigux/check_kconfig_bridge.zig`
- `scripts\zigux/check_phase2_kconfig_selftest_alignment.zig`
- `scripts\zigux/check_phase2_kconfig_allconfig_helper_packet.zig`
- `scripts\zigux/check_genksyms_bridge.zig`
- `scripts\zigux/check_phase2_genksyms_selftest_alignment.zig`
- `scripts\zigux/check_phase2_fixdep_gate.zig`
- `scripts\zigux/check_fixdep_diff.zig`
- `scripts\zigux/check_phase2_tool_manifest.zig`
- `scripts\zigux/check_phase2_artifact_tools_manifest.zig`
- `scripts\zigux/validate_phase2.zig`
- `scripts\zigux/validate_phase2_closure.zig`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`
- `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`
- `scripts/zigux/fixdep.zig`
- `scripts/zigux/zig-toolchain-policy.json`
- `scripts/zigux/artifact_diff.zig`

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
- `third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz`
- `zigux/Makefile`

## Replay Commands

- `zig run scripts/zigux/check_phase2_scripts_root_tooling_inventory.zig -- --self-test`
- `zig run scripts/zigux/check_phase2_scripts_root_tooling_inventory.zig`
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
