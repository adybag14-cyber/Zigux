# Phase 11 DesignWare Watchdog Survey

This survey note tracks the Phase 11 gap around `drivers/watchdog/dw_wdt.c` after re-reading `master` `be0f31bf64cdc200e2129992d1fed491b60fed2a`.

The live repo state is now:

- `drivers/watchdog/gpio_wdt.zig` and `drivers/watchdog/bcm2835_wdt.zig` already give the simple-driver watchdog tranche two landed Phase 11 footholds
- `drivers/watchdog/dw_wdt.zig` now ships the bounded DesignWare starter for fixed TOP timeout windows, reset-mode versus IRQ-mode timeout selection, pretimeout bookkeeping, register-image transitions, non-stoppable stop semantics, an explicit `summarizeTeardownLifecycle()` stop-and-restart helper, a tiny probe-time summary for fixed-versus-custom TOP sourcing plus already-running watchdog metadata, a small registration-facing handoff for watchdog info selection, parent linkage, driver-data setup, timeout-init intent, imported running-state bookkeeping, and register-device intent, and a tiny platform-resource preflight plus live resource-order summary for timer-clock choice, optional APB clock presence, reset-control availability, and optional pretimeout-IRQ wiring, plus the bounded tclk, optional pclk, reset, irq, and registration sequencing
- `zigux/tests/phase11_dw_wdt.zig`, `Documentation/zigux/phase11-dw-wdt-slice.md`, and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` now keep that starter reviewable without claiming platform registration, live MMIO, IRQ wiring, PM behavior, or hardware-backed execution
- `include/uapi/linux/watchdog.h` and `include/linux/watchdog.h` still own `struct watchdog_info`, the `WDIOC_*` ioctl numbers, the `WDIOF_*` or `WDIOS_*` option flags, and the shared `watchdog_device` or `watchdog_ops` core surface, so the current dw_wdt slice stops at driver-side bookkeeping instead of claiming public-header or watchdog-core parity
- `zigux/tests/phase11_build.zig` now runs the gpio starter checks, bcm2835 starter and survey checks, the dw_wdt starter checks, and the dw_wdt survey check together so watchdog-lane drift is visible in one place
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` now centralizes the fixed-TOP timeout evidence, IRQ pretimeout bookkeeping, imported running-state handoff evidence, explicit `summarizeTeardownLifecycle()` stop-and-restart failure-mode evidence, the landed platform-resource ordering surface, and the exact shared replay plus survey-specific replay commands in one place

This lane still does not claim platform-driver registration, live clock or reset acquisition, IRQ registration, suspend or resume handling, debugfs support, live MMIO access, or hardware validation coverage.

The next honest larger move is still blocked on platform-driver scaffold work such as live clock or reset acquisition, IRQ registration, watchdog registration execution, PM handling, and a hardware-validation plan.

Latest verification snapshot:

- lane key refreshed to `P11-L11` while keeping the same bounded DesignWare starter scope
- latest carried-forward shared replay status remains `PHASE11_VALIDATION=pass` for the landed starter packet
- `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- `zig test zigux/tests/phase11_dw_wdt_survey.zig`
- `python3 scripts/zigux/validate-phase11.py`
- observed outcome: the shared replay keeps `phase11-dw-wdt-tests` and `phase11-dw-wdt-survey-tests` visible in one place, while the standalone survey replay remains available for note drift without implying a standalone driver-test path outside `zigux/tests/phase11_build.zig`
