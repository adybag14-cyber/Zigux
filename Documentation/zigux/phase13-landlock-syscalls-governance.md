# Phase 13 Landlock Syscalls Governance

This note closes one helper-local governance gap for `security/landlock/syscalls.zig`.

It exists to keep the current Phase 13 Landlock syscalls lane honest about ownership, fixtures, and policy claims while the helper remains a planning-only lab anchored to `security/landlock/syscalls.c`.

## Owned surface

The current lane owns only these review surfaces:

- `security/landlock/syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`

## Current helper contract

The helper is allowed to model only the bounded in-memory planning surface that it already exposes:

- ABI shape reporting for `RulesetAttr`, `PathBeneathAttr`, and `NetPortAttr`
- create-ruleset query and mask-validation planning
- restrict-self flag translation, including the `ruleset_fd == -1` mute-subdomains-only exception
- add-rule dispatch and bounded attribute validation
- ruleset-FD mode and single-layer planning
- path-FD filtering and owned path handoff planning
- path-beneath handoff planning, including the later `put_path()` release responsibility
- ruleset release planning that keeps the retained `private_data` handoff, matching `landlock_put_ruleset()` release, and zero return contract explicit

The helper does not currently own or imply:

- anonymous inode creation
- live FD-table mutation or long-lived file ownership
- live path import or rule insertion
- credential preparation, replacement, or rollback
- sibling thread synchronization beyond flag planning
- domain merge, hierarchy mutation, or live enforcement
- adjacent `security/landlock/ruleset.zig` ownership

## Fixture governance

Future fixtures, survey notes, and helper-local tests for this lane must follow these rules:

1. Treat `SyscallsHelperLab.descriptor()` as the ownership fence for live-state claims.
2. While `touches_live_fd_table`, `touches_live_paths`, `touches_live_credentials`, and `touches_live_domains` all remain `false`, no fixture or note may describe this helper as performing live syscall enforcement.
3. Every new helper claim should be anchored to one exported planner or report function already present in `security/landlock/syscalls.zig`.
4. If a future change adds a new planner, update the slice note and survey note in the same packet so the helper boundary stays reviewable.
5. If a future change starts modeling real file-operations, credential, or domain state, treat that as a new bounded follow-up and not as an implicit extension of this note.

## Ownership boundary with nearby lanes

This note keeps `P13-Y04` inside `security/landlock/syscalls.zig` only.

It does not transfer ownership of:

- `security/landlock/ruleset.zig`
- shared Phase 13 release-surface notes
- notifier, libfs, or devres Phase 13 packets
- any broader Landlock runtime plumbing outside the helper-local planning surface

## Next honest follow-up

After the `fop_ruleset_release()` planner, keep this packet parked unless a future lane can add another equally bounded planner without implying live file-operations wiring, FD ownership, credential work, or domain state.
