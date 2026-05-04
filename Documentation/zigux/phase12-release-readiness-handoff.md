# Phase 12 Release Readiness Handoff

This note keeps the active Phase 12 PMO follow-up explicit without claiming that the shared release packet is closed.

## Current posture

- `PHASE12_RELEASE_HANDOFF_STATUS=active_not_closed`
- `PHASE12_SHARED_VALIDATE_ENTRYPOINT=make -C zigux phase12-validate`
- `PHASE12_SHARED_REPLAY_ENTRYPOINT=make -C zigux phase12`
- `PHASE12_RELEASE_READINESS_SURVEY=Documentation/zigux/phase12-release-readiness-survey.md`
- `PHASE12_SHARED_VALIDATOR=scripts/zigux/validate-phase12.py`
- `PHASE12_SHARED_VALIDATOR_BLOB_SHA=d9a1f229ff22545a3b10bc86eb4c97b2d53764d8`

## What is already live on master

The current repo already carries the release-facing survey note, the dedicated PMO packet checker, the docs-root release summary, the scripts-root helper listing, and the review-checklist prompt for the active Phase 12 release packet.

Those live surfaces are:

- `Documentation/zigux/phase12-release-readiness-survey.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/check-phase12-release-readiness-packet.py`
- `scripts/zigux/README.md`

## Remaining shared-validator gap

The shared validator still does not fail closed on the full release-readiness packet.

The next validator promotion must make `scripts/zigux/validate-phase12.py` require all of the following release-facing markers together instead of leaving them easier to drift than the surrounding driver and fallback packet:

- `scripts/zigux/check-phase12-release-readiness-packet.py`
- `Documentation/zigux/phase12-release-readiness-survey.md`
- the docs-root Phase 12 release note in `Documentation/zigux/README.md`
- the dedicated Phase 12 PMO checklist question in `Documentation/zigux/review-checklist.md`
- the existing `make -C zigux phase12-validate` release gate

## Release sequencing rule

Until that shared-validator promotion lands, treat the current Phase 12 PMO packet as active release coordination evidence, not tranche closure.

Use this order when reopening the packet:

1. materialize the exact current `scripts/zigux/validate-phase12.py` blob in a writable local staging path
2. run the saved Phase 12 release-readiness bridge against that exact blob only
3. rerun `python3 scripts/zigux/validate-phase12.py --self-test`
4. rerun `python3 scripts/zigux/validate-phase12.py`
5. rerun `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`
6. rerun `python3 scripts/zigux/check-phase12-release-readiness-packet.py`
7. rerun `make -C zigux phase12-validate`
8. confirm readback shows each release-readiness insertion exactly once

## Closure guard

Do not call Phase 12 release-ready or release-closed while any of the following remain true:

- the shared validator does not require the release-readiness survey and checker together
- the active-not-closed posture is only documented in PMO notes and not enforced by the shared validator
- the current two commit-pinned versus two shared-tree-only fallback split could drift without failing `scripts/zigux/validate-phase12.py`

## Next bounded step

The next honest PMO step is still the shared-validator promotion for `scripts/zigux/validate-phase12.py`, using the current live blob `d9a1f229ff22545a3b10bc86eb4c97b2d53764d8` and the saved release-readiness bridge bundle, then confirming the release-facing markers each land exactly once on readback.
