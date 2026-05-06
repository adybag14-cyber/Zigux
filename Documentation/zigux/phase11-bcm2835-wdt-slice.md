# Phase 11 BCM2835 Watchdog Slice

This bounded Phase 11 slice adds the first Zigux `bcm2835_wdt` starter anchored to `drivers/watchdog/bcm2835_wdt.c`.

The starter stays intentionally narrow:

- validates the watchdog timeout window exposed by the Linux driver
- adds a tiny watchdog metadata summary for the Linux identity string, watchdog option flags, static timeout bounds, and bounded start or stop or get_timeleft or restart ops coverage
- models the in-memory register image for `PM_RSTC`, `PM_RSTS`, and `PM_WDOG`
- mirrors the bounded `is_running`, `start`, `stop`, `get_timeleft`, and restart behavior through register-image transitions only
- adds a tiny probe-time summary for bootloader-carried running status, watchdog-core timeout and nowayout initialization, restart priority, stop-on-reboot setup, watchdog parent linkage, and system-power-controller eligibility
- adds a tiny registration-facing handoff summary for watchdog registration intent plus poweroff-handler claim-vs-conflict outcomes
- adds a tiny registration-outcome summary for register-device success versus failure, probe-error return intent, and poweroff-handler claim follow-through or blocking when registration does not complete
- adds a tiny platform-registration and PM-base handoff summary for parent attachment, PM base availability, drvdata handoff readiness, register-device intent, and poweroff claim-vs-conflict reviewability
- adds a tiny poweroff-path summary for shared system-poweroff callback ownership, Raspberry Pi halt-partition request bits, and the short restart arming sequence without claiming a live poweroff hook installation
- adds a tiny remove-time teardown summary for devm-managed watchdog cleanup while clearing the shared poweroff callback only when `pm_power_off` still points at `bcm2835_power_off`
- preserves the Raspberry Pi halt-partition state in the lab snapshot without claiming full poweroff plumbing

This slice does not claim platform-driver registration, watchdog-core registration, MMIO access, delayed restart behavior, module parameter wiring beyond bookkeeping, live remove-time poweroff-handler release logic beyond that exact callback-identity check, or live poweroff integration yet.

`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` now records the first bounded hardware-validation matrix for watchdog metadata, timeout conversion, register-image transition coverage, probe-time bookkeeping, registration ownership, registration-outcome failure handling, platform handoff prerequisites, poweroff-path sequencing, and remove-time teardown scope without widening into live PM base or poweroff plumbing.

The next honest bounded step inside the same Phase 11 family is no longer another note-only handoff. The remaining gap is a later hardware-facing decision about whether to model any live platform registration or PM base plumbing, and that should stay blocked until the lane carries an explicit validation plan for that wider behavior.
