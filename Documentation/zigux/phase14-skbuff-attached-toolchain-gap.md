# Phase 14 Skbuff Attached-Toolchain Evidence Gap

## Status

- `PHASE14_SKBUFF_TOOLCHAIN_GAP=present`
- `PHASE14_SKBUFF_TOOLCHAIN_GAP_KIND=anchor_packet_absent_under_attached_toolchain_policy`
- `PHASE14_SKBUFF_TOOLCHAIN_GAP_SCOPE=skbuff_packet_truthfulness_only`
- `PHASE14_SKBUFF_TOOLCHAIN_GAP_STATUS_BUCKET=study_only`
- `PHASE14_SKBUFF_TOOLCHAIN_GAP_OWNER=Repo Tooling Pod`
- re-read against current `master` on `2026-05-18`

## Why this gap note exists

The Phase 14 roadmap keeps `net/core/skbuff.c` under freeze-in-C governance.
The attached-toolchain guidance also says to run the narrowest honest Zig
verification available and not to imply compile checks that the live repo
cannot actually replay.

Current `master` already records that the earlier skbuff anchor packet is gone:

- `Documentation/zigux/phase14-skbuff-bridge-survey.md` says current `master`
  no longer exposes `zigux/tests/phase14_skbuff_bridge.zig`,
  `zigux/tests/phase14_build.zig`, `net/core/skbuff_bridge.zig`, or
  `zigux/tests/phase14_skbuff_bridge_manifest.json`
- the same survey note says the earlier `full_bundle_only` compile path is
  archival only and must not be treated as live compile evidence on current
  `master`

That means even when the attached Zig toolchain is available, there is no live
skbuff-local packet to compile on current `master`.

## Current bounded gap

The skbuff survey is truthful today, but it does not yet have a dedicated
fail-closed checker that preserves the attached-toolchain discipline around
that absent-packet state. A later note edit could accidentally reintroduce live
compile wording before the bounded skbuff packet itself returns.

## Current guardrail

`scripts/zigux/check-phase14-skbuff-toolchain-gap.py` keeps this gap note and
the live skbuff survey aligned on one narrow rule: no attached-toolchain or
compile-route claim is allowed while the skbuff anchor packet files remain
absent on current `master`.

## Next bounded fix

If this lane reopens, restore a bounded skbuff anchor packet first and only
then reintroduce attached-toolchain command inventory or compile evidence.
Until that packet exists again, keep this lane scoped to truthfulness only.
