# Zigux Review Checklist

Use this checklist before opening or merging Zigux product work.

## Scope

  * is the target phase named explicitly?
  * is the status bucket explicit: port now, port after substrate, dual implementation required, study only, or freeze in C initially?
  * is the Linux anchor file or tree path named directly?
## Safety

  * does the change avoid mirror-tree sprawl?
  * is real code co-located with the owning Linux subsystem when appropriate?
  * does the change avoid deep-core scope creep into scheduler, MM, RCU, or skbuff without an Architecture Council decision?
## Validation
  * are parity tests or fixture checks included?
  * is there a stated performance gate if the code is algorithmic, queueing-sensitive, or driver-facing?
  * is there a stated rollback owner and fallback path?
  * if the change touches the shared Phase 4 rollback-ownership and lab-matrix packet, do `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase4-repo-reality-warning.py` and `scripts/zigux/check-phase4-reversible-delivery-pins.py` still agree on the current direct-readback packet, keep the directly readable local-only perf packet explicit, keep the repo-reality warning explicit for the missing broader Phase 4 validator, lab-matrix, bitmap-diff, and roadmap-backed `atomic64_diff` companions, keep the host-side artifact-diff contract plus remaining-gap wording truthful, keep the parked kprobe and parked `test_fsmount` reminder packet framed as last-known packet members rather than current direct evidence, keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion, keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call, and keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval?
