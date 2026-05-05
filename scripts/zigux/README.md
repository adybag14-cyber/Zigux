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
- `validate-phase3-policy-unsafe-survey.py`
- `validate-phase3-low-level-wrapper-survey.py`
- `validate-phase4.py`
- `run-phase3-checks.py`
- `phase3_catalog.py`
- `phase3_check_lib.py`
- `generate-phase3-check-wrappers.py`
- `check-phase1-parity.py`
- `check-fixdep-diff.py`
- `check-genksyms-bridge.py`
- `check-genksyms-crc-diff.py`
- `check-kconfig-bridge.py`
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

Phase 2 flow
- `validate-phase2.py` checks that the bounded Phase 2 helper inventory, fixture set, workflow wiring, and docs markers stay in sync before the parity lanes run.
- `validate-phase2-closure.py` confirms the closed Phase 2 tranche still matches the workflow, the closure docs, and the Phase 2 manifests.
- `check-phase2-tests-readme-alignment.py` keeps `zigux/tests/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/Makefile`, and the Linux-style `make -C zigux phase2-validate` plus `make -C zigux phase2` replay surface aligned around the same bounded toolchain packet.
- `check-fixdep-diff.py` compares the bounded `fixdep.zig` output against the committed fixture set, including `zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt`.
- `check-genksyms-bridge.py` exercises the bounded `genksyms.zig` bridge parity lane.
- `check-genksyms-crc-diff.py` checks the bounded `genksyms_crc.zig` artifact lane.
- `check-kconfig-bridge.py` covers the bounded `kconfig/conf_bridge.zig` and `kconfig/confdata_bridge.zig` bridge lanes.
- `check-phase2-cross.py` runs the bounded Phase 2 cross-target compile checks.
- `check-mk-elfconfig-diff.py` covers the bounded `mk_elfconfig.zig` artifact parity lane.

Phase 3 flow
- `validate-phase3.py` validates discovered Phase 3 slices, their required manifests, build steps, and doc markers, and can optionally audit the generated artifact-diff section and slug-sanity rules.
- The live support packet inside that same validator-first route is `validate-phase3-policy-unsafe-survey.py`, `validate-phase3-low-level-wrapper-survey.py`, `phase3_catalog.py`, `phase3_check_lib.py`, `generate-phase3-check-wrappers.py`, and `run-phase3-checks.py`; the generated `check-phase3-*.py` wrappers stay as compatibility entrypoints derived from the discovered slice catalog instead of a second hand-maintained survey list.
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
- `validate-phase4.py` checks that the bounded Phase 4 differential gates, the canonical `zigux/tests/atomic64_diff.zig` wrapper, their shared `zigux/tests/phase4_build.zig` entrypoint, and the directly coupled documentation and workflow markers stay aligned.
- `zigux/tests/phase4_build.zig` runs the live `zigux/tests/atomic64_diff.zig` wrapper, `zigux/tests/bitmap_diff.zig` rollback-readiness gate, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` helper-backed bitmap rollback replay together, while the wrapper keeps `zigux/tests/runtime_atomic64_diff.zig` as the single shared runtime-backed replay body that Phase 9 still imports directly.
- `Documentation/zigux/phase4-validation-matrix.md` keeps the current rollback owners, threshold posture, and lab or CI replay matrix explicit for the shipped Phase 4 gates.

Phase 6 flow
- the current shared Phase 6 review surface on `master` is the four slice notes (`Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, and `Documentation/zigux/phase6-hexdump-slice.md`) plus `Documentation/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase6_build.zig`, and `zigux/Makefile`.
- `zig build test --build-file zigux/tests/phase6_build.zig` is the bundled helper replay for the current `base64`, `bsearch`, `checksum`, and `hexdump` packet.
- `make -C zigux phase6` keeps that same bundled helper replay wired through the Zigux convenience target.
- there is no separate shared `validate-phase6.py`, external portability checker packet, or `phase6-perf` make target on `master`; if those gates land later, document them here only after the files and targets ship.

Phase 9 flow
- the current shared Phase 9 review surface on `master` is `Documentation/zigux/README.md`, the four runtime survey-and-module notes (`Documentation/zigux/phase9-runtime-atomic64-module-slice.md`, `Documentation/zigux/phase9-runtime-atomic64-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, and `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`, and `Documentation/zigux/phase9-runtime-kretprobe-survey.md`, `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`, and `Documentation/zigux/phase9-runtime-trace-events-survey.md`), `zigux/tests/phase9_build.zig`, `zigux/Makefile`, the four `samples/zigux/runtime_*_loader.zig` scaffolds, and `zigux/kernel/runtime_loader.zig`.
- `make -C zigux phase9` keeps the current runtime atomic64, bitmap, trace-events, and kretprobe pilot bundle reviewable through the shared Phase 9 lane instead of widening into ad hoc per-slice checks.
- there is no dedicated shared `validate-phase9.py` on `master`; new runtime-pilot follow-through should stay inside the next smallest shared runtime-loader substrate or validation step that keeps those four loader handoffs reviewable without widening into a larger runtime-module implementation.

Phase 13 flow
- the current shared Phase 13 release surface on `master` is `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/review-checklist.md`, the four Phase 13 slice and survey note pairs plus `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/tests/phase13_build.zig`, the five Phase 13 manifests, `zigux/Makefile`, `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig`.
- `validate-phase13-release.py` keeps that shared helper release packet aligned before the shared replay runs, and `check-phase13-devres-packet.py` keeps the stricter helper-first `devres` boundary contract visible inside the same validator-first route.
- `make -C zigux phase13-validate` keeps that same release packet wired through the Linux-style validation entrypoint.
- `zig build test --build-file zigux/tests/phase13_build.zig --summary all` and `make -C zigux phase13` rerun the fifteen-step shared helper replay without widening the roadmap beyond the four manifest-backed anchors and the adjacent read-only notifier packet.

Phase 15 flow
- the current shared Phase 15 governance surface on `master` is `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, and `zigux/tests/phase15_build.zig`.
- `check-phase15-review-process-handoff.py` keeps the dedicated review-process note and its manifest-backed handoff evidence aligned around the self-reference, product-boundary, and parked-route markers that keep the Architecture Council packet reviewable without inventing a broader governance surface.
- `zig build test --build-file zigux/tests/phase15_build.zig` and `make -C zigux phase15` rerun the parked freeze-map, Architecture Council review-process, parity-scorecard, dedicated indefinite-C policy, and stay-in-C governance packet without implying any new approval claim for a freeze-map anchor.
- the current bounded Phase 15 decision is still to leave the lane parked unless a named reopen trigger fires or the deep-core blocker posture changes enough to justify another Architecture Council slice.

Windows note
- a Linux-scale checkout on NTFS must use a case-sensitive directory or a Linux filesystem
- otherwise case-colliding Linux paths will create false working-tree dirt on Windows
