# Phase 11 UAPI And Driver-Header Parity Survey

This survey note records the shared Phase 11 header boundary after re-reading `master` `27fdd21e0863cf0f8fbca7bb85b51d4dc465cb98` against the current simple-driver roadmap.

The live repo state is now:

- `drivers/watchdog/gpio_wdt.zig`, `drivers/watchdog/bcm2835_wdt.zig`, and `drivers/watchdog/dw_wdt.zig` now give the simple-driver watchdog tranche three bounded starters, but they still stop short of owning `include/uapi/linux/watchdog.h` or `include/linux/watchdog.h`
- the `dw_wdt` survey packet now records that `include/uapi/linux/watchdog.h` still owns `struct watchdog_info`, the `WDIOC_*` ioctl numbers, and the `WDIOF_*` plus `WDIOS_*` option surface, while `include/linux/watchdog.h` still owns the shared `watchdog_device` and `watchdog_ops` surface before the registration-facing handoff lands
- `drivers/tty/hvc/hvc_console.zig` still carries a tiny header-parity snapshot for `drivers/tty/hvc/hvc_console.h`, covering `MAX_NR_HVC_CONSOLES`, `HVC_ALLOC_TTY_ADAPTERS`, the `hv_ops` callback shape, and the exported `hvc_*` helper metadata without claiming tty registration or host-backed I/O
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md` now keeps that header checkpoint tied to the current bounded starter replay while the next honest follow-up remains the tty-registration and teardown handoff instead of broader shared-header ownership
- `zigux/tests/phase11_build.zig` and the shared `phase11_uapi_header_parity` survey gate keep this boundary evidence visible alongside the active starter and lane-local survey tests so later runs do not treat header checkpoints as simple-driver completion

That is real product progress because it keeps the current starter lanes honest about what they do and do not mirror from Linux, but it is still boundary evidence rather than full UAPI or shared-header parity.

This shared lane still does not claim full UAPI ownership, watchdog-core parity, tty-core parity, platform registration parity, host-backed I/O parity, or a reusable interop substrate for shared public headers.

The next honest bounded step is not another broad shared survey. Leave this lane closed unless a future Phase 11 driver starts mirroring new public-header constants or shared struct layouts. If that happens, add one driver-local checkpoint and route any lasting ownership claim to the Phase 3 interop substrate instead of treating it as simple-driver completion. Until then, let the active driver-local lanes continue with their already recorded ready-next steps: the `dw_wdt` registration-facing handoff and the `hvc_console` tty-registration plus teardown handoff.
