# Phase 10 Virtio Ring Survey
This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_ring.c`.

## Status
- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-ring-survey`
- lane: `P10-L07`
- surveyed commit: `9b68e6dfb3ca8129cc6e9ee6bf4217cc7ca26df0`
- roadmap destinations: `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`
- scope: the ring manifest, this survey note, the shared lane note, and one bounded truthfulness or restore step that keeps the queue-local virtio ring packet honest against current `master`
- product boundary:
  - `zigux/tests/phase10_virtio_ring_manifest.json`
  - `Documentation/zigux/phase10-virtio-ring-survey.md`
  - `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
  - `Documentation/zigux/freeze-map.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_ring.c` as a primary anchor and asks Zigux to prove queue-local virtio ring wrappers before widening into transport-backed lifecycle work.

Fresh live-tree inspection now shows the opposite of the earlier landed-helper story: current `master` still exposes this survey note, `zigux/tests/phase10_virtio_ring_manifest.json`, and the shared `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md` note, but exact readback returns `404` for the direct ring helper packet at `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `Documentation/zigux/phase10-virtio-ring-slice.md`, and `scripts/zigux/check-phase10-ring-packet.py`. This survey therefore exists to record that the lane is currently in a packet-truthfulness or restore state, not a compile-ready wrapper-growth state.

## Survey findings
- `drivers/virtio/virtio_ring.c` remains present on current `master` as the Linux anchor for this lane.
- the direct ring helper packet is currently absent on `master`: exact contents reads failed for `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `Documentation/zigux/phase10-virtio-ring-slice.md`, and `scripts/zigux/check-phase10-ring-packet.py`.
- the shared Phase 10 build route for this lane is also not currently readable through the expected packet path because `zigux/tests/phase10_build.zig` returns `404` on the same live readback.
- `scripts/zigux/README.md` still inventories `scripts/zigux/check-phase10-ring-packet.py` as part of the shared Phase 10 packet even though the exact contents read for that checker currently returns `404`, so the remaining same-lane work also includes a shared reminder-surface truthfulness repair.
- because the direct ring helper, verify replay, focused tests, focused checker, and shared build route are absent, there is no honest current-master ring-lane compile or wrapper-behavior replay to rerun from this survey note today.
- the next ring-local product choice is therefore bounded and binary: either restore a real queue-local ring packet and then rerun the direct Zig gates, or retell the remaining manifest and shared reminder surfaces so they stop claiming that missing packet as current-master evidence.
- the blocked transport-backed bridge still belongs to the adjacent `P10-L10` MMIO packet. This ring survey may name that dependency, but it does not absorb MMIO helper growth or MMIO next-step selection.

## Recorded gaps

Fresh repo inspection supports these narrower conclusions:
- `zigux/tests/phase10_virtio_ring_manifest.json`, `Documentation/zigux/phase10-virtio-ring-survey.md`, and `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md` are still visible and are now the minimum packet-local evidence this lane can rely on.
- the direct ring helper packet is missing from current `master`, so this lane should not describe `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `Documentation/zigux/phase10-virtio-ring-slice.md`, or `scripts/zigux/check-phase10-ring-packet.py` as currently landed review surfaces until they are restored and reread successfully.
- `scripts/zigux/README.md` still names `scripts/zigux/check-phase10-ring-packet.py` as shipped scripts-root evidence for this lane, so the shared reminder packet should also stay fail-closed until the checker and the shared build route reread successfully through the authenticated contents bridge.
- the honest same-lane follow-through is now one bounded recovery step: restore the smallest real direct ring packet and rerun its focused Zig gates, or keep the lane fail-closed and repair the remaining manifest or shared reminder packet that still inventories those missing files as live evidence.

## Freeze boundary
- `Documentation/zigux/freeze-map.md` is the governing boundary note for this queue-local survey packet.
- freeze-boundary owner: `P10-L10`
- rollback owner: keep this survey note, `zigux/tests/phase10_virtio_ring_manifest.json`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, and `Documentation/zigux/freeze-map.md` aligned before widening this queue-local note.
- this ring survey stays inside `drivers/virtio/*.zig`; it does not reopen `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, which remain Phase 14 study-only anchors under the freeze map.
- the Phase 15 freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c` also remain outside this lane; this survey does not claim scheduler, MM, RCU, or skbuff ownership, parity, or Architecture Council reopen authority.
- the allowed evidence here is the current manifest, this survey note, the shared lane note, the freeze-map boundary note, and live-tree readback; this survey does not claim a freeze-map status change or an attached Architecture Council reopen request.

## Non-goals
This survey slice does not yet claim:
- real split-ring or packed-ring descriptor parity
- DMA mapping or unmapping wrappers
- `virtqueue_add_*`, `virtqueue_get_buf`, or `vring_interrupt` lifecycle behavior
- transport-backed queue discovery, IRQ acknowledgement, queue reset execution, or probe/remove lifecycle behavior
- a landed direct ring helper packet on current `master`

## Gates
Current `master` supports only the fail-closed ring survey packet:
1. reread `zigux/tests/phase10_virtio_ring_manifest.json`
2. reread `Documentation/zigux/phase10-virtio-ring-survey.md`
3. reread `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
4. confirm that current-master contents reads still return `404` for `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `scripts/zigux/check-phase10-ring-packet.py`, and `zigux/tests/phase10_build.zig`

Do not claim a direct Phase 10 ring compile, lab, or wrapper replay from this survey until that packet is restored and those file reads succeed again.

## Next bounded step
Keep the broader Phase 10 virtio lane parked unless fresh repo inspection finds one directly coupled same-lane follow-through. Inside this ring lane, the next honest bounded step is to restore the smallest real direct ring packet that makes `drivers/virtio/virtio_ring.zig` plus one focused verify or test replay readable again, then rerun the direct ring Zig gates. If restoration is not the right move, keep the follow-through fail-closed inside `zigux/tests/phase10_virtio_ring_manifest.json`, this survey note, and `scripts/zigux/README.md` so they stop overstating the missing ring wrapper surfaces.
