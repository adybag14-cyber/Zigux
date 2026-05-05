# Phase 10, 11, and 13 Tests-Root Review Companion

Use this note when a change touches the active Phase 10 virtio lab packet, the active Phase 11 simple-driver packet, or the active Phase 13 shared-helper release packet and the review needs a compact tests-root checklist.
Keep `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, and `Documentation/zigux/phase13-contributor-workflow-guide.md` aligned with this note when they describe the same packet so the shared reviewer prompts do not drift across docs-root, tests-root, and checklist-facing guidance.
## Phase 10 tests-root packet

Keep the shared build-backed virtio packet explicit:
  * `Documentation/zigux/README.md`
  * `scripts/zigux/README.md`
  * `Documentation/zigux/phase10-virtio-core-slice.md`
  * `Documentation/zigux/phase10-virtio-core-survey.md`
  * `Documentation/zigux/phase10-virtio-ring-slice.md`
  * `Documentation/zigux/phase10-virtio-ring-survey.md`
  * `Documentation/zigux/phase10-virtio-input-slice.md`
  * `Documentation/zigux/phase10-virtio-input-module-slice.md`
  * `Documentation/zigux/phase10-virtio-input-survey.md`
  * `Documentation/zigux/phase10-virtio-mmio-slice.md`
  * `Documentation/zigux/phase10-virtio-mmio-survey.md`
  * `zigux/tests/README.md`
  * `scripts/zigux/check-phase10-core-packet.py`
  * `zigux/tests/phase10_build.zig`
  * `zigux/tests/phase10_virtio_core.zig`
  * `zigux/tests/phase10_virtio_core_reset_queue.zig`
  * `zigux/tests/phase10_virtio_driver_id.zig`
  * `zigux/tests/phase10_virtio_core_manifest.json`
  * `zigux/tests/phase10_virtio_core_survey.zig`
  * `zigux/tests/phase10_virtio_ring.zig`
  * `zigux/tests/phase10_virtio_ring_manifest.json`
  * `zigux/tests/phase10_virtio_ring_survey.zig`
  * `zigux/tests/phase10_virtio_input.zig`
  * `zigux/tests/phase10_virtio_input_manifest.json`
  * `zigux/tests/phase10_virtio_input_status_drain.zig`
  * `zigux/tests/phase10_virtio_input_survey.zig`
  * `zigux/tests/phase10_virtio_mmio.zig`
  * `zigux/tests/phase10_virtio_mmio_manifest.json`
  * `zigux/tests/phase10_virtio_mmio_survey.zig`
  * `zigux/Makefile`
Tests-root reviewer prompt:

  * Do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, the Phase 10 core, ring, input, and MMIO slice or survey notes, `scripts/zigux/check-phase10-core-packet.py`, `zigux/tests/README.md`, `zigux/tests/phase10_build.zig`, the shipped focused Phase 10 replays, the four shipped survey manifests, the four shipped survey gates, and `zigux/Makefile` still describe the same bounded build-backed virtio lab packet instead of implying a larger validator stack that is not on `master`?
## Phase 11 tests-root packet

Keep the current shared-versus-dedicated simple-driver packet explicit:
  * `Documentation/zigux/README.md`
  * `scripts/zigux/README.md`
  * `zigux/tests/README.md`
  * `Documentation/zigux/phase11-shared-replay-contract.md`
  * `Documentation/zigux/review-checklist.md`
  * `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
  * `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
  * `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
  * `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  * `Documentation/zigux/phase11-hvc-console-survey.md`
  * `zigux/tests/phase11_build.zig`
  * `zigux/tests/phase11_hvc_cleanup.zig`
  * `zigux/tests/phase11_hvc_console_survey.zig`
  * `zigux/Makefile`
Tests-root reviewer prompt:
  * Do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/review-checklist.md`, the four Phase 11 validation matrices, `Documentation/zigux/phase11-hvc-console-survey.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/Makefile`, and `make -C zigux phase11` still describe the same shared-versus-dedicated simple-driver packet without implying a removed `validate-phase11.py`, missing build-inventory fixture, or broader checker-script packet that is not on `master`?
  * Does `Documentation/zigux/phase11-hvc-console-survey.md` stay paired with `zigux/tests/phase11_hvc_console_survey.zig` as the dedicated archival replay while `Documentation/zigux/phase11-shared-replay-contract.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, and the live `make -C zigux phase11` route keep the shipped shared replay split and bounded teardown handoff explicit?
## Phase 13 tests-root packet

Keep the shared validator-first release packet explicit:
  * `Documentation/zigux/README.md`
  * `Documentation/zigux/phase13-contributor-workflow-guide.md`
  * `Documentation/zigux/phase13-release-notes-survey.md`
  * `Documentation/zigux/phase13-roadmap-traceability.md`
  * `Documentation/zigux/phase13-libfs-slice.md`
  * `Documentation/zigux/phase13-libfs-survey.md`
  * `Documentation/zigux/phase13-devres-slice.md`
  * `Documentation/zigux/phase13-devres-survey.md`
  * `Documentation/zigux/phase13-landlock-ruleset-slice.md`
  * `Documentation/zigux/phase13-landlock-ruleset-survey.md`
  * `Documentation/zigux/phase13-landlock-syscalls-slice.md`
  * `Documentation/zigux/phase13-landlock-syscalls-survey.md`
  * `Documentation/zigux/phase13-notifier-list-survey.md`
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
  * `zigux/tests/phase13_devres_reviewability.zig`
  * `zigux/tests/phase13_devres_dma_coherent.zig`
  * `zigux/tests/phase13_landlock_ruleset.zig`
  * `zigux/tests/phase13_landlock_syscalls.zig`
  * `zigux/bindings/notifier_abi.zig`
  * `include/zigux/notifier_abi.h`
  * `zigux/helpers/notifier_chain_view.zig`
  * `scripts/zigux/check-phase13-devres-packet.py`
  * `scripts/zigux/validate-phase13-release.py`
  * `zigux/Makefile`
Tests-root reviewer prompt:
  * Do `Documentation/zigux/README.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, the Phase 13 release-notes and roadmap-traceability notes, the libfs, devres, Landlock, and notifier survey notes plus their paired Phase 13 slice notes, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase13_build.zig`, the four roadmap-anchor manifests plus `zigux/tests/phase13_notifier_list_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/validate-phase13-release.py`, `zigux/Makefile`, `make -C zigux phase13-validate`, `make -C zigux phase13`, the direct libfs helper plus `zigux/tests/phase13_libfs_reviewability.zig`, the direct devres helper plus `zigux/tests/phase13_devres_reviewability.zig` and `zigux/tests/phase13_devres_dma_coherent.zig`, the direct landlock-ruleset and landlock-syscalls helper replays, and the notifier ABI or helper footholds through `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig` still describe the same shipped validator-first release path without implying extra Phase 13 checker or replay surfaces that are not on `master`?
## Checklist carryover prompts

Keep these reviewer questions explicit when `zigux/tests/README.md` or other shared contributor-facing workflow notes are refreshed:
  * Phase 10: do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-core-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, `scripts/zigux/check-phase10-core-packet.py`, `zigux/tests/README.md`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_manifest.json`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `zigux/Makefile`, `zig build test --build-file zigux/tests/phase10_build.zig`, and `make -C zigux phase10` still keep the bounded virtio core, ring, input, and MMIO packet aligned without implying a dedicated `validate-phase10.py`, `check-phase10-harness-coverage.py`, or other shared Phase 10 validator surface that is not on `master`?
  * Phase 11: do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/Makefile`, and `make -C zigux phase11` still keep the shared-versus-dedicated simple-driver packet, the bounded `hvc_cleanup()` teardown handoff, and the dedicated `hvc_console` survey boundary aligned without implying a removed `validate-phase11.py`, missing build-inventory fixture, or checker-script stack?
  * Phase 13: do `Documentation/zigux/README.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `Documentation/zigux/phase13-notifier-list-survey.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, `zigux/tests/phase13_notifier_list_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/validate-phase13-release.py`, `zigux/Makefile`, `make -C zigux phase13-validate`, `make -C zigux phase13`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig` still keep the validator-first release path, the contributor workflow guide, the release-notes plus roadmap-traceability packet, the helper-family slice and survey notes, the shared contributor-surface sync note, the four roadmap-anchor manifests plus the adjacent notifier-list manifest, the shared review checklist, the dedicated devres packet guard, the direct validator gate, the Linux-style make replay routes, the direct libfs helper plus libfs reviewability replay, the direct devres, devres reviewability, devres DMA-coherent, landlock-ruleset, and landlock-syscalls helper replays, and the adjacent notifier ABI/helper evidence aligned without implying extra Phase 13 checker or replay surfaces that are not on `master`?
## Shared rule

When one of these packets changes, keep the tests-root replay file, the packet-local manifest or focused reviewability shard, and the validator-first review surface reviewable together.
