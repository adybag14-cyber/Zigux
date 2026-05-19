# Phase 13 Gap Path Spellings

Use this note when a broad Phase 13 contributor-facing reminder needs to mention repo-reality gaps without drifting into stale path spellings.

This is a narrow developer-enablement note. It does not add a new replay route, close the Phase 13 tranche, or promote missing helper-local companions into shipped evidence.

## Purpose

Keep the shared contributor-facing packet truthful when it references missing direct replay companions or still-missing shared build routes.

Broad contributor-facing surfaces that may need this reminder:

- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

validator: `python3 scripts/zigux/check-phase13-gap-path-spellings.py`

## Canonical Gap Spellings

Keep these exact Phase 13 repo-reality-gap paths stable in broad reminder surfaces:

- `zigux/tests/phase13_devres.zig`
- `zigux/tests/phase13_devres_reviewability.zig`
- `zigux/tests/phase13_devres_boundary_evidence.zig`
- `zigux/tests/phase13_devres_manifest.json`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `zigux/helpers/notifier_chain_view.zig`
- `include/zigux/notifier_abi.h`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

Keep `zigux/Makefile` distinct from the still-missing Phase 13 route names above. The file is readable current-master evidence; those route names are not yet shipped shared build handles.

## Stale Spellings To Reject

Treat these as historical wording only, not as separate valid paths:

- `zigux/tests/phase13Devres_reviewability.zig`

If a contributor-facing note still uses one of those spellings, keep the note explicit that it is stale wording for the canonical underscore path rather than current shipped evidence.

## Review Use

Before landing a broad Phase 13 reminder change:

1. Keep helper-local packets separate from the shared contributor-facing handle.
2. Keep the canonical gap spellings above exact.
3. Keep stale spellings framed only as warnings, never as active evidence.
4. Keep `zigux/Makefile` explicit as a returned file without promoting the blocked `phase13` route names.

## Boundaries

- This note does not replace `Documentation/zigux/phase13-contributor-workflow-guide.md`.
- This note does not replace `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`.
- This note does not turn adjacent notifier evidence into a fifth helper family.