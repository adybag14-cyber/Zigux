# Phase 10 Virtio Ring Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_ring.c`.

## Status
- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-ring-survey`
- lane: `P10-L10`
- surveyed commit: `e42103fc02f544e1bd23a5ec2e5b584734f5af7d`
- roadmap destinations: `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`
- scope: keep the ring manifest, this survey note, the packet-local slice note, the ring freeze-boundary companion, and one bounded truthfulness or validation follow-through aligned with the current queue-local ring packet on `master`
- product boundary:
  - `zigux/tests/phase10_virtio_ring_manifest.json`
  - `Documentation/zigux/phase10-virtio-ring-slice.md`
  - `Documentation/zigux/phase10-virtio-ring-survey.md`
  - `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`
  - `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
  - `Documentation/zigux/phase10-closure-evidence.md`
  - `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
  - `Documentation/zigux/freeze-map.md`
  - `scripts/zigux/README.md`
  - `scripts/zigux/check-phase10-ring-packet.py`
  - `zigux/tests/phase10_build.zig`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_ring.c` as a primary anchor and asks Zigux to prove queue-local virtqueue wrappers up to the lab-driver threshold before widening into transport-backed lifecycle work.

Fresh repo-first inspection against the live Phase 10 manifest plus the shared closure packet, lane note, tests-root review companion, and scripts-root summary shows the ring packet still needs a truthfulness-first posture on current `master`: direct contents reads for `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, and `zigux/tests/phase10_virtio_ring_survey.zig` still return missing on current `master`.

This survey therefore exists to keep the remaining directly re-readable ring packet truthful and reviewable while the helper, replay, and transport-backed bridge stay blocked. Only `zigux/tests/phase10_build.zig`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, and `zigux/tests/phase10_virtio_ring_manifest.json` remain directly re-readable inside the ring packet today.

## Survey findings
- `drivers/virtio/virtio_ring.c` remains the Linux anchor for this lane, and `zigux/tests/phase10_virtio_ring_manifest.json` still records `e42103fc02f544e1bd23a5ec2e5b584734f5af7d` as the surveyed Phase 10 ring snapshot.
- the shared Phase 10 packet still keeps the ring survey note, the ring slice note, the ring freeze-boundary companion, the ring manifest, the shared closure packet, the shared lane note, the shared tests-root review companion, and the shared build gate explicit on current `master`.
- the live manifest now records the direct repo-reality gap honestly: the broader core foothold, the queue-local ring helper ladder, the wrapper-facing verify replay, and the dedicated ring survey replay are all currently absent from direct contents readback even though they remain important ring-lane destinations.
- the queue-local helper ladder still matters as bounded ring-lane vocabulary: `phase10-virtqueue-shape-helper`, `phase10-used-buffer-polling-helper`, `phase10-callback-enable-helper`, `phase10-callback-delay-helper`, `phase10-notify-prepare-helper`, `phase10-notification-data-summary-helper`, `phase10-broken-queue-poll-guard`, `phase10-queue-reset-helper`, and `phase10-queue-reset-readiness-helper` remain the reviewable helper targets that future direct helper restoration should cover.
- `Documentation/zigux/phase10-virtio-ring-slice.md` now carries that vocabulary in one packet-local note without restating the missing helper and replay paths as directly materialized evidence.
- the ring freeze-boundary companion keeps the `P10-L10` queue-local wrapper packet and the adjacent `P10-L11` risky-transport owner split explicit, so shared reminders do not silently blur reviewable ring vocabulary into MMIO-owned blocked transport claims.
- the ring lane still stays below transport-backed work: the blocked `phase10-ring-lab-driver-bridge` remains owned by the adjacent `P10-L11` MMIO packet, so this survey does not claim transport-backed queue discovery, IRQ acknowledgement, queue reset execution, DMA paths, or probe/remove lifecycle behavior.

## Recorded gaps

Fresh repo inspection supports these narrower conclusions:
- the landed `phase10-build-gate`
- the landed `phase10-virtio-ring-survey-note`
- the landed `phase10-virtio-ring-slice-note`
- the direct repo-reality gap `phase10-virtio-core-lab-starter`
- the direct repo-reality gap `phase10-virtio-ring-survey-gate`
- the direct repo-reality gap `phase10-virtqueue-shape-helper`
- the direct repo-reality gap `phase10-used-buffer-polling-helper`
- the direct repo-reality gap `phase10-callback-enable-helper`
- the direct repo-reality gap `phase10-callback-delay-helper`
- the direct repo-reality gap `phase10-notify-prepare-helper`
- the direct repo-reality gap `phase10-notification-data-summary-helper`
- the direct repo-reality gap `phase10-broken-queue-poll-guard`
- the direct repo-reality gap `phase10-queue-reset-helper`
- the direct repo-reality gap `phase10-queue-reset-readiness-helper`
- the direct repo-reality gap `phase10-ring-verify-replay`
- the still-blocked `phase10-ring-lab-driver-bridge`

That keeps the ring lane concrete and reviewable without overstating progress: the packet now treats the missing direct helper and replay surfaces as current repo reality while still preserving their exact destinations for future same-lane restoration. The next same-lane follow-through should stay inside one ring-only checker, manifest, or reminder-surface truthfulness repair rather than widening into risky transport work.

## Freeze boundary
- `Documentation/zigux/freeze-map.md` is the governing boundary note for this queue-local survey packet.
- freeze-boundary owner: `P10-L11`
- rollback owner: keep this survey note, `Documentation/zigux/phase10-virtio-ring-slice.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, and `Documentation/zigux/freeze-map.md` aligned before widening this queue-local note.
- this ring survey stays inside `drivers/virtio/*.zig`; it does not reopen `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, which remain Phase 14 study-only anchors under the freeze map.
- the Phase 15 freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c` also remain outside this lane; this survey does not claim scheduler, MM, RCU, or skbuff ownership, parity, or Architecture Council reopen authority.
- the allowed evidence here is the current manifest, this survey note, the ring slice note, the shared closure packet, the shared lane note, the shared tests-root review companion, the shared scripts-root summary, the freeze-map boundary note, and live repo readback; this survey does not claim a freeze-map status change or an attached Architecture Council reopen request.

## Non-goals
This survey slice does not claim:
- real split-ring or packed-ring transport parity beyond the bounded ring packet vocabulary
- DMA mapping or unmapping wrappers
- transport-backed queue discovery, IRQ acknowledgement, queue reset execution, or probe/remove lifecycle behavior
- a reopened Architecture Council decision

Do not reopen MMIO helper growth, DMA, interrupt delivery, queue discovery, reset execution, or probe/remove lifecycle work from this note.

## Gates
Current `master` keeps this ring lane reviewable through the bounded packet:
1. rerun the dedicated ring checker
- `python3 scripts/zigux/check-phase10-ring-packet.py --self-test`
- `python3 scripts/zigux/check-phase10-ring-packet.py`
2. rerun the shared Phase 10 build and Linux-style make routes when focused readback remains aligned
- `zig build test --build-file zigux/tests/phase10_build.zig`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Do not claim a transport-backed Phase 10 ring compile or lifecycle replay from this survey until the MMIO-owned bridge itself changes.

## Next bounded step
Keep the broader Phase 10 virtio lane parked unless fresh repo inspection finds one directly coupled same-lane follow-through. Inside this ring lane, the next honest bounded step is to keep `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, this survey note, and `scripts/zigux/check-phase10-ring-packet.py` aligned around the missing direct helper and replay surfaces while keeping the queue-local helper ladder framed as manifest-backed ring packet vocabulary until a fresh reread materializes those helper and replay paths again.
