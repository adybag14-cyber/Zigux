# Phase 10, 11, and 13 Validator-First Review Guide

Use this focused contributor guide when a change touches the active Phase 10 virtio lab packet, the active Phase 11 simple-driver packet, or the active Phase 13 shared-helper release packet.

Pair this note with `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md` when the same review needs a compact tests-root checklist beside the docs-root and shared checklist prompts.

## Why this note exists

The shared scripts index already names the checker stack for these packets, but reviewers still need one compact place that says which pre-replay gates, live replay entrypoints, and repo-reality gaps should move together.

Keep `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md` aligned with this note when they describe the same contributor-facing packets.

## Phase 10: Virtio lab packet

Keep the current validator-first route explicit:

- `python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test`
- `python3 scripts/zigux/check-phase10-bootstrap-route.py`
- `python3 scripts/zigux/check-phase10-docs-readme-shared-packet.py --self-test`
- `python3 scripts/zigux/check-phase10-docs-readme-shared-packet.py`
- `python3 scripts/zigux/check-phase10-core-packet.py`
- `python3 scripts/zigux/check-phase10-shared-freeze-boundary.py`
- `python3 scripts/zigux/check-phase10-ring-packet.py`
- `python3 scripts/zigux/check-phase10-input-packet.py`
- `python3 scripts/zigux/check-phase10-mmio-packet.py`
- `python3 scripts/zigux/check-phase10-harness-coverage.py --self-test`
- `python3 scripts/zigux/check-phase10-harness-coverage.py`
- `python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py --self-test`
- `python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py`
- `python3 scripts/zigux/check-phase10-closure-manifest-counts.py`
- `python3 scripts/zigux/validate-phase10.py`
- `python3 scripts/zigux/validate-phase10-closure.py`
- `make -C zigux phase10-validate`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Keep these evidence surfaces aligned in the same review:

- `Documentation/zigux/README.md`
- `Documentation/zigux/phase10-closure-evidence.md`
- `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
- `Documentation/zigux/phase10-virtio-core-survey.md`
- `zigux/tests/phase10_virtio_core.zig`
- `Documentation/zigux/phase10-virtio-ring-survey.md`
- `Documentation/zigux/phase10-virtio-ring-slice.md`
- `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`
- `zigux/tests/phase10_virtio_ring_manifest.json`
- `zigux/tests/phase10_virtio_ring_survey.zig`
- `Documentation/zigux/phase10-virtio-input-survey.md`
- `Documentation/zigux/phase10-virtio-input-slice.md`
- `Documentation/zigux/phase10-virtio-input-module-slice.md`
- `zigux/tests/phase10_virtio_input_manifest.json`
- `drivers/virtio/virtio_input.zig`
- `drivers/virtio/virtio_input_probe_preflight.zig`
- `drivers/virtio/virtio_input_queue_callback_preflight.zig`
- `drivers/virtio/virtio_input_registration_preflight.zig`
- `drivers/virtio/virtio_input_status_drain.zig`
- `drivers/virtio/virtio_input_teardown_preflight.zig`
- `drivers/virtio/virtio_input_teardown_observation.zig`
- `drivers/virtio/virtio_input_verify.zig`
- `zigux/tests/phase10_virtio_input.zig`
- `zigux/tests/phase10_virtio_input_probe_preflight.zig`
- `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`
- `zigux/tests/phase10_virtio_input_registration_preflight.zig`
- `zigux/tests/phase10_virtio_input_status_drain.zig`
- `zigux/tests/phase10_virtio_input_teardown_preflight.zig`
- `zigux/tests/phase10_virtio_input_teardown_observation.zig`
- `zigux/tests/phase10_virtio_input_survey.zig`
- `Documentation/zigux/phase10-virtio-mmio-survey.md`
- `Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`
- `Documentation/zigux/phase10-virtio-mmio-slice.md`
- `zigux/tests/phase10_virtio_mmio_manifest.json`
- `zigux/tests/phase10_virtio_mmio_survey.zig`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase10-bootstrap-route.py`
- `scripts/zigux/check-phase10-docs-readme-shared-packet.py`
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

Keep the current repo-reality split explicit too:

- `zigux/tests/phase10_virtio_core.zig` is back as the returned bounded core replay inside the shared closure packet.
- `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `zigux/tests/phase10_virtio_ring_survey.zig` are part of the returned ring packet and should move together with the queue-local wrapper survey instead of dropping back into neighboring reminder wording.
- `Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, `zigux/tests/phase10_virtio_mmio_manifest.json`, and `zigux/tests/phase10_virtio_mmio_survey.zig` are part of the returned helper-local MMIO packet and should stay paired with the bounded config-write, interrupt-ack, and survey evidence rather than widening into lifecycle or IRQ claims.
- `Documentation/zigux/README.md` plus `scripts/zigux/check-phase10-docs-readme-shared-packet.py` now keep the shared docs-root reminder explicit inside the live Phase 10 packet, so stale missing-route or wrapper wording in the docs root fails closed beside the broader validator-first packet instead of drifting into neighboring-surface prose.
- Keep the lane-owner split explicit in reviewer wording: `Documentation/zigux/phase10-virtio-ring-survey.md` plus `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md` remain the queue-local `P10-L10` freeze-boundary packet, while `Documentation/zigux/phase10-virtio-mmio-survey.md`, `Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`, and `zigux/tests/phase10_virtio_mmio_manifest.json` remain the bounded `P10-L11` MMIO helper packet; shared review notes should not collapse those owner lanes into one generic freeze-boundary bucket.
- `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_queue_callback_preflight.zig`, `drivers/virtio/virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_status_drain.zig`, `drivers/virtio/virtio_input_teardown_preflight.zig`, `drivers/virtio/virtio_input_teardown_observation.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_teardown_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, and `zigux/tests/phase10_virtio_input_survey.zig` are part of the returned bounded input packet and should stay paired with the survey, slice, module-slice, manifest, checker, and shared build route instead of dropping back into stale compile-path or queue-only reminder wording.
- `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, and `zigux/tests/phase10_virtio_core_survey.zig` now rematerialize through public current-`master` readback and should stay explicit as returned core-side companions beside the bounded core replay.
- `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig` now rematerialize through exact-path contents reads and should stay explicit beside the bounded core replay and returned core-side companions, while `zigux/tests/phase10_virtio_ring.zig` now rematerializes through exact-path contents reads and should stay explicit beside the returned queue-local replay packet rather than being framed as fallback-only or last-known evidence.

Reviewer prompts:

- Does the shared Phase 10 packet still read as one validator-first lab bundle, with the bootstrap-route guard, the docs-root reminder guard, the returned shared core-packet guard, the freeze-boundary guard, the ring, input, and MMIO packet guards, the tests-root reminder guard, the closure-manifest count guard, the shared validation pair, the returned bounded core replay `zigux/tests/phase10_virtio_core.zig`, the returned ring freeze-boundary and dedicated survey gate, the returned MMIO companion, manifest, and survey gate, the closure manifest, and the returned `zigux/Makefile` Phase 10 routes all naming the same bounded surfaces?
- Does the Phase 10 freeze-boundary posture still keep `Documentation/zigux/freeze-map.md` explicit, leave `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` in the separate Phase 14 study-only family, keep the queue-local `P10-L10` ring freeze-boundary packet distinct from the bounded `P10-L11` MMIO helper packet, and keep queue setup or reset execution parity, IRQ delivery, DMA behavior, input registration lifecycle closure, and MMIO lifecycle-and-IRQ follow-through parked behind the risky-transport blocker?

## Phase 11: Simple-driver packet

Keep the current pre-replay checker stack and returned shared validation route explicit:

- `python3 scripts/zigux/check-phase11-build-inventory.py`
- `python3 scripts/zigux/check-phase11-shared-replay-contract-counts.py`
- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `python3 scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`
- `python3 scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- `python3 scripts/zigux/validate-phase11.py`
- `make -C zigux phase11-validate`
- `zig build test --build-file zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`
- `zig build test --build-file zigux/tests/phase11_dw_wdt_build.zig`
- `zig build test --build-file zigux/tests/phase11_dw_wdt_restart_build.zig`
- `zig build test --build-file zigux/tests/phase11_dw_wdt_pm_build.zig`
- `zig build test --build-file zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`
- `zig build test --build-file zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig`
- `zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig`
- `zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig`
- `zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`

Keep these evidence surfaces aligned in the same review:

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
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-shared-replay-contract-counts.py`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- `scripts/zigux/validate-phase11.py`
- `zigux/Makefile`
- `drivers/watchdog/dw_wdt.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `drivers/watchdog/dw_wdt_pm.zig`
- `drivers/watchdog/dw_wdt_pm_scaffold.zig`
- `drivers/tty/hvc/hvc_console.zig`
- `drivers/tty/hvc/hvc_console.h`
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
- `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`

Keep the current repo-reality split explicit too:

- `zigux/Makefile` is present on current `master`, and its live body now exposes the shared `make -C zigux phase11-validate` route. `make -C zigux phase11` and `make -C zigux phase11-contract` still remain repo-reality gaps.
- `Documentation/zigux/phase11-shared-replay-contract.md` is back on current `master` and should stay explicit beside the shared validator, build-inventory, replay-contract-counts checker, and Makefile-backed review packet instead of being repeated as a gap.
- `scripts/zigux/check-phase11-shared-replay-contract-counts.py` is part of the current shared checker stack, and the returned shared validator packet now fans out through ten focused proof builds instead of only the narrower HVC-only quartet. Keep that counts checker and broader proof fan-out explicit in review wording so the shared Phase 11 gate does not drift behind the current contract.
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` are back as current-head matrix evidence, even though this runtime still rereads the bcm2835 and DesignWare notes through raw current-`master` fallback. Keep those returned matrix surfaces explicit beside the gpio and HVC matrices instead of treating them as missing.
- The returned DesignWare continuity packet is narrower than the older broader survey-only reminder family: keep `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `drivers/watchdog/dw_wdt_pm.zig`, `drivers/watchdog/dw_wdt_pm_scaffold.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt.zig`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` explicit, while `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, and `zigux/tests/phase11_dw_wdt_survey.zig` stay outside the current shared validator-first evidence packet until a same-mode reread proves they returned to this lane.
- The returned HVC continuity packet is broader than the older cleanup-only wording here: keep `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`, `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`, and `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` explicit beside the cleanup packet, build inventory, and proof-backed adjunct stack instead of narrowing the shared story to cleanup alone.
- `Documentation/zigux/phase11-closure-note.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-shared-summary-surfaces.py`, and `zigux/tests/phase11_build.zig` remain repo-reality gaps rather than shipped current-`master` evidence.

Reviewer prompts:

- Do the current Phase 11 checker stack, including `scripts/zigux/check-phase11-shared-replay-contract-counts.py`, the returned shared replay-contract note, the returned four-matrix packet, the narrower returned DesignWare continuity packet, the broader current-head HVC continuity packet with the targetless-unregister witness, the adjacent header-boundary proof shard, and the ten-proof-build `phase11-validate` route still describe the same bounded simple-driver packet?
- Does the guide keep the returned `zigux/Makefile` file and `make -C zigux phase11-validate` route distinct from the still-missing broader Phase 11 make routes, and keep only the older closure-note, removed shared-checker, and removed aggregate build-route surfaces framed as gaps rather than live evidence?

## Phase 13: Shared-helper release packet

Keep the current contributor-facing guard path explicit:

- `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`

Keep these contributor-facing and helper-local surfaces aligned in the same review:

- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `Documentation/zigux/phase13-notifier-summary-gap.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `scripts/zigux/check-phase13-tests-readme-alignment.py`
- `Documentation/zigux/phase13-libfs-survey.md`
- `fs/libfs.zig`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_libfs_manifest.json`
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`
- `Documentation/zigux/phase13-devres-scatterlist-slice.md`
- `scripts/zigux/check-phase13-devres-dma-boundary.py`
- `scripts/zigux/check-phase13-devres-mmio-packet.py`
- `lib/devres.zig`
- `lib/devres_scatterlist.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`
- `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`
- `zigux/tests/phase13_devres_scatterlist.zig`
- `zigux/tests/phase13_devres_scatterlist_build.zig`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `security/landlock/ruleset.zig`
- `security/landlock/syscalls.zig`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `include/zigux/abi.h`
- `drivers/tty/hvc/hvc_console.h`

Keep the current repo-reality gaps explicit too:

- `zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`.
- `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/helpers/notifier_chain_view.zig`, `include/zigux/notifier_abi.h`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` remain repo-reality gaps rather than shipped current-`master` evidence.

Reviewer prompts:

- Does the shared Phase 13 packet still route through the contributor workflow guide, the shared-summary guard, the tests-root alignment companion, the helper-local `libfs`, `devres`, and Landlock ruleset packets, and the adjacent notifier evidence without promoting repo-reality gaps back into shipped release proof?
- Does the guide keep the returned `zigux/Makefile` file distinct from the still-missing Phase 13 make routes, and keep the missing validator-first, notifier-priority, notifier-chain, and direct Landlock-syscalls replay surfaces framed as gaps rather than live evidence?

## Shared review rule

When one of these packets changes, keep the checker stack, the live replay path, the current evidence files, and the repo-reality gaps reviewable together. Do not treat a passing build file, one manifest refresh, or one survey note edit as enough on its own.