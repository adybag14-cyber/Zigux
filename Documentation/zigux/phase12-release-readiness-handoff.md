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

The current repo already carries the release-facing survey note, the compact coordination matrix, the ordered release-sequencing note, the dedicated PMO packet checker, the docs-root release summary, the scripts-root helper listing, and the review-checklist prompt for the active Phase 12 release packet.

Those live surfaces are:

- `Documentation/zigux/phase12-release-readiness-survey.md`
- `Documentation/zigux/phase12-release-coordination-matrix.md`
- `Documentation/zigux/phase12-release-sequencing.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/check-phase12-release-readiness-packet.py`
- `scripts/zigux/README.md`

## Remaining tests-root and shared-validator gaps

The tests root and the shared validator still leave part of the release-readiness packet easier to drift than the surrounding PMO notes.

The next release-facing follow-through must make `zigux/tests/README.md` explicitly name all of the following packet surfaces together instead of leaving the compact owner-split and fallback view split between docs-root and tests-root summaries:

- `Documentation/zigux/phase12-release-coordination-matrix.md`
- `Documentation/zigux/phase12-release-sequencing.md`
- `Documentation/zigux/phase12-release-readiness-handoff.md`
- `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
- `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- the existing `zigux/tests/phase12_raw_github_coverage_manifest.json` and `zigux/tests/phase12_raw_github_coverage_survey.zig` pair
- the existing `make -C zigux phase12-validate` release gate

After that tests-root release-packet follow-through lands, the next shared-validator promotion must still make `scripts/zigux/validate-phase12.py` require all of the following release-facing markers together instead of leaving them easier to drift than the surrounding driver and fallback packet:

- `scripts/zigux/check-phase12-release-readiness-packet.py`
- `Documentation/zigux/phase12-release-readiness-survey.md`
- the docs-root Phase 12 release note in `Documentation/zigux/README.md`
- the dedicated Phase 12 PMO checklist question in `Documentation/zigux/review-checklist.md`
- the existing `make -C zigux phase12-validate` release gate

## Release sequencing rule

Until those tests-root and shared-validator follow-through steps land, treat the current Phase 12 PMO packet as active release coordination evidence, not tranche closure.

Use this order when reopening the packet:

1. materialize the exact current `zigux/tests/README.md` and `scripts/zigux/validate-phase12.py` blobs in a writable local staging path
2. land the bounded tests-root PMO guidance update first so the compact release matrix and fallback packet become explicit from the tests root too
3. run the saved Phase 12 release-readiness bridge against the exact current `scripts/zigux/validate-phase12.py` blob only
4. rerun `python3 scripts/zigux/validate-phase12.py --self-test`
5. rerun `python3 scripts/zigux/validate-phase12.py`
6. rerun `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`
7. rerun `python3 scripts/zigux/check-phase12-release-readiness-packet.py`
8. rerun `make -C zigux phase12-validate`
9. confirm readback shows each tests-root and release-readiness insertion exactly once

## Closure guard

Do not call Phase 12 release-ready or release-closed while any of the following remain true:

- the tests root does not yet name the compact coordination matrix, sequencing note, handoff note, and paired commit-pinned fallback artifacts together
- the shared validator does not require the release-readiness survey and checker together
- the active-not-closed posture is only documented in PMO notes and not enforced by the shared validator
- the current two commit-pinned versus two shared-tree-only fallback split could drift without failing `scripts/zigux/validate-phase12.py`

## Next bounded step

The next honest PMO step is the tests-root Phase 12 release-packet follow-through in `zigux/tests/README.md`, explicitly naming the coordination matrix, sequencing note, handoff note, and paired fallback artifacts alongside the existing raw-coverage manifest pair and validate-before-replay route. After that lands, return to the shared-validator promotion for the current live `scripts/zigux/validate-phase12.py` blob `d9a1f229ff22545a3b10bc86eb4c97b2d53764d8` and confirm the release-facing markers each land exactly once on readback.
