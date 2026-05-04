# Phase 10 Virtio MMIO Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_mmio.c` and the landed MMIO helper follow-ons.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-mmio-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 10 build wiring, and a lane-level note that records what is present in the live repo plus the remaining MMIO transport gap against the roadmap, including the bounded transport-identity snapshots, register-window, queue-register, queue-notify, queue-address, config-window, config-write, interrupt-ack, and probe-preflight helpers
- product boundary:
  - `zigux/tests/phase10_virtio_mmio_manifest.json`
  - `zigux/tests/phase10_virtio_mmio_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-mmio-survey.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_mmio.c` as a primary anchor, but it also says to prove virtqueue wrappers before widening into MMIO or other risky transport work.

The live repo already has a bounded `drivers/virtio/virtio.zig` core starter, a dedicated `zigux/tests/phase10_virtio_core_survey.zig` gate with its paired note, a dedicated `zigux/tests/phase10_virtio_ring_survey.zig` gate, a `drivers/virtio/virtio_ring.zig` lab helper that now reaches used-buffer polling, callback re-enable, delayed-callback pacing, and queue reset discipline, and the newer `virtio_input` starter plus survey paths. The repo now also ships a `drivers/virtio/virtio_mmio.zig` bounded transport-identity and register-window helper, a bounded queue-register helper, a queue-notify helper, a queue-address helper, a config-window helper, a config-write planning helper, a bounded interrupt-ack helper, and a probe-preflight helper, so this survey can keep moving from "MMIO is still absent" toward an honest record of what tiny MMIO surface has landed and what larger transport work remains blocked.

## Survey findings

- this survey packet still records the inspected `master` head `0945df1cf664a3582d7241f859183a13f3f04adb`, and the directly coupled MMIO survey artifacts remain aligned with the current bounded helper state after the probe-preflight rung landed in this same packet.
- `drivers/virtio/virtio_mmio.c` is present on `master` at 829 lines and mixes feature negotiation, config-space reads and writes, status handling, generation checks, interrupt acknowledgement, queue selection, queue sizing, ready-state toggles, queue notify side effects, queue-address programming, virtqueue discovery, reset paths, and probe or remove lifecycle work.
- the live repo already ships `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_mmio.zig`, eleven dedicated Phase 10 virtio test or survey files under `zigux/tests/` (`phase10_virtio_core.zig`, `phase10_virtio_core_survey.zig`, `phase10_virtio_ring.zig`, `phase10_virtio_ring_reset_reuse.zig`, `phase10_virtio_ring_survey.zig`, `phase10_virtio_input.zig`, `phase10_virtio_input_multitouch_preflight.zig`, `phase10_virtio_input_survey.zig`, `phase10_virtio_mmio.zig`, `phase10_virtio_mmio_queue_isolation.zig`, and `phase10_virtio_mmio_survey.zig`), `zigux/tests/phase10_build.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-core-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, and `Documentation/zigux/phase10-virtio-mmio-survey.md`.
- the landed MMIO helper stays intentionally narrow: it now models transport-identity snapshots for the magic value, transport version support, device-id presence, vendor-id bookkeeping, and bounded probe-preflight summaries around the earliest probe gate, plus MMIO register offsets, bounded feature-page selection, queue-select and queue-size planning, queue-ready bookkeeping, queue-notify snapshots, version-scoped queue-address planning, status and reset bookkeeping, config-generation tracking, interrupt-ack bookkeeping, read-only config-window snapshots, and in-memory config-write planning for byte, halfword, and word windows only.
- the focused `zigux/tests/phase10_virtio_mmio_queue_isolation.zig` replay now keeps queue-address planning and notify bookkeeping explicit across queue-selection changes instead of leaving that multi-queue lab boundary visible only from the shared closure packet and build graph.
- this means the roadmap's "virtqueue wrappers first, MMIO wrappers later" rule now holds for a small but real MMIO foothold through the probe-preflight rung, while the broader lifecycle and IRQ paths remain intentionally blocked.

## Recorded gaps

The survey manifest now records:

- the landed `phase10-build-gate`
- the landed `phase10-virtio-core-lab-starter`
- the landed `phase10-virtio-core-survey-gate`
- the landed `phase10-virtio-core-survey-note`
- the landed `phase10-virtio-ring-survey-gate`
- the landed `phase10-virtio-ring-lab-helper`
- the landed `phase10-virtio-ring-slice-note`
- the landed `phase10-virtio-mmio-survey-gate`
- the landed `phase10-virtio-mmio-survey-note`
- the landed `phase10-virtio-mmio-slice-note`
- the landed `phase10-callback-delay-helper`
- the landed `phase10-mmio-register-window-helper`
- the landed `phase10-mmio-queue-register-helper`
- the landed `phase10-mmio-queue-notify-helper`
- the landed `phase10-mmio-queue-address-helper`
- the landed `phase10-mmio-config-window-helper`
- the landed `phase10-mmio-config-write-helper`
- the landed `phase10-mmio-interrupt-ack-helper`
- the landed `phase10-mmio-probe-preflight-helper`
- the still-blocked `phase10-mmio-lifecycle-and-irq-paths`

This keeps the lane concrete and reviewable without overstating MMIO progress: the queue-facing footholds are real, the bounded transport-identity and register-window, queue-register, queue-notify, queue-address, config-window, config-write, interrupt-ack, and probe-preflight steps are now landed, the focused queue-isolation replay is named directly in the survey packet, and the broader transport-facing lifecycle and IRQ work is still intentionally blocked.

## Freeze Boundary

- `PHASE10_FREEZE_MAP=Documentation/zigux/freeze-map.md`
- `PHASE10_FREEZE_BOUNDARY_STATUS=aligned`
- `PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes`
- `PHASE10_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=no`
- `PHASE10_ALLOWED_EVIDENCE_KINDS=driver_local_lab_slices,survey_manifests,shared_validation_gates`
- `PHASE10_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle`

The roadmap keeps Phase 10 delivery rooted in `drivers/virtio/*.zig`, with justified bridge helpers allowed in `zigux/kernel/` or `zigux/helpers/` where needed, while the freeze map still keeps the deep-core anchors in C and the study-only transport-adjacent anchors in the separate Phase 14 family:

- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

The study-only anchors therefore remain outside this MMIO lane and stay owned by the separate Phase 14 packet with `boundary maps`, `concurrency audits`, `explicit stay-in-C decisions where warranted`, and `wrapper-first or study-only posture` kept explicit before any future status change is even discussed.

This MMIO survey therefore records an aligned freeze-boundary reading rather than a status-change request:

- no Architecture Council reopen request is attached to this Phase 10 MMIO lane
- no parity scorecard entry here reopens `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`
- the allowed roadmap destinations for this lane family stay limited to `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`, while the current MMIO packet itself remains driver-local
- the allowed evidence stays limited to driver_local_lab_slices, survey manifests, and shared validation gates

## Non-goals

This survey slice does not yet claim:

- real MMIO pointer-backed reads or writes in Zig
- queue setup and teardown parity from `vm_setup_vq()` and `vm_del_vqs()`
- full queue-address programming side effects across legacy PFN or modern DESC, AVAIL, and USED windows
- interrupt-handler parity from `vm_interrupt()`
- probe, remove, or command-line device creation parity
- DMA-facing queue plumbing
- any reopen of the Phase 14 study-only anchors `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`; this lane stays inside `drivers/virtio/*.zig` and does not use the landed interrupt-ack or probe-preflight rungs as a pretext for broader transport claims

## Gates

1. run the dedicated validation guards
- `python3 scripts/zigux/check-phase10-closure-inventory.py`
- `python3 scripts/zigux/validate-phase10.py`
- `python3 scripts/zigux/validate-phase10-closure.py`
- `python3 scripts/zigux/check-phase10-harness-coverage.py`
- `make -C zigux phase10-validate`

The direct shared validator now appears here explicitly because the manifest-backed MMIO packet depends on `scripts/zigux/validate-phase10.py` plus the published closure path to keep the landed interrupt-ack rung, the landed probe-preflight rung, and the parked lifecycle-and-IRQ blocker fail-closed together.

2. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig --summary all`

3. run the Linux-style Phase 10 test entrypoint
- `make -C zigux phase10-test`

This keeps the MMIO survey note aligned with the shared closure packet's exact check list instead of implying the direct build replay alone is the only test surface that matters here.

4. run the convenience target
- `make -C zigux phase10`

## Next bounded step

Leave the MMIO lane parked unless a future inspection can split `phase10-mmio-lifecycle-and-irq-paths` into a smaller transport-safe observation helper without claiming queue setup, IRQ delivery, probe, or remove parity or reopening the separate Phase 14 study-only boundary packet.
