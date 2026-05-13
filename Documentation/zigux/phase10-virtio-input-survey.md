# Phase 10 Virtio Input Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_input.c`.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-input-survey`
- `PHASE10_LANE_KEY=P10-L13`
- `PHASE10_SURVEYED_COMMIT=7361ac51374149a96b7a7a2c6ea3c995d8cc1231`
- scope: keep the current `virtio_input` reminder packet fail-closed against live current-`master` readback instead of repeating the older restored-direct-packet story after the direct helper-facing and checker-facing surfaces dropped back out of the public tree

## Why this slice exists

The Phase 10 roadmap still names `drivers/virtio/virtio_input.c` as a VM-friendly lab-driver anchor.

This survey exists to keep that lane truthful and reviewable. Fresh current-`master` rereads show that the wider direct helper-facing packet is not directly readable right now, so the note has to stay anchored to the manifest-backed reminder packet that is still present and to the one directly readable teardown replay that remains in tree.

## Survey findings

- `drivers/virtio/virtio_input.c` is still the Phase 10 anchor at 421 lines and still mixes config-space reads, queue setup, status sends, event handling, registration, freeze or restore hooks, and teardown paths.
- fresh current-`master` reads now return 404 for `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_verify.zig`, `scripts/zigux/check-phase10-input-packet.py`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, and `zigux/tests/phase10_virtio_input_survey.zig`, so the lane cannot currently describe the direct helper and dedicated checker packet as restored current-`master` evidence.
- `zigux/tests/phase10_virtio_input_teardown_observation.zig` still keeps one bounded teardown foothold explicit: identity survives reset while queue, readiness, capability, multitouch, and queued-status state are observed as resettable runtime state rather than full transport-backed remove, freeze, or restore parity.
- `Documentation/zigux/phase10-virtio-input-slice.md` and `Documentation/zigux/phase10-virtio-input-module-slice.md` also remain repo-reality gaps on current `master`.
- the directly readable input-lane packet on current `master` is therefore limited to this survey note, the paired manifest, the shared lane-sequencing note, and `zigux/tests/phase10_virtio_input_teardown_observation.zig`.
- the broader roadmap gap is unchanged: real event delivery, `input_register_device()` lifecycle coverage, transport-backed queue callbacks, and freeze, restore, remove, or reset parity remain out of scope.

## Recorded gaps

The reminder manifest now records:

- landed `phase10-virtio-input-reminder-manifest`
- landed `phase10-virtio-input-survey-note`
- landed `phase10-virtio-input-teardown-observation-replay`
- repo-reality gap `phase10-virtio-input-direct-packet-restore`
- still-blocked `phase10-virtio-input-registration-lifecycle`

That means the honest same-lane follow-through is no longer another claim that `drivers/virtio/virtio_input.zig`, `scripts/zigux/check-phase10-input-packet.py`, or `zigux/tests/phase10_virtio_input_registration_preflight.zig` are already back on `master`. The current job is to keep the shared reminder surfaces aligned with the manifest-backed reminder packet while those direct helper, checker, replay, and slice-note paths remain absent.

When the wider direct packet is eventually restored, reintroduce dedicated checker and replay commands only after those paths are present again on current `master`.

## Non-goals

This survey slice does not claim:

- real event delivery or `input_register_device()` parity
- transport-backed queue callback execution beyond the bounded teardown-facing reminder packet
- transport-backed freeze, restore, remove, or reset parity
- packet-local slice-note companions on current `master`
- any freeze-map status change or Architecture Council reopen attachment

## Gates

Keep this lane reviewable by directly rereading:

1. `Documentation/zigux/phase10-virtio-input-survey.md`
2. `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
3. `zigux/tests/phase10_virtio_input_manifest.json`
4. `zigux/tests/phase10_virtio_input_teardown_observation.zig`

Use the shared Phase 10 docs-root, scripts-root, tests-root, and closure-manifest packet to keep the bounded teardown reminder explicit, but keep `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_verify.zig`, `scripts/zigux/check-phase10-input-packet.py`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, and `Documentation/zigux/phase10-virtio-input-slice.md` framed as repo-reality gaps until those files themselves land again.

## Next bounded step

Keep the Phase 10 `virtio_input` lane narrow. The next honest same-lane move is one shared reminder sync so `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-closure-evidence.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` stop presenting the missing direct input helper, checker, and focused replay paths as shipped current-`master` evidence while registration-lifecycle and other risky transport work remain blocked.
