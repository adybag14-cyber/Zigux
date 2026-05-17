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
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/notifier_chain_view.zig`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `include/zigux/abi.h`
- `include/zigux/notifier_abi.h`
- `drivers/tty/hvc/hvc_console.h`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`
The shipped `zigux/helpers/notifier_chain_view.zig` helper stays read-only: it walks `NotifierBlock` links, checks nonincreasing priority ordering, and now reports the first priority increase witness without claiming callback execution, registration, SRCU, or blocking-notifier semantics.
The shipped adjacent `include/zigux/abi.h` foothold now mirrors that same read-only ordering probe through `struct zigux_notifier_block` and `zigux_notifier_chain_has_nonincreasing_priority()` for C-side callers that only need notifier priority-order truthfulness.
`include/zigux/notifier_abi.h` is now shipped as adjacent notifier interop evidence, `zigux/helpers/notifier_chain_view.zig` now provides the matching read-only notifier-chain summary helpers, and `scripts/zigux/check-phase13-notifier-packet.py` now fails closed on the adjacent notifier packet.
The same current-`master` readback still keeps this packet adjacent rather than turning it into a broader list bridge: `zigux/tests/phase13_build.zig` is still intentionally absent, and the shared Phase 13 build intentionally omits this packet.
## Review Posture
Keep this packet framed as adjacent Phase 13 evidence:
- it supports the broader shared-helper release packet without becoming a fifth helper anchor
- it keeps the shipped notifier priority-signal checker explicit
- it keeps the shipped `zigux/helpers/notifier_chain_view.zig` traversal, priority-order view, and first-priority-increase witness explicit while staying read-only
- it keeps the shipped `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, and `include/zigux/notifier_abi.h` ABI footholds explicit as adjacent notifier evidence
- it keeps the shipped `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` helper surfaces explicit as bounded `list_head` or `hlist` interop evidence
- it keeps the Linux-side `drivers/tty/hvc/hvc_console.h` notifier declarations explicit as adjacent evidence without claiming HVC runtime parity
- it keeps the manifest, focused reviewability gate, focused packet checker, and shared release validator explicit as adjacent evidence instead of reopening helper behavior
- it does not add extra shared replay steps beyond the current validator-first shared-helper release handle
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
Those summaries should keep this notifier survey, the shipped `check-phase13-notifier-priority-signal.py` helper, the shipped `check-phase13-notifier-packet.py` checker, the shipped `zigux/helpers/notifier_chain_view.zig` read-only traversal helper, the shipped priority-break witness, the shipped `zigux/bindings/notifier_abi.zig` plus `include/zigux/abi.h` and `include/zigux/notifier_abi.h` ABI footholds, the shipped `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` list companions, the Linux-side `drivers/tty/hvc/hvc_console.h` notifier declarations, the shared release-notes, release-coordination-matrix, and roadmap-traceability packet, the paired Landlock ownership and syscall-governance notes, and the stable `phase13-validate` or `phase13` make routes visible while still keeping the packet adjacent to the named helper anchors.
## Non-goals
- This note does not claim a new shared-helper replay count.
- This note does not claim broader HVC runtime parity.
- This note does not reopen frozen or study-only roadmap areas.
