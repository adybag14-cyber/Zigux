# Phase 13 Notifier List Survey

## Purpose

This note records the bounded Phase 13 notifier/list evidence that current `master`
already treats as adjacent release-surface context for the shared subsystem-helper
packet.

The goal is contributor reviewability, not a new replay lane.

## Roadmap fit

Phase 13 in the Zigux roadmap is the shared-subsystem-helper tranche around bounded
helper layers such as `fs/libfs.c`, `lib/devres.c`, and the Landlock helpers.

The notifier/list packet stays adjacent to that tranche because the current release
guidance already uses it as boundary evidence for the shipped notifier ABI and helper
surfaces without promoting it into a separate shared replay count.

## Survey Snapshot

- lane key: `P13-L18`
- surveyed commit: `23d15e44622d2cedd7691c88f78709db6bf1eb7e`
- roadmap-adjacent reviewability evidence only
- shared Phase 13 build intentionally omits this packet from the eight-test shared helper replay

`include/zigux/notifier_abi.h` is now shipped as adjacent notifier interop evidence.

`zigux/helpers/notifier_chain_view.zig` now provides the matching read-only notifier-chain summary helpers.

`scripts/zigux/check-phase13-notifier-packet.py` now fails closed on the adjacent notifier packet.

## Adjacent Evidence On Current Master

- `zigux/tests/phase13_notifier_list_manifest.json`
- `zigux/tests/phase13_notifier_list_reviewability.zig`
- `zigux/bindings/notifier_abi.zig`
- `include/zigux/abi.h`
- `include/zigux/notifier_abi.h`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `zigux/helpers/notifier_chain_view.zig`
- `drivers/tty/hvc/hvc_console.h`
- `scripts/zigux/check-phase13-notifier-packet.py`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/tests/phase13_build.zig`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

## Review Posture

Keep this packet framed as adjacent Phase 13 evidence:

- it shows the shipped notifier ABI and list-helper boundary surfaces
- it keeps the dedicated notifier manifest and reviewability replay explicit
- it keeps the adjacent helper, header, and focused checker surfaces explicit
- it supports the broader contributor-facing Phase 13 release packet
- it does not add extra shared replay steps beyond the current eight-test shared helper replay

## Contributor Checks

When the shared Phase 13 contributor packet changes, re-read these surfaces together:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Those summaries should keep this notifier survey, the notifier manifest, the
reviewability replay, the ABI footholds, the list-helper footholds, the adjacent
notifier helper and exported notifier header, the focused checker, and
`drivers/tty/hvc/hvc_console.h` explicit as one adjacent evidence packet.

## Non-goals

- This note does not claim a new shared-helper replay count.
- This note does not claim broader HVC runtime parity.
- This note does not reopen frozen or study-only roadmap areas.
