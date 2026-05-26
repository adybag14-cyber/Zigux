# zigux/tests

This directory is the home of reusable Zigux parity and differential validation harnesses.

Purpose

  * hold shared harness logic before subsystem-specific tests spread through the tree
  * keep product-facing validation code separate from ad hoc experiments
  * provide the checks for helper parity, ABI assertions, and rollback readiness

## Phase 1 host-tools review packet

  * current direct-readback Phase 1 reminder packet:
- `Documentation/zigux/phase1-closure.md`
- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `scripts/zigux/check-phase1-string-review-packet.py`
- `scripts/zigux/check-phase1-direct-owner-markers.py`
- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`
- `scripts/zigux/check-phase1-bench.py`
- `scripts/zigux/check-phase1-shared-reminder-packet.py`
- `scripts/zigux/validate-phase1-closure.py`
- `zigux/tests/build.zig`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/phase1_helpers_build.zig`
- `zigux/tests/phase1_host_tools_smoke.zig`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `zigux/tests/README.md`

  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
  * current focused Phase 1 helper replay route: `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`
  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof
  * broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet
  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`

## Phase 2 review packet

  * current direct-readback Phase 2 kconfig, genksyms, and fixdep packet:
  * `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
  * `Documentation/zigux/phase2-closure.md`
  * `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`
  * `Documentation/zigux/review-checklist.md`
  * `scripts/zigux/README.md`
  * `scripts/zigux/validate-phase2.py`
  * `scripts/zigux/validate-phase2-closure.py`
  * `scripts/zigux/check-zig-toolchain.py`
  * `scripts/zigux/check-phase2-kbuild-routes.py`
  * `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
  * `scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`
  * `scripts/zigux/check-kconfig-bridge.py`
  * current shared Phase 2 kconfig route: `make -C zigux phase2-kconfig`
  * `scripts/zigux/check-phase2-tests-readme-alignment.py`
  * `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`
  * `scripts/zigux/check-phase2-cross-selftest-alignment.py`
  * `scripts/zigux/check-phase2-toolchain-pinning.py`
  * `scripts/zigux/check-phase2-toolchain-pin-scope.py`
  * `scripts/zigux/check-phase2-docs-shared-reminder.py`
  * `scripts/zigux/check-phase2-tool-manifest.py`
  * `scripts/zigux/check-phase2-artifact-tools-manifest.py`
  * `scripts/zigux/check-phase2-required-make-routes.py`
  * `scripts/zigux/check-genksyms-bridge.py`
  * `scripts/zigux/check-phase2-fixdep-gate.py`
  * `scripts/zigux/check-fixdep-diff.py`
  * `scripts/zigux/install-zig.py`
  * `scripts/zigux/check-phase2-cross.py`
  * `python3 scripts/zigux/check-zig-toolchain.py --self-test`
  * `python3 scripts/zigux/check-zig-toolchain.py --policy-only`
  * `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`
  * `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
  * `python3 scripts/zigux/install-zig.py --self-test`
  * `python3 scripts/zigux/check-phase2-cross.py --self-test`
  * Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.
  * `third_party/README.md`
  * `.github/workflows/zigux-bootstrap.yml`
  * `scripts/zigux/check-lane05-local-first-archive-workflow.py`
  * `scripts/zigux/check-lane05-local-archive-readme.py`
  * current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`, so keep that returned repo-local pinned-archive workflow, bootstrap guard, and archive README contract explicit here instead of leaving them outside the tests-root reminder
  * keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`, and the local-first `third_party`, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers
  * keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.
  * `scripts/zigux/kconfig/conf_bridge.zig`
  * `scripts/zigux/kconfig/confdata_bridge.zig`
  * `scripts/zigux/genksyms.zig`
  * `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`
  * `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`
  * `scripts/zigux/fixdep.zig`
  * `scripts/zigux/zig-toolchain-policy.json`
  * `zigux/Makefile`
  * `zigux/tests/fixtures/phase2_tool_manifest.json`
  * `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
  * `zigux/tests/fixtures/phase2_cross_targets.json`
  * `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
  * `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
  * Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.
  * `make -C zigux phase2-toolchain`
  * `make -C zigux phase2-tools`
  * `make -C zigux phase2-kconfig`
  * `make -C zigux phase2-cross`
  * `make -C zigux phase2-genksyms`
  * `make -C zigux phase2-fixdep`
  * `make -C zigux phase2-validate`
  * `make -C zigux phase2`
  * `zigux/tests/fixtures/kconfig_bridge/cases.json`
  * `zigux/tests/fixtures/genksyms_bridge/cases.json`
  * `zigux/tests/fixtures/genksyms_bridge/manifest.json`
  * `zigux/tests/fixtures/genksyms_bridge/help_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json`
  * `zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json`
  * `zigux/tests/fixtures/fixdep/cases.json`
  * the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, toolchain reminder, helper-local kconfig allconfig guard, kconfig bridge checker, the dedicated genksyms survey, selftest-alignment guard, bridge helper, and standalone version-side-effect proofs, fixdep governance and parity set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster
  * keep `scripts/zigux/zig-toolchain-policy.json`, the pinned `x86_64-linux` bootstrap archive note, the live `python3 scripts/zigux/check-zig-toolchain.py --policy-only` plus `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replays, and the repo-local `.zig-toolchain` fallback reused by the surviving `scripts/zigux/check-zig-toolchain.py` and pin-scope guards explicit in this tests-root packet
  * current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket
  * current `master` also directly materializes `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned survey, selftest-alignment, checker, bridge helper, standalone proof, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder
  * current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder
  * keep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target, helper-local kconfig allconfig, the survey-backed genksyms packet, and fixdep packet visible in the tests root without reviving missing validator-first or make-wrapper proof text

## Phase 7 leaf-library packet

  * current direct-readback Phase 7 leaf-library packet:
  * `Documentation/zigux/phase7-leaf-library-evidence-catalog.md`
  * `Documentation/zigux/README.md`
  * `Documentation/zigux/review-checklist.md`
  * `scripts/zigux/README.md`
  * `scripts/zigux/check-phase7-shared-surface.py`
  * `scripts/zigux/check-phase7-build-wiring.py`
  * `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
  * `scripts/zigux/check-phase7-argv-split-packet.py`
  * `scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`
  * `scripts/zigux/validate-phase7.py`
  * `zigux/tests/phase7_leaf_library_evidence_manifest.json`
  * `zigux/tests/phase7_build.zig`
  * `zigux/Makefile`
  * `lib/string_helpers.zig`
  * `lib/cmdline.zig`
  * `lib/argv_split.zig`
  * `lib/rbtree.zig`
  * Keep the validator-first reminder packet explicit too: `python3 scripts/zigux/check-phase7-shared-surface.py`, `python3 scripts/zigux/check-phase7-build-wiring.py`, `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `python3 scripts/zigux/check-phase7-argv-split-packet.py`, `python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`, `python3 scripts/zigux/validate-phase7.py`, and `make -C zigux phase7-validate` remain the shipped bounded replay surfaces, and `zigux/Makefile` still keeps only the narrow `phase7-validate` foothold explicit rather than a broader wrapper family.
