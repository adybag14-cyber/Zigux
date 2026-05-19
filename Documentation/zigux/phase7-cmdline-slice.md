# Phase 7 Cmdline Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/cmdline.c`.

## Status

- `PHASE7_STATUS=helper_local_packet_landed`
- `PHASE7_SLICE=cmdline-runtime-leaf`
- `PHASE7_LANE_KEY=helper-local`
- lane-key note: `helper-local` keeps the dedicated cmdline packet separate from the broader Phase 7 shared-control lanes; shared docs-root, validator, Makefile, workflow, and build-route reminders stay with those separate shared-control follow-ons
- scope: keep the Phase 7 cmdline lane limited to the current helper-local packet and the no-standalone-cmdline-sample boundary
- lane state: current `master` directly carries `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, and this helper-local packet keeps `Documentation/zigux/phase7-cmdline-slice.md`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/phase7_cmdline_sample_boundary.zig`, `zigux/tests/phase7_cmdline_manifest.json`, and `samples/zigux/README.md` aligned around the bounded cmdline helper family without widening into the separate `argv_split`, `string_helpers`, or `rbtree` packets

## Why This Slice Exists

Phase 7 is where Zigux starts carrying reusable runtime helper families in product-facing locations.

The current `cmdline` state on `master` now carries a bounded helper-local packet around option matching, integer option decoding, next-argument parsing, and memory-size parsing, plus a dedicated helper-local replay in `zigux/tests/phase7_cmdline.zig`, while keeping the broader token-splitting, string-helper, and tree-helper follow-ons in their own Phase 7 families.

This is intentionally not a Phase 5 `samples/zigux/` delivery lane. Current `master` still ships no standalone `samples/zigux/*cmdline*` reference sample, so the dedicated boundary replay should keep that separation explicit while the Phase 7 cmdline helper stays reviewable through helper-local surfaces only.

## Gates

1. keep the helper-local implementation explicit
- `lib/cmdline.zig`

2. keep the dedicated helper-local replay and review packet explicit
- `zigux/tests/phase7_cmdline.zig`
- `Documentation/zigux/phase7-cmdline-slice.md`
- `zigux/tests/phase7_cmdline_survey.zig`
- `zigux/tests/phase7_cmdline_manifest.json`

3. keep the no-standalone-cmdline-sample boundary explicit
- `samples/zigux/README.md`
- `zigux/tests/phase7_cmdline_sample_boundary.zig`

4. keep adjacent Phase 7 families out of this packet unless a fresh reread says otherwise
- do not count `lib/argv_split.zig`
- do not count `lib/string_helpers.zig`
- do not count `Documentation/zigux/phase7-rbtree-slice.md`
- do not count `lib/rbtree.zig`
- do not count shared validator, Makefile, workflow, or build-route reminders here

## Current Parity Surface

The current helper-local packet on `master` covers:

- `parseOptionStr()` and `parse_option_str`
- `getOption()` and `get_option`
- `getOptions()` and `get_options`
- `nextArg()` and `next_arg`
- `memparse()`

The current helper-local replay keeps these proofs explicit:

- exact bare-option matching inside comma-separated option strings
- signed and unsigned integer option parsing with Linux-style range handling
- malformed-option clearing behavior for caller-owned integer outputs
- wrapped integer semantics for oversized values and validate-only replay paths
- decimal, hexadecimal, octal, and suffix-aware `memparse()` decoding
- signed-clamp and unchanged-rest behavior when no parse is possible
- `nextArg()` handling for bare tokens, key-value pairs, quoted values, quoted bare tokens, empty values, leading whitespace, leading equals signs, and first-NUL boundaries
- dedicated helper-local replay coverage rooted at `zigux/tests/phase7_cmdline.zig`

The current helper-local replay also keeps these ownership and boundary rules explicit:

- `parseOptionStr()` keeps matching bounded to exact bare entries and does not promote keyed values into bare-option hits
- `getOption()` and `getOptions()` mutate only caller-owned cursor and integer storage while preserving Linux-style return codes and first-invalid-token stop behavior
- `nextArg()` returns borrowed slices inside the caller-provided command-line buffer and keeps parsing inside the first exported C-string boundary
- `memparse()` keeps the unconsumed suffix explicit through the returned `rest` slice instead of widening into hidden normalization

## Non-goals

This helper-local Phase 7 cmdline slice does not yet claim:

- the separate `argv_split` ownership-and-tokenization packet
- the separate `string_helpers` escape, quoting, and string-array helper packet
- the separate `rbtree` helper-local packet under `lib/`
- any standalone `samples/zigux/*cmdline*` sample-root delivery
- shared validator, Makefile, workflow, or tests-root reminder ownership

## Next Bounded Step

Keep the dedicated cmdline helper replay, survey, manifest, and no-standalone-cmdline-sample boundary fail-closed on the current helper-local packet, and reopen only if those same-lane reminder surfaces drift or a fresh reread proves a matching dedicated fixture companion returned on current `master`.
Route adjacent `argv_split`, `string_helpers`, and `rbtree` follow-through to their own Phase 7 helper-local packets.
