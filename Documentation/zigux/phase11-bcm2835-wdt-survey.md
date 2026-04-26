# Phase 11 BCM2835 Watchdog Survey

This survey note tracks the Phase 11 gap around `drivers/watchdog/bcm2835_wdt.c` after re-reading `master` `911ed30d6f76ddacb634887d1d740afc2145b729`.

The live repo state is now:

- `drivers/watchdog/gpio_wdt.zig` already provides one bounded Phase 11 watchdog starter, so the tranche has a real foothold
- `drivers/watchdog/bcm2835_wdt.zig` already ships the bounded bcm2835 starter for timeout tick encoding, running-bit detection, bounded start and stop register transitions, restart intent, halt-partition bookkeeping, a tiny probe-time summary, and a small registration-facing handoff or poweroff ownership summary
- `zigux/tests/phase11_bcm2835_wdt.zig` and `Documentation/zigux/phase11-bcm2835-wdt-slice.md` keep that starter reviewable without claiming platform registration or hardware-backed execution
- `zigux/tests/phase11_bcm2835_wdt_survey.zig` and `zigux/tests/phase11_bcm2835_wdt_manifest.json` still track the remaining bcm2835_wdt gap against the roadmap so the lane does not overclaim progress
- `zigux/tests/phase11_build.zig` runs the gpio starter checks, the bcm2835 starter checks, and the bcm2835 survey check together so Phase 11 watchdog drift is visible in one place

This lane still does not claim watchdog-core registration, PM base wiring, remove-time poweroff-handler release behavior, or hardware validation coverage.

The next honest bounded step inside the same lane is to add a tiny remove-time summary before any platform registration, PM base plumbing, or live poweroff-handler coordination.
