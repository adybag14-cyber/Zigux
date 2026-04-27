# Phase 11 UAPI And Driver-Header Parity Survey

This survey note records the shared Phase 11 header boundary after re-reading `master` `71c0ed93260f46dd1058e043c0bb111270628ca1`.

The live repo state is now:

- `drivers/watchdog/gpio_wdt.zig`, `drivers/watchdog/bcm2835_wdt.zig`, and `drivers/watchdog/dw_wdt.zig` now give the simple-driver watchdog tranche three bounded starters, but they still stop short of owning `include/uapi/linux/watchdog.h` or `include/linux/watchdog.h`
- the dw_wdt survey packet now records that `include/uapi/linux/watchdog.h` still owns `struct watchdog_info`, the `WDIOC_*` ioctl numbers, and the `WDIOF_*` or `WDIOS_*` option flags, while `include/linux/watchdog.h` still owns the shared `watchdog_device` and `watchdog_ops` surface
- the shared Phase 11 header survey gate now carries one bounded `layout_assert` checkpoint for `struct watchdog_info`, pinning size 40, alignment 4, and field offsets 0, 4, and 8 for `options`, `firmware_version`, and `identity[32]` without claiming full watchdog-core ownership
- `drivers/tty/hvc/hvc_console.zig` already carries a tiny header-parity snapshot for `drivers/tty/hvc/hvc_console.h`, covering `MAX_NR_HVC_CONSOLES`, `HVC_ALLOC_TTY_ADAPTERS`, the `hv_ops` callback shape, and the exported `hvc_*` helper metadata without claiming tty registration or host-backed I/O
- `zigux/tests/phase11_build.zig` now replays a shared Phase 11 UAPI or driver-header survey gate alongside the existing starter and lane-local survey tests so boundary drift is visible in one place

This shared lane still does not claim full UAPI ownership, watchdog-core parity, tty-core parity, or a reusable interop substrate for shared public headers.

The next honest bounded step is not another broad survey. Leave this lane closed unless a future Phase 11 driver starts mirroring public-header constants or shared struct layouts. If that happens, add one driver-local checkpoint and route any lasting ownership claim to the Phase 3 interop substrate instead of treating it as simple-driver completion.
