# Phase 10 Virtio Input Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_input.c`.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-input-survey`
- `PHASE10_LANE_KEY=P10-L13`
- `PHASE10_SURVEYED_COMMIT=7361ac51374149a96b7a7a2c6ea3c995d8cc1231`
- scope: keep the current `virtio_input` reminder packet fail-closed against live current-`master` readback instead of repeating older direct-helper or checker inventories that the repo no longer materializes
- product boundary:
  - `zigux/tests/phase10_virtio_input_manifest.json`
  - `Documentation/zigux/phase10-virtio-input-survey.md`
  - `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
  - `zigux/tests/phase10_virtio_input_teardown_observation.zig`

## Why this slice exists

The Phase 10 roadmap still names `drivers/virtio/virtio_input.c` as a lab-driver anchor, but current `master` no longer exposes the wider direct Zigux input packet that earlier reminder notes described.

This survey now exists to keep the lane truthful and reviewable while that direct packet is missing. It stays fail-closed around what the repo can still read directly today instead of claiming the helper-facing replay, wrapper-facing verify replay, focused probe-preflight, queue-callback-preflight, registration-preflight, status-drain, survey-gate, slice-note, module-slice, or dedicated checker surfaces as landed evidence.

## Survey findings

- `drivers/virtio/virtio_input.c` is still the Phase 10 anchor at 421 lines and still mixes config-space reads, queue setup, status sends, event handling, registration, freeze or restore hooks, and teardown paths.
- fresh current-`master` rereads still return `404` for `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_verify.zig`, `scripts/zigux/check-phase10-input-packet.py`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, `Documentation/zigux/phase10-virtio-input-slice.md`, and `Documentation/zigux/phase10-virtio-input-module-slice.md`.
- the directly readable input-lane packet on current `master` is therefore limited to this survey note, the paired manifest, the shared lane-sequencing note, and `zigux/tests/phase10_virtio_input_teardown_observation.zig`.
- `zigux/tests/phase10_virtio_input_teardown_observation.zig` still keeps one bounded teardown-parity foothold explicit: identity survives reset while queue, readiness, capability, multitouch, and queued-status state are observed as resettable runtime state rather than full transport-backed remove, freeze, or restore parity.
- the broader roadmap gap is unchanged: real event delivery, `input_register_device()` lifecycle coverage, transport-backed queue callbacks, and freeze, restore, remove, or reset parity remain out of scope.

## Recorded gaps

The reminder manifest now records:

- the landed `phase10-virtio-input-reminder-manifest`
- the landed `phase10-virtio-input-survey-note`
- the landed `phase10-virtio-input-teardown-observation-replay`
- the current `repo_reality_gap` at `phase10-virtio-input-direct-packet-restore`
- the still-blocked `phase10-virtio-input-registration-lifecycle`

This keeps the lane concrete without overstating repo state: current `master` still preserves one direct teardown-observation replay and the reminder packet around it, while the wider direct helper, checker, and focused replay surfaces remain missing and risky transport work remains blocked.

## Non-goals

This survey slice does not claim:

- a landed `drivers/virtio/virtio_input.zig` helper
- a landed `drivers/virtio/virtio_input_verify.zig` replay
- dedicated probe-preflight, queue-callback-preflight, registration-preflight, status-drain, or survey-gate replays on current `master`
- packet-local slice-note companions on current `master`
- real event delivery, `input_register_device()` parity, or transport-backed freeze, restore, remove, or callback behavior

## Gates

Keep this lane reviewable by directly rereading:

1. `zigux/tests/phase10_virtio_input_manifest.json`
2. `Documentation/zigux/phase10-virtio-input-survey.md`
3. `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
4. `zigux/tests/phase10_virtio_input_teardown_observation.zig`

When the wider direct packet is eventually restored, reintroduce dedicated checker and replay commands only after those paths are present again on current `master`.

## Next bounded step

Keep the Phase 10 `virtio_input` lane narrow. The next honest same-lane move is either one bounded restore step for a missing direct input packet surface or one more reminder-packet truthfulness repair that stays below registration-lifecycle and transport-backed work.
