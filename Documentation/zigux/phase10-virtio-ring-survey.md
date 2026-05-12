# Phase 10 Virtio Ring Survey
This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_ring.c`.

## Status
- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-ring-survey`
- lane: `P10-L07`
- surveyed commit: `bdfe88e865b94387b3c3bd41ca98054c452f78b9`
- roadmap destinations: `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`
- scope: survey manifest, this survey note, the shared lane note, and one lane-level record that keeps the queue-local virtqueue foothold and the remaining roadmap lab-driver gap framed honestly against current repo reality
- product boundary:
  - `zigux/tests/phase10_virtio_ring_manifest.json`
  - `Documentation/zigux/phase10-virtio-ring-survey.md`
  - `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
  - `Documentation/zigux/freeze-map.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_ring.c` as a primary anchor and asks Zigux to prove virtqueue wrappers before widening into transport-backed lifecycle work.

Fresh authenticated repo reads show that the ring lane does not yet materialize the direct `drivers/virtio/virtio_ring.zig` helper packet on current `master`. This survey therefore exists to answer the roadmap question honestly: the ring lane currently has a manifest-backed planning surface and a survey note, but the direct queue-local helper, verifier replay, dedicated survey gate, and drained-reset reuse replay are still repo-reality gaps rather than landed Phase 10 evidence.

## Survey findings
- `drivers/virtio/virtio_ring.c` is present on `master` and still spans split rings, packed rings, descriptor state, DMA mapping helpers, callback toggling, notification bookkeeping, queue reset, resize, and break or unbreak handling.
- the live repo directly materializes `zigux/tests/phase10_virtio_ring_manifest.json`, `Documentation/zigux/phase10-virtio-ring-survey.md`, and `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`.
- fresh authenticated reads on current `master` returned 404 for `scripts/zigux/check-phase10-ring-packet.py`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, and `zigux/tests/phase10_virtio_core_reset_queue.zig`.
- the honest roadmap gap is therefore broader than the previous note claimed: the queue-local virtqueue wrapper foothold is not yet directly reviewable on current `master`, and the ring packet remains a survey-and-manifest checkpoint rather than a landed helper packet.
- the blocked transport-backed bridge still belongs to the adjacent `P10-L10` MMIO packet. This ring survey may name that dependency, but it does not absorb MMIO helper growth or MMIO next-step selection.

## Recorded gaps

Fresh repo inspection now supports these narrower conclusions:
- `zigux/tests/phase10_virtio_ring_manifest.json` is present and still records the intended ring-lane packet shape, the freeze-boundary posture, and the blocked risky-transport bridge.
- `Documentation/zigux/phase10-virtio-ring-survey.md` and `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md` are present and keep the ring lane named.
- `scripts/zigux/check-phase10-ring-packet.py`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, and `zigux/tests/phase10_virtio_core_reset_queue.zig` do not materialize on current `master`.
- the remaining same-lane follow-through is a truthfulness repair around the ring manifest and shared reminder surfaces before any new ring-local helper or verifier claims would be honest.

## Freeze boundary
- `Documentation/zigux/freeze-map.md` is the governing boundary note for this queue-local survey packet.
- freeze-boundary owner: `P10-L10`
- rollback owner: keep this survey note, `zigux/tests/phase10_virtio_ring_manifest.json`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, and `Documentation/zigux/freeze-map.md` aligned before widening this queue-local note.
- this ring survey stays inside `drivers/virtio/*.zig`; it does not reopen `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, which remain Phase 14 study-only anchors under the freeze map.
- the Phase 15 freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c` also remain outside this lane; this survey does not claim scheduler, MM, RCU, or skbuff ownership, parity, or Architecture Council reopen authority.
- the allowed evidence here is the ring survey note, the ring manifest, the shared lane note, the freeze-map boundary note, and direct repo readback about which ring-lane files do or do not materialize on current `master`; this survey does not claim a freeze-map status change or an attached Architecture Council reopen request.

## Non-goals
This survey slice does not yet claim:
- real split-ring or packed-ring descriptor parity
- DMA mapping or unmapping wrappers
- `virtqueue_add_*`, `virtqueue_get_buf`, or `vring_interrupt` lifecycle behavior
- transport-backed queue discovery, IRQ acknowledgement, queue reset execution, or probe/remove lifecycle behavior
- a landed direct ring helper, verifier replay, dedicated ring checker, or drained-reset reuse replay on current `master`

## Gates
Current `master` supports only direct survey-surface rereads for this lane:
1. reread `zigux/tests/phase10_virtio_ring_manifest.json`
2. reread `Documentation/zigux/phase10-virtio-ring-survey.md`
3. reread `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
4. reread `Documentation/zigux/freeze-map.md`

Those reads keep the bounded ring-lane survey honest until the dedicated ring checker and direct Zig replay files actually land.

## Next bounded step
Keep the broader Phase 10 virtio lane parked unless fresh repo inspection shows the direct ring helper packet has actually landed. Inside this ring lane, the next honest bounded step is to refresh `zigux/tests/phase10_virtio_ring_manifest.json` so its landed-versus-missing status matches current `master`, then revisit the shared reminder surfaces one file at a time. Do not reopen MMIO helper growth, DMA, interrupt delivery, queue discovery, reset execution, or probe/remove lifecycle work from this note.
