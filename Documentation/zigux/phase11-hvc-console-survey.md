# Phase 11 HVC Console Survey

This note keeps the bounded Phase 11 `hvc_console` packet truthful on current
`master`.
It stays inside the simple-driver lane and records the publicly readable starter
packet, the surviving current-head reminder surfaces around it, and the bounded
execution-facing follow-through that still remains out of scope.
The original archival landing happened on `P11-L13`, while the currently coupled
continuity remains parked under `P11-L16`.

## Status

- `PHASE11_HVC_CONSOLE_SURVEY_STATUS=public_readback_packet_truthful`
- archival landing lane: `P11-L13`
- current coupled packet continuity: `P11-L16`
- archival landing checkpoint: `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- the Phase 11 roadmap still keeps `drivers/tty/hvc/*.zig` inside bounded
  simple-production-driver work where teardown parity and failure-mode
  reviewability should deepen before any live execution claims
- current public GitHub file-page readback confirms the bounded HVC starter,
  helper, focused replay, survey, teardown-note, validation-matrix, and checker
  packet remains present on `master`
- the GitHub contents API still returned flaky `404` reads for several of those
  same HVC paths in this lane, so treat public readback as the tie-breaker
  before recording a starter-packet shrink or repo-reality gap
- current public readback still does not stably confirm
  `zigux/tests/phase11_hvc_console_modem_control_split.zig`, and `zigux/Makefile`
  still exposes no dedicated `make -C zigux phase11-hvc-survey` route, so keep
  those claims bounded until a future reread reconfirms them
- remaining unported work is still tty-driver registration, khvcd worker
  execution, live sysrq execution, notifier callback execution, and host-backed
  transport or teardown validation

## Current Public-Readback Packet

Treat the current bounded HVC packet on `master` as the publicly readable packet
below:

- `drivers/tty/hvc/hvc_console.zig`
- `drivers/tty/hvc/hvc_console_verify.zig`
- `drivers/tty/hvc/hvc_console_sysrq.zig`
- `zigux/tests/phase11_hvc_console.zig`
- `zigux/tests/phase11_hvc_cleanup.zig`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `zigux/tests/phase11_hvc_console_manifest.json`
- `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-console-slice.md`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `scripts/zigux/check-phase11-hvc-survey-packet.py`

Keep that packet explicit while the lane stays below live tty registration,
notifier callback execution, khvcd execution, live sysrq dispatch, and
host-backed teardown parity.

## Supporting Reminder Surfaces

Current `master` also keeps the surrounding reminder and proof surfaces below
readable beside the publicly confirmed starter packet:

- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`

Keep those reminder surfaces coupled to the publicly readable HVC packet rather
than using them to overclaim broader runtime closure.

## Still-Bounded Gaps

The same-lane gaps are now narrower than the older survey wording implied:

- `zigux/tests/phase11_hvc_console_modem_control_split.zig` remains unconfirmed
  in this run and should stay bounded until a future reread verifies it directly
- `zigux/Makefile` still does not prove a dedicated `make -C zigux
  phase11-hvc-survey` route
- the current packet remains host-free evidence only; it does not prove live tty
  registration, notifier callback execution, khvcd worker execution, live sysrq
  dispatch, or host-backed teardown parity

## What Landed

The archival lane recorded the HVC starter, helper, focused teardown packet,
and surrounding review surfaces as bounded simple-driver evidence.
Current public readback now confirms those core starter and review surfaces are
still present on `master`, so this survey should describe them as a live
current-head packet rather than as wholly missing anchors inferred from flaky
contents-API reads.

That packet still preserves the intended review topics such as final-close
teardown summary, notifier-add handoff, khvcd polling-contract and worker-entry
summaries, `__hvc_poll` drain ordering, hangup and remove handoffs,
cleanup-time tty-port release, wakeup cues, notifier IRQ helper shape,
targetless notifier no-unregister handling, sysrq helper boundaries, and
post-teardown unavailability.

Keep those behaviors framed as bounded starter-depth evidence rather than as
proof of live tty or hypervisor execution.

## Bounded Meaning

This note records that the HVC simple-driver lane still has honest current-head
continuity through the publicly readable starter, helper, focused replay,
survey, teardown-note, validation-matrix, and checker packet, plus the coupled
cleanup and proof reminder surfaces listed above.

It does not claim tty-driver registration, notifier callback execution, khvcd
polling execution, live sysrq dispatch, host-backed cleanup, or
hardware-validated teardown parity.

The next same-lane work stays focused on one equally small truthfulness repair,
such as reconfirming the unsteady modem-control split readback or tightening one
coupled note if public readback and contents-API evidence diverge again.
