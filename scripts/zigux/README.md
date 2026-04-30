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
- `check-zig-toolchain.py`
- `validate-bootstrap.py`
- `install-zig.py`
- `validate-phase1.py`
- `check-phase1-bench.py`
- `validate-phase1-closure.py`
- `validate-phase2.py`
- `validate-phase2-closure.py`
- `validate-phase3.py`
- `validate-phase4.py`
- `validate-phase5.py`
- `validate-phase6.py`
- `validate-phase7.py`
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

Phase 2 flow
- `artifact_diff.py --self-test` exercises the shared text, JSON, SHA-256, and missing-file comparison paths before the bounded Phase 2 artifact lanes run.
- `check-artifact-diff-contract.py` keeps the outward artifact-diff CLI surface reviewable inside the closed Phase 2 packet so missing-file, malformed-JSON, and SHA-256 contract drift cannot hide behind the helper's built-in self-test.
- `validate-phase1.py` now also checks that `zigux/tests/fixtures/phase1_helpers.json` keeps the exact committed top-level helper sections and evidence-key shape, so stale Phase 1 expected-output drift fails before parity replay.
- `validate-phase2.py` checks that the bounded Phase 2 helper inventory, fixture set, workflow wiring, and docs markers stay in sync before the parity lanes run.
- `validate-phase2-closure.py` confirms the closed Phase 2 tranche still matches the workflow, the closure docs, and the Phase 2 manifests.
- `check-fixdep-diff.py` compares the bounded `fixdep.zig` output against the committed fixture set, including the multi-target, escaped-whitespace, comment-only no-target, and missing-dependency failure artifacts under `zigux/tests/fixtures/fixdep/`, reruns both the C tool and Zig tool to prove repeat-run artifact determinism, and now also fails if any success-path fixdep case starts emitting unexpected stderr noise.
- `check-genksyms-bridge.py` exercises the bounded `genksyms.zig` bridge parity lane, including success-path stderr silence and repeat-run stderr determinism for the stdout-json bridge fixtures.
- `check-genksyms-crc-diff.py` checks the bounded `genksyms_crc.zig` artifact lane and now proves repeat-run JSON determinism for both the bounded C harness and Zig tool before fixture comparison.
- `check-kconfig-bridge.py --self-test` exercises the bounded kconfig bridge checker packet itself before the Linux-style `phase2-kconfig` entrypoint replays the live bridge artifacts.
- `check-kconfig-bridge.py` covers the bounded `kconfig/conf_bridge.zig` and `kconfig/confdata_bridge.zig` bridge lanes and now proves repeat-run JSON determinism for both bridge outputs before fixture comparison.
- `check-phase2-cross.py --self-test` exercises the bounded cross-target checker packet itself before the Linux-style `phase2-cross` entrypoint replays live Zig compiles, so manifest-count and explicit-target failure drift cannot hide behind local tool availability.
- `check-phase2-cross.py` runs the bounded Phase 2 cross-target compile checks.
- `check-mk-elfconfig-diff.py` covers the bounded `mk_elfconfig.zig` artifact lane and now proves repeat-run JSON determinism for both the bounded C tool and Zig tool before fixture comparison.
- `check-phase1-parity.py` now reruns the bounded C harness after fixture comparison so the shared Phase 1 parity artifact also proves repeat-run JSON determinism instead of only a single-pass match.
- `check-phase1-bench.py --self-test` exercises the bounded Phase 1 benchmark checker itself before the live benchmark smoke runs, so parser, expected-key, and undeclared-key drift cannot hide behind a locally passing Zig bench replay.

Phase 3 flow
- `validate-phase3-roadmap-gap-survey.py` checks that `Documentation/zigux/phase3-roadmap-gap-survey.md` stays aligned with the live repo-backed Phase 3 substrate, the published README note, the current export shim and current `zigux/uapi/version.zig` boundary, the current roadmap-backed `rbtree` gap, and the already-landed Phase 1 plus Phase 7 `rbtree` evidence that still falls short of a Phase 3 boundary-facing packet.
- `validate-phase3-roadmap-gap-survey.py --self-test` exercises the survey-marker and README-hook checks without needing the full repo tree.
- `validate-phase3-export-uapi-survey.py` checks that `Documentation/zigux/phase3-export-uapi-boundary-survey.md` stays aligned with the live export-shim and bounded `zigux/uapi/version.zig` surface, the published README notes, and the shared `make -C zigux phase3-validate` entrypoint.
- `validate-phase3-export-uapi-survey.py --self-test` exercises the export-shim and UAPI survey-marker checks without needing the full repo tree.
- `validate-phase3.py` now requires the focused `phase3-policy-unsafe` build and test files plus the published `PHASE3_POLICY_UNSAFE_GATE` ABI-slice marker, so the landed policy and unsafe substrate no longer hides only inside the broader ABI replay and keeps the dedicated interop-policy unsafe-byte decoding gate reviewable on its own.
- the same validator now keeps `zigux/helpers/layout_assert.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/mmio.zig`, `zigux/unsafe/narrow.zig`, `zigux/tests/phase3_policy_unsafe.zig`, and `zigux/tests/phase3_policy_unsafe_build.zig` aligned with `zigux/tests/fixtures/phase3_abi_manifest.json` and `Documentation/zigux/phase3-abi-slice.md`, so allocator-owned init and reset requirements plus the scoped narrow-unsafe and MMIO helper path cannot drift out of the published packet silently.
- the same validator surface now also carries the latest focused policy evidence: `zigux/tests/phase3_policy_unsafe.zig` covers overflow-checked unsafe address math, and the Phase 3 source-audit self-test keeps the layout-assert, panic-policy, allocator-policy, and narrow-unsafe markers reviewable even when the full repo tree is not under replay.
- the same validator now also treats the focused low-level wrapper gate as a real anti-regression surface instead of a presence-only file list: it restores the shared self-test import path, checks the exact exported atomic, barrier, and MMIO helper surface against the published Phase 3 ABI slice, and still checks the scoped `read16`, `write16`, `read32`, and `write32` MMIO entry points plus the low-level replay’s compare-exchange mismatch, barrier probe, denied-scope, and allowed scoped-MMIO assertions so width-specific, scope-specific, or undocumented wrapper-surface drift fails before Phase 3 review claims stay green.

Phase 4 flow
- `artifact_diff.py --self-test` now runs as part of `make -C zigux phase4-validate` so the shared text, JSON, SHA-256, and missing-file comparison paths stay live before the rollback-readiness checks run.
- `check-artifact-diff-contract.py` keeps one stable pass case, one missing-file failure case, malformed expected and actual JSON failure shapes, and SHA-256 pass and drift cases of the outward helper CLI reviewable beside the built-in self-test, including the emitted `EXPECTED_JSON_ERROR=...`, `ACTUAL_JSON_ERROR=...`, `SHA256=...`, `EXPECTED_SHA256=...`, and `ACTUAL_SHA256=...` fields.
- `validate-phase4.py` checks that the bounded Phase 4 differential gates, the manifest-backed `test_fsmount` survey packet, the manifest-backed `phase4_perf_baseline_manifest.json` packet, that shared artifact-diff self-test, their shared `zigux/tests/phase4_build.zig` entrypoint, and the directly coupled documentation and workflow markers stay aligned, including the current `make M=samples/vfs` C-anchor-only replay posture while `samples/zigux/test_fsmount.zig` remains absent.
- `Documentation/zigux/phase4-validation-matrix.md` keeps the current rollback owners, threshold posture, the exact workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`, the shared `phase4-runtime-atomic64-diff-tests`, `phase4-runtime-atomic64-diff-survey-tests`, `phase4-test-fsmount-survey-tests`, `phase4-perf-baseline-survey-tests`, and `phase4-bitmap-diff-tests` replay anchors, the manifest-backed `test_fsmount` survey row, the manifest-backed perf-baseline survey row, the dedicated `make -C zigux phase4-test-fsmount-survey` and `make -C zigux phase4-perf-baseline-survey` replay paths, its current `make M=samples/vfs` C-anchor-only lab posture, the `perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land` posture, plus the reversible-delivery evidence that ties each shipped Phase 4 gate back to its current C anchor if the shared entrypoint has to drop that Zig gate.

Phase 5 flow
- `validate-phase5.py` keeps the shared Phase 5 reference-sample packet aligned before replay by checking the published notes, the workflow, `zigux/Makefile`, `zigux/tests/phase5_build.zig`, the four sample-backed survey manifests, and the shared `samples/zigux/README.md` catalog boundary.
- `make -C zigux phase5-validate` is the fail-fast bundle check for the current bytestream FIFO, kobject, kretprobe, and trace-events sample bundle.
- `make -C zigux phase5` keeps that same non-runtime reference-sample lane reviewable through one validator-first path instead of ad hoc sample-local commands.
- `zigux/tests/phase5_build.zig` is the shared replay entrypoint for `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, `zigux/tests/phase5_kobject_example_survey.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_survey.zig`, `zigux/tests/phase5_trace_events_sample.zig`, and `zigux/tests/phase5_trace_events_sample_survey.zig`.
- `samples/zigux/README.md` stays in that same validation surface so the four approved Phase 5 reference samples remain visibly distinct from the later `runtime_*` starters that share the directory.

Phase 6 flow
- `validate-phase6.py` keeps the shared Phase 6 leaf-helper bundle aligned before replay by checking the published notes, the shared manifest, the workflow, `zigux/Makefile`, and `zigux/tests/phase6_build.zig`.
- `make -C zigux phase6-validate` is the fail-fast catalog check for the current base64, bsearch, checksum, and hexdump packet.
- `make -C zigux phase6` and the per-helper perf targets keep the shared leaf-helper lane reviewable through one bundle instead of ad hoc helper-local checks.
- `Documentation/zigux/phase6-helper-parity-catalog.md` and `zigux/tests/phase6_helper_parity_manifest.json` are the shared reviewer-facing and machine-readable inventory surfaces for that same bundle and should move together with any Phase 6 helper, perf, fixture, or slice-note ownership change.
- `python3 scripts/zigux/check-phase6-base64-c-parity.py` replays a representative external C-vs-Zig base64 spot check so portability-sensitive helper drift is reviewable beyond the shared Zig-only tests.
- `python3 scripts/zigux/check-phase6-bsearch-c-parity.py` replays a representative external C-vs-Zig bsearch spot check so portability-sensitive helper drift is reviewable beyond the shared Zig-only tests.
- the current published slice notes for `Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, and `Documentation/zigux/phase6-hexdump-slice.md` are part of that same shared validation surface.

Phase 7 flow
- `validate-phase7.py` keeps the shared Phase 7 runtime-helper bundle aligned before replay by checking the published notes, the workflow, `zigux/Makefile`, `zigux/tests/phase7_build.zig`, and the current external `rbtree` parity hook.
- `validate-phase7.py --self-test` proves the shared validator still fails closed if the `phase7-validate` Makefile hook, the bootstrap workflow self-test step, or the parked argv-split survey guard drift out of the published packet.
- `make -C zigux phase7-validate` is the fail-fast bundle check for the current string-helpers, cmdline, argv-split, and rbtree packet.
- `make -C zigux phase7-test` is the shared local wrapper for the current `zigux/tests/phase7_build.zig` replay and now follows the same `zig build test --build-file zigux/tests/phase7_build.zig --summary all` path that the bootstrap workflow uses.
- `zigux/tests/phase7_build.zig` currently keeps the helper packet split in one deliberate way: `phase7_string_helpers.zig`, `phase7_cmdline.zig`, `phase7_argv_split.zig`, and `phase7_rbtree.zig` receive `lib/*.zig` code through `addImport(...)` aliases; `phase7_string_helpers_survey.zig` plus `phase7_cmdline_survey.zig` stay standalone so the helper-only string and cmdline slices keep their roadmap-backed review notes explicit without pretending there is a Phase 5 `samples/zigux/*string*` reference sample or extra helper-local bootstrap glue; and `phase7_argv_split_survey.zig` plus `phase7_rbtree_survey.zig` stay self-contained and read `zigux/tests/phase7_argv_split_manifest.json` plus `zigux/tests/phase7_rbtree_manifest.json` from repo-root paths at runtime, with `phase7_build.zig` setting those survey runs to `repo_root` so the manifest reads stay stable.
- `make -C zigux phase7` keeps that same runtime-helper lane reviewable through one shared bundle instead of ad hoc slice-local checks.
- `python3 scripts/zigux/check-phase7-rbtree-parity.py` replays the current external C-vs-Zig `rbtree` parity fixture so the parked Phase 7 packet still carries one representative non-Zig-only evidence path.
- the current published slice notes for `Documentation/zigux/phase7-string-helpers-slice.md`, `Documentation/zigux/phase7-cmdline-slice.md`, `Documentation/zigux/phase7-argv-split-slice.md`, and `Documentation/zigux/phase7-rbtree-slice.md` are part of that same shared validation surface.

Phase 8 flow
- `validate-phase8.py` keeps the shared Phase 8 tooling bundle aligned before replay by checking the published notes, the workflow, `zigux/Makefile`, `zigux/tests/phase8_build.zig`, and the current libbpf helper-family survey surfaces around `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/pin_path.zig`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, and `tools/lib/bpf/zigux_segments/type_names.zig`.
- `make -C zigux phase8-validate` is the fail-fast bundle check for the current exec-cmd, help, kallsyms, cpu-mask, logging, pin-path, file-path-handle bridge, type-name, and manifest-backed libbpf survey packet.
- `zigux/tests/phase8_help_only_build.zig` and `zigux/tests/phase8_kallsyms_only_build.zig` keep the parked help and kallsyms packets reviewable through their own focused replay entrypoints instead of only through the broader shared Phase 8 tooling bundle.
- `zigux/tests/phase8_libbpf_segments_only_build.zig` is the focused replay entrypoint for the manifest-backed libbpf survey packet and should stay exposed beside the broader `zigux/tests/phase8_build.zig` bundle so bridge-boundary and segment-survey drift is reviewable without rerunning the full Phase 8 tooling shard.
- `zigux/tests/phase8_build.zig` is the shared Phase 8 replay entrypoint for `zigux/tests/phase8_exec_cmd.zig`, `zigux/tests/phase8_help.zig`, `zigux/tests/phase8_kallsyms.zig`, `zigux/tests/phase8_cpu_mask.zig`, `zigux/tests/phase8_logging.zig`, `zigux/tests/phase8_pin_path.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_libbpf_segments.zig`, and `zigux/tests/phase8_bpf_type_names.zig`, and `make -C zigux phase8-test` now follows the same `zig build test --build-file zigux/tests/phase8_build.zig --summary all` path that the bootstrap workflow and verification note already publish.
- `Documentation/zigux/phase8-exec-cmd-slice.md` stays in that same packet so the parked `tools/lib/subcmd/exec-cmd.zig` slice keeps its deferred execution note explicit and does not drift into `execvp()` ownership or the later `kernel/workqueue.c` boundary-study lane.
- `Documentation/zigux/phase8-libbpf-segment-survey.md` keeps the bounded libbpf helper catalog explicit, including the deferred `perf-buffer-online-cpu-routing` boundary beside `tools/lib/bpf/zigux_segments/cpu_mask.zig`.
- `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md` keeps the cross-slice control-plane contract explicit between the parked command-preparation helpers and the still-deferred procfs, bpffs, token, and direct handle-lifecycle behavior.
- `Documentation/zigux/phase8-libbpf-cpu-mask-slice.md` keeps the landed `tools/lib/bpf/zigux_segments/cpu_mask.zig` helper scoped to parsing, chunk-reader ingestion, and counted mask output without overstating `parse_cpu_mask_file()` parity, `libbpf_num_possible_cpus()` caching, or perf-buffer routing behavior.
- `Documentation/zigux/phase8-bpf-type-names-slice.md` and `tools/lib/bpf/zigux_segments/type_names.zig` stay in the same review packet so the current type-name helper does not drift away from the shared `make -C zigux phase8` entrypoint.
- the same Phase 8 README packet keeps the deferred `file-path-and-handle-bridge` and `perf-buffer-online-cpu-routing` boundaries explicit so the helper-first libbpf rollout does not quietly widen into bpffs handle ownership or perf-buffer routing claims, and so the parked command-side helpers do not quietly widen into direct process-launch or terminal-probing behavior either.

Phase 9 flow
- `validate-phase9.py` keeps the shared Phase 9 runtime bundle aligned before replay by checking the published notes, the workflow, `zigux/Makefile`, `zigux/tests/phase9_build.zig`, the trace-events freeze-map boundary packet, and the shared runtime-loader release-discipline evidence, and `python3 scripts/zigux/validate-phase9.py --self-test` now proves that the shared validator still catches both Makefile-hook drift and the trace-events surveyed-head pin.
- the same Phase 9 flow also keeps the roadmap's shipped selftest-hook markers and bounded lifecycle-parity posture explicit across the runtime starter surveys, manifests, and shared `zigux/tests/phase9_build.zig` replay instead of implying a ready loadable-module path.
- `make -C zigux phase9-validate` is the fail-fast bundle check for the current runtime atomic64, bitmap, trace-events, kretprobe, and shared loader-gap packet.
- `make -C zigux phase9-trace-events-survey` is the focused trace-events survey replay when the current Phase 9 lane needs the paired survey gate without the rest of the shared runtime bundle.
- `make -C zigux phase9` keeps that same runtime lane reviewable through one shared bundle instead of ad hoc slice-local checks.
- `Documentation/zigux/phase9-runtime-loader-gap-survey.md` and `Documentation/zigux/review-checklist.md` carry the shared Phase 9 loader-handoff release-discipline evidence for the current runtime bundle.
- `zigux/tests/runtime_loader_gap_manifest.json` keeps the manifest-backed catalog and ownership map for the shared runtime-loader evidence packet, so reviewers can see which file owns the survey note, the review checklist, the shared request contract, the sample-side loader plans, and the shared `phase9_build.zig` replay path before the lane widens again.

Phase 10 flow
- `validate-phase10.py` keeps the current Phase 10 input-plus-MMIO starter packet explicit before replay by checking the published Phase 10 notes, the workflow wiring, `zigux/Makefile`, the shared `zigux/tests/phase10_build.zig` replay path, `drivers/virtio/virtio_input.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_manifest.json`, `drivers/virtio/virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio.zig`, and `zigux/tests/phase10_virtio_mmio_manifest.json`.
- `make -C zigux phase10-validate` is now the fail-fast bundle check for both the shared Phase 10 closure packet and the narrower virtio_input registration guard.
- the Phase 10 validator keeps `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, and `Documentation/zigux/phase10-virtio-input-module-slice.md` aligned with the landed `phase10-virtio-input-registration-preflight-helper`, the now-landed `phase10-virtio-input-queue-callback-preflight-helper`, and the blocked registration-lifecycle contract.
- this keeps the current input lane honest now that the queue-callback preflight helper is landed, with the already-landed registration-preflight summary and earlier `ABS_MT_SLOT` planning helper staying as bounded prerequisites before any wider `input_register_device()` claim.

Phase 11 flow
- `check-phase11-build-inventory.py` regenerates the committed `zigux/tests/fixtures/phase11_build_inventory.json` snapshot from `zigux/tests/phase11_build.zig` and fails if the shared build inventory or the dedicated `hvc_console` survey boundary drifts.
- `validate-phase11.py --self-test` now mutates a tiny Phase 11 fixture clone so the shared gate proves it fails closed if the `phase11-validate` hook disappears or if the parked `gpio_wdt` teardown-summary or `hvc_console` worker-timeout failure-mode evidence drifts out of the focused tests.
- `validate-phase11.py` keeps the current simple-driver packet aligned before replay by checking the workflow wiring, `zigux/Makefile`, `zigux/tests/phase11_build.zig`, the shared build inventory snapshot in `zigux/tests/fixtures/phase11_build_inventory.json`, the four driver-local manifests `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_manifest.json`, and `zigux/tests/phase11_hvc_console_manifest.json`, plus the shared header-boundary manifest `zigux/tests/phase11_uapi_header_parity_manifest.json`.
- `make -C zigux phase11-validate` is the fail-fast catalog check for the current watchdog, hvc, and shared header-boundary packet, and now runs the dedicated build-inventory checker before the broader validator.
- `make -C zigux phase11-hvc-survey` is the dedicated archival replay for `zigux/tests/phase11_hvc_console_survey.zig`, and it now routes through the dedicated `hvc-console-survey` step inside `zigux/tests/phase11_build.zig` so the shared `layout_assert` wiring stays intact when the bootstrap workflow runs that command after the main shared replay.
- the validator also keeps the dedicated hvc_console survey note and validation matrix aligned with the exact shared-versus-dedicated replay commands and observed outcome lines, so the repo does not silently imply that `zigux/tests/phase11_hvc_console_survey.zig` already runs inside the shared `zigux/tests/phase11_build.zig` path or that CI skips the archival survey replay.
- `make -C zigux phase11` keeps that same simple-driver lane reviewable through one shared bundle instead of ad hoc slice-local checks.

Phase 12 flow
- `check-phase12-build-inventory.py`, `check-phase12-libbpf-snapshot.py`, and `validate-phase12.py` keep the shared Phase 12 complex-driver and heavy-helper tranche aligned before replay by checking the workflow wiring, `zigux/Makefile`, `zigux/tests/phase12_build.zig`, the shared build inventory snapshot in `zigux/tests/fixtures/phase12_build_inventory.json`, the committed libbpf reproducibility packet in `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, the four manifests `zigux/tests/phase12_virtio_net_manifest.json`, `zigux/tests/phase12_nvme_pci_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_libbpf_manifest.json`, plus the survey notes pinned to each manifest's exact `surveyed_commit`.
- `make -C zigux phase12-validate` is the fail-fast bundle check for that shared degraded-workflow packet before the shared Zig replay runs, and it now also proves that the bounded libbpf manifest, survey, reviewability gate, note, and legacy segment catalog regenerate the same snapshot JSON on repeat runs.
- `make -C zigux phase12` keeps the current Phase 12 bundle reviewable through one shared tranche entrypoint instead of ad hoc complex-driver commands.
- the current shared Zig replay has moved ahead again: `zig build test --build-file zigux/tests/phase12_build.zig --summary all` now reports `Build Summary: 17/17 steps succeeded; 53/53 tests passed`, and the committed `zigux/tests/fixtures/phase12_build_inventory.json` fast-inventory packet now records that same summary so future note or validator work can treat the shared build inventory as current.
- the current active storage-driver survey packet stays explicit through `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, and the paired `zigux/tests/phase12_virtio_scsi_{manifest,survey}.zig` files, so the queue-layout, recovery, probe snapshot, host-limit summary, queue-depth summary, and io-queue-map starters remain visible without overstating the still-blocked DMA-backed queue ownership, `Scsi_Host` lifecycle, or blk-mq follow-up.

Phase 13 flow
- `validate-phase13-release.py` keeps the shared Phase 13 helper bundle aligned before replay by checking the published release note `Documentation/zigux/phase13-release-notes-survey.md`, roadmap traceability note `Documentation/zigux/phase13-roadmap-traceability.md`, review checklist `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/Makefile`, `zigux/tests/phase13_build.zig`, the four roadmap-anchor manifests `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`, plus the adjacent notifier-list reviewability packet.
- `make -C zigux phase13-validate` is the fail-fast bundle check for the current shared-helper tranche before the shared Zig replay runs.
- `make -C zigux phase13` routes through the validator before the shared replay and keeps that same Phase 13 tranche reviewable through one validator-first path instead of ad hoc slice-local commands.
- the current shared packet now carries four manifest-backed roadmap-anchor surveys, and `Documentation/zigux/phase13-devres-survey.md` plus `zigux/tests/phase13_devres_reviewability.zig` keep the helper-only MMIO or resource-planner surface explicit while still blocking live DMA-backed mappings and scatterlist ownership.

Phase 14 flow
- `validate-phase14.py` keeps the shared Phase 14 smoke packet aligned before replay by checking `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, and the four anchor-local Phase 14 manifests.
- `make -C zigux phase14-validate` is the fail-fast validator for that shared Phase 14 smoke packet before the broader replay runs.
- `make -C zigux phase14-smoke` is the focused smoke-shard replay contract for the shared packet, while `zigux/tests/phase14_build.zig` still carries the broader anchor-local replay bundle.
- `make -C zigux phase14` and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` keep the same stay-in-C boundary bundle reviewable without implying new workqueue, skbuff, ring-buffer, or RCU bridge delivery.
- the same shared Phase 14 packet now also keeps the roadmap risk bundle (`hidden runtime behavior`, `memory-ordering mistakes`, `overpromising full parity`, `deep-core scope creep`) plus one rollback threshold, fallback path, and automatic return-to-blocked trigger catalog explicit across the manifest, survey note, checklist, and validator.
