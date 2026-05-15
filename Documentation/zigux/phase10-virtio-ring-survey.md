# Phase 10 Virtio Ring Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_ring.c`.

## Status
- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-ring-survey`
- lane: `P10-L10`
- surveyed commit: `e42103fc02f544e1bd23a5ec2e5b584734f5af7d`
- roadmap destinations: `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`
- scope: keep the ring manifest and this survey note aligned with current repo reality while the direct queue-local wrapper packet still lacks one consistent contents-bridge read path
- directly readable ring survey packet on current `master`:
  - `zigux/tests/phase10_virtio_ring_manifest.json`
  - `Documentation/zigux/phase10-virtio-ring-slice.md`
  - `Documentation/zigux/phase10-virtio-ring-survey.md`
  - `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
  - `Documentation/zigux/phase10-closure-evidence.md`
  - `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
  - `Documentation/zigux/freeze-map.md`
  - `scripts/zigux/README.md`
  - `scripts/zigux/check-phase10-ring-packet.py`
  - `zigux/tests/phase10_build.zig`

## Why this slice exists

The Phase 10 roadmap still names `drivers/virtio/virtio_ring.c` as a primary anchor and still expects queue-local virtqueue wrappers plus lab-only driver validation before transport-backed lifecycle work.

Fresh repo-first inspection of current `master` shows that the shared `zigux/tests/phase10_build.zig` route and the dedicated `scripts/zigux/check-phase10-ring-packet.py` guard are now directly readable as broader Phase 10 validation packet evidence, while the direct ring helper, verify, replay, and dedicated survey-gate files still do not materialize through one consistent current-head contents-bridge path. This survey exists to keep that narrower contents-bridge gap explicit instead of overstating queue-local wrapper progress.

## Survey Findings

- `drivers/virtio/virtio_ring.c` remains the Linux anchor for this lane, and `zigux/tests/phase10_virtio_ring_manifest.json` still records `e42103fc02f544e1bd23a5ec2e5b584734f5af7d` as the surveyed Phase 10 ring snapshot.
- current `master` keeps the ring survey note, the ring manifest, the ring slice note, the shared lane note, the shared closure note, the shared tests-root review companion, the freeze-map boundary note, the scripts-root summary, the dedicated ring packet checker, and the shared `zigux/tests/phase10_build.zig` route readable in-tree.
- current `master` still does not yet materialize `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, or `zigux/tests/phase10_virtio_ring_survey.zig` through one consistent current-head contents-bridge path.
- because those direct packet files are still contents-bridge gaps, this lane cannot honestly claim a directly re-readable queue-local helper ladder, ring verify replay, reset-reuse replay, or dedicated ring survey gate on the current tree; the shared build route and dedicated checker remain broader Phase 10 validation packet evidence rather than direct ring-local helper proof.
- the blocked `phase10-ring-lab-driver-bridge` still stays with the adjacent MMIO lane, so this survey still does not claim transport-backed queue discovery, IRQ acknowledgement, queue reset execution, DMA paths, or probe or remove lifecycle behavior.

## Recorded Gaps

- `phase10-build-gate` is `starter_landed`: the shared Phase 10 build route is directly readable in `zigux/tests/phase10_build.zig` as broader validation packet evidence even while the direct ring helper packet still lacks one consistent contents-bridge path.
- `phase10-virtio-core-lab-starter` is a `repo_reality_gap`: the adjacent direct core starter file `drivers/virtio/virtio.zig` is not currently directly readable through the same contents bridge.
- `phase10-virtio-ring-survey-gate` is a `contents_bridge_gap`: `zigux/tests/phase10_virtio_ring_survey.zig` does not currently materialize through one consistent current-head contents-bridge path on `master`.
- `phase10-virtio-ring-survey-note` remains `starter_landed`: this survey note is the directly readable lane surface that keeps the roadmap gap explicit while the direct packet still lacks one consistent contents-bridge path.
- `phase10-virtqueue-shape-helper`, `phase10-used-buffer-polling-helper`, `phase10-callback-enable-helper`, `phase10-callback-delay-helper`, `phase10-notify-prepare-helper`, `phase10-notification-data-summary-helper`, `phase10-broken-queue-poll-guard`, `phase10-queue-reset-helper`, and `phase10-queue-reset-readiness-helper` are all `contents_bridge_gap` entries because the direct `drivers/virtio/virtio_ring.zig` packet still does not materialize through one consistent current-head contents-bridge path.
- `phase10-ring-verify-replay` is a `contents_bridge_gap`: current `master` does not yet surface `drivers/virtio/virtio_ring_verify.zig` through one consistent current-head contents-bridge path.
- `phase10-virtio-ring-slice-note` remains `starter_landed`: the slice note is directly readable and keeps the narrower ring-helper, verify, replay, and survey-gate contents-bridge gaps explicit without overstating queue-local wrapper progress.
- `phase10-ring-lab-driver-bridge` remains `blocked_on_risky_transport`: the roadmap still requires transport-backed queue discovery, IRQ acknowledgement, queue reset execution, and probe or remove lifecycle behavior before this lane can claim a true lab driver.

That keeps the ring lane honest and roadmap-backed without pretending that the current repo already carries a directly re-readable queue-local wrapper packet.

## Freeze Boundary
- `Documentation/zigux/freeze-map.md` remains the governing boundary note for this queue-local survey lane.
- freeze-boundary owner: `P10-L11`
- rollback owner: keep this survey note and `zigux/tests/phase10_virtio_ring_manifest.json` aligned before widening ring claims again.
- this ring survey stays inside `drivers/virtio/*.zig`; it does not reopen `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, which remain Phase 14 study-only anchors.
- the allowed evidence here is the current manifest, this survey note, the packet-local slice note, the shared lane note, the shared closure packet, the shared tests-root review companion, the scripts-root summary, the dedicated ring packet checker, the shared `zigux/tests/phase10_build.zig` route, the freeze-map boundary note, and current repo readback.

## Non-goals
This survey slice does not claim:
- landed `virtio_ring` helper code that is directly re-readable on current `master`
- landed ring verify, replay, or dedicated survey-gate files that are directly re-readable on current `master`
- real split-ring or packed-ring transport parity
- transport-backed queue discovery, IRQ acknowledgement, queue reset execution, DMA paths, or probe or remove lifecycle behavior
- an Architecture Council reopen attachment

## Gates
Current `master` now keeps one dedicated ring checker and one shared build route explicit for the broader Phase 10 packet while the direct ring helper packet still stays narrower. Keep this lane reviewable by rereading:

1. `Documentation/zigux/phase10-virtio-ring-survey.md`
2. `zigux/tests/phase10_virtio_ring_manifest.json`
3. `Documentation/zigux/phase10-virtio-ring-slice.md`
4. `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
5. `Documentation/zigux/phase10-closure-evidence.md`
6. `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
7. `scripts/zigux/check-phase10-ring-packet.py`
8. `zigux/tests/phase10_build.zig`
9. `Documentation/zigux/freeze-map.md`

## Next Bounded Step
Keep the next same-lane follow-through narrow: refresh the ring manifest and packet-local notes if another ring-local truthfulness drift appears, or land the first direct queue-local ring helper plus its dedicated replay and survey-gate surfaces before those reminder files widen ring claims again. Until that direct packet materializes, treat the dedicated checker and shared build route as broader Phase 10 validation packet evidence rather than as direct ring-local helper proof.
