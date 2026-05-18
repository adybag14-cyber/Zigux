# zigux/tests

This directory is the home of reusable Zigux parity and differential validation harnesses.

Purpose

  * hold shared harness logic before subsystem-specific tests spread through the tree
  * keep product-facing validation code separate from ad hoc experiments
  * provide the checks for helper parity, ABI assertions, and rollback readiness

Key entrypoints
  * `zigux/tests/build.zig`
  * current direct-readback Phase 1 reminder packet:
    `Documentation/zigux/phase1-closure.md`
    `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
    `Documentation/zigux/review-checklist.md`
    `scripts/zigux/README.md`
    `scripts/zigux/validate-phase1-closure.py`
    `scripts/zigux/check-phase1-string-review-packet.py`
    `scripts/zigux/check-phase1-direct-owner-markers.py`
    `scripts/zigux/check-phase1-bench.py`
    `zigux/tests/fixtures/phase1_helper_manifest.json`
  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
  * repo-reality warning for the broader historical Phase 1 validator-first, bench, and replay stack: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`
  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 8, Phase 10, and Phase 12 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof
  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`
  * current direct-readback Phase 2 kconfig bridge packet:
    `Documentation/zigux/review-checklist.md`
    `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
    `scripts/zigux/kconfig/conf_bridge.zig`
    `scripts/zigux/kconfig/confdata_bridge.zig`
    `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
    `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
  * current shared Phase 2 kconfig route: `make -C zigux phase2-kconfig`
  * Phase 2 review packet:
    `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
    `Documentation/zigux/phase2-closure.md`
    `Documentation/zigux/review-checklist.md`
    `scripts/zigux/README.md`
    `scripts/zigux/validate-phase2.py`
    `scripts/zigux/validate-phase2-closure.py`
    `scripts/zigux/check-zig-toolchain.py`
    `scripts/zigux/check-phase2-kbuild-routes.py`
    `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
    `scripts/zigux/check-phase2-tests-readme-alignment.py`
    `scripts/zigux/check-phase2-cross-selftest-alignment.py`
    `scripts/zigux/check-phase2-toolchain-pinning.py`
    `scripts/zigux/check-phase2-toolchain-pin-scope.py`
    `scripts/zigux/check-phase2-docs-shared-reminder.py`
    `scripts/zigux/check-phase2-required-make-routes.py`
    `python3 scripts/zigux/check-zig-toolchain.py --self-test`
    `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`
    `scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
    `scripts/zigux/kconfig/conf_bridge.zig`
    `scripts/zigux/kconfig/confdata_bridge.zig`
    `zigux/Makefile`
    `zigux/tests/fixtures/phase2_tool_manifest.json`
    `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
    `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
    `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
    `make -C zigux phase2-toolchain`
    `make -C zigux phase2-tools`
    `make -C zigux phase2-kconfig`
    `make -C zigux phase2-cross`
    `make -C zigux phase2-validate`
    `make -C zigux phase2`
    `zigux/tests/fixtures/kconfig_bridge/cases.json`
  * the current directly readable Phase 2 packet is the scripts-root kbuild, cross-selftest, docs-shared-reminder, required-make-route, and toolchain reminder set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, and closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster
  * keep `scripts/zigux/zig-toolchain-policy.json`, the pinned `x86_64-linux` bootstrap archive note, the live `python3 scripts/zigux/check-zig-toolchain.py --policy-only` plus `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replays, and the repo-local `.zig-toolchain` fallback reused by the surviving `scripts/zigux/check-zig-toolchain.py` and pin-scope guards explicit in this tests-root packet
  * repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep those older installer and direct cross-route names framed as historical packet members rather than direct tests-root evidence
  * keep the fixture-backed tool-manifest, artifact-tools, and kconfig bridge packet visible in the tests root without reviving missing validator-first or make-wrapper proof text
