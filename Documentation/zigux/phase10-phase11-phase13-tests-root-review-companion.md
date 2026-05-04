# Phase 10, 11, and 13 Tests-Root Review Companion

Use this note when a change touches the active Phase 10 virtio lab packet, the active Phase 11 simple-driver packet, or the active Phase 13 shared-helper release packet and the review needs a compact tests-root checklist.

Keep `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, and `Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md` aligned with this note when they describe the same packet so the shared reviewer prompts do not drift across docs-root, tests-root, and checklist-facing guidance.

## Phase 10 tests-root packet

Keep the tests-root replay packet explicit:
- `zigux/tests/phase10_build.zig`
- `zigux/tests/phase10_closure_manifest.json`
- `zigux-alpha/PHASE10_CLOSURE_LEDGER.md`
- `zigux/tests/phase10_virtio_core_manifest.json`
- `zigux/tests/phase10_virtio_core.zig`
- `zigux/tests/phase10_virtio_core_survey.zig`
- `zigux/tests/phase10_virtio_ring_manifest.json`
- `zigux/tests/phase10_virtio_ring_reset_reuse.zig`
- `zigux/tests/phase10_virtio_ring_survey.zig`
- `zigux/tests/phase10_virtio_input_multitouch_preflight.zig`
- `zigux/tests/phase10_virtio_input_registration_blocker_build.zig`
- `zigux/tests/phase10_virtio_input_manifest.json`
- `zigux/tests/phase10_virtio_input_survey.zig`
- `zigux/tests/phase10_virtio_mmio_queue_isolation.zig`
- `zigux/tests/phase10_virtio_mmio_manifest.json`
- `zigux/tests/phase10_virtio_mmio_survey.zig`
- `scripts/zigux/check-phase10-closure-inventory.py`
- `scripts/zigux/check-phase10-core-packet.py`
- `scripts/zigux/check-phase10-harness-coverage.py`
- `scripts/zigux/validate-phase10.py`
- `scripts/zigux/validate-phase10-closure.py`

Tests-root reviewer prompt:
- Do the shared Phase 10 build, the shared closure manifest, the dedicated closure-ledger supplement, all four lane survey manifests, the four survey replays, the focused ring drained-reset reuse replay, the focused multitouch preflight replay, the focused registration-blocker replay build, the focused MMIO queue-isolation replay, the closure-inventory checker, the core-packet checker, and the harness-coverage checker still describe the same validator-first lab bundle rather than a set of unrelated virtio starter files?

## Phase 11 tests-root packet

Keep the shared-versus-dedicated replay boundary explicit:
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `zigux/tests/README.md`
- `zigux/tests/phase11_build.zig`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_dw_wdt_suspend_resume.zig`
- `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`
- `zigux/tests/phase11_hvc_console_modem_control_split.zig`
- `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `zigux/tests/phase11_gpio_wdt_manifest.json`
- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_hvc_console_manifest.json`
- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-layout-assert-surface.py`
- `scripts/zigux/check-phase11-hvc-validation-flow.py`
- `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`
- `scripts/zigux/check-phase11-shared-replay-contract.py`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `scripts/zigux/validate-phase11.py`

Tests-root reviewer prompts:
- Do the pre-replay Phase 11 checkers still describe the same delivery contract that `Documentation/zigux/phase11-shared-replay-contract.md`, `zigux/tests/README.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, and `Documentation/zigux/review-checklist.md` claim?
- Does `zigux/tests/phase11_hvc_console_survey.zig` still stay separate as the dedicated archival replay while the shared starter packet remains under `zigux/tests/phase11_build.zig`, explicitly includes `zigux/tests/phase11_dw_wdt_suspend_resume.zig`, `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, and `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, and keeps the shared header-boundary packet explicit through `scripts/zigux/check-phase11-header-boundary-packet.py`?

## Phase 13 tests-root packet

Keep the shared release replay packet explicit:
- `zigux/tests/phase13_build.zig`
- `zigux/tests/phase13_libfs_manifest.json`
- `zigux/tests/phase13_devres_manifest.json`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_scatterlist.zig`
- `zigux/tests/phase13_devres_iounmap_reviewability.zig`
- `zigux/tests/phase13_devres_iomap_reviewability.zig`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_wrapper_reviewability.zig`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset_reviewability.zig`
- `zigux/tests/phase13_landlock_ruleset_fops_sync.zig`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/notifier_chain_view.zig`
- `scripts/zigux/check-phase13-libfs-packet.py`
- `scripts/zigux/check-phase13-devres-packet.py`
- `scripts/zigux/check-phase13-devres-inventory-contract.py`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `scripts/zigux/check-phase13-release-replay-exact-counts.py`
- `scripts/zigux/validate-phase13-release.py`

Tests-root reviewer prompt:
- Do the shared Phase 13 build, the four roadmap-anchor manifests plus the adjacent notifier-list manifest, the shared release validator, the dedicated libfs, devres, devres-inventory-contract, and notifier packet guards, the shared replay-count guard, the direct libfs helper plus libfs reviewability replay, the direct devres, landlock-ruleset, and landlock-syscalls helper replays, the devres coherent-DMA plus scatterlist plus `iounmap`, `iomap`, plain-wrapper, and helper reviewability replays, the Landlock ruleset plus ruleset-fops-sync plus syscall reviewability replays, the adjacent notifier reviewability packet, and the direct notifier-chain-view replay through `zigux/helpers/notifier_chain_view.zig` still name the same validator-first release path and evidence bundle instead of drifting into separate stories?

## Checklist carryover prompts

Keep these reviewer questions explicit when `zigux/tests/README.md` or other shared contributor-facing workflow notes are refreshed:
- Phase 10: do `Documentation/zigux/phase10-closure-evidence.md`, `zigux-alpha/PHASE10_CLOSURE_LEDGER.md`, `zigux/tests/phase10_closure_manifest.json`, `scripts/zigux/check-phase10-closure-inventory.py`, `scripts/zigux/check-phase10-core-packet.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_input_multitouch_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_blocker_build.zig`, and `zigux/tests/phase10_virtio_mmio_queue_isolation.zig` still describe the same validator-first lab bundle, survey replay set, and focused harness evidence?
- Phase 11: do `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-layout-assert-surface.py`, `scripts/zigux/check-phase11-hvc-validation-flow.py`, `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_dw_wdt_suspend_resume.zig`, `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_hvc_console_manifest.json`, and `zigux/tests/phase11_uapi_header_parity_manifest.json` still keep the pre-replay stack, the shared-versus-dedicated `hvc_console` split, and the shared header-boundary packet aligned?
- Phase 13: do `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-notifier-list-survey.md`, `Documentation/zigux/README.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, `zigux/tests/phase13_notifier_list_manifest.json`, `scripts/zigux/check-phase13-libfs-packet.py`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/check-phase13-devres-inventory-contract.py`, `scripts/zigux/check-phase13-notifier-packet.py`, `scripts/zigux/check-phase13-release-replay-exact-counts.py`, `scripts/zigux/validate-phase13-release.py`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, `zigux/tests/phase13_devres_iounmap_reviewability.zig`, `zigux/tests/phase13_devres_iomap_reviewability.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_wrapper_reviewability.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_reviewability.zig`, `zigux/tests/phase13_landlock_ruleset_fops_sync.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig` still keep the validator-first release path, the four roadmap-anchor manifests plus the adjacent notifier-list manifest, the dedicated libfs, devres, devres-inventory-contract, and notifier packet guards, the shared replay-count guard, the direct libfs helper plus libfs reviewability replay, the direct devres, landlock-ruleset, and landlock-syscalls helper replays, the extra devres and Landlock reviewability gates, the adjacent notifier evidence, the dedicated exported C header foothold, the Zig notifier ABI foothold, and the direct notifier-chain-view replay aligned?

## Shared rule

When one of these packets changes, keep the tests-root replay file, the packet-local manifest or focused reviewability shard, and the validator-first review surface reviewable together.
