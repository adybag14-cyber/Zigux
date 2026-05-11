# Phase 13 Landlock Syscalls Governance

This note records the bounded governance and review-owner split for the shared Phase 13 Landlock syscalls packet so contributor-facing reminder surfaces do not point at an absent file or blur syscall policy into the neighboring ruleset-helper packet.

## Scope

This note is for the syscall side of the active Phase 13 Landlock packet only.

As of `2026-05-11`, current `master` does not materialize `security/landlock/syscalls.zig`. The shipped `security/landlock/` helper surface is still limited to `security/landlock/ruleset.zig`, so this syscall lane remains a governance-only release-surface note until a bounded helper-local planner actually lands. Keep syscall wording tied to current-`master` readback instead of assuming that the helper file, the direct companions, or live syscall enforcement have already shipped.

Keep these neighboring surfaces distinct:
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md` for ruleset-helper ownership and review boundaries
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` for the broader Phase 13 owner split and lane routing
- `Documentation/zigux/phase13-contributor-workflow-guide.md` for the contributor-facing workflow packet
- adjacent notifier evidence under `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/helpers/notifier_chain_view.zig`, and `drivers/tty/hvc/hvc_console.h`; if direct companions such as `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, or `zigux/tests/phase13_notifier_list_reviewability.zig` cannot be materialized on current `master`, record them as repo-reality gaps instead of presenting them here as independently shipped evidence

## Owned Review Surface

When contributors touch the syscall-facing Landlock packet, keep this note aligned with:
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

If direct companions such as `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, or `zigux/tests/phase13_landlock_syscalls_manifest.json` cannot be materialized on current `master`, record them as repo-reality gaps and keep reviewer guidance anchored to the shipped docs-root, tests-root, validator, and make-route surfaces above instead of presenting those direct paths as independently shipped evidence.

The intent is simple: keep the syscall-facing policy packet reviewable as one bounded Phase 13 helper surface without implying that ruleset-helper ownership, notifier evidence, or broader release-packet sequencing moved into this note.

## Governance Boundaries

Use this note to keep these boundaries explicit:
- syscall policy wording, review prompts, and reminder-surface ownership belong here
- ruleset-helper ownership stays with `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- shared packet routing stays with the shipped validator-first and make-route surfaces above; if the direct syscall companions are absent, keep those paths recorded as repo reality rather than as shipped evidence
- adjacent notifier evidence stays explicit as release-surface support rather than becoming an extra shared replay step
- the parked syscall lane stays bounded to governance wording and repo-reality gap tracking; it must not imply descriptor-backed planning for `landlock_restrict_self()`, live credential mutation, ruleset lifecycle ownership, or broader syscall parity until `security/landlock/syscalls.zig` actually ships

Keep this packet parked unless a future lane can add another equally bounded planner.

## Review Prompts

If a change updates the Phase 13 Landlock syscalls packet, verify that:
- the broad Phase 13 reminder surfaces keep this governance note explicit beside the ruleset-ownership note and the adjacent notifier evidence packet when they describe the active shared-helper tranche
- no wording here implies extra shared replay steps beyond the shipped validator-first Phase 13 route
- syscall-facing policy claims stay separate from ruleset-helper ownership and from adjacent notifier evidence
- the packet remains active and reviewable rather than being described as closed or frozen
- any still-missing direct syscall companions stay framed as repo-reality gaps rather than as shipped current-`master` evidence
- helper-owned wording keeps `security/landlock/syscalls.zig` framed as an absent current-`master` helper path until a bounded syscall planner actually lands
