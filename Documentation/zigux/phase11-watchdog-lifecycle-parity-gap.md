# Phase 11 Watchdog Lifecycle Parity Gap

This note records the current lifecycle-parity gap between the two directly
readable Phase 11 watchdog packets on `master` that matter for this lane:
`bcm2835_wdt` and `dw_wdt`.

## Current Repo Reality

The current `bcm2835_wdt` survey packet records a starter-depth closure:
- `Documentation/zigux/phase11-bcm2835-wdt-survey.md` says the simple-driver
  roadmap gap is closed at starter depth on current `master`
- the same note keeps future follow-through outside more reminder-surface churn
  and points later work toward a driver-local or explicit validation-plan step

The current `dw_wdt` packet is narrower:
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` still
  frames the honest next step as one bounded acquisition-facing
  platform-registration scaffold
- `zigux/tests/phase11_dw_wdt_manifest.json` still keeps
  `phase11-dw-wdt-live-mmio-validation` at `ready_next`

That means current repo reality does not yet show straightforward lifecycle
parity between the two watchdog packets. The bcm2835 packet already reads as a
starter-complete lifecycle-backed slice, while the DesignWare packet still
keeps one narrower platform-registration follow-through open.

## Why This Lane Exists

This lane is not for widening either driver. It exists to keep Phase 11 review
surfaces truthful while the watchdog family remains split across different
bounded follow-through states.

The smallest honest same-lane move is to pin that asymmetry in one note and one
fail-closed checker so later reminder or matrix refreshes do not blur it into a
false parity claim.

## Non-Goals

This lane does not:
- reopen `drivers/watchdog/bcm2835_wdt.zig`
- reopen `drivers/watchdog/dw_wdt.zig`
- claim live platform registration, PM, IRQ, or MMIO parity for `dw_wdt`
- widen into `gpio_wdt`, `hvc_console`, or shared Phase 11 contributor-note
  churn

## Next Bounded Step

Keep future same-lane follow-through limited to refreshing this parity note and
its checker when either the bcm2835 survey packet or the DesignWare owner packet
materially changes. Any real parity closure belongs to a later DesignWare
implementation or validation step, not to reminder-surface wording alone.