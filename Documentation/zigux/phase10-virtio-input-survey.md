# Phase 10 Virtio Input Survey

This document records the bounded Phase 10 survey lane around `drivers/virtio/virtio_input.c`.

## Status
- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-input-survey`
- lane: `P10-L13`
- surveyed commit: `7361ac51374149a96b7a7a2c6ea3c995d8cc1231`
- roadmap destinations: `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`
- scope: keep the current `drivers/virtio/virtio_input.zig` helper packet, its queue-handling replays, and the shared Phase 10 build gate reviewable without claiming transport-backed queue execution, input registration lifecycle parity, freeze or restore behavior, or probe/remove closure
- product boundary:
  - `zigux/tests/phase10_virtio_input_manifest.json`
  - `Documentation/zigux/phase10-virtio-input-slice.md`
  - `Documentation/zigux/phase10-virtio-input-module-slice.md`
  - `Documentation/zigux/phase10-virtio-input-survey.md`
  - `Documentation/zigux/phase10-closure-evidence.md`
  - `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
  - `Documentation/zigux/freeze-map.md`
  - `scripts/zigux/check-phase10-input-packet.py`
  - `scripts/zigux/check-phase10-harness-coverage.py`
  - `zigux/tests/phase10_build.zig`
  - `drivers/virtio/virtio_input.zig`
  - `drivers/virtio/virtio_input_probe_preflight.zig`
  - `drivers/virtio/virtio_input_registration_preflight.zig`
  - `drivers/virtio/virtio_input_verify.zig`
  - `zigux/tests/phase10_virtio_input.zig`
  - `zigux/tests/phase10_virtio_input_probe_preflight.zig`
  - `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`
  - `zigux/tests/phase10_virtio_input_registration_preflight.zig`
  - `zigux/tests/phase10_virtio_input_status_drain.zig`
  - `zigux/tests/phase10_virtio_input_teardown_observation.zig`

## Why this slice exists

The Phase 10 roadmap keeps `drivers/virtio/virtio_input.c` inside the VM-friendly lab-driver stage. In that stage, honest progress is bounded helper, queue-handling, and validation work rather than transport-backed lifecycle delivery.

Fresh repo-first inspection against the live Phase 10 manifest, the packet-local slice notes, the shared closure evidence, the shared tests-root companion, and the shared build gate shows that the direct input packet is already present on current `master`: `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, `scripts/zigux/check-phase10-input-packet.py`, and `zigux/tests/phase10_build.zig` remain part of the bounded input lane.

This survey exists to keep that queue-local and registration-preflight packet explicit and reviewable while the broader transport-backed bridge stays parked.

## Survey findings
- `drivers/virtio/virtio_input.c` remains the Linux anchor for this lane, and `zigux/tests/phase10_virtio_input_manifest.json` still records `7361ac51374149a96b7a7a2c6ea3c995d8cc1231` as the surveyed Phase 10 input snapshot.
- the shared Phase 10 packet still keeps the direct input helper packet explicit on current `master`: `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, `scripts/zigux/check-phase10-input-packet.py`, and `zigux/tests/phase10_build.zig` remain the bounded queue-handling review surfaces that pair with this survey note.
- the live manifest keeps the current input lane concrete: the shared build gate, the direct helper foothold, the direct gate, the slice note, the module-facing slice note, the dedicated survey gate, the probe-preflight helper and replay, the queue-callback-preflight helper and replay, the registration-preflight helper and replay, the status-drain helper and replay, the teardown-observation helper and replay, and the wrapper-facing verify replay all remain landed starter evidence.
- the landed queue-handling ladder remains bounded and in-memory: probe staging stays identity-first, queue-callback readiness still sits behind queue configuration and buffer fill, registration staging still stops at blocker reporting below `input_register_device()`, queued status completions are reclaimed only in memory, and teardown review remains reset-local.
- `Documentation/zigux/phase10-virtio-input-slice.md` keeps the direct packet-local ownership story explicit, while `Documentation/zigux/phase10-virtio-input-module-slice.md` keeps the module-facing queue-callback, registration-preflight, status-drain, and teardown-local boundaries explicit in one packet-local companion.
- `zigux/tests/phase10_build.zig` remains part of the shared Phase 10 review packet and currently wires the direct input gate, the probe-preflight replay, the queue-callback-preflight replay, the registration-preflight replay, the status-drain replay, the teardown-observation replay, the wrapper-facing verify replay, and the helper-local MMIO tests into one bounded shared gate.
- the risky transport bridge is still intentionally parked: the live packet does not claim transport-backed queue callbacks, real input registration lifecycle completion, freeze or restore parity, remove lifecycle closure, IRQ parity, or DMA-backed behavior.

## Recorded gaps

Fresh repo inspection supports these narrower conclusions:
- the landed `phase10-build-gate`
- the landed `phase10-virtio-input-lab-helper`
- the landed `phase10-virtio-input-lab-gate`
- the landed `phase10-virtio-input-slice-note`
- the landed `phase10-virtio-input-module-slice-note`
- the landed `phase10-virtio-input-survey-gate`
- the landed `phase10-virtio-input-probe-preflight-helper`
- the landed `phase10-virtio-input-probe-preflight-replay`
- the landed `phase10-virtio-input-queue-callback-preflight-helper`
- the landed `phase10-virtio-input-queue-callback-preflight-replay`
- the landed `phase10-virtio-input-registration-preflight-helper`
- the landed `phase10-virtio-input-registration-preflight-replay`
- the landed `phase10-virtio-input-status-drain-helper`
- the landed `phase10-virtio-input-status-drain-replay`
- the landed `phase10-virtio-input-teardown-observation-helper`
- the landed `phase10-virtio-input-teardown-observation-replay`
- the landed `phase10-virtio-input-verify-replay`
- the still-blocked `phase10-virtio-input-registration-lifecycle`

That keeps the input lane concrete and reviewable without overstating progress: the current packet already owns real queue-local and registration-preflight evidence on the helper, replay, checker, manifest, packet-local slice-note, module-slice-note, survey-gate, and shared-build surfaces, and the next same-lane follow-through should stay inside one input-only checker, manifest, or reminder-surface truthfulness repair rather than widening into risky transport work.

## Freeze boundary
- `Documentation/zigux/freeze-map.md` is the governing boundary note for this input survey packet.
- this survey stays inside `drivers/virtio/*.zig` and shared validation surfaces.
- this survey does not reopen `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, which remain Phase 14 study-only anchors under the freeze map.
- the Phase 15 freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c` also remain outside this lane; this survey does not claim scheduler, MM, RCU, or skbuff ownership, parity, or Architecture Council reopen authority.
- the allowed evidence here is the current manifest, this survey note, the packet-local slice notes, the shared closure packet, the shared tests-root review companion, the freeze-map boundary note, and live repo readback; this survey does not claim a freeze-map status change or an attached Architecture Council reopen request.

## Non-goals
This survey slice does not claim:
- transport-backed queue callbacks or queue reset execution
- real `input_register_device()` lifecycle parity
- freeze, restore, or remove lifecycle closure
- shared IRQ delivery parity
- DMA-facing behavior
- an Architecture Council reopen or a freeze-map status change

Do not reopen MMIO helper growth, IRQ delivery, DMA, freeze or restore behavior, remove lifecycle closure, or transport-backed registration work from this note.

## Gates
Current `master` keeps this input lane reviewable through the bounded helper packet:
1. rerun the dedicated input checker
- `python3 scripts/zigux/check-phase10-input-packet.py --self-test`
- `python3 scripts/zigux/check-phase10-input-packet.py`
2. rerun the shared Phase 10 harness guard
- `python3 scripts/zigux/check-phase10-harness-coverage.py --self-test`
- `python3 scripts/zigux/check-phase10-harness-coverage.py`
3. rerun the shared Phase 10 build and Linux-style make routes when focused readback remains aligned
- `zig build test --build-file zigux/tests/phase10_build.zig`
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Do not claim a transport-backed Phase 10 input compile or lifecycle replay from this survey until the risky transport bridge itself changes.

## Next bounded step
Keep the broader Phase 10 virtio lane parked unless fresh repo inspection finds one directly coupled same-lane follow-through. Inside this input lane, the next honest bounded step is to keep `zigux/tests/phase10_virtio_input_manifest.json`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, this survey note, and the shared Phase 10 reminder surfaces aligned around the landed queue-handling and registration-preflight packet while keeping the risky transport bridge blocked.
