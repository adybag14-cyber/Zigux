# Phase 13 libfs Slice

This document tracks the bounded Phase 13 shared-filesystem-helper slice for Zigux around `fs/libfs.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=libfs-helper-filesystem-boundary-packet`
- roadmap posture: keep the Phase 13 shared-helper foothold reviewable without overstating live VFS mutation
- scope: positive-entry classification, simple-directory emptiness planning, negative-dentry lookup shaping, transaction acquire, publish, and release planning, addressability planning, offset seek, offset readdir, offset add and remove, offset rename and rename-exchange planning, cursor-open and cursor-precondition planning, packet-local cursor-reposition boundary tracing, and direct replay plus manifest review only

## Product Boundary

- `fs/libfs.zig`
- `Documentation/zigux/phase13-libfs-slice.md`
- `Documentation/zigux/phase13-libfs-survey.md`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_libfs_manifest.json`

## Why This Slice Exists

The Phase 13 roadmap explicitly names `fs/libfs.c` as a shared subsystem-helper anchor.

Current `master` already ships a real helper-first `libfs` packet, but until now that packet only had a survey note. This slice note makes the helper-local boundary directly reviewable so contributors do not need to reconstruct it from the survey, manifest, and tests alone.

This slice therefore keeps the packet focused on helper planning and direct replay while the older shared `zigux/tests/phase13_build.zig` route and the still-missing `zigux/tests/phase13_libfs_addressability.zig` companion remain outside the shipped surface.

## Current Parity Surface

The current packet covers:

- `LibfsHelperLab.descriptor()` with explicit no-live-dcache and no-live-inode flags
- `isPositiveEntry()`, `planSimpleEmpty()`, and `planSimpleLookup()` for helper-only positive-child classification, simple-directory emptiness planning, and negative-dentry lookup shaping
- `simpleTransactionGetPlan()`, `simpleTransactionSetPlan()`, and `simpleTransactionReleasePlan()` for bounded transaction acquire, publish, and release planning
- `genericCheckAddressablePlan()` for blocksize-window, sector-limit, and page-index planning without claiming page-cache ownership
- `planOffsetDirectorySeek()` and `planOffsetReaddir()` for helper-only offset seek, emit-dots gating, and end-of-directory reviewability
- `dcacheDirOpenPlan()` and `dcacheReaddirCursorPreconditionsPlan()` for bounded cursor allocation and resume-precondition planning without claiming sibling-list mutation
- `planSimpleOffsetAdd()`, `planSimpleOffsetRemove()`, `planSimpleOffsetRename()`, and `planSimpleOffsetRenameExchange()` for managed-slot bookkeeping and rename planning without mutating live directory maps
- the direct `zigux/tests/phase13_libfs.zig` replay, the dedicated `zigux/tests/phase13_libfs_reviewability.zig` companion, and the manifest-backed `zigux/tests/phase13_libfs_manifest.json` packet

The current packet does not cover:

- the still-unlanded cursor-reposition planner documented below
- the older shared `zigux/tests/phase13_build.zig` route
- the still-missing focused `zigux/tests/phase13_libfs_addressability.zig` companion
- live dcache entry insertion, inode lifetime management, page-cache-backed filesystem state, or broader filesystem registration

## Parked Cursor-Reposition Step

When this lane reopens for code, the next helper-local step should be grounded in the exact post-scan cursor bookkeeping paths already visible in Linux `fs/libfs.c`:

- `dcache_dir_lseek()` removes the private cursor from its current sibling slot with `hlist_del_init()` and, when a positive target dentry was found, reattaches it with `hlist_add_behind()` before dropping the temporary target reference
- `dcache_readdir()` removes the private cursor from its current sibling slot with `hlist_del_init()` and, when a next positive dentry remains after the emit loop, reattaches it with `hlist_add_before()` before dropping the temporary dentry reference
- both paths leave the cursor unhashed when no positive target survives the scan, so the honest helper-only contract is detach-or-reinsert bookkeeping rather than a claim of live sibling-list mutation

A future Zigux helper can therefore claim only these bounded reviewable facts:

- the cursor is explicitly detached before any reinsert decision
- seek-style resume parks the cursor behind the found positive dentry
- readdir-style resume parks the cursor before the next positive dentry
- end-of-directory and missing-target cases leave the cursor detached
- any temporary positive dentry reference is dropped after the bookkeeping step

That future helper must still not claim:

- live sibling-list ownership or mutation semantics beyond the detach-or-reinsert plan
- cursor dentry lifetime ownership
- lock-order guarantees beyond the already-noted parent dentry lock requirement
- inode lifetime, page-cache-backed filesystem state, or broader directory runtime behavior

## Gates

1. keep the helper-local libfs packet reviewable through:
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_libfs_manifest.json`

2. keep the shared contributor-facing release handle explicit through:
- `Documentation/zigux/phase13-libfs-survey.md`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

## Non-Goals

This slice does not claim:

- live dcache entry insertion or negative-dentry side effects
- live inode lifetime, inode locking, or page-cache-backed filesystem state
- live directory-map mutation, maple-tree mutation, or rename application
- broader superblock or filesystem registration behavior
- a restored shared `zigux/tests/phase13_build.zig` route

## Next Bounded Step

If this lane reopens, compare `fs/libfs.zig`, `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json` together before claiming the post-scan cursor-reposition bookkeeping step or any broader shared-build follow-through.
