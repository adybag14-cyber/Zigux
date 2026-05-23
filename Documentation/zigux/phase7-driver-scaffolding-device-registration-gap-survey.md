# Phase 7 Driver Scaffolding And Device Registration Gap Survey

This document records the bounded Phase 7 survey lane for the helper-to-driver handoff gap between the roadmap's in-kernel leaf-helper work and the later driver phases that already carry queue-registration or `register_device` scaffolding on current `master`.

## Status

- `PHASE7_STATUS=survey_packet_landed`
- `PHASE7_SLICE=driver-scaffolding-device-registration-gap-survey`
- `PHASE7_LANE_KEY=P7-L01`
- scope: keep this lane limited to surveying the current Phase 7 helper packet against directly readable later-phase driver registration evidence without widening into shared-control ownership or new driver implementation work
- current survey packet:
  - `Documentation/zigux/phase7-driver-scaffolding-device-registration-gap-survey.md`
  - `zigux/tests/phase7_driver_scaffolding_gap_manifest.json`
  - `zigux/tests/phase7_driver_scaffolding_gap_survey.zig`
- current helper-side provenance:
  - `Documentation/zigux/phase7-cmdline-slice.md`
  - `zigux/tests/phase7_cmdline_manifest.json`
  - `samples/zigux/README.md`
- current driver-side evidence:
  - `drivers/virtio/virtio.zig`
  - `drivers/virtio/virtio_input.zig`
  - `drivers/watchdog/gpio_wdt.zig`

## Why This Survey Exists

The roadmap puts Phase 7 on reusable runtime leaf helpers such as `lib/cmdline.c`, while later phases move into virtio and simple production drivers. Phase 7 is still a helper-only leaf phase in the roadmap.

Current `master` already shows that later driver lanes talk openly about registration staging:

- `drivers/virtio/virtio.zig` exposes `queue_registration_ready` and `DriverModelStage.queue_registration_ready`
- `drivers/virtio/virtio_input.zig` exposes `RegistrationPreflightSummary` and `ready_for_registration`
- `drivers/watchdog/gpio_wdt.zig` exposes `registerDeviceCallSummary`, `register_device_requested`, and the explicit `devm_watchdog_register_device` handoff

What Phase 7 did not yet record clearly enough was the handoff boundary itself: the current helper-local `cmdline` packet is a prerequisite for later driver configuration and registration flows, but it is not itself driver scaffolding, queue registration, or device-registration delivery.

This survey closes that repo-truth gap without inventing new driver code.

## Survey Findings

1. The current Phase 7 `cmdline` packet remains helper-local.

- `Documentation/zigux/phase7-cmdline-slice.md` still frames Phase 7 around exact option parsing, argument splitting, and memory parsing.
- `zigux/tests/phase7_cmdline_manifest.json` still lists only helper-local surfaces and no driver-root ownership.
- `samples/zigux/README.md` still lists `*cmdline*` among the no-extra-sample reminders.

2. Later driver phases already carry concrete registration vocabulary.

- `drivers/virtio/virtio.zig` keeps staged driver readiness explicit through `queue_registration_ready` and `DriverModelStage.queue_registration_ready`.
- `drivers/virtio/virtio_input.zig` keeps registration blocking and release criteria explicit through `RegistrationPreflightSummary`, `RegistrationBlocker`, and `ready_for_registration`.
- `drivers/watchdog/gpio_wdt.zig` keeps the platform-driver handoff explicit through `RegistrationPlanSummary`, `RegisterDeviceCallSummary`, `register_device_requested`, and `devm_watchdog_register_device`.

3. The real bounded gap is survey truthfulness, not missing helper code.

- Phase 7 already has the `cmdline` helper packet on `master`.
- Later driver lanes already have bounded lab or production-facing registration scaffolding on `master`.
- The missing connective tissue was a repo-local survey note that tells future scheduled runs not to mistake Phase 7 helper reviewability for driver registration progress.

## Boundaries

This lane does not claim:

- ownership of the existing helper-local `cmdline` packet under `P7-L08`
- shared Makefile, workflow, or validator follow-through owned by the Phase 7 shared-control lanes
- any new driver implementation under `drivers/virtio/*.zig`, `drivers/watchdog/*.zig`, or other driver roots
- that Phase 7 itself should absorb queue registration or `register_device` delivery

## Next Bounded Step

Keep this lane limited to survey truthfulness. If the current repo later changes the helper-to-driver handoff vocabulary, update only this survey packet and its manifest-backed check so scheduled runs keep the Phase 7 helper scope separate from the later driver registration lanes.