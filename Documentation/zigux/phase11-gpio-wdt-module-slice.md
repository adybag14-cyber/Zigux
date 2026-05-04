# Phase 11 GPIO Watchdog Module Slice

This bounded Phase 11 module slice records the current Zigux `gpio_wdt` lab starter anchored to `drivers/watchdog/gpio_wdt.c`.

The module-facing surface stays intentionally narrow:

- exposes a `gpio_wdt_lab` descriptor that keeps the lane scoped to a simple driver starter rather than live platform registration
- snapshots the bounded `hw_algo`, heartbeat-margin, `always-running`, `nowayout`, timeout-init, parent-linkage, and stop-on-reboot bookkeeping surfaced during probe
- models the in-memory start, ping, stop, disable, and nowayout-aware stop-request paths without claiming GPIO descriptor ownership or watchdog-core registration
- keeps the starter-local `nowayout` policy contract explicit through `nowayoutPolicySummary()`, so the `nowayout` module parameter name, the `watchdog_nowayout` default source, and the bounded `watchdog_set_nowayout()` application boundary stay reviewable as bookkeeping rather than being rediscovered later during live registration work
- adds an explicit `summarizeTeardown()` helper so `gpio_wdt_disable()`-style eternal-ping ordering, toggle-versus-level disable fallout, and `always-running` versus `nowayout` stop failure modes stay reviewable beside the current starter
- records the first chosen watchdog-registration surface as metadata-only planning, together with the validation focus that preceded the now-landed bounded register-device call summary
- keeps the first bounded `registerDeviceCallSummary()` surface explicit so the starter records one real watchdog-core handoff boundary without claiming the live `devm_watchdog_register_device()` call
- keeps the parked `registerDeviceFailureSummary()` surface explicit so descriptor preflight, platform registration, and reboot glue blockers stay machine-checkable beside the first bounded request instead of being implied by the call surface alone
- stays under the shared `zigux/tests/phase11_build.zig` review gate so the starter and survey lane remain aligned

This slice does not claim platform-driver registration, GPIO descriptor lookup, watchdog-core registration, reboot integration beyond summary bookkeeping, module parameter wiring beyond `nowayout` bookkeeping, or hardware validation coverage yet.

The active continuity owner for this review packet is `P11-Y01`, while the archived manifest identity remains `P11-L04` for traceability.

The next honest bounded step inside the same Phase 11 lane is to leave this starter parked unless fresh repo inspection finds another comparably small teardown or failure-mode drift inside `gpio_wdt`. Avoid widening straight into descriptor-backed preflight, reboot glue, or broader watchdog registration work from this packet.
