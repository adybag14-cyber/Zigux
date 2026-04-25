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
- `run-phase3-checks.py`
- `phase3_catalog.py`
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

Phase 3 flow
- `phase3_catalog.py` discovers Phase 3 slices from the docs, dump entrypoints, and fixture manifests instead of maintaining one giant hard-coded inventory, and now carries per-slice metadata such as display descriptions, build-step overrides, and the current `PHASE3_INTEROP_GATE` mode recorded in each slice doc.
- `phase3_catalog.py --self-test` exercises isolated slug discovery, manifest selection, and interop-gate classification across docs, dumps, and fixture candidates.
- `phase3_catalog.py --legacy-wrapper-docs` lists the discovered slice docs that still point at legacy `check-phase3-*.py` compatibility wrappers.
- `phase3_catalog.py --rewrite-shared-runner-docs` rewrites those legacy per-slice doc commands to the shared `run-phase3-checks.py --slug ...` form so wrapper-reference cleanup is scripted instead of manual.
- `phase3_catalog.py --legacy-wrapper-references` lists remaining discovered Phase 3 wrapper mentions in non-slice documentation, which keeps stray policy-doc references auditable now that the manifest cleanup is complete.
- `phase3_catalog.py --rewrite-legacy-wrapper-references` rewrites those non-slice documentation references to the shared runner form, leaving `artifact-diff.md` and similar policy docs on the same scripted cleanup path as the slice records.
- `phase3_catalog.py --rewrite-artifact-diff-phase3-section` regenerates the detailed `Documentation/zigux/artifact-diff.md` Phase 3 policy block from the discovered slice catalog.
- `phase3_catalog.py --audit-doc-sync` reports stale non-slice wrapper references plus a stale `artifact-diff.md` Phase 3 block, and bootstrap now runs it so documentation drift fails fast.
- `phase3_check_lib.py` holds the shared Phase 3 parity execution logic used by every wrapper and the shared runner.
- `phase3_check_lib.py --self-test` checks the shared slug, fixture-key, build-step, status-name, wrapper-template, and argument-parsing helpers without running Zig parity builds.
- `generate-phase3-check-wrappers.py` regenerates the tiny `check-phase3-*.py` wrapper stubs from one shared template.
- `generate-phase3-check-wrappers.py --self-test` exercises isolated missing-wrapper, stale-wrapper, obsolete-wrapper, and clean `--check` behavior without touching the committed tree.
- `generate-phase3-check-wrappers.py --check` fails when any discovered wrapper drifts from that shared template or when an obsolete wrapper should be removed.
- `validate-phase3.py` validates every discovered slice, its selected manifest, and the required documentation markers, accepts either the shared runner gate (`run-phase3-checks.py --slug ...`) or a legacy `check-phase3-*.py` wrapper in the slice doc, reports obsolete wrapper shims that no longer map to a discovered slice, and rejects legacy wrapper script paths inside Phase 3 manifests so those manifests stay focused on source, dump, harness, and committed fixture artifacts.
- `validate-phase3.py --self-test` exercises manifest, optional-wrapper, obsolete-wrapper, wrapper-template, and documentation-marker checks in a temporary Phase 3 fixture tree.
- `run-phase3-checks.py` lists or executes every discovered Phase 3 slice from catalog metadata through one shared entrypoint, even when a wrapper stub is missing.
- `run-phase3-checks.py --self-test` checks slug filtering plus direct runner and fail-fast behavior without launching Zig parity builds.
- `make -C zigux phase3-validate` now mirrors the lightweight CI safety net for this tranche by running the validator, the validator/catalog/shared-helper/runner self-tests, the documentation-sync audit, and the wrapper-template check before the parity suite.

Rules
- keep helpers narrow and product-facing
- do not duplicate general Linux scripts here
- if a helper becomes broadly useful, move it or integrate it with the native subsystem flow
