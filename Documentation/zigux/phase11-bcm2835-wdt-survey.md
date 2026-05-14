# Phase 11 BCM2835 Watchdog Survey

This note keeps the Phase 11 `bcm2835_wdt` simple-driver gap truthful on current `master`.
It stays inside the watchdog lane and records the roadmap anchor, the directly readable repo state, and the next bounded follow-through without claiming that the bcm2835 starter packet has already landed.

## Status

* `PHASE11_BCM2835_WDT_SURVEY_STATUS=roadmap_gap_open`
* roadmap phase: `Phase 11`
* Linux anchor: `drivers/watchdog/bcm2835_wdt.c`
* recommended Zigux destination: `drivers/watchdog/bcm2835_wdt.zig`
* current gap remains open on direct `master` readback

## Current Repo Reality

The Phase 11 roadmap still names `drivers/watchdog/bcm2835_wdt.c` as one of the bounded simple production driver anchors beside `gpio_wdt`, `dw_wdt`, and `hvc_console`.
Current direct `master` readback does not yet materialize the obvious bcm2835 watchdog packet surfaces that a landed starter would need:

* `drivers/watchdog/bcm2835_wdt.zig`
* `zigux/tests/phase11_bcm2835_wdt.zig`
* `zigux/tests/phase11_bcm2835_wdt_manifest.json`
* `zigux/tests/phase11_bcm2835_wdt_survey.zig`
* `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`

Current `master` does already keep the broader Phase 11 lane active through `drivers/watchdog/gpio_wdt.zig`, the shipped HVC packet, and the shared docs-root Phase 11 summary.
That means the honest bcm2835 state is not "Phase 11 missing entirely".
The honest bcm2835 state is narrower: the roadmap anchor is still present, but the bcm2835 driver-local starter packet is not directly readable on current `master` yet.

The shared docs-root summary in `Documentation/zigux/README.md` already names `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` as part of the Phase 11 note set.
Until the bcm2835 driver-local packet actually materializes on `master`, that shared reminder should be treated as ahead of direct readback rather than as shipped bcm2835 evidence.

## Bounded Meaning

This survey note does not claim:

* a landed `bcm2835_wdt` Zig driver starter
* a dedicated bcm2835 direct replay or survey gate
* a shipped bcm2835 validation matrix
* live platform registration, PM-base plumbing, watchdog-core registration, or poweroff-handler coordination

It records one narrower fact instead: the Phase 11 roadmap still calls for a bounded bcm2835 watchdog starter, and current `master` still shows that driver family as a real same-lane gap.

## Next Bounded Step

The next honest same-lane follow-through is to land the first directly readable bcm2835 watchdog packet on `master` in one bounded packet, starting with:

* `drivers/watchdog/bcm2835_wdt.zig`
* one directly coupled replay surface under `zigux/tests/`
* one bcm2835-local manifest-backed or survey-backed reminder surface that fails closed on what is actually present

That follow-through should stay inside the bcm2835 watchdog family only.
It should not widen into `gpio_wdt`, `dw_wdt`, shared Phase 11 wording cleanup, or speculative platform-registration work before the first directly readable starter packet exists.
