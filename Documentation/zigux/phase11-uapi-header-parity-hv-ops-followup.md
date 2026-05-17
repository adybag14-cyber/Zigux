# Phase 11 UAPI Header Parity `hv_ops` Follow-up

## Status
- `PHASE11_HV_OPS_FOLLOWUP_STATUS=shared_packet_gap_recorded`
- lane: `P11-L08`
- reviewed against current `master` on `2026-05-17`
- scope: keep the shared Phase 11 header-parity packet honest about what is already machine-checked today and what still needs one bounded follow-up for `struct hv_ops`

## Current Repo Reality
- `Documentation/zigux/phase11-uapi-header-parity-survey.md` and `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` both describe the shared packet as if `struct hv_ops` layout proof is already part of the landed shared replay.
- `zigux/tests/phase11_uapi_header_parity_survey.zig` currently keeps the bounded `watchdog_info` and `winsize` layout proofs, the shared build-hook readback, and the exported `hvc_console.h` declaration checks explicit.
- The same shared survey source still does not carry a matching in-route `struct hv_ops` callback-table layout proof even though `drivers/tty/hvc/hvc_console.h` exposes that public surface.
- `zigux/tests/phase11_uapi_header_parity_manifest.json` still summarizes the shared packet around `watchdog_info`, `winsize`, and the exported HVC helper surface only.
- Draft PR `#302` (`test(phase11): add hv_ops layout proof packet`) already carries a focused dedicated proof packet in `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig` plus its own build file, but that proof is not yet part of the shared `phase11-uapi-header-parity-survey-tests` route on current `master`.

## Why This Note Exists
The shared Phase 11 header packet is supposed to stay reviewable and bounded. Right now the easiest way for that packet to drift is for the shared note and validation matrix to imply that `hv_ops` is already covered in the same landed replay path when the live shared survey source does not yet prove it.

This note records that gap directly so later rereads do not mistake dedicated proof work for shared-packet closure.

## Next Bounded Step
- If the shared packet should truly own `hv_ops`, add one bounded `struct hv_ops` size, alignment, and callback-offset proof to `zigux/tests/phase11_uapi_header_parity_survey.zig`, then sync `zigux/tests/phase11_uapi_header_parity_manifest.json` and `scripts/zigux/check-phase11-header-boundary-packet.py` to fail closed on that new shared proof.
- If the dedicated packet from PR `#302` should remain separate, then the shared note and validation matrix should be narrowed so they stop describing `hv_ops` as already landed inside the shared survey route.

## Boundaries
- This note does not claim notifier execution, khvcd worker behavior, tty registration, host-backed HVC transport, or watchdog-core integration.
- This note does not merge or supersede the dedicated `P11-L13` proof branch.
- The immediate job here is shared-packet truthfulness only.
