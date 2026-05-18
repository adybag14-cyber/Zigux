# Phase 11 HVC Console Validation Matrix

This document records the bounded current-head validation matrix for the Zigux
`hvc_console` lane.

## Status

- `PHASE11_HVC_CONSOLE_STATUS=public_readback_packet_truthful`
- lane: `P11-L17`
- reviewed against live `master`
- archival landing checkpoint: `ee124761ef3ef5fcc6bb9cd8b7fe8d1fce326839`
- scope: keep the current HVC console validation and teardown packet truthful
  without widening into live tty registration, notifier callback execution,
  khvcd worker execution, live sysrq dispatch, or host-backed teardown
- current public-readback packet in this lane:
  - `drivers/tty/hvc/hvc_console.zig`
  - `drivers/tty/hvc/hvc_console_verify.zig`
  - `drivers/tty/hvc/hvc_console_sysrq.zig`
  - `zigux/tests/phase11_hvc_console.zig`
  - `zigux/tests/phase11_hvc_cleanup.zig`
  - `zigux/tests/phase11_hvc_console_survey.zig`
  - `zigux/tests/phase11_hvc_console_manifest.json`
  - `zigux/tests/phase11_hvc_console_poll_retry_split.zig`
  - `Documentation/zigux/phase11-hvc-console-survey.md`
  - `Documentation/zigux/phase11-hvc-console-slice.md`
  - `Documentation/zigux/phase11-hvc-console-teardown-note.md`
  - `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  - `scripts/zigux/check-phase11-hvc-survey-packet.py`
- the GitHub contents API still returned flaky `404` reads for several of those
  same paths in this run, so this matrix now prefers direct public file-page
  readback before treating the HVC packet as missing
- current public readback did not stably confirm
  `zigux/tests/phase11_hvc_console_modem_control_split.zig`, and `zigux/Makefile`
  still exposes no dedicated `make -C zigux phase11-hvc-survey` route, so keep
  those claims bounded until a future reread reconfirms them

## Why This Exists

The Phase 11 roadmap still keeps `drivers/tty/hvc/hvc_console.c` in the simple
production-driver tranche where teardown parity and failure-mode reviewability
should deepen before any live execution claims.

This matrix therefore keeps the current HVC console packet truthful in the face
of readback drift: public GitHub file pages show the starter, helper, survey,
manifest, focused tests, teardown note, and checker on `master`, while the
contents API used by some earlier lane reads still reports flaky `404`s for a
subset of those same files.

## Current-Head Matrix

| lane surface | current evidence | bounded gate today | next bounded follow-up | out of scope for now |
| --- | --- | --- | --- | --- |
| starter and helper packet | public readback confirms `drivers/tty/hvc/hvc_console.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, and `drivers/tty/hvc/hvc_console_sysrq.zig` are present on current `master` | keep the matrix, survey note, slice note, teardown note, and checker aligned with the publicly readable starter packet instead of downgrading those files to missing | if a future reread shows one of those starter files disappearing again, refresh the matrix and the coupled survey surfaces together in one bounded pass | live tty registration, notifier callback execution, khvcd worker execution, live sysrq dispatch, and host-backed teardown |
| focused teardown and replay packet | public readback confirms `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, and `zigux/tests/phase11_hvc_console_poll_retry_split.zig` remain present beside the survey-backed packet | keep final-close teardown, poll-retry, cleanup, layout-proof, and survey-gate evidence explicit across the current packet without claiming broader runtime closure | recheck `zigux/tests/phase11_hvc_console_modem_control_split.zig` only if a later lane needs that exact same-lane split surface; otherwise leave the current packet parked | reconstructing a larger replay family or claiming end-to-end runtime parity from host-free tests alone |
| failure-mode and teardown evidence | the current starter and manifest still keep close teardown, notifier-add outcome, khvcd polling and sleep handoff, hangup disconnect, remove handoff, header boundary, and cleanup ownership reviewable; the cleanup replay keeps tty-port release boundaries explicit; the verify helper remains present for targetless notifier and helper-local review surfaces | keep those handoffs named directly in the matrix instead of treating them as archival-only cues | if one new same-lane wording gap appears, keep the fix to one matrix or note clarification tied to one of those already-landed handoffs | widening into notifier delivery, live khvcd scheduling, or hardware-backed lifecycle claims |
| survey checker and route boundary | public readback confirms `scripts/zigux/check-phase11-hvc-survey-packet.py` is present, while `zigux/Makefile` still shows no dedicated `make -C zigux phase11-hvc-survey` route | treat the checker as current-head evidence, but keep the dedicated make route absent until direct readback proves it exists | if the Makefile grows a dedicated HVC survey route later, refresh this matrix and the coupled docs together | reviving missing build-route claims from historical wording alone |
| readback-drift handling | this run reproduced a real tooling split: the GitHub contents API returned `404` for several HVC paths that public GitHub file pages still show on `master` | when those sources disagree, cross-check with the public repo fallback before recording a packet shrink or repo-reality gap | keep future same-lane matrix updates explicit about which read path established the current evidence | treating one flaky contents read as enough proof to reopen or collapse the HVC packet |

## Failure-Mode Evidence

- `drivers/tty/hvc/hvc_console.zig` remains present and keeps CRLF framing,
  flush intent, final-close teardown, tty-registration handoff, notifier-add
  open handoff, khvcd polling-contract, khvcd worker-entry, khvcd
  sleep-and-reschedule handoff, `__hvc_poll` drain-order, `hvc_hangup()`
  disconnect, `hvc_remove()` handoff, and `hvc_cleanup()` tty-port release
  summaries reviewable on current `master`.
- `zigux/tests/phase11_hvc_cleanup.zig` remains present and keeps the
  `hvc_cleanup()` tty-port release boundary explicit in a host-free replay.
- `drivers/tty/hvc/hvc_console_verify.zig` remains present, so the matrix keeps
  helper-local verification and targetless notifier review surfaces in the
  current packet instead of downgrading them to archival-only vocabulary.
- `drivers/tty/hvc/hvc_console_sysrq.zig` remains present, so the matrix can
  keep bounded sysrq-handling support explicit without claiming live sysrq
  dispatch.
- `zigux/tests/phase11_hvc_console_manifest.json` still records the same-lane
  starter, teardown, hangup, remove, header, layout, signature, and matrix
  expectations, so use that manifest as the current packet inventory instead of
  reconstructing the lane from stale missing-file assumptions.
- The checker remains present, but the dedicated Makefile survey route does not,
  so fail-closed survey evidence is current-head truth while the route claim
  remains out of scope.

## Replay Posture

- Treat the publicly readable starter, helper, survey, manifest, focused test,
  teardown-note, matrix, and checker files as the truthful current-head HVC
  packet for this lane.
- Treat the contents-API `404` results from this run as flaky readback, not as
  sufficient proof that the packet disappeared from `master`.
- Keep `zigux/tests/phase11_hvc_console_modem_control_split.zig` bounded as
  unconfirmed until a future reread verifies it directly.
- Keep `zigux/Makefile` explicit only as the returned file; do not treat it as
  proof that a dedicated `phase11-hvc-survey` route exists.

## Review Rules

- Do not claim live notifier callback execution, tty registration, khvcd worker
  execution, live sysrq dispatch, or host-backed teardown from this matrix.
- If the publicly readable HVC packet changes, update the matrix together with
  the coupled HVC survey note, slice note, teardown note, or checker in one
  bounded pass.
- When the GitHub contents API and the public repo disagree, cross-check with
  the public repo fallback before recording a same-lane packet shrink.
