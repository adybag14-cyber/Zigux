# Artifact Diff Policy

Zigux keeps host-side artifact snapshots only when they anchor a bounded parity or reminder claim that reviewers can replay honestly.

## Rules

- prefer text, JSON, or stable digest output over opaque binary blobs whenever the same review goal is possible
- keep artifact scope small enough that one lane can regenerate, compare, and review it without widening into unrelated closure work
- update an artifact in the same bounded change that changed the source behavior or reminder contract it documents
- keep helper, contract-checker, and reminder-surface truthfulness explicit when broader validator-first packet members still lag behind current authenticated readback

## Current Direct-Readback Packet

- `scripts/zigux/artifact_diff.py` is directly readable on current `master`
- `python3 scripts/zigux/artifact_diff.py --self-test` is the shipped helper replay for that contract today
- `scripts/zigux/check-artifact-diff-contract.py` is directly readable on current `master`
- `python3 scripts/zigux/check-artifact-diff-contract.py --self-test` is the shipped contract-checker replay for that helper packet today
- `scripts/zigux/check-phase4-artifact-diff-determinism.py` is directly readable on current `master`
- the directly readable helper-and-checker packet currently keeps the bounded `text`, `json`, and `bytes` comparison modes, the legacy `sha256 -> bytes` alias, and the current helper or contract self-test catalogs explicit from the scripts root

## Current Reminder Surface

- keep this note aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
- current shared Phase 4 reminder surfaces still keep this docs-side note framed as a historical broader companion while the returned helper, contract checker, determinism checker, and direct local-only perf packet carry the directly readable current-head handoff
- `scripts/zigux/validate-phase4.py` still does not return through authenticated contents reads in this runtime, so treat that validator entrypoint as the remaining broader companion even when this note is restored for review
- keep the host-side artifact-diff contract explicit here without claiming that the broader validator, build, bitmap replay, or shared-CI perf packet is fully returned on current `master`

## Current Uses

- the helper and contract checker remain the shared comparison layer for bounded artifact-backed parity work under `scripts/zigux/`
- current Phase 2 reminder surfaces already rely on the host-side artifact-diff contract indirectly for bounded fixture-backed parity lanes instead of reopening older missing-route closure wording
- current Phase 4 reminder surfaces keep the helper, contract checker, determinism checker, repo-reality warning, and local-only perf packet explicit while exact authenticated blob refresh for the broader validator-side packet remains a separate follow-through

## Next Honest Follow-Through

- narrow shared reminder surfaces only when direct current-head rereads prove they still overstate or understate the returned helper-and-checker packet
- repair `scripts/zigux/check-artifact-diff-contract.py` before treating the broader contract summary as fully synchronized with the current helper packet if the contract checker still lags on current-head readback
- rematerialize `scripts/zigux/validate-phase4.py` before treating the broader artifact-diff packet as a fully returned validator-first surface
