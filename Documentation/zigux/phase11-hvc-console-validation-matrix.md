# Phase 11 HVC Console Validation Matrix

This document records the first bounded kernel-integration validation matrix for the Zigux `hvc_console` lane.

## Status

- `PHASE11_HVC_CONSOLE_STATUS=hvc_tty_registration_handoff_landed`
- scope: keep the current `hvc_console` starter honest about what is already validated, name the next kernel-facing checkpoints, and avoid overclaiming tty or hypervisor integration before those behaviors exist in Zigux
- current repo reality:
  - `drivers/tty/hvc/hvc_console.zig`
  - `zigux/tests/phase11_hvc_console.zig`
  - `zigux/tests/phase11_hvc_cleanup.zig`
  - `zigux/tests/phase11_hvc_console_manifest.json`
  - `zigux/tests/phase11_hvc_console_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `.github/workflows/zigux-bootstrap.yml`

## Why This Exists

The bounded starter now covers slot validation, CRLF framing, flush-progress intent, teardown, the final-close wait boundary, the `hvc_cleanup()` tty-port release handoff, the remove-path handoff, and the tty-registration handoff summary. The live repo still needed one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which teardown-facing behaviors are already reviewable in bounded form versus still deferred
- which areas must remain out of scope until a later kernel-facing handoff lands

Without this matrix, the slice named the right next step but did not yet preserve the validation posture in one place.

## Kernel-Integration Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| early-console slot validation | `drivers/tty/hvc/hvc_console.zig` validates slot range, adapter presence, and `removed_vtermno` handling through `HvcConsoleLab.init()`, `instantiate()`, and `teardown()` | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via `zigux/tests/phase11_hvc_console.zig` in `.github/workflows/zigux-bootstrap.yml` | keep the same slot and teardown evidence wired into any future notifier-facing or sysrq-facing handoff summary | live early-console registration, notifier callbacks, and host-backed reads or writes |
| close-wait teardown boundary | `summarizeCloseBoundary()` records final-close, hung-up close, `HVC_CLOSE_WAIT`-shaped wait intent, and `port_initialized` clearing without claiming live tty teardown | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the final-close and hung-up-close checks in `zigux/tests/phase11_hvc_console.zig` | keep the same final-close evidence stable while the lane stays parked for another comparably small host-free follow-up | real tty core teardown, khvcd worker wakeups, and backend drain timing |
| cleanup tty-port release handoff | `summarizeCleanupHandoff()` keeps final-close and hangup-driven `tty_port_put()` release reviewable, now fails closed if the tty-port reference is already gone, and still leaves final destruction deferred to the tty-port lifecycle | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the dedicated final-close, hangup, and missing-reference cleanup checks in `zigux/tests/phase11_hvc_cleanup.zig` | leave this helper parked unless another comparably small host-free notifier or sysrq split is clearer than widening further into teardown ownership | real tty-port destructor timing, notifier callback execution, and host-backed teardown drains |
| remove-path teardown handoff | `summarizeRemoveHandoff()` keeps console-slot clearing, preserved IRQ ownership for the later hangup, `tty_port_put()` release, and conditional `tty_vhangup()` then `tty_kref_put()` ordering reviewable without claiming live tty removal | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the remove-path teardown assertions in `zigux/tests/phase11_hvc_console.zig` | leave this handoff parked unless another comparably small host-free notifier or sysrq split is obvious | live tty removal, notifier callback execution, and host-backed teardown timing |
| console write-path framing | `stageWrite()` covers CRLF framing, retry-after-`-EAGAIN`, partial-write, full-write, and fatal-drop bookkeeping without claiming hypervisor I/O | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the framing and flush-progress checks in `zigux/tests/phase11_hvc_console.zig` | keep the flush-progress surface stable while the lane grows a notifier-facing or sysrq-facing handoff rather than widening straight into backend transport code | host-backed putchars calls, sysrq dispatch, and khvcd polling loops |
| tty registration and khvcd behavior | `summarizeTtyRegistrationHandoff()` now records `setup_hvc_console()` registration intent, close-wait ownership, console-binding retention, khvcd wakeup visibility, and the still-deferred worker-execution boundary without claiming live tty registration | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the tty-registration handoff assertions in `zigux/tests/phase11_hvc_console.zig` | land one tiny notifier-facing or sysrq-facing handoff summary that names callback or dispatch boundaries without claiming worker execution | full tty-driver registration, khvcd thread lifecycle, sysrq dispatch, hotplug discovery, and live hypervisor transport |

## Review Rules

- treat this lane as a bounded driver-starter plus handoff-note lane until a notifier-facing or sysrq-facing handoff actually lands
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter instead of adding ad hoc Phase 11 CI steps
- do not claim notifier callbacks, khvcd execution, sysrq, or host-backed I/O coverage until the Zig surface and tests for those behaviors exist
- when the next notifier-facing or sysrq-facing handoff lands, update this matrix, the slice note, the survey note, and the survey manifest together so the lane keeps one truthful next step
