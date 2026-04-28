# Phase 11 GPIO Watchdog Module Slice

This bounded Phase 11 module slice records the current Zigux `gpio_wdt` lab starter anchored to `drivers/watchdog/gpio_wdt.c`.

The module-facing surface stays intentionally narrow:

- exposes a `gpio_wdt_lab` descriptor that keeps the lane scoped to a simple driver starter rather than live platform registration
- snapshots the bounded `hw_algo`, heartbeat-margin, `always-running`, `nowayout`, timeout-init, parent-linkage, and stop-on-reboot bookkeeping surfaced during probe
- models the in-memory start, ping, stop, disable, and nowayout-aware stop-request paths without claiming GPIO descriptor ownership or watchdog-core registration
- records the first chosen watchdog-registration surface as metadata-only planning, together with the validation focus that still blocks a real register-device call
- stays under the shared `zigux/tests/phase11_build.zig` review gate so the starter and survey lane remain aligned

This slice does not claim platform-driver registration, GPIO descriptor lookup, watchdog-core registration, reboot integration beyond summary bookkeeping, module parameter wiring beyond `nowayout` bookkeeping, or hardware validation coverage yet.

The next honest bounded step inside the same Phase 11 lane is to move from that metadata-only registration plan to the first bounded register-device call surface so the starter can describe one real watchdog-core handoff without pulling in live GPIO or broader platform glue.
