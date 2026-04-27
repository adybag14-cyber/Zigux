# Phase 13 Release Notes Survey

This document records the current release-discipline reading for the active Phase 13 shared-helper tranche without claiming that the roadmap phase is globally closed.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_TRANCHE=shared-helper-bundle`
- `PHASE13_RELEASE_SURVEY=present`
- scope: roadmap traceability, shared helper replay entrypoints, the three manifest-backed survey packets already present on `master`, the adjacent notifier-list reviewability packet, and the remaining `devres` survey asymmetry
- product boundary:
  - `Documentation/zigux/phase13-release-notes-survey.md`
  - `Documentation/zigux/phase13-roadmap-traceability.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `zigux/tests/phase13_build.zig`
  - `zigux/Makefile`
  - `Documentation/zigux/phase13-libfs-survey.md`
  - `Documentation/zigux/phase13-landlock-ruleset-survey.md`
  - `Documentation/zigux/phase13-landlock-syscalls-survey.md`
  - `Documentation/zigux/phase13-notifier-list-survey.md`
  - `zigux/tests/phase13_libfs_manifest.json`
  - `zigux/tests/phase13_landlock_ruleset_manifest.json`
  - `zigux/tests/phase13_landlock_syscalls_manifest.json`
  - `zigux/tests/phase13_notifier_list_manifest.json`

## Why this record exists

The Phase 13 roadmap names four shared-helper anchors:

- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

The live repo already carries real helper code, dedicated tests, and shared replay wiring for those anchors, plus one adjacent notifier-list reviewability packet that helps explain preexisting list or hlist helper footing without claiming a fifth roadmap anchor.

What was still missing was one compact release-discipline record that says, in one place, how to read that bundle today:

- Phase 13 is active, not closed
- the current tranche is reviewable through `zigux/tests/phase13_build.zig` and `make -C zigux phase13`
- `libfs`, `landlock/ruleset`, and `landlock/syscalls` already have manifest-backed survey packets
- `devres` is the one remaining roadmap anchor that still lacks the same manifest-backed survey shape

This survey closes that documentation gap without inventing new helper progress.

## Current release reading

The current Phase 13 release-facing reading is:

- `fs/libfs.c`: helper slice landed, dedicated tests present, roadmap traceability present, manifest-backed survey present
- `lib/devres.c`: helper slice landed, dedicated tests present, roadmap traceability present, manifest-backed survey still missing
- `security/landlock/ruleset.c`: helper slice landed, dedicated tests present, roadmap traceability present, manifest-backed survey present
- `security/landlock/syscalls.c`: helper slice landed, dedicated tests present, roadmap traceability present, manifest-backed survey present

- `PHASE13_ROADMAP_ANCHOR_COUNT=4`
- `PHASE13_MANIFEST_BACKED_SURVEY_COUNT=3`
- `PHASE13_ACTIVE_ASYMMETRIC_ANCHOR_COUNT=1`
- `PHASE13_SHARED_BUILD_PRESENT=yes`
- `PHASE13_SHARED_MAKE_TARGET_PRESENT=yes`
- `PHASE13_RELEASE_CLOSED=no`

The adjacent notifier-list reviewability packet remains useful release evidence, but it is not counted as a fifth roadmap anchor:

- `Documentation/zigux/phase13-notifier-list-survey.md`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/tests/phase13_notifier_list_manifest.json`

## Evidence set

The current bounded release-evidence set is:

- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-libfs-slice.md`
- `Documentation/zigux/phase13-libfs-survey.md`
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `zigux/tests/phase13_build.zig`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_libfs_reviewability.zig`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/tests/phase13_libfs_manifest.json`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `zigux/tests/phase13_notifier_list_manifest.json`

## Gates

1. run the shared Phase 13 helper replay
- `zig build test --build-file zigux/tests/phase13_build.zig`

2. run the Linux-style convenience entrypoint
- `make -C zigux phase13`

## Non-goals

This survey does not claim:

- global Phase 13 closure
- a manifest-backed survey packet for `lib/devres.c` that does not exist yet
- live MMIO mappings, live device-resource teardown parity, or generic devres group ownership
- live Landlock enforcement, live tree-state ownership transfer, or broader syscall-enforcement parity
- notifier ABI parity beyond the current preexisting list or hlist reviewability packet

## Next bounded step

If this Phase 13 release-discipline lane reopens, the next honest follow-up is still to give `lib/devres.c` the same manifest-backed survey shape already used by `libfs`, `security/landlock/ruleset.c`, and `security/landlock/syscalls.c`, without widening into new helper behavior.
