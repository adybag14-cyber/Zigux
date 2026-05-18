# Phase 11 Driver Lane Sequencing

This note keeps the active Phase 11 simple-driver packet split into bounded owner lanes while reflecting only the current-head reminder, checker, and scaffold surfaces that were directly reread in this run.

## Scope

Use this note when a Phase 11 change touches the shared reminder packet under `Documentation/zigux/phase11-*.md`, the coupled `scripts/zigux/check-phase11-*.py` review surfaces, the surviving proof-backed or scaffold-backed Phase 11 files under `zigux/tests/`, or the broad contributor-facing summaries.

## Lane Split

Keep the current lane split explicit:

- shared sequencing lane `P11-Y06` owns the shared reminder wording in `Documentation/zigux/phase11-driver-lane-sequencing.md` and `Documentation/zigux/phase11-validation-matrix-gap-survey.md` together with the smallest coupled checker updates needed to keep that shared packet honest
- bcm2835 continuity stays separate from the shared sequencing lane; current direct contents reads in this run did not rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, so shared-note work must keep bcm2835 reminder surfaces framed as same-lane repo-reality gaps until a fresh reread proves they returned
- gpio continuity stays separate from the shared sequencing lane; current direct contents reads in this run did not rematerialize `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, so shared-note work must keep gpio reminder surfaces framed as same-lane repo-reality gaps until a fresh reread proves they returned
- DesignWare lane `P11-L10` currently owns the narrower watchdog-local packet through `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`; current direct contents reads in this run did not rematerialize `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, or `scripts/zigux/check-phase11-dw-wdt-packet.py`, so keep those same-lane surfaces explicit as repo-reality gaps rather than current-head lane members
- HVC archival lane `P11-L16` currently keeps the directly readable `Documentation/zigux/phase11-hvc-console-validation-matrix.md` and `Documentation/zigux/phase11-hvc-verify-helper-boundary.md` authoritative for helper-local teardown and failure-mode evidence; keep the older direct driver, replay, survey-route, and teardown-note anchors framed as archival or repo-reality-gap vocabulary until a fresh reread proves they returned
- contributor-note lane `P11-L18` owns broad cross-phase reminder wording in `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
- shared header-boundary follow-through stays adjacent to `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`; do not fold that public-surface packet into the HVC archival lane or into driver-local watchdog packets

## Shared Packet Boundaries

Treat the current shared Phase 11 packet as the returned reminder surfaces that were directly readable in this run:

- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`

Current direct rereads in this run keep the shared reminder stack readable through the shared lane note, the validation-matrix gap survey, the DesignWare gap and plan notes, the DesignWare manifest-backed registration scaffold, the paired DesignWare checkers, and the two directly readable HVC helper-local reminder surfaces above.

The same direct rereads in this run did not rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, or the older DesignWare packet handle `scripts/zigux/check-phase11-dw-wdt-packet.py`, so shared sequencing work must not list those paths as current-head packet members until a future reread proves they returned.

`Documentation/zigux/phase11-hvc-console-validation-matrix.md` currently keeps the HVC lane explicit as the only directly readable driver-local Phase 11 validation matrix note on current `master`; do not use historical four-matrix wording while the watchdog matrices remain missing.

Keep platform-registration scaffolding and teardown or failure-mode parity distinct: `zigux/tests/phase11_dw_wdt_registration_scaffold.zig` is current-head DesignWare scaffold evidence, while the missing driver-local watchdog helper and matrix surfaces remain same-lane repo-reality gaps.

## Sequencing Rules

Use this note to keep the bounded work order honest:

1. Prefer one Phase 11 lane at a time instead of batching bcm2835, gpio, DesignWare, HVC, header-boundary, and contributor-note work into one mixed change.
2. Keep the shared-versus-dedicated split explicit: the shared sequencing lane owns reminder-surface truthfulness, not driver-local execution claims.
3. Keep the current readback boundary honest: today that means the HVC helper-local reminder packet plus the narrower DesignWare docs, manifest, scaffold, and checker packet; if a future reread restores another watchdog matrix or driver-local helper, refresh this sequencing note and the coupled gap survey or checkers in the same bounded pass.
4. Keep the DesignWare follow-through parked on platform-registration scaffolding and checker truthfulness; do not use missing helper, matrix, survey, slice, teardown-note, or replay names to imply teardown closure has returned.
5. Keep HVC helper-local teardown and failure-mode evidence routed through `Documentation/zigux/phase11-hvc-console-validation-matrix.md` and `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`; do not widen that packet into tty registration, notifier execution, khvcd execution, sysrq dispatch, or host-backed teardown.
6. Do not imply broader platform registration, PM plumbing, reset execution, IRQ execution, MMIO validation, notifier execution, sysrq execution, khvcd execution, or hardware-backed closure beyond the reminder notes, checkers, and scaffold file that were directly readable in this run.
7. When contributor-facing summaries reopen, keep them aligned with the current HVC-only driver-local matrix readback and the narrower DesignWare docs-and-scaffold packet instead of reviving older four-matrix or returned-helper wording.
8. Keep the next bounded shared follow-through inside the smallest reminder-surface truthfulness repair unless a later reread restores or removes another directly readable Phase 11 packet surface.

## Non-Goals

This note does not widen Phase 11 into:

- a claim that the overall simple-driver tranche is closed
- a claim that the missing shared-validator surfaces `scripts/zigux/validate-phase11.py` or `make -C zigux phase11-validate` are already present on current `master`
- a claim that the bcm2835, gpio, or DesignWare watchdog validation matrices are directly readable today
- a claim that `drivers/watchdog/dw_wdt.zig` or `drivers/watchdog/dw_wdt_verify.zig` have returned to direct current-head readback
- broader hardware-backed watchdog validation, tty registration parity, notifier execution, sysrq dispatch, khvcd execution, or host-backed teardown closure
- a migration of driver-local reminder ownership into the shared packet