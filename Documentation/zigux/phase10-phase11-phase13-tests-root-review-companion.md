# Phase 10, 11, and 13 Tests-Root Review Companion

Use this note when a change touches the active Phase 10 virtio lab packet, the active Phase 11 simple-driver packet, or the active Phase 13 shared-helper release packet and the review needs a compact tests-root checklist.
Keep `Documentation/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/helpers/notifier_chain_view.zig`, `drivers/tty/hvc/hvc_console.h`, and `scripts/zigux/README.md` aligned with this note when they describe the same packet so the shared reviewer prompts do not drift across docs-root, tests-root, checklist-facing, and scripts-root guidance.
## Phase 10 tests-root packet

Keep the shared build-backed virtio packet explicit:
  * `Documentation/zigux/README.md`
  * `scripts/zigux/README.md`
  * `Documentation/zigux/review-checklist.md`
  * `Documentation/zigux/freeze-map.md`
  * `Documentation/zigux/phase10-closure-evidence.md`
  * `Documentation/zigux/phase10-virtio-core-slice.md`
  * `Documentation/zigux/phase10-virtio-core-survey.md`
  * `drivers/virtio/virtio_verify.zig`
  * `Documentation/zigux/phase10-virtio-ring-slice.md`
  * `Documentation/zigux/phase10-virtio-ring-survey.md`
  * `drivers/virtio/virtio_ring_verify.zig`
  * `Documentation/zigux/phase10-virtio-input-slice.md`
  * `Documentation/zigux/phase10-virtio-input-module-slice.md`
  * `Documentation/zigux/phase10-virtio-input-survey.md`
  * `drivers/virtio/virtio_input_verify.zig`
  * `Documentation/zigux/phase10-virtio-mmio-slice.md`
  * `Documentation/zigux/phase10-virtio-mmio-survey.md`
  * `drivers/virtio/virtio_mmio_verify.zig`
  * `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
  * `zigux/tests/README.md`
  * `scripts/zigux/check-phase10-core-packet.py`
  * `scripts/zigux/check-phase10-ring-packet.py`
  * `scripts/zigux/check-phase10-input-packet.py`
  * `scripts/zigux/check-phase10-mmio-packet.py`
  * `scripts/zigux/check-phase10-mmio-freeze-boundary.py`
  * `zigux/tests/phase10_build.zig`
  * `zigux/tests/phase10_closure_manifest.json`
  * `zigux/tests/phase10_virtio_core.zig`
  * `zigux/tests/phase10_virtio_core_reset_queue.zig`
  * `zigux/tests/phase10_virtio_driver_id.zig`
  * `drivers/virtio/virtio_driver_id.zig`
  * `drivers/virtio/virtio.zig`
  * `zigux/tests/phase10_virtio_core_manifest.json`
  * `zigux/tests/phase10_virtio_core_survey.zig`
  * `zigux/tests/phase10_virtio_ring.zig`
  * `zigux/tests/phase10_virtio_ring_manifest.json`
  * `zigux/tests/phase10_virtio_ring_survey.zig`
  * `zigux/tests/phase10_virtio_input.zig`
  * `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`
  * `zigux/tests/phase10_virtio_input_registration_preflight.zig`
  * `zigux/tests/phase10_virtio_input_teardown_observation.zig`
  * `zigux/tests/phase10_virtio_input_manifest.json`
  * `zigux/tests/phase10_virtio_input_status_drain.zig`
  * `zigux/tests/phase10_virtio_input_survey.zig`
  * `zigux/tests/phase10_virtio_mmio.zig`
  * `zigux/tests/phase10_virtio_mmio_manifest.json`
  * `zigux/tests/phase10_virtio_mmio_survey.zig`
  * `zigux/Makefile`
  * `zig build test --build-file zigux/tests/phase10_build.zig`
  * `make -C zigux phase10-test`
  * `make -C zigux phase10`
Treat the separate Phase 5 reference-sample packet and the separate Phase 9 runtime-loader packet as adjacent boundary evidence rather than counted Phase 10 virtio closure proof; in particular, keep the already-shipped `samples/zigux/runtime_trace_events_loader.zig` scaffold visible through `zigux/tests/phase10_closure_manifest.json` without letting that loader evidence read as additional virtio transport closure.
Tests-root reviewer prompt:

  * Do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase10-closure-evidence.md`, the Phase 10 core, ring, input, and MMIO slice or survey notes, `drivers/virtio/virtio_verify.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_input_verify.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `scripts/zigux/check-phase10-core-packet.py`, `scripts/zigux/check-phase10-ring-packet.py`, `scripts/zigux/check-phase10-input-packet.py`, `scripts/zigux/check-phase10-mmio-packet.py`, `scripts/zigux/check-phase10-mmio-freeze-boundary.py`, `zigux/tests/README.md`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_closure_manifest.json`, the shipped focused Phase 10 replays including `zigux/tests/phase10_virtio_driver_id.zig`, `drivers/virtio/virtio_driver_id.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, and `zigux/tests/phase10_virtio_mmio.zig`, the four shipped survey manifests, the four shipped survey gates, `zigux/Makefile`, `zig build test --build-file zigux/tests/phase10_build.zig`, `make -C zigux phase10-test`, and `make -C zigux phase10` still describe the same bounded build-backed virtio lab packet instead of implying a larger validator stack that is not on `master`, and do they keep the blocked risky-transport posture, the allowed `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` destination family, the separate `reference_samples` and `runtime_starters` boundary posture carried through `zigux/tests/phase10_closure_manifest.json`, the already-shipped `samples/zigux/runtime_trace_events_loader.zig` scaffold as adjacent Phase 9 evidence rather than Phase 10 closure progress, and the separate Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit?
## Phase 11 tests-root packet

Keep the current shared-versus-dedicated simple-driver packet explicit:
  * `Documentation/zigux/README.md`
  * `scripts/zigux/README.md`
  * `zigux/tests/README.md`
  * `Documentation/zigux/phase11-shared-replay-contract.md`
  * `Documentation/zigux/phase11-closure-note.md`
  * `Documentation/zigux/phase11-driver-lane-sequencing.md`
  * `Documentation/zigux/review-checklist.md`
  * `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
  * `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
  * `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
  * `Documentation/zigux/phase11-gpio-wdt-survey.md`
  * `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
  * `Documentation/zigux/phase11-dw-wdt-survey.md`
  * `Documentation/zigux/phase11-dw-wdt-teardown-note.md`
  * `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  * `Documentation/zigux/phase11-hvc-console-survey.md`
  * `Documentation/zigux/phase11-hvc-console-teardown-note.md`
  * `Documentation/zigux/phase11-uapi-header-parity-survey.md`
  * `scripts/zigux/check-phase11-shared-replay-contract.py`
  * `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`
  * `scripts/zigux/check-phase11-header-boundary-packet.py`
  * `scripts/zigux/check-phase11-hvc-survey-packet.py`
  * `zigux/tests/phase11_build.zig`
  * `zigux/tests/phase11_gpio_wdt.zig`
  * `zigux/tests/phase11_gpio_wdt_manifest.json`
  * `zigux/tests/phase11_gpio_wdt_survey.zig`
  * `zigux/tests/phase11_bcm2835_wdt.zig`
  * `zigux/tests/phase11_bcm2835_wdt_manifest.json`
  * `zigux/tests/phase11_bcm2835_wdt_survey.zig`
  * `zigux/tests/phase11_dw_wdt.zig`
  * `zigux/tests/phase11_dw_wdt_manifest.json`
  * `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
  * `zigux/tests/phase11_dw_wdt_survey.zig`
  * `zigux/tests/phase11_hvc_console.zig`
  * `zigux/tests/phase11_hvc_cleanup.zig`
  * `zigux/tests/phase11_hvc_console_manifest.json`
  * `zigux/tests/phase11_hvc_console_survey.zig`
  * `zigux/tests/phase11_uapi_header_parity_manifest.json`
  * `zigux/tests/phase11_uapi_header_parity_survey.zig`
  * `drivers/watchdog/bcm2835_wdt_verify.zig`
  * `drivers/watchdog/dw_wdt_verify.zig`
  * `drivers/tty/hvc/hvc_console_verify.zig`
  * `zigux/Makefile`
  * `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
  * `make -C zigux phase11`
  * `make -C zigux phase11-hvc-survey`
Tests-root reviewer prompt:
  * Do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, the four Phase 11 validation matrices, `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_gpio_wdt_survey.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/Makefile`, `make -C zigux phase11`, and `make -C zigux phase11-hvc-survey` still describe the same shared-versus-dedicated simple-driver packet, the bounded `hvc_cleanup()` teardown handoff, the parked shared closure checkpoint, the parked driver-lane owner map, the dedicated bcm2835 archival packet, the dedicated DesignWare teardown and registration-scaffold boundary, the dedicated `hvc_console` teardown and verify boundary, the focused header-boundary survey packet, and the focused contract, bcm2835 archival, header-boundary, and HVC checker split without implying a removed `validate-phase11.py`, missing build-inventory fixture, or broader checker-script packet that is not on `master`?
  * Does `Documentation/zigux/phase11-hvc-console-survey.md` stay paired with `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_survey.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, and `make -C zigux phase11-hvc-survey` as the dedicated archival replay while `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_gpio_wdt_survey.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, and the live `make -C zigux phase11` route keep the shipped shared replay split, bounded teardown handoff, focused header-boundary survey evidence, and focused checker-backed contributor guidance explicit?
  * Does `Documentation/zigux/phase11-bcm2835-wdt-survey.md` stay paired with `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py --self-test`, and `python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py` as the dedicated archival replay while `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_gpio_wdt_survey.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, and the live `make -C zigux phase11` route keep the shipped shared replay split, the dedicated DesignWare and HVC teardown boundaries, the focused header-boundary survey evidence, and the dedicated bcm2835 archival packet explicit without widening the shared replay route itself?
## Phase 13 tests-root packet

Keep the shared validator-first release packet explicit:
  * `Documentation/zigux/README.md`
  * `scripts/zigux/README.md`
  * `Documentation/zigux/phase13-contributor-workflow-guide.md`
  * `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
  * `Documentation/zigux/phase13-release-notes-survey.md`
  * `Documentation/zigux/phase13-roadmap-traceability.md`
  * `Documentation/zigux/phase13-libfs-slice.md`
  * `Documentation/zigux/phase13-libfs-survey.md`
  * `Documentation/zigux/phase13-devres-slice.md`
  * `Documentation/zigux/phase13-devres-survey.md`
  * `Documentation/zigux/phase13-landlock-ruleset-slice.md`
  * `Documentation/zigux/phase13-landlock-ruleset-survey.md`
  * `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
  * `Documentation/zigux/phase13-landlock-syscalls-slice.md`
  * `Documentation/zigux/phase13-landlock-syscalls-survey.md`
  * `Documentation/zigux/phase13-landlock-syscalls-governance.md`
  * `Documentation/zigux/phase13-notifier-list-survey.md`
  * `scripts/zigux/check-phase13-notifier-packet.py`
  * `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
  * `Documentation/zigux/review-checklist.md`
  * `zigux/tests/README.md`
  * `zigux/tests/phase13_build.zig`
  * `zigux/tests/phase13_libfs.zig`
  * `zigux/tests/phase13_libfs_addressability.zig`
  * `zigux/tests/phase13_devres.zig`
  * `zigux/tests/phase13_libfs_manifest.json`
  * `zigux/tests/phase13_devres_manifest.json`
  * `zigux/tests/phase13_landlock_ruleset_manifest.json`
  * `zigux/tests/phase13_landlock_syscalls_manifest.json`
  * `zigux/tests/phase13_notifier_list_manifest.json`
  * `zigux/tests/phase13_notifier_list_reviewability.zig`
  * `zigux/helpers/list_view.zig`
  * `zigux/helpers/hlist_view.zig`
  * `include/zigux/abi.h`
  * `zigux/tests/phase13_libfs_reviewability.zig`
  * `zigux/tests/phase13_devres_reviewability.zig`
  * `zigux/tests/phase13_devres_dma_coherent.zig`
  * `zigux/tests/phase13_devres_boundary_evidence.zig`
  * `zigux/tests/phase13_landlock_ruleset.zig`
  * `zigux/tests/phase13_landlock_syscalls.zig`
  * `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
  * `include/zigux/notifier_abi.h`
  * `zigux/bindings/notifier_abi.zig`
  * `zigux/helpers/notifier_chain_view.zig`
  * `drivers/tty/hvc/hvc_console.h`
  * `scripts/zigux/check-phase13-devres-packet.py`
  * `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
  * `scripts/zigux/validate-phase13-release.py`
  * `zigux/Makefile`
  * `make -C zigux phase13-validate`
  * `make -C zigux phase13`
Tests-root reviewer prompt:
  * Do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, the Phase 13 release-notes and roadmap-traceability notes, the libfs, devres, Landlock, and notifier survey notes plus their paired Phase 13 slice notes, `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/phase13_build.zig`, the four roadmap-anchor manifests plus `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/validate-phase13-release.py`, `zigux/Makefile`, `make -C zigux phase13-validate`, `make -C zigux phase13`, the direct libfs helper plus `zigux/tests/phase13_libfs_addressability.zig` and `zigux/tests/phase13_libfs_reviewability.zig`, the direct devres helper plus `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, and `zigux/tests/phase13_devres_boundary_evidence.zig`, the direct landlock-ruleset helper plus the direct landlock-syscalls helper and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and the adjacent notifier ABI and helper footholds through `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `include/zigux/abi.h`, `include/zigux/notifier_abi.h`, `zigux/bindings/notifier_abi.zig`, `zigux/helpers/notifier_chain_view.zig`, and `drivers/tty/hvc/hvc_console.h` still describe the same shipped validator-first release path without implying extra Phase 13 checker or replay surfaces that are not on `master`, and does the sequencing note keep `libfs`, `devres` helper parity, `devres` packet truthfulness, `landlock`, and adjacent notifier evidence from being treated as one shared owner?
## Checklist carryover prompts

Keep these reviewer questions explicit when `zigux/tests/README.md` or other shared contributor-facing workflow notes are refreshed:
  * Phase 10: do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-core-survey.md`, `drivers/virtio/virtio_verify.zig`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `drivers/virtio/virtio_ring_verify.zig`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, `drivers/virtio/virtio_input_verify.zig`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, `drivers/virtio/virtio_mmio_verify.zig`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `scripts/zigux/check-phase10-core-packet.py`, `scripts/zigux/check-phase10-ring-packet.py`, `scripts/zigux/check-phase10-input-packet.py`, `scripts/zigux/check-phase10-mmio-packet.py`, `scripts/zigux/check-phase10-mmio-freeze-boundary.py`, `zigux/tests/README.md`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_closure_manifest.json`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `drivers/virtio/virtio_driver_id.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, `zigux/tests/phase10_virtio_input_manifest.json`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `zigux/Makefile`, `zig build test --build-file zigux/tests/phase10_build.zig`, and `make -C zigux phase10-test` plus `make -C zigux phase10` still keep the bounded virtio core, ring, input, and MMIO packet aligned without implying a dedicated `validate-phase10.py`, `check-phase10-harness-coverage.py`, or other shared Phase 10 validator surface that is not on `master`, while also keeping the blocked risky-transport posture, the allowed `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` destination family, the separate `reference_samples` and `runtime_starters` boundary posture carried through `zigux/tests/phase10_closure_manifest.json`, the already-shipped `samples/zigux/runtime_trace_events_loader.zig` scaffold as adjacent Phase 9 evidence rather than Phase 10 closure progress, and the separate Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit?
  * Phase 11: do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_gpio_wdt_survey.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `zig build test --build-file zigux/tests/phase11_build.zig --summary all`, `zigux/Makefile`, `make -C zigux phase11`, and `make -C zigux phase11-hvc-survey` still keep the shared-versus-dedicated simple-driver packet, the bounded `hvc_cleanup()` teardown handoff, the parked shared closure checkpoint, the parked driver-lane owner map, the dedicated bcm2835 archival packet, the dedicated DesignWare teardown and registration-scaffold boundary, the dedicated `hvc_console` teardown and verify boundary, the focused header-boundary survey packet, and the focused contract, bcm2835 archival, header-boundary, and HVC checker split aligned without implying a removed `validate-phase11.py`, missing build-inventory fixture, or checker-script stack?
  * Phase 13: do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-notifier-list-survey.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/validate-phase13-release.py`, `zigux/Makefile`, `make -C zigux phase13-validate`, `make -C zigux phase13`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `include/zigux/abi.h`, `include/zigux/notifier_abi.h`, `zigux/bindings/notifier_abi.zig`, `zigux/helpers/notifier_chain_view.zig`, and `drivers/tty/hvc/hvc_console.h` still keep the validator-first release path, the contributor workflow guide, the sequencing note, the release-notes plus roadmap-traceability packet, the helper-family slice and survey notes, the two Landlock helper-owned boundary notes, the shared contributor-surface sync note, the four roadmap-anchor manifests plus the adjacent notifier-list manifest and reviewability replay, the shared review checklist, the broader tests-root guide, the dedicated devres and landlock-ruleset packet guards, the direct notifier packet guard, the direct validator gate, the Linux-style make replay routes, the direct libfs helper plus libfs addressability and libfs reviewability evidence, the direct devres, devres reviewability, devres DMA-coherent, devres boundary-evidence, landlock-ruleset, landlock-syscalls, and landlock-syscalls reviewability helper evidence, and the adjacent notifier ABI and helper footholds through `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `include/zigux/abi.h`, `include/zigux/notifier_abi.h`, `zigux/bindings/notifier_abi.zig`, `zigux/helpers/notifier_chain_view.zig`, and `drivers/tty/hvc/hvc_console.h` aligned without implying extra Phase 13 checker or replay surfaces that are not on `master`?
## Shared rule

When one of these packets changes, keep the tests-root replay file, the packet-local manifest or focused reviewability shard, and the validator-first review surface reviewable together.
