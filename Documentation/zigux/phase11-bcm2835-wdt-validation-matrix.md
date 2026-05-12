# Phase 11 BCM2835 Watchdog Validation Matrix

This document records the bounded bcm2835 watchdog validation matrix for the current Zigux Phase 11 simple-driver packet.

## Status

- `PHASE11_BCM2835_WDT_STATUS=platform_handoff_landed`
- archival packet identity remains `P11-L08` for traceability, while current scheduled watchdog-family continuity for this archived bcm2835 packet is tracked through `P11-L03`
- the last directly rechecked bcm2835 packet head recorded in this matrix is `55568844ac3ce835b0e0bef624c24c17f22b78a1`; public `master` has advanced since that packet-local replay pin
- scope: keep the current `bcm2835_wdt` packet honest about what is already reviewable in the driver-owned metadata, ownership, lifecycle, teardown, and register-state helpers without overclaiming full platform registration, PM base wiring, live poweroff coordination, or hardware-backed execution
- last directly rechecked focused replays at that packet-local head: `zig test zigux/tests/phase11_bcm2835_wdt.zig`, `zig test drivers/watchdog/bcm2835_wdt_verify.zig`, and `zig test zigux/tests/phase11_bcm2835_wdt_survey.zig`
- current shared replay boundary readback still shows that `zig build test --build-file zigux/tests/phase11_build.zig --summary all` includes `phase11-bcm2835-wdt-tests`, `phase11-bcm2835-wdt-verify-tests`, and `phase11-bcm2835-wdt-survey-tests`, and the shipped wrapper `make -C zigux phase11` still routes through that same shared packet

## Current Repo Reality

The live bcm2835 watchdog packet visible on `master` is:

- `drivers/watchdog/bcm2835_wdt.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `zigux/tests/phase11_bcm2835_wdt.zig`
- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `zigux/tests/phase11_bcm2835_wdt_survey.zig`
- `Documentation/zigux/phase11-bcm2835-wdt-slice.md`
- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`

The current driver file already keeps a bounded review packet around:

- `descriptor()` and `watchdogMetadataSummary()` for Linux-facing identity, timeout bounds, `WDIOF_SETTIMEOUT`, get-timeleft support, restart support, and starter capability coverage
- `registrationSummary()`, `registrationOutcomeSummary()`, `platformHandoffSummary()`, `poweroffSummary()`, `removeSummary()`, and `removeAfterRegistrationSummary()` for registration outcome failure boundary, shared system-poweroff callback ownership, PM-base-ready handoff posture, poweroff path summary, and remove-time teardown boundary
- `ownershipMatrixSummary()` for the claimed-handler, conflicting-handler, failed-registration, and not-system-power-controller paths
- `lifecycleMatrixSummary()` for the PM-base-available claimed-ready path, conflicting-handler path, failed-registration path, and non-system-power-controller path
- `start()`, `stop()`, `armRestart()`, `runtimeSnapshot()`, `secondsToTicks()`, `ticksToSeconds()`, and `ticksToMilliseconds()` for the register-state and restart-arm model

## Shared Replay Surface

The active watchdog validation packet still stays explicit inside the shared Phase 11 route:

- `phase11-bcm2835-wdt-tests`
- `phase11-bcm2835-wdt-verify-tests`
- `phase11-bcm2835-wdt-survey-tests`
- `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- `make -C zigux phase11`
- `zig test zigux/tests/phase11_bcm2835_wdt_survey.zig`

This bcm2835-local matrix does not claim that the whole current shared Phase 11 replay is green when unrelated non-watchdog drift can reopen elsewhere on `master`.

It also does not claim that the focused bcm2835 replays above were rerun on the newest public `master` head during this matrix refresh; only the shared build wiring and packet-local reminder surfaces were directly reread for this pass.

## Kernel-Integration Matrix

- watchdog metadata surface: `descriptor()` plus `watchdogMetadataSummary()` keep the Linux-facing anchor, human-readable identity, timeout bounds, `WDIOF_SETTIMEOUT`, get-timeleft support, restart support, and registration or poweroff-plumbing intent explicit.
- registration outcome failure boundary: `registrationOutcomeSummary()` and the focused driver-local tests keep success-versus-failure registration outcomes, claimed-versus-conflicting callback ownership, and fail-closed remove cleanup reviewable before any live watchdog-core registration side effects.
- poweroff path summary: `poweroffSummary()`, `drivers/watchdog/bcm2835_wdt_verify.zig`, and `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md` keep the shared system-poweroff callback ownership rule, halt-partition request, and short restart arm path readable without claiming board-backed shutdown execution.
- remove-time teardown boundary: `removeSummary()` and `removeAfterRegistrationSummary()` keep the owned-callback cleanup rule reviewable while leaving broader poweroff ordering and callback installation outside the driver-owned lab packet.
- ownership matrix: `ownershipMatrixSummary()` and its focused tests keep four bounded outcomes reviewable: claimed poweroff handler, conflicting pre-existing handler, failed registration, and non-system-power-controller registration that never claims shared poweroff ownership.
- lifecycle handoff matrix: `lifecycleMatrixSummary()` and its focused tests keep the PM-base-available claimed-ready path, conflicting-handler path, failed-registration path, and non-system-power-controller path readable through one bounded handoff matrix.
- runtime register model: `start()`, `stop()`, `armRestart()`, and `runtimeSnapshot()` keep the register-image model, full-reset request bit, halt-partition bit, restart arm path, and time-left derivation reviewable.
- out of scope for now: full platform registration, PM base ioremap, `platform_set_drvdata()` execution, `devm_watchdog_register_device()` side effects, probe-time MMIO execution, character-device behavior, and hardware-backed restart timing.

## Review Guardrails

- Treat this matrix as a truthfulness note for the current driver-owned bcm2835 packet, not as proof of live platform registration or hardware execution.
- Keep this matrix aligned with `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, and `scripts/zigux/check-phase11-bcm2835-wdt-packet.py` whenever ownership, lifecycle, or replay wording moves.
- Preserve the archival `P11-L08` packet identity in coupled survey surfaces unless a future run explicitly chooses a broader packet-identity rewrite.

## Next Blocked Step

The next honest bcm2835-only follow-up is still one explicit platform-registration or PM-base planning slice with the same bounded watchdog posture. Until then, keep the lane bounded to the driver, survey packet, verify replay, teardown note, and this matrix.