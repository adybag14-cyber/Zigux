# Phase 11 HVC Console Survey

This note keeps the bounded Phase 11 `hvc_console` packet truthful on current `master`. It stays inside the simple-driver lane and records the archived starter, the bounded supporting helper, the direct replay companions, the split replay surfaces, and the coupled survey route without claiming live tty or hypervisor execution. The original archival landing happened on `P11-L13`, while the currently coupled continuity remains parked under `P11-L16`.

## Status

* `PHASE11_HVC_CONSOLE_SURVEY_STATUS=starter_packet_archived`
* archival landing lane: `P11-L13`
* current coupled packet continuity: `P11-L16`
* archival landing checkpoint: `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
* current `master` still keeps the HVC archival lane reviewable through this survey note together with the shared Phase 11 inventory-backed continuity anchors `zigux/tests/fixtures/phase11_build_inventory.json` and `scripts/zigux/check-phase11-build-inventory.py`
* direct contents reads in this run did not rematerialize `drivers/tty/hvc/hvc_console.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, or `scripts/zigux/check-phase11-hvc-survey-packet.py`, so keep those as inventory-backed archival packet members until a future reread confirms them again
* remaining unported work is still tty-driver registration, khvcd worker execution, live sysrq execution, notifier callback execution, and host-backed transport or teardown validation

## Surveyed Packet

The current bounded HVC archival packet should therefore be treated as an inventory-backed packet on `master` rather than as a fully direct-readback packet:
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

Current direct readback in this run confirmed this survey note plus the shared inventory-backed continuity anchors `zigux/tests/fixtures/phase11_build_inventory.json` and `scripts/zigux/check-phase11-build-inventory.py`. The direct driver, test, split-replay, dedicated-checker, and coupled-doc companions above should stay framed as inventory-backed archival packet members until a future reread materializes them again.

## What Landed

The archival packet records `drivers/tty/hvc/hvc_console.zig` as the bounded starter for the current HVC lane.

That archived starter keeps these host-free cues reviewable without claiming live tty-driver registration, notifier callback execution, or host-backed teardown:
* final-close teardown summary
* tiny notifier-add open handoff summary
* khvcd polling-contract summary
* khvcd worker-entry summary
* khvcd sleep-and-reschedule handoff summary
* `__hvc_poll` drain-order summary
* `hvc_hangup()` disconnect summary
* `hvc_remove()` handoff summary
* `hvc_cleanup()` tty-port release handoff summary
* `hvc_kick()` wakeup cue
* notifier-IRQ helper surface through `notifier_add_irq()` and `notifier_hangup_irq()`
* targetless notifier no-unregister edge through `summarizeTargetlessNotifierEdge()`

The same archival packet records `drivers/tty/hvc/hvc_console_sysrq.zig` as the bounded supporting helper.

That archived helper keeps sysrq toggle handoff, pending-dispatch separation, literal-byte fallback on non-kernel `^O`, and post-teardown unavailability explicit without claiming live sysrq execution. The archival packet also keeps the direct `drivers/tty/hvc/hvc_console_verify.zig`, `zigux/tests/phase11_hvc_console.zig`, and `zigux/tests/phase11_hvc_cleanup.zig` companions explicit as inventory-backed continuity surfaces rather than direct readback evidence in this run.

Those archival companions keep direct `hvc_console` replay, verify-side helper boundaries, bounded cleanup-time teardown checks, and the targetless notifier no-unregister edge visible beside the archival survey gate without promoting the lane to live tty-driver registration, notifier callback execution, khvcd execution, live sysrq dispatch, or host-backed teardown parity.

The paired archival survey gate in `zigux/tests/phase11_hvc_console_survey.zig` still serves as the dedicated inventory-backed survey anchor for the manifest-backed `struct winsize` `layout_assert` proof at size `8`, alignment `2`, and offsets `0`, `2`, `4`, and `6`; the bounded `struct hv_ops` `layout_assert` proof at size `72`, alignment `8`, and callback-table offsets `0` through `64`; the bounded `hv_ops` callback-signature proof; the `MAX_NR_HVC_CONSOLES` and `HVC_ALLOC_TTY_ADAPTERS` header constant proofs; the exported-helper signature proof through `notifier_hangup_irq`; the targetless notifier no-unregister edge; the modem-control fallback split; the poll-retry split; the teardown-summary wording; and the direct companion surfaces reviewable beside this survey note, the slice note, the teardown note, and the validation matrix.

## Bounded Meaning

This archival note records the landed starter, the direct verify, replay, and cleanup companions, the helper-facing survey, the targetless notifier no-unregister edge, the split tests, the sysrq helper, and the directly coupled teardown-and-validation packet only. On current `master`, treat those driver, replay, split, checker, and coupled-doc surfaces as inventory-backed archival packet members unless a fresh reread confirms them directly again.

It does not claim tty-driver registration, notifier callback execution, khvcd polling execution, live sysrq dispatch, host-backed cleanup, or hardware-validated teardown parity.

The roadmap destination family and the bounded simple-driver support packet are still materially represented through this survey note plus the shared inventory-backed continuity anchors, so the remaining same-lane work is execution-facing follow-through rather than a missing simple-driver starter. Those follow-through steps still belong to later same-lane HVC work rather than the already-landed archival packet.