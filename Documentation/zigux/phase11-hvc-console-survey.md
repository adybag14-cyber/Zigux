# Phase 11 HVC Console Survey

This note keeps the bounded Phase 11 `hvc_console` packet truthful on current `master`.
It stays inside the simple-driver lane and records the archived starter,
its supporting helper history, the surviving current-head continuity anchors, and
what still remains execution-facing follow-through.
The original archival landing happened on `P11-L13`, while the currently coupled
continuity remains parked under `P11-L16`.

## Status

- `PHASE11_HVC_CONSOLE_SURVEY_STATUS=inventory_backed_continuity`
- archival landing lane: `P11-L13`
- current coupled packet continuity: `P11-L16`
- archival landing checkpoint: `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- current `master` still keeps the HVC lane reviewable through this survey note,
  `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`,
  `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`,
  `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`,
  `zigux/tests/fixtures/phase11_build_inventory.json`,
  `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`,
  `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`, and
  `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
- direct contents reads in this run did not rematerialize
  `drivers/tty/hvc/hvc_console.zig`, `drivers/tty/hvc/hvc_console_verify.zig`,
  `drivers/tty/hvc/hvc_console_sysrq.zig`, `zigux/tests/phase11_hvc_console.zig`,
  `zigux/tests/phase11_hvc_cleanup.zig`,
  `zigux/tests/phase11_hvc_console_survey.zig`,
  `zigux/tests/phase11_hvc_console_manifest.json`,
  `zigux/tests/phase11_hvc_console_modem_control_split.zig`,
  `zigux/tests/phase11_hvc_console_poll_retry_split.zig`,
  `Documentation/zigux/phase11-hvc-console-slice.md`,
  `Documentation/zigux/phase11-hvc-console-teardown-note.md`,
  `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and
  `scripts/zigux/check-phase11-hvc-survey-packet.py`, so keep those paths framed
  as archival packet vocabulary rather than current-head direct-readback evidence
- remaining unported work is still tty-driver registration, khvcd worker
  execution, live sysrq execution, notifier callback execution, and host-backed
  transport or teardown validation

## Current-Head Continuity Packet

Treat the current bounded HVC continuity packet on `master` as the shared
inventory-backed and proof-backed packet below:

- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`

Keep those current-head anchors explicit while the lane stays below live tty
registration, notifier callback execution, khvcd execution, live sysrq dispatch,
and host-backed teardown parity.

## Archival Packet Vocabulary

The archival HVC packet still matters for reminder truthfulness, but on current
`master` it is not direct-readback evidence in this run.
Treat the archived direct driver, helper, replay, split, teardown, validation,
and survey paths as historical packet vocabulary only until a future reread
confirms they materialize again:

- `drivers/tty/hvc/hvc_console.zig`
- `drivers/tty/hvc/hvc_console_verify.zig`
- `drivers/tty/hvc/hvc_console_sysrq.zig`
- `zigux/tests/phase11_hvc_console.zig`
- `zigux/tests/phase11_hvc_cleanup.zig`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `zigux/tests/phase11_hvc_console_manifest.json`
- `zigux/tests/phase11_hvc_console_modem_control_split.zig`
- `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
- `Documentation/zigux/phase11-hvc-console-slice.md`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `scripts/zigux/check-phase11-hvc-survey-packet.py`
- `make -C zigux phase11-hvc-survey`

## What Landed

The archival lane previously recorded `drivers/tty/hvc/hvc_console.zig` as the
bounded starter and `drivers/tty/hvc/hvc_console_sysrq.zig` as the supporting
helper for host-free HVC reviewability work.
That older packet still preserves the intended review topics such as final-close
teardown summary, notifier-add handoff, khvcd polling-contract and worker-entry
summaries, `__hvc_poll` drain ordering, hangup and remove handoffs,
cleanup-time tty-port release, wakeup cues, notifier IRQ helper shape, targetless
notifier no-unregister handling, sysrq toggle separation, literal-byte fallback,
and post-teardown unavailability.

Keep those behaviors framed as archival landing context rather than live
current-head driver readback until the direct HVC packet rematerializes again.

## Bounded Meaning

This note records that the HVC simple-driver lane still has honest current-head
continuity through the survey note, cleanup-alignment companion,
verify-helper-boundary note, shared build inventory, and the surviving HVC proof
shards.

It does not claim direct current-head readback of the archived HVC driver,
cleanup, split-replay, teardown, validation-matrix, or dedicated survey-checker
packet, and it does not claim tty-driver registration, notifier callback
execution, khvcd polling execution, live sysrq dispatch, host-backed cleanup, or
hardware-validated teardown parity.

The roadmap destination family and the bounded simple-driver support packet are
still materially represented through the current-head continuity anchors above,
so the remaining same-lane work is execution-facing follow-through rather than a
missing simple-driver starter.
