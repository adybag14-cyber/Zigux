# Phase 11 GPIO Watchdog Slice

This bounded Phase 11 slice adds the first Zigux `gpio_wdt` starter anchored to `drivers/watchdog/gpio_wdt.c`.

The starter stays intentionally narrow:

- parses the Linux driver's `hw_algo` property surface for the `toggle` and `level` modes
- enforces the same bounded hardware heartbeat margin window used by the C driver
- models the in-memory start, ping, stop, and disable transitions for both hardware algorithms
- preserves the `always-running` stop behavior so the lab model does not pretend the watchdog can be disabled when the platform contract forbids it
- reports a probe-time summary for requested GPIO line mode, `always-running` startup behavior, `nowayout`, timeout init, parent linkage, and stop-on-reboot bookkeeping before watchdog registration
- distinguishes watchdog-core `nowayout` stop blocking from the driver's own `always-running` hardware behavior so stop-path review does not blur policy gating with hardware gating
- adds a tiny registration-facing handoff summary so the starter records what startup state, stop policy, timeout init, and reboot bookkeeping reach `devm_watchdog_register_device()` without claiming the registration call itself

This slice does not claim platform-driver registration, GPIO descriptor lookup, watchdog-core registration, reboot integration, module parameter wiring beyond summary bookkeeping, or real hardware validation yet.

The next honest bounded step inside the same Phase 11 lane is to decide the first real registration surface and the minimum validation plan around it before any live GPIO or broader watchdog integration work.
