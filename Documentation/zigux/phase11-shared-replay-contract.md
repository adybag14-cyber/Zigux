# Phase 11 Shared Replay Contract

This note records the bounded shared reminder surface for the current Phase 11
simple-driver tranche on `master`.
The shared reminder packet should describe the files and routes that current
`master` now materializes directly, so the delivery-tooling story stays
reviewable without reviving removed aggregate wrappers or dedicated survey
routes that no longer exist in the shipped repo.

## Status

- `PHASE11_SHARED_REPLAY_STATUS=shared_packet_truthful`
- compatibility marker for coupled reminder notes:
  `PHASE11_SHARED_REPLAY_STATUS=closure_packet_reviewable`
- scope: keep the shared Phase 11 reminder packet honest while the current
  watchdog and HVC build-backed replay files stay bounded, reviewable, and
  separate from any broader closure claim

## Roadmap Anchor

- the product roadmap still defines Phase 11 as the simple-production-driver
  tranche for `drivers/watchdog/*.zig` and `drivers/tty/hvc/*.zig`
- the current shared Phase 11 task is reminder-surface truthfulness and checker
  discipline around the landed bounded replay packet
- driver-local teardown, survey, validation, registration, notifier, sysrq, and
  platform-backed follow-through still belong to the owning Phase 11 lanes

## Shared Reminder Surface On `master`

The active shared Phase 11 packet is currently reviewable through these shared
reminder surfaces:

- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-closure-note.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `scripts/zigux/check-phase11-shared-replay-contract.py`
- `scripts/zigux/check-phase11-shared-summary-surfaces.py`
- `scripts/zigux/check-phase11-build-inventory.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

These shared surfaces keep the Phase 11 packet reviewable as a reminder and
checker contract while the bounded build-backed replay files stay directly
materialized on current `master`, and keep the broader contributor-facing packet
aligned beside that checker-backed core instead of leaving those shared review
surfaces implicit.

Keep the scripts-root reminder honest too: broader contributor-facing summaries
should keep `scripts/zigux/check-phase11-build-inventory.py`,
`zigux/tests/fixtures/phase11_build_inventory.json`, and
`make -C zigux phase11-validate` explicit together instead of reviving removed
`phase11-contract`, `phase11`, or `phase11-hvc-survey` Makefile wrappers.

## Current Repo Reality

- direct contents readback materializes `zigux/tests/phase11_build.zig`
- direct contents readback materializes
  `zigux/tests/fixtures/phase11_build_inventory.json`
- the shared `zigux/tests/fixtures/phase11_build_inventory.json` stays part of
  the current reminder packet and records fourteen Phase 11 build test names,
  thirteen shared `test_step.dependOn(...)` edges, one dedicated
  `hvc-console-survey` build step, and four explicit shared replay markers
  beside `zigux/tests/phase11_build.zig`
- `zigux/tests/phase11_build.zig` materializes thirteen shared
  `test_step.dependOn(...)` edges across gpio, bcm2835, DesignWare,
  header-parity, `hvc_console`, `hvc_console_verify`, and `hvc_cleanup`, plus
  one dedicated `hvc-console-survey` build step
- `zigux/Makefile` no longer materializes `make -C zigux phase11-contract`,
  `make -C zigux phase11`, or `make -C zigux phase11-hvc-survey`
- `zigux/Makefile` now materializes `make -C zigux phase11-validate`
- `.github/workflows/zigux-bootstrap.yml` now replays the shared Phase 11 packet
  through `make -C zigux phase11-validate` and does not name a separate
  dedicated HVC survey workflow step
- the shared packet now uses the shipped `check-phase11-*.py` reminder scripts,
  the inventory fixture, the dedicated `validate-phase11.py` validator route,
  and the directly materialized build-backed replay files rather than the older
  wrapper family

## Exact Current Checks

These are the exact bounded checks that keep the current shared packet
deterministic and reviewable:

- shared reminder packet self-tests:
  `python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test`,
  `python3 scripts/zigux/check-phase11-shared-summary-surfaces.py --self-test`,
  and `python3 scripts/zigux/check-phase11-build-inventory.py --self-test`
- shared reminder packet direct live checkers:
  `python3 scripts/zigux/check-phase11-shared-replay-contract.py`,
  `python3 scripts/zigux/check-phase11-shared-summary-surfaces.py`, and
  `python3 scripts/zigux/check-phase11-build-inventory.py`
- shared Makefile route: `make -C zigux phase11-validate`
- current `phase11-validate` fan-out:
  `python3 scripts/zigux/validate-phase11.py`,
  `zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig`,
  `zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig`,
  `zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig`,
  and `zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`
- shared build replay: `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- dedicated HVC archival replay still exists as the build-step-only route
  `zig build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all`
  through `zigux/tests/phase11_build.zig`, but not as a current Makefile or
  workflow wrapper
- workflow replay route: `make -C zigux phase11-validate`

## Driver-Local Evidence That Still Stays Beside The Shared Route

The dedicated archival HVC evidence still stays explicit beside that shared
route:

- bcm2835, gpio, HVC, and header-boundary notes plus their dedicated
  `check-phase11-*.py` scripts remain parked as continuity surfaces beside the
  shared packet
- DesignWare continuity on current `master` stays bounded to
  `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`,
  `Documentation/zigux/phase11-dw-wdt-survey.md`,
  `Documentation/zigux/phase11-dw-wdt-slice.md`,
  `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`,
  `Documentation/zigux/phase11-dw-wdt-teardown-note.md`,
  `scripts/zigux/check-phase11-dw-wdt-packet.py`,
  `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`,
  `zigux/tests/phase11_dw_wdt.zig`,
  `zigux/tests/phase11_dw_wdt_manifest.json`,
  `zigux/tests/phase11_dw_wdt_survey.zig`, and
  `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`; keep that landed
  bounded DesignWare packet explicit beside the shared reminder stack while
  platform-registration scaffolding remains the next same-lane follow-through,
  and do not widen the compile-local teardown or restart proofs into broader
  hardware-backed closure
- the shared header-boundary packet stays bounded to
  `Documentation/zigux/phase11-uapi-header-parity-survey.md`,
  `scripts/zigux/check-phase11-header-boundary-packet.py`,
  `zigux/tests/phase11_uapi_header_parity_survey.zig`, and
  `drivers/tty/hvc/hvc_console.h`; keep that public-surface packet explicit in
  shared summaries without widening it into broader tty-core or watchdog-core
  closure
- the current-head HVC packet stays bounded to
  `Documentation/zigux/phase11-hvc-console-validation-matrix.md`,
  `Documentation/zigux/phase11-hvc-console-survey.md`,
  `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`,
  `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`,
  `drivers/tty/hvc/hvc_console.zig`,
  `scripts/zigux/check-phase11-build-inventory.py`,
  `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`,
  `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`,
  `zigux/tests/fixtures/phase11_build_inventory.json`,
  `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`,
  `zigux/tests/phase11_hvc_export_surface_layout_build.zig`,
  `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`,
  `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`,
  `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`,
  `zigux/tests/phase11_hvc_cleanup_packet_build.zig`,
  `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`, and
  `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`; keep those
  bounded current-head replay surfaces explicit in shared summaries without
  widening them into notifier, khvcd, host-backed execution, or a removed
  dedicated wrapper claim
- the materialized direct Zig driver and replay files stay bounded replay
  evidence; keep them explicit in shared summaries without treating them as
  proof of overall Phase 11 closure

## What This Contract Does Not Claim

- no overall simple-driver tranche closure
- no `make -C zigux phase11-contract`, `make -C zigux phase11`, or
  `make -C zigux phase11-hvc-survey` route on current `master`
- no dedicated HVC survey workflow step on current `master`
- no broader platform registration, PM plumbing, tty registration, notifier
  execution, khvcd execution, sysrq dispatch, or hardware-backed validation
  beyond the current bounded replay packet and parked reminder notes

## Follow-Through Rule

Future shared Phase 11 work should stay inside the next smallest
reminder-surface truthfulness repair.
Prefer one shared note or checker at a time so the shared reminder packet, the
parked driver-local notes, and the inventory-backed build surfaces remain
aligned with the files current `master` can actually materialize.
