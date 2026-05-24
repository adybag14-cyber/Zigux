# Phase 11 Codegen and Manifest Tooling Gap Survey

This note records the current deterministic tooling posture for the shared Phase 11 simple-driver packet and names the smallest roadmap-aligned manifest or generated-summary gap that still remains on current `master`.

## Status

- `PHASE11_TOOLING_GAP_STATUS=shared_packet_manifest_gap_open`
- lane: `P11-L01`
- scope: keep the shared Phase 11 codegen-and-manifest tooling story honest without widening into driver-local behavior, broader reminder-surface ownership, or retired aggregate routes

## Roadmap Anchor

Phase 11 still exists to move from lab-only slices toward bounded simple production drivers.
The roadmap still requires:

- direct-port or dual-implementation driver templates
- a hardware validation matrix
- teardown and failure-mode parity

For the shared tooling packet, that means current reminder surfaces, machine-readable manifests, and proof routes must stay deterministic without reviving retired wrappers or pretending a narrow inventory already describes the whole surviving Phase 11 packet.

## Current Shared Deterministic Tooling Packet

Current shared Phase 11 tooling evidence on `master` now centers on the returned validator-and-proof packet:

- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- `scripts/zigux/validate-phase11.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/Makefile`
- `make -C zigux phase11-validate`

That shared packet is stronger than the older replay-only story: `scripts/zigux/validate-phase11.py` now exists again, `make -C zigux phase11-validate` is the live shared route, and the shared gate fans out to focused bcm2835, gpio, DesignWare, and HVC proof builds.

## Live Gap Versus The Roadmap

The remaining same-lane tooling gap is narrower now.
Current `master` does ship a shared validator, a build-inventory checker, and a machine-readable inventory fixture, but that fixture still only describes the narrower HVC current-head continuity packet.
It does not serve as an aggregate manifest or generated summary for the full surviving shared Phase 11 packet that `scripts/zigux/validate-phase11.py` and `make -C zigux phase11-validate` actually exercise.

That leaves one real shared codegen-and-manifest gap:

- there is no current aggregate manifest or generated summary surface that tells contributors which shared checkers, shared routes, matrix notes, and proof-backed build shards are intentionally part of the live Phase 11 packet beyond the narrower HVC inventory

Without that smaller shared aggregate surface, reminder notes can still drift toward either extreme:

- understating the live packet by collapsing it to the HVC-only inventory
- overstating the live packet by treating adjacent driver-local or retired shared routes as if they were already part of one shipped aggregate manifest

## Boundaries For Follow-Through

Keep the next deterministic-tooling step narrow:

- do not revive removed `phase11`, `phase11-contract`, or `zigux/tests/phase11_build.zig` routes just to recover old naming
- do not collapse bcm2835, gpio, DesignWare, HVC, and header-boundary evidence into one fake green dashboard
- do not widen this tooling gap into driver behavior, platform-backed execution, or broader contributor-surface ownership already handled by nearby Phase 11 lanes
- do not treat the narrower `zigux/tests/fixtures/phase11_build_inventory.json` packet as if it already covers the whole shared validator route

## Recommended Next Bounded Step

The next high-value follow-through should be one small shared aggregate surface derived from the surviving packet only:

- enumerate the live shared checker and validator routes that current `master` still ships
- distinguish the narrower HVC continuity inventory from the broader shared `phase11-validate` proof fan-out
- record which driver-local matrices and proof-backed build shards the shared packet is still allowed to name
- validate that new surface with one fail-closed checker or self-test before wiring it into broader CI or reminder summaries

That would close the current shared manifest-or-generated-summary gap without reviving the retired validator story or crossing into neighboring driver-local lanes.
