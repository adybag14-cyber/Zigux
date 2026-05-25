# Phase 13 libfs Survey

This document records the bounded Phase 13 survey lane around `fs/libfs.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=libfs-helper-filesystem-boundary-survey`
- reviewed against live `master` `master-readback-2026-05-25`
- scope: the current docs-side libfs reminder packet only, keeping the helper-family boundary truthful while the direct helper, replay, and build paths remain absent on current `master`
- product boundary:
  - `Documentation/zigux/phase13-libfs-survey.md`
  - `Documentation/zigux/phase13-libfs-slice.md`
  - `zigux/tests/phase13_libfs_manifest.json`

## Why this slice exists

The Phase 13 roadmap explicitly names `fs/libfs.c` as a shared subsystem-helper anchor.

That still matters because `fs/libfs.c` contains small VFS-adjacent helpers that can easily be overstated as live filesystem behavior. The current honest repo boundary is narrower than the older reminder packet claimed: current `master` still carries the libfs survey note, slice note, and manifest fixture, but the direct helper, replay, reviewability, and Phase 13 build files those notes used to describe are not directly readable on current `master`.

## Survey findings

- `Documentation/zigux/phase13-libfs-survey.md`, `Documentation/zigux/phase13-libfs-slice.md`, and `zigux/tests/phase13_libfs_manifest.json` are directly readable on current `master`.
- the current public repository tree no longer exposes a top-level `fs/` directory on current `master`, so the previously described `fs/libfs.zig` helper path is not directly readable in the live tree.
- exact current-`master` GitHub readback also returns missing for `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_build.zig`.
- because those direct packet paths are absent, the older survey wording that treated the libfs helper, direct replay, dedicated reviewability gate, and shared Phase 13 build route as shipped current-head evidence had become stale.
- the remaining docs-side packet should therefore be read as a bounded reminder of the intended helper family and its non-goals, not as proof that the direct helper-first libfs implementation and its replay routes are currently shipped on `master`.

## Recorded gaps

The current lane state is:

- helper-local governance for this family remains tracked under `P13-Y01`, while the separate verification-only replay lane remains parked under `P13-L03`
- landed `phase13-libfs-survey-note`
- landed `phase13-libfs-slice-note`
- landed `phase13-libfs-manifest-fixture`
- blocked `phase13-libfs-direct-helper-path`
- blocked `phase13-libfs-direct-replay-path`
- blocked `phase13-libfs-reviewability-gate`
- blocked `phase13-build-gate`
- blocked `phase13-libfs-live-dcache-mutation`
- blocked `phase13-libfs-live-inode-state`

This keeps the lane explicit without overstating progress: current `master` still exposes the libfs reminder notes and manifest fixture, but it does not presently expose the direct helper, replay, reviewability, or shared Phase 13 build packet those reminder surfaces used to describe.

## Non-goals

This slice does not claim:

- live dcache entry insertion or removal side effects
- live inode lifetime or inode locking behavior
- page-cache-backed filesystem state
- live directory-map mutation, maple-tree mutation, or rename application
- broader superblock or filesystem registration behavior
- current-head proof that `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, or `zigux/tests/phase13_build.zig` are shipped on `master`
- shared release-surface ownership for unrelated Phase 13 helpers

## Next bounded step

If the libfs family reopens, prefer one same-packet truthfulness follow-through: either rematerialize the direct `fs/libfs.zig` helper packet and its coupled replay surfaces on current `master`, or keep the reminder packet parked on the docs-side evidence only without reintroducing stale shipped-path claims. Keep verification-only replay work on `P13-L03`.
