# Phase 11 Shared Replay Contract

This note records the bounded shared reminder surface for the current Phase 11 simple-driver tranche on `master`.
Direct GitHub contents reads for the previously referenced Phase 11 build and replay files now return 404, so the shared contract must describe only materialized reminder surfaces plus the remaining repo-reality gaps.

## Status

* `PHASE11_SHARED_REPLAY_STATUS=shared_packet_truthful`
* compatibility marker for coupled reminder notes: `PHASE11_SHARED_REPLAY_STATUS=closure_packet_reviewable`
* scope: keep the shared Phase 11 reminder packet honest while the direct watchdog and HVC replay files plus the shared build entrypoint remain repo-reality gaps

## Roadmap Anchor

* the product roadmap still defines Phase 11 as the simple-production-driver tranche for `drivers/watchdog/*.zig` and `drivers/tty/hvc/*.zig`
* the current shared Phase 11 task is reminder-surface truthfulness and checker discipline until the missing direct build and replay files return
* driver-local teardown, survey, validation, registration, notifier, sysrq, and platform-backed follow-through still belong to the owning Phase 11 lanes

## Shared Reminder Surface On `master`

The active shared Phase 11 packet is currently reviewable through these shared reminder surfaces:

* `Documentation/zigux/phase11-shared-replay-contract.md`
* `Documentation/zigux/phase11-closure-note.md`
* `Documentation/zigux/phase11-driver-lane-sequencing.md`
* `scripts/zigux/check-phase11-shared-replay-contract.py`
* `scripts/zigux/check-phase11-shared-summary-surfaces.py`
* `zigux/Makefile`
* `.github/workflows/zigux-bootstrap.yml`

These shared surfaces keep the Phase 11 packet reviewable as a reminder-and-checker contract even though the direct build-backed replay files are not materialized today.

## Current Repo Reality

* direct GitHub contents reads do not materialize `zigux/tests/phase11_build.zig`
* direct GitHub contents reads also do not materialize the previously referenced direct replay files `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, and `drivers/tty/hvc/hvc_console_verify.zig`
* `make -C zigux phase11` and `make -C zigux phase11-hvc-survey` remain present in `zigux/Makefile`, and the bootstrap workflow still names the same routes, but treat them as reminder-only configuration markers until the missing Phase 11 build file and direct replay files land again
* no shared `validate-phase11.py`
* no shared `make -C zigux phase11-validate` target on `master`
* no shared `zigux/tests/fixtures/phase11_build_inventory.json`
* the shared packet currently uses the shipped `check-phase11-*.py` reminder scripts rather than a materialized build-backed replay stack

## Driver-Local Evidence That Still Stays Beside The Shared Route

* bcm2835, gpio, DesignWare, HVC, and header-boundary notes plus their dedicated `check-phase11-*.py` scripts remain parked as continuity surfaces beside the shared packet
* until the direct Zig driver and replay files return, treat those parked notes and checkers as reminder evidence rather than as proof that the corresponding direct Phase 11 build or replay files are present on current `master`

## What This Contract Does Not Claim

* no overall simple-driver tranche closure
* no materialized shared build-backed replay route on current `master`
* no direct bcm2835, gpio, DesignWare, or HVC verify-and-replay packet on current `master`
* no shared `validate-phase11.py` or `phase11-validate` route
* no platform registration, PM plumbing, tty registration, notifier execution, khvcd execution, sysrq dispatch, or hardware-backed validation beyond the parked reminder notes

## Follow-Through Rule

Future shared Phase 11 work should stay inside the next smallest reminder-surface truthfulness repair.
Prefer one shared note or checker at a time so the shared reminder packet, the parked driver-local notes, and the contributor-facing summaries remain aligned with the files current `master` can actually materialize.
