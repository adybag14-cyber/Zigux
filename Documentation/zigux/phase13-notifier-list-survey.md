# Phase 13 Notifier List Survey

## Purpose

This note records the bounded Phase 13 notifier or list evidence that current `master`
can still honestly treat as adjacent release-surface context for the shared
subsystem-helper packet.

The goal is contributor reviewability, not a new replay lane.

## Roadmap fit

Phase 13 in the Zigux roadmap is the shared-subsystem-helper tranche around bounded
helper layers such as `fs/libfs.c`, `lib/devres.c`, and the Landlock helpers.

The notifier or list packet stays adjacent to that tranche because the current
release guidance still uses it as boundary evidence for notifier-oriented
truthfulness work without promoting it into a separate shared replay count.

## Survey Snapshot

- owner posture: adjacent notifier evidence rather than helper-lane ownership
- owner-map reminder: `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` keeps `P13-L13` reserved for the `landlock/syscalls` survey-companion follow-through, so this note stays adjacent release-surface evidence instead of claiming that lane id
- surveyed state: `current master` readback refreshed on `2026-05-14`
- roadmap-adjacent reviewability evidence only
- shared Phase 13 packet keeps this notifier evidence outside the validator-first shared-helper release handle as a counted helper path while still keeping it inside the broader release-facing packet as adjacent evidence rather than a fifth helper anchor or an extra shared replay count

## Current Repo Reality

As of `2026-05-14`, current `master` can still materialize these adjacent
notifier-facing surfaces:
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/bindings/notifier_abi.zig`
- `zigux/helpers/notifier_chain_view.zig`
- `include/zigux/abi.h`
- `drivers/tty/hvc/hvc_console.h`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

The shipped `zigux/helpers/notifier_chain_view.zig` helper stays read-only: it
walks `NotifierBlock` links, checks nonincreasing priority ordering, and now
reports the first priority increase witness without claiming callback execution,
registration, SRCU, or blocking-notifier semantics.

The shipped adjacent `include/zigux/abi.h` foothold now mirrors that same
read-only ordering probe through `struct zigux_notifier_block` and
`zigux_notifier_chain_has_nonincreasing_priority()` for C-side callers that only
need notifier priority-order truthfulness.

The same current-`master` readback still cannot materialize these direct notifier or
list companions, so contributor-facing summaries should record them as repo-reality
gaps instead of independently shipped evidence:
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`

Those still-missing helper paths are the nearest `list_head` and `hlist` interop
gaps in this adjacent packet, so the survey should keep them explicit instead of
implying that current `master` already ships a broader list bridge.

The direct `zigux/tests/phase13_build.zig` route is also not materialized on current
`master`, so keep the shipped validator-first handles above explicit instead of
presenting that missing build file as adjacent shipped evidence.

## Review Posture

Keep this packet framed as adjacent Phase 13 evidence:

- it supports the broader shared-helper release packet without becoming a fifth helper anchor
- it keeps the shipped notifier priority-signal checker explicit
- it keeps the shipped `zigux/helpers/notifier_chain_view.zig` traversal and priority-order view explicit while staying read-only
- it keeps the shipped `zigux/helpers/notifier_chain_view.zig` priority-break witness explicit as a review aid rather than runtime callback behavior
- it keeps the shipped `zigux/bindings/notifier_abi.zig` and `include/zigux/abi.h` ABI footholds explicit as adjacent notifier evidence
- it keeps the Linux-side `drivers/tty/hvc/hvc_console.h` notifier declarations explicit as adjacent evidence without claiming HVC runtime parity
- it keeps the broader validator-first and Linux-style replay handles explicit
- it keeps the still-missing `list_head` and `hlist` helper surfaces explicit as repo-reality gaps
- it treats still-missing direct notifier, helper, header, and tests-root companions as repo-reality gaps
- it does not add extra shared replay steps beyond the current validator-first shared-helper release handle
- it should not claim broader callback, registration, or HVC runtime parity while those direct companions remain absent on current `master`

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

Those summaries should keep this notifier survey, the shipped
`check-phase13-notifier-priority-signal.py` helper, the shipped
`zigux/helpers/notifier_chain_view.zig` read-only traversal helper, the shipped
priority-break witness, the shipped `zigux/bindings/notifier_abi.zig` plus
`include/zigux/abi.h` ABI footholds, the Linux-side
`drivers/tty/hvc/hvc_console.h` notifier declarations, the shared
release-notes, release-coordination-matrix, and roadmap-traceability packet, the
paired Landlock ownership and syscall-governance notes, and the stable
`phase13-validate` or `phase13` make routes visible while framing the still-missing
direct notifier packet, dedicated header, tests-root, `list_head`, and `hlist`
helper companions as repo-reality gaps rather than shipped current-`master`
evidence.

## Non-goals

- This note does not claim a new shared-helper replay count.
- This note does not claim broader HVC runtime parity.
- This note does not reopen frozen or study-only roadmap areas.
