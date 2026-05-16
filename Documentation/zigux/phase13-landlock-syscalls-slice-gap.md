# Phase 13 Landlock Syscalls Slice Gap

This note records one bounded Phase 13 review-noise gap in the Landlock syscall helper packet on current `master`.

## Current Drift

The shipped `security/landlock/syscalls.zig` helper, the dedicated syscall replay, the reviewability gate, the manifest, the survey note, and the governance note all now describe the release-side `fop_ruleset_release()` planner and the combined `ruleset_fops` wrapper contract.

`Documentation/zigux/phase13-landlock-syscalls-slice.md` still reads like an older path-beneath-era slice note instead:

- it stops at the older `get_ruleset_from_fd()` and `get_path_from_fd()` helper wording
- it still names `add_rule_path_beneath()` as the next honest bounded step
- it does not name `fop_ruleset_release()`
- it does not name `ruleset_fops`
- it does not name `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- it does not keep the missing shared `zigux/tests/phase13_build.zig` route explicit

## Why This Matters

The Phase 13 roadmap still keeps `security/landlock/syscalls.c` inside bounded security helper pilots. That makes truthful helper-packet wording more valuable than speculative feature growth. A stale slice note creates review noise by implying the packet is still parked before the release-side and wrapper-discipline work that current `master` already ships.

## Bounded Fix

Keep the next repair inside the lane-owned slice note only:

- refresh `Documentation/zigux/phase13-landlock-syscalls-slice.md` so it matches the current helper packet
- keep the update tied to `fop_ruleset_release()`, `ruleset_fops`, the dedicated reviewability gate, and the still-missing shared `phase13_build.zig` route
- do not widen into anonymous-inode internals, live FD installation, credential mutation, or domain state

## Guardrail

`scripts/zigux/check-phase13-landlock-syscalls-slice-alignment.py` exists to fail closed when the slice note drops the current release-side or reviewability markers, or when the old path-beneath next-step wording comes back.
