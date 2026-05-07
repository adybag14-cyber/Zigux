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
- `validate-phase3.py`
- `validate_phase3_selftest.py`
- `check-phase3-selftest-surface.py`
- `check-phase3-readme-tooling-inventory.py`
- `check-phase3-abi-dump-gate.py`
- `check-phase3-catalog-selftest.py`
- `validate-phase3-policy-unsafe-survey.py`
- `validate-phase3-low-level-wrapper-survey.py`
- `validate-phase3-export-uapi-survey.py`
- `validate-phase3-abi-bindings-syntax.py`
- `artifact_diff.py`
- `check-artifact-diff-contract.py`
- `validate-phase4.py`
- `check-phase4-gate-evidence.py`
- `check-phase6-shared-surface.py`
- `validate-phase7.py`
- `check-phase7-make-wrapper.py`
- `check-phase7-argv-split-packet.py`
- `check-phase7-rbtree-parity.py`
- `check-phase7-build-wiring.py`
- `validate-phase8.py`
- `check-phase8-exec-cmd-packet.py`
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
- `check-phase2-toolchain-pin-scope.py --self-test` and `check-phase2-toolchain-pin-scope.py` keep `scripts/zigux/zig-toolchain-policy.json`, `.github/workflows/zigux-bootstrap.yml`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, and this scripts index aligned around the current x86_64-linux bootstrap host target while the cross-target compile matrix stays a separate Phase 2 surface.
- `check-fixdep-diff.py` compares the bounded `fixdep.zig` output against the committed fixture set, including `zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt`.
- `check-genksyms-bridge.py` exercises the bounded `genksyms.zig` bridge parity lane.
- `check-genksyms-crc-diff.py` checks the bounded `genksyms_crc.zig` artifact lane.
- `check-phase2-kconfig-selftest-alignment.py --self-test` and `check-phase2-kconfig-selftest-alignment.py` keep `check-kconfig-bridge.py`, `scripts/zigux/validate-phase2.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned around the shipped kconfig self-test hooks before the bridge and Zig replays run, so the shared Phase 2 validator, the Linux-style `phase2-kconfig` route, and the workflow-backed replay surface stay on the same bounded packet.
- `check-kconfig-bridge.py` covers the bounded `kconfig/conf_bridge.zig` and `kconfig/confdata_bridge.zig` bridge lanes.
- `check-phase2-cross.py` runs the bounded Phase 2 cross-target compile checks.
- `check-mk-elfconfig-diff.py` covers the bounded `mk_elfconfig.zig` artifact parity lane.

Phase 3 flow
- `validate-phase3.py` validates discovered Phase 3 slices, their required manifests, build steps, and doc markers, and can optionally audit the generated artifact-diff section and slug-sanity rules.
- `validate_phase3_selftest.py` reruns the validator-local `--self-test` packet through one shared wrapper when contributors want a focused check on the Phase 3 validator support scripts themselves; `make -C zigux phase3-validate` already invokes those underlying self-tests directly, so the shared runner stays a manual or targeted safety check instead of duplicating the default validation route.
- `check-phase3-selftest-surface.py` keeps `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase3-abi-slice.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, `scripts/zigux/validate_phase3_selftest.py`, and `make -C zigux phase3-selftest` aligned around that manual-only support-script rerun, and `make -C zigux phase3-validate` now executes the checker so this shared review packet fails closed without turning `phase3-selftest` into a duplicate default replay route.
- The live support packet inside that same validator-first route is `check-phase3-readme-tooling-inventory.py`, `check-phase3-catalog-selftest.py`, `check-phase3-abi-dump-gate.py`, `validate-phase3-policy-unsafe-survey.py`, `validate-phase3-low-level-wrapper-survey.py`, `validate-phase3-export-uapi-survey.py`, `validate-phase3-abi-bindings-syntax.py`, `phase3_catalog.py`, `phase3_check_lib.py`, `generate-phase3-check-wrappers.py`, and `run-phase3-checks.py`; the generated `check-phase3-*.py` wrappers stay as compatibility entrypoints derived from the discovered slice catalog instead of a second hand-maintained survey list.
- `validate-phase3-policy-unsafe-survey.py` keeps the Phase 3 policy-and-unsafe boundary survey aligned with the landed allocator-policy, panic-policy, MMIO, narrow-unsafe, ABI-test, ABI-dump, and `zigux/Makefile` validation packet.
- `validate-phase3-low-level-wrapper-survey.py` keeps the focused low-level wrapper boundary survey aligned with the landed atomic, barrier, MMIO, focused wrapper replay, shared ABI packet, and blob-pinned survey evidence.
- `validate-phase3-export-uapi-survey.py` keeps the exported shim and UAPI boundary packet aligned around `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `include/linux/zigux.h`, `include/zigux/abi.h`, `zigux/kernel/export_shim.zig`, `zigux/uapi/version.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, and the workflow hooks that rerun that same survey surface.
- `validate-phase3-abi-bindings-syntax.py` keeps the authoritative Phase 3 ABI header, the curated ABI and `dev_t` bindings, the Phase 3 ABI manifest, and the slice note free of fused top-level syntax drift while the dedicated export/UAPI survey stays an adjacent boundary packet.
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
- `zig build test --build-file zigux/tests/phase5_build.zig --summary all`, `make -C zigux phase5-test`, and `make -C zigux phase5` are the shipped shared replay routes for the four approved Phase 5 reference samples, and the bootstrap workflow reruns that same bounded packet directly instead of routing Phase 5 through a dedicated scripts-side validator.
- there is no shared `validate-phase5.py`, no shipped `check-phase5-*.py` packet, and no `phase5-validate` target on `master`; future follow-through should stay inside contributor guidance or exact sample-backed replay repairs that keep the four reference samples reviewable without implying runtime-substrate closure or widening into the separate Phase 9 `samples/zigux/runtime_*` family.

Phase 6 flow
- the current shared Phase 6 review surface on `master` is the four slice notes (`Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, and `Documentation/zigux/phase6-hexdump-slice.md`) plus `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.
- `make -C zigux phase6-validate` keeps the shared Phase 6 surface checker wired through the Zigux convenience target.
- `zig build test --build-file zigux/tests/phase6_build.zig` is the bundled helper replay for the current `base64`, `bsearch`, `checksum`, and `hexdump` packet.
- `make -C zigux phase6` keeps that same shared-surface check plus bundled helper replay wired through the Zigux convenience target.
- there is no separate shared `validate-phase6.py` or broader external portability checker packet beyond `check-phase6-shared-surface.py` on `master`; the shipped dedicated perf replays are `make -C zigux phase6-base64-perf`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf`, while `make -C zigux phase6-perf` remains the narrow aggregate route for the checksum and hexdump perf packet rather than a bundle-wide Phase 6 perf closure.

Phase 7 flow
- the current shared Phase 7 review surface on `master` is `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase7-string-helpers-slice.md`, `Documentation/zigux/phase7-cmdline-slice.md`, `Documentation/zigux/phase7-argv-split-slice.md`, `Documentation/zigux/phase7-rbtree-slice.md`, `samples/zigux/README.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-argv-split-packet.py`, `scripts/zigux/check-phase7-rbtree-parity.py`, `scripts/zigux/check-phase7-build-wiring.py`, `zigux/tests/phase7_build.zig`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_survey.zig`, `zigux/tests/phase7_string_helpers_sample_boundary.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, `zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.
- `make -C zigux phase7-validate` keeps the shared Phase 7 validator plus the dedicated make-wrapper, argv_split packet, rbtree parity, and build-wiring checkers wired through the Linux-style validation entrypoint.
- `zig build test --build-file zigux/tests/phase7_build.zig --summary all` and `make -C zigux phase7` rerun that same bounded `string_helpers`, `cmdline`, `argv_split`, and `rbtree` helper packet together with the dedicated string-helper survey gate, the dedicated cmdline survey gate, the dedicated argvSplit survey gate, the dedicated no-string-sample boundary replay, and the dedicated rbtree survey gate.
- there is no separate shared `check-phase7-build-inventory.py`, `phase7_build_inventory.json`, or broader packet-checker stack on `master`; future follow-through should name only the shipped docs-root, tests-root, validator, build, and make surfaces until those broader checkers actually land.

Phase 8 flow
- the current shared Phase 8 review surface on `master` is `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase8-exec-cmd-slice.md`, `Documentation/zigux/phase8-help-slice.md`, `Documentation/zigux/phase8-kallsyms-slice.md`, `Documentation/zigux/phase8-libbpf-cpu-mask-slice.md`, `Documentation/zigux/phase8-bpf-type-names-slice.md`, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `scripts/zigux/validate-phase8.py`, `scripts/zigux/check-phase8-exec-cmd-packet.py`, `zigux/tests/phase8_build.zig`, `zigux/tests/phase8_exec_cmd.zig`, `zigux/tests/phase8_exec_cmd_only_build.zig`, `zigux/tests/phase8_help.zig`, `zigux/tests/phase8_help_only_build.zig`, `zigux/tests/phase8_kallsyms.zig`, `zigux/tests/phase8_kallsyms_only_build.zig`, `zigux/tests/phase8_cpu_mask.zig`, `zigux/tests/phase8_logging.zig`, `zigux/tests/phase8_pin_path.zig`, `zigux/tests/phase8_bpf_type_names.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, `zigux/tests/phase8_libbpf_segments.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.
- `make -C zigux phase8-validate` keeps `validate-phase8.py` plus the focused `check-phase8-exec-cmd-packet.py` checker wired through the Linux-style validation entrypoint before the tooling replays run.
- `make -C zigux phase8-exec-cmd-test`, `make -C zigux phase8-help-test`, `make -C zigux phase8-kallsyms-test`, `make -C zigux phase8-file-path-handle-bridge-test`, `make -C zigux phase8-libbpf-segments-test`, `make -C zigux phase8-perf-buffer-poll-test`, `zig build test --build-file zigux/tests/phase8_build.zig --summary all`, and `make -C zigux phase8` rerun that same bounded repo-hosted tooling packet through both the focused shard replays and the shared build-backed route.
- future follow-through should stay inside the next smallest validator-truthfulness repair, build-backed tooling slice, or reviewability note that keeps that validator-first packet aligned instead of widening into unrelated helper behavior or deferred libbpf object-model work.

Phase 9 flow
- the current shared Phase 9 review surface on `master` is `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, the four runtime survey-and-module note pairs (`Documentation/zigux/phase9-runtime-atomic64-module-slice.md`, `Documentation/zigux/phase9-runtime-atomic64-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, and `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`, and `Documentation/zigux/phase9-runtime-kretprobe-survey.md`, `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`, and `Documentation/zigux/phase9-runtime-trace-events-survey.md`), `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `scripts/zigux/check-phase9-build-only-surface.py`, `zigux/tests/phase9_build.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the four `samples/zigux/runtime_*_loader.zig` scaffolds.
- `zig build test --build-file zigux/tests/phase9_build.zig` and `make -C zigux phase9` rerun that same bounded runtime atomic64, bitmap, trace-events, and kretprobe pilot bundle together with the shared runtime-loader facade, loader contract, allocator/init-flow replay, and Linux-style replay route; `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` remains the shared owner map for how that scripts-root summary stays split between the loader lane and the four pilot-family packets.
- there is no dedicated shared `validate-phase9.py`, `check-phase9-validation-flow.py`, `check-phase9-runtime-loader-commit-alignment.py`, or `phase9-validate` target on `master`; future runtime-pilot follow-through should stay inside the next smallest shared runtime-loader substrate, validation, or review-surface step that keeps those four loader handoffs plus the shared `zigux/kernel/runtime_loader.zig` facade and `zigux/kernel/runtime_loader_contract.zig` allocator/init-flow contract reviewable without widening into a larger runtime-module implementation.

Phase 10 flow
- the current shared Phase 10 review surface on `master` is `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-core-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase10-core-packet.py`, `scripts/zigux/check-phase10-ring-packet.py`, `scripts/zigux/check-phase10-input-packet.py`, `scripts/zigux/check-phase10-mmio-packet.py`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_manifest.json`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `zig build test --build-file zigux/tests/phase10_build.zig`, `make -C zigux phase10-test`, and `make -C zigux phase10` now keep the current virtio core, bounded reset replay, core survey, driver-id review path, virtio ring, virtio input, focused status-drain replay, and virtio mmio packet reviewable through one shared manifest-backed, checker-backed build-and-make route without implying a dedicated `validate-phase10.py`, a broader Phase 10 harness-coverage checker beyond the shipped core, ring, input, and MMIO packet checkers, or a `phase10-validate` surface that does not exist on `master`.

Phase 11 flow
- the current shared Phase 11 review surface on `master` is `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.
- `python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test` and `check-phase11-shared-replay-contract.py` keep the docs-root summary, scripts-root, replay-contract note, Makefile, and workflow contract fail-closed while preserving the dedicated archival survey split, while `python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test` and `python3 scripts/zigux/check-phase11-header-boundary-packet.py` keep the focused shared header-boundary note, manifest-backed survey replay, and bounded exported `hvc` surface explicit without implying a broader validator stack.
- `zig build test --build-file zigux/tests/phase11_build.zig --summary all` and `make -C zigux phase11` rerun that same simple-driver starter packet, while `zigux/tests/phase11_hvc_cleanup.zig` keeps the bounded `hvc_cleanup()` tty-port release handoff and teardown-gating replay explicit, `zigux/tests/phase11_hvc_console_survey.zig` keeps the dedicated archival HVC replay separate, and `zigux/tests/phase11_uapi_header_parity_survey.zig` keeps the focused shared header-parity survey packet reviewable beside the shared route.
- there is no dedicated shared `validate-phase11.py`, `zigux/tests/fixtures/phase11_build_inventory.json`, or `phase11-validate` target on `master`; the shipped Phase 11 checker set stays intentionally limited to `check-phase11-shared-replay-contract.py` plus the focused `check-phase11-header-boundary-packet.py` route rather than a broader validator packet.

Phase 12 flow
- the current shared Phase 12 review surface on `master` is `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `zigux/tests/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_build.zig`, `zigux/Makefile`, the bounded Phase 12 nvme, virtio_net, virtio_scsi, and libbpf test modules wired through that build, the committed Phase 12 manifests under `zigux/tests/`, and `tools/lib/bpf/zigux_segments/manifest.json`.
- `check-build-only-phase12-surface.py --self-test` and `check-build-only-phase12-surface.py` keep the docs-root, scripts-root, tests-root, and Makefile build-only contract fail-closed while `.github/workflows/zigux-bootstrap.yml` reruns that same self-test plus the live checker in CI.
- `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` rerun that same bounded survey-backed tranche, with the shared smoke shard staying explicit beside the full replay route.
- `zigux/tests/phase12_virtio_net_syntax_lab.zig` remains the dedicated direct `virtio_net` smoke shard inside that shared packet, so the scripts-root summary keeps the driver-local syntax-lab gate visible beside `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_survey.zig`, `zigux/tests/phase12_build.zig`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12-smoke` instead of flattening the active `virtio_net` lane back into a survey-only review surface.
- there is no dedicated shared `validate-phase12.py`, `check-phase12-*.py`, or `phase12-validate` target on `master`; future Phase 12 reviewability claims should name only shipped survey, build, and make surfaces until new validator files actually land.
- keep the current public fallback split explicit here too: only `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are commit-pinned artifacts, while `virtio_net` and `libbpf` remain shared-tree-only anchors rather than implied fallback maps.

Phase 13 flow
- the current shared Phase 13 release surface on `master` is `Documentation/zigux/README.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/review-checklist.md`, the four Phase 13 slice and survey note pairs plus `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/tests/README.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig`.
- `validate-phase13-release.py` keeps that shared helper release packet aligned before the shared replay runs, while `check-phase13-devres-packet.py` and `check-phase13-landlock-ruleset-packet.py` keep the stricter helper-first `devres` and Landlock ruleset boundary contracts visible inside the same validator-first route.
- `make -C zigux phase13-validate` keeps that same release packet wired through the Linux-style validation entrypoint.
- `zig build test --build-file zigux/tests/phase13_build.zig` and `make -C zigux phase13` rerun the seven-test shared helper replay for `phase13_libfs.zig`, `phase13_devres.zig`, `phase13_devres_reviewability.zig`, `phase13_devres_dma_coherent.zig`, `phase13_landlock_ruleset.zig`, `phase13_landlock_syscalls.zig`, and `phase13_libfs_reviewability.zig`, while `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, the release-notes, roadmap-traceability, notifier survey, notifier reviewability replay, and notifier ABI-helper surfaces stay adjacent review evidence instead of adding extra shared replay steps on `master`.

Phase 14 flow
- the current shared Phase 14 study-only smoke surface on `master` is `Documentation/zigux/README.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-core-boundary-traceability.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase14.py`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `zigux/tests/README.md`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge_manifest.json`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_skbuff_bridge_manifest.json`, `zigux/tests/phase14_ring_buffer_survey.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`.
- `make -C zigux phase14-validate` keeps the shared smoke validator plus the docs-root smoke-summary checker, the rollback-threshold sequencing checker, and the release-boundary exact-counts checker wired through the Linux-style validation entrypoint before the focused smoke shard and full replay routes run.
- `make -C zigux phase14-smoke` and `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all` rerun the focused end-to-end smoke shard while keeping the release-boundary note and freeze-map posture explicit.
- `make -C zigux phase14-test`, `zig build test --build-file zigux/tests/phase14_build.zig --summary all`, and `make -C zigux phase14` rerun that same bounded workqueue-bridge, skbuff-bridge, ring-buffer-survey, rcu-tree-survey, and smoke packet without implying an active deep-core port claim.
- the shipped shared Phase 14 checker set on `master` is `check-phase14-docs-root-smoke-summary.py`, `check-phase14-rollback-threshold-sequencing.py`, and `check-phase14-release-boundary-exact-counts.py`; future follow-through should stay inside the next smallest smoke-survey, rollback-threshold, release-boundary, docs-root, tests-root, or scripts-root truthfulness repair now that all three checker routes are part of the shared packet.

Phase 15 flow
- the current shared Phase 15 governance surface on `master` is `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/tests/phase15_handoff_next_steps.zig`, `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, and `zigux/tests/phase15_readiness_gate.zig`.
- `check-phase15-scripts-readme-alignment.py` keeps `scripts/zigux/README.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, and `zigux/tests/phase15_build.zig` aligned around the parked governance packet's scripts-root validator-first route and no-approval-yet posture.
- `check-phase15-review-process-handoff.py` keeps the dedicated review-process note and its manifest-backed handoff evidence aligned around the self-reference, product-boundary, and parked-route markers that keep the Architecture Council packet reviewable without inventing a broader governance surface.
- `zig build test --build-file zigux/tests/phase15_build.zig` and `make -C zigux phase15` rerun the parked freeze-map governance, parity-scorecard, Architecture Council review-process, handoff-next-steps, dedicated indefinite-C policy, lane-owner alignment, and readiness-gate packet without implying any new approval claim for a freeze-map anchor.
- the current bounded Phase 15 decision is still to leave the lane parked unless a named reopen trigger fires or the deep-core blocker posture changes enough to justify another Architecture Council slice.

Windows note
- a Linux-scale checkout on NTFS must use a case-sensitive directory or a Linux filesystem
- otherwise case-colliding Linux paths will create false working-tree dirt on Windows
