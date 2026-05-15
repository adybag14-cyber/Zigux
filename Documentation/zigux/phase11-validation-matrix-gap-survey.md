# Phase 11 Validation Matrix Gap Survey

This note records the roadmap-facing validation-matrix coverage for the current Phase 11 simple-driver packet on `master`.

## Status

- `PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`
- lane: `P11-L01`
- reviewed against live `master`
- scope: compare the Phase 11 roadmap anchors against the current validation-matrix packet without reopening driver-local implementation, shared replay-contract wording, or DesignWare platform-registration scaffolding

## Roadmap Anchor

- Phase 11 still names `drivers/watchdog/gpio_wdt.c`, `drivers/watchdog/bcm2835_wdt.c`, `drivers/watchdog/dw_wdt.c`, and `drivers/tty/hvc/hvc_console.c` as the simple-production-driver anchors.
- Phase 11 still requires a hardware validation matrix together with teardown or failure-mode parity.

## Current Repo Reality

- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-survey.md`
- `Documentation/zigux/phase11-dw-wdt-slice.md`
- `Documentation/zigux/phase11-dw-wdt-teardown-note.md`
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `scripts/zigux/check-phase11-dw-wdt-packet.py`
- `drivers/watchdog/dw_wdt.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `zigux/tests/phase11_dw_wdt.zig`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `zigux/tests/phase11_dw_wdt_survey.zig`
- `zigux/tests/phase11_build.zig`

Current `master` now ships the bounded DesignWare review packet beside the surviving platform-registration continuity note, so the shared matrix survey should treat the DesignWare matrix as landed rather than as an open matrix-count gap.

## Gap Survey

- `bcm2835_wdt`: validation matrix present through `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, and the bounded bcm2835 packet still keeps teardown, ownership, lifecycle, and register-model evidence reviewable.
- `gpio_wdt`: validation matrix present through `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, and the bounded gpio packet still keeps descriptor, drvdata, registration-handoff, and teardown checkpoints reviewable without overclaiming live platform behavior.
- `hvc_console`: validation matrix present through `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and the bounded archival packet still keeps teardown, sysrq-helper, notifier-edge, and direct companion evidence reviewable without widening into tty or hypervisor execution.
- `dw_wdt`: validation matrix present through `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, and the bounded DesignWare packet keeps the direct starter replay, teardown or failure-mode parity, registration-order scaffold, shared build route, and deferred platform-backed registration gap reviewable without pretending that live clock, reset, IRQ, PM, or MMIO behavior is already complete.

## Review Rules

- Treat this survey as shared matrix truthfulness only, not as proof that the DesignWare starter or its platform-registration follow-through is complete.
- It is now accurate to claim four live driver-local validation matrices on current `master`; DesignWare is represented by the landed bounded review packet together with the surviving platform-registration continuity note.
- If a future DesignWare lane removes, broadens, or materially reframes that bounded matrix packet, update this survey in the same patch so the roadmap-facing matrix count stays honest.
