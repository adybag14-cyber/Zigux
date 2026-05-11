# Phase 11 HVC Console Survey

This note restores the compact archival survey for the bounded Phase 11 `hvc_console` packet on current `master`.
It stays inside the simple-drivers lane and records only the shipped starter, the bounded supporting helper, and the still-blocked follow-through that the surrounding shared packet already names.

## Status

* `PHASE11_HVC_CONSOLE_SURVEY_STATUS=starter_packet_archived`
* Phase 11 simple-production-driver gap has been closed by the bounded starter.
* remaining unported work is now tty-driver registration, khvcd worker execution, live sysrq execution, notifier callback execution, and host-backed transport or teardown validation

## Surveyed Packet

The current bounded HVC archival packet on `master` is:

* `zigux/tests/phase11_hvc_console_survey.zig`
* `zigux/tests/phase11_hvc_cleanup.zig`
* `scripts/zigux/check-phase11-hvc-survey-packet.py`
* `make -C zigux phase11-hvc-survey`
* `drivers/tty/hvc/hvc_console_verify.zig`
* `drivers/tty/hvc/hvc_console_sysrq.zig`

The survey note exists to keep those surfaces readable together without overstating runtime parity or widening the Phase 11 claim beyond the landed starter.

## What Landed

The shipped `drivers/tty/hvc/hvc_console_sysrq.zig` helper is a bounded supporting helper for the current HVC packet.
It keeps the tiny sysrq handoff explicit without claiming live sysrq execution, and it leaves the direct transport, tty registration, and callback-driving work outside the archived survey.

The paired compile-local verifier in `drivers/tty/hvc/hvc_console_verify.zig` keeps the driver-local teardown and failure-mode packet reviewable beside that archived survey without widening into live notifier callbacks, khvcd execution, or host-backed cleanup.

The bounded starter and its archival replay now keep these focused cues explicit:

* final-close teardown summary
* hvc_cleanup() tty-port release handoff summary
* tiny notifier-add open handoff summary
* cleanup-prerequisite failure replay
* notifier-prerequisite and notifierless-open failure replays
* targetless and no-dispatch sysrq or notifier deferral replays
* khvcd worker-entry summary
* khvcd sleep-and-reschedule handoff summary
* `__hvc_poll` drain-order summary
* `hvc_hangup()` disconnect summary
* impossible hangup buffered-write guard
* `hvc_remove()` handoff summary
* `hvc_kick()` wakeup cue
* notifier-IRQ helper surface through `notifier_add_irq()` and `notifier_hangup_irq()`
* exported-helper signature proof for the bounded helper-facing HVC surface

## Bounded Meaning

This archival note records the landed starter and the helper-facing survey only.
It does not claim tty-driver registration, notifier callback execution, khvcd polling execution, live sysrq dispatch, host-backed cleanup, or hardware-validated teardown parity.
Those follow-through steps still belong to later same-lane HVC work rather than the shared Phase 11 closure packet.
