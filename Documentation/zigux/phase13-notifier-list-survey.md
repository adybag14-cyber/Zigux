# Phase 13 Notifier List Survey
## Purpose
This note records the bounded Phase 13 notifier or list evidence that current `master` can still honestly treat as adjacent release-surface context for the shared subsystem-helper packet. The goal is contributor reviewability, not a new replay lane.
## Roadmap fit
Phase 13 in the Zigux roadmap is the shared-subsystem-helper tranche around bounded helper layers such as `fs/libfs.c`, `lib/devres.c`, and the Landlock helpers.
The notifier or list packet stays adjacent to that tranche because the current release guidance still uses it as boundary evidence for notifier-oriented truthfulness work without promoting it into a separate shared replay count.
## Survey Snapshot
- owner posture: adjacent notifier evidence rather than helper-lane ownership
- lane key: `P13-L18`
- surveyed commit: `23d15e44622d2cedd7691c88f78709db6bf1eb7e`
- surveyed state: `current master` readback refreshed on `2026-05-17`
- owner-map reminder: `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` keeps adjacent notifier evidence outside the four roadmap-owned helper anchors, so this note stays adjacent release-surface evidence instead of claiming a fifth helper lane
- roadmap-adjacent reviewability evidence only
- shared Phase 13 build intentionally omits this packet, so the adjacent notifier surfaces stay reviewable without adding a counted helper replay to the shared Phase 13 bundle
## Current Repo Reality
As of `2026-05-17`, current `master` can still materialize these adjacent notifier-facing surfaces:
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `include/zigux/abi.h`
- `drivers/tty/hvc/hvc_console.h`
The shipped adjacent `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` helpers stay read-only: they walk `list_head` and `hlist` links, report backlink or prev-link consistency witnesses, and stop short of claiming callback execution, registration, SRCU, or blocking-notifier semantics.
The shipped adjacent `include/zigux/abi.h` foothold now mirrors that same bounded posture through `struct zigux_notifier_block`, `struct zigux_list_head`, `struct zigux_hlist_head`, `zigux_notifier_chain_has_nonincreasing_priority()`, `zigux_notifier_first_chain_priority_increase()`, `zigux_list_has_consistent_backlinks()`, and `zigux_hlist_has_consistent_prev_links()` for C-side callers that only need read-only notifier ordering or list-link truthfulness.
Current direct readback in this lane still does not rematerialize `zigux/helpers/notifier_chain_view.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/validate-phase13-release.py`, or `include/zigux/notifier_abi.h`, so keep those paths framed as repo-reality gaps instead of shipped adjacent notifier evidence until a fresh reread proves they returned on current `master`.
The same current-`master` readback still keeps this packet adjacent rather than turning it into a broader list bridge: `zigux/tests/phase13_build.zig` is still intentionally absent, and the shared Phase 13 build intentionally omits this packet.
`zigux/Makefile` is present on current `master`, but its live body still does not expose `make -C zigux phase13-validate` or `make -C zigux phase13`, so keep the returned file distinct from those still-missing Phase 13 route names instead of treating it as a shared build handle for this adjacent packet.
## Review Posture
Keep this packet framed as adjacent Phase 13 evidence:
- it supports the broader shared-helper release packet without becoming a fifth helper anchor
- it keeps the shipped `zigux/bindings/notifier_abi.zig` plus `include/zigux/abi.h` ABI footholds explicit as adjacent notifier and list/hlist interop evidence
- it keeps the shipped `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` helper surfaces explicit as bounded `list_head` or `hlist` interop evidence
- it keeps the Linux-side `drivers/tty/hvc/hvc_console.h` notifier declarations explicit as adjacent evidence without claiming HVC runtime parity
- it keeps the missing notifier-chain helper, manifest, focused reviewability shard, focused packet checker, priority checker, shared release validator, notifier ABI header, and still-missing `make -C zigux phase13-validate` plus `make -C zigux phase13` route names framed as repo-reality gaps while keeping the returned `zigux/Makefile` file itself distinct from those gaps
- it does not add extra shared replay steps beyond the current contributor-facing reminder packet
- it should not claim broader callback, registration, SRCU, blocking-notifier, or HVC runtime parity on top of these read-only adjacent surfaces
## Contributor Checks
When the shared Phase 13 contributor packet changes, re-read these surfaces together:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
Those summaries should keep this notifier survey, the shipped `zigux/bindings/notifier_abi.zig` plus `include/zigux/abi.h` notifier/list/hlist ABI footholds, the shipped `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` list companions, and the Linux-side `drivers/tty/hvc/hvc_console.h` notifier declarations explicit as returned adjacent evidence without turning them into part of the stable shared replay handle. Keep the missing notifier-chain helper, notifier manifest, focused reviewability shard, focused packet checker, priority checker, shared release validator, notifier ABI header, and the still-missing `make -C zigux phase13-validate` plus `make -C zigux phase13` route names framed as repo-reality gaps while keeping the returned `zigux/Makefile` file distinct from those blocked routes.
## Non-goals
- This note does not claim a new shared-helper replay count.
- This note does not claim broader HVC runtime parity.
- This note does not reopen frozen or study-only roadmap areas.
