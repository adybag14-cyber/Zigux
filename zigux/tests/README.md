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
  * broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet
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
  * `zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json`
  * `zigux/tests/fixtures/fixdep/cases.json`
  * the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, toolchain reminder, helper-local kconfig allconfig guard, kconfig bridge checker, the dedicated genksyms survey, selftest-alignment guard, bridge helper, and standalone version-side-effect proofs, fixdep governance and parity set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster
  * keep `scripts/zigux/zig-toolchain-policy.json`, the pinned `x86_64-linux` bootstrap archive note, the live `python3 scripts/zigux/check-zig-toolchain.py --policy-only` plus `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replays, and the repo-local `.zig-toolchain` fallback reused by the surviving `scripts/zigux/check-zig-toolchain.py` and pin-scope guards explicit in this tests-root packet
  * current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket
  * current `master` also directly materializes `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned survey, selftest-alignment, checker, bridge helper, standalone proof, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder
  * current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder
  * keep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target, helper-local kconfig allconfig, the survey-backed genksyms packet, and fixdep packet visible in the tests root without reviving missing validator-first or make-wrapper proof text

## Phase 4 rollback-ownership and lab-matrix packet

  * current direct-readback Phase 4 shared handoff:
  * `Documentation/zigux/phase4-reversible-delivery-evidence.md`
  * `Documentation/zigux/README.md`
  * `Documentation/zigux/review-checklist.md`
  * `scripts/zigux/README.md`
  * `scripts/zigux/check-phase4-repo-reality-warning.py`
  * `scripts/zigux/check-phase4-tests-readme-packet.py`
  * `scripts/zigux/check-phase4-reversible-delivery-pins.py`
  * `zigux/tests/README.md`
  * keep the directly readable local-only perf packet explicit through `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-perf-threshold-matrix.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and `make -C zigux phase4-perf-baseline-survey`
  * keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, and `scripts/zigux/validate-phase4.py`
  * keep the roadmap-backed direct differential pair explicit through `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`
  * keep the broader validator-plus-bitmap replay packet visible too: `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` remain part of the current Phase 4 review surface even while same-route authenticated blob refresh stays narrower than the rollback-owner packet itself
  * keep the parked sample-gap packets explicit too: `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, `zigux/tests/phase4_kprobe_example_survey.zig`, `Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig`
  * keep `Validation and Perf Team` as the decision owner for any shared-CI perf promotion, with `ABI and Runtime Team` plus `Shared Subsystems Pod` as coordination owners, while `Documentation/zigux/phase4-validation-matrix.md` remains the rollback-owner source for the landed atomic64 and bitmap gates

## Phase 7 leaf-library packet

  * current direct-readback Phase 7 leaf-library packet:
  * `Documentation/zigux/phase7-leaf-library-evidence-catalog.md`
  * `Documentation/zigux/README.md`
  * `Documentation/zigux/review-checklist.md`
  * `scripts/zigux/README.md`
  * `scripts/zigux/check-phase7-shared-surface.py`
  * `scripts/zigux/check-phase7-build-wiring.py`
  * `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
  * `scripts/zigux/check-phase7-cmdline-packet.py`
  * `scripts/zigux/check-phase7-argv-split-packet.py`
  * `scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`
  * `scripts/zigux/check-phase7-rbtree-parity.py`
  * `scripts/zigux/validate-phase7.py`
  * `zigux/tests/phase7_leaf_library_evidence_manifest.json`
  * `zigux/tests/phase7_build.zig`
  * `zigux/Makefile`
  * `lib/string_helpers.zig`
  * `lib/cmdline.zig`
  * `lib/argv_split.zig`
  * `lib/rbtree.zig`
  * Keep the validator-first reminder packet explicit too: `python3 scripts/zigux/check-phase7-shared-surface.py`, `python3 scripts/zigux/check-phase7-build-wiring.py`, `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `python3 scripts/zigux/check-phase7-cmdline-packet.py`, `python3 scripts/zigux/check-phase7-argv-split-packet.py`, `python3 scripts/zigux/check-phase7-string-helpers-format-boundary-packet.py`, `python3 scripts/zigux/check-phase7-rbtree-parity.py`, `python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test`, `python3 scripts/zigux/validate-phase7.py`, `python3 scripts/zigux/validate-phase7.py --self-test`, and `make -C zigux phase7-validate` remain the shipped bounded replay surfaces, and `zigux/Makefile` still keeps only the narrow `phase7-validate` foothold explicit rather than a broader wrapper family.

## Phase 8 tooling packet

  * current direct-readback Phase 8 anchors:
  * `scripts/zigux/check-phase8-tests-readme-alignment.py`
  * `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`
  * `scripts/zigux/validate-phase8.py`
  * `zigux/tests/phase8_exec_cmd.zig`
  * `zigux/tests/phase8_exec_cmd_only_build.zig`
  * `zigux/tests/phase8_perf_buffer_poll.zig`
  * `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
  * Keep the currently returned help-and-kallsyms focused packet explicit too; current `master` now rematerializes the dedicated shard files and their route-level companions even though the broader note still treats them as public-tree-backed companion evidence:
  * `Documentation/zigux/phase8-help-slice.md`
  * `Documentation/zigux/phase8-kallsyms-slice.md`
  * `zigux/tests/phase8_help_only_build.zig`
  * `zigux/tests/phase8_help_kallsyms_only_build.zig`
  * `zigux/tests/phase8_kallsyms_only_build.zig`
  * `make -C zigux phase8-help-test`
  * `make -C zigux phase8-help-kallsyms-test`
  * `make -C zigux phase8-kallsyms-test`
  * current mixed-source file-path-handle bridge companions also remain reviewable on current `master` through the public tree and aligned reminder packet:
  * `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`
  * `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`
  * `scripts/zigux/validate-phase8.py`
  * `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
  * `zigux/tests/phase8_file_path_handle_bridge.zig`
  * `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`
  * `zigux/tests/phase8_file_path_handle_boundary_guard.zig`
  * `zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`
  * `zigux/tests/phase8_build.zig`
  * `make -C zigux phase8-exec-cmd-test`
  * `make -C zigux phase8-file-path-handle-bridge-test`
  * current `zigux/tests/phase8_build.zig` also keeps the landed boundary-guard and manifest-sync witnesses inside the shared aggregate replay, so this tests-root reminder should treat both checks as current current-`master` evidence instead of leaving them implied only by the aggregate build route
  * repo-reality warning for the broader remaining Phase 8 tooling packet:
  * `Documentation/zigux/phase8-libbpf-segment-survey.md`
  * `Documentation/zigux/phase8-perf-buffer-poll-slice.md`
  * `Documentation/zigux/phase8-tooling-lane-sequencing.md`
  * `Documentation/zigux/phase8-help-slice.md`
  * `Documentation/zigux/phase8-kallsyms-slice.md`
  * `tools/lib/bpf/zigux_segments/verify.zig`
  * `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`
  * `zigux/tests/phase8_help_kallsyms_only_build.zig`
  * `zigux/tests/phase8_verify_routing_gap.zig`
  * `zigux/tests/phase8_verify_routing_gap_only_build.zig`
  * `zigux/tests/phase8_libbpf_segments.zig`
  * `zigux/tests/phase8_libbpf_segments_only_build.zig`
  * `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
  * `zigux/Makefile`
  * `make -C zigux phase8-help-kallsyms-test`
  * `make -C zigux phase8-libbpf-segments-test`
  * `make -C zigux phase8-perf-buffer-poll-test`
  * `make -C zigux phase8-test`
  * keep the narrower current Phase 8 reminder tied to the directly readable tests-readme checker plus the surviving perf-buffer poll checker, helper, and focused test packet, while also keeping the landed mixed-source file-path-handle bridge packet visible through the shared bridge-boundary survey, bridge slice, validator entrypoint, focused bridge proof, and helper-local replay instead of treating that same-lane bridge surface as missing current-master evidence
  * current public-tree rereads now rematerialize the broader help, kallsyms, and libbpf-segment companions on `master`, so treat those returned paths as public-tree-backed broader packet evidence rather than as part of the narrow direct-readback anchor set
  * if future same-lane work rematerializes the remaining broader docs, focused perf-buffer build shard, shared libbpf segment replay, or Makefile routes, or changes the focused bridge shard, the shared build replay, or the libbpf segment review packet, refresh this tests-root summary only after rereading the current direct-readback anchors together with the mixed-source file-path-handle bridge packet on current `master`

## Phase 9 runtime pilot packet

  * current direct-readback Phase 9 reminder packet:
  * `Documentation/zigux/freeze-map.md`
  * `Documentation/zigux/phase15-study-only-anchor-accounting.md`
  * `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
  * `Documentation/zigux/review-checklist.md`
  * `Documentation/zigux/README.md`
  * `scripts/zigux/README.md`
  * `samples/zigux/README.md`
  * `zigux/tests/README.md`
  * `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`
  * `scripts/zigux/check-phase9-trace-events-runtime-packet.py`
  * `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`
  * `zigux/tests/phase9_build.zig`
  * `zigux/tests/runtime_trace_events_manifest.json`
  * `zigux/tests/runtime_trace_events_survey.zig`
  * `zigux/tests/runtime_loader_allocator_init_flow.zig`
  * `zigux/tests/runtime_bitmap_manifest.json`
  * `zigux/tests/runtime_bitmap_survey.zig`
  * `zigux/tests/runtime_bitmap_module.zig`
  * `zigux/tests/runtime_bitmap_diff.zig`
  * `zigux/tests/runtime_kretprobe_survey.zig`
  * `zigux/tests/runtime_kretprobe_module.zig`
  * `zigux/tests/runtime_first_loadable_parity_behavior.zig`
  * keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than runtime-substrate readiness proof in the tests root
  * keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`, `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`, `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` remain the current shipped runtime-pilot proof rather than a claim that broader runtime-loader or publication boundaries are solved
  * keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-shared-tests`, and `phase9-runtime-loader-command-env-boundary-guard-tests` routes, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata surfaces are complete
  * keep the bounded runtime bitmap reminder packet distinct from that returned loader shard too: `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-bitmap-tests` plus `phase9-runtime-bitmap-cold-stage-guard-tests` routes are the current bitmap-side evidence packet, but they still must not be used to imply that the broader shared runtime-loader packet or blocked publication boundaries returned
  * keep the returned runtime kretprobe pilot packet distinct from those shared loader and bitmap reminders too: `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`, `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_first_loadable_parity_behavior.zig`, and the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-loader-tests`, `phase9-runtime-kretprobe-initialized-snapshot-guard-tests`, `phase9-runtime-kretprobe-registration-reentry-gate-tests`, `phase9-runtime-kretprobe-survey-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-tests`, and `phase9-first-loadable-runtime-module-parity-behavior-tests` routes are current family-local pilot evidence, but they still must not be used to imply that the broader shared runtime-loader packet, blocked publication boundaries, or install-root surfaces are complete
  * keep the bounded Phase 9 build bundle explicit as rerun vocabulary only: `zigux/tests/phase9_build.zig` now reruns the atomic64 diff shard, the runtime bitmap sample, survey, module, diff, loader, and top-bit companion packet members, the shared loader allocator/init-flow shard, the shared loader command/environment boundary guard, the shared trace-events loader-substrate-drift shard, the returned runtime kretprobe sample, loader, initialized-snapshot guard, registration-reentry companion, survey, and module shards, and the first-loadable parity-behavior handle, but that build bundle is still not proof that blocked publication boundaries, install-root surfaces, or broader shared runtime-loader completion returned
  * keep the older `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_gap_survey.zig`, and `samples/zigux/runtime_trace_events_loader.zig` names framed as historical wider-family vocabulary rather than current direct-readback tests-root proof

## Phase 10 shared virtio closure packet

Keep `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, and `scripts/zigux/check-phase10-tests-readme-core-surfaces.py` explicit as the shared Phase 10 tests-root reminder packet.

Keep the returned checker-backed build gate explicit through `scripts/zigux/check-phase10-bootstrap-route.py`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/validate-phase10-closure.py`, `zigux/tests/phase10_closure_manifest.json`, and `zigux/tests/phase10_build.zig` so the tests-root reminder stays aligned with the same bounded closure packet already named by the docs root, the lane-sequencing note, the shared review companion, and the scripts-root Phase 10 packet.

The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`.

Current `master` does materialize `zigux/Makefile`, and its live body now exposes the dedicated `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` routes, so keep the returned file and those returned Phase 10 route names explicit as the shared build gate instead of treating them as repo-reality gaps.

Keep the bounded input packet explicit too through `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, `zigux/tests/phase10_virtio_input_manifest.json`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_probe_preflight.zig`, `drivers/virtio/virtio_input_queue_callback_preflight.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, `drivers/virtio/virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_status_drain.zig`, `drivers/virtio/virtio_input_teardown_observation.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, and `zigux/tests/phase10_virtio_input_survey.zig` so the tests-root reminder stays aligned with the same bounded input packet already carried by the survey, slice, module-slice, checker, closure manifest, and shared build gate instead of collapsing it back into core-only closure wording.

Keep the queue-callback-preflight, registration-preflight, status-drain, and teardown-observation replays explicit here so the current tests-root packet still records queue-readiness ordering, registration blockers, in-memory status reclamation, and teardown-reset parity without widening into input registration lifecycle closure, transport callbacks, IRQ delivery, or DMA behavior.

Keep the helper-local MMIO replay pair explicit too through `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig` and `zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig` so the landed apply-observation shard stays reviewable beside `Documentation/zigux/phase10-virtio-mmio-survey.md`, `Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, and `scripts/zigux/check-phase10-mmio-packet.py` without widening into lifecycle, IRQ-delivery, or DMA claims.

## Phase 12 shared release packet

  * current direct-readback Phase 12 reminder packet:
  * `Documentation/zigux/phase12-release-sequencing.md`
  * `Documentation/zigux/phase12-release-readiness-survey.md`
  * `Documentation/zigux/phase12-release-closure-checklist.md`
  * `Documentation/zigux/phase12-release-coordination-matrix.md`
  * `Documentation/zigux/phase12-raw-github-coverage-survey.md`
  * `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
  * `Documentation/zigux/phase12-cross-compile-smoke.md`
  * `Documentation/zigux/review-checklist.md`
  * `scripts/zigux/README.md`
  * `scripts/zigux/check-build-only-phase12-surface.py`
  * `scripts/zigux/check-phase12-release-readiness-packet.py`
  * `scripts/zigux/check-phase12-complex-driver-lane-packet.py`
  * `scripts/zigux/check-phase12-cross-compile-smoke.py`
  * `scripts/zigux/check-phase12-libbpf-snapshot.py`
  * `scripts/zigux/check-phase12-libbpf-lane-marker.py`
  * `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`
  * `scripts/zigux/validate-phase12.py`
  * `zigux/tests/phase12_build.zig`
  * `.github/workflows/zigux-bootstrap.yml`
  * `zigux/Makefile`
  * `zigux/tests/README.md`
  * Keep the directly readable validator-first support bundle explicit too: `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, `scripts/zigux/check-phase12-cross-compile-smoke.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, `scripts/zigux/check-phase12-libbpf-lane-marker.py`, `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the current shared build gate explicit from the tests root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` remain shipped wrapper evidence on current `master`.
  * Keep the active shared build packet explicit too: `zigux/tests/phase12_build.zig` keeps `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` wired through the shared `smoke` and `test` route, so keep that six-file `virtio_net` packet explicit instead of widening it into deeper queue, DMA, throughput, or recovery claims.
  * Keep the adjacent driver-local split explicit too: `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, and `zigux/tests/phase12_virtio_scsi_survey_build.zig` stay the rollback-lab `virtio_scsi` packet outside the shared route, `Documentation/zigux/phase12-nvme-pci-survey.md` plus `zigux/tests/phase12_nvme_pci_manifest.json` stay the bounded driver-local NVMe foothold, and `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` keep the parked libbpf packet explicit without promoting any of them into shared build outputs.
  * Tests-root reviewer prompt:
  * Does the bounded Phase 12 reminder keep the returned validator-first support bundle, the shipped `phase12-validate` / `phase12-smoke` / `phase12-test` / `phase12` wrapper set, the six-file shared `virtio_net` packet, the rollback-lab `virtio_scsi` split including `zigux/tests/phase12_virtio_scsi_survey_build.zig`, the bounded NVMe foothold, and the parked libbpf snapshot-and-lane-marker packet aligned without widening into DMA, queue ownership, throughput, recovery, or deeper transport claims?