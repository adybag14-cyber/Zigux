# Zigux Release Tranche Status

This note is a docs-root PMO release artifact.

It does not claim new code delivery, and it does not replace the phase-local closure or survey notes. Its job is to give one compact release-planning view of which roadmap-backed tranches are closed, which are still active, and which phases still need a first explicit closure-side handoff.

## Scope

- repo evidence used: current `master` docs-root and phase-local release notes visible through GitHub app reads on 2026-05-19
- roadmap authority: `ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`
- commit-train authority: `BOOTSTRAP_COMMIT_LEDGER.md`
- lane owner: `pmo-release`

## Current Release Train Reading

### Closed or parked closure-backed tranches

| Phase | Roadmap focus | Current release posture | Current authority | Next PMO action |
| --- | --- | --- | --- | --- |
| Phase 1 | host-side helper ports | closed / parked | `Documentation/zigux/phase1-closure.md` and the Phase 1 reminder packet listed in `Documentation/zigux/README.md` | leave parked unless a Phase 1 helper or closure validator drifts |
| Phase 2 | toolchain and kbuild enablement | closed / parked | `Documentation/zigux/phase2-closure.md` and the returned Phase 2 validator plus make-wrapper packet | leave parked unless the toolchain, kconfig, genksyms, cross-route, or closure packet drifts |

### Active release-planning tranches

| Phase | Roadmap focus | Current release posture | Current authority | Smallest honest next PMO follow-through |
| --- | --- | --- | --- | --- |
| Phase 3 | ABI and interop substrate | active, not release-closed | `Documentation/zigux/phase3-abi-slice.md` plus the Phase 3 reminder packet enumerated in `Documentation/zigux/README.md` | keep the Phase 3 packet aligned and only widen after the next truthful reread of the policy, wrapper, and export/UAPI companions |
| Phase 5 | bounded sample reviewability | active, packetized | `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, and the sample-root reminder packet from `Documentation/zigux/README.md` | keep the no-extra-sample boundary explicit and avoid promoting runtime samples into Phase 5 closure evidence |
| Phase 9 | runtime pilot samples | active, narrow | `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` plus the Phase 9 reminder packet from `Documentation/zigux/README.md` | keep the trace-events and runtime-bitmap packets separate from any broader runtime-loader claim |
| Phase 10 | virtio driver tranche | active, bounded | `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, and the returned validator packet called out in `Documentation/zigux/README.md` | keep closure wording tied to ring, input, MMIO, and the shared build gate only |
| Phase 11 | simple-driver tranche | active, bounded | the Phase 11 survey, matrix-gap, and owner-packet notes listed in `Documentation/zigux/README.md` | keep HVC and watchdog evidence separated from missing shared replay and absent phase11 make routes |
| Phase 12 | release planning for complex drivers | active, not release-closed | `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md` | keep `phase12-smoke`, `phase12-test`, and `phase12` treated as shipped wrappers while `phase12-validate` stays reminder-only vocabulary |
| Phase 15 | architecture council and governance | active, governance-side | current repo evidence shows `Documentation/zigux/phase15-architecture-council-review-process.md` plus matching tests | keep Phase 15 framed as review-process governance rather than as a product-closure substitute for delivery phases |

### Roadmap phases that still need a first explicit release-status handoff

The roadmap names additional phases that are not represented by a clearly visible closure-side or PMO release-status sheet in the current docs-root packet used for this run:

- Phase 4
- Phase 6
- Phase 7
- Phase 8
- Phase 13
- Phase 14

This is not a claim that those phases lack all repo work.
It is a narrower PMO claim: the current docs-root release packet does not yet provide one compact release-status handoff for them comparable to the Phase 1, Phase 2, or Phase 12 surfaces above.

## Release Order Guidance

1. Keep closed phases parked unless a current-master reread finds drift in their validator or manifest-backed closure packet.
2. Treat Phase 12 as the live PMO release tranche and keep its wording below DMA, deep queueing, and transport-complete claims.
3. Treat Phases 3, 5, 9, 10, 11, and 15 as active supporting tranches whose notes must stay truthful, but do not let them masquerade as release closure for the product as a whole.
4. When a future PMO run needs a new bounded step, prefer the smallest docs-root truthfulness repair or first explicit handoff note for one of the still-unmapped roadmap phases before widening any already-accurate active packet.

## Boundaries

- This note does not change any phase status by itself.
- This note does not reopen parked closure packets.
- This note does not widen roadmap scope beyond what current `master` documentation already supports.
- This note should stay aligned with `Documentation/zigux/README.md`, the phase-local release notes, and the roadmap if any phase posture changes.

## Next Bounded Step

The next honest PMO follow-through after this sheet lands is to add the first explicit docs-root release-status handoff for the highest-value still-unmapped roadmap phase, rather than rewording Phase 12 again unless a fresh repo reread shows new drift there.
