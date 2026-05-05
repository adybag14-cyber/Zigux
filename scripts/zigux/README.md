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
- `validate-phase6.py`
- `validate-phase7.py`
- `validate-phase8.py`
- `validate-phase9.py`
- `validate-phase10.py`
- `validate-phase10-closure.py`
- `validate-phase11.py`
- `check-phase12-build-inventory.py`
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
- `check-phase9-module-metadata-packet.py`

Zig toolchain gate
- `check-zig-toolchain.py` verifies that the selected Zig binary exists and satisfies the configured minimum version.
- `check-zig-toolchain.py --self-test` runs built-in parser and version-ordering coverage without needing a local Zig install.

Phase 2 flow
- `artifact_diff.py --self-test` exercises the shared text, JSON, SHA-256, and missing-file comparison paths before the bounded Phase 2 artifact lanes run.
- `validate-phase1.py` now also checks that `zigux/tests/fixtures/phase1_helpers.json` keeps the exact committed top-level helper sections and evidence-key shape, so stale Phase 1 expected-output drift fails before parity replay.
- `validate-phase2.py` checks that the bounded Phase 2 helper inventory, fixture set, workflow wiring, and docs markers stay in sync before the parity lanes run.
- `validate-phase2-closure.py` confirms the closed Phase 2 tranche still matches the workflow, the closure docs, and the Phase 2 manifests.
- `check-fixdep-diff.py` compares the bounded `fixdep.zig` output against the committed fixture set, including the multi-target, escaped-whitespace, comment-only no-target, and missing-dependency failure artifacts under `zigux/tests/fixtures/fixdep/`, reruns both the C tool and Zig tool to prove repeat-run artifact determinism, and now also fails if any success-path fixdep case starts emitting unexpected stderr noise.
- `check-genksyms-bridge.py` exercises the bounded `genksyms.zig` bridge parity lane.
- `check-genksyms-crc-diff.py` checks the bounded `genksyms_crc.zig` artifact lane and now proves repeat-run JSON determinism for both the bounded C harness and Zig tool before fixture comparison.
- `check-kconfig-bridge.py` covers the bounded `kconfig/conf_bridge.zig` and `kconfig/confdata_bridge.zig` bridge lanes.
- `check-phase2-cross.py` runs the bounded Phase 2 cross-target compile checks.
- `check-mk-elfconfig-diff.py` covers the bounded `mk_elfconfig.zig` artifact lane and now proves repeat-run JSON determinism for both the bounded C tool and Zig tool before fixture comparison.
- `check-phase1-parity.py` now reruns the bounded C harness after fixture comparison so the shared Phase 1 parity artifact also proves repeat-run JSON determinism instead of only a single-pass match.

Phase 3 flow
- `validate-phase3-roadmap-gap-survey.py` checks that `Documentation/zigux/phase3-roadmap-gap-survey.md` stays aligned with the live repo-backed Phase 3 substrate, the published README note, the current export shim and current `zigux/uapi/version.zig` boundary, and the current roadmap-backed `rbtree` gap.
- `validate-phase3-roadmap-gap-survey.py --self-test` exercises the survey-marker and README-hook checks without needing the full repo tree.
- `validate-phase3-export-uapi-survey.py` checks that `Documentation/zigux/phase3-export-uapi-boundary-survey.md` stays aligned with the live export-shim and bounded `zigux/uapi/version.zig` surface, the published README notes, and the shared `make -C zigux phase3-validate` entrypoint.
- `validate-phase3-export-uapi-survey.py --self-test exercises the export-shim and UAVI survey-marker checks without needing the full repo tree.
- `validate-phase3.py` now requires the focused `phase3-policy-unsafe` build and test files plus the published `PHASE3_POLICY_UNSAFE_GATE` ABI-slice marker, so the landed policy and unsafe substrate no longer hides only inside the broader ABI replay.
- the same validator now keeps `zigux/helpers/layout_assert.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/unsafe/narrow.zig`, `zigux/tests/phase3_policy_unsafe.zig`, `zigux/tests/phase3_policy_unsafe_build.zig` aligned with `zigux/tests/fixtures/phase3_abi_manifest.json` and `Documentation/zigux/phase3-abi-slice.md`.

Phase 6 flow
- `validate-phase6.py` keeps the shared Phase 6 leaf-helper bundle aligned before replay by checking the published notes, the workflow, `zigux/Makefile`, and `zigux/tests/phase6_build.zig`.
- `make -C zigux phase6-validate` is the fail-fast catalog check for the current base64, bsearch, checksum, and hexdump packet.
- `make -C zigux phase6` and the per-helper perf targets keep the shared leaf-helper lane reviewable through one bundle instead of ad hoc helper-local checks.
- `Documentation/zigux/phase6-helper-parity-catalog.md` is the shared inventory note for that same bundle and should move together with any Phase 6 helper, perf, fixture, or slice-note ownership change.
- `python3 scripts/zigux/check-phase6-base64-c-parity.py` replays a representative external C-vs-Zig base64 spot check so portability-sensitive helper drift is reviewable beyond the shared Zig-only tests.
- `python3 scripts/zigux/check-phase6-bsearch-c-parity.py` replays a representative external C-vs-Zig bsearch spot check so portability-sensitive helper drift is reviewable beyond the shared Zig-only tests.
- the current published slice notes for `Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, and `Documentation/zigux/phase6-hexdump-slice.md` are part of that same shared validation surface.

Phase 7 flow
- `validate-phase7.py` keeps the shared Phase 7 runtime-helper bundle aligned before replay by checking the published notes, the workflow, `zigux/Makefile`, `zigux/tests/phase7_build.zig`, and the current external `rbtree` parity hook.
- `make -C zigux phase7-validate` is the fail-fast bundle check for the current string-helpers, cmdline, argv-split, and rbtree packet.
- `make -C zigux phase7-test` is the shared local wrapper for the current `zigux/tests/phase7_build.zig` replay, while the bootstrap workflow intentionally uses the same build file through `zig build test --build-file zigux/tests/phase7_build.zig --summary all` so CI keeps the extra step summary without changing the exercised test bundle.
- `zigux/tests/phase7_build.zig` currently has two explicit handoff styles: `phase7_string_helpers.zig`, `phase7_cmdline.zig`, `phase7_argv_split.zig`, and `phase7_rbtree.zig` receive `lib/*.zig` code through `addImport(...)` aliases, while `phase7_argv_split_survey.zig` and `phase7_rbtree_survey.zig` stay self-contained and read `zigux/tests/phase7_argv_split_manifest.json` plus `zigux/tests/phase7_rbtree_manifest.json` from repo-root paths at runtime.
- `make -C zigux phase7` keeps that same runtime-helper lane reviewable through one shared bundle instead of ad hoc slice-local checks.
- `python3 scripts/zigux/check-phase7-rbtree-parity.py` replays the current external C-vs-Zig `rbtree` parity fixture so the parked Phase 7 packet still carries one representative non-Zig-only evidence path.
- the current published slice notes for `Documentation/zigux/phase7-string-helpers-slice.md`, `Documentation/zigux/phase7-cmdline-slice.md`, `Documentation/zigux/phase7-argv-split-slice.md`, and `Documentation/zigux/phase7-rbtree-slice.md` are part of that same shared validation surface.

Phase 8 flow
- `validate-phase8.py` keeps the shared Phase 8 tooling bundle aligned before replay by checking the published notes, the workflow, `zigux/Makefile`, `zigux/tests/phase8_build.zig`, and the current libbpf helper-family survey surfaces around `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/pin_path.zig`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, and `tools/lib/bpf/zigux_segments/type_names.zig`.
- `make -C zigux phase8-validate` is the fail-fast bundle check for the current exec-cmd, help, kallsyms, cpu-mask, logging, pin-path, file-path-handle bridge, type-name, and manifest-backed libbpf survey packet.
- `zigux/tests/phase8_libbpf_segments_only_build.zig` is the focused replay entrypoint for the manifest-backed libbpf survey packet and should stay exposed beside the broader `zigux/tests/phase8_build.zig` bundle so bridge-boundary and segment-survey drift is reviewable without rerunning the full Phase 8 tooling shard.
- `zigux/tests/phase8_build.zig` is the shared Phase 8 replay entrypoint for `zigux/tests/phase8_exec_cmd.zig`, `zigux/tests/phase8_help.zig`, `zigux/tests/phase8_kallsyms.zig`, `zigux/tests/phase8_cpu_mask.zig`, `zigux/tests/phase8_logging.zig`, `zigux/tests/phase8_pin_path.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_libbpf_segments.zig`, and `zigux/tests/phase8_bpf_type_names.zig`.
- `Documentation/zigux/phase8-exec-cmd-slice.md` stays in that same packet so the parked `tools/lib/subcmd/exec-cmd.zig` slice keeps its deferred execution note explicit and does not drift into `execvp()` ownership or the later `kernel/workqueue.c` boundary-study lane.
- `Documentation/zigux/phase8-libbpf-segment-survey.md` keeps the bounded libbpf helper catalog explicit, including the deferred `perf-buffer-online-cpu-routing` boundary beside `tools/lib/bpf/zigux_segments/cpu_mask.zig`.
- `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md` keeps the cross-slice control-plane contract explicit between the parked command-preparation helpers and the still-deferred procfs, bpffs, token, and direct handle-lifecycle behavior.
- `Documentation/zigux/phase8-libbpf-cpu-mask-slice.md` keeps the landed `tools/lib/bpf/zigux_segments/cpu_mask.zig` helper scoped to parsing, chunk-reader ingestion, and counted mask output without overstating `parse_cpu_mask_file()` parity, `libbpf_num_possible_cpus()` caching, or perf-buffer routing behavior.
- `Documentation/zigux/phase8-bpf-type-names-slice.md` and `tools/lib/bpf/zigux_segments/type_names.zig` stay in the same review packet so the current type-name helper does not drift away from the shared `make -C zigux phase8` entrypoint.
- the same Phase 8 README packet keeps the deferred `file-path-and-handle-bridge` and `perf-buffer-online-cpu-routing` boundaries explicit so the helper-first libbpf rollout does not quietly widen into bpffs handle ownership or perf-buffer routing claims, and so the parked command-side helpers do not quietly widen into direct process-launch or terminal-probing behavior either.

Phase 9 flow
- `validate-phase9.py` keeps the shared Phase 9 runtime bundle aligned before replay by checking the published notes, the workflow, `zigux/Makefile`, `zigux/tests/phase9_build.zig`, the trace-events freeze-map boundary packet, the dedicated module-metadata packet, and the shared runtime-loader release-discipline evidence.
- `make -C zigux phase9-validate` is the fail-fast bundle check for the current runtime atomic64, bitmap, trace-events, kretprobe, and shared loader-gap packet.
- `make -C zigux phase9` keeps that same runtime lane reviewable through one shared bundle instead of ad hoc slice-local checks.
- `Documentation/zigux/phase9-runtime-loader-gap-survey.md` and `Documentation/zigux/review-checklist.md` carry the shared Phase 9 loader-handoff release-discipline evidence for the current runtime bundle.
- `zigux/tests/runtime_loader_gap_manifest.json` keeps the manifest-backed catalog and ownership map for the shared runtime-loader evidence packet, so reviewers can see which file owns the survey note, the review checklist, the shared request contract, the sample-side loader plans, and the shared `phase9_build.zig` replay path before the lane widens again.
- `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`, `zigux/tests/runtime_module_metadata_manifest.json`, `zigux/tests/runtime_module_metadata_survey.zig`, and `check-phase9-module-metadata-packet.py` keep the dedicated starter-descriptor and loader-plan evidence reviewable without implying a landed depmod bridge.

Phase 10 flow
- `validate-phase10.py` keeps the current virtio_input registration boundary explicit before replay by checking the published Phase 10 notes, the workflow wiring, `zigux/Makefile`, `drivers/virtio/virtio_input.zig`, `zigux/tests/phase10_virtio_input.zig`, and `zigux/tests/phase10_virtio_input_manifest.json`.
- `make -C zigux phase10-validate` is now the fail-fast bundle check for both the shared Phase 10 closure packet and the narrower virtio_input registration guard.
- the Phase 10 validator keeps `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, and `Documentation/zigux/phase10-virtio-input-module-slice.md` aligned with the manifest-backed ready-next `phase10-virtio-input-registration-preflight-helper` and the blocked registration-lifecycle contract.
- this keeps the current input lane honest while ABS_MT_SLOT remains the single ready-next helper step before any wider `input_register_device()` claim.

Phase 12 flow
- `check-phase12-build-inventory.py` and `validate-phase12.py` keep the shared Phase 12 complex-driver and heavy-helper tranche aligned before replay by checking the workflow wiring, `zigux/Makefile`, `zigux/tests/phase12_build.zig`, the shared build inventory snapshot in `zigux/tests/fixtures/phase12_build_inventory.json`, the four manifests `zigux/tests/phase12_virtio_net_manifest.json`, `zigux/tests/phase12_nvme_pci_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_libbpf_manifest.json`, plus the survey notes pinned to each manifest's exact `surveyed_commit`.
- `make -C zigux phase12-validate` is the fail-fast bundle check for that shared degraded-workflow packet before the shared Zig replay runs.
- `make -C zigux phase12` keeps the current Phase 12 bundle reviewable through one shared tranche entrypoint instead of ad hoc complex-driver commands.
- the current active storage-driver survey packet stays explicit through `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, and the paired `zigux/tests/phase12_virtio_scsi_{manifest,survey}.zig` files, so the queue-layout, recovery, probe snapshot, and host-limit summary starters remain visible without overstating the still-blocked DMA-backed queue ownership, `Scsi_Host` lifecycle, or blk-mq follow-up.
