# Phase 11 Helper Parity Matrix Expansion Survey

This note compares the current Phase 11 simple-driver packet against the roadmap's required feature set.
It keeps the per-lane validation matrices, surveys, manifests, and owner notes in one bounded roadmap-gap view without reclassifying any Phase 11 lane as hardware-ready or Phase 11-closed.

## Status

- `PHASE11_HELPER_PARITY_MATRIX_STATUS=roadmap_gap_map_reviewable`
- phase: `Phase 11`
- scope: compare the current `gpio_wdt`, `bcm2835_wdt`, `dw_wdt`, and `hvc_console` packets against the roadmap's direct-port, validation-matrix, and teardown or failure-mode expectations
- source packet for this survey: `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, and `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- roadmap anchor: Phase 11 still requires direct-port or dual-impl driver templates, a hardware validation matrix, and teardown plus failure-mode parity for `drivers/watchdog/*.zig` and `drivers/tty/hvc/*.zig`

## Roadmap Gap Matrix

| lane family | direct-port or bounded driver template | validation-matrix or owner-note evidence | teardown and failure-mode parity evidence | remaining roadmap-backed gap |
| --- | --- | --- | --- | --- |
| `bcm2835_wdt` | `drivers/watchdog/bcm2835_wdt.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, and `zigux/tests/phase11_bcm2835_wdt_survey.zig` keep timeout conversion, probe-summary ownership, PM-base handoff, and bounded runtime-model helpers directly reviewable on current `master` | `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` keeps the starter, verify helper, dedicated replay, and survey gate explicit as the current directly readable packet | the validation matrix, teardown note, and verify helper keep restart-versus-poweroff intent and bounded teardown wording reviewable without claiming platform-backed shutdown execution | the lane still stops short of manifest-backed closure, platform-driver registration, watchdog-core execution, and hardware-backed validation |
| `gpio_wdt` | `drivers/watchdog/gpio_wdt.zig` plus `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_gpio_wdt_survey.zig`, and `zigux/tests/phase11_gpio_wdt_platform_drvdata.zig` keep descriptor preflight, timeout bookkeeping, drvdata ordering, stop-policy, registration handoff, and teardown summary visible in bounded form | `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` keeps the visible starter and dedicated survey packet honest about what is directly readable on current `master` | the matrix, survey, manifest, and teardown note keep registration-failure and teardown wording explicit, and the focused drvdata replay keeps one ordering checkpoint reviewable | the lane still lacks a directly readable main replay, a shared-build-backed confirmation path, live GPIO acquisition, watchdog-core execution, and hardware-backed validation |
| `dw_wdt` | `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` keep timeout-window selection, reset-versus-IRQ posture, probe bookkeeping, restart failure-mode parity, and acquisition-facing scaffold steps reviewable on current `master` | `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` records the live owner packet as including the direct starter, survey, manifest, slice, validation-matrix, teardown note, and registration scaffold, while still parking the next same-lane step on platform-registration scaffolding | the direct verify helper, survey-backed packet, teardown note, and registration scaffold keep teardown ownership, restart failure modes, and missing-timer-clock blocking state explicit without widening into live platform behavior | the next roadmap-backed gap is still one acquisition-facing platform-registration scaffold step; timer-clock, reset, IRQ, MMIO, platform registration, and hardware-backed validation remain absent |
| `hvc_console` | `drivers/tty/hvc/hvc_console.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, `zigux/tests/phase11_hvc_console.zig`, and `zigux/tests/phase11_hvc_cleanup.zig` keep the starter, cleanup companion, verify helper, and sysrq helper packet directly reviewable | `Documentation/zigux/phase11-hvc-console-validation-matrix.md` keeps the archival survey packet, direct companions, dedicated survey route, and shared build inventory explicit | the validation matrix, teardown note, cleanup replay, modem-control split, poll-retry split, and verify helper keep bounded notifier-add, cleanup, remove, wakeup, and sysrq failure-mode wording reviewable | the lane still does not claim tty registration, notifier callback execution, khvcd execution, host-backed transport, or hardware-backed validation |

## Cross-Lane Readout

- All four Phase 11 roadmap anchors now have directly materialized Zig driver packets on current `master`, so the direct-port or bounded driver-template requirement is represented across the whole simple-driver tranche.
- All four lanes also carry matrix-style review notes, but those notes still record reviewability rather than hardware-backed proof. The repo has validation-matrix coverage for `bcm2835_wdt`, `gpio_wdt`, and `hvc_console`, while `dw_wdt` keeps its roadmap gap accounting split between the owner plan and the direct scaffold packet.
- Hardware-backed validation remains the shared Phase 11 blocker across every current lane. The repo is carrying bounded replay, survey, verify, and teardown evidence, not real board-backed or hypervisor-backed driver confirmation.
- Teardown and failure-mode parity is the strongest current Phase 11 signal. Each lane has a dedicated bounded packet for teardown, restart, cleanup, registration-failure, or sysrq-adjacent behavior, but none of those packets should be treated as proof of full lifecycle parity yet.

## Next Bounded Step

Keep follow-up work lane-local after this survey:

1. `bcm2835_wdt`: only extend the directly readable packet when the manifest-backed closure or slice surfaces materialize again.
2. `gpio_wdt`: prefer restoring the directly readable main replay or another one-step checkpoint inside the current survey-backed packet.
3. `dw_wdt`: keep the next change inside one acquisition-facing registration scaffold step.
4. `hvc_console`: keep the next repair inside one host-free notifier, remove, cleanup, or sysrq handoff boundary.

## Non-Goals

- no claim that Phase 11 is closed
- no claim that any current Phase 11 validation matrix is hardware-backed
- no shared-route rewrite or shared-summary packet expansion beyond this dedicated roadmap-gap survey
