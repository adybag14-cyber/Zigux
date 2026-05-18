# Phase 11 Driver Lane Sequencing

This note keeps the active Phase 11 simple-driver packet split into bounded owner lanes without pretending the older shared-contract stack is still directly present on current `master`.

## Scope

Use this note when a Phase 11 change touches the shared reminder packet under `Documentation/zigux/phase11-*.md`, `scripts/zigux/check-phase11-*.py`, the surviving Phase 11 proof files under `zigux/tests/`, or the broad contributor-facing summaries.

## Lane Split

Keep the current lane split explicit:

- shared sequencing lane `P11-Y06` owns only the cross-driver current-head truthfulness surfaces that were directly re-readable in this run: `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase11-validation-matrix-gap-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-matrix-gap-survey.py`, and `zigux/tests/fixtures/phase11_build_inventory.json`
- bcm2835 continuity stays separate from the shared truthfulness lane; if future rereads rematerialize a bcm2835 replay or validation note, refresh that packet in its own bounded step instead of rebuilding it through shared-summary wording
- gpio continuity stays separate from the shared truthfulness lane; do not use shared-note work to recreate missing gpio validation-matrix claims from older reminder text alone
- DesignWare lane `P11-L10` owns the currently readable continuity packet `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`; if driver-local `dw_wdt` replay files, packet docs, or the compile-local verify helper rematerialize again, reopen them inside the same DesignWare lane rather than through the shared reminder lane
- HVC archival lane `P11-L16` owns the directly readable HVC continuity packet through `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`, `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`, and `zigux/tests/phase11_hvc_cleanup_packet_build.zig`; keep that HVC-local packet truthful while the older direct starter-depth packet stays survey-recorded archival vocabulary until fresh rereads rematerialize its missing anchors, and do not widen the lane into live tty registration, khvcd execution, notifier execution, or sysrq delivery claims
- contributor-note lane `P11-L18` owns broad cross-phase reminder wording in `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
- shared header-boundary follow-through stays adjacent to `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`; do not fold that shared UAPI surface into the HVC archival lane or into broad contributor-note refreshes

## Shared Packet Boundaries

Treat the current shared Phase 11 packet as the smaller cross-driver truthfulness stack, not as the older full contract-and-make-route packet or the HVC-local continuity packet:

- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`

Current direct rereads in this run still kept the HVC continuity packet readable through `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`, `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`, `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`, and `zigux/tests/phase11_hvc_cleanup_packet_build.zig`, while that same coupled survey keeps the older direct starter-depth packet under `drivers/tty/hvc/hvc_console.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `Documentation/zigux/phase11-hvc-console-slice.md`, and `Documentation/zigux/phase11-hvc-console-teardown-note.md` framed as survey-recorded archival vocabulary rather than current-head readback evidence.

Current direct rereads in this run still did not rematerialize `drivers/tty/hvc/hvc_console.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, or `scripts/zigux/check-phase11-hvc-survey-packet.py`, so keep those direct starter-depth anchors and the dedicated survey-checker path framed as HVC-local repo-reality gaps until a future reread proves they returned.

Current direct rereads in this run did not rematerialize `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-shared-summary-surfaces.py`, or `zigux/tests/phase11_build.zig`. Current `master` does rematerialize `zigux/Makefile`, but its live body still does not expose a dedicated Phase 11 route, so shared-note repairs should keep the returned file distinct from the still-missing Phase 11 build handles instead of presenting the file itself as a repo-reality gap.

## Sequencing Rules

Use this note to keep the bounded work order honest:

1. Prefer one Phase 11 lane at a time instead of batching bcm2835, gpio, DesignWare, HVC, header-boundary, and contributor-note work into one mixed change.
2. Keep the shared-versus-dedicated split explicit: the shared sequencing lane only repairs the smaller cross-driver truthfulness packet listed above and must not recreate missing shared-contract or make-route claims from historical wording alone.
3. Keep the validation-matrix gap survey authoritative for the four driver-local validation matrices until fresh direct reads recover those files; do not let shared-summary wording promote missing matrix files back into live evidence.
4. Keep the HVC survey, the returned HVC validation matrix, the cleanup current-head checker, and the starter-depth packet vocabulary authoritative for the HVC archival lane; shared sequencing work may cite that packet when comparing lane boundaries, but it must not claim ownership of the HVC-local note, checker, proof, direct replay surfaces, or the still-missing dedicated HVC survey-checker path.
5. Keep the shared header-boundary matrix bounded to public layout and declaration truthfulness; do not widen it into tty-core, notifier-execution, or watchdog-core ownership claims.
6. Do not imply broader registration, notifier, sysrq, khvcd, teardown, reset, or hardware-backed parity closure beyond the reminder notes and proof files that were directly readable in this run.
7. When contributor-facing summaries reopen, either keep this smaller current-head packet explicit across all broad reminder surfaces or leave them parked; do not let one summary drift back to the missing shared-contract stack while the others stay narrowed.
8. Keep the next bounded shared follow-through inside the smallest reminder-surface truthfulness repair unless a later reread restores a larger directly readable shared packet.

## Non-Goals

This note does not widen Phase 11 into:

- a claim that the overall simple-driver tranche is closed
- a claim that the older shared replay-contract, closure-note, shared-summary checker, shared build file, or Makefile routes are still directly present on current `master`
- broader hardware-backed watchdog validation, tty registration parity, notifier execution, sysrq dispatch, or khvcd execution
- a migration of driver-local reminder ownership into the shared packet
