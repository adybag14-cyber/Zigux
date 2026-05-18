# Phase 11 GPIO Watchdog Module Slice

This bounded Phase 11 module slice records the current Zigux `gpio_wdt` lab starter anchored to `drivers/watchdog/gpio_wdt.c`.

The module-facing surface stays intentionally narrow:

- exposes a `gpio_wdt_lab` descriptor that keeps the lane scoped to a simple driver starter rather than live platform registration
- snapshots the bounded `hw_algo`, heartbeat-margin, `always-running`, `nowayout`, timeout-init, parent-linkage, and stop-on-reboot bookkeeping surfaced during probe
- adds a tiny `descriptorPreflightSummary()` helper so the starter records the exact `devm_gpiod_get()` flag choice and the fact that descriptor lookup still sits before timeout parsing, `always-running` bookkeeping, and the later registration handoff without claiming live GPIO acquisition
- adds a tiny `timeoutPropertyCheckpointSummary()` helper so the starter records that the required `hw_margin_ms` property still sits between descriptor lookup and the later always-running plus registration-facing bookkeeping without claiming a live property or GPIO path
- adds a tiny `drvdataOwnershipCheckpointSummary()` helper so the starter records that parent linkage and module ownership remain attached when the bounded drvdata owner is chosen, and that this ownership checkpoint still sits before the registration-facing handoff without claiming live platform registration
- adds a tiny `registrationIntentCheckpointSummary()` helper so the starter records that `watchdog_init_timeout()`, `watchdog_set_nowayout()`, `watchdog_stop_on_reboot()`, and any optional pre-registration start stay ordered before `devm_watchdog_register_device()` without claiming that registration call
- models the in-memory start, ping, stop, disable, and nowayout-aware stop-request paths without claiming GPIO descriptor ownership or watchdog-core registration
- now pairs the stop-policy split, drvdata ownership checkpoint, registration-intent checkpoint, and registration handoff with `Documentation/zigux/phase11-gpio-wdt-teardown-note.md` so the first teardown-facing note stays adjacent to the same host-free starter packet
- stays under the shared `zigux/tests/phase11_build.zig` review gate so the starter and survey lane remain aligned

This slice does not claim platform-driver registration, live GPIO descriptor lookup, watchdog-core registration, reboot integration beyond the bounded `nowayout` and stop-on-reboot setup checkpoint, or hardware validation coverage yet.

The next honest bounded step inside the same Phase 11 lane is now one tiny hardware-validation checkpoint that stays immediately adjacent to the teardown note, the drvdata ownership checkpoint, the registration-intent checkpoint, and the existing registration handoff before any live GPIO or broader platform glue lands.
