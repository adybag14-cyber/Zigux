# Phase 10, 11, and 13 Tests-Root Review Companion

Use this note when a change touches the active Phase 10 virtio lab packet, the active Phase 11 simple-driver packet, or the active Phase 13 shared-helper contributor packet and the review needs one compact tests-root reminder.

Keep `Documentation/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, and `scripts/zigux/README.md` aligned with this note when they describe the same shared contributor-facing packet.

## Phase 10 tests-root packet

Keep the current bounded virtio closure packet explicit through these shared surfaces and closure-manifest-backed packet-local inventory claims:
- `Documentation/zigux/phase10-closure-evidence.md`
- `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
- `Documentation/zigux/phase10-virtio-core-survey.md`
- `Documentation/zigux/phase10-virtio-core-slice.md`
- `Documentation/zigux/phase10-virtio-ring-survey.md`
- `Documentation/zigux/phase10-virtio-ring-slice.md`
- `Documentation/zigux/phase10-virtio-input-survey.md`
- `Documentation/zigux/phase10-virtio-input-slice.md`
- `Documentation/zigux/phase10-virtio-input-module-slice.md`
- `Documentation/zigux/phase10-virtio-mmio-survey.md`
- `Documentation/zigux/phase10-virtio-mmio-slice.md`
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
- `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`
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
- `.github/workflows/zigux-bootstrap.yml`
- `make -C zigux phase10-validate`
- `zig build test --build-file zigux/tests/phase10_build.zig`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Treat the shared reminder notes and Linux-style make routes above together with the directly readable `zigux/tests/phase10_closure_manifest.json`, `Documentation/zigux/phase10-virtio-core-slice.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, and `Documentation/zigux/phase10-virtio-mmio-slice.md` as the currently re-readable Phase 10 anchors.

Keep `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, and `Documentation/zigux/phase10-virtio-ring-survey.md` explicit as closure-manifest-backed ring packet vocabulary when broader shared summaries refresh, with `Documentation/zigux/phase10-virtio-ring-slice.md` still named separately as the directly re-readable packet-local companion; do not restate the helper and replay paths as freshly direct re-reads unless a fresh reread proves they materialize again.

Keep the input-lane helper names `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_probe_preflight.zig`, and `drivers/virtio/virtio_input_verify.zig` explicit beside the queue-callback-preflight, registration-preflight, teardown-observation, and status-drain replays as the same closure-manifest-backed packet vocabulary, and keep the MMIO helper names `drivers/virtio/virtio_mmio.zig` and `drivers/virtio/virtio_mmio_verify.zig` explicit beside `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio_survey.zig`, and `Documentation/zigux/phase10-virtio-mmio-slice.md` on the same narrower basis.

Wrapper ownership for the input lane stays split: `drivers/virtio/virtio.zig` owns shared device-status bookkeeping, `drivers/virtio/virtio_ring.zig` owns virtqueue wrapper shape and notification planning, and `drivers/virtio/virtio_mmio.zig` owns MMIO wrapper planning, so transport-facing queue and registration-lifecycle work stays parked outside the input lane.

Current `master` now materializes the full packet-local slice set; keep `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, and `Documentation/zigux/phase10-virtio-mmio-slice.md` explicit as restored shared-review evidence instead of framing any packet-local slice companion as a repo-reality gap.

Tests-root reviewer prompt:
- Do the docs-root notes, scripts-root guards, tests-root packet, the bootstrap workflow replay of `make -C zigux phase10-validate`, and Linux-style make routes still describe the same bounded virtio core, ring, input, and MMIO closure packet, the focused core reset-queue replay, the direct `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig` interrupt-compound-ack replay, plus the restored `Documentation/zigux/phase10-virtio-core-slice.md` companion, ring drained-reset reuse replay, the closure-manifest-backed `drivers/virtio/virtio_ring.zig` ring packet vocabulary beside `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, `Documentation/zigux/phase10-virtio-ring-survey.md`, and `Documentation/zigux/phase10-virtio-ring-slice.md`, the closure-manifest-backed `drivers/virtio/virtio_input.zig` helper vocabulary beside `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_verify.zig` and the input queue-callback-preflight, registration-preflight, teardown-observation, and status-drain replays, the closure-manifest-backed `drivers/virtio/virtio_mmio.zig` helper vocabulary beside `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, and `Documentation/zigux/phase10-virtio-mmio-slice.md`, the input-lane wrapper split where `drivers/virtio/virtio.zig` owns shared device-status bookkeeping, `drivers/virtio/virtio_ring.zig` owns virtqueue wrapper shape and notification planning, and `drivers/virtio/virtio_mmio.zig` owns MMIO wrapper planning, the blocked risky-transport posture, the allowed `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` destination family, the separate `reference_samples` and `runtime_starters` boundary carried through `zigux/tests/phase10_closure_manifest.json`, the already-shipped `samples/zigux/runtime_trace_events_loader.zig` scaffold as adjacent Phase 9 evidence rather than Phase 10 closure progress, and the Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit, and do the restored core, ring, input, input-module, and MMIO slice-note companions stay explicit as directly re-readable evidence instead of leaving any packet-local slice companion framed as a repo-reality gap?

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
- `scripts/zigux/check-phase11-build-inventory.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`
- `scripts/zigux/check-phase11-dw-wdt-packet.py`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `scripts/zigux/check-phase11-hvc-survey-packet.py`
- `zigux/tests/phase11_build.zig`
- `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- `zigux/tests/phase11_gpio_wdt.zig`
- `zigux/tests/phase11_bcm2835_wdt.zig`
- `zigux/tests/phase11_dw_wdt.zig`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `drivers/watchdog/dw_wdt.zig`
- `zigux/tests/phase11_hvc_console.zig`
- `zigux/tests/phase11_hvc_cleanup.zig`
- `zigux/tests/phase11_hvc_console_manifest.json`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `zigux/tests/phase11_hvc_console_modem_control_split.zig`
- `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `drivers/tty/hvc/hvc_console_verify.zig`
- `drivers/tty/hvc/hvc_console_sysrq.zig`
- `zigux/Makefile`
- `make -C zigux phase11-contract`
- `make -C zigux phase11`
- `make -C zigux phase11-hvc-survey`

Treat the shared reminder notes and shipped checkers together with the shared `zigux/tests/fixtures/phase11_build_inventory.json` anchor, the exact shared `zig build test --build-file zigux/tests/phase11_build.zig --summary all` replay, the shared `make -C zigux phase11-contract` reminder route, the surviving DesignWare platform-registration continuity packet through `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, the dedicated HVC archival packet through `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, and `make -C zigux phase11-hvc-survey`, the standalone exported-helper proof packet through `zigux/tests/phase11_hvc_export_surface_layout_proof.zig` and `zigux/tests/phase11_hvc_export_surface_layout_build.zig`, plus the shared header-boundary survey through `Documentation/zigux/phase11-uapi-header-parity-survey.md` and `zigux/tests/phase11_uapi_header_parity_survey.zig` as the current directly re-readable Phase 11 evidence on `master`.

Direct GitHub contents reads now materialize `zigux/tests/phase11_build.zig` and the shared `zigux/tests/fixtures/phase11_build_inventory.json` anchor, so broader shared summaries should keep those directly readable shared-build surfaces explicit together with the exact `zig build test --build-file zigux/tests/phase11_build.zig --summary all` replay, `make -C zigux phase11-contract`, and the current direct watchdog, HVC, and exported-helper proof surfaces as landed bounded replay evidence rather than downgrading them into repo-reality gaps or older fallback-only wording.

Tests-root reviewer prompt:
- Do the docs-root notes, checker split, shared summary-surface checker, shared build-inventory checker, the shared `zigux/tests/fixtures/phase11_build_inventory.json` anchor, tests-root packet, the shared `phase11-contract` reminder route, the exact shared `zig build test --build-file zigux/tests/phase11_build.zig --summary all` replay, and Linux-style make routes still describe the same shared-versus-dedicated simple-driver packet, the parked shared closure checkpoint, the parked driver-lane owner map, the dedicated bcm2835 archival packet, the surviving DesignWare platform-registration continuity packet through `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, the dedicated archival HVC validation-matrix, survey-note, teardown-note, direct `zigux/tests/phase11_hvc_console.zig` replay, bounded `zigux/tests/phase11_hvc_cleanup.zig` handoff, manifest-backed survey gate, modem-control split, poll-retry split, direct `drivers/tty/hvc/hvc_console_verify.zig` replay boundary, sysrq-helper boundary, and `phase11-hvc-survey` checker-backed route, the standalone exported-helper layout proof through `zigux/tests/phase11_hvc_export_surface_layout_proof.zig` and `zigux/tests/phase11_hvc_export_surface_layout_build.zig`, plus the shared header-boundary survey through `Documentation/zigux/phase11-uapi-header-parity-survey.md` and `zigux/tests/phase11_uapi_header_parity_survey.zig`, while keeping the direct `zigux/tests/phase11_build.zig`, `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`, `zigux/tests/phase11_hvc_export_surface_layout_build.zig`, and `drivers/tty/hvc/hvc_console_verify.zig` surfaces explicit as landed bounded replay evidence without implying removed validators or missing inventory fixtures?

## Phase 13 tests-root packet

Keep the current contributor-facing Phase 13 packet explicit through these shipped shared surfaces:
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-libfs-survey.md`
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `fs/libfs.zig`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_libfs_manifest.json`
- `lib/devres.zig`
- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_boundary_evidence.zig`
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
- blocked convenience route `make -C zigux phase13`

Keep the shared validator-first release handle anchored to current repo reality: current `master` now materializes the bounded `fs/libfs.zig` foothold together with `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`.

It also materializes the devres helper packet through `lib/devres.zig`, `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, and `zigux/tests/phase13_devres_manifest.json`, and `scripts/zigux/check-phase13-devres-packet-alignment.py`, so broader contributor wording should keep that direct boundary-evidence replay explicit beside the shared devres packet instead of treating it as a missing companion.

Current `master` also materializes the helper-owned Landlock ownership and syscall-governance notes plus the shipped `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `Documentation/zigux/phase13-landlock-syscalls-survey.md` notes, the shipped `security/landlock/ruleset.zig` and `security/landlock/syscalls.zig` starters, the direct ruleset replay pair `zigux/tests/phase13_landlock_ruleset.zig` and `zigux/tests/phase13_landlock_ruleset_manifest.json`, the direct syscall replay packet `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`, so contributor workflow wording should keep those shipped helper anchors explicit beside `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, and `scripts/zigux/check-phase13-landlock-ruleset-packet.py` instead of treating Landlock as docs-only ownership metadata.

Current `master` also materializes the adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/notifier_chain_view.zig` helper, and the Linux-side `drivers/tty/hvc/hvc_console.h` header, so keep those four paths explicit as shipped adjacent evidence without counting them as extra shared replay steps.

Current `master` still does not materialize `scripts/zigux/check-phase13-shared-summary-surfaces.py`, so keep that checker framed as a remaining shared-summary repo-reality gap rather than as shipped tests-root evidence.

If direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, or the older `scripts/zigux/check-phase13-devres-packet.py` cannot be materialized on current `master`, record them as repo-reality gaps instead of presenting them here as independently shipped review evidence.

Current `master` still exposes `make -C zigux phase13` through `zigux/Makefile`, but that broader convenience route currently fans out to `phase13-test`, which still calls `zig build test --build-file zigux/tests/phase13_build.zig --summary all` while `zigux/tests/phase13_build.zig` remains a repo-reality gap.

Keep `make -C zigux phase13-validate` as the stable contributor-facing handle until the shared build companion lands, and treat the broader `phase13` route as blocked convenience wiring rather than direct shipped current-`master` evidence.

Current `master` also materializes the dedicated Phase 13 packet summary in `zigux/tests/README.md`, so keep that broader tests-root guide aligned with the contributor workflow guide and shared-helper sequencing note as shipped Phase 13 review evidence instead of framing it as a pending shared-surface follow-up.

Tests-root reviewer prompt:
- Do the contributor workflow guide, shared-helper sequencing note, release-coordination-matrix, release-notes and roadmap-traceability notes, the shipped `Documentation/zigux/phase13-libfs-survey.md` note plus `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`, the shipped devres slice and survey plus `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, and `zigux/tests/phase13_devres_manifest.json`, and `scripts/zigux/check-phase13-devres-packet-alignment.py`, the helper-owned Landlock ownership and syscall-governance notes plus the shipped `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, and `Documentation/zigux/phase13-landlock-syscalls-survey.md` notes, the shipped `security/landlock/ruleset.zig` and `security/landlock/syscalls.zig` starters, the direct ruleset replay pair `zigux/tests/phase13_landlock_ruleset.zig` and `zigux/tests/phase13_landlock_ruleset_manifest.json`, the direct syscall replay packet `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`, the shipped `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, the shared release validator `scripts/zigux/validate-phase13-release.py`, the adjacent notifier survey and priority-signal guard, the shared validator-first release handle, the blocked `make -C zigux phase13` convenience-route wording in `zigux/Makefile`, the shared contributor-surface sync note, the shared review checklist, the shipped tests-root Phase 13 summary in `zigux/tests/README.md`, and the explicit repo-reality gap note for `scripts/zigux/check-phase13-shared-summary-surfaces.py` still keep the active contributor packet aligned while keeping the shipped adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/notifier_chain_view.zig`, and the Linux-side `drivers/tty/hvc/hvc_console.h` header explicit without counting them as extra shared replay steps, while treating missing direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and the older `scripts/zigux/check-phase13-devres-packet.py` as repo-reality gaps rather than shipped evidence, and while treating the dedicated Phase 13 packet summary in `zigux/tests/README.md` as shipped review evidence instead of a remaining shared-surface gap?

## Shared rule

When one of these packets changes, keep the tests-root replay note, the packet-local manifest or focused reviewability shard when one is actually present on current `master`, and the validator-first review surface reviewable together.
