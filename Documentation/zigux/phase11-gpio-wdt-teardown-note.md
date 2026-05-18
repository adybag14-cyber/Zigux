# Phase 11 GPIO Watchdog Teardown Note

This note records the first bounded teardown-facing checkpoint for the Phase 11 `gpio_wdt` starter anchored to `drivers/watchdog/gpio_wdt.c`.

## Status

- `PHASE11_GPIO_WDT_TEARDOWN_STATUS=teardown_note_landed`
- scope: keep the current stop-policy split, drvdata ownership checkpoint, registration-intent checkpoint, and registration handoff reviewable as one teardown-facing packet without overclaiming live reboot, remove, or shutdown execution
- current packet surfaces:
  - `drivers/watchdog/gpio_wdt.zig`
  - `zigux/tests/phase11_gpio_wdt.zig`
  - `zigux/tests/phase11_gpio_wdt_survey.zig`
  - `zigux/tests/phase11_gpio_wdt_manifest.json`
  - `Documentation/zigux/phase11-gpio-wdt-module-slice.md`
  - `Documentation/zigux/phase11-gpio-wdt-survey.md`
  - `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
  - `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`

## Bounded Teardown Meaning

The current host-free teardown packet is intentionally narrow:

- `requestStop()` keeps watchdog-core `nowayout` blocking distinct from hardware `always-running` behavior, so teardown-facing review can tell whether the stop path reaches the internal disable helper at all
- `drvdataOwnershipCheckpointSummary()` keeps the bounded owner identity, parent linkage, and pre-registration ownership handoff explicit before any live `platform_set_drvdata()` or watchdog-core registration work exists
- `registrationIntentCheckpointSummary()` keeps the `watchdog_init_timeout()`, `watchdog_set_nowayout()`, `watchdog_stop_on_reboot()`, and optional pre-registration start order explicit before `devm_watchdog_register_device()`, so the teardown-facing packet can talk about shutdown intent without claiming the registration call itself
- `registrationHandoffSummary()` records what startup state, stop policy, timeout init, and stop-on-reboot bookkeeping would reach `devm_watchdog_register_device()` so the teardown-facing packet can talk about later ownership and shutdown consequences without claiming the call itself

Together these surfaces are enough to describe the first teardown-facing ownership boundary around the starter packet. They are not enough to claim live reboot-hook, remove-hook, or shutdown execution, and they do not imply that GPIO descriptor acquisition, platform-driver registration, watchdog-core registration, or hardware-backed teardown validation are already present.

## Next Bounded Step

If this lane reopens, keep the next same-driver step to one tiny hardware-validation or registration-intent-adjacent checkpoint that reuses the teardown-facing ownership language already recorded here, instead of widening straight into live GPIO or broader platform glue.
