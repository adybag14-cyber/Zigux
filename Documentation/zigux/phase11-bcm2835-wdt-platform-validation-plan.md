# Phase 11 BCM2835 Watchdog Platform Validation Plan

This plan records the validation boundary for the current `bcm2835_wdt` packet after the first driver-return proof, its coupled verify helper, the returned manifest-backed closure, the returned teardown note, the new direct replay route, and the current-head validation matrix came back onto `master`.

## Status
- `PHASE11_BCM2835_WDT_PLATFORM_VALIDATION_PLAN=starter_boundary_recorded`
- roadmap phase: `Phase 11`
- Linux anchor: `drivers/watchdog/bcm2835_wdt.c`
- scope: future slice-note, platform-registration, PM-base, watchdog-core, and shared poweroff-handler behavior for the bcm2835 watchdog packet only
- current directly readable packet remains `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md`, `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt_build.zig`, `drivers/watchdog/bcm2835_wdt.zig`, and `drivers/watchdog/bcm2835_wdt_verify.zig`

## Purpose
The current bcm2835 packet now includes a bounded driver-return proof plus a coupled verify helper for timeout limits, restart constants, PM-base handoff gating, poweroff ownership outcomes, and teardown outcomes together with one returned manifest-backed closure, one teardown note, one dedicated direct replay route, and one validation matrix that keep the returned compile and reminder packet truthful. This plan exists so later work can widen the lane in one controlled direction instead of informally drifting into slice-note sprawl, PM-base plumbing, callback ownership claims, or stale reminder-surface restatements.

## Validation Stages
1. Reminder-packet integrity stays mandatory.
- Keep the current survey note, validation plan, teardown note, current-head validation matrix, focused reminder-packet replay, dedicated reminder-packet build route, returned manifest-backed closure, focused tests-root replay, dedicated direct replay route, minimal driver-return proof, and driver-backed verify helper aligned before any wider platform-facing change lands.
- Do not fabricate current-head proof for a slice note, live platform registration, watchdog-core registration, or hardware-backed poweroff behavior.

2. Driver-return proof, verify helper, manifest, direct replay, matrix, and teardown note stay bounded until platform-registration evidence lands.
- The current Zig surface is intentionally small and only proves timeout, restart, PM-base gating, poweroff ownership, and teardown summaries.
- Required proof for the next widening step: one validation-matrix-backed platform-registration or callback-ownership note that matches the current driver-local, verify-helper, direct-replay, teardown-note, and manifest boundary without claiming successful live registration or poweroff execution.

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
- If a later lane cannot produce the required proof for one stage, keep that stage blocked and leave the current reminder-plus-driver-plus-verify-plus-direct-replay-plus-manifest-plus-teardown-plus-matrix packet as the published boundary.

## Next Bounded Step
The next honest bcm2835-only follow-through is one platform-registration or shared-callback ownership step that matches the returned driver packet, verify helper, direct replay route, teardown note, manifest, and validation matrix first and only then widens into broader platform behavior.
