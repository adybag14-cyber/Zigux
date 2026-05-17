# Phase 11 BCM2835 Watchdog Platform Validation Plan

This plan records the first explicit validation boundary for any future `bcm2835_wdt` work that grows beyond the current bounded starter packet.

## Status
- `PHASE11_BCM2835_WDT_PLATFORM_VALIDATION_PLAN=starter_boundary_recorded`
- roadmap phase: `Phase 11`
- Linux anchor: `drivers/watchdog/bcm2835_wdt.c`
- scope: future platform-registration, PM-base, watchdog-core, and shared poweroff-handler behavior for the bcm2835 watchdog packet only
- current directly readable packet remains the bounded starter in `drivers/watchdog/bcm2835_wdt.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `Documentation/zigux/phase11-bcm2835-wdt-slice.md`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`, and `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`

## Purpose
The current bcm2835 packet already makes timeout conversion, probe ownership, platform-handoff prerequisites, restart or poweroff intent, and remove-time teardown reviewable without claiming live platform-backed execution. This plan exists so later work can widen that packet in one controlled direction instead of informally drifting into PM-base plumbing or callback ownership claims.

## Validation Stages
1. Starter integrity stays mandatory.
- Keep the current dedicated replay, verify helper, survey gate, teardown note, validation matrix, manifest, and slice note aligned before any wider platform-facing change lands.
- Do not weaken the current blocked markers around live platform registration, PM-base execution, watchdog-core registration, or hardware-backed poweroff behavior.

2. Platform-registration preflight may widen first.
- Any new Zig surface for platform registration must stay summary-first.
- Required proof: explicit inputs and outputs for parent attachment, PM-base availability, timeout initialization intent, watchdog-device registration intent, restart priority, and poweroff-handler claim eligibility.
- Minimum checks: one driver-local replay, one tests-root replay, and one reminder-surface update that names the new preflight boundary without claiming a successful live registration call.

3. PM-base behavior needs dedicated failure-mode evidence.
- Before claiming PM-base-backed execution, add bounded proof for missing PM base, conflicting poweroff ownership, and registration-abort behavior.
- Required proof: fail-closed checks that later teardown or poweroff summaries still report blocked execution when PM-base prerequisites are absent.
- Do not collapse PM-base readiness into hardware-backed success.

4. Shared callback and watchdog-core claims need explicit teardown evidence.
- Any future claim about `pm_power_off` installation, watchdog-core registration, reboot coordination, or remove-time callback release must come with paired teardown checks.
- Required proof: ownership-preserving replay for claimed, conflicting, and unrelated callback states plus remove-time behavior that does not clear non-bcm2835 ownership.

5. Hardware-backed validation stays last.
- No note in this packet should claim real board-backed restart, stop, or poweroff execution until the lane records an environment, trigger, expected observation, and rollback owner.
- The first hardware-backed step should stay bcm2835-local and should record what is observed at the watchdog register and poweroff boundary, not broader shared Phase 11 behavior.

## Guardrails
- Keep this plan inside the bcm2835 watchdog packet only.
- Do not use it to reopen `gpio_wdt`, `dw_wdt`, HVC, or shared Phase 11 wording.
- Treat this as a validation-governance document, not proof that wider platform behavior is already implemented.
- If a later lane cannot produce the required proof for one stage, keep that stage blocked and leave the starter packet as the published boundary.

## Next Bounded Step
The next honest bcm2835-only follow-through is to align the current survey note, validation matrix, and manifest wording so they point at this explicit validation plan as the blocker boundary for any future platform-registration or PM-base work.