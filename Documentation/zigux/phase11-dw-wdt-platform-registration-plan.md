# Phase 11 DesignWare Watchdog Platform Registration Plan

This note records the next bounded follow-up for the live Phase 11 DesignWare watchdog packet on current `master`.

## Why this step belongs next

The live repository still keeps the directly readable DesignWare lane reviewable through:
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` for the bounded acquisition-facing scaffold that keeps timer-clock, APB-clock, reset-release, optional pretimeout-IRQ acquisition, imported-running handoff, and the missing timer-clock failure path reviewable without widening into live platform behavior
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/check-phase11-build-inventory.py`, and `zigux/tests/fixtures/phase11_build_inventory.json` for the owner-lane continuity packet that keeps the broader DesignWare platform-registration follow-through explicit without widening it into live platform-driver execution or broader hardware-backed closure

Current direct readback in this run confirmed the registration scaffold plus those owner-lane continuity surfaces, while direct contents reads for `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, and `zigux/tests/phase11_dw_wdt_manifest.json` returned missing-file responses. Until a future reread materializes those paths again, this owner note should keep them framed as inventory-backed DesignWare packet members rather than directly readable current-`master` proof.

That means the honest next step is to keep the DesignWare owner packet aligned with the directly readable registration scaffold and the owner-lane continuity surfaces current `master` actually materializes while still parking the next implementation step on platform-backed registration scaffolding instead of widening into live platform behavior.

The inventory-backed DesignWare packet still reserves compile-local teardown ownership and restart failure-mode parity for `drivers/watchdog/dw_wdt_verify.zig`, so future owner-packet wording should keep that host-free failure-mode scope explicit while platform acquisition remains the only next implementation step, without presenting the verify file as directly reread evidence until a fresh readback confirms it again.

Current scaffold readback also already proves one bounded reset-side truthfulness point that this note should preserve: when timeout programming is present and the rest of the acquisition-facing handoff is ready, optional reset-control absence can still remain a ready-to-register scaffold branch while `reset_control_deassert` stays visible as an unrequested outcome rather than an implicit blocker.

The next bounded follow-up is still to attach the existing registration-facing handoff to one acquisition-facing platform-registration scaffold without widening into live clock, reset, IRQ, or MMIO behavior.

## Scope for the first platform-backed step

Keep the next implementation bounded to one acquisition-facing scaffold inside the surviving DesignWare packet without claiming a full probe path.

The preferred first packet is:
1. model timer-clock acquisition and optional APB clock acquisition as explicit outcome-bearing steps
2. model reset-control availability and reset-release intent as explicit outcome-bearing steps while preserving the already-readable ready-to-register branch when reset control is absent
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
- keep optional reset-control absence explicit as a ready-to-register scaffold branch so the bounded packet does not overstate reset wiring as mandatory before host-free registration review
- update this plan note and `scripts/zigux/check-phase11-dw-wdt-packet.py` together when the live DesignWare packet meaning changes; refresh the shared lane note or tests-root companion only when that shared owner map needs to change
- keep proof bounded to the checker self-test plus the narrowest truthful Zig-side review available for the next scaffold change
- keep the inventory-backed `drivers/watchdog/dw_wdt_verify.zig` failure-mode scope explicit and host-free so teardown ownership and restart failure-mode parity stay visible while platform-backed acquisition remains the next bounded follow-through
- refresh the shared tests-root companion or the shared lane-sequencing note only when a future DesignWare owner-packet change materially changes the shared owner map, not just because the directly readable registration scaffold and continuity packet is still being restated
- Phase 11 shared build replay only as a truthfulness check, not as a claim that hardware-backed behavior is complete

## Recommended file targets

- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `scripts/zigux/check-phase11-dw-wdt-packet.py`
- `drivers/watchdog/dw_wdt.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`

## Handoff

If a future run picks up this packet, keep it to one acquisition-facing helper or summary family only.
If clock acquisition lands first, leave reset wiring for the next bounded step. If reset acquisition lands first, leave clock-path execution for the next bounded step. When reset control is absent, keep the ready-to-register branch explicit instead of treating reset wiring as a blocked prerequisite. Keep the missing timer-clock failure path explicit until live acquisition exists.
Keep the directly readable registration-scaffold surface and the owner-lane continuity packet explicit while the next implementation step stays inside `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, and treat the broader DesignWare driver, verify, direct replay, survey, and manifest companions as inventory-backed continuity until a fresh reread confirms them again.
