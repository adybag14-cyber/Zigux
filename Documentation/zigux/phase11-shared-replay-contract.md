# Phase 11 Shared Replay Contract

This note records the bounded shared reminder surface for the current Phase 11 simple-driver tranche on `master`.
The shared reminder packet should describe the files and routes that current `master` now materializes directly, so the delivery-tooling story stays reviewable without reviving removed validator surfaces.

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
* `Documentation/zigux/README.md`
* `Documentation/zigux/review-checklist.md`
* `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
* `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
* `scripts/zigux/README.md`
* `zigux/tests/README.md`

These shared surfaces keep the Phase 11 packet reviewable as a reminder-and-checker contract while the bounded build-backed replay files stay directly materialized on current `master`, and keep the broader contributor-facing packet aligned beside that checker-backed core instead of leaving those shared review surfaces implicit.
Keep the broader contributor-facing reminder honest too: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` should keep `scripts/zigux/check-phase11-build-inventory.py`, `zigux/tests/fixtures/phase11_build_inventory.json`, the exact shared `zig build test --build-file zigux/tests/phase11_build.zig --summary all` replay, `make -C zigux phase11-contract`, `make -C zigux phase11`, and `make -C zigux phase11-hvc-survey` explicit together instead of collapsing the inventory-backed shared packet back to helper-name-only wording.

## Current Repo Reality

* direct GitHub contents reads now materialize `zigux/tests/phase11_build.zig`
* direct GitHub contents reads now materialize `zigux/tests/fixtures/phase11_build_inventory.json`
* the shared `zigux/tests/fixtures/phase11_build_inventory.json` stays part of the current reminder packet and currently records fourteen Phase 11 build test names, thirteen shared `test_step.dependOn(...)` edges, one dedicated `hvc-console-survey` replay, and four explicit shared replay markers beside `zigux/tests/phase11_build.zig`
* `zigux/tests/phase11_build.zig` currently materializes thirteen shared `test_step.dependOn(...)` edges across gpio, bcm2835, DesignWare, header-parity, `hvc_console`, `hvc_console_verify`, and `hvc_cleanup`, plus one dedicated `hvc-console-survey` build step
* `make -C zigux phase11-contract`, `make -C zigux phase11`, and `make -C zigux phase11-hvc-survey` remain present in `zigux/Makefile`, and the bootstrap workflow still names the same shared and dedicated routes
* no shared `validate-phase11.py`
* no shared `make -C zigux phase11-validate` target on `master`
* the shared packet currently uses the shipped `check-phase11-*.py` reminder scripts together with the directly materialized build-backed replay files and the landed inventory fixture rather than a broader validator stack

## Exact Current Checks

These are the exact bounded checks that keep the current shared packet deterministic and reviewable:

* shared reminder packet self-tests: `python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test`, `python3 scripts/zigux/check-phase11-shared-summary-surfaces.py --self-test`, and `python3 scripts/zigux/check-phase11-build-inventory.py --self-test`
* shared reminder packet direct live checkers: `python3 scripts/zigux/check-phase11-shared-replay-contract.py`, `python3 scripts/zigux/check-phase11-shared-summary-surfaces.py`, and `python3 scripts/zigux/check-phase11-build-inventory.py`
* shared reminder packet live route: `make -C zigux phase11-contract`
* shared build replay: `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
* dedicated HVC archival packet self-test and live checker: `python3 scripts/zigux/check-phase11-hvc-survey-packet.py --self-test` and `python3 scripts/zigux/check-phase11-hvc-survey-packet.py`
* dedicated HVC archival replay routes: `zig build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all` and `make -C zigux phase11-hvc-survey`
* aggregate wrapper: `make -C zigux phase11`

## Driver-Local Evidence That Still Stays Beside The Shared Route

The dedicated archival HVC evidence still stays explicit beside that shared route:

* bcm2835, gpio, HVC, and header-boundary notes plus their dedicated `check-phase11-*.py` scripts remain parked as continuity surfaces beside the shared packet
* DesignWare continuity on current `master` stays bounded to `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`; keep that surviving DesignWare continuity packet explicit beside the shared reminder stack while platform-registration scaffolding remains the next same-lane follow-through, and do not reintroduce removed DesignWare survey, slice, teardown, validation-matrix, manifest, or direct replay surfaces as shared evidence until current direct reads materialize them again
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
