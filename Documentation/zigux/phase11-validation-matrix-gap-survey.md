# Phase 11 Validation Matrix Gap Survey

This note records the roadmap-facing validation-matrix coverage for the current
Phase 11 simple-driver packet on `master`.

## Status

- `PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`
- lane: `P11-L05`
- reviewed against live `master`
- scope: compare the Phase 11 roadmap anchors against the current validation-matrix
  packet without reopening driver-local implementation, DesignWare
  platform-registration follow-through, or driver-local provenance cleanup

## Roadmap Anchor

- Phase 11 still names `drivers/watchdog/gpio_wdt.c`,
  `drivers/watchdog/bcm2835_wdt.c`, `drivers/watchdog/dw_wdt.c`, and
  `drivers/tty/hvc/hvc_console.c` as the simple-production-driver anchors.
- Phase 11 still requires a hardware validation matrix together with teardown or
  failure-mode parity.

## Current Repo Reality

- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `Documentation/zigux/phase11-dw-wdt-survey.md`
- `Documentation/zigux/phase11-dw-wdt-teardown-note.md`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_survey.zig`
- `zigux/tests/phase11_build.zig`

Current `master` ships the bounded DesignWare validation-matrix packet beside the
surviving owner-plan continuity note, so the shared matrix count is four rather
than three.

## Validation Gate

- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`

## Gap Survey

- `bcm2835_wdt`: validation matrix present through
  `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, and the bounded
  bcm2835 packet still keeps teardown, ownership, lifecycle, and register-model
  evidence reviewable.
- `gpio_wdt`: validation matrix present through
  `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, and the bounded
  gpio packet still keeps descriptor, drvdata, registration-handoff, and teardown
  checkpoints reviewable without overclaiming live platform behavior.
- `hvc_console`: validation matrix present through
  `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and the bounded
  archival packet still keeps teardown, sysrq-helper, notifier-edge, and direct
  companion evidence reviewable without widening into tty or hypervisor
  execution.
- `dw_wdt`: validation matrix present through
  `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, and the bounded
  DesignWare packet now keeps the survey note, teardown note, manifest-backed
  survey evidence, and shared `phase11_build.zig` replay route reviewable beside
  the surviving owner-plan continuity packet without overclaiming live
  platform-registration or MMIO behavior.

## Review Rules

- Treat this survey as shared matrix truthfulness only, not as proof that the
  DesignWare starter or its next platform-registration step is complete.
- Claim four live driver-local validation matrices on current `master`, with
  DesignWare now represented by the landed validation matrix plus the
  still-separate owner-plan continuity packet.
- If a future simple-driver matrix is removed or materially reframed, update this
  survey in the same patch so the roadmap-facing matrix count stays honest.
