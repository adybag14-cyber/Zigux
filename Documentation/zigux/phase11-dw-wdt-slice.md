# Phase 11 DesignWare Watchdog Slice

This bounded Phase 11 slice adds the first Zigux `dw_wdt` starter anchored to `drivers/watchdog/dw_wdt.c`.

The starter stays intentionally narrow:

- derives the fixed TOP timeout windows from an injected input clock rate
- mirrors reset-mode versus IRQ-mode timeout selection and pretimeout bookkeeping
- models the register-image writes for start, ping, stop, restart, imported running-state snapshots, and time-left queries only
- keeps the DesignWare non-stoppable stop semantics explicit when reset control is unavailable
- adds a tiny probe-time summary for fixed-versus-custom TOP sourcing, nowayout and restart-priority bookkeeping, stop-on-reboot intent, and already-running watchdog state before registration
- adds a small registration-facing handoff that keeps watchdog info selection, parent linkage, driver-data setup, timeout-init intent, imported running-state bookkeeping, and register-device intent explicit before any live registration

This slice does not claim platform-driver registration, clock or reset acquisition, IRQ registration, suspend or resume handling, debugfs support, custom devicetree TOP arrays beyond the bounded in-memory ordering helper, live MMIO access, or hardware validation coverage yet.

The next honest bounded step inside the same Phase 11 lane is to add a tiny platform-resource preflight around timer-clock choice, optional APB clock presence, reset-control availability, and optional pretimeout-IRQ wiring before any live devm calls or watchdog registration work lands.
