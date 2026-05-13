# Phase 10 Virtio Ring Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_ring.c`.

## Status
- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-ring-survey`
- lane: `P10-L07`
- surveyed commit: `bdfe88e865b94387b3c3bd41ca98054c452f78b9`
- roadmap destinations: `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`
- scope: keep the ring manifest, this survey note, the shared lane note, and one bounded truthfulness or helper-follow-through step aligned with the current queue-local virtio ring packet on `master`
- product boundary:
  - `zigux/tests/phase10_virtio_ring_manifest.json`
  - `Documentation/zigux/phase10-virtio-ring-survey.md`
  - `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
  - `Documentation/zigux/phase10-closure-evidence.md`
  - `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
  - `Documentation/zigux/freeze-map.md`
  - `scripts/zigux/README.md`
  - `scripts/zigux/check-phase10-ring-packet.py`
  - `zigux/tests/phase10_build.zig`
  - `drivers/virtio/virtio_ring.zig`
  - `drivers/virtio/virtio_ring_verify.zig`
  - `zigux/tests/phase10_virtio_ring.zig`
  - `zigux/tests/phase10_virtio_ring_reset_reuse.zig`
  - `zigux/tests/phase10_virtio_ring_survey.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_ring.c` as a primary anchor and asks Zigux to prove queue-local virtqueue wrappers before widening into transport-backed lifecycle work.

Fresh repo-first inspection against the live Phase 10 manifest plus the shared closure packet, lane note, tests-root review companion, and scripts-root summary shows the direct ring packet is still present on current `master`: `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `scripts/zigux/check-phase10-ring-packet.py`, and `zigux/tests/phase10_build.zig` remain part of the bounded ring lane. This survey therefore exists to keep that queue-local wrapper packet truthful and reviewable while the transport-backed bridge stays blocked, not to collapse the lane back to a manifest-only restore story.

## Survey findings
- `drivers/virtio/virtio_ring.c` remains the Linux anchor for this lane, and `zigux/tests/phase10_virtio_ring_manifest.json` still records `bdfe88e865b94387b3c3bd41ca98054c452f78b9` as the surveyed Phase 10 ring snapshot.
- the shared Phase 10 packet still keeps the direct ring helper packet explicit on current `master`: `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `scripts/zigux/check-phase10-ring-packet.py`, and `zigux/tests/phase10_build.zig` remain the queue-local review surfaces that pair with this survey note.
- the live manifest still records seven preexisting Phase 10 test files together with the existing core foothold, the shared Phase 10 build gate, the ring survey note, and the direct ring verify replay as landed packet evidence.
- the landed queue-local wrapper ladder remains the same bounded Phase 10 ring packet: `phase10-virtqueue-shape-helper`, `phase10-used-buffer-polling-helper`, `phase10-callback-enable-helper`, `phase10-callback-delay-helper`, `phase10-notify-prepare-helper`, `phase10-notification-data-summary-helper`, `phase10-broken-queue-poll-guard`, `phase10-queue-reset-helper`, `phase10-queue-reset-readiness-helper`, and `phase10-ring-verify-replay`.
- the live manifest now keeps `phase10-notification-data-summary-helper` explicit as landed queue-local wrapper evidence, so the helper packet no longer stops at notify-prepare bookkeeping even though it still stays entirely below transport-backed lifecycle work.
- the ring lane still stays below transport-backed work: the blocked `phase10-ring-lab-driver-bridge` remains owned by the adjacent MMIO packet, so this survey does not claim queue discovery, IRQ acknowledgement, queue reset execution, DMA paths, or probe/remove lifecycle behavior.
- shared Phase 10 reminder surfaces still frame `Documentation/zigux/phase10-virtio-ring-slice.md` as a packet-local gap, so this note should keep the landed direct helper, verify, checker, and replay surfaces explicit without promoting that slice-note companion as directly re-read evidence before a fresh current-`master` reread says otherwise.

## Recorded gaps

Fresh repo inspection supports these narrower conclusions:
- the landed `phase10-build-gate`
- the landed `phase10-virtio-core-lab-starter`
- the landed `phase10-virtio-ring-survey-gate`
- the landed `phase10-virtio-ring-survey-note`
- the landed `phase10-virtqueue-shape-helper`
- the landed `phase10-used-buffer-polling-helper`
- the landed `phase10-callback-enable-helper`
- the landed `phase10-callback-delay-helper`
- the landed `phase10-notify-prepare-helper`
- the landed `phase10-notification-data-summary-helper`
- the landed `phase10-broken-queue-poll-guard`
- the landed `phase10-queue-reset-helper`
- the landed `phase10-queue-reset-readiness-helper`
- the landed `phase10-ring-verify-replay`
- the packet-local slice-note companion `Documentation/zigux/phase10-virtio-ring-slice.md` remains framed as a repo-reality gap by the shared closure packet and lane note until it is reread successfully again on current `master`
- the still-blocked `phase10-ring-lab-driver-bridge`

That keeps the ring lane concrete and reviewable without overstating progress: the current packet already owns real queue-local virtqueue wrapper evidence on the helper, verify, checker, survey-gate, and shared-build surfaces, including the landed notification-data summary helper, the next same-lane follow-through is now the packet-local slice-note truthfulness gap rather than another queue-wrapper rung, and the blocked MMIO-owned bridge remains explicit.

## Freeze boundary
- `Documentation/zigux/freeze-map.md` is the governing boundary note for this queue-local survey packet.
- freeze-boundary owner: `P10-L10`
- rollback owner: keep this survey note, `zigux/tests/phase10_virtio_ring_manifest.json`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, and `Documentation/zigux/freeze-map.md` aligned before widening this queue-local note.
- this ring survey stays inside `drivers/virtio/*.zig`; it does not reopen `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, which remain Phase 14 study-only anchors under the freeze map.
- the Phase 15 freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c` also remain outside this lane; this survey does not claim scheduler, MM, RCU, or skbuff ownership, parity, or Architecture Council reopen authority.
- the allowed evidence here is the current manifest, this survey note, the shared closure packet, the shared lane note, the shared tests-root review companion, the shared scripts-root summary, the freeze-map boundary note, and live repo readback; this survey does not claim a freeze-map status change or an attached Architecture Council reopen request.

## Non-goals
This survey slice does not claim:
- real split-ring or packed-ring transport parity beyond the bounded in-memory wrapper packet
- DMA mapping or unmapping wrappers
- transport-backed queue discovery, IRQ acknowledgement, queue reset execution, or probe/remove lifecycle behavior
- a reopened Architecture Council decision

## Gates
Current `master` keeps this ring lane reviewable through the bounded helper packet:
1. rerun the dedicated ring checker
- `python3 scripts/zigux/check-phase10-ring-packet.py --self-test`
- `python3 scripts/zigux/check-phase10-ring-packet.py`
2. rerun the dedicated ring survey gate
- `zig test zigux/tests/phase10_virtio_ring_survey.zig`
3. rerun the shared Phase 10 build and Linux-style make routes when focused readback remains aligned
- `zig build test --build-file zigux/tests/phase10_build.zig`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Do not claim a transport-backed Phase 10 ring compile or lifecycle replay from this survey until the MMIO-owned bridge itself changes.

## Next bounded step
Keep the broader Phase 10 virtio lane parked unless fresh repo inspection finds one directly coupled same-lane follow-through. Inside this ring lane, the next honest bounded step is to keep `zigux/tests/phase10_virtio_ring_manifest.json`, this survey note, and `scripts/zigux/check-phase10-ring-packet.py` aligned around the now-landed `phase10-notification-data-summary-helper` while keeping `Documentation/zigux/phase10-virtio-ring-slice.md` framed as a repo-reality gap and keeping the MMIO-owned transport bridge blocked.
