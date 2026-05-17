# Phase 11 Validation Matrix Gap Survey

This note records the roadmap-facing validation-matrix coverage for the current
Phase 11 simple-driver packet on `master`.

## Status

- `PHASE11_MATRIX_GAP_STATUS=four_matrix_direct_readback_restored`
- lane: `P11-L05`
- reviewed against live `master`
- scope: compare the Phase 11 roadmap anchors against the current validation-matrix
  packet without reopening driver-local implementation, DesignWare
  platform-registration follow-through, or HVC cleanup-alignment checker repair

## Roadmap Anchor

- Phase 11 still names `drivers/watchdog/gpio_wdt.c`,
  `drivers/watchdog/bcm2835_wdt.c`, `drivers/watchdog/dw_wdt.c`, and
  `drivers/tty/hvc/hvc_console.c` as the simple-production-driver anchors.
- Phase 11 still requires a hardware validation matrix together with teardown or
  failure-mode parity.

## Current Repo Reality

- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`
- `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`

Current direct contents reads in this run did rematerialize
`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`,
`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`,
`Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and
`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, so the shared matrix
packet is once again an honest four-matrix direct-readback claim.

That restored direct-readback count does not erase driver-local caveats:

- the bcm2835 matrix now stays directly reviewable beside its dedicated survey
  gate and manifest-backed reminder packet
- the gpio matrix is directly readable again even while it still keeps the older
  main replay and shared build route archived inside the gpio-local packet
- the HVC matrix is directly readable again even while the broader HVC archival
  packet still stays execution-limited in the current survey and companion notes
- the DesignWare matrix is directly readable again even while
  `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md` still records
  packet-alignment follow-through around lane identity and surveyed pin drift

## Validation Gate

- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`

## Gap Survey

- `bcm2835_wdt`: the direct-readback matrix is back on current `master`, so keep
  the dedicated survey gate, manifest-backed reminder packet, and bounded
  starter coverage aligned instead of presenting bcm2835 as matrix-missing.
- `gpio_wdt`: the direct-readback matrix is back on current `master`, but its
  own note still keeps the older main replay and shared build route archived, so
  treat the recovered matrix as truthful current-head evidence without
  overclaiming the broader gpio replay packet.
- `hvc_console`: the direct-readback matrix is back on current `master`, but the
  surrounding HVC continuity notes still keep execution-facing limits explicit,
  so treat the restored matrix as direct evidence without implying live notifier,
  khvcd, sysrq, or host-backed teardown execution.
- `dw_wdt`: the direct-readback matrix is back on current `master`, but the
  active DesignWare follow-through still belongs to the packet-alignment drift
  recorded in `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`
  rather than to another missing-matrix claim.

## Review Rules

- Treat this survey as current-head matrix truthfulness only, not as proof of
  full platform-backed closure for any Phase 11 driver lane.
- Do not use the restored four-matrix readback count to overclaim live
  registration, notifier execution, khvcd execution, sysrq dispatch, reset
  wiring, or hardware-backed validation parity.
- If future direct contents reads lose one of the matrices again, update this
  survey and `scripts/zigux/check-phase11-matrix-gap-survey.py` in the same patch
  so the direct-readback count stays honest.
