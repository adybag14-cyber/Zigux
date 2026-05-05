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
  * `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`
  * `zigux/tests/bitmap_diff.zig`
  * `zigux/tests/phase4_bitmap_live_helper_replay.zig`
  * `zigux/tests/phase4_build.zig`
  * `zigux/tests/phase5_build.zig`
  * `zigux/tests/phase1_helpers.zig`
  * `zigux/tests/phase1_bench.zig`
  * `zigux/tests/phase6_build.zig`
  * `zigux/tests/phase6_base64.zig`
  * `zigux/tests/phase6_bsearch.zig`
  * `zigux/tests/phase6_checksum.zig`
  * `zigux/tests/phase6_hexdump.zig`
  * `zigux/tests/phase6_checksum_perf.zig`
  * `zigux/tests/phase6_hexdump_perf.zig`
  * `zigux/tests/phase7_build.zig`
  * `zigux/tests/phase7_string_helpers.zig`
  * `zigux/tests/phase7_string_helpers_sample_boundary.zig`
  * `zigux/tests/phase7_cmdline.zig`
  * `zigux/tests/phase7_cmdline_survey.zig`
  * `zigux/tests/phase7_argv_split.zig`
  * `zigux/tests/phase7_argv_split_survey.zig`
  * `zigux/tests/phase7_rbtree.zig`
  * `zigux/tests/phase7_rbtree_survey.zig`
  * `zigux/tests/phase8_build.zig`
  * `zigux/tests/phase8_exec_cmd.zig`
  * `zigux/tests/phase8_help.zig`
  * `zigux/tests/phase8_kallsyms.zig`
  * `zigux/tests/phase8_cpu_mask.zig`
  * `zigux/tests/phase8_logging.zig`
  * `zigux/tests/phase8_pin_path.zig`
  * `zigux/tests/phase8_bpf_type_names.zig`
  * `zigux/tests/phase8_libbpf_segments.zig`
  * `zigux/tests/phase9_build.zig`
  * `zigux/tests/runtime_atomic64_survey.zig`
  * `zigux/tests/runtime_bitmap_survey.zig`
  * `zigux/tests/runtime_trace_events_survey.zig`
  * `zigux/tests/runtime_kretprobe_survey.zig`
  * `zigux/tests/runtime_loader_allocator_init_flow.zig`
  * `zigux/tests/phase10_build.zig`
  * `zigux/tests/phase10_virtio_core.zig`
  * `zigux/tests/phase10_virtio_ring.zig`
  * `zigux/tests/phase10_virtio_ring_survey.zig`
  * `zigux/tests/phase10_virtio_input.zig`
  * `zigux/tests/phase10_virtio_input_survey.zig`
  * `zigux/tests/phase10_virtio_mmio.zig`
  * `zigux/tests/phase10_virtio_mmio_survey.zig`
  * `zigux/tests/phase11_build.zig`
  * `zigux/tests/phase11_hvc_cleanup.zig`
  * `zigux/tests/phase11_hvc_console_survey.zig`
  * `zigux/tests/phase12_build.zig`
  * `zigux/tests/phase12_nvme_pci.zig`
  * `zigux/tests/phase12_nvme_pci_survey.zig`
  * `zigux/tests/phase12_virtio_net.zig`
  * `zigux/tests/phase12_virtio_net_survey.zig`
  * `zigux/tests/phase12_virtio_scsi_survey.zig`
  * `zigux/tests/phase12_virtio_scsi.zig`
  * `zigux/tests/phase12_libbpf_segments.zig`
  * `zigux/tests/phase12_libbpf_reviewability.zig`
  * `zigux/tests/phase13_build.zig`
  * `zigux/tests/phase3_abi.zig`
  * `zigux/tests/phase3_low_level_wrappers.zig`
  * `zigux/tests/phase14_build.zig`
  * `zigux/tests/phase14_ring_buffer_survey.zig`
  * `zigux/tests/phase14_skbuff_bridge.zig`
  * `zigux/tests/phase14_workqueue_bridge.zig`
  * `zigux/tests/phase14_end_to_end_smoke_survey.zig`
  * `zigux/tests/phase15_build.zig`
  * `zigux/tests/phase15_freeze_map_governance.zig`
  * `zigux/tests/phase15_parity_scorecard.zig`
  * `zigux/tests/phase15_architecture_council_review_process.zig`
  * `zigux/tests/phase15_indefinite_c_policy.zig`
  * `scripts/zigux/validate-phase3.py`
  * `scripts/zigux/validate_phase3_selftest.py`
  * `scripts/zigux/validate-phase4.py`
  * `Documentation/zigux/phase4-validation-matrix.md`
  * `scripts/zigux/phase3_catalog.py --self-test`
  * `scripts/zigux/phase3_check_lib.py --self-test`
  * `scripts/zigux/generate-phase3-check-wrappers.py --check`
  * `scripts/zigux/run-phase3-checks.py --self-test`
  * `scripts/zigux/run-phase3-checks.py`

Phase 3 fixtures
  * each Phase 3 slice keeps its expected JSON and C harness under `zigux/tests/fixtures/phase3_*`
  * manifests may live beside the fixture directory or inside it; the Phase 3 catalog selects the best valid manifest candidate
  * the catalog also discovers the matching dump entrypoint under `zigux/tests/phase3_*_dump.zig`
  * the shared runner now executes slices directly from catalog metadata, and slice docs may point their `PHASE3_INTEROP_GATE` marker at either `run-phase3-checks.py --slug <slug>` or the legacy wrapper command
  * `python3 scripts/zigux/phase3_catalog.py --legacy-wrapper-docs` lists the slice docs that still rely on legacy wrapper markers so cleanup work can stay targeted
  * `python3 scripts/zigux/phase3_catalog.py --legacy-wrapper-references` lists the remaining concrete wrapper-path mentions outside the slice docs so fixture and policy cleanup stays targeted too
  * wrapper stubs are convenience entrypoints rather than the execution path and may be pruned when the underlying slice disappears

Guidance
  * keep parity fixtures committed and readable
  * keep the closed Phase 1 host-tools packet explicit in the tests root too: `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` should continue to keep the closed helper tranche reviewable from the tests root instead of leaving the host-tools closure stack split across the docs root and scripts root
  * keep the active Phase 2 toolchain packet explicit in the tests root too: `Documentation/zigux/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, `zigux/Makefile`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `make -C zigux phase2-validate`, and `make -C zigux phase2` should continue to keep the pinned `x86_64-linux` bootstrap archive note, the bounded three-target compile matrix, and the shared kbuild-facing replay surface reviewable from the tests root instead of leaving the active Phase 2 tranche split across the docs root, scripts root, closure note, and workflow wiring alone
  * prefer discovery-based validation over hard-coded file inventories when adding new Phase 3 slices
  * keep the focused Phase 3 validator-support replay explicit in the tests root too: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase3-abi-slice.md`, `scripts/zigux/README.md`, `zigux/Makefile`, `python3 scripts/zigux/validate_phase3_selftest.py`, and `make -C zigux phase3-selftest` should continue to keep the shared validator-support runner visible as an opt-in safety check that complements but does not duplicate `make -C zigux phase3-validate`
  * keep the canonical Phase 4 atomic64 wrapper explicit: `zigux/tests/phase4_build.zig` should continue to run `zigux/tests/atomic64_diff.zig` as the roadmap entrypoint, that wrapper should remain a thin shim over the shared runtime-backed replay body, that survey gate should keep the manifest-backed wrapper handoff reviewable beside that same wrapper gate, `zigux/tests/phase4_bitmap_live_helper_replay.zig` should keep the helper-backed bitmap rollback checkpoints explicit, and `Documentation/zigux/phase4-validation-matrix.md` should keep that wrapper-versus-runtime handoff reviewable without cloning the shared replay body
  * keep the shared Phase 5 reference-sample checks wired through `zigux/tests/phase5_build.zig` so the four shipped sample-backed surveys stay reviewable without implying runtime-substrate closure
  * keep the shared Phase 6 leaf-helper packet wired through `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, including `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, and `zigux/tests/phase6_hexdump.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `make -C zigux phase6-validate`, and `make -C zigux phase6`, so the landed `base64`, `bsearch`, `checksum`, and `hexdump` bundle stays reviewable through one bounded helper gate, and keep `zigux/tests/phase6_checksum_perf.zig` plus `make -C zigux phase6-checksum-perf` and `zigux/tests/phase6_hexdump_perf.zig` plus `make -C zigux phase6-hexdump-perf` explicit as the dedicated checksum and hexdump perf routes rather than implying a broader Phase 6 packet-wide perf target
  * keep the shared Phase 7 leaf-helper packet wired through `zigux/tests/phase7_build.zig`, including the dedicated `zigux/tests/phase7_cmdline_survey.zig` cmdline survey gate, the dedicated `zigux/tests/phase7_argv_split_survey.zig` argvSplit survey gate, the dedicated `zigux/tests/phase7_string_helpers_sample_boundary.zig` boundary replay, and the dedicated `zigux/tests/phase7_rbtree_survey.zig` survey gate, so the landed `string_helpers`, `cmdline`, `argv_split`, and `rbtree` bundle stays reviewable through one bounded runtime-safe entrypoint
  * keep the shared Phase 8 tooling packet wired through `zigux/tests/phase8_build.zig`, including `zigux/tests/phase8_exec_cmd.zig`, `zigux/tests/phase8_help.zig`, `zigux/tests/phase8_help_only_build.zig`, `zigux/tests/phase8_kallsyms.zig`, `zigux/tests/phase8_kallsyms_only_build.zig`, `zigux/tests/phase8_cpu_mask.zig`, `zigux/tests/phase8_logging.zig`, `zigux/tests/phase8_pin_path.zig`, `zigux/tests/phase8_bpf_type_names.zig`, and `zigux/tests/phase8_libbpf_segments.zig`, and keep `zigux/Makefile` plus `make -C zigux phase8-help-test`, `make -C zigux phase8-kallsyms-test`, and `make -C zigux phase8` explicit so the landed repo-hosted tooling bundle stays reviewable through both the shared output-stable entrypoint and the focused help and kallsyms shard replays instead of falling back to ad hoc per-slice checks
  * keep the bounded Phase 9 runtime-loader packet wired through `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-build-only-surface.py`, `zigux/tests/phase9_build.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `make -C zigux phase9`, the four survey entrypoints `zigux/tests/runtime_atomic64_survey.zig`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/runtime_trace_events_survey.zig`, and `zigux/tests/runtime_kretprobe_survey.zig`, the four `samples/zigux/runtime_*_loader.zig` scaffolds, and the shared `zigux/kernel/runtime_loader.zig` plus `zigux/kernel/runtime_loader_contract.zig` surfaces so the loader-handoff packet stays reviewable through the same shipped build-only checker and workflow-backed replay route without implying shared runtime substrate closure or a dedicated `validate-phase9.py` surface that does not exist on `master`
  * keep the active Phase 10 virtio packet explicit in the tests root too: `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `zigux/Makefile`, `zig build test --build-file zigux/tests/phase10_build.zig`, and `make -C zigux phase10` should continue to keep the current virtio core, virtio ring, virtio input, and virtio mmio packet reviewable through one shared build-and-make route without implying a dedicated `validate-phase10.py`, `check-phase10-harness-coverage.py`, or `phase10-validate` surface that does not exist on `master`
  * keep the shared-versus-dedicated Phase 11 simple-driver packet explicit in the tests root too: `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/Makefile`, `zig build test --build-file zigux/tests/phase11_build.zig`, and `make -C zigux phase11` should continue to keep the shipped shared replay route, the dedicated `hvc_console` archival survey note and replay, the bounded `hvc_cleanup()` teardown handoff, and the four driver-local validation matrices reviewable from the tests root without implying a removed `validate-phase11.py`, missing build-inventory fixture, or broader checker-script packet that does not exist on `master`
  * keep the active Phase 12 survey-backed complex-driver packet explicit in the tests root too: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_nvme_pci_manifest.json`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, `zigux/tests/phase12_virtio_net_manifest.json`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_survey.zig`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/phase12_libbpf_manifest.json`, `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, `tools/lib/bpf/zigux_segments/manifest.json`, `zigux/tests/phase12_build.zig`, `zigux/Makefile`, and `make -C zigux phase12` should continue to keep the current nvme, virtio_net, virtio_scsi, and libbpf survey packet plus the active release-order note reviewable from the tests root through the workflow-backed build-only contract without implying removed `validate-phase12.py`, `check-phase12-*.py`, release-readiness, raw-coverage, focused-libbpf-only replay, cross-build, or `phase12-validate` surfaces that are not on `master`
  * only `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are commit-pinned artifacts, while `virtio_net` and `libbpf` remain shared-tree-only anchors rather than implied fallback maps
  * keep the shared Phase 13 contributor-workflow packet explicit in the tests root too: `Documentation/zigux/README.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-notifier-list-survey.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/validate-phase13-release.py`, `zigux/Makefile`, `make -C zigux phase13-validate`, and `make -C zigux phase13` should continue to keep the current six-test shared-helper release packet reviewable from the tests root while leaving `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, and `Documentation/zigux/phase13-notifier-list-survey.md` as adjacent release-surface evidence rather than extra shared replay steps, instead of leaving the contributor-surface sync, the contributor workflow guide, the four paired slice notes, the four paired survey notes, and the validator-first replay route visible only from docs-root and checklist-facing guidance
  * keep the current Phase 14 smoke packet reviewable through `Documentation/zigux/README.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `make -C zigux phase14-smoke`, `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`, `make -C zigux phase14-test`, `make -C zigux phase14`, and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` so the shared study-only boundary packet stays aligned across the shipped smoke shard, the full replay, the named rollback owner, the freeze-map boundary note, and the docs-root summary without implying a removed validator stack or a direct deep-core port claim
  * keep the Phase 14 shared smoke packet explicit in the tests root: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, and `zigux/tests/phase14_end_to_end_smoke_survey.zig` should continue to keep the exact rollback threshold, automatic return-to-blocked trigger list, shared-surface accounting, and ZAR-to-product transfer rationale visible from the tests root rather than relying on run memory
  * keep the parked Phase 15 governance packet explicit in the tests root too: `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_build.zig`, `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/Makefile`, `zig build test --build-file zigux/tests/phase15_build.zig`, and `make -C zigux phase15` should continue to keep the current freeze-map, review-process, parity-scorecard, and indefinite-C governance packet reviewable through one shared build-and-make route without implying any Architecture Council approval for a freeze-map status change
  * keep new Phase 6 and Phase 7 leaf-helper tests small, explicit, and tied to the owning helper path when those helper lanes reopen
