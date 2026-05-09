# Phase 11 HVC Console Teardown Note

This note captures the bounded teardown ownership that is already reviewable in the Zigux `hvc_console` starter anchored to `drivers/tty/hvc/hvc_console.c`.

The current driver-local teardown surface is intentionally small and host-free:

- `summarizeCloseBoundary()` owns the close-side decision about whether the current call is a hung-up short circuit, an already-failed open rollback, a non-final close, or the final-close path that carries the `HVC_CLOSE_WAIT`-shaped wait intent. When notifier setup has already failed and `port_initialized` never became true, it keeps the no-wait final-close rollback explicit without fabricating live tty teardown.
- `summarizeCleanupHandoff()` owns the follow-on `hvc_cleanup()` handoff where `tty_port_put()` must still be requested for a live tty-port reference, including the hangup-driven and failed-open cleanup paths, while final destruction remains deferred to the tty-port lifecycle.
- `summarizeRemoveHandoff()` owns the `hvc_remove()` handoff where it decides whether the console-slot binding still needs clearing, keeps IRQ ownership preserved for the later hangup path when a tty is still present, leaves `tty_vhangup()` then `tty_kref_put()` ordering relevant only for the tty-present branch, and keeps the already-absent-tty branch explicit by suppressing both calls when no tty remains.
- `summarizeHangupDisconnect()` owns the `hvc_hangup()` disconnect boundary where resize-work cancellation, stale-count short-circuiting, tty detachment, buffered-write clearing, oversized buffered-write rejection, and notifier-hangup ownership stay reviewable without claiming live callback execution.

## Teardown Ownership

| boundary | current Zigux owner | what stays reviewable now | still out of scope |
| --- | --- | --- | --- |
| close boundary | `summarizeCloseBoundary()` | failed-open no-wait final close, final-close detection, hung-up short-circuiting, `port_initialized` clearing, and `HVC_CLOSE_WAIT`-shaped wait intent | live tty close timing, backend drain timing, and khvcd wakeups |
| cleanup handoff | `summarizeCleanupHandoff()` | final-close versus hangup-driven or failed-open `tty_port_put()` release, missing-reference failure, and deferred final destruction | real tty-port destructor timing, notifier callback execution, and host-backed teardown |
| remove handoff | `summarizeRemoveHandoff()` | console-slot clearing versus already-detached binding, preserved IRQ handoff, `tty_port_put()` release, conditional `tty_vhangup()` then `tty_kref_put()` ordering, and the already-absent-tty no-hangup branch | live tty removal, notifier callback execution, and host-backed hypervisor teardown |
| hangup disconnect | `summarizeHangupDisconnect()` | resize-work cancellation, stale-count short-circuiting, tty detachment, buffered-write clearing, oversized buffered-write rejection, notifier-hangup ownership, and kept console binding | live notifier callback execution, remove-time tty ownership races, IRQ teardown, and host-backed disconnect timing |

## Review Guardrails

- keep this note tied only to `drivers/tty/hvc/hvc_console.zig` and its directly coupled teardown and disconnect checks
- do not treat this note as evidence of live notifier callbacks, khvcd worker execution, or host-backed hypervisor I/O
- when the bounded teardown summaries change, update this note together with `Documentation/zigux/phase11-hvc-console-slice.md` and `Documentation/zigux/phase11-hvc-console-validation-matrix.md` so the driver keeps one honest ownership story
