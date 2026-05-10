# Phase 11 DesignWare Watchdog Platform Registration Plan

This note records the first bounded follow-up after the current `dw_wdt` starter, preflight, registration-order scaffold, and verify-backed teardown packet.

## Why this step belongs next

The live Phase 11 DesignWare packet already makes these review surfaces explicit in bounded form:

- timeout and pretimeout bookkeeping in `drivers/watchdog/dw_wdt.zig`
- platform-resource preflight and registration-order intent in the paired starter and scaffold packet
- teardown and failure-mode parity through `drivers/watchdog/dw_wdt_verify.zig`
- shared replay visibility through `zigux/tests/phase11_build.zig` and the Phase 11 validation matrix

That leaves one honest simple-driver gap before any wider hardware-backed parity claim: attach the existing preflight and ordering evidence to the first real platform-backed registration scaffold.

## Scope for the first platform-backed step

Keep the next implementation bounded to a single scaffolding surface that makes clock or reset acquisition reviewable without claiming a full probe path.

The preferred first packet is:

1. model timer-clock acquisition and optional APB clock acquisition as explicit outcome-bearing steps
2. model reset-control availability and reset-release intent as explicit outcome-bearing steps
3. preserve the already-landed ordering around `platform_set_drvdata`, timeout-programming intent, stop-on-reboot intent, restart-priority sequencing, and `watchdog_register_device`
4. keep imported-running-state handoff reviewable when the timer starts hot

## Explicit non-goals

Do not widen this first scaffold into:

- live MMIO reads or writes
- devm-managed resource ownership claims
- IRQ request or handler execution
- suspend or resume behavior
- debugfs support
- devicetree TOP parsing beyond the already-landed preflight summary
- bcm2835 watchdog work or unrelated Phase 11 console work

## Validation target

The first scaffold packet should stay publishable with bounded proof only:

- focused Zig tests for the new acquisition-order summary or summaries
- a survey or manifest update only if the new scaffold actually lands
- Phase 11 shared validation replay only as a truthfulness check, not as a claim that hardware-backed behavior is complete

## Recommended file targets

- `drivers/watchdog/dw_wdt.zig`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-survey.md`
- `zigux/tests/phase11_dw_wdt_manifest.json`

## Handoff

If a future run picks up this packet, keep it to one acquisition-facing helper or summary family only. If clock acquisition lands first, leave reset wiring for the next bounded step. If reset acquisition lands first, leave clock-path execution for the next bounded step.
