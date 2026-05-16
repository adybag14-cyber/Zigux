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
  * current direct-readback Phase 4 rollback packet:
    `Documentation/zigux/phase4-reversible-delivery-evidence.md`
    `Documentation/zigux/review-checklist.md`
    `zigux/tests/README.md`
  * repo-reality warning for the broader Phase 4 packet: the reversible-delivery handoff note currently records that several older Phase 4 validator, lab-matrix, and local-only perf files return missing contents reads on current `master`, including `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig`
  * Phase 4 follow-through should treat those paths as last-known packet members that require fresh reread or re-materialization before they are presented as shipped direct evidence again
  * current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone
  * historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions, the validator-first routes, and the direct local-only perf routes stay owned by the reversible-delivery handoff note until a fresh reread confirms they are directly readable again on current `master`
  * `Documentation/zigux/phase5-kfifo-sample-survey.md`
  * `samples/zigux/bytestream_fifo.zig`
  * `zigux/tests/phase5_bytestream_fifo_manifest.json`
  * current public-tree-backed Phase 5 bytestream companions: `zigux/tests/phase5_bytestream_fifo.zig` and `zigux/tests/phase5_bytestream_fifo_survey.zig`
  * `Documentation/zigux/phase5-kobject-sample-survey.md`
  * `samples/zigux/kobject_example.zig`
  * `zigux/tests/phase5_kobject_example.zig`
  * `zigux/tests/phase5_kobject_example_manifest.json`
  * current public-tree-backed Phase 5 kobject survey companion: `zigux/tests/phase5_kobject_example_survey.zig`
  * `Documentation/zigux/phase5-kretprobe-sample-survey.md`
  * `samples/zigux/kretprobe_example.zig`
  * `zigux/tests/phase5_kretprobe_example.zig`
  * `zigux/tests/phase5_kretprobe_example_manifest.json`
  * `zigux/tests/phase5_kretprobe_example_survey.zig`
  * `Documentation/zigux/phase5-trace-events-sample-survey.md`
  * `samples/zigux/trace_events_sample.zig`
  * `zigux/tests/phase5_trace_events_sample.zig`
  * `zigux/tests/phase5_trace_events_sample_manifest.json`
  * `zigux/tests/phase5_trace_events_sample_survey.zig`
  * current public-tree-backed Phase 5 shared-build companion: `zigux/tests/phase5_build.zig`
  * `zigux/tests/phase1_helpers.zig`
  * `zigux/tests/phase1_bench.zig`
  * `zigux/tests/fixtures/phase1_helper_manifest.json`
  * `zigux/tests/fixtures/phase1_bench_expectations.json`
  * current Phase 1 review-and-replay stack: `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`
  * current public-tree-backed Phase 1 parity packet: `zigux/tests/fixtures/phase1_helpers.json` and `zigux/tests/fixtures/phase1_helpers_c_harness.c`
  * `zigux/tests/phase6_build.zig`
  * `zigux/tests/phase6_helper_parity_manifest.json`
  * `Documentation/zigux/phase6-helper-parity-catalog.md`
  * `Documentation/zigux/phase6-perf-gate-survey.md`
  * `Documentation/zigux/README.md`

Phase 2 review packet
  * `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
  * `Documentation/zigux/phase2-closure.md`
  * `Documentation/zigux/review-checklist.md`
  * `scripts/zigux/README.md`
  * `scripts/zigux/validate-phase2.py`
  * `scripts/zigux/validate-phase2-closure.py`
  * `scripts/zigux/check-phase2-tests-readme-alignment.py`
  * `scripts/zigux/check-phase2-kconfig-readme-alignment.py`
  * `scripts/zigux/check-phase2-tool-manifest-packets.py`
  * `scripts/zigux/check-phase2-toolchain-pin-scope.py`
  * `scripts/zigux/check-genksyms-bridge.py`
  * `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
  * `scripts/zigux/check-phase2-confdata-helper-anchor-alignment.py`
  * `scripts/zigux/check-phase2-fixdep-gate.py`
  * `scripts/zigux/check-kconfig-bridge.py`
  * `scripts/zigux/check-phase2-cross.py`
  * `scripts/zigux/check-phase2-cross-selftest-alignment.py`
  * `zigux/tests/fixtures/phase2_cross_targets.json`
  * `zigux/tests/fixtures/phase2_tool_manifest.json`
  * `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
  * `zigux/tests/fixtures/genksyms_bridge/manifest.json`
  * `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
  * `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
  * `scripts/zigux/kconfig/conf_bridge.zig`
  * `scripts/zigux/kconfig/confdata_bridge.zig`
  * `python3 scripts/zigux/install-zig.py --self-test`
  * `python3 scripts/zigux/check-zig-toolchain.py --self-test`
  * `zig test scripts/zigux/fixdep.zig`
  * `make -C zigux phase2-toolchain`
  * `make -C zigux phase2-validate`
  * `make -C zigux phase2-tools`
  * `make -C zigux phase2-kconfig`
  * `make -C zigux phase2-cross`
  * `make -C zigux phase2`
  * the repo-local `.zig-toolchain` fallback reused by the Linux-style `phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` routes when `ZIG` is unset
  * keep the shipped genksyms bridge direct replay visible in the tests root through the committed fixture packet instead of reviving a direct tests-root replay command

Phase 3 review packet
  * `Documentation/zigux/phase3-abi-slice.md`
  * `Documentation/zigux/phase3-abi-bindings-survey.md`
  * `Documentation/zigux/phase3-bindings-governance.md`
  * `Documentation/zigux/phase3-boundary-lane-sequencing.md`
  * `Documentation/zigux/phase3-export-uapi-boundary-survey.md`
  * `Documentation/zigux/phase3-kernel-export-shim-governance.md`
  * `Documentation/zigux/phase3-linux-zigux-header-governance.md`
  * `Documentation/zigux/phase3-abi-header-family-survey.md`
  * `Documentation/zigux/phase3-abi-h-boundary-next-step.md`
  * `Documentation/zigux/phase3-validator-support-surface.md`
  * `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md`
  * `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`
  * `include/zigux/abi.h`
  * `include/zigux/dev_t.h`
  * `include/linux/zigux.h`
  * `zigux/bindings/abi.zig`
  * `zigux/bindings/dev_t.zig`
  * `zigux/bindings/notifier_abi.zig`
  * `zigux/helpers/layout_assert.zig`
  * `zigux/kernel/export_shim.zig`
  * `zigux/uapi/version.zig`
  * `zigux/uapi/dev_t.zig`
  * `zigux/tests/phase3_abi.zig`
  * `zigux/tests/phase3_abi_dump.zig`
  * `zigux/tests/phase3_export_uapi_layout.zig`
  * `zigux/tests/phase3_export_uapi_layout_build.zig`
  * `zigux/tests/phase3_low_level_wrappers.zig`
  * `zigux/tests/phase3_low_level_wrappers_build.zig`
  * `zigux/tests/fixtures/phase3_abi_manifest.json`
  * `scripts/zigux/validate-phase3.py`
  * `scripts/zigux/validate_phase3_selftest.py`
  * `scripts/zigux/check-phase3-selftest-surface.py`
  * `scripts/zigux/check-phase3-readme-tooling-inventory.py`
  * `scripts/zigux/check-phase3-abi-dump-gate.py`
  * `scripts/zigux/check-phase3-catalog-selftest.py`
  * `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
  * `scripts/zigux/validate-phase3-export-uapi-survey.py`
  * `scripts/zigux/validate-phase3-abi-header-family-survey.py`
  * `scripts/zigux/validate-phase3-validator-support-surface.py`
  * `scripts/zigux/validate-phase3-abi-bindings-syntax.py`
  * `scripts/zigux/survey-phase3-abi-constant-parity.py`
  * `python3 scripts/zigux/validate-phase3.py`
  * `python3 scripts/zigux/validate-phase3.py --slug abi`
  * `python3 scripts/zigux/run-phase3-checks.py --slug abi`
  * `zig build phase3-test --build-file zigux/tests/build.zig`
  * `zig build phase3-dump --build-file zigux/tests/build.zig`
  * `make -C zigux phase3-validate`
  * `make -C zigux phase3-selftest`
  * `make -C zigux phase3`
  * the shared ABI substrate now stays explicit in this tests-root guide through the dedicated ABI-and-bindings survey, the dedicated bindings-governance note, the broader ABI slice note, the adjacent export/UAPI and Linux-facing header-governance notes, the validator-support packet, and the direct `phase3_abi` plus `phase3_abi_dump` replay routes instead of forcing reviewers to reconstruct that packet from the docs root and scripts root alone
  * the focused export/UAPI and low-level-wrapper support routes stay explicit here too: `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`, `make -C zigux phase3-export-uapi-layout-test`, `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`, and `make -C zigux phase3-low-level-wrappers-test`
  * `include/zigux/dev_t.h`, `zigux/uapi/version.zig`, and `zigux/uapi/dev_t.zig` stay explicit as the current starter header-family companion packet rather than implying a broader shipped UAPI family

Phase 7 review packet
  * `Documentation/zigux/phase7-helper-lane-sequencing.md`
  * `Documentation/zigux/phase7-rbtree-slice.md`
  * `scripts/zigux/check-phase7-rbtree-parity.py`
  * `zigux/tests/phase7_rbtree.zig`
  * the dedicated `zigux/tests/phase7_rbtree_survey.zig` survey gate
  * `zigux/tests/phase7_rbtree_manifest.json`
  * `zigux/tests/fixtures/phase7_rbtree.json`
  * `zigux/tests/fixtures/phase7_rbtree_c_harness.c`
  * `zigux/tests/phase7_build.zig`
  * `make -C zigux phase7-validate`
  * `make -C zigux phase7`
  * keep the parked Phase 7 rbtree packet explicit here too: `scripts/zigux/check-phase7-rbtree-parity.py`, the dedicated `zigux/tests/phase7_rbtree_survey.zig` survey gate, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, and the shared `make -C zigux phase7-validate` plus `make -C zigux phase7` replay handles keep the current runtime-safe leaf-helper reminder surface visible without widening into deeper helper-family expansion

Phase 8 review packet
  * `Documentation/zigux/phase8-tooling-lane-sequencing.md`
  * `Documentation/zigux/phase8-help-slice.md`
  * `Documentation/zigux/phase8-kallsyms-slice.md`
  * `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`
  * `Documentation/zigux/phase8-libbpf-segment-survey.md`
  * `scripts/zigux/validate-phase8.py`
  * `scripts/zigux/check-phase8-tests-readme-alignment.py`
  * `scripts/zigux/check-phase8-exec-cmd-packet.py`
  * `scripts/zigux/check-phase8-help-kallsyms-packet.py`
  * `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`
  * `scripts/zigux/check-phase8-libbpf-segment-gate.py`
  * `scripts/zigux/check-phase8-libbpf-shard-routes.py`
  * `zigux/tests/phase8_exec_cmd.zig`
  * `zigux/tests/phase8_exec_cmd_only_build.zig`
  * `zigux/tests/phase8_help.zig`
  * `zigux/tests/phase8_help_only_build.zig`
  * `zigux/tests/phase8_help_kallsyms_only_build.zig`
  * `zigux/tests/phase8_kallsyms.zig`
  * `zigux/tests/phase8_kallsyms_only_build.zig`
  * `zigux/tests/phase8_cpu_mask.zig`
  * `zigux/tests/phase8_cpu_mask_only_build.zig`
  * `zigux/tests/phase8_logging.zig`
  * `zigux/tests/phase8_pin_path.zig`
  * `zigux/tests/phase8_bpf_type_names.zig`
  * `zigux/tests/phase8_file_path_handle_bridge.zig`
  * `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`
  * `zigux/tests/phase8_perf_buffer_poll.zig`
  * `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
  * `zigux/tests/phase8_libbpf_segments.zig`
  * `zigux/tests/phase8_libbpf_segments_only_build.zig`
  * `make -C zigux phase8-validate`
  * `make -C zigux phase8-exec-cmd-test`
  * `make -C zigux phase8-help-test`
  * `make -C zigux phase8-help-kallsyms-test`
  * `make -C zigux phase8-kallsyms-test`
  * `make -C zigux phase8-cpu-mask-test`
  * `make -C zigux phase8-file-path-handle-bridge-test`
  * `make -C zigux phase8-libbpf-segments-test`
  * `make -C zigux phase8-perf-buffer-poll-test`
  * `make -C zigux phase8-test`
  * `make -C zigux phase8`
  * keep the shared Phase 8 tooling packet explicit here too: the focused exec-cmd, help, symbol, cpu-mask, file-path bridge, segmented libbpf, and perf-buffer poll replay surfaces stay reviewable from the tests root without widening into deferred process-launch, handle-ownership, or online-CPU routing work
