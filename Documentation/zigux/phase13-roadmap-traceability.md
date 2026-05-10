# Phase 13 Roadmap Traceability

## Purpose

This note maps the active Phase 13 contributor-facing packet back to the Zigux roadmap so broad reminder surfaces can stay tied to the real product lane.

## Roadmap Fit

Phase 13 in the Zigux roadmap is the shared-subsystem-helper tranche.
The active contributor-facing packet stays inside that helper-first scope by keeping attention on:
- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

Adjacent notifier evidence supports the same Phase 13 packet, but it remains adjacent evidence rather than a fifth roadmap anchor.
That adjacent evidence packet should stay explicit through:
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/abi.h`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `zigux/helpers/notifier_chain_view.zig`
- `drivers/tty/hvc/hvc_console.h`

## Traceability Map

- `libfs` maps to the bounded shared-helper tranche and should stay represented as its own contributor-facing bucket.
- `devres` maps to the bounded shared-helper tranche and should stay split between helper parity and packet truthfulness work.
- `landlock/ruleset` maps to the bounded shared-helper tranche and should keep its ownership boundary explicit.
- `landlock/syscalls` maps to the bounded shared-helper tranche and should keep its governance boundary explicit.
- adjacent notifier evidence maps to Phase 13 release-surface truthfulness only and should stay separate from the four helper anchors while keeping the notifier survey, manifest, reviewability replay, ABI footholds, list-helper footholds, and `drivers/tty/hvc/hvc_console.h` explicit.

## Broad Surface Expectations

When a shared contributor-facing summary mentions Phase 13, it should keep these expectations visible:
- the packet is still active rather than closed
- the owner split is explicit
- notifier evidence is adjacent support, not a fifth helper slice
- the guidance stays inside helper, docs, checklist, and truthfulness work unless a new roadmap-approved surface lands

## Shared Notes To Keep Aligned

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

## Non-Goals

- This note does not reopen Phase 13 into a deeper subsystem-implementation plan.
- This note does not convert notifier evidence into a new helper lane.
- This note does not claim the packet has cleared all future validator or release-surface follow-through.
