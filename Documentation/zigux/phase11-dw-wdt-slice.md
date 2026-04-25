# Phase 11 DesignWare Watchdog Slice

This bounded Phase 11 slice adds the first Zigux `dw_wdt` starter anchored to `drivers/watchdog/dw_wdt.c`.

The starter stays intentionally narrow:

- derives the fixed TOP timeout windows from an injected input clock rate
- mirrors reset-mode versus IRQ-mode timeout selection and pretimeout bookkeeping
- models the register-image writes for start, ping, stop, restart, and time-left queries only
- keeps the DesignWare non-stoppable stop semantics explicit when reset control is unavailable

This slice does not claim platform-driver registration, clock or reset acquisition, IRQ registration, suspend or resume handling, debugfs support, custom devicetree TOP arrays, live MMIO access, or hardware validation coverage yet.

The next honest bounded step inside the same Phase 11 lane is to add a tiny probe-time summary around fixed-vs-custom TOP sourcing, nowayout and restart-priority bookkeeping, and already-running watchdog state before any platform-backed behavior lands.
