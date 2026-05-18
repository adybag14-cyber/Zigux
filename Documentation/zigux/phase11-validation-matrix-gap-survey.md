# Phase 11 Validation Matrix Gap Survey

This note records the roadmap-facing validation-matrix coverage for the current
Phase 11 simple-driver packet on `master`.

## Status

- `PHASE11_MATRIX_GAP_STATUS=hvc_matrix_direct_readback_only`
- lane: `P11-L03`
- reviewed against live `master`
- scope: verify the current driver-local matrix packet against the directly
  readable HVC matrix, the three repo-reality-gap watchdog matrix note paths,
  and the adjacent shared header-boundary matrix, without reopening driver-local
  implementation or platform-backed execution

## Roadmap Anchor

- Phase 11 still names `drivers/watchdog/gpio_wdt.c`,
  `drivers/watchdog/bcm2835_wdt.c`, `drivers/watchdog/dw_wdt.c`, and
  `drivers/tty/hvc/hvc_console.c` as the simple-production-driver anchors.
- Phase 11 still requires a hardware validation matrix together with teardown or
  failure-mode parity.

## Current Repo Reality

- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-build-inventory.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`

Current direct contents reads in this run do not rematerialize
`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`,
`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, or
`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, so the shared matrix
packet is no longer an honest four-matrix direct-readback claim.

The only directly readable driver-local Phase 11 matrix note on current
`master` is `Documentation/zigux/phase11-hvc-console-validation-matrix.md`.

`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` remains
useful adjacent shared evidence, but it is not one of the driver-local Phase 11
validation matrices named by the roadmap.

`zigux/tests/fixtures/phase11_build_inventory.json` still records the narrower
current-head HVC continuity packet.

The shared build inventory now carries 3 HVC proof-backed build tests, 0 shared
 depend steps, 0 dedicated survey replays, and 3 proof adjunct replays.
That inventory does not stand in for a whole-Phase-11 replay roster while the
three watchdog-local matrix notes remain missing from direct readback.

## Validation Gate

- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-build-inventory.py`

## Matrix Survey

- `bcm2835_wdt`: current direct contents reads do not rematerialize
  `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, so keep the
  bcm2835 matrix note path framed as a repo-reality gap rather than current-head
  matrix proof until a future reread recovers it.
- `gpio_wdt`: current direct contents reads do not rematerialize
  `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, so keep the gpio
  matrix note path framed as a repo-reality gap rather than current-head matrix
  proof until a future reread recovers it.
- `hvc_console`: `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  is directly readable on current `master`, and the narrowed build inventory now
  keeps the HVC current-head continuity packet explicit through
  `phase11-hvc-hv-ops-layout-proof-tests`,
  `phase11-hvc-export-surface-layout-proof-tests`, and
  `phase11-hvc-cleanup-packet-proof`.
- `dw_wdt`: current direct contents reads do not rematerialize
  `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, so keep the
  DesignWare matrix note path framed as a repo-reality gap; the surviving
  DesignWare owner packet still stays reviewable through
  `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`,
  `zigux/tests/phase11_dw_wdt_manifest.json`, and
  `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` without pretending the
  missing matrix note has returned.

## Review Rules

- Treat this survey as current-head driver-local matrix truthfulness only, not
  as proof of full platform-backed closure for any Phase 11 driver lane.
- Do not use the returned HVC matrix, the adjacent header-parity matrix, or the
  surviving DesignWare owner packet to overclaim broader GPIO descriptor
  execution, watchdog-core registration side effects, notifier execution, khvcd
  execution, sysrq dispatch, MMIO behavior, or host-backed teardown.
- Keep `zigux/tests/fixtures/phase11_build_inventory.json` framed as the
  narrower HVC continuity packet rather than as a cross-driver replay roster.
- If one or more watchdog-local matrix notes rematerializes again or the HVC
  matrix disappears, update this survey and both matrix-gap checkers in the same
  bounded pass so the shared-packet description stays honest.
