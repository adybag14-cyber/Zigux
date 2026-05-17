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
  * if the change touches the shared Phase 4 rollback-ownership and lab-matrix packet, do `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` still agree on the current direct-readback packet, keep the repo-reality warning explicit for the missing broader Phase 4 validator, lab-matrix, and local-only perf companions, keep the host-side artifact-diff contract plus remaining-gap wording truthful, keep the parked kprobe and parked `test_fsmount` reminder packet framed as last-known packet members rather than current direct evidence, keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion, keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call, and keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval?
  * if the change is a reference sample under `samples/zigux/`, is the self-check or behavior replay explicit and small enough to stay reviewable?
  * if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `scripts/zigux/check-phase1-string-review-packet.py`, and `scripts/zigux/check-phase1-direct-owner-markers.py` still agree on the same bounded current-`master` reminder packet: the thirteen-helper owner map, the parked shared-replay-versus-direct-anchor split, the restored closure note, the live string-review and direct-owner guards, the narrow closure validator, and the repo-reality warning that older installer-backed, validator-first, make-route, bench, and replay paths such as `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` stay framed as historical packet members rather than direct current evidence unless a fresh reread materializes them again, without widening Phase 1 beyond the bounded host-side helper packet?
  * if the change touches that same Phase 1 reminder packet, does the checklist still say clearly that `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/validate-phase1-closure.py` replay the bounded live reminder checks, that `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/validate-phase1-closure.py` guard the shipped current-`master` Phase 1 reminder packet, and that `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` remains the narrow shared tests-root closure route while the older installer-companion wording stays historical until those missing companions are directly readable again?
## ABI and Runtime

  * are bindings and ABI assumptions centralized?
  * does the change avoid hidden runtime services, implicit allocation, or unclear panic behavior?
  * if unsafe code exists, is it narrow, visible, and review-owned?
## Product Discipline

  * does the patch make Zigux more buildable, more testable, or more reviewable?
  * if it came from ZAR research, is the transfer rationale explicit?
  * if the target stays in C, does the change record that ongoing policy honestly instead of implying a premature port commitment?
  * does the change strengthen the product repo instead of just extending experimental scope?
## Footer
