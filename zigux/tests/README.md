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
- `scripts/zigux/check-phase1-bench.py`
- `scripts/zigux/check-phase1-shared-reminder-packet.py`
- `scripts/zigux/validate-phase1-closure.py`
- `zigux/tests/build.zig`
- `zigux/tests/phase1_host_tools_smoke.zig`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `zigux/tests/README.md`

  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof
  * broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet
  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`

Tests-root reviewer prompt:
- Does the bounded Phase 1 reminder keep the restored closure note, the workflow-backed closure-validator and shipped checker packet, the shared tests-root smoke route, the manifest-backed owner map, the broader-companion wording for the validator-first, parity, bench-replay, and helper-replay family, and the historical-gap wording for the missing Phase 1 Makefile routes aligned without widening back into the older full closure stack?

## Phase 2 review packet

Keep the current direct-readback Phase 2 kconfig, genksyms, and fixdep packet:

- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`
- `scripts/zigux/check-kconfig-bridge.py`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/check-phase2-docs-shared-reminder.py`
- `scripts/zigux/check-phase2-tool-manifest.py`
- `scripts/zigux/check-phase2-artifact-tools-manifest.py`
- `scripts/zigux/check-phase2-required-make-routes.py`
- `scripts/zigux/check-genksyms-bridge.py`
- `scripts/zigux/check-phase2-fixdep-gate.py`
- `scripts/zigux/check-fixdep-diff.py`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`
- `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`
- `scripts/zigux/fixdep.zig`
- `scripts/zigux/zig-toolchain-policy.json`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`
- `zigux/tests/fixtures/genksyms_bridge/cases.json`
- `zigux/tests/fixtures/genksyms_bridge/manifest.json`
- `zigux/tests/fixtures/genksyms_bridge/help_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json`
- `zigux/tests/fixtures/fixdep/cases.json`

Keep the current shared Phase 2 kconfig route: `make -C zigux phase2-kconfig`

Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.

Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.

current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`, so keep that returned repo-local pinned-archive workflow, bootstrap guard, and archive README contract explicit here instead of leaving them outside the tests-root reminder

keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`, and the local-first `third_party`, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers

keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.

current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof

the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, toolchain reminder, helper-local kconfig allconfig guard, kconfig bridge checker, the dedicated genksyms survey, selftest-alignment guard, bridge helper, and standalone version-side-effect proofs, fixdep governance and parity set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster

keep `scripts/zigux/zig-toolchain-policy.json`, the pinned `x86_64-linux` bootstrap archive note, the live `python3 scripts/zigux/check-zig-toolchain.py --policy-only` plus `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replays, and the repo-local `.zig-toolchain` fallback reused by the surviving `scripts/zigux/check-zig-toolchain.py` and pin-scope guards explicit in this tests-root packet

current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket

current `master` also directly materializes `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned survey, selftest-alignment, checker, bridge helper, standalone proof, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder

current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder

keep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target, helper-local kconfig allconfig, the survey-backed genksyms packet, and fixdep packet visible in the tests root without reviving missing validator-first or make-wrapper proof text

Tests-root reviewer prompt:
- Does the bounded Phase 2 reminder keep the current direct-readback toolchain self-check, repo-local archive workflow, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, validator, closure-validator, helper-local kconfig allconfig guard, kconfig bridge, genksyms bridge, fixdep packet, make-wrapper, and fixture packet aligned without reviving older missing validator-first or wrapper-only proof?


## Phase 3 ABI substrate packet

Keep the current bounded Phase 3 tests-root reminder explicit through `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, `Documentation/zigux/phase3-policy-slice.md`, `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `Documentation/zigux/phase3-validator-support-surface.md`, and `zigux/tests/README.md`.

Keep the returned ABI header and binding boundary packet explicit through `include/linux/zigux.h`, `include/zigux/dev_t.h`, `include/zigux/abi.h`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `zigux/bindings/dev_t.zig`, and `zigux/bindings/abi.zig`.

Keep the focused helper and starter packet explicit through `zigux/helpers/err_ptr.zig`, `zigux/helpers/xa_value.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/unsafe_policy.zig`, `zigux/tests/phase3_dev_t_starter_packet.zig`, `zigux/tests/phase3_dev_t_starter_packet_build.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`, `zigux/tests/phase3_xarray_slot_starter_packet.zig`, `zigux/tests/phase3_policy_starter_packet.zig`, `zigux/tests/phase3_policy_starter_packet_build.zig`, and `zigux/tests/phase3_policy_starter_packet_manifest.json`.

Keep the narrow replay and checker packet explicit through `zigux/tests/phase3_low_level_wrappers.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, `scripts/zigux/check-phase3-dev-t-starter-packet.py`, `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`, `scripts/zigux/check-phase3-policy-starter-packet.py`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, and `zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig`.

keep the returned notifier-binding and focused export/UAPI layout replay pair explicit here instead of leaving `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, and `zigux/tests/phase3_export_uapi_layout_build.zig` framed as broader repo-reality gaps

Keep the current same-lane helper follow-through explicit too: `Documentation/zigux/phase3-bitmap-cpumask-slice.md`, `zigux/helpers/bitmap_view.zig`, `zigux/helpers/cpumask_view.zig`, `zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`, `zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`, `Documentation/zigux/phase3-list-hlist-slice.md`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `zigux/tests/phase3_list_hlist_starter_packet.zig`, and `zigux/tests/phase3_list_hlist_starter_packet_build.zig`.

Keep the direct rerun surface explicit through `zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`, `zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig`, `make -C zigux phase3-export-uapi-layout-test`, and `zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig`.

Keep the broader validator, manifest, and replay-family boundary truthful: keep `scripts/zigux/validate-phase3.py`, `zigux/tests/fixtures/phase3_abi_manifest.json`, `zigux/tests/phase3_export_uapi_c_header_smoke.c`, and `python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py` reviewable as same-lane companions instead of presenting the broader validator, export/UAPI layout, low-level-wrapper, catalog, IDR, or IDA packet as shipped tests-root evidence.

Tests-root reviewer prompt:
- Does the bounded Phase 3 reminder keep the direct helper, starter, policy, low-level-wrapper, bitmap/cpumask, list/hlist, and export/UAPI layout packet aligned without widening into the broader shared validator, catalog, or replay family?

## Phase 5 sample packet

Keep the current bounded Phase 5 tests-root reminder packet explicit through `Documentation/zigux/README.md`, `Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `Documentation/zigux/phase5-kobject-sample-survey.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-trace-events-sample-survey.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase5-review-guide-surface.py`, and `zigux/tests/README.md`.

Keep `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig` explicit as the direct bytestream replay, manifest, and survey packet while `zigux/tests/phase5_build.zig` stays current directly readable shared build-route companion evidence in this runtime.

Keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit as the shipped guide-surface guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording instead of treating the Phase 5 tests-root packet as docs-only guidance.

Keep `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig` explicit as the direct non-runtime kretprobe tests-root packet, and keep `samples/zigux/trace_events_string_formatting_sample.zig` framed only as the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample. Keep `Documentation/zigux/phase5-trace-events-sample-survey.md` explicit with the shared Phase 5 reminder packet as the directly readable survey note for that anchor, while `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` stay framed as public-tree-backed companion or repo-reality-gap references until a fresh authenticated reread returns that broader four-file trace-events packet directly again.

Keep the current kobject split explicit too: `zigux/tests/phase5_kobject_example.zig` is direct tests-root packet evidence again, `samples/zigux/kobject_example_attr_group_contract.zig` stays explicit as the direct sample-root companion for the bounded `foo`/`baz`/`bar` attribute-group contract plus the shared `0664`, unnamed-group, and NULL-terminated attribute-list cues, keep `zigux/tests/phase5_build.zig` explicit as the current directly readable shared build-route companion for that packet, while `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those routes directly again.

Keep `samples/zigux/runtime_*.zig` plus standalone `*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of this non-runtime Phase 5 tests-root packet.

Tests-root reviewer prompt:
- Does the bounded Phase 5 reminder keep the direct bytestream and non-runtime kretprobe tests-root packet, the bounded trace-events formatting companion plus the directly readable trace-events survey note, the mixed kobject split, the shipped guide-surface guard, and the no-extra-sample boundary aligned without widening into runtime samples, module registration, or a fifth sample claim?

## Phase 6 leaf-helper packet

Keep the current bounded Phase 6 tests-root reminder packet explicit through `Documentation/zigux/README.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `scripts/zigux/check-phase6-present-entrypoints.py`, `scripts/zigux/validate-phase6.py`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `zigux/tests/README.md`.

Keep the directly readable helper packet explicit too: `lib/base64.zig`, `lib/bsearch.zig`, `lib/checksum.zig`, and `lib/hexdump.zig` are the current roadmap-backed Phase 6 anchors on `master`, while the shared tests-root note should stay bounded to helper-evidence, parity, and perf-route coverage rather than restating helper-local semantics.

Keep the focused tests and perf packet explicit too: `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_perf.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/phase6_checksum_perf_matrix_test.zig`, `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/phase6_hexdump_perf_matrix.zig`, and `zigux/tests/fixtures/phase6_{base64,bsearch,checksum,hexdump}_vectors.zig` keep the helper-local replay family reviewable from the tests root without widening this reminder into helper implementation discussion.

Keep the shared replay and validator-first packet explicit too: `python3 scripts/zigux/check-phase6-shared-surface.py --self-test`, `python3 scripts/zigux/check-phase6-present-entrypoints.py --self-test`, `python3 scripts/zigux/validate-phase6.py`, `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`, `zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig`, `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`, `zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe`, and `make -C zigux phase6-perf` remain the shipped bounded replay surfaces, while `zigux/Makefile` keeps the current wrapper family explicit beside the shared manifests and build foothold.

Keep the remaining direct-readback boundary explicit too: `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig` and `zigux/tests/phase6_base64_c_casegen.zig` stay recorded as broader current-repo gaps until a fresh authenticated reread returns those generator-side base64 parity companions directly again.

Tests-root reviewer prompt:
- Does the bounded Phase 6 reminder keep the returned helper-anchor set, the focused helper-and-perf replay family, the shared manifests and build graph, the validator-first guard packet, the shared `phase6-perf` rerun surface, and the narrower generator-side base64 parity gap aligned without widening into helper semantics or treating the still-missing generator companions as shipped tests-root evidence?

## Phase 7 leaf-library packet

Keep the current bounded Phase 7 tests-root reminder packet explicit through `Documentation/zigux/phase7-leaf-library-evidence-catalog.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase7-shared-surface.py`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-argv-split-packet.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_leaf_library_evidence_manifest.json`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, `lib/rbtree.zig`, and `zigux/tests/README.md`.

Keep the directly readable helper packet explicit too: `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, and `lib/rbtree.zig` are the current roadmap-backed Phase 7 anchors on `master`, while the shared tests-root note should stay bounded to reminder and replay coverage rather than restating helper-local semantics.

Keep the shared build-wiring packet explicit too: `zigux/tests/phase7_build.zig` wires the four helpers through the dedicated `phase7-string-helpers-test`, `phase7-string-helpers-survey`, `phase7-string-helpers-sample-boundary`, `phase7-cmdline-test`, `phase7-cmdline-survey`, `phase7-argv-split-test`, `phase7-argv-split-survey`, `phase7-rbtree-test`, and `phase7-rbtree-survey` routes, while the shared `test` step aggregates those helper, survey, and sample-boundary replays.

Keep the validator-first reminder packet explicit too: `python3 scripts/zigux/check-phase7-shared-surface.py`, `python3 scripts/zigux/check-phase7-build-wiring.py`, `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `python3 scripts/zigux/check-phase7-argv-split-packet.py`, `python3 scripts/zigux/validate-phase7.py`, and `make -C zigux phase7-validate` remain the shipped bounded replay surfaces, and `zigux/Makefile` still keeps only the narrow `phase7-validate` foothold explicit rather than a broader wrapper family.

Tests-root reviewer prompt:
- Does the bounded Phase 7 reminder keep the returned helper-anchor set, the dedicated checker stack, the shared manifest-backed inventory, the shared build graph, and the narrow `phase7-validate` foothold aligned without widening into new helper semantics, recovered wrapper families, or deeper runtime validation claims?

## Phase 8 tooling packet

Keep the current direct-readback Phase 8 anchors explicit through:

- `scripts/zigux/check-phase8-tests-readme-alignment.py`
- `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`
- `scripts/zigux/validate-phase8.py`
- `zigux/tests/phase8_exec_cmd.zig`
- `zigux/tests/phase8_exec_cmd_only_build.zig`
- `zigux/tests/phase8_perf_buffer_poll.zig`
- `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`

Keep the currently returned help-and-kallsyms focused packet explicit too; current `master` now rematerializes the dedicated shard files and their route-level companions even though the broader note still treats them as public-tree-backed companion evidence:

- `Documentation/zigux/phase8-help-slice.md`
- `Documentation/zigux/phase8-kallsyms-slice.md`
- `zigux/tests/phase8_help_only_build.zig`
- `zigux/tests/phase8_kallsyms_only_build.zig`
- `zigux/tests/phase8_help_kallsyms_only_build.zig`
- `make -C zigux phase8-help-test`
- `make -C zigux phase8-help-kallsyms-test`
- `make -C zigux phase8-kallsyms-test`

Keep the current mixed-source file-path-handle bridge companions explicit too; they remain reviewable on current `master` through the public tree and the aligned reminder packet:

- `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`
- `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`
- `scripts/zigux/validate-phase8.py`
- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
- `zigux/tests/phase8_file_path_handle_bridge.zig`
- `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`
- `zigux/tests/phase8_file_path_handle_boundary_guard.zig`
- `zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`
- `zigux/tests/phase8_build.zig`
- `make -C zigux phase8-exec-cmd-test`
- `make -C zigux phase8-file-path-handle-bridge-test`

current `zigux/tests/phase8_build.zig` also keeps the landed boundary-guard and manifest-sync witnesses inside the shared aggregate replay, so this tests-root reminder should treat both checks as current current-`master` evidence instead of leaving them implied only by the aggregate build route

repo-reality warning for the broader remaining Phase 8 tooling packet:

- `Documentation/zigux/phase8-libbpf-segment-survey.md`
- `Documentation/zigux/phase8-perf-buffer-poll-slice.md`
- `Documentation/zigux/phase8-tooling-lane-sequencing.md`
- `Documentation/zigux/phase8-help-slice.md`
- `Documentation/zigux/phase8-kallsyms-slice.md`
- `tools/lib/bpf/zigux_segments/verify.zig`
- `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`
- `zigux/tests/phase8_help_kallsyms_only_build.zig`
- `zigux/tests/phase8_verify_routing_gap.zig`
- `zigux/tests/phase8_verify_routing_gap_only_build.zig`
- `zigux/tests/phase8_libbpf_segments.zig`
- `zigux/tests/phase8_libbpf_segments_only_build.zig`
- `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
- `zigux/Makefile`
- `make -C zigux phase8-help-kallsyms-test`
- `make -C zigux phase8-libbpf-segments-test`
- `make -C zigux phase8-perf-buffer-poll-test`
- `make -C zigux phase8-test`

keep the narrower current Phase 8 reminder tied to the directly readable tests-readme checker plus the surviving perf-buffer poll checker, helper, and focused test packet, while also keeping the landed mixed-source file-path-handle bridge packet visible through the shared bridge-boundary survey, bridge slice, validator entrypoint, focused bridge proof, and helper-local replay instead of treating that same-lane bridge surface as missing current-master evidence
current public-tree rereads now rematerialize the broader help, kallsyms, and libbpf-segment companions on `master`, so treat those returned paths as public-tree-backed broader packet evidence rather than as part of the narrow direct-readback anchor set

if future same-lane work rematerializes the remaining broader docs, focused perf-buffer build shard, shared libbpf segment replay, or Makefile routes, or changes the focused bridge shard, the shared build replay, or the libbpf segment review packet, refresh this tests-root summary only after rereading the current direct-readback anchors together with the mixed-source file-path-handle bridge packet on current `master`

## Phase 15 governance packet

Keep the current bounded Phase 15 governance reminder explicit through `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-parity-scorecard-survey.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.
Keep `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-tests-readme-alignment.py`, `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-handoff-note-alignment.py`, `scripts/zigux/check-phase15-shared-summary-gap.py`, and `scripts/zigux/check-phase15-readiness-gate-packet.py` explicit as the shipped reminder guards so the tests-root summary stays in maintenance-mode truthfulness work instead of implying Architecture Council approval or direct deep-core port-readiness.

Keep the directly readable tests-root Phase 15 governance packet explicit through:
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-parity-scorecard-survey.md`
- `Documentation/zigux/phase15-readiness-gate-survey.md`
- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- `Documentation/zigux/phase15-governance-lane-sequencing.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- `Documentation/zigux/phase15-shared-summary-gap.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `scripts/zigux/check-phase15-docs-readme-alignment.py`
- `scripts/zigux/check-phase15-scripts-readme-alignment.py`
- `scripts/zigux/check-phase15-tests-readme-alignment.py`
- `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`
- `scripts/zigux/check-phase15-review-process-handoff.py`
- `scripts/zigux/check-phase15-handoff-note-alignment.py`
- `scripts/zigux/check-phase15-shared-summary-gap.py`
- `scripts/zigux/check-phase15-readiness-gate-packet.py`
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_freeze_map_governance.zig`
- `zigux/tests/phase15_architecture_council_review_process.zig`
- `zigux/tests/phase15_architecture_council_review_process_build.zig`
- `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- `zigux/tests/phase15_governance_lane_sequencing_manifest.json`
- `zigux/tests/phase15_governance_lane_sequencing.zig`
- `zigux/tests/phase15_parity_scorecard.json`
- `zigux/tests/phase15_parity_scorecard.zig`
- `zigux/tests/phase15_indefinite_c_policy.json`
- `zigux/tests/phase15_indefinite_c_policy.zig`
- `zigux/tests/phase15_readiness_gate_manifest.json`
- `zigux/tests/phase15_handoff_next_steps_manifest.json`
- `zigux/tests/phase15_handoff_next_steps.zig`
- `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`

Current `master` does materialize `zigux/tests/phase15_architecture_council_review_process_build.zig`, so keep that focused build-file replay in the directly readable governance packet instead of undercounting the Architecture Council review-process evidence.

Current `master` does materialize `zigux/tests/phase15_handoff_next_steps_manifest.json`, so keep that handoff-specific manifest in the directly readable governance packet instead of carrying it as a broader repo-reality gap.

Current `master` does materialize `zigux/tests/phase15_handoff_next_steps.zig`, so keep that focused handoff-specific replay in the directly readable governance packet instead of carrying the handoff packet as manifest-only inventory.

Current `master` does materialize `zigux/tests/phase15_governance_lane_sequencing_manifest.json` and `zigux/tests/phase15_governance_lane_sequencing.zig`, so keep that focused lane-sequencing manifest-plus-replay pair in the directly readable governance packet instead of leaving the Architecture Council maintenance route undercounted.

Current `master` does materialize `zigux/tests/phase15_parity_scorecard.json`, so keep that machine-readable parity scorecard companion explicit beside `zigux/tests/phase15_parity_scorecard.zig` in the directly readable governance packet instead of carrying the scorecard as replay-only evidence.

Current `master` now directly materializes `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, so keep that focused lane-owner replay in the directly readable governance packet instead of carrying it as a broader repo-reality gap.

Current `master` now directly materializes `scripts/zigux/validate-phase15.py`, so keep that validator-first maintenance gate explicit beside the directly readable governance packet instead of carrying it as a broader repo-reality gap.

Current `master` still does not materialize `zigux/tests/phase15_build.zig`, so keep that broader dedicated-build companion framed as a repo-reality gap rather than shipped tests-root evidence.
- `zigux/tests/phase15_build.zig`

Although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`, so keep those route names in the same blocked-route bucket until direct readback proves they have returned.

Tests-root reviewer prompt:
- Does the bounded Phase 15 reminder keep the directly readable governance packet, the returned review-process build replay, the returned readiness and handoff survey packet members, the returned focused handoff replay, the shared-summary gap note, the active-governance replay entrypoints, the returned validator-first maintenance gate, and the still-missing route-level and build-level surfaces aligned without promoting blocked governance wrappers or deeper-core status changes into current tests-root evidence without implying any Architecture Council approval for a freeze-map status change or a returned dedicated-build packet?

## Phase 9 runtime packet

Keep the current bounded Phase 9 reminder packet explicit through `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, and `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`.

Keep the current shared review-checklist and trace-events checker packet explicit through `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, and `zigux/tests/README.md`, while keeping the shared loader and command/environment boundary packet distinct from the trace-events direct sample family.

Keep `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, `zigux/tests/phase9_build.zig`, and `samples/zigux/runtime_bitmap_loader.zig` explicit as the current shared loader, bounded rerun-bundle, and direct loader-companion evidence, and keep `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_gap_survey.zig`, and `samples/zigux/runtime_trace_events_loader.zig` framed as historical wider-family vocabulary until trusted direct rereads return them.

Keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`, `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` remain the current shipped runtime-pilot proof rather than shared loader evidence.

Keep the partial runtime bitmap reminder packet distinct from that returned loader shard too: `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/README.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, and `zigux/tests/runtime_bitmap_manifest.json` are the current trusted bitmap-side evidence surfaces, while that returned bitmap-side visibility still must not be used to imply that the broader shared runtime-loader or blocked publication boundaries returned.

Keep the bounded Phase 9 build bundle explicit as a rerun surface only: `zigux/tests/phase9_build.zig` reruns the atomic64 diff, runtime bitmap sample, runtime bitmap loader, bitmap survey, bitmap module, bitmap diff, bitmap cold-stage guard, bitmap top-bit companion, shared loader allocator/init-flow, shared loader command/environment boundary guard, the shared trace-events loader-substrate-drift shard, and the first-loadable parity-survey handle, but it is not proof that blocked publication boundaries or deeper runtime substrate work are complete.

Keep the Phase 8 and earlier non-owner boundaries explicit too: `tools/lib/subcmd/exec-cmd.zig` and `tools/lib/subcmd/help.zig` remain the command and environment owners, `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 config-surface references, and `rust/exports.c` plus `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than runtime-pilot evidence.

Tests-root reviewer prompt:
- Does the bounded Phase 9 reminder keep the shared checker trio, the narrow trace-events sample family, the returned shared loader and command/environment boundary packet, the partial runtime bitmap reminder packet including the returned sample-root starter, loader companion, manifest-backed ownership packet, cold-stage guard, module, and diff witnesses, the bounded build rerun surface, and the study-only freeze-map routing aligned without promoting blocked publication, install-root, or broader runtime-substrate completion claims?

## Phase 12 release packet

Keep the current bounded Phase 12 tests-root reminder packet explicit through `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/README.md`.

Keep the directly readable validator-first support bundle explicit too: `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the current shared build gate explicit from the tests root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` remain shipped wrapper evidence on current `master`.

Keep the active shared build packet explicit too: `zigux/tests/phase12_build.zig` keeps `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` wired through the shared `smoke` and `test` route, so keep that six-file `virtio_net` packet explicit instead of widening it into deeper queue, DMA, throughput, or recovery claims.

Keep the adjacent driver-local split explicit too: `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` stay the rollback-lab `virtio_scsi` packet outside the shared route, `Documentation/zigux/phase12-nvme-pci-survey.md` plus `zigux/tests/phase12_nvme_pci_manifest.json` stay the bounded driver-local NVMe foothold, and `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` keep the parked libbpf packet explicit without promoting any of them into shared build outputs.

Keep `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` explicit as the shared heavy-helper anti-overlap companion so the tests-root reminder stays aligned with the same parked libbpf boundary already named by the release-order, closure, readiness, coordination, fallback, and complex-driver notes.

Keep `Documentation/zigux/phase12-raw-github-coverage-survey.md` explicit as the shared degraded-read companion so the tests-root reminder stays aligned with the same one-catalog plus one-current-master-gap-note companion plus shared-support-bundle fallback split already named by the PMO release packet.

Tests-root reviewer prompt:
- Does the bounded Phase 12 reminder keep the validator-first support bundle, the returned wrapper set, the six-file shared `virtio_net` packet, and the adjacent `virtio_scsi`, NVMe, and parked libbpf splits aligned without promoting broader complex-driver closure, DMA-safe receive ownership, queue restart parity, or deeper transport delivery claims?