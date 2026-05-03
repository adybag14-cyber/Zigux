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
- `check-phase1-find-bit-validator-anchors.py`
- `check-phase1-bench.py`
- `validate-phase1-closure.py`
- `validate-phase2.py`
- `validate-phase2-closure.py`
- `validate-phase3.py`
- `check-phase3-abi.py`
- `check-phase3-abi-layout-packet.py`
- `check-phase3-abi-binding-constants.py`
- `check-phase3-build-roots.py`
- `check-phase3-canonical-survey-manifest.py`
- `check-phase3-policy-unsafe-mmio-consumer.py`
- `check-phase3-rbtree-shared-lift-contract.py`
- `check-phase3-readme-tooling-inventory.py`
- `check-phase3-tooling-packet.py`
- `check-phase3-validation-flow.py`
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
- `check-phase8-perf-buffer-poll-gate.py`
- `validate-phase9.py`
- `check-phase9-validation-flow.py`
- `check-phase9-loader-substrate-plan.py`
- `check-phase9-runtime-loader-commit-alignment.py`
- `check-phase9-loader-non-owner-boundary.py`
- `check-phase9-module-metadata-packet.py`
- `validate-phase10.py`
- `check-phase10-closure-inventory.py`
- `check-phase10-core-packet.py`
- `check-phase10-harness-coverage.py`
- `validate-phase10-closure.py`
- `validate-phase11.py`
- `check-phase11-build-inventory.py`
- `check-phase11-layout-assert-surface.py`
- `check-phase11-hvc-validation-flow.py`
- `check-phase11-hvc-cleanup-alignment.py`
- `check-phase12-build-inventory.py`
- `check-phase12-libbpf-snapshot.py`
- `check-phase12-libbpf-packet.py`
- `check-phase12-libbpf-focused-replay.py`
- `check-phase12-raw-github-coverage.py`
- `validate-phase12.py`
- `check-phase13-libfs-packet.py`
- `check-phase13-devres-packet.py`
- `check-phase13-notifier-packet.py`
- `validate-phase13-release.py`
- `validate-phase14.py`
- `validate-phase15.py`
- `validate-phase3-roadmap-gap-survey.py`
- `validate-phase3-rbtree-interop-survey.py`
- `validate-phase3-export-uapi-survey.py`
- `validate-phase3-low-level-wrapper-survey.py`
- `validate-phase3-policy-unsafe-survey.py`
- `validate_phase3_header_binding_markers.py`
- `validate_phase3_selftest.py`
- `generate-phase3-check-wrappers.py`
- `run-phase3-checks.py`
- `phase3_catalog.py`
- `phase3_check_lib.py`
- `check-phase1-parity.py`
- `check-fixdep-diff.py`
- `check-genksyms-bridge.py`
- `check-phase2-genksyms-bridge-selftest-alignment.py`
- `check-phase2-cross-selftest-alignment.py`
- `check-genksyms-crc-diff.py`
- `check-kconfig-bridge.py`
- `check-phase2-cross.py`
- `check-phase2-toolchain-pin-scope.py`
- `check-mk-elfconfig-diff.py`
- `check-phase6-base64-c-parity.py`
- `check-phase6-bsearch-c-parity.py`
- `check-phase6-checksum-c-parity.py`
- `check-phase6-hexdump-c-parity.py`

Zig toolchain gate
- `check-zig-toolchain.py` verifies that the selected Zig binary exists and satisfies the configured minimum version.
- `check-zig-toolchain.py --self-test` runs built-in parser and version-ordering coverage without needing a local Zig install.

Phase 1 flow
- `validate-phase1.py` is the validator-first entrypoint for the closed host-helper packet around `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/string.zig`, and `tools/lib/rbtree.zig` plus the bounded supporting helpers and committed `zigux/tests/fixtures/phase1_helpers.json` corpus.
- the same validator keeps `Documentation/zigux/phase1-closure.md`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, and the workflow hooks aligned, including the committed `PHASE1_FIND_BIT_TAIL_START_UNIT_REVIEW` and `PHASE1_FIND_BIT_ZERO_SIZED_UNIT_REVIEW` closure markers for the tail-start and zero-sized `find_bit` parity packet.
- `Documentation/zigux/README.md`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` stay aligned as the bounded Phase 1 helper inventory and validator-first replay packet.
- `check-phase1-find-bit-validator-anchors.py --self-test` and `check-phase1-find-bit-validator-anchors.py` keep `validate-phase1.py` fail-closed around those shipped `find_bit` tail-start and zero-sized closure markers plus the matching `phase1_helper_manifest.json` tail-start and zero-sized anchor checks, so the primary Phase 1 validator cannot silently stop naming that closed evidence packet.
- `check-phase1-parity.py --self-test`, `check-phase1-parity.py`, `check-phase1-bench.py --self-test`, `check-phase1-bench.py`, `validate-phase1-closure.py --self-test`, and `validate-phase1-closure.py` are the bounded fail-closed review hooks around that same closed Phase 1 helper tranche.

Phase 4 flow
- `make -C zigux phase4-validate` is the validator-first entrypoint for the current rollback-readiness packet.
- `validate-phase4.py` keeps the current gate-definition and survey packet aligned across `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/bitmap_diff.zig`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_test_fsmount_survey.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, `Documentation/zigux/phase4-validation-matrix.md`, and the paired workflow plus Makefile hooks.
- `check-phase4-gate-evidence.py` keeps `Documentation/zigux/phase4-gate-evidence.md` fail-closed across the broader survey-file and docs-root, scripts-root, and tests-root blob pins recorded for the same Phase 4 packet.
- `artifact_diff.py --self-test` and `check-artifact-diff-contract.py` stay in the same Phase 4 flow so the bounded host-side diff tooling fails closed before the rollback gates claim aligned evidence, including the published malformed-JSON `EXPECTED_JSON_ERROR=` and `ACTUAL_JSON_ERROR=` failure markers alongside the stable pass, text mismatch, missing-file, and SHA-256 contract cases.
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
- `check-phase2-toolchain-pin-scope.py --self-test` exercises the dedicated pin-scope guard without needing the full repo tree.
- `check-phase2-toolchain-pin-scope.py` keeps `scripts/zigux/zig-toolchain-policy.json`, the bootstrap workflow `install-zig.py --dest .zig-toolchain` and `check-zig-toolchain.py` steps, and `validate-phase2.py` aligned around the current `x86_64-linux`-only archive pin until another bootstrap runner target gains first-class workflow evidence.
- `check-fixdep-diff.py --self-test` exercises the bounded fixdep checker packet itself before the shared `phase2-tools` and bootstrap workflow entrypoints replay live artifacts, so case-manifest drift, explicit-tool drift, and unsupported stdout-mode changes cannot hide behind a locally passing parity run.
- `check-fixdep-diff.py` compares the bounded `fixdep.zig` output against the committed fixture set, including the multi-target, escaped-whitespace, escaped-colon, comment-only no-target, and missing-dependency failure artifacts under `zigux/tests/fixtures/fixdep/`, reruns both the C tool and Zig tool to prove repeat-run artifact determinism, and now also fails if any success-path fixdep case starts emitting unexpected stderr noise.
- `check-genksyms-bridge.py --self-test` exercises the bounded `genksyms` bridge checker packet itself before the Linux-style `phase2-tools` entrypoint replays live bridge artifacts, so missing-expected-fixture drift, duplicate expected-fixture wiring, stderr-mode contract drift, and repeat-run compare coverage cannot hide behind a locally passing bridge replay.
- `check-genksyms-bridge.py` exercises the bounded `genksyms.zig` bridge parity lane, including success-path stderr silence and repeat-run stderr determinism for the stdout-json bridge fixtures.
- `check-phase2-genksyms-bridge-selftest-alignment.py --self-test` exercises the dedicated Phase 2 alignment checker packet before the validator-first `phase2-validate` path trusts the broader closure replay, so README, closure-note, workflow, Makefile, validator, and bridge-case drift cannot hide behind a locally passing bridge packet.
- `check-phase2-genksyms-bridge-selftest-alignment.py` keeps `check-genksyms-bridge.py`, `scripts/zigux/README.md`, `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/fixtures/genksyms_bridge/cases.json` fail-closed around the committed 26-case bridge surface.
- that same committed bridge packet currently spans 26 reviewable cases under `zigux/tests/fixtures/genksyms_bridge/`, including the minimal, clustered short-inline, abbreviated long-option, lone-dash passthrough, explicit-terminator positional, missing-argument, and reference-limit fixtures that keep the widened wrapper-first surface explicit.
- `check-genksyms-crc-diff.py --self-test` exercises the bounded `genksyms_crc` checker packet itself before the Linux-style `phase2-tools` entrypoint replays the live artifact lane, so explicit-tool passthrough drift, mismatch-contract drift, and repeat-run compare coverage cannot hide behind local tool availability.
- `check-genksyms-crc-diff.py` checks the bounded `genksyms_crc.zig` artifact lane and now proves repeat-run JSON determinism for both the bounded C harness and Zig tool before fixture comparison.
- `check-kconfig-bridge.py --self-test` exercises the bounded kconfig bridge checker packet itself before the Linux-style `phase2-kconfig` entrypoint replays the live bridge artifacts.
- `check-kconfig-bridge.py` covers the bounded `kconfig/conf_bridge.zig` and `kconfig/confdata_bridge.zig` bridge lanes and now proves repeat-run JSON determinism for both bridge outputs before fixture comparison.
- `check-phase2-cross-selftest-alignment.py --self-test` and `check-phase2-cross-selftest-alignment.py` keep the shared README, Makefile, workflow, validator, and cross-target packet aligned before the Linux-style `phase2-cross` entrypoint trusts the broader compile lane.
- `check-phase2-cross.py --self-test` exercises the bounded cross-target checker packet itself before the Linux-style `phase2-cross` entrypoint replays live Zig compiles, so duplicate tool entries, duplicate requested targets, unexpected explicit targets, manifest-count drift, duplicate manifest targets, and explicit-target failure drift cannot hide behind local tool availability.
- `check-phase2-cross.py` runs the bounded Phase 2 cross-target compile checks.
- `check-mk-elfconfig-diff.py --self-test` exercises the bounded mk_elfconfig checker packet itself before the Linux-style `phase2-tools` entrypoint replays the live artifact lane, so fixture-shape and explicit-tool drift cannot hide behind local compiler or Zig availability.
- `check-mk-elfconfig-diff.py` covers the bounded `mk_elfconfig.zig` artifact lane and now proves repeat-run JSON determinism for both the bounded C tool and Zig tool before fixture comparison.
- `check-phase12-libbpf-focused-replay.py` keeps the focused `zigux/tests/phase12_libbpf_only_build.zig` replay, its dedicated survey note, and the Makefile hooks aligned before the broader Phase 12 validator trusts the libbpf-only shard.
- `check-phase12-raw-github-coverage.py --self-test` and `check-phase12-raw-github-coverage.py` keep the bounded `phase12_raw_github_coverage_manifest.json`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, and the paired commit-pinned raw fallback catalog and map explicit before the shared Phase 12 packet claims that the roadmap-wide public-read split is still reviewable.
- `check-phase1-parity.py` now reruns the bounded C harness after fixture comparison so the shared Phase 1 parity artifact also proves repeat-run JSON determinism instead of only a single-pass match.
- `check-phase1-bench.py --self-test` exercises the bounded Phase 1 benchmark checker itself before the live benchmark smoke runs, so parser, expected-key, and undeclared-key drift cannot hide behind a locally passing Zig bench replay.

Phase 3 flow
- `validate-phase3.py` is the validator-first entrypoint for the shared Phase 3 ABI and interop packet, and `make -C zigux phase3-validate` plus the bootstrap workflow replay that same route before the broader build-backed or survey-backed checks run.
- `validate-phase3-roadmap-gap-survey.py`, `validate-phase3-rbtree-interop-survey.py`, `check-phase3-rbtree-shared-lift-contract.py`, `validate-phase3-export-uapi-survey.py`, `validate-phase3-low-level-wrapper-survey.py`, `validate-phase3-policy-unsafe-survey.py`, `check-phase3-policy-unsafe-mmio-consumer.py`, `check-phase3-abi-layout-packet.py`, `check-phase3-abi-binding-constants.py`, `check-phase3-tooling-packet.py`, `check-phase3-readme-tooling-inventory.py`, `check-phase3-validation-flow.py`, `check-phase3-build-roots.py`, and `check-phase3-canonical-survey-manifest.py` stay as supporting checks inside that validator-first route rather than standalone bootstrap or release entrypoints.
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
- `validate-phase5.py` keeps the shipped Phase 5 contributor packet aligned across `samples/zigux/README.md`, the four sample-backed survey notes, the four manifest-backed surveys, `zigux/tests/phase5_build.zig`, `zigux/Makefile`, the bootstrap workflow, and the four helper-local slice notes before any shared sample replay claims stay green.
- `validate-phase5.py --self-test` exercises the sample-backed packet drift checks in a temporary fixture tree and fails if `surveyed_commit` sync, survey-build-summary evidence, manifest review-prompt groups, or the recorded sample-test command drift out of the shared Phase 5 contributor packet.
- `make -C zigux phase5-validate` is the validator-first entrypoint for the approved sample ports, reviewable Zigux idioms, contributor guidance, and `Documentation/zigux` material that Phase 5 ships today.
- `make -C zigux phase5` and `zig build test --build-file zigux/tests/phase5_build.zig --summary all` are the shared replay surface for the four roadmap-backed reference samples after the validator gate passes.
- the focused one-family replays stay explicit too: `zig test samples/zigux/bytestream_fifo.zig` and `zig test zigux/tests/phase5_bytestream_fifo.zig` cover the direct bytestream sample plus its helper-review surface, `zig test samples/zigux/kobject_example.zig`, `zig test samples/zigux/kretprobe_example.zig`, and `zig test samples/zigux/trace_events_sample.zig` cover the other direct sample roots, while `zig test zigux/tests/phase5_bytestream_fifo_survey.zig`, `zig test zigux/tests/phase5_kobject_example_survey.zig`, `zig test zigux/tests/phase5_kretprobe_example_survey.zig`, and `zig test zigux/tests/phase5_trace_events_sample_survey.zig` keep the paired manifest-backed survey packet reviewable for the same sample family without requiring the full shared bundle.
- `zigux/tests/phase5_build.zig` is the shared build entrypoint for the bytestream FIFO, kobject, kretprobe, and trace-events sample packets, including their paired direct-sample and manifest-backed survey replays.
- `samples/zigux/README.md` is the contributor-facing sample-root catalog for the approved Phase 5 anchors and the explicit boundary that keeps later `runtime_*` starters out of the sample-pattern lane.
- the same Phase 5 flow also keeps the shipped sample-root boundary explicit: current `master` still ships no `samples/zigux/*string*` or `samples/zigux/*cmdline*` reference sample, and `samples/zigux/runtime_bitmap.zig` plus `samples/zigux/runtime_bitmap_loader.zig` stay cataloged as the separate Phase 9 runtime bitmap survey packet rather than a fifth approved Phase 5 sample.

Phase 6 flow
- `validate-phase6.py` keeps the shipped Phase 6 leaf-helper packet aligned across `scripts/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase6-helper-parity-catalog.md`, `zigux/tests/phase6_helper_parity_manifest.json`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, the bootstrap workflow, and the four helper-local slice notes before any shared replay claims stay green.
- `validate-phase6.py --self-test` exercises the shared Phase 6 marker walk in a compact synthetic tree and fails if catalog-head provenance, script-README wording, perf-survey markers, shared-gates inventory, manifest `surveyed_commit`, or helper-local determinism evidence drifts.
- `make -C zigux phase6-validate` is the validator-first entrypoint for the current Phase 6 review packet.
- `make -C zigux phase6` is the shared replay path for the bounded `base64`, `bsearch`, `checksum`, and `hexdump` helper