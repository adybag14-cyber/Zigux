# zigux/tests

This directory is the home of reusable Zigux parity and differential validation harnesses.

Purpose

  * hold shared harness logic before subsystem-specific tests spread through the tree
  * keep product-facing validation code separate from ad hoc experiments
  * provide the checks for helper parity, ABI assertions, and rollback readiness

Key entrypoints
  * `zigux/tests/build.zig`
  * `zigux/tests/atomic64_diff.zig`
  * `zigux/tests/runtime_atomic64_diff.zig`
  * `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
  * `Documentation/zigux/phase1-closure.md`
  * `Documentation/zigux/review-checklist.md`
  * `Documentation/zigux/README.md`
  * `zigux/tests/fixtures/phase1_helper_manifest.json`
  * `zigux/tests/fixtures/phase1_helpers.json`
  * current direct-readback Phase 1 reminder packet: `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/validate-phase1-closure.py`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
  * repo-reality warning for the broader Phase 1 closure-and-replay packet: repeated authenticated contents reads on current `master` now return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`
  * the restored closure note plus `python3 scripts/zigux/validate-phase1-closure.py` and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` now keep the current closure-side validation route explicit in the tests root instead of leaving that narrower packet implied through docs-root wording alone
  * keep current Phase 1 follow-through tied to the live owner-map, string-review, and closure-validator reminder packet instead of reconstructing the broader validator-first tranche from those older missing closure-side files and routes alone
