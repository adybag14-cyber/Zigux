# Phase 10 Virtio Driver Lane Sequencing

This note keeps the active Phase 10 virtio lab bundle split into bounded lanes so shared reminders do not collapse core, ring, input, and MMIO work into one noisy packet.

## Scope

Use this note when a Phase 10 change touches the shipped virtio closure packet recorded in `zigux/tests/phase10_closure_manifest.json`.

Keep the current lane split explicit:
- core lane `P10-L01` owns the direct core review surfaces around `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_driver_id.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, and `drivers/virtio/virtio_verify.zig`
- ring lane `P10-L07` owns the manifest-backed ring survey packet in `zigux/tests/phase10_virtio_ring_manifest.json` plus `Documentation/zigux/phase10-virtio-ring-survey.md`, and keeps the current repo-reality gaps around `drivers/virtio/virtio_ring.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `drivers/virtio/virtio_ring_verify.zig`, and `scripts/zigux/check-phase10-ring-packet.py` explicit until those direct ring paths actually materialize on current `master`
- MMIO lane `P10-L10` owns `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `scripts/zigux/check-phase10-mmio-packet.py`, `scripts/zigux/check-phase10-mmio-freeze-boundary.py`, and the parked freeze-boundary reviewer packet around `Documentation/zigux/freeze-map.md` plus `Documentation/zigux/phase10-virtio-mmio-survey.md`
- input lane `P10-L13` owns `drivers/virtio/virtio_input.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_manifest.json`, `zigux/tests/phase10_virtio_input_survey.zig`, `scripts/zigux/check-phase10-input-packet.py`, and `drivers/virtio/virtio_input_verify.zig`

The closure manifest remains the commit-pinned inventory for the broader packet, including the packet-local slice and survey note paths, the blocked risky-transport posture, the allowed destination families, and the Phase 5, Phase 9, and Phase 14 boundary evidence.

## Owner Split

Keep the current owner map explicit:
- core truthfulness owns the direct core reminder surfaces in `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`
- core packet review owns the direct core packet surfaces in `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_driver_id.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, and `drivers/virtio/virtio_verify.zig`
- ring packet review owns the ring manifest and survey surfaces in `zigux/tests/phase10_virtio_ring_manifest.json` and `Documentation/zigux/phase10-virtio-ring-survey.md`, and it keeps the missing direct ring helper, replay, verifier, and checker paths explicit as repo-reality gaps until `drivers/virtio/virtio_ring.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `drivers/virtio/virtio_ring_verify.zig`, and `scripts/zigux/check-phase10-ring-packet.py` actually land on current `master`
- input packet review owns the direct input packet surfaces in `drivers/virtio/virtio_input.zig`, the focused input preflight and status-drain replays, `zigux/tests/phase10_virtio_input_manifest.json`, `zigux/tests/phase10_virtio_input_survey.zig`, `scripts/zigux/check-phase10-input-packet.py`, and `drivers/virtio/virtio_input_verify.zig`
- MMIO packet review owns the direct MMIO packet surfaces in `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio_survey.zig`, and `scripts/zigux/check-phase10-mmio-packet.py`
- freeze-boundary reminder truthfulness under `P10-L10` owns the parked risky-transport, allowed-destination, rollback-owner, and Phase 14 boundary wording carried through `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, and `scripts/zigux/check-phase10-mmio-freeze-boundary.py`
- shared closure truthfulness owns `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase10-harness-coverage.py`, `zigux/tests/phase10_closure_manifest.json`, `zigux/tests/phase10_build.zig`, `zigux/Makefile`, `make -C zigux phase10-validate`, `zig build test --build-file zigux/tests/phase10_build.zig`, `make -C zigux phase10-test`, and `make -C zigux phase10`

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
2. Keep the current validator posture explicit: the shared scripts-root Phase 10 truthfulness packet on current `master` is `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, and the build-backed replay routes, so reminder-surface edits should stay aligned with those shipped checks instead of implying a broader dedicated per-lane checker stack.
3. Keep risky transport blocked: do not imply queue setup or reset parity, IRQ parity, DMA paths, input registration lifecycle parity, or probe or remove lifecycle closure beyond the blocked gaps already recorded in `zigux/tests/phase10_closure_manifest.json`.
4. Treat the separate Phase 5 `reference_samples` boundary and the separate Phase 9 `runtime_starters` boundary as adjacent evidence only, not counted Phase 10 closure progress.
5. Keep the separate Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit instead of letting those anchors drift into the Phase 10 virtio packet.
6. When a shared reminder surface refreshes freeze-boundary wording, keep the parked `P10-L10` owner and rollback-owner note explicit around `Documentation/zigux/freeze-map.md` plus `Documentation/zigux/phase10-virtio-mmio-survey.md` instead of letting that policy drift back into anonymous shared wording.
7. When a broad reminder surface changes, prefer the directly shipped closure-manifest and checker-backed review packet over speculative packet-local inventory growth.
8. The shipped focused shared Phase 10 scripts on current `master` are `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/validate-phase10.py`, and `scripts/zigux/validate-phase10-closure.py`, so same-lane reminder work should stay anchored to the direct driver, docs, manifest, tests-root, validator, and shared-checker surfaces unless a new focused script actually lands.

## Non-Goals

This note does not widen Phase 10 into:
- direct risky-transport or lifecycle parity claims
- a dedicated shared validator stack beyond the shipped focused reminder checkers, validator routes, and build-backed replay routes
- Phase 5 sample closure, Phase 9 runtime-loader closure, or Phase 14 study-only evidence as counted virtio-driver progress
- a claim that the Phase 10 tranche is closed or ready for an Architecture Council reopen
