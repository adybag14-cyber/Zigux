# Phase 11 BCM2835 Watchdog Slice

This slice note records the first bcm2835-local platform-registration scaffold that is directly reviewable on current `master`.
It exists to make the explicit validation plan truthful now that the packet includes a dedicated registration-scaffold replay, while still keeping live platform-backed execution out of scope.

## Status

- `PHASE11_BCM2835_WDT_SLICE_STATUS=registration_scaffold_landed`
- roadmap phase: `Phase 11`
- continuity remains with `P11-L08`
- Linux anchor: `drivers/watchdog/bcm2835_wdt.c`
- bounded packet: starter driver, compile-local verify helper, dedicated replay, dedicated registration-scaffold replay, dedicated survey gate, manifest, survey note, teardown note, validation matrix, and this slice note

## Current Directly Reviewable Slice

The current bcm2835-local registration scaffold now spans these directly readable surfaces:

- `drivers/watchdog/bcm2835_wdt.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `zigux/tests/phase11_bcm2835_wdt.zig`
- `zigux/tests/phase11_bcm2835_wdt_registration_scaffold.zig`
- `zigux/tests/phase11_bcm2835_wdt_survey.zig`
- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`

That directly reviewable slice now makes these facts explicit:

- `summarizePlatformHandoff()` keeps parent attachment and PM-base handoff readiness reviewable before any live registration claim
- `drivers/watchdog/bcm2835_wdt_verify.zig` still covers ownership-sensitive ready and blocked handoff states
- `zigux/tests/phase11_bcm2835_wdt_registration_scaffold.zig` now adds a dedicated replay for parent-missing, PM-base-ready, and controller-free handoff states
- `zigux/tests/phase11_bcm2835_wdt_survey.zig` now fail-closes the new registration-scaffold replay and this slice note alongside the older starter packet surfaces

## Explicit Validation Plan

The explicit validation plan for the bcm2835 packet is now:

1. Keep platform-registration follow-through anchored to the already-modeled PM-base handoff and controller ownership boundary.
2. Land only one directly reviewable execution bridge next, such as publishing the already-modeled prerequisite state into one registration-sequencing helper.
3. Keep live platform registration, callback installation, IRQ ownership, and hardware-backed poweroff execution out of scope until that bridge exists and is replayed locally.

## Still Blocked

This slice note does not claim:

- live platform registration or PM-base execution wiring
- watchdog-core callback installation
- hardware-backed poweroff or reboot execution
- any shared Phase 11 closure outside the bcm2835 packet
