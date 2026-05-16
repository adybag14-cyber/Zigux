# Zigux Release Tranche Sequencing

This note is the shared PMO release spine for the current late-phase Zigux packet.

It is a sequencing artifact, not a closure claim, not a new replay route, and not permission to widen release work beyond the roadmap-backed Phase 12 through Phase 15 packet.

## Status
- `RELEASE_SPINE_STATUS=active`
- `RELEASE_SPINE_RELEASE_CLOSED=no`
- scope: keep the shipped late-phase release packet reviewable across the existing Phase 12, Phase 13, Phase 14, and Phase 15 release notes without letting phase-local summaries drift apart
- primary roadmap anchors:
  - `Phase 12: complex drivers and release coordination`
  - `Phase 13: contributor-facing shared-helper release packet`
  - `Phase 14: study-only end-to-end smoke and release-boundary evidence`
  - `Phase 15: governance, readiness gates, and indefinite-C handoff policy`
- docs-root phase owners remain:
  - `Documentation/zigux/phase12-release-sequencing.md`
  - `Documentation/zigux/phase12-release-closure-checklist.md`
  - `Documentation/zigux/phase12-release-readiness-survey.md`
  - `Documentation/zigux/phase12-release-coordination-matrix.md`
  - `Documentation/zigux/phase13-release-notes-survey.md`
  - `Documentation/zigux/phase13-release-coordination-matrix.md`
  - `Documentation/zigux/phase14-release-boundary-survey.md`
  - `Documentation/zigux/phase15-readiness-gate-survey.md`
  - `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- freeze-map boundary owner: `Documentation/zigux/freeze-map.md`

## Shared Release Order
1. Keep `Phase 12` as the first release-facing tranche because it owns the shipped validator-first then smoke-first driver packet. The stable shared order remains `make -C zigux phase12-validate`, then `make -C zigux phase12-smoke`, then `make -C zigux phase12`, with the existing `zigux/tests/phase12_build.zig`, workflow, and Makefile wiring staying authoritative for that packet.
2. Treat `Phase 13` as the next contributor-facing release tranche only after the active `Phase 12` packet stays truthful. The stable shared Phase 13 handle remains `python3 scripts/zigux/validate-phase13-release.py` and `make -C zigux phase13-validate`, while `make -C zigux phase13` stays blocked convenience wiring until `zigux/tests/phase13_build.zig` actually lands.
3. Keep `Phase 14` behind those two tranches as study-only smoke and release-boundary evidence. Its release wording may summarize smoke posture and rollback boundaries, but it must not promote `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c` into active delivery claims.
4. Leave `Phase 15` last in the release spine because it is the governance and readiness gate owner. Freeze-map status, parity scorecards, and indefinite-C policy stay parked there until the prior release packet remains stable and an Architecture Council decision record actually exists where required.

## Tranche Rules
- `Phase 12` remains active, not closed. Its release packet may coordinate `virtio_net`, `virtio_scsi`, parked libbpf reviewability, and the published-but-unwired `nvme_pci` foothold, but must stay distinct from deeper transport or queueing delivery claims.
- `Phase 13` remains active, not closed. Its release packet may summarize the shipped `libfs`, `devres`, `landlock/ruleset`, and `landlock/syscalls` helpers plus adjacent notifier evidence, but must keep repo-reality gaps explicit and must not pretend the missing shared `zigux/tests/phase13_build.zig` route is shipped.
- `Phase 14` remains study-only. Its release packet may summarize smoke evidence, rollback-threshold ordering, and freeze-map-aligned boundary surveys, but must stay review-first and must not imply deep-core release closure.
- `Phase 15` remains governance-first. Its release packet may summarize readiness gates, handoff posture, and stay-in-C policy, but it must not imply Architecture Council approval or a freeze-map status change unless the repo carries that decision record.

## Cross-Phase Handoff Conditions
- do not widen the shared release summary from `Phase 12` into `Phase 13` unless the current `Phase 12` validator-first support bundle and smoke-first wording still agree across the docs root, scripts root, tests root, workflow, and Makefile
- do not treat `Phase 13` as broadly releasable while its stable handle is still `make -C zigux phase13-validate` and the broader `make -C zigux phase13` route remains blocked convenience wiring
- do not use `Phase 14` smoke evidence as proof that study-only or freeze-in-C anchors are ready for active delivery
- do not use `Phase 15` governance wording as evidence that any earlier tranche is closed; Phase 15 owns parked readiness and handoff truthfulness, not retroactive closure of earlier active packets

## PMO Owner Split
- PMO / Release Management owns the cross-phase order, the active-versus-closed posture, and the rule that each phase-local note stays the source of truth for its own packet details.
- Phase-local docs remain the owners of direct replay commands, packet inventories, gap wording, and local non-goals.
- `Documentation/zigux/freeze-map.md` remains the owner of deep-core and study-only boundaries when release wording touches frozen anchors.

## Review Use
- reread this note beside:
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/freeze-map.md`
  - `Documentation/zigux/phase12-release-sequencing.md`
  - `Documentation/zigux/phase12-release-closure-checklist.md`
  - `Documentation/zigux/phase12-release-readiness-survey.md`
  - `Documentation/zigux/phase12-release-coordination-matrix.md`
  - `Documentation/zigux/phase13-release-notes-survey.md`
  - `Documentation/zigux/phase13-release-coordination-matrix.md`
  - `Documentation/zigux/phase14-release-boundary-survey.md`
  - `Documentation/zigux/phase15-readiness-gate-survey.md`
  - `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- keep future PMO work bounded to one wording repair or one owner-map repair at a time rather than reopening multiple phase-local packets together
- if a later run changes one phase-local release packet, update this note only when the shared late-phase release order or handoff posture changes too

## Non-Goals
- This note does not close Phase 12, Phase 13, Phase 14, or Phase 15.
- This note does not add a new validator, workflow route, or build target.
- This note does not override phase-local release notes, surveys, or coordination matrices.
- This note does not authorize delivery against freeze-in-C or study-only anchors.
