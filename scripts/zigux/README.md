# scripts/zigux

This directory holds Zigux-specific bootstrap and validation helpers.

Initial responsibilities
- Zig toolchain policy checks
- bootstrap validation
- committed parity fixture generation and checking
- future ABI/layout guards
- artifact diff helpers for host-side tools

Current bootstrap helpers
- `check-zig-toolchain.py`
- `validate-bootstrap.py`
- `install-zig.py`
- `check-phase1-installer-review-surfaces.py`
- `check-phase1-installer-companion-checks.py`
- `validate-phase1.py`
- `check-phase1-bench.py`
- `validate-phase1-closure.py`
- `validate-phase2.py`
- `validate-phase2-closure.py`
- `check-phase2-tool-manifest-packets.py`
- `validate-phase3.py`
- `validate_phase3_selftest.py`
- `check-phase3-selftest-surface.py`
- `check-phase3-readme-tooling-inventory.py`
- `check-phase3-abi-dump-gate.py`
- `check-phase3-catalog-selftest.py`
- `validate-phase3-policy-unsafe-survey.py`
- `check-phase3-policy-byte-guards.py`
- `validate-phase3-low-level-wrapper-survey.py`
- `validate-phase3-export-uapi-survey.py`
- `validate-phase3-abi-bindings-syntax.py`
- `validate-phase3-abi-header-family-survey.py`
- `survey-phase3-abi-constant-parity.py`
- `artifact_diff.py`
- `check-artifact-diff-contract.py`
- `validate-phase4.py`
- `check-phase4-gate-evidence.py`
- `check-phase4-artifact-diff-determinism.py`
- `check-phase4-workflow-route-counts.py`
- `check-phase6-shared-surface.py`
- `validate-phase7.py`
- `check-phase7-make-wrapper.py`
- `check-phase7-make-wrapper-selftest-alignment.py`
- `check-phase7-argv-split-packet.py`
- `check-phase7-rbtree-parity.py`
- `check-phase7-build-wiring.py`
- `validate-phase8.py`
- `check-phase8-exec-cmd-packet.py`
- `check-phase8-help-kallsyms-packet.py`
- `check-phase8-perf-buffer-poll-gate.py`
- `check-phase9-build-only-surface.py`
- `check-phase10-core-packet.py`
- `check-phase10-ring-packet.py`
- `check-phase10-input-packet.py`
- `check-phase10-mmio-packet.py`
- `check-phase10-mmio-freeze-boundary.py`
- `check-phase11-shared-replay-contract.py`
- `check-phase11-bcm2835-wdt-packet.py`
- `check-phase11-dw-wdt-packet.py`
- `check-phase11-header-boundary-packet.py`
- `check-phase11-hvc-survey-packet.py`
- `check-build-only-phase12-surface.py`
- `validate-phase13-release.py`
- `check-phase13-devres-packet.py`
- `check-phase13-landlock-ruleset-packet.py`
- `check-phase13-notifier-packet.py`
- `validate-phase14.py`
- `check-phase14-docs-root-smoke-summary.py`
- `check-phase14-rollback-threshold-sequencing.py`
- `check-phase14-release-boundary-exact-counts.py`
- `validate-phase15.py`
- `check-phase15-review-process-handoff.py`
- `check-phase15-scripts-readme-alignment.py`
- `run-phase3-checks.py`
- `phase3_catalog.py`
- `phase3_check_lib.py`
- `generate-phase3-check-wrappers.py`
- `check-phase1-parity.py`
- `check-phase2-fixdep-gate.py`
- `check-fixdep-diff.py`
- `check-genksyms-bridge.py`
- `check-phase2-genksyms-bridge-selftest-alignment.py`
- `check-genksyms-crc-diff.py`
- `check-kconfig-bridge.py`
- `check-phase2-kconfig-selftest-alignment.py`
- `check-phase2-tests-readme-alignment.py`
- `check-phase2-cross-selftest-alignment.py`
- `check-phase2-toolchain-pin-scope.py`
- `check-phase2-cross.py`
- `check-mk-elfconfig-diff.py`

Zig toolchain gate
- `check-zig-toolchain.py` verifies that the selected Zig binary exists and satisfies the configured minimum version.
- `check-zig-toolchain.py --self-test` runs built-in parser and version-ordering coverage without needing a local Zig install.

Phase 1 flow
- `validate-phase1.py` checks that the bounded host-side helper inventory under `tools/lib/*.zig`, its committed fixture set, the shared `zigux/tests/build.zig` wiring, and the bootstrap workflow markers stay aligned before the helper parity and benchmark lanes run.
- `validate-phase1-closure.py` confirms the closed Phase 1 packet still matches `Documentation/zigux/phase1-closure.md`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, the shared helper build wiring, and the bootstrap workflow.
- `check-phase1-parity.py` compares the bounded helper outputs against the committed Phase 1 fixture corpus so `bitmap`, `find_bit`, `string`, `rbtree`, and the rest of the closed helper set stay pinned to the current C behavior.
- `check-phase1-bench.py` verifies the benchmark smoke outputs recorded in `zigux/tests/fixtures/phase1_bench_expectations.json` so the helper hot loops keep their checksum-backed replay contract.
- `zig build test --build-file zigux/tests/build.zig` and `zig build bench --build-file zigux/tests/build.zig` remain the executable Phase 1 unit and benchmark gates behind the validator and closure records.
- `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep that same closed host-side helper packet reviewable through the docs-root closure record, the reviewer-facing checklist, the workflow-viability installer, the dedicated installer-review alignment checker, the bootstrap workflow replay, and the Linux-style replay routes instead of leaving the Phase 1 closure stack visible only through direct script and Zig commands.
- `Documentation/zigux/phase1-closure.md` and `zigux/tests/fixtures/phase1_helper_manifest.json` also keep the shared Phase 1 helper sequencing split explicit: `tools/lib/argv_split.zig`, `tools/lib/cmdline.zig`, `tools/lib/ctype.zig`, `tools/lib/hweight.zig`, `tools/lib/list_sort.zig`, `tools/lib/slab.zig`, `tools/lib/str_error_r.zig`, `tools/lib/vsprintf.zig`, and `tools/lib/zalloc.zig` stay parked on shared-replay packet drift only, while `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` keep the only direct helper-local follow-up anchors on current `master`, so shared reminder work should not batch those two sets back together.
- `tools/lib/string.zig`, `Documentation/zigux/phase1-closure.md`, and `zigux/tests/fixtures/phase1_helper_manifest.json` also keep the direct Phase 1 string review packet explicit, including the `memchr_inv()` alias replay, the zero-value prefix-alignment `memchrInv()` follow-up, and the explicit positive-overflow `memparse()` anchor, so those helper-local proofs stay reviewable without widening the shared parity fixture.

Phase 2 flow
- `validate-phase2.py` checks that the bounded Phase 2 helper inventory, fixture set, workflow wiring, and docs markers stay in sync before the parity lanes run.
- `validate-phase2-closure.py` confirms the closed Phase 2 tranche still matches the workflow, the closure docs, and the Phase 2 manifests.
- `check-phase2-genksyms-bridge-selftest-alignment.py --self-test` and `check-phase2-genksyms-bridge-selftest-alignment.py` keep `check-genksyms-bridge.py`, `.github/workflows/zigux-bootstrap.yml`, and the direct `zig test scripts/zigux/genksyms.zig` replay aligned around the shipped self-test evidence for the bounded genksyms bridge lane.
- `check-phase2-tests-readme-alignment.py` keeps `zigux/tests/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/Makefile`, and the Linux-style `make -C zigux phase2-validate` plus `make -C zigux phase2` replay surface aligned around the same bounded toolchain packet.
- `check-phase2-cross-selftest-alignment.py` keeps `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` aligned around the bounded three-target compile matrix.
- `check-phase2-tool-manifest-packets.py --self-test` and `check-phase2-tool-manifest-packets.py` keep `zigux/tests/fixtures/phase2_tool_manifest.json`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned with the committed `fixdep`, `genksyms`, `artifact_tools` (`genksyms_crc` plus `mk_elfconfig`), `kconfig`, and `confdata` packet manifests so the shared Phase 2 tool inventory, self-test route, and live gate wiring stay explicit before the direct Zig replays run.
- `check-phase2-toolchain-pin-scope.py --self-test` and `check-phase2-toolchain-pin-scope.py` keep `scripts/zigux/zig-toolchain-policy.json`, `.github/workflows/zigux-bootstrap.yml`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `zigux/Makefile`, and this scripts index aligned around the current x86_64-linux bootstrap host target, the repo-local `.zig-toolchain` fallback reused by `make -C zigux phase2-toolchain`, `make -C zigux phase2-validate`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, and `make -C zigux phase2`, while the cross-target compile matrix stays a separate Phase 2 surface.
- `check-phase2-fixdep-gate.py --self-test` and `check-phase2-fixdep-gate.py` keep `.github/workflows/zigux-bootstrap.yml`, `check-fixdep-diff.py`, and the direct `zig test scripts/zigux/fixdep.zig` replay aligned around the shipped Phase 2 fixdep gate packet before the bounded parity replay runs.
- `check-fixdep-diff.py` compares the bounded `fixdep.zig` output against the committed fixture set, including `zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt`.
- `check-genksyms-bridge.py` exercises the bounded `genksyms.zig` bridge parity lane.
- `check-genksyms-crc-diff.py` checks the bounded `genksyms_crc.zig` artifact lane.
- `check-phase2-kconfig-selftest-alignment.py --self-test` and `check-phase2-kconfig-selftest-alignment.py` keep `check-kconfig-bridge.py`, `scripts/zigux/validate-phase2.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned around the shipped kconfig self-test hooks before the bridge and Zig replays run, so the shared Phase 2 validator, the Linux-style `phase2-kconfig` route, and the workflow-backed replay surface stay on the same bounded packet.
- `check-kconfig-bridge.py` covers the bounded `kconfig/conf_bridge.zig` and `kconfig/confdata_bridge.zig` bridge lanes.
- `check-phase2-cross.py` runs the bounded Phase 2 cross-target compile checks.
- `check-mk-elfconfig-diff.py` covers the bounded `mk_elfconfig.zig` artifact parity lane.

Phase 3 flow
- `validate-phase3.py` checks that the discovered shared `abi` slice, its manifest-backed packet, the docs markers, the wrapper template stubs, the focused low-level-wrapper markers, and the related support-script gates stay aligned before the ABI replay routes run.
- `validate_phase3_selftest.py` reruns the Phase 3 validator-support packet in isolation so the docs-root, scripts-root, tests-root, and make-route expectations stay honest beside the shared ABI substrate.
- The live support packet inside that same validator-first route is `check-phase3-selftest-surface.py`, `check-phase3-readme-tooling-inventory.py`, `check-phase3-catalog-selftest.py`, `check-phase3-abi-dump-gate.py`, `validate-phase3-policy-unsafe-survey.py`, `check-phase3-policy-byte-guards.py`, `validate-phase3-low-level-wrapper-survey.py`, `validate-phase3-export-uapi-survey.py`, `validate-phase3-abi-bindings-syntax.py`, `validate-phase3-abi-header-family-survey.py`, `survey-phase3-abi-constant-parity.py`, `phase3_catalog.py`, `phase3_check_lib.py`, `generate-phase3-check-wrappers.py`, and `run-phase3-checks.py`; the generated `check-phase3-*.py` wrappers stay as compatibility entrypoints derived from the discovered slice catalog instead of a second hand-maintained survey list.
- `make -C zigux phase3-validate` keeps the shared Phase 3 validator, the ABI-bindings syntax guard, the constant-parity survey, the header-family survey, the policy-byte guard, the low-level-wrapper survey, the export/UAPI survey, the selftest review surface, and the catalog-wrapper drift checks wired through the Linux-style validation entrypoint before the ABI replay routes run.
- `validate-phase3-export-uapi-survey.py` keeps the export shim and UAPI boundary packet aligned around `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `include/linux/zigux.h`, `include/zigux/abi.h`, `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `zigux/tests/phase3_export_uapi.zig`, `zigux/tests/phase3_export_uapi_build.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, and the workflow hooks that rerun that same survey surface, while `validate-phase3-abi-header-family-survey.py`, `Documentation/zigux/phase3-abi-header-family-survey.md`, and `Documentation/zigux/phase3-abi-h-boundary-next-step.md` keep the landed `include/zigux/abi.h` review packet explicit beside that same starter `zigux/uapi/dev_t.zig` surface instead of leaving the header-family follow-through implicit.
- `python3 scripts/zigux/phase3_catalog.py --self-test`, `python3 scripts/zigux/phase3_catalog.py --audit-doc-sync`, and `make -C zigux phase3-selftest` remain a manual or targeted safety check instead of duplicating the default validation route, while `python3 scripts/zigux/run-phase3-checks.py --slug abi`, `zig build phase3-test --build-file zigux/tests/build.zig`, `zig build phase3-dump --build-file zigux/tests/build.zig`, and `make -C zigux phase3` rerun the shared ABI interop, compile, and dump packet.

Phase 4 flow
- `validate-phase4.py` checks that the shared Phase 4 rollback-readiness packet stays aligned across `scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/check-phase4-artifact-diff-determinism.py`, `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-workflow-route-counts.py`, `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, `zigux/tests/bitmap_diff.zig`, `zigux/tests/phase4_bitmap_diff_manifest.json`, `zigux/tests/phase4_bitmap_diff_survey.zig`, `zigux/tests/phase4_bitmap_live_helper_replay.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, `zigux/tests/phase4_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` before the rollback and survey replays run.
- `check-artifact-diff-contract.py` keeps the host-side artifact-diff contract explicit before the shared Phase 4 packet reuses it.
- `check-phase4-gate-evidence.py` keeps `Documentation/zigux/phase4-gate-evidence.md` aligned with the exact-readback packet and the bounded runtime-versus-bitmap rollback survey surfaces.
- `make -C zigux phase4-validate` reruns the validator-first Phase 4 route, including `scripts/zigux/check-artifact-diff-contract.py`, `scripts/zigux/check-phase4-artifact-diff-determinism.py`, `scripts/zigux/check-phase4-gate-evidence.py`, and `scripts/zigux/check-phase4-workflow-route-counts.py`, before the shared `zigux/tests/phase4_build.zig` replay.
- `zig build test --build-file zigux/tests/phase4_build.zig`, `make -C zigux phase4`, and `make -C zigux phase4-bitmap-live-helper-replay` keep the shared rollback replays explicit, while `zigux/tests/phase4_perf_baseline_manifest.json` plus `zigux/tests/phase4_perf_baseline_survey.zig` carry the approved local-only benchmark commands and acceptable limits, the Validation and Perf Team stays named here as the decision owner for any broader shared-CI perf promotion, the ABI and Runtime Team plus Shared Subsystems Pod stay named here as the coordination owners for that policy call, and the shared reminder surfaces keep that promotion explicitly pending, so the rollback packet stays measurable without implying a shipped Phase 4 slowdown budget.