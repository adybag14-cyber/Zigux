# Phase 11 UAPI Header Parity `hv_ops` Follow-up

## Status

- `PHASE11_HV_OPS_FOLLOWUP_STATUS=adjacent_hv_ops_proof_returned_shared_replay_still_missing`
- lane: `P11-L05`
- reviewed against current `master` on `2026-05-27`
- scope: keep the shared Phase 11 header-parity packet honest about the returned
  `hv_ops` proof shard while preserving the boundary between adjacent proof
  evidence and the still-missing shared replay family

## Current Repo Reality

- `Documentation/zigux/phase11-uapi-header-parity-survey.md` and
  `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` now
  frame `struct hv_ops` as adjacent proof-shard evidence rather than as a
  restored shared replay route.
- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig` and
  `zigux/tests/phase11_hvc_hv_ops_layout_build.zig` keep the bounded
  `struct hv_ops` size, alignment, and callback-table offsets directly readable
  on current `master`.
- `zigux/helpers/layout_assert.zig`, `drivers/tty/hvc/hvc_console.h`, and
  `drivers/tty/hvc/hvc_console.zig` remain the returned substrate and direct
  proof inputs for that `hv_ops` shard.
- `scripts/zigux/check-phase11-header-boundary-packet.py` now fail-closes on
  the survey, validation matrix, checker-coverage note, and this follow-up note
  so the adjacent `hv_ops` packet stays aligned with current-head wording.
- The same current-head packet still does not rematerialize
  `zigux/tests/phase11_uapi_header_parity_manifest.json`,
  `zigux/tests/phase11_uapi_header_parity_survey.zig`, or
  `zigux/tests/phase11_build.zig`, so the shared manifest, survey source, and
  build route remain absent on current `master`.

## Why This Note Exists

The `hv_ops` gap changed shape.

The live repo no longer needs a reminder that `hv_ops` proof is missing
entirely. Instead it needs a smaller truthfulness note that distinguishes
between:

- the returned adjacent `hv_ops` proof shard that is directly readable today
- the still-missing shared replay family that would be required to claim
  restored cross-driver header-parity closure

This note records that distinction directly so later rereads do not mistake the
returned `hv_ops` proof shard for recovery of the older shared replay packet.

## Next Bounded Step

- If the shared packet should truly own `hv_ops`, re-land a directly readable
  shared manifest, survey source, and build route, then sync this note together
  with the survey, validation matrix, and header-boundary checker in one bounded
  pass.
- If the dedicated packet should remain separate, keep the shared note and
  validation matrix bounded to adjacent proof-shard language and avoid claiming
  that the older shared replay family has returned.

## Boundaries

- This note does not claim notifier execution, khvcd worker behavior, tty
  registration, host-backed HVC transport, or watchdog-core integration.
- This note does not claim that the missing shared manifest, survey source, or
  build route have returned.
- The immediate job here is current-head truthfulness for the returned `hv_ops`
  proof shard only.
