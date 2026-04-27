# Phase 11 DesignWare Watchdog Survey

This survey note tracks the Phase 11 gap around `drivers/watchdog/dw_wdt.c` after re-reading `master` `8266af3574ebb9103f60b2d1888a5f1e611f9ab4`.

The live repo state is now:

- `drivers/watchdog/gpio_wdt.zig` and `drivers/watchdog/bcm2835_wdt.zig` already give the simple-driver watchdog tranche two landed Phase 11 footholds
- `drivers/watchdog/dw_wdt.zig` now ships the bounded DesignWare starter for fixed TOP timeout windows, reset-mode versus IRQ-mode timeout selection, pretimeout bookkeeping, register-image transitions, non-stoppable stop semantics, a tiny probe-time summary for fixed-versus-custom TOP sourcing plus already-running watchdog metadata, and a small registration-facing handoff for watchdog info selection, parent linkage, driver-data setup, timeout-init intent, imported running-state bookkeeping, and register-device intent
- `zigux/tests/phase11_dw_wdt.zig` and `Documentation/zigux/phase11-dw-wdt-slice.md` keep that starter reviewable without claiming platform registration, live MMIO, IRQ wiring, PM behavior, or hardware-backed execution
- `include/uapi/linux/watchdog.h` and `include/linux/watchdog.h` still own `struct watchdog_info`, the `WDIOC_*` ioctl numbers, the `WDIOF_*` or `WDIOS_*` option flags, and the shared `watchdog_device` or `watchdog_ops` core surface, so the current dw_wdt slice stops at driver-side bookkeeping instead of claiming public-header or watchdog-core parity
- `zigux/tests/phase11_build.zig` now runs the gpio starter checks, bcm2835 starter and survey checks, the dw_wdt starter checks, and the dw_wdt survey check together so watchdog-lane drift is visible in one place

This lane still does not claim platform-driver registration, clock or reset acquisition, IRQ registration, suspend or resume handling, debugfs support, live MMIO access, or hardware validation coverage.

The next honest bounded step inside the same lane is to add a tiny platform-resource preflight around timer-clock choice, optional APB clock presence, reset-control availability, and optional pretimeout-IRQ wiring before any live devm calls or watchdog registration work lands.
