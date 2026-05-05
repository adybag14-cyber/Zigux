# Phase 11 HVC Console Slice

This bounded Phase 11 slice adds the first Zigux `hvc_console` starter anchored to `drivers/tty/hvc/hvc_console.c`.

The starter stays intentionally narrow:

- validates the early-console slot range and adapter-presence gate
- models CRLF write framing for the bounded console print path
- records retry-after-`-EAGAIN`, partial-write, full-write, and fatal-drop flush progress without claiming backend I/O
- summarizes the setup-state and final-close wait boundary, including the `HVC_CLOSE_WAIT`-shaped final-close gate, without claiming live tty registration
- adds a tiny cleanup handoff summary that keeps final-close and hangup-driven `tty_port_put()` release reviewable while leaving final destruction deferred to the tty-port lifecycle
- adds a tiny remove-path handoff summary that keeps console-slot clearing, the preserved IRQ handoff into the later hangup path, the `tty_port_put()` release, and conditional `tty_vhangup()` then `tty_kref_put()` ordering reviewable without claiming live tty teardown
- adds a tiny tty-registration handoff summary that keeps `setup_hvc_console()` registration intent, close-wait ownership, and the khvcd-facing boundary reviewable without claiming worker execution
- mirrors the slot teardown that clears the early-console binding

This slice does not claim tty-driver registration, notifier callbacks, khvcd polling, sysrq handling, hotplug discovery, or live hypervisor-backed reads and writes yet.

`Documentation/zigux/phase11-hvc-console-validation-matrix.md` now records the first kernel-integration validation matrix for close-wait teardown parity, the landed cleanup replay, the landed remove-path handoff, the landed tty-registration handoff, and the still-pending notifier-facing and sysrq-facing follow-up without widening into host-backed I/O.

The next honest bounded step inside the same Phase 11 lane is still a tiny notifier-facing or sysrq-facing handoff summary that keeps callback boundaries reviewable before any host-backed I/O widens the slice.
