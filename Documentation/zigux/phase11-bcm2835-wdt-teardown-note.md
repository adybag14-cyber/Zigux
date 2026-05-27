# Phase 11 BCM2835 Watchdog Teardown Note

This note keeps the teardown-facing checkpoint for the bounded Phase 11
`bcm2835_wdt` packet truthful on current `master`. It stays inside the
simple-drivers lane and records the returned driver-plus-docs-plus-proof
surfaces that already describe the host-free teardown and ownership packet.

## Status

- `PHASE11_BCM2835_WDT_TEARDOWN_STATUS=teardown_driver_docs_and_proof_packet`
- teardown evidence remains bounded to the returned bcm2835 driver, direct
  proofs, dedicated replay routes, manifest-backed closure, and coupled docs
  packet
- remaining follow-through is still wider slice recovery, live platform
  registration, watchdog-core registration, shared poweroff-handler
  installation, remove-time callback release, reboot-backed teardown
  execution, and hardware-backed validation

## Teardown Packet

The current teardown-facing bcm2835 packet on `master` is:

- `drivers/watchdog/bcm2835_wdt.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `zigux/tests/phase11_bcm2835_wdt.zig`
- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`
- `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`
- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`
- `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`

These returned driver, driver-backed verify helper, focused replay, dedicated
replay route, manifest-backed closure, and documentation surfaces keep the
teardown packet readable without promoting the absent wider slice file into
current-head evidence.

## What The Landed Teardown Packet Covers

The current host-free teardown review packet keeps these handoffs explicit:

- `summarizeTeardown()` and the bounded nowayout-versus-stop split it records
- `Bcm2835WdtLab.stop()` and the direct stop snapshot it keeps explicit before
  any live remove-hook execution claim
- `drivers/watchdog/bcm2835_wdt_verify.zig` as the driver-backed verify helper
  that keeps `summarizePlatformHandoff()`, the claimed-versus-conflict poweroff
  split, `Bcm2835WdtLab.stop()`, `poweroff()`, and `summarizeTeardown()`
  replayable beside the direct proofs without claiming live PM-base wiring,
  live watchdog-core registration, live callback installation, or live remove
  execution
- `zigux/tests/phase11_bcm2835_wdt.zig` as the focused tests-root replay that
  keeps timeout constants, PM-base readiness, restart proof, stop proof,
  poweroff ownership, and teardown ownership explicit together instead of
  leaving the packet implied
- `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig` and
  `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig` as the
  dedicated reminder-packet route that keeps the coupled survey, validation
  plan, teardown note, and validation matrix aligned on their own bounded
  replay path
- `summarizePlatformHandoff()` as the bounded PM-base and registration-precheck
  anchor before any later live platform-registration claim
- the claimed poweroff path as the explicit owner-preserving handoff where
  halt-partition programming, restart ticks, and reset arming remain reviewable
  without claiming real board-backed execution
- the foreign-owner and non-controller teardown splits as the direct reminder
  that callback release still stays blocked unless the bounded owner and system
  power-controller conditions are satisfied
- `blocked_on_live_remove_callback` as the standing reminder that the returned
  packet stops at helper-level teardown truthfulness and does not claim a live
  platform remove hook yet
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` as the
  companion surface that keeps the current compile, failure-mode, and teardown
  review packet explicit without widening into broader platform behavior

The returned driver-backed packet and verify helper also keep timeout windows,
restart constants, PM-base readiness, claimed-versus-conflict poweroff
ownership, stop-transition snapshots, and teardown ownership boundaries visible
without claiming live `devm_watchdog_register_device()` execution, live
`watchdog_stop_on_reboot()` execution, live `pm_power_off` installation,
live remove-time callback release, or host-backed shutdown behavior.

## Bounded Meaning

This note records the returned teardown summaries, direct proofs, manifest, and
dedicated replay route only. It does not claim live platform registration,
`devm_watchdog_register_device()` execution, `watchdog_stop_on_reboot()`
execution, `pm_power_off` installation, remove-time callback release,
reboot-backed teardown execution, or hardware-validated teardown parity. Those
remain later same-lane follow-through steps rather than part of the
already-landed packet.

## Next Bounded Step

The next honest bcm2835-only follow-through is one platform-registration or
shared callback-ownership proof step that matches the returned driver,
verify-helper, manifest, and validation matrix boundary.
