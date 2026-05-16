# Phase 10 Virtio Input Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_input.c`.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-input-survey`
- `PHASE10_LANE_KEY=P10-L13`
- `PHASE10_DUAL_IMPLEMENTATION_POSTURE=blocked_on_risky_transport`
- `PHASE10_SURVEYED_COMMIT=7361ac51374149a96b7a7a2c6ea3c995d8cc1231`
- scope: keep the current `virtio_input` packet fail-closed around the landed lab-only driver validation evidence while risky transport remains blocked, the roadmap's dual implementations for risky areas stay parked at `blocked_on_risky_transport`, and the adjacent shared build-graph follow-through stays parked in `P10-L15`

## Why this slice exists

The Phase 10 roadmap still names `drivers/virtio/virtio_input.c` as a VM-friendly lab-driver anchor and requires lab-only driver validation before risky-transport dual implementations can reopen broader lifecycle claims.

This survey keeps the current packet truthful around the direct helper, the wrapper-facing verify replay in `drivers/virtio/virtio_input_verify.zig`, the direct gate in `zigux/tests/phase10_virtio_input.zig`, the dedicated probe-preflight replay in `zigux/tests/phase10_virtio_input_probe_preflight.zig`, the dedicated queue-callback-preflight replay in `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, the dedicated registration-preflight helper in `drivers/virtio/virtio_input_registration_preflight.zig`, the registration-preflight replay in `zigux/tests/phase10_virtio_input_registration_preflight.zig`, the teardown-observation replay in `zigux/tests/phase10_virtio_input_teardown_observation.zig`, the focused status-drain replay in `zigux/tests/phase10_virtio_input_status_drain.zig`, the capability-setup and multitouch-slot helper boundaries in `drivers/virtio/virtio_input.zig`, the bounded probe-preflight, registration-preflight, queue-callback-preflight, status-drain, and teardown-observation helpers, the survey gate, and the new slice companions.

The current note therefore keeps `phase10-virtio-input-verify-replay`, `phase10-virtio-input-capability-setup-helper`, `phase10-virtio-input-multitouch-slot-helper`, `phase10-virtio-input-probe-preflight-replay`, `phase10-virtio-input-probe-preflight-helper`, `phase10-virtio-input-registration-preflight-replay`, `phase10-virtio-input-registration-preflight-helper`, `phase10-virtio-input-queue-callback-preflight-replay`, `phase10-virtio-input-queue-callback-preflight-helper`, `phase10-virtio-input-status-drain-helper`, `phase10-virtio-input-teardown-observation-replay`, `phase10-virtio-input-teardown-observation-helper`, and `phase10-virtio-input-wrapper-ownership-note` explicit instead of collapsing the packet back to a helper-only story.

## Survey Findings

- `drivers/virtio/virtio_input.c` is still the Phase 10 anchor and still mixes config-space reads, queue setup, status sends, event handling, capability setup, registration-facing state, freeze or restore hooks, and teardown paths.
- current `master` now keeps the capability-setup and multitouch-slot helpers, the direct lab gate, the dedicated probe-preflight replay, the wrapper-facing verify replay, the probe-preflight summary, the queue-callback preflight summary plus replay, the dedicated registration-preflight helper plus replay, the teardown-observation summary plus replay, the focused status-drain replay plus the bounded status-drain helper, the survey gate, the survey manifest, and the packet-local slice companions visible in the same lane.
- the Phase 10 roadmap still requires dual implementations for risky areas before this lane can widen into transport-backed registration, queue callback, freeze, restore, or status-completion closure, so the current survey packet keeps that posture explicit as `blocked_on_risky_transport` instead of implying a reopened Architecture Council packet.
- wrapper ownership stays with the already-landed shared Phase 10 packets in `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, and `drivers/virtio/virtio_mmio.zig`, so those wrappers remain outside virtio_input-local work.
- the shared Phase 10 exact-check route still rereads `scripts/zigux/check-phase10-core-packet.py`, `scripts/zigux/check-phase10-ring-packet.py`, and `scripts/zigux/check-phase10-mmio-packet.py` beside the dedicated input packet checker so the roadmap-facing lab-only driver validation bundle stays reviewable as one bounded packet family.
- `zig build test --build-file zigux/tests/phase10_build.zig --summary all`, `make -C zigux phase10-test`, and `make -C zigux phase10` remain the shared replay markers for this packet even though lane-local ownership here stays on the input survey family rather than the shared compile-path follow-through.
- `make -C zigux phase10-test` and `make -C zigux phase10` remain the shared route markers for this packet even though the adjacent compile-path follow-through for the probe-preflight, registration-preflight, and teardown-observation build entries stays parked in `P10-L15`.

## Recorded Gaps

- `phase10-virtio-input-verify-replay` keeps the wrapper-facing verify replay explicit beside the probe-preflight summary and the status-drain replay.
- `phase10-virtio-input-capability-setup-helper` keeps `virtinput_cfg_bits()`, `virtinput_cfg_abs()`, and `input_set_capability()` explicit inside the bounded registration-side helper packet.
- `phase10-virtio-input-multitouch-slot-helper` keeps `ABS_MT_SLOT` handling and the slot-planning helper explicit below risky transport.
- `phase10-virtio-input-probe-preflight-replay` keeps the dedicated probe-preflight replay explicit around identity, queue-plan, and registration-handoff blocker ordering before real input registration or transport-backed callback execution.
- `phase10-virtio-input-probe-preflight-helper` keeps the probe-preflight summary explicit around identity staging, queue-fill readiness, and bounded work below `input_register_device()`.
- `phase10-virtio-input-queue-callback-preflight-helper` keeps the queue-callback preflight summary explicit around queue configuration, ready state, and transport-backed callback handoff.
- `phase10-virtio-input-queue-callback-preflight-replay` keeps the dedicated queue-callback-preflight replay explicit as the bounded blocker-ordering replay below real event delivery.
- `phase10-virtio-input-registration-preflight-replay` keeps the dedicated registration-preflight replay explicit as the bounded blocker-ordering replay below real `input_register_device()` lifecycle parity.
- `phase10-virtio-input-registration-preflight-helper` keeps the dedicated registration-preflight helper explicit around event-queue, status-queue, event-buffer, capability-setup, and multitouch-slot blockers below `input_register_device()`.
- `phase10-virtio-input-status-drain-helper` keeps the bounded status-drain helper explicit around completed status sends and transport-backed status completion callbacks that are still not executed for real.
- `phase10-virtio-input-teardown-observation-replay` keeps the dedicated teardown-observation replay explicit as the reset-local cleanup replay below remove, freeze, or restore parity.
- `phase10-virtio-input-teardown-observation-helper` keeps the teardown-observation summary explicit around reset-local identity preservation and capability cleanup without widening into remove lifecycle claims.
- `phase10-virtio-input-wrapper-ownership-note` keeps the wrapper ownership reminder explicit so virtio core, virtqueue wrapper, and MMIO wrapper work stays outside virtio_input-local work.
- `phase10-virtio-input-registration-lifecycle` remains blocked below real event delivery, input registration lifecycle parity, freeze or restore parity, transport-backed status completion callbacks, and the roadmap's dual-implementation boundary for risky transport.

## Non-Goals

This survey slice does not claim:

- real event delivery or full `input_register_device()` parity
- transport-backed status completion callbacks or queue-callback execution on live hardware paths
- probe, remove, freeze, restore, or reset parity beyond the bounded local summaries already landed
- risky-transport dual-implementation closure or an Architecture Council reopen attachment

## Gates

Keep this lane reviewable by rereading:

1. `Documentation/zigux/phase10-virtio-input-survey.md`
2. `Documentation/zigux/phase10-virtio-input-slice.md`
3. `Documentation/zigux/phase10-virtio-input-module-slice.md`
4. `zigux/tests/phase10_virtio_input_manifest.json`
5. `zigux/tests/phase10_virtio_input.zig`
6. `zigux/tests/phase10_virtio_input_probe_preflight.zig`
7. `zigux/tests/phase10_virtio_input_survey.zig`
8. `drivers/virtio/virtio_input.zig`
9. `drivers/virtio/virtio_input_probe_preflight.zig`
10. `drivers/virtio/virtio_input_registration_preflight.zig`
11. `drivers/virtio/virtio_input_verify.zig`
12. `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`
13. `zigux/tests/phase10_virtio_input_registration_preflight.zig`
14. `zigux/tests/phase10_virtio_input_teardown_observation.zig`
15. `zigux/tests/phase10_virtio_input_status_drain.zig`

## Next Bounded Step

Keep the next same-lane follow-through narrow: reread the refreshed survey note, slice companions, manifest, survey gate, direct gate, and registration-preflight replay together, then leave the shared `zigux/tests/phase10_build.zig` compile-path repair parked in `P10-L15` until that adjacent lane can land its already-prepared build-graph patch.
