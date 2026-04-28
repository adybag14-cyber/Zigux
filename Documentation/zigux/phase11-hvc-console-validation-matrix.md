# Phase 11 HVC Console Validation Matrix

This document records the first bounded kernel-integration validation matrix for the Zigux `hvc_console` lane.

## Status

- `PHASE11_HVC_CONSOLE_STATUS=khvcd_polling_contract_landed`
- scope: keep the current `hvc_console` starter honest about what is already validated, name the next kernel-facing checkpoints, and avoid overclaiming tty or hypervisor integration before those behaviors exist in Zigux
- current repo reality:
  - `drivers/tty/hvc/hvc_console.zig`
  - `zigux/tests/phase11_hvc_console.zig`
  - `zigux/tests/phase11_hvc_console_manifest.json`
  - `zigux/tests/phase11_hvc_console_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `.github/workflows/zigux-bootstrap.yml`

## Why This Exists

The bounded starter now covers slot validation, CRLF framing, flush-progress intent, teardown, the final-close wait boundary, a tiny tty-registration handoff summary, and a tiny khvcd polling-contract summary. The live repo still needed one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which khvcd and notifier-facing behaviors are already reviewable in bounded form versus still deferred
- which areas must remain out of scope until a later kernel-facing handoff lands

Without this matrix, the slice named the right next step but did not yet preserve the validation posture in one place.

## Kernel-Integration Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| early-console slot validation | `drivers/tty/hvc/hvc_console.zig` validates slot range, adapter presence, and `removed_vtermno` handling through `HvcConsoleLab.init()`, `instantiate()`, and `teardown()` | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via `zigux/tests/phase11_hvc_console.zig` in `.github/workflows/zigux-bootstrap.yml` | keep the same slot and teardown evidence wired into any future tty-registration handoff summary | live early-console registration, notifier callbacks, and host-backed reads or writes |
| exported header surface parity | `headerParitySnapshot()` now keeps `drivers/tty/hvc/hvc_console.h` limits and shape reviewable by mirroring `MAX_NR_HVC_CONSOLES`, `HVC_ALLOC_TTY_ADAPTERS`, the `hv_ops` callback table, and exported `hvc_instantiate` or `hvc_alloc` or `hvc_remove` or `hvc_poll` or `hvc_resize` surface metadata without claiming those helpers execute in Zigux | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the header-parity assertions in `zigux/tests/phase11_hvc_console.zig` | carry the same header-surface evidence forward when the tty-registration handoff lands so exported helper naming and callback scope stay honest | live tty helper execution, notifier callbacks, early-console registration, and host-backed hypervisor transport |
| close-wait teardown boundary | `summarizeCloseBoundary()` records final-close, hung-up close, `HVC_CLOSE_WAIT`-shaped wait intent, and `port_initialized` clearing without claiming live tty teardown | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the final-close and hung-up-close checks in `zigux/tests/phase11_hvc_console.zig` | carry the same final-close evidence forward while the lane deepens khvcd worker-entry and notifier drain summaries | real tty core teardown, khvcd worker wakeups, and backend drain timing |
| console write-path framing | `stageWrite()` covers CRLF framing, retry-after-`-EAGAIN`, partial-write, full-write, and fatal-drop bookkeeping without claiming hypervisor I/O | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the framing and flush-progress checks in `zigux/tests/phase11_hvc_console.zig` | keep the flush-progress surface stable while the lane grows a khvcd worker-entry summary rather than widening straight into backend transport code | host-backed putchars calls, sysrq dispatch, and khvcd worker loops |
| tty registration handoff | `summarizeTtyRegistrationHandoff()` now keeps `setup_hvc_console()`-adjacent registration intent, close-wait ownership, notifier boundaries, and khvcd wakeup intent reviewable without claiming `tty_register_driver()` or helper execution | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the tty-registration handoff assertions in `zigux/tests/phase11_hvc_console.zig` | carry the same handoff evidence forward while the lane deepens khvcd worker-entry behavior before worker execution lands | full tty-driver registration, notifier execution, setup helper side effects, and live hypervisor transport |
| khvcd polling contract | `summarizeKhvcdPollingContract()` now keeps notifier-driven versus polling-driven wakeups, bounded reschedule intent, and teardown-facing host-I/O pressure reviewable without claiming khvcd worker execution | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the khvcd polling-contract assertions in `zigux/tests/phase11_hvc_console.zig` | deepen the next bounded khvcd worker-entry summary so poll-loop drain ordering and backend handoff boundaries stay explicit before host-backed execution lands | live khvcd thread scheduling, notifier callbacks, host-backed getchars or putchars execution, and sysrq dispatch |

## Observed Replay Evidence

- shared replay observed on `master` currently runs `phase11-hvc-console-tests` but not `phase11-hvc-console-survey-tests`
- exact shared command:
  - `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- exact shared outcome:
  - `Build Summary: 17/17 steps succeeded; 42/42 tests passed`
  - included hvc artifact: `run test phase11-hvc-console-tests 7 pass (7 total)`
  - no `phase11-hvc-console-survey-tests` artifact is present in that shared replay
- dedicated survey replay still passes separately:
  - `zig test zigux/tests/phase11_hvc_console_survey.zig`
  - `2/2 ... OK`

## Review Rules

- treat this lane as a bounded driver-starter plus validation-note lane until a khvcd worker-entry helper actually lands
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter instead of adding ad hoc Phase 11 CI steps
- do not claim khvcd, sysrq, notifier, or host-backed I/O coverage until the Zig surface and tests for those behaviors exist
- when the khvcd worker-entry helper lands, update this matrix, the slice note, the survey note, and the survey manifest together so the lane keeps one truthful next step
