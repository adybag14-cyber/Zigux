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

Current `master` still exposes this sequencing note and the narrower shared-versus-adjacent owner split, but nearby runs should treat `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-tests-readme-packet.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-perf-threshold-matrix.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` as the current direct-readback handoff before widening beyond the exact packet that handoff already names.

- current direct-readback shared handoff:
  - `Documentation/zigux/phase4-reversible-delivery-evidence.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `zigux/tests/README.md`
  - `scripts/zigux/README.md`
  - `scripts/zigux/check-phase4-repo-reality-warning.py`
  - `scripts/zigux/check-phase4-tests-readme-packet.py`
  - `scripts/zigux/check-phase4-reversible-delivery-pins.py`
- directly readable dedicated local-only perf packet that still stays adjacent to the shared handoff:
  - `scripts/zigux/check-phase4-perf-baseline-packet.py`
  - `scripts/zigux/check-phase4-perf-threshold-matrix.py`
  - `zigux/tests/phase4_perf_baseline_manifest.json`
  - `zigux/tests/phase4_perf_baseline_survey.zig`
  - `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig`
  - `make -C zigux phase4-perf-baseline-survey`
- recovered broader shared exact-readback and owner-map companions that now reread directly on current `master`:
  - `Documentation/zigux/phase4-gate-evidence.md`
  - `Documentation/zigux/phase4-validation-matrix.md`
  - `Documentation/zigux/phase4-validation-lane-sequencing.md`
  - `scripts/zigux/check-phase4-gate-evidence.py`
  - `scripts/zigux/check-phase4-remaining-gap-matrix.py`
  - `scripts/zigux/check-phase4-workflow-route-counts.py`
  - `scripts/zigux/validate-phase4.py`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`
- directly readable roadmap-backed differential-gate pair and manifest-backed atomic64 handoff packet:
  - `zigux/tests/atomic64_diff.zig`
  - `zigux/tests/runtime_atomic64_diff.zig`
  - `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`
  - `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`
- public-raw returned broader build and bitmap replay companions that still need same-route authenticated blob capture:
  - `zigux/tests/phase4_build.zig`
  - `zigux/tests/bitmap_diff.zig`
  - `zigux/tests/phase4_bitmap_live_helper_replay.zig`
- parked starter-gap packets:
  - `Documentation/zigux/phase4-kprobe-example-gap-survey.md`
  - `zigux/tests/phase4_kprobe_example_manifest.json`
  - `zigux/tests/phase4_kprobe_example_survey.zig`
  - `Documentation/zigux/phase4-test-fsmount-gap-survey.md`
  - `zigux/tests/phase4_test_fsmount_manifest.json`
  - `zigux/tests/phase4_test_fsmount_survey.zig`

That means current Phase 4 work is no longer about inventing a missing validation family. The live sequencing risk is overlap between the current direct-readback handoff, the recovered broader note-and-checker companions, the directly readable atomic64 differential packet, the directly readable shared validator companion, and the public-raw returned but still same-route-uncaptured build and bitmap replay routes: shared exact-readback, reversible-delivery, or review-checklist wording can accidentally reopen local perf-policy work, parked starter-gap packet work, or the build and bitmap replay companions as if those surfaces were either still missing-current-master gaps or already one uniformly exact-pinned current-head packet again.

## Owner map

### Shared exact-readback lane

Treat `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-tests-readme-packet.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, and this sequencing note as the shared side of the current direct-readback owner map for Phase 4 wording that spans more than one validation packet, while `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-perf-threshold-matrix.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` remain directly readable adjacent evidence inside the perf-only lane rather than historical companions.

This shared lane owns only:
- wording that keeps the current direct-readback handoff explicit instead of reconstructing the broader shared packet from older route names alone
- wording that keeps `Documentation/zigux/phase4-validation-matrix.md` plus `scripts/zigux/check-phase4-remaining-gap-matrix.py` paired as one shared lab-matrix control surface now that that broader pair is directly readable again, so current runs repair the repo-reality handoff first instead of reopening parked-gap or perf lanes from stale route names alone
- wording that keeps the shipped atomic64, bitmap, helper-backed bitmap replay, and manifest-backed survey packet boundaries explicit together
- wording that keeps the shipped host-side artifact-diff helper contract, deterministic catalog replay, and validator-first replay routes explicit together without treating the directly readable validator companion or the public-raw returned but still exact-blob-debt-laden build and bitmap replay companions as either missing-current-master gaps or exact direct-readback proof
- wording that keeps the current rollback owners, reviewer prompts, reversible-delivery handoff, and validator-first replay routes explicit together
- wording that keeps the current broader shared-CI perf-promotion coordination-owner split explicit across both landed rollback gates while the dedicated Validation and Perf Team decision-owner and rollback-owner cue stays inside the adjacent local-only perf packet
- wording that keeps the directly readable local-only perf packet, the recovered broader note-and-checker companions, the directly readable atomic64 differential packet, the directly readable validator companion, the public-raw returned build and bitmap replay companions, and the parked starter-gap packets visible as adjacent evidence without claiming they are the same shared gate

This shared lane does not own the approved local perf commands and acceptable limits themselves, and it does not own starter-gap packet-local reminder wording beyond naming that those packets remain parked and adjacent.

### Local-only perf packet

The dedicated perf lane owns only the landed packet for:
- `scripts/zigux/check-phase4-perf-baseline-packet.py`
- `scripts/zigux/check-phase4-perf-threshold-matrix.py`
- `zigux/tests/phase4_perf_baseline_manifest.json`
- `zigux/tests/phase4_perf_baseline_survey.zig`
- the paired local replay routes `zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-perf-baseline-survey`

Keep perf-local follow-through inside the approved local-only packet: the dedicated local checker pair, the benchmark commands, the acceptable limits, the local-only posture, the decision-owner and rollback-owner wording for any future wider promotion, and the manifest-backed survey truthfulness.

Keep the Validation and Perf Team decision-owner and rollback-owner cue in the dedicated local-only perf packet, but leave the current cross-family coordination-owner split with the ABI and Runtime Team plus Shared Subsystems Pod in the shared exact-readback lane because that wording spans both landed rollback gates.

Do not use the perf lane to rewrite the current direct-readback handoff, shared rollback-owner wording, or parked starter-gap packet wording unless a broader shared packet change has already landed and the perf note is only catching up to that directly readable state.

### Parked starter-gap packets

The parked starter lanes own only the current absent-starter evidence for:
- `Documentation/zigux/phase4-kprobe-example-gap-survey.md`
- `zigux/tests/phase4_kprobe_example_manifest.json`
- `zigux/tests/phase4_kprobe_example_survey.zig`
- `Documentation/zigux/phase4-test-fsmount-gap-survey.md`
- `zigux/tests/phase4_test_fsmount_manifest.json`
- `zigux/tests/phase4_test_fsmount_survey.zig`

Both packet-local manifests currently still advertise `"lane_key": "P4-L19"` as the shared parked-gap coordination label.

Treat that label as historical grouping only, not as permission to batch kprobe and `test_fsmount` follow-through into the same repair.

Current shared reminder ownership is narrower than that historical label: `P4-L24` now covers the matrix-side and sequencing-note reminder wording around `Documentation/zigux/phase4-validation-matrix.md` plus `scripts/zigux/check-phase4-remaining-gap-matrix.py`, while the live `P4-L19` lane now owns checker-local measurability follow-through when that dedicated remaining-gap checker falls behind the already-landed shared matrix, sequencing, checklist, or parked-gap markers. Do not route either reminder surface through a parked starter-gap lane just because the parked manifests still say `P4-L19`, and do not assume `P4-L19` is checklist-only after the landed measurability guard tightening.

Keep starter-gap follow-through inside those parked packets: the current Linux anchor, the current replay path, the local survey wrapper, the direct validation entrypoint, the owner and rollback-owner wording, the reviewability-only threshold posture, and the next bounded evidence step while `samples/zigux/kprobe_example.zig` and `samples/zigux/test_fsmount.zig` remain absent on current `master`.

Do not use a parked starter-gap lane to reopen the current direct-readback handoff, the local perf approval packet, or the shipped atomic64 or bitmap gate wording by itself.

## Anti-overlap rules

When a Phase 4 validation change is proposed, choose the narrowest owner first.
- If a change only repairs the current direct-readback warning or reminder packet, keep it inside `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-tests-readme-packet.py`, or `scripts/zigux/check-phase4-reversible-delivery-pins.py` before reopening older broader companions.
- If a change only repairs one starter-gap survey note, one starter-gap manifest, one starter-gap survey gate, one direct validation entrypoint reminder, or one parked next-step handoff, keep it inside that single parked starter packet.
- Even while both parked starter-gap manifests still carry the historical `P4-L19` label, reopen only the one parked packet that drifted; do not repair the sibling parked packet in the same run unless the shared exact-readback lane needs a later post-publication catch-up.
- If the drift is limited to the matrix-side or sequencing-note reminder surfaces around `scripts/zigux/check-phase4-remaining-gap-matrix.py`, keep it in the live `P4-L24` matrix reminder lane; if the drift is limited to the dedicated remaining-gap checker falling behind those already-landed markers, keep it in the live `P4-L19` checker-maintenance lane before reopening either parked starter-gap packet.
- If the drift is limited to how `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, or `zigux/tests/phase4_bitmap_live_helper_replay.zig` are described beside the shared handoff, keep it in the shared exact-readback lane and describe `scripts/zigux/validate-phase4.py` as a directly readable current-`master` companion while `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` remain public-raw returned companions with exact authenticated blob refresh still pending; do not reopen perf or parked starter-gap lanes just because the same-route blob capture still flaps.
- If a change only refreshes approved local benchmark commands, acceptable limits, or the dedicated local-only perf decision-owner or rollback-owner cue for a future wider promotion, keep it inside the dedicated perf packet.
- Keep dedicated local perf checker maintenance in that same dedicated perf packet.
- If a change refreshes the current shared coordination-owner split across both landed rollback gates, keep it in the shared exact-readback lane even when the dedicated perf packet still carries the adjacent decision-owner cue.
- If a change only refreshes how the shipped rollback-readiness packet, the reversible-delivery handoff, the shared review checklist, the host-side artifact-diff tooling packet, the rollback-owner map, the validator-first route, and adjacent parked packets are described together, keep it in the shared exact-readback lane.
- If the drift is limited to `Documentation/zigux/phase4-validation-matrix.md` and `scripts/zigux/check-phase4-remaining-gap-matrix.py`, repair that shared lab-matrix pair first while keeping the narrower direct-readback handoff and the public-raw returned build and bitmap replay companions explicit, rather than treating the matrix pair as historical broader packet members.
- If the drift is limited to blob pins or exact-readback markers in `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/phase4-gate-evidence.md`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, or `scripts/zigux/check-phase4-gate-evidence.py`, repair the directly readable repo-reality handoff first and return to this sequencing note only if the published pin refresh still leaves the owner split ambiguous.
- If a shared reminder surface needs one perf-local or starter-gap cue, point to that exact packet instead of restating packet-local behavior from memory.
- Do not use the shared exact-readback lane to change local-only perf limits or starter-gap packet-local replay wording.
- Do not use the perf lane to claim shared CI perf approval unless the broader shared packet has intentionally widened and names that policy decision directly.
- Do not use the parked starter-gap lanes to imply that either Zig starter has landed while the current measurable state is still the dedicated parked survey packet.

## Next-step filter

Use this note to keep future Phase 4 follow-through bounded:
- reopen the current direct-readback shared lane first for one repo-reality warning, rollback-owner, current-head readback, review-checklist, tests-root, or exact-pin repair across the already landed shared Phase 4 packet
- route matrix-side or sequencing-note remaining-gap reminder drift through the live `P4-L24` matrix reminder lane, and route dedicated remaining-gap checker measurability drift through the live `P4-L19` checker-maintenance lane, before treating the parked starter-gap manifests' historical `P4-L19` label as a reason to reopen this sequencing note or the parked packets
- reopen broader validator/build/bitmap replay follow-through only after a same-family reread or republish gives one steady same-route authenticated blob capture for `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig`; `scripts/zigux/validate-phase4.py` is now directly readable on current `master`, so do not group it back into the still-flapping public-raw-only build and bitmap trio
- treat blob-pin refreshes inside `Documentation/zigux/phase4-reversible-delivery-evidence.md` or `Documentation/zigux/phase4-gate-evidence.md` as shared exact-readback follow-through, not as a reason to reopen this sequencing note unless the published repair still leaves the validation-lane split unclear
- reopen the dedicated perf lane only for one checker, manifest, survey, benchmark-command, acceptable-limit, or local-only policy truthfulness repair
- reopen a parked starter-gap lane only for one packet-local note, manifest, survey gate, wrapper, entrypoint, owner-map, or next-step truthfulness repair, even while the packet-local status blocks still share the historical `P4-L19` coordination label
- update the directly coupled packet first when packet-local behavior changes, then refresh shared exact-readback wording only after that packet-local state is directly readable on current `master`

This keeps Phase 4 aligned with the roadmap's validation-first rollback packet while preventing shared note maintenance from turning back into overlapping perf-policy, starter-gap, or stale broader-packet work.