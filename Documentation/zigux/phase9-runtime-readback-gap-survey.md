# Phase 9 Runtime Readback Gap Survey

This note records the current same-lane blocker for the runtime-pilot survey packet on `master`.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_LANE_KEY=runtime-pilot`
- scope: current-tree readback trust for the bounded runtime atomic64, runtime bitmap, and shared Phase 9 reminder packet only

## Roadmap target

Phase 9 still targets first loadable Zigux runtime modules, selftest hooks, and runtime module lifecycle parity under `samples/zigux/runtime_*` and `zigux/tests/runtime_*`.

For this lane, the honest question is narrower: which current `master` paths are trustworthy enough to use as shared reminder evidence before another docs-root or scripts-root truthfulness repair lands?

## Current authenticated readback

The authenticated GitHub contents route directly returns these shared reminder and bounded build surfaces on current `master`:
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- `Documentation/zigux/README.md`
- `scripts/zigux/README.md`
- `samples/zigux/README.md`
- `zigux/tests/README.md`
- `scripts\zigux/check_phase9_review_checklist_phase_boundaries.zig`
- `scripts\zigux/check_phase9_trace_events_runtime_packet.zig`
- `zigux/tests/phase9_build.zig`
- `zigux/tests/runtime_atomic64_diff.zig`

That same authenticated route still returns `404 Not Found` for these Phase 9 sample and loader paths in this runtime:
- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_loader.zig`

## Current public-tree split

The live shared reminder packet still cites the separate runtime bitmap family as present current-tree evidence, and earlier public raw fallback rereads in this lane returned bodies for at least:
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_loader.zig`

So the current blocker is not simply "bitmap is missing" or "the broader runtime packet returned." The blocker is that the trusted direct contents route and the public fallback path still disagree about exactly which runtime sample and loader files are materialized on current `master`.

## What This Means

Two facts are stable enough to keep explicit right now:
- the direct shared reminder packet is still trace-events-first and more conservative than the broader Phase 9 family wording that some reminder surfaces now carry
- `zigux/tests/phase9_build.zig` is current authenticated evidence again, so same-lane reminder surfaces should stop treating that bounded build bundle as a missing path

What is still not safe to claim without another trusted reread:
- that the runtime atomic64 sample and loader pair are directly materialized on current `master`
- that the runtime bitmap sample and loader pair are directly materialized on current `master` through the same authenticated path as the reminder packet
- that the broader shared runtime-loader kernel packet has returned

## Next bounded step

1. Re-check `samples/zigux/runtime_atomic64.zig`, `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `zigux/tests/phase9_build.zig` from one trusted current-tree materialization path.
2. If that reread confirms `zigux/tests/phase9_build.zig` but still leaves the sample and loader files split, trim only the smallest stale shared reminder surface that still treats `zigux/tests/phase9_build.zig` as missing.
3. If the same reread returns the sample and loader files directly too, widen the next repair only far enough to align one shared reminder surface with that stronger current-tree evidence.

## Anti-overlap rule

Do not use this note to reopen runtime behavior, loader implementation, deeper runtime-substrate claims, or later-phase reminder work. This note exists only to keep the Phase 9 shared reminder packet truthful while authenticated and public current-tree readback still disagree.