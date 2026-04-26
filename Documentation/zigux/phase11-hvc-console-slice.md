# Phase 11 HVC Console Slice

This bounded Phase 11 slice adds the first Zigux `hvc_console` starter anchored to `drivers/tty/hvc/hvc_console.c`.

The starter stays intentionally narrow:

- validates the early-console slot range and adapter-presence gate
- models CRLF write framing for the bounded console print path
- records retry-after-`-EAGAIN` flush intent and fatal-write drop behavior without claiming backend I/O
- summarizes the setup-state and final-close wait boundary, including the `HVC_CLOSE_WAIT`-shaped final-close gate, without claiming tty registration
- mirrors the slot teardown that clears the early-console binding

This slice does not claim tty-driver registration, khvcd polling, sysrq handling, notifier callbacks, hotplug discovery, or live hypervisor-backed reads and writes yet.

The next honest bounded step inside the same Phase 11 lane is to add the first kernel-integration validation matrix for tty registration, close-wait teardown parity, and khvcd-facing behavior without widening into host-backed I/O.
