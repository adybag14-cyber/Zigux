# Phase 11 Shared Replay Contract

This note records the bounded shared replay surface for the active Phase 11 simple-driver tranche on current `master`.
The live shared packet is build-backed again on current `master`, but it remains a reminder-and-continuity surface rather than a claim of full simple-driver closure.

## Status

* `PHASE11_SHARED_REPLAY_STATUS=shared_packet_truthful`
* compatibility marker for coupled reminder notes: `PHASE11_SHARED_REPLAY_STATUS=closure_packet_reviewable`
* scope: keep the shared Phase 11 replay route and its adjacent dedicated archival evidence honest while deeper driver follow-through stays inside the owning Phase 11 lanes

## Roadmap Anchor

* the product roadmap still defines Phase 11 as the simple-production-driver tranche for `drivers/watchdog/*.zig` and `drivers/tty/hvc/*.zig`
* the shared packet should name the replay-backed surfaces that still exist together on current `master`
* driver-local teardown, survey, validation, registration, notifier, sysrq, khvcd, and platform-backed follow-through still belong to the owning Phase 11 lanes

## Shared Replay Surface On `master`

The active shared Phase 11 packet is currently reviewable through these shared surfaces:

* `Documentation/zigux/phase11-shared-replay-contract.md`
* `Documentation/zigux/phase11-closure-note.md`
* `Documentation/zigux/phase11-driver-lane-sequencing.md`
* `scripts/zigux/check-phase11-shared-replay-contract.py`
* `scripts/zigux/check-phase11-shared-summary-surfaces.py`
* `zigux/tests/phase11_build.zig`
* `make -C zigux phase11`

These shared surfaces keep the build-backed replay route explicit without implying a broader validator stack than the current shipped checkers and surveys.

## Current Repo Reality

* shared build replay: `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
* shared make replay: `make -C zigux phase11`
* no shared `validate-phase11.py`
* no shared `make -C zigux phase11-validate` target on `master`
* no shared `zigux/tests/fixtures/phase11_build_inventory.json`
* the shared packet uses the shipped `check-phase11-*.py` reminder scripts rather than the older preflight inventory stack
* `scripts/zigux/check-phase11-shared-summary-surfaces.py` remains available as a focused direct audit for the docs-root, scripts-root, tests-root, and checklist summaries when shared Phase 11 reminder wording moves
* the remaining bcm2835 and gpio watchdog evidence stays beside the shared route on their own packet-local validation, survey, teardown, checker, and manifest-backed reminder surfaces rather than being collapsed back into one generic shared note

## Driver-Local Evidence That Still Stays Beside The Shared Route

The DesignWare watchdog lane now keeps its surviving bounded reminder packet explicit beside that shared route:

* `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
* `scripts/zigux/check-phase11-dw-wdt-packet.py`

Treat `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` together with `scripts/zigux/check-phase11-dw-wdt-packet.py` as the current DesignWare continuity packet on `master`: they keep the next bounded step pinned to platform-backed registration scaffolding while the older manifest, survey, validation-matrix, and teardown reminder surfaces stay removed rather than being silently reintroduced as shared evidence.

The dedicated archival HVC evidence still stays explicit beside that shared route:

* `Documentation/zigux/phase11-hvc-console-slice.md`
* `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
* `Documentation/zigux/phase11-hvc-console-survey.md`
* `Documentation/zigux/phase11-hvc-console-teardown-note.md`
* `zigux/tests/phase11_hvc_console_modem_control_split.zig`
* `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
* `drivers/tty/hvc/hvc_console_sysrq.zig`
* `scripts/zigux/check-phase11-hvc-survey-packet.py`
* `zigux/tests/phase11_hvc_console_manifest.json`
* `zigux/tests/phase11_hvc_console_survey.zig`
* `make -C zigux phase11-hvc-survey`

Treat `Documentation/zigux/phase11-hvc-console-teardown-note.md` together with `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, and `make -C zigux phase11-hvc-survey` as the landed dedicated HVC archival evidence on current `master`, while direct `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, and `drivers/tty/hvc/hvc_console_verify.zig` stay recorded as the remaining repo-reality gaps rather than shared proof.

The shared header-boundary evidence also stays explicit beside that shared route:

* `Documentation/zigux/phase11-uapi-header-parity-survey.md`
* `scripts/zigux/check-phase11-header-boundary-packet.py`
* `zigux/tests/phase11_uapi_header_parity_manifest.json`
* `zigux/tests/phase11_uapi_header_parity_survey.zig`

## What This Contract Does Not Claim

* no overall simple-driver tranche closure
* no shared `validate-phase11.py` or `phase11-validate` route
* no platform registration, PM plumbing, tty registration, notifier execution, khvcd execution, sysrq dispatch, or hardware-backed validation beyond the shipped bounded surveys

## Follow-Through Rule

Future shared Phase 11 work should stay inside the next smallest reminder-surface truthfulness repair.
Prefer one shared note or checker at a time so the surviving replay route, the dedicated HVC archival route, the surviving DesignWare continuity packet, and the shared header-boundary evidence remain aligned with live `master`.
