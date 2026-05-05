# Phase 10, 11, and 13 Tests-Root Review Companion

Use this note when a change touches the active Phase 10 virtio lab packet, the active Phase 11 simple-driver packet, or the active Phase 13 shared-helper release packet and the review needs a compact tests-root checklist.
Keep `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, and `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md` aligned with this note when they describe the same packet so the shared reviewer prompts do not drift across docs-root, tests-root, and checklist-facing guidance.
## Phase 10 tests-root packet

Keep the shared build-backed virtio packet explicit:
  * `Documentation/zigux/README.md`
  * `scripts/zigux/README.md`
  * `Documentation/zigux/phase10-virtio-core-slice.md`
  * `Documentation/zigux/phase10-virtio-ring-slice.md`
  * `Documentation/zigux/phase10-virtio-ring-survey.md`
  * `Documentation/zigux/phase10-virtio-input-slice.md`
  * `Documentation/zigux/phase10-virtio-input-module-slice.md`
  * `Documentation/zigux/phase10-virtio-input-survey.md`
  * `Documentation/zigux/phase10-virtio-mmio-survey.md`
  * `zigux/tests/README.md`
  * `zigux/tests/phase10_build.zig`
  * `zigux/tests/phase10_virtio_core.zig`
  * `zigux/tests/phase10_virtio_ring.zig`
  * `zigux/tests/phase10_virtio_ring_survey.zig`
  * `zigux/tests/phase10_virtio_input.zig`
  * `zigux/tests/phase10_virtio_input_survey.zig`
  * `zigux/tests/phase10_virtio_mmio.zig`
  * `zigux/tests/phase10_virtio_mmio_survey.zig`
  * `zigux/Makefile`
Tests-root reviewer prompt:

  * Do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, the Phase 10 core, ring, input, and MMIO slice or survey notes, `zigux/tests/README.md`, `zigux/tests/phase10_build.zig`, the four shipped Phase 10 Zig test modules plus the three shipped survey gates, and `zigux/Makefile` still describe the same bounded build-backed virtio lab packet instead of implying a larger validator stack that is not on `master`?
## Phase 11 tests-root packet

Keep the shared-versus-dedicated replay boundary explicit:
  * `Documentation/zigux/phase11-shared-replay-contract.md`
  * `zigux/tests/README.md`
  * `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
  * `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
  * `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
  * `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  * `zigux/tests/phase11_build.zig`
  * `zigux/tests/fixtures/phase11_build_inventory.json`
  * `zigux/tests/phase11_dw_wdt_suspend_resume.zig`
  * `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`
  * `zigux/tests/phase11_hvc_console_modem_control_split.zig`
  * `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
  * `zigux/tests/phase11_hvc_console_survey.zig`
  * `zigux/tests/phase11_gpio_wdt_manifest.json`
  * `zigux/tests/phase11_bcm2835_wdt_manifest.json`
  * `zigux/tests/phase11_dw_wdt_manifest.json`
  * `zigux/tests/phase11_hvc_console_manifest.json`
  * `zigux/tests/phase11_uapi_header_parity_manifest.json`
  * `Documentation/zigux/review-checklist.md`
  * `scripts/zigux/check-phase11-build-inventory.py`
  * `scripts/zigux/check-phase11-layout-assert-surface.py`
  * `scripts/zigux/check-phase11-hvc-validation-flow.py`
  * `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`
  * `scripts/zigux/check-phase11-shared-replay-contract.py`
  * `scripts/zigux/check-phase11-header-boundary-packet.py`
  * `zigux/Makefile`
Tests-root reviewer prompts:
  * Do the pre-replay Phase 11 checkers, the shared Makefile replay route, and the Phase 11 test entry still describe the same delivery contract that `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `zigux/tests/README.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `Documentation/zigux/review-checklist.md`, and `zigux/Makefile` claim?
  * Does `zigux/tests/phase11_hvc_console_survey.zig` still stay separate as the dedicated archival replay while the shared starter packet remains under `zigux/tests/phase11_build.zig`, explicitly includes `zigux/tests/phase11_dw_wdt_suspend_resume.zig`, `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, and `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, keeps the shared header-boundary packet explicit through `scripts/zigux/check-phase11-header-boundary-packet.py`, and routes the shared packet through `make -C zigux phase11` instead of a removed validator script?
## Phase 13 tests-root packet

Keep the shared release replay packet explicit:
  * `Documentation/zigux/phase13-release-notes-survey.md`
  * `Documentation/zigux/phase13-roadmap-traceability.md`
  * `Documentation/zigux/phase13-libfs-survey.md`
  * `Documentation/zigux/phase13-devres-survey.md`
  * `Documentation/zigux/phase13-landlock-ruleset-survey.md`
  * `Documentation/zigux/phase13-landlock-syscalls-survey.md`
  * `Documentation/zigux/phase13-notifier-list-survey.md`
  * `Documentation/zigux/phase13-devres-scatterlist-slice.md`
  * `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
  * `Documentation/zigux/review-checklist.md`
  * `zigux/tests/phase13_build.zig`
  * `zigux/tests/phase13_libfs_manifest.json`
  * `zigux/tests/phase13_devres_manifest.json`
  * `zigux/tests/phase13_landlock_ruleset_manifest.json`
  * `zigux/tests/phase13_landlock_syscalls_manifest.json`
  * `zigux/tests/phase13_notifier_list_manifest.json`
  * `zigux/tests/phase13_libfs.zig`
  * `zigux/tests/phase13_libfs_reviewability.zig`
  * `zigux/tests/phase13_devres.zig`
  * `zigux/tests/phase13_devres_dma_coherent.zig`
  * `zigux/tests/phase13_devres_iounmap_reviewability.zig`
  * `zigux/tests/phase13_devres_iomap_reviewability.zig`
  * `zigux/tests/phase13_devres_reviewability.zig`
  * `zigux/tests/phase13_devres_wrapper_reviewability.zig`
  * `zigux/tests/phase13_landlock_ruleset.zig`
  * `zigux/tests/phase13_landlock_ruleset_reviewability.zig`
  * `zigux/tests/phase13_landlock_ruleset_fops_sync.zig`
  * `zigux/tests/phase13_landlock_syscalls.zig`
  * `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
  * `zigux/tests/phase13_notifier_list_reviewability.zig`
  * `zigux/bindings/notifier_abi.zig`
  * `include/zigux/notifier_abi.h`
  * `zigux/helpers/notifier_chain_view.zig`
  * `scripts/zigux/check-phase13-libfs-packet.py`
  * `scripts/zigux/check-phase13-devres-packet.py`
  * `scripts/zigux/check-phase13-devres-inventory-contract.py`
  * `scripts/zigux/check-phase13-notifier-packet.py`
  * `scripts/zigux/check-phase13-release-replay-exact-counts.py`
  * `scripts/zigux/validate-phase13-release.py`
  * `zigux/Makefile`
Tests-root reviewer prompt:
  * Do the shared Phase 13 build, the release-notes survey, the roadmap-traceability note, the shared contributor-surface sync note, the shared review checklist, the libfs, devres, Landlock, and notifier survey notes, the direct devres scatterlist slice note, the four roadmap-anchor manifests plus the adjacent notifier-list manifest, the dedicated libfs, devres, devres-inventory-contract, and notifier packet guards, the shared replay-count guard, the validator-first release gate, the Linux-style `make -C zigux phase13-validate` and `make -C zigux phase13` replay routes, the direct libfs helper plus libfs reviewability replay, the direct devres, landlock-ruleset, and landlock-syscalls helper replays, the devres coherent-DMA plus `iounmap`, `iomap`, plain-wrapper, and helper reviewability replays, the Landlock ruleset plus ruleset-fops-sync plus syscall reviewability replays, the adjacent notifier reviewability packet, and the notifier ABI footholds through `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig` still name the same validator-first release path and evidence bundle instead of drifting into separate stories?
## Checklist carryover prompts

Keep these reviewer questions explicit when `zigux/tests/README.md` or other shared contributor-facing workflow notes are refreshed:
  * Phase 10: do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, `zigux/tests/README.md`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `zigux/Makefile`, `zig build test --build-file zigux/tests/phase10_build.zig`, and `make -C zigux phase10` still keep the bounded virtio core, ring, input, and MMIO packet aligned without implying a dedicated `validate-phase10.py`, `check-phase10-harness-coverage.py`, or other shared Phase 10 validator surface that is not on `master`?
  * Phase 11: do `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-layout-assert-surface.py`, `scripts/zigux/check-phase11-hvc-validation-flow.py`, `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_dw_wdt_suspend_resume.zig`, `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/Makefile`, and `make -C zigux phase11` still keep the pre-replay stack, the four driver-local validation matrices, the shared-versus-dedicated `hvc_console` split, and the shared header-boundary packet aligned?
  * Phase 13: do `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-libfs-survey.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `Documentation/zigux/phase13-notifier-list-survey.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, `zigux/tests/phase13_notifier_list_manifest.json`, `scripts/zigux/check-phase13-libfs-packet.py`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/check-phase13-devres-inventory-contract.py`, `scripts/zigux/check-phase13-notifier-packet.py`, `scripts/zigux/check-phase13-release-replay-exact-counts.py`, `scripts/zigux/validate-phase13-release.py`, `zigux/Makefile`, `make -C zigux phase13-validate`, `make -C zigux phase13`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_iounmap_reviewability.zig`, `zigux/tests/phase13_devres_iomap_reviewability.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_wrapper_reviewability.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_reviewability.zig`, `zigux/tests/phase13_landlock_ruleset_fops_sync.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig` still keep the validator-first release path, the release-notes plus roadmap-traceability packet, the helper-family survey notes, the direct devres scatterlist slice note, the shared contributor-surface sync note, the four roadmap-anchor manifests plus the adjacent notifier-list manifest, the shared review checklist, the dedicated libfs, devres, devres-inventory-contract, and notifier packet guards, the shared replay-count guard, the direct validator gate, the Linux-style make replay routes, the direct libfs helper plus libfs reviewability replay, the direct devres, landlock-ruleset, and landlock-syscalls helper replays, the extra devres and Landlock reviewability gates, the adjacent notifier evidence, the dedicated exported C header foothold, the Zig notifier ABI foothold, and the direct notifier-chain-view replay aligned?
## Shared rule

When one of these packets changes, keep the tests-root replay file, the packet-local manifest or focused reviewability shard, and the validator-first review surface reviewable together.
