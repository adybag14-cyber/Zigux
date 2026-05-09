# Phase 11 DesignWare Watchdog Slice

This bounded Phase 11 slice adds the first Zigux `dw_wdt` starter anchored to `drivers/watchdog/dw_wdt.c`.

The starter stays intentionally narrow:

- derives the fixed TOP timeout windows from an injected input clock rate
- mirrors reset-mode versus IRQ-mode timeout selection and pretimeout bookkeeping
- models the register-image writes for start, ping, stop, restart, imported running-state snapshots, and time-left queries only
- keeps the DesignWare non-stoppable stop semantics explicit when reset control is unavailable
- adds a tiny probe-time summary for fixed-versus-custom TOP sourcing, nowayout and restart-priority bookkeeping, stop-on-reboot intent, and already-running watchdog state before registration
- adds a small registration-facing handoff around watchdog info selection, parent linkage, timeout-programming intent, and `watchdog_register_device` without claiming platform-backed execution
- adds a bounded platform-resource preflight summary for named `tclk` versus shared-clock fallback, optional APB clock presence, optional reset-control availability, optional pretimeout-IRQ wiring, and the explicit blocked-no-timer-clock posture before any live `devm_*` acquisition
- adds a bounded platform-registration scaffold summary that names `module_platform_driver` plus the `dw_wdt_drv_probe`, `dw_wdt_drv_remove`, and `dw_wdt_drv_shutdown` anchors while reusing the existing timer-clock, `platform_set_drvdata`, imported-running-state, and timeout-programming ordering split

This slice does not claim platform-driver registration side effects, clock or reset acquisition, IRQ registration, suspend or resume handling, debugfs support, custom devicetree TOP arrays beyond the bounded in-memory ordering helper, live MMIO access, or hardware validation coverage yet.

With the paired validation matrix and dedicated teardown note now landed beside the starter, the current `dw_wdt` packet keeps both the hardware-validation plan and the stop or remove ownership split reviewable without widening into platform-backed behavior. The bounded platform-resource preflight summary also keeps the next probe or remove execution step honest about clock, reset, and pretimeout-IRQ choices before any real `devm_*` acquisition lands. The next honest bounded step inside the same Phase 11 lane is no longer another abstract handoff note: it is to turn this new platform-registration scaffold into a real probe or remove execution slice only when the lane can also carry matching clock, reset, IRQ, and validation evidence without widening into broader PM behavior.
