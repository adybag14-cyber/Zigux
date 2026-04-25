# Phase 11 DesignWare Watchdog Survey

This survey note tracks the Phase 11 gap around `drivers/watchdog/dw_wdt.c` after re-reading `master` `e29d500ea9a23162b421c587b433bb897f6ef044`.

The live repo state is now:

- `drivers/watchdog/gpio_wdt.zig` and `drivers/watchdog/bcm2835_wdt.zig` already give the simple-driver watchdog tranche two landed Phase 11 footholds
- `drivers/watchdog/dw_wdt.zig` already ships the bounded DesignWare starter for fixed TOP timeout windows, reset-mode versus IRQ-mode timeout selection, pretimeout bookkeeping, register-image transitions, and the non-stoppable stop semantics when reset control is unavailable
- `zigux/tests/phase11_dw_wdt.zig` and `Documentation/zigux/phase11-dw-wdt-slice.md` keep that starter reviewable without claiming platform registration, live MMIO, IRQ wiring, PM behavior, or hardware-backed execution
- `zigux/tests/phase11_build.zig` now runs the gpio starter checks, bcm2835 starter and survey checks, the dw_wdt starter checks, and the new dw_wdt survey check together so watchdog-lane drift is visible in one place

This lane still does not claim platform-driver registration, clock or reset acquisition, IRQ registration, suspend or resume handling, debugfs support, custom devicetree TOP arrays, live MMIO access, or hardware validation coverage.

The next honest bounded step inside the same lane is to add a tiny probe-time summary around fixed-versus-custom TOP sourcing, nowayout and restart-priority bookkeeping, and already-running watchdog state before any platform-backed behavior lands.
