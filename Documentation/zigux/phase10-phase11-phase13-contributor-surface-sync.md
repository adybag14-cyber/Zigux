# Phase 10, 11, and 13 Contributor Surface Sync
Use this note when a change touches the active Phase 10 virtio packet, the active Phase 11 simple-driver packet, or the active Phase 13 shared-helper packet and the review needs one compact contributor-facing owner map.

## Purpose
Keep the broad contributor surfaces aligned so docs-root, scripts-root, tests-root, and checklist-facing reminders do not drift across the three still-active shared packets.

Shared surfaces to keep aligned:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-libfs-slice.md`
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`
- `Documentation/zigux/phase13-devres-iounmap-planner.md`
- `Documentation/zigux/phase13-devres-iomap-planner.md`
- `Documentation/zigux/phase13-devres-scatterlist-slice.md`
- `Documentation/zigux/phase13-devres-scatterlist-planner.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `Documentation/zigux/phase13-notifier-summary-gap.md`
- `scripts/zigux/check-phase13-tests-readme-alignment.py`
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `scripts/zigux/check-phase13-landlock-syscalls-packet.py`
- `scripts/zigux/validate-phase13-release.py`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

## Phase 10 contributor packet
Keep the bounded virtio packet explicit through:
- `Documentation/zigux/phase10-closure-evidence.md`
- `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
- `Documentation/zigux/phase10-virtio-core-survey.md`
- `Documentation/zigux/phase10-virtio-core-slice.md`
- `Documentation/zigux/phase10-virtio-ring-survey.md`
- `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`
- `Documentation/zigux/phase10-virtio-input-survey.md`
- `Documentation/zigux/phase10-virtio-mmio-survey.md`
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `drivers/virtio/virtio_driver_id.zig`
- `zigux/tests/phase10_virtio_driver_id.zig`
- `scripts/zigux/check-phase10-bootstrap-route.py`
- `scripts/zigux/check-phase10-core-packet.py`
- `scripts/zigux/check-phase10-shared-freeze-boundary.py`
- `scripts/zigux/check-phase10-ring-packet.py`
- `scripts/zigux/check-phase10-input-packet.py`
- `scripts/zigux/check-phase10-mmio-packet.py`
- `scripts/zigux/check-phase10-harness-coverage.py`
- `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`
- `scripts/zigux/check-phase10-closure-manifest-counts.py`
- `scripts/zigux/validate-phase10.py`
- `scripts/zigux/validate-phase10-closure.py`
- `zigux/tests/phase10_closure_manifest.json`
- `zigux/tests/phase10_build.zig`
- `zigux/Makefile`
- `make -C zigux phase10-validate`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Current direct readback for this shared contributor lane is narrower than the full historical packet list above: `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-virtio-core-survey.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/check-phase10-bootstrap-route.py`, `scripts/zigux/check-phase10-shared-freeze-boundary.py`, `scripts/zigux/check-phase10-ring-packet.py`, `scripts/zigux/check-phase10-input-packet.py`, `scripts/zigux/check-phase10-mmio-packet.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, `scripts/zigux/check-phase10-closure-manifest-counts.py`, `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase10_closure_manifest.json`, `zigux/tests/phase10_build.zig`, and `zigux/Makefile` remain directly re-readable here. Current `master` now also rematerializes `Documentation/zigux/phase10-virtio-core-slice.md`, `scripts/zigux/check-phase10-core-packet.py`, `drivers/virtio/virtio_driver_id.zig`, and `zigux/tests/phase10_virtio_driver_id.zig`, so keep that returned core-side slice, checker, and driver-id pair explicit beside the returned closure-manifest count guard, validator pair, and shared build-gate route names. Current `master` still does not materialize `scripts/zigux/check-phase10-mmio-freeze-boundary.py` through this lane's authenticated readback, so keep that older checker name outside the live shared contributor packet until a fresh reread proves it returned. Current `master` does materialize `zigux/Makefile`, and its live body exposes `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10`, so keep that returned file, the returned validator pair, the returned closure-manifest count guard, and those shared build-gate route names explicit instead of treating them as missing-route vocabulary.

Contributor reminder:
- keep the blocked risky-transport posture explicit
- keep the allowed `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` destination family explicit
- keep the parked `P10-L11` MMIO freeze-boundary owner and rollback-owner note explicit around `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, and `scripts/zigux/check-phase10-shared-freeze-boundary.py`
- keep Phase 5 reference samples and Phase 9 runtime starters as adjacent evidence, not extra Phase 10 closure proof
- keep the separate Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit
- keep `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, and `Documentation/zigux/phase10-virtio-mmio-slice.md` explicit as directly re-readable shared-review evidence on current `master`, keep `Documentation/zigux/phase10-virtio-mmio-survey.md` as the directly re-readable MMIO companion, and keep `Documentation/zigux/phase10-virtio-core-slice.md`, `scripts/zigux/check-phase10-core-packet.py`, `drivers/virtio/virtio_driver_id.zig`, and `zigux/tests/phase10_virtio_driver_id.zig` explicit as the returned core-side slice, checker, and driver-id pair on current `master`

## Phase 11 contributor packet
Keep the current-head simple-driver truthfulness packet explicit through:
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`
- `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`
- `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `drivers/watchdog/dw_wdt.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `drivers/watchdog/dw_wdt_pm.zig`
- `drivers/watchdog/dw_wdt_pm_scaffold.zig`
- `drivers/tty/hvc/hvc_console.zig`
- `drivers/tty/hvc/hvc_console.h`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-shared-replay-contract-counts.py`
- `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `scripts/zigux/validate-phase11.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt.zig`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
- `zigux/tests/phase11_hvc_modem_control_proof.zig`
- `zigux/tests/phase11_hvc_modem_control_proof_build.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`
- `zigux/Makefile`
- `make -C zigux phase11-validate`

Current repo rereads for this contributor lane now keep all four driver-local Phase 11 validation matrices explicit on current `master`: `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`. Authenticated contents reads in this runtime rematerialize the gpio and HVC matrix notes directly, while raw `master` fallback rereads rematerialize the bcm2835 and DesignWare matrix notes, so keep those returned matrix notes explicit. The current-head DesignWare continuity packet is narrower here: keep `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, the paired DesignWare guard scripts through `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py` and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, and the adjacent PM helper pair `drivers/watchdog/dw_wdt_pm.zig` plus `drivers/watchdog/dw_wdt_pm_scaffold.zig` explicit as current-head evidence here, while `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `zigux/tests/phase11_dw_wdt_survey.zig`, and broader live platform-backed registration, PM execution, IRQ execution, MMIO validation, and shared replay should stay framed as separate-lane or repo-reality-gap follow-through. The returned HVC continuity packet is also broader than the older proof-only reminder wording here: keep `zigux/tests/phase11_hvc_modem_control_proof.zig`, `zigux/tests/phase11_hvc_modem_control_proof_build.zig`, `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`, `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`, and `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` explicit beside the existing current-head checker, build inventory, and proof-backed adjunct stack. Keep the current shared replay-contract note explicit beside `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase11-validation-matrix-gap-survey.md`, and the shared validation-and-build gate so contributor-facing reminder work does not leave the current shared Phase 11 truthfulness note behind the narrower DesignWare continuity packet and the narrower HVC current-head evidence. Keep the shared Phase 11 validation-and-build gate explicit through `scripts/zigux/validate-phase11.py`, `zigux/Makefile`, and `make -C zigux phase11-validate` so contributor-facing reminder work does not leave the validator-first lane handle implicit beside the narrower DesignWare continuity packet and the narrower HVC current-head evidence. Keep the narrower HVC current-head continuity packet as adjacent shared evidence rather than a full Phase 11 replay roster.

Contributor reminder:
- keep the shared-versus-dedicated split explicit instead of collapsing the smaller current-head truthfulness packet into one generic driver note
- keep the current-head shared packet rooted in `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase11-validation-matrix-gap-survey.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, the returned driver-local validation matrices `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, with the bcm2835 and DesignWare matrix notes currently returning through raw `master` fallback while gpio and HVC stay directly readable through the authenticated contents bridge, the narrower DesignWare continuity packet through `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `drivers/watchdog/dw_wdt_pm.zig`, and `drivers/watchdog/dw_wdt_pm_scaffold.zig`, the HVC current-head continuity packet through `drivers/tty/hvc/hvc_console.zig`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`, `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-shared-replay-contract-counts.py`, `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`, `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`, `zigux/tests/phase11_hvc_export_surface_layout_build.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`, `zigux/tests/phase11_hvc_cleanup_packet_build.zig`, `zigux/tests/phase11_hvc_modem_control_proof.zig`, `zigux/tests/phase11_hvc_modem_control_proof_build.zig`, `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`, and `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`, plus the adjacent shared header-boundary proof shard through `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`, and `drivers/tty/hvc/hvc_console.h`, with the shared validation-and-build gate kept explicit through `scripts/zigux/validate-phase11.py`, `zigux/Makefile`, and `make -C zigux phase11-validate`; do not imply that `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `zigux/tests/phase11_dw_wdt_survey.zig`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-shared-summary-surfaces.py`, `zigux/tests/phase11_build.zig`, `make -C zigux phase11`, `make -C zigux phase11-contract`, or the exact shared `zig build test --build-file zigux/tests/phase11_build.zig --summary all` replay are back on current `master` without a fresh reread; `zigux/Makefile` now rematerializes on current `master`, and its live body exposes `make -C zigux phase11-validate`, but it still does not expose `make -C zigux phase11` or `make -C zigux phase11-contract`
- keep the validation-matrix gap survey, the returned bcm2835, gpio, HVC, and DesignWare driver-local matrix notes, the narrower DesignWare platform-registration, provenance, lane-gap, verify-alignment, driver, test, registration-scaffold, and PM-helper packet, the adjacent shared header-boundary proof shard, the current shared replay-contract note, and the narrower HVC continuity build inventory aligned with the direct readback boundary without using that broader reminder packet to overclaim shared replay or live platform-backed execution
- keep bcm2835 and DesignWare explicit as returned matrix and continuity evidence while their deeper platform-backed registration, PM, IRQ, and MMIO follow-through stays in separate continuity lanes rather than broad contributor-proof vocabulary, and do not mistake the still-returned `drivers/watchdog/dw_wdt_pm.zig` and `drivers/watchdog/dw_wdt_pm_scaffold.zig` helpers for proof that live watchdog-core registration or live MMIO validation has landed
- keep the HVC packet framed as current-head continuity through the returned starter, companion notes, validation matrix, coupled checkers, shared build inventory, proof-backed adjunct builds, the returned modem-control proof pair, and the standalone targetless-unregister witness pair instead of calling the archived direct driver, teardown, split-replay, or sysrq files current-head readback evidence
- keep only genuinely materialized current-head Phase 11 surfaces explicit in broad contributor wording; do not promote missing watchdog, HVC, shared closure-side checker, or aggregate replay paths back into live contributor-facing evidence from older summary wording alone

## Phase 13 contributor packet
Keep the shared-helper packet explicit through the verified docs-root and contributor-facing reminder surfaces:
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `Documentation/zigux/phase13-notifier-summary-gap.md`
- `Documentation/zigux/phase13-libfs-slice.md`
- `fs/libfs.zig`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_libfs_manifest.json`
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`
- `Documentation/zigux/phase13-devres-iounmap-planner.md`
- `Documentation/zigux/phase13-devres-iomap-planner.md`
- `Documentation/zigux/phase13-devres-scatterlist-slice.md`
- `Documentation/zigux/phase13-devres-scatterlist-planner.md`
- `scripts/zigux/check-phase13-devres-dma-boundary.py`
- `scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`
- `scripts/zigux/check-phase13-devres-iounmap-planner.py`
- `scripts/zigux/check-phase13-devres-iomap-planner.py`
- `scripts/zigux/check-phase13-devres-mmio-packet.py`
- `scripts/zigux/check-phase13-devres-current-packet.py`
- `scripts/zigux/check-phase13-devres-scatterlist-planner.py`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`
- `zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig`
- `zigux/tests/phase13_devres_iounmap_planner.zig`
- `zigux/tests/phase13_devres_iounmap_planner_manifest.json`
- `zigux/tests/phase13_devres_iomap_planner.zig`
- `zigux/tests/phase13_devres_iomap_planner_manifest.json`
- `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `lib/devres.zig`
- `lib/devres_scatterlist.zig`
- `zigux/tests/phase13_devres_scatterlist.zig`
- `zigux/tests/phase13_devres_scatterlist_build.zig`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `scripts/zigux/check-phase13-landlock-syscalls-packet.py`
- `security/landlock/ruleset.zig`
- `security/landlock/syscalls.zig`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `scripts/zigux/check-phase13-tests-readme-alignment.py`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/abi.h`
- `drivers/tty/hvc/hvc_console.h`

Contributor reminder:
- keep the shared contributor-facing handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, keep `Documentation/zigux/phase13-release-coordination-matrix.md` plus `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` explicit as supporting coordination companions rather than as the stable handle itself, keep `scripts/zigux/check-phase13-shared-summary-surfaces.py` explicit as the shipped shared-summary guard beside that stable handle, keep `scripts/zigux/validate-phase13-release.py` explicit as the shipped release-discipline validator beside that same stable handle, keep `zigux/Makefile` explicit only as the returned file, and keep `make -C zigux phase13-validate` plus blocked convenience route `make -C zigux phase13` framed as the still-missing shared build routes on current `master`
- keep the shipped broader Phase 13 tests-root guide in `zigux/tests/README.md` explicit as shared packet evidence and keep it aligned with the workflow guide, shared-helper sequencing note, release-coordination matrix, release-notes survey, roadmap-traceability note, shared-summary-gap note, notifier-summary-gap note, review checklist, shared contributor-sync note, tests-root companion, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, and `scripts/zigux/check-phase13-tests-readme-alignment.py`
- keep `scripts/zigux/validate-phase13-release.py` explicit as the shipped release-discipline validator beside the stable contributor-facing handle, while `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, and `include/zigux/notifier_abi.h` remain repo-reality gaps until current `master` materializes them again
- keep helper-local `libfs`, the narrower current-master `devres` survey, DMA-boundary, the `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`, `Documentation/zigux/phase13-devres-iounmap-planner.md`, `Documentation/zigux/phase13-devres-iomap-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-planner.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-iounmap-planner.py`, `scripts/zigux/check-phase13-devres-iomap-planner.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `scripts/zigux/check-phase13-devres-current-packet.py`, `scripts/zigux/check-phase13-devres-scatterlist-planner.py`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig`, `zigux/tests/phase13_devres_iounmap_planner.zig`, `zigux/tests/phase13_devres_iounmap_planner_manifest.json`, `zigux/tests/phase13_devres_iomap_planner.zig`, `zigux/tests/phase13_devres_iomap_planner_manifest.json`, `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`, `zigux/tests/phase13_devres_dma_coherent.zig`, `lib/devres.zig`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist_build.zig` explicit as the narrower current `devres` planner, MMIO-boundary, current-packet, direct-helper, DMA-coherent, zero-size replay, and scatterlist packet, plus the shipped Landlock survey-and-checker packet through `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-landlock-syscalls-packet.py`, `security/landlock/ruleset.zig`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls.zig`, and `zigux/tests/phase13_landlock_syscalls_reviewability.zig` explicit, while keeping `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, and `zigux/tests/phase13_build.zig` framed as repo-reality gaps rather than shipped evidence
- keep direct helper-local tests-root and adjacent focused checker paths framed as repo-reality gaps rather than shipped evidence when current `master` still cannot materialize `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `make -C zigux phase13-validate`, `make -C zigux phase13`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `zigux/helpers/notifier_chain_view.zig`, `include/zigux/notifier_abi.h`, `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`, while the shipped `zigux/Makefile`, `Documentation/zigux/phase13-libfs-slice.md`, `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_libfs_manifest.json`, `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `Documentation/zigux/phase13-devres-iounmap-planner.md`, `Documentation/zigux/phase13-devres-iomap-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `Documentation/zigux/phase13-devres-scatterlist-planner.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-dmam-alloc-coherent-planner.py`, `scripts/zigux/check-phase13-devres-iounmap-planner.py`, `scripts/zigux/check-phase13-devres-iomap-planner.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `scripts/zigux/check-phase13-devres-current-packet.py`, `scripts/zigux/check-phase13-devres-scatterlist-planner.py`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `zigux/tests/phase13_devres_dmam_alloc_zero_size_replay_build.zig`, `zigux/tests/phase13_devres_iounmap_planner.zig`, `zigux/tests/phase13_devres_iounmap_planner_manifest.json`, `zigux/tests/phase13_devres_iomap_planner.zig`, `zigux/tests/phase13_devres_iomap_planner_manifest.json`, `zigux/tests/phase13_devres_scatterlist_planner_manifest.json`, `zigux/tests/phase13_devres_dma_coherent.zig`, `lib/devres.zig`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist_build.zig`, the shipped `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-landlock-syscalls-packet.py`, `security/landlock/ruleset.zig`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` stay explicit
- if a broad reminder still spells the missing devres reviewability companion as `zigux/tests/phase13Devres_reviewability.zig`, treat that as stale wording for `zigux/tests/phase13_devres_reviewability.zig` rather than as a separate valid path
- treat notifier evidence as adjacent release-surface support rather than a fifth shared-helper anchor, and keep the shipped `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` explicit while `zigux/helpers/notifier_chain_view.zig` remains a separate adjacent repo-reality gap; keep `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, and `zigux/tests/phase13_notifier_list_reviewability.zig` visible as the focused adjacent checker packet without promoting notifier support into a fifth helper lane.
- refresh this note only with surfaces verified on current `master`, not with hoped-for follow-up notes

## Sync Rules
1. When one of these packets changes, refresh the broad contributor surfaces before adding new packet-local wording.
2. Prefer one packet-local change at a time instead of batching Phase 10, 11, and 13 drift into a single mixed update.
3. Do not imply validator, checker, or replay surfaces that are not on current `master`.
4. Keep release-surface truthfulness explicit whenever a broad reminder references an adjacent evidence note or manifest.
5. Keep phase-local owner maps visible instead of replacing them with a generic cross-phase summary.