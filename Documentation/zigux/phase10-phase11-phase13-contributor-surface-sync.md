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
- `Documentation/zigux/phase13-libfs-survey.md`
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`
- `Documentation/zigux/phase13-devres-scatterlist-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `Documentation/zigux/phase13-notifier-summary-gap.md`
- `scripts/zigux/check-phase13-tests-readme-alignment.py`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

## Phase 10 contributor packet
Keep the bounded virtio packet explicit through:
- `Documentation/zigux/phase10-closure-evidence.md`
- `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
- `Documentation/zigux/phase10-virtio-core-survey.md`
- `Documentation/zigux/phase10-virtio-ring-survey.md`
- `Documentation/zigux/phase10-virtio-input-survey.md`
- `Documentation/zigux/phase10-virtio-mmio-survey.md`
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/check-phase10-core-packet.py`
- `scripts/zigux/check-phase10-ring-packet.py`
- `scripts/zigux/check-phase10-input-packet.py`
- `scripts/zigux/check-phase10-mmio-packet.py`
- `scripts/zigux/check-phase10-mmio-freeze-boundary.py`
- `scripts/zigux/check-phase10-harness-coverage.py`
- `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`
- `scripts/zigux/validate-phase10.py`
- `scripts/zigux/validate-phase10-closure.py`
- `zigux/tests/phase10_closure_manifest.json`
- `zigux/tests/phase10_build.zig`
- `zigux/Makefile`
- `make -C zigux phase10-validate`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Current direct readback for this shared contributor lane is narrower than the full historical packet list above: `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/check-phase10-core-packet.py`, `scripts/zigux/check-phase10-ring-packet.py`, `scripts/zigux/check-phase10-input-packet.py`, `scripts/zigux/check-phase10-mmio-packet.py`, `scripts/zigux/check-phase10-mmio-freeze-boundary.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `zigux/Makefile` remain directly re-readable here, while current authenticated contents reads still return missing for `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, and `zigux/tests/phase10_closure_manifest.json`. Current `master` does materialize `zigux/Makefile`, and its live body exposes `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10`, so keep that returned file and those shared build-gate route names explicit instead of treating them as missing-route vocabulary. Keep the validator-first and closure-manifest names framed as last-known packet members or shared reminder vocabulary until a fresh reread proves they returned on current `master`.

Contributor reminder:
- keep the blocked risky-transport posture explicit
- keep the allowed `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` destination family explicit
- keep the parked `P10-L11` MMIO freeze-boundary owner and rollback-owner note explicit around `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, and `scripts/zigux/check-phase10-mmio-freeze-boundary.py`
- keep Phase 5 reference samples and Phase 9 runtime starters as adjacent evidence, not extra Phase 10 closure proof
- keep the separate Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit
- keep `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, and `Documentation/zigux/phase10-virtio-input-module-slice.md` explicit as directly re-readable shared-review evidence on current `master`, keep `Documentation/zigux/phase10-virtio-mmio-survey.md` as the directly re-readable MMIO companion, and keep `Documentation/zigux/phase10-virtio-core-slice.md` plus `Documentation/zigux/phase10-virtio-mmio-slice.md` framed as repo-reality gaps until a fresh reread proves they returned

## Phase 11 contributor packet
Keep the current-head simple-driver truthfulness packet explicit through:
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`

Contributor reminder:
- keep the shared-versus-dedicated split explicit instead of collapsing the smaller current-head truthfulness packet into one generic driver note
- keep the current-head shared packet rooted in `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase11-validation-matrix-gap-survey.md`, the four directly readable validation matrices `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`, `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`, `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`, the current DesignWare owner packet `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-matrix-gap-survey.py`, `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`, `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`, and `zigux/tests/phase11_hvc_cleanup_packet_build.zig`; do not imply that `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-shared-summary-surfaces.py`, `zigux/tests/phase11_build.zig`, `make -C zigux phase11-contract`, or the exact shared `zig build test --build-file zigux/tests/phase11_build.zig --summary all` replay are back on current `master` without a fresh reread; `zigux/Makefile` now rematerializes on current `master`, but it still does not expose a live Phase 11 build handle there
- keep the validation-matrix gap survey authoritative for the restored bcm2835, gpio, DesignWare, and HVC matrix packet without using those directly readable matrices to overclaim broader execution-facing replay or shared-route parity
- treat the current DesignWare follow-through as the narrower `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` owner packet instead of restating the older clock-acquisition or verify-alignment continuity pair as current-head evidence
- keep the HVC packet framed as inventory-backed archival continuity through `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`, `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`, and `zigux/tests/phase11_hvc_cleanup_packet_build.zig` instead of calling the archived direct driver, teardown, split-replay, or sysrq files current-head readback evidence
- keep only genuinely materialized current-head Phase 11 surfaces explicit in broad contributor wording; do not promote missing watchdog, HVC, or shared-contract paths back into live contributor-facing evidence from older summary wording alone

## Phase 13 contributor packet
Keep the shared-helper packet explicit through the verified docs-root and contributor-facing reminder surfaces:
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-libfs-survey.md`
- `fs/libfs.zig`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_libfs_manifest.json`
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`
- `Documentation/zigux/phase13-devres-scatterlist-slice.md`
- `scripts/zigux/check-phase13-devres-dma-boundary.py`
- `scripts/zigux/check-phase13-devres-mmio-packet.py`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `lib/devres_scatterlist.zig`
- `zigux/tests/phase13_devres_scatterlist.zig`
- `zigux/tests/phase13_devres_scatterlist_build.zig`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `security/landlock/ruleset.zig`
- `security/landlock/syscalls.zig`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `Documentation/zigux/phase13-notifier-list-survey.md`
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
- keep the shared contributor-facing handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, and `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, while keeping `scripts/zigux/check-phase13-shared-summary-surfaces.py` explicit as the shipped shared-summary guard beside that stable handle, while keeping `zigux/Makefile` explicit only as the returned file and keeping `make -C zigux phase13-validate` plus blocked convenience route `make -C zigux phase13` framed as the still-missing shared build routes on current `master`
- keep the shipped broader Phase 13 tests-root guide in `zigux/tests/README.md` explicit as shared packet evidence and keep it aligned with the workflow guide, shared-helper sequencing note, release-coordination matrix, review checklist, shared contributor-sync note, tests-root companion, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, and `scripts/zigux/check-phase13-tests-readme-alignment.py`
- keep `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, and `scripts/zigux/check-phase13-notifier-packet.py` framed as repo-reality gaps until current `master` materializes them again
- keep helper-local `libfs`, the narrower current-master `devres` DMA-boundary, `zigux/tests/phase13_devres_dma_coherent.zig`, and scatterlist packet, helper-owned `landlock`, and adjacent notifier evidence as separate owners instead of flattening them into one generic shared-helper summary
- keep direct helper-local tests-root and adjacent focused checker paths framed as repo-reality gaps rather than shipped evidence when current `master` still cannot materialize `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `make -C zigux phase13-validate`, `make -C zigux phase13`, `Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `zigux/helpers/notifier_chain_view.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, and `include/zigux/notifier_abi.h`, while the shipped `zigux/Makefile`, `Documentation/zigux/phase13-libfs-survey.md`, `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_libfs_manifest.json`, `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `zigux/tests/phase13_devres_dma_coherent.zig`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist_build.zig`, the shipped `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `security/landlock/ruleset.zig`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` stay explicit
- if a broad reminder still spells the missing devres reviewability companion as `zigux/tests/phase13Devres_reviewability.zig`, treat that as stale wording for `zigux/tests/phase13_devres_reviewability.zig` rather than as a separate valid path
- treat notifier evidence as adjacent release-surface support rather than a fifth shared-helper anchor, and keep the shipped `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` explicit while `zigux/helpers/notifier_chain_view.zig` remains a separate adjacent repo-reality gap
- refresh this note only with surfaces verified on current `master`, not with hoped-for follow-up notes

## Sync Rules
1. When one of these packets changes, refresh the broad contributor surfaces before adding new packet-local wording.
2. Prefer one packet-local change at a time instead of batching Phase 10, 11, and 13 drift into a single mixed update.
3. Do not imply validator, checker, or replay surfaces that are not on current `master`.
4. Keep release-surface truthfulness explicit whenever a broad reminder references an adjacent evidence note or manifest.
5. Keep phase-local owner maps visible instead of replacing them with a generic cross-phase summary.