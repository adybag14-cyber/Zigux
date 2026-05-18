# Phase 11 HVC Console Survey

This note keeps the bounded Phase 11 `hvc_console` packet truthful on current `master`.
It stays inside the simple-driver lane and records the returned direct starter,
its supporting helper history, the surviving current-head continuity anchors, the
survey-recorded deeper starter packet, and what still remains execution-facing
follow-through.
The original archival landing happened on `P11-L13`, while the currently coupled
continuity remains parked under `P11-L16`.

## Status

- `PHASE11_HVC_CONSOLE_SURVEY_STATUS=simple_driver_current_head_gap_reopened`
- archival landing lane: `P11-L13`
- current coupled packet continuity: `P11-L16`
- archival landing checkpoint: `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- the Phase 11 roadmap still calls for a bounded simple-production-driver
destination under `drivers/tty/hvc/*.zig`, so keep the simple-driver gap marked
as reopened on current-head readback until the deeper replay and helper anchors return
- current `master` still keeps the HVC lane reviewable through this survey note,
  `drivers/tty/hvc/hvc_console.zig`,
  `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`,
  `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`,
  `Documentation/zigux/phase11-hvc-console-validation-matrix.md`,
  `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`,
  `zigux/tests/fixtures/phase11_build_inventory.json`,
  `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`,
  `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`,
  `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`,
  `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`, and
  `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
- current direct contents reads do rematerialize `drivers/tty/hvc/hvc_console.zig`,
  so keep the direct starter anchor explicit inside the current-head packet even
  while the helper, replay, and survey-route family remain incomplete
- current direct contents reads in this lane still do not rematerialize
  `zigux/tests/phase11_hvc_console_manifest.json`, so the roadmap-facing
  simple-driver closure is still no longer current-head-proven and the broader
  starter-depth packet must stay survey-recorded same-lane archival vocabulary
  until a future reread proves those deeper anchor paths returned again
- current direct contents reads do rematerialize
  `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, so keep that
  shared matrix explicit as returned current-head readback evidence instead of
  folding it back into the missing deeper anchor set
- current authenticated contents reads in this lane still do not rematerialize
  `scripts/zigux/check-phase11-hvc-survey-packet.py`, so keep that dedicated
  survey-checker path framed as a same-lane repo-reality gap until a future
  reread proves it returned
- remaining unported work is still tty-driver registration, khvcd worker
  execution, live sysrq execution, notifier callback execution, and host-backed
  transport or teardown validation

## Current-Head Continuity Packet

Treat the current bounded HVC continuity packet on `master` as the returned
starter plus the shared inventory-backed and proof-backed packet below:

- `drivers/tty/hvc/hvc_console.zig`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`

Keep those current-head anchors explicit while the lane stays below live tty
registration, notifier callback execution, khvcd execution, live sysrq dispatch,
and host-backed teardown parity.

## Survey-Recorded Starter Packet

The survey still records the remaining deeper HVC helper, replay, split,
teardown, validation, and survey paths below as the roadmap-facing
starter-depth packet for this lane:

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

Keep that packet visible as bounded survey-recorded archival vocabulary and as
the next same-lane restoration target required to re-close the Phase 11
simple-driver roadmap gap on current `master`, rather than as direct
current-head readback evidence until a future reread rematerializes its missing
anchor paths again.

Current `master` also does not rematerialize a separate
`make -C zigux phase11-hvc-survey` route through `zigux/Makefile` or
`.github/workflows/zigux-bootstrap.yml`; likewise treat
`scripts/zigux/check-phase11-hvc-survey-packet.py` as a same-lane repo-reality
gap until a future reread proves it returned.

Treat that packet as bounded starter-depth evidence rather than proof of live
tty registration, notifier callback execution, khvcd execution, live sysrq
dispatch, host-backed cleanup, or hardware-validated teardown parity.

## What Landed

The archival lane previously recorded `drivers/tty/hvc/hvc_console.zig` as the
bounded starter and `drivers/tty/hvc/hvc_console_sysrq.zig` as the supporting
helper for host-free HVC reviewability work.
Current direct contents reads now rematerialize that direct starter anchor
again, while the helper, replay, split, teardown-note, and dedicated survey
packet remain survey-recorded or missing on current-head readback.
That older packet still preserves the intended review topics such as final-close
teardown summary, notifier-add handoff, khvcd polling-contract and worker-entry
summaries, `__hvc_poll` drain ordering, hangup and remove handoffs,
cleanup-time tty-port release, wakeup cues, notifier IRQ helper shape, targetless
notifier no-unregister handling, sysrq toggle separation, literal-byte fallback,
and post-teardown unavailability.

Keep those behaviors framed as bounded starter-depth evidence rather than as
proof of live tty or hypervisor execution.

## Bounded Meaning

This note records that the HVC simple-driver lane still has honest current-head
continuity through the returned `drivers/tty/hvc/hvc_console.zig` starter, the
survey note, cleanup-alignment companion, verify-helper-boundary note, the
returned HVC validation matrix, the shared build inventory, and the surviving
HVC proof shards above.

It does not claim tty-driver registration, notifier callback execution, khvcd
polling execution, live sysrq dispatch, host-backed cleanup, or
hardware-validated teardown parity.

That current-head continuity still does not prove that the roadmap-facing simple
production driver is fully reclosed on `master`. The survey preserves the
remaining starter-depth packet as archival continuity vocabulary precisely
because the helper, manifest, replay, split, teardown-note, and dedicated survey
anchors are still missing on current-head readback. The remaining same-lane work
starts with restoring those deeper anchors before later execution-facing
follow-through, rather than claiming that the whole older direct-readback packet
is fully back on current `master`.