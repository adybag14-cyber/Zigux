# Phase 10, 11, and 13 Tests-Root Review Companion

Use this note when a change touches the active Phase 10 virtio lab packet, the active Phase 11 simple-driver packet, or the active Phase 13 shared-helper contributor packet and the review needs one compact tests-root reminder.

Keep `Documentation/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, and `scripts/zigux/README.md` aligned with this note when they describe the same shared contributor-facing packet.

## Phase 10 tests-root packet

Keep the current bounded virtio closure packet explicit through these shared surfaces and closure-manifest-backed packet-local inventory claims:
- `Documentation/zigux/phase10-closure-evidence.md`
- `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
- `Documentation/zigux/phase10-virtio-core-slice.md`
- `Documentation/zigux/phase10-virtio-core-survey.md`
- `Documentation/zigux/phase10-virtio-ring-slice.md`
- `Documentation/zigux/phase10-virtio-ring-survey.md`
- `Documentation/zigux/phase10-virtio-input-slice.md`
- `Documentation/zigux/phase10-virtio-input-module-slice.md`
- `Documentation/zigux/phase10-virtio-input-survey.md`
- `Documentation/zigux/phase10-virtio-mmio-slice.md`
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
- `drivers/virtio/virtio_input_verify.zig`
- `zigux/tests/phase10_virtio_input_probe_preflight.zig`
- `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`
- `zigux/tests/phase10_virtio_input_registration_preflight.zig`
- `zigux/tests/phase10_virtio_input_teardown_observation.zig`
- `zigux/tests/phase10_virtio_input_status_drain.zig`
- `zigux/tests/phase10_virtio_input_manifest.json`
- `zigux/tests/phase10_virtio_input_survey.zig`
- `zigux/tests/phase10_virtio_mmio.zig`
- `drivers/virtio/virtio_mmio_verify.zig`
- `zigux/tests/phase10_virtio_mmio_manifest.json`
- `zigux/tests/phase10_virtio_mmio_survey.zig`
- `zigux/Makefile`
- `make -C zigux phase10-validate`
- `zig build test --build-file zigux/tests/phase10_build.zig`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Treat the shared reminder notes, validators, and Linux-style make routes above together with the directly readable `zigux/tests/phase10_closure_manifest.json` plus `zigux/tests/phase10_virtio_ring_manifest.json` as the currently re-readable Phase 10 anchors. Treat the wider packet-local file list above as closure-manifest-backed inventory rather than as a claim that every path was directly re-read in the same review. If packet-local companions such as `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `scripts/zigux/check-phase10-mmio-packet.py`, or `zigux/tests/phase10_virtio_mmio_manifest.json` still cannot be materialized through the authenticated contents bridge on current `master`, record them as repo-reality gaps instead of presenting them as independently re-read shipped evidence.

Tests-root reviewer prompt:
- Do the docs-root notes, scripts-root guards, tests-root packet, and Linux-style make routes still describe the same bounded virtio core, ring, input, and MMIO closure packet, the focused core reset-queue replay, ring drained-reset reuse replay, the direct `drivers/virtio/virtio_ring.zig` ring surface beside `drivers/virtio/virtio_ring_verify.zig`, input preflight and status-drain replays, and MMIO verify replays, the blocked risky-transport posture, the allowed `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` destination family, the separate `reference_samples` and `runtime_starters` boundary carried through `zigux/tests/phase10_closure_manifest.json`, the already-shipped `samples/zigux/runtime_trace_events_loader.zig` scaffold as adjacent Phase 9 evidence rather than Phase 10 closure progress, and the Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit, and do any packet-local direct-read misses stay framed as repo-reality gaps rather than silently re-presented as directly re-read evidence?

## Phase 11 tests-root packet

Keep the current shared-versus-dedicated simple-driver packet explicit through these shared surfaces:
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-closure-note.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-survey.md`
- `Documentation/zigux/phase11-dw-wdt-teardown-note.md`
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
- `zigux/tests/phase11_gpio_wdt_manifest.json`
- `zigux/tests/phase11_gpio_wdt_survey.zig`
- `zigux/tests/phase11_bcm2835_wdt.zig`
- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `zigux/tests/phase11_bcm2835_wdt_survey.zig`
- `zigux/tests/phase11_dw_wdt.zig`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `zigux/tests/phase11_dw_wdt_survey.zig`
- `zigux/tests/phase11_hvc_console_manifest.json`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `zigux/tests/phase11_hvc_console_modem_control_split.zig`
- `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `zigux/tests/phase11_uapi_header_parity_survey.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `drivers/tty/hvc/hvc_console_sysrq.zig`
- `zigux/Makefile`
- `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- `make -C zigux phase11`
- `make -C zigux phase11-hvc-survey`

Tests-root reviewer prompt:
- Do the docs-root notes, checker split, shared summary-surface checker, tests-root packet, and Linux-style make routes still describe the same shared-versus-dedicated simple-driver packet, the bounded `hvc_cleanup()` teardown handoff, the parked shared closure checkpoint, the parked driver-lane owner map, the dedicated bcm2835 archival packet, the dedicated DesignWare teardown and registration-scaffold boundary, the dedicated archival `hvc_console` teardown note plus the validation matrix, manifest-backed survey gate, the dedicated `scripts/zigux/check-phase11-hvc-survey-packet.py` checker-backed replay route, modem-control split, poll-retry split, and sysrq-helper boundary, and the focused header-boundary survey packet without implying a removed `validate-phase11.py`, a missing build-inventory fixture, or a broader checker stack than current `master` ships?

## Phase 13 tests-root packet

Keep the current contributor-facing Phase 13 packet explicit through these shipped shared surfaces:
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `fs/libfs.zig`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `security/landlock/ruleset.zig`
- `security/landlock/syscalls.zig`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `scripts/zigux/check-phase13-devres-packet-alignment.py`
- `scripts/zigux/validate-phase13-release.py`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `zigux/tests/README.md`
- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_dma_coherent.zig`
- `zigux/tests/phase13_devres_manifest.json`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

Keep the shared validator-first eight-test release packet anchored to current repo reality: current `master` still materializes the bounded `fs/libfs.zig` plus `zigux/tests/phase13_libfs.zig` foothold together with `zigux/tests/phase13_libfs_reviewability.zig`, the direct `zigux/tests/phase13_devres.zig` replay together with `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_manifest.json`, plus `Documentation/zigux/phase13-devres-survey.md` and `scripts/zigux/check-phase13-devres-packet-alignment.py`. It also materializes the small helper-local `security/landlock/ruleset.zig` and `security/landlock/syscalls.zig` starters beside the ownership and governance notes, while wider direct companions remain partial. Current `master` also materializes the adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig` and `include/zigux/abi.h`, so keep those two paths explicit as shipped adjacent evidence without counting them as extra shared replay steps. If direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_landlock_*.zig`, the direct `zigux/tests/phase13_libfs_manifest.json` plus Landlock manifest files under `zigux/tests/`, the older dedicated `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/check-phase13-notifier-packet.py`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/helpers/notifier_chain_view.zig`, or `drivers/tty/hvc/hvc_console.h` cannot be materialized on current `master`, record them as repo-reality gaps instead of presenting them here as independently shipped review evidence.

Tests-root reviewer prompt:
- Do the contributor workflow guide, shared-helper sequencing note, release-notes and roadmap-traceability notes, the shipped devres slice and devres survey, the helper-owned Landlock ownership and syscall-governance notes plus the shipped `security/landlock/ruleset.zig` and `security/landlock/syscalls.zig` starters, the landlock ruleset packet checker, the adjacent notifier survey and priority-signal guard, the shipped devres packet-alignment guard, the shared validator-first eight-test release packet, the shared contributor-surface sync note, the shared review checklist, the broader tests-root guide, and Linux-style make routes still describe the same active Phase 13 contributor packet while keeping the shipped `fs/libfs.zig` plus `zigux/tests/phase13_libfs.zig` foothold together with `zigux/tests/phase13_libfs_reviewability.zig`, and the shipped `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_manifest.json`, `Documentation/zigux/phase13-devres-survey.md`, plus `scripts/zigux/check-phase13-devres-packet-alignment.py` guard explicit, while keeping the shipped adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig` and `include/zigux/abi.h` explicit without counting them as extra shared replay steps, while keeping missing direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_landlock_*.zig`, the direct `zigux/tests/phase13_libfs_manifest.json` plus Landlock manifest files under `zigux/tests/`, the older dedicated `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/check-phase13-notifier-packet.py`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/helpers/notifier_chain_view.zig`, and `drivers/tty/hvc/hvc_console.h` framed as repo-reality gaps rather than shipped current-master evidence, and does the sequencing note keep `libfs`, `devres` helper parity, `devres` packet truthfulness, the shipped Landlock starter anchors, `landlock`, and adjacent notifier evidence from being treated as one shared owner while keeping the landed nonincreasing-priority signal explicit?

## Checklist carryover prompts

Keep these reviewer questions explicit when `zigux/tests/README.md` or other shared contributor-facing workflow notes are refreshed:
- Phase 10: do the docs-root notes, scripts-root guards, tests-root packet, and Linux-style make routes still keep the bounded virtio core, ring, input, and MMIO packet aligned while preserving the shared validator-first route, the focused core reset-queue replay, ring drained-reset reuse replay, the direct `drivers/virtio/virtio_ring.zig` ring surface beside `drivers/virtio/virtio_ring_verify.zig`, input preflight and status-drain replays, and MMIO verify replays, the closure-manifest boundary, the adjacent Phase 9 scaffold, and the Phase 14 study-only deep-core ownership cues?
- Phase 11: do the docs-root notes, checker split, shared summary-surface checker, tests-root packet, and Linux-style make routes still keep the shared-versus-dedicated simple-driver packet, the bounded `hvc_cleanup()` teardown handoff, the dedicated bcm2835 archival packet, the DesignWare registration and teardown boundary, the dedicated archival `hvc_console` teardown note plus the validation matrix, manifest-backed survey gate, the dedicated `scripts/zigux/check-phase11-hvc-survey-packet.py` checker-backed replay route, modem-control split, poll-retry split, and sysrq-helper boundary aligned without implying removed validators or missing inventory fixtures?
- Phase 13: do the contributor workflow guide, shared-helper sequencing note, release-notes and roadmap-traceability notes, the shipped devres survey, the helper-owned Landlock ownership and syscall-governance notes plus the shipped `security/landlock/ruleset.zig` and `security/landlock/syscalls.zig` starters, the landlock ruleset packet checker, the adjacent notifier survey and priority-signal guard, the shipped devres packet-alignment guard, the shared validator-first eight-test release packet, the shared contributor-surface sync note, the shared review checklist, the broader tests-root guide, and Linux-style make routes still keep the active contributor packet aligned while keeping the shipped `fs/libfs.zig` plus `zigux/tests/phase13_libfs.zig` foothold together with `zigux/tests/phase13_libfs_reviewability.zig`, and the shipped `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_manifest.json`, `Documentation/zigux/phase13-devres-survey.md` plus `scripts/zigux/check-phase13-devres-packet-alignment.py` guard explicit, while keeping the shipped adjacent direct-evidence shards `zigux/bindings/notifier_abi.zig` and `include/zigux/abi.h` explicit without counting them as extra shared replay steps, while treating missing direct companions such as `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_landlock_*.zig`, the direct `zigux/tests/phase13_libfs_manifest.json` plus Landlock manifest files under `zigux/tests/`, the older dedicated `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/check-phase13-notifier-packet.py`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/helpers/notifier_chain_view.zig`, and `drivers/tty/hvc/hvc_console.h` as repo-reality gaps rather than shipped evidence?

## Shared rule

When one of these packets changes, keep the tests-root replay note, the packet-local manifest or focused reviewability shard when one is actually present on current `master`, and the validator-first review surface reviewable together.
