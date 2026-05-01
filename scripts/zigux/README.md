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
- `check-phase7-cmdline-parity.py`
- `validate-phase8.py`
- `validate-phase9.py`
- `validate-phase10.py`
- `validate-phase10-closure.py`
- `check-phase11-build-inventory.py`
- `validate-phase11.py`
- `check-phase12-build-inventory.py`
- `check-phase12-libbpf-snapshot.py`
- `validate-phase12.py`
- `validate-phase13-release.py`
- `validate-phase14.py`
- `validate-phase3-roadmap-gap-survey.py`
- `validate-phase3-export-uapi-survey.py`
- `validate-phase3-low-level-wrapper-survey.py`
- `validate-phase3-policy-unsafe-survey.py`
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
- `artifact_diff.py --self-test` and `check-artifact-diff-contract.py` stay in the same Phase 4 flow so the bounded host-side diff tooling fails closed before the rollback gates claim aligned evidence.
- `make -C zigux phase4-test-fsmount-survey` and `make -C zigux phase4-perf-baseline-survey` keep the two manifest-backed survey gates reviewable without widening them into landed Zig samples or approved benchmark thresholds.
- `phase4-test-fsmount-survey-tests` and `phase4-perf-baseline-survey-tests` remain explicit in `phase4_build.zig`, alongside `phase4-runtime-atomic64-diff-survey-tests`, so the shared replay surface stays measurable instead of dissolving into prose-only notes.
- `Documentation/zigux/phase4-validation-matrix.md` remains the published rollback-owner, local replay, and reversible-delivery evidence note for the current packet.
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
- the same validator surface now also carries the latest focused policy evidence: `zigux/tests/phase3_policy_unsafe.zig` covers overflow-checked unsafe address math, and the Phase 3 source-audit self-test keeps the layout-assert, panic-policy, allocator-policy, and narrow-unsafe markers reviewable even when the full repo tree is not under replay.
- the same validator now also treats the focused low-level wrapper gate as a real anti-regression surface instead of a presence-only file list: it restores the shared self-test import path, checks the exact exported atomic, barrier, and MMIO helper surface against the published Phase 3 ABI slice, and still checks the scoped `read16`, `write16`, `read32`, and `write32` MMIO entry points plus the low-level replay’s strong compare-exchange success and mismatch coverage, weak compare-exchange retry and mismatch coverage, barrier probe, denied-scope, and allowed scoped-MMIO assertions so width-specific, scope-specific, or undocumented wrapper-surface drift fails before Phase 3 review claims stay green.

Phase 5 flow
- `validate-phase5.py` keeps the shipped Phase 5 contributor packet aligned across `samples/zigux/README.md`, the four sample-backed survey notes, the four manifest-backed surveys, `zigux/tests/phase5_build.zig`, `zigux/Makefile`, and the bootstrap workflow before any shared sample replay claims stay green.
- `validate-phase5.py --self-test` exercises the sample-backed packet drift checks in a temporary fixture tree and now fails if `surveyed_commit` sync, survey-build-summary evidence, manifest review-prompt groups, or the recorded sample-test command drift out of the shared Phase 5 contributor packet.
- `make -C zigux phase5-validate` is the validator-first entrypoint for the approved sample ports, reviewable Zigux idioms, contributor guidance, and `Documentation/zigux` material that Phase 5 ships today.
- `make -C zigux phase5` and `zig build test --build-file zigux/tests/phase5_build.zig --summary all` are the shared replay surface for the four roadmap-backed reference samples after the validator gate passes.
- the focused one-family replays stay explicit too: `zig test samples/zigux/bytestream_fifo.zig`, `zig test samples/zigux/kobject_example.zig`, `zig test samples/zigux/kretprobe_example.zig`, and `zig test samples/zigux/trace_events_sample.zig` cover the direct sample roots, while `zig test zigux/tests/phase5_bytestream_fifo_survey.zig`, `zig test zigux/tests/phase5_kobject_example_survey.zig`, `zig test zigux/tests/phase5_kretprobe_example_survey.zig`, and `zig test zigux/tests/phase5_trace_events_sample_survey.zig` keep the paired manifest-backed survey packet reviewable for the same sample family without requiring the full shared bundle.
- `zigux/tests/phase5_build.zig` is the shared build entrypoint for the bytestream FIFO, kobject, kretprobe, and trace-events sample packets, including their paired direct-sample and manifest-backed survey replays.
- `samples/zigux/README.md` is the contributor-facing sample-root catalog for the approved Phase 5 anchors and the explicit boundary that keeps later `runtime_*` starters out of the sample-pattern lane.

Phase 6 flow
- `validate-phase6.py` keeps the shipped Phase 6 leaf-helper packet aligned across `scripts/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase6-helper-parity-catalog.md`, `zigux/tests/phase6_helper_parity_manifest.json`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, the bootstrap workflow, and the four helper-local slice notes before any shared replay claims stay green.
- `validate-phase6.py --self-test` exercises the shared Phase 6 marker walk in a compact synthetic tree and fails if catalog or manifest provenance or helper-local fixture evidence drifts.
- `make -C zigux phase6-validate` is the validator-first entrypoint for the current Phase 6 review packet.
- `make -C zigux phase6` is the shared replay path for the bounded `base64`, `bsearch`, `checksum`, and `hexdump` helper tests after the validator passes.
- the per-helper perf targets stay reviewable as explicit make entrypoints: `make -C zigux phase6-base64-perf`, `make -C zigux phase6-bsearch-perf`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf`.
- `check-phase6-base64-c-parity.py` and `check-phase6-bsearch-c-parity.py` remain the two external parity spot checks for the portability-sensitive helper slices.
