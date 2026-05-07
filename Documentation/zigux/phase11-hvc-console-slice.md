# Phase 11 HVC Console Slice

This bounded Phase 11 slice adds the first Zigux `hvc_console` starter anchored to `drivers/tty/hvc/hvc_console.c`.

The starter stays intentionally narrow:

- validates the early-console slot range and adapter-presence gate
- models CRLF write framing for the bounded console print path
- records retry-after-`-EAGAIN`, partial-write, full-write, and fatal-drop flush progress without claiming backend I/O
- summarizes the setup-state and final-close wait boundary, including the `HVC_CLOSE_WAIT`-shaped final-close gate, without claiming live tty registration
- adds a tiny cleanup handoff summary that keeps final-close and hangup-driven `tty_port_put()` release reviewable, fails closed if the tty-port reference is already gone, and leaves final destruction deferred to the tty-port lifecycle
- adds a tiny remove-path handoff summary that keeps console-slot clearing, the preserved IRQ handoff into the later hangup path, the `tty_port_put()` release, and conditional `tty_vhangup()` then `tty_kref_put()` ordering reviewable without claiming live tty teardown
- adds a tiny tty-registration handoff summary that keeps `setup_hvc_console()` registration intent, close-wait ownership, and the khvcd-facing boundary reviewable without claiming worker execution
- adds a tiny sysrq handoff summary that keeps boot-console-only dispatch intent, break detection, the notifier callback boundary, and deferred worker execution reviewable without claiming live sysrq handling
- adds a tiny notifier-facing handoff summary that keeps notifier registration intent, deferred callback ownership, and deferred unregister timing reviewable without claiming live callback execution
- adds a tiny khvcd polling-contract summary that keeps notifier-driven versus polling-driven wakeups, bounded reschedule intent, final-close wait carryover, and teardown-facing host-I/O pressure reviewable without claiming khvcd worker execution or live hypervisor transport
- adds a tiny `hvc_hangup()` disconnect summary that keeps resize-work cancellation, stale-count short-circuiting, tty detachment, buffered-write clearing, and notifier-hangup ownership reviewable without claiming live callback execution
- mirrors the slot teardown that clears the early-console binding

This slice does not claim live tty-driver registration, notifier callback execution, khvcd worker execution, live sysrq dispatch, hotplug discovery, or live hypervisor-backed reads and writes yet.

`Documentation/zigux/phase11-hvc-console-validation-matrix.md` now records the first kernel-integration validation matrix for close-wait teardown parity, the landed cleanup replay, the landed remove-path handoff, the landed tty-registration handoff, the landed sysrq handoff, the landed notifier-facing handoff, the landed khvcd polling-contract handoff, and the landed `hvc_hangup()` disconnect handoff without widening into host-backed I/O. `Documentation/zigux/phase11-hvc-console-teardown-note.md` now keeps the close, cleanup, and remove ownership split in one driver-local note so the teardown handoffs stay readable without reopening shared review infrastructure. `drivers/tty/hvc/hvc_console_verify.zig` now adds one compile-local teardown replay that keeps the final-close chain and the hung-up or detached teardown matrix reviewable beside the shared `zigux/tests/phase11_build.zig` packet. `Documentation/zigux/phase11-shared-replay-contract.md` and `scripts/zigux/check-phase11-hvc-survey-packet.py` keep that shared-versus-dedicated HVC review packet explicit so the archival survey route stays truthful when current `master` moves.

The next honest bounded step inside the same Phase 11 lane is now another similarly small teardown-facing evidence repair or remove clarification that stays inside the shipped HVC survey packet and shared replay contract, instead of reopening the already-landed notifier-facing or hangup-disconnect handoff or widening into live callback execution or host-backed I/O.
