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
- `check-phase1-bitmap-validator-anchors.py`
- `check-phase1-find-bit-validator-anchors.py`
- `check-phase1-route-summary-counts.py`
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
- `check-phase4-kprobe-example-packet.py`
- `validate-phase5.py`
- `validate-phase6.py`
- `check-phase6-docs-root-external-parity.py`
- `check-phase6-base64-catalog-evidence.py`
- `validate-phase7.py`
- `check-phase7-build-inventory.py`
- `check-phase7-make-wrapper.py`
- `check-phase7-cmdline-parity.py`
- `check-phase7-argv-split-packet.py`
- `check-phase7-argv-split-parity.py`
- `check-phase7-rbtree-parity.py`
- `validate-phase8.py`
- `check-phase8-validator-flow.py`
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
- `check-phase11-shared-replay-contract.py`
- `check-phase11-header-boundary-packet.py`
- `check-phase12-build-inventory.py`
- `check-phase12-libbpf-snapshot.py`
- `check-phase12-libbpf-packet.py`
- `check-phase12-libbpf-focused-replay.py`
- `check-phase12-raw-github-coverage.py`
- `check-phase12-release-readiness-packet.py`
- `validate-phase12.py`
- `check-phase13-libfs-packet.py`
- `check-phase13-devres-packet.py`
- `check-phase13-notifier-packet.py`
- `validate-phase13-release.py`
- `validate-phase14.py`
- `check-phase14-docs-root-smoke-summary.py`
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
- `check-phase2-kconfig-selftest-alignment.py`
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
- `check-phase1-bitmap-validator-anchors.py --self-test` and `check-phase1-bitmap-validator-anchors.py` keep the shipped bitmap header-alias, allocator-alias, double-underscore-alias, size-helper, xor-window, tail-mask, zero-bit, and empty-bitmap review packet fail-closed across `Documentation/zigux/phase1-closure.md`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`, so the shared Phase 1 validator-first lane cannot silently undercount that closed evidence surface.
- `check-phase1-find-bit-validator-anchors.py --self-test` and `check-phase1-find-bit-validator-anchors.py` keep `validate-phase1.py` fail-closed around those shipped `find_bit` tail-start and zero-sized closure markers plus the matching `phase1_helper_manifest.json` tail-start and zero-sized anchor checks, the paired tail-word-boundary anchor review, the bench self-test count marker, and the paired `zigux/Makefile` plus bootstrap workflow routes, so the primary Phase 1 validator cannot silently stop naming that closed evidence packet.
- `check-phase1-route-summary-counts.py --self-test` and `check-phase1-route-summary-counts.py` keep the two docs-root and two scripts-root Phase 1 route-summary lines fail-closed across `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`, so the shared host-helper packet cannot silently drift away from the published validator-first and review-hook wording.
- `check-phase1-bitmap-validator-anchors.py --self-test`, `check-phase1-bitmap-validator-anchors.py`, `check-phase1-find-bit-validator-anchors.py --self-test`, `check-phase1-find-bit-validator-anchors.py`, `check-phase1-route-summary-counts.py --self-test`, `check-phase1-route-summary-counts.py`, `check-phase1-validation-route-inventory.py --self-test`, `check-phase1-validation-route-inventory.py`, `check-phase1-parity.py --self-test`, `check-phase1-parity.py`, `check-phase1-bench.py --self-test`, `check-phase1-bench.py`, `validate-phase1-closure.py --self-test`, and `validate-phase1-closure.py` are the bounded fail-closed review hooks around that same closed Phase 1 helper tranche.

Phase 4 flow
- `make -C zigux phase4-validate` is the validator-first entrypoint for the current rollback-readiness packet.
- `validate-phase4.py` keeps the current gate-definition and survey packet aligned across `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/bitmap_diff.zig`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_test_fsmount_survey.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, `Documentation/zigux/phase4-validation-matrix.md`, and the paired workflow plus Makefile hooks.
- `check-phase4-gate-evidence.py` keeps `Documentation/zigux/phase4-gate-evidence.md` fail-closed across the broader survey-file and docs-root, scripts-root, and tests-root blob pins recorded for the same Phase 4 packet.
- `check-phase4-kprobe-example-packet.py --self-test` and `check-phase4-kprobe-example-packet.py` keep `zigux/tests/phase4_kprobe_example_manifest.json`, `zigux/tests/phase4_kprobe_example_survey.zig`, `zigux/tests/phase4_build.zig`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/README.md`, and the current `samples/kprobes` C anchor fail-closed around the published survey-only kprobe packet while the broader `validate-phase4.py` promotion stays open.
- `artifact_diff.py --self-test` and `check-artifact-diff-contract.py` stay in the same Phase 4 flow so the bounded host-side diff tooling fails closed before the rollback gates claim aligned evidence, including the published malformed-JSON `EXPECTED_JSON_ERROR=` and `ACTUAL_JSON_ERROR=` failure markers alongside the stable pass, text mismatch, missing-file, and SHA-256 contract cases.
- `make -C zigux phase4-kprobe-example-survey`, `make -C zigux phase4-test-fsmount-survey`, and `make -C zigux phase4-perf-baseline-survey` keep the three manifest-backed survey gates reviewable without widening them into landed Zig samples or approved benchmark thresholds.
- `phase4-kprobe-example-survey-tests`, `phase4-test-fsmount-survey-tests`, and `phase4-perf-baseline-survey-tests` remain explicit in `phase4_build.zig`, alongside `phase4-runtime-atomic64-diff-survey-tests`, so the shared replay surface stays measurable instead of dissolving into prose-only notes.
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
- `check-phase2-cross-selftest-alignment.py` keeps the shared Phase 2 cross-target packet aligned across `check-phase2-cross.py --self-test`, `check-phase2-cross.py`, the scripts index, the closure note, the workflow route, and the Makefile route, so duplicate tool entries, duplicate manifest targets, and unexpected explicit targets stay reviewable before live compile replay.
- `check-phase2-toolchain-pin-scope.py --self-test` exercises the dedicated pin-scope guard without needing the full repo tree.
- `check-phase2-toolchain-pin-scope.py` keeps `scripts/zigux/zig-toolchain-policy.json`, the bootstrap workflow `install-zig.py --dest .zig-toolchain` and `check-zig-toolchain.py` steps, and `validate-phase2.py` aligned around the current `x86_64-linux`-only archive pin until another bootstrap runner target gains first-class workflow evidence.
- `check-genksyms-bridge.py --self-test` exercises the bounded `genksyms` bridge checker packet itself before the Linux-style `phase2-tools` entrypoint replays live bridge artifacts, so missing-expected-fixture drift, duplicate expected-fixture wiring, stderr-mode contract drift, and repeat-run compare coverage cannot hide behind a locally passing bridge replay.
- `check-phase2-genksyms-bridge-selftest-alignment.py --self-test` and `check-phase2-genksyms-bridge-selftest-alignment.py` keep the bridge checker self-test markers, the shared validator pair, the workflow route, the Makefile route, and the scripts index aligned before the live bridge replay claims bounded closure evidence.
- `check-genksyms-crc-diff.py --self-test` keeps the bounded genksyms CRC checker packet reviewable before the Linux-style `phase2-tools` replay, so mismatch-contract drift and repeat-run compare coverage fail closed before the parity lane relies on local tool availability.
- that same committed bridge packet currently spans 26 reviewable cases under `zigux/tests/fixtures/genksyms_bridge/`, including the minimal, clustered short-inline, abbreviated long-option, lone-dash passthrough, explicit-terminator positional, missing-argument, and reference-limit fixtures that keep the widened wrapper-first surface explicit.

Phase 11 flow
- `make -C zigux phase11-validate` is the validator-first entrypoint for the active simple-driver packet around `zigux/tests/phase11_build.zig`, `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_hvc_console_manifest.json`, and `zigux/tests/phase11_uapi_header_parity_manifest.json`.
- `check-phase11-build-inventory.py --self-test`, `check-phase11-build-inventory.py`, `check-phase11-layout-assert-surface.py --self-test`, `check-phase11-layout-assert-surface.py`, `check-phase11-hvc-validation-flow.py --self-test`, `check-phase11-hvc-validation-flow.py`, `check-phase11-hvc-cleanup-alignment.py --self-test`, `check-phase11-hvc-cleanup-alignment.py`, `check-phase11-shared-replay-contract.py --self-test`, `check-phase11-shared-replay-contract.py`, `check-phase11-header-boundary-packet.py --self-test`, `check-phase11-header-boundary-packet.py`, `validate-phase11.py --self-test`, and `validate-phase11.py` keep the pre-replay checker stack aligned across `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.
- `make -C zigux phase11-hvc-survey` remains the dedicated archival replay for `zigux/tests/phase11_hvc_console_survey.zig`, while `make -C zigux phase11` and `zigux/tests/phase11_build.zig` keep the shared watchdog-and-console starter replay explicit.
- `Documentation/zigux/phase11-shared-replay-contract.md`, the dedicated hvc_console survey note and validation matrix, `zigux/tests/fixtures/phase11_build_inventory.json`, and the Phase 11 manifest set keep the exact shared-versus-dedicated replay commands and observed outcome lines reviewable instead of leaving the current hvc split implicit.

Phase 8 flow
- `python3 scripts/zigux/validate-phase8.py`, `make -C zigux phase8-validate`, `zig test tools/lib/subcmd/exec-cmd.zig`, `make -C zigux phase8-exec-cmd-test`, `make -C zigux phase8`, `zig test zigux/tests/phase8_libbpf_segments.zig`, `zigux/tests/phase8_exec_cmd_only_build.zig`, `zigux/tests/phase8_help_only_build.zig`, `zigux/tests/phase8_kallsyms_only_build.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, and `zigux/tests/phase8_perf_buffer_poll_only_build.zig` now keep the current Phase 8 flow reviewable across the direct helper-local `exec-cmd` replay, the focused subcmd and symbol shards, the segmented libbpf shards, and the shared tooling bundle.
- `Documentation/zigux/phase8-exec-cmd-slice.md`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `tools/lib/subcmd/exec-cmd.zig`, `deferred execution`, `execvp()`, `kernel/workqueue.c`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, `cpu_mask.zig`, and `type_names.zig` keep that Phase 8 flow explicit as helper-first tooling work rather than widened runtime or scheduler claims.

Phase 14 flow
- `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` are the current shared review path for the Phase 14 boundary-only smoke packet.
- `check-phase14-docs-root-smoke-summary.py --self-test` and `check-phase14-docs-root-smoke-summary.py` keep the docs-root Phase 14 smoke summary and the shared smoke survey fail-closed around the same validator-backed `phase14-validate`, focused `phase14-smoke`, and study-only reviewability wording before the broader shared validator runs.
- `validate-phase14.py` keeps `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned around the same validator-backed smoke commands, anchor list, rollback owners, automatic return-to-blocked triggers, and bounded study-only posture.
- the same shared flow keeps the current `phase14-smoke` shard explicit for the four roadmap anchors while leaving `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` in boundary-study posture and `kernel/rcu/tree.c` plus `net/core/skbuff.c` in the blocked Phase 15 freeze-in-C governance packet.
- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, and `zigux/tests/phase14_end_to_end_smoke_survey.zig` keep the exact rollback threshold, automatic return-to-blocked trigger list, and ZAR-to-product transfer rationale visible from the docs root rather than relying on run memory.

Phase 13 flow
- `check-phase13-libfs-packet.py`, `check-phase13-devres-packet.py`, `check-phase13-notifier-packet.py`, and `validate-phase13-release.py` keep `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/Makefile`, and `zigux/tests/phase13_build.zig` aligned as one shared release-discipline packet, with the four roadmap-anchor manifests `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`, the adjacent `zigux/tests/phase13_notifier_list_manifest.json`, the dedicated `scripts/zigux/check-phase13-devres-packet.py` guard, the `phase13-landlock-syscalls-reviewability-tests` gate under `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and the adjacent notifier evidence under `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, and `zigux/helpers/notifier_chain_view.zig` kept explicit instead of leaving the Phase 13 review path split across isolated docs or build wiring.
- `check-phase13-devres-packet.py` keeps the helper-first `devres` packet and its blocked DMA/scatterlist boundary visible in that same shared Phase 13 release flow instead of leaving the live devres guard implicit in the Makefile wiring and packet-local survey assets.
- `make -C zigux phase13-validate` runs that dedicated release validator before the broader shared replay.
- `make -C zigux phase13` routes through the validator before the shared replay, so the local convenience path matches the release-facing review contract.
- `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_devres_dma_coherent.zig`, and `zigux/tests/phase13_devres_reviewability.zig` keep the helper-first `devres` packet explicit about adjacent coherent-DMA bookkeeping while live DMA-backed mappings and scatterlist ownership stay blocked rather than implied.

Phase 12 flow
- `check-phase12-build-inventory.py`, `check-phase12-libbpf-snapshot.py`, `check-phase12-libbpf-packet.py`, and `validate-phase12.py` keep the shared Phase 12 complex-driver and heavy-helper tranche aligned before replay by checking the workflow wiring, `zigux/Makefile`, `zigux/tests/phase12_build.zig`, the shared build inventory snapshot in `zigux/tests/fixtures/phase12_build_inventory.json`, the committed libbpf reproducibility packet in `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, the bounded libbpf packet-alignment contract across `zigux/tests/phase12_libbpf_manifest.json`, `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, and `tools/lib/bpf/zigux_segments/manifest.json`, the four manifests `zigux/tests/phase12_virtio_net_manifest.json`, `zigux/tests/phase12_nvme_pci_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_libbpf_manifest.json`, plus the survey notes pinned to each manifest's exact `surveyed_commit`; the bounded build-inventory checker still proves its own repeat-run stability and artifact-drift detection path through `--self-test`, while the libbpf snapshot and packet checkers keep the committed reproducibility packet and heavier reviewability contract explicit instead of leaving them implied behind the shared validator.
- `make -C zigux phase12-validate` is the fail-fast bundle check for that shared degraded-workflow packet before the shared Zig replay runs, and it now executes the build-inventory self-test plus the committed libbpf snapshot and packet-alignment checks before comparing the live shared build file against the committed fixture.
- `make -C zigux phase12` keeps the current Phase 12 bundle reviewable through one shared tranche entrypoint instead of ad hoc complex-driver commands.
- `Documentation/zigux/phase12-shared-replay-contract.md`, `scripts/zigux/check-phase12-libbpf-focused-replay.py`, `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, and `zigux/tests/phase12_libbpf_only_build.zig` keep the shared-versus-focused Phase 12 libbpf replay boundary explicit in the scripts root, so the focused libbpf-only replay hook stays a dedicated shard instead of being implied behind the broader shared build inventory.
- the current active storage-driver survey packet stays explicit through `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, and the paired `zigux/tests/phase12_virtio_scsi_{manifest,survey}.zig` files, so the queue-layout, recovery, probe snapshot, host-limit summary, queue-depth summary, and io-queue-map starters remain visible without overstating the still-blocked DMA-backed queue ownership, `Scsi_Host` lifecycle, or blk-mq follow-up.

Phase 15 flow
- keep the current Phase 15 governance packet reviewable through `zigux/tests/phase15_build.zig`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/tests/phase15_readiness_gate.zig`, `zigux/tests/phase15_handoff_next_steps.zig`, `zigux/tests/phase15_docs_root_reviewability.zig`, `scripts/zigux/validate-phase15.py`, `make -C zigux phase15-validate`, `make -C zigux phase15`, and `zig build test --build-file zigux/tests/phase15_build.zig` so the shared governance replay and docs-root maintenance packet stay aligned.
- keep the paired manifest-backed Phase 15 governance packet explicit too: `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_parity_scorecard.json`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_readiness_gate_manifest.json`, and `zigux/tests/phase15_handoff_next_steps_manifest.json` should continue to name the same governance evidence, replay path, and blocked deep-core status-change posture as the docs root and validator.
