# Phase 11 HVC Console Validation Matrix

This document records the first bounded kernel-integration validation matrix for the Zigux `hvc_console` lane.

## Status

- `PHASE11_HVC_CONSOLE_STATUS=kernel_integration_validation_matrix_landed`
- scope: keep the current `hvc_console` starter honest about what is already validated, name the next kernel-facing checkpoints, and avoid overclaiming tty or hypervisor integration before those behaviors exist in Zigux
- current repo reality:
  - `drivers/tty/hvc/hvc_console.zig`
  - `zigux/tests/phase11_hvc_console.zig`
  - `zigux/tests/phase11_hvc_console_manifest.json`
  - `zigux/tests/phase11_hvc_console_survey.zig`
  - `zigux/tests/phase11_build.zig`
  - `.github/workflows/zigux-bootstrap.yml`

## Why This Exists

The bounded starter now covers slot validation, CRLF framing, flush-progress intent, teardown, and the final-close wait boundary. The live repo still needed one reviewable note that explains:

- which parts of the lane are already exercised by the shared Phase 11 gate
- which tty and close-boundary behaviors are only documented as the next follow-up
- which areas must remain out of scope until a later kernel-facing handoff lands

Without this matrix, the slice named the right next step but did not yet preserve the validation posture in one place.

## Kernel-Integration Matrix

| lane surface | current evidence | shared gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| early-console slot validation | `drivers/tty/hvc/hvc_console.zig` validates slot range, adapter presence, and `removed_vtermno` handling through `HvcConsoleLab.init()`, `instantiate()`, and `teardown()` | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via `zigux/tests/phase11_hvc_console.zig` in `.github/workflows/zigux-bootstrap.yml` | keep the same slot and teardown evidence wired into any future tty-registration handoff summary | live early-console registration, notifier callbacks, and host-backed reads or writes |
| exported header surface parity | `headerParitySnapshot()` now keeps `drivers/tty/hvc/hvc_console.h` limits and shape reviewable by mirroring `MAX_NR_HVC_CONSOLES`, `HVC_ALLOC_TTY_ADAPTERS`, the `hv_ops` callback table, and exported `hvc_instantiate` or `hvc_alloc` or `hvc_remove` or `hvc_poll` or `hvc_resize` surface metadata without claiming those helpers execute in Zigux | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the header-parity assertions in `zigux/tests/phase11_hvc_console.zig` | carry the same header-surface evidence forward when the tty-registration handoff lands so exported helper naming and callback scope stay honest | live tty helper execution, notifier callbacks, early-console registration, and host-backed hypervisor transport |
| close-wait teardown boundary | `summarizeCloseBoundary()` records final-close, hung-up close, `HVC_CLOSE_WAIT`-shaped wait intent, and `port_initialized` clearing without claiming live tty teardown | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the final-close and hung-up-close checks in `zigux/tests/phase11_hvc_console.zig` | add a tiny tty-registration handoff summary that keeps `setup_hvc_console()` teardown parity reviewable before any host-backed drain path lands | real tty core teardown, khvcd worker wakeups, and backend drain timing |
| console write-path framing | `stageWrite()` covers CRLF framing, retry-after-`-EAGAIN`, partial-write, full-write, and fatal-drop bookkeeping without claiming hypervisor I/O | `zig build test --build-file zigux/tests/phase11_build.zig --summary all` via the framing and flush-progress checks in `zigux/tests/phase11_hvc_console.zig` | keep the flush-progress surface stable while the lane grows a tty-registration handoff rather than widening straight into backend transport code | host-backed putchars calls, sysrq dispatch, and khvcd polling loops |
| tty registration and khvcd behavior | no live Zigux implementation yet; the current repo only records these as the next kernel-facing checkpoint in the slice, survey, and manifest | none beyond the survey or manifest guard that keeps the missing work explicit | land one tiny tty-registration handoff summary that names registration intent, close-wait ownership, and khvcd-facing boundaries without claiming worker execution | full tty-driver registration, khvcd thread lifecycle, sysrq, hotplug discovery, and live hypervisor transport |

## Observed Replay Evidence

- shared replay observed on `master` currently runs `phase11-hvc-console-tests` but not `phase11-hvc-console-survey-tests`
- exact shared command:
  - `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- exact shared outcome:
  - `Build Summary: 15/15 steps succeeded; 29/29 tests passed`
  - included hvc artifact: `run test phase11-hvc-console-tests 5 pass (5 total)`
  - no `phase11-hvc-console-survey-tests` artifact is present in that shared replay
- dedicated survey replay still passes separately:
  - `zig test zigux/tests/phase11_hvc_console_survey.zig`
  - `2/2 ... OK`

## Review Rules

- treat this lane as a bounded driver-starter plus validation-note lane until a tty-registration handoff actually lands
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter instead of adding ad hoc Phase 11 CI steps
- do not claim khvcd, sysrq, notifier, or host-backed I/O coverage until the Zig surface and tests for those behaviors exist
- when the tty-registration handoff lands, update this matrix, the slice note, the survey note, and the survey manifest together so the lane keeps one truthful next step
