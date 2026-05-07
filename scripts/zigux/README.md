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
- `survey-phase3-abi-constant-parity.py`
- `artifact_diff.py`
- `check-artifact-diff-contract.py`
- `validate-phase4.py`
- `check-phase4-gate-evidence.py`
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
- `check-phase9-build-only-surface.py`
- `check-phase10-core-packet.py`
- `check-phase10-ring-packet.py`
- `check-phase10-input-packet.py`
- `check-phase10-mmio-packet.py`
- `check-phase11-shared-replay-contract.py`
- `check-phase11-header-boundary-packet.py`
- `check-build-only-phase12-surface.py`
- `validate-phase13-release.py`
- `check-phase13-devres-packet.py`
- `check-phase13-landlock-ruleset-packet.py`
- `check-phase13-notifier-packet.py`
- `validate-phase14.py`
- `check-phase14-docs-root-smoke-summary.py`
- `check-phase14-rollback-threshold-sequencing.py`
- `check-phase14-release-boundary-exact-counts.py`
- `check-phase15-review-process-handoff.py`
- `check-phase15-scripts-readme-alignment.py`
- `run-phase3-checks.py`
- `phase3_catalog.py`
- `phase3_check_lib.py`
- `generate-phase3-check-wrappers.py`
- `check-phase1-parity.py`
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

Phase 2 flow
- `validate-phase2.py` checks that the bounded Phase 2 helper inventory, fixture set, workflow wiring, and docs markers stay in sync before the parity lanes run.
- `validate-phase2-closure.py` confirms the closed Phase 2 tranche still matches the workflow, the closure docs, and the Phase 2 manifests.
- `check-phase2-genksyms-bridge-selftest-alignment.py --self-test` and `check-phase2-genksyms-bridge-selftest-alignment.py` keep `check-genksyms-bridge.py`, `.github/workflows/zigux-bootstrap.yml`, and the direct `zig test scripts/zigux/genksyms.zig` replay aligned around the shipped self-test evidence for the bounded genksyms bridge lane.
- `check-phase2-tests-readme-alignment.py` keeps `zigux/tests/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/Makefile`, and the Linux-style `make -C zigux phase2-validate` plus `make -C zigux phase2` replay surface aligned around the same bounded toolchain packet.
- `check-phase2-cross-selftest-alignment.py` keeps `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` aligned around the bounded three-target compile matrix.
- `check-phase2-tool-manifest-packets.py --self-test` and `check-phase2-tool-manifest-packets.py` keep `zigux/tests/fixtures/phase2_tool_manifest.json`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned with the committed `fixdep`, `genksyms`, and `kconfig` packet manifests so the shared Phase 2 tool inventory, self-test route, and live gate wiring stay explicit before the direct Zig replays run.
- `check-phase2-toolchain-pin-scope.py --self-test` and `check-phase2-toolchain-pin-scope.py` keep `scripts/zigux/zig-toolchain-policy.json`, `.github/workflows/zigux-bootstrap.yml`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, and this scripts index aligned around the current x86_64-linux bootstrap host target while the cross-target compile matrix stays a separate Phase 2 surface.
- `check-fixdep-diff.py` compares the bounded `fixdep.zig` output against the committed fixture set, including `zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt`.
- `check-genksyms-bridge.py` exercises the bounded `genksyms.zig` bridge parity lane.
- `check-genksyms-crc-diff.py` checks the bounded `genksyms_crc.zig` artifact lane.
- `check-phase2-kconfig-selftest-alignment.py --self-test` and `check-phase2-kconfig-selftest-alignment.py` keep `check-kconfig-bridge.py`, `scripts/zigux/validate-phase2.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned around the shipped kconfig self-test hooks before the bridge and Zig replays run, so the shared Phase 2 validator, the Linux-style `phase2-kconfig` route, and the workflow-backed replay surface stay on the same bounded packet.
- `check-kconfig-bridge.py` covers the bounded `kconfig/conf_bridge.zig` and `kconfig/confdata_bridge.zig` bridge lanes.
- `check-phase2-cross.py` runs the bounded Phase 2 cross-target compile checks.
- `check-mk-elfconfig-diff.py` covers the bounded `mk_elfconfig.zig` artifact parity lane.

Phase 7 flow
- the current shared Phase 7 review surface on `master` is `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase7-string-helpers-slice.md`, `Documentation/zigux/phase7-cmdline-slice.md`, `Documentation/zigux/phase7-argv-split-slice.md`, `Documentation/zigux/phase7-rbtree-slice.md`, `samples/zigux/README.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-argv-split-packet.py`, `scripts/zigux/check-phase7-rbtree-parity.py`, `scripts/zigux/check-phase7-build-wiring.py`, `zigux/tests/phase7_build.zig`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_survey.zig`, `zigux/tests/phase7_string_helpers_sample_boundary.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.
- `make -C zigux phase7-validate` keeps the shared Phase 7 validator plus the dedicated make-wrapper, make-wrapper selftest-alignment, argv_split packet, rbtree parity, and build-wiring checkers wired through the Linux-style validation entrypoint.

Phase 8 flow
- the current shared Phase 8 review surface on `master` is `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase8-exec-cmd-slice.md`, `Documentation/zigux/phase8-help-slice.md`, `Documentation/zigux/phase8-kallsyms-slice.md`, `Documentation/zigux/phase8-libbpf-cpu-mask-slice.md`, `Documentation/zigux/phase8-bpf-type-names-slice.md`, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `scripts/zigux/validate-phase8.py`, `scripts/zigux/check-phase8-exec-cmd-packet.py`, `scripts/zigux/check-phase8-help-kallsyms-packet.py`, `zigux/tests/phase8_build.zig`, `zigux/tests/phase8_exec_cmd.zig`, `zigux/tests/phase8_exec_cmd_only_build.zig`, `zigux/tests/phase8_help.zig`, `zigux/tests/phase8_help_only_build.zig`, `zigux/tests/phase8_kallsyms.zig`, `zigux/tests/phase8_kallsyms_only_build.zig`, `zigux/tests/phase8_cpu_mask.zig`, `zigux/tests/phase8_logging.zig`, `zigux/tests/phase8_pin_path.zig`, `zigux/tests/phase8_bpf_type_names.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, `zigux/tests/phase8_libbpf_segments.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.
- `make -C zigux phase8-validate` keeps `validate-phase8.py` plus the focused `check-phase8-exec-cmd-packet.py` and `check-phase8-help-kallsyms-packet.py` checkers wired through the Linux-style validation entrypoint before the tooling replays run.
