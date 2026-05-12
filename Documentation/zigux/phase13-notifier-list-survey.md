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

- lane key: `P13-L18`
- surveyed state: `current master` readback refreshed on `2026-05-12`
- roadmap-adjacent reviewability evidence only
- shared Phase 13 packet keeps this notifier evidence outside the validator-first shared-helper release handle

## Current Repo Reality

As of `2026-05-12`, current `master` can still materialize these adjacent
notifier-facing surfaces:
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/abi.h`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

The same current-`master` readback still cannot materialize these direct notifier or
list companions, so contributor-facing summaries should record them as repo-reality
gaps instead of independently shipped evidence:
- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `zigux/helpers/notifier_chain_view.zig`
- `drivers/tty/hvc/hvc_console.h`

The direct `zigux/tests/phase13_build.zig` route is also not materialized on current
`master`, so keep the shipped validator-first handles above explicit instead of
presenting that missing build file as adjacent shipped evidence.

## Review Posture

Keep this packet framed as adjacent Phase 13 evidence:

- it supports the broader shared-helper release packet without becoming a fifth helper anchor
- it keeps the shipped notifier priority-signal checker explicit
- it keeps the shipped `zigux/bindings/notifier_abi.zig` and `include/zigux/abi.h` ABI footholds explicit as adjacent notifier evidence
- it keeps the broader validator-first and Linux-style replay handles explicit
- it treats still-missing direct notifier, helper, header, and tests-root companions as repo-reality gaps
- it does not add extra shared replay steps beyond the current validator-first shared-helper release handle
- it should not claim broader callback, registration, or HVC runtime parity while those direct companions remain absent on current `master`

## Contributor Checks

When the shared Phase 13 contributor packet changes, re-read these surfaces together:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
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
`zigux/bindings/notifier_abi.zig` plus `include/zigux/abi.h` ABI footholds,
the shared release-notes and roadmap-traceability packet, the paired Landlock
ownership and syscall-governance notes, and the stable `phase13-validate` or
`phase13` make routes visible while framing the still-missing direct notifier
packet, header, helper, and HVC header companions as repo-reality gaps rather
than shipped current-`master` evidence.

## Non-goals

- This note does not claim a new shared-helper replay count.
- This note does not claim broader HVC runtime parity.
- This note does not reopen frozen or study-only roadmap areas.
