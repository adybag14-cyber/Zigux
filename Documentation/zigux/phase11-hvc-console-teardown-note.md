# Phase 11 HVC Console Teardown Note

This note keeps the teardown-parity checkpoint for the bounded Phase 11 `hvc_console` packet truthful on current `master`.
It stays inside the simple-driver lane and records only the host-free teardown and failure-mode surfaces that the shipped HVC survey packet already names.

## Status

* `PHASE11_HVC_CONSOLE_TEARDOWN_STATUS=cleanup_handoff_archived`
* teardown evidence remains bounded to the landed HVC starter packet
* remaining follow-through is still live tty-driver registration, notifier callback execution, khvcd execution, live sysrq dispatch, and host-backed transport or teardown validation

## Teardown Packet

The current teardown-facing HVC packet on `master` is:

* `drivers/tty/hvc/hvc_console.zig`
* `drivers/tty/hvc/hvc_console_verify.zig`
* `drivers/tty/hvc/hvc_console_sysrq.zig`
* `zigux/tests/phase11_hvc_console.zig`
* `zigux/tests/phase11_hvc_cleanup.zig`
* `zigux/tests/phase11_hvc_console_survey.zig`
* `zigux/tests/phase11_hvc_console_manifest.json`
* `zigux/tests/phase11_hvc_console_modem_control_split.zig`
* `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
* `Documentation/zigux/phase11-hvc-console-survey.md`
* `Documentation/zigux/phase11-hvc-console-slice.md`
* `Documentation/zigux/phase11-hvc-console-teardown-note.md`
* `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
* `scripts/zigux/check-phase11-hvc-survey-packet.py`
* `make -C zigux phase11-hvc-survey`

Current `master` also materializes direct `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, and `zigux/tests/phase11_hvc_cleanup.zig` companions.
This teardown packet keeps those direct replay, verify, and cleanup surfaces explicit beside the starter, the survey gate, the split tests, the sysrq helper, and the coupled governance notes without widening into live notifier or transport claims.

## What The Landed Teardown Packet Covers

The current host-free teardown packet keeps these handoffs explicit:

* final-close teardown boundaries and close-wait ownership
* `hvc_cleanup()` tty-port release handoff and cleanup-time tty-port ownership
* `hvc_hangup()` disconnect cleanup wording
* `hvc_remove()` slot-release and handoff ordering
* notifier-facing teardown edges beside `summarizeNotifierAddOutcome()`
* bounded sysrq-handling support through `drivers/tty/hvc/hvc_console_sysrq.zig` without claiming live sysrq execution
* poll-retry and drain-order split
* modem-control fallback split
* the direct verify, replay, and cleanup companion surfaces that current `master` now materializes beside the archival survey gate

The landed survey-backed packet also keeps the close-path and cleanup-path failure-mode cues explicit around tty detachment, HUPCL-gated modem-line shutdown, close-wait ownership, notifier ownership, resize-work cancellation, wait-until-sent intent, buffered-write clearing, stale hangup short-circuit behavior, cleanup-time tty-port ownership, and keep-IRQ-until-hangup teardown boundaries.

## Bounded Meaning

This note records the shipped teardown summaries and the supporting survey-backed packet only.
It does not claim live notifier callback execution, khvcd polling behavior, tty-driver registration, host-backed cleanup, or hardware-validated teardown parity.
The direct verify, replay, and cleanup companions remain bounded host-free evidence rather than proof of live console integration.
