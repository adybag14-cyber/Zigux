# Artifact Diff Policy

Zigux keeps host-side artifact snapshots only when they anchor a bounded parity or reminder claim that reviewers can replay honestly.

## Rules

- prefer text, JSON, or stable digest output over opaque binary blobs whenever the same review goal is possible
- keep artifact scope small enough that one lane can regenerate, compare, and review it without widening into unrelated closure work
- update an artifact in the same bounded change that changed the source behavior or reminder contract it documents
- keep helper, contract-checker, determinism, validator, and reminder-surface truthfulness explicit when broader build and bitmap replay companions still rely on split readback

## Current Direct-Readback Packet

- `scripts/zigux/artifact_diff.py` is directly readable on current `master`
- `python3 scripts/zigux/artifact_diff.py --self-test` is the shipped helper replay for that contract today
- `scripts/zigux/check-artifact-diff-contract.py` is directly readable on current `master`
- `python3 scripts/zigux/check-artifact-diff-contract.py --self-test` is the shipped contract-checker replay for that helper packet today
- `scripts/zigux/check-phase4-artifact-diff-determinism.py` is directly readable on current `master`
- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test` is the shipped determinism replay for that helper packet today
- `scripts/zigux/check-phase4-artifact-diff-validator-replays.py` is directly readable on current `master`
- `scripts/zigux/validate-phase4.py` is directly readable on current `master`
- the directly readable helper-and-checker packet currently keeps the bounded `text`, `json`, and `bytes` comparison modes, the legacy `sha256 -> bytes` alias, the current helper self-test catalog, the current contract replay packet, the determinism self-test, and the validator replay surface explicit from the scripts root

## Current Reminder Surface

- keep this note aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/README.md`
- current shared Phase 4 reminder surfaces still keep this docs-side note framed as a broader companion while the returned helper, contract checker, determinism checker, validator-replay checker, validator entrypoint, and direct local-only perf packet carry the direct current-head handoff
- broader build and bitmap replay companions still rely on split readback: authenticated contents reads can still flap for `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig`, even though public raw fallback rereads return them on current `master`
- keep the host-side artifact-diff contract explicit here without claiming that the broader build, bitmap replay, or shared-CI perf-promotion packet is fully refreshed through exact authenticated blob capture

## Current Uses

- the helper and contract checker remain the shared comparison layer for bounded artifact-backed parity work under `scripts/zigux/`
- the determinism checker and validator-replay checker keep the helper summaries, contract catalogs, and validator packet fail-closed beside the direct helper replay
- current Phase 2 reminder surfaces already rely on the host-side artifact-diff contract indirectly for bounded fixture-backed parity lanes instead of reopening older missing-route closure wording
- current Phase 4 reminder surfaces keep the helper, contract checker, determinism checker, validator-replay checker, returned validator entrypoint, repo-reality warning, direct local-only perf packet, and roadmap-backed `atomic64_diff` pair explicit while broader build and bitmap replay companions still wait on steadier authenticated blob-pin refresh

## Next Honest Follow-Through

- narrow shared reminder surfaces only when direct current-head rereads prove they still overstate or understate the returned helper-and-checker packet
- refresh exact authenticated blob pins for `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` together once the split-readback path steadies
- repair `scripts/zigux/check-artifact-diff-contract.py` before treating the broader contract summary as fully synchronized with the current helper packet if the contract checker drifts on current-head reread
