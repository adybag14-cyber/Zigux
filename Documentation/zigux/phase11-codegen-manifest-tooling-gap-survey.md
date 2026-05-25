# Phase 11 Codegen and Manifest Tooling Gap Survey

This note records the current deterministic tooling posture for the shared Phase 11 simple-driver packet and names the smallest roadmap-aligned manifest or generated-summary gap that still remains on current `master`.

## Status

- `PHASE11_TOOLING_GAP_STATUS=shared_packet_aggregate_surface_materialized`
- lane: `P11-L06`
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
- `Documentation/zigux/phase11-codegen-manifest-tooling-gap-survey.md`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`
- `scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`
- `scripts/zigux/check-phase11-shared-tooling-manifest.py`
- `scripts/zigux/validate-phase11.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/fixtures/phase11_shared_tooling_manifest.json`
- `zigux/Makefile`
- `make -C zigux phase11-validate`

That shared packet is stronger than the older replay-only story: `scripts/zigux/validate-phase11.py` exists, `make -C zigux phase11-validate` is the live shared route, and the new aggregate manifest records the shared checker packet without pretending it replaces the narrower HVC continuity inventory.

## Live Gap Versus The Roadmap

The narrower shared manifest gap recorded earlier is now materially closed.

Current `master` now ships a small aggregate surface through:

- `zigux/tests/fixtures/phase11_shared_tooling_manifest.json`
- `scripts/zigux/check-phase11-shared-tooling-manifest.py`

That aggregate surface enumerates the live shared checker stack, the surviving shared validation routes, the allowed driver-local matrix notes, and the focused proof-backed build shards that the shared packet is still allowed to name.
It also distinguishes the narrower `zigux/tests/fixtures/phase11_build_inventory.json` HVC continuity packet from the broader shared `phase11-validate` proof fan-out, so reminder notes no longer need to overload one HVC-only inventory as if it covered the entire shared Phase 11 packet.

## Boundaries For Follow-Through

Keep the next deterministic-tooling step narrow:

- do not revive removed `phase11`, `phase11-contract`, or `zigux/tests/phase11_build.zig` routes just to recover old naming
- do not collapse bcm2835, gpio, DesignWare, HVC, and header-boundary evidence into one fake green dashboard
- do not widen this tooling step into driver behavior, platform-backed execution, or broader contributor-surface ownership already handled by nearby Phase 11 lanes
- do not treat the narrower `zigux/tests/fixtures/phase11_build_inventory.json` packet as if it already covers the whole shared validator route

## Recommended Next Bounded Step

- The next bounded follow-through can stay smaller: wire this checker into the shared `phase11-validate` route only after current-head rereads confirm the surrounding Phase 11 packet did not drift again.
- keep the aggregate manifest limited to shared tooling surfaces and explicitly allowed proof-backed build shards
- update broader reminder summaries only after that checker-backed surface has been reread together with the current shared Phase 11 packet
