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
- `validate-phase1.py`
- `check-phase1-bench.py`
- `validate-phase1-closure.py`
- `validate-phase2.py`
- `validate-phase2-closure.py`
- `validate-phase3.py`
- `validate_phase3_selftest.py`
- `check-phase3-selftest-surface.py`
- `check-phase3-readme-tooling-inventory.py`
- `check-phase3-catalog-selftest.py`
- `validate-phase3-policy-unsafe-survey.py`
- `validate-phase3-low-level-wrapper-survey.py`
- `artifact_diff.py`
- `check-artifact-diff-contract.py`
- `validate-phase4.py`
- `check-phase4-gate-evidence.py`
- `check-phase6-shared-surface.py`
- `check-phase9-build-only-surface.py`
- `check-phase10-core-packet.py`
- `check-phase10-input-packet.py`
- `check-phase11-shared-replay-contract.py`
- `check-build-only-phase12-surface.py`
- `validate-phase13-release.py`
- `check-phase13-devres-packet.py`
- `check-phase15-review-process-handoff.py`
- `check-phase15-scripts-readme-alignment.py`
- `run-phase3-checks.py`
- `phase3_catalog.py`
- `phase3_check_lib.py`
- `generate-phase3-check-wrappers.py`
- `check-phase1-parity.py`
- `check-fixdep-diff.py`
- `check-genksyms-bridge.py`
- `check-genksyms-crc-diff.py`
- `check-kconfig-bridge.py`
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
- `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` keep that same closed host-side helper packet reviewable through the docs-root closure record, the reviewer-facing checklist, the bootstrap workflow replay, and the Linux-style replay routes instead of leaving the Phase 1 closure stack visible only through direct script and Zig commands.

Phase 2 flow
- `validate-phase2.py` checks that the bounded Phase 2 helper inventory, fixture set, workflow wiring, and docs markers stay in sync before the parity lanes run.
- `validate-phase2-closure.py` confirms the closed Phase 2 tranche still matches the workflow, the closure docs, and the Phase 2 manifests.
- `check-phase2-tests-readme-alignment.py` keeps `zigux/tests/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/Makefile`, and the Linux-style `make -C zigux phase2-validate` plus `make -C zigux phase2` replay surface aligned around the same bounded toolchain packet.
- `check-phase2-cross-selftest-alignment.py` keeps `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` aligned around the bounded three-target compile matrix.
- `check-phase2-toolchain-pin-scope.py --self-test` and `check-phase2-toolchain-pin-scope.py` keep `scripts/zigux/zig-toolchain-policy.json`, `.github/workflows/zigux-bootstrap.yml`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, and this scripts index aligned around the current x86_64-linux bootstrap host target while the cross-target compile matrix stays a separate Phase 2 surface.
- `check-fixdep-diff.py` compares the bounded `fixdep.zig` output against the committed fixture set, including `zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt`.
- `check-genksyms-bridge.py` exercises the bounded `genksyms.zig` bridge parity lane.
- `check-genksyms-crc-diff.py` checks the bounded `genksyms_crc.zig` artifact lane.
- `check-kconfig-bridge.py` covers the bounded `kconfig/conf_bridge.zig` and `kconfig/confdata_bridge.zig` bridge lanes.
- `check-phase2-cross.py` runs the bounded Phase 2 cross-target compile checks.
- `check-mk-elfconfig-diff.py` covers the bounded `mk_elfconfig.zig` artifact parity lane.

Phase 3 flow
- `validate-phase3.py` validates discovered Phase 3 slices, their required manifests, build steps, and doc markers, and can optionally audit the generated artifact-diff section and slug-sanity rules.
- `validate_phase3_selftest.py` reruns the validator-local `--self-test` packet through one shared wrapper when contributors want a focused check on the Phase 3 validator support scripts themselves; `make -C zigux phase3-validate` already invokes those underlying self-tests directly, so the shared runner stays a manual or targeted safety check instead of duplicating the default validation route.
- `check-phase3-selftest-surface.py` keeps `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase3-abi-slice.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, `scripts/zigux/validate_phase3_selftest.py`, and `make -C zigux phase3-selftest` aligned around that manual-only support-script rerun, and `make -C zigux phase3-validate` now executes the checker so this shared review packet fails closed without turning `phase3-selftest` into a duplicate default replay route.
- The live support packet inside that same validator-first route is `check-phase3-readme-tooling-inventory.py`, `check-phase3-catalog-selftest.py`, `validate-phase3-policy-unsafe-survey.py`, `validate-phase3-low-level-wrapper-survey.py`, `phase3_catalog.py`, `phase3_check_lib.py`, `generate-phase3-check-wrappers.py`, and `run-phase3-checks.py`; the generated `check-phase3-*.py` wrappers stay as compatibility entrypoints derived from the discovered slice catalog instead of a second hand-maintained survey list.
- `validate-phase3-policy-unsafe-survey.py` keeps the Phase 3 policy-and-unsafe boundary survey aligned with the landed allocator-policy, panic-policy, MMIO, narrow-unsafe, ABI-test, ABI-dump, and `zigux/Makefile` validation packet.
- `validate-phase3-low-level-wrapper-survey.py` keeps the focused low-level wrapper boundary survey aligned with the landed atomic, barrier, MMIO, focused wrapper replay, shared ABI packet, and blob-pinned survey evidence.
- `phase3_catalog.py` discovers Phase 3 slices from the docs, dump entrypoints, and fixture manifests instead of maintaining one giant hard-coded inventory, and now carries per-slice metadata such as display descriptions, build-step overrides, and the current `PHASE3_INTEROP_GATE` mode recorded in each slice doc.
- `phase3_catalog.py --self-test` exercises isolated slug discovery, manifest selection, and interop-gate classification across docs, dumps, and fixture candidates.
- `phase3_catalog.py --legacy-wrapper-docs` lists the discovered slice docs that still point at legacy `check-phase3-*.py` compatibility wrappers.
- `phase3_catalog.py --rewrite-shared-runner-docs` rewrites those legacy per-slice doc commands to the shared `run-phase3-checks.py --slug ...` form so wrapper-reference cleanup is scripted instead of manual.
- `phase3_catalog.py --legacy-wrapper-references` lists remaining discovered Phase 3 wrapper mentions in non-slice documentation, which keeps stray policy-doc references auditable now that the manifest cleanup is complete.
- `phase3_catalog.py --rewrite-legacy-wrapper-references` rewrites those non-slice documentation references to the shared runner form, leaving `artifact-diff.md` and similar policy docs on the same scripted cleanup path as the slice records.
- `phase3_catalog.py --rewrite-artifact-diff-phase3-section` regenerates the detailed `Documentation/zigux/artifact-diff.md` Phase 3 policy block from the discovered slice catalog.
- `phase3_catalog.py --audit-doc-sync` reports stale non-slice wrapper references plus a stale `artifact-diff.md` Phase 3 block, and bootstrap now runs it so documentation drift fails fast.
- `phase3_catalog.py --suggest-slug-renames` turns the slug sanity audit into concrete cleanup candidates by pairing each repetitively overgrown slug with the longest clean prefix already present in the catalog, while skipping slugs whose only issue is crossing the token-count threshold and suppressing prefix matches whose normalized fixture manifest or `expected.json` schema does not actually line up with the shorter slice.
- `phase3_catalog.py --suggest-slug-rename-paths` lists the core slice files and directories that each safe rename would retire.
- `phase3_catalog.py --suggest-slug-merge-prep` expands those safe rename candidates into a cleanup checklist by listing the retireable long-slug artifacts and the extra docs, workflow, script, or `zigux/tests/build.zig` lines that still mention the long slug elsewhere in the tree; `--suggest-slug-merge-plans` remains accepted as a compatibility alias.
- `phase3_check_lib.py --self-test` covers the shared wrapper-template, slug, and parity-runner helper logic that sits under both the generated wrappers and `run-phase3-checks.py`.
- `generate-phase3-check-wrappers.py --check` fails if any discovered `check-phase3-*.py` wrapper drifts from the shared template or if stale wrappers remain beside the current catalog.
- `run-phase3-checks.py --self-test` exercises isolated Phase 3 slug selection and fail-fast runner coverage without launching the live parity builds.
- `phase3_check_lib.py` holds the shared Phase 3 parity execution logic used by every wrapper and the shared runner.

Phase 4 flow
- `validate-phase4.py` checks that the bounded Phase 4 differential gates, the shared `scripts/zigux/artifact_diff.py` contract replay owned by `scripts/zigux/check-artifact-diff-contract.py`, the canonical `zigux/tests/atomic64_diff.zig` wrapper, the manifest-backed `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` handoff survey, the helper-backed `zigux/tests/phase4_bitmap_live_helper_replay.zig` replay, the dedicated `scripts/zigux/check-phase4-gate-evidence.py` exact-readback gate, their shared `zigux/tests/phase4_build.zig` entrypoint, and the directly coupled documentation and workflow markers stay aligned.
- The shared Phase 4 validator-first packet reruns `python3 scripts/zigux/check-artifact-diff-contract.py` before the live `zigux/tests/atomic64_diff.zig` wrapper, that reviewability gate, `zigux/tests/bitmap_diff.zig` rollback-readiness gate, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` helper-backed bitmap rollback replay, while the wrapper keeps `zigux/tests/runtime_atomic64_diff.zig` as the single shared runtime-backed replay body that Phase 9 still imports directly.
- `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/phase4-gate-evidence.md`, and `Documentation/zigux/phase4-validation-matrix.md` keep the host-side helper contract, current rollback owners, exact-readback packet, intentionally unapproved perf-threshold posture, and lab or CI replay matrix explicit for the shipped Phase 4 gates.
- `zigux/Makefile` keeps `make -C zigux phase4-validate`, `make -C zigux phase4-test`, `make -C zigux phase4-runtime-atomic64-diff`, `make -C zigux phase4-runtime-atomic64-diff-survey`, `make -C zigux phase4-bitmap-diff`, `make -C zigux phase4-bitmap-live-helper-replay`, and `make -C zigux phase4` aligned with that same validator-first packet instead of leaving the Linux-style replay routes implicit in the shared build file alone.

Phase 5 flow
- the current shared Phase 5 review surface on `master` is `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, the four survey notes (`Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/phase5-kobject-sample-survey.md`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, and `Documentation/zigux/phase5-trace-events-sample-survey.md`), the four sample modules under `samples/zigux/`, the four paired manifests and survey tests under `zigux/tests/`, `zigux/tests/phase5_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.
- `zig build test --build-file zigux/tests/phase5_build.zig --summary all` and `make -C zigux phase5` are the shipped shared replay routes for the four approved Phase 5 reference samples, and the bootstrap workflow reruns that same bounded packet directly instead of routing Phase 5 through a dedicated scripts-side validator.
- there is no shared `validate-phase5.py`, no shipped `check-phase5-*.py` packet, and no `phase5-validate` target on `master`; future follow-through should stay inside contributor guidance or exact sample-backed replay repairs that keep the four reference samples reviewable without implying runtime-substrate closure or widening into the separate Phase 9 `samples/zigux/runtime_*` family.

Phase 6 flow
- the current shared Phase 6 review surface on `master` is the four slice notes (`Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, and `Documentation/zigux/phase6-hexdump-slice.md`) plus `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.
- `make -C zigux phase6-validate` keeps the shared Phase 6 surface checker wired through the Zigux convenience target.
- `zig build test --build-file zigux/tests/phase6_build.zig` is the bundled helper replay for the current `base64`, `bsearch`, `checksum`, and `hexdump` packet.
- `make -C zigux phase6` keeps that same shared-surface check plus bundled helper replay wired through the Zigux convenience target.
- there is no separate shared `validate-phase6.py`, external portability checker packet beyond `check-phase6-shared-surface.py`, or aggregated `phase6-perf` target on `master`; the shipped dedicated perf replays are `make -C zigux phase6-checksum-perf` and `make -C zigux phase6-hexdump-perf`, which keep the checksum slowdown ceiling and the formatter-sensitive hexdump fixture packet wired into Linux-style entrypoints without overstating perf coverage for the rest of the Phase 6 helper packet.

Phase 7 flow
- the current shared Phase 7 review surface on `master` is `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase7-string-helpers-slice.md`, `Documentation/zigux/phase7-cmdline-slice.md`, `Documentation/zigux/phase7-argv-split-slice.md`, `Documentation/zigux/phase7-rbtree-slice.md`, `samples/zigux/README.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-argv-split-packet.py`, `scripts/zigux/check-phase7-rbtree-parity.py`, `zigux/tests/phase7_build.zig`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_sample_boundary.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.
- `make -C zigux phase7-validate` keeps the shared Phase 7 validator plus the dedicated make-wrapper, argv_split packet, and rbtree parity checkers wired through the Linux-style validation entrypoint.
- `zig build test --build-file zigux/tests/phase7_build.zig --summary all` and `make -C zigux phase7` rerun that same bounded `string_helpers`, `cmdline`, `argv_split`, and `rbtree` helper packet together with the dedicated cmdline survey gate, the dedicated argv_split survey gate, the dedicated no-string-sample boundary replay, and the dedicated rbtree survey gate.
- there is no separate shared `check-phase7-build-inventory.py`, `phase7_build_inventory.json`, or broader packet-checker stack on `master`; future follow-through should name only the shipped docs-root, tests-root, validator, build, and make surfaces until those broader checkers actually land.

Phase 8 flow
- the current shared Phase 8 review surface on `master` is `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase8-exec-cmd-slice.md`, `Documentation/zigux/phase8-help-slice.md`, `Documentation/zigux/phase8-kallsyms-slice.md`, `Documentation/zigux/phase8-libbpf-cpu-mask-slice.md`, `Documentation/zigux/phase8-bpf-type-names-slice.md`, `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, `scripts/zigux/validate-phase8.py`, `scripts/zigux/check-phase8-exec-cmd-packet.py`, `zigux/tests/phase8_build.zig`, `zigux/tests/phase8_exec_cmd.zig`, `zigux/tests/phase8_exec_cmd_only_build.zig`, `zigux/tests/phase8_help.zig`, `zigux/tests/phase8_help_only_build.zig`, `zigux/tests/phase8_help_kallsyms_only_build.zig`, `zigux/tests/phase8_kallsyms.zig`, `zigux/tests/phase8_kallsyms_only_build.zig`, `zigux/tests/phase8_cpu_mask.zig`, `zigux/tests/phase8_logging.zig`, `zigux/tests/phase8_pin_path.zig`, `zigux/tests/phase8_bpf_type_names.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, `zigux/tests/phase8_libbpf_segments.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.
- `make -C zigux phase8-validate` keeps `validate-phase8.py` plus the focused `check-phase8-exec-cmd-packet.py` checker wired through the Linux-style validation entrypoint before the tooling replays run.
- `make -C zigux phase8-exec-cmd-test`, `make -C zigux phase8-help-test`, `make -C zigux phase8-kallsyms-test`, `make -C zigux phase8-libbpf-segments-test`, `make -C zigux phase8-perf-buffer-poll-test`, `zig build test --build-file zigux/tests/phase8_build.zig --summary all`, and `make -C zigux phase8` rerun that same bounded repo-hosted tooling packet through both the focused shard replays and the shared build-backed route.
- future follow-through should stay inside the next smallest validator-truthfulness repair, build-backed tooling slice, or reviewability note that keeps that validator-first packet aligned instead of widening into unrelated helper behavior or deferred libbpf object-model work.

Phase 9 flow
- the current shared Phase 9 review surface on `master` is `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, the four runtime survey-and-module note pairs (`Documentation/zigux/phase9-runtime-atomic64-module-slice.md`, `Documentation/zigux/phase9-runtime-atomic64-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, and `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`, and `Documentation/zigux/phase9-runtime-kretprobe-survey.md`, `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`, and `Documentation/zigux/phase9-runtime-trace-events-survey.md`), `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `scripts/zigux/check-phase9-build-only-surface.py`, `zigux/tests/phase9_build.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the four `samples/zigux/runtime_*_loader.zig` scaffolds.
- `zig build test --build-file zigux/tests/phase9_build.zig` and `make -C zigux phase9` rerun that same bounded runtime atomic64, bitmap, trace-events, and kretprobe pilot bundle together with the shared runtime-loader facade, loader contract, allocator/init-flow replay, and Linux-style replay route.
- there is no dedicated shared `validate-phase9.py`, `check-phase9-validation-flow.py`, `check-phase9-runtime-loader-commit-alignment.py`, or `phase9-validate` target on `master`; future runtime-pilot follow-through should stay inside the next smallest shared runtime-loader substrate, validation, or review-surface step that keeps those four loader handoffs plus the shared `zigux/kernel/runtime_loader.zig` facade and `zigux/kernel/runtime_loader_contract.zig` allocator/init-flow contract reviewable without widening into a larger runtime-module implementation.

Phase 10 flow
- the current shared Phase 10 review surface on `master` is `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-core-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `zigux/Makefile`, and `make -C zigux phase10` still agree on the same shared virtio core, virtio ring, virtio input, and virtio mmio build-and-make packet without implying a dedicated `validate-phase10.py`, `check-phase10-harness-coverage.py`, or `phase10-validate` surface that does not exist on `master`?
  * if the change touches the shared Phase 11 simple-driver packet, do `Documentation/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/Makefile`, `zig build test --build-file zigux/tests/phase11_build.zig`, and `make -C zigux phase11` still agree on the same shared-versus-dedicated replay split, the four driver-local validation matrices, the bounded `hvc_cleanup()` teardown handoff, and the dedicated archival `hvc_console` survey without implying a removed `validate-phase11.py`, missing build-inventory fixture, or broader checker-script packet that does not exist on `master`?
- if the change touches the shared Phase 12 complex-driver packet, do `Documentation/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `zigux/tests/phase12_build.zig`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_survey.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, `zigux/tests/phase12_nvme_pci_manifest.json`, `zigux/tests/phase12_virtio_net_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_libbpf_manifest.json`, `tools/lib/bpf/zigux_segments/manifest.json`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and `make -C zigux phase12` still agree on the same shipped nvme, virtio_net, virtio_scsi, and libbpf survey packet plus the active release-order note without implying removed `validate-phase12.py`, `check-phase12-*.py`, raw-coverage, or focused-libbpf-only replay surfaces that are not on `master`?
  * if the change touches the shared Phase 14 smoke packet, do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/freeze-map.md`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_workqueue_bridge_manifest.json`, `zigux/tests/phase14_skbuff_bridge_manifest.json`, `zigux/tests/phase14_ring_buffer_manifest.json`, `zigux/tests/phase14_rcu_tree_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `make -C zigux phase14-smoke`, `make -C zigux phase14-test`, and `make -C zigux phase14` still agree on the same study-only stay-in-C posture without implying an active deep-core port claim?
  * if the change touches the shared Phase 13 release packet, do `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/validate-phase13-release.py`, `zigux/Makefile`, `make -C zigux phase13-validate`, and `make -C zigux phase13` still agree on the same validator-first six-test shared-helper release packet, including the four manifest-backed anchors plus the bounded `devres` and `libfs` reviewability replays, while keeping `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig` explicit as shipped adjacent release-surface evidence rather than implying they are missing from the broader Phase 13 packet or that they add extra shared replay steps on `master`?
  * if the change touches the shared Phase 15 governance packet, do `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/tests/phase15_build.zig`, and `make -C zigux phase15` still agree on the same parked governance packet and no-approval-yet posture?
## ABI and Runtime

  * are bindings and ABI assumptions centralized?
  * does the change avoid hidden runtime services, implicit allocation, or unclear panic behavior?
  * if unsafe code exists, is it narrow, visible, and review-owned?
## Product Discipline
  * does the patch make Zigux more buildable, more testable, or more reviewable?
  * if it came from ZAR research, is the transfer rationale explicit?
  * if the target stays in C, does the change record that ongoing policy honestly instead of implying a premature port commitment?
  * does the change strengthen the product repo instead of just extending experimental scope?
  * if the change is a Phase 5 sample, does it separate reviewable idiom guidance from later runtime-substrate claims such as procfs, user-copy, or module registration parity?
  * if the change is a landed Phase 5 sample, does it update the directly coupled survey note or manifest-backed contributor prompts when the sample contract changes?
## Footer
