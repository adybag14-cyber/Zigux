# Phase 11 Shared Replay Contract

This note records the current shared contributor replay surface for the shipped Phase 11 simple-driver packet.

## Status

* `PHASE11_SHARED_REPLAY_STATUS=starter_packet_reviewable`
* scope: keep the current watchdog, shared header parity, and `hvc_console` starter tranche reviewable through one shared replay route while teardown and failure-mode parity stay explicit and host-backed integration remains out of scope

## Current Shared Review Surface On `master`

* `Documentation/zigux/README.md`
* `scripts/zigux/README.md`
* `zigux/tests/README.md`
* `Documentation/zigux/review-checklist.md`
* `Documentation/zigux/phase11-shared-replay-contract.md`
* `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
* `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
* `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
* `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
* `Documentation/zigux/phase11-hvc-console-survey.md`
* `scripts/zigux/validate-phase11.py`
* `scripts/zigux/check-phase11-build-inventory.py`
* `scripts/zigux/check-phase11-layout-assert-surface.py`
* `scripts/zigux/check-phase11-hvc-validation-flow.py`
* `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`
* `scripts/zigux/check-phase11-shared-replay-contract.py`
* `scripts/zigux/check-phase11-header-boundary-packet.py`
* `zigux/tests/phase11_build.zig`
* `zigux/tests/fixtures/phase11_build_inventory.json`
* `zigux/tests/phase11_uapi_header_parity_manifest.json`
* `zigux/tests/phase11_hvc_cleanup.zig`
* `zigux/tests/phase11_hvc_console_survey.zig`
* `zigux/Makefile`

## Shared Replay Commands

* `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
* `make -C zigux phase11`
* `python3 scripts/zigux/validate-phase11.py`
* `make -C zigux phase11-validate`

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

The dedicated archival HVC evidence still stays explicit beside that shared route:

* `zigux/tests/phase11_hvc_console_survey.zig`
* `Documentation/zigux/phase11-hvc-console-survey.md`
* `Documentation/zigux/phase11-hvc-console-validation-matrix.md`

`Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase11.py`, and `zigux/tests/fixtures/phase11_build_inventory.json` now keep that same shared-versus-dedicated replay split explicit, while `zigux/tests/phase11_hvc_cleanup.zig` keeps the bounded `hvc_cleanup()` tty-port release handoff, missing-reference failure mode, and teardown-gating replay reviewable without implying live tty teardown or host-backed cleanup.

## What This Contract Does Not Claim

* the shared `zig build test --build-file zigux/tests/phase11_build.zig --summary all` route still does not run the dedicated `zigux/tests/phase11_hvc_console_survey.zig` archival survey replay
* the dedicated archival survey route still stays separate through `make -C zigux phase11-hvc-survey`
* the Phase 11 validator stack and build-inventory fixture review the shared replay contract but do not widen this packet into tty registration, notifier execution, khvcd execution, sysrq dispatch, platform registration, PM base plumbing, poweroff-handler coordination, or host-backed teardown validation

## Follow-Through Rule

Future Phase 11 follow-through should stay inside the next smallest hardware-validation matrix, focused replay, teardown-parity note, failure-mode note, registration-facing handoff note, or shared reviewability sync now that the shipped watchdog, header-boundary, HVC replay, and validation packet are explicit, and it should avoid broader validator expansion unless a smaller same-lane truthfulness gap is gone first.
