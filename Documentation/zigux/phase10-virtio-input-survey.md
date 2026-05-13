# Phase 10 Virtio Input Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_input.c`.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-input-survey`
- `PHASE10_LANE_KEY=P10-L13`
- `PHASE10_SURVEYED_COMMIT=7361ac51374149a96b7a7a2c6ea3c995d8cc1231`
- scope: keep the current `virtio_input` packet fail-closed against live current-`master` rereads now that the broader direct helper-facing packet is visible again through public-tree fallback while risky transport remains blocked

## Why this slice exists

The Phase 10 roadmap still names `drivers/virtio/virtio_input.c` as a VM-friendly lab-driver anchor.

This survey exists to keep that lane truthful and reviewable. Fresh current-`master` rereads now show that the wider direct helper-facing packet is visible again through public-tree fallback, even though some authenticated contents reads still return `404` for those same paths. That means the note should keep the direct helper, verify, checker, and focused replay surfaces explicit without widening into registration-lifecycle or transport-backed claims.

## Survey findings

- `drivers/virtio/virtio_input.c` is still the Phase 10 anchor at 421 lines and still mixes config-space reads, queue setup, status sends, event handling, registration, freeze or restore hooks, and teardown paths.
- fresh public-tree rereads now materialize `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_verify.zig`, `scripts/zigux/check-phase10-input-packet.py`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, and `zigux/tests/phase10_virtio_input_survey.zig` on current `master`, so the lane no longer needs to describe the broader direct input packet as missing repo reality.
- `zigux/tests/phase10_virtio_input_teardown_observation.zig` still keeps one bounded teardown foothold explicit: identity survives reset while queue, readiness, capability, multitouch, and queued-status state are observed as resettable runtime state rather than full transport-backed remove, freeze, or restore parity.
- the authenticated contents bridge can still return `404` for some of those direct input paths, so shared reminder surfaces should keep the public-tree fallback evidence explicit instead of treating those transient bridge misses as repo-reality gaps.
- `Documentation/zigux/phase10-virtio-input-slice.md` and `Documentation/zigux/phase10-virtio-input-module-slice.md` remain the packet-local repo-reality gaps on current `master`.
- the broader roadmap gap is unchanged: real event delivery, `input_register_device()` lifecycle coverage, transport-backed queue callbacks, and freeze, restore, remove, or reset parity remain out of scope.

## Recorded gaps

The reminder manifest now records:

- landed `phase10-virtio-input-reminder-manifest`
- landed `phase10-virtio-input-survey-note`
- landed `phase10-virtio-input-direct-packet-restore`
- landed `phase10-virtio-input-teardown-observation-replay`
- repo-reality gap `phase10-virtio-input-slice-companions`
- still-blocked `phase10-virtio-input-registration-lifecycle`

That means the honest same-lane follow-through is no longer another restore claim for the direct input helper, checker, or focused replay packet. The current job is to keep the shared reminder surfaces, the dedicated survey note, and the paired manifest aligned around the now-public direct packet while the packet-local slice companions stay absent and risky transport work remains blocked.

## Non-goals

This survey slice does not claim:

- real event delivery or `input_register_device()` parity
- transport-backed queue callback execution beyond the bounded preflight and teardown-facing packet
- transport-backed freeze, restore, remove, or reset parity
- packet-local slice-note companions on current `master`
- any freeze-map status change or Architecture Council reopen attachment

## Gates

Keep this lane reviewable by rereading:

1. `Documentation/zigux/phase10-virtio-input-survey.md`
2. `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
3. `zigux/tests/phase10_virtio_input_manifest.json`
4. `drivers/virtio/virtio_input.zig`
5. `drivers/virtio/virtio_input_verify.zig`
6. `scripts/zigux/check-phase10-input-packet.py`
7. `zigux/tests/phase10_virtio_input_probe_preflight.zig`
8. `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`
9. `zigux/tests/phase10_virtio_input_registration_preflight.zig`
10. `zigux/tests/phase10_virtio_input_status_drain.zig`
11. `zigux/tests/phase10_virtio_input_teardown_observation.zig`
12. `zigux/tests/phase10_virtio_input_survey.zig`

Use the shared Phase 10 docs-root, scripts-root, tests-root, and closure-manifest packet to keep that direct input helper, verify, checker, and focused replay bundle explicit, but keep `Documentation/zigux/phase10-virtio-input-slice.md` and `Documentation/zigux/phase10-virtio-input-module-slice.md` framed as repo-reality gaps until those note files land.

## Next bounded step

Keep the Phase 10 `virtio_input` lane narrow. The next honest same-lane move is one bounded reminder, manifest, survey, or checker sync if a fresh repo-first reread finds new drift across `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, or the direct helper-facing input packet. Otherwise keep the lane parked below registration-lifecycle and other risky transport work.
