# Phase 11 HVC Console Slice

This bounded Phase 11 slice adds the first Zigux `hvc_console` starter anchored to `drivers/tty/hvc/hvc_console.c`.

The starter stays intentionally narrow:

- validates the early-console slot range and adapter-presence gate
- keeps a small header-parity snapshot for `drivers/tty/hvc/hvc_console.h`, including `MAX_NR_HVC_CONSOLES`, `HVC_ALLOC_TTY_ADAPTERS`, the `hv_ops` callback shape, the exported `hvc_alloc` or `hvc_remove` or `hvc_poll` or `hvc_resize` helpers, and the bounded `hvc_kick` plus notifier-IRQ helper surface
- models CRLF write framing for the bounded console print path, including repeated bare-newline normalization and preservation of pre-existing CRLF input
- records retry-after-`-EAGAIN`, partial-write, full-write, and fatal-drop flush progress without claiming backend I/O
- summarizes the setup-state and final-close wait boundary, including the `HVC_CLOSE_WAIT`-shaped final-close gate, without claiming tty registration
- adds a tiny final-close teardown summary that keeps tty detachment, `HUPCL`-gated `dtr_rts` shutdown, `notifier_del` ownership, resize-work cancellation, and `tty_wait_until_sent()` intent reviewable without claiming notifier execution or tty-core teardown timing
- adds a tiny tty-registration handoff summary that keeps `setup_hvc_console()`-adjacent close-wait ownership, notifier boundaries, and khvcd wakeup intent reviewable without claiming worker execution
- adds a tiny notifier-add open handoff summary that keeps notifier-add success, polling fallback, failed-open close cleanup, open-time IRQ request boundaries, and khvcd kick follow-through reviewable without claiming live notifier callback execution
- keeps one tiny bounded supporting helper in `drivers/tty/hvc/hvc_console_sysrq.zig` so the primary-console `^O` toggle, pending-sysrq state carry, and next-byte dispatch handoff stay reviewable without claiming live `handle_sysrq()` execution
- adds a tiny khvcd polling-contract summary that keeps notifier-driven versus polling-driven wakeups, bounded reschedule intent, and teardown-facing host-I/O boundaries reviewable without claiming worker execution
- adds a tiny khvcd worker-entry summary that keeps wake-before-sleep decisions, xmon-forced read polling, mutex-backed list walks, and timeout-backoff choices reviewable without claiming live worker execution
- adds a tiny khvcd sleep-and-reschedule handoff summary that keeps the pre-sleep kick check, the interruptible-state recheck, untimed schedule versus timed backoff selection, and running-state restore reviewable without claiming live worker execution
- adds a tiny `__hvc_poll()` drain-order summary that keeps write-drain-before-read ordering, read-poll rearm boundaries, and tty wakeup versus flip-push sequencing reviewable without claiming host-backed polling execution
- adds a tiny `hvc_hangup()` disconnect summary that keeps resize-cancel ordering, the stale-count guard, tty detach, outbuf clearing, and notifier-hangup boundaries reviewable without claiming notifier callback execution
- adds a tiny `hvc_remove()` handoff summary that keeps console-lock slot clearing, the paired `vtermnos[]` and `cons_ops[]` release, `tty_port_put()` ordering, `tty_vhangup()` follow-through, and the keep-IRQ-until-hangup teardown boundary reviewable without claiming live console locking or IRQ teardown
- adds a tiny `hvc_cleanup()` tty-port release handoff summary that keeps `tty_port_put()` ownership, port-reference drop timing, and the deferred final release boundary reviewable without claiming live tty destruction or host-backed teardown
- mirrors the slot teardown that clears the early-console binding

This slice does not claim tty-driver registration, khvcd polling or execution, live sysrq execution, notifier callback execution, hotplug discovery, or live hypervisor-backed reads and writes yet.

`Documentation/zigux/phase11-hvc-console-validation-matrix.md` now records the first kernel-integration validation matrix for close-wait teardown parity, the final-close teardown handoff, tty registration, the notifier-add open handoff, the bounded sysrq toggle-and-dispatch handoff, the landed khvcd polling-contract evidence, the khvcd worker-entry boundary, the khvcd sleep-and-reschedule handoff, the `__hvc_poll()` drain-order handoff, the `hvc_hangup()` disconnect handoff, the `hvc_remove()` teardown handoff, and the `hvc_cleanup()` tty-port release handoff without widening into host-backed I/O.

The next honest bounded step inside the same Phase 11 lane is to leave this starter parked unless another comparably small host-free notifier callback or khvcd handoff becomes obvious; otherwise avoid widening straight into live tty teardown, live khvcd worker behavior, or host-backed teardown.
