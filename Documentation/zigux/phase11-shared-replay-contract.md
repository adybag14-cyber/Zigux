# Phase 11 Shared Replay Contract

This note records the bounded shared replay surface for the active Phase 11 simple-driver tranche on current `master`.
It now treats the shared Phase 11 packet as a reminder-and-continuity surface only, because the older build-backed replay packet that some earlier wording described is not present in the live tree.

## Status

* `PHASE11_SHARED_REPLAY_STATUS=shared_packet_drift_recorded`
* compatibility marker for the coupled closure note: `PHASE11_SHARED_REPLAY_STATUS=closure_packet_reviewable`
* scope: keep the surviving shared Phase 11 closure surface honest while broader teardown, failure-mode, and execution-facing follow-through stays inside the owning driver lanes

## Roadmap Anchor

* the product roadmap still defines Phase 11 as the simple-production-driver tranche for `drivers/watchdog/*.zig` and `drivers/tty/hvc/*.zig`
* the shared packet should name only the reminder surfaces that still exist together on current `master`
* driver-local teardown, survey, validation, registration, notifier, sysrq, khvcd, and platform-backed follow-through still belong to the owning Phase 11 lanes

## Shared Replay Surface On `master`

The active shared Phase 11 packet is currently limited to these surviving shared surfaces:

* `Documentation/zigux/phase11-shared-replay-contract.md`
* `Documentation/zigux/phase11-closure-note.md`
* `Documentation/zigux/phase11-driver-lane-sequencing.md`
* `scripts/zigux/check-phase11-shared-replay-contract.py`

These shared surfaces keep the closure posture explicit and fail-closed even though the earlier build-backed replay bundle is no longer present in this tree.

## Current Repo Reality

* there is no shared `zigux/tests/phase11_build.zig` on current `master`
* there is no shared `zigux/tests/fixtures/phase11_build_inventory.json`
* there is no shared `make -C zigux phase11` route in this tree
* there is no shared `make -C zigux phase11-hvc-survey` route in this tree
* there is no shared `validate-phase11.py` on current `master`
* there is no broader shared Phase 11 validator stack beyond the surviving `check-phase11-*.py` reminder scripts

## Driver-Local Evidence That Still Stays Beside The Shared Route

The shared packet no longer claims one combined replay bundle. Instead, it points at the still-present adjacent lane surfaces:

* bcm2835 watchdog continuity: `Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md`, `scripts/zigux/check-phase11-bcm2835-archival-continuity.py`, `scripts/zigux/check-phase11-bcm2835-shared-replay-surface.py`, and `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`
* gpio watchdog continuity: `Documentation/zigux/phase11-gpio-wdt-module-slice.md`, `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`, and `scripts/zigux/check-phase11-gpio-wdt-platform-scaffold.py`
* DesignWare planning continuity: `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-failure-matrix.py`, and `scripts/zigux/check-phase11-dw-wdt-packet.py`
* HVC archival continuity: `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `scripts/zigux/check-phase11-hvc-archival-continuity.py`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, `scripts/zigux/check-phase11-hvc-teardown-failure-packet.py`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, and `zigux/tests/phase11_hvc_console_survey.zig`
* shared header-boundary continuity: `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/check-phase11-header-boundary-current-contract.py`, and `zigux/tests/phase11_uapi_header_parity_survey.zig`

## What This Contract Does Not Claim

* no live shared build replay packet for Phase 11
* no live shared watchdog or HVC starter tests in the current tree
* no live Makefile-backed Phase 11 replay route
* no overall simple-driver tranche closure
* no platform registration, PM plumbing, tty registration, notifier execution, khvcd execution, sysrq dispatch, or hardware-backed validation

## Follow-Through Rule

Future shared Phase 11 work should stay inside the next smallest reminder-surface truthfulness repair.
Prefer one shared note or checker at a time until the surviving closure surfaces stop naming missing build routes, missing replay files, or missing helper files.