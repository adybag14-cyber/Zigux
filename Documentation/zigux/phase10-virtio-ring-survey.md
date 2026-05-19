# Phase 10 Virtio Ring Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_ring.c`.

## Status
- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-ring-survey`
- lane: `P10-L05`
- surveyed commit: `0aa2db32bcb1c7065850ee3f66ec119b071fbf5c`
- roadmap destinations: `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`
- scope: keep the ring manifest, this survey note, the packet-local slice note, and one bounded truthfulness or validation follow-through aligned with the current queue-local ring packet on `master`
- product boundary:
  - `zigux/tests/phase10_virtio_ring_manifest.json`
  - `Documentation/zigux/phase10-virtio-ring-slice.md`
  - `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`
  - `Documentation/zigux/phase10-virtio-ring-survey.md`
  - `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
  - `Documentation/zigux/phase10-closure-evidence.md`
  - `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
  - `Documentation/zigux/freeze-map.md`
  - `scripts/zigux/README.md`
  - `scripts/zigux/check-phase10-ring-packet.py`
  - `zigux/tests/phase10_build.zig`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_ring.c` as a primary anchor and asks Zigux to prove queue-local virtqueue wrappers up to the lab-driver threshold before widening into transport-backed lifecycle work.

Fresh repo-first inspection against the live Phase 10 manifest plus the shared closure packet, lane note, tests-root review companion, scripts-root summary, and ring freeze-boundary note shows the ring packet now has a mixed but directly reviewable posture on current `master`: direct contents reads rematerialize `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, the focused queue-local replays `zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`, `zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig`, and `zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`, plus the dedicated survey replay `zigux/tests/phase10_virtio_ring_survey.zig`, while the broader replay `zigux/tests/phase10_virtio_ring.zig` still does not materialize on current `master`.

This survey therefore exists to keep the directly re-readable ring packet truthful and reviewable while the transport-backed bridge stays blocked. The directly re-readable ring packet surfaces on current `master` now include `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`, `zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig`, `zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `scripts/zigux/check-phase10-ring-packet.py`, `zigux/tests/phase10_build.zig`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, and `zigux/tests/phase10_virtio_ring_manifest.json`.

## Survey findings
- `drivers/virtio/virtio_ring.c` remains the Linux anchor for this lane, and `zigux/tests/phase10_virtio_ring_manifest.json` now records `0aa2db32bcb1c7065850ee3f66ec119b071fbf5c` as the surveyed Phase 10 ring snapshot.
- the shared Phase 10 packet still keeps the ring survey note, the ring slice note, the ring freeze-boundary survey, the ring manifest, the shared closure packet, the shared lane note, the shared tests-root review companion, the dedicated ring checker, and the shared build gate explicit on current `master`.
- the live packet now records the direct repo reality honestly: the queue-local ring helper ladder, the wrapper-facing verify replay, the focused notification-data, prepare-kick, reset-reuse, broken-queue, and delayed-callback replays, and the dedicated survey replay are directly readable on current `master`, while the broader replay `zigux/tests/phase10_virtio_ring.zig` remains a direct-readback gap.
- the queue-local helper ladder still matters as bounded ring-lane vocabulary: `phase10-virtqueue-shape-helper`, `phase10-used-buffer-polling-helper`, `phase10-callback-enable-helper`, `phase10-callback-delay-helper`, `phase10-notify-prepare-helper`, `phase10-notification-data-summary-helper`, `phase10-broken-queue-poll-guard`, `phase10-queue-reset-helper`, and `phase10-queue-reset-readiness-helper` remain the reviewable helper targets that the restored ring helper now carries.
- `Documentation/zigux/phase10-virtio-ring-slice.md` now carries that vocabulary in one packet-local note while keeping the focused replays and the dedicated survey replay explicit current-head evidence without promoting the missing broader replay.
- `zigux/tests/phase10_virtio_ring_survey.zig` now gives the ring lane one dedicated VM-friendly survey replay that keeps the survey note, manifest, slice note, freeze-boundary note, and build gate aligned without widening into transport-backed execution claims.
- the ring lane still stays below transport-backed work: the blocked `phase10-ring-lab-driver-bridge` remains owned by the adjacent `P10-L11` MMIO packet, so this survey does not claim transport-backed queue discovery, IRQ acknowledgement, queue reset execution, DMA paths, or probe/remove lifecycle behavior.

## Recorded gaps

Fresh repo inspection supports these narrower conclusions:
- the landed `phase10-build-gate`
- the landed `phase10-virtio-core-lab-starter` as neighboring Phase 10 evidence, not ring-owned delivery
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
- the landed `phase10-virtio-ring-slice-note`
- the still-missing broader replay `zigux/tests/phase10_virtio_ring.zig`
- the still-blocked `phase10-ring-lab-driver-bridge`

That keeps the ring lane concrete and reviewable without overstating progress: the packet treats the dedicated survey replay, the restored helper, the wrapper-facing verify replay, and the focused replays as current repo reality while keeping the MMIO-owned transport bridge and the broader ring replay outside this bounded packet. The next same-lane follow-through should stay inside one ring-only reminder-surface, checker, or manifest truthfulness repair rather than widening into risky transport work.

## Freeze boundary
- `Documentation/zigux/freeze-map.md` is the governing boundary note for this queue-local survey packet.
- freeze-boundary owner: `P10-L11`
- rollback owner: keep this survey note, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, and `Documentation/zigux/freeze-map.md` aligned before widening this queue-local note.
- this ring survey stays inside `drivers/virtio/*.zig`; it does not reopen `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, which remain Phase 14 study-only anchors under the freeze map.
- the Phase 15 freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c` also remain outside this lane; this survey does not claim scheduler, MM, RCU, or skbuff ownership, parity, or Architecture Council reopen authority.
- the allowed evidence here is the current manifest, this survey note, the ring slice note, the ring freeze-boundary survey, the dedicated ring survey replay, the shared build gate, the dedicated ring checker, the shared closure packet, the shared lane note, the shared tests-root review companion, the shared scripts-root summary, the freeze-map boundary note, and live repo readback; this survey does not claim a freeze-map status change or an attached Architecture Council reopen request.

## Non-goals
This survey slice does not claim:
- real split-ring or packed-ring transport parity beyond the bounded ring packet vocabulary
- DMA mapping or unmapping wrappers
- transport-backed queue discovery, IRQ acknowledgement, queue reset execution, or probe/remove lifecycle behavior
- a reopened Architecture Council decision

Do not reopen MMIO helper growth, DMA, interrupt delivery, queue discovery, reset execution, or probe/remove lifecycle work from this note.

## Gates
Current `master` keeps this ring lane reviewable through the bounded packet:
1. rerun the dedicated ring survey replay and the dedicated ring checker when focused readback remains aligned
- `zig test zigux/tests/phase10_virtio_ring_survey.zig`
- `python3 scripts/zigux/check-phase10-ring-packet.py --self-test`
- `python3 scripts/zigux/check-phase10-ring-packet.py`
2. rerun the shared Phase 10 build and Linux-style make routes when focused readback remains aligned
- `zig build test --build-file zigux/tests/phase10_build.zig`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Do not claim a transport-backed Phase 10 ring compile or lifecycle replay from this survey until the MMIO-owned bridge itself changes.

## Next bounded step
Keep the broader Phase 10 virtio lane parked unless fresh repo inspection finds one directly coupled same-lane follow-through. Inside this ring lane, the next honest bounded step is to keep `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, this survey note, `zigux/tests/phase10_virtio_ring_survey.zig`, and `scripts/zigux/check-phase10-ring-packet.py` aligned around the focused replays and the landed survey replay while keeping the missing broader replay and the MMIO-owned bridge framed as the remaining out-of-scope gaps on current `master`.
