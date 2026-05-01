# scripts/zigux

This directory holds Zigux-specific bootstrap and validation helpers.

Initial responsibilities
- Zig toolchain policy checks
- bootstrap validation
- committed parity fixture generation and checking
- future ABI/layout guards
- artifact diff helpers for host-side tools

Current bootstrap helpers
- `artifact_diff.py`
- `check-artifact-diff-contract.py`
- `check-zig-toolchain.py`
- `validate-bootstrap.py`
- `install-zig.py`
- `validate-phase1.py`
- `check-phase1-bench.py`
- `validate-phase1-closure.py`
- `validate-phase2.py`
- `validate-phase2-closure.py`
- `validate-phase3.py`
- `check-phase3-abi.py`
- `validate-phase4.py`
- `check-phase4-gate-evidence.py`
- `validate-phase5.py`
- `validate-phase6.py`
- `validate-phase7.py`
- `check-phase7-build-inventory.py`
- `check-phase7-make-wrapper.py`
- `check-phase7-cmdline-parity.py`
- `check-phase7-rbtree-parity.py`
- `validate-phase8.py`
- `check-phase8-tests-readme-alignment.py`
- `validate-phase9.py`
- `check-phase9-validation-flow.py`
- `check-phase9-loader-substrate-plan.py`
- `check-phase9-runtime-loader-commit-alignment.py`
- `check-phase9-loader-non-owner-boundary.py`
- `validate-phase10.py`
- `validate-phase10-closure.py`
- `check-phase11-build-inventory.py`
- `validate-phase11.py`
- `check-phase12-build-inventory.py`
- `check-phase12-libbpf-snapshot.py`
- `check-phase12-libbpf-packet.py`
- `validate-phase12.py`
- `validate-phase13-release.py`
- `validate-phase14.py`
- `validate-phase3-roadmap-gap-survey.py`
- `validate-phase3-export-uapi-survey.py`
- `validate-phase3-low-level-wrapper-survey.py`
- `validate-phase3-policy-unsafe-survey.py`
- `validate_phase3_header_binding_markers.py`
- `validate_phase3_selftest.py`
- `run-phase3-checks.py`
- `phase3_catalog.py`
- `check-phase1-parity.py`
- `check-fixdep-diff.py`
- `check-genksyms-bridge.py`
- `check-genksyms-crc-diff.py`
- `check-kconfig-bridge.py`
- `check-phase2-cross.py`
- `check-mk-elfconfig-diff.py`
- `check-phase6-base64-c-parity.py`
- `check-phase6-bsearch-c-parity.py`

Zig toolchain gate
- `check-zig-toolchain.py` verifies that the selected Zig binary exists and satisfies the configured minimum version.
- `check-zig-toolchain.py --self-test` runs built-in parser and version-ordering coverage without needing a local Zig install.

Phase 4 flow
- `make -C zigux phase4-validate` is the validator-first entrypoint for the current rollback-readiness packet.
- `validate-phase4.py` keeps the current gate-definition and survey packet aligned across `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/bitmap_diff.zig`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_test_fsmount_survey.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, `Documentation/zigux/phase4-validation-matrix.md`, and the paired workflow plus Makefile hooks.
- `check-phase4-gate-evidence.py` keeps `Documentation/zigux/phase4-gate-evidence.md` fail-closed across the broader survey-file and docs-root, scripts-root, and tests-root blob pins recorded for the same Phase 4 packet.
- `artifact_diff.py --self-test` and `check-artifact-diff-contract.py` stay in the same Phase 4 flow so the bounded host-side diff tooling fails closed before the rollback gates claim aligned evidence.
- `make -C zigux phase4-test-fsmount-survey` and `make -C zigux phase4-perf-baseline-survey` keep the two manifest-backed survey gates reviewable without widening them into landed Zig samples or approved benchmark thresholds.
- `phase4-test-fsmount-survey-tests` and `phase4-perf-baseline-survey-tests` remain explicit in `phase4_build.zig`, alongside `phase4-runtime-atomic64-diff-survey-tests`, so the shared replay surface stays measurable instead of dissolving into prose-only notes.
- `Documentation/zigux/phase4-validation-matrix.md` remains the published rollback-owner, local replay, and reversible-delivery evidence note for the current packet, and `Documentation/zigux/phase4-gate-evidence.md` remains the paired exact readback ledger for that same flow.
- `perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land` stays the explicit survey posture until one bounded benchmark command and one acceptable limit land for each shipped rollback gate.

Phase 2 flow
- `make -C zigux phase2-tools` is the Linux-style entrypoint for the bounded fixdep, genksyms, genksyms CRC, and mk_elfconfig replay packet.
- that direct `phase2-tools` path now begins with `artifact_diff.py --self-test` and `check-artifact-diff-contract.py`, so shared artifact-diff drift fails before the tool-specific self-tests, parity replays, and Zig unit lanes run.
- `make -C zigux phase2-kconfig` is the Linux-style bridge entrypoint for the bounded `kconfig/conf_bridge.zig` and `kconfig/confdata_bridge.zig` packet.
- `make -C zigux phase2-cross` is the Linux-style compile entrypoint for the closed three-target cross-arch packet.
- `make -C zigux phase2` keeps the whole bounded tranche callable as one validator-first bundle across the shared validator, tool, kconfig, and cross-target packets.
- `artifact_diff.py --self-test` exercises the shared text, JSON, SHA-256, and missing-file comparison paths before the bounded Phase 2 artifact lanes run.
- `check-artifact-diff-contract.py` keeps the outward artifact-diff CLI surface reviewable inside the closed Phase 2 packet so missing-file, malformed-JSON, and SHA-256 contract drift cannot hide behind the helper's built-in self-test.
- `validate-phase1.py` now also checks that `zigux/tests/fixtures/phase1_helpers.json` keeps the exact committed top-level helper sections and evidence-key shape, so stale Phase 1 expected-output drift fails before parity replay.
- `validate-phase2.py` checks that the bounded Phase 2 helper inventory, fixture set, workflow wiring, and docs markers stay in sync before the parity lanes run.
- `validate-phase2-closure.py` confirms the closed Phase 2 tranche still matches the workflow, the closure docs, and the Phase 2 manifests.
- `check-fixdep-diff.py --self-test` exercises the bounded fixdep checker packet itself before the shared `phase2-tools` and bootstrap workflow entrypoints replay live artifacts, so case-manifest drift, explicit-tool drift, and unsupported stdout-mode changes cannot hide behind a locally passing parity run.
- `check-fixdep-diff.py` compares the bounded `fixdep.zig` output against the committed fixture set, including the multi-target, escaped-whitespace, comment-only no-target, and missing-dependency failure artifacts under `zigux/tests/fixtures/fixdep/`, reruns both the C tool and Zig tool to prove repeat-run artifact determinism, and now also fails if any success-path fixdep case starts emitting unexpected stderr noise.
- `check-genksyms-bridge.py --self-test` exercises the bounded `genksyms` bridge checker packet itself before the Linux-style `phase2-tools` entrypoint replays live bridge artifacts, so missing-expected-fixture drift, duplicate expected-fixture wiring, stderr-mode contract drift, and repeat-run compare coverage cannot hide behind a locally passing bridge replay.
- `check-genksyms-bridge.py` exercises the bounded `genksyms.zig` bridge parity lane, including success-path stderr silence and repeat-run stderr determinism for the stdout-json bridge fixtures.
- that same committed bridge packet currently spans 26 reviewable cases under `zigux/tests/fixtures/genksyms_bridge/`, including the minimal, clustered short-inline, abbreviated long-option, lone-dash passthrough, explicit-terminator positional, missing-argument, and reference-limit fixtures that keep the widened wrapper-first surface explicit.
- `check-genksyms-crc-diff.py --self-test` exercises the bounded `genksyms_crc` checker packet itself before the Linux-style `phase2-tools` entrypoint replays the live artifact lane, so explicit-tool passthrough drift, mismatch-contract drift, and repeat-run compare coverage cannot hide behind local compiler or Zig availability.
- `check-genksyms-crc-diff.py` checks the bounded `genksyms_crc.zig` artifact lane and now proves repeat-run JSON determinism for both the bounded C harness and Zig tool before fixture comparison.
- `check-kconfig-bridge.py --self-test` exercises the bounded kconfig bridge checker packet itself before the Linux-style `phase2-kconfig` entrypoint replays the live bridge artifacts.
- `check-kconfig-bridge.py` covers the bounded `kconfig/conf_bridge.zig` and `kconfig/confdata_bridge.zig` bridge lanes and now proves repeat-run JSON determinism for both bridge outputs before fixture comparison.
- `check-phase2-cross.py --self-test` exercises the bounded cross-target checker packet itself before the Linux-style `phase2-cross` entrypoint replays live Zig compiles, so duplicate tool entries, duplicate requested targets, unexpected explicit targets, manifest-count drift, duplicate manifest targets, and explicit-target failure drift cannot hide behind local tool availability.
- `check-phase2-cross.py` runs the bounded Phase 2 cross-target compile checks.
- `check-mk-elfconfig-diff.py --self-test` exercises the bounded mk_elfconfig checker packet itself before the Linux-style `phase2-tools` entrypoint replays the live artifact lane, so fixture-shape and explicit-tool drift cannot hide behind local compiler or Zig availability.
- `check-mk-elfconfig-diff.py` covers the bounded `mk_elfconfig.zig` artifact lane and now proves repeat-run JSON determinism for both the bounded C tool and Zig tool before fixture comparison.
- `check-phase1-parity.py` now reruns the bounded C harness after fixture comparison so the shared Phase 1 parity artifact also proves repeat-run JSON determinism instead of only a single-pass match.
- `check-phase1-bench.py --self-test` exercises the bounded Phase 1 benchmark checker itself before the live benchmark smoke runs, so parser, expected-key, and undeclared-key drift cannot hide behind a locally passing Zig bench replay.

Phase 3 flow
- `validate-phase3-roadmap-gap-survey.py` checks that `Documentation/zigux/phase3-roadmap-gap-survey.md` stays aligned with the live repo-backed Phase 3 substrate, the published README note, the current export shim and current `zigux/uapi/version.zig` boundary, the current roadmap-backed `rbtree` gap, and the already-landed Phase 1 plus Phase 7 `rbtree` evidence that still falls short of a Phase 3 boundary-facing packet.
- `validate-phase3-roadmap-gap-survey.py --self-test` exercises the survey-marker and README-hook checks without needing the full repo tree.
- `validate-phase3-export-uapi-survey.py` checks that `Documentation/zigux/phase3-export-uapi-boundary-survey.md` stays aligned with the live export-shim and bounded `zigux/uapi/version.zig` surface, the published README notes, and the shared `make -C zigux phase3-validate` entrypoint.
- `validate-phase3-export-uapi-survey.py --self-test` exercises the export-shim and UAPI survey-marker checks without needing the full repo tree.
- `validate-phase3-policy-unsafe-survey.py` checks that `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md` stays aligned with the live layout-assert, panic-policy, allocator-policy, typed interop-policy, narrow-unsafe, and scoped MMIO packet plus the published docs-index and scripts-index hooks that keep that bounded survey visible.
- `validate-phase3-policy-unsafe-survey.py --self-test` exercises the policy, narrow-unsafe, and MMIO survey-marker checks without needing the full repo tree, and it now emits its own `PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass` token so isolated validator coverage stays distinguishable from a live survey replay.
- `validate-phase3.py` now requires the focused `phase3-policy-unsafe` build and test files plus the published `PHASE3_POLICY_UNSAFE_GATE` ABI-slice marker, so the landed policy and unsafe substrate no longer hides only inside the broader ABI replay and keeps the dedicated interop-policy unsafe-byte decoding gate reviewable on its own.
- the same validator now keeps `zigux/helpers/layout_assert.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/mmio.zig`, `zigux/unsafe/narrow.zig`, `zigux/tests/phase3_policy_unsafe.zig`, and `zigux/tests/phase3_policy_unsafe_build.zig` aligned with `zigux/tests/fixtures/phase3_abi_manifest.json` and `Documentation/zigux/phase3-abi-slice.md`, so allocator-owned init and reset requirements plus the scoped narrow-unsafe and MMIO helper path cannot drift out of the published packet silently.
- `validate_phase3_header_binding_markers.py` keeps the shared ABI header and bindings packet fail-closed across `include/zigux/abi.h`, `include/linux/zigux.h`, and `zigux/bindings/abi.zig`, and `validate_phase3_selftest.py` keeps the dedicated Phase 3 source-marker and survey-gate replay packet executable on its own, so the broader ABI validator does not hide those helper-local checks behind import-only coverage.
- the same validator surface now also carries the latest focused policy evidence: `zigux/tests/phase3_policy_unsafe.zig` covers overflow-checked unsafe address math, and the Phase 3 source-audit self-test keeps the layout-assert, panic-policy, allocator-policy, and narrow-unsafe markers reviewable even when the full repo tree is not under replay.
- the same validator now also treats the focused low-level wrapper gate as a real anti-regression surface instead of a presence-only file list: it restores the shared self-test import path, checks the exact exported atomic, barrier, and MMIO helper surface against the published Phase 3 ABI slice, and still checks the scoped `read16`, `write16`, `read32`, and `write32` MMIO entry points plus the low-level replay’s strong compare-exchange success and mismatch coverage, weak compare-exchange retry and mismatch coverage, barrier probe, denied-scope, and allowed scoped-MMIO assertions so width-specific, scope-specific, or undocumented wrapper-surface drift fails before Phase 3 review claims stay green.

Phase 5 flow
- `validate-phase5.py` keeps the shipped Phase 5 contributor packet aligned across `samples/zigux/README.md`, the four sample-backed survey notes, the four manifest-backed surveys, `zigux/tests/phase5_build.zig`, `zigux/Makefile`, and the bootstrap workflow before any shared sample replay claims stay green.
- `validate-phase5.py --self-test` exercises the sample-backed packet drift checks in a temporary fixture tree and fails if `surveyed_commit` sync, survey-build-summary evidence, manifest review-prompt groups, or the recorded sample-test command drift out of the shared Phase 5 contributor packet.
- `make -C zigux phase5-validate` is the validator-first entrypoint for the approved sample ports, reviewable Zigux idioms, contributor guidance, and `Documentation/zigux` material that Phase 5 ships today.
- `make -C zigux phase5` and `zig build test --build-file zigux/tests/phase5_build.zig --summary all` are the shared replay surface for the four roadmap-backed reference samples after the validator gate passes.
- the focused one-family replays stay explicit too: `zig test samples/zigux/bytestream_fifo.zig`, `zig test samples/zigux/kobject_example.zig`, `zig test samples/zigux/kretprobe_example.zig`, and `zig test samples/zigux/trace_events_sample.zig` cover the direct sample roots, while `zig test zigux/tests/phase5_bytestream_fifo_survey.zig`, `zig test zigux/tests/phase5_kobject_example_survey.zig`, `zig test zigux/tests/phase5_kretprobe_example_survey.zig`, and `zig test zigux/tests/phase5_trace_events_sample_survey.zig` keep the paired manifest-backed survey packet reviewable for the same sample family without requiring the full shared bundle.
- `zigux/tests/phase5_build.zig` is the shared build entrypoint for the bytestream FIFO, kobject, kretprobe, and trace-events sample packets, including their paired direct-sample and manifest-backed survey replays.
- `samples/zigux/README.md` is the contributor-facing sample-root catalog for the approved Phase 5 anchors and the explicit boundary that keeps later `runtime_*` starters out of the sample-pattern lane.
- the same Phase 5 flow also keeps the shipped sample-root boundary explicit: current `master` still ships no `samples/zigux/*string*` or `samples/zigux/*cmdline*` reference sample, and `samples/zigux/runtime_bitmap.zig` plus `samples/zigux/runtime_bitmap_loader.zig` stay cataloged as the separate Phase 9 runtime bitmap survey packet rather than a fifth approved Phase 5 sample.

Phase 6 flow
- `validate-phase6.py` keeps the shipped Phase 6 leaf-helper packet aligned across `scripts/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase6-helper-parity-catalog.md`, `zigux/tests/phase6_helper_parity_manifest.json`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, the bootstrap workflow, and the four helper-local slice notes before any shared replay claims stay green.
- `validate-phase6.py --self-test` exercises the shared Phase 6 marker walk in a compact synthetic tree and fails if catalog or manifest provenance or helper-local fixture evidence drifts.
- `make -C zigux phase6-validate` is the validator-first entrypoint for the current Phase 6 review packet.
- `make -C zigux phase6` is the shared replay path for the bounded `base64`, `bsearch`, `checksum`, and `hexdump` helper tests after the validator passes.
- the per-helper perf targets stay reviewable as explicit make entrypoints: `make -C zigux phase6-base64-perf`, `make -C zigux phase6-bsearch-perf`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf`.
- `check-phase6-base64-c-parity.py` and `check-phase6-bsearch-c-parity.py` remain the two external parity spot checks for the portability-sensitive helper slices.

Phase 7 flow
- `validate-phase7.py` keeps the shipped runtime-safe leaf-helper packet aligned across `scripts/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, the four Phase 7 slice notes, `zigux/tests/phase7_build.zig`, `zigux/tests/fixtures/phase7_build_inventory.json`, `zigux/Makefile`, the bootstrap workflow, the dedicated helper and survey tests, the repo-root manifest-backed survey packet, and the four helper roots in `lib/`.
- `validate-phase7.py --self-test` exercises the shared Phase 7 marker walk in a compact synthetic tree and fails if the helper-local review packet, repo-root survey packet, workflow hooks, or build wiring drift.
- `check-phase7-build-inventory.py --self-test` and `check-phase7-build-inventory.py` keep the committed `zigux/tests/fixtures/phase7_build_inventory.json` snapshot aligned with the shared `zigux/tests/phase7_build.zig` helper bundle before the broader Phase 7 replay runs.
- `check-phase7-make-wrapper.py --self-test` and `check-phase7-make-wrapper.py` keep the published `make -C zigux phase7-validate`, `make -C zigux phase7-test`, and `make -C zigux phase7` wrapper expansions aligned with the validator-first Phase 7 flow before the broader helper replay runs.
- `check-phase7-cmdline-parity.py` remains the external parity spot check for the committed `zigux/tests/fixtures/phase7_cmdline.json` fixture against the bounded `lib/cmdline.c` harness replay.
- `check-phase7-rbtree-parity.py` remains the external parity spot check for the committed `zigux/tests/fixtures/phase7_rbtree.json` fixture against the bounded `lib/rbtree.c` harness replay.
- `make -C zigux phase7-validate` is the validator-first entrypoint for the current Phase 7 flow.
- `make -C zigux phase7-test` is the shared replay path after the validator, build-inventory, make-wrapper, and parity gates pass.
- `make -C zigux phase7` keeps the one-command bundle aligned with the published review path instead of bypassing the fail-closed validator.
- `zig build test --build-file zigux/tests/phase7_build.zig --summary all` is the shared build replay for the current Phase 7 helper tranche.
- `zigux/tests/phase7_build.zig` is the shared build entrypoint for `string_helpers`, `cmdline`, `argv_split`, and `rbtree`.
- `zigux/tests/phase7_string_helpers_survey.zig` and `zigux/tests/phase7_cmdline_survey.zig` stay standalone so the helper-only string and cmdline slices keep their roadmap-backed review notes explicit without widening into extra helper-local bootstrap rules or later-phase sample claims.
- `zigux/tests/phase7_argv_split_manifest.json` and `zigux/tests/phase7_rbtree_manifest.json` stay as the repo-root survey packet inputs for the manifest-backed `argv_split` and `rbtree` review surfaces.
- `Documentation/zigux/phase7-rbtree-slice.md` remains the published helper-local review note for the `rbtree` packet.
- helper-only string and cmdline slices keep their roadmap-backed review notes explicit and separate from sample-root or later-phase runtime claims.
- `phase7_build.zig` keeps setting those survey runs to `repo_root` so the manifest-backed review packet stays truthful.

Phase 8 flow
- `validate-phase8.py` keeps the parked repo-hosted tooling packet aligned across `Documentation/zigux/phase8-exec-cmd-slice.md`, `Documentation/zigux/phase8-help-slice.md`, `Documentation/zigux/phase8-kallsyms-slice.md`, `Documentation/zigux/phase8-libbpf-cpu-mask-slice.md`, `Documentation/zigux/phase8-bpf-type-names-slice.md`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, and `Documentation/zigux/phase8-perf-buffer-poll-slice.md` so the shared review surface stays explicit.
- `check-phase8-tests-readme-alignment.py` keeps `zigux/tests/README.md`, `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `zigux/tests/phase8_build.zig`, and `zigux/Makefile` aligned with the shared Phase 8 perf-buffer poll packet and the validator-first `phase8-validate` hooks.
- `make -C zigux phase8-validate` is the validator-first entrypoint for the current Phase 8 flow.
- `zigux/tests/phase8_exec_cmd_only_build.zig`, `zigux/tests/phase8_help_only_build.zig`, `zigux/tests/phase8_kallsyms_only_build.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, `zigux/tests/phase8_bridge_boundary_survey.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_bpf_type_names.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, and `zigux/tests/phase8_build.zig` keep the focused and shared replay paths visible in one place.
- `tools/lib/subcmd/exec-cmd.zig`, the deferred execution notes around `execvp()`, and the separate `kernel/workqueue.c` freeze boundary remain helper-only review surfaces rather than new process-launch claims.
- the segmented libbpf packet stays bounded to helper-first slices such as `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/pin_path.zig`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `tools/lib/bpf/zigux_segments/type_names.zig`, and `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig` plus the shared `phase8-libbpf-segment-survey.md`, `phase8-userspace-kernel-bridge-boundary-survey.md`, and `phase8-perf-buffer-poll-slice.md` notes.
- `zigux/tests/phase8_bridge_boundary_survey.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_bpf_type_names.zig`, and `zigux/tests/phase8_perf_buffer_poll.zig` keep the bounded bridge-boundary, file-path-and-handle, type-name, and wait-result review surfaces explicit inside that same tooling packet.
- `make -C zigux phase8-test` and `zig build test --build-file zigux/tests/phase8_build.zig --summary all` remain the shared replay path after the validator passes.

Phase 9 flow
- `validate-phase9.py --self-test` exercises the shared runtime marker walk in a compact synthetic tree before the live runtime packet is trusted.
- `validate-phase9.py` keeps the current runtime pilot packet aligned across `scripts/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, the four runtime survey families, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/tests/runtime_loader_non_owner_boundary_survey.zig`, `zigux/tests/phase9_build.zig`, `zigux/Makefile`, and the bootstrap workflow so the manifest-backed catalog, ownership map, and non-owner boundary survey stay reviewable.
- `check-phase9-validation-flow.py`, `check-phase9-loader-substrate-plan.py`, `check-phase9-runtime-loader-commit-alignment.py`, and `check-phase9-loader-non-owner-boundary.py` keep the validator-first route, the shared loader substrate-plan packet, the shared loader surveyed-commit packet, and the Phase 2 plus Phase 3 non-owner boundary explicit before the broader Phase 9 replay claims stay green.
- `make -C zigux phase9-validate` is the validator-first entrypoint for the current Phase 9 flow.
- `make -C zigux phase9` and `zig build test --build-file zigux/tests/phase9_build.zig --summary all` are the shared replay path after the validator passes.
- `Documentation/zigux/phase9-runtime-loader-gap-survey.md` remains the shared loader-gap review note for the runtime packet.
- `zigux/tests/runtime_loader_non_owner_boundary_survey.zig` remains the focused replay that keeps the Phase 2 config-surface and Phase 3 export-boundary references explicit around the same runtime packet instead of letting those non-owner surfaces fade into prose-only context.
- the current Phase 9 review surface keeps the roadmap's selftest-hook markers explicit across the shipped sample, manifest-backed survey, and shared build entrypoint.
- the current runtime starter remains a bounded lifecycle-parity posture rather than a claim of live loadable-module execution.

Phase 10 flow
- `validate-phase10.py` keeps the wider Phase 10 flow aligned across `scripts/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, `zigux/tests/README.md`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_input_manifest.json`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_mmio.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, and `zigux/tests/phase10_virtio_mmio.zig` so the current Phase 10 ring-plus-input-plus-MMIO lab packet stays reviewable through one shared validation surface instead of drifting into isolated file-local claims.
- `validate-phase10.py --self-test` exercises the shared marker walk in a compact synthetic tree and fails if the published Phase 10 flow, `make -C zigux phase10-validate`, `phase10_build.zig`, the ring manifest-backed packet, the ring reset-reuse replay, the blocked registration-lifecycle contract, or the bounded MMIO interrupt-ack rung is landed only in code without the same review path staying explicit.
- `make -C zigux phase10-validate` is the validator-first entrypoint for the active Phase 10 ring-plus-input-plus-MMIO lab packet.
- `make -C zigux phase10` keeps the one-command replay path aligned with the shared fail-closed review contract after the validators pass.
- `zig build test --build-file zigux/tests/phase10_build.zig --summary all` is the shared Phase 10 replay surface for the virtio core, ring, input, and MMIO lab helpers plus their survey-backed checks.

Phase 11 flow
- `make -C zigux phase11-validate` is the validator-first entrypoint for the active simple-driver tranche.
- `validate-phase11.py --self-test` keeps the fast Python gate fail-closed before the live Phase 11 packet is trusted.
- `validate-phase11.py` keeps `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_hvc_console_manifest.json`, and `zigux/tests/phase11_uapi_header_parity_manifest.json` aligned with `zigux/tests/phase11_build.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the dedicated hvc_console survey note and validation matrix.
- `make -C zigux phase11-hvc-survey` is the dedicated archival replay for `zigux/tests/phase11_hvc_console_survey.zig`, while `make -C zigux phase11` keeps the shared Phase 11 replay plus that dedicated archival step in one published path.
- the active Phase 11 review packet should keep the exact shared-versus-dedicated replay commands and observed outcome lines explicit in review notes so the shared build inventory and the separate hvc_console survey boundary do not drift into prose-only claims.

Phase 12 flow
- `check-phase12-build-inventory.py`, `check-phase12-libbpf-snapshot.py`, `check-phase12-libbpf-packet.py`, and `validate-phase12.py` keep the shared Phase 12 complex-driver and heavy-helper tranche aligned before replay by checking the workflow wiring, `zigux/Makefile`, `zigux/tests/phase12_build.zig`, the shared build inventory snapshot in `zigux/tests/fixtures/phase12_build_inventory.json`, the committed libbpf reproducibility packet in `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, the bounded libbpf packet-alignment contract across the manifest, survey note, reviewability gate, and legacy segment catalog, the four manifests `zigux/tests/phase12_virtio_net_manifest.json`, `zigux/tests/phase12_nvme_pci_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_libbpf_manifest.json`, plus the survey notes pinned to each manifest's exact `surveyed_commit`.
- `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-packet.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`, and `python3 scripts/zigux/check-phase12-libbpf-packet.py` now prove the repeat-run snapshot and packet-alignment contract for the bounded libbpf reproducibility lane, reject invalid Phase 12 manifest metadata or legacy segment drift, preserve the committed tracked-file order, and keep the survey note plus reviewability gate aligned before `make -C zigux phase12-validate` compares against the committed fixture and shared packet.
- `make -C zigux phase12-validate` is the fail-fast bundle check for that shared degraded-workflow packet before the shared Zig replay runs, and it now also proves that the bounded libbpf manifest, survey, reviewability gate, note, and legacy segment catalog regenerate the same snapshot JSON on repeat runs and stay aligned with the separate packet checker.
- `make -C zigux phase12` keeps the current Phase 12 bundle reviewable through one shared tranche entrypoint instead of ad hoc complex-driver commands, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all` now reports `Build Summary: 19/19 steps succeeded; 55/55 tests passed`, which matches the committed `zigux/tests/fixtures/phase12_build_inventory.json` shared build inventory snapshot and the added `phase12-virtio-net-syntax-lab-tests` compile-smoke gate for lane `P12-L04`.
- the current active storage-driver survey packet stays explicit through `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, and the paired `zigux/tests/phase12_virtio_scsi_{manifest,survey}.zig` files, so the queue-layout, recovery, probe snapshot, host-limit summary, queue-depth summary, and io-queue-map starters remain visible without overstating the still-blocked DMA-backed queue ownership, `Scsi_Host` lifecycle, or blk-mq follow-up.

Phase 13 flow
- `validate-phase13-release.py` keeps `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/Makefile`, and `zigux/tests/phase13_build.zig` aligned as one shared release-discipline packet instead of leaving the Phase 13 review path split across isolated docs or build wiring.
- `make -C zigux phase13-validate` runs that dedicated release validator before the broader shared replay.
- `make -C zigux phase13` routes through the validator before the shared replay, so the local convenience path matches the release-facing review contract.
- `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres_manifest.json`, and `zigux/tests/phase13_devres_reviewability.zig` keep the helper-first `devres` packet explicit about live DMA-backed mappings and scatterlist ownership staying blocked rather than implied.

Phase 14 flow
- `validate-phase14.py` keeps the shared Phase 14 smoke packet aligned across `scripts/zigux/README.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, and the four anchor-local manifests plus survey notes so the shared stay-in-C boundary remains reviewable as one validator-backed packet.
- `make -C zigux phase14-validate` is the validator-first entrypoint for the shared Phase 14 smoke packet before any broader replay claims stay green.
- `make -C zigux phase14-smoke` is the focused smoke-shard replay contract and intentionally routes through the shared `zigux/tests/phase14_build.zig` entrypoint instead of bypassing the reviewable wrapper path.
- `zigux/tests/phase14_build.zig` is the shared Phase 14 build entrypoint: it keeps the focused smoke-shard replay contract explicit, records the same shared Phase 14 smoke packet boundary, and leaves the deeper bridge or survey slices under the broader bundle.
- the shared packet keeps the roadmap stay-in-C boundary explicit by recording the named owner, validation gate, rollback owner, and roadmap risk bundle (`hidden runtime behavior`, `memory-ordering mistakes`, `overpromising full parity`, `deep-core scope creep`) beside the focused wrapper path.
- `zigux/tests/phase14_end_to_end_smoke_manifest.json` and `Documentation/zigux/phase14-end-to-end-smoke-survey.md` keep the current four-anchor boundary map plus the bounded concurrency-audit scope explicit, so the shared smoke path stays tied to `kernel/workqueue.c`, `net/core/skbuff.c`, `kernel/trace/ring_buffer.c`, and `kernel/rcu/tree.c` without overstating live parity.
- the same packet also keeps the rollback threshold, fallback path, and automatic return-to-blocked trigger catalog explicit so the shared smoke path fails closed before it overstates Phase 14 delivery.
