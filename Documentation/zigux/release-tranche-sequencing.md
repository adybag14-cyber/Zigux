# Zigux Release Tranche Sequencing

This note records the current PMO release-sequencing view for Zigux by comparing the roadmap and bootstrap ledger against the files that are visible on `master` during this run.

## Why This Exists

The roadmap and the bootstrap ledger define a broader tranche-closing train than the shared release-planning surface currently exposes on `master`.
This note keeps release coordination honest by separating:

- roadmap and ledger intent
- packet evidence that is actually visible on `master`
- missing or stale shared artifacts that should not be treated as release-closed

## Current Master Signals

Live readback during this run found these shared release-facing artifacts on `master`:

- `Documentation/zigux/phase10-closure-evidence.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`

The same readback did not find these planned or referenced files on current `master`:

- `Documentation/zigux/phase1-closure.md`
- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `zigux/tests/phase11_uapi_header_parity_manifest.json`

## Release Sequencing Posture

### Bucket 1: Shared packets that are visible on `master`

- Phase 10 has a shared closure note on `master`, but that note still keeps risky transport blocked and parked behind the Architecture Council reopen boundary.
- Phase 11 has a shared header-parity validation matrix on `master`, which is enough to keep the packet reviewable, but not enough to treat every referenced replay surface as landed.

### Bucket 2: Ledger milestones that should stay plan-only for release reporting

Until the files are visible on `master`, release coordination should treat these bootstrap-ledger milestones as not yet landed:

- Phase 1 closure note
- Phase 2 closure note
- Phase 3 ABI slice note

This means PMO rollups should not present the early tranche closures as complete only because the roadmap or ledger names them.

### Bucket 3: Shared-note truthfulness gaps that can mislead release reporting

Current shared notes appear to refer to supporting files that were not visible on `master` during this run.
Those gaps should be resolved before any release-facing inventory claims are widened:

- the Phase 10 closure note refers to a driver lane sequencing note that was not visible on current `master`
- the Phase 11 validation matrix refers to a shared replay contract and a parity manifest that were not visible on current `master`

## PMO Guidance For The Next Release Pass

- Use this note as the release truth source before restating tranche closure in any shared dashboard, closure note, or sequencing summary.
- Treat Phase 10 as an active parked tranche with blocker-owned risky transport follow-through, not as a release-closed driver bundle.
- Treat Phase 11 as a reviewable shared packet with inventory reconciliation still needed, not as a fully reconciled replay contract.
- Keep Phase 1 through Phase 3 closure language tied to files that are actually visible on `master`.

## Next Bounded PMO Step

Reconcile one shared note against the live `master` file inventory instead of widening scope.
The smallest same-lane follow-up is to update either:

- `Documentation/zigux/phase10-closure-evidence.md` so it no longer names missing sequencing artifacts, or
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` so its packet inventory matches the files that are actually visible on `master`
