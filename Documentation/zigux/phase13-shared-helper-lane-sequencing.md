# Phase 13 Shared Helper Lane Sequencing

This note keeps the active Phase 13 shared-subsystems packet split into bounded owner lanes so contributor-facing guidance does not collapse `libfs`, `devres`, `landlock`, and adjacent notifier evidence into one noisy bucket.

## Scope

Use this note when a Phase 13 change touches any part of the shipped shared-helper release packet:

- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

Adjacent notifier evidence stays in scope for release-surface truthfulness, but it remains adjacent evidence rather than a fifth shared-helper anchor.

## Owner Split

Keep the current owner map explicit:

- `libfs` owns the `fs/libfs.zig` foothold and its focused reviewability packet
- `devres` owns the `lib/devres.zig` packet, including the boundary-evidence replay already visible on current `master`
- `landlock/ruleset` owns the ruleset ownership, slice, survey, and focused manifest-backed replay
- `landlock/syscalls` owns the syscall governance, slice, survey, and focused reviewability packet
- adjacent notifier evidence owns only release-surface truthfulness, not a fifth helper family

## Shared Packet Surfaces

Keep these shared reminder surfaces aligned when broad Phase 13 wording changes:

- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`

shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`

do not treat `zigux/Makefile`, `make -C zigux phase13-validate`, or `make -C zigux phase13` as shipped evidence

## Sequencing Rules

1. Prefer one helper lane at a time instead of batching `libfs`, `devres`, `landlock`, and notifier evidence into one mixed change.
2. Treat adjacent notifier evidence as release-surface support, not as an extra shared replay step.
3. Use the shared-summary guard before widening contributor wording across the packet.
4. Keep the Makefile-backed route family recorded as repo-reality gaps until current `master` rematerializes the shared build handle.
5. Leave broader docs-root, scripts-root, and tests-root refresh for a separate same-lane follow-up.

## Non-Goals

This note does not widen Phase 13 into:

- a direct filesystem parity claim beyond the shipped `libfs` packet
- a separate shared replay step for notifier evidence
- broader security policy ownership outside the landed Landlock notes
- a claim that the Phase 13 packet is closed or frozen
