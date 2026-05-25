# Phase 11 Watchdog Lifecycle Parity Gap

This note records the current lifecycle-parity gap between the two directly
readable Phase 11 watchdog packets on `master` that matter for this bounded
step: `bcm2835_wdt` and `dw_wdt`.

## Current Repo Reality

The current `bcm2835_wdt` packet now reads as a bounded current-driver-depth
closure:

- `Documentation/zigux/phase11-bcm2835-wdt-survey.md` says the Phase 11
  simple-driver roadmap gap is closed at bounded current-driver depth on
  `master`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` keeps the
  driver proof, verify helper, focused replay, and coupled reminder packet
  explicit without overclaiming live platform behavior

The current `dw_wdt` packet is still narrower:

- `Documentation/zigux/phase11-dw-wdt-survey.md` keeps the broader direct
  driver and direct replay stack outside the directly readable current-head
  packet
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` still treats the
  shared `zigux/tests/phase11_build.zig` route as a current-head gap
- `zigux/tests/phase11_dw_wdt_manifest.json` still keeps
  `phase11-dw-wdt-live-mmio-validation` at `ready_next`

That means current repo reality does not yet show straightforward lifecycle,
teardown, or hardware-validation parity between the two watchdog packets. The
bcm2835 packet already reads as a bounded current-driver-depth slice, while the
DesignWare packet still keeps hardware-backed MMIO validation and the broader
direct-driver stack outside the directly readable current-head packet.

## Why This Check Exists

This lane is not for widening either driver. It exists to keep the Phase 11
watchdog family truthful while the two owner packets still sit at different
bounded follow-through states.

The smallest honest same-lane move is to pin that asymmetry in one note and one
fail-closed checker so later reminder, matrix, or survey refreshes do not blur
it into a false lifecycle-parity claim.

## Non-Goals

This bounded parity note does not:

- reopen `drivers/watchdog/bcm2835_wdt.zig`
- reopen `drivers/watchdog/dw_wdt.zig`
- claim live platform registration, PM, IRQ, or hardware-backed MMIO parity for
  `dw_wdt`
- widen into `gpio_wdt`, `hvc_console`, or shared Phase 11 contributor churn

## Next Bounded Step

Keep future same-lane follow-through limited to refreshing this parity note and
its checker when either the bcm2835 current-driver packet or the DesignWare
owner packet materially changes.

Any real parity closure belongs to a later DesignWare implementation or
hardware-validation step, not to reminder-surface wording alone.
