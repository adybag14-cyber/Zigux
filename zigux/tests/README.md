# zigux/tests

This directory is the home of reusable Zigux parity and differential validation harnesses.

Purpose

  * hold shared harness logic before subsystem-specific tests spread through the tree
  * keep product-facing validation code separate from ad hoc experiments
  * provide the checks for helper parity, ABI assertions, and rollback readiness

Key entrypoints
  * `zigux/tests/build.zig`
  * roadmap-backed Phase 4 differential-gate destinations still missing on current `master`: `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig`
  * current direct-readback Phase 4 rollback packet:
    `Documentation/zigux/phase4-reversible-delivery-evidence.md`
    `Documentation/zigux/review-checklist.md`
    `zigux/tests/README.md`
    `scripts/zigux/check-phase4-repo-reality-warning.py`
    `scripts/zigux/check-phase4-reversible-delivery-pins.py`
  * Current direct-readback dedicated local-only perf checker: `scripts/zigux/check-phase4-perf-baseline-packet.py`
  * repo-reality warning for the broader Phase 4 validator, lab-matrix, and remaining local-only perf companions: authenticated contents reads on current `master` still return missing for `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig`
  * public current-`master` fallback rereads can still expose older broader Phase 4 companions, but keep that fallback visibility separate from authenticated direct-readback proof in this tests-root reminder until the same files return through direct contents reads
  * Phase 4 follow-through should treat the stale `PHASE4_REVERSIBLE_DELIVERY_LAST_KNOWN_*` lines in `Documentation/zigux/phase4-reversible-delivery-evidence.md` as historical provenance for that missing broader packet until fresh current-head evidence lands
  * The Phase 4 repo-reality warning in `zigux/tests/README.md` should stay open until that broader validator, lab-matrix, and remaining local-only perf companions are directly readable again
  * current shared Phase 4 ownership reminder: keep rollback-owner wording, artifact-diff contract references, and remaining-gap truthfulness aligned with `Documentation/zigux/phase4-reversible-delivery-evidence.md` instead of reconstructing the broader packet from older route names alone
  * historical Phase 4 route names such as the parked kprobe and `test_fsmount` survey companions, the validator-first routes, and the direct local-only perf routes stay owned by the reversible-delivery handoff note until the dedicated exact-pin refresh or a broader republish makes those companion blob values directly readable again
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
  * current public-tree-backed Phase 5 kretprobe shared-build companion: `zigux/tests/phase5_build.zig`
  * keep this tests-root reminder aligned with the restored non-runtime kretprobe packet and keep `zigux/tests/phase5_build.zig` framed as companion evidence instead of direct authenticated-contents proof
  * `Documentation/zigux/phase5-trace-events-sample-survey.md`
  * `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
  * current repo-reality warning for the remaining trace-events sample-local companions: authenticated contents reads on current `master` now return missing for `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, and `zigux/tests/phase5_build.zig`
  * keep this tests-root reminder aligned with those trace-events survey-note and approved-idiom-gap surfaces plus the shared Phase 5 review packet instead of treating those missing trace-events paths as direct tests-root proof until a fresh reread shows they returned
  * `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
  * `Documentation/zigux/phase1-closure.md`
  * `Documentation/zigux/review-checklist.md`
  * `Documentation/zigux/README.md`
  * `zigux/tests/fixtures/phase1_helper_manifest.json`
  * `zigux/tests/fixtures/phase1_helpers.json`
  * current direct-readback Phase 1 reminder packet: `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py`
  * current direct-readback shared Phase 1 closure companions visible from the tests-root reminder: `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `zigux/tests/build.zig`, and `zigux/tests/phase1_host_tools_smoke.zig`
  * repo-reality warning for the broader Phase 1 installer-backed closure-and-replay packet: repeated authenticated contents reads on current `master` now return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`
  * the restored `Documentation/zigux/phase1-closure.md` note, `scripts/zigux/validate-phase1-closure.py`, and the shared `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` route now keep the current-master-safe closure packet explicit from the tests root, while `scripts/zigux/check-phase1-bench.py` remains the shipped bench-side checker for the remaining shared reminder wording
  * current `master` does ship `scripts/zigux/check-phase1-bench.py`, and the shared `zigux/tests/build.zig` plus `zigux/tests/phase1_host_tools_smoke.zig` route keeps the restored closure-side reminder packet directly reviewable from the tests root, so keep the remaining shared reminder follow-through on the broader docs-root, checklist, and tests-root bench wording plus the shared smoke anchor instead of treating the checker or the shared route itself as missing current evidence
  * keep current Phase 1 follow-through tied to the live owner-map plus restored closure-side, string-review, bench, and shared-smoke reminder packet instead of reconstructing the broader installer-backed closure-and-replay packet from those older missing installer, validator-first, closure-side, and replay files and routes alone
  * current direct-readback Phase 6 shared packet: `Documentation/zigux/phase6-helper-evidence-catalog.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/phase6_build.zig`, and `zigux/tests/phase6_helper_evidence_manifest.json`
  * repo-reality warning for the broader Phase 6 helper parity and perf packet: repeated authenticated contents reads on current `master` now return missing for `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json`
  * keep current Phase 6 follow-through tied to those directly readable shared reminder surfaces plus the restored shared build and machine-readable evidence footholds instead of reconstructing the broader helper-local parity and perf packet from older route names alone

Phase 2 review packet
  * `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
  * `Documentation/zigux/review-checklist.md`
  * `scripts/zigux/README.md`
  * `scripts/zigux/check-zig-toolchain.py`
  * `scripts/zigux/check-phase2-kbuild-routes.py`
  * `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
  * `scripts/zigux/check-phase2-tests-readme-alignment.py`
  * `scripts/zigux/check-phase2-cross-selftest-alignment.py`
  * `scripts/zigux/check-phase2-toolchain-pinning.py`
  * `scripts/zigux/check-phase2-toolchain-pin-scope.py`
  * `python3 scripts/zigux/check-zig-toolchain.py --self-test`
  * `scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
  * `scripts/zigux/kconfig/conf_bridge.zig`
  * `scripts/zigux/kconfig/confdata_bridge.zig`
  * `zigux/tests/fixtures/phase2_tool_manifest.json`
  * `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
  * `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
  * `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
  * `zigux/tests/fixtures/kconfig_bridge/cases.json`
  * the current directly readable Phase 2 packet is the scripts-root kbuild, cross-selftest, and toolchain reminder set plus the live kconfig bridge helpers and their fixture roster; keep this tests-root summary aligned to that narrower packet instead of rebuilding the older validator-first, cross-route, and make-route stack from missing current-`master` paths
  * keep the pinned `x86_64-linux` bootstrap archive note and repo-local `.zig-toolchain` fallback reused by the surviving `scripts/zigux/check-zig-toolchain.py` and pin-scope guards explicit in this tests-root packet beside the live toolchain checker instead of widening back into missing validator-first or make-wrapper proof text
  * repeated authenticated reads on current `master` still return missing for `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-validate`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep those route names framed as historical packet members rather than direct tests-root evidence until the files or wrappers return on current `master`
  * keep the fixture-backed tool-manifest, artifact-tools, and kconfig bridge packet visible in the tests root without reviving missing validator-first or make-wrapper proof text

Phase 3 review packet
  * `Documentation/zigux/phase3-abi-slice.md`
  * `Documentation/zigux/phase3-errptr-xarray-slice.md`
  * `Documentation/zigux/phase3-policy-slice.md`
  * `Documentation/zigux/phase3-validator-support-surface.md`
  * `include/linux/zigux.h`
  * `include/zigux/dev_t.h`
  * `include/zigux/abi.h`
  * `zigux/uapi/version.zig`
  * `zigux/uapi/dev_t.zig`
  * `zigux/bindings/dev_t.zig`
  * `zigux/bindings/abi.zig`
  * `zigux/helpers/err_ptr.zig`
  * `zigux/helpers/xa_value.zig`
  * `zigux/helpers/panic_policy.zig`
  * `zigux/helpers/allocator_policy.zig`
  * `zigux/helpers/unsafe_policy.zig`
  * `zigux/tests/phase3_dev_t_starter_packet.zig`
  * `zigux/tests/phase3_dev_t_starter_packet_build.zig`
  * `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
  * `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
  * `zigux/tests/phase3_policy_starter_packet.zig`
  * `zigux/tests/phase3_policy_starter_packet_build.zig`
  * `zigux/tests/phase3_policy_starter_packet_manifest.json`
  * `scripts/zigux/check-phase3-dev-t-starter-packet.py`
  * `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`
  * `scripts/zigux/check-phase3-policy-starter-packet.py`
  * `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test`
  * `python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test`
  * `python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test`
  * keep the current shared Phase 3 reminder anchored to the bounded `dev_t` starter packet, the helper-local `err_ptr` / `xarray` slice, and the focused policy slice already described in `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-errptr-xarray-slice.md`, and `Documentation/zigux/phase3-policy-slice.md`, instead of presenting the broader validator, export/UAPI layout, low-level-wrapper, IDR, or IDA packet as shipped tests-root evidence
  * treat broader routes such as `Documentation/zigux/phase3-abi-header-family-survey.md`, `Documentation/zigux/phase3-abi-h-boundary-next-step.md`, `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, `scripts/zigux/validate-phase3.py`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, and `scripts/zigux/phase3_catalog.py` as repo-reality gaps until fresh current-tree proof lands
  * keep `Documentation/zigux/phase3-shared-reminder-gap.md` limited to tracking any future shared-surface drift or separate scripts-root inventory follow-through, because `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md` already carry the bounded three-slice posture and this tests-root packet should stay aligned with them

Phase 7 review packet
  * current direct-readback Phase 7 anchors: `Documentation/zigux/phase7-string-helpers-slice.md`, `lib/string_helpers.zig`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_survey.zig`, `zigux/tests/phase7_string_helpers_manifest.json`, and `zigux/tests/phase7_string_helpers_sample_boundary.zig`, and `zigux/tests/phase7_rbtree_survey.zig`
  * keep the current Phase 7 tests-root reminder aligned with the directly readable string_helpers helper-local packet plus the surviving direct `zigux/tests/phase7_rbtree_survey.zig` anchor instead of framing current `master` as if only the narrower rbtree reminder were still visible
  * repo-reality warning for the broader remaining Phase 7 rbtree packet:
    `Documentation/zigux/phase7-helper-lane-sequencing.md`
    `Documentation/zigux/phase7-rbtree-slice.md`
    `scripts/zigux/check-phase7-rbtree-parity.py`
    `zigux/tests/phase7_rbtree.zig`
    `zigux/tests/phase7_rbtree_manifest.json`
    `zigux/tests/fixtures/phase7_rbtree.json`
    `zigux/tests/fixtures/phase7_rbtree_c_harness.c`
    `zigux/tests/phase7_build.zig`
  * treat those broader rbtree paths plus the older `make -C zigux phase7-validate` and `make -C zigux phase7` route names as last-known packet members that still need fresh reread or re-materialization before they are presented here as shipped direct evidence again
  * leave `cmdline` and `argv_split` follow-through parked until a fresh same-lane reread justifies widening beyond the directly readable string_helpers packet and the surviving rbtree survey anchor

Phase 8 review packet
  * current direct-readback Phase 8 anchors:
    `scripts/zigux/check-phase8-tests-readme-alignment.py`
    `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`
    `zigux/tests/phase8_perf_buffer_poll.zig`
    `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
  * current mixed-source file-path-handle bridge companions also remain reviewable on current `master` through the public tree and aligned reminder packet:
    `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`
    `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`
    `scripts/zigux/validate-phase8.py`
    `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
    `zigux/tests/phase8_file_path_handle_bridge.zig`
    `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`
    `zigux/tests/phase8_build.zig`
    `make -C zigux phase8-file-path-handle-bridge-test`
  * repo-reality warning for the broader remaining Phase 8 tooling packet:
    `Documentation/zigux/phase8-tooling-lane-sequencing.md`
    `Documentation/zigux/phase8-help-slice.md`
    `Documentation/zigux/phase8-kallsyms-slice.md`
    `Documentation/zigux/phase8-libbpf-segment-survey.md`
    `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
    `zigux/tests/phase8_libbpf_segments.zig`
    `zigux/Makefile`
  * keep the narrower current Phase 8 reminder tied to the directly readable tests-readme checker plus the surviving perf-buffer poll checker, helper, and focused test packet, while also keeping the landed mixed-source file-path-handle bridge packet visible through the shared bridge-boundary survey, bridge slice, validator entrypoint, focused bridge proof, and helper-local replay instead of treating that same-lane bridge surface as missing current-master evidence
  * if future same-lane work rematerializes the remaining broader docs, focused perf-buffer build shard, shared libbpf segment replay, or Makefile routes, or changes the focused bridge shard, the shared build replay, or the libbpf segment review packet, refresh this tests-root summary only after rereading the current direct-readback anchors together with the mixed-source file-path-handle bridge packet on current `master`

Phase 9 review packet
  * `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
  * `Documentation/zigux/review-checklist.md`
  * `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`
  * `scripts/zigux/check-phase9-trace-events-runtime-packet.py`
  * `zigux/tests/README.md`
  * `samples/zigux/runtime_trace_events.zig`
  * `samples/zigux/runtime_trace_events_unregistered_gate.zig`
  * `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`
  * the surviving trace-events packet still keeps the roadmap-backed runtime pilot shape concrete by exposing `.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking inside `samples/zigux/runtime_trace_events.zig`, while `samples/zigux/runtime_trace_events_unregistered_gate.zig` keeps the same narrow packet's unregistered function-thread failures fail-closed and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` keeps balanced function-thread registration reusable before and after selftest, so reviewers can still inspect one real runtime-module plus its companion registration and lifecycle boundaries while the broader shared loader packet remains backlog
  * there is no shared `zigux/tests/runtime_*` replay packet, `zigux/tests/phase9_build.zig`, `make -C zigux phase9*` route family, or dedicated shared `validate-phase9.py` visible on current `master`

Phase 13 review packet
  * Keep the stable contributor-facing reminder handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. Keep `Documentation/zigux/review-checklist.md` and `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md` aligned with that stable handle as supporting shared reminder surfaces rather than treating the missing Makefile-backed route family as the shared entrypoint.
  * Keep the current contributor-facing Phase 13 packet explicit through these shipped shared surfaces:
  * `Documentation/zigux/phase13-contributor-workflow-guide.md`
  * `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
  * `Documentation/zigux/phase13-release-coordination-matrix.md`
  * `Documentation/zigux/phase13-release-notes-survey.md`
  * `Documentation/zigux/phase13-roadmap-traceability.md`
  * `Documentation/zigux/phase13-libfs-survey.md`
  * `Documentation/zigux/phase13-devres-slice.md`
  * `Documentation/zigux/phase13-devres-survey.md`
  * `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
  * `Documentation/zigux/phase13-landlock-ruleset-slice.md`
  * `Documentation/zigux/phase13-landlock-ruleset-survey.md`
  * `Documentation/zigux/phase13-landlock-syscalls-governance.md`
  * `Documentation/zigux/phase13-landlock-syscalls-slice.md`
  * `Documentation/zigux/phase13-landlock-syscalls-survey.md`
  * `fs/libfs.zig`
  * `zigux/tests/phase13_libfs.zig`
  * `zigux/tests/phase13_libfs_reviewability.zig`
  * `zigux/tests/phase13_libfs_manifest.json`
  * `lib/devres.zig`
  * `zigux/tests/phase13_devres.zig`
  * `zigux/tests/phase13_devres_reviewability.zig`
  * `zigux/tests/phase13_devres_dma_coherent.zig`
  * `zigux/tests/phase13_devres_boundary_evidence.zig`
  * `zigux/tests/phase13_devres_manifest.json`
  * `security/landlock/ruleset.zig`
  * `security/landlock/syscalls.zig`
  * `zigux/tests/phase13_landlock_ruleset.zig`
  * `zigux/tests/phase13_landlock_ruleset_manifest.json`
  * `zigux/tests/phase13_landlock_syscalls.zig`
  * `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
  * `zigux/tests/phase13_landlock_syscalls_manifest.json`
  * `Documentation/zigux/review-checklist.md`
  * `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
  * `zigux/helpers/notifier_chain_view.zig`
  * `zigux/bindings/notifier_abi.zig`
  * `include/zigux/abi.h`
  * `drivers/tty/hvc/hvc_console.h`
  * Current `master` still does not materialize `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, or `scripts/zigux/check-phase13-notifier-priority-signal.py`, so keep those validator-first and checker names framed as repo-reality gaps rather than shipped tests-root evidence.
  * Current `master` does materialize `scripts/zigux/check-phase13-shared-summary-surfaces.py`, so keep that guard explicit as shipped shared-summary evidence aligned with the contributor workflow guide and roadmap-traceability note instead of repeating it as a missing tests-root gap.
  * Current `master` also materializes the adjacent notifier survey plus the direct-evidence shards `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, the read-only `zigux/helpers/list_view.zig` and `zigux/helpers/hlist_view.zig` helpers, and the Linux-side `drivers/tty/hvc/hvc_console.h` header, so keep those six paths explicit as shipped adjacent evidence without counting them as extra shared replay steps.
  * Current `master` does materialize `zigux/Makefile`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep those route names framed as repo-reality-gap vocabulary rather than shipped tests-root evidence until a fresh reread proves the shared build handle returned.

Tests-root reviewer prompt:
  * keep the contributor-facing reminder handle anchored to `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
  * keep `make -C zigux phase13-validate` and blocked convenience route `make -C zigux phase13` framed as route-gap vocabulary rather than shipped tests-root proof
  * keep adjacent notifier evidence adjacent instead of promoting it into a fifth helper family

Phase 15 review packet
  * current direct-readback Phase 15 governance packet:
    `Documentation/zigux/freeze-map.md`
    `Documentation/zigux/review-checklist.md`
    `Documentation/zigux/phase15-freeze-map-governance.md`
    `Documentation/zigux/phase15-architecture-council-review-process.md`
    `Documentation/zigux/phase15-readiness-gate-survey.md`
    `Documentation/zigux/phase15-handoff-next-steps-survey.md`
    `Documentation/zigux/phase15-study-only-anchor-accounting.md`
    `Documentation/zigux/phase15-shared-summary-gap.md`
    `scripts/zigux/check-phase15-review-process-handoff.py`
    `scripts/zigux/check-phase15-tests-readme-alignment.py`
    `zigux/tests/phase15_architecture_council_review_process.zig`
    `zigux/tests/phase15_architecture_council_review_process_manifest.json`
    `zigux/tests/phase15_readiness_gate_manifest.json`
  * `python3 scripts/zigux/check-phase15-tests-readme-alignment.py --self-test` and `python3 scripts/zigux/check-phase15-review-process-handoff.py --self-test` replay the focused tests-root governance checks, while `scripts/zigux/check-phase15-tests-readme-alignment.py` and `scripts/zigux/check-phase15-review-process-handoff.py` guard the shipped reminder packet without rebuilding the missing broader validator-first or build stack
  * repeated authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_build.zig`, `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, and `zigux/Makefile`, so keep those broader validator-first, handoff-manifest, build, lane-owner, and make-wrapper paths framed as repo-reality gaps instead of direct tests-root evidence
  * keep the current Phase 15 tests-root reminder aligned with the directly materialized governance packet, including the dedicated Architecture Council review-process note and the study-only accounting note, instead of implying that the broader validator-first or make-wrapper routes are already shipped on current `master`
  * no Architecture Council approval is currently recorded for a freeze-map status change; keep the four freeze-in-C anchors parked, keep the two roadmap study-only anchors parked, and keep any future follow-through narrowed to the smallest reminder-surface repair first
