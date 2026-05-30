# Phase 1 String strsep Gap Survey

This note records one bounded `tools/lib/string.zig` survey finding for the Phase 1 host-side helper tranche.

## Scope

- `PHASE1_STRING_STRSEP_SURVEY_STATUS=packet-gap-recorded`
- `PHASE1_STRING_STRSEP_ROADMAP_SCOPE=tools/lib/string.zig host-side helper`
- `PHASE1_STRING_STRSEP_LEDGER_SCOPE=Phase 1 helper train`
- `PHASE1_STRING_STRSEP_SOURCE_HELPER=pub fn strsep(cursor: *?[]u8, delimiters: []const u8) ?[]u8 {`
- `PHASE1_STRING_STRSEP_TEST_ANCHORS=test "strsep splits mutable C strings and preserves empty tokens";test "strsep respects C-string delimiter and source boundaries";test "strsep with an empty delimiter set returns the remaining C string once"`
- `PHASE1_STRING_STRSEP_REVIEW_PACKET_GAP=scripts/zigux/check-phase1-string-review-packet.py does not yet list the strsep symbol or its three direct helper tests in EXPECTED_STRING_SOURCE_SYMBOLS or EXPECTED_HELPER_TEST_ANCHORS`
- `PHASE1_STRING_STRSEP_NEXT_STEP=when the string review packet reopens, add strsep to the existing packet checker and manifest review anchors, then retire or narrow this gap survey`

## Repo Reality

Current `master` already carries a direct `strsep` implementation and direct Zig tests in `tools/lib/string.zig`. The Phase 1 roadmap still scopes this area to host-side helper ports, and the bootstrap ledger places `tools/lib/string.zig` inside the original Phase 1 helper train.

The remaining issue is review-packet truthfulness, not helper behavior: the large string packet checker still anchors many string helpers but does not yet make `strsep` review-visible. This survey keeps that gap explicit without reopening unrelated string helpers, shared fixture keys, closure routing, or the `memparse` repair tracked by the neighboring lane.

## Boundary

Do not use this survey to widen Phase 1 or touch Phase 7 string-helper sample work. The next safe implementation step is only the packet alignment named above.
