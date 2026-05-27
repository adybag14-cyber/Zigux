# Phase 7 Base64 Slice

This note tracks a bounded Phase 7 runtime leaf-library packet around `lib/base64.c`.

## Status

- `PHASE7_STATUS=helper_local_slice_note_test_build_survey_manifest_checker_anchor`
- `PHASE7_SLICE=base64-runtime-leaf`
- `PHASE7_LANE_KEY=P7-L14`
- scope: keep this lane limited to the helper-local `base64` review packet rooted at `lib/base64.zig`, one dedicated replay, one dedicated standalone build entrypoint, one dedicated survey, one dedicated manifest, and one dedicated checker
- lane state: current packet surfaces are `Documentation/zigux/phase7-base64-slice.md`, `scripts/zigux/check-phase7-base64-packet.py`, `lib/base64.zig`, `zigux/tests/phase7_base64.zig`, `zigux/tests/phase7_base64_build.zig`, `zigux/tests/phase7_base64_survey.zig`, and `zigux/tests/phase7_base64_manifest.json`

## Why This Slice Exists

Phase 7 is where Zigux carries bounded runtime leaf helpers in product-facing locations.

`lib/base64.zig` is already a substantive helper on current `master`, but this packet keeps the same-lane review surface narrow instead of reopening the broader shared Phase 7 reminder. The dedicated packet stays focused on:

- standard, urlsafe, and IMAP alphabets
- padded and unpadded short-tail handling
- variant-pinned convenience wrappers staying separate from foreign alphabets
- exact-span slice and allocator companions for bounded caller ownership

## Gates

1. keep the returned helper explicit
- `lib/base64.zig`

2. keep the helper-local packet explicit
- `Documentation/zigux/phase7-base64-slice.md`
- `scripts/zigux/check-phase7-base64-packet.py`
- `zigux/tests/phase7_base64.zig`
- `zigux/tests/phase7_base64_build.zig`
- `zigux/tests/phase7_base64_survey.zig`
- `zigux/tests/phase7_base64_manifest.json`

3. keep the packet bounded
- do not treat this packet as ownership of the broader shared Phase 7 docs-root, tests-root, Makefile, or workflow reminder surfaces
- do not widen this packet into streaming decode, shared wrapper recovery, or broader runtime-family validator claims

## Current Helper Surface

The current helper-local packet keeps these exported surfaces explicit:

- `chars()`, `bytesStd()`, `bytesUrlsafe()`, and `bytesImap()`
- `encodeStd()`, `encodeUrlsafe()`, and `encodeImap()`
- `decodeStd()`, `decodeUrlsafe()`, and `decodeImap()`
- variant-pinned slice and allocator companions for the same bounded alphabets

The current dedicated replay keeps these bounded proofs explicit:

- standard padded convenience wrappers round-trip the current five-byte packet unchanged
- urlsafe short tails stay inside the urlsafe alphabet and reject standard `+`-prefixed foreign tails
- IMAP short tails stay inside the IMAP alphabet and reject slash-backed standard tails
- exact-span slice and allocator companions stay aligned with the standard packet without widening into broader ownership or streaming claims

## Next Bounded Step

Keep same-lane follow-through limited to this helper-local `base64` packet and only reopen it when a fresh reread finds checker, manifest, replay, build-entrypoint, or slice-note drift inside these returned packet members before widening into any broader Phase 7 shared reminder work.
