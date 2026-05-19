# Phase 13 Landlock Syscalls Survey Gap

This note records one bounded Phase 13 review-noise gap in the Landlock syscall helper packet on current `master`.

## Current Drift

The shipped `security/landlock/syscalls.zig` helper already keeps the release-side `fop_ruleset_release()` planner and the combined `ruleset_fops` wrapper contract explicit.

The remaining review-noise drift is now narrower than the older survey-first story:

  * `Documentation/zigux/phase13-landlock-syscalls-governance.md` still described `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` as materialized on current `master`
  * `Documentation/zigux/phase13-landlock-syscalls-slice.md` still carried the same overstatement and treated the shared `zigux/tests/phase13_build.zig` companion as the only missing path
  * the broader Phase 13 roadmap, contributor, and lane-sequencing notes now record those direct syscall survey and replay companions as repo-reality gaps instead

## Why This Matters

The Phase 13 roadmap still keeps `security/landlock/syscalls.c` inside bounded security helper pilots. That makes truthful packet accounting more valuable than speculative helper growth. Stale helper-local notes create review noise by implying a wider direct syscall survey or replay packet than current `master` actually materializes.

## Bounded Fix

Keep the repair inside the helper-local notes only:

  * refresh `Documentation/zigux/phase13-landlock-syscalls-governance.md` so it matches the visible helper-local packet and the currently absent direct survey, replay, reviewability, manifest, and shared-build companions
  * refresh `Documentation/zigux/phase13-landlock-syscalls-slice.md` so it matches the same current packet boundary
  * keep the update tied to `security/landlock/syscalls.zig`, `planFopRulesetRelease()`, `ruleset_fops`, and the absent `phase13-landlock-syscalls-survey.md`, `phase13_landlock_syscalls.zig`, `phase13_landlock_syscalls_reviewability.zig`, `phase13_landlock_syscalls_manifest.json`, and `phase13_build.zig` paths
  * do not widen into anonymous-inode internals, live FD installation, credential mutation, or domain state

## Guardrail

The broader shared Phase 13 reminder packet already keeps these direct syscall survey and replay companions recorded as repo-reality gaps through `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, and `Documentation/zigux/phase13-contributor-workflow-guide.md`.

Leave any future survey-file reintroduction or validation-only survey-checker retargeting to its own dedicated follow-up lane rather than mixing it into the helper-local packet again.
