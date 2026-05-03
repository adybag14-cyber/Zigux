# Phase 10, 11, and 13 Validator-First Review Guide

Use this focused contributor guide when a change touches the active Phase 10 virtio lab packet, the active Phase 11 simple-driver packet, or the active Phase 13 shared-helper release packet.

## Why this note exists

The shared scripts index already names the current checker stack for these packets, but reviewers still need one compact place that says which pre-replay gates, shared replay entrypoints, and adjacent evidence files should move together.

## Phase 10: Virtio lab packet

Keep the validator-first route explicit:
- `python3 scripts/zigux/check-phase10-closure-inventory.py --self-test`
- `python3 scripts/zigux/check-phase10-closure-inventory.py`
- `python3 scripts/zigux/check-phase10-core-packet.py --self-test`
- `python3 scripts/zigux/check-phase10-core-packet.py`
- `python3 scripts/zigux/validate-phase10.py --self-test`
- `python3 scripts/zigux/validate-phase10.py`
- `python3 scripts/zigux/validate-phase10-closure.py --self-test`
- `python3 scripts/zigux/validate-phase10-closure.py`
- `make -C zigux phase10-validate`
- `make -C zigux phase10`

Keep these evidence surfaces aligned in the same review:
- `Documentation/zigux/phase10-closure-evidence.md`
- `zigux/tests/phase10_closure_manifest.json`
- `zigux/tests/phase10_build.zig`
- `zigux/tests/phase10_virtio_ring_manifest.json`
- `zigux/tests/phase10_virtio_input_manifest.json`
- `zigux/tests/phase10_virtio_mmio_manifest.json`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

Reviewer prompt:
- Does the shared Phase 10 packet still read as one validator-first lab bundle rather than a set of independent virtio starter files?

## Phase 11: Simple-driver packet

Keep the pre-replay checker stack explicit:
- `python3 scripts/zigux/check-phase11-build-inventory.py --self-test`
- `python3 scripts/zigux/check-phase11-build-inventory.py`
- `python3 scripts/zigux/check-phase11-layout-assert-surface.py --self-test`
- `python3 scripts/zigux/check-phase11-layout-assert-surface.py`
- `python3 scripts/zigux/check-phase11-hvc-validation-flow.py --self-test`
- `python3 scripts/zigux/check-phase11-hvc-validation-flow.py`
- `python3 scripts/zigux/check-phase11-hvc-cleanup-alignment.py --self-test`
- `python3 scripts/zigux/check-phase11-hvc-cleanup-alignment.py`
- `python3 scripts/zigux/validate-phase11.py --self-test`
- `python3 scripts/zigux/validate-phase11.py`
- `make -C zigux phase11-validate`
- `make -C zigux phase11`
- `make -C zigux phase11-hvc-survey`

Keep these evidence surfaces aligned in the same review:
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_build.zig`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `zigux/tests/phase11_gpio_wdt_manifest.json`
- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_hvc_console_manifest.json`
- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

Reviewer prompts:
- Does the shared Phase 11 replay still stay separate from the dedicated archival `hvc_console` survey?
- Do the pre-replay checkers still describe the same delivery contract that the shared build inventory and manifests claim?

## Phase 13: Shared-helper release packet

Keep the validator-first release route explicit:
- `python3 scripts/zigux/check-phase13-libfs-packet.py --self-test`
- `python3 scripts/zigux/check-phase13-libfs-packet.py`
- `python3 scripts/zigux/check-phase13-notifier-packet.py --self-test`
- `python3 scripts/zigux/check-phase13-notifier-packet.py`
- `python3 scripts/zigux/validate-phase13-release.py`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

Keep these evidence surfaces aligned in the same review:
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-libfs-survey.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `zigux/tests/phase13_build.zig`
- `zigux/tests/phase13_libfs_manifest.json`
- `zigux/tests/phase13_devres_manifest.json`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

Reviewer prompt:
- Does the shared Phase 13 packet still route through the release validator before the ten-step replay bundle, with the notifier packet kept explicit as adjacent release evidence rather than an untracked side lane?

## Shared review rule

When one of these packets changes, keep the checker stack, the shared replay path, and the named evidence files reviewable together. Do not treat a passing build file, one manifest refresh, or one survey note edit as enough on its own.