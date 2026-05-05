# Phase 11 Shared Replay Contract

This note records the current shared contributor replay surface for the shipped Phase 11 simple-driver packet on current `master`.

## Status

* `PHASE11_SHARED_REPLAY_STATUS=starter_packet_reviewable`
* scope: keep the current watchdog, shared header parity, and `hvc_console` starter tranche reviewable through one shared replay route while the dedicated archival `hvc_console` survey stays explicit and host-backed integration remains out of scope

## Current Shared Review Surface On `master`

* `Documentation/zigux/README.md`
* `scripts/zigux/README.md`
* `scripts/zigux/check-phase11-shared-replay-contract.py`
* `zigux/tests/README.md`
* `Documentation/zigux/review-checklist.md`
* `Documentation/zigux/phase11-shared-replay-contract.md`
* `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
* `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
* `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
* `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
* `Documentation/zigux/phase11-hvc-console-survey.md`
* `zigux/tests/phase11_build.zig`
* `zigux/tests/phase11_hvc_cleanup.zig`
* `zigux/tests/phase11_hvc_console_survey.zig`
* `zigux/Makefile`

## Shared Replay Commands

* `python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test`
* `python3 scripts/zigux/check-phase11-shared-replay-contract.py`
* `make -C zigux phase11-contract`
* `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
* `make -C zigux phase11`
* `zig build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all`
* `make -C zigux phase11-hvc-survey`

Inside that shared `phase11_build.zig` route, the watchdog, header-parity, and HVC starter replays stay bundled together:

* `zigux/tests/phase11_gpio_wdt.zig`
* `zigux/tests/phase11_gpio_wdt_survey.zig`
* `zigux/tests/phase11_bcm2835_wdt.zig`
* `zigux/tests/phase11_bcm2835_wdt_survey.zig`
* `zigux/tests/phase11_dw_wdt.zig`
* `zigux/tests/phase11_dw_wdt_survey.zig`
* `zigux/tests/phase11_uapi_header_parity_survey.zig`
* `zigux/tests/phase11_hvc_console.zig`
* `zigux/tests/phase11_hvc_cleanup.zig`

The dedicated archival HVC evidence stays explicit beside that shared route:

* `zigux/tests/phase11_hvc_console_survey.zig`
* `Documentation/zigux/phase11-hvc-console-survey.md`
* `Documentation/zigux/phase11-hvc-console-validation-matrix.md`

`Documentation/zigux/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/Makefile` keep that same shared-versus-dedicated replay split explicit, while `zigux/tests/phase11_hvc_cleanup.zig` keeps the bounded `hvc_cleanup()` tty-port release handoff, missing-reference failure mode, and teardown-gating replay reviewable without implying live tty teardown or host-backed cleanup.

## What This Contract Does Not Claim

* the shared `zig build test --build-file zigux/tests/phase11_build.zig --summary all` route does not run the dedicated `zigux/tests/phase11_hvc_console_survey.zig` archival survey replay
* the dedicated archival survey route stays separate through `zig build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all` and `make -C zigux phase11-hvc-survey`
* there is no dedicated shared `validate-phase11.py` or `phase11-validate` packet on current `master`; the shipped checker only keeps the shared-versus-dedicated replay contract fail-closed, and this replay contract still does not widen the Phase 11 surface into tty registration, notifier execution, khvcd execution, sysrq dispatch, platform registration, PM base plumbing, poweroff-handler coordination, or host-backed teardown validation

## Follow-Through Rule

Future Phase 11 follow-through should stay inside the next smallest hardware-validation matrix, focused replay, teardown-parity note, failure-mode note, registration-facing handoff note, or shared reviewability sync now that the shipped watchdog, header-boundary, HVC replay, and dedicated-survey split are explicit, and it should avoid broader validator expansion unless a smaller same-lane truthfulness gap is gone first.
