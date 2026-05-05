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
- `validate-phase4.py` checks that the bounded Phase 4 differential gates, their shared `zigux/tests/phase4_build.zig` entrypoint, and the directly coupled documentation and workflow markers stay aligned.
- `zigux/tests/phase4_build.zig` runs the live `runtime_atomic64_diff.zig` and `bitmap_diff.zig` rollback-readiness gates together instead of letting one of them drift out of the regular validation path.
- `Documentation/zigux/phase4-validation-matrix.md` keeps the current rollback owners, threshold posture, and lab or CI replay matrix explicit for the shipped Phase 4 gates.

Phase 6 flow
- `validate-phase6.py` checks that the bounded base64, bsearch, checksum, and hexdump helper packet stays aligned across `Documentation/zigux/README.md`, `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase6_helper_parity_manifest.json`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and the bootstrap workflow before the broader shared Phase 6 review surface claims the packet is parked.
- `check-phase6-docs-root-external-parity.py` keeps the docs-root external portability inventory fail-closed across `Documentation/zigux/README.md`, `Documentation/zigux/phase6-helper-parity-catalog.md`, `scripts/zigux/README.md`, `zigux/tests/phase6_helper_parity_manifest.json`, and `zigux/Makefile` so the shared Phase 6 packet does not silently undercount the shipped checker surface.
- `check-phase6-base64-catalog-evidence.py` keeps the shared base64 review packet fail-closed on the catalog `verified head`, the manifest `surveyed_commit`, the parked shared-packet posture, and the current base64 evidence counts before the packet stays reviewable from higher-level docs.
- `check-phase6-base64-c-parity.py`, `check-phase6-bsearch-c-parity.py`, `check-phase6-checksum-c-parity.py`, and `check-phase6-hexdump-c-parity.py` are the bounded external portability spot checks for the four roadmap-backed leaf helpers before the live `zig` plus `cc` replay runs.
- `check-phase6-checksum-hexdump-perf-markers.py` keeps the shipped checksum and hexdump perf-marker packet fail-closed around the committed reporting markers before broader Phase 6 replay claims stay green.
- `make -C zigux phase6-validate` is the shared fail-fast catalog gate, `make -C zigux phase6` replays the bundled helper tests together, and `make -C zigux phase6-perf` replays the bundled perf harnesses without widening the default helper-test lane.
