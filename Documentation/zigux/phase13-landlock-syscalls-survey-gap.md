# Phase 13 Landlock Syscalls Survey Gap

This note records one bounded Phase 13 review-noise gap in the Landlock syscall helper packet on current `master`.

## Current Drift

The shipped `security/landlock/syscalls.zig` helper, the direct syscall replay, the reviewability gate, the manifest, and the shared Phase 13 build route all now expose the release-side `fop_ruleset_release()` planner and the combined `ruleset_fops` wrapper contract.

`Documentation/zigux/phase13-landlock-syscalls-survey.md` still undercounts that visible repo packet in one narrow place:

  * it still says the shared `zigux/tests/phase13_build.zig` route remains absent
  * it still treats `phase13-build-gate` as blocked even though the shared build entry exists on current `master`
  * it does not keep the already-present shared build route aligned with the helper, reviewability gate, and manifest wording

## Why This Matters

The Phase 13 roadmap still keeps `security/landlock/syscalls.c` inside bounded security helper pilots. That makes truthful packet accounting more valuable than speculative helper growth. A stale survey note creates review noise by implying the shared build route is still missing after current `master` already wires the syscall packet through `zigux/tests/phase13_build.zig`.

## Bounded Fix

Keep the next repair inside the survey packet and its guard only:

  * refresh `Documentation/zigux/phase13-landlock-syscalls-survey.md` so it matches the visible shared build route
  * keep the update tied to `phase13_build.zig`, `phase13_landlock_syscalls_reviewability.zig`, `phase13_landlock_syscalls_manifest.json`, `planFopRulesetRelease()`, and `planRulesetFops()`
  * do not widen into anonymous-inode internals, live FD installation, credential mutation, or domain state

## Guardrail

`scripts/zigux/check-phase13-landlock-syscalls-survey-alignment.py` exists to fail closed when the survey note drops the current release-side or reviewability markers, or when the stale missing-build-route wording comes back.
