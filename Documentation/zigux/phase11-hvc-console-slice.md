# Phase 11 HVC Console Slice

This bounded Phase 11 slice adds the first Zigux `hvc_console` starter anchored to `drivers/tty/hvc/hvc_console.c`.

The starter stays intentionally narrow:

- validates the early-console slot range and adapter-presence gate
- keeps a small header-parity snapshot for `drivers/tty/hvc/hvc_console.h`, including `MAX_NR_HVC_CONSOLES`, `HVC_ALLOC_TTY_ADAPTERS`, the `hv_ops` callback shape, and the exported `hvc_*` helper surface
- models CRLF write framing for the bounded console print path
- records retry-after-`-EAGAIN`, partial-write, full-write, and fatal-drop flush progress without claiming backend I/O
- summarizes the setup-state and final-close wait boundary, including the `HVC_CLOSE_WAIT`-shaped final-close gate, without claiming tty registration
- mirrors the slot teardown that clears the early-console binding

This slice does not claim tty-driver registration, khvcd polling, sysrq handling, notifier callbacks, hotplug discovery, or live hypervisor-backed reads and writes yet.

`Documentation/zigux/phase11-hvc-console-validation-matrix.md` now records the first kernel-integration validation matrix for tty registration, close-wait teardown parity, and khvcd-facing behavior without widening into host-backed I/O.

The next honest bounded step inside the same Phase 11 lane is a tiny tty-registration handoff summary that keeps `setup_hvc_console()` teardown parity and khvcd-facing behavior reviewable before any host-backed I/O widens the slice.
