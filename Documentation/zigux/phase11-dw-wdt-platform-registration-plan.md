# Phase 11 DesignWare Watchdog Platform Registration Plan

This note records the first bounded follow-up for the Phase 11 DesignWare watchdog lane on current `master`.

## Why this step belongs next

The live repository does not currently ship a `dw_wdt` test packet, manifest, or driver-local replay surface under `zigux/tests/` or `drivers/watchdog/`.

That makes one bounded next step honest and useful before any wider hardware-backed parity claim: attach the existing platform-registration intent to the first real, reviewable DesignWare scaffold packet instead of letting reminder surfaces imply that scaffold has already landed.

## Scope for the first platform-backed step

Keep the next implementation bounded to a single scaffolding surface that makes clock or reset acquisition reviewable without claiming a full probe path.

The preferred first packet is:

1. model timer-clock acquisition and optional APB clock acquisition as explicit outcome-bearing steps
2. model reset-control availability and reset-release intent as explicit outcome-bearing steps
3. preserve the intended ordering around `platform_set_drvdata`, timeout-programming intent, stop-on-reboot intent, restart-priority sequencing, and `watchdog_register_device`
4. keep imported-running-state handoff reviewable when the timer starts hot

## Explicit non-goals

Do not widen this first scaffold into:

- live MMIO reads or writes
- devm-managed resource ownership claims
- IRQ request or handler execution
- suspend or resume behavior
- debugfs support
- devicetree TOP parsing beyond a bounded preflight summary
- bcm2835 watchdog work or unrelated Phase 11 console work

## Validation target

The first scaffold packet should stay publishable with bounded proof only:

- focused Zig tests for the new acquisition-order summary or summaries
- a survey or manifest update only if the new scaffold actually lands
- Phase 11 shared validation replay only as a truthfulness check, not as a claim that hardware-backed behavior is complete

## Recommended file targets

- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `zigux/tests/README.md`

Once the first real DesignWare scaffold lands, expand the packet deliberately into the owning test, manifest, survey, and driver-local surfaces rather than predeclaring them here.

## Handoff

If a future run picks up this packet, keep it to one acquisition-facing helper or summary family only. If clock acquisition lands first, leave reset wiring for the next bounded step. If reset acquisition lands first, leave clock-path execution for the next bounded step.