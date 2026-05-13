# Phase 10 Virtio Input Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_input.c`.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-input-survey`
- `PHASE10_LANE_KEY=P10-L13`
- `PHASE10_SURVEYED_COMMIT=7361ac51374149a96b7a7a2c6ea3c995d8cc1231`
- scope: keep the current `virtio_input` packet fail-closed against live current-`master` rereads now that only part of the direct helper-facing packet is visible on the public tree while risky transport remains blocked

## Why this slice exists

The Phase 10 roadmap still names `drivers/virtio/virtio_input.c` as a VM-friendly lab-driver anchor.

This survey exists to keep that lane truthful and reviewable. Fresh current-`master` rereads now show the direct helper trio plus two focused replays, but not the dedicated checker or the broader replay bundle that older reminder surfaces still described. That means the note should keep the landed helper-local packet explicit while recording the still-missing checker, wider replay bundle, and slice companions as repo-reality gaps instead of treating them as current shipped evidence.

## Survey findings

- `drivers/virtio/virtio_input.c` is still the Phase 10 anchor at 421 lines and still mixes config-space reads, queue setup, status sends, event handling, registration, freeze or restore hooks, and teardown paths.
- fresh public-tree rereads materialize `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input_manifest.json`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, and `zigux/tests/phase10_virtio_input_teardown_observation.zig` on current `master`.
- the same public-tree rereads do not currently materialize `scripts/zigux/check-phase10-input-packet.py`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, `Documentation/zigux/phase10-virtio-input-slice.md`, or `Documentation/zigux/phase10-virtio-input-module-slice.md` on current `master`.
- `zigux/tests/phase10_virtio_input_teardown_observation.zig` still keeps one bounded teardown foothold explicit: identity survives reset while queue, readiness, capability, multitouch, and queued-status state are observed as resettable runtime state rather than full transport-backed remove, freeze, or restore parity.
- the broader roadmap gap is unchanged: real event delivery, `input_register_device()` lifecycle coverage, transport-backed queue callbacks, and freeze, restore, remove, or reset parity remain out of scope.

## Recorded gaps

The reminder manifest now records:

- landed `phase10-virtio-input-reminder-manifest`
- landed `phase10-virtio-input-survey-note`
- landed `phase10-virtio-input-helper-trio`
- landed `phase10-virtio-input-registration-and-teardown-replays`
- repo-reality gap `phase10-virtio-input-packet-checker-and-broader-replays`
- repo-reality gap `phase10-virtio-input-slice-companions`
- still-blocked `phase10-virtio-input-registration-lifecycle`

That means the honest same-lane follow-through is not to claim the whole direct packet is visible again. The current job is to keep the survey note and paired manifest aligned around the landed helper trio plus the registration-preflight and teardown-observation replays while the checker, broader replay bundle, and slice companions remain absent and risky transport stays blocked.

## Non-goals

This survey slice does not claim:

- real event delivery or `input_register_device()` parity
- transport-backed queue callback execution beyond the bounded registration-preflight and teardown-facing packet
- transport-backed freeze, restore, remove, or reset parity
- the dedicated checker or broader replay bundle on current `master`
- packet-local slice-note companions on current `master`
- any freeze-map status change or Architecture Council reopen attachment

## Gates

Keep this lane reviewable by rereading:

1. `Documentation/zigux/phase10-virtio-input-survey.md`
2. `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
3. `zigux/tests/phase10_virtio_input_manifest.json`
4. `drivers/virtio/virtio_input.zig`
5. `drivers/virtio/virtio_input_probe_preflight.zig`
6. `drivers/virtio/virtio_input_verify.zig`
7. `zigux/tests/phase10_virtio_input_registration_preflight.zig`
8. `zigux/tests/phase10_virtio_input_teardown_observation.zig`

Keep the dedicated checker, broader replay bundle, and slice companions framed as repo-reality gaps until those files actually materialize on current `master`.

## Next bounded step

Keep the Phase 10 `virtio_input` lane narrow. If a fresh repo-first reread still finds drift, the next honest same-lane move is one bounded reminder, manifest, survey, or owner-map sync that stops claiming `scripts/zigux/check-phase10-input-packet.py` or the missing broader replay bundle are already present on current `master`. Otherwise keep the lane parked below registration-lifecycle and other risky transport work.
