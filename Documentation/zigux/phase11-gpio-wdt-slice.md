# Phase 11 GPIO Watchdog Slice

This bounded Phase 11 slice adds the first Zigux `gpio_wdt` starter anchored to `drivers/watchdog/gpio_wdt.c`.

The starter stays intentionally narrow:

- parses the Linux driver's `hw_algo` property surface for the `toggle` and `level` modes
- enforces the same bounded hardware heartbeat margin window used by the C driver
- models the in-memory start, ping, stop, and disable transitions for both hardware algorithms
- preserves the `always-running` stop behavior so the lab model does not pretend the watchdog can be disabled when the platform contract forbids it
- adds an explicit `summarizeTeardown()` helper so eternal-ping disable ordering, toggle-versus-level disable fallout, and `always-running` versus `nowayout` stop failure modes stay reviewable before any unregister path exists
- reports a probe-time summary for requested GPIO line mode, `always-running` startup behavior, `nowayout`, timeout init, parent linkage, and stop-on-reboot bookkeeping before watchdog registration
- keeps the `GPIO Watchdog` watchdog-info identity plus the bounded `WDIOF_SETTIMEOUT`, `WDIOF_MAGICCLOSE`, and `WDIOF_KEEPALIVEPING` contract explicit through a small metadata summary instead of leaving that starter surface implicit inside the later register-device packet
- keeps the tiny platform-driver shell explicit through `platformDriverIdentitySummary()` so the `gpio-wdt` driver name, the `linux,wdt-gpio` OF match entry, the `gpio_wdt_probe()` callback, and the default `module_platform_driver()` versus `CONFIG_GPIO_WATCHDOG_ARCH_INITCALL` override boundary stay reviewable without claiming live registration
- distinguishes watchdog-core `nowayout` stop blocking from the driver's own `always-running` hardware behavior so teardown-facing stop review does not blur policy gating with hardware gating
- adds a tiny registration-facing handoff summary so the starter records what startup state, stop policy, timeout init, and reboot bookkeeping reach `devm_watchdog_register_device()` without claiming the registration call itself
- records the first chosen registration surface and validation focus so the lane stays explicitly parked at watchdog-device metadata planning instead of overclaiming a real register-device call
- adds one tiny `registerDeviceCallSummary()` helper so the starter records the exact watchdog metadata, timeout, parent, `nowayout`, and stop-on-reboot state that would reach the first bounded `devm_watchdog_register_device()` request without claiming the live call itself
- now pairs that starter surface with `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` so the shared replay contract, teardown-facing stop evidence, explicit teardown-summary evidence, and the first bounded register-device call boundary are recorded in one reviewable place

This slice does not claim platform-driver registration, GPIO descriptor lookup, watchdog-core registration, reboot integration, module parameter wiring beyond summary bookkeeping, or live hardware validation yet.

The active continuity owner for this review packet is `P11-Y01`.

The archived manifest identity for this landed packet remains `P11-L04` for traceability, even though later scheduled continuity revisited the same teardown-facing review packet under `P11-L03` and the same wording-only validation cleanup under `P11-L05` without reopening descriptor-backed preflight or live registration work.

The next honest bounded step inside the same Phase 11 lane is to leave the starter parked unless fresh repo inspection finds another comparably small simple-driver, teardown, or failure-mode drift inside `gpio_wdt`. Keep descriptor-backed preflight, reboot glue, and broader watchdog registration work blocked from this slice.
