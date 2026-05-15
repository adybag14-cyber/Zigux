# Phase 10 Virtio Ring Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_ring.c`.

## Status
- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-ring-survey`
- lane: `P10-L10`
- surveyed commit: `e42103fc02f544e1bd23a5ec2e5b584734f5af7d`
- roadmap destinations: `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`
- scope: keep the ring manifest and this survey note aligned with current repo reality while the direct queue-local wrapper packet remains missing on `master`
- directly readable ring survey packet on current `master`:
  - `zigux/tests/phase10_virtio_ring_manifest.json`
  - `Documentation/zigux/phase10-virtio-ring-slice.md`
  - `Documentation/zigux/phase10-virtio-ring-survey.md`
  - `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
  - `Documentation/zigux/phase10-closure-evidence.md`
  - `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
  - `Documentation/zigux/freeze-map.md`
  - `scripts/zigux/README.md`

## Why this slice exists

The Phase 10 roadmap still names `drivers/virtio/virtio_ring.c` as a primary anchor and still expects queue-local virtqueue wrappers plus lab-only driver validation before transport-backed lifecycle work.

Fresh repo-first inspection of current `master` shows that the direct ring helper, replay, survey-gate, checker, and shared build-route files named by older reminders are not currently present in the tree. The survey packet that is directly readable today is therefore documentation-first: this note, the ring manifest, the packet-local slice note, and the shared lane reminders. This survey exists to keep that repo-reality gap explicit instead of overstating queue-local wrapper progress.

## Survey Findings

- `drivers/virtio/virtio_ring.c` remains the Linux anchor for this lane, and `zigux/tests/phase10_virtio_ring_manifest.json` still records `e42103fc02f544e1bd23a5ec2e5b584734f5af7d` as the surveyed Phase 10 ring snapshot.
- current `master` keeps the ring survey note, the ring manifest, the ring slice note, the shared lane note, the shared closure note, the shared tests-root review companion, and the freeze-map boundary note readable in-tree.
- current `master` does not currently ship `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `scripts/zigux/check-phase10-ring-packet.py`, or `zigux/tests/phase10_build.zig`.
- because those direct packet files are absent, this lane cannot honestly claim a landed queue-local helper ladder, a landed ring verify replay, a landed dedicated ring checker, or a landed dedicated ring survey gate on the current tree.
- the blocked `phase10-ring-lab-driver-bridge` still stays with the adjacent MMIO lane, so this survey still does not claim transport-backed queue discovery, IRQ acknowledgement, queue reset execution, DMA paths, or probe or remove lifecycle behavior.

## Recorded Gaps

- `phase10-build-gate` is a `repo_reality_gap`: the shared Phase 10 build route named by older ring reminders is not currently present as `zigux/tests/phase10_build.zig`.
- `phase10-virtio-core-lab-starter` is a `repo_reality_gap`: the adjacent direct core starter file `drivers/virtio/virtio.zig` is not currently present even though shared reminders still treat that foothold as landed ring-adjacent evidence.
- `phase10-virtio-ring-survey-gate` is a `repo_reality_gap`: `zigux/tests/phase10_virtio_ring_survey.zig` is not currently present on `master`.
- `phase10-virtio-ring-survey-note` remains `starter_landed`: this survey note is the directly readable lane surface that keeps the roadmap gap explicit while the direct packet is still missing.
- `phase10-virtqueue-shape-helper`, `phase10-used-buffer-polling-helper`, `phase10-callback-enable-helper`, `phase10-callback-delay-helper`, `phase10-notify-prepare-helper`, `phase10-notification-data-summary-helper`, `phase10-broken-queue-poll-guard`, `phase10-queue-reset-helper`, and `phase10-queue-reset-readiness-helper` are all `repo_reality_gap` entries because current `master` does not currently ship `drivers/virtio/virtio_ring.zig`.
- `phase10-ring-verify-replay` is a `repo_reality_gap`: current `master` does not currently ship `drivers/virtio/virtio_ring_verify.zig`.
- `phase10-virtio-ring-slice-note` is a `repo_reality_gap`: the slice note exists, but it still names absent ring helper, verify, replay, checker, and survey-gate files as shipped packet evidence.
- `phase10-ring-lab-driver-bridge` remains `blocked_on_risky_transport`: the roadmap still requires transport-backed queue discovery, IRQ acknowledgement, queue reset execution, and probe or remove lifecycle behavior before this lane can claim a true lab driver.

That keeps the ring lane honest and roadmap-backed without pretending that the current repo already carries queue-local wrapper code or dedicated ring validation surfaces that are not actually present in the tree.

## Freeze Boundary
- `Documentation/zigux/freeze-map.md` remains the governing boundary note for this queue-local survey lane.
- freeze-boundary owner: `P10-L11`
- rollback owner: keep this survey note and `zigux/tests/phase10_virtio_ring_manifest.json` aligned before widening ring claims again.
- this ring survey stays inside `drivers/virtio/*.zig`; it does not reopen `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, which remain Phase 14 study-only anchors.
- the allowed evidence here is the current manifest, this survey note, the packet-local slice note, the shared lane note, the shared closure packet, the shared tests-root review companion, the scripts-root summary, the freeze-map boundary note, and current repo readback.

## Non-goals
This survey slice does not claim:
- landed `virtio_ring` helper code that is not present on current `master`
- landed ring verify, replay, checker, or dedicated survey-gate files that are not present on current `master`
- real split-ring or packed-ring transport parity
- transport-backed queue discovery, IRQ acknowledgement, queue reset execution, DMA paths, or probe or remove lifecycle behavior
- an Architecture Council reopen attachment

## Gates
Current `master` does not yet ship a dedicated ring checker or ring survey gate. Keep this lane reviewable by rereading:

1. `Documentation/zigux/phase10-virtio-ring-survey.md`
2. `zigux/tests/phase10_virtio_ring_manifest.json`
3. `Documentation/zigux/phase10-virtio-ring-slice.md`
4. `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
5. `Documentation/zigux/phase10-closure-evidence.md`
6. `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
7. `Documentation/zigux/freeze-map.md`

## Next Bounded Step
Keep the next same-lane follow-through narrow: refresh `Documentation/zigux/phase10-virtio-ring-slice.md` and `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md` so they stop naming absent ring helper, replay, checker, and survey-gate files as landed packet evidence, or land the first direct queue-local ring helper plus its dedicated survey-gate surfaces before those reminder files widen ring claims again.