# Phase 13 Landlock Syscalls Governance

This note records the bounded governance and review-owner split for the shared Phase 13 Landlock syscalls packet so contributor-facing reminder surfaces describe the helper that current `master` actually ships.

## Scope

This note is for the syscall side of the active Phase 13 Landlock packet only.

Current `master` materializes a small `security/landlock/syscalls.zig` helper starter. The shipped surface stays intentionally narrow: pure reviewable planners for `landlock_restrict_self()`, one bounded `landlock_add_rule()` wrapper step, the release-side `fop_ruleset_release()` ownership drop, and the combined `ruleset_fops` wrapper contract. Keep syscall wording tied to current-`master` readback instead of assuming broader syscall parity or live enforcement.

Keep these neighboring surfaces distinct:
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md` for ruleset-helper ownership and review boundaries
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` for the broader Phase 13 owner split and lane routing
- `Documentation/zigux/phase13-contributor-workflow-guide.md` for the contributor-facing workflow packet
- adjacent notifier evidence under `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `zigux/bindings/notifier_abi.zig`, and `include/zigux/abi.h`; if direct notifier companions such as `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/helpers/notifier_chain_view.zig`, or `drivers/tty/hvc/hvc_console.h` are still absent on current `master`, keep them framed as repo-reality gaps rather than adjacent shipped evidence

## Owned Review Surface

When contributors touch the syscall-facing Landlock packet, keep this note aligned with:
- `security/landlock/syscalls.zig`
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

The intent is simple: keep the syscall-facing policy packet reviewable as one bounded Phase 13 helper surface without implying that ruleset-helper ownership, notifier evidence, or broader release-packet sequencing moved into this note.

## Governance Boundaries

Use this note to keep these boundaries explicit:
- syscall policy wording, review prompts, and reminder-surface ownership belong here
- ruleset-helper ownership stays with `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- helper-owned wording must stay descriptor-backed and must not drift into claims about live credential mutation, live ruleset ownership, or live syscall enforcement
- the shipped release-side helper packet is still bounded helper evidence: it keeps `fop_ruleset_release()`, `FMODE_CAN_READ`, `FMODE_CAN_WRITE`, and the shared `-EINVAL` read or write contract explicit without wiring real file operations or FD ownership
- adjacent notifier evidence stays explicit as release-surface support rather than becoming an extra shared replay step

Keep this packet parked unless a future lane can add another equally bounded planner.

## Review Prompts

If a change updates the Phase 13 Landlock syscalls packet, verify that:
- the broad Phase 13 reminder surfaces keep this governance note explicit beside the ruleset-ownership note and the adjacent notifier evidence packet
- no wording here implies extra shared replay steps beyond the shipped validator-first Phase 13 route
- syscall-facing policy claims stay separate from ruleset-helper ownership and from adjacent notifier evidence
- the packet remains active and reviewable rather than being described as closed or frozen
- helper-owned wording still matches `SyscallsHelperLab.descriptor()`, including the bounded release-side `ruleset_fops` planning surface and the false live-state flags
- helper-owned wording still frames the packet as planning-only helper work rather than live syscall enforcement
