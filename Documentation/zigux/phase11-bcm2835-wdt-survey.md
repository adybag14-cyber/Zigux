# Phase 11 BCM2835 Watchdog Survey

This survey note now serves as the archival checkpoint for the original Phase 11 roadmap gap around `drivers/watchdog/bcm2835_wdt.c`.

The live repo state is now:

- reviewed against live `master` `d8638f7e136ae70164477451aadee9ec58671259`
- `drivers/watchdog/gpio_wdt.zig` already provides one bounded Phase 11 watchdog starter, so the tranche has a real foothold
- `drivers/watchdog/bcm2835_wdt.zig` already ships the bounded bcm2835 starter for timeout tick encoding, running-bit detection, bounded start and stop register transitions, restart intent, halt-partition bookkeeping, a tiny probe-time summary, a small registration-facing handoff or poweroff ownership summary, and a tiny remove-time ownership summary
- `zigux/tests/phase11_bcm2835_wdt.zig` and `Documentation/zigux/phase11-bcm2835-wdt-slice.md` keep that starter reviewable without claiming platform registration or hardware-backed execution
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` now names the shared Phase 11 test gate, the current timeout, probe, registration, and remove-time evidence, and the still-pending platform-registration or PM-base follow-up
- `zigux/tests/phase11_bcm2835_wdt_survey.zig` and `zigux/tests/phase11_bcm2835_wdt_manifest.json` still track the remaining bcm2835_wdt gap against the roadmap so the lane does not overclaim progress
- `zigux/tests/phase11_build.zig` runs the gpio starter checks, the bcm2835 starter checks, and the bcm2835 survey check together so Phase 11 watchdog drift is visible in one place

This lane is no longer survey-only, but the archival survey still does not claim watchdog-core registration, PM base wiring, live remove-time poweroff-handler release behavior, or hardware-backed execution.

The next honest bounded step inside the same lane is a tiny platform-registration and PM-base handoff summary that keeps watchdog registration intent and poweroff ownership reviewable before any live platform registration, PM base plumbing, or poweroff-handler coordination widens the slice.
