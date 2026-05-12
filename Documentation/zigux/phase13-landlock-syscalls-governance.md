# Phase 13 Landlock Syscalls Governance

This note records the bounded governance and review-owner split for the shared Phase 13 Landlock syscalls packet so contributor-facing reminder surfaces describe the helper that current `master` actually ships.

## Scope

This note is for the syscall side of the active Phase 13 Landlock packet only.

Current `master` materializes a small `security/landlock/syscalls.zig` helper starter. The shipped surface stays intentionally narrow: pure reviewable planners for `landlock_restrict_self()` with the `no_new_privs` versus `CAP_SYS_ADMIN` credential-gate split kept explicit, the current restrict-self logging-flag translation and the special `ruleset_fd = -1` plus `LANDLOCK_RESTRICT_SELF_LOG_SUBDOMAINS_OFF` detached logging-update path, bounded `landlock_add_rule()` planning for both the `path_beneath` and `net_port` branches with ruleset-write and path-or-port handoff checks, the release-side `fop_ruleset_release()` ownership drop, and the combined `ruleset_fops` wrapper contract. Keep syscall wording tied to current-`master` readback instead of assuming broader syscall parity or live enforcement.

Current `master` now also ships a direct helper-local replay and paired manifest:
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`

Current `master` still does not materialize direct helper-local companions such as:
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`

Keep those absent paths framed as repo-reality gaps until they actually land instead of treating the direct replay, the paired manifest, this note, the paired survey note, or broader shared Phase 13 reminder surfaces as substitute proof that the full helper-local review packet already exists.

Keep these neighboring surfaces distinct:
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md` for ruleset-helper ownership and review boundaries
- `Documentation/zigux/phase13-landlock-syscalls-survey.md` for the direct helper-local roadmap survey tied to the current `security/landlock/syscalls.zig` starter
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` for the broader Phase 13 owner split and lane routing
- `Documentation/zigux/phase13-contributor-workflow-guide.md` for the contributor-facing workflow packet
- adjacent notifier evidence under `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `zigux/bindings/notifier_abi.zig`, and `include/zigux/abi.h`; if direct notifier companions such as `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/helpers/notifier_chain_view.zig`, or `drivers/tty/hvc/hvc_console.h` are still absent on current `master`, keep them framed as repo-reality gaps rather than adjacent shipped evidence

## Owned Review Surface

When contributors touch the syscall-facing Landlock packet, keep this note aligned with:
- `security/landlock/syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

The lane-local review surface on current `master` is now `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, this governance note, and the paired survey note. Treat broader shared reminder surfaces as cross-packet routing aids, not as replacement proof that a dedicated reviewability gate or slice note is already shipped.

The intent is simple: keep the syscall-facing policy packet reviewable as one bounded Phase 13 helper surface without implying that ruleset-helper ownership, notifier evidence, or broader release-packet sequencing moved into this note.

## Governance Boundaries

Use this note to keep these boundaries explicit:
- syscall policy wording, review prompts, and reminder-surface ownership belong here
- ruleset-helper ownership stays with `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- helper-owned wording must stay descriptor-backed and must not drift into claims about live credential mutation, live ruleset ownership, or live syscall enforcement
- the shipped helper packet keeps the credential-gate split explicit through `CredentialGate.no_new_privs` and `CredentialGate.cap_sys_admin_override` while staying planning-only rather than mutating live credentials
- the shipped helper packet also keeps restrict-self logging policy explicit through the current named logging flags, the boolean translation they imply for same-exec, new-exec, and subdomain logging, and the special detached `ruleset_fd = -1` plus `LANDLOCK_RESTRICT_SELF_LOG_SUBDOMAINS_OFF` path that updates logging posture without claiming a new domain install
- the shipped add-rule packet keeps the `path_beneath` versus `net_port` split explicit through `AddRuleAction`, ruleset-write access validation, access-mask handling checks, and the distinct parent-fd versus port handoff cues
- the shipped release-side helper packet is still bounded helper evidence: it keeps `fop_ruleset_release()`, `FMODE_CAN_READ`, `FMODE_CAN_WRITE`, and the shared `-EINVAL` read or write contract explicit without wiring real file operations or FD ownership
- the direct replay and paired manifest now keep the helper-local packet machine-checkable on current `master`, but the dedicated reviewability shard and slice note still remain explicit repo-reality gaps
- the paired survey note owns the current roadmap-gap readback for this same helper packet and should stay aligned with this note whenever the shipped helper surface changes
- adjacent notifier evidence stays explicit as release-surface support rather than becoming an extra shared replay step

Keep this packet parked unless a future lane can add another equally bounded planner.

## Review Prompts

If a change updates the Phase 13 Landlock syscalls packet, verify that:
- the broad Phase 13 reminder surfaces keep this governance note explicit beside the paired survey note, the ruleset-ownership note, and the adjacent notifier evidence packet
- no wording here implies extra shared replay steps beyond the shipped validator-first Phase 13 route
- syscall-facing policy claims stay separate from ruleset-helper ownership and from adjacent notifier evidence
- the packet remains active and reviewable rather than being described as closed or frozen
- helper-owned wording still matches `SyscallsHelperLab.descriptor()`, including the bounded release-side `ruleset_fops` planning surface and the false live-state flags
- helper-owned wording still keeps the `no_new_privs` versus `CAP_SYS_ADMIN` credential-gate split, the named restrict-self logging flags, and the detached subdomains-only logging-update case explicit
- helper-owned wording still keeps the `path_beneath` versus `net_port` add-rule split explicit
- helper-owned wording still frames the packet as planning-only helper work rather than live syscall enforcement
- direct helper-local companions that are still absent on current `master`, especially the slice note and dedicated reviewability shard, stay framed as repo-reality gaps instead of being implied to exist through the direct replay, paired manifest, this note, the paired survey note, or other shared reminder surfaces
