# Phase 11 HVC Console Validation Matrix

This document records the bounded current-head validation matrix for the Zigux
`hvc_console` lane.

## Status

- `PHASE11_HVC_CONSOLE_STATUS=current_head_companion_packet_truthful`
- lane: `P11-L16`
- reviewed against live `master`
- scope: keep the current HVC console validation and teardown packet truthful
  without widening into live tty registration, notifier callback execution,
  khvcd worker execution, live sysrq dispatch, or host-backed teardown
- the current matrix packet now stays aligned with the smaller
  authenticated-readback companion stack

## Current-Head Matrix Packet

Treat the current matrix packet as:

- `drivers/tty/hvc/hvc_console.h`
- `drivers/tty/hvc/hvc_console.zig`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-validate-manifest-roster.py`
- `scripts/zigux/check-phase11-validate-check-roster.py`
- `scripts/zigux/check-phase11-validate-route-alignment.py`
- `scripts/zigux/check-phase11-focused-direct-build-replays.py`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `scripts/zigux/validate-phase11.py`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/fixtures/phase11_validate_checks.json`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
- `zigux/tests/phase11_hvc_modem_control_proof.zig`
- `zigux/tests/phase11_hvc_modem_control_proof_build.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`

Current contents reads stay aligned with the smaller companion stack, so keep
route claims bounded to `make -C zigux phase11-validate` until `zigux/Makefile`
exposes a dedicated `make -C zigux phase11-hvc-survey` step. The validator
route now keeps the manifest-roster, validate-check-roster, and
validate-route-alignment guards explicit beside the dedicated
`zigux/tests/fixtures/phase11_validate_checks.json` roster before the same
proof-backed build fan-out runs. The witness shard now rereads the live starter
and the boundary note together, while the focused direct-build replay checker
keeps the dedicated modem-control and targetless-unregister build routes
fail-closed without promoting either pair into the shared three-entry build
inventory. Keep the modem-control proof pair directly readable through its
focused build route without promoting it into the shared build inventory yet,
and keep the targetless-unregister witness explicitly separate from the smaller
proof-backed continuity packet. Keep the cleanup-prerequisite trigger split
just as explicit: current-head teardown evidence should keep
`error.CleanupRequiresFinalCloseOrHangup`, `CleanupTrigger.final_close_only`,
`CleanupTrigger.hangup_only`, and `CleanupTrigger.final_close_and_hangup`
visible through the starter Zig module, the verify-boundary reminder, and the
proof-backed cleanup packet rather than implying unconditional `hvc_cleanup()`
execution.

## Failure-Mode Evidence

- `drivers/tty/hvc/hvc_console.zig` keeps flush intent, final-close teardown
  including DTR/RTS shutdown, `wait_until_sent()` carryover, `close_wait`
  ownership, and `port_initialized` clearing, tty-registration handoff,
  `hvc_install()` ownership, `hvc_alloc()` slot selection, early console setup
  and device selection, `__hvc_resize()` handoff, notifier-add open handoff,
  khvcd polling-contract, khvcd worker-entry, khvcd sleep-and-reschedule
  handoff, `__hvc_poll` drain-order, `hvc_hangup()` disconnect,
  `hvc_remove()` handoff, `hvc_cleanup()` tty-port release plus
  cleanup-prerequisite trigger split, targetless notifier, `hvc_kick()` wakeup
  cue, notifier-irq, and modem-control helper summaries reviewable on current
  `master`.
- the same packet keeps `error.CleanupRequiresFinalCloseOrHangup` together with
  `CleanupTrigger.final_close_only`, `CleanupTrigger.hangup_only`, and
  `CleanupTrigger.final_close_and_hangup` explicit as teardown-gate evidence,
  so the current-head matrix stays tied to prerequisite parity instead of
  drifting into unconditional cleanup claims.
- `drivers/tty/hvc/hvc_console.h` keeps the exported `struct hvc_struct`
  forward declaration, `struct hv_ops` callback-table tag, `struct winsize`
  layout, and helper declarations directly readable for the focused exported
  surface proofs on current `master`.
- `Documentation/zigux/phase11-hvc-console-survey.md` and
  `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
  keep `Documentation/zigux/phase11-hvc-console-teardown-note.md`,
  `zigux/tests/phase11_hvc_console_manifest.json`,
  `drivers/tty/hvc/hvc_console_verify.zig`,
  `drivers/tty/hvc/hvc_console_sysrq.zig`,
  `zigux/tests/phase11_hvc_console.zig`,
  `zigux/tests/phase11_hvc_cleanup.zig`,
  `zigux/tests/phase11_hvc_console_survey.zig`, and
  `scripts/zigux/check-phase11-hvc-survey-packet.py` explicit as repo-reality
  gaps instead of returned fallback evidence.
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md` keeps helper-local
  failure-mode edges reviewable through the verify helper boundary note.
- `scripts/zigux/check-phase11-validate-manifest-roster.py`,
  `scripts/zigux/check-phase11-validate-check-roster.py`,
  `scripts/zigux/check-phase11-validate-route-alignment.py`, and
  `zigux/tests/fixtures/phase11_validate_checks.json` keep the returned shared
  validator-side manifest, exact-check, and route fan-out evidence explicit for
  the current HVC-facing packet without claiming a dedicated HVC-only validator.
- `zigux/tests/phase11_hvc_modem_control_proof.zig` and
  `zigux/tests/phase11_hvc_modem_control_proof_build.zig` keep the bounded
  `tiocmget`, `tiocmset`, `dtr_rts`, and `hupcl` teardown distinction explicit
  without promoting the lane to live modem-control execution.
- `zigux/tests/phase11_hvc_targetless_unregister_gap.zig` and
  `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` keep the
  targetless-unregister witness explicit as standalone direct-readback coverage.

## Replay Posture

- keep `make -C zigux phase11-validate` as the returned shared route
- keep the dedicated survey route absent until `zigux/Makefile` grows it
- keep helper-local failure-mode edges reviewable through the verify boundary
  note and the current companion stack
- keep `scripts/zigux/check-phase11-validate-manifest-roster.py`,
  `scripts/zigux/check-phase11-validate-check-roster.py`,
  `scripts/zigux/check-phase11-validate-route-alignment.py`, and
  `zigux/tests/fixtures/phase11_validate_checks.json` explicit as the shared
  validator-side golden-output packet
- keep `scripts/zigux/check-phase11-focused-direct-build-replays.py` explicit as
  the guard for the dedicated modem-control and targetless-unregister build
  routes while those proofs stay outside the shared three-entry build inventory
- keep `zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig`
  explicit as a focused direct-readback proof route outside the shared
  inventory-backed replay contract for now
- keep `drivers/tty/hvc/hvc_console_verify.zig`,
  `drivers/tty/hvc/hvc_console_sysrq.zig`, `zigux/tests/phase11_hvc_console.zig`,
  `zigux/tests/phase11_hvc_cleanup.zig`,
  `zigux/tests/phase11_hvc_console_survey.zig`,
  `zigux/tests/phase11_hvc_console_manifest.json`,
  `Documentation/zigux/phase11-hvc-console-teardown-note.md`, and
  `scripts/zigux/check-phase11-hvc-survey-packet.py` framed as repo-reality
  gaps or archival vocabulary until a future reread proves they returned
