# Phase 11 BCM2835 Watchdog Teardown Note

This note records the bounded teardown and restart or poweroff surface that is directly
reviewable in the current Zigux `bcm2835_wdt` starter packet. It stays inside the bcm2835
watchdog lane and avoids describing larger registration or remove flows that this run
could not read back directly from `master`.

## Status

* `PHASE11_BCM2835_WDT_TEARDOWN_STATUS=driver_teardown_truthful`
* archival packet identity remains `P11-L08`
* lane scope: keep the current bcm2835 watchdog stop, restart, and poweroff story
  reviewable without widening into platform registration, PM-base plumbing, shared
  callback installation, or hardware-backed execution
* directly readable bcm2835 reminder packet for this note:
  * `drivers/watchdog/bcm2835_wdt.zig`
  * `drivers/watchdog/bcm2835_wdt_verify.zig`
  * `zigux/tests/phase11_bcm2835_wdt.zig`
  * `zigux/tests/phase11_bcm2835_wdt_survey.zig`
  * `zigux/tests/phase11_bcm2835_wdt_manifest.json`
  * `Documentation/zigux/phase11-bcm2835-wdt-slice.md`
  * `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
  * `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`
  * `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`

## Teardown And Poweroff Surface

The current directly readable bcm2835 driver starter plus the dedicated replay,
compile-local verify helper, dedicated survey gate, and archival manifest-backed
reminder packet keep one small teardown boundary explicit:

* `summarizeProbe()` keeps the system-power-controller split and the
  claimed-versus-conflicting poweroff-handler summary readable before any live callback
  installation is implied.
* `Bcm2835WdtLab.stop()` owns the bounded stop path by recording `reset_register_written`,
  `running_before_stop`, `running_after_stop`, and `full_reset_armed_after_stop`.
* `Bcm2835WdtLab.restart()` owns the short restart-arm path by recording the fixed restart
  timeout ticks, the full-reset posture, the bounded delay marker, and the running state
  after restart intent.
* `Bcm2835WdtLab.poweroff()` keeps the halt-partition request and restart-path reuse
  explicit without claiming that a shared platform poweroff callback was actually
  installed or executed.
* `Bcm2835WdtLab.importBootloaderRunning()` keeps the imported running-state checkpoint
  readable so the restart and poweroff path can be reviewed from a nonzero time-left
  starting point.
* `zigux/tests/phase11_bcm2835_wdt.zig` replays the timeout, ownership, start-stop,
  restart, and poweroff surfaces as a dedicated tests-root proof beside the driver-local
  tests.
* `drivers/watchdog/bcm2835_wdt_verify.zig` keeps PM-base readiness and
  claimed-versus-conflicting poweroff ownership reviewable beside the driver-local replay.
* `zigux/tests/phase11_bcm2835_wdt_survey.zig` now keeps this teardown note aligned with
  the survey note and validation matrix so the directly readable bcm2835 evidence packet
  does not regress.

## Review Rules

* Treat this note as a bounded ownership and teardown reminder for the current directly
  readable driver starter, the dedicated replay, the compile-local verify helper, the
  dedicated survey gate, and the archival manifest-backed reminder packet, not as proof
  of live platform remove or shared callback execution.
* Keep this note aligned with `drivers/watchdog/bcm2835_wdt.zig`,
  `drivers/watchdog/bcm2835_wdt_verify.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`,
  `zigux/tests/phase11_bcm2835_wdt_survey.zig`,
  `zigux/tests/phase11_bcm2835_wdt_manifest.json`,
  `Documentation/zigux/phase11-bcm2835-wdt-slice.md`,
  `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, and
  `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` when the directly
  readable stop, restart, or poweroff helpers change.
* Do not describe live platform-backed closure, shared callback installation, PM-base
  plumbing, or hardware-backed execution as landed until the bcm2835 lane records an
  explicit validation plan and the wider Zig surface exists.

## Next Blocked Step

The next honest bcm2835 follow-through is one explicit validation plan that matches the
current driver starter, dedicated replay, compile-local verify helper, dedicated survey
gate, and archival manifest-backed reminder packet. Until that lands, keep this teardown
note bounded to the driver-local stop, restart, and poweroff model already visible on
`master`.
