# Phase 10, 11, and 13 Tests-Root Review Companion

Use this note when a change touches the active Phase 10 virtio lab packet, the active Phase 11 simple-driver packet, or the active Phase 13 shared-helper contributor packet and the review needs one compact tests-root reminder.

Keep `Documentation/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, and `scripts/zigux/README.md` aligned with this note when they describe the same shared contributor-facing packet.

## Phase 10 tests-root packet

Keep the current bounded virtio closure packet explicit through these shared surfaces and closure-manifest-backed packet-local inventory claims:
- `Documentation/zigux/phase10-closure-evidence.md`
- `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
- `Documentation/zigux/phase10-virtio-core-survey.md`
- `Documentation/zigux/phase10-virtio-ring-survey.md`
- `Documentation/zigux/phase10-virtio-ring-slice.md`
- `Documentation/zigux/phase10-virtio-input-survey.md`
- `Documentation/zigux/phase10-virtio-mmio-survey.md`
- `scripts/zigux/check-phase10-core-packet.py`
- `scripts/zigux/check-phase10-ring-packet.py`
- `scripts/zigux/check-phase10-input-packet.py`
- `scripts/zigux/check-phase10-mmio-packet.py`
- `scripts/zigux/check-phase10-mmio-freeze-boundary.py`
- `scripts/zigux/check-phase10-harness-coverage.py`
- `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`
- `scripts/zigux/validate-phase10.py`
- `scripts/zigux/validate-phase10-closure.py`
- `zigux/tests/phase10_build.zig`
- `zigux/tests/phase10_closure_manifest.json`
- `zigux/tests/phase10_virtio_core.zig`
- `zigux/tests/phase10_virtio_core_reset_queue.zig`
- `zigux/tests/phase10_virtio_driver_id.zig`
- `drivers/virtio/virtio_driver_id.zig`
- `drivers/virtio/virtio.zig`
- `drivers/virtio/virtio_verify.zig`
- `zigux/tests/phase10_virtio_core_manifest.json`
- `zigux/tests/phase10_virtio_core_survey.zig`
- `zigux/tests/phase10_virtio_ring.zig`
- `zigux/tests/phase10_virtio_ring_reset_reuse.zig`
- `drivers/virtio/virtio_ring.zig`
- `drivers/virtio/virtio_ring_verify.zig`
- `zigux/tests/phase10_virtio_ring_manifest.json`
- `zigux/tests/phase10_virtio_ring_survey.zig`
- `zigux/tests/phase10_virtio_input.zig`
- `drivers/virtio/virtio_input.zig`
- `drivers/virtio/virtio_input_probe_preflight.zig`
- `drivers/virtio/virtio_input_verify.zig`
- `zigux/tests/phase10_virtio_input_probe_preflight.zig`
- `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`
- `zigux/tests/phase10_virtio_input_registration_preflight.zig`
- `zigux/tests/phase10_virtio_input_teardown_observation.zig`
- `zigux/tests/phase10_virtio_input_status_drain.zig`
- `zigux/tests/phase10_virtio_input_manifest.json`
- `zigux/tests/phase10_virtio_input_survey.zig`
- `zigux/tests/phase10_virtio_mmio.zig`
- `drivers/virtio/virtio_mmio.zig`
- `drivers/virtio/virtio_mmio_verify.zig`
- `zigux/tests/phase10_virtio_mmio_manifest.json`
- `zigux/tests/phase10_virtio_mmio_survey.zig`
- `zigux/Makefile`
- `make -C zigux phase10-validate`
- `zig build test --build-file zigux/tests/phase10_build.zig`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Treat the shared reminder notes, validators, and Linux-style make routes above together with the directly readable `zigux/tests/phase10_closure_manifest.json`, `zigux/tests/phase10_virtio_ring_manifest.json`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, and `Documentation/zigux/phase10-virtio-input-module-slice.md` as the currently re-readable Phase 10 anchors. Keep the direct `drivers/virtio/virtio_ring.zig` ring surface explicit beside `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, and `Documentation/zigux/phase10-virtio-ring-slice.md` when broader shared summaries refresh. Keep the direct `drivers/virtio/virtio_input.zig` helper surface explicit beside `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, and `zigux/tests/phase10_virtio_input_status_drain.zig` when broader shared summaries refresh. Keep the direct `drivers/virtio/virtio_mmio.zig` helper surface explicit beside `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, and `zigux/tests/phase10_virtio_mmio_survey.zig` when broader shared summaries refresh. Wrapper ownership for the input lane stays split: `drivers/virtio/virtio.zig` owns shared device-status bookkeeping, `drivers/virtio/virtio_ring.zig` owns virtqueue wrapper shape and notification planning, and `drivers/virtio/virtio_mmio.zig` owns MMIO wrapper planning, so transport-facing queue and registration-lifecycle work stays parked outside the input lane. Current repo-reality gaps on `master` now narrow to `Documentation/zigux/phase10-virtio-core-slice.md` and `Documentation/zigux/phase10-virtio-mmio-slice.md`; keep only those absent packet-local companions recorded as gaps while treating `Documentation/zigux/phase10-virtio-input-slice.md` and `Documentation/zigux/phase10-virtio-input-module-slice.md` as restored shared-review evidence.

Tests-root reviewer prompt:
- Do the docs-root notes, scripts-root guards, tests-root packet, and Linux-style make routes still describe the same bounded virtio core, ring, input, and MMIO closure packet, the focused core reset-queue replay, ring drained-reset reuse replay, the direct `drivers/virtio/virtio_ring.zig` ring surface beside `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, and `Documentation/zigux/phase10-virtio-ring-slice.md`, the direct `drivers/virtio/virtio_input.zig` helper beside `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_verify.zig` and the input queue-callback-preflight, registration-preflight, teardown-observation, and status-drain replays, the direct `drivers/virtio/virtio_mmio.zig` helper beside `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, `scripts/zigux/check-phase10-mmio-packet.py`, and `scripts/zigux/check-phase10-mmio-freeze-boundary.py`, the input-lane wrapper split where `drivers/virtio/virtio.zig` owns shared device-status bookkeeping, `drivers/virtio/virtio_ring.zig` owns virtqueue wrapper shape and notification planning, and `drivers/virtio/virtio_mmio.zig` owns MMIO wrapper planning, the blocked risky-transport posture, the allowed `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` destination family, the separate `reference_samples` and `runtime_starters` boundary carried through `zigux/tests/phase10_closure_manifest.json`, the already-shipped `samples/zigux/runtime_trace_events_loader.zig` scaffold as adjacent Phase 9 evidence rather than Phase 10 closure progress, and the Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit, and do the known missing Phase 10 core and MMIO slice-note companions stay framed as repo-reality gaps while the restored input and input-module slice-note companions stay explicit as directly re-readable evidence?

## Phase 11 tests-root packet

Keep the current shared-versus-dedicated simple-driver packet explicit through these shared reminder surfaces and the bounded packet-local proof surfaces that current `master` can still materialize:
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-closure-note.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`
- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- `scripts/zigux/check-phase11-shared-replay-contract.py`
- `scripts/zigux/check-phase11-shared-summary-surfaces.py`
- `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`
- `scripts/zigux/check-phase11-dw-wdt-packet.py`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `scripts/zigux/check-phase11-hvc-survey-packet.py`
- `zigux/tests/phase11_build.zig`
- `zigux/tests/phase11_gpio_wdt.zig`
- `zigux/tests/phase11_bcm2835_wdt.zig`
- `zigux/tests/phase11_dw_wdt.zig`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `zigux/tests/phase11_hvc_console.zig`
- `zigux/tests/phase11_hvc_cleanup.zig`
- `zigux/tests/phase11_hvc_console_manifest.json`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `zigux/tests/phase11_hvc_console_modem_control_split.zig`
- `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `drivers/tty/hvc/hvc_console_verify.zig`
- `drivers/tty/hvc/hvc_console_sysrq.zig`
- `zigux/Makefile`
- `make -C zigux phase11`
- `make -C zigux phase11-hvc-survey`

Treat the shared reminder notes and shipped checkers together with the surviving DesignWare platform-registration continuity note, the dedicated HVC archival packet through `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, and `make -C zigux phase11-hvc-survey`, plus the shared header-boundary survey through `Documentation/zigux/phase11-uapi-header-parity-survey.md` and `zigux/tests/phase11_uapi_header_parity_survey.zig` as the current directly re-readable Phase 11 evidence on `master`.

Direct GitHub contents reads can still return 404 for `zigux/tests/phase11_build.zig` and some direct watchdog or HVC replay files, but raw GitHub fallback materializes the current shared build file plus `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `drivers/tty/hvc/hvc_console_verify.zig` on current `master`, so broader shared summaries should keep those paths explicit as landed bounded replay evidence rather than downgrading them into repo-reality gaps.

Tests-root reviewer prompt:
- Do the docs-root notes, checker split, shared summary-surface checker, tests-root packet, and Linux-style make routes still describe the same shared-versus-dedicated simple-driver packet, the parked shared closure checkpoint, the parked driver-lane owner map, the dedicated bcm2835 archival packet, the surviving DesignWare platform-registration continuity packet, the dedicated archival HVC validation-matrix, survey-note, teardown-note, direct `zigux/tests/phase11_hvc_console.zig` replay, bounded `zigux/tests/phase11_hvc_cleanup.zig` handoff, manifest-backed survey gate, modem-control split, poll-retry split, direct `drivers/tty/hvc/hvc_console_verify.zig` replay boundary, sysrq-helper boundary, and `phase11-hvc-survey` checker-backed route, plus the shared header-boundary survey through `Documentation/zigux/phase11-uapi-header-parity-survey.md` and `zigux/tests/phase11_uapi_header_parity_survey.zig`, while keeping the direct `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, and `drivers/tty/hvc/hvc_console_verify.zig` surfaces explicit as landed bounded replay evidence even when the direct contents bridge still 404s, and without implying a removed `validate-phase11.py`, a missing build-inventory fixture, or a broader checker stack than current `master` ships?

## Phase 13 tests-root packet

Keep the current contributor-facing Phase 13 packet explicit through these shipped shared surfaces:
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-libfs-survey.md`
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `fs/libfs.zig`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_libfs_manifest.json`
- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_manifest.json`
- `security/landlock/ruleset.zig`
- `security/landlock/syscalls.zig`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `scripts/zigux/check-phase13-devres-packet-alignment.py`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `scripts/zigux/validate-phase13-release.py`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `zigux/tests/README.md`
- `zigux/helpers/notifier_chain_view.zig`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/abi.h`
- `drivers/tty/hvc/hvc_console.h`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

Keep the shared validator-first release handle anchored to current repo reality: current `master` now materializes the bounded `fs/libfs.zig` foothold together with `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`. It also materializes the devres helper packet through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, and `zigux/tests/phase13_devres_manifest.json`, and `scripts/zigux/check-phase13-devres-packet-alignment.py`. Current `master` also materializes the helper-owned Landlock ownership and syscall-governance notes plus the shipped `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `Documentation/zigux/phase13-landlock-syscalls-survey.md` notes, the shipped `security/landlock/ruleset.zig` and `security/landlock/syscalls.zig` starters, the direct ruleset replay pair `zigux/tests/phase13_landlock_ruleset.zig` and `zigux/tests/phase13_landlock_ruleset_manifest.json`, the direct syscall replay packet `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`, so contributor workflow wording should keep those shipped helper anchors explicit beside `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py` instead of treating Landlock as docs-only ownership metadata. Current `master` also materializes the adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/notifier_chain_view.zig` helper, and the Linux-side `drivers/tty/hvc/hvc_console.h` header, so keep those four paths explicit as shipped adjacent evidence without counting them as extra shared replay steps. If direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, or the older `scripts/zigux/check-phase13-devres-packet.py` cannot be materialized on current `master`, record them as repo-reality gaps instead of presenting them here as independently shipped review evidence. Current `master` also materializes the dedicated Phase 13 packet summary in `zigux/tests/README.md`, so keep that broader tests-root guide aligned with the contributor workflow guide and shared-helper sequencing note as shipped Phase 13 review evidence instead of framing it as a pending shared-surface follow-up.

Tests-root reviewer prompt:
- Do the contributor workflow guide, shared-helper sequencing note, release-notes and roadmap-traceability notes, the shipped `Documentation/zigux/phase13-libfs-survey.md` note plus `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`, the shipped devres slice and survey plus `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, and `zigux/tests/phase13_devres_manifest.json`, and `scripts/zigux/check-phase13-devres-packet-alignment.py`, the helper-owned Landlock ownership and syscall-governance notes plus the shipped `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `Documentation/zigux/phase13-landlock-syscalls-survey.md` notes, the shipped `security/landlock/ruleset.zig` and `security/landlock/syscalls.zig` starters, the direct ruleset replay pair `zigux/tests/phase13_landlock_ruleset.zig` and `zigux/tests/phase13_landlock_ruleset_manifest.json`, the direct syscall replay packet `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`, the shipped `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, the adjacent notifier survey and priority-signal guard, the shared validator-first release handle, the shared contributor-surface sync note, the shared review checklist, the shipped broader tests-root Phase 13 guide in `zigux/tests/README.md`, and Linux-style make routes still keep the active contributor packet aligned while keeping the shipped adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/notifier_chain_view.zig`, and the Linux-side `drivers/tty/hvc/hvc_console.h` header explicit without counting them as extra shared replay steps, while treating missing direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and the older `scripts/zigux/check-phase13-devres-packet.py` as repo-reality gaps rather than shipped evidence?

## Checklist carryover prompts

Keep these reviewer questions explicit when `zigux/tests/README.md` or other shared contributor-facing workflow notes are refreshed:
- Phase 10: do the docs-root notes, scripts-root guards, tests-root packet, and Linux-style make routes still keep the bounded virtio core, ring, input, and MMIO packet aligned while preserving the shared validator-first route, the focused core reset-queue replay, ring drained-reset reuse replay, the direct `drivers/virtio/virtio_ring.zig` ring surface beside `drivers/virtio/virtio_ring_verify.zig`, the direct `drivers/virtio/virtio_input_probe_preflight.zig` helper plus the input preflight and status-drain replays, and MMIO verify replays, the closure-manifest boundary, the adjacent Phase 9 scaffold, and the Phase 14 study-only deep-core ownership cues?
- Phase 11: do the docs-root notes, checker split, shared summary-surface checker, tests-root packet, and Linux-style make routes still keep the shared-versus-dedicated simple-driver packet, the dedicated bcm2835 archival packet, the surviving DesignWare platform-registration continuity packet, the dedicated archival HVC validation-matrix, survey-note, teardown-note, direct `zigux/tests/phase11_hvc_console.zig` replay, bounded `zigux/tests/phase11_hvc_cleanup.zig` handoff, manifest-backed survey gate, modem-control split, poll-retry split, direct `drivers/tty/hvc/hvc_console_verify.zig` replay boundary, sysrq-helper boundary, and `phase11-hvc-survey` checker-backed route, plus the shared header-boundary survey through `Documentation/zigux/phase11-uapi-header-parity-survey.md` and `zigux/tests/phase11_uapi_header_parity_survey.zig`, aligned as shipped current-`master` evidence while keeping the direct `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, and `drivers/tty/hvc/hvc_console_verify.zig` surfaces explicit as landed bounded replay evidence even when the direct contents bridge still 404s, and without implying removed validators or missing inventory fixtures?
- Phase 13: do the contributor workflow guide, shared-helper sequencing note, release-notes and roadmap-traceability notes, the shipped `Documentation/zigux/phase13-libfs-survey.md` note plus `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`, the shipped devres slice and survey plus `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_manifest.json`, and `scripts/zigux/check-phase13-devres-packet-alignment.py`, the helper-owned Landlock ownership and syscall-governance notes plus the shipped `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `Documentation/zigux/phase13-landlock-syscalls-survey.md` notes, the shipped `security/landlock/ruleset.zig` and `security/landlock/syscalls.zig` starters, the direct ruleset replay pair `zigux/tests/phase13_landlock_ruleset.zig` and `zigux/tests/phase13_landlock_ruleset_manifest.json`, the direct syscall replay packet `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`, the shipped `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, the adjacent notifier survey and priority-signal guard, the shared validator-first release handle, the shared contributor-surface sync note, the shared review checklist, the shipped broader tests-root Phase 13 guide in `zigux/tests/README.md`, and Linux-style make routes still keep the active contributor packet aligned while keeping the shipped adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/notifier_chain_view.zig`, and the Linux-side `drivers/tty/hvc/hvc_console.h` header explicit without counting them as extra shared replay steps, while treating missing direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and the older `scripts/zigux/check-phase13-devres-packet.py` as repo-reality gaps rather than shipped evidence?

## Shared rule

When one of these packets changes, keep the tests-root replay note, the packet-local manifest or focused reviewability shard when one is actually present on current `master`, and the validator-first review surface reviewable together.
