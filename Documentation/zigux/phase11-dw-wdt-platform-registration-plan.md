# Phase 11 DesignWare Watchdog Platform Registration Plan

This note records the next bounded follow-up for the live Phase 11 DesignWare watchdog packet on current `master`.

## Why this step belongs next

The live repository still keeps the DesignWare lane reviewable through:

- `drivers/watchdog/dw_wdt.zig` for bounded TOP timeout windows, reset-versus-IRQ timeout selection, register-image transitions, probe-time bookkeeping, registration-facing handoff summaries, teardown-adjacent remove summaries, and an explicit missing timer-clock block
- `drivers/watchdog/dw_wdt_verify.zig` for direct teardown ownership and restart failure-mode parity that stays compile-local and host-free beside the bounded driver packet
- `zigux/tests/phase11_dw_wdt.zig` for the direct starter replay that keeps fixed-top limits, custom-top ordering, timeout behavior, restart intent, non-stoppable stop semantics, and registration-facing handoff outputs reviewable without widening into live platform behavior
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` for the bounded acquisition-facing scaffold that keeps timer-clock, APB-clock, reset-release, optional pretimeout-IRQ acquisition, imported-running handoff, and the missing timer-clock failure path reviewable without widening into live platform behavior
- `zigux/tests/phase11_dw_wdt_survey.zig` and `zigux/tests/phase11_dw_wdt_manifest.json` for the survey-backed packet record that pins the current DesignWare starter to live `master`
- `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, and `Documentation/zigux/phase11-dw-wdt-teardown-note.md` for the driver-local review packet that keeps the starter, validation posture, and teardown companion aligned beside the shared Phase 11 surfaces
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, and `scripts/zigux/check-phase11-dw-wdt-packet.py` for the owner-lane continuity packet that should now describe that already-landed DesignWare review set truthfully

That means the honest next step is to keep the DesignWare owner packet aligned with the already-landed survey, manifest, slice, validation-matrix, teardown, starter, verify, and scaffold surfaces on current `master` while still parking the next implementation step on platform-backed registration scaffolding instead of widening into live platform behavior.

The next bounded follow-up is still to attach the existing registration-facing handoff to one acquisition-facing platform-registration scaffold without widening into live clock, reset, IRQ, or MMIO behavior.

## Scope for the first platform-backed step

Keep the next implementation bounded to one acquisition-facing scaffold inside the already-landed DesignWare packet without claiming a full probe path.

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
- shared Phase 11 reminder-surface churn outside the DesignWare owner packet
- bcm2835 watchdog work, gpio watchdog work, or unrelated Phase 11 console work

## Validation target

The first scaffold packet should stay publishable with bounded proof only:

- keep missing timer-clock acquisition blocked as a distinct scaffold state so the bounded packet does not imply registration is ready before timer-clock acquisition succeeds
- update this plan note and `scripts/zigux/check-phase11-dw-wdt-packet.py` together when the driver-local DesignWare packet meaning changes; refresh the shared lane note or tests-root companion only when that shared owner map needs to change
- keep proof bounded to the checker self-test plus the narrowest truthful Zig-side review available for the next scaffold change
- keep `drivers/watchdog/dw_wdt_verify.zig` compile-local and host-free so teardown ownership and restart failure-mode parity stay explicit while platform-backed acquisition remains the next bounded follow-through
- refresh the shared tests-root companion or the shared lane-sequencing note only when a future DesignWare owner-packet change materially changes the shared owner map, not just because the already-landed driver-local survey packet exists
- Phase 11 shared build replay only as a truthfulness check, not as a claim that hardware-backed behavior is complete

## Recommended file targets

- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `scripts/zigux/check-phase11-dw-wdt-packet.py`
- `drivers/watchdog/dw_wdt.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`

## Handoff

If a future run picks up this packet, keep it to one acquisition-facing helper or summary family only. If clock acquisition lands first, leave reset wiring for the next bounded step. If reset acquisition lands first, leave clock-path execution for the next bounded step. Keep the missing timer-clock failure path explicit until live acquisition exists. Keep the already-landed survey, manifest, validation matrix, and teardown companion explicit while the next implementation step stays inside `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` and `drivers/watchdog/dw_wdt.zig`.
