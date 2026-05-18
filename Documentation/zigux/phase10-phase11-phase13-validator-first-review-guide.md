# Phase 10, 11, and 13 Validator-First Review Guide

Use this focused contributor guide when a change touches the active Phase 10 virtio lab packet, the active Phase 11 simple-driver packet, or the active Phase 13 shared-helper release packet.

Pair this note with `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md` when the same review needs a compact tests-root checklist beside the docs-root and shared checklist prompts.
## Why this note exists

The shared scripts index already names the current checker stack for these packets, but reviewers still need one compact place that says which pre-replay gates, shared replay entrypoints, and adjacent evidence files should move together.
Keep `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md` aligned with this note when they describe the same active contributor packets, so checklist prompts, tests-root workflow guidance, and packet-local evidence do not drift into separate stories.
## Phase 10: Virtio lab packet

Keep the validator-first route explicit:
  * `python3 scripts/zigux/check-phase10-closure-inventory.py --self-test`
  * `python3 scripts/zigux/check-phase10-closure-inventory.py`
  * `python3 scripts/zigux/check-phase10-core-packet.py --self-test`
  * `python3 scripts/zigux/check-phase10-core-packet.py`
  * `python3 scripts/zigux/validate-phase10.py --self-test`
  * `python3 scripts/zigux/validate-phase10.py`
  * `python3 scripts/zigux/check-phase10-harness-coverage.py --self-test`
  * `python3 scripts/zigux/check-phase10-harness-coverage.py`
  * `python3 scripts/zigux/validate-phase10-closure.py --self-test`
  * `python3 scripts/zigux/validate-phase10-closure.py`
  * `make -C zigux phase10-validate`
  * `make -C zigux phase10-test`
  * `make -C zigux phase10`
Keep these evidence surfaces aligned in the same review:
  * `Documentation/zigux/phase10-closure-evidence.md`
  * `Documentation/zigux/phase10-virtio-ring-survey.md`
  * `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`
  * `Documentation/zigux/freeze-map.md`
  * `zigux-alpha/PHASE10_CLOSURE_LEDGER.md`
  * `zigux/tests/phase10_closure_manifest.json`
  * `zigux/tests/phase10_virtio_core_manifest.json`
  * `scripts/zigux/check-phase10-closure-inventory.py`
  * `scripts/zigux/check-phase10-core-packet.py`
  * `scripts/zigux/check-phase10-harness-coverage.py`
  * `zigux/tests/phase10_build.zig`
  * `zigux/tests/phase10_virtio_core.zig`
  * `zigux/tests/phase10_virtio_core_survey.zig`
  * `zigux/tests/phase10_virtio_ring_survey.zig`
  * `zigux/tests/phase10_virtio_input_survey.zig`
  * `zigux/tests/phase10_virtio_mmio_survey.zig`
  * `zigux/tests/phase10_virtio_ring_reset_reuse.zig`
  * `zigux/tests/phase10_virtio_input_multitouch_preflight.zig`
  * `zigux/tests/phase10_virtio_mmio_queue_isolation.zig`
  * `zigux/tests/phase10_virtio_ring_manifest.json`
  * `zigux/tests/phase10_virtio_input_manifest.json`
  * `zigux/tests/phase10_virtio_mmio_manifest.json`
  * `zigux/Makefile`
  * `.github/workflows/zigux-bootstrap.yml`
Reviewer prompt:

  * Does the shared Phase 10 packet still read as one validator-first lab bundle, with the shared core lab gate, all four lane survey manifests, all four lane survey replays, the shared closure manifest, the dedicated closure-ledger supplement, the focused ring drained-reset reuse replay, the focused multitouch preflight replay, and the focused MMIO queue-isolation replay, rather than a set of independent virtio starter files?
  * Does the parked Phase 10 freeze-boundary packet still keep `Documentation/zigux/phase10-virtio-ring-survey.md` explicit as the current `P10-L10` ring packet, while `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md` and `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md` still keep the adjacent freeze-boundary owner explicit as `P10-L11`, with `Documentation/zigux/freeze-map.md` still leaving `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` in the separate Phase 14 study-only family rather than silently counting them as Phase 10 virtio evidence?
## Phase 11: Simple-driver packet

Keep the pre-replay checker stack explicit:
  * `python3 scripts/zigux/check-phase11-build-inventory.py --self-test`
  * `python3 scripts/zigux/check-phase11-build-inventory.py`
  * `python3 scripts/zigux/check-phase11-layout-assert-surface.py --self-test`
  * `python3 scripts/zigux/check-phase11-layout-assert-surface.py`
  * `python3 scripts/zigux/check-phase11-hvc-validation-flow.py --self-test`
  * `python3 scripts/zigux/check-phase11-hvc-validation-flow.py`
  * `python3 scripts/zigux/check-phase11-hvc-cleanup-alignment.py --self-test`
  * `python3 scripts/zigux/check-phase11-hvc-cleanup-alignment.py`
  * `python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test`
  * `python3 scripts/zigux/check-phase11-shared-replay-contract.py`
  * `python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test`
  * `python3 scripts/zigux/check-phase11-header-boundary-packet.py`
  * `python3 scripts/zigux/validate-phase11.py --self-test`
  * `python3 scripts/zigux/validate-phase11.py`
  * `make -C zigux phase11-validate`
  * `make -C zigux phase11`
  * `make -C zigux phase11-hvc-survey`
Keep these evidence surfaces aligned in the same review:
  * `Documentation/zigux/phase11-shared-replay-contract.md`
  * `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  * `Documentation/zigux/phase11-uapi-header-parity-survey.md`
  * `Documentation/zigux/review-checklist.md`
  * `scripts/zigux/check-phase11-build-inventory.py`
  * `scripts/zigux/check-phase11-layout-assert-surface.py`
  * `scripts/zigux/check-phase11-hvc-validation-flow.py`
  * `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`
  * `scripts/zigux/check-phase11-shared-replay-contract.py`
  * `scripts/zigux/check-phase11-header-boundary-packet.py`
  * `zigux/tests/fixtures/phase11_build_inventory.json`
  * `zigux/tests/phase11_build.zig`
  * `zigux/tests/phase11_dw_wdt_suspend_resume.zig`
  * `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`
  * `zigux/tests/phase11_hvc_console_modem_control_split.zig`
  * `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
  * `zigux/tests/phase11_hvc_console_survey.zig`
  * `zigux/tests/phase11_uapi_header_parity_manifest.json`
  * `zigux/tests/phase11_gpio_wdt_manifest.json`
  * `zigux/tests/phase11_bcm2835_wdt_manifest.json`
  * `zigux/tests/phase11_dw_wdt_manifest.json`
  * `zigux/tests/phase11_hvc_console_manifest.json`
  * `zigux/Makefile`
  * `.github/workflows/zigux-bootstrap.yml`
Reviewer prompts:
  * Does the shared Phase 11 replay still stay separate from the dedicated archival `hvc_console` survey while the shared starter packet explicitly includes `zigux/tests/phase11_dw_wdt_suspend_resume.zig`, `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, and `zigux/tests/phase11_hvc_console_poll_retry_split.zig`?
  * Do the pre-replay checkers still describe the same delivery contract that the shared build inventory, the shared header-boundary packet, the active review checklist prompt, and the Phase 11 manifests claim?
## Phase 13: Shared-helper release packet

Keep the validator-first release route explicit:
  * `python3 scripts/zigux/check-phase13-libfs-packet.py --self-test`
  * `python3 scripts/zigux/check-phase13-libfs-packet.py`
  * `python3 scripts/zigux/check-phase13-devres-packet.py --self-test`
  * `python3 scripts/zigux/check-phase13-devres-packet.py`
  * `python3 scripts/zigux/check-phase13-notifier-packet.py --self-test`
  * `python3 scripts/zigux/check-phase13-notifier-packet.py`
  * `python3 scripts/zigux/check-phase13-release-replay-exact-counts.py --self-test`
  * `python3 scripts/zigux/check-phase13-release-replay-exact-counts.py`
  * `python3 scripts/zigux/validate-phase13-release.py`
  * `make -C zigux phase13-validate`
  * `make -C zigux phase13`
Keep these evidence surfaces aligned in the same review:
  * `scripts/zigux/README.md`
  * `Documentation/zigux/README.md`
  * `Documentation/zigux/review-checklist.md`
  * `Documentation/zigux/phase13-release-notes-survey.md`
  * `Documentation/zigux/phase13-roadmap-traceability.md`
  * `Documentation/zigux/phase13-libfs-survey.md`
  * `Documentation/zigux/phase13-devres-survey.md`
  * `Documentation/zigux/phase13-landlock-ruleset-survey.md`
  * `Documentation/zigux/phase13-landlock-syscalls-survey.md`
  * `Documentation/zigux/phase13-notifier-list-survey.md`
  * `scripts/zigux/check-phase13-libfs-packet.py`
  * `scripts/zigux/check-phase13-devres-packet.py`
  * `scripts/zigux/check-phase13-notifier-packet.py`
  * `scripts/zigux/check-phase13-release-replay-exact-counts.py`
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
  * `zigux/tests/phase13_landlock_syscalls.zig`
  * `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
  * `zigux/tests/phase13_landlock_ruleset_fops_sync.zig`
  * `zigux/tests/phase13_notifier_list_reviewability.zig`
  * `zigux/bindings/notifier_abi.zig`
  * `include/zigux/notifier_abi.h`
  * `zigux/helpers/notifier_chain_view.zig`
  * `zigux/Makefile`
  * `.github/workflows/zigux-bootstrap.yml`
Reviewer prompt:
  * Does the shared Phase 13 packet still route through the libfs, devres, notifier, and exact-count guards plus the release validator before the fifteen-step replay bundle, with the scripts index, docs-root summary, review checklist, the dedicated libfs packet guard, the dedicated devres packet guard, the dedicated notifier packet guard, the shared replay-count guard, the direct libfs, devres, landlock-ruleset, and landlock-syscalls helper replays, the dedicated Landlock ruleset reviewability gate, the devres coherent-DMA plus plain-helper, `iounmap`, `iomap`, and wrapper reviewability gates, the Landlock ruleset plus ruleset-fops-sync plus syscall reviewability gates, the adjacent notifier reviewability packet, the dedicated exported C header in `include/zigux/notifier_abi.h`, the Zig notifier ABI foothold in `zigux/bindings/notifier_abi.zig`, and the direct notifier-chain-view replay through `zigux/helpers/notifier_chain_view.zig` all naming the same shared helper surfaces rather than letting those release surfaces drift apart?
## Checklist carryover prompts

Keep these reviewer questions explicit when `Documentation/zigux/review-checklist.md` or other shared contributor surfaces are refreshed:
  * Phase 10: do `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `Documentation/zigux/freeze-map.md`, `zigux-alpha/PHASE10_CLOSURE_LEDGER.md`, `zigux/tests/phase10_closure_manifest.json`, `scripts/zigux/check-phase10-closure-inventory.py`, `scripts/zigux/check-phase10-core-packet.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_input_multitouch_preflight.zig`, and `zigux/tests/phase10_virtio_mmio_queue_isolation.zig` still describe the same validator-first lab bundle and keep the current `P10-L10` ring packet plus the adjacent `P10-L11` freeze-boundary owner explicit?
  * Phase 11: do `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-layout-assert-surface.py`, `scripts/zigux/check-phase11-hvc-validation-flow.py`, `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_dw_wdt_suspend_resume.zig`, `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, and `zigux/tests/phase11_uapi_header_parity_manifest.json` still keep the pre-replay stack, the shared-versus-dedicated `hvc_console` split, and the shared header-boundary packet aligned?
  * Phase 13: do `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-notifier-list-survey.md`, `Documentation/zigux/README.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, `zigux/tests/phase13_notifier_list_manifest.json`, `scripts/zigux/check-phase13-libfs-packet.py`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/check-phase13-notifier-packet.py`, `scripts/zigux/check-phase13-release-replay-exact-counts.py`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_iounmap_reviewability.zig`, `zigux/tests/phase13_devres_iomap_reviewability.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_wrapper_reviewability.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_reviewability.zig`, `zigux/tests/phase13_landlock_ruleset_fops_sync.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig` still keep the validator-first release path, the four roadmap-anchor manifests plus the adjacent notifier-list manifest, the dedicated libfs, devres, and notifier packet guards, the shared replay-count guard, the direct libfs helper plus libfs reviewability replay, the direct devres, landlock-ruleset, and landlock-syscalls helper replays, the devres coherent-DMA plus plain-helper, `iounmap`, `iomap`, and wrapper reviewability gates, the Landlock ruleset plus ruleset-fops-sync plus syscall reviewability gates, the adjacent notifier evidence, the dedicated exported C header foothold, the Zig notifier ABI foothold, and the direct notifier-chain-view replay aligned?
## Shared review rule

When one of these packets changes, keep the checker stack, the shared replay path, and the named evidence files reviewable together. Do not treat a passing build file, one manifest refresh, or one survey note edit as enough on its own.
