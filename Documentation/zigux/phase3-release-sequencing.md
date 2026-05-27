# Phase 3 Release Sequencing

This note records the current release-order decision for the early Zigux tranches on current `master`.

It is limited to release sequencing across the already-parked Phase 1 and Phase 2 closure packets plus the still-active Phase 3 ABI and interop packet. It does not reopen helper-local implementation work, widen Phase 3 into full completion, or promote later runtime, driver, or study-only phases into the same release decision.

## Current Tranche State

- `PHASE1_RELEASE_FLOOR=parked_closure_packet_present`
- `PHASE2_RELEASE_FLOOR=parked_closure_packet_present`
- `PHASE3_RELEASE_PACKET_STATE=active_not_closed`
- `PHASE3_RELEASE_PACKET_SCOPE=shared ABI bindings, header-family relay, export-and-UAPI layout replay, policy packet, low-level-wrapper reminder surface, and bounded bitmap-cpumask, list-hlist, err_ptr-xarray, and xarray-slot interop starter packets`

Current `master` already carries the parked Phase 1 closure packet through `Documentation/zigux/phase1-closure.md`, the committed helper manifest, and the narrow closure validator path described there. It also carries the parked Phase 2 closure packet through `Documentation/zigux/phase2-closure.md`, the committed Phase 2 tool manifest, the returned validator pair, and the shipped make-wrapper routes named in that note.

Against the roadmap and bootstrap ledger, that means the release floor is no longer blocked on the first two tranches. The unfinished same-family release question is Phase 3: current `master` now serves the bounded ABI, export/UAPI, policy, low-level-wrapper, and interop packet, but the repo truth still describes it as a manifest-backed active packet rather than a closed tranche.

## Sequencing Decision

1. Keep Phase 1 host-side helpers and Phase 2 toolchain enablement as the release floor for the current early Zigux packet.
2. Treat Phase 3 as the next release-sequenced tranche, but only in its current bounded form: shared ABI substrate, focused export/UAPI replay, policy packet, low-level-wrapper packet, and the bounded interop starter slices already named by the live Phase 3 manifest.
3. Do not describe the current Phase 3 packet as closed release evidence while `Documentation/zigux/phase3-abi-slice.md` and `zigux/tests/fixtures/phase3_abi_manifest.json` still frame it as an active reminder packet with bounded replay routes.
4. Keep deeper roadmap movement parked behind this decision. No Phase 4 runtime helpers, Phase 9 runtime pilots, or Phase 12 driver-release claims should be pulled forward by this note.

- `PHASE3_RELEASE_SEQUENCE=phase1_floor_then_phase2_floor_then_phase3_active_packet`
- `PHASE3_RELEASE_PROMOTION_RULE=promote only after shared Phase 3 reminder surfaces and replay routes stay aligned and a dedicated closure packet exists`
- `PHASE3_RELEASE_NON_GOALS=do_not_claim_full_phase3_completion_or_later_phase_readiness`

## Current Release Evidence

The current release-order evidence is:

- `Documentation/zigux/phase1-closure.md`
- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/phase3-abi-slice.md`
- `zigux/tests/fixtures/phase3_abi_manifest.json`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`

That evidence is enough to keep the release sequence honest:

- Phase 1 is parked as a closed helper tranche.
- Phase 2 is parked as a closed toolchain tranche.
- Phase 3 is active, reviewable, and replay-backed, but not yet a closed release tranche.

## Next PMO Step

The next bounded same-lane follow-through is to add one dedicated Phase 3 release-closure checklist or coordination matrix that turns the current active packet into an explicit handoff target without widening into implementation work or later-phase release claims.

- `PHASE3_RELEASE_NEXT_SAFE_STEP=add one dedicated Phase 3 release-closure checklist or coordination matrix tied to the shared reminder packet and live replay routes`
