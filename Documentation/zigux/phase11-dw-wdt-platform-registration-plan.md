# Phase 11 DesignWare Watchdog Platform Registration Plan

This note records the next bounded follow-up for the surviving Phase 11 DesignWare watchdog packet on current `master`.

## Why this step belongs next

The live repository still keeps the DesignWare lane reviewable through:

- `drivers/watchdog/dw_wdt.zig` for bounded TOP timeout windows, reset-versus-IRQ timeout selection, register-image transitions, probe-time bookkeeping, and registration-facing handoff summaries
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, and `scripts/zigux/check-phase11-dw-wdt-packet.py` for the surviving owner-lane continuity packet, pinned to `P11-L10`
- direct teardown and failure-mode parity stays as a future same-lane follow-through target rather than shipped current-`master` evidence through `drivers/watchdog/dw_wdt_verify.zig`

That means the honest next step is no longer to pretend the older DesignWare manifest, survey, validation-matrix, or teardown packet is still shipped on current `master`.

The next bounded follow-up is still to attach the registration-facing handoff to one acquisition-facing platform-registration scaffold without widening into live platform behavior.

## Scope for the first platform-backed step

Keep the next implementation bounded to one acquisition-facing scaffold inside the surviving DesignWare packet without claiming a full probe path.

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

- update this plan note, `Documentation/zigux/phase11-driver-lane-sequencing.md`, and `scripts/zigux/check-phase11-dw-wdt-packet.py` together when the DesignWare packet meaning changes
- keep proof bounded to the checker self-test plus the narrowest truthful Zig-side review available for the scaffold change
- create a new DesignWare manifest, survey, validation-matrix, or teardown surface only if a future scaffold lands enough new lane evidence to justify reviving it
- Phase 11 shared build replay only as a truthfulness check, not as a claim that hardware-backed behavior is complete

## Recommended file targets

- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `scripts/zigux/check-phase11-dw-wdt-packet.py`
- `drivers/watchdog/dw_wdt.zig`

## Handoff

If a future run picks up this packet, keep it to one acquisition-facing helper or summary family only. If clock acquisition lands first, leave reset wiring for the next bounded step. If reset acquisition lands first, leave clock-path execution for the next bounded step. If no scaffold lands yet, keep these reminder surfaces aligned with the surviving DesignWare packet instead of reviving removed manifest-backed evidence.
