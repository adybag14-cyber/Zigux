# Phase 10 Virtio Input Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_input.c`.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-input-survey`
- lane: `P10-L13`
- surveyed inspected `master` head: `f5a4d6990f701937b2a3bb9ae723bb6d0f27ba21`
- scope: survey manifest, dedicated survey gate, focused multitouch-ready and registration-blocker replays, shared Phase 10 validation-plus-harness-coverage wiring, and a lane-level note that compares the already-landed starter against the remaining roadmap gap
- product boundary:
  - `drivers/virtio/virtio_input.zig`
  - `drivers/virtio/virtio_input_registration_blocker.zig`
  - `zigux/tests/phase10_virtio_input.zig`
  - `zigux/tests/phase10_virtio_input_multitouch_preflight.zig`
  - `zigux/tests/phase10_virtio_input_registration_blocker.zig`
  - `zigux/tests/phase10_virtio_input_registration_blocker_build.zig`
  - `zigux/tests/phase10_virtio_input_manifest.json`
  - `zigux/tests/phase10_virtio_input_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `scripts/zigux/check-phase10-harness-coverage.py`
  - `scripts/zigux/validate-phase10.py`
  - `Documentation/zigux/phase10-virtio-input-survey.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_input.c` as a lab-driver anchor, but the repo has already moved past a blank starting point: the live tree now ships a bounded `drivers/virtio/virtio_input.zig` helper, dedicated tests, and slice notes.

This survey exists so the lane can compare that live starter against the roadmap and record the next honest gap without pretending the helper is either absent or already close to full driver parity.

## Survey findings

- `drivers/virtio/virtio_input.c` is present on `master` at 421 lines and mixes config-space selection, bitmap and ABS metadata reads, event-queue refill, status-queue sends, multitouch timestamp suppression, input-device registration, freeze or restore hooks, and teardown paths.
- the live repo already ships `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_registration_blocker.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_registration_blocker.zig`, `Documentation/zigux/phase10-virtio-input-slice.md`, and `Documentation/zigux/phase10-virtio-input-module-slice.md`.
- the landed Zigux starter now covers identity snapshots, property and event config bitmap summaries, ABS metadata summaries, capability-setup staging, bounded multitouch slot planning from `ABS_MT_SLOT`, a bounded registration-preflight summary, a bounded queue-callback preflight summary, a bounded probe-preflight summary, a bounded registration blocker summary that keeps lifecycle claims parked, fixed event and status queue planning, capped event-buffer fill accounting, ready-state gating, reset clearing, a reset-local teardown observation summary, and multitouch `EV_MSC` plus `MSC_TIMESTAMP` suppression in memory only.
- the same P10-L13 packet now contributes roadmap-backed `lab-only driver validation` evidence through `zigux/tests/phase10_virtio_input_multitouch_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_blocker.zig`, `zigux/tests/phase10_virtio_input_registration_blocker_build.zig`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/validate-phase10.py`, and the shared Phase 10 closure packet instead of leaving that scoreboard row implied by helper prose alone.
- the live repo still does not model real event delivery, `input_register_device()` registration parity, freeze or restore parity, or transport-backed queue callbacks.
- this means the probe-preflight boundary is now landed, and the remaining virtio_input lifecycle work stays intentionally blocked rather than widening into probe, remove, MMIO, or input core lifecycle claims.

## Recorded gaps

The survey manifest now records:

- the landed `phase10-build-gate`
- the landed `phase10-virtio-core-lab-starter`
- the landed `phase10-virtio-ring-lab-helper`
- the landed `phase10-virtio-input-lab-helper`
- the landed `phase10-virtio-input-lab-gate`
- the landed `phase10-virtio-input-slice-note`
- the landed `phase10-virtio-input-survey-gate`
- the landed `phase10-virtio-input-survey-note`
- the landed `phase10-virtio-input-capability-setup-helper`
- the landed `phase10-virtio-input-multitouch-slot-helper`
- the landed `phase10-virtio-input-teardown-observation-helper`
- the landed `phase10-virtio-input-registration-preflight-helper`
- the landed `phase10-virtio-input-queue-callback-preflight-helper`
- the landed `phase10-virtio-input-probe-preflight-helper`
- the landed `phase10-virtio-input-registration-blocker-helper`
- the still-blocked `phase10-virtio-input-registration-lifecycle`

This keeps the lane concrete and reviewable without overstating progress: the starter helper is real, and the new blocker helper makes the remaining lifecycle fence explicit instead of letting probe-readiness look like input-core parity, but most of the config and registration surface from `virtio_input.c` remains intentionally out of scope.

## Freeze Boundary

- `PHASE10_FREEZE_MAP=Documentation/zigux/freeze-map.md`
- `PHASE10_FREEZE_BOUNDARY_STATUS=aligned`
- `PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes`
- `PHASE10_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=no`
- `PHASE10_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle`

The roadmap keeps this lane inside `drivers/virtio/*.zig`, with justified bridge helpers allowed in `zigux/kernel/` or `zigux/helpers/` where needed, while the freeze map still keeps the deep-core anchors in C and the study-only transport-adjacent anchors in the separate Phase 14 family:

- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

The study-only anchors therefore remain outside this input lane and stay owned by the separate Phase 14 packet with `boundary maps`, `concurrency audits`, `explicit stay-in-C decisions where warranted`, and `wrapper-first or study-only posture` kept explicit before any future status change is even discussed. `kernel/workqueue_bridge.zig` and `kernel/trace/ring_buffer.zig` remain only future Phase 14 destinations.

This input survey therefore records an aligned freeze-boundary reading rather than a status-change request:

- no Architecture Council reopen request is attached to this Phase 10 input lane
- no parity scorecard entry here reopens `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`
- the allowed roadmap destinations for this lane family stay limited to `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`, while the risky transport posture stays blocked

## Non-goals

This survey slice does not yet claim:

- `input_dev` capability setup or registration parity
- real event delivery or status completion callbacks
- freeze, restore, remove, or reset lifecycle parity
- MMIO-backed transport work or DMA-facing queue behavior
- any reopen of the Phase 14 study-only anchors `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`; this lane stays inside `drivers/virtio/*.zig` and does not use the landed probe-preflight helper as a pretext for broader transport claims

## Gates

1. run the closure-backed validation guards
- `python3 scripts/zigux/check-phase10-closure-inventory.py`
- `python3 scripts/zigux/validate-phase10.py`
- `python3 scripts/zigux/check-phase10-harness-coverage.py`
- `python3 scripts/zigux/validate-phase10-closure.py`
- `make -C zigux phase10-validate`

The direct shared validator now appears here explicitly because the manifest-backed input packet depends on `scripts/zigux/validate-phase10.py` plus the published closure and harness-coverage path to keep the landed probe-preflight rung and the parked registration-lifecycle blocker fail-closed together.

2. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig --summary all`

3. run the Linux-style Phase 10 test entrypoint
- `make -C zigux phase10-test`

4. run the convenience target
- `make -C zigux phase10`

5. run the dedicated registration blocker replay
- `zig build test --build-file zigux/tests/phase10_virtio_input_registration_blocker_build.zig --summary all`

The focused multitouch-ready replay in `zigux/tests/phase10_virtio_input_multitouch_preflight.zig` and the dedicated registration-blocker replay above are the current roadmap-facing proof that this lane contributes to Phase 10 `lab-only driver validation` without widening into transport-backed lifecycle claims.

This keeps the input survey note aligned with the shared closure packet's exact test route instead of implying the direct build replay and combined convenience target are the only executable review surfaces for the current input packet.

## Next bounded step

Keep the Phase 10 virtio_input lane parked at the current probe-preflight boundary until a later transport-backed packet can justify widening into queue callbacks, interrupts, or `input_register_device()` lifecycle work with explicit risky-transport evidence.
