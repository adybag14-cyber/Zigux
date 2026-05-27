# Phase 11 BCM2835 Watchdog Validation Matrix

This document records the bounded bcm2835 watchdog validation matrix for the
current Zigux Phase 11 packet.

## Status

- `PHASE11_BCM2835_WDT_STATUS=driver_proof_and_matrix_packet_truthful`
- archival packet identity: `P11-L08`
- current scheduled continuity for this archival bcm2835 packet is tracked
  through `P11-L10`
- reviewed against live `master`
- scope: keep the current bcm2835 watchdog compile, PM-base gating, poweroff
  ownership, verify-helper packet, manifest-backed closure, and reminder packet
  honest without widening into live platform registration, PM-base execution,
  watchdog-core registration, shared poweroff-handler installation, remove-time
  callback release, or hardware-backed validation

## Current Repo Reality

The current bcm2835 matrix packet on `master` is:

- `drivers/watchdog/bcm2835_wdt.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `zigux/tests/phase11_bcm2835_wdt.zig`
- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`
- `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`

The older wider replay and reminder surfaces
`Documentation/zigux/phase11-bcm2835-wdt-slice.md` and
`Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md` are not part of the
current `master` packet, so this matrix keeps the lane grounded on the returned
driver, verify helper, manifest, focused tests-root replay, dedicated
reminder-packet survey, and directly coupled docs surface only.

## Current Matrix

Treat the current bcm2835 matrix packet as the driver-plus-replay-plus-reminder
packet below:

- `drivers/watchdog/bcm2835_wdt.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `zigux/tests/phase11_bcm2835_wdt.zig`
- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`
- `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`

The returned driver, coupled verify helper, and focused tests-root replay keep
`summarizePlatformHandoff()`, `Bcm2835WdtLab.init()`, `start()`, `stop()`, and
`poweroff()` directly reviewable as compile-local timeout, PM-base gating,
poweroff-ownership, and stop-snapshot surfaces.

The current reminder packet keeps the returned driver packet truthful by
recording that the bcm2835 lane now has a bounded compile replay, a coupled
verify helper, a returned manifest-backed closure, and a current matrix without
pretending that the older slice or teardown-note surfaces have returned.

## Compile And Failure-Mode Review Surface

- compile anchor: `zigux/tests/phase11_bcm2835_wdt.zig` is the current focused
  replay for the live driver and keeps the compile-local validation surface
  explicit without claiming a wider shared Phase 11 build shard.
- verify-helper anchor: `drivers/watchdog/bcm2835_wdt_verify.zig` keeps the
  timeout gate, ready handoff, conflict handoff, blocked PM-base handoff,
  stop snapshot, and poweroff snapshot expectations fail-closed beside the live
  driver without claiming broader slice or teardown-note coverage.
- manifest anchor: `zigux/tests/phase11_bcm2835_wdt_manifest.json` keeps the
  archival packet identity, current scheduled continuity lane, returned packet
  surfaces, and still-blocked teardown follow-through machine-readable beside
  the same driver-local boundary.
- timeout window: the direct replay keeps `min_timeout_sec`,
  `max_timeout_sec`, `restart_priority`, and `restart_timeout_ticks` explicit
  together with the `TimeoutTooSmall` and `TimeoutTooLarge` boundaries.
- handoff gate: the ready path keeps `pm_base_handoff_ready`,
  `register_device_requested`, `stop_on_reboot_requested`,
  `poweroff_handler_claimed`, and `blocked_on_live_platform_registration`
  explicit when the parent is attached and the PM base is present.
- conflict handoff: the verify helper keeps the claimed-versus-conflict split
  explicit when the PM base is present and a poweroff handler is already
  installed.
- blocked handoff: the direct replay and verify helper both keep
  `register_device_requested`, `poweroff_handler_claimed`, and
  `poweroff_handler_conflict` false when `pm_base_present` is false, even if
  `system_power_controller` is true.
- poweroff ownership: the claimed path keeps the halt partition request,
  restart tick programming, reset arming, and reused restart path explicit,
  while the unclaimed path keeps those side effects clear.
- stop boundary: the stop replay keeps the reset-register write,
  running-before-stop, stopped-after-stop, and cleared
  `full_reset_armed_after_stop` boundary explicit without claiming live reboot
  execution.
- reminder posture: this matrix records only the current driver, verify helper,
  manifest-backed closure, focused replay, reminder-packet survey, and directly
  coupled validation-governance note and does not treat absent wider replay,
  slice, or teardown-note files as current-head evidence.

## Review Guardrails

- Treat this matrix as current-head truthfulness only, not as proof of live
  platform behavior or hardware-backed validation.
- Keep compile, teardown, and failure-mode parity bounded to the current
  driver, verify helper, manifest, focused replay, and directly coupled
  reminder packet until a later repo change restores a teardown note or wider
  replay bundle.
- Do not use this note to claim live platform registration, PM-base execution,
  watchdog-core registration, `pm_power_off` installation, remove-time callback
  release, reboot-backed teardown execution, or hardware-validated parity.
- If a future repo change restores any wider bcm2835 slice or teardown-note
  file, refresh this matrix together with the reopened companion surface in one
  bounded pass.

## Next Blocked Step

The next honest bcm2835-only follow-up is still the teardown-note return or
another equally small validation-truthfulness repair, rather than new runtime
behavior.
