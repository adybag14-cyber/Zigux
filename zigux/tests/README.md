# zigux/tests

This directory is the home of reusable Zigux parity and differential validation harnesses.

Purpose
- hold shared harness logic before subsystem-specific tests spread through the tree
- keep product-facing validation code separate from ad hoc experiments
- provide the checks for helper parity, ABI assertions, and rollback readiness

Key entrypoints
- `zigux/tests/build.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/bitmap_diff.zig`
- `zigux/tests/phase4_build.zig`
- `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`
- `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/phase1_bench.zig`
- `zigux/tests/phase6_build.zig`
- `zigux/tests/phase6_base64.zig`
- `zigux/tests/phase6_base64_perf.zig`
- `zigux/tests/phase6_base64_c_parity.zig`
- `zigux/tests/fixtures/phase6_base64_vectors.zig`
- `zigux/tests/fixtures/phase6_base64_c_harness.c`
- `zigux/tests/phase6_bsearch.zig`
- `zigux/tests/phase6_bsearch_perf.zig`
- `zigux/tests/phase6_bsearch_c_parity.zig`
- `zigux/tests/fixtures/phase6_bsearch_c_harness.c`
- `zigux/tests/phase6_checksum.zig`
- `zigux/tests/phase6_checksum_perf.zig`
- `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- `zigux/tests/phase6_hexdump.zig`
- `zigux/tests/phase6_hexdump_perf.zig`
- `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- `Documentation/zigux/phase6-helper-parity-catalog.md`
- `zigux/tests/phase7_build.zig`
- `zigux/tests/phase7_string_helpers.zig`
- `zigux/tests/phase7_cmdline.zig`
- `zigux/tests/phase7_argv_split.zig`
- `zigux/tests/phase7_argv_split_survey.zig`
- `zigux/tests/phase7_argv_split_manifest.json`
- `zigux/tests/phase7_rbtree.zig`
- `zigux/tests/phase7_rbtree_survey.zig`
- `zigux/tests/phase7_rbtree_manifest.json`
- `zigux/tests/fixtures/phase7_string_helpers_escape_vectors.zig`
- `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`
- `zigux/tests/fixtures/phase7_argv_split_vectors.zig`
- `zigux/tests/fixtures/phase7_rbtree.json`
- `zigux/tests/fixtures/phase7_rbtree_c_harness.c`
- `zigux/tests/phase8_build.zig`
- `zigux/tests/phase8_libbpf_segments_only_build.zig`
- `zigux/tests/phase8_exec_cmd.zig`
- `zigux/tests/phase8_help.zig`
- `zigux/tests/phase8_kallsyms.zig`
- `zigux/tests/phase8_cpu_mask.zig`
- `zigux/tests/phase8_logging.zig`
- `zigux/tests/phase8_pin_path.zig`
- `zigux/tests/phase8_file_path_handle_bridge.zig`
- `zigux/tests/phase8_libbpf_segments.zig`
- `zigux/tests/phase8_bpf_type_names.zig`
- `zigux/tests/phase9_build.zig`
- `zigux/tests/runtime_loader_gap_survey.zig`
- `zigux/tests/runtime_loader_gap_manifest.json`
- `zigux/tests/runtime_module_metadata_manifest.json`
- `zigux/tests/runtime_module_metadata_survey.zig`
- `scripts/zigux/check-phase9-module-metadata-packet.py`
- `zigux/tests/phase10_build.zig`
- `zigux/tests/phase10_virtio_core.zig`
- `zigux/tests/phase10_virtio_ring.zig`
- `zigux/tests/phase10_virtio_ring_survey.zig`
- `zigux/tests/phase10_virtio_input.zig`
- `zigux/tests/phase10_virtio_input_survey.zig`
- `zigux/tests/phase10_virtio_mmio_survey.zig`
- `zigux/tests/phase10_virtio_ring_manifest.json`
- `zigux/tests/phase10_virtio_input_manifest.json`
- `zigux/tests/phase10_virtio_mmio_manifest.json`
- `zigux/tests/phase10_closure_manifest.json`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase14_build.zig`
- `zigux/tests/phase14_ring_buffer_survey.zig`
- `zigux/tests/phase14_skbuff_bridge.zig`
- `zigux/tests/phase14_workqueue_bridge.zig`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/validate-phase4.py`
- `scripts/zigux/validate-phase6.py`
- `scripts/zigux/validate-phase7.py`
- `scripts/zigux/validate-phase8.py`
- `scripts/zigux/validate-phase9.py`
- `scripts/zigux/validate-phase10.py`
- `scripts/zigux/validate-phase10-closure.py`
- `Documentation/zigux/phase4-validation-matrix.md`
- `scripts/zigux/phase3_catalog.py --self-test`
- `scripts/zigux/phase3_check_lib.py --self-test`
- `scripts/zigux/generate-phase3-check-wrappers.py --check`
- `scripts/zigux/run-phase3-checks.py --self-test`
- `scripts/zigux/run-phase3-checks.py`
- the Phase 9 loader-gap manifest now also carries the manifest-backed catalog and ownership map for the current runtime evidence packet, so test-side validation names which file owns the survey note, the review checklist, the shared request contract, the sample-side loader plans, and the shared `phase9_build.zig` replay path.
- the dedicated Phase 9 module-metadata packet now also stays reviewable through `zigux/tests/runtime_module_metadata_manifest.json`, `zigux/tests/runtime_module_metadata_survey.zig`, and `scripts/zigux/check-phase9-module-metadata-packet.py`, so the starter-descriptor and loader-plan evidence remains fail-closed without implying a landed depmod bridge.

Phase 3 fixtures
- each Phase 3 slice keeps its expected JSON and C harness under `zigux/tests/fixtures/phase3_*`
- manifests may live beside the fixture directory or inside it; the Phase 3 catalog selects the best valid manifest candidate
- the catalog also discovers the matching dump entrypoint under `zigux/tests/phase3_*_dump.zig`
- the shared runner now executes slices directly from catalog metadata, and slice docs may point their `PHASE3_INTEROP_GATE` marker at either `run-phase3-checks.py --slug <slug>` or the legacy wrapper command
- `python3 scripts/zigux/phase3_catalog.py --legacy-wrapper-docs` lists the slice docs that still rely on legacy wrapper markers so cleanup work can stay targeted
- `python3 scripts/zigux/phase3_catalog.py --legacy-wrapper-references` lists the remaining concrete wrapper-path mentions outside the slice docs so fixture and policy cleanup stays targeted too
- wrapper stubs are convenience entrypoints rather than the execution path and may be pruned when the underlying slice disappears

Guidance
- keep parity fixtures committed and readable
- prefer discovery-based validation over hard-coded file inventories when adding new Phase 3 slices
- keep new leaf-helper tests small, explicit, and tied to the owning helper path when Phase 6 work starts
- refresh `Documentation/zigux/phase6-helper-parity-catalog.md` whenever the shipped Phase 6 helper inventory, perf entrypoints, fixtures, or shared slice notes change
- keep the current Phase 7 helper packet reviewable through `zigux/tests/phase7_build.zig`, `make -C zigux phase7-test`, `scripts/zigux/validate-phase7.py`, and `scripts/zigux/check-phase7-rbtree-parity.py` instead of widening into ad hoc helper-local bootstrap rules
- keep the Phase 7 handoff explicit: the helper roots in `zigux/tests/phase7_build.zig` receive `string_helpers`, `cmdline`, `argv_split`, and `rbtree` through `addImport(...)`, while `zigux/tests/phase7_argv_split_survey.zig` and `zigux/tests/phase7_rbtree_survey.zig` rely on repo-root reads of `zigux/tests/phase7_argv_split_manifest.json` and `zigux/tests/phase7_rbtree_manifest.json`
- keep the current Phase 8 tooling packet reviewable through both `zigux/tests/phase8_libbpf_segments_only_build.zig` and `zigux/tests/phase8_build.zig`, `scripts/zigux/validate-phase8.py`, `Documentation/zigux/phase8-libbpf-cpu-mask-slice.md`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, and `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, including the landed `phase8_file_path_handle_bridge.zig` helper replay, the parked command-preparation boundary, and the still-deferred `perf-buffer-online-cpu-routing` boundary beside `tools/lib/bpf/zigux_segments/cpu_mask.zig`

Phase 10 guidance
- keep the current Phase 10 lab bundle reviewable through `zigux/tests/phase10_build.zig` and the three manifest-backed survey records instead of treating individual virtio starter files as independent closure signals
- if the Phase 10 evidence bundle changes, update `zigux/tests/phase10_closure_manifest.json` and `Documentation/zigux/phase10-closure-evidence.md` together so the shared closure gate stays truthful about what is implemented versus still survey-backed
- keep `scripts/zigux/validate-phase10.py` aligned with `zigux/tests/phase10_virtio_input_manifest.json` and `zigux/tests/phase10_virtio_input_survey.zig` so the registration-preflight helper stays the only ready-next step and the registration-lifecycle blocker stays explicit
