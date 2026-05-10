# Phase 7 Shared Surface Readback Gap

This note records the current authenticated GitHub-app readback gap inside the parked Phase 7 leaf-library packet.

## Status

- `PHASE7_STATUS=parked`
- `PHASE7_SLICE=shared-phase7-readback-gap`
- `PHASE7_LANE_KEY=P7-Y03`
- scope: one bounded shared-surface truthfulness follow-through for the Phase 7 `string_helpers`, `cmdline`, `argv_split`, and `rbtree` helper family
- observed on: `2026-05-10`
- roadmap anchor: `lib/string_helpers.c`, `lib/cmdline.c`, `lib/argv_split.c`, and `lib/rbtree.c` remain the planned Phase 7 leaf-library anchors even though the current readback gap keeps the live shared packet from proving the whole four-family surface through the GitHub app alone

## Visible Shared Surfaces

Repeated authenticated GitHub-app reads on current `master` returned direct content for:

- `Documentation/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase7-string-helpers-slice.md`
- `samples/zigux/README.md`

Those shared summaries still describe a broader parked Phase 7 packet, so this note exists to pin what the live read path can currently prove before a later run rewrites broader summary prose or reconstructs any missing packet-local surfaces.

## Current Readback Gap

The same authenticated GitHub-app read path returned `404` for these currently named Phase 7 surfaces on `master`:

- `scripts/zigux/validate-phase7.py`
- `Documentation/zigux/phase7-cmdline-slice.md`
- `Documentation/zigux/phase7-argv-split-slice.md`
- `Documentation/zigux/phase7-rbtree-slice.md`
- `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`
- `lib/string_helpers.zig`
- `lib/cmdline.zig`
- `lib/argv_split.zig`
- `lib/rbtree.zig`
- `zigux/tests/phase7_string_helpers.zig`
- `zigux/tests/phase7_cmdline.zig`
- `zigux/tests/phase7_argv_split.zig`
- `zigux/tests/phase7_rbtree.zig`
- `zigux/tests/phase7_string_helpers_manifest.json`

This note does not claim that the whole Phase 7 packet is invalid or that the roadmap lane should switch away from leaf libraries. It records the narrower repo-reality problem: the live shared reminder surfaces currently overstate what the authenticated read path can directly verify on `master`.

## Why This Matters

- the roadmap still schedules a real four-anchor Phase 7 helper family, so future work here should stay in-lane
- the last same-lane docs repair restored checklist markers inside the surviving string-helper note, but the broader shared reminders still read as though the wider cmdline, `argv_split`, `rbtree`, helper, test, manifest, and validator packet is directly visible on current `master`
- recording the exact readback gap prevents future runs from treating repeated `404` results as noise and helps the next same-lane slot choose between a shared-summary truthfulness refresh and a bounded reconstruction step

## Next Bounded Step

Stay in the same kernel-leaf-libraries lane and update one shared reminder surface at a time, starting with `Documentation/zigux/README.md`, so it distinguishes:

- the directly visible `phase7-string-helpers` note plus shared reminder packet
- the broader planned `cmdline`, `argv_split`, and `rbtree` family that the current authenticated read path still cannot directly prove on `master`
