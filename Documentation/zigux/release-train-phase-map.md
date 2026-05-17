# Zigux Release Train Phase Map

This note is the compact PMO release-planning map for the current release-facing Zigux packet.

It does not close any tranche, and it does not create a new replay route. It records how the active release-planning surfaces already on `master` fit together across the late roadmap phases.

## Source Anchors

- roadmap: `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`
- bootstrap ledger: `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`
- Phase 12 sequencing: `Documentation/zigux/phase12-release-sequencing.md`
- Phase 13 coordination: `Documentation/zigux/phase13-release-coordination-matrix.md`
- Phase 14 boundary survey: `Documentation/zigux/phase14-release-boundary-survey.md`
- Phase 15 readiness survey: `Documentation/zigux/phase15-readiness-gate-survey.md`
- Phase 15 handoff survey: `Documentation/zigux/phase15-handoff-next-steps-survey.md`

## Release Order By Phase

1. Phase 12 stays the first active release packet.
   - current posture: active, not closed
   - role: validator-first then smoke-first release packet for the starter-present `virtio_net` path and the shipped `virtio_scsi` packet
   - current shared handle: `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, and `make -C zigux phase12`
   - bounded release gap: the published NVMe foothold remains outside the shared wired route, and the broader libbpf packet remains planning or fallback material rather than shared release proof

2. Phase 13 stays the second active release packet.
   - current posture: active, not closed
   - role: shared-helper release coordination across `libfs`, `devres`, and the two Landlock anchors, with notifier evidence kept adjacent rather than promoted into a fifth anchor
   - current shared handle: stable `make -C zigux phase13-validate`; `make -C zigux phase13` remains blocked convenience wiring
   - bounded release gap: the shared-summary checker, notifier survey, and shared `phase13_build` route still need to stay framed as repo-reality gaps until they materialize again

3. Phase 14 stays the release-boundary packet.
   - current posture: release boundary present, not closed
   - role: validator-backed smoke and full-bundle review for study-only deep-core boundary surfaces, not active deep-core delivery
   - current shared handle: `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `make -C zigux phase14-test`, and `make -C zigux phase14`
   - bounded release gap: Phase 14 may refine only the boundary map, smoke inventory, or concurrency-audit packet while freeze-in-C status decisions remain deferred to Phase 15 governance

4. Phase 15 stays the parked governance packet.
   - current posture: parked governance packet, no recorded Architecture Council approval for a freeze-map status change
   - role: readiness, handoff, parity-scorecard, freeze-map, and indefinite-C governance for late-phase release truthfulness
   - current shared handle: `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15`
   - bounded release gap: the remaining work is truthfulness maintenance around shared summaries, handoff wording, and blocker posture rather than a new deep-core implementation commitment

## Cross-Phase Release Rules

- Do not describe Phase 12, Phase 13, or Phase 14 as closed while their own release notes still mark them active or boundary-only.
- Treat Phase 15 as the governance owner for any future status-change discussion on frozen or study-only deep-core anchors.
- Keep Phase 13 notifier evidence adjacent to the shared-helper packet instead of treating it as a fifth roadmap anchor.
- Keep Phase 12 NVMe progress visible as a published foothold outside the shared wired route until the shared release packet actually widens.
- When release wording changes, reread the phase-local sequencing, coordination, boundary, readiness, and handoff companions together before broadening PMO language.

## Tranche Closure Posture

- Roadmap comparison: the repo already carries late-phase release-planning material beyond the bootstrap ledger's early documentation footholds.
- Ledger comparison: the remaining PMO work is no longer "create a release surface from scratch"; it is to keep the existing release surfaces sequenced, honest, and non-overlapping.
- Closure posture: none of Phases 12 through 15 should be rounded up into a closed release train yet.

## Next Bounded PMO Follow-Through

- Phase 12: refresh only the next shared reminder or support checker that drifts against the validator-first then smoke-first packet.
- Phase 13: refresh only the next shared-summary truthfulness surface without widening into helper implementation or notifier implementation work.
- Phase 14: refresh only the next boundary-map or smoke-packet truthfulness surface without reopening frozen anchors.
- Phase 15: refresh only the next docs-root, scripts-root, or tests-root governance summary drift without implying approval for a freeze-map status change.
