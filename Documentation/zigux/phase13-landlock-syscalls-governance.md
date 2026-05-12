# Phase 13 Landlock Syscalls Governance

This note records the bounded governance and review-owner split for the shared Phase 13 Landlock syscalls packet so contributor-facing reminder surfaces describe the helper packet that current `master` actually ships.

## Scope

This note is for the syscall side of the active Phase 13 Landlock packet only.

Current `master` materializes a small `security/landlock/syscalls.zig` helper starter. The shipped surface stays intentionally narrow: pure reviewable planners for `landlock_restrict_self()` with the `no_new_privs` versus `CAP_SYS_ADMIN` credential-gate split kept explicit, the current restrict-self logging-flag translation and the special `ruleset_fd = -1` plus `LANDLOCK_RESTRICT_SELF_LOG_SUBDOMAINS_OFF` detached logging-update path, bounded `landlock_add_rule()` planning for both the `path_beneath` and `net_port` branches with ruleset-write and path-or-port handoff checks, the release-side `fop_ruleset_release()` ownership drop, and the combined `ruleset_fops` wrapper contract. Keep syscall wording tied to current-`master` readback instead of assuming broader syscall parity or live enforcement.

Current `master` now also materializes the direct helper-local companions for that same bounded packet:
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`

The broader shared `zigux/tests/phase13_build.zig` surface still does not materialize on current `master`. Keep that absent build route framed as a repo-reality gap until it actually lands instead of treating the direct syscall replay packet as proof that the older shared build bundle is already back.

Keep these neighboring surfaces distinct:
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md` for ruleset-helper ownership and review boundaries
- `Documentation/zigux/phase13-landlock-syscalls-survey.md` for the direct helper-local roadmap survey tied to the current `security/landlock/syscalls.zig` starter
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` for the broader Phase 13 owner split and lane routing
- `Documentation/zigux/phase13-contributor-workflow-guide.md` for the contributor-facing workflow packet
- adjacent notifier evidence under `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `zigux/bindings/notifier_abi.zig`, and `include/zigux/abi.h`

## Owned Review Surface

When contributors touch the syscall-facing Landlock packet, keep this note aligned with:
- `security/landlock/syscalls.zig`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`

The direct lane-local replay surface on current `master` is now the helper plus the slice note, the survey note, this governance note, the manifest, the direct syscall replay, and the dedicated reviewability gate. Treat broader shared reminder surfaces as routing aids, not as replacement proof for this helper-local packet.

## Governance Boundaries

Use this note to keep these boundaries explicit:
- syscall policy wording, review prompts, and reminder-surface ownership belong here
- ruleset-helper ownership stays with `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- helper-owned wording must stay descriptor-backed and must not drift into claims about live credential mutation, live ruleset ownership, live file-descriptor installation, or live syscall enforcement
- the shipped helper packet keeps the credential-gate split explicit through `CredentialGate.no_new_privs` and `CredentialGate.cap_sys_admin_override` while staying planning-only rather than mutating live credentials
- the shipped helper packet also keeps restrict-self logging policy explicit through the current named logging flags, the boolean translation they imply for same-exec, new-exec, and subdomain logging, and the special detached `ruleset_fd = -1` plus `LANDLOCK_RESTRICT_SELF_LOG_SUBDOMAINS_OFF` path that updates logging posture without claiming a new domain install
- the shipped add-rule packet keeps the `path_beneath` versus `net_port` split explicit through `AddRuleAction`, ruleset-write access validation, access-mask handling checks, and the distinct parent-fd versus port handoff cues
- the shipped release-side helper packet is still bounded helper evidence: it keeps `fop_ruleset_release()`, `FMODE_CAN_READ`, `FMODE_CAN_WRITE`, and the shared invalid read or write contract explicit without wiring real file operations, live FD installation, or ownership transfer
- the paired survey note and dedicated reviewability gate own the current roadmap-gap readback for this same helper packet and should stay aligned with this note whenever the shipped helper surface changes

Keep this packet parked unless a future lane can add another equally bounded planner or validation-tightening step.

## Review Prompts

If a change updates the Phase 13 Landlock syscalls packet, verify that:
- no wording here implies extra shared replay steps beyond the shipped direct helper-local packet
- syscall-facing policy claims stay separate from ruleset-helper ownership and from adjacent notifier evidence
- helper-owned wording still matches `SyscallsHelperLab.descriptor()`, including the bounded release-side `ruleset_fops` planning surface and the false live-state flags
- helper-owned wording still keeps the `no_new_privs` versus `CAP_SYS_ADMIN` credential-gate split, the named restrict-self logging flags, and the detached subdomains-only logging-update case explicit
- helper-owned wording still keeps the `path_beneath` versus `net_port` add-rule split explicit
- helper-owned wording still frames the packet as planning-only helper work rather than live syscall enforcement
- the direct helper-local companions stay aligned with the helper itself while the older shared `phase13_build.zig` route remains framed as a repo-reality gap instead of being implied to exist
