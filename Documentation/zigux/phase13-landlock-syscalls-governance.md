# Phase 13 Landlock Syscalls Governance

This note records the bounded governance and review-owner split for the shared Phase 13 Landlock syscalls packet so contributor-facing reminder surfaces do not point at an absent file or blur syscall policy into the neighboring ruleset-helper packet.

## Scope

This note is for the syscall side of the active Phase 13 Landlock packet only.

Current `master` now materializes `security/landlock/syscalls.zig` as a helper-local starter for the roadmap-owned `security/landlock/syscalls.c` anchor. Keep the helper-owned wording tightly scoped to descriptor-backed create-ruleset planning, ABI-version query planning, the top-level create-ruleset initialization plus attr-presence wrapper checks, descriptor-backed add-rule planning, the top-level add-rule initialization plus attr-presence wrapper checks, one planning-only ruleset-fd install helper that fixes the `anon_inode_getfd()` label, `ruleset_fops` binding, `O_RDWR | O_CLOEXEC` flags, and release-on-fd-failure discipline, one planning-only ruleset-fd stub helper that keeps the dummy read or write mode discipline plus shared `-EINVAL` return reviewable as data, and one planning-only `fop_ruleset_release()` helper that keeps the `filp->private_data` handoff, `landlock_put_ruleset()` release, and zero return reviewable as data, and do not present that helper packet as live FD installation, file-buffer handling, credential replacement, or full Landlock enforcement.

## Current Repo Reality

Current `master` materializes the syscall helper starter plus the docs-root ownership packet through:
- `security/landlock/syscalls.zig`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `zigux/Makefile`

Current `master` still does not materialize the older direct replay companions or the dedicated Phase 13 shared replay route through:
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `zigux/tests/phase13_build.zig`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

Keep that live shape explicit as a bounded helper starter plus docs-root governance packet with a returned shared build file but no dedicated Phase 13 shared replay route, not as a fully materialized shared replay path.

Keep these neighboring surfaces distinct:
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md` for ruleset-helper ownership and review boundaries
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` for the broader Phase 13 owner split and lane routing
- `Documentation/zigux/phase13-contributor-workflow-guide.md` for the contributor-facing workflow packet
- adjacent notifier evidence under `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/helpers/notifier_chain_view.zig`, and `drivers/tty/hvc/hvc_console.h`; if direct companions such as `scripts/zigux/check-phase13-notifier-priority-signal.py`, `zigux/tests/phase13_notifier_list_manifest.json`, or `zigux/tests/phase13_notifier_list_reviewability.zig` cannot be materialized on current `master`, record them as repo-reality gaps instead of presenting them here as independently shipped evidence

## Owned Review Surface

When contributors touch the syscall-facing Landlock packet, keep this note aligned first with the shipped helper-local packet:
- `security/landlock/syscalls.zig`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`

Treat the older direct survey, replay, reviewability, and manifest route as repo-reality gaps until current `master` materializes them again:
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `zigux/tests/phase13_build.zig`

Keep contributor guidance anchored to the broader shipped reminder packet instead of presenting those absent direct companions as independently shipped evidence:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

This keeps the ownership split explicit: the helper, slice note, and this governance note are the current helper-local review surface, while the absent direct companions remain gaps rather than silently inherited owners.

The intent is simple: keep the syscall-facing policy packet reviewable as one bounded Phase 13 helper surface without implying that ruleset-helper ownership, notifier evidence, or broader release-packet sequencing moved into this note.

## Governance Boundaries

Use this note to keep these boundaries explicit:
- syscall policy wording, review prompts, and reminder-surface ownership belong here
- ruleset-helper ownership stays with `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- shared packet routing stays with the shipped docs-root reminder surfaces above while the direct syscall replay companions and shared make-route handles remain absent; keep those paths recorded as repo reality rather than as shipped evidence
- adjacent notifier evidence stays explicit as release-surface support rather than becoming an extra shared replay step
- if a future helper lands, keep it tied to descriptor-backed planning only instead of treating it as live syscall enforcement or as a claim that FD, file-buffer, credential, or domain ownership moved into Zigux

Keep this packet parked unless a future lane can add another equally bounded planner.

## Review Prompts

If a change updates the Phase 13 Landlock syscalls packet, verify that:
- the broad Phase 13 reminder surfaces keep this governance note explicit beside the ruleset-ownership note and the adjacent notifier evidence packet when they describe the active shared-helper tranche
- no wording here implies extra shared replay steps beyond the shipped helper, slice, and governance packet while the direct syscall companions remain absent
- syscall-facing policy claims stay separate from ruleset-helper ownership and from adjacent notifier evidence
- the packet remains active and reviewable rather than being described as closed or frozen
- any still-missing direct syscall companions stay framed as repo-reality gaps rather than as shipped current-`master` evidence
- helper-owned wording must match the current helper boundary: create-ruleset planning, ABI-version query planning, top-level create-ruleset initialization plus attr-presence wrapper checks, add-rule planning, top-level add-rule initialization plus attr-presence wrapper checks, ruleset-fd install planning, ruleset-fd stub planning, ruleset release planning, handled-access plus attr-size plus flag validation, incoming-layer plus tree-walk validation, delegated ruleset creation plus rule-tree search plus rule insertion planning, explicit `ruleset_fops` binding discipline, explicit `filp->private_data` release discipline, and no live FD installation, file-buffer handling, or credential replacement
