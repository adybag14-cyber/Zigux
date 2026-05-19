# Phase 11 Validation Matrix Gap Survey

This note records the roadmap-facing validation-matrix coverage for the current
Phase 11 simple-driver packet on `master`.

## Status

- `PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`
- lane: `P11-L01`
- reviewed against live `master`
- scope: verify the current driver-local matrix packet against the roadmap and
  the live bcm2835, gpio watchdog, HVC, and DesignWare matrix notes while
  keeping the narrower current-head HVC proof inventory explicit without
  reopening driver-local implementation or platform-backed execution

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

Current repo rereads in this run rematerialize all four driver-local Phase 11
matrix notes named by the roadmap, so the shared matrix packet should treat
bcm2835, gpio, HVC, and DesignWare as current reread matrix evidence while
keeping the narrower HVC current-head continuity packet explicit as adjacent
shared evidence.

The reread driver-local Phase 11 matrix notes on current `master` are
`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`,
`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`,
`Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and
`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`.

`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` remains
useful adjacent shared evidence, but it is not one of the driver-local Phase 11
validation matrices named by the roadmap.

`zigux/tests/fixtures/phase11_build_inventory.json` still records the narrower
current-head HVC continuity packet.

The shared build inventory now carries 3 HVC proof-backed build tests, 0 shared
depend steps, 0 dedicated survey replays, and 3 proof adjunct replays.
That inventory does not stand in for a whole-Phase-11 replay roster while the
current reread expansion is limited to the four driver-local matrix notes plus
the existing HVC continuity packet.

## Validation Gate

- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-build-inventory.py`

## Matrix Survey

- `bcm2835_wdt`: `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
  is directly readable on current `master`, and it keeps the bounded timeout,
  probe-summary, PM-base handoff, runtime register-model, restart-or-poweroff
  intent, dedicated survey-gate, and manifest-backed reminder packet explicit
  without claiming live platform registration or hardware-backed closure.
- `gpio_wdt`: `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` is
  directly readable on current `master`, and it keeps the bounded descriptor,
  platform-drvdata, teardown, registration-handoff, register-device request,
  and failure-mode parity review packet explicit without claiming live GPIO
  descriptor execution or platform registration.
- `hvc_console`: `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  is directly readable on current `master`, and the narrowed build inventory now
  keeps the HVC current-head continuity packet explicit through
  `phase11-hvc-hv-ops-layout-proof-tests`,
  `phase11-hvc-export-surface-layout-proof-tests`, and
  `phase11-hvc-cleanup-packet-proof`.
- `dw_wdt`: `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` is
  reread on current `master` through the returned DesignWare owner packet, and
  it keeps the bounded timeout-window, probe bookkeeping, registration-handoff,
  watchdog-header boundary, shared replay surface, and blocked platform-resource
  follow-up explicit without claiming live platform registration.

## Review Rules

- Treat this survey as current-head driver-local matrix truthfulness only, not
  as proof of full platform-backed closure for any Phase 11 driver lane.
- Do not use the returned bcm2835, gpio, HVC, and DesignWare matrix notes, the
  adjacent header-parity matrix, or the narrower HVC continuity packet to
  overclaim broader GPIO descriptor execution, watchdog-core registration side
  effects, notifier execution, khvcd execution, sysrq execution, MMIO behavior,
  or host-backed teardown.
- Keep all four reread driver-local matrix notes explicit in the shared packet
  while preserving the narrower HVC build inventory as adjacent continuity
  evidence rather than a cross-driver replay roster.
- If a reread driver-local matrix disappears, or if a future reread changes
  which matrix notes rematerialize on current `master`, update this survey and
  both matrix-gap checkers in the same bounded pass so the shared packet
  description stays honest.
