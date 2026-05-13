# Phase 10 Virtio Input Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_input.c`.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-input-survey`
- `PHASE10_LANE_KEY=P10-L13`
- `PHASE10_SURVEYED_COMMIT=7361ac51374149a96b7a7a2c6ea3c995d8cc1231`
- scope: keep the current `virtio_input` lane note aligned with live current-`master` readback instead of repeating the older reminder-only packet story after the direct driver-side and checker-side surfaces reappeared in the public tree

## Why this slice exists

The Phase 10 roadmap still names `drivers/virtio/virtio_input.c` as a VM-friendly lab-driver anchor.

This survey exists to keep that lane truthful and reviewable. Current `master` now exposes the bounded direct driver-side input packet again through the public tree and the shared Phase 10 reminder surfaces, but risky transport work is still blocked. The note therefore needs to record the restored helper-facing packet without widening the tranche into real event delivery, registration-lifecycle parity, or transport-backed freeze, restore, remove, or callback behavior.

## Survey findings

- `drivers/virtio/virtio_input.c` is still the Phase 10 anchor at 421 lines and still mixes config-space reads, queue setup, status sends, event handling, registration, freeze or restore hooks, and teardown paths.
- public-tree fallback now shows `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_verify.zig`, and `scripts/zigux/check-phase10-input-packet.py` on current `master`, so the lane no longer needs to describe the direct helper and dedicated checker packet as fully missing.
- the shared Phase 10 reminder packet in `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, and `zigux/tests/phase10_closure_manifest.json` now keeps `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_manifest.json`, and `zigux/tests/phase10_virtio_input_survey.zig` explicit as the current bounded input-lane replay family.
- `zigux/tests/phase10_virtio_input_teardown_observation.zig` still keeps one bounded teardown-parity foothold explicit: identity survives reset while queue, readiness, capability, multitouch, and queued-status state are observed as resettable runtime state rather than full transport-backed remove, freeze, or restore parity.
- the packet-local slice-note companions `Documentation/zigux/phase10-virtio-input-slice.md` and `Documentation/zigux/phase10-virtio-input-module-slice.md` still remain repo-reality gaps on current `master`.
- the broader roadmap gap is unchanged: real event delivery, `input_register_device()` lifecycle coverage, transport-backed queue callbacks, and freeze, restore, remove, or reset parity remain out of scope.

## Recorded gaps

The truthful current split is now:

- landed `phase10-virtio-input-reminder-manifest`
- landed `phase10-virtio-input-survey-note`
- landed `phase10-virtio-input-teardown-observation-replay`
- restored direct helper, dedicated checker, and bounded replay packet through `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_verify.zig`, `scripts/zigux/check-phase10-input-packet.py`, and the shared tests-root replay family
- repo-reality gaps still limited to `Documentation/zigux/phase10-virtio-input-slice.md` and `Documentation/zigux/phase10-virtio-input-module-slice.md`
- still-blocked `phase10-virtio-input-registration-lifecycle`

That means the older `phase10-virtio-input-direct-packet-restore` reminder is no longer the live repo gap. The direct packet is back; the remaining honest same-lane follow-through is to keep the shared manifest and validator surfaces aligned with that restored packet while leaving risky transport blocked.

## Non-goals

This survey slice does not claim:

- real event delivery or `input_register_device()` parity
- transport-backed queue callback execution beyond the bounded preflight packet
- transport-backed freeze, restore, remove, or reset parity
- packet-local slice-note companions on current `master`
- any freeze-map status change or Architecture Council reopen attachment

## Gates

Keep this lane reviewable by directly rereading:

1. `Documentation/zigux/phase10-virtio-input-survey.md`
2. `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
3. `drivers/virtio/virtio_input.zig`
4. `drivers/virtio/virtio_input_probe_preflight.zig`
5. `drivers/virtio/virtio_input_verify.zig`
6. `scripts/zigux/check-phase10-input-packet.py`
7. `zigux/tests/phase10_virtio_input_manifest.json`
8. `zigux/tests/phase10_virtio_input_teardown_observation.zig`

Use the shared Phase 10 docs-root, scripts-root, tests-root, and closure-manifest packet to keep the focused input replay family explicit, but keep the packet-local slice-note companions framed as gaps until those files themselves land.

## Next bounded step

Keep the Phase 10 `virtio_input` lane narrow. The next honest same-lane move is one bounded manifest or validator sync so `zigux/tests/phase10_virtio_input_manifest.json` and the shared `scripts/zigux/validate-phase10.py` route stop describing the restored direct input packet as missing, while still leaving registration-lifecycle and other risky transport work blocked.
