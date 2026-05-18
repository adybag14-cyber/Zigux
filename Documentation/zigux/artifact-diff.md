# Artifact Diff Policy

Zigux uses committed artifacts only when they anchor a bounded parity or reminder claim.

## Rules

- prefer text, JSON, or stable hashes over opaque binary blobs whenever the same review goal is possible
- keep artifact scope small enough that one lane can regenerate, compare, and review it honestly
- update an artifact in the same bounded change that changed the source behavior it documents
- keep helper contracts explicit in docs when the executable checker packet is still only partially rematerialized on current `master`

## Current Direct-Readback Helper

- `scripts/zigux/artifact_diff.py` is directly readable on current `master`
- `python3 scripts/zigux/artifact_diff.py --self-test` is the shipped direct replay for the helper contract today
- the helper exposes bounded `text`, `json`, and `sha256` comparison modes plus the outward markers `ARTIFACT_DIFF=...`, `MODE=...`, `EXPECTED=...`, `ACTUAL=...`, `EXPECTED_EXISTS=...`, `ACTUAL_EXISTS=...`, `EXPECTED_JSON_ERROR=...`, `ACTUAL_JSON_ERROR=...`, `SHA256=...`, `EXPECTED_SHA256=...`, and `ACTUAL_SHA256=...`

## Current Reminder Surface

- keep this note aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
- that current direct-readback packet keeps the helper itself explicit while the broader validator-first and contract-checker packet is still only partially present on current `master`
- authenticated contents reads on current `master` still return missing for `scripts/zigux/check-artifact-diff-contract.py` and `scripts/zigux/validate-phase4.py`, so treat those as historical or adjacent packet members until a same-family lane rematerializes them directly
- `scripts/zigux/check-phase4-artifact-diff-determinism.py` is directly readable again on current `master`, so follow-up work here should stay bounded to note and reminder truthfulness unless the missing checker or validator packet returns too

## Current Uses

- the helper remains the shared comparison layer for bounded artifact-backed parity work under `scripts/zigux/`
- current Phase 2 reminder surfaces already rely on the helper contract indirectly for bounded fixture-backed parity lanes instead of reopening the older broader closure stack from missing paths
- current Phase 4 reminder surfaces keep the host-side helper explicit as a reviewable contract anchor while the broader rollback-readiness packet continues to distinguish direct current-head proof from historical packet members

## Next Honest Follow-Through

- narrow shared reminder surfaces only when direct current-head rereads prove they still overstate the broader artifact-diff packet
- rematerialize `scripts/zigux/check-artifact-diff-contract.py` before treating the docs-side artifact-diff packet as a fully returned validator-first surface
