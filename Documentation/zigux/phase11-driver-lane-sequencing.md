# Phase 11 Driver Lane Sequencing

This note keeps the active Phase 11 simple-driver packet split into bounded owner lanes while reflecting only the current-head surfaces that were reread in this run.

## Scope

Use this note when a Phase 11 change touches the shared reminder packet under `Documentation/zigux/phase11-*.md`, the coupled `scripts/zigux/check-phase11-*.py` review surfaces, the proof-backed or scaffold-backed Phase 11 files under `zigux/tests/`, or the broad contributor-facing summaries.

## Lane Split

Keep the current lane split explicit:

- shared sequencing lane `P11-Y06` owns the shared reminder wording in `Documentation/zigux/phase11-driver-lane-sequencing.md` and `Documentation/zigux/phase11-validation-matrix-gap-survey.md` together with the smallest coupled checker updates needed to keep that shared packet honest
- bcm2835 continuity stays separate from the shared sequencing lane; this run reread the bcm2835 survey packet but did not re-open a broader bcm2835 reminder sweep, so keep bcm2835 follow-through bounded to its own same-family surfaces
- gpio continuity stays separate from the shared sequencing lane; current shared-note work should not reopen gpio reminder wording unless the gpio lane itself changes
- DesignWare lane `P11-L10` currently owns the narrower watchdog-local packet through `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`, `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`, `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`; keep `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, and the older `scripts/zigux/check-phase11-dw-wdt-packet.py` handle framed as repo-reality gaps or survey-recorded vocabulary until a future reread proves they returned on current `master`
- HVC archival lane `P11-L16` currently keeps the directly readable `Documentation/zigux/phase11-hvc-console-survey.md`, `drivers/tty/hvc/hvc_console.zig`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and `Documentation/zigux/phase11-hvc-verify-helper-boundary.md` authoritative for the current-head continuity packet and helper-local teardown or failure-mode evidence; keep the deeper replay, manifest, dedicated survey-checker, and teardown-note anchors framed as archival or repo-reality-gap vocabulary until a fresh reread proves they returned
- contributor-note lane `P11-L18` owns broad cross-phase reminder wording in `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
- shared header-boundary follow-through stays adjacent to `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`; do not fold that public-surface packet into the HVC archival lane or into driver-local watchdog packets

## Shared Packet Boundaries

Treat the current shared Phase 11 packet as the reminder surfaces that were directly reread in this run:

- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`
- `Documentation/zigux/phase11-dw-wdt-provenance-readback.md`
- `Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`
- `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `drivers/tty/hvc/hvc_console.zig`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`

Current exact contents reads in this run did not rematerialize `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, or `scripts/zigux/check-phase11-dw-wdt-packet.py`, so keep those DesignWare helper, replay, and reminder surfaces framed as repo-reality gaps or survey-recorded vocabulary instead of current-head same-lane evidence inside the shared owner map.

The same rereads also rematerialized the HVC survey note and direct driver starter together with the HVC validation matrix and verify-helper boundary. Those are current-head same-lane evidence for `P11-L16`, but the deeper HVC replay, manifest, dedicated survey-checker, and teardown-note paths remain archival or repo-reality gaps rather than shared reminder-packet ownership.

DesignWare therefore currently has a narrower directly readable owner stack than some older reminder wording still implies. HVC has directly readable current-head continuity evidence, while bcm2835 and gpio reminder follow-through still belong to their own lanes.

## Sequencing Rules

Use this note to keep the bounded work order honest:

1. Prefer one Phase 11 lane at a time instead of batching bcm2835, gpio, DesignWare, HVC, header-boundary, and contributor-note work into one mixed change.
2. Keep the shared-versus-dedicated split explicit: the shared sequencing lane owns reminder-surface truthfulness, not driver-local execution claims.
3. Keep the current readback boundary honest: today that means the HVC current-head continuity packet plus the narrower DesignWare owner stack of notes, manifest, registration scaffold, and paired teardown and verify checkers.
4. Keep the DesignWare follow-through parked on platform-registration scaffolding and reminder-surface truthfulness; do not widen the current owner stack into live watchdog-core execution, PM plumbing, reset execution, IRQ execution, MMIO validation, or claims that the absent helper, replay, matrix, survey, slice, or teardown-note surfaces are back on current `master`.
5. Keep HVC current-head continuity and helper-local teardown or failure-mode evidence routed through `Documentation/zigux/phase11-hvc-console-survey.md`, `drivers/tty/hvc/hvc_console.zig`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`; do not widen that packet into tty registration, notifier execution, khvcd execution, sysrq dispatch, or host-backed teardown.
6. Do not imply broader platform registration, PM plumbing, reset execution, IRQ execution, MMIO validation, notifier execution, sysrq execution, khvcd execution, or hardware-backed closure beyond the reminder notes, manifest-backed scaffolds, and checkers that were directly readable in this run.
7. When contributor-facing summaries reopen, keep them aligned with the narrower DesignWare owner stack and the HVC current-head continuity packet instead of reviving older returned-helper wording.
8. Keep the next bounded shared follow-through inside the smallest reminder-surface truthfulness repair unless a later reread restores or removes another directly readable Phase 11 packet surface.

## Non-Goals

This note does not widen Phase 11 into:

- a claim that the overall simple-driver tranche is closed
- a claim that the missing shared-validator surfaces `scripts/zigux/validate-phase11.py` or `make -C zigux phase11-validate` are already present on current `master`
- a claim that bcm2835 or gpio reminder packets have been broadly reread beyond the specific watchdog-local surfaces touched in their own lanes
- a claim that the absent DesignWare helper, replay, survey, matrix, slice, or teardown-note surfaces are directly readable again
- broader hardware-backed watchdog validation, tty registration parity, notifier execution, sysrq dispatch, khvcd execution, or host-backed teardown closure
- a migration of driver-local reminder ownership into the shared packet
