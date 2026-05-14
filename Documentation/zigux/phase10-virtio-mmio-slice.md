# Phase 10 Virtio MMIO Slice

This bounded Phase 10 slice records the current MMIO-local wrapper packet anchored to `drivers/virtio/virtio_mmio.c`.

- `PHASE10_SLICE=virtio-mmio-wrapper-packet`
- anchor: `drivers/virtio/virtio_mmio.c`
- scope: keep the MMIO-local review packet explicit beside the shared closure note, the dedicated MMIO survey, the packet-local manifest, and the still-blocked risky-transport boundary without widening into lifecycle-complete claims

## Shipped packet

- `drivers/virtio/virtio_mmio.zig` keeps the landed MMIO helper ladder explicit through register-window, queue-size, feature-word selector, feature-negotiation, config-window, config-write-plan, transport-identity, probe-preflight, config-write-disposition, and selected-queue-readiness helpers.
- The current packet keeps one explicit transport-identity summary, one bounded config-write disposition summary, one bounded probe-preflight summary, and one bounded selected-queue readiness summary reviewable through `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, and `zigux/tests/phase10_virtio_mmio_manifest.json`.
- `drivers/virtio/virtio_ring_verify.zig` and `drivers/virtio/virtio_input_verify.zig` stay visible beside this slice because the live MMIO survey still treats the ring-side and input-side verifier cues as adjacent review surfaces for MMIO handoff posture.
- The current packet also keeps the adjacent input-side replay surfaces explicit through `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, and `zigux/tests/phase10_virtio_input_status_drain.zig`, so the MMIO lane stays aligned with the probe-preflight and queue-handoff reminder packet that current `master` already names.
- The focused replay routes remain `zig test zigux/tests/phase10_virtio_mmio.zig` and `zig test zigux/tests/phase10_virtio_mmio_survey.zig`, while the broader shared replay packet still runs through `zig build test --build-file zigux/tests/phase10_build.zig`, `make -C zigux phase10-test`, and `make -C zigux phase10`.

## Why this packet exists

- The Phase 10 roadmap names `drivers/virtio/virtio_mmio.c` as a primary lab-driver anchor and requires MMIO wrappers plus lab-only driver validation before risky transport work.
- Current `master` already ships the dedicated MMIO survey note, the packet-local manifest, the direct MMIO helper and verify surfaces, and the shared closure packet, so this slice exists to keep that landed MMIO-local evidence reviewable as one bounded packet instead of leaving the packet-local note missing.
- This slice stays helper-first and in-memory only: it does not convert the blocked transport-facing follow-through into a queue setup, queue reset execution, IRQ, DMA, or probe-remove claim.

## Parked boundary

- `phase10-mmio-lifecycle-and-irq-paths` remains blocked on risky transport.
- `Documentation/zigux/freeze-map.md` still governs the boundary for this MMIO slice.
- The roadmap's dual-implementation posture remains blocked on risky transport, and this note does not attach an Architecture Council reopen.

## Next bounded step

Keep `Documentation/zigux/phase10-virtio-mmio-slice.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, `zigux/tests/phase10_virtio_mmio_manifest.json`, and `scripts/zigux/check-phase10-mmio-packet.py` aligned around the landed MMIO-local helper ladder. If the MMIO lane reopens, prefer one survey, manifest, checker, or replay truthfulness repair after a fresh build-backed validation pass instead of widening into transport-backed lifecycle work.
