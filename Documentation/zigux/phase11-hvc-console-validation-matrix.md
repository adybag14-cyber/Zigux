# Phase 11 HVC Console Validation Matrix

This document records the bounded kernel-integration validation matrix for the Zigux `hvc_console` lane.

## Status

- `PHASE11_HVC_CONSOLE_STATUS=hangup_disconnect_landed`
- reviewed against live `master` `97b6925916ab092c5442f8276c2ab503df0f280d`
- scope: keep the current `hvc_console` starter honest about what is already validated, name the next kernel-facing checkpoints, and avoid overclaiming tty or hypervisor integration before those behaviors exist in Zigux
- current repo reality:
  - `drivers/tty/hvc/hvc_console.zig`
  - `zigux/tests/phase11_hvc_console.zig`
  - `zigux/tests/phase11_hvc_console_manifest.json`
  - `zigux/tests/phase11_hvc_console_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `.github/workflows/zigux-bootstrap.yml`

## Why This Exists

The bounded starter now covers slot validation, CRLF framing, flush-progress intent, teardown, the final-close wait boundary, a tiny tty-registration handoff summary, a tiny khvcd polling-contract summary, a tiny khvcd worker-entry summary, a tiny khvcd sleep-and-reschedule handoff summary, a tiny `__hvc_poll()` drain-order summary, and a tiny `hvc_hangup()` disconnect summary. The live repo still needs one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which khvcd-facing behaviors are already reviewable in bounded form versus still deferred
- which teardown-facing areas are now parked in bounded form versus still out of scope until a later kernel-facing handoff lands

Without this matrix, the slice preserves the parked boundary but does not keep the validation posture in one place.

## Kernel-Integration Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| early-console slot validation | `drivers/tty/hvc/hvc_console.zig` validates slot range, adapter presence, and `removed_vtermno` handling through `HvcConsoleLab.init()`, `instantiate()`, and `teardown()` | `zigux/tests/phase11_build.zig` continues to run `zigux/tests/phase11_hvc_console.zig` inside the shared Phase 11 starter replay | keep the same slot and teardown evidence wired into any future tty-registration handoff or poll-drain summary | live early-console registration, notifier callbacks, and host-backed reads or writes |
| close-wait teardown boundary | `summarizeCloseBoundary()` records final-close, hung-up close, `HVC_CLOSE_WAIT`-shaped wait intent, and `port_initialized` clearing without claiming live tty teardown | `zigux/tests/phase11_hvc_console.zig` keeps the final-close and hung-up-close assertions inside the shared Phase 11 replay | keep the same final-close evidence stable while the lane stays parked for another comparably small host-free follow-up | real tty core teardown, khvcd worker wakeups, and backend drain timing |
| console write-path framing | `stageWrite()` covers CRLF framing, zero-progress or retry-after-`-EAGAIN` drain intent, partial-write, full-write, and fatal-drop bookkeeping without claiming hypervisor I/O | `zigux/tests/phase11_hvc_console.zig` keeps the framing and flush-progress checks inside the shared Phase 11 replay | keep the flush-progress surface stable unless a later bounded host-free handoff clearly needs the same evidence packet | host-backed putchars calls, sysrq dispatch, and khvcd worker loops |
| tty registration handoff | `summarizeTtyRegistrationHandoff()` keeps `setup_hvc_console()`-adjacent registration intent, close-wait ownership, notifier boundaries, and khvcd wakeup intent reviewable without claiming `tty_register_driver()` or helper execution | `zigux/tests/phase11_hvc_console.zig` keeps the tty-registration handoff assertions inside the shared Phase 11 replay | carry the same handoff evidence forward only if a later host-free notifier or sysrq split lands | full tty-driver registration, notifier execution, setup helper side effects, and live hypervisor transport |
| khvcd polling contract | `summarizeKhvcdPollingContract()` keeps notifier-driven versus polling-driven wakeups, bounded reschedule intent, and teardown-facing host-I/O pressure reviewable without claiming khvcd worker execution | `zigux/tests/phase11_hvc_console.zig` keeps the khvcd polling-contract assertions inside the shared Phase 11 replay | keep the poll-mask evidence parked unless a later host-free khvcd or notifier split becomes obvious | live khvcd thread scheduling, notifier callbacks, host-backed getchars or putchars execution, and sysrq dispatch |
| khvcd worker entry | `summarizeKhvcdWorkerEntry()` keeps freezer checks, kick-reset timing, xmon-forced read polling, mutex-backed list walks, sleep-versus-timeout choices, and timeout-backoff growth reviewable without claiming live worker execution | `zigux/tests/phase11_hvc_console.zig` now keeps the worker-entry sleep and backoff assertions inside the shared Phase 11 replay | keep the worker-entry evidence stable unless a later host-free follow-up can stay smaller than live worker execution | live khvcd kthread execution, scheduler timing, backend poll loops, and host-backed transport |
| khvcd sleep-and-reschedule handoff | `summarizeKhvcdSleepHandoff()` keeps the pre-sleep kick check, the interruptible-state recheck, untimed `schedule()` versus timed `schedule_timeout_interruptible()` selection, the guarded timeout tick, and the running-state restore reviewable without claiming live khvcd execution | `zigux/tests/phase11_hvc_console.zig` now keeps the timed-sleep, untimed-sleep, pre-state kick, and post-state kick assertions inside the shared Phase 11 replay | leave this handoff parked unless another comparably small host-free khvcd split is obvious | live khvcd kthread execution, scheduler timing, notifier callbacks, and host-backed transport |
| `__hvc_poll()` drain ordering | `summarizePollDrainOrder()` keeps write-drain-before-read ordering, stalled-write timeout posture, IRQ-free read-poll rearm intent, `-EPIPE` hangup pressure, and tty-wakeup versus flip-push sequencing reviewable without claiming host-backed polling execution | `zigux/tests/phase11_hvc_console.zig` now keeps the drain-order and wakeup sequencing assertions inside the shared Phase 11 replay | leave this helper packet parked unless a later host-free khvcd or notifier split needs the same drain-order evidence | live `get_chars()` or `put_chars()` execution, khvcd thread scheduling, notifier callback execution, and sysrq dispatch |
| `hvc_hangup()` disconnect boundary | `summarizeHangupDisconnect()` keeps resize-work cancellation, the stale-count short-circuit, tty detachment, buffered-write clearing, and `notifier_hangup` ownership reviewable without claiming live callback execution | `zigux/tests/phase11_hvc_console.zig` now keeps the active-hangup and stale-hangup assertions inside the shared Phase 11 replay | leave this helper parked unless a comparably small host-free `hvc_remove()` handoff becomes obvious | live notifier callback execution, remove-time tty ownership races, irq teardown, and host-backed disconnect timing |

## Failure-Mode Evidence

- khvcd timeout underflow is now pinned in the focused hvc replay: `zigux/tests/phase11_hvc_console.zig` drives `summarizeKhvcdWorkerEntry()` with `timeout_ms = 0` plus a pending read poll and proves that the worker path clamps back to the minimum timeout, widens once to `11ms`, and still avoids the max-timeout cap unless the poll backlog really justifies it.
- `__hvc_poll()` hangup pressure is now pinned separately from the throttled and detached cases: `zigux/tests/phase11_hvc_console.zig` drives `summarizePollDrainOrder()` with a tty-attached `-EPIPE` read result and proves that the helper keeps `read_hangup_pending`, preserves the IRQ-free read-poll rearm posture, and carries backend handoff pressure without inventing a flip-buffer push or wakeup ordering that the bounded model does not own.
- these failure edges stay deliberately host-free: they validate the current helper contracts for timeout normalization and teardown-facing hangup bookkeeping, not live khvcd execution, notifier callbacks, tty-core teardown, or hypervisor-backed polling.

## Replay Posture

- the shared Phase 11 gate for this lane remains `zigux/tests/phase11_build.zig`
- the dedicated archival survey gate remains `zigux/tests/phase11_hvc_console_survey.zig`
- the dedicated survey replay still passes separately from the shared Phase 11 replay and remains the archival checkpoint for this lane
- this bounded worker-entry, sleep-handoff, drain-order, and hangup-disconnect evidence stays inside the existing starter, test, survey, manifest, and note files rather than adding a new Phase 11 entry point

## Review Rules

- treat this lane as a bounded driver-starter plus validation-note lane until another comparably small host-free khvcd, notifier, or remove handoff actually lands
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter instead of adding ad hoc Phase 11 CI steps
- do not claim khvcd execution, sysrq, notifier callbacks, or host-backed I/O coverage until the Zig surface and tests for those behaviors exist
- after this landed `hvc_hangup()` disconnect handoff, update this matrix, the slice note, the survey note, and the survey manifest together again only if a later host-free khvcd, notifier, sysrq, or remove split actually lands so the lane keeps one truthful next step
