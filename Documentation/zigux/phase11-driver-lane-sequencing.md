# Phase 11 Driver Lane Sequencing

This note keeps the active Phase 11 simple-driver packet split into bounded owner lanes while reflecting the shared reminder stack and build-backed replay files that current `master` now materializes directly.

## Scope

Use this note when a Phase 11 change touches the shared reminder packet under `Documentation/zigux/phase11-*.md`, `scripts/zigux/check-phase11-*.py`, the surviving Phase 11 build and proof files under `zigux/tests/`, or the broad contributor-facing summaries.

## Lane Split

Keep the current lane split explicit:

- shared sequencing lane `P11-Y06` owns the current cross-driver reminder and build-backed replay stack that was directly re-readable in this run: `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase11-validation-matrix-gap-survey.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-shared-summary-surfaces.py`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-matrix-gap-survey.py`, `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`, `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/phase11_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- bcm2835 continuity stays separate from the shared sequencing lane; keep the returned bcm2835 driver, verify helper, dedicated replay, dedicated survey gate, manifest-backed reminder packet, and teardown note inside the bcm2835 lane instead of rebuilding that packet through shared summary wording
- gpio continuity stays separate from the shared sequencing lane; keep the returned gpio starter, focused `phase11_gpio_wdt_platform_drvdata.zig` replay, dedicated survey gate, and archived reminder packet explicit without using shared-note work to overclaim the missing main replay or broader platform-backed execution
- DesignWare lane `P11-L10` owns the current watchdog-local packet through `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt.zig`, and `zigux/tests/phase11_dw_wdt_survey.zig`; keep platform-registration scaffolding and teardown wording inside that same DesignWare lane instead of moving it into the shared reminder lane
- HVC archival lane `P11-L16` owns the dedicated HVC archival packet through `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`, `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, `drivers/tty/hvc/hvc_console.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`, `zigux/tests/phase11_hvc_cleanup_packet_build.zig`, and `make -C zigux phase11-hvc-survey`; keep that HVC-local packet truthful without widening it into live tty registration, khvcd execution, notifier execution, sysrq delivery, or host-backed teardown claims
- contributor-note lane `P11-L18` owns broad cross-phase reminder wording in `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
- shared header-boundary follow-through stays adjacent to `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`; do not fold that public-surface packet into the HVC archival lane or into driver-local watchdog packets

## Shared Packet Boundaries

Treat the current shared Phase 11 packet as the returned reminder-and-build-backed replay stack below:

- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-closure-note.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `scripts/zigux/check-phase11-shared-replay-contract.py`
- `scripts/zigux/check-phase11-shared-summary-surfaces.py`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_build.zig`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

Current direct rereads in this run keep the shared reminder stack readable through `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-shared-summary-surfaces.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`, while the same rereads also keep all four driver-local validation matrices directly readable on current `master`.

Current direct rereads in this run also keep the dedicated HVC archival packet readable through `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`, `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, `drivers/tty/hvc/hvc_console.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, and `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, so shared-note work should keep that packet explicit instead of reverting it to missing-anchor vocabulary.

Current `master` does materialize `zigux/Makefile`, and its live body now keeps `make -C zigux phase11-contract`, `make -C zigux phase11`, and `make -C zigux phase11-hvc-survey` explicit beside `zigux/tests/phase11_build.zig`. Keep those returned Phase 11 routes distinct from the still-missing shared-validator surfaces `scripts/zigux/validate-phase11.py` and `make -C zigux phase11-validate`.

## Sequencing Rules

Use this note to keep the bounded work order honest:

1. Prefer one Phase 11 lane at a time instead of batching bcm2835, gpio, DesignWare, HVC, header-boundary, and contributor-note work into one mixed change.
2. Keep the shared-versus-dedicated split explicit: the shared sequencing lane owns the returned reminder stack, the restored four-matrix packet, the shared checker stack, the shared build inventory, and the shared build-backed replay route, but it must not absorb driver-local teardown, registration, or execution claims.
3. Keep the validation-matrix gap survey authoritative for the current four-matrix packet until a fresh reread removes or changes one of those files; if the direct matrix set changes again, refresh this sequencing note, the survey, and the coupled checkers in the same bounded pass.
4. Keep the HVC survey, cleanup-alignment companion, verify-helper-boundary note, returned validation matrix, returned survey checker, direct HVC archival files, and HVC route authoritative for the HVC archival lane; shared sequencing work may cite that packet when comparing lane boundaries, but it must not claim live tty registration, notifier execution, khvcd execution, sysrq dispatch, or host-backed teardown closure.
5. Keep the shared header-boundary matrix bounded to public layout and declaration truthfulness; do not widen it into tty-core, notifier-execution, or watchdog-core ownership claims.
6. Do not imply broader platform registration, PM plumbing, remove-hook execution, reset-controller execution, notifier execution, sysrq dispatch, khvcd execution, or hardware-backed validation beyond the reminder notes, matrices, routes, and replay files that were directly readable in this run.
7. When contributor-facing summaries reopen, either keep this returned current-head packet explicit across all broad reminder surfaces or leave them parked; do not let one summary drift back to missing-route or missing-matrix claims while the others keep the returned shared replay stack visible.
8. Keep the next bounded shared follow-through inside the smallest reminder-surface truthfulness repair unless a later reread restores or removes another directly readable shared packet surface.

## Non-Goals

This note does not widen Phase 11 into:

- a claim that the overall simple-driver tranche is closed
- a claim that the missing shared-validator surfaces `scripts/zigux/validate-phase11.py` or `make -C zigux phase11-validate` are already present on current `master`
- broader hardware-backed watchdog validation, tty registration parity, notifier execution, sysrq dispatch, khvcd execution, or host-backed teardown closure
- a migration of driver-local reminder ownership into the shared packet
