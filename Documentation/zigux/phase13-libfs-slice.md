# Phase 13 libfs Slice

This document tracks the bounded Phase 13 shared-filesystem-helper slice for Zigux around `fs/libfs.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=libfs-helper-filesystem-boundary-packet`
- roadmap posture: keep the Phase 13 shared-helper foothold reviewable without overstating live VFS mutation
- scope: positive-entry classification, simple-directory emptiness planning, negative-dentry lookup shaping, transaction acquire, publish, and release planning, addressability planning, offset seek, offset readdir, offset add and remove, offset rename and rename-exchange planning, cursor-open and cursor-precondition planning, and direct replay plus manifest review only

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

- the next helper-local cursor-reposition bookkeeping step around `hlist_del_init()` plus `hlist_add_before()` and `hlist_add_behind()`
- the older shared `zigux/tests/phase13_build.zig` route
- the still-missing focused `zigux/tests/phase13_libfs_addressability.zig` companion
- live dcache entry insertion, inode lifetime management, page-cache-backed filesystem state, or broader filesystem registration

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
