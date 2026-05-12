# Phase 11 DesignWare Watchdog Platform Registration Plan

This note records the next bounded follow-up for the landed Phase 11 DesignWare watchdog packet on current `master`.

## Why this step belongs next

The live repository already ships a bounded `dw_wdt` packet under the DesignWare lane:

- `drivers/watchdog/dw_wdt.zig` keeps fixed and custom TOP timeout windows, reset-versus-IRQ timeout selection, register-image transitions, probe-time bookkeeping, and the registration-facing handoff reviewable
- `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, and `zigux/tests/phase11_dw_wdt_survey.zig` keep the current teardown, registration-order, and survey packet replayable
- `zigux/tests/phase11_dw_wdt_manifest.json`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, and `Documentation/zigux/phase11-dw-wdt-teardown-note.md` keep the current lane evidence and ownership boundaries explicit

That means the honest next step is no longer to invent a first DesignWare packet. The next bounded follow-up is to attach the already-landed registration-facing handoff to one acquisition-facing platform-registration scaffold while keeping the current validation matrix and teardown note as the lane's truth surfaces.

## Scope for the first platform-backed step

Keep the next implementation bounded to one acquisition-facing scaffold inside the existing DesignWare packet without claiming a full probe path.

The preferred first packet is:

1. model timer-clock acquisition and optional APB clock acquisition as explicit outcome-bearing steps
2. model reset-control availability and reset-release intent as explicit outcome-bearing steps
3. reuse the existing ordering around `platform_set_drvdata`, timeout-programming intent, stop-on-reboot intent, restart-priority sequencing, and `watchdog_register_device`
4. keep imported-running-state handoff reviewable when the timer starts hot

## Explicit non-goals

Do not widen this first scaffold into:

- live MMIO reads or writes
- devm-managed resource ownership claims
- IRQ request or handler execution
- suspend or resume behavior
- debugfs support
- devicetree TOP parsing beyond a bounded preflight summary
- shared Phase 11 reminder-surface churn outside the DesignWare packet
- bcm2835 watchdog work, gpio watchdog work, or unrelated Phase 11 console work

## Validation target

The first scaffold packet should stay publishable with bounded proof only:

- focused Zig tests for the new acquisition-order summary or summaries in `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` or a directly coupled DesignWare replay
- update `zigux/tests/phase11_dw_wdt_manifest.json` and `Documentation/zigux/phase11-dw-wdt-survey.md` only if the new scaffold changes shipped lane evidence
- update `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` only if the new scaffold changes the next hardware-validation checkpoint
- keep `Documentation/zigux/phase11-dw-wdt-teardown-note.md` unchanged unless `stop()`, `teardownSummary()`, or `removeSummary()` ownership actually moves
- Phase 11 shared build replay only as a truthfulness check, not as a claim that hardware-backed behavior is complete

## Recommended file targets

- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `drivers/watchdog/dw_wdt.zig`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `zigux/tests/phase11_dw_wdt_manifest.json` only if the scaffold lands or the next-step wording changes
- `Documentation/zigux/phase11-dw-wdt-survey.md` and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` only if the bounded packet evidence actually moves

## Handoff

If a future run picks up this packet, keep it to one acquisition-facing helper or summary family only. If clock acquisition lands first, leave reset wiring for the next bounded step. If reset acquisition lands first, leave clock-path execution for the next bounded step. If neither acquisition branch lands yet, keep this note aligned with the already-landed DesignWare packet instead of reopening shared Phase 11 reminder surfaces.