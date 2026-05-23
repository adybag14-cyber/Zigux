# Phase 11 BCM2835 Watchdog Platform Validation Plan

This plan records the validation boundary for the current `bcm2835_wdt` packet after the first driver-return proof came back onto `master`.

## Status
- `PHASE11_BCM2835_WDT_PLATFORM_VALIDATION_PLAN=starter_boundary_recorded`
- roadmap phase: `Phase 11`
- Linux anchor: `drivers/watchdog/bcm2835_wdt.c`
- scope: future verify-helper, validation-matrix, platform-registration, PM-base, watchdog-core, and shared poweroff-handler behavior for the bcm2835 watchdog packet only
- current directly readable packet remains `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`, `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`, `drivers/watchdog/bcm2835_wdt.zig`, and `zigux/tests/phase11_bcm2835_wdt.zig`

## Purpose
The current bcm2835 packet now includes a bounded driver-return proof for timeout limits, restart constants, PM-base handoff gating, and poweroff ownership outcomes. This plan exists so later work can widen the lane in one controlled direction instead of informally drifting into verify-helper sprawl, PM-base plumbing, callback ownership claims, or stale reminder-surface restatements.

## Validation Stages
1. Reminder-packet integrity stays mandatory.
- Keep the current survey note, focused reminder-packet replay, dedicated build route, minimal driver-return proof, and focused tests-root replay aligned before any wider platform-facing change lands.
- Do not fabricate current-head proof for a verify helper, manifest-backed closure packet, slice note, teardown note, validation matrix, live platform registration, watchdog-core registration, or hardware-backed poweroff behavior.

2. Driver-return proof stays bounded until coupled proof returns.
- The current Zig surface is intentionally small and only proves timeout, restart, PM-base gating, and poweroff ownership summaries.
- Required proof for the next widening step: one coupled note or checker return that matches the current driver-local boundary without claiming successful live registration or poweroff execution.

3. Platform-registration and PM-base behavior need dedicated failure-mode evidence.
- Before claiming platform-backed execution, add bounded proof for missing PM base, conflicting poweroff ownership, and registration-abort behavior.
- Required proof: fail-closed checks that later teardown or poweroff summaries still report blocked execution when platform prerequisites are absent.

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
- If a later lane cannot produce the required proof for one stage, keep that stage blocked and leave the current reminder-plus-driver packet as the published boundary.

## Next Bounded Step
The next honest bcm2835-only follow-through is one explicit verify-helper or validation-matrix step that matches the returned driver packet first and only then widens into broader platform behavior.
