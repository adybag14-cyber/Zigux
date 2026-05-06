# Phase 11 GPIO Watchdog Module Slice

This bounded Phase 11 module slice records the current Zigux `gpio_wdt` lab starter anchored to `drivers/watchdog/gpio_wdt.c`.

The module-facing surface stays intentionally narrow:

- exposes a `gpio_wdt_lab` descriptor that keeps the lane scoped to a simple driver starter rather than live platform registration
- snapshots the bounded `hw_algo`, heartbeat-margin, `always-running`, `nowayout`, timeout-init, parent-linkage, and stop-on-reboot bookkeeping surfaced during probe
- adds a tiny `descriptorPreflightSummary()` helper so the starter records the exact `devm_gpiod_get()` flag choice and the fact that descriptor lookup still sits before timeout parsing, `always-running` bookkeeping, and the later registration handoff without claiming live GPIO acquisition
- adds a tiny `timeoutPropertyCheckpointSummary()` helper so the starter records that `hw_margin_ms` stays required and bounds-checked after descriptor lookup but before `always-running` bookkeeping, `watchdog_set_drvdata()`, and the registration-facing handoff without claiming a live property read
- models the in-memory start, ping, stop, disable, and nowayout-aware stop-request paths without claiming GPIO descriptor ownership or watchdog-core registration
- stays under the shared `zigux/tests/phase11_build.zig` review gate so the starter and survey lane remain aligned

This slice does not claim platform-driver registration, live GPIO descriptor lookup, watchdog-core registration, reboot integration beyond summary bookkeeping, module parameter wiring beyond `nowayout` bookkeeping, or hardware validation coverage yet.

The next honest bounded step inside the same Phase 11 lane is now one tiny drvdata-order checkpoint that stays immediately adjacent to the new timeout-property checkpoint and the existing registration handoff, before any live GPIO or broader platform glue lands.
