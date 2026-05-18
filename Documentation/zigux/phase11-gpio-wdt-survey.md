# Phase 11 GPIO Watchdog Survey

This survey note now tracks the landed Phase 11 `gpio_wdt` starter anchored to `drivers/watchdog/gpio_wdt.c`.

The live repo state is now:

- `drivers/watchdog/gpio_wdt.zig` models `hw_algo` parsing, heartbeat-margin validation, the narrow start, ping, stop, and disable transitions from the Linux GPIO watchdog driver, a small probe-time summary for startup and registration-facing bookkeeping, a tiny `descriptorPreflightSummary()` helper for the `devm_gpiod_get()` flag choice and probe ordering, a tiny `timeoutPropertyCheckpointSummary()` helper for the required `hw_margin_ms` ordering, a tiny `drvdataOwnershipCheckpointSummary()` helper for the bounded drvdata ownership decision, a tiny `registrationIntentCheckpointSummary()` helper for the `watchdog_init_timeout()`, `watchdog_set_nowayout()`, `watchdog_stop_on_reboot()`, and optional pre-registration start order before watchdog registration, a tiny nowayout-aware stop helper that separates watchdog-core policy blocking from hardware `always-running` behavior, and a registration handoff summary
- `zigux/tests/phase11_gpio_wdt.zig` keeps the toggle and level algorithms reviewable without claiming GPIO registration or hardware-backed execution, and now checks always-running startup, descriptor preflight ordering, timeout-property ordering, drvdata ownership ordering, registration-intent ordering, pre-registration bookkeeping, stop-request outcomes, and registration handoff reporting
- `zigux/tests/phase11_build.zig` runs the starter and survey paths together so lane-local freshness drift shows up in one place
- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md` now records the bounded teardown-facing meaning of the stop-policy split, the drvdata ownership checkpoint, the registration-intent checkpoint, and the registration handoff without claiming live reboot or remove execution
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` now records the bounded validation posture for the landed starter and the still-deferred kernel-facing follow-up

This remains intentionally small. The lane still does not claim platform-driver registration, live GPIO descriptor lookup, watchdog core registration, reboot hooks beyond the bounded `nowayout` and stop-on-reboot setup checkpoint, live GPIO execution, or hardware-backed validation beyond the bounded matrix evidence already recorded for the current starter.

The next honest bounded step inside the same lane is to pick one tiny hardware-validation checkpoint that stays immediately adjacent to the new teardown note, descriptor, timeout-property, drvdata ownership, and registration-intent boundaries, while still avoiding live GPIO and platform glue until the handoff bookkeeping is no longer the blocker.
