# zigux/tests

This directory is the home of reusable Zigux parity and differential validation harnesses.

Purpose
- hold shared harness logic before subsystem-specific tests spread through the tree
- keep product-facing validation code separate from ad hoc experiments
- provide the checks for helper parity, ABI assertions, and rollback readiness

Key entrypoints
- `zigux/tests/build.zig`
- `zigux/tests/atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/bitmap_diff.zig`
- `zigux/tests/phase4_build.zig`
- `zigux/tests/phase5_build.zig`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/phase1_bench.zig`
- `zigux/tests/phase6_build.zig`
- `zigux/tests/phase6_checksum.zig`
- `zigux/tests/phase7_build.zig`
- `zigux/tests/phase7_string_helpers.zig`
- `zigux/tests/phase7_cmdline.zig`
- `zigux/tests/phase7_argv_split.zig`
- `zigux/tests/phase7_rbtree.zig`
- `zigux/tests/phase7_rbtree_survey.zig`
- `zigux/tests/phase9_build.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_bitmap_survey.zig`
- `zigux/tests/runtime_trace_events_survey.zig`
- `zigux/tests/runtime_kretprobe_survey.zig`
- `zigux/tests/phase11_build.zig`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `zigux/tests/phase3_abi.zig`
- `zigux/tests/phase14_build.zig`
- `zigux/tests/phase14_ring_buffer_survey.zig`
- `zigux/tests/phase14_skbuff_bridge.zig`
- `zigux/tests/phase14_workqueue_bridge.zig`
- `scripts/zigux/validate-phase3.py`
- `scripts/zigux/validate-phase4.py`
- `Documentation/zigux/phase4-validation-matrix.md`
- `scripts/zigux/phase3_catalog.py --self-test`
- `scripts/zigux/phase3_check_lib.py --self-test`
- `scripts/zigux/generate-phase3-check-wrappers.py --check`
- `scripts/zigux/run-phase3-checks.py --self-test`
- `scripts/zigux/run-phase3-checks.py`

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
- keep the closed Phase 1 host-tools packet explicit in the tests root too: `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `zig build test --build-file zigux/tests/build.zig`, and `zig build bench --build-file zigux/tests/build.zig` should continue to keep the closed helper tranche reviewable from the tests root instead of leaving the host-tools closure stack split across the docs root and scripts root
- prefer discovery-based validation over hard-coded file inventories when adding new Phase 3 slices
- keep the canonical Phase 4 atomic64 wrapper explicit: `zigux/tests/phase4_build.zig` should continue to run `zigux/tests/atomic64_diff.zig` as the roadmap entrypoint, `zigux/tests/atomic64_diff.zig` should remain the thin wrapper over `zigux/tests/runtime_atomic64_diff.zig`, and `Documentation/zigux/phase4-validation-matrix.md` should keep that wrapper-versus-runtime handoff reviewable without cloning the shared replay body
- keep the shared Phase 5 reference-sample checks wired through `zigux/tests/phase5_build.zig` so the four shipped sample-backed surveys stay reviewable without implying runtime-substrate closure
- keep the shared Phase 7 leaf-helper packet wired through `zigux/tests/phase7_build.zig`, including the dedicated `zigux/tests/phase7_rbtree_survey.zig` survey gate, so the landed `string_helpers`, `cmdline`, `argv_split`, and `rbtree` bundle stays reviewable through one bounded runtime-safe entrypoint
- keep the bounded Phase 9 runtime surveys wired through `zigux/tests/phase9_build.zig` so the loader-handoff packet stays reviewable without implying shared runtime substrate closure
- keep the shared-versus-dedicated Phase 11 simple-driver packet explicit in the tests root too: `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/phase11_dw_wdt_suspend_resume.zig`, `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-layout-assert-surface.py`, `scripts/zigux/check-phase11-hvc-validation-flow.py`, `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, and `scripts/zigux/validate-phase11.py` should continue to keep the shared pre-replay starter packet aligned while leaving the dedicated `hvc_console` survey replay separate
- keep the release-facing Phase 12 PMO packet explicit in the tests root too: `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-shared-replay-contract.md`, `Documentation/zigux/phase12-cross-compile-smoke.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-raw-github-coverage.py`, `scripts/zigux/check-phase12-libbpf-focused-replay.py`, `zigux/tests/phase12_raw_github_coverage_manifest.json`, `zigux/tests/phase12_raw_github_coverage_survey.zig`, `zigux/tests/phase12_libbpf_only_build.zig`, `zigux/tests/phase12_build.zig`, `scripts/zigux/validate-phase12.py`, `make -C zigux phase12-validate`, and `make -C zigux phase12` should continue to keep the active-not-closed release posture, the approved `x86_64-linux-musl`, `aarch64-linux-musl`, and `riscv64-linux-musl` smoke set, the compact owner-split and rollback matrix, and the current two commit-pinned versus two shared-tree-only fallback split visible from the tests root instead of leaving that release coordination stack split across the docs root and scripts root
- keep the current Phase 14 smoke packet reviewable through `zigux/tests/phase14_build.zig`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`, `make -C zigux phase14`, and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` so the shared study-only boundary packet stays aligned across the dedicated docs-root and release-boundary smoke helpers, the focused smoke shard, the full replay, the named rollback owner, `Documentation/zigux/phase14-release-boundary-survey.md`, and the docs-root summary instead of widening into ad hoc bridge or deep-core claims
- keep the Phase 14 shared smoke packet explicit in the tests root: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, and `zigux/tests/phase14_end_to_end_smoke_survey.zig` should continue to keep the exact rollback threshold, automatic return-to-blocked trigger list, shared-surface accounting, and ZAR-to-product transfer rationale visible from the tests root rather than relying on run memory
- keep new Phase 6 and Phase 7 leaf-helper tests small, explicit, and tied to the owning helper path when those helper lanes reopen
