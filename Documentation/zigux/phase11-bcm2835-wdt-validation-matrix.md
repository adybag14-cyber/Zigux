# Phase 11 BCM2835 Watchdog Validation Matrix

This document restores the missing bcm2835 watchdog validation matrix for the current Zigux Phase 11 simple-driver packet.

## Status

- `PHASE11_BCM2835_WDT_STATUS=validation_matrix_restored`
- lane: `P11-Y02`
- reviewed against live `master` on `2026-05-11`
- scope: keep the current `bcm2835_wdt` packet honest about what is already reviewable in the driver-owned metadata, ownership, lifecycle, teardown, and register-state helpers without claiming the older dedicated survey or manifest packet is still present on `master`

## Current Repo Reality

The current bcm2835 watchdog packet visible on `master` is:

- `drivers/watchdog/bcm2835_wdt.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`

The current driver file already keeps a bounded review packet around:

- `descriptor()` and `watchdogMetadataSummary()` for Linux-facing identity, timeout bounds, and starter capability coverage
- `registrationOutcomeSummary()` and `removeAfterRegistrationSummary()` for shared `pm_power_off` ownership and remove-time cleanup decisions
- `ownershipMatrixSummary()` for the claimed-handler, conflicting-handler, failed-registration, and not-system-power-controller paths
- `lifecycleMatrixSummary()` for the platform handoff through PM-base readiness, drvdata readiness, register-device intent, poweroff ownership, and teardown outcomes
- `start()`, `stop()`, `armRestart()`, and `runtimeSnapshot()` for the register-state and restart-arm model

## Why This Exists

The live bcm2835 driver packet already carries real ownership and lifecycle evidence, but the dedicated validation-matrix note was missing from `master` while the teardown note and shared Phase 11 surfaces still referred to it. Restoring this file closes that matrix gap without widening the lane into new platform-registration code, PM-base plumbing, shared governance, or hardware-backed execution claims.

## Kernel-Integration Matrix

lane surface current evidence reviewable now next bounded follow-up out of scope for now
metadata and starter identity `descriptor()` plus `watchdogMetadataSummary()` in `drivers/watchdog/bcm2835_wdt.zig` and the driver-local descriptor and metadata tests keep the Linux-facing anchor, human-readable identity, timeout bounds, get-timeleft support, restart support, and registration or poweroff-plumbing intent explicit preserve the same helper and test coverage while any future replay stays bcm2835-only live watchdog-core registration, character-device behavior, and hardware-backed timeout execution
shared poweroff ownership `registrationOutcomeSummary()`, `poweroffSummary()`, `removeSummary()`, `removeAfterRegistrationSummary()`, `drivers/watchdog/bcm2835_wdt_verify.zig`, and `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md` keep the `pm_power_off == bcm2835_power_off` ownership rule, conflicting-handler fail-closed rule, claimed poweroff-ready path, and owned-callback remove-time cleanup rule reviewable keep the teardown note and verification replay aligned if callback wording or ownership branches move live callback installation, board-backed shutdown, and global poweroff ordering outside the driver-owned lab packet
ownership matrix `ownershipMatrixSummary()` and its focused driver-local tests keep four bounded outcomes reviewable: claimed poweroff handler, conflicting pre-existing handler, failed registration, and non-system-power-controller registration that never claims shared poweroff ownership preserve the same four-path matrix if a later bcm2835-only note or checker is restored broader shared Phase 11 checker growth, unrelated watchdog families, and platform-driver execution claims
lifecycle handoff matrix `lifecycleMatrixSummary()` and its focused driver-local tests keep the PM-base-available claimed-ready path, conflicting-handler path, failed-registration path, and non-system-power-controller path readable through one bounded handoff matrix preserve the same lifecycle matrix while any future bcm2835 packet restoration stays tied to this driver only live PM-base mapping, `platform_set_drvdata()` execution, `devm_watchdog_register_device()` side effects, and probe-time MMIO execution
runtime register model `start()`, `stop()`, `armRestart()`, `runtimeSnapshot()`, `secondsToTicks()`, `ticksToSeconds()`, and `ticksToMilliseconds()` keep the register-image model, full-reset request bit, halt-partition bit, restart arm path, and time-left derivation reviewable keep the runtime helper and direct tests aligned if timeout or restart constants move hardware-backed restart timing, reset propagation, and Raspberry Pi firmware or board behavior

## Review Guardrails

- Treat this matrix as a truthfulness note for the current driver-owned bcm2835 packet, not as proof of live platform registration or hardware execution.
- Do not claim that a dedicated bcm2835 survey gate, manifest-backed survey packet, or shared checker-backed replay is currently present on `master` unless those files are restored in the repo.
- If `registrationOutcomeSummary()`, `ownershipMatrixSummary()`, `lifecycleMatrixSummary()`, `poweroffSummary()`, `removeSummary()`, or the register-state helpers change, update this matrix together with `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md` so the lane keeps one honest ownership story.

## Next Blocked Step

The next honest bcm2835-only follow-up is to restore a directly coupled survey or manifest packet only after a future run can prove the exact current file set on `master` and keep the restored note or checker aligned with this driver-owned matrix. Until then, keep the lane bounded to the driver, verify replay, teardown note, and this matrix.
