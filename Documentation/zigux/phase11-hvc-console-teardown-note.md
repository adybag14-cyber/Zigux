# Phase 11 HVC Console Teardown Note

This note captures the bounded teardown ownership that is already reviewable in the Zigux `hvc_console` starter anchored to `drivers/tty/hvc/hvc_console.c`.

The current driver-local teardown surface is intentionally small and host-free:

- `summarizeCloseBoundary()` owns the close-side decision about whether the current call is a hung-up short circuit, a non-final close, or the final-close path that carries the `HVC_CLOSE_WAIT`-shaped wait intent.
- `summarizeCleanupHandoff()` owns the follow-on `hvc_cleanup()` handoff where `tty_port_put()` must still be requested for a live tty-port reference, including the hangup-driven path, while final destruction remains deferred to the tty-port lifecycle.
- `summarizeRemoveHandoff()` owns the `hvc_remove()` handoff where the console-slot binding is cleared, IRQ ownership stays preserved for the later hangup path, and `tty_vhangup()` then `tty_kref_put()` ordering only becomes relevant when a tty is still present.

## Teardown Ownership

| boundary | current Zigux owner | what stays reviewable now | still out of scope |
| --- | --- | --- | --- |
| close boundary | `summarizeCloseBoundary()` | final-close detection, hung-up short-circuiting, `port_initialized` clearing, and `HVC_CLOSE_WAIT`-shaped wait intent | live tty close timing, backend drain timing, and khvcd wakeups |
| cleanup handoff | `summarizeCleanupHandoff()` | final-close versus hangup-driven `tty_port_put()` release, missing-reference failure, and deferred final destruction | real tty-port destructor timing, notifier callback execution, and host-backed teardown |
| remove handoff | `summarizeRemoveHandoff()` | console-slot clearing, preserved IRQ handoff, `tty_port_put()` release, and conditional `tty_vhangup()` then `tty_kref_put()` ordering | live tty removal, notifier callback execution, and host-backed hypervisor teardown |

## Review Guardrails

- keep this note tied only to `drivers/tty/hvc/hvc_console.zig` and its directly coupled teardown checks
- do not treat this note as evidence of live notifier callbacks, khvcd worker execution, or host-backed hypervisor I/O
- when the bounded teardown summaries change, update this note together with `Documentation/zigux/phase11-hvc-console-slice.md` and `Documentation/zigux/phase11-hvc-console-validation-matrix.md` so the driver keeps one honest ownership story