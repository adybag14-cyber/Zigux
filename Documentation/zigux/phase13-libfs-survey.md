# Phase 13 libfs Survey

This document records the bounded Phase 13 survey lane around `fs/libfs.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=libfs-helper-filesystem-boundary-survey`
- reviewed against live `master` `master-readback-2026-05-12`
- scope: the shipped `fs/libfs.zig` helper lab, the direct `zigux/tests/phase13_libfs.zig` and `zigux/tests/phase13_libfs_reviewability.zig` replays, and the manifest-backed survey packet that keeps the filesystem-helper boundary truthful without widening into other shared-helper families
- product boundary:
  - `fs/libfs.zig`
  - `Documentation/zigux/phase13-libfs-survey.md`
  - `zigux/tests/phase13_libfs.zig`
  - `zigux/tests/phase13_libfs_reviewability.zig`
  - `zigux/tests/phase13_libfs_manifest.json`

## Why this slice exists

The Phase 13 roadmap explicitly names `fs/libfs.c` as a shared subsystem-helper anchor.

That matters because `fs/libfs.c` contains small VFS-adjacent helpers that can easily be overstated as live filesystem behavior when the honest near-term product boundary is still helper-first planning. Zigux already ships a real `fs/libfs.zig` foothold, so the highest-value bounded work in this lane is to record exactly which helper slices are present and which live filesystem behaviors remain blocked.

## Survey findings

- `fs/libfs.zig` still models positive-entry classification, simple-directory emptiness planning, negative-dentry lookup shaping, and simple transaction release planning as pure helper surfaces.
- the helper lab also ships bounded transaction acquire planning around `simple_transaction_get()`, keeping the page-bounded write limit, zeroed page allocation, one-write-per-open staging, and private-data handoff explicit without claiming live readback or pseudo-filesystem execution.
- the helper lab also ships bounded transaction publish planning around `simple_transaction_set()`, keeping the response-size limit, required private-data handoff, publish barrier, and published-size bookkeeping explicit without claiming live readback or file-lifecycle execution.
- the helper lab also ships bounded offset-directory seek and readdir planners that keep the real-entry window, emit-dots gate, and end-of-directory sentinel explicit without claiming live iteration side effects.
- the current helper packet already includes offset-based rename and rename-exchange planners that keep managed slots, missing offsets, reserved dot-window offsets, and end-of-directory sentinels explicit without mutating live directory maps.
- current `master` ships the direct `zigux/tests/phase13_libfs.zig` replay and the manifest-backed survey packet, so the helper starter plus its transaction acquire and transaction publish follow-ups are directly re-readable.
- current `master` still does not materialize the older shared `zigux/tests/phase13_build.zig` surface, so the libfs lane remains a direct helper-local replay packet rather than part of a wider shared Phase 13 build route.
- exact helper readback on current `master` shows no live dcache entry insertion, no inode lifetime management, no page-cache-backed state changes, and no broader filesystem runtime ownership; the current packet stays at helper-only planning.

## Recorded gaps

The current lane state is:

- landed `phase13-libfs-helper-starter`
- landed `phase13-libfs-offset-rename-planner`
- landed `phase13-libfs-transaction-acquire-helper`
- landed `phase13-libfs-transaction-publish-helper`
- landed `phase13-libfs-reviewability-gate`
- landed `phase13-libfs-survey-note`
- blocked `phase13-build-gate`
- blocked `phase13-libfs-live-dcache-mutation`
- blocked `phase13-libfs-live-inode-state`

This keeps the lane explicit without overstating progress: Zigux has a real helper-first libfs foothold for reviewable directory, lookup, transaction acquire, transaction release, transaction publish, and offset-based rename planning, but it does not yet claim the missing shared Phase 13 build surface or any live dcache and inode state transitions.

## Non-goals

This slice does not claim:

- live dcache entry insertion or removal side effects
- live inode lifetime or inode locking behavior
- page-cache-backed filesystem state
- live directory-map mutation or rename application
- broader superblock or filesystem registration behavior
- shared release-surface ownership for unrelated Phase 13 helpers

## Next bounded step

Leave `P13-L01` parked unless fresh current-master inspection finds new same-packet drift across `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, or `zigux/tests/phase13_libfs_manifest.json`; if the libfs family reopens for code later, require a new equally small helper-first step with explicit non-goals before claiming it.
