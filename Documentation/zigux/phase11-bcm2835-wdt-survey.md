# Phase 11 BCM2835 Watchdog Survey

This survey note now serves as the archival checkpoint for the original Phase 11 roadmap gap around `drivers/watchdog/bcm2835_wdt.c`.

The live repo state is now:

- reviewed against live `master` `55568844ac3ce835b0e0bef624c24c17f22b78a1`
- `drivers/watchdog/gpio_wdt.zig` already provides one bounded Phase 11 watchdog starter, so the tranche has a real foothold
- `drivers/watchdog/bcm2835_wdt.zig` already ships the bounded bcm2835 starter for watchdog metadata, timeout tick encoding, running-bit detection, bounded start and stop register transitions, restart intent, halt-partition bookkeeping, a tiny probe-time summary, a small registration-facing handoff or poweroff ownership summary, a tiny registration-outcome summary, a tiny platform-registration or PM-base handoff summary, a small poweroff-path summary, and a tiny remove-time teardown summary that only clears the shared callback when `pm_power_off` still matches `bcm2835_power_off`
- `zigux/tests/phase11_bcm2835_wdt.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, and `Documentation/zigux/phase11-bcm2835-wdt-slice.md` keep that starter reviewable without claiming platform registration or hardware-backed execution, and the focused driver replays now keep timeout-window, register-device success-versus-failure, poweroff-path, and remove-time ownership evidence explicit without claiming a live probe path
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` now names the shared Phase 11 test gate, the current timeout, register-image transition, probe, registration, registration-outcome, platform-handoff, poweroff-path, and remove-time evidence, and the still-blocked live platform-registration or PM-base decision
- `zigux/tests/phase11_bcm2835_wdt_survey.zig` and `zigux/tests/phase11_bcm2835_wdt_manifest.json` now treat the handoff and poweroff summaries as landed while still keeping the live platform-registration and PM-base gap explicit so the lane does not overclaim progress
- the focused replays `zig test zigux/tests/phase11_bcm2835_wdt.zig`, `zig test drivers/watchdog/bcm2835_wdt_verify.zig`, and `zig test zigux/tests/phase11_bcm2835_wdt_survey.zig` still pass for the bounded bcm2835 packet on current `master`
- `zigux/tests/phase11_build.zig` still compiles and runs the gpio starter checks, the `phase11-bcm2835-wdt-tests` starter replay, the `phase11-bcm2835-wdt-verify-tests` verify replay, and the `phase11-bcm2835-wdt-survey-tests` survey replay together so Phase 11 watchdog drift is visible in one place, but this archival watchdog note no longer claims that the whole current shared Phase 11 replay is green when unrelated non-watchdog drift can reopen elsewhere on `master`

This lane is no longer survey-only, and the archival survey now carries `P11-L08` packet identity so the bcm2835 watchdog review record stays traceable alongside the live manifest, survey gate, and validator ownership for the current lane key. It does not claim watchdog-core registration, PM base wiring, live remove-time poweroff-handler release behavior beyond that exact callback-identity check, or hardware-backed execution.

The next honest bounded step inside the same Phase 11 family is not another review-only handoff. Any later move into live platform registration, PM base plumbing, or shared poweroff-handler coordination should stay blocked until the lane carries an explicit hardware-validation plan for that wider behavior.
