# Phase 11 Shared Replay Contract

This note records the bounded shared reminder surface for the current Phase 11
simple-driver tranche on `master`.
The shared reminder packet should describe only the files and routes that
current `master` still materializes directly, so the delivery-tooling story
stays reviewable without reviving removed aggregate wrappers or older replay
surfaces that no longer exist in the shipped repo.

## Status

- `PHASE11_SHARED_REPLAY_STATUS=shared_packet_truthful`
- compatibility marker for coupled reminder notes:
  `PHASE11_SHARED_REPLAY_STATUS=closure_packet_reviewable`
- scope: keep the shared Phase 11 reminder packet honest while the current
  validation-matrix, DesignWare continuity, and HVC current-head proof packet
  stay bounded and reviewable beside the shared `phase11-validate` route

## Roadmap Anchor

- the product roadmap still defines Phase 11 as the simple-production-driver
  tranche for `drivers/watchdog/*.zig` and `drivers/tty/hvc/*.zig`
- the current shared Phase 11 task is reminder-surface truthfulness and checker
  discipline around the landed validation-first packet
- driver-local teardown, survey, validation, registration, notifier, sysrq, and
  platform-backed follow-through still belong to the owning Phase 11 lanes

## Shared Reminder Surface On `master`

The active shared Phase 11 packet is currently reviewable through these shared
reminder surfaces:

- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- `scripts/zigux/validate-phase11.py`
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
checker contract while the bounded driver-local matrices, DesignWare continuity,
and HVC proof-backed packet stay directly materialized on current `master`.

Keep the scripts-root reminder honest too: broader contributor-facing summaries
should keep `scripts/zigux/check-phase11-build-inventory.py`,
`scripts/zigux/check-phase11-matrix-gap-survey.py`,
`scripts/zigux/check-phase11-validation-matrix-gap-survey.py`,
`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`,
`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`,
`scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`,
`scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`,
`scripts/zigux/validate-phase11.py`, `zigux/tests/fixtures/phase11_build_inventory.json`,
and `make -C zigux phase11-validate` explicit together instead of reviving
removed `phase11-contract`, `phase11`, `phase11-hvc-survey`,
`check-phase11-shared-replay-contract.py`, `check-phase11-shared-summary-surfaces.py`,
or `zigux/tests/phase11_build.zig` routes.

## Current Repo Reality

- `zigux/Makefile` now materializes `make -C zigux phase11-validate`
- `zigux/Makefile` no longer materializes `make -C zigux phase11-contract`,
  `make -C zigux phase11`, or `make -C zigux phase11-hvc-survey`
- `.github/workflows/zigux-bootstrap.yml` now replays the shared Phase 11 packet
  through `make -C zigux phase11-validate` and does not name a separate
  dedicated HVC survey workflow step
- the shared packet now uses the shipped `check-phase11-*.py` reminder scripts,
  `scripts/zigux/validate-phase11.py`, the shared inventory fixture, and the
  directly materialized proof-backed build routes rather than the older wrapper
  family
- `zigux/tests/fixtures/phase11_build_inventory.json` now records the narrower
  HVC current-head continuity packet rather than a whole-Phase-11 replay roster
- that inventory currently records 3 build test names, 0 shared
  `test_step.dependOn(...)` edges, 0 dedicated survey replays, 3 shared adjunct
  proof replays, 3 adjunct build replays, and 8 HVC current-head exact command
  markers, while `scripts/zigux/validate-phase11.py` plus
  `make -C zigux phase11-validate` keep the broader matrix-gap,
  targetless-unregister, and DesignWare checker chain explicit beside that
  narrower inventory packet
- `zigux/tests/phase11_build.zig` is not part of the current shared packet on
  `master`

## Exact Current Checks

These are the exact bounded checks that keep the current shared packet
deterministic and reviewable:

- shared checker self-tests:
  `python3 scripts/zigux/check-phase11-build-inventory.py --self-test`,
  `python3 scripts/zigux/check-phase11-matrix-gap-survey.py --self-test`,
  `python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py --self-test`,
  `python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test`,
  `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py --self-test`,
  `python3 scripts/zigux/check-phase11-dw-wdt-teardown-packet.py --self-test`,
  and `python3 scripts/zigux/check-phase11-dw-wdt-verify-alignment.py --self-test`
- shared checker live routes:
  `python3 scripts/zigux/check-phase11-build-inventory.py`,
  `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`,
  `python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py`,
  `python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py`,
  `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`,
  `python3 scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`,
  and `python3 scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- shared validator route: `python3 scripts/zigux/validate-phase11.py`
- shared Makefile route: `make -C zigux phase11-validate`
- current `phase11-validate` proof fan-out:
  `zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig`,
  `zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig`,
  `zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig`,
  and `zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`
- workflow replay route: `make -C zigux phase11-validate`

## Driver-Local Evidence That Still Stays Beside The Shared Route

The dedicated driver-local evidence still stays explicit beside that shared
route:

- the shared matrix packet keeps `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`,
  `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`,
  `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and
  `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` explicit as the
  current four-driver validation-matrix roster
- DesignWare continuity on current `master` stays bounded to
  `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`,
  `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`,
  `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`,
  `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`,
  `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`,
  `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`,
  `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`,
  `zigux/tests/phase11_dw_wdt_manifest.json`,
  `zigux/tests/phase11_dw_wdt.zig`,
  `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`,
  `drivers/watchdog/dw_wdt_pm.zig`, and
  `drivers/watchdog/dw_wdt_pm_scaffold.zig`; keep that landed bounded
  DesignWare packet explicit beside the shared route while platform-backed
  registration, PM execution, IRQ execution, and MMIO follow-through remain the
  next same-lane work
- the shared header-boundary packet stays bounded to
  `Documentation/zigux/phase11-uapi-header-parity-survey.md`,
  `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`, and
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
- the materialized direct Zig driver and proof-backed replay files stay bounded
  evidence; keep them explicit in shared summaries without treating them as
  proof of overall Phase 11 closure

## What This Contract Does Not Claim

- no overall simple-driver tranche closure
- no `make -C zigux phase11-contract`, `make -C zigux phase11`, or
  `make -C zigux phase11-hvc-survey` route on current `master`
- no dedicated HVC survey workflow step on current `master`
- no shared `zigux/tests/phase11_build.zig` replay route on current `master`
- no `scripts/zigux/check-phase11-shared-replay-contract.py` or
  `scripts/zigux/check-phase11-shared-summary-surfaces.py` route on current
  `master`
- no broader platform registration, PM plumbing, tty registration, notifier
  execution, khvcd execution, sysrq dispatch, or hardware-backed validation
  beyond the current bounded replay packet and parked reminder notes

## Follow-Through Rule

Future shared Phase 11 work should stay inside the next smallest
reminder-surface truthfulness repair.
Prefer one shared note or checker at a time so the shared reminder packet, the
parked driver-local notes, and the inventory-backed validation surfaces remain
aligned with the files current `master` can actually materialize.
