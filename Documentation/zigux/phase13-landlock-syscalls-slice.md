# Phase 13 Landlock Syscalls Slice

This bounded Phase 13 slice keeps `security/landlock/syscalls.zig` aligned with `security/landlock/syscalls.c` as a pure helper-first packet.

The current helper stays intentionally narrow:
- keeps `landlock_create_ruleset()` reviewable around the ABI-version query branch, the sibling ERRATA query branch, minimum attr sizing, flag validation, handled-access filtering, empty-ruleset rejection, delegated ruleset planning, and the top-level initialization plus attr-presence wrapper checks while threading the ruleset-fd install planner only for the create-handle path
- keeps one planning-only `landlock_restrict_self()` helper explicit about the initialization gate, ruleset presence, `no_new_privs`, supported logging and `TSYNC` flags, and domain-preparation plus merge intent without presenting live credential replacement or task enforcement as shipped Zigux behavior
- keeps `landlock_add_rule()` reviewable around ruleset-fd presence, incoming-layer validation, delegated rule-tree search and insertion planning, and the top-level initialization plus attr-presence wrapper checks without presenting live ruleset mutation or syscall enforcement as shipped Zigux behavior
- keeps ruleset-fd lookup, ruleset-fd install, ruleset-fd stub, and `fop_ruleset_release()` planning explicit as descriptor-backed packet edges rather than as live file-descriptor or buffer-handling behavior

Current repo reality stays explicit: `security/landlock/syscalls.zig`, this slice note, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `scripts/zigux/check-phase13-landlock-syscalls-packet.py`, `zigux/tests/phase13_landlock_syscalls.zig`, and `zigux/tests/phase13_landlock_syscalls_reviewability.zig` are the active materialized helper-local, direct replay, and reviewability packet companions on current `master`.

Keep `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md` adjacent only as a historical breadcrumb for older lane notes and review references, not as active packet evidence.

The still-missing directly coupled surfaces stay narrow and honest: `zigux/tests/phase13_landlock_syscalls_manifest.json` and the older shared `zigux/tests/phase13_build.zig` companion remain repo-reality gaps.

This slice does not claim live anonymous-fd creation internals beyond the bounded install planner handoff, live fd ownership, live path imports, live credential replacement, thread synchronization side effects, domain merges as shipped behavior, or live syscall enforcement, and it keeps the landed create-ruleset, restrict-self, add-rule, ruleset-fd lookup, ruleset-fd install, ruleset-fd stub, and `fop_ruleset_release()` entrypoints strictly at planning depth.
