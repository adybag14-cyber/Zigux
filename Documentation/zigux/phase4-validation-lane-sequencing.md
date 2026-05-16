# Phase 4 Validation Lane Sequencing

This note records the current owner map for the shipped Phase 4 validation packet so shared exact-readback work, the shipped host-side artifact-diff tooling packet, the dedicated local-only perf packet, and the parked starter-gap surveys do not drift back into overlapping maintenance.

## Scope

Use this note only for bounded sequencing and anti-overlap decisions across the already landed validation-lane surfaces on current `master`.

Keep this note grounded in the roadmap-backed Phase 4 destination set:

- `lib/atomic64_test.c`
- `lib/test_bitmap.c`
- `samples/kprobes/kprobe_example.c`
- `samples/vfs/test-fsmount.c`

Treat the current Phase 4 validation packet as the shipped rollback-readiness and reviewability boundary for those anchors unless the roadmap changes.

## Current repo reality

Current `master` already carries the active shared-versus-adjacent Phase 4 packet:

- shared exact-readback and owner-map surfaces:
  - `Documentation/zigux/artifact-diff.md`
  - `Documentation/zigux/phase4-gate-evidence.md`
  - `Documentation/zigux/phase4-reversible-delivery-evidence.md`
  - `Documentation/zigux/phase4-validation-matrix.md`
  - `Documentation/zigux/review-checklist.md`
  - `scripts/zigux/artifact_diff.py`
  - `scripts/zigux/check-artifact-diff-contract.py`
  - `scripts/zigux/check-phase4-artifact-diff-determinism.py`
  - `scripts/zigux/check-phase4-gate-evidence.py`
  - `scripts/zigux/check-phase4-remaining-gap-matrix.py`
  - `scripts/zigux/check-phase4-reversible-delivery-pins.py`
  - `scripts/zigux/check-phase4-workflow-route-counts.py`
  - `scripts/zigux/validate-phase4.py`
  - `zigux/tests/phase4_build.zig`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`
- dedicated local-only perf packet:
  - `scripts/zigux/check-phase4-perf-baseline-packet.py`
  - `zigux/tests/phase4_perf_baseline_manifest.json`
  - `zigux/tests/phase4_perf_baseline_survey.zig`
  - `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig`
  - `make -C zigux phase4-perf-baseline-survey`
- parked starter-gap packets:
  - `Documentation/zigux/phase4-kprobe-example-gap-survey.md`
  - `zigux/tests/phase4_kprobe_example_manifest.json`
  - `zigux/tests/phase4_kprobe_example_survey.zig`
  - `Documentation/zigux/phase4-test-fsmount-gap-survey.md`
  - `zigux/tests/phase4_test_fsmount_manifest.json`
  - `zigux/tests/phase4_test_fsmount_survey.zig`

That means current Phase 4 work is no longer about inventing a missing validation family. The live risk is overlap: shared exact-readback, reversible-delivery handoff, review-checklist, or host-side artifact-diff wording reopening local perf-policy work, or parked starter-gap truthfulness repairs drifting into shared rollback-owner, artifact-diff tooling, or validator-first maintenance.

## Owner map

### Shared exact-readback lane

Treat `Documentation/zigux/phase4-gate-evidence.md` together with `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, and the shipped host-side tooling note at `Documentation/zigux/artifact-diff.md` as the shared owner map for current-head Phase 4 wording that spans more than one validation packet.

This shared lane owns only:

- the connector-readback and host-side artifact-diff packet in `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/check-phase4-artifact-diff-determinism.py`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- wording that keeps `Documentation/zigux/phase4-validation-matrix.md` plus `scripts/zigux/check-phase4-remaining-gap-matrix.py` paired as one shared lab-matrix control surface, so drift in the parked-gap Lab And CI Matrix row or the rollback-failure rule is repaired there before widening into `Documentation/zigux/phase4-gate-evidence.md` or the parked starter-gap notes
- wording that keeps the shipped atomic64, bitmap, helper-backed bitmap replay, and manifest-backed survey packet boundaries explicit together
- wording that keeps the shipped host-side artifact-diff helper contract, deterministic catalog replay, and validator-first replay routes explicit together
- wording that keeps the current rollback owners, reviewer prompts, reversible-delivery handoff, and validator-first replay routes explicit together
- wording that keeps the current broader shared-CI perf-promotion coordination-owner split explicit across both landed rollback gates while the dedicated Validation and Perf Team decision-owner cue stays inside the adjacent local-only perf packet
- wording that keeps the local-only perf packet and the parked starter-gap packets visible as adjacent evidence without claiming they are the same shared gate

This shared lane does not own the approved local perf commands and acceptable limits themselves, and it does not own starter-gap packet-local reminder wording beyond naming that those packets remain parked and adjacent.

### Local-only perf packet

The dedicated perf lane owns only the landed packet for:

- `scripts/zigux/check-phase4-perf-baseline-packet.py`
- `zigux/tests/phase4_perf_baseline_manifest.json`
- `zigux/tests/phase4_perf_baseline_survey.zig`
- the paired local replay routes `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey`

Keep perf-local follow-through inside the approved local-only packet: the dedicated local checker, the benchmark commands, the acceptable limits, the local-only posture, the decision-owner wording for any future wider promotion, and the manifest-backed survey truthfulness.

Keep the Validation and Perf Team decision-owner cue in the dedicated local-only perf packet, but leave the current cross-family coordination-owner split with the ABI and Runtime Team plus Shared Subsystems Pod in the shared exact-readback lane because that wording spans both landed rollback gates.

Do not use the perf lane to rewrite shared exact-readback blob pins, shared rollback-owner wording, or parked starter-gap packet wording unless a broader shared packet change has already landed and the perf note is only catching up to that directly readable state.

### Parked starter-gap packets

The parked starter lanes own only the current absent-starter evidence for:

- `Documentation/zigux/phase4-kprobe-example-gap-survey.md`
- `zigux/tests/phase4_kprobe_example_manifest.json`
- `zigux/tests/phase4_kprobe_example_survey.zig`
- `Documentation/zigux/phase4-test-fsmount-gap-survey.md`
- `zigux/tests/phase4_test_fsmount_manifest.json`
- `zigux/tests/phase4_test_fsmount_survey.zig`

Both packet-local manifests currently still advertise `"lane_key": "P4-L19"` as the shared parked-gap coordination label. Treat that label as historical grouping only, not as permission to batch kprobe and `test_fsmount` follow-through into the same repair.

Keep starter-gap follow-through inside those parked packets: the current Linux anchor, the current replay path, the local survey wrapper, the direct validation entrypoint, the owner and rollback-owner wording, the reviewability-only threshold posture, and the next bounded evidence step while `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` remain absent on current `master`.

Do not use a parked starter-gap lane to reopen shared exact-readback inventory, the local perf approval packet, or the shipped atomic64 or bitmap gate wording by itself.

## Anti-overlap rules

When a Phase 4 validation change is proposed, choose the narrowest owner first.

- If a change only repairs one starter-gap survey note, one starter-gap manifest, one starter-gap survey gate, one direct validation entrypoint reminder, or one parked next-step handoff, keep it inside that single parked starter packet.
- Even while both parked starter-gap manifests still carry `P4-L19`, reopen only the one parked packet that drifted; do not repair the sibling parked packet in the same run unless the shared exact-readback lane needs a later post-publication catch-up.
- If a change only refreshes approved local benchmark commands, acceptable limits, or the dedicated local-only perf decision-owner cue for a future wider promotion, keep it inside the dedicated perf packet.
- Keep dedicated local perf checker maintenance in that same dedicated perf packet.
- If a change refreshes the current shared coordination-owner split across both landed rollback gates, keep it in the shared exact-readback lane even when the dedicated perf packet still carries the adjacent decision-owner cue.
- If a change only refreshes how the shipped rollback-readiness packet, the reversible-delivery handoff, the shared review checklist, the host-side artifact-diff tooling packet, the rollback-owner map, the validator-first route, and adjacent parked packets are described together, keep it in the shared exact-readback lane.
- If the drift is limited to `Documentation/zigux/phase4-validation-matrix.md` and `scripts/zigux/check-phase4-remaining-gap-matrix.py`, repair that shared lab-matrix pair first and only widen into `Documentation/zigux/phase4-gate-evidence.md` or the parked starter-gap packets if the published matrix-side repair leaves a directly coupled readback mismatch behind.
- If the drift is limited to blob pins or exact-readback markers in `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/phase4-gate-evidence.md`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, or `scripts/zigux/check-phase4-gate-evidence.py`, repair that shared exact-readback handoff first and return to this sequencing note only if the published pin refresh still leaves the owner split ambiguous.
- If a shared reminder surface needs one perf-local or starter-gap cue, point to that exact packet instead of restating packet-local behavior from memory.
- Do not use the shared exact-readback lane to change local-only perf limits or starter-gap packet-local replay wording.
- Do not use the perf lane to claim shared CI perf approval unless the broader shared packet has intentionally widened and names that policy decision directly.
- Do not use the parked starter-gap lanes to imply that either Zig starter has landed while the current measurable state is still the dedicated parked survey packet.

## Next-step filter

Use this note to keep future Phase 4 follow-through bounded:

- reopen the shared exact-readback lane only for one rollback-owner, current-head readback, host-side artifact-diff tooling, workflow-route, cross-packet sequencing, reversible-delivery, review-checklist, or shared coordination-owner repair across the already landed shared Phase 4 packet
- treat blob-pin refreshes inside `Documentation/zigux/phase4-reversible-delivery-evidence.md` or `Documentation/zigux/phase4-gate-evidence.md` as shared exact-readback follow-through, not as a reason to reopen this sequencing note unless the published repair still leaves the validation-lane split unclear
- reopen the dedicated perf lane only for one checker, manifest, survey, benchmark-command, acceptable-limit, or local-only policy truthfulness repair
- reopen a parked starter-gap lane only for one packet-local note, manifest, survey gate, wrapper, entrypoint, owner-map, or next-step truthfulness repair, even while the packet-local status blocks still share the historical `P4-L19` coordination label
- update the directly coupled packet first when packet-local behavior changes, then refresh shared exact-readback wording only after that packet-local state is directly readable on current `master`

This keeps Phase 4 aligned with the roadmap's validation-first rollback packet while preventing shared note maintenance from turning back into overlapping perf-policy or starter-gap work.
