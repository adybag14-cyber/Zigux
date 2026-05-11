# Phase 10 Virtio Driver Lane Sequencing

This note keeps the active Phase 10 virtio lab bundle split into bounded lanes so shared reminders do not collapse core, ring, input, and MMIO work into one noisy packet.

## Scope

Use this note when a Phase 10 change touches the shipped virtio closure packet recorded in `zigux/tests/phase10_closure_manifest.json`.

Keep the current lane split explicit:
- core lane `P10-L01` owns the direct core review surfaces around `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_driver_id.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, and `drivers/virtio/virtio_verify.zig`
- ring lane `P10-L07` owns `drivers/virtio/virtio_ring.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, and `drivers/virtio/virtio_ring_verify.zig`
- MMIO lane `P10-L10` owns `drivers/virtio/virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `drivers/virtio/virtio_mmio_verify.zig`, and `scripts/zigux/check-phase10-mmio-freeze-boundary.py`
- input lane `P10-L13` owns `drivers/virtio/virtio_input.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_manifest.json`, `zigux/tests/phase10_virtio_input_survey.zig`, and `drivers/virtio/virtio_input_verify.zig`

The closure manifest remains the commit-pinned inventory for the broader packet, including the packet-local slice and survey note paths, the blocked risky-transport posture, the allowed destination families, and the Phase 5, Phase 9, and Phase 14 boundary evidence.

## Owner Split

Keep the current owner map explicit:
- core truthfulness owns the direct core reminder surfaces in `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`
- core packet review owns `scripts/zigux/check-phase10-core-packet.py` together with `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, and `drivers/virtio/virtio_verify.zig`
- ring packet review owns `scripts/zigux/check-phase10-ring-packet.py`, `drivers/virtio/virtio_ring.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, and `drivers/virtio/virtio_ring_verify.zig`
- input packet review owns `scripts/zigux/check-phase10-input-packet.py`, `drivers/virtio/virtio_input.zig`, the focused input preflight and status-drain replays, `zigux/tests/phase10_virtio_input_manifest.json`, and `drivers/virtio/virtio_input_verify.zig`
- MMIO packet review owns `scripts/zigux/check-phase10-mmio-packet.py`, `scripts/zigux/check-phase10-mmio-freeze-boundary.py`, `drivers/virtio/virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio_survey.zig`, and `drivers/virtio/virtio_mmio_verify.zig`
- shared closure truthfulness owns `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, `zigux/tests/phase10_closure_manifest.json`, `zigux/tests/phase10_build.zig`, `zigux/Makefile`, `make -C zigux phase10-validate`, `zig build test --build-file zigux/tests/phase10_build.zig`, `make -C zigux phase10-test`, and `make -C zigux phase10`

## Shared Packet Surfaces

When a real Phase 10 change lands, keep these shared surfaces aligned:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase10-closure-evidence.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`
- `scripts/zigux/check-phase10-harness-coverage.py`
- `scripts/zigux/validate-phase10.py`
- `scripts/zigux/validate-phase10-closure.py`
- `scripts/zigux/check-phase10-core-packet.py`
- `scripts/zigux/check-phase10-ring-packet.py`
- `scripts/zigux/check-phase10-input-packet.py`
- `scripts/zigux/check-phase10-mmio-packet.py`
- `scripts/zigux/check-phase10-mmio-freeze-boundary.py`
- `zigux/tests/phase10_closure_manifest.json`
- `zigux/tests/phase10_build.zig`
- `zigux/Makefile`
- `make -C zigux phase10-validate`
- `zig build test --build-file zigux/tests/phase10_build.zig`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

## Sequencing Rules

Use this note to keep the bounded work order honest:
1. Prefer one virtio lane at a time instead of batching core, ring, input, and MMIO reminders into one mixed change.
2. Keep the current validator posture explicit: shared `validate-phase10.py`, `validate-phase10-closure.py`, `check-phase10-harness-coverage.py`, and the Linux-style `phase10-validate` target are shipped truthfulness guards on `master`, so reminder-surface edits should stay aligned with those routes instead of claiming they are absent.
3. Keep risky transport blocked: do not imply queue setup or reset parity, IRQ parity, DMA paths, input registration lifecycle parity, or probe or remove lifecycle closure beyond the blocked gaps already recorded in `zigux/tests/phase10_closure_manifest.json`.
4. Treat the separate Phase 5 `reference_samples` boundary and the separate Phase 9 `runtime_starters` boundary as adjacent evidence only, not counted Phase 10 closure progress.
5. Keep the separate Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit instead of letting those anchors drift into the Phase 10 virtio packet.
6. When a broad reminder surface changes, prefer the directly shipped closure-manifest and checker packet over speculative packet-local inventory growth.

## Non-Goals

This note does not widen Phase 10 into:
- direct risky-transport or lifecycle parity claims
- a dedicated shared validator stack beyond the shipped focused packet checkers, `validate-phase10.py`, `validate-phase10-closure.py`, `check-phase10-harness-coverage.py`, and build-backed replay routes
- Phase 5 sample closure, Phase 9 runtime-loader closure, or Phase 14 study-only evidence as counted virtio-driver progress
- a claim that the Phase 10 tranche is closed or ready for an Architecture Council reopen
