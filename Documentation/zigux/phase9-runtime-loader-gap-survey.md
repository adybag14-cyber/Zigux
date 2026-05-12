# Phase 9 Runtime Loader Gap Survey

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-loader-gap-survey`
- `PHASE9_LANE_KEY=P9-L15`

## Current Repo Reality

Current `master` keeps the four sample-side loader scaffolds visible:

- `samples/zigux/runtime_atomic64_loader.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`
- `samples/zigux/runtime_trace_events_loader.zig`

Those four files still carry the bounded lifecycle, selftest, and rollback cues
that matter for this lane: initialized-stage and selftest-complete shared-request
snapshots stay reviewable, and the current rollback posture remains the explicit
`waiting_on_runtime_substrate` to `released_without_substrate` path through
`releaseSharedWithoutSubstrate`.

The shared runtime-loader files are not currently shipped on `master`.
`zigux/kernel/runtime_loader.zig` and `zigux/kernel/runtime_loader_contract.zig`
return missing-file results on current `master`.

That missing shared surface changes the honest gate posture for this lane.
`zigux/tests/phase9_build.zig` remains an adjacent stale shared-build scaffold
because it still points at those missing shared files, so it is not a replayable
shared-loader route today.

## Delivery Packet

This bounded Phase 9 packet is limited to:

- `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
- `zigux/tests/runtime_loader_gap_manifest.json`
- `zigux/tests/runtime_loader_gap_survey.zig`
- `zigux/tests/phase9_build.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`
- `samples/zigux/runtime_trace_events_loader.zig`
- `zigux/tests/runtime_trace_events_manifest.json`
- `zigux/tests/runtime_kretprobe_manifest.json`

## What Is Reviewable Now

The current evidence is deliberately pre-execution and fail-closed:

- each sample-side loader scaffold keeps initialized-stage and selftest-complete
  shared-request snapshots explicit before any live substrate claim
- each sample-side loader scaffold keeps the rollback-only
  `waiting_on_runtime_substrate` to `released_without_substrate` path explicit
- `samples/zigux/runtime_trace_events_loader.zig` still keeps registration
  snapshot drift, idle-registration, and drain handling review-only rather than
  executable registration parity
- `zigux/tests/runtime_trace_events_manifest.json` and
  `zigux/tests/runtime_kretprobe_manifest.json` still keep their family-local
  runtime substrate blockers explicit

## Boundaries

The shared Phase 9 loader-gap packet does not own the older command or
environment control surfaces.

- `tools/lib/subcmd/exec-cmd.zig` owns the Phase 8 command-name and path-shaping
  cues
- `tools/lib/subcmd/help.zig` owns the Phase 8 terminal-layout cues

Keep those controls outside this Phase 9 packet until the repo ships a real
shared runtime-loader surface that can consume them honestly.

## Gates

The current honest gate for this lane is direct and local:

1. `zig test zigux/tests/runtime_loader_gap_survey.zig`
2. treat `zigux/tests/phase9_build.zig` as a blocked boundary reference until
   the shared runtime-loader files land
3. `make -C zigux phase9-runtime-loader-shared-tests` stays blocked until the
   shared runtime-loader files land
4. `make -C zigux phase9` stays blocked until the shared runtime-loader files
   land

## Next Bounded Step

Either land readable shared runtime-loader surfaces and then restore the shared
build route, or keep the family-local loader scaffolds and blocker manifests
aligned without claiming runtime substrate parity early.
