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
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-focused-direct-build-replays.py`
- `scripts/zigux/check-phase11-shared-replay-contract-counts.py`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- `scripts/zigux/validate-phase11.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `zigux/tests/README.md`

These shared surfaces keep the Phase 11 packet reviewable as a reminder and
checker contract while the bounded driver-local matrices, DesignWare continuity,
and HVC proof-backed packet stay directly materialized on current `master`.

Keep the broader reminder follow-through honest too: the shared reviewer-facing
checklist now carries the active Phase 11 packet, but broader contributor-facing
summaries in `scripts/zigux/README.md` still skip that active packet and live
current-`master` rereads also show `Documentation/zigux/README.md` still
skipping the active Phase 11 packet entirely, so treat those two broad surfaces
as the next same-lane reminder follow-through instead of as already current
packet members. Until that broader reminder work lands, keep the shared Phase 11
packet rooted in the narrower lane-sequencing, matrix-gap, checklist,
checker, workflow, contributor-sync, tests-root-companion, and tests-root
reminder stack listed above.

## Current Repo Reality

- `zigux/Makefile` now materializes `make -C zigux phase11-validate`
- `zigux/Makefile` no longer materializes `make -C zigux phase11-contract`,
  `make -C zigux phase11`, or `make -C zigux phase11-hvc-survey`
- `.github/workflows/zigux-bootstrap.yml` now replays the shared Phase 11 packet
  through `make -C zigux phase11-validate` and does not name a separate
  dedicated HVC survey workflow step
- the shared review checklist now carries the live Phase 11 packet, while the
  broader docs-root README and scripts-root README still skip it on current
  `master`, so do not treat those two broader reminders as current shared-packet
  proof until a future same-lane repair restores explicit simple-driver
  coverage there
- the shared packet now uses the shipped `check-phase11-*.py` reminder scripts,
  the validator self-test `python3 scripts/zigux/validate-phase11.py --self-test`,
  `scripts/zigux/validate-phase11.py`, the shared inventory fixture, and the
  directly materialized proof-backed build routes rather than the older wrapper
  family
- `zigux/tests/fixtures/phase11_build_inventory.json` now records the narrower
  HVC current-head continuity packet rather than a whole-Phase-11 replay roster
- that inventory currently records 3 build test names, 0 shared
  `test_step.dependOn(...)` edges, 0 dedicated survey replays, 3 shared adjunct
  proof replays, 3 adjunct build replays, 2 focused direct build checker
  routes, 2 focused direct build replays, and 11 HVC current-head exact command
  markers, while `python3 scripts/zigux/validate-phase11.py --self-test`,
  `scripts/zigux/validate-phase11.py`, and `make -C zigux phase11-validate`
  keep the broader matrix-gap, focused direct replay, targetless-unregister,
  DesignWare, bcm2835, and gpio checker chain explicit beside that narrower
  inventory packet.
  The same shared validator packet and `make -C zigux phase11-validate`
  wrapper now cover thirteen focused proof builds through
  `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`,
  `zigux/tests/phase11_dw_wdt_build.zig`,
  `zigux/tests/phase11_dw_wdt_restart_build.zig`,
  `zigux/tests/phase11_dw_wdt_pm_build.zig`,
  `zigux/tests/phase11_gpio_wdt_preflight_review_build.zig`,
  `zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`,
  `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig`,
  `zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig`,
  `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`,
  `zigux/tests/phase11_hvc_export_surface_layout_build.zig`,
  `zigux/tests/phase11_hvc_cleanup_packet_build.zig`,
  `zigux/tests/phase11_hvc_modem_control_proof_build.zig`, and
  `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`, so keep that
  thirteen-proof-build packet explicit instead of reducing the current shared gate to
  the narrower HVC inventory alone.
- the returned note-side `scripts/zigux/check-phase11-header-boundary-packet.py`
  route now sits beside that shared validator packet as reminder-surface
  truthfulness evidence for the narrower shared survey and validation-matrix
  notes; keep it explicit as returned note-side continuity without counting it
  as another HVC inventory marker or using it to claim that the removed shared
  replay files already returned
- `zigux/tests/phase11_build.zig` is not part of the current shared packet on
  `master`

## Exact Current Checks

These are the exact bounded checks that keep the current shared packet
deterministic and reviewable:

- shared validator self-test: `python3 scripts/zigux/validate-phase11.py --self-test`
- shared checker self-tests:
  `python3 scripts/zigux/check-phase11-build-inventory.py --self-test`,
  `python3 scripts/zigux/check-phase11-focused-direct-build-replays.py --self-test`,
  `python3 scripts/zigux/check-phase11-shared-replay-contract-counts.py --self-test`,
  `python3 scripts/zigux/check-phase11-matrix-gap-survey.py --self-test`,
  `python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py --self-test`,
  `python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test`,
  `python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test`,
  `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py --self-test`,
  `python3 scripts/zigux/check-phase11-dw-wdt-teardown-packet.py --self-test`,
  and `python3 scripts/zigux/check-phase11-dw-wdt-verify-alignment.py --self-test`
- shared checker live routes:
  `python3 scripts/zigux/check-phase11-build-inventory.py`,
  `python3 scripts/zigux/check-phase11-focused-direct-build-replays.py`,
  `python3 scripts/zigux/check-phase11-shared-replay-contract-counts.py`,
  `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`,
  `python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py`,
  `python3 scripts/zigux/check-phase11-header-boundary-packet.py`,
  `python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py`,
  `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`,
  `python3 scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`,
  and `python3 scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- shared validator route: `python3 scripts/zigux/validate-phase11.py`
- shared Makefile route: `make -C zigux phase11-validate`
- current `phase11-validate` proof fan-out:
  `zig build test --build-file zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`,
  `zig build test --build-file zigux/tests/phase11_dw_wdt_build.zig`,
  `zig build test --build-file zigux/tests/phase11_dw_wdt_restart_build.zig`,
  `zig build test --build-file zigux/tests/phase11_dw_wdt_pm_build.zig`,
  `zig build test --build-file zigux/tests/phase11_gpio_wdt_preflight_review_build.zig`,
  `zig build test --build-file zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`,
  `zig build test --build-file zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig`,
  `zig build test --build-file zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig`,
  `zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig`,
  `zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig`,
  `zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig`,
  `zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig`,
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
  `Documentation/zigux/phase11-dw-wdt-survey.md`,
  `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`,
  `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`,
  `zigux/tests/phase11_dw_wdt_manifest.json`,
  `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`,
  `zigux/tests/phase11_dw_wdt_survey.zig`,
  `drivers/watchdog/dw_wdt_restart.zig`,
  `drivers/watchdog/dw_wdt_pm.zig`, and
  `drivers/watchdog/dw_wdt_pm_scaffold.zig`; keep that returned smaller
  DesignWare packet explicit beside the shared route while the broader direct
  driver, verify-helper, replay-backed stack, platform-backed registration, PM
  execution, IRQ execution, and MMIO follow-through remain parked as the next
  same-lane work
- the shared header-boundary packet stays bounded to
  `Documentation/zigux/phase11-uapi-header-parity-survey.md`,
  `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`,
  `scripts/zigux/check-phase11-header-boundary-packet.py`, and
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
  `scripts/zigux/check-phase11-focused-direct-build-replays.py`,
  `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`,
  `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`,
  `zigux/tests/fixtures/phase11_build_inventory.json`,
  `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`,
  `zigux/tests/phase11_hvc_export_surface_layout_build.zig`,
  `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`,
  `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`,
  `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`,
  `zigux/tests/phase11_hvc_cleanup_packet_build.zig`,
  `zigux/tests/phase11_hvc_modem_control_proof.zig`,
  `zigux/tests/phase11_hvc_modem_control_proof_build.zig`,
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
- no `Documentation/zigux/README.md` or `scripts/zigux/README.md` Phase 11
  coverage on current `master`
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