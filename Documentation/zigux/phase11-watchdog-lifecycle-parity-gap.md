# Phase 11 Watchdog Lifecycle Parity Gap

This note records the current lifecycle-parity gap between the two directly
readable Phase 11 watchdog packets on `master` that matter for this bounded
step: `bcm2835_wdt` and `dw_wdt`.

## Current Repo Reality

The current `bcm2835_wdt` packet still reads as a bounded current-driver-depth
closure:

- `Documentation/zigux/phase11-bcm2835-wdt-survey.md` says the Phase 11
  simple-driver roadmap gap is closed at bounded current-driver depth on
  `master`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` keeps the
  driver proof, verify helper, focused replay, teardown note, manifest-backed
  closure, and coupled reminder packet explicit without overclaiming live
  platform behavior
- `zigux/tests/phase11_bcm2835_wdt_manifest.json` keeps the remaining
  follow-through blocked on current-head platform registration, shared
  poweroff-callback ownership, and hardware-backed validation

The current `dw_wdt` packet is stronger than an archival scaffold-only slice,
but it is still narrower than bcm2835 at the family lifecycle level:

- `Documentation/zigux/phase11-dw-wdt-survey.md` and
  `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` now keep the
  returned driver, direct tests-root replay, restart helper, verify helper,
  registration scaffold, and bounded PM-helper packet explicit on current
  `master`
- `zigux/tests/phase11_dw_wdt_manifest.json` still keeps
  `phase11-build-gate` as a shared current-head gap and leaves
  `phase11-dw-wdt-live-mmio-validation` at `ready_next`
- that means the current DesignWare packet has landed teardown and
  failure-mode starter coverage, but it still has a nearer next-step MMIO
  validation gap before it reads like the bcm2835 packet's bounded closure

That leaves family-level lifecycle parity intentionally asymmetric on current
`master`: bcm2835 reads as a bounded current-driver-depth closure with blocked
platform follow-through, while DesignWare reads as a returned starter-plus-test
packet whose next bounded step is still live MMIO validation around suspend,
resume, and platform-backed probe or remove execution.

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
