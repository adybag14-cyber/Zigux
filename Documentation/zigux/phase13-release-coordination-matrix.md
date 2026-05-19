# Phase 13 Release Coordination Matrix

This matrix is the compact PMO coordination companion for the active Phase 13 shared-helper packet.

It is a release-planning artifact, not a closure claim and not a new replay route.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_RELEASE_CLOSED=no`
- shared-summary owner: `PMO / Release Management`
- workflow companion: `Documentation/zigux/phase13-contributor-workflow-guide.md`
- sequencing companion: `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`
- tests-root alignment companion: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`

shared-summary guard: `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`

tests-root alignment companion: `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`

Keep the Makefile-backed route family recorded as repo-reality gaps until current `master` rematerializes the shared build handle.

## Active Shared Packet

Keep shared release wording tied to the four roadmap-owned Linux anchors:

- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

The active shared packet stays contributor-facing and review-first. Helper-local proof remains owned by the `libfs`, `devres`, and `landlock` packets, while notifier evidence stays adjacent release-surface support through `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h`.

## Owner Split

- PMO / Release Management: keep this matrix, the workflow guide, the sequencing note, the shared-summary guard, and the tests-root alignment companion aligned
- helper-local owners: keep `libfs`, `devres`, and `landlock` packet wording grounded in their shipped surveys, slices, starter files, and focused reviewability manifests
- adjacent notifier support: keep `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check-phase13-notifier-packet.py`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` truthful as support evidence without promoting them into a fifth helper lane

## Release Handle

1. `Documentation/zigux/phase13-contributor-workflow-guide.md`
2. `Documentation/zigux/phase13-release-coordination-matrix.md`
3. `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
4. `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`
5. `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`

That is the shipped shared-summary handle for this packet, with the tests-root alignment companion kept explicit beside it.

## Repo-Reality Gaps

Keep the still-missing Phase 13 route family recorded as repo-reality gaps rather than shipped current-`master` release support. `zigux/Makefile` itself is present again on current `master`, but it still does not expose the Phase 13 shared build handle.

- `make -C zigux phase13-validate`
- `make -C zigux phase13`
- `scripts/zigux/validate-phase13-release.py`
- `scripts/zigux/check-phase13-devres-packet-alignment.py`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`

## Review Use

When shared Phase 13 wording changes:

1. reread this matrix beside the workflow guide and shared-helper sequencing note
2. rerun `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`
3. rerun `python3 scripts/zigux/check-phase13-tests-readme-alignment.py` when the tests-root reminder packet changes or when shared wording could drift into `zigux/tests/README.md`
4. keep the Makefile-backed route family recorded as repo-reality gaps while distinguishing the returned `zigux/Makefile` file from the still-missing Phase 13 routes
5. leave broader README or tests-root packet refresh for a separate same-lane step when a fresh reread proves a new reminder-surface drift

## Next Coordinated Step

The last docs-root `devres` wording repair is now landed, so keep the broader shared Phase 13 packet parked unless a fresh reread opens another reminder-surface drift.

- keep `Documentation/zigux/README.md`, `Documentation/zigux/phase13-release-notes-survey.md`, and `Documentation/zigux/phase13-roadmap-traceability.md` aligned around the narrower current-`master` `devres` packet now that the docs root no longer treats `Documentation/zigux/phase13-devres-survey.md` and `lib/devres.zig` as repo-reality gaps
- keep the shipped tests-root alignment companion plus the focused adjacent notifier packet explicit when broader contributor-facing reminder surfaces refresh
- keep the missing Phase 13 route family, the direct Landlock syscall companions, and the adjacent notifier follow-through parked as separate same-lane or helper-local work until a fresh reread proves one of those broader reminder surfaces drifted

## Boundaries

- This matrix does not close the Phase 13 tranche.
- This matrix does not imply a shipped Makefile-backed review handle.
- This matrix does not promote adjacent notifier evidence into a fifth helper anchor.
