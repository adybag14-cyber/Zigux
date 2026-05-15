# Phase 11 Shared Replay Contract

This note records the bounded shared reminder surface for the current Phase 11 simple-driver tranche on `master`.
Direct GitHub contents reads for some current Phase 11 build and replay files can still return 404, so the shared contract must describe both the reminder surfaces and the raw-fallback materialization story honestly.

## Status

* `PHASE11_SHARED_REPLAY_STATUS=shared_packet_truthful`
* compatibility marker for coupled reminder notes: `PHASE11_SHARED_REPLAY_STATUS=closure_packet_reviewable`
* scope: keep the shared Phase 11 reminder packet honest while the current direct watchdog and HVC replay files stay bounded, reviewable, and separate from any broader closure claim

## Roadmap Anchor

* the product roadmap still defines Phase 11 as the simple-production-driver tranche for `drivers/watchdog/*.zig` and `drivers/tty/hvc/*.zig`
* the current shared Phase 11 task is reminder-surface truthfulness and checker discipline around the landed bounded replay packet
* driver-local teardown, survey, validation, registration, notifier, sysrq, and platform-backed follow-through still belong to the owning Phase 11 lanes

## Shared Reminder Surface On `master`

The active shared Phase 11 packet is currently reviewable through these shared reminder surfaces:

* `Documentation/zigux/phase11-shared-replay-contract.md`
* `Documentation/zigux/phase11-closure-note.md`
* `Documentation/zigux/phase11-driver-lane-sequencing.md`
* `scripts/zigux/check-phase11-shared-replay-contract.py`
* `scripts/zigux/check-phase11-shared-summary-surfaces.py`
* `scripts/zigux/check-phase11-build-inventory.py`
* `zigux/tests/fixtures/phase11_build_inventory.json`
* `zigux/Makefile`
* `.github/workflows/zigux-bootstrap.yml`

These shared surfaces keep the Phase 11 packet reviewable as a reminder-and-checker contract while the bounded build-backed replay files stay directly materialized through raw fallback on current `master`.

## Current Repo Reality

* direct GitHub contents reads can still return 404 for `zigux/tests/phase11_build.zig`
* direct GitHub contents reads still materialize `zigux/tests/fixtures/phase11_build_inventory.json`
* raw GitHub fallback confirms current `master` materializes `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `drivers/tty/hvc/hvc_console_verify.zig`
* the shared `zigux/tests/fixtures/phase11_build_inventory.json` stays part of the current reminder packet and records the shared test inventory, the dedicated HVC replay split, and the explicit shared replay markers beside `zigux/tests/phase11_build.zig`
* those explicit shared replay markers currently cover `zigux/tests/phase11_dw_wdt_suspend_resume.zig`, `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, and `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
* `make -C zigux phase11` and `make -C zigux phase11-hvc-survey` remain present in `zigux/Makefile`, and the bootstrap workflow still names the same routes, so treat them as landed bounded replay evidence even when the direct contents bridge still 404s
* no shared `validate-phase11.py`
* no shared `make -C zigux phase11-validate` target on `master`
* the shared packet currently uses the shipped `check-phase11-*.py` reminder scripts together with the materialized build-backed replay files and the landed inventory fixture rather than a broader validator stack

## Exact Current Checks

These are the exact bounded checks that keep the current shared packet deterministic and reviewable:

* shared reminder packet self-tests: `python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test`, `python3 scripts/zigux/check-phase11-shared-summary-surfaces.py --self-test`, and `python3 scripts/zigux/check-phase11-build-inventory.py --self-test`
* shared reminder packet live route: `make -C zigux phase11-contract`
* shared build replay: `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
* dedicated HVC archival packet self-test and live checker: `python3 scripts/zigux/check-phase11-hvc-survey-packet.py --self-test` and `python3 scripts/zigux/check-phase11-hvc-survey-packet.py`
* dedicated HVC archival replay route: `make -C zigux phase11-hvc-survey`
* aggregate wrapper: `make -C zigux phase11`

## Driver-Local Evidence That Still Stays Beside The Shared Route

The dedicated archival HVC evidence still stays explicit beside that shared route:

* bcm2835, gpio, HVC, and header-boundary notes plus their dedicated `check-phase11-*.py` scripts remain parked as continuity surfaces beside the shared packet
* DesignWare continuity on current `master` stays bounded to `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`; keep that smaller surviving DesignWare continuity packet explicit beside the shared reminder stack while platform-registration scaffolding remains the next same-lane follow-through, do not reintroduce the older DesignWare survey, slice, teardown, validation-matrix, manifest, survey-gate, or direct replay files as landed shared evidence until current reads materialize them again, and do not widen the compile-local teardown or restart proofs into broader hardware-backed closure
* the shared header-boundary packet stays bounded to `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, and `drivers/tty/hvc/hvc_console.h`; keep that public-surface packet explicit in shared summaries without widening it into broader tty-core or watchdog-core closure
* the dedicated HVC archival packet stays bounded to `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `drivers/tty/hvc/hvc_console.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, and `make -C zigux phase11-hvc-survey`; keep those landed bounded replay surfaces explicit in shared summaries without widening them into notifier, khvcd, or host-backed execution closure
* the materialized direct Zig driver and replay files stay bounded replay evidence; keep them explicit in shared summaries without treating them as proof of overall Phase 11 closure

## What This Contract Does Not Claim

* no overall simple-driver tranche closure
* no shared `validate-phase11.py` or `phase11-validate` route
* no broader platform registration, PM plumbing, tty registration, notifier execution, khvcd execution, sysrq dispatch, or hardware-backed validation beyond the current bounded replay packet and parked reminder notes

## Follow-Through Rule

Future shared Phase 11 work should stay inside the next smallest reminder-surface truthfulness repair.
Prefer one shared note or checker at a time so the shared reminder packet, the parked driver-local notes, and the inventory-backed build surfaces remain aligned with the files current `master` can actually materialize.
